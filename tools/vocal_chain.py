#!/usr/bin/env python3
"""THE VOCAL CHAIN — the r-12 topology becomes action (wave 46; R-12
items 065 + the universal chain-order law).

r-12 verbatim: HPF -> subtractive EQ -> COMPRESSION -> DE-ESS ->
additive EQ -> saturation -> pitch-correction -> reverb/delay ON SENDS
(never inserts); de-ess AFTER the compressor (comp exaggerates esses);
lead vocals default to TWO-STAGE compression (fast stage catches
consonant spikes, a slow 2:1 stage rides the phrase). The numbers come
from the wave-24 VocalTarget table (KG, seed presets fail-open).

  build_vocal_chain(genre)        the ordered fx list + the send spec
  apply_vocal_chain(song, genre)  land it on the lead vocal lane +
                                  build the verb bus/send; idempotent;
                                  NEVER overwrites an existing chain
                                  (hand work is sacred)
  court_vocal_chain(song)         topology advisories: deess-before-
                                  comp, reverb-as-insert (the sends
                                  law), missing second stage on leads
"""
import copy
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _target(genre):
    try:
        import kg
        rows = kg.KG().q(
            "MATCH (v:VocalTarget {name: '"
            + str(genre or "").lower().replace("'", "") + "'}) "
            "RETURN v.comp_attack_ms, v.comp_release_ms, v.comp_ratio, "
            "v.deess_hz, v.deess_gr_db, v.sat_drive_db, v.sat_mix, "
            "v.reverb_decay_s, v.predelay_ms, v.delay_division, "
            "v.delay_feedback_pct")
        if rows and rows[0][0] is not None:
            r = rows[0]
            return {"comp_attack_ms": float(r[0]),
                    "comp_release_ms": float(r[1]),
                    "comp_ratio": float(r[2]), "deess_hz": float(r[3]),
                    "deess_gr_db": float(r[4]),
                    "sat_drive_db": float(r[5]), "sat_mix": float(r[6]),
                    "reverb_decay_s": float(r[7]),
                    "predelay_ms": float(r[8]),
                    "delay_division": str(r[9]),
                    "delay_feedback_pct": float(r[10])}
    except Exception:
        pass
    import kg_seed_vocal as KV
    return dict(KV.PRESETS[KV.preset_for(genre or "pop")])


def build_vocal_chain(genre="", bpm=120.0):
    """The ordered INSERT chain + the send spec (verb lives on a bus)."""
    t = _target(genre)
    import lowend_court as LC
    inserts = [
        {"id": "fx_hipass", "params": {"cutoff": 90, "res": 0.7}},
        {"id": "fx_comp", "params": {                 # stage 1: FAST
            "thresh": -22, "ratio": t["comp_ratio"],
            "attack": t["comp_attack_ms"],
            "release": t["comp_release_ms"], "makeup": 2.0}},
        {"id": "fx_comp", "params": {                 # stage 2: SLOW 2:1
            "thresh": -18, "ratio": 2.0, "attack": 30,
            "release": 200, "makeup": 1.0}},
        {"id": "fx_deess", "params": {"freq": t["deess_hz"],
                                      "thresh": -30}},
        {"id": "fx_saturate", "params": {"drive": t["sat_drive_db"],
                                         "tone": 4500,
                                         "mix": min(t["sat_mix"], 0.5)}},
    ]
    send = {"bus": "vox_verb",
            "bus_fx": [{"id": "fx_reverb",
                        "params": {"decay": t["reverb_decay_s"],
                                   "predelay": t["predelay_ms"]}},
                       {"id": "fx_delay",
                        "params": {"time": LC.note_division_ms(
                            bpm, t["delay_division"]),
                            "feedback": t["delay_feedback_pct"] / 100.0,
                            "mix": 1.0}}],
            "gainDb": -10.0}
    return {"inserts": inserts, "send": send}


