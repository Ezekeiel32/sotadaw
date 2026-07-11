#!/usr/bin/env python3
"""AUTO-MASTER — the closed-loop mastering engine (deterministic; no model in the loop).

  auto_master.py <song|path.json> [--genre g] [--reference ref.wav] [--max-iters N] [--no-eq]

Normalizes the master chain to the shape that measures right (character inserts
preserved, legacy master_limiter killed, masterGainDb folded into the input trim,
trim -> saturate -> trim -> truepeak-wall tail ensured), then iterates render->measure->
adjust until the verdict's hard checks pass:
  ceiling  <- true peak + the SUB-DOMINANT law (low band >= 45% -> -1.5 floor)
  makeup   <- LUFS distance to the genre window's centre (excess spills into the
              input trim = saturator density, the mix-headroom recovery recipe)
  band eq  <- capped +/-3 dB managed 4-band nudges toward the target band order
              (marker param _am=1; at most 2 nudge rounds — deeper imbalance is a
              SOURCE problem and is reported, never faked at the bus)

Targets: --genre KG MixTarget lane | --reference wav (LUFS window +/-1.5 around the
record, band order read off its spectrum) | generic. Only master[] and masterGainDb
are touched — never tracks (edit-locks are moot by construction).

Emits JSON: moves, before/after metrics, final chain, and the full master_report
verdict of the LAST render. Exit 0 = converged (pass true), 3 = ran but not passing
(source problems remain), 2 = could not run.
"""
import argparse, copy, json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
SONGS = os.path.join(ROOT, "songs")
M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")

from analyze2 import analyze
from master_report import kg_target, band_order_ok, GENERIC, build_report

BANDS = ("low_20_120", "lowmid_120_500", "mid_500_2k", "himid_2k_6k", "high_6k_up")
SHORT = {"low_20_120": "low", "lowmid_120_500": "lowmid", "mid_500_2k": "mid",
         "himid_2k_6k": "himid", "high_6k_up": "high"}
# managed 4-band eq: band -> (freq key, freq Hz, gain key)
EQ_LANE = {"low": ("loFreq", 100, "loGain"), "lowmid": ("midFreq", 300, "midGain"),
           "mid": ("midFreq2", 1400, "midGain2"), "himid": ("hiFreq", 5000, "hiGain"),
           "high": ("hiFreq", 7000, "hiGain")}


def resolve(arg):
    """name | songs/x.json | any path.json -> (json_path, wav_path)."""
    p = arg if os.path.isabs(arg) else os.path.join(ROOT, arg)
    if arg.endswith(".json") and os.path.exists(p):
        return p, os.path.splitext(p)[0] + ".wav"
    name = "".join(c for c in arg.lower() if c.isalnum() or c == "_")
    return os.path.join(SONGS, f"{name}.json"), os.path.join(SONGS, f"{name}.wav")


def reference_targets(ref_wav):
    """A record to sit like: LUFS window around it, band order read off its spectrum."""
    a = analyze(ref_wav)
    lufs = a["lufs_integrated"] if a["lufs_integrated"] is not None else -12.0
    order = sorted(BANDS, key=lambda b: -a["band_energy_pct"][b])[:3]
    return {"lufs_lo": max(-30.0, round(lufs - 1.5, 1)),
            "lufs_hi": min(-5.0, round(lufs + 1.5, 1)),
            "band_order": ">".join(SHORT[b] for b in order),
            "clipped": 0, "mid_floor": None, "himid_floor": None,
            "_source": f"reference:{os.path.basename(ref_wav)}"}


def split_chain(master):
    """master[] -> (character[], managed) — recognize an existing tail from the end:
    [... , trim(in), saturate, trim(mk), wall]. Missing pieces get defaults.
    The wall slot adopts fx_truepeak OR legacy fx_brickwall (upgraded in place later).
    A managed eq (params._am == 1) anywhere is adopted. Legacy limiters die here."""
    ch = [e for e in copy.deepcopy(master)
          if e.get("type") != "limiter" and (e.get("id") or "") != "master_limiter"]
    eq = None
    rest = []
    for e in ch:
        if e.get("type") == "eq" and (e.get("params") or {}).get("_am") == 1 and eq is None:
            eq = e
        else:
            rest.append(e)
    tail = {"wall": None, "mk": None, "sat": None, "in": None}
    order = ("wall", "mk", "sat", "in")
    want = {"wall": ("fx_truepeak", "fx_brickwall"), "mk": ("fx_trim",),
            "sat": ("fx_saturate",), "in": ("fx_trim",)}
    oi = 0
    while rest and oi < 4:
        e = rest[-1]
        if (e.get("id") or "") in want[order[oi]] and not e.get("bypass"):
            tail[order[oi]] = rest.pop()
            oi += 1
        else:
            break
    defaults = {"wall": {"id": "fx_truepeak", "params": {"ceiling": -1.2}},
                "mk":   {"id": "fx_trim", "params": {"level": 0.0}},
                "sat":  {"id": "fx_saturate", "params": {"drive": 5.0, "mix": 1.0}},
                "in":   {"id": "fx_trim", "params": {"level": -6.0}}}
    created = [k for k in tail if tail[k] is None]
    for k in created:
        tail[k] = defaults[k]
    for k in tail:                       # params dict must exist for the controllers
        tail[k].setdefault("params", {})
    tail["sat"]["params"].setdefault("mix", 1.0)   # FULL WET law (dry path leaks transients)
    return rest, eq, tail, created


