---
name: jersey_drill-arrangement
version: 1
kind: genre
tags: [jersey_drill, drill, jerseyclub, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 130-150; set the song key (suggested: C# minor).
  - Mix: clipped_samples == 0, LUFS -9..-6, band order low>lowmid>mid.
  - JERSEY FIVE KICK is non-negotiable: THE Jersey club kick: 5 hits per bar at slots 1, 2, 3, 3.75, 4.5 (grid 0,4,8,11,14) — boom / boom / boom-boom / boom, nonstop
  - DRILL SLIDE 808 is non-negotiable: dark drill 808s GLIDING between notes (portamento) under the club kick — the NY drill low end on Jersey legs
  - CLUB DRILL SWITCHUP is non-negotiable: 8-bar switch-ups alternating drill half-time sections with full Jersey club kick sections — two grooves, one song
---
# Jersey_Drill arrangement (graph-compiled)

Jersey_Drill is a child of **drill, jerseyclub** — its groove laws apply unless overridden below.

## The pocket — squeak_drill
Jersey drill (~138 BPM): THE Jersey 5-kick — grid slots 0,4,8,11,14 (1, 2, 3, 3.75, 4.5) — runs nonstop under DARK sliding drill 808s; claps stabbed at slots 9&12 (+11); hats mark 2&4 with triplet rolls; 8-bar switch-ups alternate drill half-time (snare 3, kick sparse) with the full club kick. Bed-squeak rides the kick figure.  *(source: curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*

## Techniques (weight order — the top ones DEFINE the genre)
- **jersey five kick** (w1.0): THE Jersey club kick: 5 hits per bar at slots 1, 2, 3, 3.75, 4.5 (grid 0,4,8,11,14) — boom / boom / boom-boom / boom, nonstop *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **drill slide 808** (w0.92): dark drill 808s GLIDING between notes (portamento) under the club kick — the NY drill low end on Jersey legs *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **club drill switchup** (w0.84): 8-bar switch-ups alternating drill half-time sections with full Jersey club kick sections — two grooves, one song *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **bed squeak** (w0.76): the bed-squeak sample as a percussion instrument riding the kick pattern — Jersey club's meme-turned-signature *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **triplet hat roll** (w0.68): trap hats with fast triplet/roll bursts and stutters over a straight grid, snare/clap on beat 3 (half-time feel) at a hot ~140-155 BPM *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*

## Inherited from drill, jerseyclub
- halftime groove: snare on beat 3 (not 2&4); space is the instrument
- hat rolls: 16th->32nd bursts at phrase ends; velocity ramps
- sliding 808: 808 pitch slides between roots (overlapping notes)
- ghost snare drill: extra snares at 3.75/4.25 around the main pocket
- brickwall mastering: master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain).
- tempo map motion: tempoMap on any song: halftime drops, ritardando outros (curve 0), section tempo switches — beats, warped audio, automation all follow
- true peak safety: master to <=-1 dBTP TRUE peak, not sample peak — Spotify/Apple/EBU R128 all specify -1 dBTP; inter-sample peaks reconstruct ~1-1.4dB higher than sample peaks (up to 1.81dB on drill 808s) and clip after lossy codec transcoding. A sample-domain limiter alone cannot guarantee it.
- streaming loudness target: the 2026 universal streaming target is -14 LUFS integrated (Spotify/YouTube/Tidal/Amazon all normalize to -14; Apple/Facebook -16). Do not chase loudness past it — platforms normalize DOWN. Master to -14 LUFS / <=-1 dBTP and it plays everywhere.
- softclip pre limiter: a TRANSPARENT soft clipper (pure tanh, no de-emphasis tone filter) before the final limiter shaves the sharpest 1-3dB of transients so the limiter works less hard = more loudness that still breathes. fx_saturate is the WRONG tool (its tone filter darkens 19-33%); use fx_softclip. The standard trap/drill loudness move.
- inter sample headroom by genre: dense 808/kick material (drill, house four-on-floor) generates the most inter-sample overshoot (~1.4-1.8dB); sparse material (ambient) almost none. A fixed sample ceiling of -3.0 lands all 14 tested genres <=-1 dBTP at ~0.3dB loudness cost (the ceiling clips transient PEAKS, not sustained level). Oversampled (4x/8x) true-peak limiting is the textbook fix.
- send reverb: reverb on a BUS at mix 1.0, balance via send level; kick/808 DRY
- vocal chops: short pitched vocal stabs (choir kit, high keys) placed rhythmically
- club kick pattern: THE jersey 5-kick: 1, 1.5, 2.5, 3, 3.5 — dance instructions in kick form
- bed squeak chops: chopped vocal/stab on straight 8ths riding the kick pattern
- triplet break: bar-4 triplet kick fill (hands-up moment) before the pattern restarts
- loudness recovery: CLOSING STEP, numeric: after the mix is clean (clipped 0, dbtp <= -1), if lufs_integrated < the genre window's LOW bound, raise the makeup fx_trim (the one before fx_brickwall) by (low_bound - lufs) dB, re-render, re-check. Quiet-but-clean is still a FAIL.
- brickwall mastering: master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain).
- warp beatmatch: beat-match by sourceBpm warp onto ONE grid — never nudge notes; transparent to ~+/-8% tempo distance
- phrase aligned blend: transitions start on a 4-bar boundary of the outgoing deck; dance music breathes in 4/8/16-bar phrases
- bass swap: ONE bass at a time: incoming deck rides fx_djfilter knob +0.5..0.7 until the swap beat, then lows change hands in 0.25 beat
- filter transition: fx_djfilter bipolar knob: LP sweep out the old deck / HP hold the new — the one-knob DJ mixer filter

## Sound recipes (this palette, these moves)
- **squeak kit**: clipped Jersey kick (kick_punch layered kick_808) on the 5-figure; drill 808 gliding (sub_clean + portamento feel via note slides); dark FM bell (fmbell) minor motifs; the bed-squeak = a high pitched short formant_vox/pluck squeak riding the kick slots

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -9..-6, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