def _lead_vocal(song):
    for t in (song or {}).get("tracks", []) or []:
        if not isinstance(t, dict) or t.get("muted"):
            continue
        nm = str(t.get("name", "")).lower()
        if nm.endswith(("_sketch", "_identity")) or "stack" in nm \
                or "adlib" in nm:
            continue
        if any(w in nm for w in ("vocal", "vox", "voice", "topline")):
            return t
    return None


def apply_vocal_chain(song, genre=""):
    """Land the chain on the lead vocal lane + the verb bus/send.
    HAND WORK IS SACRED: a lane already carrying fx keeps them (no-op).
    Idempotent. Mutates; returns ledger."""
    lane = _lead_vocal(song)
    if lane is None:
        return []
    if lane.get("fx"):
        return []                       # existing chain = hand work
    spec = build_vocal_chain(genre, float(song.get("bpm", 120) or 120))
    lane["fx"] = copy.deepcopy(spec["inserts"])
    buses = song.setdefault("buses", [])
    if not any(str(b.get("name")) == "vox_verb" for b in buses
               if isinstance(b, dict)):
        buses.append({"name": "vox_verb",
                      "fx": copy.deepcopy(spec["send"]["bus_fx"])})
    sends = song.setdefault("sends", [])
    if not any(s.get("from") == lane.get("name")
               and s.get("to") == "vox_verb" for s in sends
               if isinstance(s, dict)):
        sends.append({"from": lane.get("name"), "to": "vox_verb",
                      "gainDb": spec["send"]["gainDb"]})
    return [{"kind": "vocal_chain", "track": lane.get("name"),
             "inserts": [f["id"] for f in lane["fx"]],
             "send": "vox_verb"}]


def court_vocal_chain(song):
    """Topology advisories (the chain-order law)."""
    advisories = []
    lane = _lead_vocal(song)
    if lane is None or not lane.get("fx"):
        return {"court": "vocal_chain", "ok": True, "advisories": [],
                "skipped": "no vocal chain to judge"}
    ids = [str(f.get("id", "")) for f in lane["fx"]]
    if "fx_deess" in ids and "fx_comp" in ids and \
            ids.index("fx_deess") < ids.index("fx_comp"):
        advisories.append({
            "kind": "deess_before_comp",
            "why": "the de-esser sits BEFORE the compressor — comp "
                   "exaggerates esses; deess belongs after (r-12 order)"})
    if "fx_reverb" in ids or "fx_delay" in ids:
        advisories.append({
            "kind": "space_as_insert",
            "why": "reverb/delay ride the vocal as INSERTS — the sends "
                   "law: space lives on a bus so the dry voice keeps "
                   "its front (r-12)"})
    if ids.count("fx_comp") == 1:
        advisories.append({
            "kind": "single_stage",
            "why": "one compressor carries the whole vocal — leads "
                   "default to TWO-STAGE (fast spike-catcher + slow "
                   "2:1 ride, r-12)"})
    return {"court": "vocal_chain", "ok": True, "advisories": advisories}


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="THE VOCAL CHAIN (wave 46)")
    ap.add_argument("song")
    ap.add_argument("--genre", default="")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    song = json.load(open(a.song))
    if a.apply:
        out = apply_vocal_chain(song, a.genre)
        if out:
            json.dump(song, open(a.song, "w"), indent=1)
        print(json.dumps({"landed": out}, indent=1))
    else:
        print(json.dumps(court_vocal_chain(song), indent=1))


# ------------------------------------------------------------ w68 (202)
_BREATH_ATTEN = (
    (("singer_songwriter", "folk", "acoustic", "ballad", "intimate",
      "jazz"), -3.0),
    (("pop", "edm", "trap", "house", "dance", "electro"), -12.0),
)


def breath_atten_for(genre):
    g = str(genre or "").lower().replace("-", "_").replace(" ", "_")
    for words, db in _BREATH_ATTEN:
        if any(w in g for w in words):
            return db
    return -8.0


