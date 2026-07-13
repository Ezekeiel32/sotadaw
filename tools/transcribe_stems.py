#!/usr/bin/env python3
"""STEM -> MIDI v2: per-stem SPECIALIST rails (the 'kosher' fix, 2026-07-06).

One generic polyphonic model (basic-pitch) for every stem was the bug: on a
Detroit 808 bass stem it transcribed 20 notes covering 0.8% of the active
audio (fundamentals at 30-60Hz sit under its floor), and on wet rap vocals it
covered 46% in confetti fragments. Measured on the real stems, per rail:

  bass    fcpe OCTAVE TRICK (claim sr=2x so 30Hz reads as 60Hz, halve the f0):
          99.4% voiced coverage, median f0 33.4Hz (=C1, pyin cross-witnessed).
          Direct fcpe: 96.6% but octave-blind at the floor. pyin: 46.7%, 66s.
  vocals  fcpe 60-1000Hz chunked: 87.3% coverage in 1.9s GPU (the retune.py
          law holds here too: harvest/basic-pitch drop 1/3 on reverb/bleed).
  drums   3-band onset LANES (kick<140 / snare 180-2000 / hat>5500) heard
          291/673/869 events where the old single 600-cap sketch kept 600
          total; tatum measured 0.125b (29ms residual) vs the old hard 0.25b
          snap (56ms) — half-time BPM detections made 1/16 snap eat hat rolls.
  other   basic-pitch IS the right tool for polyphony — tuned (fmin 55,
          onset 0.4, min-note 70ms) + midi_polish, chord-snapped upstream.

Segmentation (mono rails): voiced runs on a 10ms f0 grid, gated at -38..-40dB
vs stem peak; pitch splits need 3 consecutive frames >0.7-0.8 semitones from
the running median (vibrato/scoops survive, real moves split); librosa onsets
(backtracked) re-split same-pitch retriggers (repeated 808s, rap syllables);
micro-gaps bridge; velocities = per-note dB percentile-mapped. GPU->CPU
elastic (a training daemon may own the card — chunks fall back per-call).

Every public rail returns (notes, receipt) — receipt says engine, coverage,
and counts so the import log carries proof, not vibes.
"""
import math, os, sys
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

FPS = 100.0                       # f0/RMS analysis grid: 10ms frames
GATE_DB = 38.0                    # voiced frames must clear peak-GATE_DB

# ---------------------------------------------------------------- audio utils
def _load_mono(path):
    from scipy.io import wavfile
    sr, x = wavfile.read(path)
    if x.dtype.kind == "i":
        x = x.astype(np.float64) / np.iinfo(x.dtype).max
    else:
        x = x.astype(np.float64)
    if x.ndim > 1:
        x = x.mean(axis=1)
    return sr, x

def _bars_of(path, bpm):
    """Cheap duration -> bar count (no full decode). Caps SCALE with length:
    a cap tuned for a 2.5-min track silently truncated an 8-min one (every
    lane pinned at its ceiling). Notes-per-bar budget instead of a flat number."""
    try:
        import soundfile as sf
        info = sf.info(path)
        dur = info.frames / float(info.samplerate)
    except Exception:
        sr, x = _load_mono(path)
        dur = len(x) / sr
    return max(1.0, dur * bpm / 240.0)

def _rms_db_10ms(x, sr, n_frames):
    """RMS dB on the exact 10ms f0 grid (n_frames long)."""
    hop = int(sr / FPS)
    env = np.zeros(n_frames)
    for i in range(n_frames):
        seg = x[i * hop:(i + 1) * hop]
        env[i] = math.sqrt(float((seg ** 2).mean())) if len(seg) else 0.0
    return 20.0 * np.log10(env + 1e-9)

def _onset_frames(x, sr, min_gap_s=0.03):
    """Backtracked full-band onsets on the 10ms grid (re-attack witnesses)."""
    import librosa
    env = librosa.onset.onset_strength(y=x.astype(np.float32), sr=sr, hop_length=256)
    pk = np.percentile(env, 98) or 1.0
    on = librosa.onset.onset_detect(onset_envelope=env / pk, sr=sr, hop_length=256,
                                    units="time", backtrack=True,
                                    delta=0.05, wait=max(1, int(min_gap_s * sr / 256)))
    return sorted({int(round(t * FPS)) for t in on})

# ---------------------------------------------------------------- fcpe rail
_FCPE = {}

def _octave_guard(f0):
    """Fold lone octave flips onto the running median (the retune.py law —
    fcpe jumps octaves on growls/plosives; the melody doesn't)."""
    f0 = f0.copy()
    hist = []
    for i in range(len(f0)):
        v = float(f0[i])
        if v <= 0:
            continue
        if len(hist) >= 5:
            med = float(np.median(hist[-15:]))
            if med > 0 and abs(1200.0 * math.log2(v / med)) > 900.0:
                for mult in (2.0, 0.5):
                    if abs(1200.0 * math.log2(v / (med * mult))) < 150.0:
                        v = v / mult
                        f0[i] = v
                        break
        hist.append(v)
    return f0

