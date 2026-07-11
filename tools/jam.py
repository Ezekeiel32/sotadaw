#!/usr/bin/env python3
"""THE JAM — the AI band that plays on VIBE by closing the loop: GENERATE a phrase
-> the EARS BUS hears it -> the band brain decides a move toward the vibe -> GENERATE
the next phrase, continuously. The synthesis of E3 (listening) + loop generation.

  jam.py <genre> <vibe> [--phrases 8] [--seed 0] [--name _jam]
  vibe: build | peak | breakdown | wave | steady   (an energy ARC the band realizes)

The loop is REAL, not scripted: the band's next move comes from what it HEARD its
last phrase actually sound like — the MID/HIGH spectral fullness of the render (the
same signal the ears bus taps live; computed here from the complete wav via FFT so
it's deterministic and load-robust). If a build came back thin, it builds harder;
the ablation proof = the SAME seed under 'build' vs 'breakdown' produces DIVERGING
arcs. The LLM never touches the audio thread — compose/listen off-thread.

Realtime: gen+render of a phrase (~2s) < its playback (~7.6s @ 126bpm) = ~3.5x headroom,
so live, the band renders phrase N+1 while phrase N plays and swaps at the bar line.
"""
import argparse
import glob
import io
import json
import math
import os
import subprocess
import sys
import contextlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")
SONGS = os.path.join(ROOT, "songs")

# THE ARRANGEMENT LADDER: foundation always holds the groove; the band adds/drops
# rungs (in this order) to raise/lower energy — the way a real band builds a jam.
FOUNDATION = ["kick", "bass"]
LADDER = ["hat", "color", "clap", "snare", "openhat", "lead", "rim", "perc", "openhi"]

# a VIBE is a target energy arc over the phrases, in [0,1] — what the band steers toward.
VIBES = {
    "build":     lambda p, n: 0.2 + 0.75 * (p / max(1, n - 1)),
    "peak":      lambda p, n: min(1.0, 0.5 + 0.9 * (p / max(1, n - 1))),
    "breakdown": lambda p, n: 0.9 - 0.7 * (p / max(1, n - 1)),
    "wave":      lambda p, n: 0.25 + 0.7 * math.sin(math.pi * p / max(1, n - 1)),
    "steady":    lambda p, n: 0.6,
}


def phrase_energy(wav, ears_jsonl=None):
    """What the band HEARD its phrase sound like -> a raw energy the genre-relative
    calibration normalizes. The signal is MID+HIGH spectral fullness (rises as the
    band fills the arrangement — rms is limiter-flat, anchored by kick+bass). Computed
    from the COMPLETE render via FFT band power: DETERMINISTIC and load-independent
    (the ears-bus realtime consumer thread gets starved under CPU contention and drops
    frames; the wav is always whole). Same signal the ears bus taps live — the ears
    bus is the LIVE organ, this is its robust offline equivalent."""
    import numpy as np
    if not os.path.exists(wav):
        return -120.0
    import wave
    w = wave.open(wav); sr = w.getframerate(); sw = w.getsampwidth()
    raw = w.readframes(w.getnframes()); ch = w.getnchannels()
    if sw == 3:
        a = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3)
        x = (a[:, 0].astype(np.int32) | (a[:, 1].astype(np.int32) << 8) | (a[:, 2].astype(np.int32) << 16))
        x = np.where(x & 0x800000, x - 0x1000000, x).astype(np.float64) / 8388608.0
    else:
        x = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0
    x = x.reshape(-1, ch).mean(axis=1)
    if len(x) < 256:
        return -120.0
    P = np.abs(np.fft.rfft(x * np.hanning(len(x)))) ** 2
    f = np.fft.rfftfreq(len(x), 1.0 / sr)
    band = lambda lo, hi: (10 * np.log10(P[(f >= lo) & (f < hi)].mean() + 1e-12)
                           if ((f >= lo) & (f < hi)).any() else -120.0)
    mid, high = band(800, 4000), band(4000, sr / 2)        # the fullness bands
    return 0.6 * high + 0.4 * mid                          # raw dB blend; norm() scales it


