#!/usr/bin/env python3
"""THE SOUND COURT — per-stem timbre law (wave 20; R-16 items 018/019,
R-7 item 055).

Five deterministic features per SOLO stem (numpy/soundfile, zero tokens,
zero models), verdicted against per-role BANDS — never point targets
(r-16 adversarial law: a stem 200Hz off a 3kHz center is inaudible;
centroid covaries with F0/dynamics, so every cell is a fail band + a
warn band, and centroid is A-WEIGHTED to sit nearer perception).

  measure_stem(wav)     -> {centroid_hz, attack_ms, flatness, width_pct,
                            low_pct, rms_db, duration_s}
  ROLE_TABLE            item 018: per-role bands (centroid/attack/width/
                            tonal class), sources cited
  court_stem(feats, role, genre)     fail-band conviction + warn advisory
  court_attack_class(...)            r-16: attack classes sit orders of
                            magnitude apart (pad 100ms-3s, lead 10-60ms,
                            pluck/perc <10ms) — near-zero-FP role-vs-
                            label court
  heal_attack(song, track, verdict)  symbolic: the DAW authored the
                            voice, so move its OWN attack zone into the
                            class band (only when the param already
                            exists — proof the zone is real); else the
                            verdict carries the fix as an advisory
  court_role_levels(stems, genre)    item 055: vocal-to-mix offset
                            (-3..-6 LU, avg -4.5; rock -6..-8; hip-hop
                            drums~vocal), ordering advisories, kick/bass
                            anchor. Levels ride RMS-dB deltas (honest
                            proxy: offsets/ordering are RELATIVE).
  court_stems(stems_dir, song, genre)  the aggregate (on-demand lane:
                            stems renders are expensive — this court
                            serves CLIs/eval/import QC, not per-proposal)

Bands are seeded from r-16's cited table and CORPUS-CALIBRATED where the
corpus disagrees (self-measure law, item 135 — see BAND notes).
"""
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

SUB_HZ = 120.0


def _read_mono_stereo(wav):
    import soundfile as sf
    x, sr = sf.read(wav, always_2d=True, dtype="float64")
    if x.shape[1] == 1:
        x = np.repeat(x, 2, axis=1)
    return x[:, :2], sr


def _a_weight_db(f):
    """IEC 61672 A-weighting in dB (standard closed form)."""
    f = np.asarray(f, dtype="float64") + 1e-9
    f2 = f * f
    ra = (12194.0 ** 2 * f2 * f2) / (
        (f2 + 20.6 ** 2)
        * np.sqrt((f2 + 107.7 ** 2) * (f2 + 737.9 ** 2))
        * (f2 + 12194.0 ** 2))
    return 20 * np.log10(ra) + 2.0


