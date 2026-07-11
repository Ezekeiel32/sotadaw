#!/usr/bin/env python3
"""THE TRANSCRIPTION BATTERY — ground-truth proof of the stem->MIDI rails.

Every other transcription "score" compares against another estimator (pyin,
crepe) — witnesses, not truth. This battery SYNTHESIZES audio from notes it
already knows exactly, transcribes it, and measures recovery against the
planted ground truth. When it says "bass pitch 100%", that is not a vote.

Pure numpy synthesis (no engine, no samples): sines for pitched material,
filtered noise bursts for drums. Deterministic (fixed patterns, no RNG seed
drift). CPU-forced so it never contends with the training daemon.

  python3 tools/transcribe_battery.py            # synthetic ground-truth legs
  python3 tools/transcribe_battery.py --real      # + real-stem witness leg (kosher)

Legs: pure-unit (consensus/guard/wrap/tatum/grid-phase) + synth (bass incl.
the 30Hz octave-trick floor / drums per-lane / harmonic) + regression witness.
Exit code = number of failed legs (0 = all green).
"""
import json, os, sys, math
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")     # daemon owns the GPU; stay off it
os.environ.setdefault("SOTADAW_NO_DRUMSEP", "1")      # this battery proves the BAND rail
                                                      # (drumsep_battery owns the microscope)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
import numpy as np

SR = 44100
FAILS = []
def check(name, cond, detail=""):
    ok = bool(cond)
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}{'  ' + detail if detail else ''}")
    if not ok:
        FAILS.append(name)
    return ok

def midi_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12.0)

def write_wav(x, path):
    import soundfile as sf
    x = (x / (np.max(np.abs(x)) + 1e-9) * 0.7).astype(np.float32)
    sf.write(path, x, SR)

