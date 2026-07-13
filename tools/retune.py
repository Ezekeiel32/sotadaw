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
    # center_amt/drift_amt = THE MELODYNE SPLIT (pros: center ~100%, drift ~80%,
    # modulation kept — vibrato_keep). amount stays the fallback for both.
    # flex_cents = FLEX-TUNE (Antares craft): a tolerance zone around the target —
    # a note whose CENTER already sits inside it is left completely raw
    # (reason held(in-tune)); slides/scoops survive, correction engages only
    # when the singer actually strays.
    "tpain":       dict(amount=1.0,  retune_ms=3.0,   vibrato_keep=0.15, humanize=0.0,
                        center_amt=1.0, drift_amt=1.0, flex_cents=0.0,
                        split_cents=55.0, min_note_ms=35.0,
                        w_prox=0.7, w_chord=1.6, w_scale=0.9, w_bass=0.3, w_out=2.5, w_contour=0.6),
    "hard":        dict(amount=1.0,  retune_ms=12.0,  vibrato_keep=0.35, humanize=1.0,
                        center_amt=1.0, drift_amt=0.9, flex_cents=10.0,
                        split_cents=60.0, min_note_ms=45.0,
                        w_prox=0.8, w_chord=1.4, w_scale=0.9, w_bass=0.25, w_out=2.2, w_contour=0.7),
    "natural":     dict(amount=0.85, retune_ms=90.0,  vibrato_keep=0.9,  humanize=2.5,
                        center_amt=1.0, drift_amt=0.8, flex_cents=25.0,
                        split_cents=70.0, min_note_ms=60.0,
                        w_prox=1.2, w_chord=0.9, w_scale=0.8, w_bass=0.2, w_out=1.5, w_contour=0.8),
    "transparent": dict(amount=0.6,  retune_ms=150.0, vibrato_keep=1.0,  humanize=2.0,
                        center_amt=0.8, drift_amt=0.5, flex_cents=35.0,
                        split_cents=80.0, min_note_ms=80.0,
                        w_prox=3.0, w_chord=0.3, w_scale=0.6, w_bass=0.1, w_out=1.0, w_contour=1.0),
}

DRUM_RX = re.compile(r"kick|snare|clap|hat\b|hats|hihat|perc|ride|crash|shak|cym|tom", re.I)

# Krumhansl-Kessler key profiles (major/minor), for symbolic scale fit
KK_MAJ = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
KK_MIN = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
SCALE_PCS = {"major": [0, 2, 4, 5, 7, 9, 11], "minor": [0, 2, 3, 5, 7, 8, 10],
             # "A harmonic minor" was unparseable (2026-07-13: the G# class — the
             # tuner erased every leading tone to G natural on a harmonic-minor song)
             "harmonic minor": [0, 2, 3, 5, 7, 8, 11],
             "melodic minor": [0, 2, 3, 5, 7, 9, 11]}


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


def parse_note_name(s):
    """'A3' / 'C#4' / 'Bb2' / 57 -> midi int (midi_name's convention, C4 = 60)."""
    if isinstance(s, (int, float)):
        return int(round(float(s)))
    m = re.match(r"^([A-Ga-g])([#b]?)(-?\d+)$", str(s).strip())
    if not m:
        return None
    base = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}[m.group(1).upper()]
    acc = {"#": 1, "b": -1, "": 0}[m.group(2)]
    return base + acc + (int(m.group(3)) + 1) * 12


def parse_key(s):
    if not s:
        return None
    m = re.match(r"\s*([A-Ga-g])\s*([b#]?)\s*(harmonic\s+minor|melodic\s+minor|"
                 r"major|minor|maj|min|m\b)?", str(s), re.IGNORECASE)
    if not m:
        return None
    pc = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}[m.group(1).upper()]
    pc = (pc + (1 if m.group(2) == "#" else -1 if m.group(2) == "b" else 0)) % 12
    kind = (m.group(3) or "").lower()
    if kind.startswith("harmonic"):
        mode = "harmonic minor"
    elif kind.startswith("melodic"):
        mode = "melodic minor"
    else:
        mode = "minor" if kind.startswith(("min", "m")) else "major"
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
_FCPE_MODEL = {}


def _f0_neural(y, fs, t_grid, mode):
    """FCPE (fast context model) or CREPE f0 on the WORLD 5ms grid; 0 = unvoiced.
    The rail for WET/IN-MIX sources — harvest collapses on reverb/bleed, these don't.
    The fcpe model is a per-device singleton and CUDA scratch is released after
    every rail — consensus calls both models back-to-back and repeated spawns
    OOM'd the selftest's sixth in-process run."""
    import torch
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    try:
        if mode == "fcpe":
            if dev not in _FCPE_MODEL:
                from torchfcpe import spawn_bundled_infer_model
                _FCPE_MODEL[dev] = spawn_bundled_infer_model(device=dev)
            model = _FCPE_MODEL[dev]
            au = torch.from_numpy(y.astype(np.float32)).unsqueeze(0).unsqueeze(-1).to(dev)
            f0 = model.infer(au, sr=fs, decoder_mode="local_argmax", threshold=0.006,
                             f0_min=60.0, f0_max=1300.0, interp_uv=False,
                             output_interp_target_length=len(t_grid))
            f0 = f0.squeeze().cpu().numpy().astype(np.float64)
        else:                                          # crepe
            import torchcrepe
            hop = int(fs * FRAME_MS / 1000.0)
            au = torch.from_numpy(y.astype(np.float32)).unsqueeze(0).to(dev)
            f0t, pd = torchcrepe.predict(au, fs, hop, 60.0, 1300.0, "full",
                                         return_periodicity=True, device=dev,
                                         batch_size=256)
            f0 = f0t.squeeze().cpu().numpy().astype(np.float64)
            f0[pd.squeeze().cpu().numpy() < 0.3] = 0.0
            f0 = np.interp(t_grid, np.arange(len(f0)) * FRAME_MS / 1000.0, f0)
    finally:
        if dev == "cuda":
            torch.cuda.empty_cache()
    f0[f0 < 60.0] = 0.0
    return f0


def _f0_consensus(y, fs, t_grid, f0_ref):
    """THE CONSENSUS RAIL (2026-07-13, "get on par and surpass"): fcpe and crepe have
    near-equal accuracy (MIR-1K RPA ~97-98%) but DECORRELATED error modes (mel-context
    vs raw-waveform CNN) — voting kills exactly the octave flips and ghost voicing
    that survive any single rail. Agreement (<=50c) -> geometric mean; one-sided
    voicing -> that rail; disagreement -> harvest referees (closest wins), fcpe on a
    silent referee. Returns (f0 | None, used_label, note)."""
    outs, downs = {}, []
    for m in ("fcpe", "crepe"):
        try:
            outs[m] = _f0_neural(y, fs, t_grid, m)
        except Exception as e:
            downs.append(f"{m} down ({type(e).__name__})")
    if not outs:
        return None, "harvest", "; ".join(downs) + " — harvest fallback"
    if len(outs) == 1:
        m = next(iter(outs))
        return outs[m], m, f"consensus degraded ({'; '.join(downs)}) — {m} only"
    a, b = outs["fcpe"], outs["crepe"]
    va, vb = a > 0, b > 0
    both = va & vb
    sa = np.where(va, a, 1.0)
    sb = np.where(vb, b, 1.0)
    cents_ab = np.abs(1200.0 * np.log2(sa / sb))
    agree = both & (cents_ab <= 50.0)
    f0 = np.zeros_like(a)
    f0[agree] = np.sqrt(a[agree] * b[agree])
    f0[va & ~vb] = a[va & ~vb]
    f0[vb & ~va] = b[vb & ~va]
    dis = both & ~agree
    if dis.any():
        ref = np.where(f0_ref > 0, f0_ref, 1.0)
        ca = np.abs(1200.0 * np.log2(sa / ref))
        cb = np.abs(1200.0 * np.log2(sb / ref))
        f0[dis] = a[dis]                                   # default: fcpe
        pick_b = dis & (f0_ref > 0) & (cb < ca)
        f0[pick_b] = b[pick_b]
    pct = round(100.0 * float(dis.sum()) / max(int(both.sum()), 1), 1)
    return f0, "consensus", f"fcpe+crepe agree on {100.0 - pct:.1f}% of voiced frames; harvest refereed {pct}%"


