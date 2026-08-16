---
name: motown-arrangement
version: 2
kind: genre
tags: [motown, soul, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 90-140; set the song key (suggested: C major).
  - Mix: clipped_samples == 0, LUFS -14..-11, band order lowmid>mid>low.
  - TAMBOURINE BACKBEAT is non-negotiable: (see technique node)
  - HANDCLAPS BACKBEAT is non-negotiable: (see technique node)
  - MELODIC BASS LINES is non-negotiable: (see technique node)
  - FOUR FLOOR SNARE is non-negotiable: the Motown stomp: SNARE (not kick) on ALL FOUR beats (Supremes grammar) — or heavy 2&4 backbeat; either way the snare leads
  - TAMBOURINE 24 is non-negotiable: tambourine locked on 2 & 4 (with the snare) — the shimmer that says Hitsville
---
# Motown arrangement (graph-compiled)

Motown is a child of **soul** — its groove laws apply unless overridden below.

## The pocket — hitsville_stomp
Motown (~126 BPM, straight-8th to light shuffle): the SNARE stomps ALL FOUR beats (Supremes grammar) with tambourine shimmering 2&4; kick anchors 1&3; the Jamerson bass WEAVES syncopated 16ths against the straight grid (root on 1, chromatic approaches, ghost pickups); piano/vibes stab the offbeats; baritone sax pumps the floor; call-and-response backings answer the lead every 2 bars. Swing 0.52 rides the 16th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*

## Techniques (weight order — the top ones DEFINE the genre)
- **tambourine backbeat** (wNone):  *(r-23 instrumentation whitelists w78 (2026-07-16))*
- **handclaps backbeat** (wNone):  *(r-23 instrumentation whitelists w78 (2026-07-16))*
- **melodic bass lines** (wNone):  *(r-23 instrumentation whitelists w78 (2026-07-16))*
- **horn stabs backbeat** (wNone):  *(r-23 instrumentation whitelists w78 (2026-07-16))*
- **glockenspiel sparkle** (wNone):  *(r-23 instrumentation whitelists w78 (2026-07-16))*
- **vibes sparkle** (wNone):  *(r-23 instrumentation whitelists w78 (2026-07-16))*
- **four floor snare** (w1.0): the Motown stomp: SNARE (not kick) on ALL FOUR beats (Supremes grammar) — or heavy 2&4 backbeat; either way the snare leads *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **tambourine 24** (w0.92): tambourine locked on 2 & 4 (with the snare) — the shimmer that says Hitsville *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **jamerson bass weave** (w0.84): James Jamerson bass: syncopated 16th-note weaving line — roots on the one, then chromatic approaches, drops, ghost 16ths AGAINST the straight grid *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **gospel plagal pop** (w0.76): major-key I-IV plagal gospel motion + ii-V pop cadences, 2-4 chords a bar of harmonic drive *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **baritone sax floor** (w0.68): baritone sax doubling the bass line / pumping roots — the warm floor under the strings and vibes *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **call response backings** (w0.6): lead vocal answered by group backings ('ooh', hand-claps, ad-libs) every 2 bars — church call-and-response as pop architecture *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*

## Inherited from soul
- send reverb: reverb on a BUS at mix 1.0, balance via send level; kick/808 DRY
- behind beat snare: snare 0.02-0.05 beats late = laid-back head-nod
- m7 chords: minor 7th / extended chords, mid register, soft velocity
- walking bass: bass walks chord tones + chromatic approaches, one note per beat — funk/soul/jazz glue; syncopated pickups into the 1
- horn stabs: tight unison brass hits on arrangement accents (1 and the +of-2) — call-response with the vocal; short, loud, then GONE (space is the funk)
- spectral presence: the top octaves are the genre's FACE: after limiting, verify mid_500_2k >= ~8%% and himid_2k_6k >= ~1%% of band energy for horn/clav/lead genres — a passing band ORDER with collapsed magnitudes is still a dead mix. Fix at the SOURCE: brighter voicings, less lowpass, lead levels up — never a master shelf.
- plagal shuttle: I<->IV oscillation (the 'amen' motion) — harmonic warmth without dominant tension; loops forever without demanding a cadence [Popular music: harmonic schemas]
- mode mixture: borrowed iv / bVI / bVII inside major — instant bittersweet color; the borrowed iv on the pre-cadence is the classic tearjerker [Chromaticism: mode mixture]
- ...and from the soul skill itself: cadence modal VII i, doo wop schema, minor blues, mud zone 200 400, parallel detail pump, refrain hook, bridge contrast law, expressive performance, organ bed

## Sound recipes (this palette, these moves)
- **hitsville rig**: vibraphone + jazz_piano offbeat stabs; upright_bass/bass_warm playing the Jamerson weave (write the 16th syncopation INTO the notes); tambourine = bright hat on 2&4; sax_section/brass_stab baritone floor + string pads (strings_disco soft); warm tape saturation, mid-forward vintage master — do NOT brickwall

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='rock_drive', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (8th-note push a hair ahead, heavy 2&4 — motorik/punk/indie engine))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -14..-11, band order lowmid>mid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
