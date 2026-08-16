---
name: house-arrangement
version: 15
kind: genre
tags: [house, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 120-128; set the song key (suggested: A minor).
  - Mix: clipped_samples == 0, LUFS -10..-6, band order low>lowmid>mid.
  - Harmony: min7/9th piano and organ stabs (the M1-piano lineage voicing).
  - FOUR ON FLOOR is non-negotiable: kick every beat; openhat on offbeat 8ths
  - BRICKWALL MASTERING is non-negotiable: master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain).
  - OFFBEAT BASS is non-negotiable: bass hits on the 8th between kicks
  - VST FACTORY PRESETS is non-negotiable: factory sounds FIRST for synth-genre leads/pads/basses — ONE CALL: vst_presets(query='PAD'|'BASS'|'LEAD'|..., mode='get', song=<song>, track=<track>) APPLIES the sound directly (source set, or fx appended for Surge XT Effects) — no params to copy. Browse first with mode='list'. Then write notes on the track and reshape 2-5 named knobs per synth-maps. Faust voices are for drums/percussion/utility
  - GROOVE UKG SHUFFLE is non-negotiable: THE pocket move: apply_groove(track='hats', groove='ukg_shuffle', amount=0.85) after writing on-grid hats - hard 16th swing + ghosted e/a. Quantized-dead hats fail this genre.
  - WARP BEATMATCH is non-negotiable: beat-match by sourceBpm warp onto ONE grid — never nudge notes; transparent to ~+/-8% tempo distance
  - FORBIDDEN: echo out cut — beyond ~16% tempo distance: echo-out/cut transition (fx_delay feedback tail on the outgoing deck), not a long blend
---
# House arrangement (graph-compiled)

## The pocket — house_grid
kick 1/2/3/4, openhat offbeats, clap 2&4  *(source: curated:claude/2026-07-05 (wave28 functional layer; FHO blueprint KG_SOURCES inc.9))*

