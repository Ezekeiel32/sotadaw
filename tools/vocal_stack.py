#!/usr/bin/env python3
"""THE STACK — doubling is symbolic, never an audio doubler (wave 25;
R-12 item 014).

Real records stack the hook: a unison double glued under the lead, an
octave ghost, chord-aware harmony thirds. This DAW owns the notes, so
stacks are NOTE LANES the voice re-sings — never a chorus/doubler fx
(the whole point of item 014). The doubling policy (intervals, level,
detune) comes from the VocalTarget table (wave 24), fail-open to the
seed presets.

  plan_stacks(song, genre)   -> [{name, notes, gainDb, pan, interval}]
        Hook-class sections only (r-12: stacks live on hooks; verses
        stay solo). unison = same notes; octave_up = +12 clamped by
        melody_court's tessitura; third_up = the nearest CHORD TONE
        3..5 semitones up per note (theory chord field — a parallel
        major-third machine would leave the key).
  apply_stacks(song, genre)  -> mutates song: adds the lanes (marked
        "stack_of": lead lane) + returns them. Idempotent (existing
        stack lanes are refreshed, never duplicated).
  CLI: vocal_stack.py <song.json> --genre g [--apply]

The SING integration (each stack lane re-sung via a temp lyrics window)
is the documented follow-up — the lanes land with the lead's own voice
source as the proxy until re-sung (the whisper-double idiom), so the
arrangement is ALREADY true after --apply.
"""
import copy
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

_HOOKISH = ("chorus", "drop", "hook", "theme")


def _policy(genre):
    """VocalTarget doubling policy: KG first, seed presets fail-open."""
    try:
        import kg
        rows = kg.KG().q(
            "MATCH (v:VocalTarget {name: '"
            + str(genre or "").lower().replace("'", "") + "'}) "
            "RETURN v.double_level_db, v.double_detune_cents, "
            "v.double_intervals")
        if rows and rows[0][0] is not None:
            return {"level_db": float(rows[0][0]),
                    "detune_cents": float(rows[0][1] or 7),
                    "intervals": str(rows[0][2] or "unison").split(",")}
    except Exception:
        pass
    import kg_seed_vocal as KV
    p = KV.PRESETS[KV.preset_for(genre or "pop")]
    return {"level_db": p["double_level_db"],
            "detune_cents": p["double_detune_cents"],
            "intervals": p["double_intervals"].split(",")}


def _lead(song):
    best = None
    for t in song.get("tracks", []) or []:
        if not isinstance(t, dict) or t.get("muted"):
            continue
        nm = str(t.get("name", "")).lower()
        if nm.endswith(("_sketch", "_identity")) or "stack" in nm:
            continue
        if any(w in nm for w in ("lead", "vocal", "vox", "topline")) \
                and (t.get("notes") or []):
            if best is None or len(t["notes"]) > len(best["notes"]):
                best = t
    return best


def _hook_windows(song):
    secs = sorted((s for s in song.get("sections", []) or []
                   if isinstance(s, dict)),
                  key=lambda s: float(s.get("startBar", 0)))
    out = []
    for i, s in enumerate(secs):
        nm = str(s.get("name", "")).lower()
        if not any(h in nm for h in _HOOKISH):
            continue
        b0 = float(s.get("startBar", 0)) * 4
        b1 = float(secs[i + 1].get("startBar", 1e9)) * 4 \
            if i + 1 < len(secs) else 1e9
        out.append((b0, b1))
    return out


def _chord_at(chords, beat):
    cur = None
    for c in chords or []:
        if float(c.get("beat", c.get("startBeat", 0))) <= beat:
            cur = c
        else:
            break
    return cur


def _third_up(pitch, chord):
    """Nearest chord tone 3..5 semitones above — never a parallel-third
    machine (that leaves the key)."""
    try:
        import theory
        pcs = None
        if chord and chord.get("chord"):
            parsed = theory.parse_chord(str(chord["chord"]))
            if parsed:
                pcs = parsed.get("pcs")
        if pcs:
            for up in (3, 4, 5):
                if (pitch + up) % 12 in pcs:
                    return pitch + up
            return None           # no chord tone a third-ish up: sit out
    except Exception:
        pass
    return pitch + 4 if chord is None else None


