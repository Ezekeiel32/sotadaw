#!/usr/bin/env python3
"""W15d — THE TIMBRE MAP: measure the voice space ONCE, search it forever.

timbre_map.py [--force]

Renders a fixed 6-note probe phrase through every catalogued blend of the four
voice embeds (pures, 50/50 pairs, 70/30 leans), measures each render with the ears
(centroid, band tilt, high-air ratio, rms), and caches the map to
library/voices/timbre_map.json. voice_design.py then searches this map INSTANTLY —
no rendering, no black box: every judgment is a number you can re-measure.
"""
import itertools, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import sing  # noqa: E402
from analyze2 import analyze  # noqa: E402

OUT = os.path.join(ROOT, "library", "voices", "timbre_map.json")
EMBEDS = ["standard", "hunter", "lilith", "phantom"]
PROBE = [  # A3 D4 C4 E4 B3 A3 — spans the alto/mezzo range, mixed intervals
    {"start": 0.0, "len": 0.9, "pitch": 57, "vel": 0.8},
    {"start": 1.0, "len": 0.9, "pitch": 62, "vel": 0.8},
    {"start": 2.0, "len": 0.9, "pitch": 60, "vel": 0.8},
    {"start": 3.0, "len": 0.9, "pitch": 64, "vel": 0.8},
    {"start": 4.0, "len": 0.9, "pitch": 59, "vel": 0.8},
    {"start": 5.0, "len": 1.4, "pitch": 57, "vel": 0.8},
]


def blends():
    out = [(e, e) for e in EMBEDS]                                   # pures
    for a, b in itertools.combinations(EMBEDS, 2):                   # 50/50 pairs
        out.append((f"{a}:0.5,{b}:0.5", f"{a}+{b}"))
    for a, b in itertools.permutations(EMBEDS, 2):                   # 70/30 leans (adjacent chars)
        if EMBEDS.index(a) < EMBEDS.index(b):
            out.append((f"{a}:0.7,{b}:0.3", f"{a}~{b}"))
    return out


def features(wav):
    m = analyze(wav)
    b = m["band_energy_pct"]
    body = b["lowmid_120_500"] + b["mid_500_2k"]
    air = b["himid_2k_6k"] + b["high_6k_up"]
    return {"centroid_hz": m["spectral_centroid_hz"],
            "air_pct": round(air, 2), "body_pct": round(body, 2),
            "tilt": round(air / max(body, 1e-3), 4),   # >: brighter/airier, <: darker/huskier
            "rms_db": m["rms_db"]}


def main():
    force = "--force" in sys.argv
    if os.path.exists(OUT) and not force:
        print(f"map exists ({OUT}) — use --force to re-measure")
        return
    rows = []
    for emb, label in blends():
        tmp_name = "_timbre_probe"
        tmp = {"version": 2, "bpm": 90, "key": "A minor", "lengthBars": 2,
               "tracks": [{"name": "probe", "source": {"kind": "faust", "id": "pluck"},
                           "gainDb": -60, "notes": PROBE}]}
        json.dump(tmp, open(os.path.join(ROOT, "songs", f"{tmp_name}.json"), "w"), indent=1)
        sing.hum(tmp_name, "probe", "laa", emb)
        wav = os.path.join(ROOT, "songs", f"{tmp_name}_vocal.wav")
        if not os.path.exists(wav):
            print(f"  {label}: RENDER FAILED — skipped")
            continue
        f = features(wav)
        rows.append({"embed": emb, "label": label, **f})
        print(f"  {label:22} centroid {f['centroid_hz']:>5}  tilt {f['tilt']:.3f}  air {f['air_pct']}%")
        os.remove(wav)
    for scratch in ("_timbre_probe.json",):
        p = os.path.join(ROOT, "songs", scratch)
        os.path.exists(p) and os.remove(p)
    json.dump({"probe": "A3-D4-C4-E4-B3-A3 laa @90bpm", "voices": rows},
              open(OUT, "w"), indent=1)
    print(f"timbre map: {len(rows)} blends -> {OUT}")


if __name__ == "__main__":
    main()