def measure_stem(wav_or_arr, sr=None):
    """The 5-feature kernel (item 019). Deterministic; returns {} when
    the stem is effectively silent."""
    if isinstance(wav_or_arr, str):
        x, sr = _read_mono_stereo(wav_or_arr)
    else:
        x = np.asarray(wav_or_arr, dtype="float64")
        if x.ndim == 1:
            x = np.stack([x, x], axis=1)
    mid = x.mean(axis=1)
    n = len(mid)
    rms = float(np.sqrt(np.mean(mid ** 2)))
    if n < sr // 4 or rms < 1e-5:
        return {}
    # --- (1) A-weighted spectral centroid
    nfft = 8192
    win = np.hanning(nfft)
    cents, flats = [], []
    step = max(nfft // 2, (n - nfft) // 64 or nfft // 2)
    for i in range(0, max(n - nfft, 1), step):
        fr = mid[i:i + nfft]
        if len(fr) < nfft:
            break
        if float(np.sqrt(np.mean(fr ** 2))) < rms * 0.1:
            continue
        spec = np.abs(np.fft.rfft(fr * win))
        freqs = np.fft.rfftfreq(nfft, 1.0 / sr)
        pw = spec ** 2
        aw = pw * (10 ** (_a_weight_db(freqs) / 10.0))
        tot = float(aw.sum()) or 1e-12
        cents.append(float((aw * freqs).sum()) / tot)
        p = pw[1:] + 1e-18
        flats.append(float(np.exp(np.mean(np.log(p))) / np.mean(p)))
    if not cents:
        return {}
    # --- (2) attack time: median rise 10%->peak across detected onsets
    env_w = max(int(sr * 0.005), 8)
    env = np.abs(mid)
    kernel = np.ones(env_w) / env_w
    env = np.convolve(env, kernel, mode="same")
    emax = float(env.max()) or 1e-12
    attacks = []
    i, arm = 0, True
    while i < n - 1:
        if arm and env[i] > 0.25 * emax:
            j = i
            while j > 0 and env[j] > 0.1 * emax:
                j -= 1
            k_end = min(i + int(0.4 * sr), n - 1)
            k = j + int(np.argmax(env[j:k_end]))
            attacks.append((k - j) / sr * 1000.0)
            arm = False
            i = k_end
        elif not arm and env[i] < 0.08 * emax:
            arm = True
            i += 1
        else:
            i += 1
        if len(attacks) >= 24:
            break
    # --- (4) width above 200Hz + (5) low share
    spec_l = np.abs(np.fft.rfft(x[:, 0], n=nfft * 2))
    spec_r = np.abs(np.fft.rfft(x[:, 1], n=nfft * 2))
    freqs2 = np.fft.rfftfreq(nfft * 2, 1.0 / sr)
    hp = freqs2 >= 200.0
    m_e = float(((spec_l[hp] + spec_r[hp]) ** 2).sum()) / 4.0 or 1e-12
    s_e = float(((spec_l[hp] - spec_r[hp]) ** 2).sum()) / 4.0
    spec_m = np.abs(np.fft.rfft(mid, n=nfft * 2)) ** 2
    tot_e = float(spec_m.sum()) or 1e-12
    low_e = float(spec_m[freqs2 < SUB_HZ].sum())
    return {"centroid_hz": round(float(np.median(cents)), 1),
            "attack_ms": round(float(np.median(attacks)), 2)
            if attacks else None,
            "flatness": round(float(np.median(flats)), 4),
            "width_pct": round(100.0 * s_e / m_e, 1),
            "low_pct": round(100.0 * low_e / tot_e, 1),
            "rms_db": round(20 * math.log10(rms + 1e-12), 2),
            "duration_s": round(n / sr, 2)}


# ---------------------------------------------------------- item 018 table
# BANDS, NOT POINTS (the r-16 adversarial law: a stem 200Hz off a 3kHz
# center is inaudible; centroid covaries with F0/dynamics). fail =
# conviction edges; warn = advisory. Sources: r-16 f5/f6 role table +
# De Man; attack classes r-16 'orders of magnitude' finding.
ROLE_TABLE = {
    "sub":    {"centroid_fail": (20, 900), "attack_fail": (0.5, 200),
               "width_max": 12.0, "flat_max": 0.35, "tonal": True},
    # kick attack CORPUS-CALIBRATED (self-measure law 2026-07-15): the
    # project's own kick_808 measures 76ms amplitude attack (the boom
    # peaks when the glide lands) — r-16's '<5ms' is the acoustic CLICK
    # class; the band holds both, still convicts a 300ms swell.
    "kick":   {"centroid_fail": (80, 2500), "attack_fail": (0.5, 120),
               "width_max": 20.0, "flat_max": 0.6},
    "snare":  {"centroid_fail": (800, 6500), "attack_fail": (0.5, 30),
               "width_max": 60.0},
    "hat":    {"centroid_fail": (3000, 16000), "attack_fail": (0.5, 20)},
    "pad":    {"attack_fail": (50, 5000)},
    "lead":   {"attack_fail": (1, 150)},
    "pluck":  {"attack_fail": (0.5, 100)},
    "vocal":  {"centroid_fail": (300, 6000)},
}
_ROLE_WORDS = (
    ("sub", ("sub", "808")), ("kick", ("kick", "bd")),
    ("snare", ("snare", "clap", "sd", "rim")),
    ("hat", ("hat", "hh", "cymbal", "ride", "shaker")),
    ("pad", ("pad", "string", "swell", "atmo", "drone")),
    ("pluck", ("pluck", "stab", "arp")),
    # vocal BEFORE lead: 'lead_vocals' is a vocal, not a lead synth
    ("vocal", ("vocal", "vox", "voice", "choir", "sing", "topline")),
    ("lead", ("lead", "melody", "flute", "brass", "keys", "piano",
              "guitar", "synth")),
    ("bass", ("bass",)),
)


def role_of(name):
    nm = str(name or "").lower()
    for role, keys in _ROLE_WORDS:
        if any(k in nm for k in keys):
            return role
    return None


def court_stem(feats, role, genre="", name="?"):
    """Fail-band convictions + warn advisories for one measured stem."""
    if not feats:
        return {"court": "stem", "ok": True, "skipped": "silent stem"}
    spec = ROLE_TABLE.get(role)
    if not spec:
        return {"court": "stem", "ok": True, "skipped": f"no law for "
                f"role '{role}'"}
    flags, advisories = [], []
    c = feats.get("centroid_hz")
    if c is not None and "centroid_fail" in spec:
        lo, hi = spec["centroid_fail"]
        if not (lo <= c <= hi):
            flags.append({"kind": "timbre_offrole", "track": name,
                          "feature": "centroid_hz", "got": c,
                          "band": [lo, hi],
                          "why": f"{name} ({role}): A-weighted centroid "
                                 f"{c:.0f}Hz outside the {role} band "
                                 f"[{lo}-{hi}] — the sound does not sit "
                                 "where the role lives"})
    a = feats.get("attack_ms")
    if a is not None and "attack_fail" in spec:
        lo, hi = spec["attack_fail"]
        if not (lo <= a <= hi):
            flags.append({"kind": "attack_class", "track": name,
                          "feature": "attack_ms", "got": a,
                          "band": [lo, hi],
                          "why": f"{name} ({role}): attack {a:.0f}ms vs "
                                 f"the {role} class [{lo}-{hi}]ms — "
                                 "attack classes sit orders of magnitude "
                                 "apart (a 2ms 'pad' is a pluck wearing "
                                 "a pad's name)"})
    w = feats.get("width_pct")
    if w is not None and "width_max" in spec and w > spec["width_max"]:
        advisories.append({"kind": "role_width", "track": name, "got": w,
                           "why": f"{name} ({role}): side energy "
                                  f"{w:.0f}% above 200Hz — {role} cores "
                                  "usually stay near mono"})
    fl = feats.get("flatness")
    if fl is not None and spec.get("tonal") and "flat_max" in spec \
            and fl > spec["flat_max"]:
        advisories.append({"kind": "tonal_class", "track": name,
                           "got": fl,
                           "why": f"{name} ({role}): spectral flatness "
                                  f"{fl:.2f} reads NOISY — a {role} is a "
                                  "tonal instrument"})
    return {"court": "stem", "ok": not flags, "flags": flags,
            "advisories": advisories, "features": feats}


def heal_attack(song, verdict_flags):
    """Move a mislabeled voice's OWN attack zone into its class band —
    only when source.params already carries 'attack' (proof the zone
    exists). Mutates; returns edit ledger."""
    edits = []
    by_name = {str(t.get("name", "")): t
               for t in (song or {}).get("tracks", []) or []
               if isinstance(t, dict)}
    for f in verdict_flags:
        if f.get("kind") != "attack_class":
            continue
        t = by_name.get(f.get("track"))
        if not t:
            continue
        params = (t.get("source") or {}).get("params") or {}
        if "attack" not in params:
            continue
        lo, hi = f["band"]
        target_s = round(math.sqrt(max(lo, 1) * hi) / 1000.0, 3)
        old = params.get("attack")
        params["attack"] = target_s
        edits.append({"track": f["track"], "kind": "attack_zone",
                      "old": old, "new_s": target_s})
    return edits


# ------------------------------------------------------- item 055 levels
VOCAL_OFFSET = {                # vocal LU below full mix (r-7: avg -4.5)
    "default": (3.0, 6.0),
    "rock": (6.0, 8.0), "metal": (6.0, 8.0), "punk": (6.0, 8.0),
    "hiphop": (0.0, 3.0), "hip_hop": (0.0, 3.0), "trap": (0.0, 3.0),
    "drill": (0.0, 3.0), "rap": (0.0, 3.0),
}


def court_role_levels(stem_levels, genre="", mix_db=None):
    """stem_levels: {track_name: rms_db}. Ordering + vocal offset +
    kick/bass anchor. Levels are RELATIVE (RMS-dB deltas as LU proxy).
    Convicts only the vocal offset when WAY off (> 4dB outside its
    window); everything else advises (mix taste is real)."""
    roles = {}
    for name, db in (stem_levels or {}).items():
        r = role_of(name)
        if r and db is not None:
            roles.setdefault("bass" if r == "sub" else r, []).append(
                (name, float(db)))
    lev = {r: max(v for _, v in rows) for r, rows in roles.items()}
    flags, advisories = [], []
    g = str(genre or "").lower().replace("-", "_").replace(" ", "_")
    if mix_db is not None and "vocal" in lev:
        win = VOCAL_OFFSET["default"]
        for k, w in VOCAL_OFFSET.items():
            if k != "default" and k in g:
                win = w
                break
        off = float(mix_db) - lev["vocal"]        # positive = vocal under
        if off < win[0] - 4 or off > win[1] + 4:
            flags.append({"kind": "vocal_offset", "offset_db": round(off, 1),
                          "window": list(win),
                          "why": f"lead vocal sits {off:.1f}dB under the "
                                 f"mix vs the [{win[0]}-{win[1]}] window "
                                 "(r-7: 21/25 top hits within +-1.5dB of "
                                 "-4.5) — the vocal is "
                                 + ("buried" if off > win[1] + 4
                                    else "riding on top")})
        elif not (win[0] <= off <= win[1]):
            advisories.append({"kind": "vocal_offset_soft",
                               "offset_db": round(off, 1),
                               "why": f"vocal {off:.1f}dB under the mix — "
                                      f"window [{win[0]}-{win[1]}]"})
    if "kick" in lev and "bass" in lev:
        gap = abs(lev["kick"] - lev["bass"])
        # W98 (r-5 item 230): THE 3-LU LAW — the kick-bass bus balance
        # holds within ~3 LU (advisory) and 6 is the hard line;
        # loudness_recovery inherits the balance because these are the
        # stem levels it staged
        if gap > 3.0:
            advisories.append({"kind": "kick_bass_anchor",
                               "kick_db": round(lev["kick"], 1),
                               "bass_db": round(lev["bass"], 1),
                               "gap_db": round(gap, 1),
                               "tier": "hard" if gap > 6 else "soft",
                               "why": f"kick and bass sit {gap:.1f}dB "
                                      "apart — the bus balance law is "
                                      "~3 LU (6 = the hard line); "
                                      "rebalance at the STEMS, the "
                                      "loudness pass then lands true"})
    order = ("kick", "snare", "bass")
    if all(r in lev for r in order):
        rockish = any(k in g for k in ("rock", "metal", "punk", "indie"))
        if rockish:
            if lev["snare"] < lev["kick"] - 1:
                advisories.append({"kind": "ordering",
                                   "why": "rock backbeat law: snare "
                                          "usually rides ~3dB OVER kick"})
        elif lev["snare"] > lev["kick"] + 3:
            advisories.append({"kind": "ordering",
                               "why": "snare rides "
                                      f"{lev['snare'] - lev['kick']:.0f}dB "
                                      "over kick — electronic forms "
                                      "usually keep kick on top"})
    return {"court": "role_levels", "ok": not flags, "flags": flags,
            "advisories": advisories,
            "levels": {k: round(v, 1) for k, v in lev.items()}}


def heal_vocal_offset(song, verdict):
    """Bounded gainDb nudge (+-3) on the vocal lane toward its window.
    Mutates; returns ledger."""
    if verdict.get("ok", True):
        return []
    edits = []
    for f in verdict.get("flags", []):
        if f.get("kind") != "vocal_offset":
            continue
        off = float(f["offset_db"])
        lo, hi = f["window"]
        target = (lo + hi) / 2.0
        delta = max(min(off - target, 3.0), -3.0)
        for t in (song or {}).get("tracks", []) or []:
            if isinstance(t, dict) and role_of(t.get("name")) == "vocal" \
                    and not t.get("muted"):
                old = float(t.get("gainDb", 0) or 0)
                t["gainDb"] = round(old + delta, 1)
                edits.append({"track": t.get("name"), "kind": "vocal_gain",
                              "old": old, "new": t["gainDb"]})
                break
    return edits


# ---------------------------------------------------------------- aggregate
def court_stems(stems_dir, song=None, genre="", heal=False):
    """Measure every stem wav in a render-stems dir and court it.
    ON-DEMAND lane (CLI / eval / import QC) — never per-proposal."""
    out = {"stems": {}, "levels": {}}
    names = sorted(f for f in os.listdir(stems_dir) if f.endswith(".wav"))
    for f in names:
        name = f[:-4]
        feats = measure_stem(os.path.join(stems_dir, f))
        role = role_of(name)
        out["stems"][name] = court_stem(feats, role, genre, name)
        if feats:
            out["levels"][name] = feats["rms_db"]
    mix_db = None
    if song and song.get("_mix_rms_db") is not None:
        mix_db = song["_mix_rms_db"]
    out["role_levels"] = court_role_levels(out["levels"], genre, mix_db)
    if heal and song is not None:
        heals = {}
        att_flags = [f for v in out["stems"].values()
                     for f in v.get("flags", [])
                     if f.get("kind") == "attack_class"]
        if att_flags:
            heals["attack"] = heal_attack(song, att_flags)
        if not out["role_levels"].get("ok", True):
            heals["vocal_offset"] = heal_vocal_offset(song,
                                                      out["role_levels"])
        out["heals"] = {k: v for k, v in heals.items() if v}
    out["ok"] = all(v.get("ok", True) for v in out["stems"].values()) \
        and out["role_levels"].get("ok", True)
    return out


def main():
    import argparse
    ap = argparse.ArgumentParser(description="THE SOUND COURT (wave 20)")
    ap.add_argument("stems_dir")
    ap.add_argument("--song", default=None)
    ap.add_argument("--genre", default="")
    ap.add_argument("--heal", action="store_true")
    args = ap.parse_args()
    song = json.load(open(args.song)) if args.song else None
    v = court_stems(args.stems_dir, song, args.genre, heal=args.heal)
    if args.heal and song is not None and v.get("heals"):
        with open(args.song, "w") as fh:
            json.dump(song, fh, indent=1)
        v["saved"] = args.song
    print(json.dumps(v, indent=1))
    return 0 if v["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
