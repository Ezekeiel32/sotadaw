#!/usr/bin/env python3
"""Wave 49: THE WORLD KIT part 2 (2026-07-12) — cumbia, samba, bossanova,
soca cells + the gqom triplet groove. Same discipline as wave 47: the cell
is the law, the western backbeat leaves where the culture never had one.

  cumbia     was a rock kit (kick 1&3, backbeat snare). Now: kick quarters,
             LLAMADOR conga on the offbeats [2,6,10,14] (THE cumbia cell),
             guiro-rhythm shaker [0,4,6,8,12,14], backbeat snare REMOVED.
  samba      surdo truth: LOW conga (pitch 48) answers on beats 2&4 over the
             kick's 1&3; ganza shaker carpet; backbeat snare REMOVED (the
             existing telecoteco hat cell [0,3,6,10,13] stays — it was right).
  bossanova  the rim rode SON clave [.,20,24] — the bossa cell ends 22,26
             (the Jobim displacement). Soft ganza 16ths joined.
  soca       the ENGINE ROOM: cowbell 8ths with quarter accents (soca keeps
             its big backbeat snare — that one is culture-true).
  gqom       a 16-slot grid cannot write triplets — the TRIPLET PULL rides a
             groove profile: e/a slots drag toward the 1/3 positions
             (+0.083/+0.167/-0.083 per beat), percs/hats lope while kick+bass
             stay anchored (the atlas anchor law).
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG, esc

PROV = ("curated:claude/2026-07-12 (wave49 world kit 2: llamador/surdo/bossa-"
        "clave/engine-room cells + gqom triplet-pull groove; ledger dr28)")


def edit_grid(kg, genre, fn):
    rows = kg.q(f"MATCH (g:Genre {{name:'{esc(genre)}'}})-[:CHARACTERIZED_BY]->"
                "(p:PatternArchetype) WHERE p.grid IS NOT NULL RETURN id(p), p.grid")
    if not rows:
        return False
    pid, grid = rows[0]
    d = json.loads(grid)
    fn(d)
    kg.q(f"MATCH (p:PatternArchetype) WHERE id(p) = {int(pid)} "
         f"SET p.grid = '{esc(json.dumps(d))}', "
         f"p.provenance = p.provenance + ' | {esc(PROV)}'")
    return True


def fix_cumbia(d):
    d["kick"] = [0, 4, 8, 12]
    d.pop("snare", None)
    d["conga"] = [2, 6, 10, 14]
    d["shaker"] = [0, 4, 6, 8, 12, 14]
    vel = d.setdefault("vel", {})
    vel.pop("snare", None)
    vel["conga"] = {str(s): 0.8 for s in (2, 6, 10, 14)}
    vel["shaker"] = {"0": 0.62, "8": 0.62, "4": 0.45, "6": 0.45, "12": 0.45, "14": 0.45}
    # the fill's snare roll re-voiced as a high drum (tambora territory) —
    # the same salsa-class heal: no machine snare anywhere in cumbia
    d["snare_voice"] = "conga"
    d["snare_pitch"] = 60


def fix_samba(d):
    d.pop("snare", None)
    d["conga"] = [4, 12]
    d["conga_pitch"] = 48            # the surdo speaks LOW
    d["shaker"] = list(range(16))
    vel = d.setdefault("vel", {})
    vel.pop("snare", None)
    vel["conga"] = {"4": 0.9, "12": 0.95}
    vel["shaker"] = {str(i): (0.55 if i % 4 == 2 else 0.4) for i in range(16)}


def fix_bossa(d):
    d["rim"] = [0, 6, 12, 22, 26]    # the Jobim displacement (was son 20,24)
    d["steady_lanes"] = ["rim"]      # the rim IS the clave here — never breathes
    d["shaker"] = list(range(0, 32, 2))
    vel = d.setdefault("vel", {})
    vel["shaker"] = {str(i): 0.35 for i in range(0, 32, 2)}


def fix_soca(d):
    d["cowbell"] = [0, 2, 4, 6, 8, 10, 12, 14]
    d.setdefault("vel", {})["cowbell"] = {"0": 0.8, "4": 0.8, "8": 0.8, "12": 0.8,
                                          "2": 0.55, "6": 0.55, "10": 0.55, "14": 0.55}


GQOM_PROFILE = {
    "prov": PROV,
    # per beat [down, e, and, a]: e/a drag toward the triplet thirds; the
    # "and" pulls hardest (+0.167 -> the 2/3 position = the gqom lope)
    "off": [0, 0.083, 0.167, -0.083] * 4,
    "vel": [1.0, 0.5, 0.85, 0.5] * 4,
}

if __name__ == "__main__":
    kg = KG()
    done = []
    for g, fn in (("cumbia", fix_cumbia), ("samba", fix_samba),
                  ("bossanova", fix_bossa), ("soca", fix_soca)):
        if edit_grid(kg, g, fn):
            done.append(g)
    # the gqom triplet groove: store profile + HAS_GROOVE edge
    store_p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "library", "grooves.json")
    st = json.load(open(store_p))
    if "gqom_triplet" not in st:
        st["gqom_triplet"] = GQOM_PROFILE
        tmp = store_p + ".w~"
        json.dump(st, open(tmp, "w"), indent=0)
        os.replace(tmp, store_p)
    kg.q("MERGE (gr:Groove {name:'gqom_triplet'}) "
         f"SET gr.provenance = '{esc(PROV)}'")
    kg.q("MATCH (g:Genre {name:'gqom'}), (gr:Groove {name:'gqom_triplet'}) "
         "MERGE (g)-[:HAS_GROOVE]->(gr)")
    done.append("gqom (triplet-pull groove)")
    print(f"wave49: {', '.join(done)}")
