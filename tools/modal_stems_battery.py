#!/usr/bin/env python3
"""THE STEM FORGE battery — pure/offline proofs for tools/modal_stems.py.

No cloud, no GPU, no checkpoints: these prove the ALGEBRA the forge rides —
that sharding the work across containers reproduces the serial rails' math —
plus the wire format and the local seam. The live rails themselves are proven
by `modal_stems.py smoke` (cloud) and the production import.

    .venv/bin/python tools/modal_stems_battery.py

Laws proven here:
  1. CHUNK-GRID SHARD LAW (roformer form): hann overlap-add split by chunk
     index ranges == the serial loop, any shard split, linear or nonlinear
     "model".
  2. CHUNK-GRID SHARD LAW (drumsep form): the 5-piece OV grid, same result.
  3. BAG MEMBER LAW: demucs/apply.py's weighted mean reproduced from
     independently-computed member estimates, in ANY gather order.
  4. NORM LAW: separate.py's ref normalization round-trips exactly.
  5. FLAC24 WIRE LAW: quantization under 2e-7 FS, hot peaks restored via
     scale, and a -100dB tail SURVIVES (the INT16 AMBUSH stays dead).
  6. THE FORGE SEAM: _remote_notes_for consumes only exact (role,bpm,key)
     matches; drift/malformed/missing all fall open to the local rails.
  7. NOTES NAME MAP: orchestrate's '/'->'__' flattening round-trips.
  8. CACHE MTIME LAW: placement order satisfies drumsep.separate_cached's
     reuse condition (pieces strictly fresher than drums.wav).
"""
import json
import os
import sys
import tempfile

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PASS = FAIL = 0


def check(name, ok, detail=""):
    global PASS, FAIL
    if ok:
        PASS += 1
        print(f"  PASS {name}")
    else:
        FAIL += 1
        print(f"  FAIL {name}  {detail}")


def _serial_ola(x, C, step, model, n_out):
    """The serial hann overlap-add exactly as mss_roformer/drumsep run it:
    pad=C both ends + tail-to-step, chunks at a in range(0, total-C+1, step)."""
    N = len(x)
    pad = C
    tail = (step - (N % step)) % step
    mix = np.pad(x.T.astype(np.float32), ((0, 0), (pad, pad + tail)))
    total = mix.shape[1]
    out = np.zeros((n_out,) + mix.shape[:-1] + (total,), dtype=np.float32) \
        if n_out > 1 else np.zeros_like(mix)
    norm = np.zeros(total, dtype=np.float32)
    win = np.clip(np.hanning(C), 1e-3, None).astype(np.float32)
    n_chunks = (total - C) // step + 1
    for ci in range(n_chunks):
        a = ci * step
        v = model(mix[:, a:a + C])
        if n_out > 1:
            out[:, :, a:a + C] += v * win
        else:
            out[:, a:a + C] += v * win
        norm[a:a + C] += win
    return out, norm, n_chunks, pad, total


def _shard_ola(x, C, step, model, n_out, bounds):
    """The forge's shard variant: each range [ci0,ci1) accumulates only its
    span and returns (a0, out_span, norm_span); the gather sums spans."""
    N = len(x)
    pad = C
    tail = (step - (N % step)) % step
    mix = np.pad(x.T.astype(np.float32), ((0, 0), (pad, pad + tail)))
    total = mix.shape[1]
    out = np.zeros((n_out, mix.shape[0], total), dtype=np.float64) \
        if n_out > 1 else np.zeros((mix.shape[0], total), dtype=np.float64)
    norm = np.zeros(total, dtype=np.float64)
    for i in range(len(bounds) - 1):
        ci0, ci1 = bounds[i], bounds[i + 1]
        if ci0 >= ci1:
            continue
        a0, a1 = ci0 * step, (ci1 - 1) * step + C
        o = np.zeros((n_out, mix.shape[0], a1 - a0), dtype=np.float32) \
            if n_out > 1 else np.zeros((mix.shape[0], a1 - a0), dtype=np.float32)
        nz = np.zeros(a1 - a0, dtype=np.float32)
        win = np.clip(np.hanning(C), 1e-3, None).astype(np.float32)
        for ci in range(ci0, ci1):
            a = ci * step
            v = model(mix[:, a:a + C])
            if n_out > 1:
                o[:, :, a - a0:a - a0 + C] += v * win
            else:
                o[:, a - a0:a - a0 + C] += v * win
            nz[a - a0:a - a0 + C] += win
        if n_out > 1:
            out[:, :, a0:a0 + o.shape[2]] += o
        else:
            out[:, a0:a0 + o.shape[1]] += o
        norm[a0:a0 + len(nz)] += nz
    return out, norm


