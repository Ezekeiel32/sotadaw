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
      4. WALL RELIEF   lanes matched to stems means the pre-master sum sits
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
    "other": ("other_sketch", "guitar_sketch", "piano_sketch", "keys_sketch"),
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
    rp = song_path
    if len(kept) != len(tracks):
        song["tracks"] = kept
        rp = os.path.join(out_dir, "_strip.json")
        json.dump(song, open(rp, "w"))
    try:
        r = subprocess.run([M1, "render-stems", rp, out_dir],
                           capture_output=True, text=True, timeout=1800)
    finally:
        if rp != song_path and os.path.exists(rp):
            os.remove(rp)
    if r.returncode != 0:
        raise RuntimeError(f"m1 render-stems rc={r.returncode}: {r.stderr[-300:]}")
    return (sorted(f for f in os.listdir(out_dir) if f.endswith(".wav")),
            kept)


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
