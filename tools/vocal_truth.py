#!/usr/bin/env python3
"""THE VOCAL TRUTH LANE (A2M byte-par, Chezy 2026-07-10: "THE VOCALS TRACKS
FROM AUDIO NEED TO BE TRULY 100% ACCURATELY LIKE THE VOCAL AUDIO").

The record's OWN vocal performance, re-synthesized from parametric spectral
capture (tools/spectral.py: sinusoidal partials + noise bands — MIDI-shaped
data, NEVER a chop of the record), landing as the sounding 'vocals_true' lane.
The DiffSinger take (vocals_sung) stays as the muted synth alternative and
vocals_sketch stays the melody edit surface.

RAM LAW (this box runs earlyoom + systemd-oomd; a whole-song capture was
SIGTERM'd twice, even 60s under load): the vocal is captured in PHRASE WINDOWS
(voiced spans grouped at breath gaps, default <=30s), each window a separate
bounded capture; renders are placed at absolute offsets into one buffer.
A RAM-WAIT gate (SOTADAW_VTRUTH_WAIT_S) holds before each window when the box
is tight — the finisher would rather land late than die.

    vocal_truth.py <song> [--stem wav] [--win 30] [--report json]
"""
import argparse
import gc
import json
import math
import os
import sys
import time
import wave

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "songs")
sys.path.insert(0, os.path.join(ROOT, "tools"))


def say(msg):
    print(f"[vtruth] {msg}", flush=True)


def _mem_avail_gb():
    try:
        for line in open("/proc/meminfo"):
            if line.startswith("MemAvailable:"):
                return int(line.split()[1]) / 1048576.0
    except Exception:
        pass
    return 99.0


def _gate(need_gb=2.0, wait_env="SOTADAW_VTRUTH_WAIT_S"):
    deadline = time.time() + float(os.environ.get(wait_env, "0") or 0)
    while _mem_avail_gb() < need_gb:
        if time.time() >= deadline:
            return _mem_avail_gb() >= need_gb
        time.sleep(5)
    return True


def load_mono(p):
    try:                       # soundfile first: capture's render.wav is
        import soundfile as sf  # float32 (format tag 3) — stdlib wave dies
        x, sr = sf.read(p, dtype="float32", always_2d=False)
        if getattr(x, "ndim", 1) == 2:
            x = x.mean(axis=1, dtype=np.float32)
        return np.asarray(x, dtype=np.float32), int(sr)
    except Exception:
        pass
    w = wave.open(p)
    sw, n, sr, ch = (w.getsampwidth(), w.getnframes(), w.getframerate(),
                     w.getnchannels())
    raw = w.readframes(n)
    if sw == 2:
        x = np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768
    elif sw == 3:
        b = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3)
        x = (b[:, 0].astype(np.int32) | (b[:, 1].astype(np.int32) << 8)
             | (b[:, 2].astype(np.int32) << 16))
        x = np.where(x >= 1 << 23, x - (1 << 24), x).astype(np.float32) / (1 << 23)
    else:
        x = np.frombuffer(raw, dtype="<i4").astype(np.float32) / 2 ** 31
    del raw
    if ch == 2:
        x = x.reshape(-1, 2).mean(1, dtype=np.float32)
    return x, sr


