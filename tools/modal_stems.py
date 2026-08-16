#!/usr/bin/env python3
"""THE STEM FORGE — serverless H100 audio->stems, the whole DAG parallel.

Chezy's order (2026-08-02): "FULLY SERVERLESS GPU PIPELINE FOR THE AUDIO TO
STEM CONVERSION FOR EXTREME SPEED ... FULLY PERFECTLY PARALLELISE THE ENTIRE
THING". The CPU rung's ledger for a 6:53 song: separation 2524s + drum
finisher 1557s + transcription 175s. This rail lands the same artifacts in
tens of seconds of cloud wall.

ARCHITECTURE (the xg_agent worker doctrine, ported to Modal):
  * WEIGHTS BAKED AT BUILD — like the RunPod worker's `RUN python -c 'load'`
    lines: bs_roformer ep317 (public UVR mirror), htdemucs_ft + htdemucs_6s
    (torch hub), drumsep mdx23c OpenVINO IR (HF Intel repo) all download into
    image layers during the CLOUD build. A cold container boots with every
    checkpoint already on local disk. Nothing ever uploads from home.
  * ONE GPU CLASS, MANY METHODS — roformer shards, demucs bag members, the 6s
    microscope and the transcription rails all live on `StemGpu`, so a
    container warmed by stage 1 is REUSED by stages 2..4 (no rebooted pools).
  * SCALE OUT, NOT JUST UP — the v41 worker pooled 64 replicas on one H200;
    serverless inverts it: each shard/member is its own container, Modal
    autoscales the fleet, scaledown_window keeps it warm between imports.

EXACTNESS LAWS (the local rail is the reference; the forge must land the SAME
artifacts the local caches would hold):
  * CHUNK-GRID SHARDING: mss_roformer + drumsep both run chunked hann
    overlap-add on a deterministic grid (chunk C, step, pad=C, tail). A shard
    owns a CONTIGUOUS RANGE OF CHUNK INDICES over the same padded coordinates
    and returns its (out_span, norm_span) accumulators; the orchestrator's
    sum equals the serial result exactly (modulo float addition order).
    No crossfade heuristics — the same math, split by index.
  * BAG-MEMBER FAN: htdemucs_ft is a BagOfModels(4). demucs/apply.py sums
    member estimates weighted per-source and divides by the weight totals —
    members are independent, so each runs in its own container and the
    orchestrator reproduces the exact weighted mean (shifts=1, split=True,
    overlap=0.25 — the CLI defaults the local rail uses).
  * separate.py NORM LAW: ref = wav.mean(0); wav = (wav - ref.mean()) /
    ref.std(); estimates * ref.std() + ref.mean(). Recomputed identically
    wherever needed (same input -> same floats).
  * THE CLEAN SPLIT (Chezy 2026-07-11): roformer vocals FIRST on the full
    mix, demucs only ever hears instrumental = mix - vocals; the landed
    vocals.wav carries the `.model` = "bs_roformer" marker so the local
    refine pass knows the pass is already paid.
  * SIX-STEM RE-SUM LAW: the 6s microscope listens to the RE-SUMMED landed
    stems (not the original mix), peak-guarded to 0.98 above 0.99 — exactly
    six_stem_assist()'s input construction.
  * BPM/KEY REPLICATION: transcription notes are beat-domain, so the forge
    computes bpm (estimate_bpm on the drums stem + the octave + tatum laws
    from build_session) and key (analyze2 Krumhansl on 'other' + the keyvote
    override) with the SHIPPED local code. The local seam in transcribe_v2
    only consumes remote notes whose bpm/key/role match what it would have
    passed — any drift falls open to the local rails.
  * WIRE FORMAT: FLAC 24-bit + per-file peak scale (manifest["scales"]).
    -144dB quantization floor, far under the -90dB tails the INT16 AMBUSH
    law protects; local placement decodes back to float32 WAV (subtype
    FLOAT), the exact format every downstream court expects. Stems whose
    peaks exceed |1.0| are scaled into range and restored on decode.

CACHES THE CLIENT PRE-FILLS (songs/<name>_stems/) — the local import then
skips every heavy stage through its OWN reuse laws, untouched:
    drums/bass/other/vocals.wav      -> import_song's 4-stem reuse branch
    vocals.wav.model = "bs_roformer" -> refine_vocals_roformer marker skip
    6s/{guitar,piano,other}.wav      -> six_stem_assist idempotent reuse
    drum_pieces/{kick,snare,toms,hh,cymbals}.wav (mtime > drums.wav)
                                     -> drumsep.separate_cached REUSE LAW
                                        (also kills the deferred finisher)
    remote_notes/<wav>.json          -> transcribe_v2 remote seam
                                        {bpm,key,role,engine,notes}

USAGE:
    modal deploy tools/modal_stems.py            # once (cloud build bakes weights)
    .venv/bin/python tools/modal_stems.py run song.mp3 myname   # forge only
    SOTADAW_STEMS_REMOTE=1 tools/stems_import.py song.mp3 myname  # full import
    .venv/bin/python tools/modal_stems.py smoke  # 8s synthetic through every rail

Config env: SOTADAW_MODAL_GPU (default "H100", comma list = fallbacks),
SOTADAW_MODAL_KEEP=1 keeps the job dir on the volume for autopsy.
Fail-open: any forge error -> the caller keeps the local rails (the import
must never die of a cloud hiccup).
"""
import io
import json
import math
import os
import sys
import time

import modal

APP_NAME = "sotadaw-stems"
VOL_NAME = "sotadaw-stems-io"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REMOTE_ROOT = "/root/sota"                 # tools/ + third_party/ land here
MSS = "/root/.cache/sotadaw/mss"           # where the tools expect weights

BS_CKPT_URL = ("https://github.com/TRvlvr/model_repo/releases/download/"
               "all_public_uvr_models/model_bs_roformer_ep_317_sdr_12.9755.ckpt")
