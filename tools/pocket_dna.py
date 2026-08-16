#!/usr/bin/env python3
"""THE POCKET DNA (PRODUCER MIND P13; R-3 research fold, 2026-07-14).

Corpus-MEASURED feel numbers as a deterministic kernel — the formulas behind
groove.py's slot profiles. Every constant carries its study; the vocal is
docs/research_producer_mind/r-3.json (32-agent wave, cited).

  swing_ratio_jazz(bpm)      ride long:short vs tempo (3.5:1 slow -> 1:1 fast)
  mpc_offset_beats(pct)      MPC swing % -> off-16th delay in BEATS (tempo-free)
  role_timing_beats(genre, role, bpm)   measured push/drag per instrument
  ghost_vel(), backbeat_vel(), accent_vel()   the velocity grammar (0..1 house vel)
  humanize_sd_beats(genre, bpm)         the NATURAL random SD — and the LAW:
                                        tasteful jitter = 40-60% of it; more
                                        LOWERS groove (measured optimum).
"""


def clamp(lo, hi, x):
    return max(lo, min(hi, x))


# the study's cited measurements (the r-3 agent's own linear fit contradicted
# these points — 3.05 vs the cited 2.38 @ 132; the POINTS are the law):
_JAZZ_RATIO_PTS = ((100.0, 3.5), (132.0, 2.38), (150.0, 2.0),
                   (200.0, 1.5), (290.0, 1.0))


def swing_ratio_jazz(bpm):
    """Ride-cymbal long:short vs tempo, interpolated through the corpus's
    MEASURED points (~3.5:1 slow, 2.38:1 @132, 2:1 @150, 1:1 by ~290)."""
    b = float(bpm)
    pts = _JAZZ_RATIO_PTS
    if b <= pts[0][0]:
        return pts[0][1]
    if b >= pts[-1][0]:
        return pts[-1][1]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= b <= x1:
            return round(y0 + (y1 - y0) * (b - x0) / (x1 - x0), 3)
    return 1.0


def swing_ratio_to_pct(ratio):
    """long:short ratio -> MPC swing % (50 = straight, 66.7 = 2:1 triplet)."""
    r = max(float(ratio), 1.0)
    return 100.0 * r / (r + 1.0)


def mpc_offset_beats(pct):
    """MPC swing % -> delay of the OFF-16th in beats (tempo-free: the % IS
    a fraction of the 8th pair). 58% @ 120bpm = +20ms = 0.04 beats."""
    return (clamp(50.0, 75.0, float(pct)) - 50.0) / 100.0 * 0.5


def ms_to_beats(ms, bpm):
    return float(ms) * float(bpm) / 60000.0


# Per-genre-family, per-role MEASURED timing (ms; negative = AHEAD of grid).
# jazz @~150bpm ratio 2.66 medians; funk @100 (kick ON TOP is the sound);
# dilla/neo-soul: hats STRAIGHT, kick/snare off-grid, bass anticipates.
ROLE_TIMING_MS = {
    "jazz":   {"ride": -14.0, "bass": -17.5, "hat_foot": -33.0, "snare": 0.0,
               "lead_downbeat": +32.0},   # the real swing lever: delayed lead
    "funk":   {"kick": -12.5, "hat": -3.0, "snare": -4.0, "bass": -3.0},
    "dilla":  {"hat": 0.0, "kick": -20.0, "snare": +45.0, "bass": -95.0},
    "neosoul": {"hat": 0.0, "kick": +10.0, "snare": +55.0, "bass": -60.0},
    "reggae": {"kick": +10.0, "snare": +10.0, "skank": +8.0, "bass": +12.0},
    "afrobeat": {"kick": +8.0, "snare": +10.0, "bell": -6.0, "bass": 0.0},
}


def role_timing_beats(family, role, bpm):
    fam = ROLE_TIMING_MS.get(str(family or "").lower(), {})
    return ms_to_beats(fam.get(str(role or "").lower(), 0.0), bpm)


# Velocity grammar (R-3; MIDI 0-127 -> house 0..1 floats):
# snare ghosts 20-45, backbeat 100-110, accents 120+, kick 90-115,
# hats on-beat > off-beat by 5-10 for subtle groove.
def ghost_vel(seed_frac=0.5):
    return round((20 + 25 * clamp(0.0, 1.0, seed_frac)) / 127.0, 3)


def backbeat_vel(hot=False):
    return round((110 if hot else 102) / 127.0, 3)


def accent_vel():
    return round(121 / 127.0, 3)


def hat_spread(subtle=True):
    """On-beat minus off-beat velocity delta (0..1 scale)."""
    return round((7 if subtle else 14) / 127.0, 3)


# Natural human random SD (measured): swing ~27ms, funk ~16ms. THE CEILING
# LAW: tasteful humanize = 40-60% of natural SD; exaggerated microtiming
# LOWERS groove ratings; grid-quantized rates as high as natural.
NATURAL_SD_MS = {"jazz": 27.0, "swing": 27.0, "funk": 16.0, "default": 20.0}


def humanize_sd_beats(genre, bpm, scale=0.5):
    g = str(genre or "").lower()
    ms = next((v for k, v in NATURAL_SD_MS.items() if k in g),
              NATURAL_SD_MS["default"])
    return ms_to_beats(ms * clamp(0.4, 0.6, scale), bpm)


# Samba 16th DURATION pattern (23 / 23.6 / 22.8 / 30.7 % of the beat; grid =
# 25 each): onsets land at cumulative sums -> 3rd & 4th 16ths AHEAD.
SAMBA_16TH_ONSETS = (0.0, 0.230, 0.466, 0.694)     # fractions of one beat


def samba_offsets_beats():
    grid = (0.0, 0.25, 0.50, 0.75)
    return tuple(round(o - g, 4) for o, g in zip(SAMBA_16TH_ONSETS, grid))


# West-African jembe ternary ratios (short:medium:long per beat):
JEMBE_TERNARY = {"manjanin": (0.27, 0.33, 0.40), "suku": (0.22, 0.34, 0.44)}


def jembe_onsets_beats(pattern="manjanin"):
    s, m, _l = JEMBE_TERNARY.get(pattern, JEMBE_TERNARY["manjanin"])
    return (0.0, round(s, 4), round(s + m, 4))    # 3 onsets inside one beat


if __name__ == "__main__":
    import json
    print(json.dumps({
        "jazz_ratio@100": swing_ratio_jazz(100), "jazz_ratio@150": swing_ratio_jazz(150),
        "jazz_ratio@280": swing_ratio_jazz(280),
        "mpc58_beats": mpc_offset_beats(58),
        "dilla_snare@92": role_timing_beats("dilla", "snare", 92),
        "samba_offsets": samba_offsets_beats(),
        "humanize@120_funk": humanize_sd_beats("funk", 120),
    }, indent=1))