def _crepe_f0(y16, f0_min, f0_max, sr_claim=16000, conf=0.40):
    """torchcrepe SECOND WITNESS on the shared 10ms grid. sr_claim=32000 = the
    same octave trick (crepe hop then lands every 20ms real; nearest-sample the
    result back onto the 10ms grid). Elastic: cuda full -> cuda tiny -> cpu tiny.
    Returns zeros on total failure — consensus then degrades to fcpe-only."""
    import torch, torchcrepe
    n_out = len(y16) // 160
    hop = 160 if sr_claim == 16000 else 320
    au = torch.from_numpy(y16).unsqueeze(0)
    f0 = None
    plans = ([("cuda", "full", 64), ("cuda", "tiny", 256)] if torch.cuda.is_available() else [])
    plans += [("cpu", "tiny", 512)]
    for dev, model, bs in plans:
        try:
            f0t, pd = torchcrepe.predict(au, sr_claim, hop, f0_min, f0_max, model,
                                         return_periodicity=True, device=dev,
                                         batch_size=bs)
            f0 = f0t.squeeze().cpu().numpy().astype(np.float64)
            p = pd.squeeze().cpu().numpy()
            f0[p < conf] = 0.0
            break
        except Exception:
            try:
                torch.cuda.empty_cache()
            except Exception:
                pass
    if f0 is None:
        return np.zeros(n_out)
    if sr_claim != 16000:
        f0 = f0 / 2.0
    step_real = hop / 16000.0
    idx = np.minimum((np.arange(n_out) * 0.010 / step_real).round().astype(int),
                     len(f0) - 1)
    return f0[idx]

def _consensus(f0_f, f0_c, agree_cents=50.0, stable_cents=30.0):
    """Dual-witness fusion: where fcpe and crepe AGREE (<=50c) keep fcpe (the
    proven wet-stem rail); fcpe-only frames survive only where fcpe is locally
    STABLE (frame jitter = hallucination, sustained pitch = music); crepe-only
    frames are dropped (fcpe is primary). Raises pitch truth without gutting
    coverage — the hearing-faculty locality law: each frame decides alone."""
    n = min(len(f0_f), len(f0_c))
    a, b = f0_f[:n], f0_c[:n]
    out = np.zeros(n)
    for i in range(n):
        if a[i] <= 0:
            continue
        if b[i] > 0 and abs(1200.0 * math.log2(a[i] / b[i])) <= agree_cents:
            out[i] = a[i]
            continue
        w = a[max(0, i - 2):i + 3]
        w = w[w > 0]
        med = float(np.median(w)) if len(w) else 0.0
        if med > 0 and abs(1200.0 * math.log2(a[i] / med)) <= stable_cents:
            out[i] = a[i]
    return out

def _fcpe_model(device):
    if device not in _FCPE:
        from torchfcpe import spawn_bundled_infer_model
        _FCPE[device] = spawn_bundled_infer_model(device=device)
    return _FCPE[device]

