#!/usr/bin/env python3
"""MIDI POLISH — the kernel that turns raw transcription soup into a USABLE sketch.

basic-pitch (and every AMT model) emits: octave/harmonic ghosts, fragmented
sustains, flam doubles, polyphonic overlaps on monophonic sources, off-grid
starts, salience-flat velocities, and register chirps. Producers call the result
"needs much work". This kernel is that work, role-aware and deterministic:

  polish(notes, role, bpm, key)   role in {"bass","vocal","melodic","poly"}
      flams -> harmonic ghosts -> fragment merge -> monophony (bass/vocal) ->
      register fold -> weak off-key prune -> grid snap (tolerant: swing and
      triplets survive) -> velocity spread -> cap BY SALIENCE (never truncate
      the song's tail) -> exact-dup collapse

  drum_sketch(wav_path, bpm)      the drums stem was never transcribed at all.
      3-band onset lanes (low->kick 36, mid->snare 38, high->hat 42, GM map),
      kick-bleed gating on the snare lane, hard 1/16 snap (drums ARE the grid),
      strengths -> velocities. One muted gm_drums track = editable drum MIDI.

Notes are song.json dicts {start,len,pitch,vel} in BEATS. Pure python (numpy
only inside drum_sketch). Battery: tools/midi_polish_battery.py (+ --real).
"""

NOTE_PC = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5,
           "F#": 6, "Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11}

ROLE_RANGE = {"bass": (26, 55), "vocal": (40, 86), "melodic": (24, 96), "poly": (21, 108)}

def _key_pcs(key):
    if not key or " " not in str(key):
        return None
    note, mode = str(key).rsplit(" ", 1)
    root = NOTE_PC.get(note.strip())
    if root is None:
        return None
    iv = [0, 2, 3, 5, 7, 8, 10] if mode.strip().lower().startswith("min") else [0, 2, 4, 5, 7, 9, 11]
    return {(root + i) % 12 for i in iv}

def _srt(ns):
    ns.sort(key=lambda n: (n["start"], n["pitch"]))
    return ns

def kill_flams(ns, win=0.08):
    """Two same-pitch onsets within `win` beats = one machine-gunned note."""
    out = []
    for n in _srt(list(ns)):
        if out:
            p = out[-1]
            if p["pitch"] == n["pitch"] and n["start"] - p["start"] < win:
                end = max(p["start"] + p["len"], n["start"] + n["len"])
                p["len"] = end - p["start"]
                p["vel"] = max(p["vel"], n["vel"])
                continue
        out.append(dict(n))
    return out

def dedupe_harmonics(ns, win=0.06, ratio=0.75):
    """The classic AMT ghost: the note + its octave/12th/double-octave born at the
    same instant, weaker, living inside the real note's span. Drop the ghost."""
    ns = _srt([dict(n) for n in ns])
    dead = set()
    for i, a in enumerate(ns):
        if i in dead:
            continue
        for j in range(i + 1, len(ns)):
            b = ns[j]
            if b["start"] - a["start"] > win:
                break
            if j in dead or abs(a["pitch"] - b["pitch"]) not in (12, 19, 24):
                continue
            hi, lo = (a, b) if a["vel"] >= b["vel"] else (b, a)
            k = j if lo is ns[j] else i
            if (lo["vel"] < ratio * hi["vel"]
                    and lo["start"] + lo["len"] <= hi["start"] + hi["len"] + 0.1):
                dead.add(k)
    return [n for i, n in enumerate(ns) if i not in dead]

def merge_fragments(ns, gap=0.15):
    """Vibrato/tremolo shatters one held note into shards with micro-gaps."""
    by_pitch = {}
    for n in _srt([dict(n) for n in ns]):
        by_pitch.setdefault(n["pitch"], []).append(n)
    out = []
    for _, seq in by_pitch.items():
        cur = seq[0]
        for n in seq[1:]:
            g = n["start"] - (cur["start"] + cur["len"])
            if -1e-9 <= g <= gap:
                cur["len"] = n["start"] + n["len"] - cur["start"]
                cur["vel"] = max(cur["vel"], n["vel"])
            else:
                out.append(cur)
                cur = n
        out.append(cur)
    return _srt(out)

