#!/usr/bin/env python3
"""CONTEXT-TUNE (the tune rail) — song-aware vocal pitch correction. SPEC V45.

Classic autotune knows ONE static scale. This knows the ARRANGEMENT: it reads song.json,
builds a per-half-beat harmonic field from every other track's actual notes (bass-weighted),
maps the vocal into musical time through its audioClip (startBeat/offsetSec/sourceBpm warp
+ tempoMap), segments the performance into note events, and picks each event's target pitch
by Viterbi over chord-tone/scale/contour scores — then resynthesizes through the WORLD
vocoder (harvest F0 -> cheaptrick envelope -> d4c aperiodicity -> synthesize with the
corrected F0 curve). Spectral envelope untouched = formants preserved = T-Pain, not chipmunk.
Timing untouched = sample-sync safe for clip swaps.

Styles: tpain (retune 3ms hard quantize; the yodel stairs come from the segmenter) ·
hard · natural (drift corrected, vibrato kept) · transparent (never changes note identity
unless harmony demands it; keeps blue notes). Correction curve per frame:
  dev = sung_cents - target; slow/fast split (median filter ~150ms);
  out = (1-amount)*slow + vibrato_keep*fast + humanize_walk; exp glide-in tau=retune_ms.

Everything is inspectable: a JSON report lists every note event — sung, target, cents
moved, and WHY (chord(G) / scale(C major) / guide(lead) / nearest). No song context ->
degrades to key-scale mode (--key) = classic autotune as the floor, never the ceiling.

CLI:
  retune.py in.wav out.wav --song songs/x.json --track vocals --style tpain
  retune.py in.wav out.wav --key "F minor" --style natural       # no-song floor
  retune.py --selftest                                           # synthesized proof
Flags: --strength 0..1 · --retune-ms · --vibrato-keep · --humanize-cents · --guide-track
       --region B0 B1 (beats w/ --song, else seconds) · --report path.json · --clip-index
"""
import argparse, json, math, os, re, sys

import numpy as np

try:
    import soundfile as sf
except ImportError:
    sys.exit("retune: needs soundfile (pip install soundfile)")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRAME_MS = 5.0
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

STYLES = {
    "tpain":       dict(amount=1.0,  retune_ms=3.0,   vibrato_keep=0.15, humanize=0.0,
                        split_cents=55.0, min_note_ms=35.0,
                        w_prox=0.7, w_chord=1.6, w_scale=0.9, w_bass=0.3, w_out=2.5, w_contour=0.6),
    "hard":        dict(amount=1.0,  retune_ms=12.0,  vibrato_keep=0.35, humanize=1.0,
                        split_cents=60.0, min_note_ms=45.0,
                        w_prox=0.8, w_chord=1.4, w_scale=0.9, w_bass=0.25, w_out=2.2, w_contour=0.7),
    "natural":     dict(amount=0.85, retune_ms=90.0,  vibrato_keep=0.9,  humanize=2.5,
                        split_cents=70.0, min_note_ms=60.0,
                        w_prox=1.2, w_chord=0.9, w_scale=0.8, w_bass=0.2, w_out=1.5, w_contour=0.8),
    "transparent": dict(amount=0.6,  retune_ms=150.0, vibrato_keep=1.0,  humanize=2.0,
                        split_cents=80.0, min_note_ms=80.0,
                        w_prox=3.0, w_chord=0.3, w_scale=0.6, w_bass=0.1, w_out=1.0, w_contour=1.0),
}

DRUM_RX = re.compile(r"kick|snare|clap|hat\b|hats|hihat|perc|ride|crash|shak|cym|tom", re.I)

# Krumhansl-Kessler key profiles (major/minor), for symbolic scale fit
KK_MAJ = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
KK_MIN = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
SCALE_PCS = {"major": [0, 2, 4, 5, 7, 9, 11], "minor": [0, 2, 3, 5, 7, 8, 10]}


def midi_name(m):
    mi = int(round(m))
    return f"{NOTE_NAMES[mi % 12]}{mi // 12 - 1}"


def hz_of(m):
    return 440.0 * 2.0 ** ((m - 69.0) / 12.0)


def midi_of(hz):
    return 69.0 + 12.0 * np.log2(np.maximum(hz, 1e-9) / 440.0)


# ---------------------------------------------------------------- song context
def beat_maps(song):
    """beat<->seconds from bpm + tempoMap (bar 1-based, 4/4; curve!=0 hold-then-step,
    curve 0 linear ramp approximated in 16 substeps). Returns (beat_to_sec, sec_to_beat)."""
    base = float(song.get("bpm", 120.0))
    tm = sorted(song.get("tempoMap") or [], key=lambda p: p.get("bar", 1))
    total_beats = max(64.0, 4.0 * float(song.get("lengthBars", 16))) + 64.0
    grid_b = [0.0]
    grid_bpm = [base if not tm else float(tm[0]["bpm"]) if tm[0].get("bar", 1) <= 1 else base]
    pts = [(4.0 * (float(p.get("bar", 1)) - 1.0), float(p["bpm"]), float(p.get("curve", 1))) for p in tm]
    for k, (b, bpm, curve) in enumerate(pts):
        nb = pts[k + 1][0] if k + 1 < len(pts) else total_beats
        if curve == 0 and k + 1 < len(pts):        # linear ramp to next point's bpm
            for s in range(16):
                grid_b.append(b + (nb - b) * s / 16.0)
                grid_bpm.append(bpm + (pts[k + 1][1] - bpm) * s / 16.0)
        else:                                       # hold then step (engine default)
            grid_b.append(b)
            grid_bpm.append(bpm)
    grid_b.append(total_beats)
    grid_bpm.append(grid_bpm[-1])
    bs, bpms = np.array(grid_b), np.array(grid_bpm)
    order = np.argsort(bs)
    bs, bpms = bs[order], bpms[order]
    secs = np.zeros_like(bs)
    for i in range(1, len(bs)):
        secs[i] = secs[i - 1] + (bs[i] - bs[i - 1]) * 60.0 / max(bpms[i - 1], 1e-6)
    return (lambda b: float(np.interp(b, bs, secs))), (lambda s: float(np.interp(s, secs, bs)))