def frame_energy(y, fs, nfr):
    """Per-WORLD-frame RMS (the one energy truth: voicing sanity, gates, confidence)."""
    hop = int(fs * FRAME_MS / 1000.0)
    pads = np.pad(y ** 2, (0, hop * (nfr + 1)))
    return np.sqrt(np.array([pads[i * hop:(i + 1) * hop].mean() for i in range(nfr)]) + 1e-12)


def detect_world(y, fs, f0_mode="harvest"):
    """f0/spectral analysis + THE OCTAVE COURT. Returns (f0, t, sp, ap, meta) where
    meta carries the TRUTH the report and the agent need: which f0 rail actually ran
    (stats.f0_mode used to echo the REQUEST even after a fallback — a lie), per-frame
    RMS, the singer's register center, and the octave-court run flags."""
    import pyworld as pw
    f0, t = pw.harvest(y, fs, f0_floor=60.0, f0_ceil=1300.0, frame_period=FRAME_MS)
    used, note = "harvest", ""
    if f0_mode == "consensus":
        f0c, used, note = _f0_consensus(y, fs, t, f0)
        if f0c is not None and (f0c > 0).sum() >= 8:
            f0 = f0c
        else:
            used = "harvest"
            note = note or "consensus found no voice — harvest fallback"
        if note:
            print(f"[retune] {note}")
    elif f0_mode in ("fcpe", "crepe"):
        try:
            f0n = _f0_neural(y, fs, t, f0_mode)
            if (f0n > 0).sum() >= 8:
                f0, used = f0n, f0_mode
            else:
                note = f"{f0_mode} found no voice — harvest fallback"
                print(f"[retune] {note}")
        except Exception as e:
            note = f"{f0_mode} unavailable ({type(e).__name__}) — harvest fallback"
            print(f"[retune] {note}: {e}")
    f0 = octave_guard(f0)
    frame_rms = frame_energy(y, fs, len(f0))
    v_ref = float(np.percentile(frame_rms[f0 > 0], 90)) if (f0 > 0).any() else 1.0
    f0, run_flags, center = heal_octaves(f0, frame_rms, v_ref)
    sp = pw.cheaptrick(y, f0, t, fs)
    ap = pw.d4c(y, f0, t, fs)
    meta = {"f0_used": used, "f0_requested": f0_mode, "f0_note": note,
            "frame_rms": frame_rms, "v_ref": v_ref,
            "run_flags": run_flags, "center_midi": center}
    return f0, t, sp, ap, meta


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


def heal_octaves(f0, frame_rms, v_ref):
    """THE OCTAVE COURT (2026-07-13, "WHEN IT GOES TO LOWER AND HIGHER NOTES, ITS
    STILL OFF KEY!"): octave_guard folds LONE flips, but a SUSTAINED subharmonic
    lock (harvest at register extremes, breathy onsets) migrates the running median
    and sails through — then the Viterbi candidates (±3 st of the halved median) put
    the TARGET in the wrong octave and the tuner confidently lands garbage on a
    wrong-octave scale tone. Judge whole voiced RUNS against the singer's register
    center, on evidence only:
      - pulsed low run (high frame jitter, f0<110Hz, well below center) = vocal FRY:
        real periodicity, not an error — folding would mint a fake note. Flag "fry".
      - WEAK far run that folds home by whole octaves = detector halving/doubling on
        a breathy tail/onset. HEAL (shift the run's f0) + flag "healed±12".
      - STRONG far run: could be deliberate (a real octave drop is usually sung with
        intent) — never guess. Flag "octave?".
    The law downstream: healed runs tune normally; fry/octave? runs are HELD
    (passthrough — the singer's raw sound is never worse than a wrong correction)
    and the flag reaches the report so the agent SEES why.
    Returns (f0_healed, run_flags [(i0, i1, flag)], center_midi)."""
    v = f0 > 0
    if not v.any():
        return f0, [], 0.0
    f0 = f0.copy()
    midi = midi_of(np.where(v, f0, 1.0))
    strong = v & (frame_rms > v_ref * 10 ** (-20.0 / 20.0))
    center = float(np.median(midi[strong if strong.any() else v]))
    idx = np.flatnonzero(v)
    cuts = np.flatnonzero(np.diff(idx) > 1)
    runs = [(int(g[0]), int(g[-1]) + 1) for g in np.split(idx, cuts + 1)]
    plans = []
    for a, b in runs:
        if b - a < 5:                                   # <25ms: too short to judge
            continue
        m = float(np.median(midi[a:b]))
        d = m - center
        jit = float(np.median(np.abs(np.diff(midi[a:b]))))
        weak = float(np.median(frame_rms[a:b])) < v_ref * 10 ** (-26.0 / 20.0)
        if d < -8.0 and jit > 0.6 and float(np.median(f0[a:b])) < 110.0:
            plans.append((a, b, "fry", 0))
        elif abs(d) >= 7.0:
            shift = -12 * int(round(d / 12.0))
            if shift != 0 and abs(d + shift) <= 4.0 and weak and jit <= 0.6:
                plans.append((a, b, f"healed{'+' if shift > 0 else ''}{shift}", shift))
            else:
                plans.append((a, b, "octave?", 0))
    heals = [p for p in plans if p[3]]
    if len(heals) > max(3, int(len(runs) * 0.4)):       # center itself suspect:
        plans = [(a, b, "octave?" if s else f, 0)       # heal NOTHING, flag instead
                 for a, b, f, s in plans]
    flags = []
    for a, b, flag, shift in plans:
        if shift:
            f0[a:b] = f0[a:b] * (2.0 ** (shift / 12.0))
        flags.append((a, b, flag))
    return f0, flags, center


def event_flags(events, run_flags):
    """Map octave-court run flags onto note events (flag covering the event's majority)."""
    out = []
    for a, b in events:
        best, cover = "", 0
        for ra, rb, fl in run_flags:
            ov = min(b, rb) - max(a, ra)
            if ov > cover and ov * 2 > (b - a):
                best, cover = fl, ov
        out.append(best)
    return out


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


