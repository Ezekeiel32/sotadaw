---
name: psytrance-arrangement
version: 8
kind: genre
tags: [psytrance, techno, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 140-148; set the song key (suggested: E minor).
  - Mix: clipped_samples == 0, LUFS -14..-8, band order low>lowmid>mid.
  - ROLLING OFFBEAT BASS is non-negotiable: bass SILENT on the kick, galloping the three 16ths after (null,x,x,x) — kick and bass never collide, so the mix pumps with ZERO sidechain: the arrangement IS the sidechain | lore-verified: 16th-pulse rolling bass, fundamentals 40-80Hz; the pump comes from the kick-hole OR sidechain - both canon, the hole needs zero processing
  - LOUDNESS RECOVERY is non-negotiable: CLOSING STEP, numeric: after the mix is clean (clipped 0, dbtp <= -1), if lufs_integrated < the genre window's LOW bound, raise the makeup fx_trim (the one before fx_brickwall) by (low_bound - lufs) dB, re-render, re-check. Quiet-but-clean is still a FAIL.
  - JOURNEY STRUCTURE is non-negotiable: 6-8 min arc: intro(no bass) -> build -> peak -> BREAKDOWN at ~60% (kick+bass OUT, pads/leads breathe, 8-16 bars) -> filter rebuild -> peak2 -> outro. Use duplicate_bars to stamp sections, clear_bars to carve the breakdown
  - GROOVE PSY STRAIGHT is non-negotiable: apply_groove('psy_straight', amount 1.0) - machine grid with accented offbeat 8ths; psytrance/techno want NO drag, only accent shape.
  - WARP BEATMATCH is non-negotiable: beat-match by sourceBpm warp onto ONE grid — never nudge notes; transparent to ~+/-8% tempo distance
  - LONG FORM PATIENCE is non-negotiable: tension accumulates in MINUTES, not bars: 12-32-bar sections, one journey over 300+ bars; the peak earns itself by arriving late
  - FILTER JOURNEY LAYERS is non-negotiable: motion at three timescales AT ONCE: per-note filter env inside a per-section cutoff ceiling inside a master LP walk — sweeps riding sweeps is the hypnosis
  - FORBIDDEN: echo out cut — beyond ~16% tempo distance: echo-out/cut transition (fx_delay feedback tail on the outgoing deck), not a long blend
---
# Psytrance arrangement (graph-compiled)

Psytrance is a child of **techno** — its groove laws apply unless overridden below.

## The pocket — psy_fullon
kick 1/2/3/4 dry+punchy; bass gallop fills every beat's offbeat 16ths; hats drive 16ths; NO swing (grid is the trance)  *(source: curated:claude/2026-07-06 (wave38 world/anthem canon; freygish+bigroom-vamp+levels-anthem cited f148; afro_pocket i-VII = canon-prior, cite pending))*

## Techniques (weight order — the top ones DEFINE the genre)
- **rolling offbeat bass** (w0.95): bass SILENT on the kick, galloping the three 16ths after (null,x,x,x) — kick and bass never collide, so the mix pumps with ZERO sidechain: the arrangement IS the sidechain | lore-verified: 16th-pulse rolling bass, fundamentals 40-80Hz; the pump comes from the kick-hole OR sidechain - both canon, the hole needs zero processing *(chezy-prototype forensics 2026-07-05 (song_editor goa act, 346 bars))*
- **loudness recovery** (w0.95): CLOSING STEP, numeric: after the mix is clean (clipped 0, dbtp <= -1), if lufs_integrated < the genre window's LOW bound, raise the makeup fx_trim (the one before fx_brickwall) by (low_bound - lufs) dB, re-render, re-check. Quiet-but-clean is still a FAIL. *(eval:2026-07-03 (techno -14.99, grime -12.92 vs windows — recurring clean-but-quiet residual))*
- **journey structure** (w0.93): 6-8 min arc: intro(no bass) -> build -> peak -> BREAKDOWN at ~60% (kick+bass OUT, pads/leads breathe, 8-16 bars) -> filter rebuild -> peak2 -> outro. Use duplicate_bars to stamp sections, clear_bars to carve the breakdown *(curated:claude/2026-07-02)*
- **groove psy straight** (w0.9): apply_groove('psy_straight', amount 1.0) - machine grid with accented offbeat 8ths; psytrance/techno want NO drag, only accent shape. *(curated:claude/2026-07-03 (groove engine profiles -> graph))*
- **warp beatmatch** (w0.9): beat-match by sourceBpm warp onto ONE grid — never nudge notes; transparent to ~+/-8% tempo distance *(skill:dj-blend@v1 (2026-07-03, engine-verified warp primitive))*
- **long form patience** (w0.9): tension accumulates in MINUTES, not bars: 12-32-bar sections, one journey over 300+ bars; the peak earns itself by arriving late *(chezy-prototype forensics 2026-07-05 (song_editor goa act, 346 bars))*
- **filter journey layers** (w0.9): motion at three timescales AT ONCE: per-note filter env inside a per-section cutoff ceiling inside a master LP walk — sweeps riding sweeps is the hypnosis *(chezy-prototype forensics 2026-07-05 (song_editor goa act, 346 bars))*
- **acid squelch lead** (w0.86): resonant 303-style line (acid303), cutoff automated per phrase, res 2-4; THE lead voice *(curated:claude/2026-07-02)*
- **phrase aligned blend** (w0.85): transitions start on a 4-bar boundary of the outgoing deck; dance music breathes in 4/8/16-bar phrases *(skill:dj-blend@v1 (2026-07-03, engine-verified warp primitive))*
- **one change per section** (w0.85): every 8-14 bars exactly ONE element enters or leaves — the ear tracks a single novelty; two changes at once read as a restart *(chezy-prototype forensics 2026-07-05 (song_editor goa act, 346 bars))*
- **glue comp grip** (w0.85): a MUSICAL bus compressor (~6dB grip, ~200ms release) BEFORE the brickwall makes the whole mix breathe with the kick — compliance chains measure right but don't GRIP; add the glue stage *(chezy-prototype forensics 2026-07-05 (song_editor goa act, 346 bars))*
- **bass hp discipline** (w0.85): HP-filter EVERYTHING that is not kick or bass — the 40-80Hz lane belongs to the bassline fundamentals alone; clash-free low end is arrangement + EQ discipline, not limiting *(psytrance production lore verified 2026-07-05 (dsokolovskiy/psychedelicisland/feelyoursound))*
- also in this genre's DNA (lower weight): mono below 120, bass swap, one root lattice, psy hat drive, filter transition, four on floor, curve shaped automation, riser throws, tempo map motion, riser into drop, impact downbeat, seam connects law, downlifter drain, filter build, gain staged saturation

## Inherited from techno
- pump sidechain: fx_pump rate=bpm/60 on pads/keys, depth 0.5-0.8; never on drums
- rumble kick: kick tail feeds a send reverb lowpassed into a rolling rumble
- modular stab: single dark stab/chord repeated with filter automation variation
- brickwall mastering: master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain).
- pedal point: static bass under moving harmony — tension by refusal; the dominant pedal is the classic pre-drop device [Diatonic harmony: pedal/prolongation]
- complementary eq unmask: two voices collide in one band (kick/bass is the classic): BOOST that band slightly in the priority voice and CUT the same band in the other — one collision, two opposite small moves; stem_callouts finds the pair, this is the fix [MASK]
- acapella bridge: the third DJ transition (blend / echo-out / BRIDGE): the outgoing deck cuts at its phrase but its LAST SUNG PHRASE rides HP-filtered (~130Hz) over the incoming deck and fades by bar 8; find the phrase by probing the final ~24 played bars for the loudest-voiced 8-bar window — a DJ cuts where the VOICE ends, not where the file does [battery: solo render -26dB voice exactly across the swap; voiceless tails fall back honestly]
- chance operations: probability on scene transitions (followChance 0.6-0.8): the build advances when the die says so, else runs another pass — organic, never-identical performances from one grid; the aleatoric lineage (Cage's chance operations -> Eno's generative systems -> the Turing-machine module) as a LAUNCHER primitive
- ...and from the techno skill itself: mono check law, mono sub stereo body, symbolic unmask, true peak safety, streaming loudness target, softclip pre limiter, inter sample headroom by genre, tension and release, section contrast, energy contour, strategic pause

## Sound recipes (this palette, these moves)
- **psy bass sound**: sub_clean or reese LOW notes 0.2 len through fx_filter cutoff ~900 + fx_saturate drive 4 (then trim gain -4); DRY (no sends)
- **psy kick sound**: kick_punch dry, gain ~-4; NEVER widened
- **supersaw wall**: supersaw_fat (7-voice detune, zones cutoff/spread/sub): trance/edm pads+leads; automate cutoff for builds; spread 0.7+ on hooks
- **psy kick tight**: kick_psy (zones punch/decay): psy/techno kick — punch 10-16 hard styles, decay 0.2-0.3 tight; ALWAYS dry

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='psy_straight', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-03 (machine grid, accented offbeat 8ths))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -14..-8, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
