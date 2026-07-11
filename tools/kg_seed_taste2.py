#!/usr/bin/env python3
"""Taste wave 2 (§7.5 'DO IT ALL', 2026-07-07): the VOICING SWEEP — 86 genres that
rode the uniform default (smooth 48-70) get their documented chord-voicing idiom.

Style vocabulary = what voicing.voice_pcs implements TODAY (smooth = voice-led
close, triad = melodic-lead triads, open = root-low + spread tenth, drop2 = the
sectional voicing). Register (lo..hi MIDI) is the genre fingerprint: a metal bed
lives 38-58, a future-bass stab stack 55-80. Groundings per family block below —
documented idiom, not vibes. NULL-guarded: never clobbers an existing curated
voicing. Provenance on every write.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG, esc

PROV = "curated:claude/2026-07-07 (taste wave 2 — voicing sweep, documented idiom per family)"

V = {}
def fam(style, lo, hi, names):
    for n in names:
        V[n] = {"style": style, "lo": lo, "hi": hi}

# power-chord beds: root+5 low close — the wall lives low (metal down-tuned lower)
fam("smooth", 38, 58, ["metal"])
fam("smooth", 40, 62, ["punk", "rock"])
fam("smooth", 43, 64, ["post_punk", "industrial", "ebm"])
# sampled-soul low-mid keys: chopped rhodes/soul registers (MPC-era comping)
fam("smooth", 45, 64, ["hiphop", "boombap", "lofi", "triphop", "downtempo",
                       "new_jack_swing", "gfunk", "crunk"])
fam("smooth", 43, 62, ["sexy_drill", "memphis_rap"])
# smeared night-time UK chords (Burial-class pads sit dark and close)
fam("smooth", 45, 66, ["future_garage", "jungle", "dubstep"])
# tight funk/afro comping: terse stabs in the tenor range (E9-shell idiom)
fam("smooth", 48, 68, ["funk", "afrobeat", "zouk", "kompa"])
# sectional drop2: the documented big-band/fusion voicing
fam("drop2", 50, 74, ["swing_bigband", "jazzfusion"])
# stab families: percussive triads (rave/house/club stab idiom)
fam("triad", 50, 70, ["acid_house", "tech_house", "bassline", "uk_funky",
                      "bounce", "baltimore_club", "jerseyclub"])
fam("triad", 52, 72, ["french_house", "italo_disco", "soca", "ska"])
fam("triad", 48, 68, ["electro", "ghettotech", "miami_bass", "footwork",
                      "reggaeton", "dembow", "moombahton", "baile_funk"])
fam("triad", 52, 74, ["gabber", "happy_hardcore", "breakbeat_hardcore", "nightcore"])
fam("triad", 48, 70, ["big_beat", "breaks", "breakcore", "kuduro", "singeli"])
fam("triad", 45, 66, ["grime", "hard_techno"])
fam("triad", 48, 66, ["minimal_techno"])
fam("triad", 43, 62, ["gqom"])                      # gqom = dark sparse stabs, low
fam("triad", 50, 72, ["goa", "psytrance", "klezmer", "forro", "samba"])
fam("triad", 52, 76, ["mariachi"])                  # vihuela strum register
fam("triad", 45, 68, ["corridos_tumbados", "country"])
fam("triad", 45, 70, ["rocksteady"])                # bubble-organ triad inversions
# open spreads: root low, wide tenth — pads/strings/anthems/orchestration spacing
fam("open", 52, 79, ["trance", "hardwave"])
fam("open", 55, 79, ["bigroom"])
fam("open", 55, 80, ["future_bass", "kpop"])        # supersaw stacks live high+wide
fam("open", 50, 74, ["balearic", "vaporwave", "disco", "italo_disco"])
fam("open", 48, 76, ["shoegaze", "idm"])
fam("open", 40, 76, ["drone"])
fam("open", 40, 66, ["witch_house", "flamenco"])    # flamenco = open low guitar voicings
fam("open", 45, 81, ["orchestral_cinematic"])       # orchestral open spacing law
fam("open", 45, 68, ["dub_techno"])                 # the dub chord: minor, wide, filtered
fam("open", 48, 72, ["celtic"])                     # DADGAD-class open strings
fam("open", 45, 70, ["indie_rock"])                 # add9/open-string indie beds
fam("smooth", 45, 70, ["tango"])                    # bandoneon close-position comping
fam("smooth", 36, 55, ["gnawa"])                    # guembri register: low riff bed
fam("smooth", 45, 64, ["blues"])                    # comping shells/close, tenor range


def main():
    kg = KG()
    names = {r[0] for r in kg.q("MATCH (g:Genre) RETURN g.name")}
    have = {r[0] for r in kg.q("MATCH (g:Genre) WHERE g.voicing IS NOT NULL RETURN g.name")}
    done, kept, absent = 0, [], []
    for g, v in sorted(V.items()):
        if g not in names:
            absent.append(g)
            continue
        if g in have:                    # NULL-guard: curated voicings are law
            kept.append(g)
            continue
        kg.q(f"MATCH (g:Genre {{name: '{esc(g)}'}}) "
             f"SET g.voicing = '{esc(json.dumps(v))}', g.voicing_prov = '{esc(PROV)}'")
        done += 1
    print(f"taste wave 2: voicing set on {done} genres"
          + (f"; kept existing on {len(kept)}" if kept else "")
          + (f"; absent: {absent}" if absent else ""))
    left = kg.q("MATCH (g:Genre) WHERE g.voicing IS NULL RETURN g.name")
    print(f"still default-voiced: {sorted(r[0] for r in left)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
