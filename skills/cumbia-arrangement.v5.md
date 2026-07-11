---
name: cumbia-arrangement
version: 5
kind: genre
tags: [cumbia, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 88-100; set the song key (suggested: A minor).
  - Mix: clipped_samples == 0, LUFS -15..-9, band order low>lowmid>mid.
  - GUACHARACA SCRAPE is non-negotiable: cumbia: continuous shaker/scrape 8ths (hat_metal decay .05 vel-alternating) + offbeat accordion-style stabs
  - OFFBEAT BASS is non-negotiable: bass hits on the 8th between kicks
  - CALL RESPONSE MELODY is non-negotiable: 2-bar call, 2-bar answer; melody talks to itself
---
# Cumbia arrangement (graph-compiled)

## The pocket — cumbia_roll
scrape 8ths continuous, bass 1&3, offbeat stabs; accordion-style melody call/answer  *(source: curated:claude/2026-07-06 (wave36 canon harmony; cumbia/bachata canon own-search f146; Andalusian/royal-road/pop-four/12-bar = textbook commons))*

## Techniques (weight order — the top ones DEFINE the genre)
- **guacharaca scrape** (w1.0): cumbia: continuous shaker/scrape 8ths (hat_metal decay .05 vel-alternating) + offbeat accordion-style stabs *(curated:claude/2026-07-03)*
- **offbeat bass** (w0.93): bass hits on the 8th between kicks *(skill:house-arrangement@v1)*
- **call response melody** (w0.86): 2-bar call, 2-bar answer; melody talks to itself *(curated:claude/2026-07-02)*

## Sound recipes (this palette, these moves)
- **sota drums kit**: kit sota_drums: OUR self-sampled drums - kick 36, deep kick 35, snare 38, clap 39, bright metallic hat 42, dark hat 41, open 46, perc 43, crash 49, repitchable 808 sub 24-40. Loudness-staged, stereo-baked cymbals. PREFER over gm_drums for modern genres.
- **squeeze box**: faust accordion: musette detuned reeds, bellows swell — forró leads, cumbia riffs, tango sighs (slow attack, long phrases), klezmer oom-pah color

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -15..-9, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
