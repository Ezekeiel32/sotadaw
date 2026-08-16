---
name: psybient-arrangement
version: 2
kind: genre
tags: [psybient, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 70-120; set the song key (suggested: E Phrygian).
  - Mix: clipped_samples == 0, LUFS -14..-11, band order low>lowmid>mid.
  - DUB SPACE BLOOM is non-negotiable: psybient space law: long dark delays + a huge damped hall bloom behind everything — the SPACE is an instrument; sends run hot on pads/leads, the sub stays bone dry
  - ACID WHISPER is non-negotiable: a 303 line UNDER the mix (gain low, cutoff modest) — the acid is felt as movement, never a scream; whispered squelch on offbeats
  - WORLD PERC CONVERSATION is non-negotiable: hand percussion (dhol/duduk-adjacent voices) converses in the midground — sparse call-answer hits, never a loop wall
---
# Psybient arrangement (graph-compiled)

## The pocket — psybient_journey
Psybient (~98 BPM): heartbeat kick (1 + and-of-2), deep rolling sub in Phrygian, lush motion pads breathing whole bars, a whispered 303 on offbeats, sparse world percs conversing; the space blooms dark and long — Shpongle/Entheogenic territory. Swing 0.52 rides the 16th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-11 (coverage wave 5: the user's own live genres, session fable-gen; reference class = his Entheogenic imports))*

## Techniques (weight order — the top ones DEFINE the genre)
- **dub space bloom** (w1.0): psybient space law: long dark delays + a huge damped hall bloom behind everything — the SPACE is an instrument; sends run hot on pads/leads, the sub stays bone dry *(curated:claude/2026-07-11 (coverage wave 5: the user's own live genres, session fable-gen; reference class = his Entheogenic imports))*
- **acid whisper** (w0.92): a 303 line UNDER the mix (gain low, cutoff modest) — the acid is felt as movement, never a scream; whispered squelch on offbeats *(curated:claude/2026-07-11 (coverage wave 5: the user's own live genres, session fable-gen; reference class = his Entheogenic imports))*
- **world perc conversation** (w0.84): hand percussion (dhol/duduk-adjacent voices) converses in the midground — sparse call-answer hits, never a loop wall *(curated:claude/2026-07-11 (coverage wave 5: the user's own live genres, session fable-gen; reference class = his Entheogenic imports))*
- **heartbeat half kick** (w0.76): the psybient pulse: a soft round kick on 1 and the and-of-2 (heartbeat), NOT a club four-floor — the sub carries the drive *(curated:claude/2026-07-11 (coverage wave 5: the user's own live genres, session fable-gen; reference class = his Entheogenic imports))*

## Sound recipes (this palette, these moves)
- **psybient space**: lush motion pads (detune pair) = the bed; acid303 whispered LOW (gain -12, its squelch felt not heard); sub = rolling wub reese; dhol speaks midground at 196Hz; sends hot to a dark long hall; kick soft and round — the sub drives, not the kick

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='reggae_lean', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (behind-the-beat lag ~8-12ms, offbeat-8th bubble accents; one-drop space))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -14..-11, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
