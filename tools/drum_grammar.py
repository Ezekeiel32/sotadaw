#!/usr/bin/env python3
"""THE DRUM GRAMMAR (PRODUCER MIND backlog wave 14; R-4/R-3/R-22 fold).

Deterministic drum-language GENERATORS — the heal assets the groove courts
reach for. Zero randomness without a seed; every number cites its study
(docs/research_producer_mind/r-{3,4,22}.json).

  drum_role(name)                 lane name -> kick|snare|clap|hat|ohat|ride|
                                  tom|crash|rim|shaker|perc|cowbell|other
  ghost_snares(notes, ...)        R-4 ghost grammar: soft taps on the e/a
                                  slots before backbeats at 0.30-0.45x
  hat_roll(...)                   R-3 trap roll: subdiv burst w/ velocity
                                  crescendo (50->110 class) into a target
  hat_pattern(genre, bars)        R-4 articulation automaton: closed/open/
                                  pedal + MONOPHONIC CHOKE (open truncated
                                  by the next hit)
  fill(genre, boundary_beat, ...) R-4 section-boundary fill: snare ladder +
                                  velocity ramp (+ crash marker on the 1)
  downbeat_delay(notes, ...)      R-3 swing's REAL lever: delay the lead's
                                  DOWNBEATS ~30ms while offbeats stay synced
  apply_slot_groove(notes, ...)   pure per-16th-slot offset+vel application
                                  (groove.py's file CLI stays the shopfront)
"""

_ROLE_WORDS = (
    ("kick", ("kick", "bd", "bassdrum", "bass_drum")),
    ("snare", ("snare", "sd", "snr")),
    ("clap", ("clap", "handclap")),
    ("rim", ("rim", "sidestick", "side_stick", "cross_stick")),
    ("ohat", ("openhat", "open_hat", "ohat", "open hh", "openhh", "oh")),
    ("hat", ("hat", "hh", "hihat", "hi_hat", "closedhat")),
    ("ride", ("ride",)),
    ("crash", ("crash", "cymbal", "splash")),
    ("tom", ("tom", "floortom")),
    ("shaker", ("shaker", "cabasa", "maraca", "egg")),
    ("cowbell", ("cowbell", "bell808", "cencerro")),
    ("perc", ("perc", "conga", "bongo", "timbale", "clave", "guiro",
              "guacharaca", "tamb", "log", "djembe", "dhol", "tabla", "cuica",
              "agogo", "woodblock", "rimshot", "snap")),
)


def drum_role(name):
    nm = str(name or "").lower().replace("-", "_")
    for role, words in _ROLE_WORDS:
        if any(w in nm for w in words):
            return role
    return "other"


def _note(start, pitch, vel, ln=0.1):
    return {"start": round(float(start), 4), "pitch": int(pitch),
            "len": round(float(ln), 4), "vel": round(float(vel), 3)}


# ------------------------------------------------------- R-4 ghost grammar
# Rule set (R-4): fill empty 'e'/'a' 16th slots with soft snare taps at
# 0.30-0.45x the backbeat velocity, prioritizing (a) 'and of 1' -> beat-2
# snare and (b) the 16th immediately BEFORE each main snare (tension->
# resolve). Density per genre family.
GHOST_DENSITY = {"funk": 0.7, "neosoul": 0.6, "dilla": 0.6, "dnb": 0.5,
                 "hiphop": 0.4, "boombap": 0.45, "soul": 0.5, "gospel": 0.5,
                 "rock": 0.25, "default": 0.35}


def ghost_snares(snare_notes, bars, beats_per_bar=4.0, genre="default",
                 pitch=None, seed=7):
    """New ghost-note dicts for a snare lane (does not mutate input).
    Deterministic: slot choice cycles on a seeded stride, not random()."""
    fam = next((k for k in GHOST_DENSITY if k != "default"
                and k in str(genre or "").lower()), "default")
    density = GHOST_DENSITY[fam]
    mains = sorted(float(n.get("start", 0)) for n in snare_notes or []
                   if float(n.get("vel", 0.8)) > 0.5)
    if not mains:
        return []
    vel_ref = max(float(n.get("vel", 0.8)) for n in snare_notes)
    taken = {round(float(n.get("start", 0)) * 4) for n in snare_notes}
    p = pitch if pitch is not None else int(snare_notes[0].get("pitch", 38))
    out = []
    k = seed
    for m in mains:
        # the 16th immediately before the main hit (tension -> resolve)
        for slot in (m - 0.25, m - 0.75 + 0.25):
            key = round(slot * 4)
            if slot < 0 or key in taken:
                continue
            k = (k * 1103515245 + 12345) & 0x7fffffff
            if (k / 0x7fffffff) > density:
                continue
            taken.add(key)
            out.append(_note(slot, p, vel_ref * (0.30 + 0.15 * ((k >> 8) % 100) / 100.0),
                             0.08))
    return out


# ------------------------------------------------------------ R-3 hat roll
def hat_roll(start, length_beats, pitch=42, start_vel=0.4, end_vel=0.9,
             subdiv=0.125, triplet=False):
    """Accelerationless roll (fixed subdiv) with a velocity crescendo —
    the single highest-leverage trap fill primitive (R-3)."""
    step = (1.0 / 12.0) * (0.5 / subdiv) if triplet else subdiv
    step = (1.0 / 6.0) if triplet and subdiv >= 0.25 else \
        (1.0 / 12.0) if triplet else subdiv
    out = []
    t = start
    n = max(int(round(length_beats / step)), 1)
    for i in range(n):
        v = start_vel + (end_vel - start_vel) * (i / max(n - 1, 1))
        out.append(_note(t, pitch, v, step * 0.8))
        t += step
    return out


