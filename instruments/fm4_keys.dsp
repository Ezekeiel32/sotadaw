// fm4_keys — THE 4-OPERATOR FM FAMILY exemplar (BEST_DAW_30 #6).
// DX-class: four sine operators, one ALGO morph knob (0 = full chain 4>3>2>1
// = growly EP bite; 1 = two parallel pairs = glassy bell-keys), a global
// modulation `index` with its own decay (the FM "strike"), and per-op ratios.
// Alias-safe: carrier+sideband energy bounded by modest max index and the
// ratio caps; headroom law calibrated at vel 1.0.
import("stdfaust.lib");
freq  = hslider("freq", 220, 20, 4000, 0.001);
gain  = hslider("gain", 0.5, 0, 1, 0.01);
gate  = button("gate");
algo  = hslider("algo", 0.35, 0, 1, 0.001);        // chain -> parallel morph
index = hslider("index", 1.4, 0, 4, 0.01);         // FM depth (the strike)
idec  = hslider("index_decay", 0.35, 0.02, 2.0, 0.001);
r2    = hslider("ratio2", 2.0, 0.25, 8, 0.001);    // op ratios vs the note
r3    = hslider("ratio3", 3.0, 0.25, 8, 0.001);
r4    = hslider("ratio4", 7.0, 0.25, 12, 0.001);
att   = hslider("attack", 0.003, 0.001, 1.0, 0.001);
rel   = hslider("release", 0.5, 0.02, 3.0, 0.001);

amp  = en.adsr(att, 0.25, 0.7, rel, gate);
ienv = en.are(0.001, idec, gate) * index;          // the strike fades to tone
dev(f, m) = f * ienv * m;                          // deviation in Hz (bounded)
// operators (frequency-modulation form; each op's freq guarded under Nyquist)
guard(f) = f * (f < ma.SR * 0.45);
op4 = os.osc(guard(freq * r4));
op3c = os.osc(guard(freq * r3) + dev(freq * r3, op4 * 0.5));      // chain: 4 -> 3
op2c = os.osc(guard(freq * r2) + dev(freq * r2, op3c));           // 3 -> 2
op1c = os.osc(guard(freq)      + dev(freq, op2c));                // 2 -> 1
op3p = os.osc(guard(freq * r3) + dev(freq * r3, op4));            // pair B: 4 -> 3
op1p = os.osc(guard(freq)      + dev(freq, os.osc(guard(freq * r2)) * 0.8)); // pair A: 2 -> 1
chain    = op1c;
parallel = 0.62 * op1p + 0.38 * op3p;
process = (chain * (1 - algo) + parallel * algo) * amp * gain : *(0.80) <: _,_;  // headroom law
