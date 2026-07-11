---
name: sigilkore-arrangement
version: 2
kind: genre
tags: [sigilkore, hyperpop, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 105-190; set the song key (suggested: F# minor (Phrygian)).
  - Mix: clipped_samples == 0, LUFS -9..-6, band order low>lowmid>mid.
  - DROWNED REVERB CHAIN is non-negotiable: everything drenched: long detuned choir/pad reverb tails BEHIND heavy bitcrush — drowned cathedral under digital rot
  - BITCRUSH PATINA is non-negotiable: bitcrush/sample-rate-reduction ON THE BUS as the genre's texture (8-16 bit, srate drops) — apply to bells, vocals, even the master color
  - GHOST GLIDE 808 is non-negotiable: long-tail 808 on beat 1 with ghost glides trailing after — half-time (snare 3) with hyperactive 1/16-1/64 hat spatter
---
# Sigilkore arrangement (graph-compiled)

Sigilkore is a child of **hyperpop** — its groove laws apply unless overridden below.

## The pocket — drowned_ritual
Sigilkore (~155 BPM, half-time): long-tail 808 on beat 1 with ghost glides trailing; snare on 3; hyperactive 1/16 hat spatter (bursts, not steady); detuned choir pads DROWNED in reverb behind heavy bitcrush; FM-bell/chip leads play narrow dark minor motifs; tape-stop fills close phrases.  *(source: curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*

## Techniques (weight order — the top ones DEFINE the genre)
- **drowned reverb chain** (w1.0): everything drenched: long detuned choir/pad reverb tails BEHIND heavy bitcrush — drowned cathedral under digital rot *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **bitcrush patina** (w0.92): bitcrush/sample-rate-reduction ON THE BUS as the genre's texture (8-16 bit, srate drops) — apply to bells, vocals, even the master color *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **ghost glide 808** (w0.84): long-tail 808 on beat 1 with ghost glides trailing after — half-time (snare 3) with hyperactive 1/16-1/64 hat spatter *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **occult bell lead** (w0.76): detuned FM bells and chiptune leads playing narrow dark minor motifs — music-box-from-a-ritual energy *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **tape stop fill** (w0.68): tape-stop / pitch-drop fills close phrases instead of drum fills *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*

## Inherited from hyperpop
- width bloom: fx_widen width 0.6 verse -> 1.4-1.7 hook; never on low end
- gain staged saturation: saturation adds LEVEL: after set_track_fx with fx_saturate, trim that track's gainDb by 4-6 dB (drive is tone, gain is level). Get LOUD the clean way: masterGainDb +2..+4 INTO the master limiter (ceiling -1). Verify: clipped_samples 0 AND true_peak_dbtp <= -1 AND LUFS inside the genre window — if LUFS too low, raise masterGainDb (never remove the trims).
- supersaw uplift: trance: supersaw_fat layered octaves, long chords, cutoff rises 8-16 bars, sidechain pump throughout
- pitch vox hyper: hyperpop: chipmunk vocal chops (choir kit +12st equivalents), bitcrush-bright synths, extreme widen

## Sound recipes (this palette, these moves)
- **sigil rig**: detuned FM bells (fmbell) + chip leads (chiptune_pulse) for the occult motifs; vox_pad choir sent HUGE into a reverb bus, then the BUS crushed with fx_crush (bits 6-9, srate 6-12k — reverb BEHIND the crush = the drowned-rot order) ; gliding kick_808 with long tails; everything darker than hyperpop, wetter than trap

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -9..-6, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
