---
name: mastering
version: 1
kind: mastering
tags: [mastering, loudness, dynamics, delivery, imaging, verdict]
hard_constraints:
  - "LOUDNESS IS A RESULT, NOT A RACE (research_mastering_sota.md §1, VERIFIED). Every streaming service normalizes playback to a fixed integrated-LUFS reference (ITU-R BS.1770) — a master HOTTER than the ref is turned DOWN at playback, so chasing loudness past it trades dynamics for nothing. Master TO the platform reference under its true-peak ceiling. Integrated LUFS is what you READ at the end, not what you push toward."
  - "PLATFORM TARGETS (S11-V62): master to a named platform with auto_master(song, platform=<p>) and gate with master_report(song, platform=<p>). References (integrated LUFS / true-peak dBTP): Spotify -14/-1, Apple -16/-1 (GAIN-ONLY — never limits), YouTube -14/-1, Tidal -14/-1, Amazon -14/-2, Deezer -15/-1, TikTok+Reels -10/-1 (hotter). TIGHTEN dBTP to -2 whenever the master is hotter than -14 LUFS (Spotify rule) or for Amazon. genre still sets band balance; platform sets loudness+ceiling."
  - "THE TRUE-PEAK WALL is -1 dBTP so lossy transcode (Ogg Vorbis/AAC) has room — a +0.3 dBTP file encodes to +1.0. End master[] with {\"id\":\"fx_truepeak\",\"params\":{\"ceiling\":-1.2}} (ceiling = OUTPUT dBTP; -1.5..-2.0 for sub-heavy genres; -2 for Amazon or hot masters). fx_truepeak/fx_brickwall(legacy) is ALWAYS the last live master[] entry. Never type \"limiter\"."
  - "THE CHAIN-ORDER LAW (§2, VERIFIED Ozone/Ian Stewart): corrective BEFORE sweetening; linear (EQ) BEFORE non-linear (compression) ~9/10; the maximizer/wall and dither are ALWAYS last. Order for the bus: EQ/clean -> multiband dynamics -> saturation/exciter -> stereo/M-S imaging -> makeup -> fx_truepeak. Judge TONE at final playback loudness (level-dependent perception), not quiet."
  - "MEASURE LIKE A PRO (S11-V59): master_report surfaces the pro meter set — LUFS integrated/short-term-max/momentary-max, LRA, true-peak dBTP, crest, PLR (TP-integrated), PSR (TP-loudest-3s), L/R correlation. Watch PSR >= ~6 dB (convention): under it = over-limited/crushed. Correlation must stay > -0.2 (mono safety)."
  - "MONO THE LOWS (§3, VERIFIED): a wide sub cancels in mono and ruins vinyl/club. Keep low frequencies centered — never pan/fx_widen the kick/bass (doctor M1 catches it). Image narrowest at the bottom, widest at the top: fx_ms_eq side_low CUT + side_high BOOST widens air without smearing the center. M/S boosts add level — they sit BEFORE the wall."
  - "MULTIBAND for band-specific DYNAMICS only (S11-V60): when ONE band misbehaves (boomy sustained sub, harsh spiky mid) use fx_multiband (LR4 3-band). Gentle 1.3-2:1 high threshold = glue; steeper = corrective. It is transparent at unity — reach for it when broadband compression would move the whole tonal balance to fix one band. NOT a loudness tool."
  - "FIX AT THE SOURCE, never the 2-bus (§6): mastering cannot repair a bad mix. If master_report/auto_master hints point to band balance or a dynamics problem, fix track gains/notes/EQ/parts, then re-run. auto_master exhausts the LEGAL bus moves by construction — its failures ARE source problems."
  - "DITHER only on the FINAL bit-depth reduction, never twice (§2, VERIFIED as 'always last'). 24-bit streaming masters ship UN-dithered (the correct default). For 16-bit CD/delivery: export_master.py --bits 16 applies TPDF dither before the write. Bit-depth policy is convention, not a sourced law."
---
# Mastering — master like the pros (v1)

Grounded in `docs/research_mastering_sota.md` (106-agent verified fan-out). This skill is the
PRO DEPTH on top of `mix-headroom` (which owns the core auto_master/verdict/wall flow). Read it
when the user says "master for Spotify / Apple / club", "make it release-ready", "match this
reference", or when a master needs multiband, mid-side, per-platform loudness, or dither.

## The loop (unchanged, now platform-aware)
1. `auto_master(song, genre, platform=<p>)` — the deterministic converger. It normalizes the
   chain and iterates render→measure→adjust to the target: LUFS into the platform window,
   ceiling to the platform dBTP (+ sub-dominant law), band order via capped ±3 dB EQ / dark
   filter. Character inserts (your multiband, M-S, saturators) are PRESERVED in place.
2. `master_report(song, genre, platform=<p>)` — the ship gate. Fix `fix_first` by its hint,
   repeat until `pass:true`. Then `hear` for what numbers can't judge.
