#!/usr/bin/env python3
"""BS-Roformer vocal separation — THE ROBUST separator for LAYERED vocals.

Why it earns its place (ground truth 2026-07-09, THREE dry-vocal oracles — a
real a-cappella never in any mix + wad3 instrumental, SI-SDR vs the TRUE voice):

    clip       demucs-base   demucs_ft   roformer
    lead          +24.72       +22.24      +13.99   (clean lead: demucs wins)
    harmony        -2.69       -12.50      +12.64   (demucs COLLAPSES; roformer holds)
    double        +13.83        +1.58      +13.91   (demucs_ft near-dead; roformer holds)

demucs is spectacular on an isolated LEAD but goes NEGATIVE on harmony/doubled
vocals — worse than silence. Roformer is flat ~13dB whatever the density. This
DAW's material is rap with doubled hooks, ad-libs and harmonies (the exact
failure case), so vocals route through roformer; drums/bass/other stay demucs
(roformer is vocals-only). BS-Roformer (Wang et al. 2023, band-split RoPE
transformer), community checkpoint viperx ep317 (multisong SDR 12.97, UVR
public repo), vendored MIT arch in third_party/bs_roformer/.

Files (one-time, ~/.cache/sotadaw/mss/ — outside the repo, like torch hub):
  bs_roformer_ep317.ckpt   639,331,213 bytes
  bs_roformer_ep317.yaml   the training config (freqs_per_bands etc.)

The model is single-stem (target=Vocals): vocals = model(mix);
instrumental = mix - vocals (exact closure — stems always resum to the mix).

GPU-GATED: ~0.5s/audio-s on CUDA, unusable on Pi-class CPU — callers fall
back to the demucs path when available() is False. Pure inference; no
training deps.
"""
import math
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MSS_DIR = os.path.expanduser("~/.cache/sotadaw/mss")
CKPT = os.path.join(MSS_DIR, "bs_roformer_ep317.ckpt")
CFG = os.path.join(MSS_DIR, "bs_roformer_ep317.yaml")
CKPT_BYTES = 639331213                 # guards a truncated download


def available(need_gpu=True):
    """Model + config on disk (and a CUDA device unless need_gpu=False)."""
    try:
        if not (os.path.exists(CFG) and os.path.exists(CKPT)
                and os.path.getsize(CKPT) == CKPT_BYTES):
            return False
        if need_gpu:
            import torch
            return torch.cuda.is_available()
        return True
    except Exception:
        return False


def _load_model(device):
    import torch
    import yaml
    sys.path.insert(0, os.path.join(ROOT, "third_party", "bs_roformer"))
    from bs_roformer import BSRoformer
    import inspect
    cfg = yaml.unsafe_load(open(CFG))     # our own vendored file (python/tuple tag)
    mk = dict(cfg["model"])
    sig = set(inspect.signature(BSRoformer.__init__).parameters)
    model = BSRoformer(**{k: v for k, v in mk.items() if k in sig})
    state = torch.load(CKPT, map_location="cpu", weights_only=True)
    if isinstance(state, dict) and "state_dict" in state:
        state = state["state_dict"]
    state = { (k[6:] if k.startswith("model.") else k): v for k, v in state.items() }
    model.load_state_dict(state)
    model.eval().to(device)
    return model, cfg


def separate_vocals(x, sr, num_overlap=2, progress=None):
    """x: float array [N, 2] (or [N] mono) at 44100 — returns (vocals [N, 2],
    instrumental [N, 2]) via chunked hann overlap-add through the model.
    num_overlap 2 = the speed default; 4 = the config's max-quality setting."""
    import torch
    assert sr == 44100, f"BS-Roformer runs at 44100 (got {sr})"
    if x.ndim == 1:
        x = np.stack([x, x], axis=1)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, cfg = _load_model(device)
    C = int(cfg["audio"]["chunk_size"])
    step = C // max(1, int(num_overlap))
    N = len(x)
    mix = torch.from_numpy(np.ascontiguousarray(x.T)).float()     # [2, N]
    pad = C                                                        # edge room
    mix = torch.nn.functional.pad(mix, (pad, pad + (step - (N % step)) % step))
    total = mix.shape[1]
    out = torch.zeros_like(mix)
    norm = torch.zeros(total)
    win = torch.hann_window(C, periodic=False).clamp(min=1e-3)
    n_chunks = (total - C) // step + 1
    with torch.no_grad():
        for ci, a in enumerate(range(0, total - C + 1, step)):
            seg = mix[:, a:a + C].unsqueeze(0).to(device)
            with torch.autocast("cuda", dtype=torch.float16,
                                enabled=(device == "cuda")):
                v = model(seg)
            v = v.float().cpu()
            if v.dim() == 4:               # (b, stems, ch, t) -> target stem 0
                v = v[:, 0]
            out[:, a:a + C] += v[0] * win
            norm[a:a + C] += win
            if progress and (ci % 8 == 0 or ci == n_chunks - 1):
                progress(ci + 1, n_chunks)
    voc = (out / norm.clamp(min=1e-6)).numpy().T[pad:pad + N].astype(np.float64)
    inst = x[:, :2].astype(np.float64) - voc
    return voc, inst


def _load_audio(path):
    """Any audio -> (x [N,2] float64, 44100) via soundfile, else ffmpeg."""
    try:
        import soundfile as sf
        x, sr = sf.read(path, always_2d=True)
    except Exception:
        import subprocess
        import tempfile
        t = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        subprocess.run(["ffmpeg", "-y", "-i", path, "-ar", "44100", "-ac", "2",
                        t.name], check=True, capture_output=True)
        import soundfile as sf
        x, sr = sf.read(t.name, always_2d=True)
        os.unlink(t.name)
    if sr != 44100:
        import scipy.signal as ss
        n2 = int(round(len(x) * 44100.0 / sr))
        x = ss.resample(x, n2, axis=0)
        sr = 44100
    if x.shape[1] == 1:
        x = np.repeat(x, 2, axis=1)
    return x[:, :2], sr


def main():
    if len(sys.argv) < 3:
        sys.exit("usage: mss_roformer.py in_audio out_vocals.wav [out_inst.wav] "
                 "[--overlap N]")
    inp, out_v = sys.argv[1], sys.argv[2]
    out_i = sys.argv[3] if len(sys.argv) > 3 and not sys.argv[3].startswith("--") else None
    ov = int(sys.argv[sys.argv.index("--overlap") + 1]) if "--overlap" in sys.argv else 2
    x, sr = _load_audio(inp)
    import time
    t0 = time.time()
    voc, inst = separate_vocals(x, sr, num_overlap=ov,
                                progress=lambda i, n: print(
                                    f"\r[mss] {i}/{n} chunks", end="", flush=True))
    print(f"\n[mss] {len(x)/sr:.0f}s audio in {time.time()-t0:.0f}s (overlap {ov})")
    import soundfile as sf
    sf.write(out_v, voc, sr, subtype="PCM_16")
    if out_i:
        sf.write(out_i, inst, sr, subtype="PCM_16")


if __name__ == "__main__":
    main()
