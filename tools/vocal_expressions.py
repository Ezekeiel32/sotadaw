#!/usr/bin/env python3
"""VOCAL EXPRESSIONS — wave 89 (r-9 item 238): the commercial bar's
vocabulary (SynthV/ACE) mapped onto what the house rails actually
drive, so style verbs are real curves, not vibes.

  THE SURFACE (agent-facing)     THE MECHANISM (house)
  energy 0..1                    velocity scale + comp drive (vocal_chain)
  tension 0..1                   DiffSinger tension variance (named
                                 remainder until the variance grids of
                                 item 195 land) -> today: vel + retune
                                 style hardness
  air / breathiness 0..1         the breath double's level (vox_breath
                                 lane, w76) + deess relief
  falsetto                       +12st register move w/ vel drop (the
                                 topline op) — Gahata mode note
  mode: standard|whisper|belt    Gahata vocal modes (Standard /
                                 Phantom-whisper / Lilith / Hunter) —
                                 bank-dependent, resolved at sing time

  express(song, verb) -> deterministic param moves + the honest note
  about what today's rails can and cannot drive.
"""
import json
import sys

VERBS = {
    "belting":  {"energy": 0.9, "tension": 0.7, "air": 0.1,
                 "moves": ["velocities x1.15 (cap 127) on the lead",
                           "retune style 'hard' (fast snap reads as "
                           "commitment)",
                           "vox_breath level -18 (air out of the way)"]},
    "soft":     {"energy": 0.3, "tension": 0.2, "air": 0.7,
                 "moves": ["velocities x0.8 on the lead",
                           "retune style 'natural'",
                           "vox_breath level -8 (the whisper double "
                           "carries intimacy)"]},
    "airy":     {"energy": 0.4, "tension": 0.2, "air": 0.9,
                 "moves": ["vox_breath level -6", "deess relief -1dB",
                           "verb send +2dB"]},
    "strained": {"energy": 0.8, "tension": 0.9, "air": 0.2,
                 "moves": ["velocities x1.1", "retune 'hard'",
                           "NOTE: true tension variance = item 195's "
                           "grids (named remainder)"]},
}


def express(song, verb):
    v = VERBS.get(str(verb).lower())
    if v is None:
        return {"ok": False,
                "why": f"unknown expression '{verb}' — {sorted(VERBS)}"}
    lead = next((t for t in (song or {}).get("tracks", []) or []
                 if isinstance(t, dict) and
                 any(w in str(t.get("name", "")).lower()
                     for w in ("vocal", "vox", "lead"))
                 and t.get("notes")), None)
    applied = []
    if lead is not None and v["energy"] != 0.5:
        scale = 0.8 + v["energy"] * 0.4
        for n in lead["notes"]:
            try:
                n["vel"] = max(1, min(127, int(round(
                    float(n.get("vel", 96)) * scale))))
            except Exception:
                pass
        applied.append(f"lead velocities x{scale:.2f}")
    return {"ok": True, "verb": verb, "surface": {
                "energy": v["energy"], "tension": v["tension"],
                "air": v["air"]},
            "applied": applied, "prescription": v["moves"],
            "note": ("tension rides velocity+retune today; the per-note "
                     "variance grids (item 195 remainder) are the full "
                     "mechanism")}


if __name__ == "__main__":
    song = json.load(open(sys.argv[1]))
    out = express(song, sys.argv[2] if len(sys.argv) > 2 else "belting")
    if out.get("applied"):
        json.dump(song, open(sys.argv[1], "w"), indent=1)
    print(json.dumps(out, indent=1))