def court_breath(song, genre=""):
    """W68 (r-12 item 202): breaths live in the KNOWN gaps between
    lyric phrases — the compressor exaggerates them unless clip-gained
    FIRST. Court: a sung lane (lyrics + vocal audio clip) with breath-
    sized gaps (0.4-2.5s) and no gain treatment = advisory."""
    lyr = sorted((l for l in (song or {}).get("lyrics", []) or []
                  if isinstance(l, dict)),
                 key=lambda l: float(l.get("beat", 0)))
    if len(lyr) < 3:
        return {"court": "breath", "ok": True, "advisories": [],
                "skipped": "needs staged lyrics"}
    lane = None
    for t in (song or {}).get("tracks", []) or []:
        if not isinstance(t, dict) or t.get("muted"):
            continue
        nm = str(t.get("name", "")).lower()
        if ("voc" in nm or "voice" in nm or "sing" in nm) and                 (t.get("audioClips") or []):
            lane = t
            break
    if lane is None:
        return {"court": "breath", "ok": True, "advisories": [],
                "skipped": "no sung audio lane"}
    if any(a.get("target") == "gainDb"
           for a in lane.get("automation") or []):
        return {"court": "breath", "ok": True, "advisories": [],
                "skipped": "gainDb already ridden (rider/hand work)"}
    spb = 60.0 / float((song or {}).get("bpm", 120) or 120)
    gaps = []
    for a, b in zip(lyr, lyr[1:]):
        wa = str(a.get("text", "")).split()
        # a line entry's window runs to the next entry; the gap starts
        # after its last word's rough footprint (0.45s/word spoken-sung)
        end_s = float(a.get("beat", 0)) * spb + max(len(wa), 1) * 0.45
        start_next = float(b.get("beat", 0)) * spb
        if 0.4 <= start_next - end_s <= 2.5:
            gaps.append((end_s, start_next))
    advisories = []
    if len(gaps) >= 2:
        advisories.append({
            "kind": "raw_breaths", "gaps": len(gaps),
            "atten_db": breath_atten_for(genre),
            "why": (f"{len(gaps)} breath-sized gaps between phrases with "
                    "no gain treatment — the chain's compressor will "
                    "EXAGGERATE every inhale; clip-gain them "
                    f"{breath_atten_for(genre):.0f}dB before it (never "
                    "delete — silence between phrases reads robotic)")})
    return {"court": "breath", "ok": True, "advisories": advisories,
            "lane": lane.get("name"), "gaps": gaps}


def heal_breath(song, verdict=None, genre=""):
    """Dip gainDb across each breath gap (0.15s ramps), scaled by
    genre. Skips lanes whose gainDb is already ridden (the rider and
    the hand are sacred)."""
    v = verdict or court_breath(song, genre)
    if not v.get("advisories"):
        return []
    lane = next((t for t in (song or {}).get("tracks", []) or []
                 if isinstance(t, dict) and t.get("name") == v.get("lane")),
                None)
    if lane is None:
        return []
    spb = 60.0 / float((song or {}).get("bpm", 120) or 120)
    att = breath_atten_for(genre)
    base = float(lane.get("gainDb", 0) or 0)
    pts = []
    for (a_s, b_s) in v.get("gaps", []):
        a_b, b_b = a_s / spb, b_s / spb
        r = 0.15 / spb
        pts += [{"beat": round(a_b, 3), "v": base},
                {"beat": round(a_b + r, 3), "v": round(base + att, 1)},
                {"beat": round(b_b - r, 3), "v": round(base + att, 1)},
                {"beat": round(b_b, 3), "v": base}]
    lane.setdefault("automation", []).append(
        {"target": "gainDb", "points": pts})
    return [{"kind": "breath_dips", "lane": lane.get("name"),
             "gaps": len(v.get("gaps", [])), "atten_db": att,
             "why": (f"'{lane.get('name')}': {len(v.get('gaps', []))} "
                     f"breath gaps dipped {att:.0f}dB with 150ms ramps "
                     "BEFORE the compressor sees them")}]