def enforce_mono(ns, min_len=0.1):
    """Bass and lead vocals are ONE voice: no chords, no self-overlap."""
    ns = _srt([dict(n) for n in ns])
    out = []
    for n in ns:
        if not out:
            out.append(n)
            continue
        c = out[-1]
        if n["start"] >= c["start"] + c["len"] - 1e-9:
            out.append(n)
            continue
        if n["pitch"] == c["pitch"]:              # same pitch overlap: extend
            c["len"] = max(c["len"], n["start"] + n["len"] - c["start"])
            c["vel"] = max(c["vel"], n["vel"])
            continue
        inside = n["start"] + n["len"] <= c["start"] + c["len"] + 0.05
        if inside and n["vel"] <= c["vel"] * 1.15:
            continue                              # a weaker note living inside -> ghost
        c["len"] = n["start"] - c["start"]        # real change: hand over the voice
        if c["len"] < min_len:
            out.pop()
        out.append(n)
    return out

def fold_range(ns, role):
    """Register chirps (harmonics heard as notes): weak strays die, strong strays
    fold by octaves into the role's honest range."""
    lo, hi = ROLE_RANGE.get(role, ROLE_RANGE["poly"])
    out = []
    for n in ns:
        n = dict(n)
        if n["pitch"] < lo or n["pitch"] > hi:
            if n["vel"] < 0.5:
                continue
            while n["pitch"] < lo:
                n["pitch"] += 12
            while n["pitch"] > hi:
                n["pitch"] -= 12
        out.append(n)
    return out

def prune_offkey(ns, key):
    """CONSERVATIVE: only kill a note that is weak AND short AND chromatic AND
    shadowed by a stronger in-key neighbor — transcription noise, never blue notes."""
    pcs = _key_pcs(key)
    if not pcs:
        return list(ns)
    ns = _srt([dict(n) for n in ns])
    out = []
    for i, n in enumerate(ns):
        if (n["pitch"] % 12) not in pcs and n["vel"] < 0.3 and n["len"] < 0.25:
            shadowed = any((m["pitch"] % 12) in pcs and m["vel"] > n["vel"]
                           and abs(m["start"] - n["start"]) < 0.5
                           for m in ns[max(0, i - 4):i + 5] if m is not n)
            if shadowed:
                continue
        out.append(n)
    return out

def quantize(ns, grid=0.25, tol=0.07):
    """Snap starts within `tol` beats of the grid. tol=0.07 catches transcription
    jitter (~35ms @120) but is BELOW the triplet offset (1/12=0.083) — swing and
    triplets keep their positions (tolerant, not tyrannical)."""
    out = []
    for n in ns:
        n = dict(n)
        q = round(n["start"] / grid) * grid
        if abs(n["start"] - q) <= tol:
            n["start"] = q
        n["len"] = max(0.06, round(n["len"] * 32) / 32.0)
        out.append(n)
    return _srt(out)

def spread_velocity(ns, lo=0.35, hi=1.0):
    """Salience is not dynamics: percentile-map so the sketch breathes."""
    if len(ns) < 4:
        return [dict(n) for n in ns]
    vs = sorted(n["vel"] for n in ns)
    p10 = vs[int(0.10 * (len(vs) - 1))]
    p95 = vs[int(0.95 * (len(vs) - 1))]
    if p95 - p10 < 1e-6:
        return [dict(n) for n in ns]
    out = []
    for n in ns:
        n = dict(n)
        t = (n["vel"] - p10) / (p95 - p10)
        n["vel"] = min(1.0, max(lo, lo + t * (hi - lo)))
        out.append(n)
    return out

def cap_by_salience(ns, max_notes=400):
    """The old cap sorted by START and truncated — the song's tail silently
    vanished. Keep the STRONGEST notes from the whole timeline instead."""
    if len(ns) <= max_notes:
        return list(ns)
    keep = sorted(ns, key=lambda n: -n["vel"])[:max_notes]
    return _srt(keep)

