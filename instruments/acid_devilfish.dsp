declare name "acid_devilfish";
declare description "Devil-Fish-grade acid voice: drifting detuned saw pair + sub square into a diode-ladder with velocity-accented squelch and tanh drive";
import("stdfaust.lib");

freq = hslider("freq", 110, 20, 4000, 0.01);
gain = hslider("gain", 0.6, 0, 1, 0.01);
gate = button("gate");

cutoff = hslider("cutoff", 1250, 120, 9000, 1) : si.smoo;
reso = hslider("reso", 0.78, 0, 1, 0.01) : si.smoo;
envmod = hslider("envmod", 0.62, 0, 1, 0.01) : si.smoo;
fdecay = hslider("fdecay", 0.17, 0.03, 1.2, 0.005);
drive = hslider("drive", 1.7, 0.4, 6, 0.01) : si.smoo;
subamt = hslider("sub", 0.38, 0, 1, 0.01) : si.smoo;
detamt = hslider("detune", 0.5, 0, 1, 0.01) : si.smoo;

accent = max(0.0, gain - 0.72) * 3.5714;
drift = 1.0 + os.osc(0.11)*0.0016 + no.lfnoise0(3.1)*0.0011;
f0 = freq * drift;

oscA = os.sawtooth(f0);
oscB = os.sawtooth(f0*(1.0 + 0.0052*detamt) + 0.11);
oscSub = os.square(f0*0.5);
premix = oscA*0.50 + oscB*0.34 + oscSub*0.4*subamt;

fenv = en.adsr(0.0008, fdecay*(1.0 + 0.35*accent), 0.0, 0.07, gate);
sweep = pow(2.0, fenv * envmod * (2.1 + 1.7*accent));
fc = max(90.0, min(cutoff * sweep * (0.55 + 0.45*gain), 11500.0));
nfreq = min(0.45, fc*2.0/ma.SR);
q = 0.72 + reso*(9.5 + 4.0*accent);

filt = premix*(0.55 + 0.5*accent) : ve.diodeLadder(nfreq, q);
sat = ma.tanh(filt*drive) * (1.0/sqrt(max(0.4, drive)));
aenv = en.adsr(0.0012, 0.18, 0.45, 0.09, gate);
lvl = 0.22 + 0.78*gain;

process = sat*aenv*lvl*0.5 : fi.highpass(2, 80.0) <: _,_;
