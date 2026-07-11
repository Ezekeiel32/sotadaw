#!/usr/bin/env python3
"""Wave 34: THE SPACE LANE — stereo width, mid/side, mono-compatibility.

The KG had EQ + dynamics (wave 30) but almost nothing on the STEREO FIELD —
the skill every bedroom mix gets wrong. Sources (read via search-verified
excerpts + corroborating pro references, iZotope 503-rate-limited at fetch
2026-07-05): iZotope 'What is mid/side processing' + '8 Common Mistakes in
Mid/Side Mixing'; corroborated by Weapon (mono-sub/stereo-body techno),
Native Instruments (wide basslines), Mastering The Mix (mastering width).

The through-line: WIDTH IS A TRADE against MONO. Every side-channel move must
survive the mono-fold, and the low end must stay centered or it cancels on
club/phone systems. fx_widen (width zone) + master fx are the levers.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG

PROV = ("iZotope Learn (mid/side processing; 8 mid/side mistakes) + Weapon/NI/"
        "Mastering-The-Mix corroboration, read 2026-07-05 via "
        "curated:claude (wave34 space lane)")

TECHNIQUES = {
    "mono_below_120": (
        "keep everything below ~120Hz CENTERED — a stereo/out-of-phase sub "
        "cancels on mono club subs and phone speakers and eats headroom; the "
        "single most important width rule. fx_widen with a low-cut on the side, "
        "or simply pan/write bass + kick dead center [mono-compatibility law]",
        0.85, ["techno", "house", "dnb", "dubstep", "trap", "psytrance"]),
    "mono_check_law": (
        "AUDITION IN MONO with and without your width moves: side-channel content "
        "disappears completely in the fold, and aggressive M/S EQ (the classic "
        "+8dB-lows-on-sides) can make a track barely audible summed — if the mix "
        "collapses, the width was borrowed, not earned [the fold test]",
        0.75, ["house", "techno", "trance", "citypop"]),
    "mid_side_width_control": (
        "width is DYNAMIC, not a static knob: compressing/boosting the MID makes "
        "loud center sounds read wider by contrast; side-only processing adds air "
        "that vanishes in mono (acceptable IF it only sweetens the stereo image) "
        "— treat mid and side as two mixes [mid/side processing]",
        0.7, ["ambient", "citypop", "synthwave", "trance"]),
    "mono_sub_stereo_body": (
        "the techno bass trick: split the bass — a MONO sub (sine, dead center, "
        "<120Hz) carries the weight; a STEREO body (harmonics, saturated, widened "
        "above ~150Hz) carries the character. Club-safe AND wide [Weapon/NI law]",
        0.7, ["techno", "house", "dubstep", "future_bass"]),
    "width_by_arrangement": (
        "the widest mixes earn it in the WRITE, not the widener: hard-pan doubled "
        "parts (two takes L/R), spread a stereo pad wide UNDER a centered lead, "
        "keep the focal element (lead/vocal/kick) center — width is contrast, and "
        "a wall of wide reads as narrow [arrangement-first width]",
        0.65, ["citypop", "synthwave", "ambient", "lofi"]),
    "haas_caution": (
        "the Haas trick (10-40ms delay on one side = instant width) is a MONO "
        "TRAP: the delay comb-filters on the fold. Use it on throwaway ear-candy, "
        "NEVER the bass, kick, or lead — and always fold-check [width without "
        "phase, the caveat]",
        0.5, ["future_bass", "trance", "synthwave"]),
}

if __name__ == "__main__":
    kg = KG()
    added, linked, skipped = 0, 0, []
    for name, (desc, w, genres) in TECHNIQUES.items():
        kg.upsert("Technique", name, PROV, desc=desc, weight=w)
        added += 1
        for g in genres:
            if kg.q(f"MATCH (g:Genre {{name: '{g}'}}) RETURN g.name"):
                kg.link("Genre", g, "USES_TECHNIQUE", "Technique", name, weight=w)
                linked += 1
            else:
                skipped.append(g)
    print(f"wave34 space lane: {added} techniques, {linked} links"
          + (f"; skipped: {sorted(set(skipped))}" if skipped else ""))
