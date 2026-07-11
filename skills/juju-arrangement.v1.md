---
name: juju-arrangement
version: 1
kind: genre
tags: [juju, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 100-125; set the song key (suggested: G major).
  - Mix: clipped_samples == 0, LUFS -13..-10, band order lowmid>mid>low.
  - TALKING DRUM SPEECH is non-negotiable: the dundun talking drum BENDS pitch mid-phrase (squeeze the strings) to 'speak' — use a bending drum voice (dhol bend zone) playing conversational phrases across the groove
  - SHEKERE EIGHTHS is non-negotiable: shekere/beaded-gourd rides straight 8ths with hand accents — the juju timekeeper
  - PRAISE CALL RESPONSE is non-negotiable: leader sings praise lines, the chorus answers the SAME melody — long-form medleys that flow without stopping
---
# Juju arrangement (graph-compiled)

## The pocket — juju_weave
Jùjú (~112 BPM, 12/8 undercurrent — swing ~0.56): kick 1&3 soft; shekere rides straight 8ths; the TALKING DRUM (pitch-bending) speaks conversational accents across slots 3/6/11/14; two clean guitars interlock a two-chord major vamp (I-IV cycling); leader/chorus praise call-response; long-form — flow, don't drop. Swing 0.56 rides the 16th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*

## Techniques (weight order — the top ones DEFINE the genre)
- **talking drum speech** (w1.0): the dundun talking drum BENDS pitch mid-phrase (squeeze the strings) to 'speak' — use a bending drum voice (dhol bend zone) playing conversational phrases across the groove *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*
- **shekere eighths** (w0.92): shekere/beaded-gourd rides straight 8ths with hand accents — the juju timekeeper *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*
- **praise call response** (w0.84): leader sings praise lines, the chorus answers the SAME melody — long-form medleys that flow without stopping *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*
- **interlocking guitars** (w0.76): three guitars in distinct registers (lead, mi-solo mid, rhythm) weave complementary cyclic riffs — no one plays chords, the interlock is the harmony *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*

## Sound recipes (this palette, these moves)
- **juju band**: talking drum = dhol with the BEND zone ridden per-note (it speaks); shekere = bright hat 8ths; two interlocking plucks (lead octave 5 + mi-solo pluck2 octave 4); warm bass; pedal-steel color = pad_motion soft swells

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -13..-10, band order lowmid>mid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
