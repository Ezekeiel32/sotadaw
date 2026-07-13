#!/usr/bin/env bash
# THE GUARDIAN SUITE — one command proves every surface the ghost-3b78 campaign
# built (2026-07-06, ships #1-#21). Four sessions sweep each other's files
# hourly; THIS is the durable safety. Run it before/after any burst that
# touches ui_main.cpp, ProposalDeck.h, sidecar handlers, daw_mcp write/tweak
# paths, midi_polish, or the skills registry.
#
#   tools/ghost_suite.sh          # everything except GPU/model-heavy --real legs
#   tools/ghost_suite.sh --full   # + real-stems midi_polish leg (basic-pitch CPU)
#
# PIPESTATUS law: every leg's exit code is captured; grep never masks a failure.
set -u
cd "$(dirname "$0")/.."
VENVPY=.venv/bin/python; [ -x "$VENVPY" ] || VENVPY=python3
POLITE=0; for a in "$@"; do [ "$a" = "--polite" ] && POLITE=1; done
declare -a NAMES RCS NOTES
leg() {  # leg <name> <cmd...>
  local name="$1"; shift
  # W121 THE POLITE SUITE: with --polite, every leg boundary re-checks the
  # stand-down gate — the user returning mid-suite pauses the run instead
  # of contending (the one-check-at-start gap let a live session collide
  # with leg 30 of 52, 2026-07-11).
  if [ "$POLITE" = "1" ]; then
    while python3 tools/user_live.py >/dev/null 2>&1; do
      sleep 45
    done
  fi
  local t0=$SECONDS out rc
  out=$("$@" 2>&1); rc=$?
  NAMES+=("$name"); RCS+=($rc)
  NOTES+=("$(echo "$out" | tail -1 | cut -c1-70) ($((SECONDS-t0))s)")
  printf '%-28s %s\n' "$name" "$([ $rc -eq 0 ] && echo PASS || echo "FAIL(rc=$rc)")"
  [ $rc -ne 0 ] && echo "$out" | tail -12
  return 0
}

