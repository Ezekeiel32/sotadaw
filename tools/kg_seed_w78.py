#!/usr/bin/env python3
"""KG SEED WAVE 78 — item 152 (r-23): the genre INSTRUMENTATION
whitelists + TUNING maps, verbatim from the research. The court half
already stands (form_court.court_signature reads USES_TECHNIQUE /
CHARACTERIZED_BY names — one resolver); this seeds Technique nodes
whose names CARRY the instrument tokens for the four researched
families, plus the metal drop-tuning ladder as a Genre field.

Idempotent; --verify = query-backs + a court round-trip.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kg  # noqa: E402

PROV = "r-23 instrumentation whitelists w78 (2026-07-16)"

WHITELISTS = {
    "country": ("acoustic_guitar_boom_chick", "telecaster_twang",
                "pedal_steel_bed", "fiddle_lines", "banjo_rolls",
                "mandolin_chop", "high_third_harmony"),
    "citypop": ("rhodes_chords", "slap_bass_16beat", "funk_guitar_chank",
                "synth_brass_stabs"),
    "motown": ("tambourine_backbeat", "handclaps_backbeat",
               "melodic_bass_lines", "horn_stabs_backbeat",
               "glockenspiel_sparkle", "vibes_sparkle"),
    "soul": ("horn_stabs_backbeat", "melodic_bass_lines",
             "tambourine_backbeat", "organ_bed"),
    "metal": ("double_tracked_guitar_wall", "drop_tuned_riff",
              "sample_reinforced_drums"),
}
TUNINGS = {
    "metal": "Drop D (DADGBE) -> Drop C -> Drop B -> Drop A; 7-string "
             "often Drop A; djent 7/8-string",
    "citypop": "standard E; maj7/9 voicings live high on the neck",
    "country": "standard E + capo culture; pedal steel E9 neck",
}


def seed(g):
    have = {r[0] for r in g.q("MATCH (x:Genre) RETURN x.name")}
    n_t = n_l = n_tun = 0
    for genre, toks in WHITELISTS.items():
        if genre not in have:
            g.upsert("Genre", genre, PROV)
            have.add(genre)
        for t in toks:
            g.upsert("Technique", t, PROV, kind="signature_instrument")
            g.link("Genre", genre, "USES_TECHNIQUE", "Technique", t,
                   provenance=PROV)
            n_t += 1
            n_l += 1
    for genre, ladder in TUNINGS.items():
        if genre in have:
            g.upsert("Genre", genre, PROV, tuning=ladder)
            n_tun += 1
    return n_t, n_l, n_tun


def verify(g):
    fails = []

    def check(name, cond):
        print(f"[{'PASS' if cond else 'FAIL'}] {name}")
        if not cond:
            fails.append(name)

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import form_court as FC
    toks = FC.signature_tokens("country")
    check("country tokens reach the court (steel/fiddle/banjo family)",
          any("steel" in t or "fiddle" in t or "banjo" in t
              for t in toks))
    v = FC.court_signature({"tracks": [{"name": "drums", "notes": []},
                                       {"name": "synth", "notes": []}]},
                           "country")
    check("a country take with no steel/fiddle/tele FLAGS",
          any(a["kind"] == "no_signature_voice"
              for a in v.get("advisories", [])))
    v2 = FC.court_signature({"tracks": [
        {"name": "pedal_steel_bed", "notes": []}]}, "country")
    check("the steel lane satisfies the whitelist",
          not v2.get("advisories"))
    row = g.q("MATCH (x:Genre {name:'metal'}) RETURN x.tuning")
    check("metal carries the drop-tuning ladder",
          row and "Drop D" in str(row[0][0]))
    toksc = FC.signature_tokens("citypop")
    check("citypop demands the rhodes", any("rhodes" in t for t in toksc))
    return fails


def main():
    g = kg.KG()
    print(f"[kg_w78] seeded {seed(g)}")
    if "--verify" in sys.argv:
        seed(g)
        fails = verify(g)
        if fails:
            print(f"kg_w78: {len(fails)} RED — {fails}")
            return 1
        print("kg_w78: ALL GREEN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
