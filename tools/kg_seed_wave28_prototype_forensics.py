#!/usr/bin/env python3
"""Wave 28: PROTOTYPE FORENSICS — why Chezy's browser toy out-grooves our renders.

The pasted goa-act prototype (song_editor_plus_arrangement, 346 bars) was dissected
and the answer is ARRANGEMENT LAWS, not synthesis. Encoded here so every future
skill compile carries them. Provenance: the prototype itself.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG

PROV = "chezy-prototype forensics 2026-07-05 (song_editor goa act, 346 bars)"

T = {
    "long_form_patience": ("tension accumulates in MINUTES, not bars: 12-32-bar sections, "
                           "one journey over 300+ bars; the peak earns itself by arriving late",
                           0.9, ["goa", "psytrance", "trance"]),
    "one_change_per_section": ("every 8-14 bars exactly ONE element enters or leaves — the ear "
                               "tracks a single novelty; two changes at once read as a restart",
                               0.85, ["goa", "psytrance", "trance", "house", "techno"]),
    "rolling_offbeat_bass": ("bass SILENT on the kick, galloping the three 16ths after "
                             "(null,x,x,x) — kick and bass never collide, so the mix pumps "
                             "with ZERO sidechain: the arrangement IS the sidechain",
                             0.95, ["goa", "psytrance"]),
    "filter_journey_layers": ("motion at three timescales AT ONCE: per-note filter env inside "
                              "a per-section cutoff ceiling inside a master LP walk — sweeps "
                              "riding sweeps is the hypnosis",
                              0.9, ["goa", "psytrance", "trance", "acid_house"]),
    "one_root_lattice": ("every voice octave-locked to ONE fundamental (x1 bass, x2 acid, "
                         "x4 pad, x8 lead) — the spectrum fuses into a single instrument; "
                         "voicings that wander break the lattice",
                         0.8, ["goa", "psytrance", "trance"]),
    "glue_comp_grip": ("a MUSICAL bus compressor (~6dB grip, ~200ms release) BEFORE the "
                       "brickwall makes the whole mix breathe with the kick — compliance "
                       "chains measure right but don't GRIP; add the glue stage",
                       0.85, ["goa", "psytrance", "trance", "house", "techno"]),
}

if __name__ == "__main__":
    kg = KG()
    n_links = 0
    for name, (desc, w, genres) in T.items():
        kg.upsert("Technique", name, PROV, desc=desc, weight=w)
        for g in genres:
            if kg.q(f"MATCH (g:Genre {{name: '{g}'}}) RETURN g.name"):
                kg.link("Genre", g, "USES_TECHNIQUE", "Technique", name, weight=w)
                n_links += 1
    print(f"wave28 forensics: {len(T)} laws upserted, {n_links} genre links")