def wav_rms_db(p):
    import wave
    import numpy as np
    w = wave.open(p); sw = w.getsampwidth(); raw = w.readframes(w.getnframes())
    if sw == 3:
        a = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3)
        x = (a[:, 0].astype(np.int32) | (a[:, 1].astype(np.int32) << 8) | (a[:, 2].astype(np.int32) << 16))
        x = np.where(x & 0x800000, x - 0x1000000, x).astype(np.float64) / 8388608.0
    else:
        x = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0
    return 20 * math.log10(float(np.sqrt((x ** 2).mean())) + 1e-12)


def read_human(path):
    """B3 THE FOLLOW's seam (docs/THE_BAND_SEAT.md), BOTH lanes: the human's notes as a
    GROWING file any Rec tap can write. Accepts a bare JSON array of notes, a song
    dict ({tracks:[{notes:[...]}]}), or JSONL (one note object per line — the
    append-friendly shape). Beats are SET-relative (0 = the set's downbeat;
    pre-set noodling may sit at negative beats). Torn trailing writes are
    tolerated: an unparseable tail line simply waits for the next read."""
    if not path or not os.path.exists(path):
        return []
    try:
        txt = open(path).read().strip()
    except OSError:
        return []
    if not txt:
        return []
    try:
        doc = json.loads(txt)
        if isinstance(doc, list):
            return [n for n in doc if isinstance(n, dict) and "pitch" in n]
        if isinstance(doc, dict):
            if "pitch" in doc and "start" in doc:
                return [doc]
            return [n for t in doc.get("tracks", []) for n in t.get("notes", [])]
        return []
    except json.JSONDecodeError:
        pass
    notes = []                                    # JSONL: one note per line
    for ln in txt.splitlines():
        ln = ln.strip()
        if not ln:
            continue
        try:
            n = json.loads(ln)
        except json.JSONDecodeError:
            continue
        if isinstance(n, dict) and "pitch" in n and "start" in n:
            notes.append(n)
    return notes


MELODIC = ("lead", "color")   # the rungs a band member never stacks over a busy soloist