def plan_stacks(song, genre=""):
    lead = _lead(song)
    if not lead:
        return []
    hooks = _hook_windows(song)
    if not hooks:
        return []
    pol = _policy(genre)
    hook_notes = [n for n in lead["notes"]
                  if any(b0 <= float(n.get("start", 0)) < b1
                         for b0, b1 in hooks)]
    if len(hook_notes) < 4:
        return []
    chords = song.get("chords") or []
    lanes = []
    pans = {"unison": -0.25, "octave_up": 0.25, "third_up": 0.3,
            "fifth_up": -0.3, "sixth_up": 0.3}
    try:
        import melody_court
        clamp = melody_court.clamp_tessitura   # mutates, returns ledger
    except Exception:
        def clamp(notes, voice="female"):
            return []
    for iv in pol["intervals"]:
        iv = iv.strip()
        if iv == "unison":
            notes = [dict(n, vel=round(float(n.get("vel", 0.8)) * 0.9, 3))
                     for n in copy.deepcopy(hook_notes)]
        elif iv == "octave_up":
            notes = [dict(n, pitch=int(n.get("pitch", 60)) + 12)
                     for n in copy.deepcopy(hook_notes)]
            clamp(notes, "female")     # fold back into the singable window
        elif iv in ("third_up", "sixth_up", "fifth_up"):
            base_up = {"third_up": None, "fifth_up": 7, "sixth_up": 9}[iv]
            notes = []
            for n in hook_notes:
                p = int(n.get("pitch", 60))
                if base_up is None:
                    up = _third_up(p, _chord_at(chords,
                                                float(n.get("start", 0))))
                    if up is None:
                        continue
                else:
                    up = p + base_up
                notes.append(dict(copy.deepcopy(n), pitch=up))
            if len(notes) < len(hook_notes) * 0.5:
                continue          # too few chord-safe notes: skip the lane
        else:
            continue
        lanes.append({"name": f"vox_stack_{iv}",
                      "interval": iv,
                      "gainDb": pol["level_db"],
                      "pan": pans.get(iv, 0.2),
                      "notes": notes})
    return lanes


def apply_stacks(song, genre=""):
    """Mutates: land the stack lanes (source = the lead's own source as
    the proxy voice until re-sung). Idempotent by lane name."""
    plans = plan_stacks(song, genre)
    if not plans:
        return []
    lead = _lead(song)
    tracks = song.setdefault("tracks", [])
    by_name = {str(t.get("name", "")): t for t in tracks
               if isinstance(t, dict)}
    landed = []
    for p in plans:
        lane = by_name.get(p["name"])
        if lane is None:
            lane = {"name": p["name"]}
            tracks.append(lane)
        lane.update({
            "notes": p["notes"], "gainDb": p["gainDb"], "pan": p["pan"],
            "source": copy.deepcopy(lead.get("source") or {}),
            "stack_of": lead.get("name", "lead")})
        landed.append({"lane": p["name"], "interval": p["interval"],
                       "notes": len(p["notes"]), "gainDb": p["gainDb"],
                       "pan": p["pan"]})
    return landed


def main():
    import argparse
    ap = argparse.ArgumentParser(description="THE STACK (wave 25)")
    ap.add_argument("song")
    ap.add_argument("--genre", default="")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    song = json.load(open(args.song))
    if args.apply:
        out = apply_stacks(song, args.genre)
        if out:
            json.dump(song, open(args.song, "w"), indent=1)
        print(json.dumps({"landed": out, "saved": bool(out)}, indent=1))
    else:
        print(json.dumps({"planned": [
            {k: (len(v) if k == "notes" else v) for k, v in p.items()}
            for p in plan_stacks(song, args.genre)]}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