BS_CKPT_BYTES = 639331213                  # mss_roformer.py's size pin
OV_REPO = "Intel/drumsep_mdx23c_jarredou_openvino"
OV_FILES = {"mdx23c_pre.xml": 23755, "mdx23c_pre.bin": 4250,
            "mdx23c_fwd.xml": 775191, "mdx23c_fwd.bin": 218753348,
            "mdx23c_post.xml": 21482, "mdx23c_post.bin": 4214}
PIECES_OV = ("kick", "snare", "toms", "hh", "cymbals")
DS_CHUNK, DS_SR = 523776, 44100            # drumsep grid constants


def _gpu_kind():
    g = os.environ.get("SOTADAW_MODAL_GPU", "H100")
    return [s.strip() for s in g.split(",")] if "," in g else g


# --------------------------------------------------------------- image bake
def _bake_weights():
    """Runs INSIDE the image build (cloud CPU, fat pipe): every checkpoint
    lands in image layers so cold containers never download anything."""
    import shutil
    import urllib.request
    os.makedirs(MSS + "/drumsep", exist_ok=True)
    # 1) BS-Roformer ep317 — the vocals separator (size-pinned identity).
    ck = os.path.join(MSS, "bs_roformer_ep317.ckpt")
    for attempt in range(3):
        try:
            if not (os.path.exists(ck) and os.path.getsize(ck) == BS_CKPT_BYTES):
                print(f"[bake] bs_roformer <- {BS_CKPT_URL}", flush=True)
                urllib.request.urlretrieve(BS_CKPT_URL, ck)
            break
        except Exception as e:
            print(f"[bake] retry {attempt + 1} ({e})", flush=True)
            time.sleep(10)
    got = os.path.getsize(ck)
    assert got == BS_CKPT_BYTES, f"bs_roformer ckpt {got} != {BS_CKPT_BYTES}"
    # 2) demucs htdemucs_ft (bag of 4) + htdemucs_6s via torch hub.
    from demucs.pretrained import get_model
    get_model("htdemucs_ft")
    get_model("htdemucs_6s")
    # 3) drumsep mdx23c OpenVINO IR (the drum microscope).
    from huggingface_hub import snapshot_download
    snap = snapshot_download(OV_REPO)
    found = {}
    for base, _dirs, files in os.walk(snap):
        for f in files:
            if f in OV_FILES:
                found[f] = os.path.join(base, f)
    for f, want in OV_FILES.items():
        assert f in found, f"drumsep IR missing {f} in {snap}"
        got = os.path.getsize(found[f])
        assert got == want, f"drumsep {f}: {got} != {want}"
        shutil.copy2(found[f], os.path.join(MSS, "drumsep", f))
    # 4) transcription rails: basic-pitch/fcpe/crepe ship weights in-wheel;
    #    import once so any lazy unpack happens at build, not first request.
    import torch  # noqa: F401  (CUDA PRELOAD LAW — torch before basic_pitch)
    import basic_pitch.inference  # noqa: F401
    import torchcrepe  # noqa: F401
    import torchfcpe  # noqa: F401
    print("[bake] all weights baked", flush=True)


image = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("ffmpeg", "libsndfile1")
    # torch alone first: the heavy layer stays cached across pin tweaks below
    .pip_install("torch==2.12.1", "torchaudio")
    .pip_install(
        "numpy==1.26.4", "scipy==1.16.1",
        "soundfile==0.13.1", "librosa==0.11.0",
        "demucs==4.0.1",
        "einops==0.8.2", "rotary-embedding-torch==0.9.1", "beartype==0.22.9",
        "pyyaml", "onnxruntime==1.23.0",               # CPU ORT: no preload trap
        "torchfcpe==0.0.4", "torchcrepe==0.0.24",
        "openvino", "huggingface_hub",
        # basic-pitch's REAL runtime deps (see below): it declares tensorflow
        # <2.15.1 which does not exist for py3.12, yet runs pure-ONNX — the
        # local venv proves it (0 tensorflow packages installed).
        "pretty_midi==0.2.11", "mir_eval==0.8.2", "resampy==0.4.3",
        "scikit-learn",
    )
    .pip_install("basic-pitch==0.4.0", extra_options="--no-deps")
    .run_function(_bake_weights, cpu=4, memory=8192, timeout=3600)
    # runtime layers (code iterates without image rebuilds) — must come last
    .add_local_file(os.path.join(ROOT, "tools", "modal_assets",
                                 "bs_roformer_ep317.yaml"),
                    remote_path=MSS + "/bs_roformer_ep317.yaml")
    .add_local_dir(os.path.join(ROOT, "third_party", "bs_roformer"),
                   remote_path=REMOTE_ROOT + "/third_party/bs_roformer")
    .add_local_dir(os.path.join(ROOT, "tools"),
                   remote_path=REMOTE_ROOT + "/tools",
                   ignore=lambda p: not str(p).endswith(".py"))
)

app = modal.App(APP_NAME)
io_vol = modal.Volume.from_name(VOL_NAME, create_if_missing=True)
VOLS = {"/io": io_vol}


# ------------------------------------------------------------ shared helpers
def _wire_path():
    sys.path.insert(0, REMOTE_ROOT + "/tools")


def _flac24(path, x, sr):
    """float array [N,C] -> FLAC 24-bit; returns the peak scale to restore.
    scale > 1 means the file holds x/scale (peaks over |1.0| squeezed in)."""
    import numpy as np
    import soundfile as sf
    peak = float(np.max(np.abs(x)) + 1e-12)
    scale = peak / 0.999 if peak > 0.999 else 1.0
    sf.write(path, (x / scale).astype("float64"), sr, subtype="PCM_24",
             format="FLAC")
    return scale


def _read_stage(job, name):
    import soundfile as sf
    x, sr = sf.read(f"/io/{job}/stage/{name}.wav", dtype="float32",
                    always_2d=True)
    return x, sr


