---
name: goa-arrangement
version: 1
kind: genre
tags: [goa, psytrance, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 135-145; set the song key (suggested: E phrygian).
  - Mix: clipped_samples == 0, LUFS -14..-8, band order low>lowmid>mid.
  - FM METALLIC ARPS is non-negotiable: FM bell/metallic 16th arps in phrygian/harmonic minor — the goa melodic signature
  - ROLLING OFFBEAT BASS is non-negotiable: THE psy engine: kick on each beat, bass 16ths at +0.25/+0.5/+0.75 of EVERY beat (k-b-b-b gallop), short (~0.2) same-root notes for 8-16 bars; root follows the key
  - JOURNEY STRUCTURE is non-negotiable: 6-8 min arc: intro(no bass) -> build -> peak -> BREAKDOWN at ~60% (kick+bass OUT, pads/leads breathe, 8-16 bars) -> filter rebuild -> peak2 -> outro. Use duplicate_bars to stamp sections, clear_bars to carve the breakdown
---
# Goa arrangement (graph-compiled)

Goa is a child of **psytrance** — its groove laws apply unless overridden below.

## The pocket — goa_layers
psy_fullon pocket + 2-3 LAYERED melodic arps entering one per section (call-and-answer), eastern scales  *(source: curated:claude/2026-07-02)*

## Techniques (weight order — the top ones DEFINE the genre)
- **fm metallic arps** (w1.0): FM bell/metallic 16th arps in phrygian/harmonic minor — the goa melodic signature *(curated:claude/2026-07-02)*
- **rolling offbeat bass** (w0.93): THE psy engine: kick on each beat, bass 16ths at +0.25/+0.5/+0.75 of EVERY beat (k-b-b-b gallop), short (~0.2) same-root notes for 8-16 bars; root follows the key *(curated:claude/2026-07-02)*
- **journey structure** (w0.86): 6-8 min arc: intro(no bass) -> build -> peak -> BREAKDOWN at ~60% (kick+bass OUT, pads/leads breathe, 8-16 bars) -> filter rebuild -> peak2 -> outro. Use duplicate_bars to stamp sections, clear_bars to carve the breakdown *(curated:claude/2026-07-02)*
- **acid squelch lead** (w0.79): resonant 303-style line (acid303), cutoff automated per phrase, res 2-4; THE lead voice *(curated:claude/2026-07-02)*
- **tape saturation** (w0.72): heavy fx_saturate drive 8-14 over the whole beat bus = grit *(curated:claude/2026-07-02)*

## Inherited from psytrance
- filter build: fx_filter cutoff automated 250->9000 over 4-8 bars, lands ON the drop
- four on floor: kick every beat; openhat on offbeat 8ths
- gain staged saturation: saturation adds LEVEL: after set_track_fx with fx_saturate, trim that track's gainDb by 4-6 dB (drive is tone, gain is level). Get LOUD the clean way: masterGainDb +2..+4 INTO the master limiter (ceiling -1). Verify: clipped_samples 0 AND true_peak_dbtp <= -1 AND LUFS inside the genre window — if LUFS too low, raise masterGainDb (never remove the trims).
- psy hat drive: closed hats straight 16ths vel ~0.5 with offbeat-8th accents ~0.8; open hat on the offbeat
- riser throws: before each section change: reverb-send throw or 2-bar filter riser (automate cutoff up)

## Sound recipes (this palette, these moves)
- **goa arp sound**: fmbell or pluck2 16th arps + fx_delay dotted (feedback 0.35) + send to verb bus

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -14..-8, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
