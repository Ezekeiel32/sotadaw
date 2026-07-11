---
name: tool-guide
version: 2
description: FULL usage laws for the CORE-LANE tools (the long tail's laws live in tool-guide-tail — get_skill it right after expand_tools)
tags: [always]
---

# TOOL GUIDE — the long-form laws the schemas no longer carry

Schemas were dieted (firing 110, the defer tax): each tool's description is now its
essence; EVERYTHING below remains law. Find your tool before big moves.

## arrange_song

LOOP -> SONG SKELETON (deterministic, zero tokens): takes any loop song (e.g. generate_loop output) and builds genre-aware form: EDM genres get intro/build/DROP/break/outro; song-form genres (gospel/soul/rock/reggae...) get verse/CHORUS/bridge — pass genre to pick by class-aware stripping — intro = kick+hat only, break = no drums, builds ramp velocities, outro decays, filter-arc into the first drop. THE fastest 'whole track' start; differentiate sections after. form='pop' [seed=N] samples a REAL pop form from the Harmonix label grammar (912 human structures: verse-chorus placement, bridge late, measured durations) — new seed = new believable form; or form='intro,build:8,drop:16,...' explicit.

## chord_map

CHORDS FROM THE SYMBOLS: bar-wise chord map voted from the song's own notes (duration x velocity, bass witnesses x2.5, dominant-7 detection; muted *_sketch tracks vote on imports; drums excluded). Battery: 9/12 exact incl. the 7s on 12-bar blues (audio-HMM baseline was 2/12), 4/4 on clean triads. write=true persists song['chords'] as a chord lane; tracks= filters the voters. Use for reharmonization, 'what key/chords is this', and matching new parts to an import's harmony.

## doctor

SONG DOCTOR: symbolic critique WITHOUT rendering — reads a song and reports fixable issues, each naming the exact fix tool: no harmony, no arrangement (->arrange/finish), doesn't breathe (->harmonize sectioned), off-center/widened sub (->automix mono law), mud collision (->automix unmask), off-center lead, dead-mechanical part (->humanize), no master limiter (->finish). The 'what's wrong / how to make it better' first half; composes chordvote+automix-roles+NOMML+section analysis. Fast, glass-box.

## generate_loop

THE LOOP GENERATOR (from scratch): genre in -> a complete, editable, loop-perfect song out in one call — drums from the genre's PatternArchetype grid (KG loop DNA, ALL 130 graph genres), bass in the genre's key by its bass_style (offbeat/roots/sliding-808/psy-rolling/sustained/log-drum), a color pad from its SoundRecipe voice, swing + sub-dominant-aware master applied. Deterministic per seed; new seed = new take from the same DNA. Start here, then edit/extend/loop_variations.

## harmonize

COMPOSE FROM THE CHORD LANE: generate a NEW bass/pad/arp track that plays the song's OWN voted chord changes, in key, as an editable track (verified: the new part re-votes the exact progression 4/4). role=bass|pad|arp; rhythm=straight|offbeat|roll (bass) / whole|pulse (pad) / up|updown (arp); octave shifts register; track names it. role=melody generates a SINGABLE lead over the changes (chord tones on every strong beat — verified 8/8 — scale passing tones + rests between, arcing contour; rhythm=flowing|sparse|busy, seed varies the line). THE ANSWER to 'rewrite/fix the melody': one scoped call, not thousands of hand-notes. sectioned=true makes ANY role's density follow the arrangement (verse sparse, drop busy — battery: 7x density swing, harmony intact 116/116 downbeats). The chord lane's fourth verb after read/transform/match.

## locate

THE SCALPEL'S EYES — resolve any human coordinate into song coordinates. Give a timestamp ('1:23'), beat, bar, or section name: returns the exact beat (tempoMap-aware), the section, clock time, bpm, and WHAT IS SOUNDING there per track (notes with pitch names, active clips, live automation values, roles, muted/locked). Give a free-text query ('the squelchy bass') and it ranks track candidates with evidence + a ready selector. No args beyond song = the song MAP (sections, tracks, roles). ALWAYS the first call when the user points at a sound, a moment, or 'this part here'.

## master_report

THE MASTERING VERDICT: render (if stale) + measure + judge against the genre's KG MixTarget in ONE call — pass/score, per-check got-vs-want (clipped, true peak, LUFS window, band order, spectral floors, phase, masterGainDb=0 law, brickwall-last law) and a SOURCE-FIX hint on every failure, ordered by what to fix first. THE loop: edit -> master_report -> fix the fix_first check -> repeat until pass:true. Same engine as the UI's MASTER CHECK button and the eval gauntlet.

## select_notes

DRY-RUN a surgical selector — see the EXACT notes it matches (track, beat, bar, pitch name, vel, len) before cutting. Zero edits. Selector fields (all optional, AND-ed): tracks ('name' | ['a','b'] | {match} | {role: kick|bass|snare|hat|perc|pad|lead|keys|chords|vocal|fx}); range as beats [a,b) | bars [a,b) | section 'drop' (or {name, occurrence}) | time '1:23' or [t0,t1] | around {beat|bar|time, widthBeats}; pitch (29 | 'F#1' | [lo,hi] | {classes:['F','Ab']} | {names:['F#2']}); vel {min,max}; len {min,max}; grid {step, phase, tol} (e.g. step 1, phase 0.5 = offbeat 8ths); nth 3 = 3rd matching onset (-1 = last, chords count once); every {step:2, phase:0} = every 2nd onset; count N = first N onsets; indices [..] = the UI selection's note indices (one track).

## surgical_edit

THE CUT — apply ops to EXACTLY the selector's notes and file a receipt; every other note/track/param is untouchable (the sidecar diffs the proposal against receipts and flags anything out of scope). Ops run in order on the matched set: {op:'set', vel|pitch|len|start} absolute · {op:'shift', pitch:+2 (transpose st) | start:+0.25 (nudge beats) | vel:+0.1} · {op:'scale', vel|len: factor} · {op:'quantize', grid:0.25, strength:0..1, phase} · {op:'humanize', timing:0.02, vel:0.05, seed} (deterministic) · {op:'stretch', factor, anchor} (half/double-time in place) · {op:'velocity_ramp', from, to} (crescendo across the range) · {op:'delete'} · {op:'insert', notes:[{start,len,pitch(midi or 'F#1'),vel,track?}]} (must land inside the range) · {op:'replace', notes:[...]} (rewrite the matched riff) · {op:'retrack', to:'track'} (move notes to another track). preview:true = show the receipt without writing. THE LAW: user asks for a scoped change -> locate -> select_notes (verify) -> surgical_edit. NEVER rewrite whole tracks/songs for a scoped ask.

LONG-TAIL LAW POINTER: tools mounted via expand_tools (auto_master, automix, dj_set, finish, humanize, tune_vocal, vst_presets, ...) have their FULL laws in the tool-guide-tail skill — get_skill("tool-guide-tail") the moment you expand.


## THE PERCUSSIVE WALL LAW (f139, proven by bisect + ablation)

On percussive-dominant material (kick/snare-led mixes), fx_trim INTO a master wall
buys GAIN REDUCTION, not loudness: the transients already ride the ceiling, so
+12dB of trim returned +2dB of rms with the wall in place and +10.4dB without it
(kick-only ablation, untitled_3). Loudness on such material comes from TRACK
BALANCE, density and sustain — never from pushing the wall. A dBTP reading pinned
well BELOW the ceiling (e.g. -5.3 under a -1.0 wall) on percussive content is the
limiter's between-hits behavior, not a broken ceiling.
