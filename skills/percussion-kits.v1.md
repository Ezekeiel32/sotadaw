---
name: percussion-kits
version: 1
kind: sound-design
tags: [faust, drums, percussion, modal, acoustic-kit, orchestral, latin, marching, glitch, cookbook]
hard_constraints:
  - Modal voices reuse skills/faust-reusable-blocks block #5 (pm.strikeModel + pm.modalModel). Zones freq/gain/gate, end `<: _,_`.
  - pm.strikeModel argument order is (HPcutoff, LPcutoff) per physmodels.lib line 2789 -- the library's OWN usage comment reverses it. Getting this wrong dulls or over-brightens every strike.
  - Real acoustic-kit realism (cymbal wash, phase-coherent bleed, room IR) is sample-reinforced; the modeled core is the tunable win.
  - Build under UNREGISTERED .dsp names first (instant JIT re-render), promote hot voices via gen_faust.sh + rebuild once.
---
# Percussion kits (Slice D) -- acoustic · orchestral/mallet · Latin · marching · glitch

Assume `import("stdfaust.lib");`. All tuned/struck voices are ONE modal recipe with swapped tables.
Full DNA + sources: docs/research_sound_foundry_ii.md. Deepens the marimba/vibraphone/timpani stubs.

## The modal skeleton (extends reusable block #5 to bars/tubes/plates)
```
modalBank(f0,N,ratio,mgain,t60) = _ <: par(i,N, pm.modeFilter(f0*ratio(i), t60(i), mgain(i))) :> _;
hard = hslider("hardness",0.4,0,1,0.01);                       // mallet: felt <-> brass
exc  = pm.strikeModel(40+hard*400, 1500+hard*14500, 0.3, gain, gate);  // (HP, LP) -- NOT (LP,HP)
process = exc : modalBank(freq,N,ratio,mgain,t60) : fi.dcblocker <: _,_;
```
Swap {ratio, t60, gain} per material (metal T60 = seconds; wood = tens of ms; membrane = air-damped):

## Orchestral & mallet (pure Faust)
- Glockenspiel/orch bells: `ratio=(1, 2.76, 5.40, 8.93, 13.3)`, long metal T60. Xylophone: bar ratios, short.
- Marimba/vibraphone: DEEPEN the existing voices; vibes add motor tremolo (AM LFO ~5Hz) + pedal sustain.
- Tubular bells: the strike pitch is a "phantom" of modes 4:5:6 (Hibberts). Celesta = small struck bars, bright+short.
- Crotales = high tuned bronze (gamelan-adjacent). Timpani = membrane modal + tuned + roll (fast low-vel repeats).
- Untuned battery: orch bass drum, snare, triangle, woodblock, castanets, whip/slapstick, wind machine (filtered noise).
- **LAW: gong/tam-tam/cymbal shimmer is a nonlinear low->high energy CASCADE -- a linear modal bank cannot make it; add nonlinear mode coupling or a slow-attack-HF fake / sample layer. Do NOT hard-code "a few ms" for its timescale.**

## Studio acoustic kits -- jazz/rock/metal + brushes (hybrid)
- Kick = body `os.osc(f0*(1+drop*en.ar(0.001,0.045,gate)))` + beater click `strikeModel` (felt=low HP/LP, wood=bright tick) + shell modes + `ma.tanh` glue.
- SNARE (the hard one) = two-head air-coupled mode PAIRS + nonlinear threshold-triggered wire buzz (ghost notes barely rattle, rimshots snap) -- gate `no.noise` bandpass by head energy.
- Toms = membrane modal tuned; hats/ride/crash = the cymbal energy-cascade caveat above (sample-reinforce the wash). Brushes = sustained noise swish vs tap.
- Multi-mic = close + overhead + room as a bus SoundRecipe (bleed delays PHASE-COHERENT or the sum combs to mud); gated-reverb as an 80s template.
- Unlocks the live-kit genres the EDM library lacked: jazz/rock/metal/funk/soul/gospel/blues/Americana/fusion + a real drum-TUNING surface.

## Latin & Afro-Cuban ensemble -- clave-locked (pure Faust)
- Membranes (congas/bongos/timbale heads) = modal block, `freqs = fund*(1,1.593,2.135,2.295,2.653,...)`, N=6-10; tuning: quinto~C5, conga~D4, tumba~G3.
- 5 conga strokes = a preset table over {exPos, t60_scale, noise_crack, sub_thud}: open{0.7,0.35}, slap{0.9,0.12,+HP crack}, bass{low,long}, muff, heel-toe ghost.
- Shakers/scrapers (maraca/cabasa/shekere/guiro) = PhISEM (Poisson noise bursts through `fi.resonbp`). Bells (cowbell/campana/agogo) = two-osc square bandpassed (808-bell relative).
- **THE CLAVE BRAIN (the real value):** encode son 3-2/2-3 direction + the son/rumba 1-sixteenth difference + interlocking roles (cascara/tumbao/martillo/bell/shaker) as SoundRecipes / HAS_GROOVE so parts sound like an ENSEMBLE, not a stack. Clave/tresillo also upgrades any 3-2 genre (Bo Diddley, New Orleans, reggaeton dembow).
- LAW: the 6/8 "bembe clave" narrative was refuted -- use the standard son/rumba claves.

## Marching / drumline (hybrid)
- High-tension Kevlar snare = modal head `f0~260-320Hz` ratios (1,1.59,2.14,2.30,2.65,2.92), SHORT decreasing T60s + tensioned-WIRE buzz (nonlinear chatter gated by head energy, NOT plain white noise).
- Tenors/quads = tuned membranes (arcs/sweeps); tuned 5-6 bass line = split/unison "runs"; clash-cymbal line is the weak spot (sample-layer the crash + choke).
- **PAS-40 RUDIMENT ENGINE** = a symbolic template pack (tap/diddle/flam/drag/roll primitives) into library/grooves.json. Unlocks marching/DCI + hybrid trap/drill/phonk that sample drumline snares/buzz-rolls.

## Glitch / IDM percussion (100% pure Faust)
- Click/ping = `trig:ba.impulsify -> fi.resonbp(fc,Q,g)`, Q 5 (pop) to 30-120 (metallic); bank inharmonic fc for bell/rim.
- Pure sine beep (Alva Noto) = `fi.nlf2(f,1)` pinged or `os.osc(f)*en.ar(0.0003,rel,gate)` sub-ms attack. Pulsar trains, ring-mod, FM-metal (block #7).
- Bitcrush + stutter = reuse fx_lofi (#2) + `de.sdelay` buffer-repeat. **LAW: sample-rate reduction = ZOH sample-and-hold (hold ONE value N samples), NOT a running average -- averaging is anti-aliasing decimation that KILLS the grit.**
- Challenge = sample-accurate micro-timing: reset every retriggered envelope or it injects its own spurious click.

Companions: faust-reusable-blocks (#5 membrane + the new bar/tube/plate + PhISEM), sound-palette
(which drum when), faust-808 (the 808), fx-usage (space + gated-reverb).
