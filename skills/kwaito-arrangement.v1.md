---
name: kwaito-arrangement
version: 1
kind: genre
tags: [kwaito, house, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 95-112; set the song key (suggested: A minor).
  - Mix: clipped_samples == 0, LUFS -11..-8, band order low>lowmid>mid.
  - SLOWED HOUSE BOUNCE is non-negotiable: house slowed to ~100-110 BPM: four-on-the-floor kick with a lazy, swung, half-speed-feeling bounce — the space and the slow-motion groove are the point
  - KWAITO DEEP BASSLINE is non-negotiable: a deep, simple, repeating synth/DX bassline (M1/DX7 era) locked to the kick — round sub, minimal notes, the low-end hook
  - M1 ORGAN STAB is non-negotiable: the Korg M1 'organ'/'piano' house stab: a bright plucky chord stab on the offbeats — the melodic signature of kwaito and its house lineage
---
# Kwaito arrangement (graph-compiled)

Kwaito is a child of **house** — its groove laws apply unless overridden below.

## The pocket — kwaito_bounce
Kwaito (~105 BPM, slowed-house bounce, swing ~55%): four-on-the-floor kick with a lazy half-speed feel, clap/snare on 2 & 4, loosely-swung offbeat hats; a deep simple synth bassline locked to the kick; a bright M1-organ chord stab on the offbeats; laid-back chanted township vocals riding the pocket. Space and slow-motion groove are the point. Swing 0.55 rides the 16th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*

## Techniques (weight order — the top ones DEFINE the genre)
- **slowed house bounce** (w1.0): house slowed to ~100-110 BPM: four-on-the-floor kick with a lazy, swung, half-speed-feeling bounce — the space and the slow-motion groove are the point *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **kwaito deep bassline** (w0.92): a deep, simple, repeating synth/DX bassline (M1/DX7 era) locked to the kick — round sub, minimal notes, the low-end hook *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **m1 organ stab** (w0.84): the Korg M1 'organ'/'piano' house stab: a bright plucky chord stab on the offbeats — the melodic signature of kwaito and its house lineage *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **chanted township vocal** (w0.76): laid-back, repetitive chanted/spoken vocals in township slang, call-and-response, riding the pocket rather than singing over it *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **loose swing hats** (w0.68): offbeat hats with a loose human swing (not quantized) giving the slow groove its lilt and shuffle *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*

## Inherited from house
- filter build: fx_filter cutoff automated 250->9000 over 4-8 bars, lands ON the drop
- pump sidechain: fx_pump rate=bpm/60 on pads/keys, depth 0.5-0.8; never on drums
- four on floor: kick every beat; openhat on offbeat 8ths
- offbeat bass: bass hits on the 8th between kicks
- loudness recovery: CLOSING STEP, numeric: after the mix is clean (clipped 0, dbtp <= -1), if lufs_integrated < the genre window's LOW bound, raise the makeup fx_trim (the one before fx_brickwall) by (low_bound - lufs) dB, re-render, re-check. Quiet-but-clean is still a FAIL.
- brickwall mastering: master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain).
- groove ukg shuffle: THE pocket move: apply_groove(track='hats', groove='ukg_shuffle', amount=0.85) after writing on-grid hats - hard 16th swing + ghosted e/a. Quantized-dead hats fail this genre.
- warp beatmatch: beat-match by sourceBpm warp onto ONE grid — never nudge notes; transparent to ~+/-8% tempo distance
- phrase aligned blend: transitions start on a 4-bar boundary of the outgoing deck; dance music breathes in 4/8/16-bar phrases
- bass swap: ONE bass at a time: incoming deck rides fx_djfilter knob +0.5..0.7 until the swap beat, then lows change hands in 0.25 beat
- filter transition: fx_djfilter bipolar knob: LP sweep out the old deck / HP hold the new — the one-knob DJ mixer filter
- tempo map motion: tempoMap on any song: halftime drops, ritardando outros (curve 0), section tempo switches — beats, warped audio, automation all follow
- curve shaped automation: automation point curve -1..1 shapes the leaving segment: >0 late-bloom (THE build shape into drops), <0 early-jump (post-drop settle). Linear builds feel early/flat.
- vst factory presets: factory sounds FIRST for synth-genre leads/pads/basses — ONE CALL: vst_presets(query='PAD'|'BASS'|'LEAD'|..., mode='get', song=<song>, track=<track>) APPLIES the sound directly (source set, or fx appended for Surge XT Effects) — no params to copy. Browse first with mode='list'. Then write notes on the track and reshape 2-5 named knobs per synth-maps. Faust voices are for drums/percussion/utility
- sentence phrase: the 2+2+4 sentence: presentation (idea x2) then continuation/drive to cadence — THE build shape; EDM risers are sentences in disguise [Form: phrase models]
- one change per section: every 8-14 bars exactly ONE element enters or leaves — the ear tracks a single novelty; two changes at once read as a restart
- glue comp grip: a MUSICAL bus compressor (~6dB grip, ~200ms release) BEFORE the brickwall makes the whole mix breathe with the kick — compliance chains measure right but don't GRIP; add the glue stage
- cadence modal VII i: the modal cadence: bVII -> i (no leading tone; THE loop-closer of minor-modal electronic music)
- andalusian descent: stepwise minor descent (i-VII-VI-...): the andalusian/lament lineage
- singer songwriter schema: vi-IV-I-V (Am-F-C-G) or its rotation I-V-vi-IV: THE four-chord pop engine since the mid-90s; relative-minor reading i-VI-III-VII is equally valid [Popular music: four-chord schemas]
- tonal ambiguity dual tonic: the singer/songwriter schema carries NO authentic cadence (only plagal IV-I or stepwise VII-i), so one loop reads as major AND relative minor at once (the 'Despacito' law: Bm-G-D-A = vi-IV-I-V in D or i-VI-III-VII in Bm) — write one progression, recolor it dark/bright per section via bass root emphasis + melody tones, zero modulation cost [Popular music: four-chord schemas]
- schema rotation: cyclical schemas keep their identity started ANYWHERE in the cycle (rotation) — one schema = four progressions; choose the rotation whose first chord is the section's mood anchor (IV-start = lift, vi-start = ache) [Popular music: four-chord schemas (variation laws)]
- complementary eq unmask: two voices collide in one band (kick/bass is the classic): BOOST that band slightly in the priority voice and CUT the same band in the other — one collision, two opposite small moves; stem_callouts finds the pair, this is the fix [MASK]
- unmask escalation ladder: unmask in escalating precision, stop at the first rung that works: 1) static complementary EQ; 2) wideband sidechain duck (whole voice, when trigger plays); 3) dynamic-EQ/multiband duck (ONLY the masked band, ONLY when the trigger hits) — never pay more transparency than the collision costs [MASK]
- sidechain unmask bass: sustained bass masks a percussive kick because the ear locks onto the constant voice — duck the bass only when the kick hits and both survive; the FX-side complement to rolling_offbeat_bass (where the ARRANGEMENT is the sidechain: bass written in the kick's holes needs no ducking) [MASK]
- acapella bridge: the third DJ transition (blend / echo-out / BRIDGE): the outgoing deck cuts at its phrase but its LAST SUNG PHRASE rides HP-filtered (~130Hz) over the incoming deck and fades by bar 8; find the phrase by probing the final ~24 played bars for the loudest-voiced 8-bar window — a DJ cuts where the VOICE ends, not where the file does [battery: solo render -26dB voice exactly across the swap; voiceless tails fall back honestly]
- structure inheritance: a remix/companion inherits the SOURCE'S section skeleton: its sections become the arrangement form at their real durations — same bar count, same energy arc [battery: Foote on the RENDER, blind to the JSON, found 5/6 joints within 3 bars of the source's]
- auxiliary sections law: intros/outros/interludes/codas are AUXILIARY: they never count toward a form's identity (a strophic song with an intro is still AAA) — judge form by the MAIN-section pattern only; our labeler/arranger semantics follow this
- mono below 120: keep everything below ~120Hz CENTERED — a stereo/out-of-phase sub cancels on mono club subs and phone speakers and eats headroom; the single most important width rule. fx_widen with a low-cut on the side, or simply pan/write bass + kick dead center [mono-compatibility law]
- mono check law: AUDITION IN MONO with and without your width moves: side-channel content disappears completely in the fold, and aggressive M/S EQ (the classic +8dB-lows-on-sides) can make a track barely audible summed — if the mix collapses, the width was borrowed, not earned [the fold test]
- mono sub stereo body: the techno bass trick: split the bass — a MONO sub (sine, dead center, <120Hz) carries the weight; a STEREO body (harmonics, saturated, widened above ~150Hz) carries the character. Club-safe AND wide [Weapon/NI law]
- riser into drop: the build-up riser: a bandpass-swept noise tension line in the 1-2 bars before a drop, gain late-blooming (env^2) to land EXACTLY on the downbeat — the single most universal EDM/pop transition; place at every low->high section seam, never drop->drop
- impact downbeat: a single low sub-boom ON the drop downbeat (the counterpart to the riser): marks the arrival, fills the sub the riser vacated as it peaks — cheap, essential, one note
- seam connects law: sections must CONNECT, not just abut: after each part breathes per-section (density), the boundary INTO a lift wants a build (riser/fill/filter-open) and the arrival wants a mark (impact/crash) — the glue is what separates an arrangement from a playlist of loops
- downlifter drain: the drop-out drain: close a lowpass filter on the outgoing lead/pad over the last 1-2 bars into a break/outro (cutoff 18k->~420Hz, early-jump curve) — energy LEAVES so the break lands as relief; the automation complement to the riser (no dedicated FX needed)
- symbolic unmask: find frequency collisions WITHOUT rendering: two sustained melodic tracks whose note pitch-RANGES overlap share a register (the range IS the band profile) -> complementary EQ at the overlap center (focal +1.5, accompaniment -3.5, mud zone 120-2000Hz only). The unmask ladder rung 1, applied symbolically
- true peak safety: master to <=-1 dBTP TRUE peak, not sample peak — Spotify/Apple/EBU R128 all specify -1 dBTP; inter-sample peaks reconstruct ~1-1.4dB higher than sample peaks (up to 1.81dB on drill 808s) and clip after lossy codec transcoding. A sample-domain limiter alone cannot guarantee it.
- streaming loudness target: the 2026 universal streaming target is -14 LUFS integrated (Spotify/YouTube/Tidal/Amazon all normalize to -14; Apple/Facebook -16). Do not chase loudness past it — platforms normalize DOWN. Master to -14 LUFS / <=-1 dBTP and it plays everywhere.
- softclip pre limiter: a TRANSPARENT soft clipper (pure tanh, no de-emphasis tone filter) before the final limiter shaves the sharpest 1-3dB of transients so the limiter works less hard = more loudness that still breathes. fx_saturate is the WRONG tool (its tone filter darkens 19-33%); use fx_softclip. The standard trap/drill loudness move.
- inter sample headroom by genre: dense 808/kick material (drill, house four-on-floor) generates the most inter-sample overshoot (~1.4-1.8dB); sparse material (ambient) almost none. A fixed sample ceiling of -3.0 lands all 14 tested genres <=-1 dBTP at ~0.3dB loudness cost (the ceiling clips transient PEAKS, not sustained level). Oversampled (4x/8x) true-peak limiting is the textbook fix.
- tension and release: the core arrangement arc: build energy + anticipation (risers, filter opens, added layers, strategic PAUSE) then release it dramatically at the drop. A track without a tension curve is a loop. (composes with transitions risers/impacts + automation builds)
- section contrast: adjacent sections MUST differ to keep engagement — the chorus/drop stands out from the verse by altering melody, harmony, rhythm OR instrumentation; the bridge/break introduces new material. Sameness across sections = the doctor A2 breathe failure.
- energy contour: shape dynamics across the song. THE KEY LAW: impact comes from CONTRAST, not pushing the limiter — if the build is already loud+full, the drop has nowhere to go. So make a drop hit harder by SOFTENING the section before it (intensify build -) AND hardening the drop (intensify drop +): louder hits + more 16th hats + more layers. Keep the sub OUT of the build so the drop bass lands. Density+velocity+layer-count are the energy dial.
- strategic pause: a beat of silence or a filter-swept gap right BEFORE the release amplifies its impact — the ear resolves the held breath. The downlifter + a 1-beat drum cut sells the drop.

## Sound recipes (this palette, these moves)
- **kwaito kit**: M1-organ/piano stab = organ_soul/hammond_organ on the offbeats; deep round bassline = sub_clean/bass_warm (DX7 character) locked to the kick; clap_909 + kick_808/kick_punch for the slowed-house kit; loose swing (not quantized).

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -11..-8, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
