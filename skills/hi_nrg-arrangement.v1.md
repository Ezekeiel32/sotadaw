---
name: hi_nrg-arrangement
version: 1
kind: genre
tags: [hi_nrg, disco, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 120-142; set the song key (suggested: A minor).
  - Mix: clipped_samples == 0, LUFS -11..-8, band order low>lowmid>mid.
  - OCTAVE BASS 16THS is non-negotiable: THE Hi-NRG signature: octave-pumping synth bass in straight 8ths/16ths (R-r'-R-r') replacing the hi-hat as timekeeper — accent via filter envelope
  - FOURFLOOR HINRG is non-negotiable: kick 1-2-3-4, clap+snare on 2 & 4, open hat on every off-8th — the relentless 130 BPM engine
  - MINOR ARP STAB is non-negotiable: natural-minor arpeggio stabs and octave lead lines (Prophet/Juno) — energetic, campy, melodramatic
---
# Hi_Nrg arrangement (graph-compiled)

Hi_Nrg is a child of **disco** — its groove laws apply unless overridden below.

## The pocket — octane_engine
Hi-NRG (~130 BPM, machine-straight): kick 1-2-3-4, clap+snare on 2&4, open hat every off-8th; THE signature — the synth bass pumps ROOT-OCTAVE straight 8ths/16ths (R-r'-R-r') replacing the hi-hat as timekeeper, accent via filter; natural-minor arpeggio stabs; Simmons tom fills into sections; diva belt on top.  *(source: curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*

## Techniques (weight order — the top ones DEFINE the genre)
- **octave bass 16ths** (w1.0): THE Hi-NRG signature: octave-pumping synth bass in straight 8ths/16ths (R-r'-R-r') replacing the hi-hat as timekeeper — accent via filter envelope *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **fourfloor hinrg** (w0.92): kick 1-2-3-4, clap+snare on 2 & 4, open hat on every off-8th — the relentless 130 BPM engine *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **minor arp stab** (w0.84): natural-minor arpeggio stabs and octave lead lines (Prophet/Juno) — energetic, campy, melodramatic *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **simmons tom fill** (w0.76): Simmons/synth-tom descending fills into section changes — the 80s dance exclamation mark *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **disco diva belt** (w0.68): a belted diva vocal riding the top, big reverb, call-and-answer with the synth stabs *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*

## Inherited from disco
- offbeat bass: bass hits on the 8th between kicks
- tape saturation: heavy fx_saturate drive 8-14 over the whole beat bus = grit
- walking bass: bass walks chord tones + chromatic approaches, one note per beat — funk/soul/jazz glue; syncopated pickups into the 1
- horn stabs: tight unison brass hits on arrangement accents (1 and the +of-2) — call-response with the vocal; short, loud, then GONE (space is the funk)
- four floor disco: disco four-on-floor: live kick + open-hat on the offbeat 8ths + 16th hi-hat ride; strings/octave bass carry euphoria
- spectral presence: the top octaves are the genre's FACE: after limiting, verify mid_500_2k >= ~8%% and himid_2k_6k >= ~1%% of band energy for horn/clav/lead genres — a passing band ORDER with collapsed magnitudes is still a dead mix. Fix at the SOURCE: brighter voicings, less lowpass, lead levels up — never a master shelf.
- two chord vamp: two-chord vamp: harmony as texture, motion lives in the beat (dnb/dub/phonk/ambient)
- cadence plagal IV i: plagal IV->i: the soft 'amen' close — gospel/soul/lofi warmth

## Sound recipes (this palette, these moves)
- **octane rig**: the octave bass = chip_bass/bass_warm playing R-r' 8ths/16ths (write the octave INTO the notes — it IS the genre); Prophet arp stabs = supersaw; clap_909 + four-floor kick_punch; Simmons toms = timpani pitched high w/ short decay; bright, relentless, campy

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -11..-8, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