def assemble(character, eq, tail):
    out = list(character)
    if eq is not None:
        out.append(eq)
    out += [t for t in (tail["in"], tail["sat"], tail["mk"], tail["wall"]) if t is not None]
    return out


def dark_lane(spec, bands):
    """Darkening is on-genre iff the target order is LED by low or lowmid and the
    overshoot sits above it (mid/himid/high loud) — ambient/lofi/dub shapes."""
    if not spec:
        return False
    lead = spec.split(">")[0].split("~")[0].strip()
    keymap = {v: k for k, v in SHORT.items()}
    hi_energy = bands["mid_500_2k"] + bands["himid_2k_6k"] + bands["high_6k_up"]
    return lead in ("low", "lowmid") and hi_energy > bands[keymap[lead]] * 0.4


def order_violations(bands, spec):
    """[(a_short, op, b_short)] pairs the current bands break."""
    import re
    if not spec:
        return []
    keymap = {v: k for k, v in SHORT.items()}
    toks = re.split(r"([>~])", spec)
    bad = []
    for i in range(0, len(toks) - 2, 2):
        a, op, b = toks[i], toks[i + 1], toks[i + 2]
        va, vb = bands[keymap[a]], bands[keymap[b]]
        if op == ">" and va < vb:
            bad.append((a, op, b))
        elif op == "~" and abs(va - vb) > 15.0:
            bad.append((a if va > vb else b, "~", b if va > vb else a))  # (louder, ~, quieter)
    return bad