def human_context(notes, bpm=120, window_bars=4, now_beat=None):
    """B3 THE FOLLOW (docs/THE_BAND_SEAT.md): what the HUMAN is playing right now,
    as a band member hears it. notes = song-grammar [{start,len,pitch,vel}] — the
    exact material Rec lands from ANY controller (a no-name kit is just notes).
    Returns None when the human is silent in the window (solo mode: the vibe arc
    alone steers). Pure + deterministic — provable without a render."""
    if not notes:
        return None
    end = now_beat if now_beat is not None else max(
        float(n["start"]) + float(n.get("len", 0.25)) for n in notes)
    w0 = end - window_bars * 4.0
    win = [n for n in notes if w0 <= float(n["start"]) < end]
    if not win:
        return None
    # density over the span the human has actually been PLAYING inside the window
    # (first note -> now), floored at a beat: a set's OPENING bars must not read
    # sparse just because the window still reaches into the silence before them;
    # a human who STOPPED dilutes naturally as `end` walks away from their notes.
    beats = max(1.0, min(window_bars * 4.0, end - min(float(n["start"]) for n in win)))
    density = max(0.0, min(1.0, (len(win) / beats) / 4.0))   # 16ths wall-to-wall = 1.0
    vels = [float(n.get("vel", 0.8)) for n in win]
    energy = max(0.0, min(1.0, 0.65 * (sum(vels) / len(vels)) + 0.35 * density))
    from collections import Counter
    wt = Counter()
    for n in win:
        wt[int(n["pitch"]) % 12] += max(0.05, float(n.get("vel", 0.8)))
    # THE GROOVE FOLLOW: the human's timing FEEL, in the schema's own grammar
    # (swing amount = the offbeat's fractional position in its pair; 0.5 =
    # straight, ~0.62 = swung, ~0.667 = triplet). Two lanes measured — off-8ths
    # within the beat, off-16ths within the half-beat — the AUDIBLE one wins.
    # windows top out at 0.72: a straight 16th at x.75 is GRID, not swing — it
    # polluted the 8th lane and read quantized takes as feel (battery-caught)
    fr8, fr16 = [], []
    for n in win:
        f1 = float(n["start"]) % 1.0
        if 0.42 <= f1 <= 0.72:
            fr8.append(f1)
        f2 = (float(n["start"]) % 0.5) / 0.5
        if 0.42 <= f2 <= 0.72:
            fr16.append(f2)
    def _lane(fr):
        if len(fr) < 3:
            return 0.5
        fr = sorted(fr)
        return max(0.5, min(0.7, fr[len(fr) // 2]))
    a8, a16 = _lane(fr8), _lane(fr16)
    swing = ({"grid": "8th", "amount": round(a8, 3)} if abs(a8 - 0.5) >= abs(a16 - 0.5)
             else {"grid": "16th", "amount": round(a16, 3)})
    if swing["amount"] < 0.53:
        swing = {"grid": swing["grid"], "amount": 0.5}       # straight is straight
    return {"density": round(density, 3), "energy": round(energy, 3),
            "pitch_classes": sorted(pc for pc, _ in wt.most_common(7)),
            "register": sum(int(n["pitch"]) for n in win) / len(win),
            "swing": swing}


def brain(measured, target, state, hysteresis=0.08, human=None):
    """LISTEN -> DECIDE. Compare what the band HEARD to the vibe target; pick a move
    to close the gap, playing AT EASE (bounded step, hysteresis, foundation never
    drops so the groove stays alive). Returns (move, new_state).

    B3 THE FOLLOW: pass `human` (human_context()) and the band plays WITH them —
    the energy target blends toward the human's energy (state['follow'] weight,
    default 0.5), and while the human is BUSY (density > 0.7) the melodic rungs
    stay out of the way (comp, don't solo over the soloist) — the space rule is
    sticky, not oscillating: percussion rungs still carry the build."""
    active = list(state["active"])
    level = state["level"]
    if human is not None:                        # play WITH me: the target bends
        w = float(state.get("follow", 0.5))
        target = (1.0 - w) * target + w * float(human["energy"])
    busy = human is not None and float(human["density"]) > 0.7
    gap = target - measured
    move = "HOLD"
    if gap > hysteresis:                         # too quiet for the vibe -> BUILD
        nxt = next((r for r in LADDER if r in state["available"] and r not in active
                    and not (busy and r in MELODIC)), None)
        if nxt is not None:
            active.append(nxt); move = f"BUILD +{nxt}"
        elif state["bright"] < 1.0:
            state = dict(state, bright=min(1.0, state["bright"] + 0.25)); move = "BUILD brighten"
        else:
            move = "BUILD (maxed)"
        level = min(1.0, level + 0.15)
    elif gap < -hysteresis:                       # too loud -> EASE (drop the top rung)
        droppable = [r for r in reversed(LADDER) if r in active]
        if droppable:
            active.remove(droppable[0]); move = f"EASE -{droppable[0]}"
        elif state["bright"] > 0.0:
            state = dict(state, bright=max(0.0, state["bright"] - 0.25)); move = "EASE darken"
        else:
            move = "EASE (core)"
        level = max(0.0, level - 0.15)
    elif busy and any(r in active for r in MELODIC):
        drop = next(r for r in MELODIC if r in active)
        active.remove(drop); move = f"SPACE -{drop}"   # the soloist has the floor
    else:                                         # in the pocket -> EVOLVE or breathe
        move = "EVOLVE" if state["phrase"] % 2 == 0 else "HOLD"
    ns = dict(state, active=active, level=level)
    return move, ns


PERC_VARIABLE = ("hat", "perc", "rim", "openhat", "openhi", "clap", "snare")

_PC = {"c": 0, "d": 2, "e": 4, "f": 5, "g": 7, "a": 9, "b": 11}


def key_root(key):
    """Pitch class of a key string ('A minor', 'F# major', 'Bb minor') or None."""
    s = str(key or "").strip().lower()
    if not s or s[0] not in _PC:
        return None
    pc = _PC[s[0]]
    if len(s) > 1 and s[1] == "#":
        pc += 1
    elif len(s) > 1 and s[1] == "b":
        pc -= 1
    return pc % 12


def retarget_base(base, bpm=None, key=None):
    """THE ROOM'S WORLD (B6): a jam that enters over YOUR song must live at YOUR
    tempo and key. bpm just restamps (patterns are relative beats); key transposes
    the HARMONIC rungs by the nearest interval (drums sacred; unparseable keys
    leave pitches alone but never lie about the label)."""
    if bpm and float(bpm) > 0:
        base["bpm"] = float(bpm)
    if key:
        src, dst = key_root(base.get("key")), key_root(key)
        if src is not None and dst is not None and src != dst:
            delta = ((dst - src + 6) % 12) - 6
            for t in base.get("tracks", []):
                if t.get("name") in HARMONIC:
                    for n in t.get("notes", []):
                        n["pitch"] = int(n["pitch"]) + delta
        if dst is not None:
            base["key"] = str(key)
    return base

# THE HARMONIC JOURNEY: the band's harmony MOVES when it owns the room — a
# tasteful minor cycle (i i VI VI III III VII VII), each degree voiced at its
# NEAREST offset so the register never lurches. One step per 2 phrase-
# equivalents = a real band's harmonic rhythm. PRECEDENCE LAW: a human with
# pitch classes OWNS the root — callers force prog=0 under a mask; the journey
# never fights the soloist.
JOURNEY = (0, -4, 3, -2)          # minor: i VI III VII (nearest-voiced)
JOURNEY_MAJOR = (0, -5, -3, 5)    # major: I V vi IV (nearest-voiced) — ambient
                                  # etc. carry "X major" DNA keys; minor degrees
                                  # on a major field are modally wrong
HARMONIC = ("bass",) + tuple(r for r in ("lead", "color"))


def journey_offset(phrase_equiv, key=""):
    """Deterministic degree for a phrase (in DEFAULT-length equivalents);
    the table follows the DNA key's MODE (default minor)."""
    J = JOURNEY_MAJOR if "major" in str(key).lower() else JOURNEY
    return J[(int(phrase_equiv) // 2) % len(J)]


def _evolve_pattern(notes, op_idx):
    """THE EVOLVE LAW: a deterministic pocket variation on ONE percussion rung —
    a band-mate in the pocket breathes, ghosts and fills; it never photocopies
    (the generative-seed law's disease, killed here too). Same op_idx = same
    pattern, byte-exact. Ops cycle: THIN (every 4th breathes out), GHOST
    (alternates soften), FILL (a pickup into the bar line)."""
    out = [dict(n) for n in notes]
    if not out:
        return out
    op = op_idx % 3
    if op == 0:                                   # THIN
        out = [n for i, n in enumerate(out) if (i + op_idx // 3) % 4 != 3]
    elif op == 1:                                 # GHOST
        for i, n in enumerate(out):
            if i % 2 == 1:
                n["vel"] = round(max(0.05, float(n.get("vel", 0.8)) * 0.55), 3)
    else:                                         # FILL
        last = max(out, key=lambda n: float(n["start"]))
        end = float(last["start"]) + float(last.get("len", 0.25))
        fill_at = max(0.0, math.ceil(end) - 0.25)
        out.append({"start": fill_at, "len": min(0.25, float(last.get("len", 0.25))),
                    "pitch": int(last["pitch"]),
                    "vel": round(min(1.0, float(last.get("vel", 0.8)) * 0.9), 3)})
    return out


def build_phrase_song(base, active, bright, bpm, key, pc_mask=None, evolve=None,
                      swing=None, prog=0, touch=None):
    """A 4-bar song of exactly the active layers at the given brightness — what the
    band plays THIS phrase (rendered to be heard). B3 THE FOLLOW: pc_mask = the
    human's pitch classes — melodic rungs SNAP toward them (nearest step, max +-2
    semitones; farther notes keep their pitch — answer the harmony, never destroy
    the melody). Drums and foundation are never touched. evolve = THE EVOLVE LAW:
    an int varies the TOPMOST active percussion rung deterministically (pocket
    phrases breathe instead of photocopying); None = verbatim."""
    mask = sorted(set(int(p) % 12 for p in pc_mask)) if pc_mask else None
    vary = None
    if evolve is not None:
        vary = next((r for r in reversed(LADDER)
                     if r in active and r in PERC_VARIABLE), None)
    prog = 0 if mask else int(prog)   # PRECEDENCE: the human owns the root
    # THE TOUCH FOLLOW: how hard the human plays shades how hard the band plays —
    # non-foundation rungs scale toward the human's energy (0.75..1.15, clamped);
    # kick+bass stay anchored (the sub stays dominant — mix-headroom law).
    tscale = None if touch is None else 0.75 + 0.4 * max(0.0, min(1.0, float(touch)))
    tracks = []
    for t in base["tracks"]:
        if t["name"] not in active:
            continue
        tt = json.loads(json.dumps(t))
        if prog and t["name"] in HARMONIC:        # the journey moves the harmonic layers
            for n in tt.get("notes", []):
                n["pitch"] = int(n["pitch"]) + prog
        if tscale is not None and t["name"] not in FOUNDATION:
            for n in tt.get("notes", []):
                n["vel"] = round(max(0.05, min(1.0, float(n.get("vel", 0.8)) * tscale)), 3)
        if t["name"] in ("color", "lead"):        # brightness rides a filter on the tone layers
            cutoff = 400 + int(bright * 6000)
            tt.setdefault("fx", [])
            tt["fx"] = [f for f in tt["fx"] if (f.get("id") != "fx_filter")]
            tt["fx"].insert(0, {"id": "fx_filter", "params": {"cutoff": cutoff, "res": 1.0}})
            if mask:                              # voice toward the human's harmony
                for n in tt.get("notes", []):
                    pc = int(n["pitch"]) % 12
                    if pc in mask:
                        continue
                    step = next((d for d in (1, -1, 2, -2) if (pc + d) % 12 in mask), None)
                    if step is not None:
                        n["pitch"] = int(n["pitch"]) + step
        if vary is not None and t["name"] == vary:
            tt["notes"] = _evolve_pattern(tt.get("notes", []), int(evolve))
        tracks.append(tt)
    # NO master wall on the phrase probe: the limiter flattens the very loudness the
    # band listens for (the continuous song gets the wall; the probe is heard RAW).
    # BUSES RIDE (B6): the DNA's send buses come along or every phrase plays DRY —
    # tracks carry sends to 'space' etc. and m1 warned "unknown send bus" per phrase.
    s = {"version": 2, "bpm": bpm, "lengthBars": 4, "key": key, "masterGainDb": 0.0,
         "master": [], "buses": base.get("buses", []), "tracks": tracks}
    # THE GROOVE FOLLOW: the human's feel stamps the phrase (engine-native swing);
    # straight or absent leaves the song untouched (solo contract byte-intact)
    if swing and float(swing.get("amount", 0.5)) > 0.53:
        s["swing"] = {"grid": swing.get("grid", "16th"),
                      "amount": round(min(0.7, float(swing["amount"])), 3)}
    return s


def jam(genre, vibe, phrases=8, seed=0, name="_jam", ipc=None,
        human_path=None, follow=0.5, bpm=None, key=None):
    if vibe not in VIBES:
        return None, f"unknown vibe '{vibe}' (have: {', '.join(VIBES)})"
    ipc = ipc or os.path.join(SONGS, ".jam_ipc")
    os.makedirs(ipc, exist_ok=True)
    with contextlib.redirect_stdout(io.StringIO()):
        base_res = __import__("loop_gen").generate(genre, name + "_seed", bars=4, seed=seed)
    if isinstance(base_res, tuple) and base_res[0] is None:
        return None, base_res[1]
    base = json.load(open(os.path.join(SONGS, f"{name}_seed.json")))
    os.remove(os.path.join(SONGS, f"{name}_seed.json"))
    retarget_base(base, bpm=bpm, key=key)        # the room's world wins (B6)
    bpm, key = base.get("bpm", 120), base.get("key", "A minor")
    available = [t["name"] for t in base["tracks"] if t["name"] in LADDER]

    # GENRE-RELATIVE calibration: a band knows its OWN dynamic range. Probe this
    # genre's stripped (foundation) vs full+bright energy so the vibe 0..1 maps to
    # what THIS genre can actually do (melodic_techno is darker than house — same
    # scale would peg it low). Two renders up front; then measured normalizes to [lo,hi].
    def probe(active, bright):
        # THE SOUND-CHECK IS CACHED (B5 START LATENCY): identical probes (same
        # genre/seed/binary) come back in ~ms via the content-addressed cache;
        # phrase_energy reads the wav, so a hit measures identically.
        s = build_phrase_song(base, active, bright, bpm, key)
        pj, pw = os.path.join(ipc, "cal.json"), os.path.join(ipc, "cal.wav")
        json.dump(s, open(pj, "w"))
        e = os.path.join(ipc, "ears.jsonl")
        if os.path.exists(e):
            os.remove(e)
        if os.path.exists(pw):
            os.remove(pw)                 # never let a stale probe masquerade as a hit
        try:
            import render_cache as _rcc
            _rcc.render_cached(pj, pw, quiet=True)
        except Exception:
            pass
        if not os.path.exists(pw):        # cache rail unavailable/failed: the old way
            subprocess.run([M1, "render", pj, pw],
                           capture_output=True, timeout=120, env=dict(os.environ, SOTADAW_IPC=ipc))
        return phrase_energy(pw, e)
    e_lo = probe(list(FOUNDATION), 0.2)
    e_hi = probe(list(FOUNDATION) + available, 1.0)
    # THREE-POINT calibration (W13 hardening): birth EQs made the ladder's top
    # rungs spectrally HOT (lead presence shelf, hat air) while the foundation
    # stayed dark — a 2-point line no longer linearizes the ladder and the
    # steering overshoots (measured: build corr 0.90 -> 0.56). A mid probe
    # (half the ladder, mid bright) bends the map back; piecewise-linear
    # through (lo->0, mid->0.5, hi->1). Cached like the others; the sound-
    # check stays ~ms on repeat jams. NOT a threshold change — the battery
    # bar stays 0.6.
    e_mid = probe(list(FOUNDATION) + available[: max(1, len(available) // 2)], 0.6)
    span = max(1.5, e_hi - e_lo)   # dB span floor (phrase_energy is dB now)
    e_mid = min(max(e_mid, e_lo + 0.25), e_hi - 0.25)   # keep the knee inside

    def norm(raw):
        if raw <= e_mid:
            return max(0.0, 0.5 * (raw - e_lo) / max(0.5, e_mid - e_lo))
        return min(1.0, 0.5 + 0.5 * (raw - e_mid) / max(0.5, e_hi - e_mid))

    # continuous song: every role is one track; phrases append notes at their bar offset
    cont = {"version": 2, "bpm": bpm, "key": key, "lengthBars": phrases * 4,
            "masterGainDb": 0.0, "master": [{"id": "fx_truepeak", "params": {"ceiling": -1.2}}],
            "buses": base.get("buses", []), "sections": [], "tracks": []}
    trackmap = {t["name"]: {"name": t["name"], "source": t["source"],
                            "gainDb": t.get("gainDb", -6), "notes": [],
                            "fx": t.get("fx", []), "automation": []}
                for t in base["tracks"]}

    # the band OPENS where the vibe wants it: a build starts sparse (foundation), a
    # breakdown starts near-full. Initial rungs = the vibe's first target.
    t0 = VIBES[vibe](0, phrases)
    n0 = int(round(t0 * len(available)))
    state = {"active": list(FOUNDATION) + available[:n0], "available": available,
             "level": t0, "bright": 0.3 + 0.5 * t0, "phrase": 0, "follow": follow}
    log, arc = [], []
    smoothed = None                              # the band perceives DEVELOPING energy,
    smooth_a = 0.5                               # not per-bar jitter — EMA = playing "at ease"
    ev_prev = None                               # EVOLVE decided last phrase varies THIS one
    human = None
    for p in range(phrases):
        state["phrase"] = p
        target = VIBES[vibe](p, phrases)
        # THE FOLLOW, offline lane: a static human take (Rec/import/audio_follow
        # output) — the window slides phrase-aligned, so the band composes AROUND
        # the riff's arc: space where it solos, its harmony/feel where it plays.
        if human_path:
            human = human_context(read_human(human_path), now_beat=(p + 1) * 16.0)
        # play THIS phrase = the active layers, rendered so the band can hear it
        ph_song = build_phrase_song(base, state["active"], state["bright"], bpm, key,
                                    pc_mask=human["pitch_classes"] if human else None,
                                    swing=human["swing"] if human else None,
                                    touch=human["energy"] if human else None,
                                    evolve=ev_prev, prog=journey_offset(p, key))
        pj = os.path.join(ipc, "phrase.json"); pw = os.path.join(ipc, "phrase.wav")
        json.dump(ph_song, open(pj, "w"))
        ears = os.path.join(ipc, "ears.jsonl")
        if os.path.exists(ears):
            os.remove(ears)
        subprocess.run([M1, "render", pj, pw], capture_output=True, timeout=120,
                       env=dict(os.environ, SOTADAW_IPC=ipc))
        raw = norm(phrase_energy(pw, ears))          # normalized to THIS genre's range
        smoothed = raw if smoothed is None else smooth_a * smoothed + (1 - smooth_a) * raw
        measured = smoothed                          # what the band perceives (calm)
        arc.append(round(measured, 3))
        # place the active layers into the continuous song at this phrase's bar offset
        off = p * 4 * 4.0                       # beats
        for t in ph_song["tracks"]:
            tm = trackmap[t["name"]]
            for n in t.get("notes", []):
                m = dict(n); m["start"] = n["start"] + off
                tm["notes"].append(m)
            if t.get("fx") and not tm["fx"]:
                tm["fx"] = t["fx"]
        cont["sections"].append({"name": f"{vibe} {p+1} (e{measured:.2f}/t{target:.2f})",
                                 "startBar": p * 4})
        # LISTEN -> DECIDE the next move
        move, state = brain(measured, target, state, human=human)
        ev_prev = p + 1 if move == "EVOLVE" else None
        log.append({"phrase": p, "target": round(target, 2), "measured": round(measured, 2),
                    "move": move, "active": list(ph_song and state["active"])})

    cont["tracks"] = [tm for tm in trackmap.values() if tm["notes"]]
    out = os.path.join(SONGS, f"{name}.json")
    json.dump(cont, open(out, "w"), indent=1)
    return {"song": out, "log": log, "arc": arc, "bpm": bpm, "key": key,
            "vibe": vibe, "genre": genre}, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("genre")
    ap.add_argument("vibe", choices=list(VIBES))
    ap.add_argument("--phrases", type=int, default=8)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--name", default="_jam")
    a = ap.parse_args()
    res, err = jam(a.genre, a.vibe, a.phrases, a.seed, a.name)
    if res is None:
        sys.exit(f"jam failed: {err}")
    print(f"[jam] {a.genre} on '{a.vibe}' — {a.phrases} phrases @ {res['bpm']}bpm {res['key']}")
    for e in res["log"]:
        bar = "#" * int(e["measured"] * 30)
        print(f"  ph{e['phrase']:2d} heard {e['measured']:.2f} vs vibe {e['target']:.2f}  "
              f"{bar:<30} -> {e['move']}")
    print(f"[jam] -> {res['song']} ({len(res['arc'])} phrases, one continuous take)")


if __name__ == "__main__":
    main()
