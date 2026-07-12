#!/usr/bin/env python3
"""Wave 51: ANTHEM WAVE II — THE HOOKLESS TAIL (2026-07-12, worldclass
ledger 162 'THE REMAINS'). dr03 counted 38 melody-defined genres born with
zero topline; wave 46 covered 11. This wave takes the 12 strongest remaining
MELODY CULTURES — genres a listener identifies BY the lead line — and gives
each its signature one-bar skeleton in [step16, scale_degree, len16] grammar
(the hook engine supplies anchors/climax/cadence on top; the KEY law holds
every note diatonic; HAS_GROOVE supplies the feel — swing_bigband's straight
steps SWING at birth).

Voice picks are identity, not convenience — the roster already carries the
real instruments:

  klezmer            fiddle       the bulgar turn-figure line (violin = core)
  tango              bandoneon    marcato + sincopa, dramatic held arrival
  citypop            ep_bright    the syncopated DX7 pop hook (offbeat pushes)
  afrobeat           sax_section  Fela horn-section calls — space IS the funk
  calypso            steel_pan    rolling stepwise 8th line
  forro              accordion    baiao anticipations on the 'and'
  highlife           clean_chime_guitar  palm-wine sparkle, even 8ths
  swing_bigband      brass_stab   the riff head (arpeggio cell, groove swings it)
  corridos_tumbados  clean_chime_guitar  requinto ornament turns, mid register
  jazzfusion         rhodes       angular 16th head, upbeat octave tail
  melodic_techno     supersaw     sparse held minor motif (the Afterlife arc)
  zouk               ep_bright    the zouk-love bounce

Deliberately NOT touched (hookless is honest there): dub/dub_techno,
minimal_techno, tech/deep/chicago/french house (loop-and-filter cultures),
gabber/hard_techno (kick cultures), bassline/speed_garage (the bass IS the
hook), ambient/drone/orchestral_cinematic (through-composed), big_beat,
future_garage, downtempo, chillwave, balearic, uk_funky, rocksteady, dub,
vaporwave, ebm, acid_house (the 303 bass_params ARE the melody).
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG, esc

PROV = ("curated:claude/2026-07-12 (wave51 anthem II: the hookless tail — "
        "12 melody cultures; ledger 162 THE REMAINS)")

LEADS = {
    "klezmer": {"voice": "fiddle", "octave": 5,
                "steps": [[0, 5, 1], [1, 4, 1], [2, 3, 2], [4, 1, 2],
                          [6, 3, 1], [7, 4, 1], [8, 5, 2], [10, 8, 2],
                          [12, 5, 2], [14, 4, 2]]},
    "tango": {"voice": "bandoneon", "octave": 5,
              "steps": [[0, 3, 3], [3, 5, 1], [4, 6, 4], [8, 5, 2],
                        [10, 4, 2], [12, 1, 4]]},
    "citypop": {"voice": "ep_bright", "octave": 5,
                "steps": [[0, 5, 2], [3, 6, 1], [4, 5, 2], [7, 3, 1],
                          [8, 4, 2], [11, 5, 1], [12, 6, 2], [14, 5, 2]]},
    "afrobeat": {"voice": "sax_section", "octave": 4,
                 "steps": [[2, 1, 1], [4, 3, 1], [6, 4, 2], [10, 5, 1],
                           [12, 4, 1], [14, 3, 2]]},
    "calypso": {"voice": "steel_pan", "octave": 5,
                "steps": [[0, 1, 2], [2, 3, 2], [4, 5, 2], [6, 6, 2],
                          [8, 5, 2], [10, 3, 2], [12, 4, 2], [14, 2, 2]]},
    "forro": {"voice": "accordion", "octave": 5,
              "steps": [[0, 1, 2], [3, 3, 1], [4, 5, 2], [7, 6, 1],
                        [8, 5, 2], [11, 4, 1], [12, 3, 2], [14, 2, 2]]},
    "highlife": {"voice": "clean_chime_guitar", "octave": 5,
                 "steps": [[0, 3, 1], [2, 5, 1], [4, 8, 1], [6, 5, 1],
                           [8, 6, 1], [10, 5, 1], [12, 3, 1], [14, 5, 1]]},
    "swing_bigband": {"voice": "brass_stab", "octave": 4,
                      "steps": [[0, 1, 1], [2, 3, 1], [4, 5, 1], [6, 8, 2],
                                [8, 1, 1], [10, 3, 1], [12, 5, 4]]},
    "corridos_tumbados": {"voice": "clean_chime_guitar", "octave": 4,
                          "steps": [[0, 5, 2], [2, 4, 1], [3, 3, 1], [4, 1, 2],
                                    [8, 3, 2], [10, 4, 1], [11, 5, 1],
                                    [12, 3, 2], [14, 2, 1]]},
    "jazzfusion": {"voice": "rhodes", "octave": 5,
                   "steps": [[0, 1, 1], [1, 3, 1], [2, 5, 1], [4, 6, 2],
                             [7, 5, 1], [8, 4, 1], [10, 3, 1], [12, 5, 2],
                             [15, 8, 1]]},
    "melodic_techno": {"voice": "supersaw", "octave": 4,
                       "steps": [[0, 1, 4], [6, 3, 2], [8, 4, 4], [14, 6, 2]]},
    "zouk": {"voice": "ep_bright", "octave": 5,
             "steps": [[0, 5, 2], [2, 6, 1], [4, 5, 2], [8, 3, 2],
                       [10, 4, 1], [12, 5, 3]]},
}

if __name__ == "__main__":
    kg = KG()
    done, miss = [], []
    for g, lead in LEADS.items():
        rows = kg.q(f"MATCH (g:Genre {{name:'{esc(g)}'}})-[:CHARACTERIZED_BY]->"
                    "(p:PatternArchetype) WHERE p.grid IS NOT NULL RETURN id(p), p.grid")
        if not rows:
            miss.append(g)
            continue
        pid, grid = rows[0]
        d = json.loads(grid)
        if (d.get("lead") or {}).get("steps"):
            done.append(f"{g} (already has a hook — untouched)")
            continue
        d["lead"] = lead
        kg.q(f"MATCH (p:PatternArchetype) WHERE id(p) = {int(pid)} "
             f"SET p.grid = '{esc(json.dumps(d))}', "
             f"p.provenance = p.provenance + ' | {esc(PROV)}'")
        done.append(f"{g}: {lead['voice']} oct{lead['octave']} x{len(lead['steps'])} steps")
    print(f"wave51: {len(done)} anthems\n  " + "\n  ".join(done)
          + (f"\n  MISSING: {miss}" if miss else ""))
