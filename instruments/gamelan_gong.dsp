// gamelan_gong — the gong ageng: a deep slowly-beating sub fundamental + soft
// inharmonic partials + the characteristic DOWNWARD pitch-glide after the strike,
// very long tail. Marks the colotomic cycle END (the strongest metric point).
// Research: docs/research_genre_expansion_sota.md. ZONE-ENRICHED (face law).
import("stdfaust.lib");
freq = hslider("freq", 65.4, 25, 400, 0.001);   // C2 default
gain = hslider("gain", 0.55, 0, 1, 0.01);
gate = button("gate");
tail  = hslider("tail", 6.0, 1.0, 12.0, 0.1);     // ring seconds
ombak = hslider("ombak", 0.9, 0.0, 4.0, 0.05);    // slow pair-beat Hz
glide = hslider("glide", 0.045, 0, 0.15, 0.001);  // downward pitch-glide depth
boom  = hslider("boom", 0.4, 0, 1, 0.01);         // strike knock level
genv = en.ar(0.002, 0.5, gate);                    // strike-sharp -> settles down = the glide
f0 = freq * (1.0 + glide * genv);
core = (os.osc(f0) + os.osc(f0 + ombak)) * 0.42 * en.adsr(0.004, tail, 0.0, 1.0, gate);
p2   = os.osc(f0 * 2.38) * en.adsr(0.003, tail * 0.4, 0.0, 0.4, gate) * 0.30;
p3   = os.osc(f0 * 4.13) * en.adsr(0.002, tail * 0.2, 0.0, 0.2, gate) * 0.15;
knock = no.noise * en.ar(0.001, 0.02, gate) * boom : fi.resonlp(freq * 6.0, 2.0, 1.0);
process = (core + p2 + p3 + knock) * gain * 0.82 : fi.lowpass(2, 2500) : *(0.887) <: _,_;  // headroom law: cert-calibrated, 0 clipped @ vel 1.0  // vel-1.0 headroom (gain zone is engine-driven)