def group_notes(events, targets, reasons, correct_mask, ev_fl, midi, t, spans,
                frame_rms, v_ref, tgt_off=None):
    """THE NOTE COURT (2026-07-13, "the actual notes from the audio need to be clear
    as day"): correction EVENTS are style-granular by design (tpain's 35ms stairs ARE
    the sound) — but the agent was reading those fragments as "the notes" (466 rows,
    64% under 150ms, on untitled_43). Group adjacent gap-free events that share a
    target/verdict into MUSICAL notes; name each by its STABLE CORE (central 60% of
    frames when long enough — onset scoops and release falls stop biasing the name);
    carry a confidence and the octave-court flag. One row = one note a human
    producer would point at, to 128-MIDI precision."""
    groups = []
    for k, (a, b) in enumerate(events):
        if groups and groups[-1]["i1"] == a and groups[-1]["target"] == targets[k] \
           and groups[-1]["held"] == (not correct_mask[k]) and groups[-1]["flag"] == ev_fl[k]:
            groups[-1]["i1"] = b
            groups[-1]["k1"] = k
            groups[-1]["sub"] += 1
            continue
        groups.append({"i0": a, "i1": b, "k0": k, "k1": k, "target": targets[k],
                       "reason": reasons[k], "held": not correct_mask[k],
                       "flag": ev_fl[k], "sub": 1})
    rows = []
    for g in groups:
        a, b = g["i0"], g["i1"]
        seg = midi[a:b]
        core = seg[int(len(seg) * 0.2):max(int(len(seg) * 0.8), int(len(seg) * 0.2) + 1)] \
            if (b - a) * FRAME_MS >= 120.0 else seg
        cm = float(np.median(core))
        off = float(tgt_off[g["k0"]]) if tgt_off is not None else 0.0
        d0 = (cm - (g["target"] + off / 100.0)) * 100.0
        stability = max(0.0, 1.0 - float(np.std(core)))
        energy = min(1.0, float(np.median(frame_rms[a:b])) / (v_ref * 10 ** (-12.0 / 20.0)))
        register = 1.0 if not g["flag"] else 0.25
        sign = "+" if d0 >= 0 else ""
        row = {
            "t0": round(float(t[a]), 3), "t1": round(float(t[min(b, len(t) - 1)]), 3),
            "beat0": round(spans[g["k0"]][0], 3) if spans and spans[g["k0"]][0] is not None else None,
            "beat1": round(spans[g["k1"]][1], 3) if spans and spans[g["k1"]][0] is not None else None,
            "dur_ms": int(round((b - a) * FRAME_MS)),
            "sung": f"{midi_name(cm)}{sign}{d0:.0f}c" if abs(d0) >= 1 else midi_name(cm),
            "sung_midi": round(cm, 2),
            "target": int(g["target"]), "target_name": midi_name(g["target"]),
            "cents_moved": 0.0 if g["held"] else round(-d0, 1),
            "reason": g["reason"], "sub": g["sub"],
            "conf": round(0.35 * stability + 0.35 * energy + 0.3 * register, 2),
        }
        if g["flag"]:
            row["flag"] = g["flag"]
        if abs(off) >= 1.0:
            row["offset_cents"] = round(off, 1)
        rows.append(row)
    return rows, [(g["k0"], g["k1"]) for g in groups]


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


def build_curve(f0, events, targets, style, correct_mask, rng, ev_styles=None,
                tgt_off=None):
    """Corrected f0 array (WORLD grid). Uncorrected/unvoiced frames pass through.
    ev_styles: optional per-event style dicts (THE GRAPH MODE — a manual edit can
    carry its own amount/retune_ms/vibrato_keep/center_amt/drift_amt, vib_gen =
    (rate_hz, depth_cents, delay_ms) regenerates the vibrato outright, and
    max_move_st widens the ±7 st safety when the editor's intent is explicit).
    tgt_off: per-event target offset in CENTS (just intonation / offset_cents —
    the aim point is target + offset, e.g. a just major third at −13.7c).
    THE TRANSITION LAW (2026-07-14): a corrected note used to enter from the RAW
    pitch even when the PREVIOUS note's exit had been pulled elsewhere — an
    instant step at every note boundary. Contiguous corrected events now slew
    from the previous OUTPUT pitch (true retune-speed semantics: tpain's 3ms
    still yodels, natural's 90ms glides)."""
    out = f0.copy()
    midi = midi_of(np.where(f0 > 0, f0, 1.0))
    hop_s = FRAME_MS / 1000.0
    slow_k = int(150.0 / FRAME_MS) | 1
    prev_end, prev_out_last = -1, None
    for k, ((i0, i1), T, corr) in enumerate(zip(events, targets, correct_mask)):
        if not corr:
            prev_end, prev_out_last = i1, None
            continue
        st = ev_styles[k] if (ev_styles and ev_styles[k]) else style
        tau = max(st["retune_ms"], 1.0) / 1000.0
        aim = T + (float(tgt_off[k]) if tgt_off is not None else 0.0) / 100.0
        seg = midi[i0:i1]
        dev = (seg - aim) * 100.0                     # cents vs the aim point
        # THE MELODYNE SPLIT (2026-07-14 research): pros correct THREE things
        # independently — pitch CENTER (where the note sits: correct hard),
        # pitch DRIFT (slow intra-note wander, usually unintentional: correct
        # ~80%), pitch MODULATION (vibrato/trills, usually intentional: keep).
        slow = medfilt1(dev, slow_k)
        fast = dev - slow                             # modulation (vibrato)
        center = float(np.median(slow))               # the note's seat
        drift = slow - center                         # slow wander around it
        c_amt = float(st.get("center_amt", st["amount"]))
        d_amt = float(st.get("drift_amt", st["amount"]))
        walk = np.cumsum(rng.normal(0, 1, len(dev)))
        if np.std(walk) > 1e-6 and st["humanize"] > 0:
            walk = medfilt1(walk, 5)
            walk = walk / (np.std(walk) + 1e-9) * st["humanize"]
        else:
            walk = np.zeros(len(dev))
        if st.get("vib_gen"):
            # VIBRATO REGENERATION (research: rate 5–7 Hz, depth 40–70c natural,
            # onset-delayed, slightly irregular — a perfect sinusoid reads
            # synthetic, so the rate carries a ~3% slow wander)
            rate, depth, delay_ms = st["vib_gen"]
            tt = np.arange(len(dev)) * hop_s
            ramp = np.clip((tt - delay_ms / 1000.0) / 0.15, 0.0, 1.0)
            rj = medfilt1(np.cumsum(rng.normal(0, 1, len(dev))), 31)
            rj = 1.0 + 0.03 * rj / (np.std(rj) + 1e-9)
            # instantaneous rate INTEGRATES (sin(2π·rate·t·jitter) drifts sharp —
            # the selftest measured 12 Hz on an asked 6)
            phase = 2.0 * np.pi * rate * np.cumsum(rj) * hop_s
            mod = depth * ramp * np.sin(phase + float(rng.uniform(0, 2 * np.pi)))
        else:
            mod = st["vibrato_keep"] * fast
        cdev = (1.0 - c_amt) * center + (1.0 - d_amt) * drift + mod + walk
        entry_from = dev[0]
        if i0 == prev_end and prev_out_last is not None:
            entry_from = (prev_out_last - aim) * 100.0    # slew from the last OUTPUT
        g = np.exp(-(np.arange(len(dev)) * hop_s) / tau)
        cdev = cdev + g * (entry_from - cdev[0])      # continuous entry, then seat
        lim = float(st.get("max_move_st", 7.0))
        new_m = aim + np.clip(cdev, -700.0 * lim / 7.0, 700.0 * lim / 7.0) / 100.0
        new_m = np.clip(new_m, seg - lim, seg + lim)  # ± safety vs sung
        out[i0:i1] = np.where(f0[i0:i1] > 0, hz_of(new_m), 0.0)
        prev_end, prev_out_last = i1, float(new_m[-1])
    return out