def drum_roll(voice_pitch, into_beat, into_bars=2, beats_per_bar=4.0,
              start_vel=0.4, end_vel=1.0):
    """R-15 accelerating fill: subdivision LADDER [1/4,1/8,1/16,1/32] stepping
    each bar/half-bar at FIXED tempo (the illusion, no time-warp)."""
    ladder = [1.0, 0.5, 0.25, 0.125]
    total = into_bars * beats_per_bar
    seg = total / len(ladder)
    out = []
    t0 = into_beat - total
    prog = 0.0
    for step in ladder:
        t = t0
        while t < t0 + seg - 1e-9:
            frac = prog / total
            out.append(_note(t, voice_pitch,
                             start_vel + (end_vel - start_vel) * frac,
                             step * 0.8))
            t += step
            prog += step
        t0 += seg
    return out


# ------------------------------------------- R-4 hi-hat automaton + choke
HAT_TEMPLATES = {
    # slot16 -> articulation: c=closed, o=open, p=pedal, .=rest
    "house":   "c.o.c.o.c.o.c.o.",     # open on every offbeat 8th (the '+')
    "techno":  "c.o.c.o.c.o.c.o.",
    "ukg":     "c.cco.c.c.cco.c.",
    "trap":    "cccccccccccccccc",     # rolls injected separately
    "boombap": "c.c.c.c.c.c.c.c.",
    "funk":    "cccccccccccccccc",
    "reggae":  "c.c.c.c.c.c.c.c.",
    "disco":   "c.o.c.o.c.o.c.o.",
    "default": "c.c.c.c.c.c.c.c.",
}


def hat_pattern(genre, bars=1, beats_per_bar=4.0, pitch_closed=42,
                pitch_open=46, pitch_pedal=44, base_vel=0.75):
    """Articulated hat lane with the MONOPHONIC CHOKE LAW: an open hat's
    length is truncated by the NEXT hat event (R-4)."""
    g = str(genre or "").lower()
    tpl = next((v for k, v in HAT_TEMPLATES.items() if k != "default" and k in g),
               HAT_TEMPLATES["default"])
    out = []
    for bar in range(bars):
        for i, ch in enumerate(tpl):
            if ch == ".":
                continue
            t = bar * beats_per_bar + i * 0.25
            on_beat = i % 4 == 0
            vel = base_vel + (0.08 if on_beat else -0.06)
            pitch = {"c": pitch_closed, "o": pitch_open, "p": pitch_pedal}[ch]
            out.append(_note(t, pitch, vel, 0.6 if ch == "o" else 0.12))
    # choke: truncate every note at the next event's start
    out.sort(key=lambda n: n["start"])
    for a, b in zip(out, out[1:]):
        gap = b["start"] - a["start"]
        if a["len"] > gap:
            a["len"] = round(gap * 0.95, 4)
    return out


# ---------------------------------------------------- R-4 boundary fills
def fill(genre, boundary_beat, kind="half", snare_pitch=38, tom_pitch=45,
         beats_per_bar=4.0):
    """Fill INTO a boundary: snare 16th ladder with velocity ramp; 'quarter'
    (1 beat), 'half' (2 beats), 'full' (whole bar). Returns (fill_notes,
    crash_note_on_the_1)."""
    span = {"quarter": 1.0, "half": 2.0, "full": beats_per_bar}[kind]
    t0 = boundary_beat - span
    g = str(genre or "").lower()
    notes = []
    if any(k in g for k in ("trap", "drill", "phonk", "grime")):
        notes = hat_roll(t0, span, pitch=snare_pitch, start_vel=0.45,
                         end_vel=1.0, subdiv=0.125)
    else:
        t = t0
        i = 0
        n = int(span / 0.25)
        while t < boundary_beat - 1e-9:
            vel = 0.5 + 0.5 * (i / max(n - 1, 1))
            pitch = snare_pitch if i % 4 < 3 else tom_pitch
            notes.append(_note(t, pitch, vel, 0.2))
            t += 0.25
            i += 1
    crash = _note(boundary_beat, 49, 0.95, 1.5)
    return notes, crash


# -------------------------------------------- R-3 downbeat delay (the lever)
def downbeat_delay(notes, delay_beats, beats_per_bar=4.0):
    """Delay DOWNBEAT onsets only (lead/soloist lanes) — Nature 2022: swing
    is heard when the soloist's downbeats run ~30ms late while offbeats stay
    synced. Mutates; returns edit count."""
    edits = 0
    for n in notes or []:
        s = float(n.get("start", 0))
        pos = s % 1.0
        if abs(pos) < 1e-6:                          # on a quarter downbeat
            n["start"] = round(s + delay_beats, 4)
            edits += 1
    return edits


# ------------------------------------------------- pure slot-groove kernel
def apply_slot_groove(notes, off, vel, amount=1.0, beats_per_bar=4.0):
    """Per-16th-slot offset (beats) + velocity multiplier — the pure kernel
    behind groove.py's file CLI. Only notes ON the 16th grid move (off-grid
    onsets are performance intent). Mutates; returns edit count."""
    edits = 0
    for n in notes or []:
        s = float(n.get("start", 0))
        slot_f = s / 0.25
        slot = int(round(slot_f))
        if abs(slot_f - slot) > 0.08:
            continue
        idx = slot % 16
        n["start"] = round(slot * 0.25 + off[idx] * amount, 4)
        n["vel"] = round(max(min(float(n.get("vel", 0.8))
                                 * (1.0 + (vel[idx] - 1.0) * amount), 1.0),
                             0.05), 3)
        edits += 1
    return edits


if __name__ == "__main__":
    import json
    print(json.dumps({"hats_house": hat_pattern("house", 1)[:6],
                      "roll": hat_roll(14.0, 2.0)[:4]}, indent=1))
