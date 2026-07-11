---
name: synthpop-arrangement
version: 2
kind: genre
tags: [synthpop, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 110-130; set the song key (suggested: C major).
  - Mix: clipped_samples == 0, LUFS -11..-8, band order lowmid>low>mid.
  - SYNTHPOP HOOK is non-negotiable: synthpop: a MONOPHONIC analog lead hook carries the song (the hook IS the chorus), big gated snare, arpeggiated 8th bass; melody over texture, always
  - GATED REVERB SNARE is non-negotiable: big snare through short bright reverb (mix 0.4-0.5, small size) — 80s exception to the dry-drums law
  - ARP 8TH is non-negotiable: relentless 8th/16th arpeggio (pluck) outlining the chord, fx_delay dotted
---
# Synthpop arrangement (graph-compiled)

## Techniques (weight order — the top ones DEFINE the genre)
- **synthpop hook** (w0.95): synthpop: a MONOPHONIC analog lead hook carries the song (the hook IS the chorus), big gated snare, arpeggiated 8th bass; melody over texture, always *(curated:claude/2026-07-03-w11)*
- **gated reverb snare** (w0.85): big snare through short bright reverb (mix 0.4-0.5, small size) — 80s exception to the dry-drums law *(curated:claude/2026-07-02)*
- **arp 8th** (w0.8): relentless 8th/16th arpeggio (pluck) outlining the chord, fx_delay dotted *(curated:claude/2026-07-02)*
- **topline first** (w0.7): pop law: the melody IS the product — a hook every 2 bars, sections exist to frame the topline; if a part fights the vocal melody, the part loses *(curated:claude/2026-07-03-w9)*
- **vst factory presets** (w0.6): playing a VST like its designers intended: tal_presets.py get '<name>' returns the params dict — inline it as source {kind:'vst3', plugin:'TAL-NoiseMaker', params:{...}}; 256 factory sounds in 8 categories (54 BASS, 77 LEAD, 26 PAD...); search library.json vst_presets by category, then tweak the named params from there *(verified:tal-preset-rail/2026-07-03 (pad 448ms attack/779Hz; bass 10ms/338Hz))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -11..-8, band order lowmid>low>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
