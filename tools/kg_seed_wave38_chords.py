#!/usr/bin/env python3
"""Wave 38: CHORD DNA — world/folk + anthem/atmosphere tail (f148).

Grounding (own search, stamp f148): klezmer freygish = minor home + V major
(i-V shuttle); big-room festival = 1-2 chord minor VAMPS (Animals-class, cited)
while the anthem lane runs i-III-VII-VI (Levels-class, cited); merengue I-V,
trance/psy/acid/electro = static-by-form vamps. afro_pocket rides a documented
modal i-VII shuttle (cited 2026-07-07: afro-house/afrobeats progression guides
name i-VII(-VI) Dorian modal shuttles as the canon — samplesoundmusic.com
afro-house progressions; soundfly flypaper afrobeat modal-vamp analysis;
beatstorapon afrobeats production guide). Wave25 grammar; idempotent.
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG

PROV = ("curated:claude/2026-07-06 (wave38 world/anthem canon; freygish+bigroom-vamp"
        "+levels-anthem cited f148; afro_pocket i-VII CITED 2026-07-07: samplesound"
        " afro-house i-VII(-VI) Dorian guide + soundfly afrobeat modal-vamp analysis)")

C = {
    # world / folk
    "freylekh_bounce":  [[0, 1], [1, 5], [2, 1], [3, 5]],   # freygish i-V
    "tambora_gallop":   [[0, 1], [2, 5]],                   # merengue I-V
    "surdo_two":        [[0, 1], [1, 5], [2, 1], [3, 5]],   # samba I-V two-feel
    "reel_lilt":        [[0, 1], [1, 7], [2, 1], [3, 5]],   # celtic I-bVII-I-V
    "tuba_sway":        [[0, 1], [1, 5], [2, 4], [3, 5]],   # corridos I-V-IV-V
    "zouk_machine":     [[0, 1], [1, 6], [2, 7], [3, 6]],
    "afro_pocket":      [[0, 1], [2, 7]],                   # i-VII modal shuttle (cited 2026-07-07)
    "kuduro_carnival":  [[0, 1], [2, 7]],
    "allen_ghosts":     [[0, 1]],                           # afrobeat: ONE dominant vamp (Allen/Fela law)
    "krakeb_shuffle":   [[0, 1]],                           # gnawa: one-mode trance
    "gqom_dark":        [[0, 1]],                           # gqom IS drums
    "singeli_sprint":   [[0, 1]],
    # anthems vs vamps (the cited split)
    "happy_bounce":     [[0, 1], [1, 6], [2, 3], [3, 7]],   # i-VI-III-VII anthem
    "eurodance_stomp":  [[0, 1], [1, 6], [2, 3], [3, 7]],
    "hard_pocket":      [[0, 1], [1, 6], [2, 7], [3, 6]],   # hardstyle i-VI-VII-VI
    "hyper_burst":      [[0, 1], [1, 5], [2, 6], [3, 4]],   # hyperpop = pop four, sped
    "nightcore_sped":   [[0, 1], [1, 5], [2, 6], [3, 4]],
    "festival_four":    [[0, 1]],                           # big-room vamp (Animals-class, cited)
    "cinematic_pulse":  [[0, 1], [1, 6], [2, 3], [3, 7]],
    "melodic_sparse":   [[0, 1], [1, 7], [2, 6], [3, 7]],   # melodic techno drift
    "prog_roll":        [[0, 1], [1, 7], [2, 6], [3, 7]],
    "hardwave_halftime":[[0, 1], [2, 6]],
    # atmosphere / broken / downtempo
    "gaze_wash":        [[0, 1], [1, 6], [2, 4], [3, 5]],   # I-vi-IV-V wash
    "washed_backbeat":  [[0, 1], [2, 4]],                   # chillwave I-IV shuttle
    "balearic_lazy":    [[0, 1], [2, 4]],
    "trip_drag":        [[0, 1], [2, 4]],
    "down_drag":        [[0, 1], [2, 7]],
    "fg_drift":         [[0, 1], [2, 7]],
    "broken_grid":      [[0, 2], [2, 5]],                   # bruk ii-V dorian
    "njs_swingbeat":    [[0, 2], [2, 5]],                   # new jack ii-V
    "bigband_ride":     [[0, 2], [1, 5], [2, 1], [3, 6]],   # ii-V-I-vi
    "fusion_sixteen":   [[0, 2], [1, 5], [2, 1], [3, 6]],
    # static-by-form
    "psy_fullon":       [[0, 1]],
    "goa_layers":       [[0, 1]],
    "acid_shuffle":     [[0, 1]],
    "dubtech_pulse":    [[0, 1]],
    "electro_break":    [[0, 1]],
    "mia_electro":      [[0, 1]],
    "bigbeat_swagger":  [[0, 1], [2, 4]],
    "funky_snap":       [[0, 1], [2, 4]],
    "funky_lift":       [[0, 1], [2, 4]],
    "breakcore_chaos":  [[0, 1]],
    "slowed_quarters":  [[0, 1]],
    "jersey_kicks":     [[0, 1]],
    "bmore_cell":       [[0, 1]],
    "hardcore_breaks":  [[0, 1], [2, 6]],
    "jpop_drive":       [[0, 4], [1, 5], [2, 3], [3, 6]],
}

if __name__ == "__main__":
    kg = KG()
    done = skip = miss = 0
    for pname, prog in C.items():
        rows = kg.q(f"MATCH (p:PatternArchetype {{name: '{pname}'}}) RETURN p.grid")
        if not rows or not rows[0][0]:
            print(f"  {pname}: MISSING"); miss += 1; continue
        grid = json.loads(rows[0][0])
        if "chords" in grid:
            skip += 1; continue
        grid["chords"] = prog
        kg.upsert("PatternArchetype", pname, PROV, grid=json.dumps(grid))
        done += 1
    print(f"wave38: {done} seeded, {skip} already had, {miss} missing")
