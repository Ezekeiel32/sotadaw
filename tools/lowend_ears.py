#!/usr/bin/env python3
"""THE LOW-END EARS — audio-domain twins of the low-end court (wave 16;
R-5 item 050 sub-mono, R-16 item 077 translation, R-5 item 051 co-peak).

The symbolic court (lowend_court.py) judges what the JSON can show —
panned subs, widen fx, note pileups. THESE ears judge what only the
RENDERED wav can show: a stereo-voiced patch smearing the sub band, a
pure-sine 808 that vanishes on small speakers, kick+bass co-peaking in
the same 1/3-octave bin. Pure numpy/scipy on the wav — deterministic,
no models, no tokens.

  measure(wav)               -> {sub_corr, sub_side_ratio, sine_ratio,
                                 sub_rms_db, f0_med} raw metrics
  court_sub_mono(wav|m)      050: sub band (<120Hz) must be MONO —
                                 correlation + side/mid energy verdict
  heal_sub_mono(song, v)     master fx_ms_eq side_low cut at 120Hz,
                                 inserted BEFORE the wall (order law)
  court_translation(wav|m, song, genre)
                             077: a phone-first-genre 808 whose partials
                                 sit at the corpus tail (pure sine) gets
                                 an ADVISORY carrying the drive recipe —
                                 missing-fundamental physics, never an
                                 auto-conviction (see calibration below)
  heal_translation(song, v)  raise the source's native `drive` (zone
                                 0.5..5) — harmonics from the voice
                                 itself, never a bolted-on saturator;
                                 serves EXPLICIT asks only
  court_copeak(wav|m, song)  051: kick transient + bass sustain sharing
                                 one 1/3-octave bin = masking (ADVISORY —
                                 arrangement taste varies)
  court_ears(wav, song, genre, heal=False)  aggregate, heal ledgers

Thresholds are CORPUS-CALIBRATED (self-measure law, 217 rendered wavs,
2026-07-15): sub_corr p1=0.798 / side_ratio p99=0.394, so the conviction
edges (0.55 / 0.40) sit beyond the whole corpus mass; eval_ambient
(corr 0.65, side 0.525 — a blind-judge WINNER) proved wide sub IS the
texture-genre aesthetic -> _TEXTURE_EXEMPT; _anxrofo proved imports trip
it with the record's own truth -> THE WITNESS LAW. sine_ratio p50=0.053
with goldenbrown (a REAL imported record) at 0.0032 proved the master-wav
partial ratio cannot separate 'won't translate' from 'sub loud in a
sparse low-mid mix' -> translation is ADVISORY-ONLY (the heal exists for
explicit asks, never auto). After the full-band FFT fix the distribution
re-measured p1=0.098 / p50=0.436 over 180 wavs; the advisory floor (0.07)
sits under every corpus member incl. chezy_song_2 (accepted, 0.093).
"""
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

SUB_HZ = 120.0
# full-band recalibration (180 wavs, 2026-07-15): sine_ratio p1=0.098,
# p50=0.436; purest corpus members goldenbrown_vox 0.077 (imported record,
# witness-exempt) and chezy_song_2 0.093 (an ACCEPTED take). 0.07 sits
# under every corpus member; the bare-sine crime class measures ~0.00x.
SINE_RATIO_FLOOR = 0.07
SUB_CORR_FLOOR = 0.55     # corpus p1=0.798; only physical collapse convicts
SIDE_RATIO_CEIL = 0.40    # corpus p99=0.394

# wide low-end is the AESTHETIC in texture genres (eval_ambient winner law)
_TEXTURE_EXEMPT = ("ambient", "drone", "dark_ambient", "cinematic",
                   "soundscape", "field", "new_age", "meditation",
                   "atmospheric", "dungeon_synth", "lowercase")


def _is_imported(song):
    """THE WITNESS LAW: stems-imported records (sketch/identity lanes)
    are evidence, never defendants."""
    for t in (song or {}).get("tracks", []) or []:
        nm = str((t or {}).get("name", "")).lower() if isinstance(t, dict) else ""
        if nm.endswith("_sketch") or nm.endswith("_identity"):
            return True
    return False


def _read(wav):
    import soundfile as sf
    x, sr = sf.read(wav, always_2d=True, dtype="float64")
    if x.shape[1] == 1:
        x = np.repeat(x, 2, axis=1)
    return x[:, :2], sr


def _butter_lp(x, sr, hz, order=4):
    from scipy.signal import butter, sosfiltfilt
    sos = butter(order, hz / (sr / 2.0), btype="low", output="sos")
    return sosfiltfilt(sos, x, axis=0)


