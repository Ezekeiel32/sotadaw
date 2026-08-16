#!/usr/bin/env python3
"""THE MASTERING VERDICT — one source of truth for "does this master measure right".

  master_report.py <song|path.json> [--genre g] [--no-render]
  master_report.py --wav songs/x.wav [--genre g]

Render (if stale) -> analyze2 metrics -> KG MixTarget for the genre -> per-check
verdict JSON with got/want deltas and SOURCE-FIX hints (the mix-headroom laws).
Used by the DAW's master rack (CHECK button), the master_report MCP tool, and
anything else that needs a pass/fix answer instead of raw numbers.

Genre resolution: --genre > song._loop.genre > none (generic streaming/club target).
Exit code 0 = ran (read "pass" in the JSON); 2 = could not run.
"""
import argparse, json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
SONGS = os.path.join(ROOT, "songs")
M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")

from analyze2 import analyze                      # the ears (dtype-aware, LUFS, dBTP, bands)

GENERIC = {"lufs_lo": -16.0, "lufs_hi": -8.0, "band_order": "", "clipped": 0,
           "mid_floor": None, "himid_floor": None}

# LONG-FORM SET/MIX profile: a 30-60min set with quiet intros/outros reads
# 1-3 LU lower integrated than a 3-min song AT THE SAME perceived density
# (Apple normalizes to -16; DJ-mix platform norms -14..-16). PROVEN NEEDED
# 2026-07-05: trim 2.0->2.7 into the brickwall moved a 39.5-min set's
# integrated by 0.01 LU — the limiter absorbs the push; the material's
# density ceiling IS ~-16.3. Judge the material, not the stopwatch.
SET_PROFILE = {"lufs_lo": -17.5, "lufs_hi": -11.0, "band_order": "", "clipped": 0,
               "mid_floor": None, "himid_floor": None}


def kg_target(genre):
    """MixTarget lane from the graph; None if genre unknown/graph down."""
    if not genre:
        return None
    try:
        from eval_daw import genre_targets
        return genre_targets(genre)
    except Exception:
        return None


def band_order_ok(bands, spec):
    from eval_daw import band_order_ok as _ok
    return _ok(bands, spec)


def resolve_song(arg):
    """name | songs/x.json | absolute path -> (name, json_path)."""
    p = arg if os.path.isabs(arg) else os.path.join(ROOT, arg)
    if arg.endswith(".json") and os.path.exists(p):
        return os.path.splitext(os.path.basename(p))[0], p
    name = "".join(c for c in arg.lower() if c.isalnum() or c == "_")
    return name, os.path.join(SONGS, f"{name}.json")