def collapse_dups(ns):
    best = {}
    for n in ns:
        k = (round(n["start"], 4), n["pitch"])
        if k not in best or n["vel"] > best[k]["vel"]:
            best[k] = n
    return _srt(list(best.values()))

def polish(notes, role="melodic", bpm=120.0, key=None, max_notes=400,
           grid=0.25, tol=0.07):
    ns = [dict(n) for n in notes]
    ns = kill_flams(ns)
    ns = dedupe_harmonics(ns)
    ns = merge_fragments(ns)
    if role in ("bass", "vocal"):
        ns = enforce_mono(ns)
    ns = fold_range(ns, role)
    ns = prune_offkey(ns, key)
    ns = quantize(ns, grid=grid, tol=tol)
    if role in ("bass", "vocal"):
        ns = enforce_mono(ns)                 # snapping can re-create tiny overlaps
    ns = collapse_dups(ns)
    ns = spread_velocity(ns)
    ns = cap_by_salience(ns, max_notes)
    for n in ns:
        n["start"] = round(n["start"], 4)
        n["len"] = round(n["len"], 4)
        n["vel"] = round(n["vel"], 3)
    return ns


def editable(notes, bpm=120.0, max_per_bar=12, beats_per_bar=4.0):
    """THE EDITABLE PASS (Chezy live directive 2026-07-09: 'the instrument MIDI
    notes are so complex that its impossible to edit'). The harmonic microscope
    maximizes coverage (~14 notes/bar); this organizes its output into a roll a
    human can WORK without rewriting the music:
      1. dust OFF — weak specks (short AND quiet) are transcription noise
      2. CHORD BLOCKS — near-simultaneous onsets share ONE start, and members
         whose lengths roughly agree share ONE length (a chord reads as a
         block, not a smear)
      3. re-articulation merge — same-pitch stutters within a grace gap fuse
      4. per-BAR salience cap — no bar is a wall; the strongest notes of THAT
         bar survive (a global cap starves quiet sections instead)
    Deliberately does NOT hard-quantize: the record's feel is the groove."""
    ns = _srt([dict(n) for n in notes])
    ns = [n for n in ns if not (n["len"] < 0.09 and n["vel"] < 0.30)]
    i = 0
    while i < len(ns):                          # chord blocks
        j = i + 1
        while j < len(ns) and ns[j]["start"] - ns[i]["start"] <= 0.08:
            j += 1
        grp = ns[i:j]
        if len(grp) > 1:
            s = sorted(g["start"] for g in grp)[len(grp) // 2]
            ls = sorted(g["len"] for g in grp)
            lm = ls[len(ls) // 2]
            for g in grp:
                g["start"] = s
                if lm > 0 and abs(g["len"] - lm) <= 0.25 * lm:
                    g["len"] = lm
        i = j
    ns = merge_fragments(_srt(ns), gap=0.12)
    by_bar = {}
    for n in ns:
        by_bar.setdefault(int(n["start"] // beats_per_bar), []).append(n)
    out = []
    for b in sorted(by_bar):
        row = by_bar[b]
        if len(row) > max_per_bar:
            row = sorted(row, key=lambda n: -(n["vel"] * (n["len"] ** 0.5)))[:max_per_bar]
        out.extend(row)
    ns = _srt(out)
    for n in ns:
        n["start"] = round(n["start"], 4)
        n["len"] = round(n["len"], 4)
        n["vel"] = round(n["vel"], 3)
    return ns


def _chord_pcs(label):
    """'D#m7' -> {root, third, fifth(, b7)} pitch classes; None if unparseable."""
    import re as _re
    m = _re.match(r"^([A-G]#?)(m?)(7?)$", str(label or ""))
    if not m or m.group(1) not in NOTE_PC:
        return None
    root = NOTE_PC[m.group(1)]
    pcs = {root, (root + (3 if m.group(2) else 4)) % 12, (root + 7) % 12}
    if m.group(3):
        pcs.add((root + 10) % 12)
    return pcs

def chord_snap(ns, chords, key=None, beats_per_bar=4.0, weak=0.45, conf_min=0.5):
    """CHORD PRIOR for polyphonic sketches (round 2 of song-to-MIDI): the voted
    chord lane judges the transcription's weak guesses. A note that is weak AND
    short AND non-chord AND non-scale snaps to the nearest chord tone (<=2
    semitones; triads guarantee one) or, defensively, dies. Strong notes and
    diatonic passing tones are MUSIC - untouched. The chord at note START rules.
    Idempotent (snapped notes become chord tones) and deterministic."""
    by_bar = {int(c["bar"]): c for c in (chords or []) if float(c.get("conf", 0)) >= conf_min}
    scale = _key_pcs(key)
    out = []
    for n in ns:
        bar = int(float(n["start"]) // beats_per_bar) + 1
        c = by_bar.get(bar)
        if c is None or n["vel"] >= weak or n["len"] >= 0.5:
            out.append(dict(n))
            continue
        pcs = _chord_pcs(c.get("chord"))
        pc = n["pitch"] % 12
        if pcs and pc not in pcs and not (scale and pc in scale):
            snapped = None
            for d in (1, -1, 2, -2):
                if (pc + d) % 12 in pcs:
                    snapped = n["pitch"] + d
                    break
            if snapped is None:
                continue
            n = dict(n, pitch=snapped)
        out.append(dict(n))
    return _srt(out)

def chord_consistency(ns, chords, key=None, beats_per_bar=4.0, weak=0.45):
    """Share of WEAK notes whose pc lands in chord-union-scale at their bar (the
    chord-prior metric; 1.0 when no weak notes face a voted bar)."""
    by_bar = {int(c["bar"]): c for c in (chords or [])}
    scale = _key_pcs(key) or set()
    tot = good = 0
    for n in ns:
        if n["vel"] >= weak:
            continue
        c = by_bar.get(int(float(n["start"]) // beats_per_bar) + 1)
        pcs = _chord_pcs(c.get("chord")) if c else None
        if not pcs:
            continue
        tot += 1
        good += 1 if (n["pitch"] % 12) in (pcs | scale) else 0
    return (good / tot) if tot else 1.0


def bass_prior(ns, chords, key=None, beats_per_bar=4.0, weak=0.45, conf_min=0.5):
    """BASS grammar prior (chord prior 2b): a bass line is roots and fifths first.
    Weak non-chord/non-scale bass notes snap to the nearest of {root, fifth}
    (always within 3 semitones); weak notes further than a major 6th from the
    line's median fold by octaves toward it (octave-error repair). Strong notes
    — real fills, walks, octave jumps — untouched. Idempotent, deterministic."""
    by_bar = {int(c["bar"]): c for c in (chords or []) if float(c.get("conf", 0)) >= conf_min}
    scale = _key_pcs(key)
    pitches = sorted(n["pitch"] for n in ns)
    med = pitches[len(pitches) // 2] if pitches else 33
    out = []
    for n in ns:
        n = dict(n)
        # ORDER LAW: snap FIRST (pitch-class move), fold SECOND (octave move
        # preserves the pc) — both reach fixed points, so the pass is idempotent
        # (fold-then-snap could land on dist>=10 and refold forever).
        c = by_bar.get(int(float(n["start"]) // beats_per_bar) + 1)
        if c is not None and n["vel"] < weak:
            pcs = _chord_pcs(c.get("chord"))
            pc = n["pitch"] % 12
            if pcs and pc not in pcs and not (scale and pc in scale):
                m2 = __import__("re").match(r"^([A-G]#?)", str(c.get("chord", "")))
                root = NOTE_PC.get(m2.group(1)) if m2 else None
                if root is not None:
                    targets = {root % 12, (root + 7) % 12}
                    best, bestd = None, 99
                    for d in range(-3, 4):
                        if (pc + d) % 12 in targets and abs(d) < bestd:
                            best, bestd = n["pitch"] + d, abs(d)
                    if best is not None:
                        n["pitch"] = best
        if n["vel"] < weak and abs(n["pitch"] - med) >= 10:
            folded = n["pitch"]
            while folded - med >= 10:
                folded -= 12
            while med - folded >= 10:
                folded += 12
            lo, hi = ROLE_RANGE["bass"]
            if lo <= folded <= hi:
                n["pitch"] = folded
        out.append(n)
    return _srt(out)

# ---------------------------------------------------------------- drums
def _onsets(env, fps, min_gap_s):
    """Adaptive peak-pick on a positive onset envelope: median + 2.5*MAD floor."""
    import numpy as np
    d = np.maximum(0.0, np.diff(env, prepend=env[:1]))
    med = float(np.median(d))
    mad = float(np.median(np.abs(d - med))) + 1e-12
    thr = med + 2.5 * mad
    picks, last = [], -1e9
    for i in range(1, len(d) - 1):
        if d[i] >= thr and d[i] >= d[i - 1] and d[i] >= d[i + 1]:
            t = i / fps
            if t - last >= min_gap_s:
                picks.append((t, float(d[i])))
                last = t
    return picks

def drum_sketch(wav_path, bpm, grid=0.25, max_notes=600):
    """drums stem -> GM drum MIDI: low band = kick 36, mid = snare 38, high = hat 42.
    Hard 1/16 snap (drums ARE the grid), kick-bleed gating on the snare lane."""
    import numpy as np
    from scipy.io import wavfile
    from scipy.signal import butter, sosfilt
    sr, x = wavfile.read(wav_path)
    if x.dtype.kind == "i":
        x = x.astype(np.float64) / np.iinfo(x.dtype).max
    elif x.dtype.kind == "f":
        x = x.astype(np.float64)
    if x.ndim > 1:
        x = x.mean(axis=1)
    peak = float(np.max(np.abs(x)) or 1.0)
    x = x / peak
    hop = 256
    n = (len(x) // hop) * hop
    if n < hop * 32:
        return []
    fps = sr / hop
    spb = 60.0 / bpm

    def env_of(sig):
        fr = sig[:n].reshape(-1, hop)
        return np.sqrt((fr ** 2).mean(axis=1))

    bands = {
        36: sosfilt(butter(4, 150.0 / (sr / 2), "low", output="sos"), x),
        38: sosfilt(butter(4, [500.0 / (sr / 2), min(4000.0, sr / 2 - 1) / (sr / 2)],
                           "band", output="sos"), x),
        42: sosfilt(butter(4, min(6000.0, sr / 2 - 1) / (sr / 2), "high", output="sos"), x),
    }
    lane_picks = {p: _onsets(env_of(sig), fps, min_gap_s=0.10 * spb)
                  for p, sig in bands.items()}
    # kick bleed: a snare "onset" landing on a kick with no real mid dominance is bleed
    kick_ts = [t for t, _ in lane_picks[36]]
    kick_str = {t: s for t, s in lane_picks[36]}
    gated = []
    for t, s in lane_picks[38]:
        near = [kt for kt in kick_ts if abs(kt - t) < 0.05 * spb]
        if near and s < 1.2 * max(kick_str[kt] for kt in near):
            continue
        gated.append((t, s))
    lane_picks[38] = gated

    LEN = {36: 0.22, 38: 0.2, 42: 0.1}
    notes = []
    for pitch, picks in lane_picks.items():
        if not picks:
            continue
        strengths = sorted(s for _, s in picks)
        s10 = strengths[int(0.10 * (len(strengths) - 1))]
        s95 = strengths[int(0.95 * (len(strengths) - 1))]
        rng = max(1e-12, s95 - s10)
        for t, s in picks:
            beat = round((t / spb) / grid) * grid       # drums: hard snap
            v = 0.4 + 0.6 * min(1.0, max(0.0, (s - s10) / rng))
            notes.append({"start": round(beat, 4), "len": LEN[pitch],
                          "pitch": pitch, "vel": round(v, 3)})
    notes = collapse_dups(notes)
    return cap_by_salience(notes, max_notes)