def measure(wav_or_arr, sr=None):
    """Raw low-end metrics. Accepts a path or (N,2) float array + sr."""
    if isinstance(wav_or_arr, str):
        x, sr = _read(wav_or_arr)
    else:
        x = np.asarray(wav_or_arr, dtype="float64")
        if x.ndim == 1:
            x = np.stack([x, x], axis=1)
    n = len(x)
    if n < sr // 2:
        return {"ok": False, "why": "too short"}
    sub = _butter_lp(x, sr, SUB_HZ)
    frame, hop = 4096, 2048
    l, r = sub[:, 0], sub[:, 1]
    mid, side = (l + r) / 2.0, (l - r) / 2.0
    full_rms = float(np.sqrt(np.mean(x ** 2)) + 1e-12)
    corrs, srats, amps = [], [], []
    for i in range(0, n - frame, hop):
        fl, fr = l[i:i + frame], r[i:i + frame]
        fm, fs = mid[i:i + frame], side[i:i + frame]
        rm = float(np.sqrt(np.mean(fm ** 2)))
        amps.append(rm)
        if rm < full_rms * 0.05:      # sub quiet in this frame: no vote
            continue
        sl, sr_ = float(np.std(fl)), float(np.std(fr))
        if sl > 1e-9 and sr_ > 1e-9:
            corrs.append(float(np.corrcoef(fl, fr)[0, 1]))
        srats.append(float(np.sqrt(np.mean(fs ** 2))) / (rm + 1e-12))
    active = len(corrs)
    sub_rms = float(np.sqrt(np.mean(mid ** 2)))
    out = {"ok": True, "active_frames": active,
           "sub_rms_db": round(20 * np.log10(sub_rms + 1e-12), 1),
           "sub_vs_full_db": round(20 * np.log10((sub_rms + 1e-12) /
                                                 full_rms), 1)}
    if active >= 8:
        out["sub_corr"] = round(float(np.median(corrs)), 3)
        out["sub_side_ratio"] = round(float(np.median(srats)), 3)
    # ---- sine-purity of the sub: peak in 32..110Hz vs its 2nd+3rd partials.
    # FULL-BAND mid, not the sub-filtered one — the partials being measured
    # live ABOVE the sub band (the battery caught the LP eating its own
    # evidence: a planted 0.375 ratio read 0.20 through the filter).
    nfft = 16384
    if n >= nfft * 2:
        m = x.mean(axis=1)
        win = np.hanning(nfft)
        ratios, f0s = [], []
        for i in range(0, n - nfft, nfft // 2):
            # gate on SUB-band activity, analyze the FULL band
            if float(np.sqrt(np.mean(mid[i:i + nfft] ** 2))) < full_rms * 0.05:
                continue
            spec = np.abs(np.fft.rfft(m[i:i + nfft] * win))
            freqs = np.fft.rfftfreq(nfft, 1.0 / sr)
            lo_i, hi_i = np.searchsorted(freqs, 32), np.searchsorted(freqs, 110)
            if hi_i - lo_i < 4:
                break
            p = lo_i + int(np.argmax(spec[lo_i:hi_i]))
            # parabolic peak interpolation: the raw bin grid (2.7Hz at
            # 16384/44k1) is +-42 CENTS at 55Hz — the key court's
            # stability gate would starve on quantization alone
            if 0 < p < len(spec) - 1:
                a, b, c = float(spec[p - 1]), float(spec[p]), \
                    float(spec[p + 1])
                den = a - 2 * b + c
                delta = 0.5 * (a - c) / den if abs(den) > 1e-12 else 0.0
                f0 = (p + max(min(delta, 0.5), -0.5)) * float(freqs[1])
            else:
                f0 = freqs[p]
            h1 = float(spec[max(p - 1, 0):p + 2].max())
            if h1 <= 0:
                continue

            def _mag(mult):
                c = int(round(f0 * mult / freqs[1]))
                return float(spec[max(c - 2, 0):c + 3].max())
            ratios.append((_mag(2) + _mag(3)) / h1)
            f0s.append((round(i / sr, 3), round(float(f0), 2)))
        if len(ratios) >= 6:
            out["sine_ratio"] = round(float(np.median(ratios)), 4)
            out["f0_med"] = round(float(np.median(
                [f for _, f in f0s])), 1)
            # wave 31 (item 113): the per-frame sub f0 track — the key
            # court maps these onto the chord field
            out["f0_frames"] = f0s
    return out


# ------------------------------------------------------- 050 SUB-MONO COURT
def court_sub_mono(wav_or_metrics, song=None, genre=""):
    g = str(genre or "").lower().replace("-", "_").replace(" ", "_")
    if any(k in g for k in _TEXTURE_EXEMPT):
        return {"court": "sub_mono", "ok": True,
                "skipped": "texture genre — wide lows are the aesthetic"}
    if _is_imported(song):
        return {"court": "sub_mono", "ok": True,
                "skipped": "imported record (witness law)"}
    m = wav_or_metrics if isinstance(wav_or_metrics, dict) \
        else measure(wav_or_metrics)
    if not m.get("ok") or "sub_corr" not in m:
        return {"court": "sub_mono", "ok": True,
                "skipped": "sub band too quiet to judge"}
    flags = []
    if m["sub_corr"] < SUB_CORR_FLOOR or \
            m["sub_side_ratio"] > SIDE_RATIO_CEIL:
        flags.append({"kind": "wide_sub", "sub_corr": m["sub_corr"],
                      "side_ratio": m["sub_side_ratio"],
                      "why": f"sub band (<{SUB_HZ:.0f}Hz) L/R correlation "
                             f"{m['sub_corr']} / side ratio "
                             f"{m['sub_side_ratio']} — stereo lows cancel "
                             "on mono systems (clubs, phones); the sub is "
                             "a MONO CENTER band"})
    return {"court": "sub_mono", "ok": not flags, "flags": flags,
            "metrics": {k: m[k] for k in ("sub_corr", "sub_side_ratio")
                        if k in m}}


def _wall_index(master):
    for i, f in enumerate(master):
        if str(f.get("id", f.get("type", "")) or "").startswith(
                ("fx_truepeak", "fx_brickwall")):
            return i
    return len(master)


def heal_sub_mono(song, verdict=None):
    """Mono the sub band on the MASTER: fx_ms_eq side_low -12dB shelf at
    120Hz, inserted BEFORE the wall (master topology law). If a master
    fx_ms_eq already exists, deepen its side_low instead. Mutates."""
    v = verdict or {}
    if v.get("ok", True):
        return []
    master = song.setdefault("master", [])
    for f in master:
        if str(f.get("id", "")) == "fx_ms_eq":
            p = f.setdefault("params", {})
            old = float(p.get("side_low", 0) or 0)
            p["side_low"] = -12.0
            p["low_freq"] = min(float(p.get("low_freq", 250) or 250), 120.0)
            return [{"kind": "mono_sub", "via": "existing fx_ms_eq",
                     "old_side_low": old, "new_side_low": -12.0}]
    master.insert(_wall_index(master),
                  {"id": "fx_ms_eq",
                   "params": {"side_low": -12.0, "low_freq": 120.0}})
    return [{"kind": "mono_sub", "via": "fx_ms_eq insert (pre-wall)",
             "side_low": -12.0, "low_freq": 120.0}]


# --------------------------------------------------- 077 TRANSLATION COURT
def _drive_sources(song):
    """808/sub lanes whose SOURCE carries a native drive zone."""
    out = []
    for t in song.get("tracks", []) or []:
        if not isinstance(t, dict) or t.get("muted"):
            continue
        nm = str(t.get("name", "")).lower()
        src = t.get("source") or {}
        sid = str(src.get("id", "")).lower()
        if any(w in nm or w in sid for w in ("808", "sub")) and \
                src.get("kind", "faust") in ("faust", None, "") and \
                ("808" in sid or "sub" in sid):
            out.append(t)
    return out


def court_translation(wav_or_metrics, song, genre=""):
    """ADVISORY-ONLY (corpus law: goldenbrown, a real imported record,
    measures 0.0032 — the metric cannot convict). The advisory carries
    the drive recipe; heal_translation serves explicit asks."""
    m = wav_or_metrics if isinstance(wav_or_metrics, dict) \
        else measure(wav_or_metrics)
    if not m.get("ok") or "sine_ratio" not in m:
        return {"court": "translation", "ok": True,
                "skipped": "no steady sub fundamental to judge"}
    if _is_imported(song):
        return {"court": "translation", "ok": True,
                "skipped": "imported record (witness law)"}
    lanes = _drive_sources(song or {})
    if not lanes:
        return {"court": "translation", "ok": True,
                "skipped": "no drive-capable 808/sub source (nothing to heal)"}
    advisories = []
    g = str(genre or "").lower()
    phone_first = any(k in g for k in ("trap", "drill", "phonk", "hiphop",
                                       "hip_hop", "rap", "grime", "pop"))
    if m["sine_ratio"] < SINE_RATIO_FLOOR and phone_first:
        advisories.append({
            "kind": "sine_808", "sine_ratio": m["sine_ratio"],
            "f0": m.get("f0_med"),
            "tracks": [t.get("name", "?") for t in lanes],
            "why": f"sub partials sit {m['sine_ratio']:.3f}x under the "
                   f"{m.get('f0_med', 0):.0f}Hz fundamental — phones "
                   "reproduce nothing below ~150Hz; if the 808 should cut "
                   "through small speakers, raise its `drive` (harmonics "
                   "from the voice itself)"})
    return {"court": "translation", "ok": True, "advisories": advisories,
            "metrics": {"sine_ratio": m["sine_ratio"]}}


def heal_translation(song, verdict=None):
    """Raise `drive` on the convicted 808/sub SOURCES (zone 0.5..5) — the
    voice grows its own harmonics; no bolted-on saturator. Mutates."""
    v = verdict or {}
    if v.get("ok", True):
        return []
    edits = []
    for t in _drive_sources(song):
        params = (t.get("source") or {}).setdefault("params", {})
        old = float(params.get("drive", 1.4) or 1.4)
        new = round(min(max(old * 1.6, 2.2), 5.0), 2)
        if new > old + 0.05:
            params["drive"] = new
            edits.append({"track": t.get("name", "?"), "kind": "drive_up",
                          "old": old, "new": new})
        elif not any(str(f.get("id")) == "fx_bass_grit"
                     for f in t.get("fx") or []):
            # W69 (item 188): the voice's own drive is maxed — the
            # MULTIBAND grit layer takes over (sub clean, mids driven)
            t.setdefault("fx", []).append(
                {"id": "fx_bass_grit", "params": {"drive": 9.0,
                                                  "grit": 0.5}})
            edits.append({"track": t.get("name", "?"),
                          "kind": "grit_layer",
                          "why": "source drive maxed — fx_bass_grit "
                                 "adds phone-visible harmonics, sub "
                                 "stays clean"})
    return edits


# ------------------------------------------------- 113 SUB KEY COURT (w31)
def court_sub_key(wav_or_path, song, genre=""):
    """Item 113, the RENDER-TRUTH half: the notes may be lawful while the
    SOUND betrays them (a sample 808 a semitone flat, a detuned freq
    zone). THE CORPUS REWROTE THE DETECTOR (demo_track: a band-global f0
    picked the KICK's 44Hz tail and convicted an honest sub — kicks are
    not chord-bound): the court now searches for the bass AT ITS NOTATED
    PITCH (+-3 st) inside its own note windows and measures the
    systematic offset in cents. Immune to kick tails (outside the search
    window), immune to chord-field rot (the NOTE is the contract; the
    f0-vs-chords half is transitively the symbolic key court through
    lawful notes). Convicts on |median offset| > 60 cents with MAD < 60
    (systematic detune, never performance vibrato). No auto-heal — audio
    re-pitch is the retune rail's hand tool."""
    if _is_imported(song):
        return {"court": "sub_key", "ok": True,
                "skipped": "imported record (witness law)"}
    if len((song or {}).get("tempoMap") or []) > 1:
        return {"court": "sub_key", "ok": True,
                "skipped": "tempoMap song (beat mapping assumes one tempo)"}
    if not isinstance(wav_or_path, str):
        return {"court": "sub_key", "ok": True,
                "skipped": "needs the wav (targeted per-note search)"}
    try:
        import lowend_court as _lc
        lanes = _lc.bass_lanes(song or {})
    except Exception:
        lanes = []
    notes = [n for t in lanes for n in (t.get("notes") or [])
             if int(n.get("pitch", 60)) <= 45]      # A2=110Hz and below
    if len(notes) < 8:
        return {"court": "sub_key", "ok": True,
                "skipped": "too few notated sub notes (<=A2) to verify"}
    x, sr = _read(wav_or_path)
    mid = x.mean(axis=1)
    bpm = float((song or {}).get("bpm", 120) or 120)
    spb = 60.0 / max(bpm, 1.0)
    nfft = 16384
    win = np.hanning(nfft)
    freqs = np.fft.rfftfreq(nfft, 1.0 / sr)
    note_offsets = []
    for nn in sorted(notes, key=lambda n: float(n.get("start", 0)))[:200]:
        exp_hz = 440.0 * 2 ** ((int(nn.get("pitch", 60)) - 69) / 12.0)
        s0 = float(nn.get("start", 0)) * spb + 0.03   # skip the attack
        s1 = (float(nn.get("start", 0))
              + float(nn.get("len", 0.25))) * spb
        deltas = []
        i = int(s0 * sr)
        while i + nfft <= min(int(s1 * sr), len(mid)):
            spec = np.abs(np.fft.rfft(mid[i:i + nfft] * win))
            lo_i = int(np.searchsorted(freqs, exp_hz * 2 ** (-0.25)))
            hi_i = int(np.searchsorted(freqs, exp_hz * 2 ** (0.25)))
            if hi_i - lo_i < 3:
                break
            p = lo_i + int(np.argmax(spec[lo_i:hi_i]))
            # the note must actually SOUND there (not masked silence)
            noise = float(np.median(spec[max(lo_i - 40, 1):hi_i + 40]))
            if float(spec[p]) < noise * 4.0:
                i += nfft // 2
                continue
            if 0 < p < len(spec) - 1:
                a, b, c = (float(spec[p - 1]), float(spec[p]),
                           float(spec[p + 1]))
                den = a - 2 * b + c
                d = 0.5 * (a - c) / den if abs(den) > 1e-12 else 0.0
                f0 = (p + max(min(d, 0.5), -0.5)) * float(freqs[1])
            else:
                f0 = float(freqs[p])
            deltas.append(1200.0 * math.log2(max(f0, 1.0) / exp_hz))
            i += nfft // 2
        if deltas:
            deltas.sort()
            note_offsets.append(deltas[len(deltas) // 2])
    if len(note_offsets) < 6:
        return {"court": "sub_key", "ok": True,
                "skipped": "too few sounding sub notes reached the ear"}
    note_offsets.sort()
    med = note_offsets[len(note_offsets) // 2]
    mad = sorted(abs(v - med) for v in note_offsets)[len(note_offsets) // 2]
    flags = []
    if abs(med) > 60.0 and mad < 60.0:
        flags.append({
            "kind": "sub_detuned", "median_cents": round(med, 1),
            "mad_cents": round(mad, 1), "notes_measured": len(note_offsets),
            "why": f"the sub RENDERS {med:+.0f} cents off its own notated "
                   f"pitches (systematic across {len(note_offsets)} notes, "
                   f"spread {mad:.0f}c) — the notes are the contract and "
                   "the SOUND betrays them; retune the 808 sample / check "
                   "the voice's freq calibration"})
    return {"court": "sub_key", "ok": not flags, "flags": flags,
            "median_cents": round(med, 1), "mad_cents": round(mad, 1),
            "notes_measured": len(note_offsets)}


# --------------------------------------------- 139 KICK TUNING COURT (w32)
def court_kick_tuning(wav_or_path, song, genre=""):
    """Item 139: TONAL kicks (long boom, clear fundamental) tune to the
    key's root or fifth (+-50 cents, r-18); SHORT percussive kicks are
    EXEMPT — and the exemption is PHYSICS here, not a name list: a kick
    whose decay-steady region yields no stable fundamental (4x-noise
    gate, >=60% of frames) simply cannot be judged. f0 is measured in
    the DECAY-STEADY region (the 808 glide falls ~1 st through the
    attack — it never votes). Verdict folds the measured pitch class to
    the nearest {root, fifth} target in cents."""
    if _is_imported(song):
        return {"court": "kick_tuning", "ok": True,
                "skipped": "imported record (witness law)"}
    if len((song or {}).get("tempoMap") or []) > 1:
        return {"court": "kick_tuning", "ok": True,
                "skipped": "tempoMap song"}
    if not isinstance(wav_or_path, str):
        return {"court": "kick_tuning", "ok": True, "skipped": "needs wav"}
    try:
        import theory
        key = theory.parse_key((song or {}).get("key")) or \
            theory.infer_key([n for t in (song or {}).get("tracks", []) or []
                              if isinstance(t, dict) and not t.get("muted")
                              for n in t.get("notes", []) or []], genre)
    except Exception:
        key = None
    if not key:
        return {"court": "kick_tuning", "ok": True, "skipped": "no key"}
    # THE SCALE-TONE LAW (corpus wolf 2026-07-15: root/fifth targets
    # convicted 18/90 incl. six EVAL WINNERS, clustered at +-200c [the
    # b7] and +290c [the relative-major root] — key-inference ambiguity
    # and legit degree choices, not detune. The diatonic SET is immune
    # to relative-key confusion, so the crime becomes the CHROMATIC
    # kick: parked >50c from ANY scale tone, systematically.)
    targets = tuple(key.get("scale_pcs") or ())
    if not targets:
        root = int(key.get("tonic_pc", 0))
        targets = (root, (root + 7) % 12)
    kick_notes = []
    for t in (song or {}).get("tracks", []) or []:
        if not isinstance(t, dict) or t.get("muted"):
            continue
        nm = str(t.get("name", "")).lower()
        if "kick" in nm and not nm.endswith(("_sketch", "_identity")):
            kick_notes += [(t, n) for n in t.get("notes") or []]
    if len(kick_notes) < 6:
        return {"court": "kick_tuning", "ok": True,
                "skipped": "too few kick notes"}
    x, sr = _read(wav_or_path)
    mid = x.mean(axis=1)
    bpm = float((song or {}).get("bpm", 120) or 120)
    spb = 60.0 / max(bpm, 1.0)
    nfft = 8192
    win = np.hanning(nfft)
    freqs = np.fft.rfftfreq(nfft, 1.0 / sr)
    lo_i, hi_i = int(np.searchsorted(freqs, 35)), \
        int(np.searchsorted(freqs, 150))
    per_note = []
    tonal_frames = total_frames = 0
    for _, nn in sorted(kick_notes,
                        key=lambda p: float(p[1].get("start", 0)))[:120]:
        on_s = float(nn.get("start", 0)) * spb
        s0 = on_s + 0.12                              # decay-steady only
        i = int(s0 * sr)
        if i + nfft > len(mid):
            continue
        total_frames += 1
        # THE SUSTAIN GATE (r-18: only decay > ~200ms kicks are tonal;
        # battery-caught: a 30ms punch's residue still peaked 4x above a
        # QUIET band's noise median — level-vs-noise cannot prove
        # sustain, only level-vs-ATTACK can): the decay window must hold
        # >= 15% of the attack window's energy.
        a0, a1 = int(on_s * sr), int((on_s + 0.1) * sr)
        d1 = min(int((s0 + 0.1) * sr), len(mid))
        atk = float(np.sqrt(np.mean(mid[a0:max(a1, a0 + 8)] ** 2)))
        dec = float(np.sqrt(np.mean(mid[i:max(d1, i + 8)] ** 2)))
        if atk < 1e-6 or dec / atk < 0.15:
            continue                        # percussive: exempt by physics
        spec = np.abs(np.fft.rfft(mid[i:i + nfft] * win))
        p = lo_i + int(np.argmax(spec[lo_i:hi_i]))
        noise = float(np.median(spec[lo_i:hi_i]))
        if float(spec[p]) < noise * 4.0:
            continue                        # no clear fundamental
        tonal_frames += 1
        if 0 < p < len(spec) - 1:
            a, b, c = (float(spec[p - 1]), float(spec[p]),
                       float(spec[p + 1]))
            den = a - 2 * b + c
            d = 0.5 * (a - c) / den if abs(den) > 1e-12 else 0.0
            f0 = (p + max(min(d, 0.5), -0.5)) * float(freqs[1])
        else:
            f0 = float(freqs[p])
        midi_f = 12.0 * math.log2(f0 / 440.0) + 69.0
        # fold to the NEAREST target pitch class, signed semitones
        deltas = []
        for tpc in targets:
            dd = (midi_f - tpc) % 12.0
            if dd > 6.0:
                dd -= 12.0
            deltas.append(dd)
        per_note.append(min(deltas, key=abs) * 100.0)
    if total_frames >= 6 and tonal_frames / total_frames < 0.6:
        return {"court": "kick_tuning", "ok": True,
                "skipped": "percussive kick (no stable fundamental — "
                           "the adversarial exemption is physics)"}
    if len(per_note) < 6:
        return {"court": "kick_tuning", "ok": True,
                "skipped": "too few tonal kick frames"}
    per_note.sort()
    med = per_note[len(per_note) // 2]
    mad = sorted(abs(v - med) for v in per_note)[len(per_note) // 2]
    flags = []
    if abs(med) > 50.0 and mad < 50.0:
        flags.append({
            "kind": "kick_off_key", "median_cents": round(med, 1),
            "mad_cents": round(mad, 1), "notes": len(per_note),
            "targets": list(targets),
            "why": f"the TONAL kick's fundamental sits {med:+.0f} cents "
                   "from the nearest SCALE TONE (systematic, "
                   f"spread {mad:.0f}c over {len(per_note)} hits) — "
                   "long-boom kicks carry harmony (r-18: 10c is audible,"
                   " +-50c is the floor)"})
    return {"court": "kick_tuning", "ok": not flags, "flags": flags,
            "median_cents": round(med, 1), "mad_cents": round(mad, 1),
            "tonal_frac": round(tonal_frames / max(total_frames, 1), 2)}


def heal_kick_tuning(song, verdict):
    """Shift the kick lane's NOTATED pitches by the whole-semitone delta
    that lands the measured fundamental on its target (the voice tracks
    note pitch; the next render carries it). Once per lane
    (kick_tune_shift marker — never ping-pongs across re-renders).
    Mutates; returns ledger."""
    if verdict.get("ok", True):
        return []
    med = float(verdict.get("median_cents",
                            (verdict.get("flags") or [{}])[0]
                            .get("median_cents", 0)))
    shift = -int(round(med / 100.0))
    if shift == 0:
        return []
    edits = []
    for t in (song or {}).get("tracks", []) or []:
        if not isinstance(t, dict) or t.get("muted"):
            continue
        nm = str(t.get("name", "")).lower()
        if "kick" not in nm or nm.endswith(("_sketch", "_identity")):
            continue
        if t.get("kick_tune_shift") is not None:
            continue
        for n in t.get("notes") or []:
            n["pitch"] = int(n.get("pitch", 36)) + shift
        t["kick_tune_shift"] = shift
        edits.append({"track": t.get("name"), "kind": "kick_retune",
                      "semitones": shift})
    return edits


# ------------------------------------------------------ 051 CO-PEAK COURT
def court_missing_fundamental(wav_or_path, song, genre=""):
    """W53 (r-17 item 078): a sub whose fundamental sits <60Hz with NO
    harmonics above 80Hz is INVISIBLE on small speakers — the missing-
    fundamental illusion needs harmonics to reconstruct the pitch.
    Note-windowed FFT on the mix (the court_sub_key machinery): energy
    at f0 vs the summed 2f0..5f0 harmonic bins across the lane's sub
    notes. Harmonics >30dB under the fundamental = advisory; heal =
    fx_saturate on THAT lane (symbolic, hand work sacred)."""
    if _is_imported(song):
        return {"court": "missing_fundamental", "ok": True,
                "skipped": "imported record (witness law)"}
    if len((song or {}).get("tempoMap") or []) > 1:
        return {"court": "missing_fundamental", "ok": True,
                "skipped": "tempoMap song"}
    if not isinstance(wav_or_path, str):
        return {"court": "missing_fundamental", "ok": True,
                "skipped": "needs the wav"}
    try:
        import lowend_court as _lc
        lanes = _lc.bass_lanes(song or {})
    except Exception:
        lanes = []
    x = None
    advisories = []
    for t in lanes:
        notes = [n for n in (t.get("notes") or [])
                 if int(n.get("pitch", 60)) <= 43        # G2 ~ 98Hz
                 and 440.0 * 2 ** ((int(n.get("pitch", 60)) - 69) / 12.0)
                 < 60.0]
        if len(notes) < 6:
            continue
        if x is None:
            x, sr = _read(wav_or_path)
            mid = x.mean(axis=1)
            nfft = 16384
            win = np.hanning(nfft)
            freqs = np.fft.rfftfreq(nfft, 1.0 / sr)
        bpm = float((song or {}).get("bpm", 120) or 120)
        spb = 60.0 / max(bpm, 1.0)
        ratios = []
        for nn in sorted(notes, key=lambda n: float(n.get("start", 0)))[:60]:
            f0 = 440.0 * 2 ** ((int(nn.get("pitch", 60)) - 69) / 12.0)
            s0 = float(nn.get("start", 0)) * spb + 0.03
            i = int(s0 * sr)
            if i + nfft > len(mid):
                continue
            spec = np.abs(np.fft.rfft(mid[i:i + nfft] * win)) ** 2

            def band_e(hz):
                lo = int(np.searchsorted(freqs, hz * 2 ** (-1 / 6)))
                hi = int(np.searchsorted(freqs, hz * 2 ** (1 / 6)))
                return float(spec[lo:max(hi, lo + 1)].sum())
            fund = band_e(f0)
            if fund <= 0:
                continue
            harm = sum(band_e(f0 * k) for k in (2, 3, 4, 5))
            ratios.append(10.0 * math.log10(max(harm, 1e-18) /
                                            max(fund, 1e-18)))
        if len(ratios) < 4:
            continue
        ratios.sort()
        med = ratios[len(ratios) // 2]
        if med < -30.0:
            advisories.append({
                "kind": "missing_fundamental", "track": t.get("name"),
                "harm_db": round(med, 1), "notes": len(ratios),
                "why": (f"'{t.get('name')}' sounds <60Hz with harmonics "
                        f"{med:.0f}dB under the fundamental — pure sub "
                        "is INVISIBLE on phones/laptops (the missing-"
                        "fundamental illusion needs harmonics); saturate "
                        "the lane so small speakers reconstruct the "
                        "pitch")})
    return {"court": "missing_fundamental", "ok": True,
            "advisories": advisories}


def heal_missing_fundamental(song, verdict):
    """fx_saturate on the flagged lane — ONLY when no saturation rides
    it already (hand work sacred). Symbolic; the shared re-render+wall
    downstream proves it."""
    acts = []
    by_name = {t.get("name"): t for t in (song or {}).get("tracks", [])
               if isinstance(t, dict)}
    for adv in (verdict or {}).get("advisories", []):
        t = by_name.get(adv.get("track"))
        if t is None:
            continue
        fx = t.setdefault("fx", [])
        if any(str(f.get("id", "")) in ("fx_bass_grit",) or
               "saturate" in str(f.get("id", "")) or
               "dist" in str(f.get("id", "")) for f in fx):
            continue
        # W69 (r-5 item 188): the MULTIBAND move — sub stays CLEAN and
        # mono-summable, only the upper band grows grit harmonics
        fx.append({"id": "fx_bass_grit", "params": {"drive": 9.0,
                                                    "grit": 0.5}})
        acts.append({"kind": "missing_fundamental_heal",
                     "track": t.get("name"),
                     "why": (f"'{t.get('name')}': fx_bass_grit landed — "
                             "sub <120Hz passes CLEAN, the upper band "
                             "grows the 850-1200Hz grit that phones can "
                             "reconstruct the fundamental from")})
    return acts


def court_copeak(wav_or_arr, song, sr=None):
    """Kick transient and bass sustain sharing one 1/3-octave bin in
    40..160Hz = spectral masking. ADVISORY (taste varies; layering with
    intent is real). Needs the song for kick onset times."""
    if isinstance(wav_or_arr, str):
        x, sr = _read(wav_or_arr)
    else:
        x = np.asarray(wav_or_arr, dtype="float64")
        if x.ndim == 1:
            x = np.stack([x, x], axis=1)
    import lowend_court as LC
    kicks = LC.kick_onsets(song or {})
    bpm = float((song or {}).get("bpm", 120) or 120)
    if len(kicks) < 4:
        return {"court": "copeak", "ok": True, "skipped": "needs kick lane"}
    mid = x.mean(axis=1)
    spb = 60.0 / bpm            # seconds per beat
    nfft = 8192
    freqs = np.fft.rfftfreq(nfft, 1.0 / sr)
    win = np.hanning(nfft)

    def peak_hz(t0, t1):
        i0, i1 = int(t0 * sr), int(t1 * sr)
        seg = mid[i0:i1]
        if len(seg) < nfft:
            seg = np.pad(seg, (0, nfft - len(seg)))
        spec = np.abs(np.fft.rfft(seg[:nfft] * win))
        lo_i, hi_i = np.searchsorted(freqs, 40), np.searchsorted(freqs, 160)
        if hi_i <= lo_i:
            return None, 0.0
        p = lo_i + int(np.argmax(spec[lo_i:hi_i]))
        return float(freqs[p]), float(spec[p])

    kick_hz, bass_hz = [], []
    for k in kicks[:24]:
        t = k * spb
        if (t + 0.09) * sr >= len(mid):
            break
        hz, mag = peak_hz(t, t + 0.09)          # the transient window
        if hz and mag > 0:
            kick_hz.append(hz)
        mid_t = t + spb * 0.5                    # between this kick and next
        if (mid_t + 0.12) * sr < len(mid):
            hz2, mag2 = peak_hz(mid_t, mid_t + 0.12)
            if hz2 and mag2 > 0:
                bass_hz.append(hz2)
    if len(kick_hz) < 4 or len(bass_hz) < 4:
        return {"court": "copeak", "ok": True, "skipped": "too few windows"}
    km, bm = float(np.median(kick_hz)), float(np.median(bass_hz))
    third_oct = abs(np.log2(km / bm)) < (1.0 / 6.0)   # same 1/3-oct band
    advisories = []
    if third_oct:
        advisories.append({
            "kind": "kick_bass_copeak", "kick_hz": round(km, 1),
            "bass_hz": round(bm, 1),
            "why": f"kick fundamental ~{km:.0f}Hz and bass ~{bm:.0f}Hz share "
                   "one 1/3-octave band — they mask each other; tune the "
                   "kick off the bass root or carve with a sidechained "
                   "notch"})
    return {"court": "copeak", "ok": True, "advisories": advisories,
            "metrics": {"kick_hz": round(km, 1), "bass_hz": round(bm, 1)}}


# ---------------------------------------------------------------- aggregate
def court_ears(wav, song=None, genre="", heal=False):
    m = measure(wav)
    out = {"sub_mono": court_sub_mono(m, song, genre),
           "translation": court_translation(m, song or {}, genre),
           "sub_key": court_sub_key(wav, song or {}, genre),
           "missing_fundamental": court_missing_fundamental(
               wav, song or {}, genre),
           "copeak": court_copeak(wav, song or {})}
    if heal and song is not None:
        heals = {}
        if out["missing_fundamental"].get("advisories"):
            heals["missing_fundamental"] = heal_missing_fundamental(
                song, out["missing_fundamental"])
        if not out["sub_mono"].get("ok", True):
            heals["sub_mono"] = heal_sub_mono(song, out["sub_mono"])
        out["heals"] = {k: v for k, v in heals.items() if v}
    out["ok"] = all(v.get("ok", True) for v in out.values()
                    if isinstance(v, dict))
    return out


def main():
    import argparse
    ap = argparse.ArgumentParser(description="THE LOW-END EARS (wave 16)")
    ap.add_argument("wav")
    ap.add_argument("--song", default=None)
    ap.add_argument("--genre", default="")
    ap.add_argument("--measure", action="store_true")
    args = ap.parse_args()
    if args.measure:
        print(json.dumps(measure(args.wav), indent=1))
        return 0
    song = json.load(open(args.song)) if args.song else None
    v = court_ears(args.wav, song, args.genre)
    print(json.dumps(v, indent=1))
    return 0 if v["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