def psola_channel(yc, fs, f0, f0_new, spans, ap_hf=None):
    """THE HILDEBRAND ENGINE (2026-07-14 research): Auto-Tune's own synthesis is
    pitch-synchronous granular — single-period grains re-emitted at the target
    rate; Melodyne edits notes the same time-domain way. TD-PSOLA is measured
    preferable to WORLD resynthesis for singing naturalness (WORLD full-band
    resynthesis was this rail's artifact source). Grains: 2 local periods,
    Hann-windowed, centered on waveform peaks (phase coherence); output marks
    walk at the CORRECTED period; the source pointer tracks output time
    (duration preserved); overlap-sum normalized (no COLA ripple). Only the
    splice spans are touched — everything else stays bit-exact original."""
    out = yc.copy()
    hop = int(fs * FRAME_MS / 1000.0)
    nfr = len(f0)
    wins = {}

    def period(arr, smp):
        v = arr[min(nfr - 1, max(0, smp // hop))]
        return (fs / v) if v > 0 else 0.0

    for s, e in spans:
        # ONE COHERENT MARK TRAIN per span (v1 snapped a peak per output grain
        # independently — adjacent grains carried arbitrary phase offsets: the
        # selftest measured +25c error and ADDED wobble. The reference method
        # marks the whole train first, then respaces it.)
        marks = []
        m = float(s)
        while m < e:
            Po = period(f0, int(m))
            if Po <= 0:
                m += hop
                continue
            c, q = int(m), max(2, int(Po // 4))
            a, b = max(0, c - q), min(len(yc), c + q + 1)
            if b - a > 3:
                c = a + int(np.argmax(np.abs(yc[a:b])))
            if not marks or c > marks[-1]:    # monotonic train, never backwards
                marks.append(c)
            m = max(m + Po * 0.5, float(c) + Po)   # advance one true period
        if len(marks) < 2:
            continue
        marks_arr = np.array(marks, dtype=np.float64)
        seg = np.zeros(e - s)
        wsum = np.zeros(e - s)
        t = float(s)
        src_i = 0
        guard = 0
        while t < e and guard < 400000:
            guard += 1
            Pn, Po = period(f0_new, int(t)), period(f0, int(t))
            if Pn <= 0 or Po <= 0:
                t += hop
                continue
            # source mark: nearest to output time, monotonically advancing
            j = int(np.searchsorted(marks_arr, t))
            cand = [i for i in (j - 1, j) if 0 <= i < len(marks)]
            src_i = max(src_i, min(cand, key=lambda i: abs(marks[i] - t)) if cand else src_i)
            c = marks[min(src_i, len(marks) - 1)]
            half = int(Po)
            if half < 8 or c - half < 0 or c + half > len(yc):
                t += max(Pn, 8.0)
                continue
            if half not in wins:
                wins[half] = np.hanning(2 * half)
            w = wins[half]
            grain = yc[c - half:c + half] * w
            o0 = int(t) - s - half
            oa, ob = max(0, o0), min(e - s, o0 + 2 * half)
            if ob > oa:
                seg[oa:ob] += grain[oa - o0:ob - o0]
                wsum[oa:ob] += w[oa - o0:ob - o0]
            t += Pn
        landed = wsum > 0.25
        out[s:e] = np.where(landed, seg / np.maximum(wsum, 0.25), yc[s:e])
        # THE AIR BLEND (HNM research, 2026-07-14): PSOLA's known buzz lives in
        # BREATHY voiced frames — re-spaced grains correlate the aspiration
        # noise. HNM's answer: shift the harmonic part, keep the noise part.
        # Approximation: above 3.8 kHz, breathy frames (high WORLD HF
        # aperiodicity) keep the ORIGINAL air; clean frames keep the shifted
        # highs. Complementary split (hp = x − lp): perfect reconstruction.
        if ap_hf is not None and e - s > 400:
            w_fr = np.clip((ap_hf - 0.45) / 0.35, 0.0, 1.0)
            idx = np.minimum(len(ap_hf) - 1, np.arange(s, e) // hop)
            w_smp = w_fr[idx]
            if float(w_smp.max()) > 0.05:
                from scipy.signal import butter, sosfiltfilt
                sos_lp = butter(4, 3800.0 / (fs / 2.0), btype="low", output="sos")
                span_ps = out[s:e]
                lp_ps = sosfiltfilt(sos_lp, span_ps)
                hp_ps = span_ps - lp_ps
                hp_or = yc[s:e] - sosfiltfilt(sos_lp, yc[s:e])
                out[s:e] = lp_ps + hp_ps * (1.0 - w_smp) + hp_or * w_smp
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
            report_path=None, quiet=False, f0_mode="harvest", emit_midi_path=None,
            note_edits=None, only_edits=False, engine="psola", tuning="equal"):
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

    f0, t, sp, ap, f0meta = detect_world(y, fs, f0_mode=f0_mode)
    frame_rms, v_ref = f0meta["frame_rms"], f0meta["v_ref"]
    # ghost-frame gate: an f0 with no energy under it is not a voice (breath clicks
    # and room rumble used to become "notes" and only get muted AFTER they voted)
    voiced = (f0 > 0) & (frame_rms > v_ref * 10 ** (-40.0 / 20.0))
    midi = midi_of(np.where(voiced, f0, 1.0))
    events = segment_notes(midi, voiced, style["split_cents"], style["min_note_ms"])
    med_midi = [float(np.median(midi[a:b])) for a, b in events]
    spans = None
    if beat_of:
        spans = [(beat_of(t[a]), beat_of(t[min(b, len(t) - 1)])) for a, b in events]
    elif ctx:
        spans = [(None, None)] * len(events)

    # THE HOLD COURT — BEFORE the Viterbi (2026-07-13): quiet/fry/octave-suspect
    # events used to enter the DP and drag real neighbors through the contour
    # cost (the -26 dB gate ran AFTER target choice, so garbage still voted).
    ev_fl = event_flags(events, f0meta["run_flags"])
    correct_mask = [True] * len(events)
    reasons = [""] * len(events)
    for k, (a, b) in enumerate(events):
        if float(np.median(frame_rms[a:b])) < v_ref * 10 ** (-26.0 / 20.0):
            correct_mask[k], reasons[k] = False, "held(quiet)"
        elif ev_fl[k] == "fry":
            correct_mask[k], reasons[k] = False, "held(fry)"
        elif ev_fl[k] == "octave?":
            correct_mask[k], reasons[k] = False, "held(octave?)"
    if region and len(region) == 2:
        lo, hi = float(region[0]), float(region[1])
        for k, (a, b) in enumerate(events):
            pos0, pos1 = (spans[k] if (spans and spans[k][0] is not None)
                          else (t[a], t[min(b, len(t) - 1)]))
            if not (pos1 > lo and pos0 < hi):
                correct_mask[k], reasons[k] = False, "held(region)"

    # Viterbi over the CORRECTABLE events only — contour links never cross garbage
    live = [k for k in range(len(events)) if correct_mask[k]]
    targets = [int(round(m)) for m in med_midi]
    if ctx and live:
        lt, lr = choose_targets([events[k] for k in live], [med_midi[k] for k in live],
                                ([spans[k] for k in live] if spans else None),
                                ctx, style, guide_notes)
        for j, k in enumerate(live):
            targets[k], reasons[k] = lt[j], lr[j]
    else:
        for k in live:
            reasons[k] = "nearest"
    # FLEX-TUNE (Antares craft, 2026-07-14 research): a note already seated inside
    # the tolerance zone is left completely raw — slides and scoops survive,
    # correction engages only where the singer actually strayed.
    flex = float(style.get("flex_cents", 0.0))
    if flex > 0:
        for k in live:
            if abs(med_midi[k] - targets[k]) * 100.0 <= flex:
                correct_mask[k] = False
                reasons[k] = f"held(in-tune<={flex:.0f}c)"

    # ADAPTIVE JUST INTONATION (2026-07-14 research, the barbershop law): chord
    # tones aim at pure ratios RELATIVE TO THE CHORD ROOT — M3 −13.7c, m3 +15.6c,
    # P5 +2c — the locked-chord sweetness 12-TET can't give. Opt-in (tuning=just),
    # applied only when the bar's root is actually known.
    tgt_off = [0.0] * len(events)
    if tuning == "just" and ctx is not None and spans:
        JI = {0: 0.0, 3: 15.6, 4: -13.7, 5: -2.0, 7: 2.0, 9: -15.6, 10: 17.6}
        for k in range(len(events)):
            if not correct_mask[k] or spans[k][0] is None:
                continue
            chord, bass = ctx.field_for_note(spans[k][0], spans[k][1])
            if bass is None or (targets[k] % 12) not in chord:
                continue
            iv = (targets[k] - bass) % 12
            if iv in JI:
                tgt_off[k] = JI[iv]

    # THE GRAPH MODE (2026-07-13, "the LLM will do the manual edits to perfection"):
    # per-note manual edits, addressed by the analyze map's beat0 (t0 seconds when
    # no grid). A manual verdict OVERRIDES the courts — the editor saw the flag and
    # decided — and may move further than auto's ±7 st safety. only_edits=True is
    # pure graph mode: nothing tunes except what the editor named.
    ev_styles = [None] * len(events)
    edits_applied, edits_unmatched = [], []
    if note_edits:
        rows0, kmap = group_notes(events, targets, reasons, correct_mask, ev_fl,
                                  midi, t, spans, frame_rms, v_ref, tgt_off=tgt_off)
        if only_edits:
            for k in range(len(events)):
                if correct_mask[k]:
                    correct_mask[k], reasons[k] = False, "held(manual-mode)"
        anchors = [(r["beat0"] if r["beat0"] is not None else r["t0"]) for r in rows0]
        tol = 0.3 if (spans and spans[0][0] is not None) else 0.08
        for ed in note_edits:
            try:
                at = float(ed.get("at"))
            except (TypeError, ValueError):
                edits_unmatched.append({**ed, "why": "no 'at'"})
                continue
            dists = [abs(a0 - at) for a0 in anchors]
            best = int(np.argmin(dists)) if dists else -1
            if best < 0 or dists[best] > tol:
                edits_unmatched.append({**ed, "why": f"no note within {tol} of {at}"})
                continue
            k0, k1 = kmap[best]
            if ed.get("hold"):
                for k in range(k0, k1 + 1):
                    correct_mask[k], reasons[k] = False, "edited(hold)"
                lab = "hold"
            else:
                T = parse_note_name(ed["target"]) if ed.get("target") is not None \
                    else targets[k0]
                if T is None or not (0 <= T <= 127):
                    edits_unmatched.append({**ed, "why": f"bad target {ed.get('target')!r}"})
                    continue
                st2 = dict(style)
                st2.update({kk: float(ed[kk]) for kk in
                            ("amount", "retune_ms", "vibrato_keep", "center_amt", "drift_amt")
                            if ed.get(kk) is not None})
                st2["max_move_st"] = 24.0
                st2["flex_cents"] = 0.0        # an explicit edit is intent — no zone
                if ed.get("offset_cents") is not None:
                    for k in range(k0, k1 + 1):
                        tgt_off[k] = float(ed["offset_cents"])
                vib = ed.get("vibrato")
                if isinstance(vib, dict):      # regenerate the note's vibrato outright
                    st2["vib_gen"] = (float(vib.get("rate", 5.5)),
                                      float(vib.get("depth", 55.0)),
                                      float(vib.get("delay_ms", 200.0)))
                for k in range(k0, k1 + 1):
                    targets[k], correct_mask[k] = T, True
                    reasons[k] = f"edited({midi_name(T)})"
                    ev_styles[k] = st2
                lab = midi_name(T)
            edits_applied.append({"at": at, "matched_beat0": rows0[best]["beat0"],
                                  "matched_t0": rows0[best]["t0"],
                                  "was": rows0[best]["sung"], "edit": lab})

    rng = np.random.default_rng(0xC0FFEE ^ len(y))
    f0_new = build_curve(f0, events, targets, style, correct_mask, rng, ev_styles,
                         tgt_off=tgt_off)

    rs_spans = splice_spans(f0, f0_new, fs, len(y)) if out_path else []
    resynth_smp = sum(e - s for s, e in rs_spans)
    if out_path:
        chans = []
        ap_hf = ap[:, ap.shape[1] // 3:].mean(axis=1)   # HF aperiodicity = breathiness
        for c in range(y_multi.shape[1]):
            yc = np.ascontiguousarray(y_multi[:, c], dtype=np.float64)
            if engine == "psola":
                shifted = psola_channel(yc, fs, f0, f0_new, rs_spans, ap_hf=ap_hf)
            else:
                import pyworld as pw
                spc = pw.cheaptrick(yc, f0, t, fs)
                apc = pw.d4c(yc, f0, t, fs)
                shifted = resynth(yc, fs, f0, spc, apc, f0_new)
            chans.append(splice(yc, shifted, rs_spans, fs))
        out = np.stack(chans, axis=1) if len(chans) > 1 else chans[0]
        # FLOAT DECK LAW: float inputs stay float (vocal_truth decks carry
        # sub-int16-LSB content; forcing PCM_16 truncated it to zero and made
        # passthrough spans non-bit-true). Unknown exotic subtypes -> PCM_16.
        keep = info.subtype.startswith("PCM") or "FLOAT" in info.subtype or "DOUBLE" in info.subtype
        # THE LIVE-APP STOMP LAW: a same-style re-tune targets the wav the UI is
        # already playing (clip file == _tuned_<stem>_<style>.wav) — writing it in
        # place truncates under the engine's memory map (audio-thread SEGV, the
        # 2026-07-12 sing crash class). Land atomically: new inode, old map lives.
        _tmp_out = out_path + ".w~.wav"
        sf.write(_tmp_out, out, fs, subtype=info.subtype if keep else "PCM_16")
        os.replace(_tmp_out, out_path)

    # report v2: rows = THE NOTE COURT's musical notes (fragment truth in stats)
    moved = [abs((med_midi[k] - targets[k]) * 100.0)
             for k in range(len(events)) if correct_mask[k]]
    notes_rep, _ = group_notes(events, targets, reasons, correct_mask, ev_fl,
                               midi, t, spans, frame_rms, v_ref, tgt_off=tgt_off)
    held = [r for r in notes_rep if r["cents_moved"] == 0.0 and r["reason"].startswith("held")]
    rep = {
        "tool": "retune", "version": 2, "style": style_name,
        "params": {k: style[k] for k in ("amount", "retune_ms", "vibrato_keep", "humanize")},
        "input": in_path, "output": out_path, "song": song_path, "track": track,
        "scale": {"name": ctx.scale_name(), "source": getattr(ctx, "scale_src", "arg")} if ctx else None,
        "notes": notes_rep,
        "stats": {"notes": len(notes_rep), "fragments": len(events),
                  "corrected": int(sum(correct_mask)),
                  "held": {r: sum(1 for x in held if x["reason"] == f"held({r})")
                           for r in ("quiet", "fry", "octave?", "region")},
                  "healed_runs": sum(1 for _, _, f in f0meta["run_flags"]
                                     if f.startswith("healed")),
                  "register_center": round(f0meta["center_midi"], 1),
                  "register_center_name": midi_name(f0meta["center_midi"]),
                  "median_abs_cents_off": round(float(np.median(moved)), 1) if moved else 0.0,
                  "max_abs_cents_off": round(float(np.max(moved)), 1) if moved else 0.0,
                  "f0_mode": f0meta["f0_used"], "f0_requested": f0meta["f0_requested"],
                  "f0_note": f0meta["f0_note"], "engine": engine, "tuning": tuning,
                  "resynth_pct": round(100.0 * resynth_smp / max(len(y), 1), 1),
                  "passthrough_pct": round(100.0 - 100.0 * resynth_smp / max(len(y), 1), 1)},
    }
    if note_edits is not None:
        rep["edits_applied"] = edits_applied
        rep["edits_unmatched"] = edits_unmatched
    if report_path:
        json.dump(rep, open(report_path, "w"), indent=1)
    if emit_midi_path:
        # the detected melody AS NOTES (and the tuner's targets beside it) — beats
        # when the song grid is known, else seconds in start_s/len_s
        det, tgt = [], []
        for r in notes_rep:
            vel = round(min(1.0, 0.35 + 0.65 * r["conf"]), 2)
            if r["beat0"] is not None:
                base = {"start": r["beat0"], "len": round(max(r["beat1"] - r["beat0"], 0.05), 3), "vel": vel}
            else:
                base = {"start_s": r["t0"], "len_s": round(max(r["t1"] - r["t0"], 0.02), 3), "vel": vel}
            det.append({**base, "pitch": int(round(r["sung_midi"]))})
            tgt.append({**base, "pitch": r["target"]})
        json.dump({"tool": "retune", "version": 2, "input": in_path,
                   "detected": det, "targets": tgt}, open(emit_midi_path, "w"), indent=1)
    if not quiet:
        sc = f" scale={ctx.scale_name()}({getattr(ctx, 'scale_src', 'arg')})" if ctx else ""
        st = rep["stats"]
        print(f"[retune] {os.path.basename(in_path)} style={style_name}{sc} "
              f"notes={st['notes']} (fragments={st['fragments']}) corrected={st['corrected']} "
              f"median_off={st['median_abs_cents_off']}c f0={st['f0_mode']} "
              f"register={st['register_center_name']}")
        for nr in notes_rep[:40]:
            bb = f"b{nr['beat0']:.2f}" if nr["beat0"] is not None else f"{nr['t0']:.2f}s"
            fl = f" [{nr['flag']}]" if nr.get("flag") else ""
            print(f"  {bb:>8} {nr['sung']:>9} -> {nr['target_name']:<4} "
                  f"({nr['cents_moved']:+.0f}c) {nr['reason']}{fl}")
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

    # ---- THE NOTE COURT legs (2026-07-13, "notes clear as day / 128-note precision")
    # clean singer stays untouched by the octave court (over-healing regression)
    if rep["stats"]["healed_runs"] != 0 or rep["stats"]["held"]["fry"] != 0:
        fails.append(f"clean singer got courted: {rep['stats']['healed_runs']} heals, "
                     f"{rep['stats']['held']['fry']} fry")
    if rep["version"] != 2 or rep["stats"]["notes"] > rep["stats"]["fragments"]:
        fails.append("report v2 shape wrong")

    # heal_octaves unit: sustained halved run heals home; fry flagged, never folded
    fr = np.concatenate([np.full(200, 220.0),          # A3 body (center)
                         np.zeros(5),
                         np.full(100, 110.0),          # sustained HALVED run (weak)
                         np.zeros(5),
                         55.0 * 2 ** (np.tile([0.0, 1.4], 30) / 12.0)])  # pulsed fry
    rms = np.concatenate([np.full(200, 0.30), np.zeros(5), np.full(100, 0.004),
                          np.zeros(5), np.full(60, 0.004)])
    healed, rfl, center = heal_octaves(fr, rms, 0.30)
    if not (56.0 < center < 58.5):
        fails.append(f"octave court: center {center:.1f} not ~A3")
    if abs(float(np.median(healed[205:305])) - 220.0) > 1.0:
        fails.append("octave court: halved run NOT healed to 220Hz")
    if not any(f.startswith("healed") for _, _, f in rfl):
        fails.append("octave court: no healed flag")
    if not any(f == "fry" for _, _, f in rfl):
        fails.append("octave court: fry not flagged")
    if abs(float(np.median(healed[310:370])) - float(np.median(fr[310:370]))) > 1.0:
        fails.append("octave court: fry was FOLDED (must stay raw)")

    # group_notes unit: same-target gap-free stairs merge into ONE note (sub counts)
    gm = np.full(30, 60.2)
    g_rows, g_kmap = group_notes([(0, 10), (10, 20), (20, 30)], [60, 60, 62],
                                 ["scale(x)", "scale(x)", "scale(x)"], [True, True, True],
                                 ["", "", ""], gm, np.arange(30) * FRAME_MS / 1000.0,
                                 None, np.full(30, 0.3), 0.3)
    if g_kmap != [(0, 1), (2, 2)]:
        fails.append(f"note court: kmap wrong {g_kmap}")
    if len(g_rows) != 2 or g_rows[0]["sub"] != 2 or g_rows[1]["sub"] != 1:
        fails.append(f"note court: merge wrong ({[(r['target'], r['sub']) for r in g_rows]})")
    if not (0.0 <= g_rows[0]["conf"] <= 1.0 and g_rows[0]["dur_ms"] == 100):
        fails.append("note court: conf/dur wrong")

    # analyze mode: EARS ONLY — no wav written, report still lands whole
    an_rep_p = os.path.join(tmpdir, "_tune_selftest_analyze.json")
    an_midi_p = os.path.join(tmpdir, "_tune_selftest_melody.json")
    rep_a, *_ = process(wav, None, song_path=song_path, track="vox",
                        style_name="hard", quiet=True, report_path=an_rep_p,
                        emit_midi_path=an_midi_p)
    if rep_a["output"] is not None or not os.path.exists(an_rep_p):
        fails.append("analyze: output not None / report missing")
    mel = json.load(open(an_midi_p))
    if len(mel["detected"]) != rep_a["stats"]["notes"] or \
       not all(0 <= n["pitch"] <= 127 and "start" in n for n in mel["detected"]):
        fails.append("emit-midi: detected melody malformed")
    if rep_a["stats"]["notes"] < 7:
        fails.append(f"analyze: only {rep_a['stats']['notes']} notes heard (want >=7)")

    # f0 truth: a fallen neural rail must be REPORTED, not echoed as requested
    global _f0_neural
    _orig_neural = _f0_neural
    _f0_neural = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("rig: rail down"))
    try:
        rep_f, *_ = process(wav, None, song_path=song_path, track="vox",
                            style_name="hard", quiet=True, f0_mode="fcpe")
    finally:
        _f0_neural = _orig_neural
    if rep_f["stats"]["f0_mode"] != "harvest" or rep_f["stats"]["f0_requested"] != "fcpe" \
       or "fallback" not in rep_f["stats"]["f0_note"]:
        fails.append(f"f0 truth: {rep_f['stats']['f0_mode']}/{rep_f['stats']['f0_requested']}"
                     f"/{rep_f['stats']['f0_note']!r}")
    # parse_note_name: the editor's vocabulary
    if [parse_note_name(x) for x in ("A3", "C#5", "Bb2", 57, "H9")] != [57, 73, 46, 57, None]:
        fails.append("parse_note_name wrong")

    # THE GRAPH MODE: manual edits land where ASKED (measured), holds stay raw
    ed_out = os.path.join(tmpdir, "_tune_selftest_edit.wav")
    rep_e, f0_e, _fn, _te, ev_e, _tg = process(
        wav, ed_out, song_path=song_path, track="vox", style_name="hard", quiet=True,
        note_edits=[{"at": 1.0, "target": "F4"},        # push note 1 (auto D4) to F4
                    {"at": 3.0, "hold": True},          # leave note 3 (worst, +55c) RAW
                    {"at": 99.0, "target": "C4"}])      # ghost edit -> honest unmatched
    if len(rep_e["edits_applied"]) != 2 or len(rep_e["edits_unmatched"]) != 1:
        fails.append(f"graph mode: applied={len(rep_e['edits_applied'])} "
                     f"unmatched={len(rep_e['edits_unmatched'])}")
    if not any(r["reason"] == "edited(F4)" and r["target"] == 65 for r in rep_e["notes"]):
        fails.append("graph mode: F4 edit row missing")
    if not any(r["reason"] == "edited(hold)" for r in rep_e["notes"]):
        fails.append("graph mode: hold row missing")
    yo2 = sf.read(ed_out)[0]
    f0o, _t2 = pw.harvest(np.ascontiguousarray(yo2.astype(np.float64)), fs,
                          f0_floor=60, f0_ceil=1300, frame_period=FRAME_MS)
    def _land(ev):
        a2, b2 = ev[0] + int(60 / FRAME_MS), ev[1] - int(60 / FRAME_MS)
        seg = f0o[a2:b2]
        return float(np.median(midi_of(seg[seg > 0])))
    land1, land3 = _land(ev_e[1]), _land(ev_e[3])
    if abs(land1 - 65.0) > 0.25:
        fails.append(f"graph mode: asked F4(65), landed {land1:.2f}")
    a3, b3 = ev_e[3]
    sung3 = float(np.median(midi_of(f0_e[a3:b3][f0_e[a3:b3] > 0])))
    if abs(land3 - sung3) > 0.2 or abs(land3 - 67.0) < 0.3:
        fails.append(f"graph mode: hold leaked (landed {land3:.2f}, sung {sung3:.2f})")

    # engine truth + WORLD regression (psola is the new default: the style loop
    # above already proved psola's landings/vibrato/bit-exact gaps)
    if rep_e["stats"].get("engine") != "psola":
        fails.append(f"engine default not psola ({rep_e['stats'].get('engine')})")
    w_out = os.path.join(tmpdir, "_tune_selftest_world.wav")
    rep_w, _f0w, _fnw, _tw, ev_w, tg_w = process(
        wav, w_out, song_path=song_path, track="vox", style_name="tpain",
        quiet=True, engine="world")
    yo3 = sf.read(w_out)[0]
    f0w2, _t3 = pw.harvest(np.ascontiguousarray(yo3.astype(np.float64)), fs,
                           f0_floor=60, f0_ceil=1300, frame_period=FRAME_MS)
    errs_w = []
    for k in range(7):
        a2, b2 = ev_w[k][0] + int(60 / FRAME_MS), ev_w[k][1] - int(60 / FRAME_MS)
        segw = f0w2[a2:b2]
        segw = segw[segw > 0]
        if len(segw) >= 4:
            errs_w.append(abs(float(np.median(midi_of(segw))) - tg_w[k]) * 100.0)
    med_w = float(np.median(errs_w))
    if rep_w["stats"].get("engine") != "world" or med_w > 10.0:
        fails.append(f"world engine regression: {med_w:.1f}c")

    # THE CONSENSUS RAIL on the synth (both neural rails live in this venv)
    rep_c, *_ = process(wav, None, song_path=song_path, track="vox",
                        style_name="hard", quiet=True, f0_mode="consensus")
    c_tg = [r["target"] for r in rep_c["notes"]][:7]
    c_hit = sum(1 for x, y in zip(c_tg, intended) if x == y)
    if rep_c["stats"]["f0_mode"] != "consensus" or rep_c["stats"]["notes"] < 7 or c_hit < 5:
        fails.append(f"consensus: mode={rep_c['stats']['f0_mode']} "
                     f"notes={rep_c['stats']['notes']} first7hit={c_hit}")

    # ---- THE CRAFT LEGS (2026-07-14 round 3: JI, offsets, vibrato regen, transitions)
    # adaptive just intonation: the M3 over C aims −13.7c; the root aims true
    j_out = os.path.join(tmpdir, "_tune_selftest_just.wav")
    rep_j, f0_j, f0n_j, t_j, ev_j, tg_j = process(
        wav, j_out, song_path=song_path, track="vox", style_name="tpain",
        quiet=True, tuning="just")
    j_rows = rep_j["notes"]
    m3 = [r for r in j_rows if r["target"] == 64 and r.get("offset_cents") is not None]
    if not m3 or abs(m3[0]["offset_cents"] + 13.7) > 0.3:
        fails.append(f"JI: M3 offset row missing/wrong ({[r.get('offset_cents') for r in j_rows[:8]]})")
    if any(r["target"] == 60 and r.get("offset_cents") for r in j_rows):
        fails.append("JI: the root should carry no offset")
    if rep_j["stats"].get("tuning") != "just":
        fails.append("JI: stats.tuning missing")
    yoj = sf.read(j_out)[0]
    f0j2, _tj = pw.harvest(np.ascontiguousarray(yoj.astype(np.float64)), fs,
                           f0_floor=60, f0_ceil=1300, frame_period=FRAME_MS)
    def _land2(ev, arr):
        a2, b2 = ev[0] + int(60 / FRAME_MS), ev[1] - int(60 / FRAME_MS)
        seg2 = arr[a2:b2]
        return float(np.median(midi_of(seg2[seg2 > 0])))
    land_m3 = _land2(ev_j[2], f0j2)                    # beat-2 note: E4 over C
    if abs(land_m3 - (64.0 - 0.137)) > 0.12:
        fails.append(f"JI: M3 landed {land_m3:.3f}, want ~63.863")

    # THE TRANSITION LAW: contiguous corrected events slew from the previous
    # OUTPUT — no discontinuous step at note boundaries (the glide's tpain
    # stairs are the contiguous case)
    worst_step = 0.0
    for i in range(len(ev_j) - 1):
        if ev_j[i][1] != ev_j[i + 1][0]:
            continue
        b = ev_j[i + 1][0]
        if f0n_j[b - 1] > 0 and f0n_j[b] > 0 and \
           (abs(f0n_j[b - 1] - f0_j[b - 1]) > 1e-9 or abs(f0n_j[b] - f0_j[b]) > 1e-9):
            step = abs(float(midi_of(np.array([f0n_j[b]]))[0]
                             - midi_of(np.array([f0n_j[b - 1]]))[0]))
            worst_step = max(worst_step, step)
    if worst_step > 0.25:
        fails.append(f"transitions: boundary step {worst_step:.2f} st (want <=0.25)")

    # offset_cents per edit: asked C4+30c, must land there
    o_out = os.path.join(tmpdir, "_tune_selftest_off.wav")
    rep_o, _f1, _f2, _t4, ev_o, _t5 = process(
        wav, o_out, song_path=song_path, track="vox", style_name="hard", quiet=True,
        note_edits=[{"at": 0.0, "target": "C4", "offset_cents": 30.0}])
    yoo = sf.read(o_out)[0]
    f0o2, _to2 = pw.harvest(np.ascontiguousarray(yoo.astype(np.float64)), fs,
                            f0_floor=60, f0_ceil=1300, frame_period=FRAME_MS)
    land_off = _land2(ev_o[0], f0o2)
    if abs(land_off - 60.30) > 0.12:
        fails.append(f"offset edit: asked C4+30c, landed {land_off:.3f}")

    # vibrato regeneration: asked 6 Hz / 80c on note 4 — measure rate + extent
    v_out = os.path.join(tmpdir, "_tune_selftest_vib.wav")
    rep_v, _f3, _f4, _t6, ev_v, _t7 = process(
        wav, v_out, song_path=song_path, track="vox", style_name="hard", quiet=True,
        note_edits=[{"at": 4.0, "vibrato": {"rate": 6.0, "depth": 80.0}}])
    yov = sf.read(v_out)[0]
    f0v2, _tv2 = pw.harvest(np.ascontiguousarray(yov.astype(np.float64)), fs,
                            f0_floor=60, f0_ceil=1300, frame_period=FRAME_MS)
    a4, b4 = ev_v[4][0] + int(80 / FRAME_MS), ev_v[4][1] - int(40 / FRAME_MS)
    segv = f0v2[a4:b4]
    mv = midi_of(np.where(segv > 0, segv, 1.0))
    mv = mv[segv > 0] * 100.0
    # spectral rate estimate (zero-crossing counting on a median-detrended track
    # inflates the rate — the detrend window beats against the vibrato period)
    xv = mv - np.mean(mv)
    spv = np.abs(np.fft.rfft(xv * np.hanning(len(xv))))
    frv = np.fft.rfftfreq(len(xv), FRAME_MS / 1000.0)
    bandv = (frv >= 3.0) & (frv <= 10.0)
    rate_meas = float(frv[bandv][np.argmax(spv[bandv])]) if bandv.any() else 0.0
    fastv = mv - medfilt1(mv, 61)
    extent = float(np.percentile(fastv, 92) - np.percentile(fastv, 8))
    if not (4.8 <= rate_meas <= 7.2):
        fails.append(f"vibrato regen: rate {rate_meas:.1f}Hz (asked 6)")
    if not (90.0 <= extent <= 260.0):
        fails.append(f"vibrato regen: extent {extent:.0f}c (asked depth 80)")
    land_v = _land2(ev_v[4], f0v2)
    if abs(land_v - 64.0) > 0.35:
        fails.append(f"vibrato regen: note center drifted ({land_v:.2f} vs 64)")

    print(f"[selftest:craft] JI M3 -> {land_m3:.3f} (aim 63.863) · boundary step "
          f"{worst_step:.2f}st · offset edit -> {land_off:.3f} (aim 60.30) · "
          f"vibrato {rate_meas:.1f}Hz/{extent:.0f}c (asked 6Hz/80c)")

    print(f"[selftest:note-court] center={center:.1f} healed+fry flagged, "
          f"merge {[(r['target'], r['sub']) for r in g_rows]}, "
          f"analyze notes={rep_a['stats']['notes']} f0-truth OK")
    print(f"[selftest:graph-mode] F4 asked -> landed {land1:.2f}; hold stayed raw "
          f"({land3:.2f} = sung {sung3:.2f}); ghost edit refused. "
          f"consensus first7 {c_hit}/7 ({rep_c['stats']['f0_note'] or 'clean'})")

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
    ap.add_argument("--f0", default="harvest",
                    choices=["harvest", "fcpe", "crepe", "consensus"],
                    help="F0 rail: harvest (dry, default) | fcpe/crepe (neural) | "
                         "consensus (fcpe+crepe vote, harvest referee — the accuracy rail)")
    ap.add_argument("--tuning", default="equal", choices=["equal", "just"],
                    help="target tuning: equal (12-TET) | just (adaptive JI — chord "
                         "tones aim at pure ratios vs the chord root: M3 -13.7c, "
                         "m3 +15.6c, P5 +2c; the barbershop lock)")
    ap.add_argument("--engine", default="psola", choices=["psola", "world"],
                    help="synthesis engine: psola (pitch-synchronous grains — Auto-Tune's "
                         "own principle, superior singing naturalness, DEFAULT) | world "
                         "(full vocoder resynthesis, the legacy path)")
    ap.add_argument("--edits", help="THE GRAPH MODE: json file with per-note manual edits "
                                    "[{at: <beat0 from the analyze map>, target: 'A3'|57, "
                                    "hold: true, amount/retune_ms/vibrato_keep}]")
    ap.add_argument("--only-edits", action="store_true",
                    help="pure graph mode: ONLY the edited notes tune, everything else raw")
    ap.add_argument("--report", help="write per-note JSON report here")
    ap.add_argument("--analyze", action="store_true",
                    help="EARS ONLY: no audio written — the note map (sung vs target, "
                         "flags, confidence) prints + lands in the report json")
    ap.add_argument("--emit-midi", help="write the detected melody (and targets) as "
                                        "note lists to this json — lanes-ready")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        tmp = os.path.join(ROOT, "songs")
        sys.exit(selftest(tmp))
    if not a.input or (not a.output and not a.analyze):
        ap.error("input and output required (or --analyze / --selftest)")
    ov = dict(amount=a.strength, retune_ms=a.retune_ms,
              vibrato_keep=a.vibrato_keep, humanize=a.humanize_cents)
    out = None if a.analyze else a.output
    report = a.report or (os.path.splitext(out or a.input)[0] + ".report.json")
    edits = json.load(open(a.edits)) if a.edits else None
    process(a.input, out, song_path=a.song, track=a.track, style_name=a.style,
            overrides=ov, key=a.key, guide_track=a.guide_track, region=a.region,
            clip_index=a.clip_index, report_path=report, f0_mode=a.f0,
            emit_midi_path=a.emit_midi, note_edits=edits, only_edits=a.only_edits,
            engine=a.engine, tuning=a.tuning)
    print(f"[retune] wrote {(out + ' + ') if out else '(analyze only) '}{report}"
          + (f" + {a.emit_midi}" if a.emit_midi else ""))


if __name__ == "__main__":
    main()
