// gamelan_saron — struck bronze bar (saron/gangsa): INHARMONIC stretched partials
// (~1 : 2.76 : 5.40 : 8.93, BYU bar-acoustics via docs/research_genre_expansion_sota.md)
// + OMBAK built in: the whole voice is a detuned PAIR (pengumbang + pengisep, ~6 Hz
// apart) so the sum BEATS and shimmers — the beating IS the gamelan sound.
// Sharp mallet attack, long exponential bronze ring, no sustain.
// ZONE-ENRICHED (face law).
import("stdfaust.lib");
freq = hslider("freq", 293.66, 40, 2000, 0.001);  // D4 default (slendro-ish center)
gain = hslider("gain", 0.45, 0, 1, 0.01);
gate = button("gate");
ombak   = hslider("ombak", 6.0, 0.0, 12.0, 0.1);   // pair beat rate Hz (gender ~5, kebyar ~7)
ring    = hslider("ring", 1.6, 0.3, 4.0, 0.01);    // bronze decay s
shimmer = hslider("shimmer", 0.5, 0, 1, 0.01);     // upper-partial level
strike  = hslider("strike", 0.3, 0, 1, 0.01);      // mallet thump level
bar(f) = os.osc(f)        * en.adsr(0.001, ring,        0.0, 0.20, gate)
       + os.osc(f * 2.76) * en.adsr(0.001, ring * 0.55, 0.0, 0.12, gate) * (0.60 * shimmer)
       + os.osc(f * 5.40) * en.adsr(0.001, ring * 0.30, 0.0, 0.08, gate) * (0.35 * shimmer)
       + os.osc(f * 8.93) * en.adsr(0.001, ring * 0.18, 0.0, 0.05, gate) * (0.18 * shimmer);
thump = no.noise * en.ar(0.001, 0.008, gate) * strike : fi.resonbp(freq * 3.0, 2.0, 1.0);
pair = (bar(freq) + bar(freq + ombak)) * 0.5;
process = (pair + thump) * gain * 0.68 : fi.lowpass(2, 9000) <: _,_;  // 0.68 = vel-1.0 headroom (gain zone is engine-driven)
