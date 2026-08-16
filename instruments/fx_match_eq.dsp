// THE MATCH EQ (F3, docs/IMPORT_FINALE.md 2026-07-15): 8 log-spaced peaking
// bells sitting on the exact geometric centers of master_match.py's 60-16k
// measurement bands — the import finale EQs the product's MEASURED band
// deltas back toward the record (shelves alone left band_rms 4.4dB: +6 mud
// at ~700, -9 missing presence at ~5.6k on goldenbrown). Stereo-through;
// every gain is an automatable zone like any fx. One-octave bandwidths.
import("stdfaust.lib");

g1 = hslider("g85",    0, -9, 9, 0.1);
g2 = hslider("g171",   0, -9, 9, 0.1);
g3 = hslider("g344",   0, -9, 9, 0.1);
g4 = hslider("g691",   0, -9, 9, 0.1);
g5 = hslider("g1389",  0, -9, 9, 0.1);
g6 = hslider("g2790",  0, -9, 9, 0.1);
g7 = hslider("g5609",  0, -9, 9, 0.1);
g8 = hslider("g11272", 0, -9, 9, 0.1);

eq = fi.peak_eq(g1, 85, 60)
   : fi.peak_eq(g2, 171, 121)
   : fi.peak_eq(g3, 344, 243)
   : fi.peak_eq(g4, 691, 489)
   : fi.peak_eq(g5, 1389, 982)
   : fi.peak_eq(g6, 2790, 1973)
   : fi.peak_eq(g7, 5609, 3966)
   : fi.peak_eq(g8, 11272, 7970);

process = eq, eq;