def _fcpe_f0(y16, f0_min, f0_max, sr_claim=16000):
    """Chunked fcpe on 16k mono float32. sr_claim=32000 = THE OCTAVE TRICK:
    the model resamples our 16k audio 2:1, everything reads +1 octave, so a
    30Hz 808 lands at 60Hz (inside the model's floor); caller halves the f0.
    30s windows, 0.5s left-overlap, per-chunk GPU->CPU OOM fallback."""
    import torch
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    hop = 160                                   # 10ms of REAL audio at 16k
    n_out = len(y16) // hop
    f0 = np.zeros(n_out)
    win, ov = 30 * 16000, 8000
    i = 0
    while i < len(y16):
        seg = y16[max(0, i - ov):i + win]
        pre = min(i, ov)
        nfr = len(seg) // hop
        for attempt in (dev, "cpu"):
            try:
                model = _fcpe_model(attempt)
                au = torch.from_numpy(seg).unsqueeze(0).unsqueeze(-1).to(attempt)
                out = model.infer(au, sr=sr_claim, decoder_mode="local_argmax",
                                  threshold=0.006, f0_min=f0_min, f0_max=f0_max,
                                  interp_uv=False,
                                  output_interp_target_length=nfr
                                  ).squeeze().cpu().numpy()
                dev = attempt
                break
            except Exception:
                if attempt == "cpu":
                    raise
                try:
                    torch.cuda.empty_cache()
                except Exception:
                    pass
        a = i // hop
        seg_out = out[pre // hop:]
        f0[a:a + len(seg_out)] = seg_out[:max(0, n_out - a)]
        i += win
    return f0, dev

# ---------------------------------------------------------------- segmentation
def _segment(f0_hz, db, bpm, min_note_s=0.07, bridge_s=0.06, split_semis=0.8,
             onset_frames=(), gate_db=GATE_DB, fold_lo=None, fold_hi=None):
    """Voiced f0 frames -> note dicts {start,len,pitch,vel} in beats."""
    peak = float(db.max())
    n = min(len(f0_hz), len(db))
    midi = np.zeros(n)
    m = f0_hz[:n] > 0
    midi[m] = 69.0 + 12.0 * np.log2(f0_hz[:n][m] / 440.0)
    voiced = m & (db[:n] > peak - gate_db)
    # 5-frame median smooth inside voiced runs (kills single-frame octave blips)
    sm = midi.copy()
    for i in range(n):
        if voiced[i]:
            a, b = max(0, i - 2), min(n, i + 3)
            vals = midi[a:b][voiced[a:b]]
            if len(vals):
                sm[i] = float(np.median(vals))
    bridge_f = int(round(bridge_s * FPS))
    min_f = max(2, int(round(min_note_s * FPS)))

    segs, i = [], 0
    while i < n:
        if not voiced[i]:
            i += 1
            continue
        member = [i]
        j = i
        while j + 1 < n:
            k = j + 1
            med = float(np.median(sm[member[-12:]]))
            if voiced[k]:
                if abs(sm[k] - med) > split_semis:
                    # real move only if it HOLDS ~3 frames (vibrato survives)
                    ahead = [sm[t] for t in range(k, min(n, k + 3)) if voiced[t]]
                    if len(ahead) >= 2 and all(abs(v - med) > split_semis for v in ahead):
                        break
                member.append(k)
                j = k
                continue
            g = k
            while g < n and not voiced[g] and (g - k) < bridge_f:
                g += 1
            if g < n and voiced[g] and abs(sm[g] - med) <= split_semis:
                j = g                          # bridged: continue the same note
                member.append(g)
                continue
            break
        segs.append(member)
        i = j + 1

    # onset re-attacks: same-pitch retriggers (808 restrikes, rap syllables)
    if onset_frames:
        cut = []
        for mem in segs:
            s0, s1 = mem[0], mem[-1]
            splits = [f for f in onset_frames if s0 + min_f <= f <= s1 - min_f]
            if not splits:
                cut.append(mem)
                continue
            last = s0
            for f in splits + [s1 + 1]:
                part = [t for t in mem if last <= t < f]
                if len(part) >= min_f:            # short heads merge into the
                    cut.append(part)              # next part (last stays put)
                    last = f
        segs = cut

    notes = []
    for mem in segs:
        if len(mem) < min_f:
            continue
        pitch = int(round(float(np.median(sm[mem]))))
        if fold_lo is not None:
            while pitch < fold_lo:
                pitch += 12
            while pitch > fold_hi:
                pitch -= 12
        t0, t1 = mem[0] / FPS, (mem[-1] + 1) / FPS
        loud = float(np.percentile(db[mem], 90))
        vel = min(1.0, max(0.0, (loud - (peak - 36.0)) / 36.0))
        spb = 60.0 / bpm
        notes.append({"start": round(t0 / spb, 4),
                      "len": round(max(0.05, (t1 - t0) / spb), 4),
                      "pitch": max(0, min(127, pitch)),
                      "vel": round(max(0.2, vel), 3)})
    return notes

def _coverage(notes, db, bpm, gate_db=35.0):
    """Fraction of loud frames (peak-gate) lying under some note span."""
    peak = float(db.max())
    active = db > peak - gate_db
    if not active.any():
        return 1.0
    spb = 60.0 / bpm
    cov = np.zeros(len(db), bool)
    for nte in notes:
        a = int(nte["start"] * spb * FPS)
        b = int((nte["start"] + nte["len"]) * spb * FPS) + 1
        cov[max(0, a):min(len(db), b)] = True
    return float(cov[active].mean())

def _mono_polish(notes, bpm):
    """NO grid quantize here — the imported grid can sit a constant phase off
    the music (video-rip t=0 != beat 1; measured ~29ms on the kosher stems),
    and a replica's notes belong where the AUDIO is, not on an ideal ruler."""
    import midi_polish
    ns = midi_polish.merge_fragments(notes, gap=0.08)
    ns = midi_polish.enforce_mono(ns, min_len=0.04)
    ns = midi_polish.collapse_dups(ns)
    ns = midi_polish.spread_velocity(ns)
    for nte in ns:
        nte["start"] = round(nte["start"], 4)
        nte["len"] = round(nte["len"], 4)
        nte["vel"] = round(nte["vel"], 3)
    return ns

# ---------------------------------------------------------------- public rails
def bass_notes(path, bpm):
    """808/bass rail v3: fcpe octave trick + octave guard + CREPE consensus,
    finer glide chains (0.55 semi), re-attack splits."""
    import librosa
    sr, x = _load_mono(path)
    y16 = librosa.resample(x, orig_sr=sr, target_sr=16000).astype(np.float32)
    f0, dev = _fcpe_f0(y16, f0_min=48.0, f0_max=520.0, sr_claim=32000)
    f0 = _octave_guard(f0 / 2.0)               # undo the octave trick, fold flips
    f0c = _crepe_f0(y16, 48.0, 520.0, sr_claim=32000)
    fused = _consensus(f0, f0c)
    agree = round(float((fused > 0).sum() / max(1, (f0 > 0).sum())), 3)
    db = _rms_db_10ms(x, sr, len(fused))
    ons = _onset_frames(x, sr, min_gap_s=0.06)
    notes = _segment(fused, db, bpm, min_note_s=0.09, bridge_s=0.08,
                     split_semis=0.55, onset_frames=ons, gate_db=40.0,
                     fold_lo=22, fold_hi=55)
    notes = _mono_polish(notes, bpm)
    rec = {"engine": f"fcpe-octave+crepe:{dev}", "notes": len(notes),
           "consensus_kept": agree,
           "coverage": round(_coverage(notes, db, bpm), 3)}
    return notes, rec

def vocal_notes(path, bpm):
    """Vocal rail v3: fcpe + octave guard + CREPE consensus, rap-tuned
    segmentation with finer melisma chains (0.6 semi)."""
    import librosa
    sr, x = _load_mono(path)
    y16 = librosa.resample(x, orig_sr=sr, target_sr=16000).astype(np.float32)
    f0, dev = _fcpe_f0(y16, f0_min=60.0, f0_max=1000.0)
    f0 = _octave_guard(f0)
    f0c = _crepe_f0(y16, 60.0, 1000.0)
    fused = _consensus(f0, f0c)
    agree = round(float((fused > 0).sum() / max(1, (f0 > 0).sum())), 3)
    db = _rms_db_10ms(x, sr, len(fused))
    ons = _onset_frames(x, sr, min_gap_s=0.05)
    notes = _segment(fused, db, bpm, min_note_s=0.06, bridge_s=0.05,
                     split_semis=0.6, onset_frames=ons, gate_db=38.0,
                     fold_lo=36, fold_hi=89)
    notes = _mono_polish(notes, bpm)
    rec = {"engine": f"fcpe+crepe:{dev}", "notes": len(notes),
           "consensus_kept": agree,
           "coverage": round(_coverage(notes, db, bpm), 3)}
    return notes, rec

def vocal_chops(path, bpm, voiced_notes, min_events=8):
    """THE OTHER HALF OF THE FLOW: unvoiced consonant hits (onsets that live
    OUTSIDE every voiced note span) as a percussive lane — pitch-MIDI cannot
    say 's/t/k', but the RHYTHM is performance information. GM 39 events."""
    sr, x = _load_mono(path)
    n_frames = int(len(x) / sr * FPS)
    db = _rms_db_10ms(x, sr, n_frames)
    peak = float(db.max())
    ons = _onset_frames(x, sr, min_gap_s=0.05)
    spb = 60.0 / bpm
    spans = sorted((int(nte["start"] * spb * FPS) - 4,
                    int((nte["start"] + nte["len"]) * spb * FPS) + 4)
                   for nte in voiced_notes)
    notes = []
    for f in ons:
        if f >= n_frames or db[f] < peak - 30.0:
            continue
        if any(a <= f <= b for a, b in spans):
            continue
        vel = min(1.0, max(0.3, (db[f] - (peak - 30.0)) / 30.0))
        notes.append({"start": round(f / FPS / spb, 4),
                      "len": round(max(0.03, 0.05 / spb), 4),
                      "pitch": 39, "vel": round(vel, 3)})
    return notes if len(notes) >= min_events else []

def _uncovered_spans(notes, db, bpm, gate_db=35.0, min_s=0.7):
    """Loud spans no note covers — where the first pass went deaf."""
    peak = float(db.max())
    active = db > peak - gate_db
    spb = 60.0 / bpm
    cov = np.zeros(len(db), bool)
    for nte in notes:
        a = int(nte["start"] * spb * FPS)
        b = int((nte["start"] + nte["len"]) * spb * FPS) + 1
        cov[max(0, a):min(len(db), b)] = True
    hole = active & ~cov
    spans, i = [], 0
    while i < len(hole):
        if hole[i]:
            j = i
            while j + 1 < len(hole) and hole[j + 1]:
                j += 1
            if (j - i + 1) / FPS >= min_s:
                spans.append((i / FPS, (j + 1) / FPS))
            i = j + 1
        else:
            i += 1
    spans.sort(key=lambda ab: ab[0] - ab[1])           # longest first
    return spans

def other_notes(path, bpm, key=None, max_notes=None):
    """Harmonic rail v3: tuned basic-pitch + SALVAGE PASS — the biggest loud
    spans the first pass left uncovered get re-transcribed at lower thresholds
    (windowed second listen), then one merged polish. Cap SCALES with length
    (~14 notes/bar) so an 8-min comp isn't truncated to a 2.5-min budget."""
    import torch  # noqa: F401 — CUDA PRELOAD before basic_pitch (law: tools/stems_import.py)
    from basic_pitch.inference import predict
    import midi_polish
    spb = 60.0 / bpm
    if max_notes is None:
        max_notes = max(900, int(_bars_of(path, bpm) * 14))

    def events_to_notes(events, t_off=0.0, min_amp=0.10):
        out = []
        for ev in events:
            s, e, pitch, amp = ev[0] + t_off, ev[1] + t_off, int(ev[2]), float(ev[3])
            if e - s < 0.05 or amp < min_amp:
                continue
            out.append({"start": round(s / spb, 3),
                        "len": round(max(0.05, (e - s) / spb), 3),
                        "pitch": pitch, "vel": round(min(1.0, max(0.2, amp)), 2)})
        return out

    _, _, events = predict(path, onset_threshold=0.4, frame_threshold=0.3,
                           minimum_note_length=70, minimum_frequency=55.0)
    notes = midi_polish.polish(events_to_notes(events), role="melodic", bpm=bpm,
                               key=key, max_notes=max_notes, grid=0.125, tol=0.05)
    sr, x = _load_mono(path)
    db = _rms_db_10ms(x, sr, int(len(x) / sr * FPS))
    salvaged = 0
    holes = _uncovered_spans(notes, db, bpm)
    if holes:
        import soundfile as sf
        import tempfile
        tmp = os.path.join(tempfile.gettempdir(), f"_salvage_{os.getpid()}.wav")
        add = []
        for t0, t1 in holes[:8]:
            a = max(0, int((t0 - 0.15) * sr))
            b = min(len(x), int((t1 + 0.15) * sr))
            sf.write(tmp, x[a:b].astype(np.float32), sr)
            try:
                _, _, ev2 = predict(tmp, onset_threshold=0.3, frame_threshold=0.25,
                                    minimum_note_length=60, minimum_frequency=55.0)
            except Exception:
                continue
            add += events_to_notes(ev2, t_off=a / sr, min_amp=0.08)
        if os.path.exists(tmp):
            os.remove(tmp)
        if add:
            salvaged = len(add)
            notes = midi_polish.polish(notes + add, role="melodic", bpm=bpm,
                                       key=key, max_notes=max_notes,
                                       grid=0.125, tol=0.05)
    rec = {"engine": "basic-pitch(tuned+salvage)", "notes": len(notes),
           "salvaged": salvaged,
           "coverage": round(_coverage(notes, db, bpm), 3)}
    return notes, rec

def tatum_wants_double(drums_wav, bpm, min_events=64, occupancy=0.22):
    """HALF-TIME ALIAS DETECTOR: True when a meaningful share of strong drum
    onsets OCCUPY the odd 1/32 cells of the detected grid (phase-corrected) —
    i.e. the music's real 1/16 lattice is twice as fine as the detected bpm's
    (Detroit 69.8 -> 139.6). A genuinely slow track leaves those cells empty."""
    import librosa
    sr, x = _load_mono(drums_wav)
    peak = float(np.max(np.abs(x)) or 1.0)
    env = librosa.onset.onset_strength(y=(x / peak).astype(np.float32), sr=sr,
                                       hop_length=256)
    pk = float(np.percentile(env, 98)) or 1.0
    on = librosa.onset.onset_detect(onset_envelope=env / pk, sr=sr, hop_length=256,
                                    units="time", backtrack=False, delta=0.07, wait=3)
    if len(on) < min_events:
        return False
    spb = 60.0 / bpm
    beats = np.array(on) / spb
    grid = 0.125
    ang = 2 * np.pi * (beats % grid) / grid
    z = complex(np.cos(ang).sum(), np.sin(ang).sum())
    phase = (np.angle(z) % (2 * np.pi)) / (2 * np.pi) * grid if abs(z) > 1e-9 else 0.0
    rel = beats - phase
    on_lattice = np.abs(_wrap(rel, 0.125)) < 0.04
    odd_cell = np.abs(_wrap(rel - 0.125, 0.25)) < 0.04
    if on_lattice.sum() < min_events // 2:
        return False                                   # music isn't grid-quantized
    return float((on_lattice & odd_cell).sum() / max(1, on_lattice.sum())) >= occupancy

# ---------------------------------------------------------------- drums v3
GM = {"kick": 36, "snare": 38, "chat": 42, "ohat": 46, "perc": 39, "crash": 49,
      # drum-pieces rail additions (physical toms + ride; gm_drums has voices
      # for all four, so the stock-kit fallback can never leave them silent)
      "tomlo": 43, "tommid": 47, "tomhi": 50, "ride": 51}

# engine note lengths per GM (seconds; /spb at note build)
LEN_S = {36: 0.10, 38: 0.12, 42: 0.04, 46: 0.28, 39: 0.08, 49: 0.60,
         43: 0.32, 47: 0.28, 50: 0.24, 51: 0.40}

def _wrap(x, grid):
    """Signed distance to the nearest grid line."""
    return (x + grid / 2) % grid - grid / 2


def _finish_drum_notes(events, band_of, sr, bpm, max_notes, engine_prefix):
    """The proven drums post-pipeline (v4/v5 laws), shared by the band path
    and the drum-pieces path: GRID PHASE estimate -> tight snap (<=12ms) ->
    amplitude-true velocities against the lane CEILING -> dust floor ->
    midi_polish. events = [(t_s, strength, gm)]; band_of maps gm -> the
    signal its peaks are measured in (band or physical piece)."""
    spb = 60.0 / bpm
    # GRID PHASE: imported audio rarely puts beat 1 at t=0 — estimate the
    # constant offset as the strength-weighted circular mean of the onset
    # residuals, then snap AROUND that phase (notes stay where the audio is).
    beats = np.array([t / spb for t, _, _ in events])
    strengths = np.array([s for _, s, _ in events])
    grid = 0.125
    phase = 0.0
    if len(beats) >= 8:
        ang = 2 * np.pi * (beats % grid) / grid
        z = complex((strengths * np.cos(ang)).sum(), (strengths * np.sin(ang)).sum())
        if abs(z) > 1e-9:
            phase = (np.angle(z) % (2 * np.pi)) / (2 * np.pi) * grid
        r16 = float(np.median(np.abs(_wrap(beats - phase, 0.25))))
        r32 = float(np.median(np.abs(_wrap(beats - phase, 0.125))))
        grid = 0.25 if r16 <= r32 * 1.15 else 0.125
    # TIGHT SNAP LAW (v4): straighten only detection jitter (<=12ms) — a wider
    # tolerance (the old 0.04b = 26ms at 91bpm) both ERASED the record's
    # micro-feel and moved slice points off the attacks. Feel stays human,
    # tight tracks still come out grid-clean.
    tol = min(0.04, 0.012 / spb)

    # AMPLITUDE-TRUE VELOCITIES (v4, the engine law): the old onset-strength
    # percentile vels lied (a -32dBFS ghost wore vel 0.72 -> the source kit
    # baked the snare -28.8dB). Measure each hit's peak in its LANE BAND and
    # map through the sampler's measured dB law (vel = 1 + log10(pk/ref):
    # vel 1.0 = the lane's CEILING level, -6dB = 0.7, -19dB = 0.05). Events
    # below body-24dB (or -46dBFS absolute) are detection dust — dropped: they gave
    # the anxiety track 84 "open hats" whose real median level was -35dBFS.
    def _bpk(gm, t):
        sig = band_of[gm]
        a = max(0, int((t - 0.006) * sr))
        b2 = min(len(sig), int((t + 0.045) * sr))
        seg = sig[a:b2]
        return float(np.abs(seg).max()) if len(seg) else 0.0
    ev_pk = [(t, s, gm, _bpk(gm, t)) for t, s, gm in events]
    # CEILING LAW (v5, lockstep with source_kit's zone anchors): vel ref =
    # the lane's LOUDEST band peak (capped p95+9dB vs glitches) so vel 1.0 =
    # the record's biggest hit and NO real accent clamps (p95 anchoring
    # squashed the top 5% — the "non snappy" complaint). The dust floor
    # stays vs the p95 BODY (ceiling-24dB would eat real ghost notes).
    lane_ref = {}
    lane_body = {}
    for gm in set(g for _, _, g, _ in ev_pk):
        pks = [p for _, _, g, p in ev_pk if g == gm and p > 0]
        if pks:
            body = float(np.percentile(pks, 95))
            lane_body[gm] = body
            lane_ref[gm] = float(min(max(pks), body * 10.0 ** (9.0 / 20.0)))
    notes = []
    dust = 0
    for t, s, gm, pk in ev_pk:
        ref = lane_ref.get(gm, 0.0)
        body = lane_body.get(gm, 0.0)
        if ref <= 0 or pk < max(body * 10.0 ** (-24.0 / 20.0), 10.0 ** (-46.0 / 20.0)):
            dust += 1
            continue
        b = t / spb
        q = round((b - phase) / grid) * grid + phase
        if abs(b - q) <= tol:
            b = q
        v = min(1.0, max(0.05, 1.0 + math.log10(pk / ref)))
        notes.append({"start": round(b, 4), "len": round(max(0.03, LEN_S[gm] / spb), 4),
                      "pitch": gm, "vel": round(v, 3)})
    import midi_polish
    notes = midi_polish.collapse_dups(notes)
    notes = midi_polish.cap_by_salience(notes, max_notes)
    rec = {"engine": f"{engine_prefix} grid={grid}b vel=sampler-db",
           "grid_phase_ms": round(phase * spb * 1000.0, 1),
           "dust_dropped": dust,
           "notes": len(notes)}
    for nm, gm in GM.items():
        c = sum(1 for n in notes if n["pitch"] == gm)
        if c:
            rec[nm] = c
    return notes, rec


def _drum_piece_signals(path, sr, n, peak):
    """Physical piece signals via tools/drumsep (cached next to the stem).
    Returns (sigs dict name->mono float64 on the caller's normalized scale,
    hh_derived bool, mode str) or None -> caller keeps the band path."""
    try:
        import drumsep
        mode = drumsep.available()
        if mode is None:
            return None
        paths = drumsep.separate_cached(path)
    except Exception as e:
        print(f"[drums] pieces skipped ({e}) -> band lanes", flush=True)
        return None
    if not paths or "kick" not in paths:
        return None
    import soundfile as sf
    sigs = {}
    for nm, p in paths.items():
        y, psr = sf.read(p, always_2d=True)
        y = y.mean(axis=1)
        if psr != sr or abs(len(y) - n) > sr * 0.05:
            import scipy.signal as ss
            y = ss.resample(y, n)
        y = np.pad(y, (0, max(0, n - len(y))))[:n]
        sigs[nm] = y / peak
    hh_derived = False
    if "hh" not in sigs and "cymbals" in sigs:
        # demucs-fallback model has no hh piece: carve hats out of the
        # cymbals piece with the classic 5.5k highpass
        from scipy.signal import butter, sosfilt
        sigs["hh"] = sosfilt(butter(4, 5500.0 / (sr / 2), "high", output="sos"),
                             sigs["cymbals"])
        hh_derived = True
    return sigs, hh_derived, mode


def _drum_notes_pieces(sigs, hh_derived, mode, sr, bpm, max_notes):
    """Drum rail v6 — THE DRUM MICROSCOPE: lanes come from PHYSICAL piece
    stems (mdx23c drumsep), not butterworth bands. New truths the bands
    could never hear: a real TOMS lane (per-hit fundamental -> 43/47/50),
    hats and cymbals unconflated (ride 51 vs crash 49 by ring), layered
    hits unmasked. Bleed gates die (separation IS the gate); the shared
    post-pipeline (_finish_drum_notes) keeps every v4/v5 law."""
    import librosa
    hop = 256
    fps = sr / hop

    def lane(sig, min_gap_s, delta):
        pk_s = float(np.max(np.abs(sig)) or 0.0)
        if pk_s < 10.0 ** (-46.0 / 20.0):
            return []                              # silent piece: no events
        env = librosa.onset.onset_strength(y=sig.astype(np.float32), sr=sr,
                                           hop_length=hop)
        pk = float(np.percentile(env, 98)) or 1.0
        fr = librosa.onset.onset_detect(onset_envelope=env / pk, sr=sr,
                                        hop_length=hop, units="frames",
                                        backtrack=False, delta=delta,
                                        wait=max(1, int(min_gap_s * fps)))
        return [(f / fps, float(env[f] / pk)) for f in fr]

    z = np.zeros(1)
    kicks = lane(sigs.get("kick", z), 0.06, 0.06)
    snares = lane(sigs.get("snare", z), 0.05, 0.06)
    toms = lane(sigs.get("toms", z), 0.05, 0.06)
    hats = lane(sigs.get("hh", z), 0.024, 0.05)
    cyms = lane(sigs.get("cymbals", z), 0.08, 0.06)

    events = []
    for t, s in kicks:
        events.append((t, s, 36))
    for t, s in snares:
        events.append((t, s, 38))
    # toms: per-hit fundamental (dominant rFFT peak 50-400Hz in the 120ms
    # after the attack) bins low/mid/high — the gm_drums pitches
    tsig = sigs.get("toms", z)
    for t, s in toms:
        a = int(t * sr)
        seg = tsig[a:a + int(0.12 * sr)]
        gm = 47
        if len(seg) >= 512:
            S = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
            fr_hz = np.fft.rfftfreq(len(seg), 1.0 / sr)
            m = (fr_hz >= 50) & (fr_hz <= 400)
            if m.any() and S[m].max() > 0:
                f0 = float(fr_hz[m][int(np.argmax(S[m]))])
                gm = 43 if f0 < 105.0 else (47 if f0 < 150.0 else 50)
        events.append((t, s, gm))
    # open/closed hat by post-onset decay on the hh PIECE (no crash case —
    # cymbals are their own physical stem now)
    hsig = sigs.get("hh", z)
    nfr = len(hsig) // hop
    henv = np.sqrt((hsig[:nfr * hop].reshape(-1, hop) ** 2).mean(axis=1)) \
        if nfr else np.zeros(1)
    hats_sorted = sorted(hats)
    for idx, (t, s) in enumerate(hats_sorted):
        f = int(t * fps)
        e0 = float(henv[f:f + int(0.03 * fps) + 1].mean()) if f < len(henv) else 0.0
        a1 = f + int(0.06 * fps)
        b1 = f + int(0.16 * fps)
        e1 = float(henv[a1:b1].mean()) if a1 < len(henv) else 0.0
        nxt = hats_sorted[idx + 1][0] - t if idx + 1 < len(hats_sorted) else 9e9
        if e0 > 0 and (e1 > 0.55 * e0) and nxt > 0.14:
            events.append((t, s, 46))
        else:
            events.append((t, s, 42))
    # cymbals: ring past 250ms + room to breathe = crash, else ride. On the
    # derived-hh fallback a short cymbal event coincident with a hat IS the
    # hat (same signal highpassed) — skip the double-count.
    csig = sigs.get("cymbals", z)
    nfc = len(csig) // hop
    cenv = np.sqrt((csig[:nfc * hop].reshape(-1, hop) ** 2).mean(axis=1)) \
        if nfc else np.zeros(1)
    cyms_sorted = sorted(cyms)
    hat_ts = [t for t, _ in hats_sorted]
    for idx, (t, s) in enumerate(cyms_sorted):
        f = int(t * fps)
        e0 = float(cenv[f:f + int(0.03 * fps) + 1].mean()) if f < len(cenv) else 0.0
        a2 = f + int(0.25 * fps)
        b2 = f + int(0.50 * fps)
        e2 = float(cenv[a2:b2].mean()) if a2 < len(cenv) else 0.0
        nxt = cyms_sorted[idx + 1][0] - t if idx + 1 < len(cyms_sorted) else 9e9
        is_crash = e0 > 0 and e2 > 0.35 * e0 and nxt > 0.4
        if hh_derived and not is_crash and hat_ts and \
                min(abs(h - t) for h in hat_ts) < 0.02:
            continue
        events.append((t, s, 49 if is_crash else 51))

    if len(events) < 3:
        return None                            # separation came up empty: bands judge
    band_of = {36: sigs.get("kick", z), 38: sigs.get("snare", z),
               43: tsig, 47: tsig, 50: tsig,
               42: hsig, 46: hsig, 49: csig, 51: csig}
    return _finish_drum_notes(events, band_of, sr, bpm, max_notes,
                              f"drum-pieces:{mode}")


def drum_notes(path, bpm, max_notes=None):
    """Drum rail: THE DRUM MICROSCOPE first (physical kick/snare/toms/hh/
    cymbals piece stems via tools/drumsep -> per-piece onset lanes, toms and
    ride EXIST for the first time), band lanes v3 as the ever-present
    fallback (no models / SOTADAW_NO_DRUMSEP=1 / silent pieces).

    Band path v3: per-band onset LANES (simultaneous kick+hat survive),
    bleed gating, open/closed hat + CRASH by post-onset decay, a 2-5kHz PERC
    lane (the measured miss hole: snaps/rims/claps), 24ms hat gaps (1/64 rolls
    at 140 survive), adaptive tolerant snap around the measured GRID PHASE,
    velocities from lane strength. Cap SCALES with length (~30 hits/bar)."""
    import librosa
    from scipy.signal import butter, sosfilt
    sr, x = _load_mono(path)
    if max_notes is None:
        max_notes = max(2500, int(len(x) / sr * bpm / 240.0 * 30))
    peak = float(np.max(np.abs(x)) or 1.0)
    x = x / peak

    got = _drum_piece_signals(path, sr, len(x), peak)
    if got is not None:
        res = _drum_notes_pieces(got[0], got[1], got[2], sr, bpm, max_notes)
        if res is not None:
            return res
        print("[drums] pieces path empty -> band lanes", flush=True)

    hop = 256
    fps = sr / hop
    spb = 60.0 / bpm

    def lane(sig, min_gap_s, delta):
        env = librosa.onset.onset_strength(y=sig.astype(np.float32), sr=sr, hop_length=hop)
        pk = float(np.percentile(env, 98)) or 1.0
        fr = librosa.onset.onset_detect(onset_envelope=env / pk, sr=sr, hop_length=hop,
                                        units="frames", backtrack=False, delta=delta,
                                        wait=max(1, int(min_gap_s * fps)))
        return [(f / fps, float(env[f] / pk)) for f in fr], env / pk

    low = sosfilt(butter(4, 140.0 / (sr / 2), "low", output="sos"), x)
    mid = sosfilt(butter(4, [180.0 / (sr / 2), 2000.0 / (sr / 2)], "band", output="sos"), x)
    upmid = sosfilt(butter(4, [2000.0 / (sr / 2), 5000.0 / (sr / 2)], "band", output="sos"), x)
    high = sosfilt(butter(4, 5500.0 / (sr / 2), "high", output="sos"), x)
    kicks, _ = lane(low, 0.06, 0.06)
    snares, _ = lane(mid, 0.05, 0.06)
    percs, _ = lane(upmid, 0.05, 0.06)
    hats, _ = lane(high, 0.024, 0.05)

    # high-band RMS for open/closed hat decay
    nfr = (len(x) // hop)
    henv = np.sqrt((high[:nfr * hop].reshape(-1, hop) ** 2).mean(axis=1))

    # kick-bleed gate on the snare lane (the old law, kept)
    kt = [t for t, _ in kicks]
    ks = {t: s for t, s in kicks}
    sn_str = sorted(s for _, s in snares) or [0]
    p35 = sn_str[int(0.35 * (len(sn_str) - 1))]
    ht = [t for t, _ in hats]
    gated = []
    for t, s in snares:
        near_k = [k for k in kt if abs(k - t) < 0.025]
        if near_k and s < 1.15 * max(ks[k] for k in near_k):
            continue
        near_h = any(abs(h - t) < 0.02 for h in ht)
        if near_h and s < p35:                 # hat bleed masquerading as snare
            continue
        gated.append((t, s))
    snares = gated

    events = []                                # (t, strength, gm)
    for t, s in kicks:
        events.append((t, s, GM["kick"]))
    for t, s in snares:
        events.append((t, s, GM["snare"]))
    # perc lane: 2-5kHz hits that are NOT bleed from a neighbor lane's event
    others = sorted([t for t, _ in kicks] + [t for t, _ in snares] + [t for t, _ in hats])
    others = np.array(others) if others else np.array([9e9])
    for t, s in percs:
        if np.abs(others - t).min() < 0.015:
            continue
        events.append((t, s, GM["perc"]))
    hats_sorted = sorted(hats)
    for idx, (t, s) in enumerate(hats_sorted):
        f = int(t * fps)
        e0 = float(henv[f:f + int(0.03 * fps) + 1].mean()) if f < len(henv) else 0.0
        a1 = f + int(0.06 * fps)
        b1 = f + int(0.16 * fps)
        e1 = float(henv[a1:b1].mean()) if a1 < len(henv) else 0.0
        a2 = f + int(0.25 * fps)
        b2 = f + int(0.50 * fps)
        e2 = float(henv[a2:b2].mean()) if a2 < len(henv) else 0.0
        nxt = hats_sorted[idx + 1][0] - t if idx + 1 < len(hats_sorted) else 9e9
        if e0 > 0 and e2 > 0.35 * e0 and nxt > 0.4:
            events.append((t, s, GM["crash"]))          # rings past 250ms = cymbal
        elif e0 > 0 and (e1 > 0.55 * e0) and nxt > 0.14:
            events.append((t, s, GM["ohat"]))
        else:
            events.append((t, s, GM["chat"]))

    band_of = {36: low, 38: mid, 39: upmid, 42: high, 46: high, 49: high}
    return _finish_drum_notes(events, band_of, sr, bpm, max_notes, "band-lanes")

# ---------------------------------------------------------------- CLI
if __name__ == "__main__":
    import argparse, json
    ap = argparse.ArgumentParser()
    ap.add_argument("wav")
    ap.add_argument("--role", required=True, choices=["bass", "vocal", "other", "drums"])
    ap.add_argument("--bpm", type=float, required=True)
    ap.add_argument("--key", default=None)
    ap.add_argument("--json", default=None, help="write notes to this path")
    a = ap.parse_args()
    fn = {"bass": bass_notes, "vocal": vocal_notes, "drums": drum_notes,
          "other": lambda p, b: other_notes(p, b, key=a.key)}[a.role]
    notes, rec = fn(a.wav, a.bpm)
    print(f"[{a.role}] {rec}")
    lens = sorted(n["len"] for n in notes)
    if notes:
        print(f"  {len(notes)} notes, median len {lens[len(lens)//2]:.3f}b, "
              f"pitch {min(n['pitch'] for n in notes)}-{max(n['pitch'] for n in notes)}")
    if a.json:
        json.dump(notes, open(a.json, "w"))
        print(f"  -> {a.json}")