def voiced_windows(x, sr, win_s=30.0, gate_db=-44.0, gap_s=0.6):
    """Voiced spans on a 10ms RMS grid, grouped into <=~win_s windows split at
    breath gaps (sing.py's CHUNK LAW, re-derived for raw audio)."""
    hop = int(0.010 * sr)
    n = (len(x) // hop) * hop
    e = np.sqrt((x[:n].reshape(-1, hop) ** 2).mean(axis=1))
    db = 20 * np.log10(e + 1e-9)
    thr = float(db.max()) + gate_db
    v = db > thr
    spans = []
    i = 0
    while i < len(v):
        if v[i]:
            j = i
            while j < len(v) and (v[j] or (j + 30 < len(v) and v[j:j + 30].any())):
                j += 1                      # bridge holes < 300ms
            spans.append((i * 0.010, j * 0.010))
            i = j
        i += 1
    if not spans:
        return []
    groups, cur = [], [spans[0]]
    for s in spans[1:]:
        gap = s[0] - cur[-1][1]
        span = s[1] - cur[0][0]
        if (gap > gap_s and span > win_s) or span > 1.4 * win_s:
            groups.append(cur)
            cur = []
        cur.append(s)
    if cur:
        groups.append(cur)
    wins = []
    for g in groups:                            # HARD CAP: no window may exceed
        a, b = max(0.0, g[0][0] - 0.15), g[-1][1] + 0.25   # 1.5*win_s — a long
        while b - a > 1.5 * win_s:              # sustained phrase splits mid-air
            wins.append((a, a + win_s))         # (the OOM daemons kill big
            a += win_s                          # analyze allocations, measured)
        wins.append((a, b))
    # ROLL-OUT (2026-07-11, seam forensics on the 97.34 vocals deck): the gate
    # cut decaying tails MID-FLIGHT — the true -gate..-18dB-further decay
    # continued OUTSIDE every window, so the deck filled it with floor noise
    # (measured: join-local mel err 1.63x its ring, tail band 1.5x mid).
    # Extend each end down its OWN decay (to thr-18dB, <=0.8s), never into
    # the next window; contiguous split-mid-air windows stay contiguous.
    ext = []
    for i, (a, b) in enumerate(wins):
        nxt = wins[i + 1][0] if i + 1 < len(wins) else float(len(x)) / sr
        if nxt - b > 0.15:
            j0 = int(b / 0.010)
            jmax = min(len(db), j0 + 80,
                       int(max(0.0, nxt - 0.10) / 0.010))
            j = j0
            while j < jmax and db[j] > thr - 18.0:
                j += 1
            b = max(b, min(j * 0.010, float(len(x)) / sr))
        ext.append((a, b))
    return ext


def _floor_layer(x, sr, covered, buf, bands=32, min_span_s=0.25,
                 rms_gate_db=-100.0):
    """WAVE 2 FLOOR LAW: between voiced windows the stem is not silence — it
    is reverb dust and room tone (-93dB RMS on aranyanyara) sitting above the
    mel ruler's -80dB floor; a silent deck pays ~1.5 spectral points there
    (measured 24.7% of total deck error). There is nothing tonal to track at
    that depth, so model every uncovered span as banded noise only and render
    it into the deck buffer. Returns (floor descriptors for merge(), seconds)."""
    import base64
    import spectral as spx
    hop = max(128, int(round(sr * 0.006)))
    dur = len(x) / sr
    gaps, t = [], 0.0
    for a, b in sorted(covered):
        if a - t >= min_span_s:
            gaps.append((t, a))
        t = max(t, b)
    if dur - t >= min_span_s:
        gaps.append((t, dur))
    floors, sec = [], 0.0
    for a, b in gaps:
        s0, s1 = int(a * sr), min(len(x), int(b * sr))
        y = x[s0:s1]
        if len(y) < hop * 4:
            continue
        rms = float(np.sqrt((y.astype(np.float64) ** 2).mean()))
        if rms < 10.0 ** (rms_gate_db / 20.0):
            continue                            # true digital silence
        env = spx.noise_analyze(y.astype(np.float32), sr, hop, n_bands=bands)
        renv = spx.ruler_env(y.astype(np.float32), sr, bands)  # exact target
        fl = spx.noise_render(env, sr, hop, len(y),
                              ruler_env=renv).astype(np.float32)
        fade = min(int(0.010 * sr), len(fl) // 2)
        if fade > 1:
            r = np.linspace(0.0, 1.0, fade, dtype=np.float32)
            fl[:fade] *= r
            fl[-fade:] *= r[::-1]
        buf[s0:s0 + len(fl)] += fl
        floors.append({"t0": round(a, 4), "t1": round(b, 4),
                       "bands": int(env.shape[0]),
                       "frames": int(env.shape[1]),
                       "data": base64.b64encode(
                           env.astype(np.float16).tobytes()).decode(),
                       "ruler": {"frames": int(renv.shape[1]),
                                 "data": base64.b64encode(
                                     renv.astype(np.float16)
                                     .tobytes()).decode()}})
        sec += b - a
        del env, fl
    return floors, sec


def run(song_name, stem=None, win_s=30.0, report_path=None,
        stem_name="vocals", gate_db=-44.0, quality="max", redo_below=None):
    """stem_name: vocals|drums|bass|other — lands <stem_name>_true.
    Non-vocal truth decks land MUTED (the musical sketch lanes stay the
    sounding product; the deck is the fidelity layer you flip to)."""
    os.nice(10)
    sp = os.path.join(SONGS, f"{song_name}.json")
    song = json.load(open(sp))
    bpm = float(song.get("bpm", 120.0))
    if stem is None:
        stem = next((c.get("file") for t in song.get("tracks", [])
                     if t.get("name") == stem_name
                     for c in (t.get("audioClips") or [])
                     if "_stems/" in str(c.get("file", ""))), None)
    if not stem:
        say(f"no '{stem_name}' stem reference in this song — nothing to capture")
        return None
    stem_abs = stem if os.path.isabs(stem) else os.path.join(ROOT, stem)
    x, sr = load_mono(stem_abs)
    out_root = os.path.join(SONGS, f"{song_name}_spectral",
                            "vtruth" if stem_name == "vocals"
                            else f"truth_{stem_name}")
    os.makedirs(out_root, exist_ok=True)
    sj = os.path.join(out_root, "spans.json")
    wins = None
    if os.path.exists(sj):                     # GEOMETRY LAW: once cut, window
        try:                                   # boundaries are DISK TRUTH — a
            meta = json.load(open(sj))         # re-run with different gate/win
            if int(meta.get("n_samples", -1)) == len(x):   # params must still
                wins = [tuple(s) for s in meta["spans"]]   # resume w{k} dirs
                say(f"geometry from spans.json ({len(wins)} windows, "
                    "resume-safe)")
        except Exception:
            wins = None
    if wins is None:
        wins = voiced_windows(x, sr, win_s=win_s, gate_db=gate_db)
    # BLEED WINDOW LAW (wave 2): the phrase gate cuts clean phrases, but
    # separation bleed / quiet ad-libs between them carry TONAL content the
    # floor's banded noise cannot mimic (mel sees harmonic peaks vs flat
    # noise — measured 26.7% of deck error living outside the windows).
    # Detect deeper (-78 rel max — the phrase cut itself already ran at -55/
    # -65, so the bleed pass must outreach it; the 45s energy-ranked budget
    # below keeps the dust out), keep spans mostly uncovered, APPEND ONLY:
    # existing w{k} indices stay resume-stable.
    deep = voiced_windows(x, sr, win_s=win_s, gate_db=-78.0)

    def _uncovered(s):
        # INTERVAL DIFFERENCE, never overlap: the deck buffer ADDS window
        # renders — a bleed span half-inside an existing window doubled 4s
        # of audio (+6dB seam, measured worst-segment 2.5e5 err mass).
        segs = [(max(0.0, float(s[0])), float(s[1]))]
        for wa, wb in sorted(wins):
            nxt = []
            for a0, b0 in segs:
                if wb <= a0 or wa >= b0:
                    nxt.append((a0, b0))
                    continue
                if a0 < wa - 1e-6:
                    nxt.append((a0, wa))
                if wb < b0 - 1e-6:
                    nxt.append((wb, b0))
            segs = nxt
        return [(a0, b0) for a0, b0 in segs if b0 - a0 >= 1.2]

    bleed = [p for s in deep for p in _uncovered(s)]
    # LEVEL FLOOR: a piece whose slice never rises above -70dBFS is floor
    # territory (the FLOOR LAW's banded noise already models it) — without
    # this gate every pass eats the next-quietest 45s of dust forever
    bleed = [p for p in bleed
             if float(np.abs(x[int(p[0] * sr):int(p[1] * sr)]).max()
                      if int(p[1] * sr) > int(p[0] * sr) else 0.0)
             >= 10.0 ** (-70.0 / 20.0)]
    if bleed:                                  # budget: loudest first, <=45s
        def _e(s):
            a0, b0 = int(s[0] * sr), min(len(x), int(s[1] * sr))
            return float((x[a0:b0].astype(np.float64) ** 2).sum())
        bleed.sort(key=_e, reverse=True)
        kept, tot = [], 0.0
        for s in bleed:
            if tot + (s[1] - s[0]) > 45.0:
                continue
            kept.append(s)
            tot += s[1] - s[0]
        if kept:
            say(f"BLEED WINDOWS: +{len(kept)} deep-gate spans the phrase "
                f"gate missed ({tot:.0f}s) — appended, resume-stable")
            wins = list(wins) + sorted(kept)
    dur = len(x) / sr
    # SPAN = SLICE law: a window record past the file end disagrees with its
    # clipped capture (merge aborts on n_samples vs span mismatch)
    wins = [(max(0.0, a), min(dur, b)) for a, b in wins if min(dur, b) - a > 0.1]
    voiced = sum(b - a for a, b in wins)
    say(f"{stem_name} stem {dur:.0f}s, {len(wins)} activity windows "
        f"({voiced:.0f}s active)")
    if not wins:
        return None
    buf = np.zeros(len(x), dtype=np.float32)
    try:                                       # spans persist for merge()
        json.dump({"win_s": win_s, "sr": sr, "n_samples": len(x),
                   "spans": [[round(a, 4), round(b, 4)] for a, b in wins]},
                  open(sj, "w"))
    except Exception:
        pass

    if redo_below:                             # starved windows recapture; the
        for k in range(len(wins)):             # old capture is kept as *.bak
            cp = os.path.join(out_root, f"w{k}", "capture.json")
            try:
                c0 = json.load(open(cp))
                fid = c0.get("fidelity", {}).get("spectral_pct")
            except Exception:
                continue
            if c0.get("quality") == quality:   # TIER-SKIP: this window already
                continue                       # paid this tier — a same-tier
            if fid is not None and float(fid) < float(redo_below):   # redo is
                bak = os.path.join(out_root, f"w{k}.q{int(float(fid))}bak")  # a
                if not os.path.exists(bak):    # deterministic photocopy
                    os.rename(os.path.join(out_root, f"w{k}"), bak)
                    say(f"redo-below {redo_below}: w{k} ({fid}%) -> recapture")

    import tempfile

    from scipy.io import wavfile as _wf
    import spectral as spx
    t0 = time.time()
    fids, covered, bands_seen = [], [], 0
    for k, (a, b) in enumerate(wins):
        # RESUME LAW: a window already captured on disk is never recomputed —
        # under this box's weather a landing can take several attempts and a
        # window costs ~6 minutes.
        wdir = os.path.join(out_root, f"w{k}")
        cap = None
        cap_p = os.path.join(wdir, "capture.json")
        if os.path.exists(cap_p):
            try:
                c0 = json.load(open(cap_p))
                if os.path.exists(os.path.join(ROOT, c0["files"]["render"])):
                    cap = c0
                    say(f"window {k + 1}/{len(wins)}: resumed from disk")
            except Exception:
                cap = None
        if cap is None:
            if not _gate(2.0):
                say(f"window {k + 1}/{len(wins)}: box too tight (avail "
                    f"{_mem_avail_gb():.1f}GB) — landing what's captured so far")
                break
            # WINDOW-WAV LAW: capture() loads its WHOLE input before t0/t1
            # slicing — on a 410s stem that full-file load per window is what
            # the OOM daemons killed. Hand it a temp wav of JUST this window.
            tmp = os.path.join(tempfile.gettempdir(),
                               f"_vtruth_{os.getpid()}_{k}.wav")
            a0s, b0s = int(a * sr), min(len(x), int(b * sr))
            _wf.write(tmp, sr,                 # float in, float out: int16
                      np.clip(x[a0s:b0s], -1.0, 1.0).astype(np.float32))
            # window wavs fed the capture as int16 pre-wave-2 (tails truncated
            # at -90dB before analysis ever saw them)
            try:
                cap = spx.capture(tmp, name=f"{song_name}_vt{k}", bpm=bpm,
                                  mode="spectral", out_dir=wdir,
                                  quality=quality,
                                  prefix=f"vtruth_w{k}",
                                  prog=spx.Prog([("load", 3), ("analyze", 38),
                                                 ("carve", 22), ("notes", 7),
                                                 ("render", 22), ("residual", 5),
                                                 ("verify", 3)],
                                                label=f"vtruth {k + 1}/{len(wins)}"))
            except Exception as ce:
                say(f"window {k + 1} failed ({type(ce).__name__}: {ce}) — skipped")
                continue
            finally:
                if os.path.exists(tmp):
                    os.remove(tmp)
        rend, rsr = load_mono(os.path.join(ROOT, cap["files"]["render"]))
        a0 = int(round(a * rsr))
        b0 = min(len(buf), a0 + len(rend))
        buf[a0:b0] += rend[:b0 - a0]
        f = cap.get("fidelity", {})
        fids.append((b - a, f.get("spectral_pct") or 0.0))
        covered.append((a, b))
        bands_seen = int(cap.get("noise_bands", bands_seen) or bands_seen)
        say(f"window {k + 1}/{len(wins)} [{a:.1f}-{b:.1f}s]: "
            f"spectral {f.get('spectral_pct')}% (partials "
            f"{len(cap['tracks']['partials'])})")
        del rend, cap
        gc.collect()

    floors, fsec = _floor_layer(x, sr, covered, buf, bands=bands_seen or 32)
    if floors:
        try:
            json.dump({"floors": floors},
                      open(os.path.join(out_root, "floor.json"), "w"))
        except Exception:
            pass
        say(f"FLOOR LAW: {len(floors)} uncovered spans ({fsec:.0f}s) modeled "
            "as banded noise — the deck is never digital silence where the "
            "record still breathes")

    out = os.path.join(SONGS, f"{song_name}_{stem_name}_true.wav")
    from scipy.io import wavfile
    # FLOAT DECK LAW (wave 2): int16 TRUNCATES sub-LSB content to zero — the
    # -93dB reverb dust the floor layer models sits below the -90.3dB int16
    # floor, and quiet in-window tails lose ~4dB (measured). The engine and
    # every loader here read IEEE-float wavs natively.
    wavfile.write(out, sr, np.clip(buf, -1.0, 1.0).astype(np.float32))
    wsum = sum(w for w, _ in fids) or 1.0
    fid = sum(w * s for w, s in fids) / wsum
    say(f"captured {len(fids)}/{len(wins)} windows in {time.time() - t0:.0f}s "
        f"-> {os.path.relpath(out, ROOT)} (voiced-weighted spectral {fid:.1f}%)")

    # LAND IT (fresh reload — the landing owns the swap): vocals_true SOUNDS,
    # the synth take mutes, the melody sketch stays the muted edit surface.
    song = json.load(open(sp))
    lane = f"{stem_name}_true"
    vt = next((t for t in song["tracks"] if t.get("name") == lane), None)
    if vt is None:
        vt = {"name": lane,
              "source": {"kind": "audio", "id": lane},
              "gainDb": 0.0, "notes": []}
        song["tracks"].append(vt)
    vt["audioClips"] = [{"file": os.path.relpath(out, ROOT), "startBeat": 0}]
    vt["muted"] = stem_name != "vocals"        # vocal truth SOUNDS (it replaced
    vt["comment"] = (f"the record's own {stem_name}, re-synthesized from "   # the
                     "spectral capture (parametric, not a chop)"             # synth
                     + ("" if stem_name == "vocals"
                        else " — FIDELITY DECK: unmute to hear the record's "
                             "layer instead of the sketch lanes"))
    try:                                       # LEVEL LAW: land at the stem's LUFS
        import pyloudnorm
        m = pyloudnorm.Meter(sr)
        l_ref = m.integrated_loudness(x.astype(np.float64))
        l_out = m.integrated_loudness(buf.astype(np.float64))
        if np.isfinite(l_ref) and np.isfinite(l_out) and l_ref > -55:
            vt["gainDb"] = round(max(-12.0, min(12.0, l_ref - l_out)), 2)
            say(f"LEVEL LAW: truth {l_out:.1f} LUFS, stem {l_ref:.1f} "
                f"-> lane gain {vt['gainDb']:+.1f}dB")
    except Exception as le:
        say(f"level match skipped ({type(le).__name__}: {le})")
    if stem_name == "vocals":
        for t in song["tracks"]:
            if t.get("name") == "vocals_sung":
                t["muted"] = True              # the human voice outranks the synth
    json.dump(song, open(sp, "w"), indent=1)
    say(f"LANDED: {lane} " + ("sounds (synth take muted)" if stem_name == "vocals"
                              else "muted fidelity deck ready"))
    if stem_name == "vocals":
        # THE FOLLOWING VOICE (Chezy 2026-07-11: "IT NEEDS TO BE EDITABLE
        # MIDI!"): vocals_true is a RENDER — bind it to the melody lane so
        # editing the MIDI re-sings it in the record's own timbre (the
        # sidecar watcher runs tools/vocal_follow.py). Mint the lane if the
        # import never landed one (opptical's exact hole).
        try:
            import vocal_follow as _vf
            song = json.load(open(sp))
            if not any(t.get("name") == _vf.SKETCH_LANE
                       for t in song["tracks"]):
                mel = _vf.cached_melody(song_name)
                if mel:
                    _vf.land_sketch(song_name, mel)
                else:
                    _vf.mint(song_name, stem_abs, float(song.get("bpm", 120)))
            _vf.bind(song_name, _vf.SKETCH_LANE, os.path.relpath(out, ROOT),
                     os.path.relpath(stem_abs, ROOT))
            say("FOLLOWING VOICE: vocals_true bound to vocals_sketch - "
                "edit the MIDI and the voice re-sings (original timbre)")
        except Exception as fe:
            say(f"follow binding skipped ({type(fe).__name__}: {fe})")
    rep = {"song": song_name, "windows": len(wins), "captured": len(fids),
           "voiced_s": round(voiced, 1),
           "spectral_weighted": round(fid, 2), "wav": os.path.relpath(out, ROOT)}
    if report_path:
        json.dump(rep, open(report_path, "w"), indent=1)
    return rep


def merge(song_name, verify=True, stem_name="vocals"):
    """WAVE 3 — FULL-MIDI VOCALS: fuse the window captures into ONE sidecar so
    the partial lanes (vocals_true_low/mid/high) are live-editable through the
    engine's SpectralVoicePlugin. Every note payload is start-relative (merge =
    beat shift); noise env/phase matrices paste at frame offsets."""
    import base64
    # #10 import-chain law: a big-deck fuse peaks ~4GB (aranyanyara 47w hit
    # earlyoom at 3.95GB) — gate on the box and SKIP honestly rather than die
    # mid-fuse; the landed wav is untouched and --merge re-runs any time.
    if not _gate(4.5):
        say(f"merge: box too tight (avail {_mem_avail_gb():.1f}GB < 4.5) — "
            f"deck stays per-window; re-run --merge when the box frees up")
        return None
    sp_ = os.path.join(SONGS, f"{song_name}.json")
    song = json.load(open(sp_))
    root = os.path.join(SONGS, f"{song_name}_spectral")
    vt = os.path.join(root, "vtruth" if stem_name == "vocals"
                      else f"truth_{stem_name}")
    sj = os.path.join(vt, "spans.json")
    wdirs = sorted((d for d in os.listdir(vt) if d.startswith("w")
                    and d[1:].isdigit()        # w{k} ONLY — .q*bak/.ultra_lost
                    and os.path.exists(os.path.join(vt, d, "capture.json"))),
                   key=lambda d: int(d[1:]))
    if os.path.exists(sj):
        meta = json.load(open(sj))
        spans, sr, n_total = meta["spans"], meta["sr"], meta["n_samples"]
    else:                                      # pre-spans runs: re-derive (the
        stem = next((c.get("file") for t in song.get("tracks", [])   # windowing
                     if t.get("name") == stem_name                   # is pure)
                     for c in (t.get("audioClips") or [])
                     if "_stems/" in str(c.get("file", ""))), None)
        x, sr = load_mono(stem if os.path.isabs(stem)
                          else os.path.join(ROOT, stem))
        spans = voiced_windows(x, sr, win_s=12.0)   # matches the runner default
        n_total = len(x)
        del x
    if len(spans) < len(wdirs):
        say(f"merge: {len(wdirs)} windows on disk but {len(spans)} spans — abort")
        return None
    import spectral as spx
    caps = []
    for d in wdirs:
        k = int(d[1:])
        c = json.load(open(os.path.join(vt, d, "capture.json")))
        a, b = spans[k]
        want = int((b - a) * c["sr"])
        if abs(c["n_samples"] - want) > c["sr"] * 0.05:
            say(f"merge: {d} n_samples {c['n_samples']} != span {want} — abort")
            return None
        caps.append((k, a, c))
    base = caps[0][2]
    hop, sr = base["hop"], base["sr"]
    spb = 60.0 / float(base["bpm"])
    frames_total = 1 + n_total // hop
    bands = int(base["noise_bands"])
    env_full = np.zeros((bands, frames_total), np.float32)
    # RULER-TRUE (wave 3.5): fuse the per-window exact ruler targets too, so
    # full-song python re-renders of the merged sidecar get the exact finish
    # (the deck WAV already carries it via window renders)
    rframes_total = 1 + n_total // spx.RULER_HOP
    ruler_full = np.zeros((bands, rframes_total), np.float32)
    ruler_any = False
    # wave 3.6: fuse the whole-mix polish targets too — ALL-OR-NOTHING (a
    # window without one would get dimmed toward a zero target)
    mix_full = np.zeros((bands, rframes_total), np.float32)
    mix_all = True
    partials, clicks, noise = [], [], []
    for k, a, c in caps:
        boff = round(a / spb, 6)
        for src, dst in ((c["tracks"]["partials"], partials),
                         (c["tracks"].get("clicks", []), clicks),
                         (c["tracks"]["noise"], noise)):
            for nt in src:
                m = dict(nt)
                m["start"] = round(float(nt["start"]) + boff, 6)
                dst.append(m)
        ne = c.get("noise_env")
        if ne:
            e = np.frombuffer(base64.b64decode(ne["data"]),
                              dtype=np.float16).reshape(ne["bands"],
                                                        ne["frames"])
            f0 = int(round(a * sr / hop))
            f1 = min(frames_total, f0 + e.shape[1])
            env_full[:, f0:f1] = np.maximum(env_full[:, f0:f1],
                                            e[:, :f1 - f0].astype(np.float32))
        nr = c.get("noise_env_ruler")
        if nr and int(nr["bands"]) == bands:
            e = np.frombuffer(base64.b64decode(nr["data"]),
                              dtype=np.float16).reshape(nr["bands"],
                                                        nr["frames"])
            f0 = int(round(a * sr / spx.RULER_HOP))
            f1 = min(rframes_total, f0 + e.shape[1])
            if f1 > f0:
                ruler_full[:, f0:f1] = np.maximum(
                    ruler_full[:, f0:f1], e[:, :f1 - f0].astype(np.float32))
                ruler_any = True
        mr = c.get("mix_env_ruler")
        if mr and int(mr["bands"]) == bands:
            e = np.frombuffer(base64.b64decode(mr["data"]),
                              dtype=np.float16).reshape(mr["bands"],
                                                        mr["frames"])
            f0 = int(round(a * sr / spx.RULER_HOP))
            f1 = min(rframes_total, f0 + e.shape[1])
            if f1 > f0:
                mix_full[:, f0:f1] = np.maximum(
                    mix_full[:, f0:f1], e[:, :f1 - f0].astype(np.float32))
        else:
            mix_all = False
    fj = os.path.join(vt, "floor.json")
    if os.path.exists(fj):                     # FLOOR LAW: the uncovered-span
        n_fl = 0                               # noise floor rides the sidecar
        for f in json.load(open(fj)).get("floors", []):   # too, so the live
            if int(f["bands"]) != bands:       # spectral lanes render the same
                continue                       # deck the wav carries
            e = np.frombuffer(base64.b64decode(f["data"]),
                              dtype=np.float16).reshape(f["bands"],
                                                        f["frames"])
            f0 = int(round(float(f["t0"]) * sr / hop))
            f1 = min(frames_total, f0 + e.shape[1])
            if f1 > f0:
                env_full[:, f0:f1] = np.maximum(env_full[:, f0:f1],
                                                e[:, :f1 - f0].astype(np.float32))
                n_fl += 1
            fr = f.get("ruler")
            if fr:
                e = np.frombuffer(base64.b64decode(fr["data"]),
                                  dtype=np.float16).reshape(bands,
                                                            fr["frames"])
                f0 = int(round(float(f["t0"]) * sr / spx.RULER_HOP))
                f1 = min(rframes_total, f0 + e.shape[1])
                if f1 > f0:
                    ruler_full[:, f0:f1] = np.maximum(
                        ruler_full[:, f0:f1],
                        e[:, :f1 - f0].astype(np.float32))
                    ruler_any = True
                    # a floor span has NO tonal layer — the gap source IS
                    # the residual, so its ruler env doubles as the mix
                    # polish target there
                    mix_full[:, f0:f1] = np.maximum(
                        mix_full[:, f0:f1], e[:, :f1 - f0].astype(np.float32))
        if n_fl:
            say(f"floor.json: {n_fl} noise-floor spans pasted into the sidecar")
    cap = {"version": 1, "sr": sr, "hop": hop, "bpm": base["bpm"],
           "n_samples": int(n_total), "seed": base["seed"],
           "noise_bands": bands, "quality": base.get("quality", "max"),
           "mode": "spectral", "prefix": f"{stem_name}_true",
           "source": base.get("source", ""),
           "noise_env": {"bands": bands, "frames": frames_total,
                         "data": base64.b64encode(
                             env_full.astype(np.float16).tobytes()).decode()},
           "tracks": {"partials": sorted(partials, key=lambda n: n["start"]),
                      "clicks": sorted(clicks, key=lambda n: n["start"]),
                      "noise": sorted(noise, key=lambda n: n["start"])}}
    if ruler_any:
        cap["noise_env_ruler"] = {"bands": bands, "frames": rframes_total,
                                  "data": base64.b64encode(
                                      ruler_full.astype(np.float16)
                                      .tobytes()).decode()}
    if mix_all and len(caps) > 0:
        cap["mix_env_ruler"] = {"bands": bands, "frames": rframes_total,
                                "data": base64.b64encode(
                                    mix_full.astype(np.float16)
                                    .tobytes()).decode()}
    cap_path = os.path.join(root, "capture.json" if stem_name == "vocals"
                            else f"capture_{stem_name}.json")
    cap["files"] = {"capture": os.path.relpath(cap_path, ROOT)}
    tmp_path = cap_path + ".tmp"       # ATOMIC: an OOM kill mid-write tore a
    with open(tmp_path, "w") as _f:    # 318MB sidecar in place (2026-07-11);
        json.dump(cap, _f)             # rename is the only crash-safe commit
    os.replace(tmp_path, cap_path)
    say(f"merged {len(caps)} windows -> {os.path.relpath(cap_path, ROOT)} "
        f"({len(partials)} partials / {len(clicks)} clicks / {len(noise)} noise)")
    if verify:
        say("verify: deterministic render of the merged sidecar…")
        rend = spx.render_capture(cap)
        wav = os.path.join(SONGS, f"{song_name}_{stem_name}_true.wav")
        ref, rsr = load_mono(wav)
        m = min(len(ref), len(rend))
        v = spx.verify_arrays(ref[:m], np.asarray(rend[:m], dtype=np.float32),
                              rsr)
        say(f"merged render vs landed wav: spectral {v.get('spectral_pct')}% "
            f"corr {v.get('wave_corr')}")
        del rend, ref
    spx.inject_into_song(cap, sp_)
    song = json.load(open(sp_))                # inject rewrote it; re-tidy
    lane = f"{stem_name}_true"
    CAP = 4000                                 # edit lanes are a HUMAN surface
    for t in song["tracks"]:
        if t.get("name") == lane:              # vocal truth sounds; other decks
            t["muted"] = stem_name != "vocals"     # stay the muted fidelity flip
        elif t.get("name", "").startswith(lane + "_") \
                and len(t.get("notes", [])) > CAP:
            before = len(t["notes"])
            t["notes"] = sorted(sorted(t["notes"],
                                       key=lambda x: -float(x["vel"]))[:CAP],
                                key=lambda x: float(x["start"]))
            t["comment"] = (f"edit surface: strongest {CAP} of {before} "
                            f"partials (full set lives in the sidecar)")
    json.dump(song, open(sp_, "w"), indent=1)
    say(f"lanes landed: {lane}_low/mid/high (+noise/clicks) muted = the "
        f"edit surface (capped {CAP}); {lane} (audio) = the "
        + ("sounding mix" if stem_name == "vocals" else "muted fidelity deck"))
    return cap_path


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("song")
    ap.add_argument("--stem", default=None, help="vocal stem wav (default: the "
                    "song's own muted 'vocals' reference)")
    ap.add_argument("--win", type=float, default=30.0)
    ap.add_argument("--report", default=None)
    ap.add_argument("--merge", action="store_true",
                    help="fuse existing window captures into one sidecar + "
                         "editable spectral lanes (wave 3)")
    ap.add_argument("--stem-name", default="vocals",
                    choices=["vocals", "drums", "bass", "other"],
                    help="which stem to capture (wave 4: truth decks for all)")
    ap.add_argument("--gate-db", type=float, default=-44.0,
                    help="activity gate rel max (bass sustains need -55: the "
                         "-44 default left decaying subs out — deck env 0.80)")
    ap.add_argument("--quality", default="max",
                    choices=["fast", "standard", "max", "ultra"],
                    help="spectral.QUALITY tier for window captures")
    ap.add_argument("--redo-below", type=float, default=None,
                    help="recapture windows whose stored fidelity is below "
                         "this spectral%% (old capture kept as w{k}.q*bak)")
    a = ap.parse_args()
    if a.merge:
        merge(a.song, stem_name=a.stem_name)
    else:
        run(a.song, stem=a.stem, win_s=a.win, report_path=a.report,
            stem_name=a.stem_name, gate_db=a.gate_db, quality=a.quality,
            redo_below=a.redo_below)
