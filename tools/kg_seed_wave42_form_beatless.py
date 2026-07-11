#!/usr/bin/env python3
"""Wave 42: FORM FAMILY for the unambiguous form-less genres (2026-07-11).

74 genres carried no form_family and fell to arrange.py's generic FORM — the
drop-form (intro/build/drop/break/drop2/outro). Probe receipts: ambient, drone
and orchestral_cinematic all arranged with CLUB DROPS. This wave assigns only
the UNCONTESTED families:

  through_composed — beatless/unfolding musics (the Eno/film-cue tradition:
    texture accumulates to a climax and resolves; a drop betrays the genre).
  song — verse/chorus band musics whose parents/kin already carry "song"
    (rock=song since wave41; metal/punk/shoegaze are the same grammar; ska/
    rocksteady mirror reggae=song; swing_bigband mirrors jazz=song; triphop is
    Massive Attack/Portishead songcraft; new_jack_swing mirrors rnb=song).

Contested calls stay OPEN for the deep-research verdicts: the rap cluster
(trap/drill/phonk/boombap... wants a purpose-built verse/hook form, not a
borrowed one), latin/world cells, and loop-culture genres (lofi/vaporwave/
dub/idm) where the generic loop form may actually be right.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG

PROV = ("curated:claude/2026-07-11 (wave42 beatless+band forms; probe receipt: "
        "ambient/drone/orchestral_cinematic arranged club drops via generic FORM)")

FAM = {}
for g in ("ambient", "drone", "orchestral_cinematic"):
    FAM[g] = "through_composed"
for g in ("metal", "punk", "post_punk", "shoegaze", "triphop", "ska",
          "rocksteady", "swing_bigband", "new_jack_swing"):
    FAM[g] = "song"

if __name__ == "__main__":
    kg = KG()
    done, missing = 0, []
    for g, fam in FAM.items():
        if kg.q(f"MATCH (g:Genre {{name:'{g}'}}) RETURN g.name"):
            kg.upsert("Genre", g, PROV, form_family=fam)
            done += 1
        else:
            missing.append(g)
    print(f"wave42: {done} genres carry a form family"
          + (f" (missing from graph: {missing})" if missing else ""))
