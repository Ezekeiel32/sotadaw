#!/usr/bin/env python3
"""THE MASKING COURT — who is burying whom (wave 21; R-6 items
052/053/054).

AUDIO SIDE (item 052, the validated MSR court): per stem, the masker is
the SUM of all other stems. Masking threshold via the Schroeder
spreading function over masker peaks — ASYMMETRIC and the asymmetry is
load-bearing (r-6 f6: the gentle ~-10dB/Bark slope faces the HIGH side,
upward spread of masking; steep ~-25dB/Bark faces low). dB SPL mapping
96+20log10(|X|*2/N); absolute threshold = Terhardt Tq. Bands stay FINE
LINEAR, never 24-Bark (r-6 f7: linear bands predict clarity at rho
-0.838 vs -0.688 — HF masking carries more weight than Bark implies).

Verdict grades (the r-6 deliverable): per-band MSR GREEN<=0 <AMBER<=6
<RED<=12 <SEVERE; per-stem NormalizedMask GREEN<0.15 AMBER<0.30 RED>=.
TIME-PERSISTENCE GATE: a band is a fixable collision only when MSR>6dB
in >30% of frames where BOTH stems are active — momentary overlaps are
music, not crimes.

HEAL (item 053) is SOURCE-FIRST, EQ-LAST, bounded:
  (1) REGISTER — collision centers within ~1 Bark persistent -> a
      re-voicing RECIPE (advisory; auto-octaving melodies rewrites the
      music, so the arranger applies it, not the court)
  (2) LEVEL — bounded -2dB gain on the masker lane
  (3) PAN — separate near-center pairs by +-0.2
  (4) STATIC EQ LAST — fx_bell cut on the MASKER at the collision
      center, depth clip(MSR,0,6)dB, q=2, <=3 bells and <=6dB total per
      lane. Over-unmasking makes mixes thin (r-6 f8): the e2e requires
      the re-render to LOWER NormalizedMask without raising the maskee's
      centroid/energy beyond a small bound. NEVER per-proposal — the
      stems court is the ON-DEMAND lane.

SYMBOLIC SIDE (item 054, the DAW's structural advantage): masking is
PREVENTED at compose time — simultaneous notes on different melodic
lanes within ~1 Bark at comparable velocity, persistently, draw an
advisory carrying the r-6 f10 register-allocation map (sub 20-60, bass
60-250, keep 250-500 mud thin, vocals own 2-5k). Advisory-only: overlap
is also unison/doubling, a real idiom.
"""
import json
import re
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

MSR_AMBER, MSR_RED, MSR_SEVERE = 0.0, 6.0, 12.0
MASK_AMBER, MASK_RED = 0.15, 0.30
PERSIST_FRAC = 0.30
DOWNSHIFT_DB = 14.0
EQ_MAX_DB, EQ_MAX_BELLS = 6.0, 3


def bark(f):
    f = np.asarray(f, dtype="float64")
    return 13.0 * np.arctan(0.00076 * f) + \
        3.5 * np.arctan((f / 7500.0) ** 2)


def terhardt_tq_db(f):
    f = np.asarray(f, dtype="float64") + 1e-6
    k = f / 1000.0
    return (3.64 * k ** -0.8 - 6.5 * np.exp(-0.6 * (k - 3.3) ** 2)
            + 1e-3 * k ** 4)


def schroeder_spread(dz):
    """Masking level drop (dB, <=0 shape around the peak) at bark
    distance dz = z_maskee - z_masker. Asymmetric: gentle on +dz."""
    dz = np.asarray(dz, dtype="float64")
    return (15.81 + 7.5 * (dz + 0.474)
            - 17.5 * np.sqrt(1.0 + (dz + 0.474) ** 2))


