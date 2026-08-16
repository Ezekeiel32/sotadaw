#!/usr/bin/env python3
"""THE DE-ESS TUNER — aim the de-esser at THIS voice's sibilance
(wave 42; R-12 item 129).

r-12: male sibilance centers 5-6kHz, female 7-8kHz, search band 4-10kHz
— a fixed default misses by a kHz either way. The tuner MEASURES the
sung stem: sibilant frames are where the 4-10kHz band carries the
frame's energy (fricative bursts); the center = the energy-weighted
centroid of those frames. court+heal: an fx_deess aimed >1.5kHz off the
measured center re-aims; a sibilant-heavy stem with NO de-esser gets
the chain-order advisory (deess sits AFTER compression, r-12 topology).

  sibilant_center(wav)   -> {center_hz, sibilant_frames, frac}
  court_deess(song, wav) -> verdict + heal-ready measurement
  heal_deess(song, verdict) -> re-aim / insert fx_deess on vocal lanes
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

S_LO, S_HI = 4000.0, 10000.0
AIM_TOL_HZ = 1500.0
SIB_FRAC_ADVISE = 0.12       # stem-time share that reads sibilant


def sibilant_center(wav_or_arr, sr=None):
    import soundfile as sf
    if isinstance(wav_or_arr, str):
        x, sr = sf.read(wav_or_arr, always_2d=True, dtype="float64")
        mono = x.mean(axis=1)
    else:
        mono = np.asarray(wav_or_arr, dtype="float64")
        if mono.ndim > 1:
            mono = mono.mean(axis=1)
    n = len(mono)
    nfft = 2048
    if n < nfft * 4:
        return {"skipped": "too short"}
    win = np.hanning(nfft)
    freqs = np.fft.rfftfreq(nfft, 1.0 / sr)
    s_band = (freqs >= S_LO) & (freqs <= S_HI)
    full_rms = float(np.sqrt(np.mean(mono ** 2)) + 1e-12)
    centers, weights = [], []
    frames = sib = 0
    for i in range(0, n - nfft, nfft // 2):
        seg = mono[i:i + nfft]
        if float(np.sqrt(np.mean(seg ** 2))) < full_rms * 0.1:
            continue
        frames += 1
        spec = np.abs(np.fft.rfft(seg * win)) ** 2
        tot = float(spec[1:].sum()) or 1e-18
        s_e = float(spec[s_band].sum())
        if s_e / tot < 0.5:
            continue                     # not a fricative burst
        sib += 1
        centers.append(float((spec[s_band] * freqs[s_band]).sum() / s_e))
        weights.append(s_e)
    if sib < 4 or not frames:
        return {"skipped": "no sibilant frames", "frames": frames}
    c = float(np.average(centers, weights=weights))
    return {"center_hz": round(c, 1), "sibilant_frames": sib,
            "frac": round(sib / frames, 3)}


def _vocal_lanes(song):
    out = []
    for t in (song or {}).get("tracks", []) or []:
        if not isinstance(t, dict) or t.get("muted"):
            continue
        nm = str(t.get("name", "")).lower()
        if nm.endswith(("_sketch", "_identity")):
            continue
        if any(w in nm for w in ("vocal", "vox", "voice", "topline",
                                 "sing", "choir")):
            out.append(t)
    return out


def court_deess(song, vocal_wav):
    """Measure the stem; verdict the lanes' de-essers against it."""
    m = sibilant_center(vocal_wav)
    if m.get("skipped"):
        return {"court": "deess", "ok": True, "advisories": [],
                "skipped": m["skipped"]}
    lanes = _vocal_lanes(song)
    if not lanes:
        return {"court": "deess", "ok": True, "advisories": [],
                "skipped": "no vocal lane"}
    c = m["center_hz"]
    flags, advisories = [], []
    for t in lanes:
        de = next((f for f in t.get("fx") or []
                   if str(f.get("id")) == "fx_deess"), None)
        if de is None:
            if m["frac"] >= SIB_FRAC_ADVISE:
                advisories.append({
                    "kind": "no_deess", "track": t.get("name", "?"),
                    "center_hz": c,
                    "why": f"{m['frac']:.0%} of the sung stem reads "
                           f"sibilant (center {c:.0f}Hz) with no "
                           "de-esser — fx_deess belongs AFTER the "
                           "compressor (r-12 chain order)"})
            continue
        aimed = float((de.get("params") or {}).get("freq", 5500) or 5500)
        if abs(aimed - c) > AIM_TOL_HZ:
            flags.append({
                "kind": "deess_misaimed", "track": t.get("name", "?"),
                "aimed_hz": aimed, "center_hz": c,
                "why": f"{t.get('name', '?')}: fx_deess aims {aimed:.0f}Hz "
                       f"but THIS voice's sibilance centers {c:.0f}Hz "
                       f"(>{AIM_TOL_HZ:.0f}Hz off) — the esses walk past "
                       "the detector"})
    return {"court": "deess", "ok": not flags, "flags": flags,
            "advisories": advisories, "center_hz": c, "frac": m["frac"]}


def heal_deess(song, verdict):
    """Re-aim mis-aimed de-essers at the measured center. Mutates."""
    if verdict.get("ok", True):
        return []
    c = float(verdict.get("center_hz", 5500))
    edits = []
    by = {f["track"]: f for f in verdict.get("flags", [])}
    for t in _vocal_lanes(song):
        f = by.get(t.get("name", "?"))
        if not f:
            continue
        for fx in t.get("fx") or []:
            if str(fx.get("id")) == "fx_deess":
                old = (fx.get("params") or {}).get("freq")
                fx.setdefault("params", {})["freq"] = round(c, 1)
                edits.append({"track": f["track"], "kind": "deess_aim",
                              "from_hz": old, "to_hz": round(c, 1)})
    return edits


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="THE DE-ESS TUNER (wave 42)")
    ap.add_argument("song")
    ap.add_argument("vocal_wav")
    ap.add_argument("--heal", action="store_true")
    a = ap.parse_args()
    song = json.load(open(a.song))
    v = court_deess(song, a.vocal_wav)
    if a.heal and not v.get("ok", True):
        v["heals"] = heal_deess(song, v)
        if v["heals"]:
            json.dump(song, open(a.song, "w"), indent=1)
            v["saved"] = a.song
    print(json.dumps(v, indent=1))
