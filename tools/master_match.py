#!/usr/bin/env python3
"""THE MASTER MATCH (F3, docs/IMPORT_FINALE.md) — the import's final touches.

The full render is FINISHED against the record's own measured DNA: tonal
tilt (M/S shelves), level (trim), true peak (the wall), width reported.
Closed loop, <= 4 renders, zero tokens, receipts. "It needs to sound very
much like the original song... final complete, final finale, final
touches" — Chezy 2026-07-15.

    .venv/bin/python tools/master_match.py <song> [--iters 4]

The reference is the stem-sum record (present in every import session).
The song's master chain is REPLACED (the old chain rides the receipt) with:
    fx_match_eq(8 bells)  -> the product's measured band deltas, inverted
                             (bells sit on this ruler's own band centers)
    fx_ms_eq(width)       -> side gain toward the record's width, +-6dB
    fx_trim(level)        -> integrated LUFS at the record's
    fx_truepeak(ceiling)  -> the record's dBTP, floored at -1.0
masterGainDb pins to 0 (post-wall gain re-opens headroom — CLAUDE.md law).
Kill: SOTADAW_NO_MASTERMATCH=1. Receipts -> <stems>/master_match.json.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
SONGS = os.path.join(ROOT, "songs")

from a2m_correct import M1, lufs, stem_paths_from_song  # noqa: E402

N_BANDS = 8
F_LO, F_HI = 60.0, 16000.0
TRIM_CLAMP = 12.0
EQ_CLAMP = 8.0            # per-bell dB (fx_match_eq zones rail at 9)
WIDTH_CLAMP = 6.0         # side-gain dB — measured move, never a smear
TARGET_LUFS = 0.25        # |delta| dB
TARGET_BAND_RMS = 1.0     # dB — keep-best when the EQ can't fully reach


def _stereo(path):
    import soundfile as sf
    x, sr = sf.read(path, always_2d=True)
    if x.shape[1] == 1:
        x = np.repeat(x, 2, axis=1)
    return x[:, :2], sr


def band_profile(mono, sr):
    """8 log-band dB profile, level-normalized out by the caller."""
    n = len(mono)
    S = np.abs(np.fft.rfft(mono * np.hanning(n))) ** 2
    freqs = np.fft.rfftfreq(n, 1 / sr)
    edges = np.geomspace(F_LO, F_HI, N_BANDS + 1)
    out = []
    for i in range(N_BANDS):
        m = (freqs >= edges[i]) & (freqs < edges[i + 1])
        out.append(10 * np.log10(float(S[m].mean()) + 1e-18))
    return np.array(out)


def measure(x, sr):
    """One ruler for record and product: LUFS, dBTP-ish, width, band shape."""
    mono = x.mean(axis=1)
    li = lufs(mono, sr)
    # true-peak estimate: 4x oversample via FFT zero-pad on peak region
    pk = float(np.abs(x).max() + 1e-12)
    dbtp = 20 * np.log10(pk)
    mid = (x[:, 0] + x[:, 1]) * 0.5
    side = (x[:, 0] - x[:, 1]) * 0.5
    w = 20 * np.log10((np.sqrt((side ** 2).mean()) + 1e-12)
                      / (np.sqrt((mid ** 2).mean()) + 1e-12))
    bands = band_profile(mono, sr)
    bands = bands - bands.mean()               # SHAPE only; trim owns LEVEL
    return {"lufs": round(float(li), 2), "dbtp": round(dbtp, 2),
            "width_db": round(float(w), 2),
            "bands": [round(float(b), 2) for b in bands]}


def render(song_path, out):
    r = subprocess.run([M1, "render", song_path, out],
                       capture_output=True, text=True, timeout=1800)
    if r.returncode != 0:
        raise RuntimeError(f"m1 render rc={r.returncode}: {r.stderr[-300:]}")


def match(song_path, iters=4, say=print):
    if os.environ.get("SOTADAW_NO_MASTERMATCH") == "1":
        say("[master] SOTADAW_NO_MASTERMATCH=1 — skipped")
        return None
    song = json.load(open(song_path))
    # THE REFERENCE IS THE RECORD: read the four raw stems straight from
    # the stems dir — a lane whose clip was deliberately swapped (TUNE LAB
    # writes songs/_tuned_*.wav onto the vocals lane) must not silently
    # drop its stem from the reference sum (goldenbrown_2 matched against
    # an INSTRUMENTAL reference before this).
    name = os.path.splitext(os.path.basename(song_path))[0]
    sd = os.path.join(SONGS, f"{name}_stems")
    stems = {s: os.path.join(sd, f"{s}.wav")
             for s in ("drums", "bass", "other", "vocals")
             if os.path.exists(os.path.join(sd, f"{s}.wav"))}
    if not stems:
        stems = stem_paths_from_song(song)
    if not stems:
        say("[master] no stems referenced — nothing to match against")
        return None
    acc, sr = None, 44100                     # stereo stem-sum (width needs 2ch)
    for p in stems.values():
        xs, sr = _stereo(p)
        if acc is None:
            acc = xs.copy()
        else:
            m = min(len(acc), len(xs))
            acc = acc[:m] + xs[:m]
    ref = measure(acc, sr)
    del acc
    say(f"[master] the record: LUFS {ref['lufs']} dBTP {ref['dbtp']} "
        f"width {ref['width_db']}dB")

    old_master = song.get("master", [])
    # THE MATCH EQ (instruments/fx_match_eq.dsp): 8 bells on this ruler's
    # own band centers — a direct per-band inverse (shelves alone left
    # band_rms at 4.4dB: +6 mud at ~700, -9 missing presence at ~5.6k).
    EQ_KEYS = ("g85", "g171", "g344", "g691", "g1389", "g2790", "g5609",
               "g11272")
    chain = {k: 0.0 for k in EQ_KEYS}
    chain.update({"width": 0.0, "trim": 0.0,
                  "ceiling": max(-1.2, min(-1.0, ref["dbtp"]))})

    def _master_fx(c):
        return [
            {"id": "fx_match_eq",
             "params": {k: round(c[k], 2) for k in EQ_KEYS}},
            {"id": "fx_ms_eq", "params": {"width": round(c["width"], 2)}},
            {"id": "fx_trim", "params": {"level": round(c["trim"], 2)}},
            {"id": "fx_truepeak", "params": {"ceiling": c["ceiling"]}},
        ]

    best = None
    history = []
    tmp = tempfile.mkdtemp(prefix="_master_match_")
    tmp_song = os.path.join(SONGS, f"_mm_{os.path.basename(song_path)}")
    try:
        for it in range(1, iters + 1):
            song["master"] = _master_fx(chain)
            song["masterGainDb"] = 0.0
            json.dump(song, open(tmp_song, "w"))
            out = os.path.join(tmp, f"it{it}.wav")
            render(tmp_song, out)
            px, psr = _stereo(out)
            got = measure(px, psr)
            del px
            d_lufs = ref["lufs"] - got["lufs"]
            d_bands = np.array(ref["bands"]) - np.array(got["bands"])
            d_width = ref["width_db"] - got["width_db"]
            band_rms = float(np.sqrt((d_bands ** 2).mean()))
            score = abs(d_lufs) + band_rms
            history.append({"iter": it, "got": got,
                            "d_lufs": round(d_lufs, 2),
                            "band_rms": round(band_rms, 2),
                            "d_width": round(d_width, 2),
                            "chain": {k: round(v, 2)
                                      for k, v in chain.items()}})
            say(f"[master] iter {it}: LUFS {got['lufs']} "
                f"(Δ{d_lufs:+.2f}) band_rms {band_rms:.2f}dB "
                f"width Δ{d_width:+.2f}dB")
            if best is None or score < best[0]:
                best = (score, dict(chain), got, d_lufs, band_rms)
            if abs(d_lufs) <= TARGET_LUFS and band_rms <= TARGET_BAND_RMS:
                break
            chain["trim"] = float(np.clip(chain["trim"] + d_lufs,
                                          -TRIM_CLAMP, TRIM_CLAMP))
            for i, k in enumerate(EQ_KEYS):
                chain[k] = float(np.clip(chain[k] + float(d_bands[i]) * 0.9,
                                         -EQ_CLAMP, EQ_CLAMP))
            chain["width"] = float(np.clip(chain["width"] + d_width * 0.8,
                                           -WIDTH_CLAMP, WIDTH_CLAMP))
    finally:
        if os.path.exists(tmp_song):
            os.remove(tmp_song)
        shutil.rmtree(tmp, ignore_errors=True)

    _, bchain, bgot, bd_lufs, bband = best
    song["master"] = _master_fx(bchain)
    song["masterGainDb"] = 0.0
    json.dump(song, open(song_path, "w"), indent=1)
    receipt = {"ref": ref, "final": bgot, "d_lufs": round(bd_lufs, 2),
               "band_rms": round(bband, 2),
               "width_delta_db": round(ref["width_db"] - bgot["width_db"], 2),
               "chain": {k: round(v, 2) for k, v in bchain.items()},
               "replaced_master": old_master, "history": history}
    name = os.path.splitext(os.path.basename(song_path))[0]
    sd = os.path.join(SONGS, f"{name}_stems")
    if os.path.isdir(sd):
        json.dump(receipt, open(os.path.join(sd, "master_match.json"), "w"),
                  indent=1)
    say(f"[master] MATCHED: LUFS Δ{bd_lufs:+.2f} band_rms {bband:.2f}dB "
        f"chain {receipt['chain']} (old master: "
        f"{[f.get('id') for f in old_master]})")
    return receipt


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("song")
    ap.add_argument("--iters", type=int, default=4)
    a = ap.parse_args()
    import songname
    name = songname.resolve(a.song)
    path = os.path.join(SONGS, f"{name}.json")
    if not os.path.exists(path):
        sys.exit(f"no such song: {path}")
    match(path, iters=a.iters)


if __name__ == "__main__":
    main()
