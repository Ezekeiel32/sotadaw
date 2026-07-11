---
name: producer-workflow
version: 1
kind: workflow
tags: [always, workflow, finish, doctor, prescribe, style, variations, infill, humanize, mastering]
compiled_from: hand-written (campaign firings 52-83, each verb battery-verified)
---
# Producer workflow — the "make it better" arc

The DAW ships a full production arc as MCP verbs. This skill maps what a producer
SAYS to the verb that does it, the order to compose them, and the gotchas. Every
verb here is battery-verified; prefer them over hand-editing notes one by one.

## Intent → verb
- "finish this / turn this loop into a track / arrange it out" → **finish** (chords
  → arrange to a pop form → harmonize a missing bass/pad sectioned → transitions
  (risers/impacts/downlifters/fills) → automix → true-peak master). Idempotent.
- "what's wrong with it / critique my mix / is this good" → **doctor** (symbolic,
  no render): reports fixable issues (no arrangement, doesn't breathe, off-center/
  widened sub, mud collision, off-center lead, dead-mechanical, no master), each
  naming its fix. Shows its work — every finding is a fact about the JSON.
- "fix it / clean it up / make it better" → **prescribe** (doctor + auto-apply the
  safe fixes, then re-diagnose to prove it). Creative issues (no arrangement,
  doesn't breathe) are SUGGESTED not auto-applied.
- "it sounds robotic / add feel / humanize" → **humanize** (microtiming + velocity;
  measure=true first to see the NOMML class + expressiveness score, then apply).
- "make it sound like me / my style / on-brand" → **style_profile**: action=extract
  from the user's songs → a fingerprint; action=score any track 0-100; then
  **infill_region** with style=<fingerprint> to generate in their register+density.
- "regenerate these bars / redo the lead in the drop" → **infill_region** (window
  regen conditioned on the surrounding chords + density; only the window changes).
  density=N and duration=N are the two effective attribute controls.
- "give me options / a few versions / alternatives" → **variations** (N distinct
  region regenerations as _var1..N proposal copies to audition/Accept).

## Sequences
- **"make this release-ready"**: finish → doctor (verify 0 issues) → prescribe (any
  remainder). The master lands at the 2026 streaming spec (~-14 LUFS, true peak
  <= -1 dBTP) automatically across genres.
- **"diagnose then fix"**: doctor → (read the findings aloud) → prescribe → doctor
  again (prove the count dropped).
- **"personalize"**: style_profile extract (their catalog) → score (this track) →
  infill_region style=<them> on the weak sections.

## Gotchas (hard-won)
- **variations / style density is LOW for bass & pad** — they follow chord roots, so
  you get fewer distinct options and register-bias only. Melodic/focal roles give
  the full N. Don't promise 3 bass variations.
- **true-peak master is -3.0 sample ceiling** (fx_brickwall is a sample limiter;
  inter-sample peaks reconstruct ~1.4dB higher on dense 808/kick material). This is
  safe across 14 genres. A transparent fx_softclip exists for louder masters but its
  loudness integration is not yet wired into finish.
- **LOCKED tracks are never touched** by any verb.
- **doctor is symbolic (no render)** — fast; use it freely before/after edits.
- Everything edits PROPOSAL copies; the base changes only on the user's Accept.

## Verify (the ears/batteries back every verb)
finish/prescribe output is checked by tools/arc_quality.py + arc_quality_sweep.py
(release-shaped across genres). humanize by expressive_battery. The whole arc is
reachable through the sidecar (tools/mcp_smoke.py). If a producer asks "is it
actually good," run analyze_wav — 0 clipped, true peak <= -1 dBTP, mono-safe.
