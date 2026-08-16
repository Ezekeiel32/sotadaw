#!/usr/bin/env python3
"""THE TRANSLATION COURTS — does the master travel? (wave 22; R-7 items
119/190/191/232).

Master-wav spectral law. THE CORPUS OUTRANKS THE LITERATURE here
(self-measure 2026-07-15, 29 winners+demos): the researched 'commercial
masters sit at -4.5+-1 dB/oct' would convict nearly the whole corpus —
real winner tilts span -13.5 (vaporwave) to -3.1 (deep house demo), and
the iZotope band %s (power domain) run low-band 55-98%, nothing like
the published averages. So: UNIVERSAL edges sit beyond the corpus span
(convictions), GENRE-FAMILY windows ride as advisories (KG-seeded from
the corpus table itself).

  ltas(wav)               Welch PSD (Hann 4096/2048) -> 1/6-oct-smoothed
                          curve + log-log slope fit 100Hz-4kHz (dB/oct)
  bands5(wav)             the de-facto split + the 20-50 sub cell:
                          20-50 / 20-250 / 250-2k / 2k-8k / 8k-20k (%)
  brightness(wav)         item 232: 85% ROLL-OFF + high-band % — naive
                          centroid RETIRED for master brightness (sub
                          mass drags centroid the WRONG way: electronic
                          reads darker than rock by centroid while being
                          brighter by roll-off)
  court_tilt (190)        conviction only beyond [-14.5, -2.0] dB/oct
                          (outside every winner + margin); genre-family
                          window advisory. HEAL: bounded fx_ms_eq shelf
                          tilt (+-2dB) pre-wall.
  court_bands (119)       conviction only at corpus-impossible extremes
                          (highmid>20%, high>5%, low>99%); family
                          windows advisory (band-dependent tolerance:
                          bass wild, mids tight — the r-7 law).
  court_width_master(191) full-band L/R correlation >= +0.5 law,
                          SUSTAINED NEGATIVE = conviction (phase-flip
                          class) + phase court mean|dphi| < 1.7 rad.
                          Sub-band mono law lives in lowend_ears
                          (ONE-RESOLVER: never duplicated here).
  court_translation(wav, song, genre, heal=False)  aggregate
"""
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

TILT_HARD = (-14.5, -2.0)      # beyond every corpus winner + margin
HM_MAX_PCT, HI_MAX_PCT, LOW_MAX_PCT = 20.0, 5.0, 99.0
# CORR_NEG corpus-calibrated: eval_vaporwave (a WINNER) measures -0.05 —
# decorrelated-around-zero is a wide aesthetic, not the phase-flip class
# (-0.5..-1). The research's own ladder: <+0.2 advises, SUSTAINED
# negative convicts.
CORR_FLOOR, CORR_NEG = 0.5, -0.2
PHASE_RAD_MAX = 1.7            # r-7: at-scale phase-issue threshold

# genre-family windows MEASURED FROM THIS CORPUS (advisory tier).
# (tilt_lo, tilt_hi, low_lo, low_hi, highmid_max)
FAMILY_WINDOWS = {
    "deep_bass": (-13.0, -4.5, 78.0, 99.0, 8.0),    # drill/grime/phonk/
    "electronic": (-13.0, -3.0, 60.0, 97.0, 10.0),  # house/techno/edm
    "live": (-11.0, -3.0, 38.0, 80.0, 16.0),        # rock/jazz/blues/soul
    "texture": (-14.0, -5.0, 10.0, 95.0, 6.0),      # ambient family
}
_FAMILY = (
    ("deep_bass", ("drill", "grime", "phonk", "trap", "dubstep", "riddim",
                   "memphis", "808")),
    ("texture", ("ambient", "drone", "meditation", "soundscape",
                 "vaporwave", "chillout", "downtempo", "lofi")),
    ("live", ("rock", "metal", "punk", "jazz", "blues", "soul", "funk",
              "gospel", "country", "folk", "bluegrass", "americana",
              "orchestral", "cinematic", "classical", "soundtrack",
              "swing", "indie", "reggae")),
    ("electronic", ("house", "techno", "trance", "edm", "garage", "dnb",
                    "amapiano", "disco", "synthwave", "electro", "dance",
                    "hiphop", "hip_hop", "boombap", "pop", "soca")),
)


