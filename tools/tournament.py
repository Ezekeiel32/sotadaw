#!/usr/bin/env python3
"""THE TOURNAMENT kernel (A3-T1, docs/SPEC_TRANSCENDENCE.md).

Every zero-token MAKE becomes a SEARCH: K candidate takes fan out from
derived seeds, the symbolic courts are the bracket, the machine picks the
winner, and only the winner rides the (unchanged) downstream pipeline —
vocals, heals, loudness pass, wall, render.

LAWS:
- INCUMBENT LAW: candidate 0 is the REQUESTED seed's take; ties go to the
  incumbent, so an explicit seed keeps its take unless a sibling BEATS it
  on court evidence.
- SEED LAW: sibling seeds derive deterministically from the request's seed
  — same request, same K candidates, same winner (byte-reproducible).
- DQ class: an off-key take or a take violating the user's explicit
  constitution NEVER wins over a clean one (hard courts outrank counts).
- HONEST PODIUM: the pick explains itself (per-candidate one-liners); the
  losers are banked as preference pairs (telemetry/tournament.jsonl —
  DPOP-ready data, the taste circle's richest label).

Pure kernel: scoring takes an injectable courts callable so the battery
proves the bracket without heavy court imports.
"""
import json
import os
import time

# hard courts: a fail here disqualifies against any non-DQ sibling
_HARD = ("key", "constitution")
# advisory courts counted as penalties (missing court = no penalty)
_SOFT = ("pocket", "arc", "flow", "melody", "harmony", "structure",
         "tension", "lowend", "groove")


def derive_seeds(seed, k):
    """[requested seed, then k-1 deterministic siblings]. Stable forever —
    changing this function changes every historical podium, so don't."""
    seed = int(seed)
    out = [seed]
    s = seed & 0x7FFFFFFF
    for _ in range(max(0, k - 1)):
        s = (s * 1000003 + 40527) & 0x7FFFFFFF
        out.append(s)
    return out


def _default_courts(doc, genre):
    import music_court
    return music_court.run_courts(doc, genre, heal=False)


def score_doc(doc, genre, courts=None):
    """One candidate -> {dq, why, penalties, flags}. Fail-open: a courts
    crash scores the candidate neutral (never kills the MAKE)."""
    try:
        v = (courts or _default_courts)(doc, genre)
    except Exception as e:
        return {"dq": False, "why": f"courts unavailable ({e})",
                "penalties": 0, "flags": []}
    flags, dq_why = [], []
    for name in _HARD:
        cv = v.get(name)
        if isinstance(cv, dict) and cv.get("ok") is False:
            dq_why.append(name)
    pen = 0
    for name in _SOFT:
        cv = v.get(name)
        if isinstance(cv, dict) and cv.get("ok") is False:
            pen += 1
            flags.append(name)
    return {"dq": bool(dq_why),
            "why": ("+".join(dq_why) if dq_why else
                    (",".join(flags) if flags else "clean")),
            "penalties": pen, "flags": flags}


def pick(scored):
    """(winner_idx, one-line summary). Ordering: non-DQ first, fewest
    penalties, then the INCUMBENT (lowest index) on ties."""
    if not scored:
        return 0, "podium: no candidates"
    order = sorted(range(len(scored)),
                   key=lambda i: (scored[i]["dq"], scored[i]["penalties"], i))
    w = order[0]
    parts = []
    for i, s in enumerate(scored):
        tag = "WINNER" if i == w else ("DQ" if s["dq"] else f"-{s['penalties']}")
        parts.append(f"#{i} {tag} ({s['why']})")
    return w, "podium: " + "  ".join(parts)


def bank(root, song, genre, seeds, scored, winner_idx):
    """Losers become preference pairs (append-only, gitignored telemetry).
    Never raises."""
    try:
        tdir = os.path.join(root, "telemetry")
        os.makedirs(tdir, exist_ok=True)
        row = {"t": round(time.time(), 1), "song": song, "genre": genre,
               "seeds": list(seeds), "winner": winner_idx,
               "scores": [{"dq": s["dq"], "penalties": s["penalties"],
                           "why": s["why"]} for s in scored]}
        with open(os.path.join(tdir, "tournament.jsonl"), "a") as f:
            f.write(json.dumps(row) + "\n")
    except Exception:
        pass