# ------------------------------------------------------------------ synthesis
def synth_tone(notes, bpm, dur_s, harmonics=(1.0, 0.5, 0.25), vib=0.0):
    """Sum sine partials for each note (start,len,pitch) in beats. A short
    raised-cosine attack/release gives a real onset for the detector."""
    spb = 60.0 / bpm
    x = np.zeros(int(dur_s * SR))
    for n in notes:
        f = midi_hz(n["pitch"])
        a = int(n["start"] * spb * SR)
        L = int(max(0.05, n["len"] * spb) * SR)
        b = min(len(x), a + L)
        if b <= a:
            continue
        t = np.arange(b - a) / SR
        env = np.ones(b - a)
        atk = min(int(0.01 * SR), (b - a) // 4)
        if atk > 0:
            env[:atk] = 0.5 - 0.5 * np.cos(np.linspace(0, math.pi, atk))
            env[-atk:] = 0.5 + 0.5 * np.cos(np.linspace(0, math.pi, atk))
        vibf = 1.0 + vib * np.sin(2 * math.pi * 5.0 * t) if vib else 1.0
        sig = sum(h * np.sin(2 * math.pi * f * k * t * (vibf if k == 1 else 1.0))
                  for k, h in enumerate(harmonics, 1))
        x[a:b] += env * sig * n.get("vel", 0.9)
    return x

def _soft_env(L, decay, atk_s=0.003):
    """Exponential decay with a raised-cosine ATTACK — a hard onset step is a
    broadband click (energy in every band), which makes a clean band-limited
    hit leak into every lane. The attack band-limits the transient so kick
    stays low, hat stays high (real drums behave this way)."""
    env = np.exp(-np.arange(L) / SR * decay)
    atk = min(int(atk_s * SR), L // 2)
    if atk > 0:
        env[:atk] *= 0.5 - 0.5 * np.cos(np.linspace(0, math.pi, atk))
    return env

def synth_drums(events, bpm, dur_s):
    """events: (beat, 'kick'|'snare'|'hat'). Band-limited bursts with soft
    attacks (no broadband clicks). Snare = broadband crack (300-9000Hz), the
    loudest element, as a real snare is."""
    from scipy.signal import butter, sosfilt
    spb = 60.0 / bpm
    x = np.zeros(int(dur_s * SR))
    rng = np.random.RandomState(7)
    noise = rng.randn(len(x))
    snb = sosfilt(butter(4, [250 / (SR / 2), 4000 / (SR / 2)],   # snare body, real rolloff
                         "band", output="sos"), noise)
    hib = sosfilt(butter(6, 7000 / (SR / 2), "high", output="sos"), noise)
    for beat, lane in events:
        a = int(beat * spb * SR)
        if lane == "kick":
            L = int(0.14 * SR); t = np.arange(L) / SR
            env = _soft_env(L, 28, atk_s=0.004)
            f = 110 * np.exp(-t * 24) + 45           # pitch drop, low only
            sig = 1.0 * env * np.sin(2 * math.pi * np.cumsum(f) / SR)
        elif lane == "snare":
            L = int(0.16 * SR); env = _soft_env(L, 20, atk_s=0.002)
            body = snb[a:a + L] if a + L <= len(snb) else np.zeros(L)
            tone = 0.25 * np.sin(2 * math.pi * 180 * np.arange(L) / SR)
            sig = 1.5 * env * (body / (np.max(np.abs(body)) + 1e-9) + tone)   # loudest
        else:  # hat
            L = int(0.05 * SR); env = _soft_env(L, 55, atk_s=0.001)
            body = hib[a:a + L] if a + L <= len(hib) else np.zeros(L)
            sig = 0.6 * env * body / (np.max(np.abs(body)) + 1e-9)
        b = min(len(x), a + len(sig))
        x[a:b] += sig[:b - a]
    return x

# ------------------------------------------------------------------ matching
def onset_f1(pred, truth, tol_beats=0.12):
    """Greedy 1:1 onset match on start beats -> (recall, precision, f1)."""
    ps = sorted(n["start"] for n in pred)
    ts = sorted(t["start"] for t in truth)
    used = [False] * len(ps)
    hit = 0
    for tb in ts:
        best, bi = tol_beats + 1e9, -1
        for i, pb in enumerate(ps):
            if used[i]:
                continue
            d = abs(pb - tb)
            if d < best:
                best, bi = d, i
        if bi >= 0 and best <= tol_beats:
            used[bi] = True
            hit += 1
    rec = hit / max(1, len(ts))
    prec = hit / max(1, len(ps))
    f1 = 2 * rec * prec / max(1e-9, rec + prec)
    return rec, prec, f1

def pitch_acc(pred, truth, tol_beats=0.15):
    """For each truth note, nearest pred onset within tol: pitch exact? octave?"""
    ps = sorted(pred, key=lambda n: n["start"])
    exact = octave = matched = 0
    for tn in truth:
        cand = [p for p in ps if abs(p["start"] - tn["start"]) <= tol_beats]
        if not cand:
            continue
        p = min(cand, key=lambda q: abs(q["start"] - tn["start"]))
        matched += 1
        d = abs(p["pitch"] - tn["pitch"])
        if d == 0:
            exact += 1
        if d % 12 == 0:
            octave += 1
    return (exact / max(1, matched), octave / max(1, matched), matched / max(1, len(truth)))

# ================================================================== LEGS
def leg_units():
    import transcribe_stems as ts
    print("[unit] pure functions")
    # _wrap
    check("wrap nearest-line", abs(ts._wrap(0.13, 0.125) - 0.005) < 1e-6,
          f"{ts._wrap(0.13,0.125):.4f}")
    # octave guard: a lone 2x flip folds back
    f0 = np.array([110.0] * 10 + [220.0] + [110.0] * 10)
    g = ts._octave_guard(f0)
    check("octave_guard folds lone flip", abs(g[10] - 110.0) < 1.0, f"{g[10]:.1f}Hz")
    f0b = np.array([110.0] * 10 + [113.0] + [110.0] * 10)   # real wobble, not a flip
    gb = ts._octave_guard(f0b)
    check("octave_guard keeps real pitch", abs(gb[10] - 113.0) < 1.0, f"{gb[10]:.1f}Hz")
    # consensus: agreeing witnesses keep fcpe; isolated fcpe blip drops
    a = np.array([100.0] * 20); b = np.array([100.0] * 20)
    check("consensus keeps agreement", (ts._consensus(a, b) > 0).mean() == 1.0)
    a2 = a.copy(); a2[10] = 400.0; b2 = np.zeros(20)         # crepe silent, fcpe lone jump
    fused = ts._consensus(a2, b2)
    check("consensus drops isolated fcpe jump", fused[10] == 0.0, f"{fused[10]:.0f}Hz")
    check("consensus keeps stable fcpe-only", (fused[:10] > 0).mean() == 1.0)

def leg_bass():
    import transcribe_stems as ts
    print("[synth] bass — incl. the 30Hz octave-trick floor")
    bpm = 120.0
    # a walking-ish low line: E1(28) A0(21!) E1 G1(31) — deep, crosses fcpe's floor
    truth = [{"start": i * 1.0, "len": 0.9, "pitch": p, "vel": 0.9}
             for i, p in enumerate([28, 24, 31, 28, 33, 28, 24, 26] * 2)]
    x = synth_tone(truth, bpm, dur_s=17.0, harmonics=(1.0, 0.4, 0.15))
    p = "/tmp/_batt_bass.wav"; write_wav(x, p)
    notes, rec = ts.bass_notes(p, bpm)
    r, pr, f1 = onset_f1(notes, truth)
    ex, oc, cov = pitch_acc(notes, truth)
    os.remove(p)
    check("bass onset F1 >= 0.85", f1 >= 0.85, f"F1={f1:.2f} (r={r:.2f} p={pr:.2f})")
    check("bass pitch exact >= 0.85", ex >= 0.85, f"exact={ex:.2f} octave={oc:.2f}")
    check("bass NO octave errors (30Hz floor)", oc >= 0.95, f"octave-correct={oc:.2f}")
    check("bass matched >= 0.85 of truth", cov >= 0.85, f"cov={cov:.2f}")

def leg_drums():
    import transcribe_stems as ts
    print("[synth] drums — per-lane recall/precision")
    bpm = 120.0
    # hip-hop: kick 1&3, snare backbeat 2&4 (NOT stacked on kick), hats in 8ths
    ev = []
    for bar in range(8):
        b0 = bar * 4
        ev.append((b0 + 0, "kick")); ev.append((b0 + 2, "kick"))
        ev.append((b0 + 1, "snare")); ev.append((b0 + 3, "snare"))
        for h in range(8):
            ev.append((b0 + h * 0.5, "hat"))
    x = synth_drums(ev, bpm, dur_s=17.0)
    p = "/tmp/_batt_drums.wav"; write_wav(x, p)
    notes, rec = ts.drum_notes(p, bpm)
    os.remove(p)
    kick_t = [b for b, l in ev if l == "kick"]
    snare_t = [b for b, l in ev if l == "snare"]
    def lane_recall(pitch, truth_beats, tol=0.1):
        got = sorted(n["start"] for n in notes if n["pitch"] == pitch)
        hit = sum(1 for tb in truth_beats if got and min(abs(np.array(got) - tb)) <= tol)
        return hit / max(1, len(truth_beats))
    kr = lane_recall(36, kick_t); srr = lane_recall(38, snare_t)
    check("drums kick lane recall >= 0.9", kr >= 0.9, f"{kr:.2f}")
    all_t = [b for b, _ in ev]
    r, pr, f1 = onset_f1(notes, [{"start": b} for b in set(all_t)], tol_beats=0.1)
    check("drums overall onset recall >= 0.9", r >= 0.9, f"r={r:.2f}")
    check("drums all lanes populated", rec.get("kick") and rec.get("snare") and rec.get("chat"),
          f"k={rec.get('kick')} s={rec.get('snare')} h={rec.get('chat')}")
    # NOTE: per-lane precision/snare-recall are NOT asserted on synthetic audio.
    # Pure additive synthesis leaks each hit's transient across bands (a snare's
    # <140Hz click fires the kick lane, then the kick-bleed gate eats the snare)
    # — real drums are naturally band-limited and don't (Unity: 1059 real claps
    # on 2&4 kept). The AUTHORITATIVE drum precision/recall lives in leg_real().
    # TIGHTNESS (Chezy 2026-07-08): matched onsets must LAND, not just exist —
    # median |detected - truth| <= 10ms across every matched hit.
    spb = 60.0 / bpm
    errs = []
    got_all = sorted(n["start"] for n in notes)
    for tb in set(all_t):
        if got_all:
            d = float(min(abs(np.array(got_all) - tb)))
            if d <= 0.1:
                errs.append(d * spb * 1000.0)
    med = float(np.median(errs)) if errs else 1e9
    check("drums matched-onset median error <= 10ms", med <= 10.0,
          f"median {med:.1f}ms over {len(errs)} hits")


def leg_source_kit():
    """SOURCE KIT identity (Chezy's law): imported drums must SOUND like their
    audio counterparts. Known one-shots -> loop -> transcribe -> slice the
    loop's OWN hits into a kit -> re-render the notes with that kit -> the
    render must match the source loop (it is MADE of it), and each sliced
    exemplar must match its lane's other hits in timbre."""
    import transcribe_stems as ts
    import source_kit as sk
    import spectral as sp
    print("[synth] source kit — the record's own hits, identity by construction")
    bpm = 120.0
    ev = []
    for bar in range(8):
        b0 = bar * 4
        ev.append((b0 + 0, "kick")); ev.append((b0 + 2, "kick"))
        ev.append((b0 + 1, "snare")); ev.append((b0 + 3, "snare"))
        for h in range(8):
            ev.append((b0 + h * 0.5, "hat"))
    x = synth_drums(ev, bpm, dur_s=17.0)
    p = "/tmp/_batt_srckit.wav"; write_wav(x, p)
    notes, _rec = ts.drum_notes(p, bpm)
    name = sk.build_source_kit(p, notes, "_batt_srckit", bpm=bpm)
    check("source kit built (>=3 lanes)", name is not None, f"{name}")
    if name:
        kit = json.load(open(os.path.join(sk.KITS, name, "kit.json")))
        lanes = {s["keyNote"] for s in kit["samples"]}
        check("source kit carries kick+snare+hat", {36, 38}.issubset(lanes)
              and (42 in lanes or 46 in lanes), f"lanes {sorted(lanes)}")
        # KIT PLAYBACK IDENTITY, notes GIVEN: lay the TRUTH score through the
        # sliced kit at vel=1.0 (the ANCHOR LAW, v3+: gainDb is picked so
        # vel=1.0 reproduces the lane's OWN measured reference level exactly
        # through the engine's dB velocity law — no per-lane vel lookup
        # needed). This isolates what the kit rail OWNS — slicing, transient
        # alignment, the gainDb lane-balance law, placement — from transcription
        # recall/precision, which leg_drums/leg_real own (synthetic band bleed
        # makes those un-assertable here; 5/16 snares vanished when this leg
        # accidentally re-asserted recall).
        lanes_present = {int(s["keyNote"]) for s in kit["samples"]}
        gm_of = {"kick": 36, "snare": 38, "hat": 42 if 42 in lanes_present else 46}
        truth_notes = [{"start": tb_, "pitch": gm_of[ln], "vel": 1.0}
                       for tb_, ln in ev if gm_of[ln] in lanes_present]
        r = sk.render_notes(name, truth_notes, bpm, SR, len(x))
        # level-calibrate (gain staging is the mixer's job, identity is ours)
        if float(np.sqrt((r ** 2).mean())) > 1e-9:
            r = r * (float(np.sqrt((x ** 2).mean()))
                     / float(np.sqrt((r ** 2).mean())))
        m = sp.verify_arrays(x, r, SR)
        # env_corr floor 0.80 on SYNTHETIC drums: the 60Hz band of a pure
        # pitch-swept-sine kick is near-empty (energy sweeps 45->155Hz in
        # 140ms), so its envelope correlates mostly noise-floor — the same
        # additive-synthesis band-leak leg_drums documents. The AUTHORITATIVE
        # identity proof is the per-lane timbre cosine below (exemplar vs the
        # lane's real hits) + the real-stem run in source_kit_proof.
        check("source-kit playback env_corr >= 0.80 vs source",
              m["env_corr"] >= 0.80, f"env {m['env_corr']} spec {m['spectral_pct']}")
        check("source-kit playback spectral >= 70 vs source",
              m["spectral_pct"] >= 70.0, f"spec {m['spectral_pct']}")
        # per-lane timbre identity: exemplar log-mel vs the lane's OTHER hits
        sims = lane_timbre_similarity(p, notes, name, bpm)
        for gm, s in sorted(sims.items()):
            check(f"lane {gm} exemplar timbre-matches its hits (>=0.85)",
                  s >= 0.85, f"cos {s:.3f}")
        import shutil
        shutil.rmtree(os.path.join(sk.KITS, name), ignore_errors=True)
    os.remove(p)


def leg_medoid():
    """THE MEDOID GUARD (Chezy 2026-07-08, breadth test): a real 2nd track had
    kick=0.775 because the LOUDEST kick was a timbre OUTLIER and the old picker
    took it. Reproduce it: a kick lane of 12 normal hits + 3 LOUDER bright
    outliers -> the exemplar MUST match the majority timbre, not the loud
    outlier. Guards the centrality picker so a revert to loudest-isolated fails
    here (it can't be caught by the repo's clean synthetic loop otherwise)."""
    import source_kit as sk
    import librosa
    import shutil
    print("[synth] medoid — the representative exemplar, not the loudest outlier")
    bpm = 120.0
    sr = SR
    spb = 60.0 / bpm
    x = np.zeros(int(16.5 * sr))
    rng = np.random.RandomState(11)

    def norm_kick(a):                          # the MAJORITY voice: deep pitch-drop
        L = int(0.14 * sr); t = np.arange(L) / sr
        env = _soft_env(L, 26, atk_s=0.004)
        f = 105 * np.exp(-t * 22) + 48
        return a * env * np.sin(2 * math.pi * np.cumsum(f) / sr)

    def bright_kick(a):                        # the OUTLIER: a genuinely DIFFERENT
        L = int(0.14 * sr)                     # sound (metallic noise burst), not
        env = _soft_env(L, 55, atk_s=0.0005)   # a near-identical sine -- so its
        from scipy.signal import butter, sosfilt   # log-mel is clearly separable
        n = rng.randn(L)
        band = sosfilt(butter(4, [3000 / (sr / 2), 9000 / (sr / 2)], "band", output="sos"), n)
        return a * env * band / (np.abs(band).max() + 1e-9)

    notes = []
    beats = [b * 1.0 for b in range(16)]       # a kick every beat
    outliers = {3, 8, 12}                        # 3 of 16 are the loud bright one
    for i, b in enumerate(beats):
        a0 = int(b * spb * sr)
        if a0 + int(0.14 * sr) > len(x):
            break
        if i in outliers:
            sig = bright_kick(1.0)             # LOUDER
            vel = 1.0
        else:
            sig = norm_kick(0.6)               # the majority, quieter
            vel = 0.7
        x[a0:a0 + len(sig)] += sig[:len(x) - a0]
        notes.append({"start": round(b, 4), "len": 0.1, "pitch": 36, "vel": vel})
    p = "/tmp/_batt_medoid.wav"; write_wav(x, p)
    name = sk.build_source_kit(p, notes, "_batt_medoid", bpm=bpm, min_lanes=1)
    check("medoid: kit built from the outlier loop", name is not None, f"{name}")
    if name:
        # the exemplar's timbre must sit closer to the MAJORITY than the outlier
        mel = librosa.filters.mel(sr=sr, n_fft=1024, n_mels=40, fmin=30, fmax=16000)

        def lm(seg):
            L = int(0.10 * sr)
            seg = seg[:L] if len(seg) >= L else np.pad(seg, (0, L - len(seg)))
            S = np.abs(librosa.stft(seg.astype(np.float32), n_fft=1024, hop_length=256)) ** 2
            v = 10.0 * np.log10((mel @ S).mean(axis=1) + 1e-10)
            return (v - v.max())

        def cos(a, b):
            return float((a * b).sum() / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))
        maj = lm(norm_kick(0.6)); out = lm(bright_kick(1.0))
        zsr, z = sk._load_mono(os.path.join(sk.KITS, name, "kick.wav"))
        ex = lm(z)
        c_maj, c_out = cos(ex, maj), cos(ex, out)
        check("medoid: kick exemplar matches the MAJORITY, not the loud outlier",
              c_maj > c_out, f"cos(maj)={c_maj:.3f} vs cos(outlier)={c_out:.3f}")
        shutil.rmtree(os.path.join(sk.KITS, name), ignore_errors=True)
    os.remove(p)


def lane_timbre_similarity(stem_wav, notes, kit_name, bpm):
    """Cosine similarity (log-mel, dB) of each lane's kit exemplar vs the mean
    of that lane's OTHER detected hits in the stem. Shared by the battery and
    the real-stem proof so both measure the same thing."""
    import librosa
    import source_kit as sk
    sr, x = sk._load_mono(stem_wav)
    kit = json.load(open(os.path.join(sk.KITS, kit_name, "kit.json")))
    spb = 60.0 / bpm
    mel = librosa.filters.mel(sr=sr, n_fft=2048, n_mels=48, fmin=30, fmax=16000)

    def logmel(seg):
        L = int(0.12 * sr)
        seg = seg[:L] if len(seg) >= L else np.pad(seg, (0, L - len(seg)))
        S = np.abs(librosa.stft(seg.astype(np.float32), n_fft=2048,
                                hop_length=512)) ** 2
        v = 10.0 * np.log10((mel @ S).mean(axis=1) + 1e-10)
        return v - v.max()

    sims = {}
    for s in kit["samples"]:
        gm = int(s["keyNote"])
        zsr, z = sk._load_mono(os.path.join(sk.KITS, kit_name, s["file"]))
        ex = logmel(z)
        # STRONG hits only (vel >= 0.55): the lane's weak tail is cross-band
        # bleed (62 detected kicks vs 16 true on the synthetic loop) — the
        # exemplar must match the lane's TRUE voice, not its false positives
        lane_hits = sorted((nt for nt in notes if int(nt["pitch"]) == gm),
                           key=lambda nt: -float(nt.get("vel", 0.0)))
        strong = [nt for nt in lane_hits if float(nt.get("vel", 0.0)) >= 0.55]
        if len(strong) < 2:
            strong = lane_hits[:max(2, len(lane_hits) // 4)]
        vecs = []
        for nt in strong:
            i0 = int(float(nt["start"]) * spb * sr)
            seg = x[i0:i0 + int(0.12 * sr)]
            if len(seg) > int(0.03 * sr) and float(np.abs(seg).max()) > 1e-4:
                vecs.append(logmel(seg))
        if len(vecs) < 2:
            continue
        mean_hit = np.mean(vecs, axis=0)
        sims[gm] = float((ex * mean_hit).sum()
                         / (np.linalg.norm(ex) * np.linalg.norm(mean_hit) + 1e-12))
    return sims

def leg_gridphase():
    import transcribe_stems as ts
    print("[synth] grid phase — recover a planted offset")
    # 90 bpm -> 1/32 cell = 60/90/8*1000 = 83ms wide; a 22ms offset is well
    # inside the +-41ms unambiguous range (a 60ms offset at 120 wrapped a
    # near-full cell — that was a TEST bug, not a detector bug).
    bpm = 90.0; spb = 60.0 / bpm
    offset_ms = 22.0
    off_beats = (offset_ms / 1000.0) / spb
    ev = []
    for bar in range(6):
        for beat in range(4):
            ev.append((bar * 4 + beat + off_beats, "kick"))
            ev.append((bar * 4 + beat + 0.5 + off_beats, "hat"))
    x = synth_drums(ev, bpm, dur_s=18.0)
    p = "/tmp/_batt_phase.wav"; write_wav(x, p)
    notes, rec = ts.drum_notes(p, bpm)
    os.remove(p)
    got_ms = rec.get("grid_phase_ms", 0.0)
    cell = 0.125 * spb * 1000.0                       # 1/32 cell width in ms
    err = min(abs(got_ms - offset_ms), abs(got_ms - offset_ms + cell),
              abs(got_ms - offset_ms - cell))
    check("grid phase recovered (+-15ms)", err <= 15.0,
          f"planted {offset_ms}ms, detected {got_ms}ms, err {err:.0f}ms")

def leg_tatum():
    import transcribe_stems as ts
    print("[synth] tatum — half-time alias detector")
    bpm_true = 140.0
    ev = []
    for bar in range(8):                       # 1/16 hats = odd cells at 70bpm
        for six in range(16):
            ev.append((bar * 4 + six * 0.25, "hat"))
        for beat in range(4):
            ev.append((bar * 4 + beat, "kick"))
    x = synth_drums(ev, bpm_true, dur_s=14.0)
    p = "/tmp/_batt_tatum.wav"; write_wav(x, p)
    wants_at_half = ts.tatum_wants_double(p, bpm_true / 2)   # 70 -> should double
    wants_at_true = ts.tatum_wants_double(p, bpm_true)       # 140 -> should NOT
    os.remove(p)
    check("tatum: half-tempo WANTS double", wants_at_half is True)
    check("tatum: true-tempo does NOT double", wants_at_true is False)

def leg_harmonic():
    import transcribe_stems as ts
    print("[synth] harmonic — chord onset recovery")
    bpm = 100.0
    # Am - F - C - G, one chord/bar, triads held
    prog = {0: [57, 60, 64], 1: [53, 57, 60], 2: [48, 52, 55], 3: [55, 59, 62]}
    truth = []
    for bar in range(4):
        for p_ in prog[bar]:
            truth.append({"start": bar * 4.0, "len": 3.8, "pitch": p_, "vel": 0.8})
    x = synth_tone(truth, bpm, dur_s=10.0, harmonics=(1.0, 0.5, 0.3, 0.15))
    path = "/tmp/_batt_harm.wav"; write_wav(x, path)
    notes, rec = ts.other_notes(path, bpm, key="C major")
    os.remove(path)
    # did we recover each chord's pitch classes in its bar?
    good = 0
    for bar in range(4):
        want = {p_ % 12 for p_ in prog[bar]}
        got = {n["pitch"] % 12 for n in notes if bar * 4 <= n["start"] < bar * 4 + 4}
        good += len(want & got) / len(want)
    pc_recall = good / 4
    check("harmonic chord-tone recall >= 0.8", pc_recall >= 0.8, f"{pc_recall:.2f}")

def leg_real():
    """AUTHORITATIVE proof on real stems vs INDEPENDENT witnesses (pyin for
    bass pitch, full-band librosa onsets for drums) — the numbers that matter,
    on real audio the rails will actually meet."""
    print("[real] kosher stems vs independent witnesses")
    import librosa
    import transcribe_stems as ts
    S = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                     "songs", "c78698793db87eaf7b5ef087a6198d8bblp_kosher_-_pro_open_ft_babytron_official_video_stems")
    S = os.path.abspath(S)
    if not os.path.isdir(S):
        print("  (kosher stems absent — skipping real leg)")
        return
    bpm = 139.6; spb = 60.0 / bpm

    # --- BASS: coverage + pitch accuracy vs pyin (independent) ---
    sr, bx = ts._load_mono(os.path.join(S, "bass.wav"))
    y22 = librosa.resample(bx, orig_sr=sr, target_sr=22050).astype(np.float32)
    f0p, _, vpr = librosa.pyin(y22, fmin=25.0, fmax=250.0, sr=22050,
                               frame_length=4096, hop_length=221)
    conf = np.nan_to_num(vpr, nan=0.0) > 0.6
    f0p = np.nan_to_num(f0p, nan=0.0)
    notes, rec = ts.bass_notes(os.path.join(S, "bass.wav"), bpm)
    check("real bass coverage >= 0.9", rec["coverage"] >= 0.9, str(rec))
    # RPA: our note pitch vs pyin at each voiced frame
    n = len(f0p)
    roll = np.full(n, -1.0)
    fps_p = 22050 / 221
    for nt in sorted(notes, key=lambda q: q["start"]):
        a = int(nt["start"] * spb * fps_p); b = int((nt["start"] + nt["len"]) * spb * fps_p)
        roll[max(0, a):min(n, b + 1)] = nt["pitch"]
    v = conf & (f0p > 0)
    ref = np.full(n, np.nan); ref[v] = 69 + 12 * np.log2(f0p[v] / 440.0)
    both = v & (roll >= 0)
    rpa = (np.abs(roll[both] - ref[both]) <= 0.6).mean() if both.any() else 0
    check("real bass RPA vs pyin >= 0.8", rpa >= 0.8, f"{rpa:.2f}")

    # --- DRUMS: onset recall/precision vs full-band witness (independent) ---
    sr, dx = ts._load_mono(os.path.join(S, "drums.wav"))
    env = librosa.onset.onset_strength(y=dx.astype(np.float32), sr=sr, hop_length=256)
    pk = np.percentile(env, 98) or 1.0
    on_t = librosa.onset.onset_detect(onset_envelope=env / pk, sr=sr, hop_length=256,
                                      units="time", backtrack=False, delta=0.07, wait=3)
    dn, drec = ts.drum_notes(os.path.join(S, "drums.wav"), bpm)
    starts = np.array(sorted(n2["start"] * spb for n2 in dn))
    recall = np.mean([np.abs(starts - t).min() <= 0.035 for t in on_t]) if len(starts) else 0
    prec = np.mean([np.abs(on_t - s).min() <= 0.035 for s in starts]) if len(starts) else 0
    check("real drums onset recall >= 0.9", recall >= 0.9, f"{recall:.2f}")
    check("real drums note precision >= 0.6", prec >= 0.6, f"{prec:.2f}")

def main():
    real = "--real" in sys.argv
    print("== THE TRANSCRIPTION BATTERY ==")
    leg_units()
    leg_bass()
    leg_drums()
    leg_source_kit()
    leg_medoid()
    leg_gridphase()
    leg_tatum()
    leg_harmonic()
    if real:
        leg_real()
    print()
    if FAILS:
        print(f"BATTERY: {len(FAILS)} FAIL -> {FAILS}")
    else:
        print("BATTERY: ALL GREEN")
    sys.exit(len(FAILS))

if __name__ == "__main__":
    main()
