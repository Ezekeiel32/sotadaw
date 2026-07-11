#!/usr/bin/env python3
"""THE INSTRUMENT EAR (2026-07-11, Chezy live: "USER NEED TO BE ABLE TO CHOOSE
UPON CONVERSION IF THEY WANT THE ORIGINAL INSTRUMENTS IMPORT OR HAVE THE
SYSTEM PICK INSTS BASED ON EAR — AND THIS EAR NEEDS TO BE A MILLION PERCENT
ACCURATE!")

Given a stem and the lane's transcribed notes, pick the palette voice that IS
that sound. Accuracy comes from being CLOSED-LOOP, not clever:

  1. PRESCREEN — the stem snippet's footprint (the voice_spectrum ruler:
     5 band shares + centroid + sustain) against a REGISTER-TRUE table:
     every candidate measured at the lane's own register (bass/mid/high
     probe renders, built once on demand, merge-cached in
     eval/voice_spectrum_registers.json). Top-K survive.
  2. FINALS — each finalist RENDERS THE LANE'S ACTUAL NOTES through the real
     engine (m1, densest 8-beat window); its render is measured with the
     same ruler against the same window of the stem. The winner is the
     measured twin — the pick is proven on the material, never guessed
     from a table. Self-identification (render a known voice, the ear must
     name it) is the battery's law.

Every pick ships a receipt: winner, score, runners-up, and the measured WHY.
Fallback ladder: no engine/render failure -> prescreen-only pick, receipt
says so honestly.
"""
import json
import math
import os
import subprocess
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)

import numpy as np

M1 = os.path.join(ROOT, "app/build/m1_artefacts/Release/m1")
TABLE = os.path.join(ROOT, "eval/voice_spectrum_registers.json")
BANDS = (("low", 20, 120), ("lowmid", 120, 350), ("mid", 350, 2000),
         ("himid", 2000, 6000), ("high", 6000, 16000))
REGISTERS = {"bass": 40, "mid": 60, "high": 76}   # probe root per bucket

# the melodic palette the ear may pick from (the voice_spectrum universe)
CANDIDATES = ["acid303", "brass_stab", "clav_funk", "clean_chime_guitar",
              "ep_bright", "fmbell", "formant_vox", "guitar_grit",
              "hammond_organ", "harp", "jazz_piano", "kalimba", "keys_dark",
              "marimba", "organ_soul", "pad_motion", "pluck", "pluck2",
              "rhodes", "sax_section", "strings_disco", "strings_stacc",
              "supersaw", "supersaw_fat", "vibraphone", "vox_pad"]

# ROLE LINEUPS: an ear can't name a suspect that isn't in the lineup — a bass
# stem judged against a melodic-only lineup "picks" a vibraphone (measured
# live on opptical, 47Hz window). Each lane role gets its own suspects; the
# register table banks any new name on demand.
ROLE_CANDIDATES = {
    "bass": ["bass_warm", "chip_bass", "reese", "sub_808_slide", "sub_clean",
             "upright_bass", "acid303", "wobble"],
    "keys": ["jazz_piano", "rhodes", "ep_bright", "keys_dark", "organ_soul",
             "hammond_organ", "clav_funk", "vibraphone", "marimba"],
    "guitar": ["clean_chime_guitar", "guitar_grit", "fuzz_guitar",
               "highgain_guitar", "harp", "pluck", "pluck2"],
    "vocal": ["formant_vox", "vox_pad", "sax_section", "duduk", "flute_lead"],
    "melodic": CANDIDATES,
}


def _load_mono(path):
    import soundfile as sf
    y, sr = sf.read(path, always_2d=True, dtype="float64")
    return sr, y.mean(axis=1)


