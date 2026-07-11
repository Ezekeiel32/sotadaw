---
name: bluegrass-arrangement
version: 1
kind: genre
tags: [bluegrass, country, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 80-180; set the song key (suggested: G major).
  - Mix: clipped_samples == 0, LUFS -16..-12, band order mid>lowmid>low.
  - SCRUGGS ROLL is non-negotiable: Scruggs 3-finger banjo ROLLS: continuous syncopated 8th-note arpeggio patterns (forward/backward/alternating-thumb) that never stop — the perpetual-motion sparkle of bluegrass
  - MANDOLIN CHOP is non-negotiable: the mandolin 'chop': a short, damped closed-chord stab on beats 2 & 4 — it IS the snare of a drumless string band
  - BOOM CHUCK BASS is non-negotiable: the upright bass plays the 'boom' (root on 1, fifth on 3) as the kick of the band — root-five alternation driving the pulse
---
# Bluegrass arrangement (graph-compiled)

Bluegrass is a child of **country** — its groove laws apply unless overridden below.

## The pocket — boom_chuck_roll
Bluegrass 'drive' (~140 BPM, 4/4, near-straight ~52%): a DRUMLESS string-band kit — upright bass = the boom (root on 1, fifth on 3), mandolin CHOP = the snare (damped chord on 2 & 4), banjo Scruggs rolls = the continuous 8th-note hi-hat sparkle; fiddle and banjo trade fast breaks; high-lonesome tenor harmony above. Swing 0.52 rides the 16th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*

## Techniques (weight order — the top ones DEFINE the genre)
- **scruggs roll** (w1.0): Scruggs 3-finger banjo ROLLS: continuous syncopated 8th-note arpeggio patterns (forward/backward/alternating-thumb) that never stop — the perpetual-motion sparkle of bluegrass *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **mandolin chop** (w0.92): the mandolin 'chop': a short, damped closed-chord stab on beats 2 & 4 — it IS the snare of a drumless string band *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **boom chuck bass** (w0.84): the upright bass plays the 'boom' (root on 1, fifth on 3) as the kick of the band — root-five alternation driving the pulse *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **fiddle lead break** (w0.76): a bowed fiddle takes melodic breaks with bluesy double-stops and slides between the vocal verses *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **high lonesome harmony** (w0.68): tight, high, often modal-tinged tenor/baritone vocal harmony stacked above the melody — the 'high lonesome' sound (Bill Monroe) *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **bluegrass breakdown drive** (w0.6): an up-tempo instrumental 'breakdown' where soloists trade fast breaks over the relentless boom-chuck + banjo roll *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*

## Inherited from country
- tape saturation: heavy fx_saturate drive 8-14 over the whole beat bus = grit
- walking bass: bass walks chord tones + chromatic approaches, one note per beat — funk/soul/jazz glue; syncopated pickups into the 1
- twelve bar blues: the 12-bar blues as head and blowing form — central to hard bop
- train beat: country train beat: brushed snare 16th chug (accent 2&4), boom-chick alternating bass (root-5th), ~0 swing — momentum from the chug, not from fills

## Sound recipes (this palette, these moves)
- **string band**: banjo = bright pluck rolling continuous 8ths; mandolin chop = pluck2 damped on 2&4; upright_bass boom-chuck (root-five walking); fiddle break via strings_stacc/`erhu` stand-in (a dedicated `fiddle.dsp` would elevate); acoustic, dynamic, mid-forward — do NOT brickwall (keep the crest).

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -16..-12, band order mid>lowmid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
