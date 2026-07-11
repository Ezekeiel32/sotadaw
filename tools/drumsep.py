#!/usr/bin/env python3
"""THE DRUM MICROSCOPE — physical drum-piece separation (kick/snare/toms/hh/cymbals).

Why: the drum rail's 3-band butterworth lanes (kick<140 / snare 180-2000 /
hat>5500) are a HEURISTIC ear — toms have no band at all, rides and crashes
share the hat band, and layered hits mask each other. This module gives the
rail PHYSICAL piece stems instead: jarredou's MDX23C DrumSep checkpoint
(DrumSep test SDR: kick 16.66 / snare 11.53 / toms 12.33 / hh 4.04 /
cymbals 6.36 — the best public drum separator, 2026-07-12 survey in
docs/A2M_MAX_RESEARCH.md).

Runtime: Intel's OpenVINO IR port (huggingface.co/Intel/drumsep_mdx23c_jarredou_openvino)
— the STFT/iSTFT live in tiny pre/post graphs, the net in mdx23c_fwd:
    pre  [1,2,523776]        -> [1,4,1024,1024]      (waveform chunk -> re/im x 2ch spec)
    fwd  [1,4,1024,1024]     -> [1,5,4,1024,1024]    (5 piece specs)
    post [1,5,4,1024,1024]   -> [1,5,2,523776]       (piece waveforms)
CPU inference BY DESIGN: the CUDA card belongs to training runs (voice_shell)
— this rail must never contend. ~11.9s chunks, hann overlap-add (the
mss_roformer law). License: CC-BY-NC-SA-4.0 (non-commercial, attribution
"MDX23C DrumSep by aufr33 & jarredou, OpenVINO port by Intel") — same class
as the Gahata Meiji voice bank.

Fallback: inagoy's htdemucs drumsep (~/.cache/sotadaw/mss/drumsep_htdemucs.th,
kick/snare/cymbals/toms — no hh split; hats are carved from the cymbals piece
by the classic 5.5k highpass) through the installed demucs package.

PIECE ORDER: pinned empirically by tools/drumsep_battery.py's self-ID probe
(synthesized kick/snare/hat/tom/crash -> energy routing); see PIECES_OV.

Kill switch: SOTADAW_NO_DRUMSEP=1 (available() -> None, callers keep the
band-lane path). Cache law: separate_cached() writes pieces next to the stem
(<stem_dir>/drum_pieces/<piece>.wav, float32) and reuses them while they
outdate the stem — separation is the expensive pass, transcription retunes
free.
"""
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MSS_DIR = os.path.expanduser("~/.cache/sotadaw/mss")
OV_DIR = os.path.join(MSS_DIR, "drumsep")
OV_FILES = {"mdx23c_pre.xml": 23755, "mdx23c_pre.bin": 4250,
            "mdx23c_fwd.xml": 775191, "mdx23c_fwd.bin": 218753348,
            "mdx23c_post.xml": 21482, "mdx23c_post.bin": 4214}
TH_CKPT = os.path.join(MSS_DIR, "drumsep_htdemucs.th")
TH_BYTES = 167400043

# Model output slot -> piece name. Pinned by the battery's self-ID probe
# (energy routing of synthesized hits; 2026-07-12): jarredou's training
# order kick/snare/toms/hh/cymbals landed as-is in Intel's IR.
PIECES_OV = ("kick", "snare", "toms", "hh", "cymbals")
CHUNK = 523776                            # pre graph's static waveform window
SR = 44100

_OV = {"chain": None}                     # compiled pre/fwd/post, loaded once


def available():
    """None | "openvino" | "demucs" — what the box can run right now."""
    if os.environ.get("SOTADAW_NO_DRUMSEP") == "1":
        return None
    try:
        ok = all(os.path.exists(os.path.join(OV_DIR, f))
                 and os.path.getsize(os.path.join(OV_DIR, f)) == sz
                 for f, sz in OV_FILES.items())
        if ok:
            import openvino  # noqa: F401
            return "openvino"
    except Exception:
        pass
    try:
        if os.path.exists(TH_CKPT) and os.path.getsize(TH_CKPT) == TH_BYTES:
            import demucs.pretrained  # noqa: F401
            return "demucs"
    except Exception:
        pass
    return None


def _ov_chain():
    if _OV["chain"] is None:
        import openvino as ov
        core = ov.Core()
        comp = [core.compile_model(core.read_model(
            os.path.join(OV_DIR, f"mdx23c_{s}.xml")), "CPU")
            for s in ("pre", "fwd", "post")]
        _OV["chain"] = comp
    return _OV["chain"]


