---
name: tool-guide-tail
version: 8
description: FULL usage laws for the EXPAND-TOOLS long tail (mounted on demand; fetch this the moment expand_tools runs)
tags: [expanded]
---

# TOOL GUIDE (TAIL) — laws for the tools expand_tools mounts

These tools are not in the core lane; when you mount them, their laws are HERE.
Read your tool's section before big moves — everything below is law.
## auto_master

AUTO-MASTER, THE CONVERGER: closed-loop mastering in one call — normalizes the chain (character inserts preserved, legacy master_limiter killed, masterGainDb folded into the input trim), then iterates render->measure->adjust (makeup/input trims for LUFS, ceiling for true peak + sub-dominant law, capped +/-3dB eq and an on-genre dark filter for band order, NO saturator on quiet lanes) until the verdict passes — typically 2-7 renders. Targets: genre KG lane / reference wav (sit like THIS record) / generic. Touches ONLY master[] + masterGainDb; remaining failures are SOURCE problems reported with hints. Returns moves + before/after + the full master_report. Use FIRST when asked to master/finish/make-it-loud; hand-refine after with update_song_meta + master_report.

## automix

AUTOMIX: the KG mix laws become action, by track role — subs/kick pan CENTER + widener stripped (mono_below_120), pads get fx_widen + filter for a wide bed, bass gets a bpm-locked fx_pump sidechain under the kick, focal parts (lead/vocal) stay centered. Structural + instant (no render loop). VERIFIED: on a bass+pad mix, width -11->-6.6dB (wider) while the sub's stereo side-energy dropped 10x (0.30->0.035, mono-safe) — width WITHOUT losing the low end. COMPLEMENTARY EQ: two sustained melodic tracks whose pitch RANGES overlap (mud) get opposite EQ at the shared register — focal boosts, accompaniment cuts (proven -5.1dB at the collision band, no render needed: the range IS the band profile). The complement to stem_callouts (which finds collisions): this applies the fixes.

## color

COLOR (semantic sound axes, deterministic): warmer (filter tilt + touch of drive on melodic voices) / darker (harder tilt) / brighter (air EQ +hiGain@6k, re-opens filters) / wider (fx_widen on pads/keys/lead ONLY — kick/bass/808 NEVER widen, the mono law holds). amount 0..1; track= scopes one track. EARS-verified: centroid warmer<base<brighter (699<1106<1238Hz), wider +107dB width with the bass untouched. Repeats CLAMP (cutoff floor 900, width cap 1.8) — ten clicks converge, never destroy. vst3 params-based tracks are honestly SKIPPED (directional maps need natural-unit ranges — use set_track_param with the SEMANTIC PARAM MAPS block instead); locked tracks untouched. For 'warmer/brighter/wider' asks on Faust tracks this beats hand-picking fx params.

## compose_line

THE CELL PRIOR (learned, corpus-true): compose a melodic LINE for one EXISTING track — bass/lead/pad — recombined from real phrase cells mined off the house corpus, key+genre-aware, SEARCH-LAW judged: candidates run the music courts + the corpus nearest-lane meter, the track's CURRENT notes are the incumbent, and only a STRICTLY better take displaces them (an empty lane always gets a line; a tie or a dry genre bin leaves the track untouched and says so honestly). Zero tokens, deterministic per seed (omit seed for a fresh roll — it's echoed back; same seed reproduces exactly). Chroma survives only where the target key+genre allowance permits — in-key by the court's OWN law. Use for free toplines, basslines, and melodic lanes on an arrangement you already have; generate_loop stays the genre-RHYTHM authority (its DNA owns the rhythm — do not expect compose_line to speak a genre's drum-locked hook language).

## describe_sound