def clip_beat_fn(clip, song):
    """file-time (sec) -> song beat for one audioClip (handles sourceBpm warp)."""
    b2s, s2b = beat_maps(song)
    start = float(clip.get("startBeat", 0.0))
    off = float(clip.get("offsetSec", 0.0))
    src_bpm = float(clip.get("sourceBpm", 0.0) or 0.0)
    if src_bpm > 0:                                  # warped: file tempo -> beats directly
        return lambda t: start + (t - off) * src_bpm / 60.0
    t0 = b2s(start)
    return lambda t: s2b(t0 + (t - off))


def parse_key(s):
    if not s:
        return None
    m = re.match(r"\s*([A-Ga-g])\s*([b#]?)\s*(major|minor|maj|min|m\b)?", str(s))
    if not m:
        return None
    pc = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}[m.group(1).upper()]
    pc = (pc + (1 if m.group(2) == "#" else -1 if m.group(2) == "b" else 0)) % 12
    mode = "minor" if (m.group(3) or "").lower().startswith(("min", "m")) else "major"
    return pc, mode


def fit_scale(pc_hist):
    best = (-2.0, 0, "major")
    for mode, prof in (("major", KK_MAJ), ("minor", KK_MIN)):
        for tonic in range(12):
            r = np.corrcoef(np.roll(prof, tonic), pc_hist)[0, 1]
            if r > best[0]:
                best = (r, tonic, mode)
    return best[1], best[2]


class SongContext:
    """Per-half-beat harmonic field + global scale, from every non-vocal symbolic track."""
    WIN = 0.5

    def __init__(self, song, exclude_track=None, key_override=None):
        self.song = song
        nb = int(math.ceil(4.0 * float(song.get("lengthBars", 16)))) + 8
        n = int(nb / self.WIN)
        self.w_pcs = np.zeros((n, 12))
        self.w_bass = [(None, 1e9)] * n           # (pc, lowest pitch) per window
        hist = np.zeros(12)
        for tr in song.get("tracks", []):
            if tr.get("name") == exclude_track:
                continue
            sid = str(tr.get("source", {}).get("id", "")) + " " + str(tr.get("name", ""))
            if DRUM_RX.search(sid):
                continue
            for nt in tr.get("notes", []):
                p, st = nt.get("pitch"), float(nt.get("start", 0))
                ln, vel = float(nt.get("len", 0.25)), float(nt.get("vel", 0.8))
                if p is None:
                    continue
                w = (2.0 if p < 48 else 1.0) * max(vel, 0.1)
                hist[int(p) % 12] += ln * w
                i0, i1 = int(st / self.WIN), int(math.ceil((st + ln) / self.WIN))
                for i in range(max(i0, 0), min(i1, n)):
                    ov = min(st + ln, (i + 1) * self.WIN) - max(st, i * self.WIN)
                    if ov <= 0:
                        continue
                    self.w_pcs[i, int(p) % 12] += ov * w
                    if p < self.w_bass[i][1]:
                        self.w_bass[i] = (int(p) % 12, p)
        ko = parse_key(key_override) or parse_key(song.get("key"))
        if ko:
            self.tonic, self.mode, self.scale_src = ko[0], ko[1], "meta"
        elif hist.sum() > 0:
            self.tonic, self.mode = fit_scale(hist)
            self.scale_src = "fitted"
        else:
            self.tonic, self.mode, self.scale_src = 0, "major", "default"
        self.scale = {(self.tonic + d) % 12 for d in SCALE_PCS[self.mode]}
        self.has_notes = hist.sum() > 0

    def scale_name(self):
        return f"{NOTE_NAMES[self.tonic]} {self.mode}"

    def field(self, b0, b1):
        """(chord_pcs, bass_pc) in beat span [b0,b1] — windows weighted by overlap,
        so a few ms of bleed into the next chord can't poison the set."""
        b0, b1 = max(b0, 0.0), max(b1, b0 + 1e-3)
        i0, i1 = int(b0 / self.WIN), min(int(math.ceil(b1 / self.WIN)), len(self.w_pcs))
        if i0 >= len(self.w_pcs):
            return set(), None
        acc = np.zeros(12)
        basses = []
        for i in range(i0, max(i1, i0 + 1)):
            ov = min(b1, (i + 1) * self.WIN) - max(b0, i * self.WIN)
            if ov <= 0:
                continue
            acc += self.w_pcs[i] * ov
            if self.w_bass[i][0] is not None and ov > 0.4 * self.WIN:
                basses.append(self.w_bass[i])
        if acc.sum() <= 0:
            return set(), None
        chord = {pc for pc in range(12) if acc[pc] >= 0.25 * acc.max()}
        bass = min(basses, key=lambda x: x[1])[0] if basses else None
        return chord, bass

    def field_for_note(self, b0, b1):
        """Field query for a sung note: its front-biased BODY (first 70%) — where a
        note lands defines its harmony; tail bleed over a chord change is ignored."""
        return self.field(b0, b0 + 0.7 * max(b1 - b0, 1e-3))


