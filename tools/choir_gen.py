#!/usr/bin/env python3
"""THE CHOIR GENERATOR — wave 76 (r-23 item 033): a lead melody +
chords[] become idiomatic multi-voice stacks the DiffSinger bank can
sing. Composes the standing kernels (vocal_stack intervals, adlib_op,
theory chords) — never re-encodes them.

  GOSPEL  SATB block voicing on the HOOKS: S = the melody; A/T/B fill
          the sounding chord inside the real ranges (A F3-F5, T C3-C5,
          B E2-E4), common tones HELD, parallel perfect fifths between
          voice pairs avoided (re-seat the tenor). Verses stay unison —
          the harmony arriving AT the hook is the gospel move. (The
          half-step reprise modulation stays a named arrangement op.)
  K-POP   the 6-12 layer chorus formation: center lead + octave +
          chordal 3rd (vocal_stack lanes) + a BREATH layer (vel x0.3
          whisper double) + a WIDE choir pair (+-0.8 pan unisons) +
          the ad-lib lane (adlib_op vocabulary).

Lanes are named vocals_* so the sing rails render them; levels follow
the stack policy (doubles sit under the lead).
"""
import copy
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

RANGES = {"alto": (53, 77), "tenor": (48, 72), "bass": (40, 64)}


def _chord_pcs(chords, beat):
    import theory
    bar = int(beat // 4) + 1
    ch = theory.chord_at(chords or [], bar)
    return sorted(ch["pcs"]) if ch else None


def _nearest_in_range(pc, prev, lo, hi):
    """The pc's pitch nearest prev (or range center), inside [lo, hi]."""
    anchor = prev if prev is not None else (lo + hi) // 2
    best = None
    for octv in range(0, 11):
        for p in (pc + 12 * octv,):
            if lo <= p <= hi:
                if best is None or abs(p - anchor) < abs(best - anchor):
                    best = p
    return best


def satb_block(lead_notes, chords):
    """S = melody; A/T/B fill each sounding chord, common tones held,
    parallel P5s between pairs re-seated. Returns {alto, tenor, bass}
    note lists."""
    out = {"alto": [], "tenor": [], "bass": []}
    prev = {"alto": None, "tenor": None, "bass": None}
    prev_s = None
    for n in sorted(lead_notes, key=lambda x: float(x.get("start", 0))):
        s_pitch = int(n.get("pitch", 60))
        pcs = _chord_pcs(chords, float(n.get("start", 0)))
        if not pcs:
            continue
        # the melody claims its pc; the others fill, bass takes the root
        root = pcs[0]
        fill = [pc for pc in pcs if pc != s_pitch % 12] or pcs
        bass_p = _nearest_in_range(root, prev["bass"], *RANGES["bass"])
        remaining = [pc for pc in fill if pc != root] or fill
        tenor_p = _nearest_in_range(remaining[0], prev["tenor"],
                                    *RANGES["tenor"])
        alto_pc = remaining[1] if len(remaining) > 1 else remaining[0]
        alto_p = _nearest_in_range(alto_pc, prev["alto"], *RANGES["alto"])
        # parallel-P5 guard: S/T moving in lockstep a fifth apart —
        # re-seat the tenor on another chord tone
        if prev_s is not None and prev["tenor"] is not None and \
                tenor_p is not None:
            was5 = (prev_s - prev["tenor"]) % 12 == 7
            is5 = (s_pitch - tenor_p) % 12 == 7
            moved = (s_pitch != prev_s) and (tenor_p != prev["tenor"]) \
                and (s_pitch - prev_s) * (tenor_p - prev["tenor"]) > 0
            if was5 and is5 and moved:
                alt = [pc for pc in pcs if pc != tenor_p % 12]
                if alt:
                    tenor_p = _nearest_in_range(alt[0], prev["tenor"],
                                                *RANGES["tenor"])
        for voice, p in (("alto", alto_p), ("tenor", tenor_p),
                         ("bass", bass_p)):
            if p is None:
                continue
            out[voice].append({"start": n.get("start"),
                               "len": n.get("len", 0.5),
                               "pitch": int(p),
                               "vel": round(float(n.get("vel", 90))
                                            * 0.8, 3)})
            prev[voice] = p
        prev_s = s_pitch
    return out


def _lead_and_hooks(song):
    import vocal_stack as VS
    lead = VS._lead(song)
    hooks = VS._hook_windows(song)
    if not lead or not hooks:
        return None, None, []
    hook_notes = [n for n in lead["notes"]
                  if any(a <= float(n.get("start", 0)) < b
                         for a, b in hooks)]
    return lead, hooks, hook_notes


def gospel_choir(song):
    """SATB lanes on the hooks; verses stay unison (no lanes there —
    the harmony ARRIVING is the move). Mutates; returns ledger."""
    lead, hooks, hook_notes = _lead_and_hooks(song)
    if not hook_notes or len(hook_notes) < 4:
        return []
    names = {t.get("name") for t in song.get("tracks", [])}
    if "vocals_alto" in names:
        return []
    satb = satb_block(hook_notes, song.get("chords"))
    edits = []
    pans = {"alto": -0.35, "tenor": 0.35, "bass": 0.0}
    for voice, notes in satb.items():
        if len(notes) < 4:
            continue
        song["tracks"].append({
            "name": f"vocals_{voice}", "gainDb": -5.0,
            "pan": pans[voice], "source": copy.deepcopy(lead.get(
                "source") or {"id": "vocals"}), "notes": notes})
        edits.append({"kind": "satb_lane", "voice": voice,
                      "notes": len(notes)})
    if edits:
        edits.append({"kind": "gospel_choir",
                      "why": (f"SATB block lands on the hook ONLY "
                              f"({len(hook_notes)} lead notes harmonized;"
                              " verses stay unison — the choir arriving "
                              "IS the lift); common tones held, parallel "
                              "fifths re-seated")})
    return edits


def kpop_stack(song, genre="kpop"):
    """The 6-12 layer chorus formation, composed from the standing
    kernels. Mutates; returns ledger."""
    import vocal_stack as VS
    lead, hooks, hook_notes = _lead_and_hooks(song)
    if not hook_notes or len(hook_notes) < 4:
        return []
    names = {t.get("name") for t in song.get("tracks", [])}
    if "vox_breath" in names:
        return []
    edits = []
    lanes = VS.plan_stacks(song, genre)           # intervals: one resolver
    for ln in lanes:
        if ln["name"] in names:
            continue
        ln["source"] = copy.deepcopy(lead.get("source") or
                                     {"id": "vocals"})
        song["tracks"].append(ln)
        edits.append({"kind": "stack_lane", "name": ln["name"]})
    breath = [dict(copy.deepcopy(n),
                   vel=round(float(n.get("vel", 90)) * 0.3, 3))
              for n in hook_notes]
    song["tracks"].append({"name": "vox_breath", "gainDb": -12.0,
                           "pan": 0.0,
                           "source": copy.deepcopy(lead.get("source")
                                                   or {"id": "vocals"}),
                           "notes": breath})
    edits.append({"kind": "breath_layer", "notes": len(breath)})
    for side, pan in (("L", -0.8), ("R", 0.8)):
        song["tracks"].append({
            "name": f"vox_choir{side}", "gainDb": -9.0, "pan": pan,
            "source": copy.deepcopy(lead.get("source") or
                                    {"id": "vocals"}),
            "notes": copy.deepcopy(hook_notes)})
        edits.append({"kind": "wide_choir", "side": side})
    try:                                          # the ad-lib lane
        import adlib_op
        eds = adlib_op.place_adlibs(song, genre)
        if eds:
            edits.append({"kind": "adlib_lane", "n": len(eds)})
    except Exception:
        pass
    total = sum(1 for e in edits if e["kind"] in
                ("stack_lane", "breath_layer", "wide_choir",
                 "adlib_lane")) + 1               # +1 = the lead itself
    edits.append({"kind": "kpop_stack", "layers": total,
                  "why": (f"{total}-layer chorus formation (window "
                          "6-12): center lead + interval stacks + "
                          "breath double + wide choir pair + ad-libs — "
                          "each layer a SINGABLE vocals lane, levels "
                          "under the lead per the stack policy")})
    return edits


def wordless_choir(song, vowel="a"):
    """W98 (r-26 item 223): THE WORDLESS CHOIR — the epic-choir signal
    without lyrics. Compose: gospel SATB lanes (w76) + a hum phoneme
    stream staged per choir lane (@<vowel> tokens, one per note — the
    sing rail's hum contract) so sing.py renders each voice on the
    Gahata bank. The choir sings 'ah', not words: cinema's oldest
    lift. Mutates; returns the ledger."""
    edits = gospel_choir(song)
    if not any(e.get("kind") == "satb_lane" for e in edits):
        return edits
    lyr = song.setdefault("lyrics", [])
    staged = 0
    for t in song.get("tracks", []) or []:
        nm = str(t.get("name", ""))
        if not nm.startswith("vocals_") or nm == "vocals_lead":
            continue
        for n in t.get("notes") or []:
            lyr.append({"beat": float(n.get("start", 0)),
                        "text": f"@{vowel}", "lane": nm})
            staged += 1
    lyr.sort(key=lambda l: float(l.get("beat", 0)))
    edits.append({"kind": "wordless_choir", "phonemes": staged,
                  "vowel": vowel,
                  "why": (f"{staged} '@{vowel}' hum tokens staged across "
                          "the SATB lanes — the sing rail renders each "
                          "voice wordless (cinema's oldest lift); words "
                          "never enter")})
    return edits


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="THE CHOIR GENERATOR (w76)")
    ap.add_argument("song")
    ap.add_argument("style", choices=("gospel", "kpop", "wordless"))
    a = ap.parse_args()
    song = json.load(open(a.song))
    eds = (gospel_choir(song) if a.style == "gospel" else
           kpop_stack(song) if a.style == "kpop" else
           wordless_choir(song))
    if eds:
        json.dump(song, open(a.song, "w"), indent=1)
    print(json.dumps(eds, indent=1))