SEMANTIC EARS SPEAK: zero-shot CLAP words for any wav — ranked role/timbre/energy/space tags + one honest sentence ('punchy, aggressive kick drum, dry'). Battery truth: committed kick/hat/choir named correctly, never cross-family (a drum is never 'female vocals'). Family precision, not species: a boomy kick may read 'tom drum' — trust the family, verify with analyze_wav when the exact species matters. Use before library moves, on import stems, or to narrate what a render actually sounds like. Degrades clean when the CLAP checkpoint isn't cached (available:false, exit 3).

## dj_set

AI DJ SET BUILDER: N audio tracks -> ONE continuous set. THE PLAYLIST BRAIN picks deck order by default (tempo arc + harmonic path + cut placement; pass auto_order false to keep the given order) and each hop picks its transition style: beat-matched staggered blend within warp distance, ECHO-OUT CUT beyond 16% tempo distance (outgoing clip ends phrase-exact, fx_delay tail rings over the incoming deck's clean start — genre-traveling events work: funk 104 -> techno 132). Auto bpm per deck, traveling tempoMap grid, phrase-aligned crossfades, fx_djfilter bass swaps, harmonic-clash warnings. Flags 8-16% blends (soundtouch transparency). bridge=[hopIdx,...] = THE ACAPELLA BRIDGE: the outgoing deck cuts at its phrase but its LAST SUNG PHRASE (demucs two-stems on the tail, loudest-voiced 8-bar window) rides HP-filtered over the incoming deck and fades by bar 8 — verified: -26dB of voice exactly across the swap. Falls back to a plain cut with a warning when the deck has no vocal.

## energy_curve

ENERGY CURVE (symbolic, no render): the song's per-bar energy (velocity x density; drums=onsets, melodic=sustain overlap) as a normalized curve + ASCII sparkline + per-section means, PLUS the contrast-law check — if a build sits within 15% of its drop's energy it flags the violation and prescribes the exact fix (intensify(build,-) + intensify(drop,+); impact comes from CONTRAST, not level). Use before/after intensify to SEE the arrangement's dynamic shape; a dead-flat curve on a multi-section song = it doesn't breathe. track= filters one track. ENERGY_JSON line = machine-readable.

## finish

FINISH THE TRACK — the full auto-production chain in one call: vote chords -> arrange a bare loop into a pop form -> harmonize any MISSING bass/pad section-aware -> place risers/impacts/downlifters at the seams -> automix (center subs, widen pads, sidechain, symbolic unmask). Idempotent (every step no-ops if already present). VERIFIED composite: a 16-bar loop -> 4-min / 12-section track, riser energy in, 0 clipped, sub mono-safe (0.04). out=<name> proposes safely.

## find_genre

SEMANTIC GENRE ROUTING — vibe/mood words -> the nearest REAL genres from the knowledge graph (MiniLM caption KNN over 200+ Genre nodes; kg_vibe kernel). Scores are cosine similarity; "weak": true (top < 0.35) = ADVISORY ONLY — do not force a weak route, ask or default instead. Use when the ask describes a FEEL with no genre word ("smoky late night jazz bar" -> jazz 0.57; "aggressive rap with booming 808s" -> memphis_rap 0.52). Returned names are valid genre context for generate_loop / make_track / start_session — start_session already auto-routes on a tag miss, so call this directly when YOU need genre candidates mid-run (e.g. picking a dna seed or a skill to fetch). Read-only, ~5s (model load).

## freeze_track

TRACK FREEZE (V47) — freeze IS a cached render of symbols, never a bounce-and-forget: the track's source/notes/fx/automation stash VERBATIM in track.frozen (sha-stamped) and the lane plays the cache as audio; gain/pan/mute/sends stay LIVE for mixing. unfreeze restores the symbols bit-exact and deletes the cache (battery: 10/10 round-trip). Use to pin a heavy/JIT voice while arranging or A/B a sound decision. LAWS: never edit a frozen track's notes (unfreeze first — the frozen block is the truth); freeze refuses LOCKED tracks; action=check lists frozen tracks + stale caches. V46 rides the same audio lane: warped clips default to the signalsmith hq rail ("stretch":"fast" = legacy SoundTouch), and audioClips take fadeInBeats/fadeOutBeats/fadeCurve (linear|convex|concave|s) for edge fades.

## humanize

MEASURABLE HUMANIZATION (GrooVAE/GigaMIDI-grounded): adds correlated microtiming drift + metric-accent velocity to a track (the two axes GrooVAE names), with a VERIFIABLE expressiveness score (mechanical=0, human rises — battery: dead grid 0.0 -> 28.1, real groove 60.9; microtiming survives the render at 9.1ms). measure=true scores without changing. track filters (default all), amount 0-1, seed varies. Never touches LOCKED tracks. Unlike a black-box 'humanize' button, the score PROVES it worked.

## infill_region

INFILL (MIDI-GPT lane, symbolic): regenerate ONE track's chosen BARS conditioned on surrounding context — the window's chords (harmony continuity), the track's own density/register elsewhere (feel continuity), and its role. ONLY the window changes; everything else byte-identical (verified: outside-window + other tracks untouched, new notes are chord tones on strong beats 8/8, density matches context, deterministic per seed). density=N (notes/bar) and duration=N (length scale) are the two MIDI-GPT attribute controls the paper found EFFECTIVE (verified: density sparse->busy 8->57 notes, duration 0.5->2.0 scales lengths). style=<fingerprint> (from style_profile extract) generates in the producer's signature register+density (personalization apply; verified: register moves toward the fingerprint, melodic density follows it). 'regenerate bars 17-24 of the lead busier / in my style' without touching the rest. Never LOCKED tracks.

## prescribe

PRESCRIBE (doctor + auto-fix): diagnose then AUTO-APPLY the safe fixes in one call — center/de-widen subs, humanize dead-mechanical parts, unmask mud, add a master limiter — then RE-DIAGNOSE to prove the issue count dropped (self-verifying: battery 6 issues -> 1, idempotent). Creative-decision issues (no arrangement, doesn't breathe) are SUGGESTED not auto-applied. 'fix my track' in one call, every move a named glass-box tool. out= writes a copy; else edits in place.

## readout

THE READOUT (AMAZING PART V): ONE stable page of numbers for any take — five fixed lines, deviations first, every unknown SAID. TAKE = order echo (bpm/key/bars/tracks/notes). EARS = the render's numbers, or 'unrendered — render_song first' (it judges the wav it finds, never renders). GATE = the five-gate states with the first hard reason inline (+ '=> NOT RELEASABLE' when any hard gate fails). COURTS = bad first, then flagged with counts, then ok. DIFF = what changed since YOUR last readout of this song (note deltas per lane, LUFS drift, courts that flipped NEW-BAD/healed, gate flips) — stamped per song, so read-before-and-after every big move and the DIFF line tells you what your move actually did. This is the cheapest full sight of a take; prefer it over re-reading the whole song JSON.

## release_gate

THE RELEASE GATE (AMAZING PART III): the five-gate release verdict on a take. G1 CENSUS = music courts + worldclass floor hard traps; G2 REFERENCE = the genre's gold envelope (LUFS window, clipped=0, PSR floor, band ORDER; measured-closeness is a readout row, not a hard gate); G3 TASTE = the personal head (honest SKIP while the bank is thin — only a FED verdict blocks); G4 NOVELTY = corpus 8-gram substantial-similarity court (the take's own history is pardoned; foreign replay convicts); G5 BLIND = always named not-run. pass:false lists EVERY hard reason plus the honest-gap ledger — fix at the SOURCE (notes/gains/arrangement), never by normalizing output, then re-gate. Reuses songs/<name>.wav when fresher than the json, else renders cache-first. Use before export/finish sign-off, after big arrangement moves, or when the user asks "is it done?" — the gate's word outranks vibes.

## reharmonize

REHARMONIZE: vote the song's chord cycle (chordvote), then rotate=N (wave-29 schema-rotation law: one cycle = N progressions, pick the start that fits the section's mood) or to='Eb,Fm,Ab,Db' (explicit per-cycle target). Retunes melodic tracks ROLE-to-role (root->root, third->third quality-aware) with minimal motion (battery: mean 3.0 semitones, re-vote reads the exact target 4/4, render 0 clipped); tensions keep contour via root delta; drums + LOCKED tracks untouched. out= writes to another song name (propose safely).

