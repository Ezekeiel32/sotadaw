#!/usr/bin/env python3
"""DJ-LIVE R4 (E3's realtime half of P7) — the deck-swap ADVISOR.

While a dj_set song plays, the ears bus streams 10 Hz frames; this kernel folds
the recent window + the set's plan (<name>.setplan.json = deck boundaries in
wall-seconds) into working-DJ advice, one line at a time:

  APPROACH   next deck lands in <=20s -> hands to the filter (the bass swap)
  RIDE       energy rising into the boundary -> let it ride, swap on the drop
  PLATEAU/CLIFF/DEAD_AIR  live dj_listener verdicts mid-deck -> their fixes

Pure + replay-provable: advise(frames, setplan) is deterministic; the CLI
replays a recorded ears.jsonl. The sidecar's idle loop is the live speaker
(throttled, deduped, SOTADAW_DJ_LIVE=0 kills it).

  dj_live.py <set.setplan.json> --frames <ears.jsonl> [--hop 4]
"""
import argparse
import json
import sys

import dj_listener


def deck_at(setplan, sec):
    """(index, entry, next_entry) of the deck sounding at wall-second sec."""
    cur, nxt = None, None
    for i, e in enumerate(setplan):
        if sec >= e.get("start", 0.0):
            cur = (i, e)
        elif nxt is None:
            nxt = e
    return (cur[0] if cur else 0), (cur[1] if cur else (setplan[0] if setplan else {})), nxt


def advise(frames, setplan, hop=4.0):
    """frames (ears.jsonl dicts) + setplan -> [{t, kind, deck, text}] advice.
    Deduped by (kind, deck) — a live speaker repeats nothing."""
    live = [f for f in frames if f.get("playing")]
    if not live or not setplan:
        return []
    out, seen = [], set()

    def say(t, kind, deck, text):
        key = (kind, deck)
        if key in seen:
            return
        seen.add(key)
        out.append({"t": round(t, 1), "kind": kind, "deck": deck, "text": text})

    # positional advice: walk the frames against the plan
    for f in live:
        sec = float(f.get("sec", 0.0))
        i, cur, nxt = deck_at(setplan, sec)
        if nxt is not None:
            gap = nxt.get("start", 0.0) - sec
            if 0 < gap <= 20.0:
                rising = False
                win = [g for g in live if 0 <= sec - float(g.get("sec", 0)) <= 12.0]
                if len(win) >= 3:
                    r0 = sum(win[0].get("rms_db", [-120, -120])) / 2
                    r1 = sum(win[-1].get("rms_db", [-120, -120])) / 2
                    rising = (r1 - r0) > 1.5
                nm = nxt.get("song", f"deck {i + 2}")
                if rising:
                    say(sec, "RIDE", i + 1,
                        f"energy is climbing into the handover — let it ride, swap '{nm}' in ~{gap:.0f}s ON the drop")
                else:
                    say(sec, "APPROACH", i + 1,
                        f"'{nm}' lands in ~{gap:.0f}s — hands to the filter: kill the incoming bass, swap it at the boundary")

    # live listener verdicts over the same window -> their named fixes, deck-tagged
    feats = dj_listener.frames_to_feats(live, hop=hop)
    for v in dj_listener.listen(feats, hop):
        t = float(v.get("t", 0.0)) + float(live[0].get("sec", 0.0))
        i, cur, _ = deck_at(setplan, t)
        say(t, v["kind"], i, f"deck {chr(65 + i)}: {v['fix']}")

    return sorted(out, key=lambda a: a["t"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("setplan")
    ap.add_argument("--frames", required=True, help="ears.jsonl (live or recorded)")
    ap.add_argument("--hop", type=float, default=4.0)
    a = ap.parse_args()
    setplan = json.load(open(a.setplan))
    frames = []
    for ln in open(a.frames):
        try:
            frames.append(json.loads(ln))
        except Exception:
            continue
    adv = advise(frames, setplan, a.hop)
    for x in adv:
        print(f"[dj-live] t={x['t']:>7.1f}s [{x['kind']}] {x['text']}")
    print("DJLIVE_JSON " + json.dumps(adv))
    return 0


if __name__ == "__main__":
    sys.exit(main())
