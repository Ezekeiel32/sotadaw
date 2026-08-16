#!/usr/bin/env python3
"""THE FINAL CORRECTION (A2M byte-par campaign, Chezy 2026-07-09: "FUCKING
CORRECTION! TO THE ORIGINAL SONG!").

Closed-loop, per-lane calibration of an imported MIDI product against the
record's OWN stems — analysis-by-synthesis, deterministic (the Inverse-Drum-
Machine idea without the neural net: we already hold the kit and the notes).

    render-stems the product -> pair every MIDI lane group with its source
    stem on the engine's own clock -> correct AT THE SOURCE (never the output):

      1. GAIN LAW      group LUFS delta -> member lane gainDb (clamped)
      2. DRUM TIMING   every hit re-anchored to the nearest same-band onset
                       of the REAL drum stem (<=35ms reach) — kills detector
                       jitter AND grid-snap residue; the record's feel is the
                       target, not a lattice
      3. DRUM VELOCITY per-hit band-peak refit vs the stem through the
                       sampler's measured dB law (20dB per vel unit) — the
                       accent map becomes the record's accent map
      4. THE MELODIC EAR (2026-07-16, "NOT PRODUCTION READY" gap): the same
                       per-note truth for PITCHED lanes, through the REAL
                       engine render. build_pitched_kit's closed loop
                       calibrates velocities against a numpy SIMULATION of
                       the sampler; the engine (fx chains, voice stacking,
                       range-fill resampling) drifts from it, and nothing
                       ever measured melodic per-note timing at all. Level rules by
                       the note's BAND RMS (attack-peak matching crushed
                       sustained beds); starts re-anchor to the stem's own
                       band attack — TRANSIENT-GATED (crest >=10dB; a bed's
                       "attack" is fiction), 50ms melodic reach, evidence-
                       gated; velocities refit damped through the sampler law.
                       THE LANE LATENCY LAW (F6, ruler retired once by the
                       regression court): lane-wide timing is judged by
                       ENERGY — the env-xcorr lag between the lane render
                       and its stem (lane_env_lag), applied to un-anchored
                       notes as one body. The attack-foot median was
                       mad-coherent AND wrong on swell lanes (feet aligned,
                       energy 30-40ms late, the bass dragged — the ear
                       outranks the foot model); a flat/weak xcorr peak
                       refuses the verdict.
      5. WALL RELIEF   lanes matched to stems means the pre-master sum sits
                       at the record's own loudness -> fx_truepeak barely
                       works -> no more "heavily limited vs the original"

Iterates (render -> measure -> correct) up to --iters; every number printed.
Used by stems_import as the import's final act and exposed to the agent (MCP
a2m_correct). Pure stdlib + numpy/scipy/librosa/pyloudnorm — no GPU, Pi-OK.
"""
import argparse
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import wave

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")

from source_kit import LANE_BAND_HZ, _band_filter, _hit_band_peak  # noqa: E402

# song-lane name -> which stem file answers for it
GROUPS = {
    "drums": ("Kick", "Snare", "Hats", "Perc", "Cymbals", "drums_sketch"),
    "bass": ("bass_sketch",),
    "other": ("other_sketch", "guitar_sketch", "piano_sketch", "keys_sketch")
             # THE STREAM SPLIT lanes (note_streams.py 2026-07-15): the
             # harmonic bucket decomposes into voice lanes; the level law
             # answers for all of them with the same 'other' stem.
             + tuple(f"{p}_{s}" for p in ("other", "guitar", "piano", "keys")
                     for s in ("lead", "pad", "chords")),
    "vocals": ("vocals_true", "vocals_sung", "vocals_true_mix", "vocals_sketch"),
}
LANE_GM = {"Kick": 36, "Snare": 38, "Hats": 42, "Perc": 39, "Cymbals": 49}
MAX_GAIN_STEP = 12.0     # dB per iteration
MAX_GAIN_TOTAL = 18.0    # dB cumulative vs import default
TIMING_REACH_S = 0.035   # re-anchor hits only within this of a real onset
VEL_DB_PER_UNIT = 20.0   # sampler law: vel = 1 + log10(pk/ceiling)


def say(msg):
    print(f"[correct] {msg}", flush=True)


def load_mono(path):
    try:                        # soundfile first: stems are float32 since THE
        import soundfile as sf  # CLEAN SPLIT (stdlib wave dies on format 3)
        x, sr = sf.read(path, dtype="float32", always_2d=False)
        if x.ndim > 1:
            x = x.mean(axis=1, dtype=np.float32)
        return x.astype(np.float32, copy=False), int(sr)
    except Exception:
        pass
    w = wave.open(path)
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


def lufs(x, sr):
    try:
        import pyloudnorm
        v = pyloudnorm.Meter(sr).integrated_loudness(x.astype(np.float64))
        if np.isfinite(v):
            return float(v)
    except Exception:
        pass
    r = float(np.sqrt((x.astype(np.float64) ** 2).mean()) + 1e-12)
    return 20 * math.log10(r)


