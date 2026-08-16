#!/usr/bin/env python3
"""FX ZONE TRUTH — the one table + the param court every seam shares.

setZone() is EXACT-name: a param not in the voice's zone set is a SILENT
no-op. The corpus sweep (2026-07-24) found that class alive and breeding —
fx_filter {"resonance"}, {"mode"}, fx_trim {"gain"} — born as recently as
07-16 because the write seams validated fx IDs but never param names.

Three laws live here:
  ZONES     — per-fx zone truth (extracted from instruments/fx_*.dsp sliders;
              doctor.py imports THIS — one table, never two).
  ALIASES   — the obvious-intent map (resonance->res, gain->level on trim...).
              heal_params() rewrites them in place: agent intent lands on the
              real knob instead of dying silently.
  MARKERS   — params keys starting with "_" are FIRST-PARTY markers
              (auto_master's params._am). They round-trip the C++ resave
              (entry-level custom fields DON'T — probed 2026-07-24), are
              never zones, never errors, never healed.

check_params(fx_id, params) -> (healed: [(old, new)], unknown: [name]).
Callers decide the verdict: agent tool seams FAIL CLOSED on unknown (the
agent self-corrects mid-run); doctor keeps nagging standing files.
"""

FX_ZONES = {
    "fx_brickwall": {"ceiling"},
    "fx_comp": {"thresh", "ratio", "attack", "release", "makeup"},
    "fx_crush": {"bits", "srate", "mix"},
    "fx_deess": {"freq", "thresh", "ratio"},
    "fx_delay": {"time", "feedback", "mix"},
    "fx_djfilter": {"knob", "res"},
    "fx_filter": {"cutoff", "res"},
    "fx_chorus": {"rate", "depth", "mix", "voices"},
    "fx_flanger": {"rate", "depth", "feedback", "mix"},
    "fx_gate": {"thresh", "depth", "rel"},
    "fx_hipass": {"cutoff", "res"},
    "fx_ms_eq": {"mid_low", "mid_high", "side_low", "side_high",
                 "width", "low_freq", "high_freq"},
    "fx_multiband": {"xlow", "xhigh", "attack", "release",
                     "low_thresh", "low_ratio", "mid_thresh", "mid_ratio",
                     "high_thresh", "high_ratio", "makeup"},
    "fx_pump": {"rate", "depth", "release"},
    "fx_reverb": {"mix", "size", "damp"},
    "fx_saturate": {"drive", "tone", "mix"},
    "fx_softclip": {"drive"},
    "fx_tremolo": {"rate", "depth", "shape", "spread"},
    "fx_transient": {"attack", "sustain"},
    "fx_trim": {"level"},
    "fx_truepeak": {"ceiling"},
    "fx_widen": {"width", "rate"},
    # completed 2026-07-24 (the advertise lint counts 25 usable fx; the table
    # held 20 — these five were fail-open, unprotected):
    "fx_bell": {"freq", "gain", "q"},        # real zones NAMED gain/q/freq —
    "fx_bass_grit": {"xover", "drive", "grit"},   # the alias zone-gate keeps
    "fx_dubdelay": {"time", "feedback", "damp", "mix"},   # them un-healed
    "fx_match_eq": {"g85", "g171", "g344", "g691", "g1389", "g2790",
                    "g5609", "g11272"},
    "fx_polarity": {"flip"},
}


def dsp_zone_truth(instruments_dir):
    """Parse instruments/fx_*.dsp slider/checkbox names — the SOURCE truth the
    table must mirror (battery invariant: table == dsp, per fx present)."""
    import os
    import re
    out = {}
    for f in sorted(os.listdir(instruments_dir)):
        if not (f.startswith("fx_") and f.endswith(".dsp")):
            continue
        src = open(os.path.join(instruments_dir, f), errors="ignore").read()
        names = set(re.findall(r'(?:hslider|vslider|nentry|checkbox)\s*\(\s*"([^"\[]+)', src))
        out[f[:-4]] = {n.strip() for n in names}
    return out

# per-fx first (specific intent), global second; an alias applies ONLY when
# the written name is not a real zone AND the target IS one for that fx
ALIASES_PER_FX = {
    "fx_trim": {"gain": "level", "db": "level", "trim": "level"},
    "fx_comp": {"gain": "makeup"},
    "fx_reverb": {"room": "size", "wet": "mix"},
    "fx_saturate": {"amount": "drive"},
    "fx_widen": {"amount": "width"},
    "fx_pump": {"amount": "depth"},
    "fx_brickwall": {"limit": "ceiling", "threshold": "ceiling"},
    "fx_truepeak": {"limit": "ceiling", "threshold": "ceiling"},
}
ALIASES_GLOBAL = {"resonance": "res", "q": "res", "frequency": "cutoff",
                  "freq": "cutoff", "threshold": "thresh", "wet": "mix",
                  "fb": "feedback", "rel": "release", "release": "rel"}

# unknown params whose intent NAMES a different tool — teach, don't guess
TEACHINGS = {
    ("fx_filter", "mode"): "fx_filter is low-pass only; high-pass = fx_hipass, DJ sweep = fx_djfilter",
    ("fx_filter", "type"): "fx_filter is low-pass only; high-pass = fx_hipass, DJ sweep = fx_djfilter",
}


def check_params(fx_id, params):
    """-> (healed [(old,new)], unknown [names]). Mutates params in place for
    heals. '_'-prefixed keys are first-party markers: untouched, legal."""
    zones = FX_ZONES.get(fx_id)
    healed, unknown = [], []
    if zones is None or not isinstance(params, dict):
        return healed, unknown            # unknown fx: fail-open (new voice)
    for k in list(params.keys()):
        if k in zones or k.startswith("_"):
            continue
        tgt = ALIASES_PER_FX.get(fx_id, {}).get(k) or ALIASES_GLOBAL.get(k)
        if tgt and tgt in zones:
            if tgt in params:             # both written: the real knob wins
                params.pop(k)
                healed.append((k, tgt + " (duplicate dropped)"))
            else:
                params[tgt] = params.pop(k)
                healed.append((k, tgt))
        else:
            unknown.append(k)
    return healed, unknown


def unknown_error(fx_id, unknown):
    """One teaching line for a fail-closed seam."""
    teach = "; ".join(t for k in unknown
                      for t in [TEACHINGS.get((fx_id, k))] if t)
    return (f"{fx_id} has no zone(s) {sorted(unknown)} — real zones: "
            f"{sorted(FX_ZONES.get(fx_id, []))}"
            + (f". {teach}" if teach else ""))


if __name__ == "__main__":
    import json
    import sys
    fid, raw = sys.argv[1], json.loads(sys.argv[2])
    h, u = check_params(fid, raw)
    print(json.dumps({"params": raw, "healed": h, "unknown": u}))
