// guira — metal scraper (bachata/merengue's timekeeper; the palette's shaker
// is soft maraca-class — no metallic scrape existed). A stick dragged across
// ridges: noise through a bright metallic band, amplitude-modulated by the
// RIDGE PULSE (a fast pulse train = individual ridge ticks). PITCH SELECTS
// STROKE like darbuka: low notes = short closed "chick", high notes = long
// open sweep "shhhick" (the classic bachata upbeat). freq also sets ridge
// rate, so grid pitch shapes the scrape's texture.
// ZONE-ENRICHED (face law): edge/ridges agent-tweakable.
import("stdfaust.lib");
freq = hslider("freq", 220, 50, 1200, 0.1);
gain = hslider("gain", 0.7, 0, 1, 0.01);
gate = button("gate");
edge = hslider("edge", 0.6, 0, 1, 0.01);        // metallic brightness
ridges = hslider("ridges", 0.5, 0, 1, 0.01);    // ridge-tick prominence

open = max(0.0, min(1.0, (freq - 180.0) / 180.0));  // 180Hz->closed .. 360Hz->open
dur = 0.045 + open * 0.16;                       // chick .. sweep
env = en.ar(0.004 + open * 0.02, dur, gate);
ridgehz = 55.0 + freq * 0.35;
pulse = (os.lf_sawpos(ridgehz) < 0.28) * (0.45 + 0.55 * ridges);
body = no.noise * env * (1.0 - ridges * 0.5 + pulse)
     : fi.resonbp(2800 + edge * 2600, 1.6, 1.0)
     : fi.highpass(2, 1500);
shine = no.noise * env : fi.resonbp(7200, 3.0, 1.0) * (0.3 + 0.5 * edge);
process = (body + shine) * gain * 0.34 <: _, _;  // headroom law: 0 clipped @ vel 1.0 (bachata + cert probes)