# ---------------------------------------------------------------- F0 + notes
def _f0_neural(y, fs, t_grid, mode):
    """FCPE (fast context model) or CREPE f0 on the WORLD 5ms grid; 0 = unvoiced.
    The rail for WET/IN-MIX sources — harvest collapses on reverb/bleed, these don't."""
    import torch
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    if mode == "fcpe":
        from torchfcpe import spawn_bundled_infer_model
        model = spawn_bundled_infer_model(device=dev)
        au = torch.from_numpy(y.astype(np.float32)).unsqueeze(0).unsqueeze(-1).to(dev)
        f0 = model.infer(au, sr=fs, decoder_mode="local_argmax", threshold=0.006,
                         f0_min=60.0, f0_max=1300.0, interp_uv=False,
                         output_interp_target_length=len(t_grid))
        f0 = f0.squeeze().cpu().numpy().astype(np.float64)
    else:                                              # crepe
        import torchcrepe
        hop = int(fs * FRAME_MS / 1000.0)
        au = torch.from_numpy(y.astype(np.float32)).unsqueeze(0).to(dev)
        f0t, pd = torchcrepe.predict(au, fs, hop, 60.0, 1300.0, "full",
                                     return_periodicity=True, device=dev, batch_size=512)
        f0 = f0t.squeeze().cpu().numpy().astype(np.float64)
        f0[pd.squeeze().cpu().numpy() < 0.3] = 0.0
        f0 = np.interp(t_grid, np.arange(len(f0)) * FRAME_MS / 1000.0, f0)
    f0[f0 < 60.0] = 0.0
    return f0


def detect_world(y, fs, f0_mode="harvest"):
    import pyworld as pw
    f0, t = pw.harvest(y, fs, f0_floor=60.0, f0_ceil=1300.0, frame_period=FRAME_MS)
    if f0_mode in ("fcpe", "crepe"):
        try:
            f0n = _f0_neural(y, fs, t, f0_mode)
            if (f0n > 0).sum() >= 8:
                f0 = f0n
            else:
                print(f"[retune] {f0_mode} found no voice — falling back to harvest")
        except Exception as e:
            print(f"[retune] {f0_mode} unavailable ({type(e).__name__}: {e}) — harvest fallback")
    f0 = octave_guard(f0)
    sp = pw.cheaptrick(y, f0, t, fs)
    ap = pw.d4c(y, f0, t, fs)
    return f0, t, sp, ap


def octave_guard(f0):
    """Fold lone octave flips back onto the running median."""
    f0 = f0.copy()
    med = 0.0
    hist = []
    for i in range(len(f0)):
        if f0[i] <= 0:
            continue
        if hist:
            med = float(np.median(hist[-15:]))
            for mult in (2.0, 0.5):
                if abs(1200.0 * math.log2(f0[i] / (med * mult))) < 120.0 and \
                   abs(1200.0 * math.log2(f0[i] / med)) > 900.0:
                    f0[i] = f0[i] / mult
                    break
        hist.append(f0[i])
    return f0


