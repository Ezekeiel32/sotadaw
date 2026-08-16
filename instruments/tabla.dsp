// tabla — the Indian drum pair (bollywood/bhangra-adjacent/raga family; dhol
// existed but the tabla's SPEECH did not). PITCH SELECTS STROKE (darbuka law):
// low notes = BAYAN (the bass drum's ge stroke — the signature DOWNWARD pitch
// bend of heel pressure released), high notes = DAYAN (na/tin: tuned metallic
// ring from the syahi-loaded head, quick). Mid = tun (open resonant). Write
// bols as two-pitch lines: ge on the low pitch, na/tin phrases on the high.
// ZONE-ENRICHED (face law): bend/ring agent-tweakable.
import("stdfaust.lib");
freq = hslider("freq", 110, 50, 1200, 0.1);
gain = hslider("gain", 0.7, 0, 1, 0.01);
gate = button("gate");
bend = hslider("bend", 0.6, 0, 1, 0.01);        // bayan heel-release depth
ring = hslider("ring", 0.5, 0, 1, 0.01);        // dayan ring length

exc = ba.impulsify(gate);
dayanness = max(0.0, min(1.0, (freq - 150.0) / 150.0));  // 150->bayan .. 300->dayan
// BAYAN: dark membrane fundamental with the ge PITCH FALL (starts ~35% high,
// heel releases over ~90ms) + a soft skin thud
gef = max(60.0, min(freq, 130.0));
fall = 1.0 + 0.35 * bend * en.ar(0.001, 0.09, gate);
bayan = (os.osc(gef * fall) * en.ar(0.002, 0.32, gate)) * 0.9
      + ((exc : fi.resonbp(gef * 2.4, 9, 1)) * 0.25 * en.ar(0.001, 0.06, gate));
// DAYAN: syahi ring — tight inharmonic pair + skin tap, gated by ring zone
dayf = max(280.0, freq * 1.6);
dayan = ((exc : fi.resonbp(dayf, 42, 1)) * 0.9
       + (exc : fi.resonbp(dayf * 1.34, 38, 1)) * 0.4
       + (no.noise * en.ar(0.0004, 0.006, gate) : fi.highpass(2, 3000)) * 0.3)
      * en.ar(0.0008, 0.10 + 0.22 * ring, gate);
process = (bayan * 2.2 * (1.0 - 0.9 * dayanness) + dayan * 2.6 * (0.1 + 0.9 * dayanness))
        * gain * 0.4 <: _, _;