def render_stems(song_path, out_dir):
    """Per-lane renders for the correction. SPECTRAL LANES ARE STRIPPED from
    a temp copy first: render-stems solos EVERY lane, and each spectral edit
    lane force-loads its merged sidecar (365-570MB json -> GBs transient) —
    earlyoom killed the correction twice on a merged song (rc=-15, measured
    2026-07-10; plain `m1 render` is safe at 245MB because muted spectral
    lanes never process). They are muted edit surfaces, never in GROUPS —
    invisible to the correction. Returns (files, rendered_tracks): the zip
    mapping must follow the STRIPPED track list."""
    os.makedirs(out_dir, exist_ok=True)
    song = json.load(open(song_path))
    tracks = song.get("tracks", [])
    kept = [t for t in tracks
            if (t.get("source") or {}).get("kind") != "spectral"]
    # THE STAGE SEPARATION LAW (2026-07-15, IMPORT_FINALE F3): correction
    # renders are MASTER-FREE. With a real master chain (the match EQ) in
    # the graph, lane renders absorb its color — velocity refits compensate
    # for EQ, the match then re-aims on top, and the two stages fight
    # (goldenbrown_2 env_corr 0.62 -> 0.38 before this law). Lanes
    # calibrate RAW against the stems; the master match owns the SUM.
    rp = song_path
    if len(kept) != len(tracks) or song.get("master") \
            or song.get("masterGainDb"):
        song["tracks"] = kept
        song["master"] = []
        song["masterGainDb"] = 0.0
        rp = os.path.join(out_dir, "_strip.json")
        json.dump(song, open(rp, "w"))
    try:
        r = subprocess.run([M1, "render-stems", rp, out_dir],
                           capture_output=True, text=True, timeout=1800)
        if r.returncode != 0:
            # transient engine aborts happen under box contention (a parallel
            # session's sing/import; SIGABRT "terminate called without an
            # active exception" = the allocation-pressure flavor). One
            # patient retry before giving up.
            say(f"render-stems rc={r.returncode} — waiting 20s, one retry")
            import time as _t
            _t.sleep(20)
            r = subprocess.run([M1, "render-stems", rp, out_dir],
                               capture_output=True, text=True, timeout=1800)
    finally:
        if rp != song_path and os.path.exists(rp):
            os.remove(rp)
    if r.returncode != 0:
        raise RuntimeError(f"m1 render-stems rc={r.returncode}: {r.stderr[-300:]}")
    files = sorted(f for f in os.listdir(out_dir) if f.endswith(".wav"))
    # INDEX-PREFIX MAPPING (2026-07-15): m1 names stems NN_<track>.wav by
    # rendered-track index. A lane that renders no file (goldenbrown's
    # legacy 'goldenbrown_master' audio lane) used to desync the count+order
    # zip and kill the whole correction; the prefix maps each file to ITS
    # track and missing renders just drop out of the correction.
    if files and all(f.split("_", 1)[0].isdigit() for f in files):
        pairs = [(f, int(f.split("_", 1)[0])) for f in files]
        pairs = [(f, i) for f, i in pairs if i < len(kept)]
        return [f for f, _ in pairs], [kept[i] for _, i in pairs]
    return files, kept


def stem_paths_from_song(song):
    """The muted stem-ref lanes carry the truth: audioClips under *_stems/."""
    out = {}
    for t in song.get("tracks", []):
        for c in t.get("audioClips", []):
            f = c.get("file", "")
            if "_stems/" in f.replace("\\", "/"):
                base = os.path.splitext(os.path.basename(f))[0]
                if base in GROUPS:
                    p = f if os.path.isabs(f) else os.path.join(ROOT, f)
                    if os.path.exists(p):
                        out[base] = p
    return out


def group_of(track_name):
    for g, names in GROUPS.items():
        if track_name in names:
            return g
    return None


def sum_files(paths):
    acc, sr = None, 44100
    for p in paths:
        x, sr = load_mono(p)
        if acc is None:
            acc = x
        else:
            m = min(len(acc), len(x))
            acc = acc[:m]
            acc += x[:m]
        del x
    return acc, sr


def band_balance(path, lo, hi):
    """Stereo energy balance (-1 all-L .. +1 all-R) of a file inside one
    band — the IMAGE LAW's ruler. None when the band holds no real energy."""
    try:
        import soundfile as sf
        x, sr = sf.read(path, dtype="float32", always_2d=True)
    except Exception:
        return None
    if x.shape[1] < 2:
        return 0.0
    from scipy.signal import butter, sosfilt
    ny = sr / 2.0
    lo, hi = max(lo, 20.0), min(hi, ny * 0.98)
    if hi <= lo:
        return None
    sos = butter(2, [lo / ny, hi / ny], "band", output="sos")
    full = float((x.astype(np.float64) ** 2).mean())
    el = float((sosfilt(sos, x[:, 0]) ** 2).mean())
    er = float((sosfilt(sos, x[:, 1]) ** 2).mean())
    del x
    # RELATIVE gate: a band holding < -45dB of the file's own energy is
    # empty — filter leakage and noise floors never testify about image
    if full < 1e-12 or (el + er) / full < 10.0 ** (-45.0 / 10.0):
        return None
    return (er - el) / (el + er)


