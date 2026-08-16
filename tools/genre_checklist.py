#!/usr/bin/env python3
"""THE GENRE CHECKLIST — the court system, one page per genre (wave 30;
R-21 item 029).

r-21 asked for '12 per-genre checklists as court-line rule sets:
{tempo_range, kick_topology, swing_range, required_chords, bass_pattern,
drum_machine, arrangement_phrasing, forbidden}'. Waves 12-27 built every
rule as a LIVE court; this module is the assembled VIEW — the rule block
per genre pulled from the same tables the courts enforce (never a second
copy of the law: groove_court/lowend_court/harmony_court/tension/
translation_court/kg_seed_* are imported, one-resolver style), plus
checklist(song, genre) = the composite verdict the eval lane and UI
chips consume.

  rule_block(genre)      -> the r-21 dict, assembled from the live tables
  checklist(song, genre) -> {rules, verdicts, ok} — runs the owning
                            courts and folds their verdicts under the
                            checklist keys
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _norm(genre):
    return str(genre or "").lower().replace("-", "_").replace(" ", "_")


def rule_block(genre):
    """The r-21 rule set, assembled from the SAME tables the courts
    enforce."""
    import groove_court as GC
    import kg_seed_groove_law as GL
    import harmony_court as HC
    import translation_court as TC
    import kg_seed_vocal as KV
    g = _norm(genre)
    block = {"genre": g}
    win = GC.tempo_window(genre)
    if win:
        block["tempo_range"] = list(win)
    if any(k == g or k in g for k in GC._KICK_4X4):
        block["kick_topology"] = "4x4"
    elif any(k in g for k in GC._KICK_NO_4X4):
        block["kick_topology"] = "no_4x4"
    else:
        block["kick_topology"] = "free"
    for k, w in sorted(GC.SWING_WINDOWS.items(), key=lambda kv: -len(kv[0])):
        if k in g:
            block["swing_range"] = list(w)
            break
    block["drum_machine"] = GL.drum_machine_for(genre)
    try:
        block["progression_family"] = HC._prog_family(genre)
    except Exception:
        pass
    block["translation_family"] = TC.family_for(genre)
    block["vocal_family"] = KV.preset_for(genre)
    block["sub_mono"] = True          # the one genre-independent floor
    forbidden = []
    if block.get("swing_range") and block["swing_range"][0] > 0.54:
        forbidden.append("straight_grid")
    if block["kick_topology"] == "no_4x4":
        forbidden.append("four_on_floor_kick")
    if block["kick_topology"] == "4x4":
        forbidden.append("unpumped_onbeat_bass")
    forbidden.append("panned_or_widened_sub")
    block["forbidden"] = forbidden
    return block


def checklist(song, genre=""):
    """Run the OWNING courts and fold verdicts under the checklist keys.
    Pure composition — every law stays in its own court."""
    import groove_court as GC
    import lowend_court as LC
    import harmony_court as HC
    import tension as TN
    rules = rule_block(genre)
    verdicts = {}
    try:
        verdicts["tempo"] = GC.court_tempo(song, genre)
        verdicts["kick"] = GC.court_kick(song, genre)
        verdicts["swing"] = GC.court_swing(song, genre)
    except Exception as e:
        verdicts["groove_error"] = str(e)
    try:
        verdicts["sub_mono"] = LC.court_sub_width(song)
        verdicts["interlock"] = LC.court_interlock(song, genre)
    except Exception as e:
        verdicts["lowend_error"] = str(e)
    try:
        verdicts["progression"] = HC.court_progression(song, genre)
    except Exception as e:
        verdicts["harmony_error"] = str(e)
    try:
        verdicts["arc"] = TN.court_tension_arc(song, genre)
    except Exception as e:
        verdicts["tension_error"] = str(e)
    ok = all(v.get("ok", True) for v in verdicts.values()
             if isinstance(v, dict))
    return {"rules": rules, "verdicts": verdicts, "ok": ok}


def main():
    import argparse
    ap = argparse.ArgumentParser(description="THE GENRE CHECKLIST (wave 30)")
    ap.add_argument("genre")
    ap.add_argument("--song", default=None)
    args = ap.parse_args()
    if args.song:
        out = checklist(json.load(open(args.song)), args.genre)
    else:
        out = rule_block(args.genre)
    print(json.dumps(out, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
