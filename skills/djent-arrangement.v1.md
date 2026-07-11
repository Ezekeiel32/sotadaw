---
name: djent-arrangement
version: 1
kind: genre
tags: [djent, metal, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 90-180; set the song key (suggested: E minor (Phrygian)).
  - Mix: clipped_samples == 0, LUFS -9..-6, band order low>lowmid>mid.
  - POLYMETRIC CHUG is non-negotiable: a fixed odd-length riff cell (3/16, 5/16, 7/16) cycled over a straight 4/4 kick/snare so the accents PHASE against the backbeat and re-sync every few bars — the polymeter is the hook
  - EXTENDED RANGE CHUG is non-negotiable: machine-tight straight-16th palm-muted single-note chugs on a 7/8/9-string's lowest string (drop tuning), gated silent between hits so the low end is percussive not sustained
  - KICK FOLLOWS RIFF is non-negotiable: the kick drum doubles EVERY chug hit exactly (riff and kick are one rhythm), snare pinned to 2 & 4 as the only steady backbeat
---
# Djent arrangement (graph-compiled)

Djent is a child of **metal** — its groove laws apply unless overridden below.

## The pocket — poly_chug
Djent (~120 BPM, 4/4 with a phasing odd-length riff cell): machine-tight straight-16th palm-muted chugs on the lowest string of a 7/8-string (drop tuning), gated silent between hits; the KICK doubles every chug exactly; snare pinned to 2 & 4; a 5/16 or 7/16 riff cell cycles over the 4/4 so accents phase and re-sync on a big downbeat every few bars. Lush reverbed clean bloom in the interludes.  *(source: curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*

## Techniques (weight order — the top ones DEFINE the genre)
- **polymetric chug** (w1.0): a fixed odd-length riff cell (3/16, 5/16, 7/16) cycled over a straight 4/4 kick/snare so the accents PHASE against the backbeat and re-sync every few bars — the polymeter is the hook *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **extended range chug** (w0.92): machine-tight straight-16th palm-muted single-note chugs on a 7/8/9-string's lowest string (drop tuning), gated silent between hits so the low end is percussive not sustained *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **kick follows riff** (w0.84): the kick drum doubles EVERY chug hit exactly (riff and kick are one rhythm), snare pinned to 2 & 4 as the only steady backbeat *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **djent thall** (w0.76): the 'thall' articulation: a slack, pick-scraped, almost-bend low-string chug with a rounded pitched attack (Meshuggah/Fredrik Thordendal), heavier than a clean palm-mute *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **ambient clean bloom** (w0.68): lush reverbed clean/quartal-arpeggio interludes (major9 / add-color guitars, often odd meter) that make the returning chug feel heavier by contrast *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **poly over common** (w0.6): riff written so a repeating melodic figure of one length rides a bar of another length — 'djent math' that resolves on a big downbeat every 2-4 bars *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*

## Inherited from metal
- layered snare: sample clap + synth snare body at -12 to -18
- gain staged saturation: saturation adds LEVEL: after set_track_fx with fx_saturate, trim that track's gainDb by 4-6 dB (drive is tone, gain is level). Get LOUD the clean way: masterGainDb +2..+4 INTO the master limiter (ceiling -1). Verify: clipped_samples 0 AND true_peak_dbtp <= -1 AND LUFS inside the genre window — if LUFS too low, raise masterGainDb (never remove the trims).
- loudness recovery: CLOSING STEP, numeric: after the mix is clean (clipped 0, dbtp <= -1), if lufs_integrated < the genre window's LOW bound, raise the makeup fx_trim (the one before fx_brickwall) by (low_bound - lufs) dB, re-render, re-check. Quiet-but-clean is still a FAIL.
- power chords: rock rhythm guitar: root-5 power chords, palm-muted 8ths into open chorus hits — energy = dynamics contrast, not density
- palm mute chug: metal rhythm: down-tuned palm-muted 8th/16th chugs locked SAMPLE-TIGHT with double-kick; the guitar and kick are ONE instrument — quantize both or neither
- wall of sustain: metal density law: loudness comes from what SUSTAINS between the chug hits — but the GUITARS are the face of the wall: doubled rhythm guitars sustain/ring on chorus chords, cymbal wash fills the top, and the bass guitar sustains UNDERNEATH at -6 or lower relative to the guitars (lowmid must stay dominant over low; a loud sustaining bass flips the balance and reads as mud, not power)

## Sound recipes (this palette, these moves)
- **djent guitar**: highgain_guitar (tight, gated, HP ~90 Hz, mids KEPT for the chug to read), hard L/R double-track; sub_clean doubling the low chug for weight; clean interludes = clean_chime_guitar into a big reverb bus; a punchy triggered kick (hardkick/kick_punch) glued to the riff. Tight, loud, gated low end.

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -9..-6, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
