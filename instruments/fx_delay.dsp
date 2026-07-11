// stereo feedback delay with damped repeats; time in ms (agent sets to beat-fractions)
import("stdfaust.lib");
dtime = hslider("time", 375, 20, 1500, 1);       // ms
fb    = hslider("feedback", 0.35, 0, 0.85, 0.01);
mix   = hslider("mix", 0.22, 0, 1, 0.01) : si.smoo;
echo(x) = x : (+ : de.fdelay(65536, dtime*ma.SR/1000.0)) ~ (fi.lowpass(2, 4500) : *(fb));
process = _,_ <: (par(i,2,echo) : par(i,2,*(mix))), par(i,2,*(1-mix)) :> _,_;