def family_for(genre):
    g = str(genre or "").lower().replace("-", "_").replace(" ", "_")
    for fam, keys in _FAMILY:
        if any(k in g for k in keys):
            return fam
    return "electronic"


def _read(wav):
    import soundfile as sf
    x, sr = sf.read(wav, always_2d=True, dtype="float64")
    if x.shape[1] == 1:
        x = np.repeat(x, 2, axis=1)
    return x[:, :2], sr


def _welch(mid, sr):
    from scipy.signal import welch
    return welch(mid, sr, window="hann", nperseg=4096, noverlap=2048)


def ltas(wav_or_arr, sr=None):
    """(freqs, psd_db_smoothed, slope_db_per_oct)"""
    if isinstance(wav_or_arr, str):
        x, sr = _read(wav_or_arr)
        mid = x.mean(axis=1)
    else:
        mid = np.asarray(wav_or_arr, dtype="float64")
        if mid.ndim > 1:
            mid = mid.mean(axis=1)
    f, pxx = _welch(mid, sr)
    db = 10 * np.log10(pxx + 1e-18)
    # 1/6-octave gaussian smoothing on the log-f axis
    logf = np.log2(f + 1e-9)
    sm = np.copy(db)
    for i in range(1, len(f)):
        w = np.exp(-0.5 * ((logf - logf[i]) / (1.0 / 12.0)) ** 2)
        w /= w.sum()
        sm[i] = float((db * w).sum())
    sel = (f >= 100) & (f <= 4000)
    slope = float(np.polyfit(np.log2(f[sel]), db[sel], 1)[0])
    return f, sm, round(slope, 2)


def bands5(wav_or_arr, sr=None):
    if isinstance(wav_or_arr, str):
        x, sr = _read(wav_or_arr)
        mid = x.mean(axis=1)
    else:
        mid = np.asarray(wav_or_arr, dtype="float64")
        if mid.ndim > 1:
            mid = mid.mean(axis=1)
    f, pxx = _welch(mid, sr)
    # normalize over the AUDIBLE total (20Hz+): DC offset / sub-20 rumble
    # must not dilute the band shares
    tot = float(pxx[f >= 20.0].sum()) or 1e-18

    def pct(lo, hi):
        return round(float(pxx[(f >= lo) & (f < hi)].sum()) / tot * 100, 1)
    return {"sub2050": pct(20, 50), "low": pct(20, 250),
            "lowmid": pct(250, 2000), "highmid": pct(2000, 8000),
            "high": pct(8000, 22050)}


def brightness(wav_or_arr, sr=None):
    """Item 232: 85% roll-off Hz + high-band % — the master brightness
    metric. Centroid is RETIRED at master scope (sub mass inverts it)."""
    if isinstance(wav_or_arr, str):
        x, sr = _read(wav_or_arr)
        mid = x.mean(axis=1)
    else:
        mid = np.asarray(wav_or_arr, dtype="float64")
        if mid.ndim > 1:
            mid = mid.mean(axis=1)
    f, pxx = _welch(mid, sr)
    csum = np.cumsum(pxx)
    roll = float(f[int(np.searchsorted(csum, 0.85 * csum[-1]))])
    hi = float(pxx[f >= 8000].sum() / (csum[-1] or 1e-18) * 100)
    return {"rolloff_85_hz": round(roll, 1), "high_pct": round(hi, 2)}


