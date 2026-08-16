// polarity flip (stereo-through) — wave 36, THE PHASE INTERLOCK's heal:
// when kick+808 sum LOSES sub vs the louder alone (destructive phase),
// flipping one side restores the weight (r-5: mono-fold is the test).
import("stdfaust.lib");
flip = checkbox("flip");
g = 1.0 - 2.0 * flip;
process = *(g), *(g);