## remix_import

THE FULL FLIP: generate an ORIGINAL track in any genre that FITS an absorbed song — reads the import's bpm/key/voted chord cycle/learned groove, generates a fresh genre loop AT that bpm+key, reharmonizes it TO the import's chords (role-mapped minimal motion), applies the import's timing DNA to hats/snare, then VERIFIES by re-voting (battery: 8-bar Cm->G cycle matched root-for-root). Not a copy — a companion: layer it, bridge it, DJ them together. song=<import>, genre=<any KG genre>, seed=N for new takes.

## restore_audio

THE REPAIR RAIL: run BEFORE a real-world recording becomes a track (phone takes, room mics, old bounces) — fixing hum/floor/DC at the SOURCE beats fighting them with fx downstream (mix law). report_only first: QC = peak/RMS, DC, noise floor, 50/60Hz hum + harmonics, hard-clip regions. Auto policy repairs ONLY what QC flags (clean file = byte-copy out, applied=[]); output is ALWAYS a new wav (<in>_restored.wav) — swap it into the clip yourself. Denoise is a bounded spectral gate (default 10 dB, profile from the quietest frames) — at 20+ dB expect audible pumping on tails; prefer two gentle passes over one violent one. Declipping is deliberately NOT attempted: clip_regions > 0 means re-record or accept the crunch (fx_saturate can own it). Studio-clean stems (floor < -60 dB) need NOTHING — do not launder them.