echo "== THE GUARDIAN SUITE =="
leg "ghost_e2e (accept+reject x3)" python3 tools/ghost_e2e.py 3
leg "scalpel (kernel battery)"     python3 tools/surgical_battery.py
leg "revise_receipts (seam)"       python3 tools/revise_receipts_e2e.py
leg "delta_ear (revise Δ seam)"    python3 tools/delta_ear_e2e.py
leg "blind_round (N-take A/B)"     python3 tools/blind_round_e2e.py
leg "blind_card (UI pick seam)"    python3 tools/blind_card_e2e.py
leg "world_grid (#1 den-8/16)"     python3 tools/world_grid_e2e.py
leg "midi_meter (#1 FF58 bridge)"  python3 tools/midi_meter_battery.py
leg "grid (#1 agent-layer bars)"   python3 tools/grid_battery.py
leg "meter (#1 native_meter)"      python3 tools/meter_battery.py
leg "grid_lint (ONE resolver)"     python3 tools/grid_lint.py
leg "cuda_preload_lint (bp rail)"  python3 tools/cuda_preload_lint.py
leg "refresh_guard (no storm)"     python3 tools/refresh_guard_battery.py
leg "done_court (one done/run)"    python3 tools/done_court_battery.py
leg "crash_pin (symbolize law)"    python3 tools/crash_symbolize.py --selftest
leg "resurrection_court (zombies)" python3 tools/resurrection_battery.py
leg "context_tune (note court)"    "$VENVPY" tools/retune.py --selftest
leg "one_tempo (no bpm splits)"    python3 tools/one_tempo_battery.py
leg "prop_fence (base immutable)"  python3 tools/prop_fence_e2e.py
leg "living_cards (chat rolls)"    python3 tools/cards_e2e.py 1
leg "ears_on_write"                python3 tools/ears_on_write_battery.py
leg "session_diet"                 python3 tools/session_diet_battery.py
leg "gold_standard (DNA bank)"     python3 tools/gold_battery.py
leg "feedback_loop"                python3 tools/feedback_loop_battery.py
leg "chronicle (kernel)"           python3 tools/chronicle_battery.py
leg "chronicle (protocol seam)"    python3 tools/chronicle_e2e.py 1
leg "chronicle (ui replay)"        python3 tools/chronicle_e2e.py --ui
leg "clip_wall (pure)"             python3 tools/clip_wall_battery.py
leg "midi_polish (synthetic)"      python3 tools/midi_polish_battery.py
leg "plausibility_court"           "$VENVPY" tools/court_battery.py
leg "worldclass_floor"             "$VENVPY" tools/worldclass_battery.py
leg "instrument_ear (self-ID)"     "$VENVPY" tools/ear_battery.py
leg "following_voice"              python3 tools/vocal_follow_battery.py
leg "drum_pieces (microscope)"     "$VENVPY" tools/drumsep_battery.py
leg "voice_adopt (verdict seam)"   python3 tools/voice_adopt_battery.py
leg "lyric_bank (words kernel)"    python3 tools/lyric_bank_battery.py
leg "make_sings (W104 e2e)"        .venv/bin/python tools/make_sings_e2e.py
leg "transcribe_rails (synth GT)"  "$VENVPY" tools/transcribe_battery.py
leg "kg_taste"                     "$VENVPY" tools/kg_taste_battery.py
leg "taste_skill"                  "$VENVPY" tools/taste_skill_battery.py
leg "stranger_first_loop"          python3 tools/stranger_e2e.py 1
leg "groove_drop"                  python3 tools/groove_drop_e2e.py 1
leg "midi_clock"                   python3 tools/midi_clock_e2e.py 1
leg "ableton_link"                 python3 tools/link_e2e.py 1
leg "wall_lint"                    python3 tools/wall_lint.py
leg "receipt_lint"                 python3 tools/receipt_lint.py
leg "songname_lint"                python3 tools/songname_lint.py
leg "card_lint"                    python3 tools/card_lint.py
leg "uismoke_pixels (frame-0)"     python3 tools/uismoke_pixel_lint.py
leg "sidecar_refresh"              python3 tools/sidecar_refresh_e2e.py 1
leg "feel_born"                    python3 tools/feel_born_battery.py
leg "face_census"                  python3 tools/face_census.py
leg "flows (musicflow + QC probe)" "$VENVPY" tools/flow_battery.py
leg "controller_profiles"          python3 tools/controller_profiles_lint.py
leg "semantic_ears (V53)"          "$VENVPY" tools/semantic_battery.py
leg "palettes_v2"                  "$VENVPY" tools/palette_battery.py
leg "add_topline"                  "$VENVPY" tools/topline_tool_battery.py
leg "chords_audio (V54)"           "$VENVPY" tools/chords_audio_battery.py
leg "align_lyrics (auto-melisma)"  "$VENVPY" tools/align_lyrics_battery.py
leg "dj_key_clash (§7.7)"          "$VENVPY" tools/dj_clash_battery.py
leg "fx_advertise_lint"            "$VENVPY" tools/fx_advertise_lint.py
leg "sing_preflight (OOM gate)"    python3 tools/sing_preflight_battery.py
leg "dj_arc+bridge_auto (§7.7)"    "$VENVPY" tools/dj_arc_battery.py
leg "ears_bus (E3 R1-R3)"          python3 tools/ears_bus_battery.py
leg "nam_rail (V51)"               python3 tools/nam_battery.py
leg "clap_host (V50)"              "$VENVPY" tools/clap_battery.py
leg "dj_live (R4 advisor)"          python3 tools/dj_live_battery.py
leg "jam (AI band on vibe)"       "$VENVPY" tools/jam_battery.py
leg "jam_live (realtime)"         "$VENVPY" tools/jam_live_battery.py
leg "jam_endless (B6 bandstand)"  "$VENVPY" tools/jam_endless_battery.py
leg "jam_follow (B3 play-WITH-me)" python3 tools/jam_follow_battery.py
leg "audio_ear (mic->follow)"      "$VENVPY" tools/audio_follow_battery.py
leg "band_set (composed laws)"     "$VENVPY" tools/band_set_proof.py
leg "punch_play (crossfade seam)"  python3 tools/punch_play_e2e.py 1
leg "jam_strip (face + view law)"  python3 tools/jam_strip_e2e.py 1
leg "jam_pod (B6 lifecycle e2e)"   python3 tools/jam_pod_e2e.py 1
leg "keytest (gesture suite)"      python3 tools/keytest.py
leg "render_serve (warm rail)"     "$VENVPY" tools/render_serve_battery.py
leg "keep_jam (capture law)"       python3 tools/keep_jam_battery.py
leg "action_wire (agent stream)"  "$VENVPY" tools/action_wire_e2e.py
leg "audio_receipt_lint (E3)"      python3 tools/audio_receipt_lint.py
leg "composition (W14-26 laws)"    "$VENVPY" tools/composition_battery.py
leg "generation_court (W46)"       "$VENVPY" tools/generation_court.py
if [ "${1:-}" = "--full" ]; then
  leg "audio_rec (B4 capture)"     python3 tools/audio_rec_e2e.py 2
  leg "jam_genre_sweep (8 shapes)" "$VENVPY" tools/jam_genre_sweep.py
  leg "midi_polish --real"         "$VENVPY" tools/midi_polish_battery.py --real
  leg "transcribe_rails --real"    "$VENVPY" tools/transcribe_battery.py --real
  leg "clip_wall --real"           "$VENVPY" tools/clip_wall_battery.py --real
  leg "stranger x3"                python3 tools/stranger_e2e.py 3
  # THE PHYSICS batteries (render-heavy; docs/THE_PHYSICS.md EB2/EB3/EB4)
  leg "dsp_bench (A1 selftest)"    "$VENVPY" tools/dsp_bench.py --selftest
  leg "null_bench (A2 3-case x3)"  "$VENVPY" tools/null_bench.py --selftest
  leg "dynamics_ears (A4 vs refs)" "$VENVPY" tools/dynamics_ears.py --validate
  leg "render_cache (A6 prove)"    "$VENVPY" tools/render_cache.py --prove
  leg "audio_receipts_e2e (E3)"    python3 tools/audio_receipts_e2e.py 1
fi

echo
echo "== VERDICT =="
FAILS=0
for i in "${!NAMES[@]}"; do
  printf '%-28s %s\n' "${NAMES[$i]}" "$([ "${RCS[$i]}" -eq 0 ] && echo PASS || echo FAIL)"
  [ "${RCS[$i]}" -ne 0 ] && FAILS=$((FAILS+1))
done
if [ $FAILS -eq 0 ]; then
  echo "GUARDIAN: ALL GREEN (${#NAMES[@]} legs)"
else
  echo "GUARDIAN: $FAILS leg(s) RED"
fi
exit $FAILS