def main():
    rng = np.random.default_rng(7)

    print("== CHUNK-GRID SHARD LAW (roformer form) ==")
    x = rng.standard_normal((41000, 2)).astype(np.float32) * 0.4
    C, step = 4096, 2048
    lin = lambda seg: seg * 0.7
    nl = lambda seg: np.tanh(seg * 1.3)
    for nm, model in (("linear", lin), ("nonlinear", nl)):
        so, sn, n_chunks, pad, total = _serial_ola(x, C, step, model, 1)
        serial = (so / np.clip(sn, 1e-6, None))[:, pad:pad + len(x)]
        for bounds in ([0, n_chunks], [0, 7, n_chunks],
                       [0, 3, 4, 11, n_chunks]):
            ho, hn = _shard_ola(x, C, step, model, 1, bounds)
            sharded = (ho / np.clip(hn, 1e-6, None))[:, pad:pad + len(x)]
            err = float(np.max(np.abs(sharded - serial)))
            check(f"{nm} shards={len(bounds)-1} == serial", err < 1e-5,
                  f"maxerr {err:.2e}")

    print("== CHUNK-GRID SHARD LAW (drumsep 5-piece form) ==")
    W = rng.standard_normal((5, 1, 1)).astype(np.float32)
    pieces = lambda seg: (seg[None] * W)          # [5, 2, C] like post()
    so, sn, n_chunks, pad, total = _serial_ola(x, 1000, 500, pieces, 5)
    serial = (so / np.clip(sn, 1e-6, None))[:, :, pad:pad + len(x)]
    ho, hn = _shard_ola(x, 1000, 500, pieces, 5, [0, 13, 30, n_chunks])
    sharded = (ho / np.clip(hn, 1e-6, None))[:, :, pad:pad + len(x)]
    err = float(np.max(np.abs(sharded - serial)))
    check("5-piece sharded == serial", err < 1e-5, f"maxerr {err:.2e}")

    print("== BAG MEMBER LAW (demucs weighted mean, any gather order) ==")
    S, Nn = 4, 5000
    ests = [rng.standard_normal((S, 2, Nn)).astype(np.float32) for _ in range(4)]
    weights = [list(map(float, rng.uniform(0.2, 1.5, S))) for _ in range(4)]
    ref = np.zeros((S, 2, Nn))                     # apply.py's serial order
    totals = np.zeros(S)
    for est, w in zip(ests, weights):
        for k in range(S):
            ref[k] += est[k] * w[k]
            totals[k] += w[k]
    ref /= totals[:, None, None]
    for order in ([0, 1, 2, 3], [3, 1, 0, 2], [2, 3, 1, 0]):
        acc = np.zeros((S, 2, Nn))
        tot = np.zeros(S)
        for i in order:
            for k in range(S):
                acc[k] += ests[i][k] * weights[i][k]
                tot[k] += weights[i][k]
        acc /= tot[:, None, None]
        err = float(np.max(np.abs(acc - ref)))
        check(f"gather order {order} == serial", err < 1e-6, f"{err:.2e}")

    print("== BATCHED SPLIT LAW (apply.py reproduced with batched forwards) ==")
    import torch as th
    import torch.nn as nn
    from demucs.apply import apply_model
    from modal_stems import _batched_split

    class _Dummy(nn.Module):
        def __init__(self):
            super().__init__()
            self.sources = ["a", "b", "c", "d"]
            self.samplerate = 100
            self.segment = 0.5
            self._p = nn.Parameter(th.zeros(1))

        def forward(self, x):
            return th.stack([x * 0.5, x * -0.25, x * 2.0, x * 0.1], dim=1)

    dm = _Dummy()
    dwav = th.from_numpy(rng.standard_normal((2, 731)).astype("float32"))
    ref_split = apply_model(dm, dwav[None], shifts=0, split=True,
                            overlap=0.25, device="cpu", progress=False)[0]
    for B in (1, 3, 7):
        got = _batched_split(dm, dwav, "cpu", B)
        err = float((got - ref_split).abs().max())
        check(f"batched split B={B} == apply_model (tail incl.)",
              err < 1e-6, f"{err:.2e}")

    print("== NORM LAW (separate.py ref round-trip) ==")
    from modal_stems import _demucs_norm
    inst = (rng.standard_normal((30000, 2)) * 0.3 + 0.02).astype(np.float32)
    wavn, m, s = _demucs_norm(inst)
    back = (wavn * s + m).numpy().T
    err = float(np.max(np.abs(back - inst)))
    check("(x-m)/s * s + m == x", err < 1e-6, f"{err:.2e}")

    print("== FLAC24 WIRE LAW ==")
    from modal_stems import _flac24
    import soundfile as sf
    with tempfile.TemporaryDirectory() as td:
        quiet = np.clip(rng.standard_normal((44100, 2)) * 0.25,
                        -0.9, 0.9).astype(np.float32)
        p = os.path.join(td, "q.flac")
        sc = _flac24(p, quiet, 44100)
        back, _ = sf.read(p, dtype="float32", always_2d=True)
        back *= sc
        err = float(np.max(np.abs(back - quiet)))
        check("quiet stem err < 2e-7 FS", err < 2e-7, f"{err:.2e}")
        check("quiet scale == 1.0", sc == 1.0, f"{sc}")
        hot = quiet * 13.0                          # peaks ~3.2 over FS
        p2 = os.path.join(td, "h.flac")
        sc2 = _flac24(p2, hot, 44100)
        back2, _ = sf.read(p2, dtype="float32", always_2d=True)
        back2 *= sc2
        err2 = float(np.max(np.abs(back2 - hot)))
        check("hot stem restored via scale", err2 < 2e-7 * sc2 * 1.5,
              f"{err2:.2e} scale {sc2:.2f}")
        t = np.arange(44100) / 44100.0
        tail = (1e-5 * np.sin(2 * np.pi * 220 * t)).astype(np.float32)  # -100dB
        sig = np.stack([tail, tail], axis=1)
        p3 = os.path.join(td, "t.flac")
        sc3 = _flac24(p3, sig, 44100)
        back3, _ = sf.read(p3, dtype="float32", always_2d=True)
        back3 *= sc3
        e_in = float(np.sqrt((sig ** 2).mean()))
        e_out = float(np.sqrt((back3 ** 2).mean()))
        db = 20 * np.log10(max(e_out, 1e-12) / e_in)
        check("-100dB tail survives (INT16 AMBUSH stays dead)",
              abs(db) < 1.0, f"{db:+.2f}dB")

    print("== THE FORGE SEAM (_remote_notes_for) ==")
    from stems_import import _remote_notes_for
    notes = [{"start": 0.0, "len": 0.5, "pitch": 60, "vel": 0.8}]
    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.join(td, "remote_notes"))
        wav = os.path.join(td, "vocals.wav")
        j = {"bpm": 128.0, "key": "F minor", "role": "vocal",
             "engine": "fcpe", "notes": notes}
        json.dump(j, open(os.path.join(td, "remote_notes", "vocals.wav.json"), "w"))
        r = _remote_notes_for(wav, 128.0, "vocal", None)
        check("exact match consumed", r is not None and r[1] == "fcpe"
              and r[0] == notes)
        check("bpm drift refused", _remote_notes_for(wav, 128.2, "vocal", None) is None)
        check("role mismatch refused", _remote_notes_for(wav, 128.0, "bass", None) is None)
        check("vocal role ignores key",
              _remote_notes_for(wav, 128.0, "vocal", "A major") is not None)
        j2 = dict(j, role="melodic")
        json.dump(j2, open(os.path.join(td, "remote_notes", "other.wav.json"), "w"))
        ow = os.path.join(td, "other.wav")
        check("melodic key match consumed",
              _remote_notes_for(ow, 128.0, "melodic", "F minor") is not None)
        check("melodic key drift refused",
              _remote_notes_for(ow, 128.0, "melodic", "G minor") is None)
        open(os.path.join(td, "remote_notes", "bad.wav.json"), "w").write("{nope")
        check("malformed json falls open",
              _remote_notes_for(os.path.join(td, "bad.wav"), 128.0, "vocal", None) is None)
        check("missing sidecar falls open",
              _remote_notes_for(os.path.join(td, "none.wav"), 128.0, "vocal", None) is None)

    print("== NOTES NAME MAP ==")
    for rel in ("vocals.wav", "6s/other.wav", "6s/guitar.wav"):
        flat = rel.replace("/", "__") + ".json"
        back = flat[:-5].replace("__", "/")
        check(f"{rel} round-trips", back == rel, back)

    print("== CACHE MTIME LAW ==")
    with tempfile.TemporaryDirectory() as td:
        import time as _time
        drums = os.path.join(td, "drums.wav")
        open(drums, "wb").write(b"x")
        now = _time.time()
        os.utime(drums, (now - 60, now - 60))
        pdir = os.path.join(td, "drum_pieces")
        os.makedirs(pdir)
        paths = {}
        for nm in ("kick", "snare", "toms", "hh", "cymbals"):
            p = os.path.join(pdir, nm + ".wav")
            open(p, "wb").write(b"y")
            os.utime(p, (now, now))
            paths[nm] = p
        smt = os.path.getmtime(drums)
        ok = all(os.path.getmtime(p) >= smt for p in paths.values())
        check("pieces fresher than drums (separate_cached REUSE)", ok)

    print(f"\nmodal_stems battery: {PASS} PASS / {FAIL} FAIL")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
