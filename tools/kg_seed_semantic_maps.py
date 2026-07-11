#!/usr/bin/env python3
"""Semantic Parameter Maps v1 (NIGGUN adopt #5 — the moat corpus, seeded).

Intent -> parameter-cluster maps for the params-dict rails, hand-curated from
VERIFIED param vocabularies (tal_presets/odin_presets dict keys, 2026-07-04).
Graph = source of truth; agent/semantic_maps.json = compiled rail the sidecar
inlines when a mapped plugin appears in the song digest (sidecar runs system
python, no falkordb dep — same graph->artifact pattern as skills).
Provenance: curated:claude/2026-07-04 (semantic maps v1).
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROV = "curated:claude/2026-07-04 (semantic maps v1 — verified param vocabularies)"

MAPS = {
    "TAL-NoiseMaker": {
        "intents": {
            "darker":   [["cutoff", "-", "log taper; the money move"], ["reverbhighcut", "-", "tame verb sizzle"]],
            "brighter": [["cutoff", "+", "log"], ["resonance", "+", "small; >0.6 whistles"]],
            "punchier": [["ampattack", "-", "to ~0"], ["filterattack", "-", ""], ["filterdecay", "-", "slightly"]],
            "softer":   [["ampattack", "+", ""], ["cutoff", "-", "small"]],
            "wider":    [["chorus1enable", "=1", ""], ["detune", "+", "small"]],
            "warmer":   [["cutoff", "-", "small"], ["reverbhighcut", "-", ""], ["osc1volume", "+", "small"]],
            "pluckier": [["ampdecay", "-", ""], ["filterdecay", "-", ""], ["portamento", "-", "to 0"]],
        },
        "gotchas": ["set via set_track_param NATURAL display names, never 0..1",
                    "chorus2enable stacks a second slower chorus — both on = seasick"],
    },
    "Odin2": {
        "intents": {
            "darker":   [["Filter1 Frequency", "-", "log; primary path"], ["Filter2 Frequency", "-", "if serial"]],
            "brighter": [["Filter1 Frequency", "+", ""], ["Filter1 Resonance", "+", "small"]],
            "punchier": [["AmpEnv Attack", "-", "to ~0"], ["FilterEnv Attack", "-", ""], ["FilterEnv Decay", "-", "small"]],
            "pluckier": [["AmpEnv Decay", "-", ""], ["FilterEnv Decay", "-", ""], ["Glide", "-", "to 0"]],
            "wider":    [["Chorus On", "=1", ""], ["Chorus Amount", "+", ""], ["Chorus DryWet", "+", "to ~0.5"]],
            "movement": [["LFO1 Frequency", "~", "bind via matrix; audition"], ["Chorus Rate", "+", "subtle"]],
        },
        "gotchas": ["251 params, THREE filters — Filter1 is the default money path",
                    "'Amplifier Gain -5' through the 0..1 layer was the historic silencer: NATURAL units only"],
    },
    "Surge XT": {
        "intents": {
            "darker":   [["Filter 1 Cutoff", "-", "VERIFY name via list_plugin_params first"]],
            "brighter": [["Filter 1 Cutoff", "+", "verify"], ["Filter 1 Resonance", "+", "small, verify"]],
            "punchier": [["Amp EG Attack", "-", "verify"], ["Filter EG Attack", "-", "verify"]],
            "wider":    [["Scene Width", "+", "verify"], ["Osc 1 Unison Detune", "+", "verify"]],
        },
        "gotchas": ["state-blob rail: params vary per patch — ALWAYS list_plugin_params before setting",
                    "prefer loading a closer factory preset over deep param surgery"],
    },
}

if __name__ == "__main__":
    from kg import KG
    kg = KG()
    for plugin, m in MAPS.items():
        kg.upsert("SemanticMap", f"semmap_{plugin.lower().replace(' ', '_').replace('-', '_')}",
                  PROV, plugin=plugin, intents=json.dumps(m["intents"]),
                  gotchas=json.dumps(m["gotchas"]))
        print(f"  seeded {plugin}: {len(m['intents'])} intents")
    out = os.path.join(ROOT, "agent", "semantic_maps.json")
    json.dump(MAPS, open(out, "w"), indent=1)
    print(f"compiled rail -> {out}")
