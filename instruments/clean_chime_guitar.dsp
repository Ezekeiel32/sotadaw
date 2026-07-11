// clean_chime_guitar — bright, ringing, shimmering clean electric for
// math-rock / midwest-emo fingerpicked open-tuning arpeggios (American Football twinkle).
// Dual detuned Karplus-Strong strings (slow beating = chorus), broadband pick
// excitation (keeps high harmonics), long sustain so open notes ring & overlap.
// Totally clean — no distortion. ZONE-ENRICHED (face law).
import("stdfaust.lib");
freq   = hslider("freq", 440, 40, 3000, 0.01);
gain   = hslider("gain", 0.7, 0, 1, 0.01);
gate   = button("gate");
sus    = hslider("sustain", 0.996, 0.9, 0.999, 0.0001); // string feedback (long ring)
damp   = hslider("damp", 8000, 1000, 12000, 1);         // string damping (bright, high = chime)
chorus = hslider("chorus", 0.5, 0, 1, 0.01);            // detune + modulation depth (shimmer)

// bright, chime-y pick: broadband noise burst (NOT lowpassed = keeps highs) + a short click transient
// highpass the exciter so we inject a guitar-like body, not sub/DC into the string
pick  = en.ar(0.0006, 0.010, gate) * no.noise;
click = en.ar(0.0002, 0.004, gate) * no.noise;
exc   = (pick + 0.4*click) : fi.highpass(1, 160);

// one Karplus-Strong string tuned to freq*det: bright (high damp), long sustain.
// highpass INSIDE the loop = DC blocker: a one-pole lowpass has unity DC gain, so
// ~0.997 feedback would otherwise amplify the burst's DC offset into a sub roar.
kstr(det) = exc : (+ : de.fdelay4(4096, ma.SR/(freq*det) - 1))
                ~ (fi.lowpass(1, damp) : fi.highpass(1, 100) : *(sus));

// two slightly detuned strings -> slow beating = shimmer
s1  = kstr(1.0);
s2  = kstr(1.0 + 0.004*chorus);          // up to ~7 cents sharp
dry = (s1 + s2) * 0.5;

// gentle modulated (chorus) delay adds movement/depth on top of the beating
lfo = os.osc(0.45) * (1.0 + 5.0*chorus); // modulation depth in samples
cho = dry : de.fdelay(2048, 22 + lfo);
mix = dry*(1.0 - 0.45*chorus) + cho*(0.45*chorus);

// clean bright output veil (tames only the very top harshness) — no distortion
process = mix : fi.lowpass(1, 11000) : *(gain*0.55) <: _,_;