# ------------------------------------------------------------- the courts
def court_tilt(wav, genre="", measured=None):
    slope = measured if measured is not None else ltas(wav)[2]
    flags, advisories = [], []
    if not (TILT_HARD[0] <= slope <= TILT_HARD[1]):
        flags.append({"kind": "tilt_extreme", "slope": slope,
                      "band": list(TILT_HARD),
                      "why": f"LTAS slope {slope:.1f} dB/oct sits outside "
                             f"[{TILT_HARD[0]}, {TILT_HARD[1]}] — beyond "
                             "every corpus winner (harsh/thin above, "
                             "mudball below)"})
    else:
        fam = family_for(genre)
        lo, hi = FAMILY_WINDOWS[fam][0], FAMILY_WINDOWS[fam][1]
        if not (lo <= slope <= hi):
            advisories.append({
                "kind": "tilt_offfamily", "slope": slope,
                "family": fam, "window": [lo, hi],
                "why": f"tilt {slope:.1f} dB/oct vs the {fam} family "
                       f"window [{lo}, {hi}] (corpus-measured)"})
    return {"court": "tilt", "ok": not flags, "flags": flags,
            "advisories": advisories, "slope": slope}


def heal_tilt(song, verdict):
    """Bounded master tilt via fx_ms_eq mid shelves (+-2dB), inserted
    BEFORE the wall. Only at hard-edge convictions. Mutates."""
    if verdict.get("ok", True):
        return []
    slope = float(verdict.get("slope", -7))
    too_dark = slope < TILT_HARD[0]
    master = song.setdefault("master", [])
    idx = len(master)
    for i, fx in enumerate(master):
        if str(fx.get("id", fx.get("type", "")) or "").startswith(
                ("fx_truepeak", "fx_brickwall")):
            idx = i
            break
    lift = 2.0 if too_dark else -2.0
    master.insert(idx, {"id": "fx_ms_eq",
                        "params": {"mid_high": lift, "mid_low": -lift / 2,
                                   "high_freq": 6000, "low_freq": 250}})
    return [{"kind": "tilt_shelf", "mid_high": lift,
             "mid_low": -lift / 2}]


def court_bands(wav, genre="", measured=None):
    b = measured if measured is not None else bands5(wav)
    flags, advisories = [], []
    if b["highmid"] > HM_MAX_PCT:
        flags.append({"kind": "highmid_flood", "got": b["highmid"],
                      "why": f"2-8kHz carries {b['highmid']:.0f}% of power "
                             f"(corpus max ~14.5) — the harshness zone is "
                             "flooded"})
    if b["high"] > HI_MAX_PCT:
        flags.append({"kind": "hf_flood", "got": b["high"],
                      "why": f"8kHz+ carries {b['high']:.0f}% of power — "
                             "no winner exceeds ~2%"})
    if b["low"] > LOW_MAX_PCT:
        flags.append({"kind": "all_sub", "got": b["low"],
                      "why": "everything below 250Hz — a mudball"})
    fam = family_for(genre)
    lo_lo, lo_hi, hm_max = FAMILY_WINDOWS[fam][2:5]
    if not flags:
        if not (lo_lo <= b["low"] <= lo_hi):
            advisories.append({
                "kind": "low_offfamily", "got": b["low"], "family": fam,
                "window": [lo_lo, lo_hi],
                "why": f"low band {b['low']:.0f}% vs the {fam} window "
                       f"[{lo_lo:.0f}-{lo_hi:.0f}]% (bass tolerance is "
                       "wide by law; mids are the tight cells)"})
        elif b["highmid"] > hm_max:
            advisories.append({
                "kind": "highmid_hot", "got": b["highmid"], "family": fam,
                "why": f"2-8kHz at {b['highmid']:.0f}% vs {fam} max "
                       f"{hm_max:.0f}%"})
    return {"court": "bands", "ok": not flags, "flags": flags,
            "advisories": advisories, "bands": b}


