#!/usr/bin/env bash
# Run the autonomous producer agent (claude -p driving the DAW MCP tools).
# Usage: agent/run_agent.sh "brief" [song_name]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BRIEF="${1:-make a dark trap beat in F minor at 142 bpm, 8 bars}"
NAME="${2:-agent_beat}"
# Producer model — same env knob the sidecar's override rail reads (claude-* ids only on this lane).
MODEL="${SOTADAW_MODEL:-claude-opus-4-8}"
# THE DAW'S OWN ANTHROPIC ACCOUNT: armed by the app's Acct button — this lane rides it too.
DAW_CLAUDE_HOME="$HOME/.config/sotadaw/claude_home"
[ -f "$DAW_CLAUDE_HOME/.credentials.json" ] && export CLAUDE_CONFIG_DIR="$DAW_CLAUDE_HOME"

PROMPT="You are the producer-agent of an AI DAW. Produce a finished, GREAT-sounding beat for this brief: \"$BRIEF\".

Work ONLY through the daw MCP tools, in this discipline:
1. start_session with the genre — READ the force-injected skills; hard constraints are binding. Note the sample kits, Faust instruments, and VST3 plugins available (sound-palette skill has the kit key maps).
2. Compose a full song (write_song, name it \"$NAME\") using the HYBRID palette: real sampled drums (gm_drums keys), the Faust 808 as the tuned bassline, real pitched samples (piano/strings/etc.) and/or the Dexed VST for melody/harmony. Use song-level swing, humanized velocities, halftime structure, intro/breath/fill per the arrangement skill. ALWAYS end \"master\" with fx_brickwall (ceiling -1.2) - never type limiter; masterGainDb stays 0 (see mix-headroom).
3. render_song, then analyze_wav on songs/$NAME.wav.
4. Apply the mix-headroom skill: drive clipped_samples to 0 (in-chain fx_trim staging into fx_brickwall), check band balance and LUFS. Iterate (max 3).
5. Finish with a one-paragraph summary: what you made (instruments per track), final analysis numbers, wav path.

Do not write new instruments this run. Be decisive; no questions."

exec env MCP_TIMEOUT=30000 MCP_TOOL_TIMEOUT=600000 \
  claude -p "$PROMPT" \
  --model "$MODEL" \
  --mcp-config "$ROOT/agent/mcp.json" \
  --strict-mcp-config \
  --permission-mode dontAsk \
  --allowedTools "mcp__daw__start_session,mcp__daw__list_instruments,mcp__daw__list_kits,mcp__daw__get_skill,mcp__daw__write_song,mcp__daw__update_track,mcp__daw__update_song_meta,mcp__daw__set_track_fx,mcp__daw__render_song,mcp__daw__analyze_wav,mcp__daw__vst_presets,mcp__daw__apply_groove,mcp__daw__extract_groove,mcp__daw__duplicate_bars" \
  --max-turns 30 \
  --output-format text