def lane_latency_verdict(lat_ms, min_n=10, floor_ms=10.0, cap_ms=40.0):
    """(retired ruler — kept for the battery contract and as a secondary
    coherence witness.) The attack-foot docket: coherent median over ungated
    feet. F6 regression court (goldenbrown, live ears 2026-07-17): for SWELL
    lanes the foot ruler is systematically wrong — our exemplar's energy
    peaks at note-on while the record's swell peaks after its foot, so
    aligning FEET misaligns ENERGY (env-xcorr read the shifted lanes 30-40ms
    LATE; bass dragged audibly). The shipping verdict is lane_env_lag."""
    if len(lat_ms) < min_n:
        return 0.0
    v = np.asarray(lat_ms, dtype=np.float64)
    med = float(np.median(v))
    if abs(med) <= floor_ms or abs(med) > cap_ms:
        return 0.0
    mad = float(np.median(np.abs(v - med)))
    if mad >= 0.6 * abs(med):
        return 0.0
    return med


def lane_env_lag(env_stem, env_prod, fps=100.0, max_lag_ms=60.0,
                 floor_ms=10.0, min_corr=0.35, min_gain=0.02):
    """THE LANE LATENCY LAW, energy ruler (F6 regression court): the lag that
    maximizes the 100Hz-envelope correlation between the lane render and its
    stem IS the lane's timing error — it measures exactly what the ear hears
    (energy co-movement), no attack model, no swell assumption. Verdict only
    when the peak is REAL: corr at the peak >= min_corr and the peak beats
    zero-lag by >= min_gain (a flat xcorr = no timing information; never
    shift on noise). Returns shift in ms to ADD to note starts (positive =
    product plays too early -> move later), 0.0 = no verdict."""
    m = min(len(env_stem), len(env_prod))
    if m < 400:                                 # >=4s of evidence
        return 0.0
    es = np.asarray(env_stem[:m], dtype=np.float64)
    ep = np.asarray(env_prod[:m], dtype=np.float64)
    es = es - es.mean()
    ep = ep - ep.mean()
    if float(np.abs(es).max()) < 1e-12 or float(np.abs(ep).max()) < 1e-12:
        return 0.0
    max_lag = max(1, int(round(max_lag_ms * fps / 1000.0)))
    best_c, best_lag, c0 = -1.0, 0, 0.0
    for lag in range(-max_lag, max_lag + 1):
        if lag < 0:
            a, b = es[:lag], ep[-lag:]
        elif lag > 0:
            a, b = es[lag:], ep[:-lag]
        else:
            a, b = es, ep
        c = float(np.corrcoef(a, b)[0, 1])
        if not np.isfinite(c):
            continue
        if lag == 0:
            c0 = c
        if c > best_c:
            best_c, best_lag = c, lag
    shift_ms = best_lag * 1000.0 / fps
    if best_c < min_corr or (best_c - c0) < min_gain \
            or abs(shift_ms) <= floor_ms:
        return 0.0
    # lag > 0 pairs es[t+lag] with ep[t]: the stem's later frames match the
    # product's earlier ones -> the product plays EARLY -> starts move LATER
    # (+). lag < 0 is the mirror (product LATE -> starts move earlier). The
    # returned value is exactly what to ADD to note starts, in ms.
    return shift_ms


def band_onsets(xb, sr, min_gap_s=0.024):
    """Onset times of one lane band of the REAL stem (the timing truth)."""
    import librosa
    pk = float(np.abs(xb).max()) or 1.0
    env = librosa.onset.onset_strength(y=(xb / pk).astype(np.float32), sr=sr,
                                       hop_length=256)
    ep = float(np.percentile(env, 98)) or 1.0
    on = librosa.onset.onset_detect(onset_envelope=env / ep, sr=sr,
                                    hop_length=256, units="time",
                                    backtrack=False, delta=0.05,
                                    wait=max(1, int(min_gap_s * sr / 256)))
    return np.asarray(on)


