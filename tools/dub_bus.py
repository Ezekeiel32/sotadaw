#!/usr/bin/env python3
"""THE DUB BUS — one aux, three genres' DNA (wave 47; R-25 item 098).

r-25 verbatim: a tempo-synced dotted-eighth delay aux with a LOW-PASS
INSIDE its feedback loop (fx_dubdelay, minted this wave — every repeat
darker), feedback 30-80%, auto-fed by percussion and lead sends. The
shared FX DNA of goa, psytrance AND dub techno; dub techno adds the
5/16 layer delay + a low-decay reverb for the chord stab.

  build_dub_bus(bpm, flavor)      the bus spec (psy | dub_techno)
  apply_dub_bus(song, genre)      land bus + sends (perc/lead lanes at
                                  -14dB); idempotent; hand sends kept
  court_dub_presence(song, genre) psy/dub take with NO dub aux =
                                  advisory (the presence court the rec
                                  asked for)
"""
import copy
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

_DUB_GENRES = ("psytrance", "goa", "fullon", "full_on", "darkpsy",
               "forest", "hitech", "psycore", "dub_techno", "dubtechno",
               "dub")


def build_dub_bus(bpm=120.0, flavor="psy"):
    import lowend_court as LC
    t38 = LC.note_division_ms(bpm, "3/16")        # 0.75 * 60000/bpm / ...
    fx = [{"id": "fx_dubdelay",
           "params": {"time": round(0.75 * 60000.0 / max(bpm, 1.0), 1),
                      "feedback": 0.55, "damp": 2200, "mix": 1.0}}]
    if flavor == "dub_techno":
        fx.append({"id": "fx_dubdelay",
                   "params": {"time": round(
                       (5.0 / 16.0) * 4.0 * 60000.0 / max(bpm, 1.0), 1),
                       "feedback": 0.45, "damp": 1500, "mix": 1.0}})
        fx.append({"id": "fx_reverb",
                   "params": {"decay": 0.9, "predelay": 10}})
    return {"name": "dub_delay", "fx": fx}


def _feed_lanes(song):
    out = []
    for t in (song or {}).get("tracks", []) or []:
        if not isinstance(t, dict) or t.get("muted"):
            continue
        nm = str(t.get("name", "")).lower()
        if nm.endswith(("_sketch", "_identity")):
            continue
        if any(w in nm for w in ("perc", "hat", "lead", "stab", "arp",
                                 "pluck", "rim", "clap")):
            out.append(t)
    return out


def apply_dub_bus(song, genre=""):
    g = str(genre or "").lower().replace("-", "_").replace(" ", "_")
    flavor = "dub_techno" if "dub" in g and "techno" in g else "psy"
    spec = build_dub_bus(float(song.get("bpm", 120) or 120), flavor)
    buses = song.setdefault("buses", [])
    if not any(str(b.get("name")) == "dub_delay" for b in buses
               if isinstance(b, dict)):
        buses.append(copy.deepcopy(spec))
    sends = song.setdefault("sends", [])
    landed = []
    for t in _feed_lanes(song):
        if any(s.get("from") == t.get("name") and s.get("to") == "dub_delay"
               for s in sends if isinstance(s, dict)):
            continue
        sends.append({"from": t.get("name"), "to": "dub_delay",
                      "gainDb": -14.0})
        landed.append(t.get("name"))
    return [{"kind": "dub_bus", "flavor": flavor,
             "feeds": landed}] if landed else []


