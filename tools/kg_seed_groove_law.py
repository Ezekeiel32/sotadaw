#!/usr/bin/env python3
"""KG SEED: THE GROOVE LAW (backlog wave 14 — R-21/R-22/R-24 items).

Idempotent Genre-field upserts into FalkorDB from the groove court's
verified tables: bpm_min/bpm_max (micro-ranges), kick_topology
(4x4|no_4x4|free), backbeat (snare24|snare3|free), swing_lo/swing_hi,
drum_machine (909|808|707|breaks|sp1200|acoustic|kit).

Provenance: r-{21,22,24}.json numbers tables via groove_court, wave 14.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kg  # noqa: E402
import groove_court as GC  # noqa: E402

PROV = "backlog-w14 groove law (R-21/R-22/R-24, 2026-07-14)"

# R-21 drum-machine authenticity routing (157)
DRUM_MACHINE = (
    (("house", "chicago"), "909"),
    (("techno", "trance", "hardstyle", "hard_house", "gabber"), "909"),
    (("electro", "miami", "freestyle", "808_"), "808"),
    (("trap", "drill", "phonk", "crunk", "memphis", "rage", "plugg"), "808"),
    (("boombap", "boom_bap", "lofi", "jazzhop"), "sp1200"),
    (("dnb", "jungle", "breakbeat", "breaks", "big_beat"), "breaks"),
    (("rock", "punk", "metal", "indie", "grunge", "country", "folk", "jazz",
      "blues", "soul", "funk", "gospel"), "acoustic"),
)


def _tok_match(key, norm):
    """Token-boundary genre matching — 'rage' must NEVER hit 'ukgaRAGE'
    (the hyphen-resolver class, 2026-07-10). Short keys (<5) match whole
    tokens only; longer keys may substring (compound names)."""
    toks = norm.split("_")
    if key == norm or key in toks:
        return True
    return len(key) >= 5 and key in norm


def drum_machine_for(name):
    norm = name.lower().replace("-", "_").replace(" ", "_")
    for keys, machine in DRUM_MACHINE:
        if any(_tok_match(k.strip("_"), norm) for k in keys):
            return machine
    return "kit"


def main():
    g = kg.KG()
    genres = [r[0] for r in g.q("MATCH (x:Genre) RETURN x.name")]
    if not genres:
        print("kg_seed_groove_law: no Genre nodes (is sotadaw-kg up?)")
        return 1
    n = 0
    for name in genres:
        low = name.lower()
        attrs = {"drum_machine": drum_machine_for(name)}
        win = GC.tempo_window(name)
        if win:
            attrs["bpm_min"], attrs["bpm_max"] = float(win[0]), float(win[1])
        norm = low.replace("-", "_").replace(" ", "_")
        if any(k == norm or k in norm for k in GC._KICK_4X4):
            attrs["kick_topology"] = "4x4"
        elif any(k in norm for k in GC._KICK_NO_4X4):
            attrs["kick_topology"] = "no_4x4"
        else:
            attrs["kick_topology"] = "free"
        if any(k in norm for k in GC._BB_3):
            attrs["backbeat"] = "snare3"
        elif any(k in norm for k in GC._BB_24):
            attrs["backbeat"] = "snare24"
        else:
            attrs["backbeat"] = "free"
        for k, w in sorted(GC.SWING_WINDOWS.items(), key=lambda kv: -len(kv[0])):
            if k in norm:
                attrs["swing_lo"], attrs["swing_hi"] = float(w[0]), float(w[1])
                break
        g.upsert("Genre", name, PROV, **attrs)
        n += 1
    print(f"kg_seed_groove_law: {n} genres tagged "
          "(bpm window / kick topology / backbeat / swing / drum machine)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
