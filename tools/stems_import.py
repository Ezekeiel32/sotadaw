#!/usr/bin/env python3
"""ABSORPTION WEDGE #2: drop ANY finished song -> an editable symbolic session.

  stems_import.py <audio> <song_name> [--quality max] [--no-midi] [--bpm N]

Pipeline (all local, GPU if available):
  1. demucs htdemucs (or htdemucs_ft with --quality max) -> drums/bass/other/vocals stems
  2. BPM estimate (onset autocorrelation on the drums stem) unless --bpm given
  3. key estimate (Krumhansl chromagram, reused from analyze2) on the harmonic stem
  4. SPECIALIST MIDI rails (tools/transcribe_stems.py, the kosher fix): fcpe
     octave-trick for bass (99% coverage where basic-pitch heard 0.8% of an 808
     line), fcpe for vocals, band-lane drums (98.5% onset recall vs 24%), tuned
     basic-pitch for the polyphonic 'other' — basic-pitch+polish is the fallback
  5. songs/<name>.json: EDITABLE MIDI tracks sounding (named drum lanes, pitched
     source kits, sung vocal melody) + 4 muted stem-reference audio tracks

Their render becomes OUR project. Suno exports stems; we import them into structure.
"""
import argparse, importlib.util, json, math, os, shutil, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "songs")


def _hb(stage, pct, detail=""):
    """Import progress heartbeat -> agent/ipc/import_progress.json (atomic).
    The UI/agent polls it; a dead heartbeat is just a stale ts. Never fails."""
    try:
        p = os.path.join(ROOT, "agent", "ipc", "import_progress.json")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        tmp = p + ".tmp"
        json.dump({"stage": str(stage), "pct": round(float(pct), 3),
                   "detail": str(detail)[:200], "ts": time.time()},
                  open(tmp, "w"))
        os.replace(tmp, p)
    except Exception:
        pass
sys.path.insert(0, os.path.join(ROOT, "tools"))   # midi_polish, beatgrid, keyvote…