def auto_master(song_arg, genre=None, reference=None, max_iters=8, use_eq=True, platform=None):
    sj, wav = resolve(song_arg)
    if not os.path.exists(sj):
        return {"error": f"no song {song_arg}"}
    song = json.load(open(sj))
    genre = genre or (song.get("_loop") or {}).get("genre")
    if reference:
        rp = reference if os.path.isabs(reference) else os.path.join(ROOT, reference)
        if not os.path.exists(rp):
            return {"error": f"no reference {reference}"}
        t = reference_targets(rp)
        target_src = t["_source"]
    else:
        t = kg_target(genre) or dict(GENERIC)
        target_src = f"kg:{genre}_mix" if kg_target(genre) else "generic"
    lufs_lo, lufs_hi = float(t["lufs_lo"]), float(t["lufs_hi"])
    band_spec = t.get("band_order") or ""

    moves = []
    # PER-PLATFORM DELIVERY (S11-V62): a platform overrides the LUFS window + true-peak target
    # (genre keeps band balance). Reference lane wins over platform if both are given.
    dbtp_base = -1.0
    plat = None
    if platform and not reference:
        try:
            from platform_targets import platform_target
            plat = platform_target(platform)
        except Exception:
            plat = None
        if plat:
            lufs_lo, lufs_hi = float(plat["lufs_lo"]), float(plat["lufs_hi"])
            dbtp_base = float(plat["dbtp_max"])
            target_src = (f"platform:{plat['platform']}"
                          + (f" + kg:{genre}" if kg_target(genre) else ""))
            moves.append(f"platform {plat['platform']}: aim {plat['lufs']:g} LUFS / "
                         f"{plat['dbtp_max']:g} dBTP" + (f" — {plat['note']}" if plat['note'] else ""))
    orig = song.get("master") or []
    killed = sum(1 for e in orig if e.get("type") == "limiter"
                 or (e.get("id") or "") == "master_limiter")
    character, eq, tail, created = split_chain(orig)
    # sparse/quiet lanes (ambient etc.): saturate LOWPASSES + eats gain on such masters
    # (measured 2026-07): recover with trims + wall only — unless the chain already had one.
    if float(t["lufs_hi"]) <= -12.0 and "sat" in created:
        tail["sat"] = None
        created.remove("sat")
        moves.append("quiet target: no saturate in the tail (it darkens sparse masters)")
    if created:
        moves.append("chain: added " + "+".join(
            {"in": "input trim", "sat": "saturate(mix 1.0)", "mk": "makeup trim",
             "wall": "fx_truepeak"}[k] for k in ("in", "sat", "mk", "wall") if k in created))
    if killed > 0:
        moves.append(f"chain: removed {killed} legacy master_limiter (non-functional ceiling)")
    if (tail["wall"] or {}).get("id") == "fx_brickwall":   # ISP-blind legacy wall
        tail["wall"]["id"] = "fx_truepeak"
        moves.append("wall: fx_brickwall upgraded to fx_truepeak in place "
                     "(release wall; ceiling = output dBTP)")
    mg = float(song.get("masterGainDb") or 0.0)
    if mg != 0.0:
        tail["in"]["params"]["level"] = float(tail["in"]["params"].get("level", 0.0)) + mg
        song["masterGainDb"] = 0.0
        moves.append(f"masterGainDb {mg:+.1f} folded into input trim (post-chain gain law)")

    before = None
    eq_rounds = 0
    filter_rounds = 0
    dark = next((e for e in character if (e.get("id") or "") == "fx_filter"
                 and (e.get("params") or {}).get("_am") == 1), None)
    it = 0
    passed = False
    for it in range(1, max_iters + 1):
        song["master"] = assemble(character, eq, tail)
        json.dump(song, open(sj, "w"), indent=1)
        r = subprocess.run([M1, "render", sj, wav], capture_output=True, text=True, timeout=900)
        if "ok=1" not in r.stdout + r.stderr:
            return {"error": f"render failed on pass {it}: {(r.stdout + r.stderr)[-300:]}"}
        a = analyze(wav)
        bands = a["band_energy_pct"]
        lufs, dbtp, clipped = a["lufs_integrated"], a["true_peak_dbtp"], a["clipped_samples"]
        if before is None:
            before = {"lufs": lufs, "dbtp": dbtp, "clipped": clipped, "bands": bands}
            if a["duration_s"] > 240 and max_iters > 3:
                max_iters = 3
                moves.append(f"long render ({a['duration_s']:.0f}s): capped at 3 passes")

        order_ok = band_order_ok(bands, band_spec)
        lufs_ok = lufs is not None and lufs_lo <= lufs <= lufs_hi
        dbtp_target = dbtp_base
        if plat and plat["platform"] == "spotify" and lufs is not None and lufs > -14.0:
            dbtp_target = min(dbtp_target, -2.0)     # Spotify: hotter than -14 LUFS => -2 dBTP
        if clipped == 0 and dbtp <= dbtp_target and lufs_ok and order_ok:
            passed = True
            break

        did = []
        p = lambda e: e["params"]
        ceil = float(p(tail["wall"]).get("ceiling", -1.2))
        base_ceil = min(-1.2, dbtp_target)           # ceiling param = output dBTP; sit under the target
        want_ceil = min(base_ceil, -1.5) if bands["low_20_120"] >= 45.0 else base_ceil
        if dbtp > dbtp_target:
            want_ceil = min(want_ceil, ceil - (dbtp - dbtp_target) - 0.2)
        want_ceil = max(-3.0, min(dbtp_target, round(want_ceil, 2)))
        if abs(want_ceil - ceil) > 0.05:
            p(tail["wall"])["ceiling"] = want_ceil
            did.append(f"ceiling {ceil:+.2f} -> {want_ceil:+.2f}"
                       + (" (sub-dominant)" if bands["low_20_120"] >= 45.0 else ""))
        if lufs is not None and not lufs_ok:
            d = (lufs_lo + lufs_hi) / 2.0 - lufs
            mk = float(p(tail["mk"]).get("level", 0.0)) + max(-6.0, min(6.0, d))
            if mk > 12.0:                              # spill excess into density (input trim)
                spill = min(8.0, mk - 12.0)
                mk = 12.0
                iv = float(p(tail["in"]).get("level", 0.0)) + spill
                p(tail["in"])["level"] = round(iv, 1)
                did.append(f"input trim +{spill:.1f} (density)")
            p(tail["mk"])["level"] = round(mk, 1)
            did.append(f"makeup -> {mk:+.1f} dB (lufs {lufs:.1f} vs [{lufs_lo:g},{lufs_hi:g}])")
        if clipped > 0:
            p(tail["mk"])["level"] = round(float(p(tail["mk"]).get("level", 0.0)) - 1.5, 1)
            did.append(f"clipped {clipped}: makeup -1.5")
        if not order_ok and use_eq and eq_rounds < 2:
            if eq is None:
                eq = {"type": "eq", "params": {"_am": 1.0}}
            for a_s, op, b_s in order_violations(bands, band_spec):
                fa, hz_a, ga = EQ_LANE[a_s]
                fb, hz_b, gb = EQ_LANE[b_s]
                step = 1.2 if op == ">" else 1.5
                if op == ">":
                    eq["params"][fa] = hz_a
                    eq["params"][ga] = max(-3.0, min(3.0, float(eq["params"].get(ga, 0.0)) + step))
                eq["params"][fb] = hz_b
                eq["params"][gb] = max(-3.0, min(3.0, float(eq["params"].get(gb, 0.0)) - step))
                did.append(f"eq nudge {a_s}{'+' if op == '>' else ''} / {b_s}- (round {eq_rounds + 1})")
            eq_rounds += 1
        elif not order_ok and use_eq and filter_rounds < 3 and dark_lane(band_spec, bands):
            # the ambient band-order fix (recorded 2026-07): +/-3 bells can't move a
            # 20-point mid overshoot — a DARK FILTER can, and it's on-genre when the
            # target order is led by low/lowmid. Walk the cutoff toward the recorded
            # winning zone (~300-550 Hz), capped at 3 rounds.
            if dark is None:
                dark = {"id": "fx_filter", "params": {"_am": 1.0, "cutoff": 2500.0, "res": 0.7}}
                character = character + [dark]
            else:
                dark["params"]["cutoff"] = max(350.0, round(dark["params"]["cutoff"] * 0.36))
            filter_rounds += 1
            did.append(f"dark filter -> cutoff {dark['params']['cutoff']:g} Hz "
                       f"(round {filter_rounds})")
        if not did:
            break                                      # controllers exhausted — report honestly
        moves += [f"pass {it}: " + m for m in did]

    report = build_report(song_path=sj, genre=(None if reference else genre), no_render=True,
                          platform=(None if reference else platform))
    if reference:                                      # judge vs the reference lane, not KG
        bands = report["metrics"]["bands"]
        lufs = report["metrics"]["lufs"]
        for c in report["checks"]:
            if c["name"] == "lufs":
                c["ok"] = lufs is not None and lufs_lo <= lufs <= lufs_hi
                c["want"] = f"[{lufs_lo:g}, {lufs_hi:g}] ({target_src})"
            if c["name"] == "band_order":
                c["ok"] = band_order_ok(bands, band_spec)
                c["want"] = band_spec
        hard = [c for c in report["checks"] if c["hard"]]
        report["pass"] = all(c["ok"] for c in hard)
        report["target"] = target_src
        failing = [c for c in report["checks"] if not c["ok"]]
        report["fix_first"] = failing[0]["name"] if failing else None

    after = {"lufs": report["metrics"]["lufs"], "dbtp": report["metrics"]["true_peak_dbtp"],
             "clipped": report["metrics"]["clipped"], "bands": report["metrics"]["bands"]}
    return {"song": os.path.splitext(os.path.basename(sj))[0], "genre": genre,
            "platform": (plat["platform"] if plat else None),
            "target": target_src, "iterations": it, "pass": report["pass"],
            "moves": moves, "before": before, "after": after,
            "master": song["master"], "masterGainDb": song.get("masterGainDb", 0),
            "report": report,
            "note": None if report["pass"] else
                    "bus moves exhausted — remaining failures are SOURCE problems "
                    "(see report hints): fix track gains/notes, then re-run"}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("song")
    ap.add_argument("--genre")
    ap.add_argument("--reference", help="master toward this record (LUFS window + band tilt)")
    ap.add_argument("--max-iters", type=int, default=8)
    ap.add_argument("--platform", help="deliver to a platform ref (S11-V62): "
                    "spotify|apple|youtube|tidal|amazon|deezer|tiktok|reels|streaming")
    ap.add_argument("--no-eq", action="store_true", help="never touch band balance at the bus")
    a = ap.parse_args()
    rep = auto_master(a.song, a.genre, a.reference, a.max_iters, not a.no_eq, a.platform)
    print(json.dumps(rep, indent=1))
    sys.exit(2 if "error" in rep else 0 if rep["pass"] else 3)