def _separate_ov(x, progress=None, spool_dir=None):
    """x [N,2] float at 44100 -> dict piece -> [N,2] float32.
    Chunked hann overlap-add through pre->fwd->post (the mss_roformer law).

    MEMORY LAW (earlyoom court 2026-07-12): the first live run died a silent
    SIGKILL at minute 20 — float64 accumulators (~1.5GB on a 410s stem) on
    top of the OV runtime pushed RSS to 3.7GB on a loaded box. Accumulate
    float32, and when spool_dir is given (the cached rail does), back the
    [5,2,total] accumulator with a disk memmap so RAM peak is the OV runtime
    alone. NVMe eats the ~40MB/chunk of IO without noticing."""
    pre, fwd, post = _ov_chain()
    N = len(x)
    mix = np.ascontiguousarray(x.T, dtype=np.float32)          # [2, N]
    step = CHUNK // 2
    pad = CHUNK
    tail = (step - (N % step)) % step
    mix = np.pad(mix, ((0, 0), (pad, pad + tail)))
    total = mix.shape[1]
    spool = None
    if spool_dir:
        os.makedirs(spool_dir, exist_ok=True)
        spool = os.path.join(spool_dir, ".accum.f32")
        out = np.memmap(spool, dtype=np.float32, mode="w+",
                        shape=(5, 2, total))
    else:
        out = np.zeros((5, 2, total), dtype=np.float32)
    norm = np.zeros(total, dtype=np.float32)
    win = np.clip(np.hanning(CHUNK), 1e-3, None).astype(np.float32)
    n_chunks = (total - CHUNK) // step + 1
    try:
        for ci, a in enumerate(range(0, total - CHUNK + 1, step)):
            seg = mix[:, a:a + CHUNK][None]                    # [1,2,C]
            spec = pre(seg)[0]
            sep = fwd(spec)[0]
            wavs = post(sep)[0][0]                             # [5,2,C]
            out[:, :, a:a + CHUNK] += wavs * win
            norm[a:a + CHUNK] += win
            if progress and (ci % 2 == 0 or ci == n_chunks - 1):
                progress(ci + 1, n_chunks)
        nz = np.clip(norm, 1e-6, None)
        pieces = {}
        for i, nm in enumerate(PIECES_OV):
            y = np.asarray(out[i], dtype=np.float32) / nz      # one piece at a time
            pieces[nm] = y[:, pad:pad + N].T.copy()
    finally:
        del out
        if spool and os.path.exists(spool):
            os.unlink(spool)
    return pieces


def _separate_demucs(x, progress=None):
    """inagoy htdemucs fallback: kick/snare/cymbals/toms (self-described by
    model.sources). No hh piece — callers highpass the cymbals piece."""
    import torch
    from pathlib import Path
    from demucs.pretrained import get_model
    from demucs.apply import apply_model
    # inagoy's .th is an OLD-STYLE full-model pickle (not a state dict):
    # torch>=2.6 weights_only default refuses it. The file is size-pinned
    # (TH_BYTES) from the known mirror — allowlist the demucs classes.
    import demucs.hdemucs
    import demucs.demucs
    import demucs.htdemucs
    with torch.serialization.safe_globals(
            [demucs.hdemucs.HDemucs, demucs.demucs.Demucs,
             demucs.htdemucs.HTDemucs, Path("dummy").__class__]):
        model = get_model(name="drumsep_htdemucs", repo=Path(MSS_DIR))
    model.eval()
    mix = torch.from_numpy(np.ascontiguousarray(x.T)).float()[None]
    with torch.no_grad():
        est = apply_model(model, mix, device="cpu", split=True,
                          overlap=0.25, progress=False)[0]     # [S,2,N]
    names = [s.lower() for s in model.sources]
    pieces = {}
    alias = {"bombo": "kick", "redoblante": "snare", "platillos": "cymbals",
             "toms": "toms", "kick": "kick", "snare": "snare",
             "cymbals": "cymbals", "tom": "toms"}
    for i, nm in enumerate(names):
        pieces[alias.get(nm, nm)] = est[i].numpy().T.astype(np.float64)
    if progress:
        progress(1, 1)
    return pieces


