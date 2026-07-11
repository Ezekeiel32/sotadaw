// harness validator: constant 440 Hz sine, stereo
import("stdfaust.lib");
process = os.osc(440) * 0.2 <: _,_;