def build_report(song_path=None, wav=None, genre=None, no_render=False, profile=None, platform=None):
    song, name = None, None
    if song_path:
        name, sj = resolve_song(song_path)
        if not os.path.exists(sj):
            return {"error": f"no song {song_path}"}
        song = json.load(open(sj))
        genre = genre or (song.get("_loop") or {}).get("genre")
        wav = wav or os.path.splitext(sj)[0] + ".wav"   # beside the json (temp copies too)
        if not no_render and (not os.path.exists(wav)
                              or os.path.getmtime(wav) < os.path.getmtime(sj)):
            r = subprocess.run([M1, "render", sj, wav], capture_output=True, text=True, timeout=600)
            if not os.path.exists(wav):
                return {"error": f"render failed: {(r.stdout + r.stderr)[-400:]}"}
    if not wav or not os.path.exists(wav):
        return {"error": f"no wav to analyze: {wav}"}

    a = analyze(wav)
    tgt = kg_target(genre)
    source = f"kg:{genre}_mix" if tgt else ("generic (genre unknown to KG)" if genre else "generic")
    if profile == "set":
        tgt, source = dict(SET_PROFILE), "set profile (long-form mix)"
    t = tgt or dict(GENERIC)
    lufs_lo, lufs_hi = t.get("lufs_lo", -16), t.get("lufs_hi", -8)
    bands = a["band_energy_pct"]
    sub_heavy = bands["low_20_120"] >= 45.0
    dbtp_max = -1.0

    # PER-PLATFORM DELIVERY (S11-V62): a named platform overrides the LUFS window + true-peak
    # ceiling with its normalization reference. Genre still supplies band balance below.
    platform_info = None
    if platform:
        try:
            from platform_targets import platform_target
            pt = platform_target(platform)
        except Exception:
            pt = None
        if pt:
            lufs_lo, lufs_hi = pt["lufs_lo"], pt["lufs_hi"]
            dbtp_max = pt["dbtp_max"]
            # Spotify rule: a master hotter than -14 LUFS must tighten to -2 dBTP
            if pt["platform"] == "spotify" and a["lufs_integrated"] is not None \
                    and a["lufs_integrated"] > -14.0:
                dbtp_max = min(dbtp_max, -2.0)
            source = f"platform:{pt['platform']}" + (f" + {source}" if tgt else "")
            platform_info = pt

    checks = []
    def check(nm, ok, got, want, hint=None, hard=True):
        c = {"name": nm, "ok": bool(ok), "got": got, "want": want, "hard": hard}
        if hint and not ok:
            c["hint"] = hint
        checks.append(c)

    check("clipped", a["clipped_samples"] <= t.get("clipped", 0),
          a["clipped_samples"], "== 0",
          "clipped samples: lower the makeup fx_trim into the brickwall (or hot track gains). "
          "NEVER normalise output or touch masterGainDb; clipped_samples is the convergence "
          "signal — drive it to 0.")
    check("true_peak", a["true_peak_dbtp"] <= dbtp_max,
          a["true_peak_dbtp"], f"<= {dbtp_max}",
          ("sub-dominant material overshoots the ceiling in TRUE peak: set fx_truepeak "
           "ceiling -1.5..-2.0 (ceiling = OUTPUT dBTP) and keep it LAST in master[]." if sub_heavy else
           "inter-sample overs: lower the fx_truepeak ceiling (-1.2..-1.5) and verify the wall "
           "is the LAST master[] entry."))
    lufs = a["lufs_integrated"]
    lufs_ok = lufs is not None and lufs_lo <= lufs <= lufs_hi
    check("lufs", lufs_ok, lufs, f"[{lufs_lo}, {lufs_hi}]",
          None if lufs is None or lufs_ok else
          (f"quiet by {lufs_lo - lufs:.1f} LU: recover density INSIDE the chain — fx_trim (+in) "
           f"-> fx_saturate mix 1.0 -> fx_trim (makeup) -> fx_truepeak; iterate the trims."
           if lufs < lufs_lo else
           f"hot by {lufs - lufs_hi:.1f} LU for the genre window: back off the makeup trim."))
    if t.get("band_order"):
        check("band_order", band_order_ok(bands, t["band_order"]),
              {k: bands[k] for k in ("low_20_120", "lowmid_120_500", "mid_500_2k",
                                     "himid_2k_6k", "high_6k_up")},
              t["band_order"],
              "band balance is a SOURCE problem: fix track gains/notes/EQ bells "
              "(never master-bus makeup). See mix-headroom + the ambient band-order lesson.")
    if t.get("mid_floor") is not None:
        floor_ok = (bands["mid_500_2k"] >= t["mid_floor"]
                    and bands["himid_2k_6k"] >= (t.get("himid_floor") or 0))
        check("spectral_floor", floor_ok,
              {"mid": bands["mid_500_2k"], "himid": bands["himid_2k_6k"]},
              {"mid": t["mid_floor"], "himid": t.get("himid_floor") or 0},
              "order can pass while magnitudes collapse: restore presence at the source "
              "(lead/keys gain, himid content), don't just reorder bands.")
    if a.get("lr_correlation") is not None:
        check("phase", a["lr_correlation"] > -0.2, a["lr_correlation"], "> -0.2",
              "L/R anti-correlation = mono-collapse risk: pull fx_widen off low elements, "
              "reduce width on the offenders.", hard=False)
    if a.get("psr") is not None:
        # W83 (item 233): the ONE resolver — the master court and the
        # dynamics court must agree (flat 6.0 convicted gabber, pardoned
        # crushed classical)
        try:
            import psr_floors as _pf
            _fl = _pf.floor_for_genre(genre)
            _fl = float(_fl[0] if isinstance(_fl, (tuple, list)) else _fl)
        except Exception:
            _fl = 6.0
        check("dynamics", a["psr"] >= _fl, a["psr"],
              f">= {_fl:g} dB (PSR, genre floor)",
              "over-limited: PSR (true-peak minus loudest 3s loudness) under ~6 dB = crushed "
              "dynamics (research_mastering_sota.md §4, convention). Ease the makeup trim / limiter "
              "drive — streaming normalises loudness DOWN anyway, so you lose punch for nothing.",
              hard=False)

    # song-side chain laws (only when we have the song JSON)
    if song is not None:
        mg = float(song.get("masterGainDb", 0) or 0)
        check("masterGainDb_zero", mg == 0.0, mg, "== 0",
              "masterGainDb runs AFTER the whole master chain — post-limiter gain re-opens the "
              "headroom you just limited. Set it 0 and stage inside the chain with fx_trim "
              "(zone 'level').", hard=False)
        chain = song.get("master") or []
        ids = [(m.get("id") or m.get("type", "?")) for m in chain]
        live = [(m.get("id") or m.get("type", "?")) for m in chain if not m.get("bypass")]
        wall_last = bool(live) and live[-1] in ("fx_truepeak", "fx_brickwall")
        check("wall_last", wall_last, ids or "empty chain",
              "ends with fx_truepeak (fx_brickwall legacy-ok)",
              "end master[] with THE RELEASE WALL: {\"id\": \"fx_truepeak\", \"params\": "
              "{\"ceiling\": -1.2}} (ceiling = OUTPUT dBTP; fx_brickwall is ISP-blind legacy "
              "— finish() upgrades it in place; master_limiter/type:limiter ceilings are "
              "non-functional; a wall that isn't last isn't a wall).", hard=False)

    hard = [c for c in checks if c["hard"]]
    soft = [c for c in checks if not c["hard"]]
    score = (2 * sum(c["ok"] for c in hard) + sum(c["ok"] for c in soft)) \
            / max(1, 2 * len(hard) + len(soft))
    failing = [c for c in checks if not c["ok"]]
    return {
        "song": name, "wav": os.path.relpath(wav, ROOT) if wav.startswith(ROOT) else wav,
        "genre": genre or None, "target": source,
        "platform": platform_info["platform"] if platform_info else None,
        "pass": all(c["ok"] for c in hard), "score": round(score, 3),
        "fix_first": failing[0]["name"] if failing else None,
        "checks": checks,
        "metrics": {"lufs": lufs, "true_peak_dbtp": a["true_peak_dbtp"],
                    "peak_dbfs": a["peak_dbfs"], "clipped": a["clipped_samples"],
                    "rms_db": a["rms_db"], "width_db": a.get("stereo_width_db"),
                    "lr_correlation": a.get("lr_correlation"),
                    # pro dynamics/loudness meter set (S11-V59)
                    "lufs_short_term_max": a.get("lufs_short_term_max"),
                    "lufs_momentary_max": a.get("lufs_momentary_max"),
                    "lra": a.get("lra"), "crest_factor_db": a.get("crest_factor_db"),
                    "plr": a.get("plr"), "psr": a.get("psr"),
                    "centroid_hz": a["spectral_centroid_hz"], "bands": bands,
                    "duration_s": a["duration_s"]},
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("song", nargs="?", help="song name or songs/x.json")
    ap.add_argument("--wav", help="analyze this wav (skip song-side checks if no song)")
    ap.add_argument("--genre", help="KG MixTarget lane (default: song._loop.genre or generic)")
    ap.add_argument("--platform", help="deliver to a platform ref (S11-V62): "
                    "spotify|apple|youtube|tidal|amazon|deezer|tiktok|reels|streaming")
    ap.add_argument("--profile", default=None, choices=("set",),
                    help="material profile: set = long-form mix windows")
    ap.add_argument("--no-render", action="store_true")
    a = ap.parse_args()
    if not a.song and not a.wav:
        ap.error("need a song or --wav")
    rep = build_report(a.song, a.wav, a.genre, a.no_render, a.profile, a.platform)
    print(json.dumps(rep, indent=1))
    sys.exit(2 if "error" in rep else 0)
