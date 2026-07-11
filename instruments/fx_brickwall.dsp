// fx_brickwall: TRUE brickwall = lookahead limiter (musical gain riding) +
// hard safety clip at the ceiling (catches the attack-window transient leak).
// Replaces the broken master_limiter. ceiling in dBFS.
import("stdfaust.lib");
ceil_db = hslider("ceiling", -1.0, -12.0, 0.0, 0.1);
c = ba.db2linear(ceil_db);
clip(x) = max(-c, min(c, x));
process = co.limiter_lad_stereo(0.005, c, 0.0008, 0.05, 0.2) : clip, clip;