def _demucs_norm(inst_f32):
    """separate.py's exact normalization: returns (wav_norm [2,N] tensor,
    ref_mean, ref_std) — recomputed identically wherever needed."""
    import torch
    wav = torch.from_numpy(inst_f32.T.copy())          # [2, N] float32
    ref = wav.mean(0)
    m, s = ref.mean(), ref.std()
    return (wav - m) / s, m, s


def _batched_split(model, wav, device, B0):
    """THE FULL-GPU LAW (Chezy: "UTILISE ENTIRE GPU BUT NO OOMING"):
    demucs apply_model(shifts=0, split=True) reproduced with BATCHED
    forwards. Exactness: for HTDemucs, valid_length == segment_length, so
    TensorChunk.padded() is a delta-0 no-op on every FULL segment — the
    else-branch degenerates to model(raw_slice), and batching raw slices is
    the same math. The (possibly short) TAIL segment routes through
    apply_model itself (centered context pad — the one case that differs).
    OOM ladder: start at B0, halve on CUDA OOM, floor 1 (= stock demucs).
    wav: [2, N] float32 cpu tensor (already separate.py-normalized).
    Returns [S, 2, N] float32 cpu."""
    import torch as th
    from demucs.apply import apply_model, TensorChunk
    length = wav.shape[-1]
    S = len(model.sources)
    segment_length = int(model.samplerate * model.segment)
    stride = int((1 - 0.25) * segment_length)          # CLI overlap default
    offsets = list(range(0, length, stride))
    weight = th.cat([th.arange(1, segment_length // 2 + 1),
                     th.arange(segment_length - segment_length // 2, 0, -1)])
    weight = (weight / weight.max()) ** 1.0            # transition_power 1
    out = th.zeros(S, 2, length)
    sum_weight = th.zeros(length)
    full = [o for o in offsets if o + segment_length <= length]
    tail = [o for o in offsets if o + segment_length > length]
    i, B = 0, max(1, B0)
    while i < len(full):
        take = full[i:i + B]
        try:
            segs = th.stack([wav[:, o:o + segment_length] for o in take]).to(device)
            with th.no_grad():
                est = model(segs)                      # [b, S, 2, seg]
            est = est.cpu()
        except th.cuda.OutOfMemoryError:
            th.cuda.empty_cache()
            if B == 1:
                raise
            B = max(1, B // 2)
            continue
        for k, o in enumerate(take):
            out[..., o:o + segment_length] += weight * est[k]
            sum_weight[o:o + segment_length] += weight
        i += len(take)
    for o in tail:                                     # exact stock path
        chunk = TensorChunk(wav[None], o, segment_length)
        est = apply_model(model, chunk, shifts=0, split=False,
                          overlap=0.25, device=device, progress=False)[0]
        cl = est.shape[-1]
        out[..., o:o + cl] += weight[:cl] * est.cpu()
        sum_weight[o:o + cl] += weight[:cl]
    assert float(sum_weight.min()) > 0
    return out / sum_weight


def _shifted_split(model, wav, device, B0):
    """apply_model's shifts=1 wrapper around the batched split — the same
    random equivariant shift the CLI applies (statistical, not bit, parity;
    the stock rail's shift is random too)."""
    import random
    import torch as th
    length = wav.shape[-1]
    max_shift = int(0.5 * model.samplerate)
    offset = random.randint(0, max_shift)
    padded = th.nn.functional.pad(wav, (max_shift, max_shift))
    shifted = padded[:, offset:offset + length + max_shift]
    res = _batched_split(model, shifted, device, B0)
    return res[..., max_shift - offset:max_shift - offset + length]


# ------------------------------------------------------------- GPU workers
# COST LAW (Chezy 2026-08-03 "fix that!"): the compute is ~400 GPU-s per full
# song (~$0.45 on H100) — the REAL burn was the idle tail: scaledown_window
# 240s x N warm containers billed ~2min of idle H100 per container after the
# work ended. 60s keeps stage-to-stage reuse (gaps are seconds) and caps the
# tail at ~$0.07/container. SOTADAW_MODAL_SCALEDOWN overrides (e.g. 300 for
# a batch of imports back-to-back); SOTADAW_MODAL_GPU=A100-40GB is the ~45%
# cheaper / ~1.6x slower ride.
_SCALEDOWN = int(os.environ.get("SOTADAW_MODAL_SCALEDOWN", "60"))


@app.cls(image=image, gpu=_gpu_kind(), cpu=4, memory=16384, timeout=1800,
         scaledown_window=_SCALEDOWN, max_containers=6, retries=1, volumes=VOLS)
class StemGpu:
    @modal.enter()
    def boot(self):
        _wire_path()
        import torch  # noqa: F401 (CUDA runtime up before any rail)
        self.models = {}                    # lazy per-method warm cache

    # ---- BS-Roformer: one shard = a contiguous range of hann chunks ----
    @modal.method()
    def roformer_span(self, x_f32, ci0, ci1, num_overlap=2):
        """x_f32 [N,2] full mix at 44100. Returns (a0, out_span, norm_span)
        — the exact accumulator contributions of chunks [ci0, ci1)."""
        import numpy as np
        import torch
        if "rof" not in self.models:
            import mss_roformer as mr
            self.models["rof"] = mr._load_model("cuda")
        model, cfg = self.models["rof"]
        C = int(cfg["audio"]["chunk_size"])
        step = C // max(1, int(num_overlap))
        N = len(x_f32)
        mix = torch.from_numpy(np.ascontiguousarray(x_f32.T)).float()
        pad = C
        mix = torch.nn.functional.pad(mix, (pad, pad + (step - (N % step)) % step))
        a0, a1 = ci0 * step, (ci1 - 1) * step + C
        out = torch.zeros((2, a1 - a0))
        norm = torch.zeros(a1 - a0)
        win = torch.hann_window(C, periodic=False).clamp(min=1e-3)
        # THE FULL-GPU LAW: batch B chunks per forward (chunks are
        # independent; per-chunk accumulation order unchanged). B starts
        # from a VRAM probe, halves on CUDA OOM, floors at 1 (= the old
        # serial loop) — no OOM can kill a shard, even edge cases.
        B = int(os.environ.get("SOTADAW_MODAL_ROF_BATCH", "0"))
        if B <= 0:
            free, _tot = torch.cuda.mem_get_info()
            B = max(1, min(16, int(free / (1.5 * 2 ** 30))))
        idxs = list(range(ci0, ci1))
        i = 0
        with torch.no_grad():
            while i < len(idxs):
                take = idxs[i:i + B]
                try:
                    segs = torch.stack(
                        [mix[:, ci * step:ci * step + C] for ci in take]
                    ).to("cuda")
                    with torch.autocast("cuda", dtype=torch.float16):
                        v = model(segs)
                    v = v.float().cpu()
                except torch.cuda.OutOfMemoryError:
                    torch.cuda.empty_cache()
                    if B == 1:
                        raise
                    B = max(1, B // 2)
                    continue
                if v.dim() == 4:
                    v = v[:, 0]
                for k, ci in enumerate(take):
                    a = ci * step
                    out[:, a - a0:a - a0 + C] += v[k] * win
                    norm[a - a0:a - a0 + C] += win
                i += len(take)
        return a0, out.numpy(), norm.numpy()

    # ---- htdemucs_ft: one bag member over the whole instrumental ----
    @modal.method()
    def demucs_member(self, inst_f32, idx):
        """Returns (idx, weights_row, sources, est [S,2,N] float32 in the
        NORMALIZED domain) — the orchestrator does the weighted mean + unnorm."""
        import torch
        from demucs.apply import apply_model
        from demucs.pretrained import get_model
        if "ft" not in self.models:
            self.models["ft"] = get_model("htdemucs_ft")
        bag = self.models["ft"]
        sub, w = bag.models[idx], list(bag.weights[idx])
        sub.to("cuda").eval()
        wav, _m, _s = _demucs_norm(inst_f32)
        B0 = int(os.environ.get("SOTADAW_MODAL_FT_BATCH", "8"))
        est = _shifted_split(sub, wav, "cuda", B0)
        return idx, w, list(bag.sources), est.numpy().astype("float32")

    # ---- htdemucs_6s: the harmonic microscope (single model) ----
    @modal.method()
    def demucs_6s(self, job):
        """Reads the landed stems off the volume, re-sums them exactly like
        six_stem_assist, separates, writes 6s stage wavs. Returns sources."""
        import numpy as np
        import soundfile as sf
        import torch
        from demucs.apply import apply_model
        from demucs.pretrained import get_model
        io_vol.reload()
        mix, sr = None, 44100
        for s in ("drums", "bass", "other", "vocals"):
            sx, sr = _read_stage(job, s)
            mix = sx if mix is None else mix[:len(sx)] + sx[:len(mix)]
        peak = float(np.max(np.abs(mix)) or 1.0)
        if peak > 0.99:
            mix = mix / peak * 0.98        # six_stem_assist's exact guard
        if "6s" not in self.models:
            self.models["6s"] = get_model("htdemucs_6s")
        model = self.models["6s"]
        bag6 = getattr(model, "models", None)
        sub6 = bag6[0] if bag6 else model          # 6s ships as a bag of 1
        sub6.to("cuda").eval()
        wav, m, sd = _demucs_norm(mix.astype("float32"))
        B0 = int(os.environ.get("SOTADAW_MODAL_FT_BATCH", "8"))
        est = _shifted_split(sub6, wav, "cuda", B0)
        est = est * sd + m
        srcs = list(model.sources)
        os.makedirs(f"/io/{job}/stage/6s", exist_ok=True)
        for want in ("guitar", "piano", "other"):
            if want in srcs:
                y = est[srcs.index(want)].cpu().numpy().T
                sf.write(f"/io/{job}/stage/6s/{want}.wav",
                         y.astype("float32"), sr, subtype="FLOAT")
        io_vol.commit()
        return srcs

    # ---- the specialist transcription rails (fcpe/crepe/basic-pitch) ----
    @modal.method()
    def transcribe(self, job, rel_wav, bpm, role, key):
        """One lane through the same rails transcribe_v2 would run locally.
        Returns {"engine", "notes"} or {"error"} (caller just skips the seam)."""
        _wire_path()
        import torch  # noqa: F401
        io_vol.reload()
        wav = f"/io/{job}/stage/{rel_wav}"
        try:
            import transcribe_stems as ts
            if role == "bass":
                notes, rec = ts.bass_notes(wav, bpm)
            elif role == "vocal":
                notes, rec = ts.vocal_notes(wav, bpm)
            else:
                notes, rec = ts.other_notes(wav, bpm, key=key)
            return {"engine": rec.get("engine", "remote"), "notes": notes,
                    "rec": {k: v for k, v in rec.items()
                            if isinstance(v, (int, float, str))}}
        except Exception as e:
            return {"error": f"{type(e).__name__}: {e}"}


# ------------------------------------------------------------- CPU workers
@app.cls(image=image, cpu=8, memory=8192, timeout=1800,
         scaledown_window=_SCALEDOWN, max_containers=14, retries=1, volumes=VOLS)
class DrumCpu:
    @modal.enter()
    def boot(self):
        _wire_path()

    @modal.method()
    def drumsep_span(self, job, ci0, ci1):
        """Chunks [ci0, ci1) of the mdx23c OV grid over the drums stem.
        Returns (a0, out_span [5,2,L], norm_span [L]) float32."""
        import numpy as np
        import drumsep as ds
        io_vol.reload()
        x, sr = _read_stage(job, "drums")
        assert sr == DS_SR
        pre, fwd, post = ds._ov_chain()
        mix = np.ascontiguousarray(x.T, dtype=np.float32)
        step, pad = DS_CHUNK // 2, DS_CHUNK
        N = mix.shape[1]
        tail = (step - (N % step)) % step
        mix = np.pad(mix, ((0, 0), (pad, pad + tail)))
        a0, a1 = ci0 * step, (ci1 - 1) * step + DS_CHUNK
        out = np.zeros((5, 2, a1 - a0), dtype=np.float32)
        norm = np.zeros(a1 - a0, dtype=np.float32)
        win = np.clip(np.hanning(DS_CHUNK), 1e-3, None).astype(np.float32)
        for ci in range(ci0, ci1):
            a = ci * step
            seg = mix[:, a:a + DS_CHUNK][None]
            wavs = post(fwd(pre(seg)[0])[0])[0][0]     # [5,2,C]
            out[:, :, a - a0:a - a0 + DS_CHUNK] += wavs * win
            norm[a - a0:a - a0 + DS_CHUNK] += win
        return a0, out, norm


# ------------------------------------------------------------ orchestrator
def _progress(job, stage, frac, detail=""):
    try:
        os.makedirs(f"/io/{job}", exist_ok=True)
        with open(f"/io/{job}/progress.json", "w") as f:
            json.dump({"stage": stage, "frac": frac, "detail": detail,
                       "t": time.time()}, f)
        io_vol.commit()
    except Exception:
        pass


@app.function(image=image, cpu=8, memory=32768, timeout=3600, volumes=VOLS)
def orchestrate(job, src_name, opts=None):
    """The DAG. Reads /io/<job>/in/<src_name>, lands /io/<job>/out/* + manifest.
    Every stage fans as wide as the math allows; barriers only where the local
    rail itself is serial (the clean-split cascade)."""
    import numpy as np
    import soundfile as sf
    _wire_path()
    opts = opts or {}
    t0 = time.time()
    tl = {}
    io_vol.reload()

    import mss_roformer as mr
    src = f"/io/{job}/in/{src_name}"
    x64, sr = mr._load_audio(src)              # EXACT local decode law
    x32 = x64.astype("float32")
    N = len(x32)
    dur = N / sr
    if dur > float(os.environ.get("SOTADAW_MODAL_MAX_S", "1500")):
        raise RuntimeError(f"song {dur:.0f}s over the forge cap")
    os.makedirs(f"/io/{job}/stage", exist_ok=True)
    os.makedirs(f"/io/{job}/out/notes", exist_ok=True)
    tl["decode"] = round(time.time() - t0, 1)
    _progress(job, "roformer", 0.08, f"{dur:.0f}s at {sr}Hz")

    # ---- stage 1: BS-Roformer vocals, chunk-grid sharded ----
    t = time.time()
    import yaml
    cfg = yaml.unsafe_load(open(MSS + "/bs_roformer_ep317.yaml"))
    C = int(cfg["audio"]["chunk_size"])
    step = C // 2                               # num_overlap=2, the local default
    tail = (step - (N % step)) % step
    total = N + 2 * C + tail
    n_chunks = (total - C) // step + 1
    n_shards = max(1, min(int(opts.get("rof_shards", 4)),
                          math.ceil(n_chunks / 8)))
    bounds = [round(i * n_chunks / n_shards) for i in range(n_shards + 1)]
    gpu = StemGpu()
    rof_futs = [gpu.roformer_span.spawn(x32, bounds[i], bounds[i + 1])
                for i in range(n_shards)]
    out = np.zeros((2, total), dtype=np.float64)
    norm = np.zeros(total, dtype=np.float64)
    for f in rof_futs:
        a0, o, nz = f.get()
        out[:, a0:a0 + o.shape[1]] += o
        norm[a0:a0 + len(nz)] += nz
    voc = (out / np.clip(norm, 1e-6, None)).T[C:C + N]        # [N,2] f64
    inst = x64 - voc                                          # exact complement
    sf.write(f"/io/{job}/stage/vocals.wav", voc.astype("float32"), sr,
             subtype="FLOAT")
    tl["roformer"] = round(time.time() - t, 1)
    _progress(job, "demucs_ft", 0.30, f"{n_shards} shards in {tl['roformer']}s")

    # ---- stage 2: htdemucs_ft bag members fanned over the instrumental ----
    t = time.time()
    inst32 = inst.astype("float32")
    ft_futs = [gpu.demucs_member.spawn(inst32, i) for i in range(4)]
    est_sum, totals, sources = None, None, None
    for f in ft_futs:
        _idx, w, srcs, est = f.get()
        sources = srcs
        if est_sum is None:
            est_sum = np.zeros_like(est, dtype=np.float64)
            totals = np.zeros(len(srcs))
        for k, iw in enumerate(w):
            est_sum[k] += est[k] * iw
            totals[k] += iw
    wavn, m, sd = _demucs_norm(inst32)
    del wavn
    est_sum /= totals[:, None, None]
    est_sum = est_sum * float(sd) + float(m)                  # un-normalize
    for s in ("drums", "bass", "other"):
        y = est_sum[sources.index(s)].T                       # [N,2]
        sf.write(f"/io/{job}/stage/{s}.wav", y.astype("float32"), sr,
                 subtype="FLOAT")
    del est_sum
    io_vol.commit()                       # stems visible to every worker below
    tl["demucs_ft"] = round(time.time() - t, 1)
    _progress(job, "bpm_key", 0.48, f"bag x4 in {tl['demucs_ft']}s")

    # ---- stage 3: bpm + key with the SHIPPED local code (must match) ----
    t = time.time()
    from stems_import import estimate_bpm, load_analyze2
    bpm, conf = estimate_bpm(f"/io/{job}/stage/drums.wav")
    bpm, conf = float(bpm), float(conf)
    if conf < 0.3 and bpm < 85 and bpm * 2 <= 200:
        bpm *= 2
    elif bpm < 90:
        try:
            import transcribe_stems as ts
            if ts.tatum_wants_double(f"/io/{job}/stage/drums.wav", bpm):
                bpm = round(bpm * 2, 1)
        except Exception:
            pass
    a2 = load_analyze2()
    ox, osr = _read_stage(job, "other")
    key, key_conf = a2.estimate_key(ox.mean(axis=1), osr)
    key, key_conf = (str(key) if key else key), float(key_conf)
    try:
        from keyvote import vote as _keyvote
        kv_key, kv_conf, kv_n = _keyvote(src)
        if kv_key and kv_n >= 12:
            key, key_conf = kv_key, kv_conf
    except Exception:
        pass
    tl["bpm_key"] = round(time.time() - t, 1)
    _progress(job, "fan", 0.55, f"bpm {bpm} key {key}")

    # ---- stage 4: EVERYTHING ELSE AT ONCE ----
    #   drum microscope shards (CPU) + 6s microscope (GPU) + the melodic/
    #   vocal/bass transcription rails (GPU) all fly concurrently.
    t = time.time()
    dx, _dsr = _read_stage(job, "drums")
    dN = len(dx)
    dstep = DS_CHUNK // 2
    dtail = (dstep - (dN % dstep)) % dstep
    dtotal = dN + 2 * DS_CHUNK + dtail
    d_chunks = (dtotal - DS_CHUNK) // dstep + 1
    d_shards = max(1, min(int(opts.get("drum_shards", 12)),
                          math.ceil(d_chunks / 3)))
    dbounds = [round(i * d_chunks / d_shards) for i in range(d_shards + 1)]
    drum = DrumCpu()
    d_futs = [drum.drumsep_span.spawn(job, dbounds[i], dbounds[i + 1])
              for i in range(d_shards)]
    six_fut = gpu.demucs_6s.spawn(job)
    tr_specs = [("vocals.wav", bpm, "vocal", None),
                ("bass.wav", bpm, "bass", None),
                ("other.wav", bpm, "melodic", key)]
    tr_futs = {rel: gpu.transcribe.spawn(job, rel, b, r, k)
               for rel, b, r, k in tr_specs}

    dout = np.zeros((5, 2, dtotal), dtype=np.float64)
    dnorm = np.zeros(dtotal, dtype=np.float64)
    for f in d_futs:
        a0, o, nz = f.get()
        dout[:, :, a0:a0 + o.shape[2]] += o
        dnorm[a0:a0 + len(nz)] += nz
    dnz = np.clip(dnorm, 1e-6, None)
    os.makedirs(f"/io/{job}/out/drum_pieces", exist_ok=True)
    scales = {}
    for i, nm in enumerate(PIECES_OV):
        y = (dout[i] / dnz)[:, DS_CHUNK:DS_CHUNK + dN].T      # [N,2]
        scales[f"drum_pieces/{nm}.flac"] = _flac24(
            f"/io/{job}/out/drum_pieces/{nm}.flac", y.astype("float32"), sr)
    del dout
    tl["drumsep"] = round(time.time() - t, 1)
    _progress(job, "6s+notes", 0.75, f"{d_shards} drum shards in {tl['drumsep']}s")

    t = time.time()
    six_sources = six_fut.get()
    io_vol.reload()                       # see the 6s worker's stage writes
    six_notes = []
    for lane in ("guitar", "piano", "other"):
        if os.path.exists(f"/io/{job}/stage/6s/{lane}.wav"):
            six_notes.append((f"6s/{lane}.wav", bpm, "melodic", key))
    for rel, b, r, k in six_notes:
        tr_futs[rel] = gpu.transcribe.spawn(job, rel, b, r, k)
    tl["6s"] = round(time.time() - t, 1)

    t = time.time()
    engines = {}
    for rel, f in tr_futs.items():
        res = f.get()
        if "notes" in res:
            role = dict((s[0], s[2]) for s in tr_specs + six_notes)[rel]
            with open(f"/io/{job}/out/notes/{rel.replace('/', '__')}.json",
                      "w") as fh:
                json.dump({"bpm": bpm, "key": key, "role": role,
                           "engine": res["engine"], "notes": res["notes"]}, fh)
            engines[rel] = res["engine"]
        else:
            engines[rel] = "ERR " + res.get("error", "?")[:120]
    tl["transcribe"] = round(time.time() - t, 1)
    _progress(job, "encode", 0.9, "flac24 wire encode")

    # ---- stage 5: wire-encode the stems + manifest ----
    t = time.time()
    os.makedirs(f"/io/{job}/out/6s", exist_ok=True)
    from concurrent.futures import ThreadPoolExecutor
    def _enc(spec):
        rel, stage_rel = spec
        y, ysr = sf.read(f"/io/{job}/stage/{stage_rel}", dtype="float32",
                         always_2d=True)
        scales[rel] = _flac24(f"/io/{job}/out/{rel}", y, ysr)
    enc = [(f"{s}.flac", f"{s}.wav") for s in ("vocals", "drums", "bass", "other")]
    enc += [(f"6s/{s}.flac", f"6s/{s}.wav") for s in ("guitar", "piano", "other")
            if os.path.exists(f"/io/{job}/stage/6s/{s}.wav")]
    with ThreadPoolExecutor(4) as ex:
        list(ex.map(_enc, enc))
    tl["encode"] = round(time.time() - t, 1)
    tl["total"] = round(time.time() - t0, 1)

    manifest = {"job": job, "sr": sr, "n_samples": N, "dur_s": round(dur, 2),
                "bpm": bpm, "bpm_conf": round(float(conf), 3), "key": key,
                "key_conf": round(float(key_conf), 3), "engines": engines,
                "six_sources": six_sources, "scales": scales,
                "rof_shards": n_shards, "drum_shards": d_shards,
                "timings": tl, "gpu": str(_gpu_kind())}
    with open(f"/io/{job}/out/manifest.json", "w") as f:
        json.dump(manifest, f, indent=1)
    io_vol.commit()
    _progress(job, "done", 1.0, f"{tl['total']}s cloud wall")
    return manifest


# ------------------------------------------------------------- local client
def _say(msg):
    print(f"[forge] {msg}", flush=True)


def prewarm(audio_path, stems_dir, hb=None):
    """The local hook: forge remotely, then pre-fill every cache the local
    import already checks. Returns the manifest dict on success; raises on
    any failure (the caller falls open to the local rails)."""
    import numpy as np
    import soundfile as sf
    t0 = time.time()
    hb = hb or (lambda *_a, **_k: None)
    vol = modal.Volume.from_name(VOL_NAME, create_if_missing=True)
    # THE RESUME DOOR (2026-08-11 dead-air court: a VPN drop mid-download
    # left the forged job DONE and paid in the volume while the local pool
    # blocked forever. SOTADAW_FORGE_RESUME_JOB=<job> skips upload+spawn
    # and re-enters at download+place — a stalled wire never pays the GPU
    # twice.)
    job = os.environ.get("SOTADAW_FORGE_RESUME_JOB", "")
    if job:
        manifest = json.loads(
            b"".join(vol.read_file(f"{job}/out/manifest.json")).decode())
        _say(f"RESUME {job}: forge already paid — re-entering at download")
    else:
        job = time.strftime("j%Y%m%d_%H%M%S")
        fn = modal.Function.from_name(APP_NAME, "orchestrate")
        src_name = "src" + os.path.splitext(audio_path)[1].lower()
        _say(f"upload {os.path.basename(audio_path)} "
             f"({os.path.getsize(audio_path) / 1e6:.1f}MB)")
        hb("forging stems (cloud GPU)", 0.04, "uploading the record")
        with vol.batch_upload(force=True) as b:
            b.put_file(audio_path, f"{job}/in/{src_name}")

        call = fn.spawn(job, src_name)
        _say(f"orchestrating on {_gpu_kind()} (job {job})")
        manifest, last_stage = None, ""
        while manifest is None:
            try:
                manifest = call.get(timeout=6)
            except TimeoutError:
                try:
                    # NB: Volume.reload() is container-only; local reads are
                    # always served fresh from the last commit.
                    pj = json.loads(b"".join(
                        vol.read_file(f"{job}/progress.json")).decode())
                    if pj.get("stage") != last_stage:
                        last_stage = pj.get("stage", "")
                        _say(f"cloud: {last_stage} — {pj.get('detail', '')}")
                    # PROGRESS ORDER LAW (Chezy: "% ORDER IS ALL FUCKED UP"):
                    # build_session's stage fracs start at 0.44 (microscope) —
                    # the forge phase must stay strictly UNDER them or the bar
                    # runs backwards at handoff. Cloud maps into 0.05..0.35.
                    hb("forging stems (cloud GPU)",
                       0.05 + 0.30 * float(pj.get("frac", 0)),
                       f"{last_stage} {pj.get('detail', '')}")
                except Exception:
                    pass
    tl = manifest["timings"]
    _say(f"cloud wall {tl['total']}s — rof {tl['roformer']}s / ft "
         f"{tl['demucs_ft']}s / drums {tl['drumsep']}s / notes "
         f"{tl['transcribe']}s (bpm {manifest['bpm']}, key {manifest['key']})")

    # ---- download + place the caches (mtime law: pieces AFTER drums) ----
    hb("forging stems (cloud GPU)", 0.37, "downloading stems (flac24 wire)")
    os.makedirs(stems_dir, exist_ok=True)
    from modal.volume import FileEntryType
    files = [e.path for e in vol.listdir(f"{job}/out", recursive=True)
             if e.type == FileEntryType.FILE]
    scales = manifest["scales"]

    beat = {"t": time.time()}   # any chunk landing anywhere beats this clock

    def _fetch(relentry):
        rel = relentry.split(f"{job}/out/", 1)[1]
        buf = bytearray()
        for chunk in vol.read_file(relentry):
            buf += chunk
            beat["t"] = time.time()
        blob = bytes(buf)
        if rel.endswith(".flac"):
            x, xsr = sf.read(io.BytesIO(blob), dtype="float32", always_2d=True)
            x *= float(scales.get(rel, 1.0))
            dst = os.path.join(stems_dir, rel[:-5] + ".wav")
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            sf.write(dst, x, xsr, subtype="FLOAT")
        else:
            dst = os.path.join(stems_dir, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            with open(dst, "wb") as f:
                f.write(blob)
        return rel, len(blob)

    # THE DEAD-AIR COURT (2026-08-11: a VPN drop mid-download left every
    # socket ESTAB on a vanished tunnel IP — read_file has no timeout, so
    # the pool waited 40min on wire that could never speak again. Blocked
    # threads can't be interrupted; so DAEMON workers + a chunk-beat stall
    # clock: dead air for SOTADAW_FORGE_STALL_S (default 120) raises into
    # the caller's fail-open, and the job STAYS in the volume for a free
    # SOTADAW_FORGE_RESUME_JOB rerun.)
    import queue as _queue
    import threading as _threading
    stall_s = float(os.environ.get("SOTADAW_FORGE_STALL_S", "") or 120)
    order = sorted(files, key=lambda p: ("drum_pieces" in p, p))  # pieces last
    todo, done = _queue.Queue(), _queue.Queue()
    for p in order:
        todo.put(p)

    def _pull():
        while True:
            try:
                p = todo.get_nowait()
            except _queue.Empty:
                return
            try:
                done.put(_fetch(p))
            except Exception as fe:   # the verdict crosses the queue
                done.put((p, fe))

    for _ in range(min(6, len(order)) or 1):
        _threading.Thread(target=_pull, daemon=True).start()
    got, landed = 0, 0
    while landed < len(order):
        try:
            res = done.get(timeout=5)
        except _queue.Empty:
            if time.time() - beat["t"] > stall_s:
                raise RuntimeError(
                    f"download DEAD-AIR {int(stall_s)}s with {landed}/"
                    f"{len(order)} placed — wire lost; the job is kept: "
                    f"rerun with SOTADAW_FORGE_RESUME_JOB={job}")
            continue
        if isinstance(res[1], Exception):
            raise RuntimeError(
                f"download failed on {res[0]}: {res[1]!r} — job kept: "
                f"rerun with SOTADAW_FORGE_RESUME_JOB={job}")
        rel, nbytes = res
        got += nbytes
        landed += 1
        hb("forging stems (cloud GPU)", 0.37 + 0.06 * landed / len(order),
           f"downloading stems {landed}/{len(order)}")
    _say(f"downloaded {got / 1e6:.0f}MB -> {os.path.basename(stems_dir)}/")

    # VERIFY-ON-PLACE (the truncated-wav court, 2026-08-03: a placed
    # drums.wav landed 1KB short of its RIFF header's claim on a 99%-full
    # disk — soundfile shrugged, scipy died, the whole import fell over):
    # probe every wav with BOTH readers the pipeline uses; a broken file is
    # DELETED so the local rails regenerate it instead of crashing on it.
    import scipy.io.wavfile as _wv
    import warnings as _warn
    bad = []
    for root, _dirs, fnames in os.walk(stems_dir):
        for f in fnames:
            if not f.endswith(".wav"):
                continue
            p = os.path.join(root, f)
            try:
                with _warn.catch_warnings():
                    _warn.simplefilter("ignore")
                    sf.read(p, frames=8)
                    _wv.read(p)
            except Exception as ve:
                bad.append((os.path.relpath(p, stems_dir),
                            f"{type(ve).__name__}: {str(ve)[:60]}"))
                os.unlink(p)
    if bad:
        _say(f"VERIFY: {len(bad)} placed wav(s) unreadable, deleted -> "
             f"local rails regenerate them: "
             + "; ".join(f"{r} ({w})" for r, w in bad))
        if any(r in ("drums.wav", "bass.wav", "other.wav", "vocals.wav")
               for r, _w in bad):
            raise RuntimeError("core stem failed verify-on-place "
                               "(disk full?) — falling open to local rails")

    # notes/<x>.json -> the transcribe_v2 seam layout next to each wav
    ndir = os.path.join(stems_dir, "notes")
    placed_notes = 0
    if os.path.isdir(ndir):
        for f in sorted(os.listdir(ndir)):
            rel = f[:-5].replace("__", "/")            # 6s__other.wav -> 6s/other.wav
            wav_dir = os.path.join(stems_dir, os.path.dirname(rel))
            os.makedirs(os.path.join(wav_dir, "remote_notes"), exist_ok=True)
            os.replace(os.path.join(ndir, f),
                       os.path.join(wav_dir, "remote_notes",
                                    os.path.basename(rel) + ".json"))
            placed_notes += 1
        os.rmdir(ndir) if not os.listdir(ndir) else None
    if placed_notes:
        _say(f"{placed_notes} note seams placed (transcription pre-paid)")
    else:
        # HONESTY (2026-08-08 the full-disk run placed ZERO silently and the
        # local rails re-listened for 163s without a word of why)
        _say("0 note seams placed (download/disk?) — local rails will "
             "re-listen")
    # the clean-split marker: the refine pass is already paid
    with open(os.path.join(stems_dir, "vocals.wav.model"), "w") as f:
        f.write("bs_roformer")
    # mtime law: pieces strictly after drums.wav (separate_cached REUSE)
    now = time.time()
    os.utime(os.path.join(stems_dir, "drums.wav"), (now - 60, now - 60))
    pdir = os.path.join(stems_dir, "drum_pieces")
    if os.path.isdir(pdir):
        for f in os.listdir(pdir):
            os.utime(os.path.join(pdir, f), (now, now))
    try:
        with open(os.path.join(stems_dir, "forge_manifest.json"), "w") as f:
            json.dump(manifest, f, indent=1)
    except Exception as me:
        _say(f"manifest stamp failed ({me}) — placement already succeeded "
             f"(disk full?)")
    if os.environ.get("SOTADAW_MODAL_KEEP") != "1":
        try:
            vol.remove_file(job, recursive=True)
        except Exception:
            pass
    _say(f"caches pre-filled in {time.time() - t0:.0f}s wall "
         f"(cloud {tl['total']}s) — local import now skips every heavy stage")
    return manifest


# ---------------------------------------------------------------- CLI
def _cli():
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    runp = sub.add_parser("run", help="forge stems for an audio file")
    runp.add_argument("audio")
    runp.add_argument("name", help="songs/<name>_stems/ target")
    sub.add_parser("smoke", help="8s synthetic clip through every rail")
    a = ap.parse_args()
    if a.cmd == "run":
        stems_dir = os.path.join(ROOT, "songs", f"{a.name}_stems")
        m = prewarm(a.audio, stems_dir)
        print(json.dumps({k: m[k] for k in ("bpm", "key", "timings", "engines")},
                         indent=1))
    elif a.cmd == "smoke":
        import numpy as np
        import soundfile as sf
        sr = 44100
        tt = np.arange(8 * sr) / sr
        kick = np.sin(2 * np.pi * 55 * tt) * (np.sin(2 * np.pi * 2 * tt) > 0.97)
        tone = 0.3 * np.sin(2 * np.pi * 220 * tt) + 0.2 * np.sin(2 * np.pi * 330 * tt)
        x = np.stack([kick + tone, kick + tone], axis=1) * 0.7
        p = "/tmp/forge_smoke.wav"
        sf.write(p, x.astype("float32"), sr, subtype="FLOAT")
        m = prewarm(p, os.path.join(ROOT, "songs", "_forge_smoke_stems"))
        print(json.dumps(m["timings"], indent=1))


if __name__ == "__main__":
    _cli()
