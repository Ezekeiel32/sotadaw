// saz — Turkish baglama long-neck lute (arabesk/turkish folk lead; the worst
// eval genre's identity string — births rode generic staccato strings). The
// character IS the doubled course: two Karplus-Strong strings per note,
// detuned a few cents, chorusing as they ring. Bright metallic pluck, long
// neck sustain, small deep-bowl body. Melody lines UNISON (the tradition),
// ornament with fast grace notes.
// ZONE-ENRICHED (face law): shimmer/bowl agent-tweakable.
import("stdfaust.lib");
freq = hslider("freq", 220, 70, 2000, 0.1);
gain = hslider("gain", 0.8, 0, 1, 0.01);
gate = button("gate");
shimmer = hslider("shimmer", 0.5, 0, 1, 0.01);  // course detune spread (cents)
bowl = hslider("bowl", 0.3, 0, 1, 0.01);        // body resonance blend

burst = no.noise * en.ar(0.0004, 0.0028, gate);
damphz = (3800.0 + 3200.0) * (0.65 + 0.35 * gain);  // vel = pick force: soft strums darken                        // bright steel courses
one(f) = excite : string
with {
    n = ma.SR / max(70.0, f);
    pluckdel = max(1.0, n * 0.16);
    excite = burst : (_ <: _, @(int(pluckdel)) :> _ - _) * 0.5
           : fi.lowpass(2, damphz);
    loopfilter = fi.lowpass(1, damphz) * 0.9955;
    string = (+ : de.fdelay4(4096, max(2.0, n - 2.0))) ~ loopfilter;
};
det = 1.0 + (0.0018 + 0.0022 * shimmer);
course = one(freq) + one(freq * det) * 0.85;
bowlres = _ <: fi.resonbp(180, 4, 0.4), fi.resonbp(430, 5, 0.3) :> _;
voice = course <: _ * (1.0 - bowl * 0.5), (bowlres * bowl) :> _;
process = voice * gain * 0.62 <: _, _;  // headroom law: 0 clipped @ vel 1.0 (phrase probe)