def footprint(x, sr):
    """The ruler: 5 band shares (%), spectral centroid, sustain ratio."""
    x = np.asarray(x, dtype=np.float64)
    if len(x) < 512:
        return None
    rms = float(np.sqrt(np.mean(x ** 2)))
    if rms < 1e-6:
        return None
    P = np.abs(np.fft.rfft(x)) ** 2
    fr = np.fft.rfftfreq(len(x), 1.0 / sr)
    aud = float(P[(fr >= 20) & (fr < 16000)].sum()) + 1e-12
    bands = {nm: round(100.0 * float(P[(fr >= lo) & (fr < hi)].sum()) / aud, 2)
             for nm, lo, hi in BANDS}
    centroid = float((fr * P).sum() / (P.sum() + 1e-12))
    # sustain: energy of the tail half vs the attack half, averaged over
    # 0.5s frames — separates pluck/pad families decisively
    fw = int(0.5 * sr)
    ratios = []
    for i in range(0, len(x) - fw, fw):
        seg = x[i:i + fw]
        a = float(np.sqrt(np.mean(seg[: fw // 2] ** 2)) + 1e-9)
        b = float(np.sqrt(np.mean(seg[fw // 2:] ** 2)) + 1e-9)
        ratios.append(min(4.0, b / a))
    sustain = round(float(np.median(ratios)) if ratios else 1.0, 3)
    return {"bands": bands, "centroid_hz": round(centroid),
            "sustain": sustain, "rms_db": round(20 * math.log10(rms), 1)}


def distance(fa, fb):
    """Measured distance between two footprints (smaller = same sound)."""
    d = sum(abs(fa["bands"][k] - fb["bands"][k]) for k, _, _ in BANDS) / 100.0
    d += 0.8 * abs(math.log2((fa["centroid_hz"] + 1) / (fb["centroid_hz"] + 1)))
    d += 0.5 * abs(fa.get("sustain", 1.0) - fb.get("sustain", 1.0))
    return round(d, 4)


LAST_RENDER_ERR = ""   # why the last probe render failed (never silent)


def _render_probe(voice, notes, bpm, tag):
    """Render `voice` playing `notes` solo through the real engine; return
    the wav path or None (LAST_RENDER_ERR says why). Caller cleans up.
    One bounded retry: probe renders are seconds long, and a busy box
    (parallel builds, live captures) can transiently kill one."""
    global LAST_RENDER_ERR
    if not os.path.exists(M1):
        LAST_RENDER_ERR = "m1 binary missing"
        return None
    end = max(n["start"] + n["len"] for n in notes)
    song = {"bpm": float(bpm), "lengthBars": int(end // 4) + 2,
            "masterGainDb": 0.0,
            "tracks": [{"name": "probe", "source": {"kind": "faust", "id": voice},
                        "gainDb": -6.0, "pan": 0.0, "notes": notes}]}
    pj = os.path.join(ROOT, "songs", f"_earprobe_{tag}.json")
    pw = pj.replace(".json", ".wav")
    json.dump(song, open(pj, "w"))
    try:
        for attempt in (1, 2):
            try:
                r = subprocess.run([M1, "render", pj, pw], capture_output=True,
                                   cwd=ROOT, timeout=180)
            except Exception as e:
                LAST_RENDER_ERR = f"{type(e).__name__}: {e}"
                continue
            if r.returncode == 0 and os.path.exists(pw):
                LAST_RENDER_ERR = ""
                return pw
            LAST_RENDER_ERR = (f"rc={r.returncode} "
                               + (r.stderr or r.stdout or b"").decode(
                                   "utf-8", "replace").strip()[-160:])
        return None
    finally:
        if os.path.exists(pj):
            os.remove(pj)


def _register_of(notes):
    med = float(np.median([n["pitch"] for n in notes]))
    if med < 52:
        return "bass"
    if med > 70:
        return "high"
    return "mid"


def _table():
    if os.path.exists(TABLE):
        try:
            return json.load(open(TABLE))
        except Exception:
            pass
    return {}


def _bank_voice(voice, register, table):
    """Measure a candidate at a register (probe render), merge-cache."""
    root = REGISTERS[register]
    notes = [{"start": float(b * 4), "len": 3.9, "pitch": p, "vel": 0.6}
             for b in range(2) for p in (root, root + 4, root + 7)]
    pw = _render_probe(voice, notes, 100.0, f"bank_{voice}_{register}")
    if pw is None:
        return None
    try:
        sr, x = _load_mono(pw)
        fp = footprint(x, sr)
    finally:
        os.remove(pw)
    if fp is None:
        return None
    table.setdefault(voice, {})[register] = fp
    tmp = TABLE + ".tmp"
    json.dump(table, open(tmp, "w"), indent=1, sort_keys=True)
    os.replace(tmp, TABLE)
    return fp


def _densest_window(notes, beats=8.0):
    """Start beat of the busiest window (the lane's most representative bars)."""
    starts = sorted(n["start"] for n in notes)
    best, best_n = starts[0], 0
    for s in starts:
        n = sum(1 for x in starts if s <= x < s + beats)
        if n > best_n:
            best, best_n = s, n
    return best


def pick_voice(stem_wav, notes, bpm, candidates=None, topk=3, finals=True,
               role=None, log=lambda s: None):
    """The ear. Returns {"voice", "score", "mode", "ranked", "why"} or None
    when the stem window is silent/unreadable."""
    cands = candidates or ROLE_CANDIDATES.get(role or "", CANDIDATES)
    notes = [n for n in notes if n.get("len", 0) > 0]
    if not notes:
        return None
    w0 = _densest_window(notes)
    w1 = w0 + 8.0
    spb = 60.0 / float(bpm)
    sr, x = _load_mono(stem_wav)
    a, b = int(w0 * spb * sr), min(len(x), int(w1 * spb * sr))
    target = footprint(x[a:b], sr)
    if target is None:
        return None
    register = _register_of(notes)
    table = _table()
    ranked = []
    for v in cands:
        fp = (table.get(v) or {}).get(register)
        if fp is None:
            fp = _bank_voice(v, register, table)
            if fp is None:
                continue
        ranked.append((distance(target, fp), v))
    if not ranked:
        return None
    ranked.sort()
    mode = "prescreen"
    win = [{"start": round(n["start"] - w0, 4), "len": round(min(n["len"], 8.0), 4),
            "pitch": int(n["pitch"]), "vel": float(n.get("vel", 0.8))}
           for n in notes if w0 <= n["start"] < w1][:32]
    if finals and win and os.path.exists(M1):
        # MILLION-PERCENT LAW: for role lineups (<=12 suspects) EVERY candidate
        # auditions on the lane's own notes — prescreen can starve the true
        # voice out of a top-3 (rhodes lost to jazz_piano when the triad table
        # met a melody window). Prescreen only trims the big melodic universe.
        n_finals = len(ranked) if len(ranked) <= 12 else max(topk, 6)
        finals_ranked = []
        for _, v in ranked[:n_finals]:
            pw = _render_probe(v, win, bpm, f"final_{v}")
            if pw is None:
                continue
            try:
                psr, px = _load_mono(pw)
                pfp = footprint(px, psr)
            finally:
                os.remove(pw)
            if pfp is not None:
                finals_ranked.append((distance(target, pfp), v))
                log(f"[ear] finals: {v} d={finals_ranked[-1][0]}")
        if finals_ranked:
            finals_ranked.sort()
            ranked = finals_ranked + [r for r in ranked
                                      if r[1] not in {v for _, v in finals_ranked}]
            mode = "closed-loop"
    score, voice = ranked[0]
    fp_win = (table.get(voice) or {}).get(register, {})
    why = (f"{mode}: stem window {w0:g}-{w1:g}b centroid "
           f"{target['centroid_hz']}Hz sustain {target['sustain']} -> "
           f"{voice} d={score}"
           + (f" (runner-up {ranked[1][1]} d={ranked[1][0]})"
              if len(ranked) > 1 else ""))
    return {"voice": voice, "score": score, "mode": mode, "register": register,
            "ranked": [[d, v] for d, v in ranked[:5]], "why": why,
            "target": target, "picked_fp": fp_win}


# ---------------------------------------------------------------- CLI
def main(argv):
    import argparse
    ap = argparse.ArgumentParser(description="Pick the palette voice that IS "
                                 "a stem's sound (receipted).")
    ap.add_argument("stem")
    ap.add_argument("notes", help="json file with a notes[] list, or a "
                    "song.json track name via --track")
    ap.add_argument("--track", default=None)
    ap.add_argument("--bpm", type=float, required=True)
    ap.add_argument("--role", default=None, choices=sorted(ROLE_CANDIDATES))
    ap.add_argument("--no-finals", action="store_true")
    a = ap.parse_args(argv)
    doc = json.load(open(a.notes))
    notes = doc if isinstance(doc, list) else None
    if notes is None:
        if a.track:
            t = next(t for t in doc["tracks"] if t.get("name") == a.track)
            notes = t["notes"]
        else:
            notes = doc.get("notes") or []
    r = pick_voice(a.stem, notes, a.bpm, finals=not a.no_finals, role=a.role,
                   log=lambda s: print(s, flush=True))
    if r is None:
        print("[ear] stem window silent/unreadable — no pick")
        return 1
    print(f"[ear] PICK: {r['voice']} ({r['mode']}, d={r['score']})")
    print(f"[ear] {r['why']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