def separate_pieces(x, sr, progress=None, spool_dir=None):
    """x [N,2] (or mono [N]) at any sr -> dict piece -> [N,2] float32 at the
    INPUT sr (resampled back if needed). Keys: kick/snare/toms/hh/cymbals
    (hh absent on the demucs fallback). Returns None when unavailable."""
    mode = available()
    if mode is None:
        return None
    if x.ndim == 1:
        x = np.stack([x, x], axis=1)
    if x.shape[1] == 1:
        x = np.repeat(x, 2, axis=1)          # mono [N,1] files (battery wavs)
    x = x[:, :2].astype(np.float32)
    N0, sr0 = len(x), sr
    if sr != SR:
        import scipy.signal as ss
        x = ss.resample(x, int(round(len(x) * SR / sr)), axis=0).astype(np.float32)
    if mode == "openvino":
        pieces = _separate_ov(x, progress, spool_dir=spool_dir)
    else:
        pieces = _separate_demucs(x, progress)
    if sr0 != SR:
        import scipy.signal as ss
        pieces = {k: ss.resample(v, N0, axis=0).astype(np.float32)
                  for k, v in pieces.items()}
    return pieces


def separate_cached(stem_wav, progress=None, say=print):
    """Pieces for a drum stem, cached in <dir>/drum_pieces/ next to it.
    Returns dict piece -> wav path, or None when the rail is unavailable."""
    mode = available()
    if mode is None:
        return None
    import soundfile as sf
    pdir = os.path.join(os.path.dirname(os.path.abspath(stem_wav)), "drum_pieces")
    want = list(PIECES_OV) if mode == "openvino" else ["kick", "snare", "toms", "cymbals"]
    paths = {nm: os.path.join(pdir, nm + ".wav") for nm in want}
    smt = os.path.getmtime(stem_wav)
    if all(os.path.exists(p) and os.path.getmtime(p) >= smt
           for p in paths.values()):
        return paths                                   # REUSE LAW
    # RAM gate (measured: OV separation peaks ~3.7GB RSS on a 410s stem) —
    # a fresh separation on a starved box would OOM the whole import; the
    # band path is the honest fallback. Cache hits above cost nothing.
    try:
        avail_kb = int(next(l for l in open("/proc/meminfo")
                            if l.startswith("MemAvailable")).split()[1])
        if avail_kb < 3 * 1024 * 1024:
            say("[drumsep] <3GB RAM free -> band lanes this pass", flush=True)
            return None
    except (StopIteration, OSError):
        pass
    x, sr = sf.read(stem_wav, always_2d=True)
    say(f"[drumsep] {mode}: splitting {len(x)/sr:.0f}s of drums into "
        f"{len(want)} pieces (CPU, ~3x realtime)…", flush=True)
    if progress is None:                       # imports must never sit silent
        # _separate_ov rate-limits callbacks to every 2nd chunk (i arrives
        # ODD) — an i%8==0 filter here composed to NEVER; thin further by
        # elapsed count, not divisibility
        seen = [0]

        def progress(i, n):
            seen[0] += 1
            if seen[0] % 4 == 1 or i == n:
                say(f"[drumsep] {i}/{n} chunks", flush=True)
    pieces = separate_pieces(x[:, :2], sr, progress=progress, spool_dir=pdir)
    if pieces is None:
        return None
    os.makedirs(pdir, exist_ok=True)
    for nm in want:
        if nm in pieces:
            sf.write(paths[nm], pieces[nm].astype(np.float32), sr,
                     subtype="FLOAT")                  # f32 deck law
    return {nm: p for nm, p in paths.items() if os.path.exists(p)}


def main():
    import argparse
    import time
    import soundfile as sf
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("drums_wav")
    ap.add_argument("out_dir", nargs="?", default=None,
                    help="default: <stem_dir>/drum_pieces/")
    a = ap.parse_args()
    mode = available()
    if mode is None:
        sys.exit("[drumsep] unavailable (no models, or SOTADAW_NO_DRUMSEP=1)")
    t0 = time.time()
    if a.out_dir:
        x, sr = sf.read(a.drums_wav, always_2d=True)
        pieces = separate_pieces(x[:, :2], sr, progress=lambda i, n: print(
            f"\r[drumsep] {i}/{n} chunks", end="", flush=True))
        os.makedirs(a.out_dir, exist_ok=True)
        for nm, y in pieces.items():
            sf.write(os.path.join(a.out_dir, nm + ".wav"),
                     y.astype(np.float32), sr, subtype="FLOAT")
        print()
        outs = sorted(pieces)
    else:
        paths = separate_cached(a.drums_wav, progress=lambda i, n: print(
            f"\r[drumsep] {i}/{n} chunks", end="", flush=True))
        print()
        outs = sorted(paths) if paths else []
    print(f"[drumsep] {mode}: {', '.join(outs)} in {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
