// jazz RIDE cymbal (spang-a-lang): 9 inharmonic metal partials + defined bell PING
//   at onset + a LONG shimmering noise WASH (slow decay, rings ~2s+).
// Zones: freq (bell tracks it), gain, gate, decay (wash length s), ping (bell level),
//   wash (shimmer level). Bright, high centroid, sustained.
import("stdfaust.lib");
freq  = hslider("freq", 440, 20, 2000, 0.001);
gain  = hslider("gain", 0.6, 0, 1, 0.01);
gate  = button("gate");
decay = hslider("decay", 2.2, 0.5, 4.0, 0.01);   // wash decay in seconds (LONG default)
ping  = hslider("ping", 0.6, 0, 1.5, 0.01);      // bell / stick attack level
wash  = hslider("wash", 0.7, 0, 1.5, 0.01);      // shimmer wash level

// inharmonic metallic partials (9 detuned squares, bell-like non-integer ratios)
partials = os.square(411) + os.square(527) + os.square(638) + os.square(793)
         + os.square(951) + os.square(1123) + os.square(1327) + os.square(1621)
         + os.square(1897);
menv = en.ar(0.0007, decay*0.55, gate);          // metal body: medium-long decay
metallic = partials/9 : fi.highpass(3, 2600) : *(menv);

// the PING: short pitched bell tone at onset (defined stick attack, tracks freq)
pingenv = en.ar(0.0008, 0.16, gate);
bell = (os.osc(freq*5) + os.osc(freq*7.35)*0.6) : *(pingenv*ping);

// the WASH: highpassed noise, SLOW decay -> the ride rings + shimmers
washenv = en.ar(0.003, decay, gate);
shimmer = no.noise : fi.highpass(4, 6500) : fi.resonbp(9200, 1.4, 1) : *(washenv*wash);

process = (metallic + bell*0.55 + shimmer*0.75) : *(gain*0.55) <: _,_;