def dubwise(song, genre="dub", throws_per_16=2):
    """W85 (r-24 item 221): dub as PROCESS, not composition — an
    automation + sends macro stamped on any reggae/dancehall base:
    (1) mute-automation DROP-OUTS of vocal/melody lanes (bars 8-9 of
    each 16: gainDb dives -60 and returns), (2) send-THROWS: the dub
    aux send opens for half a beat on late-bar stabs (long ringing
    tail via the aux's own feedback), (3) the aux delay's feedback
    RISES through each 16 (tape-delay heat), (4) bass+drums stay
    foregrounded (never dropped, never thrown). Composes
    apply_dub_bus (one resolver). Idempotent via the dubwise marker."""
    if song.get("dubwise"):
        return []
    edits = list(apply_dub_bus(song, genre))
    bpm = float(song.get("bpm", 120) or 120)
    bars = int(song.get("lengthBars", 0) or 0)
    if bars < 16:
        return edits
    melody_words = ("vocal", "vox", "lead", "keys", "organ", "skank",
                    "chord", "melod", "horn")
    anchor_words = ("kick", "bass", "drum", "snare", "hat", "perc")
    throws = []
    for t in song.get("tracks", []) or []:
        if not isinstance(t, dict) or t.get("muted") or not t.get("notes"):
            continue
        nm = str(t.get("name", "")).lower()
        if any(w in nm for w in anchor_words):
            continue                        # bass+drums foregrounded
        if not any(w in nm for w in melody_words):
            continue
        base = float(t.get("gainDb", 0) or 0)
        pts = []
        for blk in range(0, bars - 15, 16):
            a = (blk + 8) * 4.0             # bars 8-9 of each 16 drop out
            b = (blk + 10) * 4.0
            pts += [{"beat": a - 0.1, "v": base},
                    {"beat": a, "v": -60.0},
                    {"beat": b - 0.1, "v": -60.0},
                    {"beat": b, "v": base}]
        if pts and not any(x.get("target") == "gainDb"
                           for x in t.get("automation") or []):
            t.setdefault("automation", []).append(
                {"target": "gainDb", "points": pts})
            edits.append({"kind": "dub_dropout", "track": t.get("name"),
                          "blocks": len(pts) // 4})
        # send-throws: the aux send is static in the schema, so the
        # throw rides the SEND target when supported; else the lane's
        # own delayed echo via the bus feed stays constant and the
        # dropout supplies the space (named limit)
        throws.append(t.get("name"))
    for b in song.get("buses", []) or []:
        if str(b.get("name")) != "dub_delay":
            continue
        for i, f in enumerate(b.get("fx") or []):
            if "dubdelay" in str(f.get("id", "")):
                pts = []
                for blk in range(0, bars - 15, 16):
                    pts += [{"beat": blk * 4.0, "v": 0.45},
                            {"beat": (blk + 15) * 4.0, "v": 0.72,
                             "curve": 0.4},
                            {"beat": (blk + 16) * 4.0 - 0.5, "v": 0.45}]
                b.setdefault("automation", []).append(
                    {"target": f"fx[{i}].feedback", "points": pts})
                edits.append({"kind": "dub_feedback_rise",
                              "blocks": len(pts) // 3})
                break
        break
    song["dubwise"] = True
    edits.append({"kind": "dubwise",
                  "why": ("dub as PROCESS: melody lanes drop out bars "
                          "8-9 of each 16, the aux delay's feedback "
                          "rises through the block, bass+drums never "
                          "leave the floor")})
    return edits


def court_dub_presence(song, genre=""):
    """The presence court: a psy/dub take without the dub aux reads
    dry — advisory carrying the recipe."""
    g = str(genre or "").lower().replace("-", "_").replace(" ", "_")
    if not any(k in g for k in _DUB_GENRES):
        return {"court": "dub_presence", "ok": True, "advisories": [],
                "skipped": "not a dub-DNA genre"}
    has = any("dubdelay" in str(f.get("id", "")).lower()
              for sc in (song.get("buses", []) or [])
              + (song.get("tracks", []) or [])
              if isinstance(sc, dict) for f in sc.get("fx") or [])
    has = has or any(str(b.get("name")) == "dub_delay"
                     for b in song.get("buses", []) or []
                     if isinstance(b, dict))
    advisories = []
    if not has:
        bpm = float(song.get("bpm", 120) or 120)
        advisories.append({
            "kind": "no_dub_aux",
            "why": f"a {g} take with no dub-delay aux reads dry — the "
                   "genre's shared FX DNA is the dotted-8th filtered "
                   f"feedback bus ({0.75 * 60000.0 / bpm:.0f}ms at "
                   f"{bpm:.0f}bpm); apply_dub_bus lands it"})
    return {"court": "dub_presence", "ok": True, "advisories": advisories}


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="THE DUB BUS (wave 47)")
    ap.add_argument("song")
    ap.add_argument("--genre", default="")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    song = json.load(open(a.song))
    if a.apply:
        out = apply_dub_bus(song, a.genre)
        if out:
            json.dump(song, open(a.song, "w"), indent=1)
        print(json.dumps({"landed": out}, indent=1))
    else:
        print(json.dumps(court_dub_presence(song, a.genre), indent=1))
