#!/usr/bin/env python3
"""A2 — THE DIFFERENTIAL EAR (docs/THE_PHYSICS.md §6; gap G3; law E3).

Any two renders subtract into a residual that testifies. JSON receipts say what
was ASKED; null receipts say what the AIR did. The SCALPEL's surgical{} verdict
gains its audio grounding here: "claimed kick-only: kick delta active, 6 other
stems null < -120 dBFS => SURGICAL (AUDIO-PROVEN)".

usage:
  null_bench.py wavs a.wav b.wav                       compare two files
  null_bench.py songs a.json b.json [--stems]          render both (sealed m1), compare
  null_bench.py stems dirA dirB [--claim t1,t2] [--bar -120]
  null_bench.py --selftest [--keep]                    the 3-case proof x3 seeds
Prints NULL_JSON <payload>. Exit 0 = null/claim verdict holds (selftest: all green).

Physics notes: the SEAL (EB1) pins render bytes, so offset MUST measure 0 between
takes of the same song — it is measured anyway and reported (a nonzero offset on
sealed renders is itself a finding). 24-bit file floor is ~-144 dBFS; the no-op
bar sits at -120 (honest margin), the E3 out-of-scope bar at -90 (master-bus
nonlinearity margin).
"""
import json
import math
import os
import shutil
import subprocess
import sys

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "songs")
M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")

BANDS = (("low_20_120", 20, 120), ("lowmid_120_500", 120, 500),
         ("mid_500_2k", 500, 2000), ("himid_2k_6k", 2000, 6000),
         ("high_6k_up", 6000, None))


def _db(v, floor=-200.0):
    return round(20.0 * math.log10(v), 2) if v > 10 ** (floor / 20.0) else floor


def _read(path):
    x, sr = sf.read(path, always_2d=True, dtype="float64")
    return x, sr


def _offset(a, b, sr, span_s=10.0, max_lag=4096):
    """lag of b relative to a (samples), by cross-correlation of mono heads."""
    n = min(len(a), len(b), int(span_s * sr))
    am = a[:n].mean(axis=1)
    bm = b[:n].mean(axis=1)
    if not am.any() or not bm.any():
        return 0
    from scipy.signal import correlate
    c = correlate(am, bm, mode="full", method="fft")
    lags = np.arange(-n + 1, n)
    w = (lags >= -max_lag) & (lags <= max_lag)
    return int(lags[w][np.argmax(c[w])])


