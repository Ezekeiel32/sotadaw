#!/usr/bin/env python3
"""KG SEED: THE VOCAL TARGET TABLE (backlog wave 24 — R-12 item 013).

VocalTarget node per genre (parallel to MixTarget), family-routed from
r-12's ready-to-encode presets. Fields map 1:1 onto the project's fx:
comp (fx_comp attack/release/ratio), deess (fx_deess freq/gr), tune
(retune style/speed), reverb (type/decay/predelay), delay (division of
the BPM — quarter_ms = 60000/bpm law), saturation (fx_saturate
drive/mix — PARALLEL mix 0.3-0.5, never fully wet on a lead), doubling
(level/detune/intervals — symbolic lanes, never an audio doubler),
adlib vocabulary hints.

Provenance: r-12.json (chain order + bimodal compression + genre preset
tables), wave 24 (2026-07-15). Idempotent.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kg  # noqa: E402

PROV = "backlog-w24 vocal targets (R-12, 2026-07-15)"

# family -> the ready-to-encode preset (r-12 findings 1/10/11/4/5/6/7)
PRESETS = {
    "trap": dict(comp_attack_ms=3, comp_release_ms=60, comp_ratio=6.0,
                 deess_hz=6000, deess_gr_db=3.0,
                 tune_style="tpain", retune_ms=0,
                 reverb_type="room", reverb_decay_s=0.8, predelay_ms=20,
                 delay_division="1/4", delay_feedback_pct=50,
                 sat_drive_db=8.0, sat_mix=0.4,
                 double_level_db=-6.0, double_detune_cents=8,
                 double_intervals="unison,octave_up",
                 adlib_vocab="yeah,uh,skrrt,gang,okay,letsgo",
                 adlib_per_section=3),
    "pop": dict(comp_attack_ms=8, comp_release_ms=80, comp_ratio=4.0,
                deess_hz=6500, deess_gr_db=3.0,
                tune_style="hard", retune_ms=10,
                reverb_type="plate", reverb_decay_s=1.8, predelay_ms=30,
                delay_division="3/16", delay_feedback_pct=35,
                sat_drive_db=6.0, sat_mix=0.35,
                double_level_db=-5.0, double_detune_cents=7,
                double_intervals="unison,third_up",
                adlib_vocab="", adlib_per_section=1),
    "rnb": dict(comp_attack_ms=25, comp_release_ms=170, comp_ratio=2.5,
                deess_hz=7000, deess_gr_db=2.5,
                tune_style="natural", retune_ms=40,
                reverb_type="hall", reverb_decay_s=3.5, predelay_ms=45,
                delay_division="1/8", delay_feedback_pct=30,
                sat_drive_db=4.0, sat_mix=0.3,
                double_level_db=-6.0, double_detune_cents=6,
                double_intervals="unison,third_up,sixth_up",
                adlib_vocab="ooh,yeah,baby", adlib_per_section=2),
    "rock": dict(comp_attack_ms=15, comp_release_ms=120, comp_ratio=4.0,
                 deess_hz=5500, deess_gr_db=2.5,
                 tune_style="transparent", retune_ms=60,
                 reverb_type="plate", reverb_decay_s=2.2, predelay_ms=25,
                 delay_division="slapback_90ms", delay_feedback_pct=0,
                 sat_drive_db=10.0, sat_mix=0.45,
                 double_level_db=-4.0, double_detune_cents=10,
                 double_intervals="unison",
                 adlib_vocab="", adlib_per_section=0),
    "folk": dict(comp_attack_ms=30, comp_release_ms=180, comp_ratio=2.5,
                 deess_hz=6000, deess_gr_db=2.0,
                 tune_style="transparent", retune_ms=70,
                 reverb_type="room", reverb_decay_s=1.2, predelay_ms=30,
                 delay_division="slapback_90ms", delay_feedback_pct=0,
                 sat_drive_db=3.0, sat_mix=0.25,
                 double_level_db=-8.0, double_detune_cents=5,
                 double_intervals="unison",
                 adlib_vocab="", adlib_per_section=0),
    "edm": dict(comp_attack_ms=5, comp_release_ms=70, comp_ratio=5.0,
                deess_hz=6500, deess_gr_db=3.0,
                tune_style="hard", retune_ms=5,
                reverb_type="plate", reverb_decay_s=1.5, predelay_ms=25,
                delay_division="3/16", delay_feedback_pct=40,
                sat_drive_db=7.0, sat_mix=0.4,
                double_level_db=-5.0, double_detune_cents=9,
                double_intervals="unison,octave_up",
                adlib_vocab="", adlib_per_section=1),
    "gospel": dict(comp_attack_ms=20, comp_release_ms=150, comp_ratio=3.0,
                   deess_hz=6500, deess_gr_db=2.5,
                   tune_style="natural", retune_ms=45,
                   reverb_type="hall", reverb_decay_s=3.0, predelay_ms=40,
                   delay_division="1/8", delay_feedback_pct=25,
                   sat_drive_db=4.0, sat_mix=0.3,
                   double_level_db=-4.0, double_detune_cents=6,
                   double_intervals="unison,third_up,fifth_up",
                   adlib_vocab="oh,yeah,hallelujah", adlib_per_section=2),
}
ROUTE = (
    ("trap", ("trap", "drill", "phonk", "grime", "rap", "hiphop", "hip_hop",
              "memphis", "crunk", "boombap", "reggaeton", "dancehall")),
    ("gospel", ("gospel", "soul", "motown", "doo_wop", "doowop", "choir")),
    ("rnb", ("rnb", "r_b", "ballad", "neo_soul")),
    ("rock", ("rock", "metal", "punk", "grunge", "indie")),
    ("folk", ("folk", "country", "singer", "acoustic", "americana",
              "bluegrass")),
    ("edm", ("edm", "house", "techno", "trance", "garage", "dnb",
             "dubstep", "electro", "dance", "hardstyle")),
)


def preset_for(name):
    norm = str(name).lower().replace("-", "_").replace(" ", "_")
    for fam, keys in ROUTE:
        if any(k in norm for k in keys):
            return fam
    return "pop"


def main():
    g = kg.KG()
    genres = [r[0] for r in g.q("MATCH (x:Genre) RETURN x.name")]
    if not genres:
        print("kg_seed_vocal: no Genre nodes (is sotadaw-kg up?)")
        return 1
    n = 0
    for name in genres:
        fam = preset_for(name)
        attrs = dict(PRESETS[fam], vocal_family=fam)
        g.upsert("VocalTarget", name, PROV, **attrs)
        g.link("Genre", name, "HAS_VOCAL_TARGET", "VocalTarget", name, provenance=PROV)
        n += 1
    print(f"kg_seed_vocal: {n} VocalTarget nodes "
          "(chain numbers, doubling policy, ad-lib vocab)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
