#!/usr/bin/env python3
"""Wave 43: THE RAP FORM + the remaining uncontested form families (2026-07-12).

The worldclass ledger (docs/WORLDCLASS_LEDGER_2026_07_12.md, campaign #2 + the
forms CRIT) measured: 62 genres carried no form_family and fell to the EDM
twin-DROP form — every rap genre arranged club drops with risers; lofi/flamenco/
dub got riser whoosh + crash impacts. Wave 42 took the beatless + rock-kin
uncontested set and left the rap cluster OPEN for a purpose-built form. This
wave delivers it:

  rap  — NEW family (arrange.py RAP_FORM): 16-bar verses over the FULL beat
         (rap verses never thin to a heartbeat; the vocal carries the contrast),
         8-bar hooks at full energy, one stripped bridge, no drops, no risers.
         Includes the trap-kin set that had BORROWED "song" (rage/plugg/pluggnb/
         jersey_drill — a 4-bar pop bridge grammar is not rap's).
  loop — NEW family (arrange.py LOOP_FORM): beat-tape/chill cultures where the
         loop IS the song — themes cycle with texture variation, nothing drops.
  song — the ledger's reggae-family + folk/trad calls (dub/dancehall/zouk/soca/
         kompa/reggaeton verse-chorus vocal musics; flamenco/mariachi/tango/
         klezmer/celtic/gnawa/forro/samba trad song forms; jazzfusion mirrors
         jazz=song; corridos_tumbados are ballads).
  club — the unassigned genres a DJ actually beatmatches (they were only ever
         "right" on the drop-form by accident; now it's a decision with
         provenance, and the fail-closed router needs it to be explicit).

Still OPEN (contested, needs listening/desk): afrobeat (Fela long-form groove),
breakcore/idm (collage/through?), witch_house, nightcore.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG

PROV = ("curated:claude/2026-07-12 (wave43 THE RAP FORM; ledger dr24 campaign #2: "
        "13 rap genres arranged EDM club drops; probe receipt: arrange --genre "
        "trap|boombap|lofi|dub all produced intro/build/DROP/break/DROP2/outro "
        "with riser+crash tracks)")

FAM = {}
for g in ("trap", "hiphop", "boombap", "drill", "sexy_drill", "phonk",
          "driftphonk", "memphis_rap", "gfunk", "latin_trap", "crunk",
          "rage", "plugg", "pluggnb", "jersey_drill"):
    FAM[g] = "rap"
for g in ("lofi", "downtempo", "vaporwave"):
    FAM[g] = "loop"
for g in ("dub", "dancehall", "zouk", "soca", "kompa", "reggaeton",
          "flamenco", "mariachi", "tango", "klezmer", "celtic", "gnawa",
          "forro", "samba", "corridos_tumbados", "jazzfusion"):
    FAM[g] = "song"
for g in ("big_beat", "breakbeat_hardcore", "gabber", "happy_hardcore",
          "hard_techno", "tech_house", "minimal_techno", "french_house",
          "italo_disco", "ebm", "industrial", "gqom", "singeli", "kuduro",
          "footwork", "future_garage", "uk_funky", "moombahton",
          "future_bass", "balearic", "hardwave", "baile_funk",
          "baltimore_club", "bounce", "miami_bass", "ghettotech", "dembow"):
    FAM[g] = "club"

if __name__ == "__main__":
    kg = KG()
    done, missing = 0, []
    for g, fam in FAM.items():
        if kg.q(f"MATCH (g:Genre {{name:'{g}'}}) RETURN g.name"):
            kg.upsert("Genre", g, PROV, form_family=fam)
            done += 1
        else:
            missing.append(g)
    print(f"wave43: {done} genres carry a form family (rap 15 / loop 3 / song 16 / club 27)"
          + (f" (missing from graph: {missing})" if missing else ""))
