---
name: italo_disco-arrangement
version: 4
kind: genre
tags: [italo_disco, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 115-125; set the song key (suggested: C minor).
  - Mix: clipped_samples == 0, LUFS -11..-8, band order low>lowmid>mid.
  - ITALO ARP is non-negotiable: italo disco: octave-jump bass 8ths + bright polysynth arps + gated snare at 115-125; romantic minor melodies sung earnestly — drama over cool
  - GATED REVERB SNARE is non-negotiable: big snare through short bright reverb (mix 0.4-0.5, small size) — 80s exception to the dry-drums law
  - OFFBEAT BASS is non-negotiable: bass hits on the 8th between kicks
---
# Italo_Disco arrangement (graph-compiled)

## Techniques (weight order — the top ones DEFINE the genre)
- **italo arp** (w0.95): italo disco: octave-jump bass 8ths + bright polysynth arps + gated snare at 115-125; romantic minor melodies sung earnestly — drama over cool *(curated:claude/2026-07-03-w10)*
- **gated reverb snare** (w0.8): big snare through short bright reverb (mix 0.4-0.5, small size) — 80s exception to the dry-drums law *(curated:claude/2026-07-02)*
- **offbeat bass** (w0.7): bass hits on the 8th between kicks *(skill:house-arrangement@v1)*
- **vst factory presets** (w0.6): playing a VST like its designers intended: tal_presets.py get '<name>' returns the params dict — inline it as source {kind:'vst3', plugin:'TAL-NoiseMaker', params:{...}}; 256 factory sounds in 8 categories (54 BASS, 77 LEAD, 26 PAD...); search library.json vst_presets by category, then tweak the named params from there *(verified:tal-preset-rail/2026-07-03 (pad 448ms attack/779Hz; bass 10ms/338Hz))*
- **supersaw pads** (w0.5): wide detuned saw chords, whole/half notes, fx_widen — the neon wall *(curated:claude/2026-07-02)*

## Sound recipes (this palette, these moves)
- **string ostinato**: faust strings_stacc: spiccato section, bow bite + no sustain — THE ostinato engine: 8th/16th cells (same 1-2 pitches per bar) under cine_brass swells + timpani hits; also disco/funk stabs
- **tal analog bass**: TAL-NoiseMaker as the analog bass/lead: source {kind:'vst3', id:'TAL-NoiseMaker', params:{'Filter Cutoff':0.2-0.5,'Filter Resonance':0.2-0.5,'Filter Contour':0.3+}} — params fuzzy-match by NAME; automate any of its 93 knobs via set_track_param/automate

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -11..-8, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