## restyle

RESTYLE (one-gesture style morph): keep EVERY note byte-identical, swap the SOUND + FEEL to any of the 130 KG genres — kick slides to 808 when the genre slides, bass follows the genre's bass_style voice, leads take the genre grid's lead voice, pads/chords take the recipe color voice, swing follows the genre (straight genres REMOVE swing); bpm:true also moves tempo into the genre's range (safe — all timing is in beats, warped audio follows). vst3/preset/sample tracks keep their identity (a preset IS a sound choice); locked untouched. EARS-verified: house->trap moved the rendered centroid 4290->2623Hz with 0 clipped and zero note changes. 'flip this to trap / make it house' = one call, then MAKE-grade fx dressing via automix/finish if wanted.

## set_clip_slot

PERFORMANCE VIEW: author a launcher slot (track x scene) — loopable pattern launched live in the Live view, bar-quantised. notes[] inline OR from_bar (copy arrangement bars). Audio slots: audio_file + offset_sec (+ source_bpm to warp the loop to the song tempo). clear:true empties. Build scene columns that tell a story: A=groove, B=build, C=drop. follow=next|any|stop makes the story PLAY ITSELF (engine-native follow actions: the clip finishing triggers the next/random/stop).

## sidechain_bake

TRUE KEYED SIDECHAIN, zero routing: the duck follows the trigger track's ACTUAL notes — use it whenever the groove is NOT four-on-the-floor (swung trap, breakbeats, half-time: fx_pump's LFO ducks on air there). Returns per-target gainDb automation plans (ABSOLUTE values around each track's base gain); land them with automate (which files receipts) — never hand-copy points into write_song. depth 3-5 dB = musical pump, 6-8 = EDM slam; release 0.3-0.5 beats breathes with the tempo (longer at slower bpm). Re-bake after the kick pattern changes (the bake is a snapshot, not a listener). Four-on-the-floor + you want the classic pump = fx_pump is still the cheaper verb; targets with prior gainDb automation get it REPLACED on --write, so bake LAST or apply via automate onto a clean lane.

## smart_tempo

SMART TEMPO, THE RUBATO CONFORM: a freely-played recording (live piano, a drummer, any un-clicked take) becomes the song's grid. Neural beats/downbeats (beat_this, GPU-elastic; librosa fallback) -> offsetSec + tempoMap[]{bar,bpm,curve}: near-equal bars MERGE into spans (1.2% human jitter never becomes a map), gradual drift rides curve-0 ramps, real tempo jumps step with curve 1, steady takes report stable:true with ONE entry. APPLY LAW: update_song_meta with bpm + tempoMap, and set the recording clip's offsetSec to the reported first downbeat so bar 1 IS downbeat 1. meter is measured from downbeat spacing (waltz reads 3). Confidence < 0.7 = the take fought the tracker — listen before conforming. Read-only; nothing mutates until you apply.

## song_structure

EARS v4b: section boundaries of any wav (audio_path, optional bpm -> bar numbers). Foote-novelty on mel self-similarity, PRECISION-tuned (battery: every emitted boundary within ~2s of a real transition on two ground-truth songs; subtle 8-bar layer-adds may merge). Use on imports, DJ decks, or your own renders to see the arrangement's true joints; feed bars straight into sections[] or duplicate_bars. v2: sections come LABELED (intro/build/drop/hook/break/verse/outro) from energy+vocal-share heuristics with a flat-dynamics guard — loudness-flat material honestly gets neutral part-N names instead of drop-spam; pass a vocal stem path as vocal to unlock verse/hook.

## stem_callouts

PER-STEM CALLOUTS (V28): render stems, analyze each track SOLO, cross-examine pairs — inaudible tracks, solo clippers, misplaced low weight, phase risk, masking fights (with the kick/808-layering exception). sections=true PINS callouts to the timeline (per-section analysis: 'melody+pad fight in lowmid AT Intro bars 1-8' -> fix with automation there, not a global cut). Use when a mix feels crowded or before finish_audit sign-off.

## structure_transfer

STRUCTURE TRANSFER: a reference record's SHAPE becomes a measured arrangement plan — Foote boundaries + labeled sections (intro/build/drop/break...) mapped proportionally onto the target's bar grid (4-bar snapped, monotonic, tiny spans merged), each with measured energy (section RMS/peak) and density hints (break = drop_drums, build = rising+riser, intro/outro = thin). READ-ONLY by law: it plans; you apply via update_song_meta sections[] + duplicate_bars/clear_bars on proposal rails. Same withhold law as song_structure: loudness-flat references get honest part-N names. Battery: planted 3-part reference recovered both cuts within one 4-bar snap, energy arc peaks mid, deterministic.

## style_profile

STYLE FINGERPRINT (MIDI-RWKV personalization lane, symbolic): action=extract learns a producer's signature from their songs (tempo, chord-quality mix, density+register per role, groove/NOMML, dynamics, sections) into a reusable fingerprint; action=score rates any track 0-100 for how ON-BRAND it is, with a per-dimension breakdown. 'is this mine?' as a number with receipts (verified: in-corpus 90, off-style 59-69, self-match 100). No trained model.

## suggest_chords

HARMONY ADVISOR (Scaler-class, fully symbolic): per-slot substitutions + whole-progression rewrites for the song's OWN voted/stored chord lane, each with the theory WHY — function flow (T→S→D→T, retrogressions penalized), secondary dominants (V7 of next), tritone subs, mode mixture (borrowed iv/bVI/bVII), backdoor dominants, harmonic-minor V, chromatic mediants — ranked by voice-leading cost through voicing.py (the same kernel real parts use) + optional KG genre-DNA prior (degrades KG-less). Speaks reharm's exact grammar; every rewrite ships a ready `reharm --to` line and reharm's own law (chordvote reads the target back) closes the circle. Battery: I-vi-IV-V analyzed correctly, tritone/backdoor/secondary all offered with WHYs, full suggest→apply→re-vote circle green. Read-only — suggesting never mutates; apply via reharmonize.

## transitions

THE GLUE: auto-place risers (+optional impacts) at every section boundary INTO a high-energy section (drop/chorus/main/finale) — a bandpass-swept build in the preroll bars landing bar-exact on the downbeat (verified late-bloom: -33->-17->-13dB into the drop). Reads sections[]; skips drop->drop and refuses non-electronic arrangements. preroll=bars (default 2), impacts=true adds a downbeat boom. downlifters=true adds the drain: fx_filter closing on the outgoing track into every drop->break/outro (centroid 2152->539Hz proven). Makes the SEAMS connect after section-aware harmonize makes parts breathe.

## transcribe_lyrics

THE WORDS: ASR for recorded vocals — faster-whisper word timestamps mapped onto the song's OWN clock (bpm + tempoMap via the surgical TempoClock), per-word confidence kept. Lines land write_lyrics-shaped ({beat, text}): apply via write_lyrics and the imported song's words become editable, alignable (align_lyrics) and re-singable (sing.py). find answers "where is the second 'yeah'" in beats — locate for words; pair with clear_bars/surgical moves on the vocal's lanes. HONESTY LAW: sung/rapped ASR is imperfect — the BEATS are the product, the words are evidence; never overwrite user-written lyrics[] with ASR output unless asked. GPU->CPU elastic; first call may download the model.

## tune_vocal

CONTEXT-TUNE (V45), the song-aware autotune: retunes a track's audio clip reading the ARRANGEMENT itself — per-beat chord field from every other track + scale + optional guide melody — target picked by Viterbi (chord-tone/scale/contour), resynthesized through the WORLD vocoder (formants preserved = T-Pain not chipmunk; timing untouched). Styles: tpain (3ms hard quantize + yodel stairs) | hard | natural (drift fixed, vibrato kept) | transparent (never changes note identity). Non-destructive: new wav + clip swap + tuning provenance; always re-tunes from the original. Returns note-by-note report (sung -> target, cents, WHY). guide_track = any melody lane becomes the explicit target line (pitch-to-melody). region [b0,b1] = surgical span only.

## variations

VARIATIONS (propose-and-pick): generate N DISTINCT options for a track's region, each pairwise-different, all playing the window chords, all scoped (nothing outside changes) — written as _<song>_var1..N proposal copies to audition/Accept. For melodic/focal roles you get N real options; low-diversity roles (bass following roots) honestly return fewer. 'give me 3 versions of these bars'. Composes infill.

## vocal_rider

VOCAL RIDER, THE GENERATED FIX: stem_callouts DETECTS "vocal buried in the chorus" — this writes the ride. Per-half-beat vocal-vs-backing margin from the song's own stems (m1 render-stems, or stems_dir for imports) -> slew-limited (1.5dB/half-beat) bounded (±range) ABSOLUTE gainDb points, median-smoothed, thinned to real automation; the fader comes home to base in silence (never boosts noise). target = desired margin over the backing (0 = level with it, +2 = vocal-forward pop). APPLY via automate on the vocal track's gainDb (automate files the receipts). Fader riding, not compression: the waveform is untouched and the move is VISIBLE on the lane. Complementary to automix (static structure) — this is level over TIME.

## vst_presets

THE 4300-SOUND RAIL: factory presets across hosted synths (Surge XT 3559, TAL 256, Odin2 260) AND FX (Surge XT Effects 291: reverbs/delays/chorus/EQ/distortion + experimental Airwindows category — 'get' returns use_as_fx {id, preset} to drop into any fx chain) by name or category (BASS/LEAD/PAD/Atmospheres/Drones/Stabs...). mode='list' browses; mode='get' returns the params dict to inline as source params — presets are STARTING POINTS: tweak named params after.
