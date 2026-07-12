#!/usr/bin/env python3
"""Wave 47: THE WORLD KIT part 1 (2026-07-12) — ledger dr28: "No signature-
percussion lanes exist — every Latin/Afro/World groove collapses to a Western
kit." The voices now exist (shaker/clave/conga/cowbell, headroom-certified);
this wave puts the CELLS in the DNA.

  salsa       the deep fix: 2-bar clave grid. Son clave 3-2 on the clave lane
              (the timeline), campana quarters, conga marcha with open-tone
              accents, cascara on the rim — and the BACKBEAT SNARE REMOVED
              (salsa has no backbeat; that was the caricature). Bass goes
              "tumbao": and-of-2 fifth + anticipated beat-4 root, downbeat
              EMPTY (dr28: root-on-1 was the opposite of the culture).
  moombahton  the corrupted dembow cell healed: snare [3,7,11,15] was a plain
              offbeat — the tresillo is [3,6,11,14] (reggaeton's is correct).
  amapiano    the shaker carpet (16ths, offbeat-8th accents) beside the log.
  afrobeats   the shaker carpet with 8th accents.
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG, esc

PROV = ("curated:claude/2026-07-12 (wave47 world kit: son clave 3-2, tumbao "
        "anticipation, dembow tresillo heal, shaker carpets; ledger dr28)")


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


def fix_salsa(d):
    d["bars"] = 2
    d["kick"] = [7, 15, 23, 31]
    d.pop("snare", None)
    d["hat"] = [0, 2, 3, 5, 7, 8, 10, 11, 13, 15,
                16, 18, 19, 21, 23, 24, 26, 27, 29, 31]
    d["rim"] = [0, 3, 4, 7, 8, 11, 12, 14, 16, 19, 20, 23, 24, 27, 28, 30]
    d["clave"] = [0, 6, 12, 20, 24]
    d["cowbell"] = [0, 4, 8, 12, 16, 20, 24, 28]
    d["conga"] = [3, 6, 7, 11, 14, 15, 19, 22, 23, 27, 30, 31]
    d["bass_style"] = "tumbao"
    vel = d.setdefault("vel", {})
    vel.pop("snare", None)
    vel["cowbell"] = {"0": 0.85, "16": 0.85}
    vel["conga"] = {"6": 0.85, "7": 0.85, "22": 0.85, "23": 0.85}
    vel["clave"] = {str(s): 0.8 for s in (0, 6, 12, 20, 24)}
    # the fill's snare roll stays (the abanico turnaround) but voiced as a
    # HIGH DRUM (timbale territory), never the machine backbeat snare
    d["snare_voice"] = "conga"
    d["snare_pitch"] = 62


def fix_moombahton(d):
    d["snare"] = [3, 6, 11, 14]


def add_shaker(accents):
    def fn(d):
        d["shaker"] = list(range(16))
        d.setdefault("vel", {})["shaker"] = {
            str(i): (0.6 if i in accents else 0.42) for i in range(16)}
    return fn


if __name__ == "__main__":
    kg = KG()
    done = []
    if edit_grid(kg, "salsa", fix_salsa):
        done.append("salsa: 2-bar clave grid + tumbao (backbeat snare removed)")
    if edit_grid(kg, "moombahton", fix_moombahton):
        done.append("moombahton: dembow tresillo healed [3,6,11,14]")
    if edit_grid(kg, "amapiano", add_shaker({2, 6, 10, 14})):
        done.append("amapiano: shaker carpet, offbeat-8th accents")
    if edit_grid(kg, "afrobeats", add_shaker({0, 4, 8, 12})):
        done.append("afrobeats: shaker carpet, 8th accents")
    print(f"wave47: {len(done)}\n  " + "\n  ".join(done))