def compare_wavs(pa, pb, bar=-120.0):
    a, sra = _read(pa)
    b, srb = _read(pb)
    out = {"a": pa, "b": pb, "bar_dbfs": bar}
    if sra != srb:
        out["error"] = f"sample-rate mismatch {sra} vs {srb}"
        return out
    off = _offset(a, b, sra)
    out["offset_samples"] = off
    if off > 0:
        b = b[off:]
    elif off < 0:
        a = a[-off:]
    n = min(len(a), len(b))
    out["length_delta_samples"] = int(len(a) - len(b))
    ch = min(a.shape[1], b.shape[1])
    r = a[:n, :ch] - b[:n, :ch]
    rm = r.mean(axis=1)
    rms = float(np.sqrt(np.mean(rm ** 2))) if n else 0.0
    peak = float(np.max(np.abs(r))) if n else 0.0
    out["residual_rms_dbfs"] = _db(rms)
    out["residual_peak_dbfs"] = _db(peak)
    out["null"] = out["residual_rms_dbfs"] <= bar
    # per-band residual
    bands = {}
    for name, lo, hi in BANDS:
        hi_eff = min(hi or sra / 2 - 100, sra / 2 - 100)
        sos = butter(4, [lo, hi_eff], btype="bandpass", fs=sra, output="sos")
        bands[name] = _db(float(np.sqrt(np.mean(sosfilt(sos, rm) ** 2))))
    out["residual_bands_dbfs"] = bands
    # residual-over-time strip (where in the song the change lives)
    hops = max(1, min(96, int(n / sra / 0.5)))
    hop = max(1, n // hops)
    out["residual_strip_dbfs"] = [
        _db(float(np.sqrt(np.mean(rm[i * hop:(i + 1) * hop] ** 2))))
        for i in range(hops)]
    try:
        if out["residual_rms_dbfs"] > -70:
            import pyloudnorm
            v = pyloudnorm.Meter(sra).integrated_loudness(rm)
            out["residual_lufs"] = round(float(v), 2) if np.isfinite(v) else None
    except Exception:
        pass
    return out


def _render(song_path, tag):
    wv = os.path.join(SONGS, f"_null_{tag}.wav")
    r = subprocess.run([M1, "render", song_path, wv], capture_output=True,
                       text=True, timeout=600)
    return wv if "ok=1" in (r.stdout + r.stderr) else None


def _render_stems(song_path, tag):
    d = os.path.join(SONGS, f"_null_{tag}_stems")
    r = subprocess.run([M1, "render-stems", song_path, d], capture_output=True,
                       text=True, timeout=900)
    return d if os.path.isdir(d) else None


def compare_stem_dirs(da, db_, claim=None, bar=-120.0):
    """Per-track nulls + the claim court. claim = track names EXPECTED to change."""
    claim = set(claim or [])

    def stems(d):
        m = {}
        for f in sorted(os.listdir(d)):
            if f.endswith(".wav"):
                name = f.split("_", 1)[1][:-4] if "_" in f else f[:-4]
                m[name] = os.path.join(d, f)
        return m

    sa, sb = stems(da), stems(db_)
    tracks = {}
    unclaimed_active, claimed_quiet = [], []
    for name in sorted(set(sa) | set(sb)):
        if name not in sa or name not in sb:
            tracks[name] = {"null": False, "residual_dbfs": None,
                            "note": "present on one side only"}
            if name not in claim:
                unclaimed_active.append(name)
            continue
        c = compare_wavs(sa[name], sb[name], bar=bar)
        tracks[name] = {"null": c["null"], "residual_dbfs": c["residual_rms_dbfs"],
                        "residual_peak_dbfs": c["residual_peak_dbfs"]}
        if not c["null"] and name not in claim:
            unclaimed_active.append(name)
        if c["null"] and name in claim:
            claimed_quiet.append(name)
    verdict = {
        "tracks": tracks,
        "claim": sorted(claim),
        "unclaimed_active": unclaimed_active,
        "claimed_but_null": claimed_quiet,
        "surgical_audio_proven": not unclaimed_active,
        "bar_dbfs": bar,
    }
    if claim:
        n_null = sum(1 for t, v in tracks.items() if v["null"])
        verdict["summary"] = (
            f"claimed {sorted(claim)}: "
            + ", ".join(f"{t} Δ {tracks[t]['residual_dbfs']} dB"
                        for t in sorted(claim) if t in tracks)
            + f"; {n_null} other stems null <= {bar} "
            + ("✓ SURGICAL (AUDIO-PROVEN)" if not unclaimed_active
               else f"✗ OUT OF SCOPE: {unclaimed_active}"))
    return verdict


# ---------------------------------------------------------------- selftest
def _mini_song(seed):
    import random
    rng = random.Random(seed)
    roots = rng.choice([[36, 39, 41, 36], [38, 41, 43, 38], [36, 41, 44, 36]])
    kick = [{"start": b, "len": 0.4, "pitch": 36, "vel": 0.95} for b in range(0, 8, 2)]
    hat = [{"start": b * 0.5, "len": 0.15, "pitch": 70,
            "vel": 0.5 + 0.05 * (b % 3)} for b in range(16)]
    bass = [{"start": i * 2.0, "len": 1.6, "pitch": roots[i], "vel": 0.8}
            for i in range(4)]
    mk = lambda nm, src, notes: {"name": nm, "source": {"kind": "faust", "id": src},
                                 "gainDb": -6.0, "notes": notes}
    return {"version": 2, "bpm": 120, "lengthBars": 2, "masterGainDb": 0,
            "master": [],
            "tracks": [mk("kick", "kick_808", kick), mk("hat", "hat", hat),
                       mk("bass", "bass_warm", bass)]}


def _write_song(song, tag):
    p = os.path.join(SONGS, f"_null_{tag}.json")
    with open(p, "w") as f:
        json.dump(song, f, indent=1)
    return p


def _cleanup(keep=False):
    if keep:
        return
    for f in os.listdir(SONGS):
        if f.startswith("_null_"):
            p = os.path.join(SONGS, f)
            (shutil.rmtree(p, ignore_errors=True) if os.path.isdir(p)
             else os.remove(p))


def selftest(keep=False):
    checks, fails = [], []

    def check(nm, ok, detail=""):
        checks.append({"name": nm, "ok": bool(ok), "detail": str(detail)[:220]})
        if not ok:
            fails.append(nm)
        print(("  ok " if ok else "FAIL ") + f"{nm}  {detail}", flush=True)

    try:
        for seed in (11, 23, 47):
            base = _mini_song(seed)
            pa = _write_song(base, f"a{seed}")

            # case 1: no-op copy => everything nulls
            pb = _write_song(json.loads(json.dumps(base)), f"b{seed}")
            da, db_ = _render_stems(pa, f"a{seed}"), _render_stems(pb, f"b{seed}")
            if not da or not db_:
                check(f"seed{seed} renders", False, "stems render failed")
                continue
            v = compare_stem_dirs(da, db_, claim=None)
            allnull = all(t["null"] for t in v["tracks"].values())
            worst = max((t["residual_dbfs"] or -200)
                        for t in v["tracks"].values())
            check(f"seed{seed} C1 no-op edit nulls everywhere (worst {worst} dBFS)",
                  allnull and v["surgical_audio_proven"], worst)

            # case 2: kick-only +0.5 dB => kick active, others null, claim holds
            kicked = json.loads(json.dumps(base))
            kicked["tracks"][0]["gainDb"] += 0.5
            pk = _write_song(kicked, f"k{seed}")
            dk = _render_stems(pk, f"k{seed}")
            v2 = compare_stem_dirs(da, dk, claim=["kick"])
            kick_active = not v2["tracks"]["kick"]["null"]
            check(f"seed{seed} C2 +0.5dB kick flags kick and ONLY kick",
                  kick_active and v2["surgical_audio_proven"],
                  v2.get("summary", ""))

            # case 3: broken claim (kick AND hat edited, kick claimed) => RED
            broken = json.loads(json.dumps(base))
            broken["tracks"][0]["gainDb"] += 0.5
            broken["tracks"][1]["notes"] = broken["tracks"][1]["notes"][::2]
            pbr = _write_song(broken, f"x{seed}")
            dbr = _render_stems(pbr, f"x{seed}")
            v3 = compare_stem_dirs(da, dbr, claim=["kick"])
            check(f"seed{seed} C3 broken claim turns RED (hat out of scope)",
                  (not v3["surgical_audio_proven"])
                  and "hat" in v3["unclaimed_active"], v3["unclaimed_active"])

        result = {"pass": not fails, "failing": fails, "checks": checks}
    finally:
        _cleanup(keep)
    print("NULL_JSON " + json.dumps(result))
    print(f"\n== NULL BENCH: {len(checks) - len(fails)} pass / {len(fails)} fail ==")
    return 0 if not fails else 1


# ---------------------------------------------------------------- cli
def main():
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    if a[0] == "--selftest":
        return selftest("--keep" in a)

    def opt(flag, default=None):
        return a[a.index(flag) + 1] if flag in a else default

    bar = float(opt("--bar", "-120"))
    if a[0] == "wavs":
        r = compare_wavs(a[1], a[2], bar=bar)
        print("NULL_JSON " + json.dumps(r))
        return 0 if r.get("null") else 1
    if a[0] == "songs":
        wa, wb = _render(a[1], "sa"), _render(a[2], "sb")
        if not wa or not wb:
            print("NULL_JSON " + json.dumps({"error": "render failed"}))
            return 2
        r = {"mix": compare_wavs(wa, wb, bar=bar)}
        if "--stems" in a:
            da, db_ = _render_stems(a[1], "sa"), _render_stems(a[2], "sb")
            claim = [c for c in (opt("--claim") or "").split(",") if c]
            r["stems"] = compare_stem_dirs(da, db_, claim=claim, bar=bar)
        print("NULL_JSON " + json.dumps(r))
        _cleanup()
        return 0
    if a[0] == "stems":
        claim = [c for c in (opt("--claim") or "").split(",") if c]
        r = compare_stem_dirs(a[1], a[2], claim=claim, bar=bar)
        print("NULL_JSON " + json.dumps(r))
        return 0 if r["surgical_audio_proven"] else 1
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