def court_width_master(wav):
    """Item 191's MASTER half: full-band correlation + phase court.
    The sub-band mono law lives in lowend_ears (one resolver)."""
    x, sr = _read(wav)
    l, r = x[:, 0], x[:, 1]
    if l.std() < 1e-9 or r.std() < 1e-9:
        return {"court": "width_master", "ok": True, "skipped": "mono/silent"}
    corr = float(np.corrcoef(l, r)[0, 1])
    n = len(l) // 4096 * 4096
    L = np.fft.rfft(l[:n].reshape(-1, 4096) * np.hanning(4096), axis=1)
    R = np.fft.rfft(r[:n].reshape(-1, 4096) * np.hanning(4096), axis=1)
    mag = np.abs(L) * np.abs(R)
    dphi = np.abs(np.angle(L * np.conj(R)))
    sel = mag > np.percentile(mag, 90)
    phase = float((dphi[sel] * mag[sel]).sum() / (mag[sel].sum() or 1e-18))
    flags, advisories = [], []
    if corr < CORR_NEG:
        flags.append({"kind": "phase_flip", "corr": round(corr, 3),
                      "why": f"master L/R correlation {corr:.2f} — "
                             "SUSTAINED NEGATIVE means the sides cancel "
                             "the mix in mono (phase-flip class)"})
    elif corr < CORR_FLOOR:
        advisories.append({"kind": "corr_low", "corr": round(corr, 3),
                           "why": f"master correlation {corr:.2f} < "
                                  f"{CORR_FLOOR} — mono compatibility "
                                  "at risk"})
    if phase > PHASE_RAD_MAX:
        advisories.append({"kind": "phase_wide", "phase": round(phase, 2),
                           "why": f"mean |L/R phase| {phase:.2f} rad > "
                                  f"{PHASE_RAD_MAX} (the at-scale "
                                  "phase-issue threshold)"})
    return {"court": "width_master", "ok": not flags, "flags": flags,
            "advisories": advisories, "corr": round(corr, 3),
            "phase": round(phase, 2)}


def heal_width_master(song, verdict):
    """Phase-flip conviction: strip master wideners (the usual cause);
    else nothing automatic — re-recording phase is not a knob. Mutates."""
    if verdict.get("ok", True):
        return []
    edits = []
    master = song.get("master") or []
    kept = []
    for fx in master:
        fid = str(fx.get("id", fx.get("type", "")) or "").lower()
        if "widen" in fid:
            edits.append({"kind": "strip_master_widen"})
            continue
        kept.append(fx)
    if edits:
        song["master"] = kept
    return edits


def court_translation(wav, song=None, genre="", heal=False):
    """The aggregate. NEVER per-proposal by itself — rides the audio
    pass at loudness_recovery's entry (one wav read, verdicts +
    bounded heals + one re-render shared with the low-end ears)."""
    x, sr = _read(wav)
    mid = x.mean(axis=1)
    _, _, slope = ltas(mid, sr)
    b = bands5(mid, sr)
    br = brightness(mid, sr)
    out = {"tilt": court_tilt(wav, genre, measured=slope),
           "bands": court_bands(wav, genre, measured=b),
           "width_master": court_width_master(wav),
           "brightness": br}
    if heal and song is not None:
        heals = {}
        if not out["tilt"].get("ok", True):
            heals["tilt"] = heal_tilt(song, out["tilt"])
        if not out["width_master"].get("ok", True):
            heals["width"] = heal_width_master(song, out["width_master"])
        out["heals"] = {k: v for k, v in heals.items() if v}
    out["ok"] = all(v.get("ok", True) for v in out.values()
                    if isinstance(v, dict))
    return out


def main():
    import argparse
    ap = argparse.ArgumentParser(description="THE TRANSLATION COURTS "
                                             "(wave 22)")
    ap.add_argument("wav")
    ap.add_argument("--song", default=None)
    ap.add_argument("--genre", default="")
    ap.add_argument("--heal", action="store_true")
    args = ap.parse_args()
    song = json.load(open(args.song)) if args.song else None
    v = court_translation(args.wav, song, args.genre, heal=args.heal)
    if args.heal and song is not None and v.get("heals"):
        json.dump(song, open(args.song, "w"), indent=1)
        v["saved"] = args.song
    print(json.dumps(v, indent=1))
    return 0 if v["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
