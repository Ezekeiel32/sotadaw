#!/usr/bin/env python3
"""W15d VOICE DESIGN FROM DESCRIPTION — embed-space search, acoustically judged.

voice_design.py "<description>" [--fast]

The four voicebank embeds are a timbre space; blends mint new singers for free
(sing.py mixes raw 384-float vectors). This searches that space: candidate blends
each sing a short fixed phrase, the EARS measure them (centroid = brightness,
lowmid share = weight/huskiness, high share = air), and the description's target
wins by distance. Deterministic, interpretable, zero new models — the winner is a
blend string you paste straight into choir.py --stack.

Descriptions understood (composable): dark/warm/bright/airy, light/husky/heavy,
low/mid/high (register of the test phrase).
"""
import argparse, itertools, json, os, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import sing  # noqa: E402
from analyze2 import analyze  # noqa: E402

EMBEDS = ["standard", "hunter", "lilith", "phantom"]


def targets_from(desc):
    """DIRECTIONS, not anchors: 'dark' = darkest AVAILABLE blend (z-scored across
    candidates) — absolute targets were fantasy against a real sung register."""
    d = desc.lower()
    w = {"centroid": 0.0, "lowmid": 0.0, "high": 0.0}
    if "dark" in d or "husky" in d:  w["centroid"] -= 1.0
    if "warm" in d:                  w["centroid"] -= 0.5
    if "bright" in d:                w["centroid"] += 1.0
    if "airy" in d:                  w["high"] += 1.0
    if "clean" in d:                 w["high"] -= 0.5
    if "husky" in d or "heavy" in d: w["lowmid"] += 1.0
    if "light" in d:                 w["lowmid"] -= 1.0
    root = 57 if ("low" in d or "alto" in d) else (69 if "high" in d or "soprano" in d else 63)
    return w, root


def candidates(fast):
    cands = [(e, None, 1.0) for e in EMBEDS]                       # pures
    for a, b in itertools.combinations(EMBEDS, 2):                  # pairs
        for w in ((0.5,) if fast else (0.3, 0.5, 0.7)):
            cands.append((a, b, w))
    return cands


def blend_str(a, b, w):
    return a if b is None else f"{a}:{round(w,2)},{b}:{round(1-w,2)}"


def sing_candidate(blend, root):
    """5-note phrase -> temp song -> DiffSinger -> analyze. Returns ears dict."""
    notes = [{"start": i * 0.9, "len": 0.8, "pitch": p, "vel": 0.8}
             for i, p in enumerate((root, root + 3, root + 5, root + 3, root))]
    tmp = {"version": 2, "bpm": 120, "key": "C minor", "lengthBars": 2,
           "tracks": [{"name": "probe", "source": {"kind": "faust", "id": "pluck"},
                       "gainDb": -60, "notes": notes}]}
    json.dump(tmp, open(os.path.join(ROOT, "songs", "_vdesign.json"), "w"), indent=1)
    sing.hum("_vdesign", "probe", "laa", blend)
    wav = os.path.join(ROOT, "songs", "_vdesign_vocal.wav")
    return analyze(wav) if os.path.exists(wav) else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("description")
    ap.add_argument("--fast", action="store_true", help="pures + 50/50 pairs only (10 renders)")
    a = ap.parse_args()
    wants, root = targets_from(a.description)
    print(f"[voice_design] '{a.description}' -> directions {wants}, phrase root MIDI {root}")
    rows = []
    for (ea, eb, w) in candidates(a.fast):
        bs = blend_str(ea, eb, w)
        m = sing_candidate(bs, root)
        if not m:
            continue
        cen = float(m["spectral_centroid_hz"])
        lowmid = m["band_energy_pct"]["lowmid_120_500"] + m["band_energy_pct"]["mid_500_2k"] * 0.3
        high = m["band_energy_pct"]["high_6k_up"] + m["band_energy_pct"]["himid_2k_6k"] * 0.3
        rows.append([bs, cen, lowmid, high])
        print(f"  {bs:32} centroid {round(cen):5}  weight {round(lowmid,1):5}  air {round(high,1):4}")
    import statistics as st
    scored = []
    axes = {"centroid": 1, "lowmid": 2, "high": 3}
    stats = {k: (st.mean(r[i] for r in rows), max(st.pstdev(r[i] for r in rows), 1e-6))
             for k, i in axes.items()}
    for r in rows:
        score = sum(wants[k] * (r[axes[k]] - stats[k][0]) / stats[k][1] for k in axes)
        scored.append((round(-score, 3), r[0], round(r[1]), round(r[2], 1), round(r[3], 1)))
    for f in ("songs/_vdesign.json", "songs/_vdesign_vocal.wav"):
        p = os.path.join(ROOT, f)
        if os.path.exists(p):
            os.remove(p)
    scored.sort()
    print("[voice_design] WINNERS:")
    for d, bs, cen, lm, hi in scored[:3]:
        print(f"  {bs}   (dist {d}; centroid {cen}, weight {lm}, air {hi})")
    print(f'[voice_design] use it: choir.py ... --stack "lead={scored[0][1]}@0,..."')


if __name__ == "__main__":
    main()
