---
name: goa-arrangement
version: 7
kind: genre
tags: [goa, psytrance, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 135-150; set the song key (suggested: E phrygian).
  - Mix: clipped_samples == 0, LUFS -14..-8, band order low>lowmid>mid.
  - FM METALLIC ARPS is non-negotiable: FM bell/metallic 16th arps in phrygian/harmonic minor — the goa melodic signature
  - ROLLING OFFBEAT BASS is non-negotiable: bass SILENT on the kick, galloping the three 16ths after (null,x,x,x) — kick and bass never collide, so the mix pumps with ZERO sidechain: the arrangement IS the sidechain | lore-verified: 16th-pulse rolling bass, fundamentals 40-80Hz; the pump comes from the kick-hole OR sidechain - both canon, the hole needs zero processing
  - LOUDNESS RECOVERY is non-negotiable: CLOSING STEP, numeric: after the mix is clean (clipped 0, dbtp <= -1), if lufs_integrated < the genre window's LOW bound, raise the makeup fx_trim (the one before fx_brickwall) by (low_bound - lufs) dB, re-render, re-check. Quiet-but-clean is still a FAIL.
  - GROOVE PSY STRAIGHT is non-negotiable: apply_groove('psy_straight', amount 1.0) - machine grid with accented offbeat 8ths; psytrance/techno want NO drag, only accent shape.
  - LONG FORM PATIENCE is non-negotiable: tension accumulates in MINUTES, not bars: 12-32-bar sections, one journey over 300+ bars; the peak earns itself by arriving late
  - FILTER JOURNEY LAYERS is non-negotiable: motion at three timescales AT ONCE: per-note filter env inside a per-section cutoff ceiling inside a master LP walk — sweeps riding sweeps is the hypnosis
---
# Goa arrangement (graph-compiled)

Goa is a child of **psytrance** — its groove laws apply unless overridden below.

## The pocket — goa_layers
psy_fullon pocket + 2-3 LAYERED melodic arps entering one per section (call-and-answer), eastern scales  *(source: curated:claude/2026-07-06 (wave38 world/anthem canon; freygish+bigroom-vamp+levels-anthem cited f148; afro_pocket i-VII = canon-prior, cite pending) +1 more)*

## Techniques (weight order — the top ones DEFINE the genre)
- **fm metallic arps** (w1.0): FM bell/metallic 16th arps in phrygian/harmonic minor — the goa melodic signature *(curated:claude/2026-07-02)*
- **rolling offbeat bass** (w0.95): bass SILENT on the kick, galloping the three 16ths after (null,x,x,x) — kick and bass never collide, so the mix pumps with ZERO sidechain: the arrangement IS the sidechain | lore-verified: 16th-pulse rolling bass, fundamentals 40-80Hz; the pump comes from the kick-hole OR sidechain - both canon, the hole needs zero processing *(chezy-prototype forensics 2026-07-05 (song_editor goa act, 346 bars))*
- **loudness recovery** (w0.9): CLOSING STEP, numeric: after the mix is clean (clipped 0, dbtp <= -1), if lufs_integrated < the genre window's LOW bound, raise the makeup fx_trim (the one before fx_brickwall) by (low_bound - lufs) dB, re-render, re-check. Quiet-but-clean is still a FAIL. *(eval:2026-07-03 (techno -14.99, grime -12.92 vs windows — recurring clean-but-quiet residual))*
- **groove psy straight** (w0.9): apply_groove('psy_straight', amount 1.0) - machine grid with accented offbeat 8ths; psytrance/techno want NO drag, only accent shape. *(curated:claude/2026-07-03 (groove engine profiles -> graph))*
- **long form patience** (w0.9): tension accumulates in MINUTES, not bars: 12-32-bar sections, one journey over 300+ bars; the peak earns itself by arriving late *(chezy-prototype forensics 2026-07-05 (song_editor goa act, 346 bars))*
- **filter journey layers** (w0.9): motion at three timescales AT ONCE: per-note filter env inside a per-section cutoff ceiling inside a master LP walk — sweeps riding sweeps is the hypnosis *(chezy-prototype forensics 2026-07-05 (song_editor goa act, 346 bars))*
- **journey structure** (w0.86): 6-8 min arc: intro(no bass) -> build -> peak -> BREAKDOWN at ~60% (kick+bass OUT, pads/leads breathe, 8-16 bars) -> filter rebuild -> peak2 -> outro. Use duplicate_bars to stamp sections, clear_bars to carve the breakdown *(curated:claude/2026-07-02)*
- **one change per section** (w0.85): every 8-14 bars exactly ONE element enters or leaves — the ear tracks a single novelty; two changes at once read as a restart *(chezy-prototype forensics 2026-07-05 (song_editor goa act, 346 bars))*
- **glue comp grip** (w0.85): a MUSICAL bus compressor (~6dB grip, ~200ms release) BEFORE the brickwall makes the whole mix breathe with the kick — compliance chains measure right but don't GRIP; add the glue stage *(chezy-prototype forensics 2026-07-05 (song_editor goa act, 346 bars))*
- **bass hp discipline** (w0.85): HP-filter EVERYTHING that is not kick or bass — the 40-80Hz lane belongs to the bassline fundamentals alone; clash-free low end is arrangement + EQ discipline, not limiting *(psytrance production lore verified 2026-07-05 (dsokolovskiy/psychedelicisland/feelyoursound))*
- **one root lattice** (w0.8): every voice octave-locked to ONE fundamental (x1 bass, x2 acid, x4 pad, x8 lead) — the spectrum fuses into a single instrument; voicings that wander break the lattice *(chezy-prototype forensics 2026-07-05 (song_editor goa act, 346 bars))*
- **acid squelch lead** (w0.79): resonant 303-style line (acid303), cutoff automated per phrase, res 2-4; THE lead voice *(curated:claude/2026-07-02)*
- also in this genre's DNA (lower weight): tape saturation

## Inherited from psytrance
- filter build: fx_filter cutoff automated 250->9000 over 4-8 bars, lands ON the drop
- four on floor: kick every beat; openhat on offbeat 8ths
- gain staged saturation: saturation adds LEVEL: after set_track_fx with fx_saturate, trim that track's gainDb by 4-6 dB (drive is tone, gain is level). Get LOUD the clean way: masterGainDb +2..+4 INTO the master limiter (ceiling -1). Verify: clipped_samples 0 AND true_peak_dbtp <= -1 AND LUFS inside the genre window — if LUFS too low, raise masterGainDb (never remove the trims).
- psy hat drive: closed hats straight 16ths vel ~0.5 with offbeat-8th accents ~0.8; open hat on the offbeat
- riser throws: before each section change: reverb-send throw or 2-bar filter riser (automate cutoff up)
- warp beatmatch: beat-match by sourceBpm warp onto ONE grid — never nudge notes; transparent to ~+/-8% tempo distance
- phrase aligned blend: transitions start on a 4-bar boundary of the outgoing deck; dance music breathes in 4/8/16-bar phrases
- bass swap: ONE bass at a time: incoming deck rides fx_djfilter knob +0.5..0.7 until the swap beat, then lows change hands in 0.25 beat
- ...and from the psytrance skill itself: filter transition, tempo map motion, curve shaped automation, mono below 120, riser into drop, impact downbeat, seam connects law, downlifter drain

## Sound recipes (this palette, these moves)
- **goa arp sound**: fmbell or pluck2 16th arps + fx_delay dotted (feedback 0.35) + send to verb bus
- **supersaw wall**: supersaw_fat (7-voice detune, zones cutoff/spread/sub): trance/edm pads+leads; automate cutoff for builds; spread 0.7+ on hooks
- **psy kick tight**: kick_psy (zones punch/decay): psy/techno kick — punch 10-16 hard styles, decay 0.2-0.3 tight; ALWAYS dry

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='psy_straight', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-03 (machine grid, accented offbeat 8ths))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -14..-8, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