def _stft_db(x, sr, nfft=4096):
    win = np.hanning(nfft)
    frames = []
    for i in range(0, len(x) - nfft, nfft // 2):
        spec = np.abs(np.fft.rfft(x[i:i + nfft] * win))
        frames.append(96.0 + 20.0 * np.log10(spec * 2.0 / nfft + 1e-12))
    freqs = np.fft.rfftfreq(nfft, 1.0 / sr)
    return (np.array(frames) if frames else np.zeros((0, nfft // 2 + 1)),
            freqs)


def masking_threshold_db(masker_frame_db, freqs, zs, top_k=24):
    """MT per bin: max over the masker's top spectral peaks spread with
    Schroeder, minus the standard ~14dB downshift, floored by Tq."""
    mt = terhardt_tq_db(freqs).copy()
    m = masker_frame_db
    if len(m) > 2:
        peaks = np.where((m[1:-1] > m[:-2]) & (m[1:-1] >= m[2:]))[0] + 1
        if len(peaks):
            top = peaks[np.argsort(m[peaks])[-top_k:]]
            for p in top:
                lv = m[p] - DOWNSHIFT_DB
                if lv < 0:
                    continue
                mt = np.maximum(mt, lv + schroeder_spread(zs - zs[p])
                                - 15.81)
    return mt


def msr_pair(target, masker, sr, nfft=4096):
    """Per-band MSR stats for one (target, masker-sum) pair.
    Returns {mask_norm, red_bands: [{hz, msr_db, persist}], frames}."""
    T, freqs = _stft_db(target, sr, nfft)
    M, _ = _stft_db(masker, sr, nfft)
    n = min(len(T), len(M))
    if n < 4:
        return {"mask_norm": 0.0, "red_bands": [], "frames": 0}
    zs = bark(freqs)
    tq = terhardt_tq_db(freqs)
    # group bins into fine linear bands (~86Hz at 44k1/512) above bin 2
    band_w = 8
    nb = (len(freqs) - 2) // band_w
    msr_hits = np.zeros((n, nb))
    active = np.zeros((n, nb), dtype=bool)
    norm_scores = []
    for i in range(n):
        mt = masking_threshold_db(M[i], freqs, zs)
        e = T[i]
        # SELF-MASKING WITNESS LAW (battery-caught 2026-07-15): the
        # window-leakage skirts of the target's own peak are 'audible'
        # above Tq yet are NOT independent content — a bin testifies
        # only when it clears the target's OWN spreading threshold.
        mt_self = masking_threshold_db(e, freqs, zs)
        audible = (e > tq + 3.0) & (e >= mt_self - 3.0)
        msr = mt - e
        both = audible & (mt > tq + 3.0)
        if both.any():
            norm_scores.append(float(np.mean(
                np.clip(msr[both], 0.0, 20.0) / 20.0)))
        for b in range(nb):
            sl = slice(2 + b * band_w, 2 + (b + 1) * band_w)
            if audible[sl].any():
                active[i, b] = True
                msr_hits[i, b] = float(np.max(msr[sl]))
    red_bands = []
    for b in range(nb):
        act = active[:, b]
        if act.sum() < max(4, n * 0.1):
            continue
        persist = float((msr_hits[act, b] > MSR_RED).mean())
        if persist > PERSIST_FRAC:
            sl = slice(2 + b * band_w, 2 + (b + 1) * band_w)
            red_bands.append({
                "hz": round(float(freqs[sl].mean()), 1),
                "msr_db": round(float(np.median(
                    msr_hits[act, b][msr_hits[act, b] > MSR_RED])), 1),
                "persist": round(persist, 2)})
    red_bands.sort(key=lambda r: -r["msr_db"])
    return {"mask_norm": round(float(np.mean(norm_scores)), 3)
            if norm_scores else 0.0,
            "red_bands": red_bands[:6], "frames": n}


def court_masking_stems(stems_dir, genre=""):
    """Item 052: every stem vs the sum of the others. ON-DEMAND lane —
    never per-proposal."""
    import soundfile as sf
    stems = {}
    for f in sorted(os.listdir(stems_dir)):
        if not f.endswith(".wav"):
            continue
        x, sr = sf.read(os.path.join(stems_dir, f), always_2d=True,
                        dtype="float64")
        m = x.mean(axis=1)
        if float(np.sqrt(np.mean(m ** 2))) > 1e-5:
            stems[f[:-4]] = (m, sr)
    if len(stems) < 2:
        return {"court": "masking", "ok": True,
                "skipped": "needs >=2 sounding stems"}
    names = list(stems)
    n_min = min(len(v[0]) for v in stems.values())
    sr = stems[names[0]][1]
    flags, advisories, per_stem = [], [], {}
    for name in names:
        target = stems[name][0][:n_min]
        masker = np.sum([stems[o][0][:n_min] for o in names if o != name],
                        axis=0)
        r = msr_pair(target, masker, sr)
        per_stem[name] = r
        grade = ("RED" if r["mask_norm"] >= MASK_RED else
                 "AMBER" if r["mask_norm"] >= MASK_AMBER else "GREEN")
        if grade == "RED" and r["red_bands"]:
            flags.append({
                "kind": "masked_stem", "track": name,
                "mask_norm": r["mask_norm"],
                "bands": r["red_bands"][:3],
                "why": f"{name}: NormalizedMask {r['mask_norm']:.2f} "
                       f">= {MASK_RED} — persistently buried at "
                       + ", ".join(f"{b['hz']:.0f}Hz ({b['msr_db']:.0f}dB, "
                                   f"{b['persist']:.0%} of active frames)"
                                   for b in r["red_bands"][:3])})
        elif grade == "AMBER":
            advisories.append({
                "kind": "crowded_stem", "track": name,
                "mask_norm": r["mask_norm"],
                "why": f"{name}: NormalizedMask {r['mask_norm']:.2f} — "
                       "crowded but audible"})
    return {"court": "masking", "ok": not flags, "flags": flags,
            "advisories": advisories,
            "per_stem": {k: v["mask_norm"] for k, v in per_stem.items()}}


# ------------------------------------------------ item 053 the heal ladder
def _dominant_masker(stems_dir, maskee, band_hz):
    """Which other stem carries the most energy at the collision band."""
    import soundfile as sf
    best, best_e = None, -1.0
    for f in sorted(os.listdir(stems_dir)):
        if not f.endswith(".wav") or f[:-4] == maskee:
            continue
        x, sr = sf.read(os.path.join(stems_dir, f), always_2d=True,
                        dtype="float64")
        m = x.mean(axis=1)
        n = len(m) // 2 * 2
        if n < sr // 4:
            continue
        spec = np.abs(np.fft.rfft(m[:n])) ** 2
        freqs = np.fft.rfftfreq(n, 1.0 / sr)
        sel = (freqs > band_hz * 0.8) & (freqs < band_hz * 1.25)
        e = float(spec[sel].sum())
        if e > best_e:
            best, best_e = f[:-4], e
    return best


def heal_masking(song, verdict, stems_dir=None):
    """The bounded SOURCE-FIRST ladder on the MASKER lane. Mutates song;
    returns edit ledger. Register moves stay RECIPES (rewriting melodies
    is the arranger's power, not the court's)."""
    if verdict.get("ok", True) or not verdict.get("flags"):
        return []
    by_name = {}
    for t in (song or {}).get("tracks", []) or []:
        if isinstance(t, dict):
            by_name[str(t.get("name", ""))] = t
    edits = []
    for f in verdict.get("flags", []):
        if f.get("kind") != "masked_stem" or not f.get("bands"):
            continue
        maskee = f["track"]
        # stem names carry m1's index prefix (00_kick) — resolve loosely
        def find(name):
            if name in by_name:
                return by_name[name]
            base = name.split("_", 1)[-1]
            return by_name.get(base) or next(
                (t for k, t in by_name.items() if base and base in k), None)
        band = f["bands"][0]
        masker_name = _dominant_masker(stems_dir, maskee, band["hz"]) \
            if stems_dir else None
        mt = find(masker_name) if masker_name else None
        if mt is None:
            continue
        # rung 2: LEVEL (bounded -2dB on the masker)
        old_g = float(mt.get("gainDb", 0) or 0)
        mt["gainDb"] = round(old_g - 2.0, 1)
        edits.append({"kind": "level", "track": masker_name,
                      "old": old_g, "new": mt["gainDb"]})
        # rung 3: PAN separation when both sit near center
        me = find(maskee)
        if me is not None:
            p_m = float(mt.get("pan", 0) or 0)
            p_e = float(me.get("pan", 0) or 0)
            low_band = band["hz"] < 200.0
            if abs(p_m) < 0.1 and abs(p_e) < 0.1 and not low_band:
                mt["pan"] = -0.2
                me["pan"] = 0.2
                edits.append({"kind": "pan_split", "masker": masker_name,
                              "maskee": maskee})
        # rung 4: STATIC EQ LAST — fx_bell cut at the collision center
        fx = mt.setdefault("fx", [])
        bells = [x for x in fx if str(x.get("id")) == "fx_bell"]
        spent = sum(abs(float((x.get("params") or {}).get("gain", 0)))
                    for x in bells)
        for b in f["bands"][:EQ_MAX_BELLS]:
            if len(bells) >= EQ_MAX_BELLS or spent >= EQ_MAX_DB:
                break
            depth = min(max(float(b["msr_db"]), 0.0), 6.0,
                        EQ_MAX_DB - spent)
            if depth < 1.0:
                continue
            bell = {"id": "fx_bell",
                    "params": {"freq": round(float(b["hz"]), 1),
                               "gain": round(-depth, 1), "q": 2.0}}
            fx.insert(0, bell)
            bells.append(bell)
            spent += depth
            edits.append({"kind": "bell_cut", "track": masker_name,
                          "hz": bell["params"]["freq"],
                          "gain": bell["params"]["gain"]})
    return edits


# ---------------------------------------------- item 054 compose-time law
_BROADBAND = ("kick", "snare", "hat", "perc", "drum", "clap", "cym",
              "crash", "ride", "shaker", "fx", "riser", "impact")
REGISTER_MAP = ("r-6 f10 allocation: sub 20-60Hz, bass 60-250, keep the "
                "250-500 mud zone thin, vocals/leads own 2-5k presence")


def _hz(pitch):
    return 440.0 * 2 ** ((float(pitch) - 69) / 12.0)


def court_compose_masking(song, genre=""):
    """Item 054: PREVENT masking before any render. THE CORPUS REWROTE
    THIS COURT (2026-07-15): pair-wise 1-Bark collision flagged 95/222
    songs incl. 11/21 EVAL WINNERS — pad+strings, guitar+guitar,
    bass+organ are the LAYERING VOCABULARY of real arrangement, not
    crimes. What ground truth never does: pile FOUR+ melodic lanes into
    the 250-500Hz MUD ZONE persistently (crate 0/8, eval 0/21 at >=4;
    the organ forms legitimately hold three). Advisory-only."""
    lanes = []
    for t in (song or {}).get("tracks", []) or []:
        if not isinstance(t, dict) or t.get("muted"):
            continue
        nm = str(t.get("name", "")).lower()
        if any(w in nm for w in _BROADBAND) or nm.endswith("_sketch"):
            continue
        notes = sorted((n for n in t.get("notes") or []
                        if isinstance(n, dict)),
                       key=lambda n: float(n.get("start", 0)))
        if len(notes) >= 4:
            lanes.append((t.get("name", "?"), notes))
    if len(lanes) < 4:
        return {"court": "compose_masking", "ok": True, "advisories": []}
    beats = int(float(song.get("lengthBars", 8) or 8) * 4)
    crowded, names_hits = 0, {}
    checked = 0
    for b in range(0, min(beats, 512)):
        t_beat = b + 0.01
        here = []
        for name, notes in lanes:
            for n in notes:
                s = float(n.get("start", 0))
                if s > t_beat:
                    break
                if s <= t_beat < s + float(n.get("len", 0.25)) and \
                        250.0 <= _hz(n.get("pitch", 60)) <= 500.0:
                    here.append(name)
                    break
        checked += 1
        if len(here) >= 4:
            crowded += 1
            for nm in here:
                names_hits[nm] = names_hits.get(nm, 0) + 1
    advisories = []
    if checked and crowded / checked > 0.3:
        top = sorted(names_hits, key=names_hits.get, reverse=True)[:5]
        advisories.append({
            "kind": "mud_crowding",
            "tracks": top, "frac": round(crowded / checked, 2),
            "why": f"{len(top)}+ melodic lanes ({', '.join(top)}) sustain "
                   f"inside 250-500Hz on {crowded / checked:.0%} of beats "
                   "— the mud zone is the single most common masking "
                   f"trap; thin it ({REGISTER_MAP})"})
    return {"court": "compose_masking", "ok": True,
            "advisories": advisories}


def main():
    import argparse
    ap = argparse.ArgumentParser(description="THE MASKING COURT (wave 21)")
    ap.add_argument("target", help="stems dir (audio court) or song.json "
                                   "(compose court)")
    ap.add_argument("--song", default=None)
    ap.add_argument("--genre", default="")
    ap.add_argument("--heal", action="store_true")
    args = ap.parse_args()
    if os.path.isdir(args.target):
        v = court_masking_stems(args.target, args.genre)
        if args.heal and args.song:
            song = json.load(open(args.song))
            v["heals"] = heal_masking(song, v, args.target)
            if v["heals"]:
                json.dump(song, open(args.song, "w"), indent=1)
                v["saved"] = args.song
    else:
        v = court_compose_masking(json.load(open(args.target)), args.genre)
    print(json.dumps(v, indent=1))
    return 0 if v.get("ok", True) else 1


if __name__ == "__main__":
    sys.exit(main())