def load_analyze2():
    spec = importlib.util.spec_from_file_location("analyze2", os.path.join(ROOT, "tools", "analyze2.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def _feed_reference_circle(audio_path, name, song, bpm_conf, key_conf):
    """R2: persist this import's production DNA as a KG (:Reference) node —
    sha1-keyed (re-import = same node) + SOUNDS_LIKE the nearest MixTarget
    genre + HAS_GROOVE when the learned groove persisted. The mix ears run
    on the SOURCE file (ffmpeg-transcoded when not wav). Sandbox law mirrors
    groove.py: rig imports must not leak into the brain."""
    if os.environ.get("SOTADAW_SANDBOX") == "1" or name.endswith("_e2e"):
        print("[stems] reference circle: sandbox/test - NOT persisted", flush=True)
        return
    if os.path.isdir(audio_path):
        print("[stems] reference circle: retrofit (stems dir, no source file) — "
              "DNA was banked by the original import; skipped", flush=True)
        return
    import hashlib
    import subprocess
    import tempfile
    h = hashlib.sha1()
    with open(audio_path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    sha = h.hexdigest()
    a2 = load_analyze2()
    wav, tmp = audio_path, None
    if not audio_path.lower().endswith(".wav"):
        t = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        t.close()
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", audio_path,
                        "-ac", "2", "-ar", "44100", t.name], check=True)
        wav, tmp = t.name, t.name
    try:
        m = a2.analyze(wav)
    finally:
        if tmp:
            os.unlink(tmp)
    profile = {"band_energy_pct": m["band_energy_pct"],
               "band_lufs": m.get("band_lufs"),
               "spectral_centroid_hz": m["spectral_centroid_hz"],
               "stereo_width_db": m["stereo_width_db"],
               "rms_by_quarter_db": m["rms_by_quarter_db"]}
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    from kg import KG, esc
    kg = KG()
    groove_name = f"import_{name}"
    has_groove = bool(kg.q(f"MATCH (g:Groove {{name: '{esc(groove_name)}'}}) "
                           f"RETURN g LIMIT 1"))
    kg.ensure_reference(
        name, sha,
        f"import {time.strftime('%Y-%m-%d')} {os.path.basename(audio_path)}",
        bpm=float(song.get("bpm") or 0), bpm_conf=round(float(bpm_conf or 0), 3),
        key=song.get("key") or "", key_conf=round(float(key_conf or 0), 3),
        sections_json=json.dumps(song.get("sections") or []),
        chords_json=json.dumps(song.get("chords") or []),
        groove_name=groove_name if has_groove else "",
        band_profile_json=json.dumps(profile),
        lufs=m["lufs_integrated"], dbtp=m["true_peak_dbtp"],
        crest=round(m["true_peak_dbtp"] - m["rms_db"], 2))
    ng = kg.nearest_genre_by_mix(m["lufs_integrated"], m["band_energy_pct"])
    if ng:
        kg.link_reference(sha, "SOUNDS_LIKE", "Genre", ng[0], weight=ng[1])
    if has_groove:
        kg.link_reference(sha, "HAS_GROOVE", "Groove", groove_name)
    print(f"[stems] reference circle: KG Reference '{name}' ({sha[:10]}) "
          f"sounds-like {ng[0] if ng else '?'}"
          + (f" + groove {groove_name}" if has_groove else ""), flush=True)

def estimate_bpm(wav_path, lo=60.0, hi=200.0):
    """EARS v4 first: Beat This! neural grid (battery: ~±1bpm on the eval set; locks
    through beatless intros) -> (bpm, confidence); autocorr fallback if unavailable."""
    try:
        import sys as _sys, os as _os
        _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
        from beatgrid import analyze_grid
        g = analyze_grid(wav_path)
        if g.get("bpm") and lo <= g["bpm"] <= hi and (g.get("bpm_stability") or 0) >= 0.5:
            return round(float(g["bpm"]), 1), float(g["bpm_stability"])
    except Exception:
        pass
    return _estimate_bpm_autocorr(wav_path, lo, hi)

def _estimate_bpm_autocorr(wav_path, lo=60.0, hi=200.0):
    """Onset-envelope autocorrelation on (ideally) the drums stem (v3 fallback)."""
    import numpy as np
    from scipy.io import wavfile
    sr, x = wavfile.read(wav_path)
    if x.dtype.kind == "i":
        x = x.astype(np.float64) / np.iinfo(x.dtype).max
    if x.ndim > 1:
        x = x.mean(axis=1)
    hop = 512
    n = (len(x) // hop) * hop
    if n < hop * 64:
        return 120.0, 0.0
    frames = x[:n].reshape(-1, hop)
    env = np.sqrt((frames ** 2).mean(axis=1))
    onset = np.maximum(0, np.diff(env))
    onset -= onset.mean()
    ac = np.correlate(onset, onset, "full")[len(onset) - 1:]
    fps = sr / hop
    lags = np.arange(len(ac)) / fps                      # seconds per beat candidates
    mask = (lags >= 60.0 / hi) & (lags <= 60.0 / lo)
    if not mask.any() or ac[0] <= 0:
        return 120.0, 0.0
    # score each candidate + its half/double to prefer the metrically stable tempo
    idx = np.where(mask)[0]
    best, best_score = idx[0], -1.0
    for i in idx:
        score = ac[i]
        if 2 * i < len(ac): score += 0.5 * ac[2 * i]
        if i // 2 > 0:      score += 0.25 * ac[i // 2]
        if score > best_score:
            best_score, best = score, i
    bpm = 60.0 / lags[best]
    while bpm >= 165: bpm /= 2     # fold into the common range; producers can double in-app
    while bpm < 65:   bpm *= 2
    return round(float(bpm), 1), float(ac[best] / (ac[0] + 1e-12))

def _remote_notes_for(wav_path, bpm, role, key):
    """THE FORGE SEAM's pure kernel: (notes, engine) from a pre-computed
    remote_notes sidecar, or None. Strict match law — the forge derived
    bpm/key with the same shipped code, so any drift means the local rails
    must listen for themselves (fail-open, battery-proven)."""
    rn = os.path.join(os.path.dirname(os.path.abspath(wav_path)),
                      "remote_notes", os.path.basename(wav_path) + ".json")
    if not os.path.exists(rn):
        return None
    try:
        j = json.load(open(rn))
        if (j.get("role") == role
                and abs(float(j.get("bpm", -1)) - float(bpm)) < 0.05
                and (role != "melodic" or j.get("key") == key)
                and isinstance(j.get("notes"), list)):
            return j["notes"], j.get("engine", "remote")
        print("[stems] remote notes stale (role/bpm/key drift) -> local rails",
              flush=True)
    except Exception as rex:
        print(f"[stems] remote notes unreadable ({rex}) -> local rails",
              flush=True)
    return None


def transcribe_v2(wav_path, bpm, role="melodic", key=None):
    """SPECIALIST rails first (measured on real stems — see transcribe_stems.py
    header), old basic-pitch path as the no-torch fallback. Returns
    (notes, engine_tag); the tag gates the downstream grammar priors — an fcpe
    line at 84% independent RPA doesn't want its chromatic 808 slides
    'corrected', but basic-pitch guesswork still does."""
    # THE FORGE SEAM (tools/modal_stems.py): a remote import pre-computes these
    # notes on cloud GPU through the SAME rails, with bpm/key derived by the
    # shipped local code. Consume only on an exact (role, bpm, key) match —
    # any drift falls open to the local rails below.
    remote = _remote_notes_for(wav_path, bpm, role, key)
    if remote is not None:
        print(f"[stems] {role} rail: REMOTE {remote[1]} "
              f"({len(remote[0])} notes — the forge already listened)",
              flush=True)
        return remote
    try:
        import transcribe_stems as ts
        if role == "bass":
            notes, rec = ts.bass_notes(wav_path, bpm)
        elif role == "vocal":
            notes, rec = ts.vocal_notes(wav_path, bpm)
        else:
            src = wav_path
            # DRY TRUTH (#51) — VERIFIED NEGATIVE for this role (2026-07-15,
            # the goldenbrown autopsy): anvuew's dereverb is a VOCAL-target
            # cleaner; on the instrumental 'other' stem it returned ~silence
            # (-81dB) and three imports transcribed 72 notes / 8.6% coverage
            # out of a wall-to-wall harpsichord bed (wet stem: 999 / 66.4%).
            # The melodic rail transcribes the WET stem. Opt back in with
            # SOTADAW_DRYCLEAN_OTHER=1 — mel_clean's dry-twin health gate
            # (retention in active spans) now refuses a nuked twin either way.
            if os.environ.get("SOTADAW_DRYCLEAN_OTHER") == "1":
                try:
                    import mel_clean
                    dry = mel_clean.clean_cached(wav_path, "dereverb")
                    if dry:
                        src = dry
                except Exception as ce:
                    print(f"[stems] dry-clean skipped ({ce})", flush=True)
            notes, rec = ts.other_notes(src, bpm, key=key)
            if src != wav_path:
                rec["engine"] = str(rec.get("engine", "")) + "+dry"
        print(f"[stems] {role} rail: {rec}", flush=True)
        return notes, rec["engine"]
    except Exception as e:
        print(f"[stems] {role} specialist rail failed ({type(e).__name__}: {e}) "
              f"-> basic-pitch fallback", flush=True)
        return transcribe(wav_path, bpm, role=role, key=key), "basic-pitch"

def transcribe(wav_path, bpm, max_notes=400, min_len_s=0.06, min_amp=0.15,
               role="melodic", key=None):
    """basic-pitch (ONNX) -> song.json notes in beats, then MIDI POLISH: the raw
    events are soup (octave ghosts, shattered sustains, overlaps on mono sources,
    off-grid jitter — and the old cap truncated the song's TAIL). midi_polish
    fixes all of it role-aware; battery: tools/midi_polish_battery.py --real."""
    # THE CUDA PRELOAD LAW (2026-07-12, the transcription rail was DEAD on Chezy's
    # box): the onnxruntime that serves basic-pitch here is a CUDA build whose
    # libcudart.so.13 ships inside the nvidia wheels — NOT on the dynamic loader
    # path. Imported bare it raises ImportError, and basic_pitch's backend probe
    # catches that as "onnxruntime is not installed": all four backends go False,
    # _default_model_type never binds, and the import dies on a NameError that
    # names nothing. torch loads libcudart first (this is why sing.py's CUDA voice
    # always worked and this rail never did). Import torch BEFORE basic_pitch.
    import torch  # noqa: F401  (side-effect import: preloads the CUDA runtime)
    from basic_pitch.inference import predict
    import midi_polish
    _, _, note_events = predict(wav_path)
    spb = 60.0 / bpm
    notes = []
    for ev in note_events:
        start_s, end_s, pitch, amp = ev[0], ev[1], int(ev[2]), float(ev[3])
        if end_s - start_s < min_len_s or amp < min_amp:
            continue
        notes.append({"start": round(start_s / spb, 3),
                      "len": round(max(0.05, (end_s - start_s) / spb), 3),
                      "pitch": pitch, "vel": round(min(1.0, max(0.2, amp)), 2)})
    return midi_polish.polish(notes, role=role, bpm=bpm, key=key, max_notes=max_notes)

DAEMON_PAUSE = os.path.expanduser("~/.cache/looplm/daemon_pause")

def _gpu_free_mb():
    import subprocess as _sp
    try:
        o = _sp.run(["nvidia-smi", "--query-gpu=memory.free",
                     "--format=csv,noheader,nounits"],
                    stdout=_sp.PIPE, text=True, timeout=10)
        return int(o.stdout.strip().splitlines()[0])
    except Exception:
        return -1

class GpuWindow:
    """THE GPU LEVER (the ZPE-roadmap contention law, firing 'Unity'): the
    base-training daemon owns the idle card (~5.1GB), so imports OOM'd into a
    single-threaded CPU crawl that blew the MCP timeout — user saw 'no song'.
    The daemon ships its OWN clean pause lever: touch ~/.cache/looplm/
    daemon_pause -> it SAVES + EXITS (zero steps lost, watchdog relaunches
    within ~3min of the flag clearing). Acquire pauses ONLY when (cuda + the
    daemon is actually running + not already user-paused); release ALWAYS
    clears what WE created. Opt-out: SOTADAW_NO_PAUSE=1."""
    def __init__(self, need_mb=2600):
        self.need = need_mb
        self.owned = False
    def acquire(self):
        if os.environ.get("SOTADAW_NO_PAUSE") == "1":
            return False
        free = _gpu_free_mb()
        if free < 0:
            return False
        if free >= self.need:
            return True
        if os.path.exists(DAEMON_PAUSE):
            return False                       # user's own pause — not ours to manage
        import subprocess as _sp
        if _sp.run(["pgrep", "-f", "train_base_daemo[n]"],
                   stdout=_sp.DEVNULL).returncode != 0:
            # NAME THE SQUATTER (aranyanyara_4, 2026-07-17): an orphaned bench
            # held 4.9G, the strip just said "on cpu", and the user had to ask
            # why the import crawled — a fallback nobody can attribute reads
            # as "the import is broken". No pause lever for foreign jobs;
            # naming them is the honest floor.
            try:
                o = _sp.run(["nvidia-smi",
                             "--query-compute-apps=pid,name,used_memory",
                             "--format=csv,noheader"], stdout=_sp.PIPE,
                            text=True, timeout=10).stdout.strip()
                if o:
                    top = max(o.splitlines(), key=lambda l: int(
                        l.split(",")[-1].strip().split()[0]))
                    print(f"[stems] GPU held by a foreign job ({top.strip()})"
                          f" — no pause lever for it, CPU path "
                          f"({free}MB free, need {self.need}MB)", flush=True)
            except Exception:
                pass
            return False                       # VRAM is full but not by the daemon
        open(DAEMON_PAUSE, "w").close()
        self.owned = True
        print(f"[stems] GPU window: pausing the training daemon (clean save+exit, "
              f"auto-resume after) — {free}MB free, need {self.need}MB", flush=True)
        for _ in range(60):                    # ckpt save ~828MB; allow up to 3min
            time.sleep(3)
            free = _gpu_free_mb()
            if free >= self.need:
                print(f"[stems] GPU window OPEN: {free}MB free", flush=True)
                return True
        print("[stems] GPU window never opened -> CPU path", flush=True)
        return False
    def release(self):
        if self.owned:
            try:
                os.remove(DAEMON_PAUSE)
                print("[stems] GPU window closed: daemon resume flag cleared "
                      "(watchdog relaunches within ~3min)", flush=True)
            except FileNotFoundError:
                pass
            self.owned = False

def _stem_audible(path, peak_floor_db=-40.0, rms_floor_db=-55.0):
    """Is there actually an instrument in this stem, or separation dust?"""
    import numpy as np
    from scipy.io import wavfile
    sr, x = wavfile.read(path)
    if x.dtype.kind == "i":
        x = x.astype(np.float64) / np.iinfo(x.dtype).max
    if x.ndim > 1:
        x = x.mean(axis=1)
    peak = float(np.max(np.abs(x)) + 1e-12)
    rms = float(np.sqrt((x ** 2).mean()) + 1e-12)
    return 20 * math.log10(peak) > peak_floor_db and 20 * math.log10(rms) > rms_floor_db

def _assist_ok(device):
    """THE MICROSCOPE IS THE DEFAULT (2026-07-15, Chezy: other = 'many
    instruments... more than one lead' and the MIDI must represent them):
    htdemucs_6s runs on every CUDA import — one extra ~30-60s GPU pass buys
    dedicated guitar/piano lanes. It was quality==max-only before, so the
    default product never decomposed 'other' at all. CPU boxes still skip
    (a second demucs pass on the slow rung doubles a 20-40min import);
    SOTADAW_6S=1 forces, SOTADAW_NO_6S=1 kills."""
    if os.environ.get("SOTADAW_NO_6S") == "1":
        return False
    return device == "cuda" or os.environ.get("SOTADAW_6S") == "1"


def _other_family(nm):
    """Lane names born from the harmonic bucket ('other' + 6s parts + their
    stream splits) — the chord prior and the level law both need the family."""
    return (nm.split("_")[0] in ("other", "guitar", "piano", "keys")
            and nm.endswith(("_sketch", "_lead", "_pad", "_chords")))


def six_stem_assist(stems, stems_dir):
    """THE HARMONIC MICROSCOPE: htdemucs_6s re-listens to the (re-summed) mix
    and hands the TRANSCRIPTION layer dedicated guitar/piano stems + a cleaner
    harmonic residual. The 4-stem lanes stay the session's AUDIO truth (the
    ft separator is better there); 6s stems exist only to be transcribed.
    Elastic GPU->CPU (--segment 7); idempotent (reuses <stems>/6s/); returns {}
    on any failure — the assist is optional by design."""
    out_dir = os.path.join(stems_dir, "6s")
    have = {s: os.path.join(out_dir, f"{s}.wav") for s in ("guitar", "piano", "other")}
    if all(os.path.exists(p) for p in have.values()):
        return have
    import numpy as np
    from scipy.io import wavfile
    import soundfile as sf
    mix, sr = None, None
    for s in ("drums", "bass", "other", "vocals"):
        if s not in stems:
            continue
        ssr, sx = wavfile.read(stems[s])
        if sx.dtype.kind == "i":
            sx = sx.astype(np.float64) / np.iinfo(sx.dtype).max
        sr = ssr
        mix = sx if mix is None else mix[:len(sx)] + sx[:len(mix)]
    if mix is None:
        return {}
    peak = float(np.max(np.abs(mix)) or 1.0)
    if peak > 0.99:
        mix = mix / peak * 0.98                # stems re-sum hot; demucs wants sane input
    work = os.path.join(stems_dir, "_6s_work")
    os.makedirs(work, exist_ok=True)
    mixp = os.path.join(work, "mix.wav")
    sf.write(mixp, mix.astype(np.float32), sr)
    import subprocess as _sp
    import torch
    def _run(dev, lowmem):
        cmd = [sys.executable, "-m", "demucs.separate", "-n", "htdemucs_6s", "-d", dev,
               "-o", work, "--filename", "{stem}.{ext}"]
        if lowmem:
            cmd += ["--segment", "7", "-j", "1"]
        cmd.append(mixp)
        p = _sp.run(cmd, stdout=_sp.PIPE, stderr=_sp.STDOUT, text=True)
        return p.returncode, p.stdout or ""
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    rc, _out = _run(dev, lowmem=False)
    if rc != 0:
        rc, _out = _run("cpu", lowmem=True)
    if rc != 0:
        shutil.rmtree(work, ignore_errors=True)
        print(f"[stems] 6s assist unavailable (demucs exit {rc})", flush=True)
        return {}
    os.makedirs(out_dir, exist_ok=True)
    got = {}
    src = os.path.join(work, "htdemucs_6s")
    for s in ("guitar", "piano", "other"):
        p = os.path.join(src, f"{s}.wav")
        if os.path.exists(p):
            shutil.move(p, have[s])
            got[s] = have[s]
    shutil.rmtree(work, ignore_errors=True)
    return got

def pick_loop_windows(x, sr, bpm, n=4, bars=8):
    """Find the song's SECTIONS: n non-overlapping `bars`-bar windows on the 4-bar
    phrase grid, chosen by energy + spectral distinctness (not fixed offsets — a
    real song's drop is rarely at bar 0). Returns offsets (sec), song-order."""
    import numpy as np
    spb = 60.0 / bpm
    win, step = bars * 4 * spb, 16 * spb            # 8-bar window, 4-bar grid
    cands = []
    off = 0.0
    while off + win <= len(x) / sr + 1e-9:
        seg = x[int(off * sr):int((off + win) * sr)]
        e = float(np.sqrt((seg ** 2).mean()))
        dec = seg[:: max(1, len(seg) // 65536)]        # fingerprint, not fidelity
        S = np.abs(np.fft.rfft(dec))
        fr = np.fft.rfftfreq(len(dec))                 # normalized 0..0.5, same axis for all
        cent = float((S * fr).sum() / (S.sum() + 1e-12))
        lowr = float(S[:max(1, len(S) // 16)].sum() / (S.sum() + 1e-12))
        cands.append({"off": off, "e": e, "fp": (cent, lowr)})
        off += step
    cands = [c for c in cands if c["e"] > 1e-5]
    if not cands:
        return []
    dist = lambda a, b: (abs(a["fp"][0] - b["fp"][0]) / (a["fp"][0] + b["fp"][0] + 1e-12)
                         + abs(a["fp"][1] - b["fp"][1]))
    overlaps = lambda a, b: abs(a["off"] - b["off"]) < win
    emax = max(c["e"] for c in cands)
    picked = [max(cands, key=lambda c: c["e"])]                   # the PEAK
    loud = [c for c in cands if c["e"] > 0.25 * emax and not any(overlaps(c, p) for p in picked)]
    if loud:                                                       # the OTHER section
        picked.append(max(loud, key=lambda c: dist(c, picked[0])))
    while len(picked) < n:                                         # fill by energy
        rest = [c for c in cands if not any(overlaps(c, p) for p in picked)]
        if not rest:
            break
        picked.append(max(rest, key=lambda c: c["e"]))
    return sorted(round(c["off"], 4) for c in picked)


def reference_pull(out, song, stems, name, bpm):
    """THE REFERENCE PULL (wave 2 — auto-baked from the fable runs' recurring
    moves: 'make the MIDI sound like the original' asked twice on one import,
    answered both times with the record's OWN groove on the sketch lanes + a
    tone pull toward the record). CLOSED LOOP OR NOTHING — probe-proven:
    blind-baking these onto a grid-true record COST 1.13 spectral (detected
    sketches already carry true timing; the average groove profile smears
    them). Apply to a TEMP copy, render, verify vs the record's stem sum,
    keep ONLY on a measured win (≥ +0.05). Returns the (possibly updated)
    song dict, or None when nothing changed."""
    import subprocess as _sp
    import numpy as _np
    import groove as _gr
    import source_kit as _sk
    from spectral import verify_arrays as _va
    _m1 = os.path.join(ROOT, "app/build/m1_artefacts/Release/m1")

    def _mix_score(song_path):
        import tempfile as _tf
        import soundfile as _sf
        w = os.path.join(_tf.gettempdir(), f"_refpull_{os.getpid()}.wav")
        r = _sp.run([_m1, "render", song_path, w], capture_output=True,
                    text=True, timeout=1200)
        if r.returncode != 0:
            return None
        prod, psr = _sf.read(w, dtype="float32")
        os.remove(w)
        if prod.ndim > 1:
            prod = prod.mean(axis=1)
        rec = None
        for st_ in ("drums", "bass", "other", "vocals"):
            if st_ not in stems:
                continue
            xs_, _ssr = _sf.read(stems[st_], dtype="float32")
            if xs_.ndim > 1:
                xs_ = xs_.mean(axis=1)
            rec = xs_ if rec is None else rec[:len(xs_)] + xs_[:len(rec)]
        if rec is None:
            return None
        n_ = min(len(rec), len(prod))
        return _va(rec[:n_], prod[:n_], psr)["spectral_pct"]

    gname = f"import_{name}"
    cand = out + ".refpull"
    shutil.copyfile(out, cand)
    moves = []
    if gname in _gr.store():
        for ln in ("bass_sketch", "other_sketch", "vocals_sketch",
                   "piano_sketch", "guitar_sketch"):
            if any(t.get("name") == ln and t.get("notes")
                   for t in song["tracks"]):
                if str(_gr.apply_groove(cand, ln, gname,
                                        amount=0.65)).startswith("OK"):
                    moves.append(f"groove@0.65:{ln}")
    cs = json.load(open(cand))

    def _centroid(x, sr_):
        from scipy.signal import welch as _welch
        f, p = _welch(_np.asarray(x, dtype=_np.float32), fs=sr_,
                      nperseg=8192)
        tot = float(p.sum())
        return float((f * p).sum() / tot) if tot > 1e-12 else 0.0

    for ln, st in (("bass_sketch", "bass"), ("other_sketch", "other")):
        tr = next((t for t in cs["tracks"]
                   if t.get("name") == ln and t.get("notes")), None)
        kit = (tr or {}).get("source", {}).get("kit")
        if tr is None or not kit or st not in stems \
                or any(fx.get("id") == "fx_filter"
                       for fx in (tr.get("fx") or [])):
            continue
        sr_s, xs = _sk._load_mono(stems[st])
        rend = _sk.render_notes(kit, tr["notes"], bpm, sr_s, len(xs))
        c_stem, c_lane = _centroid(xs, sr_s), _centroid(rend, sr_s)
        del xs, rend
        # a brightness gap only counts when the content is actually bright
        # (>=1kHz centroids) — sub-500Hz ratios are noise (probe-measured)
        if c_stem > 1000 and c_lane > c_stem * 1.2:
            tr.setdefault("fx", []).append(
                {"id": "fx_filter",
                 "params": {"cutoff": max(2200, int(c_stem * 1.6))}})
            moves.append(f"tone:{ln}")
    json.dump(cs, open(cand, "w"), indent=1)

    if not moves:
        os.remove(cand)
        return None
    base_score = _mix_score(out)
    cand_score = _mix_score(cand) if base_score is not None else None
    if base_score is not None and cand_score is not None \
            and cand_score >= base_score + 0.05:
        shutil.move(cand, out)
        print(f"[stems] REFERENCE PULL KEPT "
              f"(+{cand_score - base_score:.2f} spectral: {base_score:.2f} "
              f"-> {cand_score:.2f}): {', '.join(moves)}", flush=True)
        return json.load(open(out))
    os.remove(cand)
    print(f"[stems] reference pull measured and DROPPED "
          f"({base_score} -> {cand_score}): the record's detected "
          "timing already wins", flush=True)
    return None


def refine_vocals_roformer(stems, audio_path, name, device):
    """Replace the demucs VOCALS stem with BS-Roformer's when GPU + model are
    present. GROUND TRUTH (2026-07-09, three dry-vocal oracles + wad3 inst):
    demucs is great on a clean LEAD (+24.7dB) but COLLAPSES on layered vocals
    (harmony -12.5dB, double +1.6dB on htdemucs_ft) — negative SI-SDR = worse
    than doing nothing. Roformer is ROBUST: +13.9/+12.6/+13.9dB flat, whatever
    the vocal density. This DAW's material is rap with DOUBLED/harmonised hooks
    and ad-libs — the exact case demucs fails and roformer wins. drums/bass/
    other stay demucs (roformer is vocals-only). Pi-safe: available(need_gpu)
    is False without CUDA -> demucs vocals kept untouched. SOTADAW_NO_ROFORMER=1
    forces the demucs path (A/B + regression testing)."""
    if os.environ.get("SOTADAW_NO_ROFORMER") == "1" or device != "cuda":
        return stems
    voc_path = stems.get("vocals")
    if not voc_path:
        return stems
    marker = voc_path + ".model"
    if os.path.exists(marker) and open(marker).read().strip() == "bs_roformer":
        return stems                              # already refined (reuse path)
    try:
        import mss_roformer as mr
    except Exception:
        return stems
    if not mr.available(need_gpu=True):
        return stems
    try:
        import soundfile as sf
        x, sr = mr._load_audio(audio_path)        # the honest input: the full mix
        print(f"[stems] roformer: refining vocals on {len(x)/sr:.0f}s "
              f"(demucs collapses on layered vocals; roformer holds ~13dB)…",
              flush=True)
        def _prog(i, n):
            _hb("refining vocals (roformer)", 0.41 + 0.03 * i / max(1, n),
                f"chunk {i}/{n}")
            print(f"\r[stems] roformer {i}/{n}", end="", flush=True)
        voc, _inst = mr.separate_vocals(x, sr, num_overlap=2, progress=_prog)
        print(flush=True)
        sf.write(voc_path, voc, sr, subtype="FLOAT")    # overwrite demucs vocals
                                                        # (float: tails survive)
        open(marker, "w").write("bs_roformer")
        print(f"[stems] roformer vocals -> {os.path.basename(voc_path)} "
              f"(the record's own voice, layered-safe)", flush=True)
    except Exception as e:
        print(f"[stems] roformer refine skipped ({e}) -> demucs vocals kept",
              flush=True)
    return stems


def roformer_vocals_first(audio_path, stems_dir, work):
    """THE CLEAN SPLIT (Chezy 2026-07-11: vocal/instrument separation "MUCH
    MUCH better"): vocals FIRST (BS-Roformer, the layered-safe model), then
    demucs separates the INSTRUMENTAL (mix - vocals) instead of the full mix.
    Two structural wins over refine-after: (1) vocal residue can no longer
    bleed into drums/other — demucs never hears the voice at all; (2)
    vocals + instrumental = the mix SAMPLE-EXACT by construction (the old
    flow's stem-sum error lived exactly on that seam). Float32 end to end:
    int16 at this boundary truncated -90dB tails BEFORE capture ever saw
    them. Returns (vocals_path, instrumental_path) or None -> the caller
    keeps the classic full-mix demucs path (no GPU / no model / kill-switch
    SOTADAW_NO_CASCADE=1; SOTADAW_NO_ROFORMER=1 kills both roformer rails)."""
    if (os.environ.get("SOTADAW_NO_ROFORMER") == "1"
            or os.environ.get("SOTADAW_NO_CASCADE") == "1"):
        return None
    try:
        import mss_roformer as mr
        import soundfile as sf
    except Exception:
        return None
    if not mr.available(need_gpu=True):
        return None
    voc_path = os.path.join(stems_dir, "vocals.wav")
    inst_path = os.path.join(work, "instrumental.wav")
    marker = voc_path + ".model"
    try:
        os.makedirs(work, exist_ok=True)
        x, sr = mr._load_audio(audio_path)        # the honest input: the full mix
        if (os.path.exists(voc_path) and os.path.exists(marker)
                and open(marker).read().strip() == "bs_roformer"):
            voc, vsr = sf.read(voc_path, dtype="float32", always_2d=True)
            if vsr == sr and len(voc) == len(x):  # crash-resume: keep the paid pass
                sf.write(inst_path, x - voc, sr, subtype="FLOAT")
                print("[stems] clean split: reusing roformer vocals (marker)",
                      flush=True)
                return voc_path, inst_path
        print(f"[stems] clean split: roformer vocals FIRST on {len(x)/sr:.0f}s "
              f"(demucs will only ever hear the instrumental)…", flush=True)
        def _prog(i, n):
            _hb("isolating vocals (roformer)", 0.05 + 0.15 * i / max(1, n),
                f"chunk {i}/{n} — the clean split's first pass")
            print(f"\r[stems] roformer {i}/{n}", end="", flush=True)
        voc, _inst = mr.separate_vocals(x, sr, num_overlap=2, progress=_prog)
        print(flush=True)
        sf.write(voc_path, voc, sr, subtype="FLOAT")
        sf.write(inst_path, x - voc, sr, subtype="FLOAT")   # exact complement
        open(marker, "w").write("bs_roformer")
        return voc_path, inst_path
    except Exception as e:
        print(f"[stems] clean split skipped ({e}) -> classic full-mix demucs",
              flush=True)
        return None


def import_song(audio_path, name, quality="fast", with_midi=True, bpm_override=None,
                spectral_mode=None, instruments="original"):
    t0 = time.time()
    audio_path = os.path.abspath(audio_path)
    if not os.path.exists(audio_path):
        raise SystemExit(f"no such file: {audio_path}")
    _hb("reading audio", 0.02, os.path.basename(audio_path))
    # SEPARATION MODEL LAW: htdemucs_ft beats plain htdemucs by ~0.4-0.6dB
    # SDR on every stem (published + our ground-truth) at 4x the compute —
    # nothing on a CUDA box (~1min), real on a Pi. So the DEFAULT is
    # GPU-aware: cuda gets the better model free, cpu keeps the fast one
    # unless the user explicitly asks for max.
    try:
        import torch as _t
        _gpu = _t.cuda.is_available()
    except Exception:
        _gpu = False
    model = "htdemucs_ft" if (quality == "max" or _gpu) else "htdemucs"
    stems_dir = os.path.join(SONGS, f"{name}_stems")
    work = os.path.join(stems_dir, "_demucs")
    os.makedirs(stems_dir, exist_ok=True)

    # THE STEM FORGE (Chezy 2026-08-02 "fully serverless GPU pipeline for the
    # audio to stem conversion, extreme speed"): SOTADAW_STEMS_REMOTE=1 runs
    # every heavy stage on cloud H100s first (tools/modal_stems.py) and
    # pre-fills the EXACT caches the stages below already check — the local
    # run becomes assembly + courts. Fail-open: any forge error (no token, no
    # net, cloud hiccup) keeps the local rails untouched.
    # THE DEFAULT IS THE FORGE (Chezy 2026-08-03, watching a UI-door import
    # crawl "htdemucs_ft on cpu... CPU?!"): the UI spawns stems_import.py
    # DIRECTLY (ui_main), bypassing the daw_mcp door — so the gate lives
    # HERE, under every door there is. Token present = ride the H100s;
    # SOTADAW_STEMS_REMOTE=0 or SOTADAW_NO_FORGE=1 opts out; =1 forces.
    _remote_env = os.environ.get("SOTADAW_STEMS_REMOTE", "")
    _forge_on = (_remote_env == "1"
                 or (_remote_env != "0"
                     and os.environ.get("SOTADAW_NO_FORGE") != "1"
                     and os.path.exists(os.path.expanduser("~/.modal.toml"))))
    if _forge_on and all(os.path.exists(os.path.join(stems_dir, f"{s}.wav"))
                         for s in ("drums", "bass", "other", "vocals")):
        # ALREADY FORGED (Chezy's double-click, 2026-08-03): the stems are on
        # disk — the reuse law below consumes them; re-forging would pay the
        # cloud twice for the same bytes.
        print("[stems] forge skip: 4 stems already local -> reuse law",
              flush=True)
        _forge_on = False
    # THE DISK COURT (2026-08-08, root hit 100% mid-import: zero-byte
    # forge_status, unplaced note seams, and last week a truncated drums.wav
    # crashed a whole run): imports write GBs — say so BEFORE the damage.
    try:
        _free_gb = shutil.disk_usage(stems_dir).free / 2 ** 30
        if _free_gb < 5.0:
            print(f"[stems] DISK NEARLY FULL: {_free_gb:.1f}GB free — an "
                  f"import writes GBs; truncated writes corrupt stems. "
                  f"Free space.", flush=True)
            _hb("DISK NEARLY FULL", 0.02,
                f"{_free_gb:.1f}GB free — imports write GBs; free space")
    except Exception:
        _free_gb = 999.0
    if _forge_on and _free_gb < 2.0:
        print(f"[stems] forge refused: {_free_gb:.1f}GB free cannot hold the "
              f"stem downloads (would truncate) -> local rails", flush=True)
        _forge_on = False
    if _forge_on:
        _fstat = os.path.join(stems_dir, "forge_status.json")
        try:
            import modal_stems
            _hb("forging stems (cloud GPU)", 0.03, "serverless H100 rail")
            m = modal_stems.prewarm(audio_path, stems_dir, hb=_hb)
            if m:
                try:
                    # stamp failures (ENOSPC) must never re-read as a forge
                    # failure — the placement above already succeeded
                    json.dump({"state": "forged", "cloud_wall_s":
                               m["timings"]["total"], "gpu": m.get("gpu"),
                               "t": time.time()}, open(_fstat, "w"))
                except Exception as se:
                    print(f"[stems] forge status stamp failed ({se}) — "
                          f"the forge itself SUCCEEDED (disk full?)",
                          flush=True)
                if all(os.path.exists(os.path.join(stems_dir, "6s", f"{s}.wav"))
                       for s in ("guitar", "piano", "other")):
                    os.environ["SOTADAW_6S"] = "1"   # consume the pre-filled
                    # microscope cache even on the CPU device path
        except Exception as fe:
            # NAME THE FAILURE (the squatter law, cloud edition): a silent
            # fallback reads as "the import is broken" 40 minutes later.
            # The dock banner, the log and the status file all carry the WHY
            # and the honest local expectation.
            why = f"{type(fe).__name__}: {str(fe)[:140]}"
            print(f"[stems] FORGE DOWN ({why}) -> local rails "
                  f"(the slow rung: expect minutes on GPU, tens of minutes "
                  f"on a busy CPU)", flush=True)
            _hb("FORGE DOWN -> local rails", 0.04,
                f"{why} — continuing locally, the slow rung")
            try:
                json.dump({"state": "fallback", "why": why,
                           "t": time.time()}, open(_fstat, "w"))
            except Exception:
                pass

    # REUSE LAW (speed): demucs separation is the expensive GPU pass (the whole
    # point of the retry path in ghost_e2e crashes) — a re-import of the SAME
    # song name that already separated cleanly skips straight to transcription
    # instead of paying for it twice. --retrofit remains the explicit manual
    # door for a stems dir that didn't come from THIS function.
    cached = {s: os.path.join(stems_dir, f"{s}.wav") for s in ("drums", "bass", "other", "vocals")}
    cached = {s: p for s, p in cached.items() if os.path.exists(p)}
    if len(cached) == 4:
        print(f"[stems] reusing {len(cached)} already-separated stems in "
              f"{os.path.basename(stems_dir)}/ (skip demucs)", flush=True)
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"
        gw = GpuWindow()
        if device == "cuda" and not gw.acquire():
            device = "cpu"
        try:
            cached = refine_vocals_roformer(cached, audio_path, name, device)
            return build_session(cached, audio_path, name, with_midi, bpm_override,
                                 0.0, t0, device,
                                 assist_ok=_assist_ok(device),
                                 spectral_mode=spectral_mode,
                                 instruments=instruments)
        finally:
            gw.release()

    import torch
    device = "cuda" if torch.cuda.is_available() else "cpu"
    gw = GpuWindow()
    if device == "cuda" and not gw.acquire():
        device = "cpu"                        # window closed: honest CPU from the start
    # THE SLOW-RUNG TRUTH (Chezy live 2026-07-11: a 2.5-min song "converting"
    # 23 min read as STUCK): when the GPU window is denied the import honestly
    # runs the CPU rung at ~10-20x the wall time — the heartbeat must SAY so,
    # with the why and the scale, so the banner reads as work, not a hang.
    if device == "cpu":
        why = "GPU busy" if _gpu else "no GPU"
        _hb("separating stems", 0.05,
            f"{model} on CPU ({why}) — the slow rung, ~10-20x GPU time")
    else:
        _hb("separating stems", 0.05, f"{model} on {device}")
    print(f"[stems] separating with {model} on {device}…", flush=True)
    # THE CLEAN SPLIT (Chezy 2026-07-11: "separation needs to be MUCH MUCH
    # better"): vocals FIRST, demucs sees only the instrumental — see
    # roformer_vocals_first. None -> the classic full-mix path, unchanged.
    sep_input, cascade = audio_path, None
    if device == "cuda":
        cascade = roformer_vocals_first(audio_path, stems_dir, work)
        if cascade:
            sep_input = cascade[1]

    # SUPERVISED SUBPROCESS (firing 106, the Yeshievishe Reid lesson): in-process
    # demucs dies WITH us when the system OOM-killer strikes on a loaded box —
    # no exception, no fallback, a progress bar frozen at 3%. As a child process
    # WE survive to read the verdict: negative returncode/137 = killed -> retry
    # on CPU with low-memory segmenting (--segment 7, htdemucs' window cap) and
    # bounded threads. Graceful CUDA OOM (stderr) takes the same retry.
    import subprocess as _sp
    def _run_demucs(dev, lowmem, mdl=None):
        # --float32: int16 at the stem boundary truncates -90dB tails BEFORE
        # capture/judge ever see them (the INT16 AMBUSH, killed at the source)
        cmd = [sys.executable, "-m", "demucs.separate", "-n", mdl or model,
               "-d", dev, "-o", work, "--filename", "{stem}.{ext}", "--float32"]
        if lowmem:
            cmd += ["--segment", "7", "-j", "1"]
        cmd.append(sep_input)
        if os.environ.get("SOTADAW_TEST_KILL_DEMUCS") == "1" and not lowmem:
            os.environ.pop("SOTADAW_TEST_KILL_DEMUCS")   # prove the retry path e2e
            return -9, "simulated OOM-kill (test hook)"
        env = dict(os.environ)
        if lowmem:
            env["PYTORCH_NO_CUDA_MEMORY_CACHING"] = "1"   # 2GB-class boxes (demucs docs)
        # STREAMED, NOT CAPTURED (Chezy 2026-07-16 "progress says STARTING till
        # the end"): demucs prints tqdm bars (one per model in its bag) — relay
        # their percent into the separation heartbeat window so the dock's bar
        # rides the actual GPU work. \r-updates never form lines: read raw
        # chunks and split on \r AND \n. Binary read1 never blocks waiting to
        # fill a buffer on a trickling pipe.
        import re as _re
        bag = 4 if (mdl or model) == "htdemucs_ft" else 1
        p = _sp.Popen(cmd, stdout=_sp.PIPE, stderr=_sp.STDOUT, env=env)
        lines, buf = [], b""
        done_bars, last_pc = 0, 0
        while True:
            ch = p.stdout.read1(4096)
            if not ch:
                break
            buf += ch
            while True:
                cr, nl = buf.find(b"\r"), buf.find(b"\n")
                cut = min(x for x in (cr, nl) if x >= 0) if (cr >= 0 or nl >= 0) else -1
                if cut < 0:
                    break
                seg, buf = buf[:cut], buf[cut + 1:]
                text = seg.decode("utf-8", "replace")
                if text.strip():
                    lines.append(text)
                    if len(lines) > 400:       # the retry court reads a TAIL, not a saga
                        del lines[:200]
                pcs = _re.findall(r"(\d{1,3})%\|", text)
                if pcs:
                    pc = min(100, int(pcs[-1]))
                    if pc < last_pc - 30:      # the bag's next model restarted its bar
                        done_bars = min(bag - 1, done_bars + 1)
                    last_pc = pc
                    frac = (done_bars + pc / 100.0) / bag
                    _hb("separating stems", 0.20 + 0.20 * frac,
                        f"{mdl or model} on {dev}"
                        + (" (low-mem retry)" if lowmem else ""))
        p.wait()
        tail = buf.decode("utf-8", "replace").strip()
        if tail:
            lines.append(tail)
        return p.returncode, "\n".join(lines)
    def _why(rc, out):
        if rc < 0 or rc == 137:
            return "OOM-killed by the system (box under load)"
        return "CUDA out of memory" if "out of memory" in out.lower() else f"exit {rc}"
    used_model = model
    try:
        rc, out = _run_demucs(device, lowmem=False)
        if rc != 0 and device == "cuda":
            # MIDDLE RUNG (the aranyanyara lesson): a 6GB card OOMs htdemucs_ft
            # at full window on LONG tracks but fits fine at --segment 7 — stay
            # on the GPU (~20x CPU) before surrendering to the CPU rung, which
            # the system OOM-killer hunts whenever the box is loaded.
            print(f"[stems] demucs died: {_why(rc, out)} -> GPU low-mem retry "
                  f"(--segment 7)…", flush=True)
            rc, out = _run_demucs("cuda", lowmem=True)
        if rc != 0:
            # LAST RUNG: CPU, low-mem, and the SINGLE htdemucs model — _ft's
            # bag-of-4 is 4x the work, exactly what gets a slow CPU pass killed.
            print(f"[stems] demucs died: {_why(rc, out)} -> low-mem CPU retry "
                  f"(htdemucs, --segment 7, single-threaded)…", flush=True)
            rc, out = _run_demucs("cpu", lowmem=True, mdl="htdemucs")
            device, used_model = "cpu", "htdemucs"
            if rc != 0:
                tail = "\n".join(l for l in out.splitlines()
                                  if "error" in l.lower() or "Trace" in l)[-300:]
                raise SystemExit(f"demucs failed twice (exit {rc}). {tail or out[-200:]}")
        src_dir = os.path.join(work, used_model)
        stems = {}
        for stem in ("drums", "bass", "other", "vocals"):
            if cascade and stem == "vocals":
                continue        # demucs' vocals-of-the-instrumental is ~silence;
            p = os.path.join(src_dir, f"{stem}.wav")   # roformer's is THE vocal
            if os.path.exists(p):
                dst = os.path.join(stems_dir, f"{stem}.wav")
                shutil.move(p, dst)
                stems[stem] = dst
        shutil.rmtree(work, ignore_errors=True)
        if not stems:
            raise SystemExit("demucs produced no stems")
        if cascade:
            stems["vocals"] = cascade[0]
        stems = refine_vocals_roformer(stems, audio_path, name, device)
        t_sep = time.time() - t0
        return build_session(stems, audio_path, name, with_midi, bpm_override,
                             t_sep, t0, device,
                             assist_ok=_assist_ok(device),
                             spectral_mode=spectral_mode,
                             instruments=instruments)
    finally:
        gw.release()                           # the daemon resumes no matter what


def melodic_lanes(part, wav_in, notes, fallback_src, name, bpm):
    """THE STREAM SPLIT landing (F2, docs/IMPORT_FINALE.md) — true lengths
    FIRST, then voices. Pass 1 builds a kit for the WHOLE part: its
    calibration measures the TRUE ring lengths (the sustain law, F1
    poly-bounded). THE SPLIT judges on those true lengths — raw
    transcription lens read everything as fast surface and nothing ever
    split (the goldenbrown re-heal receipt). A decisive split re-kits each
    stream from ITS OWN notes (a pad lane rings sustains, a lead lane
    plucks attacks); an indecisive part lands pass 1's kit as one lane.
    Returns finished track dicts; shared by build_session and
    other_decompose so the paths cannot drift."""
    base_src, base_notes = fallback_src, notes
    try:
        import source_kit
        pk, pn = source_kit.build_pitched_kit(
            wav_in, notes, f"{name}_{part}", bpm=bpm, role="melodic")
        if pk:
            base_src = {"kind": "sample", "kit": pk}
            base_notes = pn
            print(f"[stems] pitched kit: kits/{pk} ({len(pn)} real-pitch "
                  f"notes, the record's own timbre)", flush=True)
    except Exception as pe:
        print(f"[stems] pitched kit skipped for {part} ({pe}) "
              f"-> generic voice", flush=True)
    try:
        import note_streams
        streams = note_streams.split_streams(base_notes)
    except Exception:
        streams = [("all", base_notes)]
    if len(streams) <= 1:
        return [{"name": f"{part}_sketch", "source": base_src,
                 "gainDb": -1.5, "muted": False, "notes": base_notes}]
    print(f"[stems] stream split: {part} {len(base_notes)} notes -> "
          + " + ".join(f"{nm} {len(ns)}" for nm, ns in streams), flush=True)
    lanes = []
    for nm, ns in streams:
        lane = f"{part}_{nm}"
        use_src, use_notes = base_src, ns      # pass-1 kit covers the range
        try:
            import source_kit
            pk2, pn2 = source_kit.build_pitched_kit(
                wav_in, ns, f"{name}_{lane}", bpm=bpm, role="melodic")
            if pk2:
                use_src = {"kind": "sample", "kit": pk2}
                use_notes = pn2
                print(f"[stems] pitched kit: kits/{pk2} ({len(pn2)} notes)",
                      flush=True)
        except Exception as pe:
            print(f"[stems] stream kit skipped for {lane} ({pe}) "
                  f"-> the part kit", flush=True)
        lanes.append({"name": lane, "source": use_src, "gainDb": -1.5,
                      "muted": False, "notes": use_notes})
    return lanes


def land_drum_lanes(drums_wav, name, bpm):
    """The drum rail, one kernel for BOTH homes (F4, docs/IMPORT_FINALE.md):
    transcribe (physical pieces when drumsep may run / is cached, band lanes
    otherwise) -> runs court -> source kit -> exemplar assignment -> named
    AWARE lanes. Returns (drum_tracks, docket). build_session calls it at
    import; tools/import_finisher.py calls it again with pieces cached to
    upgrade the landed lanes — same code, the paths cannot drift."""
    docket = []
    dn = None
    try:
        import transcribe_stems as ts
        dn, drec = ts.drum_notes(drums_wav, bpm)
        print(f"[stems] drums rail: {drec}", flush=True)
    except Exception as de:
        print(f"[stems] drums v2 failed ({type(de).__name__}: {de}) "
              f"-> 3-band fallback", flush=True)
        import midi_polish
        dn = midi_polish.drum_sketch(drums_wav, bpm)
    if dn and os.environ.get("SOTADAW_NO_COURT") != "1":
        # PLAUSIBILITY COURT, runs judge (Chezy live 2026-07-11: "no way
        # it'll be 32 beats of a bass drum unless it's a double bass — 100%
        # confident"): dense same-family runs must PROVE their family on the
        # stem's own slices. Runs BEFORE the source kit builds, so the kit
        # is built from true labels (a mislabeled hat roll would otherwise
        # donate its slices to the KICK voice).
        try:
            import import_court
            n0 = len(dn)
            dn, crr = import_court.court_runs(dn, drums_wav, bpm)
            docket += crr
            for r_ in crr:
                print(f"[court] {import_court.fmt(r_)}", flush=True)
            if len(dn) != n0:
                print(f"[court] drums {n0} -> {len(dn)} hits "
                      f"(bleed doubles dropped)", flush=True)
        except Exception as ce_:
            print(f"[stems] runs court skipped ({ce_})", flush=True)
    drum_tracks = []
    if dn and len(dn) >= 16:
        # SOURCE KIT (Chezy's identity law): the sketch triggers the
        # record's OWN hits — per-lane exemplars sliced out of the
        # stem — never a stock GM kit. gm_drums stays the fallback
        # only when the stem yields too few clean lanes.
        drum_kit = "gm_drums"
        try:
            import source_kit
            sk = source_kit.build_source_kit(drums_wav, dn,
                                             f"{name}_drums", bpm=bpm)
            if sk:
                drum_kit = sk
                print(f"[stems] source kit: kits/{sk} "
                      f"(the record's own hits)", flush=True)
                try:                   # wave 2: each hit plays the
                    mv = source_kit.assign_exemplars(   # exemplar
                        drums_wav, dn, sk, bpm=bpm)     # that IS
                    if mv:                              # its moment
                        print(f"[stems] exemplar assignment: {mv} "
                              f"hits -> alt voices", flush=True)
                except Exception as ae:
                    print(f"[stems] exemplar assign skipped ({ae})",
                          flush=True)
        except Exception as ke:
            print(f"[stems] source kit skipped ({ke}) -> gm_drums",
                  flush=True)
        # DRUM AWARENESS (Chezy live, 2026-07-09: "the drums arent
        # aware of what sound is hi-hat, bass, etc"): every voice
        # gets its OWN NAMED track — Kick/Snare/Hats/Perc/Cymbals —
        # all triggering the record's own kit, so repositioning a
        # hat never means hunting pitches inside a wall of hits.
        lane_of = lambda p: ("Kick" if p in (33, 35, 36) else
                             "Snare" if p in (34, 37, 38, 40) else
                             "Hats" if p in (26, 41, 42, 44, 46) else
                             "Cymbals" if p in (49, 51, 52, 55, 57, 59)
                             else "Perc")
        # families include source_kit.ALT_GM alt voices (wave 2):
        # 33/35 kick, 34/40 snare, 41/44 closed-hat, 26 open-hat
        lanes = {}
        for n_ in dn:
            lanes.setdefault(lane_of(int(n_["pitch"])), []).append(n_)
        counts = []
        for lname in ("Kick", "Snare", "Hats", "Perc", "Cymbals"):
            if lanes.get(lname):
                drum_tracks.append({"name": lname,
                                    "source": {"kind": "sample",
                                               "kit": drum_kit},
                                    "gainDb": -1.5, "muted": False,
                                    "notes": lanes[lname]})
                counts.append(f"{lname} {len(lanes[lname])}")
        print(f"[stems] drums AWARE: {' / '.join(counts)} "
              f"({len(dn)} hits on kits/{drum_kit})", flush=True)
    return drum_tracks, docket


def build_session(stems, audio_path, name, with_midi=True, bpm_override=None,
                  t_sep=0.0, t0=None, device="cpu", assist_ok=True,
                  spectral_mode=None, instruments="original"):
    t0 = t0 or time.time()
    court_docket = []                  # PLAUSIBILITY COURT receipts (both sites)
    # STAGE RECEIPTS (F4.1, docs/IMPORT_FINALE.md): "45 minutes" must never
    # be a mystery again — every stage records its wall seconds, the whole
    # ledger lands in <stems>/import_stages.json with the device decision.
    stage_secs = {"separation": round(t_sep, 1)}
    _t_last = [time.time()]

    def _ckpt(stage):
        now = time.time()
        stage_secs[stage] = round(stage_secs.get(stage, 0.0)
                                  + (now - _t_last[0]), 1)
        _t_last[0] = now
        print(f"[stage] {stage}: {stage_secs[stage]}s", flush=True)

    a2 = load_analyze2()
    _hb("tempo + key", 0.44, "")
    if bpm_override:
        bpm, conf = float(bpm_override), 1.0
    else:
        bpm, conf = estimate_bpm(stems.get("drums", next(iter(stems.values()))))
        # octave heuristic: low-confidence sub-85 detections are usually the half-tempo
        # alias of a modern-genre track (most live in 85-180)
        if conf < 0.3 and bpm < 85 and bpm * 2 <= 200:
            bpm *= 2
        elif bpm < 90 and "drums" in stems:
            # TATUM LAW: even a CONFIDENT sub-90 grid can be the half-time alias
            # (Detroit 69.8 = 139.6). Evidence: strong onsets OCCUPYING the odd
            # 1/32 cells of the detected grid — a truly slow track leaves them
            # empty. Doubling BEFORE any beat math keeps everything coherent.
            try:
                import transcribe_stems as ts
                if ts.tatum_wants_double(stems["drums"], bpm):
                    print(f"[stems] tatum law: {bpm} is the half-time alias -> "
                          f"{round(bpm * 2, 1)} (onsets occupy the 1/32 lattice)",
                          flush=True)
                    bpm = round(bpm * 2, 1)
            except Exception:
                pass
    from scipy.io import wavfile
    import numpy as np
    mix_x, sr, x = None, None, None
    for s, p in stems.items():
        ssr, sx = wavfile.read(p)
        if sx.dtype.kind == "i":
            sx = sx.astype(np.float64) / np.iinfo(sx.dtype).max
        if sx.ndim > 1:
            sx = sx.mean(axis=1)
        if s == "other" or x is None:
            sr, x = ssr, sx                    # key comes from the harmonic stem
        mix_x = sx if mix_x is None else (mix_x[:len(sx)] + sx[:len(mix_x)])
    key, key_conf = a2.estimate_key(x, sr)
    try:   # KEYVOTE first (battery 7/12 vs chroma 4/12): transcription-based — bass
        # testimony + third evidence on NOTES beat raw spectrum mass (lab notes vindicated)
        from keyvote import vote as _keyvote
        kv_key, kv_conf, kv_n = _keyvote(audio_path)
        if kv_key and kv_n >= 12:
            key, key_conf = kv_key, kv_conf
    except Exception:
        pass
    dur_s = len(mix_x) / sr
    beats = dur_s / (60.0 / bpm)
    length_bars = max(1, math.ceil(beats / 4.0))

    rel = lambda p: os.path.relpath(p, ROOT)
    spb = 60.0 / bpm
    # W9 stems->slots v2: windows picked ONCE from the summed mix by energy +
    # spectral distinctness (the drop is rarely at bar 0), then every stem is
    # sliced at the SAME offsets so each scene is a coherent song section.
    loop_offs = pick_loop_windows(mix_x, sr, bpm)
    if not loop_offs:                          # very short material: one window at 0
        loop_offs = [0.0]
    tracks = []
    for stem in ("drums", "bass", "other", "vocals"):
        if stem in stems:
            slots = [{"name": f"{stem} {chr(65 + k)}", "lengthBeats": 32.0,
                      "audioFile": rel(stems[stem]), "offsetSec": off,
                      "sourceBpm": round(bpm, 2)}     # warp: loop follows the song tempo
                     for k, off in enumerate(loop_offs)]
            # -1.5 STAGING LAW: a mastered record peaks ~-0.1dBTP; at 0dB the
            # stem sum sits ON the -1.2 truepeak wall and every drum transient
            # takes standing gain reduction ("HEAVILY LIMITED", Chezy
            # 2026-07-08). All content lanes carry the same -1.5 trim so
            # either listening mode (audio OR sketch) clears the wall with the
            # wall idle, and A/B stays level-fair.
            # THE EDIT-FIRST LAW (Chezy live, 2026-07-09): "THE GOAL IS TO
            # TRANSFORM AN AUDIO SONG TO COMPLETELY EDITABLE MIDI". The MIDI
            # reconstruction IS the product and sounds by default; the raw
            # stems are the muted A/B reference (unmute = hear the record).
            # The old default (audio loud, 8 muted MIDI lanes) made the user
            # hand-solve a 12-lane mute puzzle and hear a pileup.
            # REFERENCE TRUTH LAW (A2M byte-par, 2026-07-10): the timeline stem
            # ref plays UNWARPED. The song grid was BORN from this record, so
            # sourceBpm==bpm — a ratio-1.0 warp — yet SoundTouch still smears
            # transients AND drifts (measured: clip onsets F1 0.27 vs its own
            # source file at ANY constant lag, while the MIDI lanes hit 0.96).
            # A/B against a corrupted reference reads as "the MIDI is off".
            # Launcher slots keep sourceBpm — loops must follow tempo changes.
            tracks.append({"name": stem, "source": {"kind": "audio", "id": stem},
                           "gainDb": -1.5, "muted": with_midi,
                           "audioClips": [{"file": rel(stems[stem]),
                                           "startBeat": 0}],
                           "notes": [], "slots": slots})

    sketches = 0
    engines = {}
    defer_pieces = False               # F4: drum microscope -> finisher?
    if with_midi:
        # THE HARMONIC MICROSCOPE: when htdemucs_6s can hear real guitar/piano
        # inside 'other', transcribe THOSE on dedicated lanes and give the
        # other_sketch the cleaner residual. Audio lanes stay 4-stem truth.
        # THE DECOMPOSITION LAW (2026-07-15): when the parts take EVERYTHING
        # (residual inaudible — goldenbrown: guitar -26dB + piano -36dB left
        # a -68dB residual), other_sketch must NOT be born from the full wet
        # stem — it would duplicate the parts as a third blurred lane.
        assist_lanes = []
        other_src = stems.get("other")
        skip_other = False
        try:
            if not assist_ok:
                raise RuntimeError(
                    "no CUDA for the 6s pass (SOTADAW_6S=1 forces, "
                    "SOTADAW_NO_6S=1 kills)")
            _hb("harmonic microscope (6-stem)", 0.44,
                "listening for real guitar/piano inside 'other'")
            assist = six_stem_assist(stems, os.path.dirname(next(iter(stems.values()))))
            for s in ("guitar", "piano"):
                if s in assist and _stem_audible(assist[s]):
                    assist_lanes.append((s, assist[s]))
            if assist_lanes:
                if assist.get("other") and _stem_audible(assist["other"]):
                    other_src = assist["other"]
                    print(f"[stems] 6s microscope: "
                          f"{'+'.join(s for s, _ in assist_lanes)} heard -> "
                          f"dedicated lanes + residual other", flush=True)
                else:
                    skip_other = True
                    print(f"[stems] 6s microscope: "
                          f"{'+'.join(s for s, _ in assist_lanes)} heard, "
                          f"residual ~empty -> 'other' fully decomposed",
                          flush=True)
        except Exception as ae:
            print(f"[stems] 6s assist skipped ({type(ae).__name__}: {ae})", flush=True)
        _ckpt("6s_microscope")

        def land_melodic(part, wav_in, notes, fallback_src, engine_tag):
            """Delegates to melodic_lanes (module kernel, F2): TRUE lengths
            first (pass-1 kit measures the ring), split on them, per-stream
            kits. Registers engines for the chord-prior gate."""
            nonlocal sketches
            for tr in melodic_lanes(part, wav_in, notes, fallback_src,
                                    name, bpm):
                tracks.append(tr)
                engines[tr["name"]] = engine_tag
                sketches += 1

        sketch_src = {"bass": ({"kind": "faust", "id": "sub_clean"}, "bass"),
                      "other": ({"kind": "sample", "kit": "piano"}, "melodic"),
                      "vocals": ({"kind": "sample", "kit": "choir"}, "vocal")}
        for _si, (stem, (src, role)) in enumerate(sketch_src.items()):
            if stem not in stems:
                continue
            if stem == "other" and skip_other:
                continue                       # THE DECOMPOSITION LAW (above)
            _hb(f"transcribing {stem}", 0.45 + 0.05 * _si,
                "CPU rung" if device == "cpu" else "")
            print(f"[stems] transcribing {stem}…", flush=True)
            wav_in = other_src if stem == "other" else stems[stem]
            notes, engines[f"{stem}_sketch"] = transcribe_v2(wav_in, bpm,
                                                             role=role, key=key)
            if stem == "other" and len(notes) >= 4:
                # EDITABLE PASS (Chezy live, 2026-07-09: "impossible to edit"):
                # the harmonic microscope's coverage-first output becomes a
                # roll a human can work — chord blocks, merged stutters,
                # per-bar salience cap. The feel stays (no hard quantize).
                import midi_polish
                n0 = len(notes)
                notes = midi_polish.editable(notes, bpm=bpm)
                print(f"[stems] editable pass: other {n0} -> {len(notes)} notes",
                      flush=True)
                land_melodic("other", wav_in, notes, src,
                             engines.get("other_sketch", "basic-pitch"))
                if os.environ.get("SOTADAW_ID_LANES") == "1":
                    try:
                        import source_kit
                        ik, inotes = source_kit.build_phrase_kit(
                            wav_in, notes, f"{name}_other_id", bpm=bpm)
                        if ik and len(inotes) >= 3:
                            tracks.append({"name": "other_identity",
                                           "source": {"kind": "sample",
                                                      "kit": ik},
                                           "gainDb": -1.5, "muted": True,
                                           "notes": inotes})
                            sketches += 1
                            print(f"[stems] identity lane: kits/{ik} "
                                  f"({len(inotes)} phrases replay the record)",
                                  flush=True)
                    except Exception as ie:
                        print(f"[stems] identity lane skipped for other "
                              f"({ie})", flush=True)
                continue                       # streams landed the lanes
            if len(notes) >= 4:
                # REAL-NOTES IDENTITY LAW (Chezy 2026-07-08): the roll must
                # show THE MUSIC — real transcribed pitches — and every pitch
                # triggers the record's OWN timbre (per-pitch exemplar zones,
                # range-filled so edits keep speaking). Generic voice only
                # when the stem is too sparse for exemplars.
                # VOCAL EXCEPTION (Chezy live, 2026-07-09: "why is the vocals
                # chopped audio from the track itself?! I TOLD YOU NOT TO"):
                # the vocal lane NEVER plays slices of the user's own record —
                # its melody is TRUE MIDI on a generic voice, and the vocal
                # SOUND comes from the local singing synth (vocals_sung below).
                use_src, use_notes = src, notes
                if stem != "vocals":
                    try:
                        import source_kit
                        pk, pnotes = source_kit.build_pitched_kit(
                            wav_in, notes, f"{name}_{stem}", bpm=bpm, role=role)
                        if pk:
                            use_src = {"kind": "sample", "kit": pk}
                            use_notes = pnotes
                            print(f"[stems] pitched kit: kits/{pk} "
                                  f"({len(pnotes)} real-pitch notes, the record's "
                                  f"own timbre)", flush=True)
                    except Exception as pe:
                        print(f"[stems] pitched kit skipped for {stem} ({pe}) "
                              f"-> generic voice", flush=True)
                tracks.append({"name": f"{stem}_sketch", "source": use_src,
                               "gainDb": -1.5, "muted": False, "notes": use_notes})
                sketches += 1
                # THE IDENTITY LANE (MPC chop rail + audio=MIDI receipt,
                # 99.6-99.98% spectral) is OPT-IN ONLY now: SOTADAW_ID_LANES=1.
                # Chezy live-rejected chop lanes in the default product twice
                # ("completely editable MIDI... I TOLD YOU NOT TO DO THAT").
                # Never for vocals, even opted in.
                if os.environ.get("SOTADAW_ID_LANES") == "1" and stem != "vocals":
                    try:
                        import source_kit
                        ik, inotes = source_kit.build_phrase_kit(
                            wav_in, notes, f"{name}_{stem}_id", bpm=bpm)
                        if ik and len(inotes) >= 3:
                            tracks.append({"name": f"{stem}_identity",
                                           "source": {"kind": "sample", "kit": ik},
                                           "gainDb": -1.5, "muted": True,
                                           "notes": inotes})
                            sketches += 1
                            print(f"[stems] identity lane: kits/{ik} "
                                  f"({len(inotes)} phrases replay the record)",
                                  flush=True)
                    except Exception as ie:
                        print(f"[stems] identity lane skipped for {stem} ({ie})",
                              flush=True)
            if stem == "vocals" and len(notes) >= 4 \
                    and os.environ.get("SOTADAW_ID_LANES") == "1":
                try:                       # the flow's other half: consonant hits
                    import transcribe_stems as ts
                    chops = ts.vocal_chops(stems[stem], bpm, notes)
                    if chops:
                        tracks.append({"name": "vocals_chops",
                                       "source": {"kind": "sample", "kit": "gm_drums"},
                                       "gainDb": -8, "muted": True, "notes": chops})
                        sketches += 1
                        print(f"[stems] vocal chops: {len(chops)} consonant hits",
                              flush=True)
                except Exception:
                    pass
        _ckpt("transcribe_sketches")
        for s, p in assist_lanes:
            _hb(f"transcribing {s}", 0.6, "")
            print(f"[stems] transcribing {s} (6s)…", flush=True)
            notes, eng6 = transcribe_v2(p, bpm, role="melodic", key=key)
            engines[f"{s}_sketch"] = eng6
            if len(notes) >= 8:
                import midi_polish
                n0 = len(notes)
                notes = midi_polish.editable(notes, bpm=bpm)
                print(f"[stems] editable pass: {s} {n0} -> {len(notes)} notes",
                      flush=True)
                src = ({"kind": "sample", "kit": "piano"} if s == "piano"
                       else {"kind": "faust", "id": "pluck"})
                land_melodic(s, p, notes, src, eng6)
        _ckpt("transcribe_parts")
        if "drums" in stems:
            # THE LANDING DEADLINE (F4, docs/IMPORT_FINALE.md — "45 minutes
            # is unacceptable"): the drum-piece microscope (mdx23c, CPU
            # BY DESIGN) costs 4-6x realtime — ~15-20 min of a 3-4 min
            # song's import, ALL of it blocking the landing. Unless the
            # pieces are already cached (re-import) the inline pass lands
            # the byte-proven BAND rail now and the detached finisher
            # (tools/import_finisher.py) re-lands the SAME kernel with
            # pieces later — identical final state, minutes-earlier landing
            # (THE QUALITY INVARIANT: same models, same thresholds, every
            # stage still runs). SOTADAW_IMPORT_INLINE=1 keeps everything
            # inline (batteries, determinism rigs).
            pieces_cached = os.path.exists(os.path.join(
                os.path.dirname(stems["drums"]), "drum_pieces", "kick.wav"))
            defer_pieces = (not pieces_cached
                            and os.environ.get("SOTADAW_IMPORT_INLINE") != "1"
                            and os.environ.get("SOTADAW_NO_DRUMSEP") != "1")
            if defer_pieces:
                os.environ["SOTADAW_NO_DRUMSEP"] = "1"
                print("[stage] drum microscope DEFERRED to the finisher "
                      "(band lanes land now; physical pieces upgrade in "
                      "background)", flush=True)
            _hb("drum lanes", 0.66,
                "band rail now" + (", physical pieces upgrade in background"
                                   if defer_pieces else ""))
            try:
                dtracks, ddocket = land_drum_lanes(stems["drums"], name, bpm)
                court_docket += ddocket
                tracks += dtracks
                sketches += len(dtracks)
            except Exception as de:
                print(f"[stems] drum sketch skipped: {de}", flush=True)
            finally:
                if defer_pieces:
                    os.environ.pop("SOTADAW_NO_DRUMSEP", None)
            _ckpt("drums_rail")

    if "drums" in stems:                       # W11: the import FEEDS THE FACTORY —
        try:                                   # the record's timing DNA becomes a
            import groove                      # named, transferable groove + KG node
            print(f"[stems] {groove.extract_audio(stems['drums'], bpm, f'import_{name}')}", flush=True)
        except Exception as ge:
            print(f"[stems] groove extraction skipped: {ge}", flush=True)

    nscenes = max((len(t.get("slots", [])) for t in tracks), default=0)
    song = {"version": 2, "bpm": bpm, "lengthBars": length_bars, "masterGainDb": 0.0,
            "master": [{"id": "fx_truepeak", "params": {"ceiling": -1.2}}], "tracks": tracks}
    if nscenes:
        song["scenes"] = [{"name": f"Part {chr(65 + i)} @bar{int(round(loop_offs[i] / spb / 4)) + 1}"}
                          for i in range(nscenes)]
    if key:
        song["key"] = key
    if instruments == "ear" and with_midi:
        # THE INSTRUMENT EAR (Chezy 2026-07-11: the user chooses at conversion —
        # the record's ORIGINAL instruments, or the system PICKS by ear).
        # Closed-loop: candidates render the lane's own notes through the real
        # engine and the winner is MEASURED against the stem (tools/ear_pick.py;
        # the self-ID battery is the accuracy law). Original mode = untouched.
        try:
            import ear_pick
            roles = {"bass": "bass", "vocals": "vocal", "piano": "keys",
                     "guitar": "guitar", "other": "melodic"}
            ear_report = {}
            for t in song["tracks"]:
                nm = t.get("name", "")
                if not nm.endswith("_sketch") or not t.get("notes"):
                    continue
                stem_nm = nm[:-len("_sketch")]
                wavp = stems.get(stem_nm)
                if not wavp or not os.path.exists(wavp):
                    continue
                _hb("picking instruments by ear", 0.87, nm)
                r = ear_pick.pick_voice(wavp, t["notes"], bpm,
                                        role=roles.get(stem_nm, "melodic"))
                if r:
                    t["source"] = {"kind": "faust", "id": r["voice"]}
                    ear_report[nm] = {k: r[k] for k in
                                      ("voice", "score", "mode", "why")}
                    print(f"[ear] {nm}: {r['voice']} ({r['mode']}, "
                          f"d={r['score']}) — {r['why']}", flush=True)
                    # THE GENERATIVE HANDOFF (BEST_DAW_30 #8): when the whole
                    # palette is FAR from the stem (pick distance past the
                    # forge gate), FORGE a fitted voice instead of settling —
                    # sound_clone's coordinate descent on a template family,
                    # kept only when it measures CLOSER than the pick.
                    # SOTADAW_CLONE_ON_IMPORT=0 kills; fail-open to the pick.
                    _fgate = float(os.environ.get("SOTADAW_FORGE_GATE", "0.9"))
                    if (os.environ.get("SOTADAW_CLONE_ON_IMPORT", "1") != "0"
                            and stem_nm not in ("drums", "vocals")
                            and float(r.get("score", 0)) > _fgate):
                        try:
                            import sound_clone
                            _hb("forging a closer voice", 0.88, nm)
                            fo = sound_clone.clone(
                                wavp, f"{name}_{stem_nm}",
                                budget=int(os.environ.get(
                                    "SOTADAW_FORGE_BUDGET", "24")),
                                quiet=True)
                            if (fo.get("verdict") == "FORGED"
                                    and fo["distance"] < float(r["score"])):
                                t["source"] = fo["source"]
                                ear_report[nm]["forged"] = {
                                    "template": fo["source"]["id"],
                                    "distance": fo["distance"]}
                                print(f"[ear] {nm}: FORGED "
                                      f"{fo['source']['id']} d={fo['distance']}"
                                      f" (pick was {r['score']})", flush=True)
                        except Exception as fe:
                            print(f"[ear] {nm}: forge skipped "
                                  f"({type(fe).__name__}: {fe})", flush=True)
                else:
                    print(f"[ear] {nm}: window silent — original source kept",
                          flush=True)
            if ear_report:
                sdir = os.path.dirname(next(iter(stems.values()), ""))
                if sdir and os.path.isdir(sdir):
                    json.dump(ear_report,
                              open(os.path.join(sdir, "ear.json"), "w"), indent=1)
        except Exception as ee:
            print(f"[stems] ear picking skipped ({type(ee).__name__}: {ee}) — "
                  f"original instruments kept", flush=True)
    _hb("structure", 0.80, "section boundaries")
    try:                                       # EARS v4b: real section boundaries
        import segment as seg                  # (Foote novelty; precision-tuned —
        witness = audio_path if audio_path.lower().endswith(".wav") \
            else stems.get("drums")            # every boundary emitted is real)
        if witness:
            sr_ = seg.segment(witness, bpm=bpm, vocal_path=stems.get("vocals"))
            labs = sr_.get("labels", [])
            secs = [{"name": labs[0] if labs else "start", "startBar": 0.0}]
            secs += [{"name": (labs[i + 1] if i + 1 < len(labs) else f"part {i + 2}"),
                      "startBar": float(b - 1)}
                     for i, b in enumerate(sr_.get("bars", [])) if b - 1 > 0]
            if len(secs) > 1:
                song["sections"] = secs
                print(f"[stems] structure: {len(secs)} sections at bars "
                      f"{[int(s['startBar']) + 1 for s in secs]}", flush=True)
    except Exception as se:
        print(f"[stems] segmentation skipped: {se}", flush=True)
    _hb("chords + priors", 0.82, "bar-wise vote over the sketches")
    try:                                       # THE CHORD LANE on every import:
        import chordvote                       # bar-wise vote over the sketches
        ch = chordvote.chord_map(song, audio_wav=stems.get("other"), audio_bpm=bpm)
        # (symbols + a CQT-chroma witness from the harmonic 'other' stem — V54)
        if len(ch) >= 2:
            song["chords"] = ch
            runs, prev = 0, None
            for c in ch:
                if c["chord"] != prev:
                    runs += 1
                    prev = c["chord"]
            print(f"[stems] chords: {len(ch)} bars voted, {runs} changes "
                  f"(first: {' '.join(c['chord'] for c in ch[:4])}…)", flush=True)
            # CHORD PRIOR (song-to-MIDI round 2): the voted lane judges the harmonic
            # sketch's weak guesses — snap to chord tones or die; strong notes and
            # diatonic passing tones untouched (midi_polish.chord_snap).
            # ENGINE GATE: priors exist to repair basic-pitch GUESSES. An fcpe
            # line (84% RPA vs an independent witness) is testimony, not a guess
            # — 'correcting' it would erase real chromatic 808 slides.
            import midi_polish
            for t in song["tracks"]:
                eng = engines.get(t.get("name"), "basic-pitch")
                if _other_family(t.get("name", "")) and t.get("notes"):
                    n0 = len(t["notes"])
                    c0 = midi_polish.chord_consistency(t["notes"], ch, key=song.get("key"))
                    t["notes"] = midi_polish.chord_snap(t["notes"], ch, key=song.get("key"))
                    c1 = midi_polish.chord_consistency(t["notes"], ch, key=song.get("key"))
                    print(f"[stems] chord prior: {t['name']} {n0} -> {len(t['notes'])} notes, "
                          f"weak-note consistency {c0:.0%} -> {c1:.0%}", flush=True)
                elif t.get("name") == "bass_sketch" and t.get("notes") \
                        and not eng.startswith("fcpe"):
                    # BASS grammar prior: weak strays snap to root/fifth; weak
                    # octave-outliers fold toward the line (midi_polish.bass_prior)
                    c0 = midi_polish.chord_consistency(t["notes"], ch, key=song.get("key"))
                    t["notes"] = midi_polish.bass_prior(t["notes"], ch, key=song.get("key"))
                    c1 = midi_polish.chord_consistency(t["notes"], ch, key=song.get("key"))
                    print(f"[stems] bass prior: weak-note consistency {c0:.0%} -> {c1:.0%}",
                          flush=True)
    except Exception as ce:
        print(f"[stems] chord vote skipped: {ce}", flush=True)
    if os.environ.get("SOTADAW_NO_COURT") != "1":
        _hb("plausibility court", 0.84, "key/snap/echo verdicts")
        # PLAUSIBILITY COURT, melodic judges (same live directive: "no way
        # by accident there'll be two notes off key ... no non snap to note
        # ... no echoey weird sounding music"): isolated off-key accidents
        # snap to scale (pattern-supported = intent, kept), echo-tap chains
        # die, consensus lanes lose their jitter. Every verdict receipted.
        try:
            import import_court
            crr = import_court.hold_court(song, courts=("key", "snap", "echo",
                                                        "length"))
            court_docket += crr
            for r_ in crr:
                print(f"[court] {import_court.fmt(r_)}", flush=True)
        except Exception as ce_:
            print(f"[stems] plausibility court skipped ({ce_})", flush=True)
    if court_docket:
        try:                               # the docket rides with the stems —
            sdir = os.path.dirname(next(iter(stems.values()), ""))
            if sdir and os.path.isdir(sdir):   # WHY answers live next to WHAT
                json.dump(court_docket,
                          open(os.path.join(sdir, "court.json"), "w"), indent=1)
        except Exception:
            pass
    _ckpt("chords_court")
    out = os.path.join(SONGS, f"{name}.json")
    json.dump(song, open(out, "w"), indent=1)
    # THE REFERENCE CIRCLE (R2): the DNA this import just computed — bpm/key
    # (+confidences), sections, voted chords, learned groove, the mix's own
    # ears — becomes a KG (:Reference) node the agent can match against
    # ("make it sound like this record"). Idempotent by source sha1; a down
    # graph can NEVER fail an import.
    try:
        _feed_reference_circle(audio_path, name, song, conf, key_conf)
    except Exception as rce:
        print(f"[stems] reference circle skipped "
              f"({type(rce).__name__}: {rce})", flush=True)
    if spectral_mode:
        # RECONSTRUCTION LANES per stem (docs/SPECTRAL_CAPTURE.md): each stem
        # becomes editable spectral MIDI + its exact render; ~6-7x realtime
        # per stem — an import-time investment, announced honestly.
        import spectral as spx
        for stem, wav in stems.items():
            try:
                if not _stem_audible(wav):
                    print(f"[stems] spectral: '{stem}' inaudible — skipped", flush=True)
                    continue
                print(f"[stems] spectral capture of '{stem}' ({spectral_mode})…",
                      flush=True)
                cap = spx.capture(wav, name=name, bpm=bpm, mode=spectral_mode,
                                  prefix=f"spectral_{stem}",
                                  prog=spx.Prog([("load", 3), ("analyze", 38),
                                                 ("carve", 22), ("notes", 7),
                                                 ("render", 22), ("residual", 5),
                                                 ("verify", 3)],
                                                label=f"spectral:{stem}"))
                spx.inject_into_song(cap, out)
                f = cap.get("fidelity", {})
                print(f"[stems] spectral '{stem}': {f.get('spectral_pct')}% "
                      f"si {f.get('si_sdr_db')}dB byte_exact={f.get('byte_exact')}",
                      flush=True)
            except Exception as se:
                print(f"[stems] spectral '{stem}' failed: {type(se).__name__}: {se}",
                      flush=True)
    # THE REFERENCE PULL (wave 2 — auto-baked from the fable runs' recurring
    # moves on this record class: "make the MIDI sound like the original" was
    # asked twice on one import and answered both times with the same
    # deterministic moves — the record's OWN groove on the sketch lanes + a
    # tone pull toward the record). CLOSED LOOP OR NOTHING (probe-proven:
    # blind-baking these onto a grid-true record COST 1.13 spectral — detected
    # sketches already carry true timing, and the average groove profile
    # smears them): apply to a TEMP copy, render, verify vs the record, keep
    # ONLY on a measured win. Opt-out: SOTADAW_NO_REFPULL=1.
    if with_midi and os.environ.get("SOTADAW_NO_REFPULL") != "1":
        try:
            _hb("reference pull", 0.86,
                "the record's groove + tone, kept only on a measured win")
            song = reference_pull(out, song, stems, name, bpm) or song
        except Exception as pe:
            print(f"[stems] reference pull skipped "
                  f"({type(pe).__name__}: {pe})", flush=True)

    # THE FINAL CORRECTION (A2M byte-par, Chezy 2026-07-10: "FUCKING
    # CORRECTION! TO THE ORIGINAL SONG!"): close the loop against the record's
    # own stems BEFORE the user ever hears the product. Forensics on the
    # uncorrected product: bass +2.6dB / other +3.4dB / drums -2dB vs their
    # stems, pre-master sum peaking +4.8dBFS into the -1.2 wall (the measured
    # "HEAVILY LIMITED" mutilation) and drum recall 0.78. One correction pass
    # matches lane gains to the stems, re-anchors/refits/salvages drum hits.
    # Opt-out: SOTADAW_A2M_CORRECT=0.
    if with_midi and os.environ.get("SOTADAW_A2M_CORRECT") != "0":
        try:
            _hb("final correction", 0.9, "closed-loop calibration vs the record")
            print("[stems] FINAL CORRECTION: closed loop vs the record's stems…",
                  flush=True)
            import a2m_correct as a2c
            rep = a2c.correct(out, iters=1, verify=False)
            if rep and rep.get("gain"):
                deltas = {g: v.get("delta_db") for g, v in rep["gain"].items()}
                d = rep.get("drums", {})
                print(f"[stems] corrected: lane gains {deltas}"
                      + (f", drums {d.get('hits_moved', 0)} re-anchored / "
                         f"{d.get('vels_refit', 0)} vels / "
                         f"{d.get('hits_salvaged', 0)} salvaged" if d else ""),
                      flush=True)
            song = json.load(open(out))        # the corrected truth from disk
        except Exception as ce:
            print(f"[stems] final correction skipped "
                  f"({type(ce).__name__}: {ce})", flush=True)
        _ckpt("final_correction")

    # THE GRADIENT COURT (F7, docs/IMPORT_FINALE.md — "it needs perfect loss
    # and gradient descent for all audio", Chezy 2026-07-17): every stage
    # above is per-lane; this one owns the SUM a human hears. Multi-res
    # log-mel loss vs the stem-sum record, analytic descent on the lane-gain
    # vector (the pre-master mix is linear in lane amps), real-render
    # verify-or-revert. Balance lands BEFORE the master match owns the tone.
    if with_midi and os.environ.get("SOTADAW_NO_MIXCOURT") != "1":
        try:
            _hb("mix balance", 0.92, "gradient descent on the full experience")
            import mix_court as mxc
            mrep = mxc.court(out)
            if mrep and mrep.get("applied"):
                print(f"[stems] balance: {mrep['verdict']}", flush=True)
            song = json.load(open(out))
        except Exception as xe:
            print(f"[stems] mix court skipped "
                  f"({type(xe).__name__}: {xe})", flush=True)
        _ckpt("mix_court")

    # THE MASTER MATCH (F3, docs/IMPORT_FINALE.md — "no final mastering...
    # it needs to sound very much like the original song"): the full render
    # is FINISHED against the record's own measured DNA — tonal tilt (M/S
    # shelves), level (trim), true peak (the wall), width reported. Closed
    # loop, zero tokens, receipts -> <stems>/master_match.json.
    if with_midi and os.environ.get("SOTADAW_NO_MASTERMATCH") != "1":
        try:
            _hb("master match", 0.94, "the finale: tone/level/peak vs the record")
            import master_match as mm
            budget = float(os.environ.get("SOTADAW_IMPORT_BUDGET_S", "420"))
            mm.match(out, iters=(3 if time.time() - t0 > budget else 4))
            song = json.load(open(out))
        except Exception as me:
            print(f"[stems] master match skipped "
                  f"({type(me).__name__}: {me})", flush=True)
        _ckpt("master_match")

    # THE VOCAL MIDI RAIL (Chezy live, 2026-07-09: "ACE STUDIO HAS VOCAL MIDI,
    # SO WE CAN DO THE VOCALS WELL TOO"): the melody lane is the edit surface;
    # a LOCAL singing synth (DiffSinger, tools/sing.py — Gahata Meiji from
    # LUNAI Project) renders it as the vocal SOUND. Wordless on import ('ooh');
    # write_lyrics + sing_lyrics / hum_topline re-sing edits — those verbs
    # already exist as MCP tools. THE DETACH LAW: the spawn is the import's
    # LAST act and the child WAITS for RAM — a blocking child died on arrival
    # on every real import (this importer holds the transcription models; the
    # sing gate saw <3GB free, proven live). The child reloads the song fresh
    # at landing and mutes vocals_sketch itself. Opt-out: SOTADAW_NO_SING=1.
    sing_bg = False
    finisher_steps = []                # ONE detached child: landings never race
    drum_step = None                   # CPU-patient: runs LAST (vocals first)
    import shlex
    py_q = shlex.quote(sys.executable)
    if defer_pieces:
        # F4 THE DRUM FINISHER: stamp what landed so the upgrade can refuse
        # a stomped song, then queue the microscope pass (drumsep -> the
        # SAME land_drum_lanes kernel -> re-correct -> master refresh).
        try:
            import hashlib as _dh
            song = json.load(open(out))
            stamp = {t["name"]: _dh.sha256(json.dumps(
                t.get("notes", []), sort_keys=True).encode()).hexdigest()
                for t in song["tracks"]
                if t.get("name") in ("Kick", "Snare", "Hats", "Perc",
                                     "Cymbals")}
            sdir = os.path.dirname(stems["drums"])
            json.dump(stamp, open(os.path.join(sdir, "drum_land.json"), "w"))
            drum_step = (
                f"{py_q} {shlex.quote(os.path.join(ROOT, 'tools', 'import_finisher.py'))} "
                f"{shlex.quote(name)} --drums")
        except Exception as dfe:
            print(f"[stems] drum finisher not queued ({dfe})", flush=True)
    if with_midi and os.environ.get("SOTADAW_NO_SING") != "1":
        vt = next((t for t in song["tracks"]
                   if t.get("name") == "vocals_sketch"), None)
        if vt and len(vt.get("notes", [])) >= 4:
            try:
                song = json.load(open(out))    # spectral may have rewritten it
                if not any(t.get("name") == "vocals_sung"
                           for t in song["tracks"]):
                    song["tracks"].append(
                        {"name": "vocals_sung",
                         "source": {"kind": "audio", "id": "vocals_sung"},
                         "gainDb": -1.5, "muted": True, "notes": [],
                         "comment": "synth alt voice (lands in background; "
                                    "the record's own vocal_true outranks it)"})
                    json.dump(song, open(out, "w"), indent=1)
                # THE FINISHER CHAIN (A2M byte-par, one detached child so the
                # landings never write-race): 1) vocals_true — the record's
                # OWN vocal re-synthesized from spectral capture (the default
                # sound, "exactly the human"); 2) vocals_sung — the DiffSinger
                # synth take, landing MUTED as the editable alternative.
                # BORN MEL-TRUE (wave 3): 10s windows, ultra tier (128-band
                # noise = the fidelity ruler's own resolution). A failed
                # merge leaves the landed wav untouched and sing still runs
                # (';' by design).
                vtq = shlex.quote(os.path.join(ROOT, 'tools', 'vocal_truth.py'))
                finisher_steps += [
                    f"{py_q} {vtq} {shlex.quote(name)} --win 10 --quality ultra",
                    f"{py_q} {vtq} {shlex.quote(name)} --merge",
                    f"{py_q} {shlex.quote(os.path.join(ROOT, 'tools', 'sing.py'))} "
                    f"hum {shlex.quote(name)} vocals_sketch ooh"]
                sing_bg = True
            except Exception as sge:
                print(f"[stems] vocal finisher not queued "
                      f"({type(sge).__name__}: {sge})", flush=True)
    if drum_step:
        finisher_steps.append(drum_step)
    if finisher_steps:
        try:
            import subprocess as _sp
            slog = os.path.join(ROOT, "agent", "ipc", f"sing_{name}.log")
            os.makedirs(os.path.dirname(slog), exist_ok=True)
            env = dict(os.environ, SOTADAW_SING_WAIT_S="900",
                       SOTADAW_SING_MUTED="1", SOTADAW_VTRUTH_WAIT_S="900")
            _sp.Popen(["bash", "-c", "; ".join(finisher_steps)],
                      stdout=open(slog, "a"), stderr=_sp.STDOUT, env=env,
                      start_new_session=True)
            print(f"[stems] finishers IN BACKGROUND ({len(finisher_steps)} "
                  f"steps{': vocals_true + vocals_sung' if sing_bg else ''}"
                  f"{', then the drum microscope upgrade' if drum_step else ''}); "
                  f"log {os.path.relpath(slog, ROOT)}", flush=True)
        except Exception as fse:
            print(f"[stems] finisher spawn skipped "
                  f"({type(fse).__name__}: {fse})", flush=True)
    # MUSICFLOWS on_import (BEST_DAW_30 #25): every enabled on_import flow runs
    # against the landed session, detached (import_qc ships: preview render ->
    # clip gate -> ears -> finish audit; journal in flows/.runs). SOTADAW_FLOWS=0
    # kills inside the runner; failures never touch the import result.
    try:
        import subprocess as _spf
        _spf.Popen([sys.executable, os.path.join(ROOT, "tools", "musicflow.py"),
                    "run-trigger", "on_import", "--song", name],
                   stdout=open(os.path.join(ROOT, "agent", "ipc",
                                            "flows_stdout.log"), "a"),
                   stderr=_spf.STDOUT, start_new_session=True)
        print("[stems] on_import musicflows dispatched "
              "(journal: flows/.runs)", flush=True)
    except Exception as _fe:
        print(f"[stems] on_import flows skipped ({type(_fe).__name__}: {_fe})",
              flush=True)
    try:                               # F4.1 the stage ledger lands with the stems
        stage_secs["total"] = round(time.time() - t0, 1)
        sdir = os.path.dirname(next(iter(stems.values()), ""))
        if sdir and os.path.isdir(sdir):
            json.dump({"device": device, "deferred_drum_pieces": defer_pieces,
                       "stages": stage_secs},
                      open(os.path.join(sdir, "import_stages.json"), "w"),
                      indent=1)
        top = sorted(((k, v) for k, v in stage_secs.items() if k != "total"),
                     key=lambda kv: -kv[1])[:4]
        print(f"[stage] ledger: total {stage_secs['total']}s on {device} | "
              + " ".join(f"{k}={v}s" for k, v in top), flush=True)
    except Exception:
        pass
    msg = (f"imported '{os.path.basename(audio_path)}' -> songs/{name}.json: "
           f"{sketches} EDITABLE MIDI tracks sounding + {len(stems)} muted stem refs"
           + (", vocal melody singing in background -> vocals_sung" if sing_bg else "")
           + f", bpm {bpm} (conf {conf:.2f}), key {key or '?'} ({key_conf}), {length_bars} bars | "
           f"separation {t_sep:.0f}s, total {time.time()-t0:.0f}s on {device}")
    _hb("done", 1.0, msg[:160])
    print(msg)
    return msg

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("audio", help="source audio; with --retrofit: an existing <name>_stems dir")
    ap.add_argument("song")
    ap.add_argument("--quality", choices=["fast", "max"], default="fast")
    ap.add_argument("--no-midi", action="store_true")
    ap.add_argument("--bpm", type=float, default=None)
    ap.add_argument("--spectral", choices=["lossless", "spectral"], default=None,
                    help="also spectral-capture each stem (reconstruction MIDI lanes; ~6-7x realtime per stem)")
    ap.add_argument("--instruments", choices=["original", "ear"],
                    default="original",
                    help="original = the record's own kits/timbres (default); "
                         "ear = the system auditions the palette against each "
                         "stem and picks the measured twin (receipted)")
    ap.add_argument("--retrofit", action="store_true",
                    help="rebuild the session from already-separated stems (no demucs/GPU)")
    ap.add_argument("--remote", action="store_true",
                    help="THE STEM FORGE: separation + microscope + drum pieces "
                         "+ transcription on serverless cloud GPU "
                         "(tools/modal_stems.py; fail-open to local rails)")
    a = ap.parse_args()
    if a.remote:
        os.environ["SOTADAW_STEMS_REMOTE"] = "1"
    if a.retrofit:
        d = os.path.abspath(a.audio)
        stems = {s: os.path.join(d, f"{s}.wav") for s in ("drums", "bass", "other", "vocals")
                 if os.path.exists(os.path.join(d, f"{s}.wav"))}
        if not stems:
            raise SystemExit(f"no drums/bass/other/vocals wavs in {d}")
        gw = GpuWindow()
        gw.acquire()                           # retrofit transcribes faster on GPU too
        try:
            build_session(stems, d, a.song, not a.no_midi, a.bpm,
                          spectral_mode=a.spectral, instruments=a.instruments)
        finally:
            gw.release()
    else:
        import_song(a.audio, a.song, a.quality, not a.no_midi, a.bpm,
                    spectral_mode=a.spectral, instruments=a.instruments)
