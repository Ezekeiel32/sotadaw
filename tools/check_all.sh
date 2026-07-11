#!/bin/bash
# ALL SIX regression nets in one command — the machine's full self-check.
#   check_all.sh          full run (renders; ~6-8 min)
#   check_all.sh --fast   JSON/registry only (no renders; ~seconds)
# Fast checks run first so failures surface early. Eval briefs are paid/gated
# and NOT part of this (run tools/eval_daw.py --brief <genre> separately).
set -e
cd "$(dirname "$0")/.."
PY=.venv/bin/python
FAST=0; [ "$1" = "--fast" ] && FAST=1

echo "=== [1/6] DNA battery (loop-DNA correctness, 130 genres) ==="
$PY tools/dna_battery.py

echo "=== [2/6] skills registry ==="
python3 tools/skills_build.py > /dev/null && echo "registry rebuilds clean"

echo "=== [2b] MCP schema integrity (every advertised param reachable) ==="
$PY tools/tool_audit.py

echo "=== [2c-model] model rails (Codex CLI isolation + selector/provider routing) ==="
$PY tools/codex_agent_battery.py
$PY tools/model_routing_battery.py

if [ "$FAST" = "1" ]; then echo "FAST NETS GREEN (renders skipped)"; exit 0; fi

echo "=== [3/6] preset battery (the 4,366-sound rail) ==="
$PY tools/preset_battery.py --per-plugin 4 --seed 2

echo "=== [4/6] maketrack battery (genre -> arranged track, 10 genres) ==="
$PY tools/maketrack_battery.py

echo "=== [5/6] song battery (every committed song renders clean) ==="
$PY tools/song_battery.py

echo "=== [6/6] sing battery (4 voices sing the melody on-pitch) ==="
$PY tools/sing_battery.py

echo "=== [7] pipeline e2e (finish: chords->arrange->harmonize->transitions->automix->master) ==="
$PY tools/pipeline_battery.py

echo "=== [8] expressive (humanize + NOMML metrics discriminate, microtiming survives render) ==="
$PY tools/expressive_battery.py

echo "=== [9] arc quality (rough loop -> full arc -> ears certify release-shaped) ==="
$PY tools/arc_quality.py

echo "=== [10] arc quality sweep (arc makes release-shaped music ACROSS 5 genres) ==="
$PY tools/arc_quality_sweep.py

echo "=== [2c] MCP smoke (new tools reachable through the real sidecar allowlist + handlers) ==="
$PY tools/mcp_smoke.py

echo "=== [2d] VST moat (list-params exposes every VST3 knob; skip-safe) ==="
$PY tools/vst_moat_battery.py

echo "=== [2e] arc x VST (producer arc is source-agnostic: Faust + VST3) ==="
$PY tools/arc_vst_battery.py

echo "=== [2f] verb bus (zero-token lane: instant proposals, receipts, locks, traps closed) ==="
$PY tools/verb_bus_battery.py

echo "=== [2g] energy curve (per-bar truth, sustain spill, contrast law, composes intensify) ==="
$PY tools/energy_battery.py

echo "=== [2h] color axes (warmer/brighter/wider move the SOUND; mono law; clamps) ==="
$PY tools/color_battery.py

echo "=== [2i] restyle (genre morph: notes byte-identical, palette+feel swap, audible) ==="
$PY tools/restyle_battery.py

echo "=== [2j] true-peak wall (ISP sine discriminates walls; music holds dBTP; loudness refunded) ==="
$PY tools/truepeak_battery.py

echo "=== [2k] voicing kernel (minimal motion, common tones, register law, style geometry) ==="
$PY tools/voicing_battery.py

echo "ALL NETS GREEN"