## Techniques (weight order — the top ones DEFINE the genre)
- **four on floor** (w1.0): kick every beat; openhat on offbeat 8ths *(skill:house-arrangement@v1)*
- **brickwall mastering** (w0.97): master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain). *(autonomy-cycle:techno/2026-07-03 (0.571->0.714 after loudness lesson; residual lufs/dbtp fails traced to broken master_limiter era))*
- **offbeat bass** (w0.95): bass hits on the 8th between kicks *(skill:house-arrangement@v1)*
- **vst factory presets** (w0.95): factory sounds FIRST for synth-genre leads/pads/basses — ONE CALL: vst_presets(query='PAD'|'BASS'|'LEAD'|..., mode='get', song=<song>, track=<track>) APPLIES the sound directly (source set, or fx appended for Surge XT Effects) — no params to copy. Browse first with mode='list'. Then write notes on the track and reshape 2-5 named knobs per synth-maps. Faust voices are for drums/percussion/utility *(verified:one-call-apply/2026-07-04 (phrasing lesson FALSIFIED: 0.857->0.857 w/ 0 usage; refined to tool-side friction fix — TAL 87-param + Surge blob applied+rendered via single calls))*
- **groove ukg shuffle** (w0.9): THE pocket move: apply_groove(track='hats', groove='ukg_shuffle', amount=0.85) after writing on-grid hats - hard 16th swing + ghosted e/a. Quantized-dead hats fail this genre. *(curated:claude/2026-07-03 (groove engine profiles -> graph))*
- **warp beatmatch** (w0.9): beat-match by sourceBpm warp onto ONE grid — never nudge notes; transparent to ~+/-8% tempo distance *(skill:dj-blend@v1 (2026-07-03, engine-verified warp primitive))*
- **loudness recovery** (w0.85): CLOSING STEP, numeric: after the mix is clean (clipped 0, dbtp <= -1), if lufs_integrated < the genre window's LOW bound, raise the makeup fx_trim (the one before fx_brickwall) by (low_bound - lufs) dB, re-render, re-check. Quiet-but-clean is still a FAIL. *(eval:2026-07-03 (techno -14.99, grime -12.92 vs windows — recurring clean-but-quiet residual))*
- **phrase aligned blend** (w0.85): transitions start on a 4-bar boundary of the outgoing deck; dance music breathes in 4/8/16-bar phrases *(skill:dj-blend@v1 (2026-07-03, engine-verified warp primitive))*
- **one change per section** (w0.85): every 8-14 bars exactly ONE element enters or leaves — the ear tracks a single novelty; two changes at once read as a restart *(chezy-prototype forensics 2026-07-05 (song_editor goa act, 346 bars))*
- **glue comp grip** (w0.85): a MUSICAL bus compressor (~6dB grip, ~200ms release) BEFORE the brickwall makes the whole mix breathe with the kick — compliance chains measure right but don't GRIP; add the glue stage *(chezy-prototype forensics 2026-07-05 (song_editor goa act, 346 bars))*
- **singer songwriter schema** (w0.85): vi-IV-I-V (Am-F-C-G) or its rotation I-V-vi-IV: THE four-chord pop engine since the mid-90s; relative-minor reading i-VI-III-VII is equally valid [Popular music: four-chord schemas] *(OMT2 'Four-Chord Schemas' + 'Blues Harmony' (Hughes & Lavengood, Open Music Theory v2, CC BY-SA, viva.pressbooks.pub/openmusictheory) via curated:claude/2026-07-05 (wave29))*
- **mono below 120** (w0.85): keep everything below ~120Hz CENTERED — a stereo/out-of-phase sub cancels on mono club subs and phone speakers and eats headroom; the single most important width rule. fx_widen with a low-cut on the side, or simply pan/write bass + kick dead center [mono-compatibility law] *(iZotope Learn (mid/side processing; 8 mid/side mistakes) + Weapon/NI/Mastering-The-Mix corroboration, read 2026-07-05 via curated:claude (wave34 space lane))*
- also in this genre's DNA (lower weight): pump sidechain, bass swap, complementary eq unmask, filter build, filter transition, unmask escalation ladder, sidechain unmask bass, structure inheritance, mono check law, curve shaped automation, tonal ambiguity dual tonic, acapella bridge, mono sub stereo body, schema rotation, tension and release, section contrast, energy contour, strategic pause, tempo map motion, sentence phrase, cadence modal VII i, andalusian descent, riser into drop, impact downbeat, seam connects law, downlifter drain, symbolic unmask, true peak safety, streaming loudness target, softclip pre limiter, inter sample headroom by genre, auxiliary sections law

## Sound recipes (this palette, these moves)
- **sota drums kit**: kit sota_drums: OUR self-sampled drums - kick 36, deep kick 35, snare 38, clap 39, bright metallic hat 42, dark hat 41, open 46, perc 43, crash 49, repitchable 808 sub 24-40. Loudness-staged, stereo-baked cymbals. PREFER over gm_drums for modern genres.
- **tal analog bass**: TAL-NoiseMaker as the analog bass/lead: source {kind:'vst3', id:'TAL-NoiseMaker', params:{'Filter Cutoff':0.2-0.5,'Filter Resonance':0.2-0.5,'Filter Contour':0.3+}} — params fuzzy-match by NAME; automate any of its 93 knobs via set_track_param/automate
- **kick punch zones**: kick_punch now has knobs (source.params or automate): punch 0-1.5 (click level), drop 0-8 (pitch-env depth), decay 0.05-1.2s (body), tail 0-1, drive 0.2-4 (pre-tanh). Defaults = the classic sound. Longer decay 0.6-0.9 = room-shaking house kick; drive 2+ = distorted techno.
- **hat zones**: hat knobs: decay 0.01-0.6 (0.05 closed default; 0.25-0.4 = OPEN HAT — same voice, one knob), tone 4k-16k (bp centre), sizzle 0.5-8 (Q). Automate decay for open/closed patterns on ONE track.
- **clap 909 zones**: clap_909 knobs: decay 0.08-0.8s (main burst), tone 600-4000 (bp centre), spread 0.3-2.5 (pre-burst roll tightness). tone 2800 = brighter electro clap; spread 2 = loose human clap.

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='house_shuffle', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (classic house ~56%: pushed e/a 16ths, offbeat-8th open-hat accents))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -10..-6, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