3. `export_master(song)` (24-bit, C2PA-signed) — or `--bits 16` (dithered) for CD.

`platform=` overrides the loudness window + dBTP ceiling with the platform's normalization
reference; `genre` still supplies band balance. Omit platform → generic streaming (-14/-1) or the
genre's KG window. `reference=<wav>` on auto_master = "sit like THIS record" instead.

## Per-platform delivery (VERIFIED primary — §1)
| Platform | Integrated LUFS | True-peak | Note |
|---|---|---|---|
| Spotify / YouTube / Tidal | **-14** | **-1 dBTP** | tighten to -2 if you land hotter than -14 |
| Apple Music | **-16** | **-1 dBTP** | GAIN-ONLY — never limits; don't over-compress for it |
| Amazon Music | **-14** | **-2 dBTP** | enforces -2 |
| Deezer | **-15** | -1 dBTP | |
| TikTok / IG Reels | **-10** (-9..-12) | -1 dBTP | social, hotter |
Quieter than the ref is SAFE (turned up); HOTTER is the risk (turned down + transcode distortion).
CD / club / vinyl targets are **unverified** (§7) — do not invent them; deliver 24-bit -1 dBTP and
say so, or ask.

## The pro chain (order = law)
`fx_trim(in)` → **`fx_multiband`** (band dynamics, if needed) → `fx_saturate`/exciter (density) →
**`fx_ms_eq`** (imaging: mono lows, air on top) → `fx_trim(makeup)` → **`fx_truepeak`** (wall, LAST).
- Corrective EQ (track/source or a managed bus `{type:eq}`) comes BEFORE compression so the comp
  reacts to a balanced signal, not excess bass.
- Reverb never on the master (fx-usage law). Dither is conceptually last (at export, not in the
  chain — the wall is the last audio processor).

## The new pro FX (JIT — no rebuild)
- **fx_multiband** (LR4 3-band comp): `xlow`(150) `xhigh`(2500) crossovers, `attack`/`release`,
  `{low,mid,high}_thresh` `{low,mid,high}_ratio`, `makeup`. Glue: ratios ~1.5, thresholds high,
  makeup ~0. Tame a boomy sub: low_ratio 3-4, low_thresh -24. Transparent at unity.
- **fx_ms_eq** (mid-side EQ): `mid_low`/`mid_high` (center shelves), `side_low`/`side_high` (sides),
  `width` (overall side gain, dB), `low_freq`(250)/`high_freq`(8000). Mono the bass: `side_low -6..-12`.
  Air/width: `side_high +2..+6`. Center presence: `mid_high +1..+3`. Sits BEFORE the wall (adds level).
- Both are Faust FX added like any insert: `{"id":"fx_multiband","params":{...}}` in master[] (or a
  bus). They JIT-compile at load; promote to AOT later for CPU. auto_master keeps them as character.

## The meter set (what master_report now reports — §4)
- **LUFS** integrated (∞, the delivery number), short-term (3s, the loudest section), momentary
  (400ms). Keep loudest short-term no hotter than ~-10 LUFS (Ian Shepherd, convention).
- **dBTP** true-peak (≤ platform ceiling). **LRA** loudness range (dynamic span over time).
- **crest** (peak-RMS), **PLR** (TP−integrated, whole-track headroom), **PSR** (TP−loudest-3s):
  PSR/DR ≥ ~6-8 dB or you're over-limiting (convention — streaming turns you down anyway).
- **correlation** +1 mono / −1 out-of-phase; > -0.2 required. **bands** for tonal balance
  (low 20-120 / lowmid / mid / himid / high) — the TBC pro bands are 20-250/250-2k/2k-8k/8k-20k.

## Genre moves (convention — §5)
- EDM/house/trap/hip-hop/pop: hot (-8..-12 LUFS on the master's own scale), mono sub hard,
  multiband glue on the low band, a touch of side_high air. Reference the platform, not raw volume.
- Acoustic/folk/classical: quiet & dynamic (~-16..-18), minimal limiting, protect PSR/LRA, little
  to no widening; the QUIET-LANE law (no saturator) applies.

## The mistakes to refuse (§6)
Over-limiting (kills PSR) · no true-peak headroom (transcode clip) · wide/panned bass (mono
cancel) · judging tone quiet (decide at final SPL) · mastering the mix's problems (fix at source) ·
over-EQ (many small moves, boost narrow / cut wide).

## Honesty
VERIFIED (build as hard targets): the platform LUFS/dBTP refs, chain order, meter definitions,
mono-bass. CONVENTION (defaults, overridable, never gate a master): genre LUFS ranges, the ~6-8 dB
DR floor, reference/headroom numbers. UNVERIFIED (never fabricate): CD/club/vinyl targets, dither
numerics, per-genre multiband settings, match-EQ tolerance. When you need a value there, use a
labeled engineering default and say so.