def segment_notes(midi, voiced, split_cents, min_note_ms, persist=3):
    """Voiced frames -> note events [(i0,i1)] (end-exclusive). A sustained deviation
    > split_cents from the running median opens a new event (glides become stairs —
    with tpain thresholds this IS the yodel machine)."""
    hop_frames_min = max(2, int(min_note_ms / FRAME_MS))
    events = []
    n = len(midi)
    i = 0
    while i < n:
        if not voiced[i]:
            i += 1
            continue
        j = i
        start = i
        buf = []
        anchor = midi[i]
        while j < n and voiced[j]:
            buf.append(midi[j])
            if len(buf) <= 8:                      # anchor = median of the note's head,
                anchor = float(np.median(buf))     # then FROZEN (glides break away from
            cur = float(np.median(buf[-3:]))       # it and become stairs)
            if len(buf) >= 4 and abs(cur - anchor) * 100.0 > split_cents:
                ahead = midi[j:min(n, j + persist)]
                vh = voiced[j:min(n, j + persist)]
                if len(ahead) == persist and all(vh) and \
                   all(abs(a - anchor) * 100.0 > split_cents for a in ahead) and \
                   len({np.sign(a - anchor) for a in ahead}) == 1:
                    events.append((start, j))
                    start, buf = j, [midi[j]]
                    anchor = midi[j]
            j += 1
        events.append((start, j))
        i = j
    events = [(a, b) for a, b in events if b > a]
    # absorb pitch-sweep transients (note transitions, onset scoops) into the note
    # they lead into — a 40ms sweep is an approach, not a note
    absorbed = []
    i = 0
    while i < len(events):
        a, b = events[i]
        seg = midi[a:b]
        sweep = (b - a) * FRAME_MS < 80.0 and \
            float(np.percentile(seg, 90) - np.percentile(seg, 10)) > 1.2
        if sweep and i + 1 < len(events) and events[i + 1][0] == b:
            events[i + 1] = [a, events[i + 1][1]]
        elif sweep and absorbed and absorbed[-1][1] == a:
            absorbed[-1] = [absorbed[-1][0], b]
        else:
            absorbed.append([a, b])
        i += 1
    events = absorbed
    # merge splinters into the closer-pitch adjacent event within the same voiced run
    merged = []
    for ev in events:
        if merged and ev[1] - ev[0] < hop_frames_min and merged[-1][1] == ev[0]:
            merged[-1] = [merged[-1][0], ev[1]]
        else:
            merged.append(list(ev))
    events = merged
    out = []
    for k, ev in enumerate(events):
        if ev[1] - ev[0] < hop_frames_min and k + 1 < len(events) and events[k + 1][0] == ev[1]:
            events[k + 1][0] = ev[0]              # give to the next event
            continue
        out.append((ev[0], ev[1]))
    return [(a, b) for a, b in out if b - a >= max(2, hop_frames_min // 2)]


# ---------------------------------------------------------------- targets (Viterbi)
def choose_targets(events, med_midi, spans, ctx, style, guide_notes=None):
    """Per-event target pitch by DP: emission = proximity + chord/scale/bass membership,
    transition = contour preservation. Returns (targets, reasons)."""
    cands, emis = [], []
    for k, (i0, i1) in enumerate(events):
        m = med_midi[k]
        b0, b1 = spans[k] if spans else (None, None)
        chord, bass = ctx.field_for_note(b0, b1) if (ctx and b0 is not None) else (set(), None)
        gp = []
        if guide_notes is not None and b0 is not None:
            for nt in guide_notes:
                st, ln = float(nt.get("start", 0)), float(nt.get("len", 0.25))
                if nt.get("pitch") is not None and st < b1 and st + ln > b0:
                    g = float(nt["pitch"])
                    gp.append(int(round(g + 12.0 * round((m - g) / 12.0))))  # octave-fold to singer
        if gp:
            cs = sorted(set(gp))
        else:
            base = int(round(m))
            cs = list(range(base - 3, base + 4))
        row = []
        for p in cs:
            d = abs(p - m)                                   # semitones
            e = -style["w_prox"] * d
            if gp:
                e += 3.0                                     # guide candidates pre-blessed
            pc = p % 12
            in_chord = pc in chord
            in_scale = pc in ctx.scale if ctx else False
            if in_chord:
                e += style["w_chord"]
            if in_scale:
                e += style["w_scale"]
            if bass is not None and pc == bass:
                e += style["w_bass"]
            if ctx and not in_chord and not in_scale:
                e -= style["w_out"]
            row.append(e)
        cands.append(cs)
        emis.append(row)
    # Viterbi
    n = len(events)
    if n == 0:
        return [], []
    dp = [list(emis[0])]
    bk = [[0] * len(cands[0])]
    for k in range(1, n):
        dpk, bkk = [], []
        sung_iv = med_midi[k] - med_midi[k - 1]
        for j, p in enumerate(cands[k]):
            best, arg = -1e18, 0
            for i, q in enumerate(cands[k - 1]):
                cost = style["w_contour"] * min(abs((p - q) - sung_iv), 4.0)
                v = dp[k - 1][i] - cost
                if v > best:
                    best, arg = v, i
            dpk.append(best + emis[k][j])
            bkk.append(arg)
        dp.append(dpk)
        bk.append(bkk)
    j = int(np.argmax(dp[-1]))
    path = [0] * n
    for k in range(n - 1, -1, -1):
        path[k] = cands[k][j]
        j = bk[k][j]
    reasons = []
    for k, p in enumerate(path):
        b0, b1 = spans[k] if spans else (None, None)
        chord, bass = ctx.field_for_note(b0, b1) if (ctx and b0 is not None) else (set(), None)
        pc = p % 12
        if guide_notes is not None and abs(p - med_midi[k]) < 12 and b0 is not None and \
           any(nt.get("pitch") is not None and (int(nt["pitch"]) - p) % 12 == 0 and
               float(nt.get("start", 0)) < b1 and float(nt.get("start", 0)) + float(nt.get("len", 0.25)) > b0
               for nt in guide_notes):
            reasons.append("guide")
        elif pc in chord:
            label = NOTE_NAMES[bass] if bass is not None else \
                "+".join(NOTE_NAMES[c] for c in sorted(chord))
            reasons.append(f"chord({label})")
        elif ctx and pc in ctx.scale:
            reasons.append(f"scale({ctx.scale_name()})")
        else:
            reasons.append("nearest")
    return path, reasons


# ---------------------------------------------------------------- curve + resynth
def medfilt1(x, k):
    if len(x) < 3:
        return x.copy()
    k = min(k if k % 2 else k + 1, len(x) - (1 - len(x) % 2))
    k = max(k, 1)
    pad = k // 2
    xp = np.pad(x, pad, mode="edge")
    return np.array([np.median(xp[i:i + k]) for i in range(len(x))])


def build_curve(f0, events, targets, style, correct_mask, rng):
    """Corrected f0 array (WORLD grid). Uncorrected/unvoiced frames pass through."""
    out = f0.copy()
    midi = midi_of(np.where(f0 > 0, f0, 1.0))
    hop_s = FRAME_MS / 1000.0
    tau = max(style["retune_ms"], 1.0) / 1000.0
    slow_k = int(150.0 / FRAME_MS) | 1
    for (i0, i1), T, corr in zip(events, targets, correct_mask):
        if not corr:
            continue
        seg = midi[i0:i1]
        dev = (seg - T) * 100.0                       # cents vs target
        slow = medfilt1(dev, slow_k)
        fast = dev - slow
        walk = np.cumsum(rng.normal(0, 1, len(dev)))
        if np.std(walk) > 1e-6 and style["humanize"] > 0:
            walk = medfilt1(walk, 5)
            walk = walk / (np.std(walk) + 1e-9) * style["humanize"]
        else:
            walk = np.zeros(len(dev))
        cdev = (1.0 - style["amount"]) * slow + style["vibrato_keep"] * fast + walk
        g = np.exp(-(np.arange(len(dev)) * hop_s) / tau)
        cdev = cdev + g * (dev[0] - cdev[0])          # continuous entry, then snap
        new_m = T + np.clip(cdev, -700.0, 700.0) / 100.0
        new_m = np.clip(new_m, seg - 7.0, seg + 7.0)  # ±7 st safety vs sung
        out[i0:i1] = np.where(f0[i0:i1] > 0, hz_of(new_m), 0.0)
    return out


def resynth(y, fs, f0, sp, ap, f0_new):
    import pyworld as pw
    out = pw.synthesize(np.ascontiguousarray(f0_new), sp, ap, fs, frame_period=FRAME_MS)
    if len(out) < len(y):
        out = np.pad(out, (0, len(y) - len(out)))
    out = out[:len(y)]
    peak = float(np.max(np.abs(out)) or 1.0)
    if peak > 0.999:
        out = out * (0.98 / peak)
    return out


def splice_spans(f0, f0_new, fs, n_samples):
    """THE SURGICAL SPLICE: sample spans that must go through WORLD — frames where
    pitch audibly changes (>3.5 cents), padded 10ms, merged across <20ms gaps.
    Everything OUTSIDE stays bit-exact original (consonants, breaths, silence:
    zero vocoder coloration where nothing needed fixing)."""
    hop = int(fs * FRAME_MS / 1000.0)
    changed = (f0 > 0) & (np.abs(f0_new / np.where(f0 > 0, f0, 1.0) - 1.0) > 0.002)
    idx = np.flatnonzero(changed)
    if len(idx) == 0:
        return []
    pad = int(0.010 * fs)
    raw = []
    s = e = idx[0]
    for i in idx[1:]:
        if (i - e) * hop <= int(0.020 * fs):     # merge only truly small gaps
            e = i
        else:
            raw.append((s, e))
            s = e = i
    raw.append((s, e))
    spans = []
    for s, e in raw:                              # pad AFTER merging; coalesce overlaps
        a, b = max(0, s * hop - pad), min(n_samples, (e + 1) * hop + pad)
        if spans and a <= spans[-1][1]:
            spans[-1] = (spans[-1][0], b)
        else:
            spans.append((a, b))
    return spans


def splice(orig, world, spans, fs):
    """orig with WORLD spans crossfaded in (cos^2, ~6ms)."""
    out = orig.copy()
    xf = min(int(0.006 * fs), 1024)
    ramp = np.sin(np.linspace(0, np.pi / 2, xf)) ** 2
    for s, e in spans:
        out[s:e] = world[s:e]
        a = max(0, s - xf)
        if s > 0 and s - a > 8:
            w = ramp[-(s - a):]
            out[a:s] = orig[a:s] * (1 - w) + world[a:s] * w
        b = min(len(out), e + xf)
        if e < len(out) and b - e > 8:
            w = ramp[:b - e][::-1]
            out[e:b] = orig[e:b] * (1 - w) + world[e:b] * w
    return out


# ---------------------------------------------------------------- driver
def process(in_path, out_path, song_path=None, track=None, style_name="natural",
            overrides=None, key=None, guide_track=None, region=None, clip_index=0,
            report_path=None, quiet=False, f0_mode="harvest"):
    style = dict(STYLES[style_name])
    style.update({k: v for k, v in (overrides or {}).items() if v is not None})
    y_multi, fs = sf.read(in_path, always_2d=True)
    info = sf.info(in_path)
    y = np.ascontiguousarray(y_multi.mean(axis=1), dtype=np.float64)

    song = ctx = beat_of = None
    guide_notes = None
    if song_path:
        song = json.load(open(song_path))
        ctx = SongContext(song, exclude_track=track, key_override=key)
        clip = {"startBeat": 0.0}
        if track:
            trs = [t for t in song.get("tracks", []) if t.get("name") == track]
            if trs and trs[0].get("audioClips"):
                clips = trs[0]["audioClips"]
                clip = clips[min(clip_index, len(clips) - 1)]
        beat_of = clip_beat_fn(clip, song)
        if guide_track:
            gts = [t for t in song.get("tracks", []) if t.get("name") == guide_track]
            guide_notes = gts[0].get("notes", []) if gts else None
    elif key:
        class _K:                                     # key-only floor (classic mode)
            pass
        ctx = _K()
        pk = parse_key(key) or (0, "major")
        ctx.tonic, ctx.mode = pk
        ctx.scale = {(pk[0] + d) % 12 for d in SCALE_PCS[pk[1]]}
        ctx.scale_name = lambda: f"{NOTE_NAMES[pk[0]]} {pk[1]}"
        ctx.field = lambda b0, b1: (set(), None)
        ctx.has_notes = False

    f0, t, sp, ap = detect_world(y, fs, f0_mode=f0_mode)
    voiced = f0 > 0
    midi = midi_of(np.where(voiced, f0, 1.0))
    events = segment_notes(midi, voiced, style["split_cents"], style["min_note_ms"])
    med_midi = [float(np.median(midi[a:b])) for a, b in events]
    spans = None
    if beat_of:
        spans = [(beat_of(t[a]), beat_of(t[min(b, len(t) - 1)])) for a, b in events]
    elif ctx:
        spans = [(None, None)] * len(events)

    targets, reasons = choose_targets(events, med_midi, spans, ctx, style, guide_notes) \
        if ctx else (list(map(lambda m: int(round(m)), med_midi)), ["nearest"] * len(events))

    # energy gate: events buried >26 dB under the voiced body are breath/rumble —
    # pass them through untouched (below-threshold input, classic tuner behavior)
    hop = int(fs * FRAME_MS / 1000.0)
    nfr = len(f0)
    pads = np.pad(y ** 2, (0, hop * (nfr + 1)))
    frame_rms = np.sqrt(np.array([pads[i * hop:(i + 1) * hop].mean() for i in range(nfr)]) + 1e-12)
    v_ref = np.percentile(frame_rms[voiced], 90) if voiced.any() else 1.0
    correct_mask = [True] * len(events)
    for k, (a, b) in enumerate(events):
        ev_rms = float(np.median(frame_rms[a:b]))
        if ev_rms < v_ref * 10 ** (-26.0 / 20.0):
            correct_mask[k] = False
            reasons[k] = "held(quiet)"
    if region and len(region) == 2:
        lo, hi = float(region[0]), float(region[1])
        for k, (a, b) in enumerate(events):
            pos0, pos1 = (spans[k] if (spans and spans[k][0] is not None) else (t[a], t[min(b, len(t) - 1)]))
            correct_mask[k] = pos1 > lo and pos0 < hi
        for k in range(len(events)):
            if not correct_mask[k]:
                reasons[k] = "held(region)"

    rng = np.random.default_rng(0xC0FFEE ^ len(y))
    f0_new = build_curve(f0, events, targets, style, correct_mask, rng)

    rs_spans = splice_spans(f0, f0_new, fs, len(y)) if out_path else []
    resynth_smp = sum(e - s for s, e in rs_spans)
    if out_path:
        chans = []
        for c in range(y_multi.shape[1]):
            yc = np.ascontiguousarray(y_multi[:, c], dtype=np.float64)
            import pyworld as pw
            spc = pw.cheaptrick(yc, f0, t, fs)
            apc = pw.d4c(yc, f0, t, fs)
            world_c = resynth(yc, fs, f0, spc, apc, f0_new)
            chans.append(splice(yc, world_c, rs_spans, fs))
        out = np.stack(chans, axis=1) if len(chans) > 1 else chans[0]
        # FLOAT DECK LAW: float inputs stay float (vocal_truth decks carry
        # sub-int16-LSB content; forcing PCM_16 truncated it to zero and made
        # passthrough spans non-bit-true). Unknown exotic subtypes -> PCM_16.
        keep = info.subtype.startswith("PCM") or "FLOAT" in info.subtype or "DOUBLE" in info.subtype
        sf.write(out_path, out, fs, subtype=info.subtype if keep else "PCM_16")

    # report
    notes_rep = []
    moved = []
    for k, (a, b) in enumerate(events):
        d0 = (med_midi[k] - targets[k]) * 100.0
        if correct_mask[k]:
            moved.append(abs(d0))
        sign = "+" if d0 >= 0 else ""
        notes_rep.append({
            "t0": round(float(t[a]), 3), "t1": round(float(t[min(b, len(t) - 1)]), 3),
            "beat0": round(spans[k][0], 3) if spans and spans[k][0] is not None else None,
            "beat1": round(spans[k][1], 3) if spans and spans[k][0] is not None else None,
            "sung": f"{midi_name(med_midi[k])}{sign}{d0:.0f}c" if abs(d0) >= 1 else midi_name(med_midi[k]),
            "sung_midi": round(med_midi[k], 2),
            "target": int(targets[k]), "target_name": midi_name(targets[k]),
            "cents_moved": round(-d0, 1) if correct_mask[k] else 0.0,
            "reason": reasons[k],
        })
    rep = {
        "tool": "retune", "version": 1, "style": style_name,
        "params": {k: style[k] for k in ("amount", "retune_ms", "vibrato_keep", "humanize")},
        "input": in_path, "output": out_path, "song": song_path, "track": track,
        "scale": {"name": ctx.scale_name(), "source": getattr(ctx, "scale_src", "arg")} if ctx else None,
        "notes": notes_rep,
        "stats": {"events": len(events), "corrected": int(sum(correct_mask)),
                  "median_abs_cents_off": round(float(np.median(moved)), 1) if moved else 0.0,
                  "max_abs_cents_off": round(float(np.max(moved)), 1) if moved else 0.0,
                  "f0_mode": f0_mode,
                  "resynth_pct": round(100.0 * resynth_smp / max(len(y), 1), 1),
                  "passthrough_pct": round(100.0 - 100.0 * resynth_smp / max(len(y), 1), 1)},
    }
    if report_path:
        json.dump(rep, open(report_path, "w"), indent=1)
    if not quiet:
        sc = f" scale={ctx.scale_name()}({getattr(ctx, 'scale_src', 'arg')})" if ctx else ""
        print(f"[retune] {os.path.basename(in_path)} style={style_name}{sc} "
              f"events={len(events)} corrected={sum(correct_mask)} "
              f"median_off={rep['stats']['median_abs_cents_off']}c")
        for nr in notes_rep[:40]:
            bb = f"b{nr['beat0']:.2f}" if nr["beat0"] is not None else f"{nr['t0']:.2f}s"
            print(f"  {bb:>8} {nr['sung']:>9} -> {nr['target_name']:<4} "
                  f"({nr['cents_moved']:+.0f}c) {nr['reason']}")
        if len(notes_rep) > 40:
            print(f"  ... +{len(notes_rep) - 40} more (see report)")
    return rep, f0, f0_new, t, events, targets


# ---------------------------------------------------------------- selftest
def synth_bad_singer(fs=44100):
    """A saw 'voice' with formant filters singing C D E G E D C + a C->E glide,
    detuned way off (up to 70c), with drift + 5.5Hz vibrato. Ground truth known."""
    from scipy.signal import butter, lfilter
    seq = [(60, +40), (62, +60), (64, -45), (67, +55), (64, -70), (62, +25), (60, +40)]
    dur, gap = 0.44, 0.06
    total = (len(seq) + 1) * (dur + gap)
    n = int(total * fs)
    tt = np.arange(n) / fs
    f = np.zeros(n)
    env = np.zeros(n)
    for k, (m, c) in enumerate(seq + [(60, 0)]):
        t0 = k * (dur + gap)
        i0, i1 = int(t0 * fs), int((t0 + dur) * fs)
        seg_t = tt[i0:i1] - t0
        vib = 0.30 * np.sin(2 * np.pi * 5.5 * seg_t) * np.clip((seg_t - 0.12) / 0.1, 0, 1)
        drift = 0.15 * seg_t / dur
        if k < len(seq):
            mm = m + c / 100.0 + drift + vib
        else:                                          # final: glide C4 -> E4
            mm = 60.0 + 4.0 * (seg_t / dur) + 0.10 * np.sin(2 * np.pi * 5.5 * seg_t)
        f[i0:i1] = hz_of(mm)
        e = np.ones(i1 - i0)
        r = int(0.012 * fs)
        e[:r] = np.linspace(0, 1, r)
        e[-r:] = np.linspace(1, 0, r)
        env[i0:i1] = e
    phase = np.cumsum(f) / fs
    saw = 2.0 * (phase % 1.0) - 1.0
    y = saw * env
    for fc in (600.0, 1150.0):
        b, a = butter(2, [fc * 0.7 / (fs / 2), fc * 1.4 / (fs / 2)], btype="band")
        y = y + 1.2 * lfilter(b, a, saw * env)
    b, a = butter(2, 3800 / (fs / 2))
    y = lfilter(b, a, y)
    gate = np.ones(n)                              # HONEST silence between notes
    r = int(0.003 * fs)                            # (kills filter ring so harvest
    for k in range(1, len(seq) + 1):               #  truly unvoices the gaps —
        g0, g1 = int((k * 0.5 - gap + 0.004) * fs), int((k * 0.5 - 0.004) * fs)
        gate[g0:g1] = 0.0                          #  the splice passthrough test)
        gate[g0 - r:g0] = np.linspace(1, 0, r)
        gate[g1:g1 + r] = np.linspace(0, 1, r)
    y = y * gate
    y = y / np.max(np.abs(y)) * 0.5
    return y.astype(np.float64), fs, seq


def selftest(tmpdir):
    y, fs, seq = synth_bad_singer()
    wav = os.path.join(tmpdir, "_tune_selftest_in.wav")
    sf.write(wav, y, fs, subtype="PCM_16")
    chords = {0: [(48, "C"), (52, "C"), (55, "C")], 1: [(43, "G"), (47, "G"), (50, "G")],
              2: [(48, "C"), (52, "C"), (55, "C")], 3: [(48, "C"), (52, "C"), (55, "C")],
              4: [(45, "A"), (48, "A"), (52, "A")], 5: [(43, "G"), (47, "G"), (50, "G")],
              6: [(48, "C"), (52, "C"), (55, "C")], 7: [(48, "C"), (52, "C"), (55, "C")]}
    pad = [{"start": float(b), "len": 1.0, "pitch": p, "vel": 0.8}
           for b, cs in chords.items() for p, _ in cs]
    bass = [{"start": float(b), "len": 1.0, "pitch": cs[0][0] - 12, "vel": 0.9}
            for b, cs in chords.items()]
    song = {"version": 2, "bpm": 120.0, "lengthBars": 2, "tracks": [
        {"name": "pads", "source": {"kind": "faust", "id": "pad"}, "notes": pad},
        {"name": "bass", "source": {"kind": "faust", "id": "bass"}, "notes": bass},
        {"name": "vox", "source": {"kind": "audio", "id": "vox"}, "notes": [],
         "audioClips": [{"file": wav, "startBeat": 0}]}]}
    # note dur .47+gap .03 = .5s = 1 beat @120
    song_path = os.path.join(tmpdir, "_tune_selftest_song.json")
    json.dump(song, open(song_path, "w"))
    intended = [60, 62, 64, 67, 64, 62, 60]
    naive = [int(round(m + c / 100.0)) for m, c in seq]
    fails = []

    for style in ("tpain", "natural"):
        out = os.path.join(tmpdir, f"_tune_selftest_{style}.wav")
        rep, f0, f0n, t, events, targets = process(
            wav, out, song_path=song_path, track="vox", style_name=style, quiet=True)
        # map first 7 sung beats -> chosen targets (glide events come after)
        got = targets[:7]
        if got != intended:
            fails.append(f"{style}: targets {got} != intended {intended}")
        if targets[-1] != 64:
            fails.append(f"{style}: glide should land on E4(64), got {targets[-1]}")
        yo, fso = sf.read(out)
        yi = sf.read(wav)[0]
        if abs(len(yo) - len(yi)) > 4:
            fails.append(f"{style}: length changed")
        if np.any(~np.isfinite(yo)) or np.max(np.abs(yo)) > 0.999:
            fails.append(f"{style}: bad samples")
        # surgical splice: unvoiced gap centers must be BIT-EXACT passthrough
        for k in range(1, 7):
            gi = int((k * 0.5 - 0.030) * fso)
            if not np.array_equal(yo[gi:gi + 64], yi[gi:gi + 64]):
                fails.append(f"{style}: gap {k} not bit-exact (splice leak)")
                break
        rp = rep["stats"].get("resynth_pct", 100.0)
        if not (5.0 < rp < 99.9):                 # synthetic singer is wrong EVERYWHERE
            fails.append(f"{style}: resynth_pct {rp} out of sane range")
        # measured post-correction accuracy on steady middles
        import pyworld as pw
        f0v, tv = pw.harvest(np.ascontiguousarray(yo.astype(np.float64)), fso,
                             f0_floor=60, f0_ceil=1300, frame_period=FRAME_MS)
        errs, vib_ratio = [], []
        for k in range(7):
            a, b = events[k]
            a2, b2 = a + int(60 / FRAME_MS), b - int(60 / FRAME_MS)
            if b2 <= a2:
                continue
            seg = f0v[a2:b2]
            seg = seg[seg > 0]
            if len(seg) < 4:
                continue
            mo = midi_of(seg)
            errs.append(abs(float(np.median(mo)) - targets[k]) * 100.0)
            devo = (mo - targets[k]) * 100.0
            fasto = devo - medfilt1(devo, 31)
            mi = midi_of(f0[a2:b2][f0[a2:b2] > 0])
            devi = (mi - targets[k]) * 100.0
            fasti = devi - medfilt1(devi, 31)
            if np.std(fasti) > 2:
                vib_ratio.append(np.std(fasto) / np.std(fasti))
        med_err = float(np.median(errs))
        lim = 10.0 if style == "tpain" else 30.0
        if med_err > lim:
            fails.append(f"{style}: post-tune median error {med_err:.1f}c > {lim}c")
        vr = float(np.median(vib_ratio)) if vib_ratio else 0.0
        if style == "natural" and vr < 0.45:
            fails.append(f"natural: vibrato retention {vr:.2f} < 0.45")
        if style == "tpain" and vr > 0.6:
            fails.append(f"tpain: vibrato retention {vr:.2f} > 0.6 (should flatten)")
        print(f"[selftest:{style}] targets={got}+glide->{targets[-1]} "
              f"post_err={med_err:.1f}c vib_keep={vr:.2f} "
              f"resynth={rep['stats'].get('resynth_pct')}% (rest bit-exact)")

    hits = [(k, naive[k], intended[k]) for k in range(7) if naive[k] != intended[k]]
    print(f"[selftest] classic chromatic snap would hit WRONG notes at beats "
          f"{[k for k, _, _ in hits]}: " +
          ", ".join(f"b{k} {midi_name(nv)}(sour)->{midi_name(iv)}" for k, nv, iv in hits))
    if fails:
        print("[selftest] FAIL:\n  - " + "\n  - ".join(fails))
        return 1
    print(f"[selftest] PASS — context beat chromatic snapping on {len(hits)} traps")
    return 0


def main():
    ap = argparse.ArgumentParser(description="CONTEXT-TUNE: song-aware vocal pitch correction")
    ap.add_argument("input", nargs="?")
    ap.add_argument("output", nargs="?")
    ap.add_argument("--song")
    ap.add_argument("--track")
    ap.add_argument("--style", default="natural", choices=sorted(STYLES))
    ap.add_argument("--strength", type=float, help="override amount 0..1")
    ap.add_argument("--retune-ms", type=float)
    ap.add_argument("--vibrato-keep", type=float)
    ap.add_argument("--humanize-cents", type=float)
    ap.add_argument("--key", help="e.g. 'F minor' — used when no --song (or to override)")
    ap.add_argument("--guide-track", help="track whose notes are the target melody")
    ap.add_argument("--region", nargs=2, type=float, metavar=("B0", "B1"),
                    help="only correct events inside this span (beats with --song, else sec)")
    ap.add_argument("--clip-index", type=int, default=0)
    ap.add_argument("--f0", default="harvest", choices=["harvest", "fcpe", "crepe"],
                    help="F0 rail: harvest (dry, default) | fcpe/crepe (wet/in-mix sources)")
    ap.add_argument("--report", help="write per-note JSON report here")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        tmp = os.path.join(ROOT, "songs")
        sys.exit(selftest(tmp))
    if not a.input or not a.output:
        ap.error("input and output required (or --selftest)")
    ov = dict(amount=a.strength, retune_ms=a.retune_ms,
              vibrato_keep=a.vibrato_keep, humanize=a.humanize_cents)
    report = a.report or (os.path.splitext(a.output)[0] + ".report.json")
    process(a.input, a.output, song_path=a.song, track=a.track, style_name=a.style,
            overrides=ov, key=a.key, guide_track=a.guide_track, region=a.region,
            clip_index=a.clip_index, report_path=report, f0_mode=a.f0)
    print(f"[retune] wrote {a.output} + {report}")


if __name__ == "__main__":
    main()