def correct_once(song, song_path, tmp, spb, stems, iter_no, report):
    """One render->measure->correct pass. Returns #changes applied."""
    say(f"iter {iter_no}: rendering product stems…")
    files, rtracks = render_stems(song_path, tmp)
    tracks = song.get("tracks", [])
    if len(files) != len(rtracks):
        raise RuntimeError(f"render-stems gave {len(files)} files for "
                           f"{len(rtracks)} rendered tracks")
    lane_wav = {t.get("name", ""): os.path.join(tmp, f)
                for t, f in zip(rtracks, files)}
    changes = 0

    # ---- 1. GAIN LAW: group LUFS -> member lane gainDb ----
    for g, stem_path in stems.items():
        members = [t for t in tracks
                   if group_of(t.get("name", "")) == g and not t.get("muted")]
        missing = [t["name"] for t in members if t.get("name") not in lane_wav]
        if missing:
            say(f"  {g:7s}: no render for {missing} — skipped in the sum")
            members = [t for t in members if t.get("name") in lane_wav]
        if not members:
            continue
        ref, sr = load_mono(stem_path)
        l_ref = lufs(ref, sr)
        del ref
        prod, sr = sum_files([lane_wav[t["name"]] for t in members])
        l_prod = lufs(prod, sr)
        del prod
        if l_ref < -55.0:
            say(f"  {g:7s} stem near-silent ({l_ref:.1f} LUFS) — left alone")
            continue
        d = l_ref - l_prod
        step = max(-MAX_GAIN_STEP, min(MAX_GAIN_STEP, d))
        rep = report.setdefault("gain", {})
        rep[g] = {"lufs_ref": round(l_ref, 2), "lufs_prod": round(l_prod, 2),
                  "delta_db": round(d, 2)}
        say(f"  {g:7s} LUFS prod {l_prod:7.2f} ref {l_ref:7.2f} "
            f"-> {'%+.2f' % step}dB on {len(members)} lane(s)")
        if abs(step) < 0.4:
            continue
        for t in members:
            g0 = float(t.get("gainDb", 0.0))
            t["gainDb"] = round(max(-MAX_GAIN_TOTAL,
                                    min(MAX_GAIN_TOTAL, g0 + step)), 2)
            if t["gainDb"] != g0:
                changes += 1

    # ---- 2+3. DRUMS: timing re-anchor + per-hit velocity refit +
    # ----         MISSING-HIT SALVAGE (recall was 0.78: 22% of the record's
    # ----         onsets never got transcribed — insert them from the stem)
    if "drums" in stems and iter_no == 1:      # geometry once; gains may iterate
        xs, sr = load_mono(stems["drums"])
        moved = veled = born = 0
        vel_errs = []
        LEN_B = {36: 0.10, 38: 0.12, 42: 0.04, 39: 0.08, 49: 0.60}
        for t in tracks:
            gm = LANE_GM.get(t.get("name", ""))
            if gm is None or t.get("muted") or not t.get("notes"):
                continue
            lo, hi = LANE_BAND_HZ.get(gm, (0.0, 0.0))
            xb = _band_filter(xs, sr, lo, hi)
            ons = band_onsets(xb, sr)
            if not len(ons):
                continue
            # product lane render, same band — what the sampler ACTUALLY did
            xp, _ = load_mono(lane_wav[t["name"]])
            xpb = _band_filter(xp, sr, lo, hi)
            del xp
            vel_c = []                          # sampler law fit: vel - log10(pk)
            for n in t["notes"]:
                t_s = float(n["start"]) * spb
                i = int(np.argmin(np.abs(ons - t_s)))
                if abs(ons[i] - t_s) <= TIMING_REACH_S and abs(ons[i] - t_s) > 0.001:
                    n["start"] = round(float(ons[i]) / spb, 5)
                    t_s = float(ons[i])
                    moved += 1
                pk_ref = _hit_band_peak(xb, sr, t_s)
                pk_prod = _hit_band_peak(xpb, sr, t_s)
                if pk_ref > 0:
                    vel_c.append(float(n["vel"]) - math.log10(pk_ref))
                if pk_ref > 0 and pk_prod > 0:
                    dv = math.log10(pk_ref / pk_prod)
                    vel_errs.append(dv * VEL_DB_PER_UNIT)
                    if abs(dv) > 0.015:
                        n["vel"] = round(min(1.0, max(0.05,
                                                      float(n["vel"]) + dv)), 3)
                        veled += 1
            # SALVAGE: ref onsets this lane's band owns but no note answers.
            # Cymbals share the high band with Hats — only Hats salvages there
            # (a ringing crash misread as a hat is worse than a missing hat).
            if t.get("name") != "Cymbals" and vel_c:
                c = float(np.median(vel_c))
                have = np.array(sorted(float(n["start"]) * spb
                                       for n in t["notes"]))
                lane_new = []
                for o in ons:
                    if len(have) and float(np.min(np.abs(have - o))) <= 0.030:
                        continue
                    pk = _hit_band_peak(xb, sr, float(o))
                    if pk <= 0:
                        continue
                    v = c + math.log10(pk)
                    if v < 0.10:                # below the lane's real dust floor
                        continue
                    lane_new.append({"start": round(float(o) / spb, 5),
                                     "len": round(LEN_B.get(gm, 0.08) / spb, 4)
                                     if spb else 0.05,
                                     "pitch": gm,
                                     "vel": round(min(1.0, max(0.05, v)), 3)})
                cap = max(60, int(0.5 * len(t["notes"])))
                if len(lane_new) > cap:
                    lane_new = sorted(lane_new,
                                      key=lambda n: -n["vel"])[:cap]
                if lane_new:
                    t["notes"] = sorted(t["notes"] + lane_new,
                                        key=lambda n: n["start"])
                    born += len(lane_new)
            del xb, xpb
        del xs
        changes += moved + veled + born
        if vel_errs:
            report["drums"] = {
                "hits_moved": moved, "vels_refit": veled, "hits_salvaged": born,
                "vel_err_db_median_before": round(float(np.median(np.abs(vel_errs))), 2)}
            say(f"  drums: {moved} hits re-anchored, {veled} velocities refit "
                f"(median |err| was {report['drums']['vel_err_db_median_before']}dB), "
                f"{born} missing hits salvaged from the record")

    # ---- 4. THE MELODIC EAR (2026-07-16): per-note timing + velocity for
    # ----      pitched lanes through the REAL render. The kit's closed loop
    # ----      calibrated velocities against a numpy SIMULATION; the engine
    # ----      (fx chains, voice stacking, range-fill resampling) drifts from
    # ----      it, and melodic per-note timing was never measured anywhere.
    # ----      Rulers are the kit's own: pitch-band peak in the attack window,
    # ----      stem vs product lane render. Geometry once, like drums.
    if iter_no == 1:
        from scipy.signal import butter, sosfilt
        from source_kit import _pitch_band, _find_attack
        # melodic transcription lag runs past the drums' detector jitter
        # (bass sat +29ms median, mad 10 — a real tail beyond 35ms; capped
        # at 35 the re-anchor left a bimodal half-moved lane). Sparse-to-
        # moderate melodic lines (inter-onset >=100ms) tolerate the longer
        # reach; the evidence gate keeps neighbours out.
        MELODIC_REACH_S = 0.050

        def _band_meas(sig, sos, t0, t1):
            """(band peak, band RMS, window abs start, banded window) over the
            note's span. RMS is the LEVEL ruler — attack-peak level-matching
            crushed sustained beds (a wash has no attacks; our one-shots have
            high crest; peak-matching cut vox's other_sketch -18.8dB and the
            bed vanished from the mix, env 0.825 -> 0.773 over two passes).
            Peak stays for the ghost test and the TRANSIENT GATE."""
            a = max(0, int((t0 - 0.06) * sr))
            b = min(len(sig), int((t1 + 0.06) * sr))
            if b - a < 256:
                return None, 0.0, a, np.zeros(0)
            w = sosfilt(sos, sig[a:b])
            c0 = max(0, int((t0 - 0.005) * sr) - a)
            c1 = min(len(w), int((t1 + 0.010) * sr) - a)
            if c1 <= c0:
                return None, 0.0, a, w
            seg = w[c0:c1]
            return (float(np.abs(seg).max()),
                    float(np.sqrt((seg ** 2).mean())), a, w)

        for t in tracks:
            nm = t.get("name", "")
            g = group_of(nm)
            if g in (None, "drums") or t.get("muted") or not t.get("notes") \
                    or nm not in lane_wav or g not in stems:
                continue
            # THE DOUBLING GUARD (goldenbrown regression: env 0.668->0.542,
            # 2026-07-16): when a REAL audio lane of this family also SOUNDS
            # (vocals_true / vocals_sung / a tuned take), the note lane is a
            # DOUBLING — its level is a MIX choice, not a stem match. The
            # stem's level is already reproduced by the audio lane; boosting
            # the double toward it (vocals_sketch +3.5dB) triples the voice.
            fam0 = nm.split("_")[0]
            if any(t2 is not t and not t2.get("muted")
                   and (t2.get("audioClips") or [])
                   and t2.get("name", "").split("_")[0] == fam0
                   and any("_stems/" not in (c.get("file", "") or "")
                           for c in t2["audioClips"])
                   for t2 in tracks):
                say(f"  {nm}: a real {fam0} take sounds — doubling, "
                    f"ear skipped (level is a mix choice)")
                continue
            # the ruler: the family's OWN microscope stem when the import
            # decomposed it (guitar lanes vs 6s/guitar.wav), else the group's
            fam = nm.split("_")[0]
            six = os.path.join(os.path.dirname(stems[g]), "6s", f"{fam}.wav")
            ruler = six if os.path.exists(six) else stems[g]
            x_s, sr = load_mono(ruler)
            x_p, _ = load_mono(lane_wav[nm])
            # THE LANE LATENCY LAW's energy ruler: 100Hz envelopes of the
            # whole lane vs its stem (computed here, signals freed below)
            _hop = max(1, int(sr / 100))
            _me = min(len(x_s), len(x_p)) // _hop
            env_s = np.sqrt((x_s[:_me * _hop].reshape(-1, _hop) ** 2).mean(1))
            env_p = np.sqrt((x_p[:_me * _hop].reshape(-1, _hop) ** 2).mean(1))
            ny = sr / 2.0
            sos_cache = {}
            moved = 0
            rows = []                       # (note, signed vel-unit error)
            ghosts = []                     # notes the record never played
            anchored = set()                # individually re-anchored notes
            meas = []                       # (note, pk_s, pk_p) — the SILENCE
                                            # COURT's docket (relative floor)
            for n in t["notes"]:
                p = int(n["pitch"])
                if p not in sos_cache:
                    f0 = 440.0 * 2.0 ** ((p - 69) / 12.0)
                    lo, hi = _pitch_band(f0, sr)
                    sos_cache[p] = butter(4, [lo / ny, min(hi, ny * 0.99) / ny],
                                          "band", output="sos")
                t0 = float(n["start"]) * spb
                t1 = t0 + min(max(0.02, float(n["len"]) * spb), 0.35)
                pk_s, rms_s, a, ws = _band_meas(x_s, sos_cache[p], t0, t1)
                if pk_s is None:
                    continue
                # the stem's own attack near the start (per-note re-anchor
                # evidence; lane-wide timing is judged by the ENERGY ruler)
                off, foot_ok = 0.0, False
                if pk_s > 1e-5:
                    try:
                        off = (a / sr + _find_attack(ws, sr, t0 - a / sr,
                                                     search_s=MELODIC_REACH_S
                                                     + 0.01) / sr - t0)
                    except Exception:
                        off = 0.0
                    if abs(off) <= MELODIC_REACH_S:
                        # evidence gate: the found attack must be a real event
                        # of THIS note's band (>=half its own peak), not bleed
                        j0 = max(0, int((t0 + off - 0.003) * sr) - a)
                        j1 = min(len(ws), j0 + int(0.02 * sr))
                        foot_ok = (j1 > j0 and
                                   float(np.abs(ws[j0:j1]).max()) >= 0.5 * pk_s)
                # THE TRANSIENT GATE: re-anchor only notes with a REAL
                # articulation (crest >= ~10dB). In a sustained bed the
                # "attack foot" is fiction — anchoring to the steepest rise
                # of a wash injects +-50ms jitter, never truth.
                if foot_ok and abs(off) > 0.004 and rms_s > 0 \
                        and pk_s > rms_s * 3.2:
                    n["start"] = round((t0 + off) / spb, 5)
                    t0, t1 = t0 + off, t1 + off
                    moved += 1
                    anchored.add(id(n))
                pk_p, rms_p, _, _ = _band_meas(x_p, sos_cache[p], t0, t1)
                if pk_p is None:
                    continue
                # THE GHOST CULL (gb2 autopsy: piano p90 vel-err 45dB = a tail
                # of fantasy notes): we play CLEARLY (>-60dB) where the record's
                # band holds digital silence (<-94dB) -> the note never happened
                if pk_s < 2e-5 and pk_p > 1e-3:
                    ghosts.append(n)
                    continue
                meas.append((n, pk_s, pk_p))
                if rms_s <= 1e-6 or rms_p <= 1e-7:
                    continue
                rows.append((n, math.log10(rms_s / rms_p)))
            del x_s, x_p
            # THE SILENCE COURT (F6, _import_bench: 33 guitar notes at vel
            # 0.55-0.70 inside the record's INSTRUMENTAL-SILENCE intro; the
            # absolute cull needs digital silence <-94dB and a separated
            # stem's bleed floor sits ~-60 — every ghost survived). RELATIVE
            # floor: the stem's window >=40dB under the lane's own BODY
            # (p90 of measured note peaks) while the product clearly plays
            # = the record does not play there. Same 20% distrust bound.
            if len(meas) >= 12:
                body = float(np.percentile([m[1] for m in meas], 90))
                floor = body * 10.0 ** (-40.0 / 20.0)
                if floor > 2e-5:               # meaningless under digital floor
                    rel = [m[0] for m in meas
                           if m[1] < floor and m[2] > 1e-3]
                    if rel:
                        dead_r = {id(q) for q in rel}
                        rows = [(q, dv) for q, dv in rows
                                if id(q) not in dead_r]
                        ghosts.extend(rel)
            culled = 0
            # THE TRUST BOUND, coherence-refined (F6: piano_lead sat at
            # 22-23% candidates on BOTH goldenbrowns — just over the bound —
            # while its surviving rows measured mad 0.5-1.0dB. A mismatched
            # ruler cannot measure 78% of a lane coherently; a coherent
            # ruler's big docket is a REAL fantasy tail, so it earns a
            # deeper cull. Incoherent rulers keep the strict bound.
            trust = 0.20
            if rows:
                _d = np.array([d for _, d in rows])
                if float(np.median(np.abs(_d - np.median(_d)))) \
                        * VEL_DB_PER_UNIT <= 3.5:
                    trust = 0.35
            if ghosts and len(ghosts) <= trust * len(t["notes"]):
                dead = {id(q) for q in ghosts}
                t["notes"] = [q for q in t["notes"] if id(q) not in dead]
                culled = len(ghosts)
                changes += culled
            elif len(ghosts) > trust * len(t["notes"]):
                # past even the earned bound: the RULER is suspect (family
                # stem vs transcription source mismatch) — cull nothing
                say(f"  {nm}: {len(ghosts)} ghost candidates exceed the "
                    f"{trust:.0%} trust bound — ruler distrusted, "
                    f"nothing culled")
                ghosts = []
            # THE LANE LATENCY LAW (energy ruler): the env-xcorr lag between
            # the lane render and its stem is the lane's timing error — it
            # measures what the ear hears. (The attack-foot docket shifted
            # swell lanes the WRONG way: feet aligned, energy 30-40ms late,
            # bass dragged — regression court 2026-07-17, Chezy's ears.)
            lat_ms = lane_env_lag(env_s, env_p)
            lat_shift = 0
            if lat_ms:
                d_beats = (lat_ms / 1000.0) / spb
                for q in t["notes"]:
                    if id(q) not in anchored:
                        q["start"] = round(max(0.0, float(q["start"])
                                               + d_beats), 5)
                        lat_shift += 1
                if lat_shift:
                    changes += 1
                    say(f"  {nm}: energy rides {-lat_ms:+.1f}ms off the "
                        f"record (env-xcorr) — {lat_shift} notes shifted "
                        f"{lat_ms:+.1f}ms as one body")
            veled = 0
            med_db = 0.0
            if rows:
                # a whole-lane offset is a LEVEL problem, not 400 velocity
                # problems: the signed median lands in gainDb (velocities
                # near 1.0 cannot express "louder" — other_sketch sat 18dB
                # under its stem with velocities pinned), residuals per note.
                dvs = np.array([d for _, d in rows])
                med = float(np.median(dvs))
                med_db = med * VEL_DB_PER_UNIT
                # THE COHERENCE GATE (vox regression court #2): a real level
                # offset is CONSISTENT across notes (piano mad ~2dB, bass
                # 0.9). The residual-bucket lane measured mad 11.3dB — pitch
                # windows over heterogeneous bed content = noise, and a
                # median of noise is not a level truth (cutting by it dropped
                # env 0.825 -> 0.773). Incoherent lanes leave LEVEL to the
                # group law; timing + ghosts (absolute evidence) stand.
                mad_db0 = float(np.median(np.abs(dvs - med))) * VEL_DB_PER_UNIT
                if mad_db0 > 3.5:
                    say(f"  {nm}: per-note level incoherent (mad "
                        f"{mad_db0:.1f}dB) — level left to the group law")
                    rows = []
                    med_db = 0.0
                if abs(med_db) > 3.0:
                    g0 = float(t.get("gainDb", 0.0))
                    t["gainDb"] = round(max(-MAX_GAIN_TOTAL,
                                            min(MAX_GAIN_TOTAL,
                                                g0 + max(-MAX_GAIN_STEP,
                                                         min(MAX_GAIN_STEP,
                                                             med_db)))), 2)
                    changes += 1
                else:
                    med = 0.0
                for n, dv in rows:
                    r = float(np.clip(dv - med, -0.3, 0.3)) * 0.8   # damped
                    if abs(r) > 0.015:
                        n["vel"] = round(min(1.0, max(0.05,
                                                      float(n["vel"]) + r)), 3)
                        veled += 1
            if moved or veled or culled or lat_shift or abs(med_db) > 3.0:
                t["notes"] = sorted(t["notes"], key=lambda q: q["start"])
                changes += moved + veled
                mad = round(float(np.median(np.abs(
                    [d * VEL_DB_PER_UNIT - med_db for _, d in rows]))), 2) if rows else 0.0
                report.setdefault("melodic", {})[nm] = {
                    "starts_reanchored": moved, "vels_refit": veled,
                    "ghosts_culled": culled,
                    "lane_gain_db": round(med_db, 2) if abs(med_db) > 3.0 else 0.0,
                    "lane_latency_ms": round(lat_ms, 1),
                    "vel_err_db_mad_before": mad}
                say(f"  {nm}: {moved} starts re-anchored, {veled} velocities "
                    f"refit"
                    + (f", {culled} ghosts culled" if culled else "")
                    + (f", lane level {med_db:+.1f}dB -> gain"
                       if abs(med_db) > 3.0 else "")
                    + f" (per-note |err| mad {mad}dB)")

    # ---- 5. THE IMAGE LAW (2026-07-16): every lane sits WHERE THE RECORD
    # ----      PUT IT. Drum kits are mono by construction and imports never
    # ----      set a pan — the whole pre-master image collapsed to center,
    # ----      and the master width match could only crank what little side
    # ----      existed. Closed loop: the stem's stereo balance in the lane's
    # ----      own band is the target; the lane render's balance is the
    # ----      state; pan nudges toward it (engine curve is steep — measured
    # ----      pan 0.3 -> balance +0.6 — so the step is damped and iterates).
    # ----      Bass group exempt: the sub stays center (doctor law).
    for t in tracks:
        nm = t.get("name", "")
        g = group_of(nm)
        if g in (None, "bass") or t.get("muted") or not t.get("notes") \
                or nm not in lane_wav or g not in stems:
            continue
        gm = LANE_GM.get(nm)
        if gm is not None:
            lo, hi = LANE_BAND_HZ.get(gm, (0.0, 0.0))
            if hi <= lo:                   # LANE_BAND_HZ convention: hi==0 =
                hi = 20000.0               # "to Nyquist" (Hats/Cymbals bands)
        else:
            ps = sorted(int(n["pitch"]) for n in t["notes"])
            f_lo = 440.0 * 2.0 ** ((ps[len(ps) // 10] - 69) / 12.0)
            f_hi = 440.0 * 2.0 ** ((ps[(len(ps) * 9) // 10] - 69) / 12.0)
            lo, hi = f_lo * 0.75, min(f_hi * 6.0, 12000.0)
        if hi <= lo:
            continue
        fam = nm.split("_")[0]
        six = os.path.join(os.path.dirname(stems[g]), "6s", f"{fam}.wav")
        ruler = six if os.path.exists(six) else stems[g]
        b_s = band_balance(ruler, lo, hi)
        b_p = band_balance(lane_wav[nm], lo, hi)
        if b_s is None or b_p is None or abs(b_s - b_p) <= 0.08:
            continue
        pan0 = float(t.get("pan", 0.0))
        t["pan"] = round(max(-0.85, min(0.85, pan0 + 0.35 * (b_s - b_p))), 3)
        if abs(t["pan"] - pan0) < 0.01:
            t.pop("pan", None) if pan0 == 0.0 else None
            continue
        changes += 1
        report.setdefault("image", {})[nm] = {
            "balance_stem": round(b_s, 3), "balance_prod": round(b_p, 3),
            "pan": t["pan"]}
        say(f"  {nm}: image {b_p:+.2f} -> target {b_s:+.2f}, pan {pan0:+.2f}"
            f" -> {t['pan']:+.2f}")

    # ---- 6. THE CREDIBILITY COURT (2026-07-16, goldenbrown_vox autopsy:
    # ----      Perc env-corr 0.195 vs the record = a lane of NOISE wearing a
    # ----      drum's name; the band rail manufactured it from bleed). A drum
    # ----      lane must CO-MOVE with the record inside its own band. Judged
    # ----      once, on the 100Hz envelope correlation of the lane render vs
    # ----      the drum stem, both band-limited to the lane's band: < 0.25
    # ----      with a real docket (>=8 notes) -> MUTED + receipt. The notes
    # ----      stay — un-muting is one click, and accept adopts the verdict.
    if iter_no == 1 and "drums" in stems:
        xs, srd = load_mono(stems["drums"])
        for t in tracks:
            nm = t.get("name", "")
            gm = LANE_GM.get(nm)
            if gm is None or t.get("muted") or len(t.get("notes", [])) < 8 \
                    or nm not in lane_wav:
                continue
            lo, hi = LANE_BAND_HZ.get(gm, (0.0, 0.0))
            if hi <= lo:
                continue
            xb = _band_filter(xs, srd, lo, hi)
            xp, _ = load_mono(lane_wav[nm])
            xpb = _band_filter(xp, srd, lo, hi)
            del xp
            hop = max(1, int(srd / 100))
            m = min(len(xb), len(xpb)) // hop
            if m < 400:                     # need real evidence to convict
                del xb, xpb
                continue
            ea = np.sqrt((xb[:m * hop].reshape(-1, hop) ** 2).mean(1))
            eb = np.sqrt((xpb[:m * hop].reshape(-1, hop) ** 2).mean(1))
            del xb, xpb
            c = float(np.corrcoef(ea, eb)[0, 1])
            if np.isfinite(c) and c < 0.25:
                t["muted"] = True
                changes += 1
                report.setdefault("credibility", {})[nm] = round(c, 3)
                say(f"  {nm}: band env corr {c:.2f} vs the record — noise "
                    f"wearing a drum's name, muted (court receipt filed)")
        del xs
    return changes


def full_check(song_path, stems, tmp):
    """Render the finished product and score it against the stem-sum record."""
    from spectral import verify_arrays
    out = os.path.join(tmp, "_product.wav")
    r = subprocess.run([M1, "render", song_path, out],
                       capture_output=True, text=True, timeout=1800)
    if r.returncode != 0:
        raise RuntimeError(f"m1 render rc={r.returncode}: {r.stderr[-300:]}")
    rec, sr = sum_files(list(stems.values()))
    prod, _ = load_mono(out)
    m = min(len(rec), len(prod))
    v = verify_arrays(rec[:m], prod[:m], sr)
    l_r, l_p = lufs(rec[:m], sr), lufs(prod[:m], sr)
    return {"spectral_pct": v.get("spectral_pct"), "env_corr": v.get("env_corr"),
            "lufs_record": round(l_r, 2), "lufs_product": round(l_p, 2),
            "lufs_delta": round(l_p - l_r, 2)}


def correct(song_path, iters=2, verify=True, keep_tmp=False):
    song = json.load(open(song_path))
    spb = 60.0 / float(song.get("bpm", 120.0))
    stems = stem_paths_from_song(song)
    if not stems:
        say("no *_stems/ references in this song — nothing to correct against")
        return None
    say(f"stems found: {sorted(stems)} — the record is the target")
    tmp = tempfile.mkdtemp(prefix="a2m_correct_")
    report = {"song": os.path.relpath(song_path, ROOT), "iters": 0}
    try:
        for it in range(1, iters + 1):
            ch = correct_once(song, song_path, tmp, spb, stems, it, report)
            report["iters"] = it
            json.dump(song, open(song_path, "w"), indent=1)
            say(f"iter {it}: {ch} corrections written")
            if ch == 0:
                break
            for f in os.listdir(tmp):          # fresh render next pass
                if f.endswith(".wav"):
                    os.remove(os.path.join(tmp, f))
        if verify:
            say("final verify: rendering the corrected product…")
            report["final"] = full_check(song_path, stems, tmp)
            say(f"FINAL vs record: spectral {report['final']['spectral_pct']}% "
                f"LUFS delta {report['final']['lufs_delta']:+.2f}dB "
                f"(record {report['final']['lufs_record']}, "
                f"product {report['final']['lufs_product']})")
    finally:
        if not keep_tmp:
            shutil.rmtree(tmp, ignore_errors=True)
        try:                       # receipts contract: the correction leaves
            sd = os.path.splitext(song_path)[0] + "_stems"   # a machine trace
            if os.path.isdir(sd):
                json.dump(report, open(os.path.join(sd, "a2m_report.json"),
                                       "w"), indent=1)
        except Exception:
            pass
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("song", help="songs/<name>.json (an imported product)")
    ap.add_argument("--iters", type=int, default=2)
    ap.add_argument("--no-verify", action="store_true",
                    help="skip the final full render + score")
    ap.add_argument("--report", default=None, help="write report json here")
    a = ap.parse_args()
    rep = correct(a.song, iters=a.iters, verify=not a.no_verify)
    if rep and a.report:
        json.dump(rep, open(a.report, "w"), indent=1)
        say(f"report -> {a.report}")


if __name__ == "__main__":
    main()
