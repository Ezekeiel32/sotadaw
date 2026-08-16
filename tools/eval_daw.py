#!/usr/bin/env python3
"""THE EVAL HARNESS — CI for musicality (SPEC S6-V35 gauntlet, v1).

  eval_daw.py --brief phonk            run ONE genre brief through the REAL agent + machine-check
  eval_daw.py --check <song>           machine-check an existing rendered song against its genre
  eval_daw.py --suite                  check all briefs' latest outputs (no agent calls)

Machine checks per genre (from the KG MixTarget + genre props):
  bpm in range · key set · clipped_samples == 0 · LUFS in range · band order · length >= 8 bars
Results append to eval/history.jsonl — the trend line IS the regression suite.
No skill ships if its genre's eval goes red (registry gate, enforced by humans for now).
"""
import argparse, json, os, re, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
SONGS = os.path.join(ROOT, "songs")
M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")
VENV_PY = os.path.join(ROOT, ".venv", "bin", "python")

BRIEFS = {
    "phonk":      "make a dark phonk beat, 12 bars, cowbell lead front and center",
    "trap":       "make a dark trap beat with a walking 808 and rolled hats, 16 bars",
    "house":      "make a warm house groove with an offbeat bass and a filter build, 16 bars",
    "techno":     "make a driving techno track around one dark stab, 16 bars",
    "dnb":        "make a dnb roller with a reese bassline, 16 bars",
    "lofi":       "make a dusty lofi beat with lazy drums and m7 keys, 12 bars",
    "ambient":    "make a breathing ambient piece with evolving pads and sparse bells, 16 bars",
    "dembow":     "make a dembow beat with the 3-3-2 lilt and a dark melody, 16 bars",
    "amapiano":   "make an amapiano groove led by log drums with lots of space, 16 bars",
    "dubstep":    "make a dubstep half-time track where the wobble answers the drums, 16 bars",
    "trance":     "make an uplifting trance section with supersaw swells and a filter rise, 16 bars",
    "hardstyle":  "make a hardstyle track where the kick carries the bassline, 16 bars",
    "jungle":     "make a jungle roller with re-chopped breaks every 4 bars, 16 bars",
    "footwork":   "make a footwork track with triplet kick cells against straight claps, 16 bars",
    "gqom":       "make a dark gqom track from broken drum pulses only, 16 bars",
    "hyperpop":   "make a hyperpop burst with bright chopped vox and extreme width, 16 bars",
    "bossanova":  "make a soft bossa nova with rim clave and M7 comping, 16 bars",
    "cumbia":     "make a cumbia with continuous scrape and offbeat stabs, 16 bars",
    "moombahton": "make a moombahton groove at 110 with big builds, 16 bars",
    "driftphonk": "make a drift phonk track with a wow'd cowbell lead and car sub, 16 bars",
    "breakcore":  "make a breakcore track that switches patterns every 2 bars, 16 bars",
    "boombap":    "make a dusty boombap beat with heavy backbeat and m7 keys, 12 bars",
    "drill":      "make a UK drill beat with sliding 808s and ghost snares, 16 bars",
    "ukgarage":   "make a 2-step garage groove with shuffled hats, 16 bars",
    "afrobeats":  "make an afrobeats groove with 3:2 percs and a log-drum bass, 16 bars",
    "jerseyclub": "make a jersey club track on the 5-kick bed, 16 bars",
    "synthwave":  "make a synthwave track with supersaw pads and a driving arp, 16 bars",
    "goa":        "make a goa trance journey with layered FM arps, 16 bars",
}

def genre_targets(genre):
    from kg import KG
    v = KG().genre_view(genre)
    if v is None:
        return None
    mt = v["mixtargets"][0] if v["mixtargets"] else {}
    return {"bpm_lo": v["props"].get("bpm_lo", 40), "bpm_hi": v["props"].get("bpm_hi", 220),
            "lufs_lo": mt.get("lufs_lo", -30), "lufs_hi": mt.get("lufs_hi", -5),
            "band_order": mt.get("band_order", ""), "clipped": mt.get("clipped_samples", 0),
            "mid_floor": mt.get("mid_floor_pct"), "himid_floor": mt.get("himid_floor_pct")}

def band_order_ok(bands, spec):
    """spec like 'low>lowmid>mid>himid>high' or 'low~lowmid>mid' (~ = within 15pts)."""
    if not spec:
        return True
    keymap = {"low": "low_20_120", "lowmid": "lowmid_120_500", "mid": "mid_500_2k",
              "himid": "himid_2k_6k", "high": "high_6k_up"}
    tokens = re.split(r"([>~])", spec)
    ok = True
    for i in range(0, len(tokens) - 2, 2):
        a, op, b = bands[keymap[tokens[i]]], tokens[i + 1], bands[keymap[tokens[i + 2]]]
        ok &= (a >= b) if op == ">" else (abs(a - b) <= 15.0)
    return ok

def check_song(name, genre):
    tgt = genre_targets(genre)
    sj = os.path.join(SONGS, f"{name}.json")
    wav = os.path.join(SONGS, f"{name}.wav")
    if not os.path.exists(sj):
        return {"error": f"no song {name}"}
    song = json.load(open(sj))
    if not os.path.exists(wav) or os.path.getmtime(wav) < os.path.getmtime(sj):
        subprocess.run([M1, "render", sj, wav], capture_output=True, timeout=300)
    py = VENV_PY if os.path.exists(VENV_PY) else "python3"
    a = json.loads(subprocess.run([py, os.path.join(ROOT, "tools", "analyze2.py"), wav],
                                  capture_output=True, text=True, timeout=180).stdout)
    checks = {
        "bpm_in_range": tgt["bpm_lo"] <= float(song.get("bpm", 0)) <= tgt["bpm_hi"],
        "key_set": bool(song.get("key")),
        "clipped_ok": a["clipped_samples"] <= tgt["clipped"],
        "lufs_in_range": (a["lufs_integrated"] is not None
                          and tgt["lufs_lo"] <= a["lufs_integrated"] <= tgt["lufs_hi"]),
        "band_order_ok": band_order_ok(a["band_energy_pct"], tgt["band_order"]),
        "length_ok": float(song.get("lengthBars", 0)) >= 8,
        "true_peak_ok": a["true_peak_dbtp"] <= -0.3,
    }
    # spectral floors (judge lesson 2026-07-03): order can pass while magnitudes collapse
    if tgt.get("mid_floor") is not None:
        checks["spectral_floor_ok"] = (
            a["band_energy_pct"]["mid_500_2k"] >= tgt["mid_floor"]
            and a["band_energy_pct"]["himid_2k_6k"] >= (tgt.get("himid_floor") or 0))
    # THE GENRE-TRUTH GATE (ledger dr30, 2026-07-12): clap_genre_sim was
    # measured everywhere and GATED nowhere — a take embedding nowhere near
    # its genre scored 1.0. This is a DISASTER GATE, not a quality bar
    # (weakest legit take measured 0.359; wrong-genre embeddings land
    # ~0.1-0.2) — ab_closeness stays the quality axis. CLAP is heavy:
    # SOTADAW_EVAL_CLAP=0 skips (the check drops out of the denominator,
    # never a free pass), and unavailability fails open the same way.
    _gs = None
    if os.environ.get("SOTADAW_EVAL_CLAP", "1") != "0":
        _gs = clap_genre_sims([wav], genre)[0]
        if _gs is not None:
            # DATA PASS (16 rotation rows, 2026-07-12): raw births measure
            # min 0.073 / med 0.223 — the 0.25 calibration came from
            # LOUDNESS-PASSED briefs (0.36-0.49) and flags half of all raw
            # world-genre rows (label sensitivity + level correlation).
            # Rotation context gates at the true disaster floor.
            _floor = 0.10 if os.environ.get("SOTADAW_EVAL_RAW") == "1" else 0.25
            checks["genre_sim_ok"] = _gs >= _floor
    # PRODUCER MIND P19 (2026-07-14): the MUSIC checks join the gauntlet —
    # engineering floors said "not broken"; these say "not mid". All
    # deterministic from song.json + the analysis (docs/SPEC_PRODUCER_MIND.md).
    _music = {}
    try:
        import music_court as _mc
        import arc_court as _ac
        _kv = _mc.court_key(song, genre)
        if not _kv.get("skipped"):
            checks["key_court_ok"] = bool(_kv.get("ok"))
            _music["in_key_pct"] = _kv.get("in_key_pct")
        checks["pocket_ok"] = bool(_mc.court_pocket(song, genre).get("ok"))
        _av = _ac.court_arc(song, genre, a)
        if not _av.get("skipped"):
            checks["arc_ok"] = bool(_av.get("ok"))
            _music["arc_flags"] = [f.get("kind") for f in _av.get("flags", [])]
    except Exception:
        pass
    score = sum(checks.values()) / len(checks)
    return {"song": name, "genre": genre, "score": round(score, 3), "checks": checks,
            "metrics": {"bpm": song.get("bpm"), "key": song.get("key"),
                        "clap_genre_sim": _gs, **_music,
                        "lra": a.get("lra"),
                        "lufs": a["lufs_integrated"], "peak": a["peak_dbfs"],
                        "dbtp": a["true_peak_dbtp"], "clipped": a["clipped_samples"],
                        "bands": a["band_energy_pct"]}}

# TRANSFORM genres: the mechanic IS reworking a source (slow/pitch/speed an
# existing record). Their briefs hand the agent a committed render as material —
# import_song_audio + sourceBpm warp is the flow under test.
TRANSFORM_SOURCES = {
    "vaporwave": "songs/eval_gospel.wav",      # soulful source to slow + drench
    "nightcore": "songs/eval_ukgarage.wav",    # a groove to pitch/tempo UP
    "witch_house": "songs/eval_memphis_rap.wav",
}

def graph_brief(genre):
    """Derive a brief from the KG for any genre not hand-listed — the suite
    grows with the graph (40+ genres eval-able the moment they're curated)."""
    from kg import KG
    view = KG().genre_view(genre)
    if not view:
        raise SystemExit(f"genre '{genre}' not in BRIEFS or the knowledge graph")
    p = view.get("props", {})
    bpm = int((p.get("bpm_lo", 120) + p.get("bpm_hi", 120)) / 2)
    key = p.get("common_key", "")
    tech = [t["name"].replace("_", " ") for t in view.get("techniques", [])[:2]]
    lean = f" leaning on {' and '.join(tech)}" if tech else ""
    if genre in TRANSFORM_SOURCES:
        return (f"transform the existing record {TRANSFORM_SOURCES[genre]} into a "
                f"{genre.replace('_', ' ')} piece at {bpm}bpm{lean} — import it and warp it "
                f"(sourceBpm vs song bpm is the transform), then add what the genre needs, 16 bars")
    return f"make a {genre.replace('_', ' ')} track at {bpm}bpm{' in ' + key if key else ''}{lean}, 16 bars"

def run_brief(genre, model="claude-opus-4-8"):
    """One real-agent run: brief -> song eval_<genre> -> machine checks.
    --model exists to prove SMALL models hold the bar now that THE GOLD
    STANDARD (library/gold) rides start_session — the whole point of the bank."""
    name = f"eval_{genre}"
    brief = BRIEFS.get(genre) or graph_brief(genre)
    prompt = f"""You are the producer agent under EVALUATION. Produce a song from scratch.
Brief: "{brief}"
Rules: use ONLY daw MCP tools (no ToolSearch/Read/Bash). start_session with genre "{genre}" FIRST
(that loads the {genre} skill — obey its hard constraints exactly: bpm range, key, mix targets).
write_song name "{name}". Then render_song + analyze_wav and fix violations (max 2 fix rounds).
End with one line: DONE <bpm> <key>."""
    env = dict(os.environ, MCP_TIMEOUT="30000", MCP_TOOL_TIMEOUT="600000")
    t0 = time.time()
    cost, exit_code = None, None
    try:
        p = subprocess.run(
            ["claude", "-p", prompt, "--model", model,
             "--mcp-config", os.path.join(ROOT, "agent", "mcp.json"), "--strict-mcp-config",
             "--permission-mode", "dontAsk",
             "--allowedTools", ",".join("mcp__daw__" + t for t in
                 ("start_session", "get_skill", "list_kits", "list_instruments", "write_song",
                  "update_track", "set_track_fx", "set_buses", "automate", "update_song_meta",
                  "render_song", "analyze_wav", "hear", "vst_presets", "apply_groove", "extract_groove",
                  "duplicate_bars", "import_song_audio", "set_clip_slot")),
             "--max-turns", "25", "--output-format", "stream-json", "--verbose"],
            capture_output=True, text=True, timeout=1500, cwd=ROOT, env=env)
        exit_code = p.returncode
        # transcript: every brief keeps its stream (the W19k diagnosis gap)
        try:
            with open(os.path.join(ROOT, "eval", f"run_{genre}.log"), "w") as lf:
                lf.write(p.stdout + "\n--- STDERR ---\n" + p.stderr)
        except Exception:
            pass
        try:
            for line in reversed(p.stdout.strip().splitlines()):
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                if obj.get("type") == "result":
                    cost = obj.get("total_cost_usd")
                    break
        except Exception:
            pass
    except subprocess.TimeoutExpired:
        exit_code = "timeout"          # judge the artifact anyway — the song on disk is what counts
    elapsed = round(time.time() - t0)
    result = check_song(name, genre)
    result.update({"elapsed_s": elapsed, "cost_usd": cost, "agent_exit": exit_code,
                   "brief": brief, "t": time.time()})
    os.makedirs(os.path.join(ROOT, "eval"), exist_ok=True)
    with open(os.path.join(ROOT, "eval", "history.jsonl"), "a") as f:
        f.write(json.dumps(result) + "\n")
    return result

# ---------------- R3: THE HARDER RULER — blind A/B vs REAL RECORDS ----------------
# The structural checks saturated (history 2026-07: nine of twelve rows = 1.0);
# the new ceiling is real released records, unsaturable by construction: to score
# 100 a render must sit MORE inside the real-record cloud than the records
# themselves do. Reference pool = the actual records on this box (Chezy's
# imports). Families: rap-adjacent genres score against the rap records; every
# other genre scores against the whole real-music cloud (small-N honesty: the
# percentile is coarse but the baseline is REAL). Excluded on purpose:
# untitled_3_master.mp3 (Chezy's own master, not a released record) and the
# non-music recordings.
#
# MEASURED ORDERING BOUNDARY (2026-07-09; eval_funk + 3 controlled degradations):
# insiderness orders destruction DOWN (hard clip 80.7->75.7 closeness,
# dark-mono ->74.1) but REWARDS spectral tilt TOWARD the cloud (+14dB bass on
# funk vs this rap-heavy pool: ->82.3) — it is RECORD-COHERENCE, not
# genre-truth. CLAP genre-sim is the complementary axis (catches the bass
# tilt 0.148->0.144 and the clip ->0.110, but hears dark-mono as 'vintage
# funk' ->0.189). Neither is a total order at ~0.01-cosine resolution, so the
# row carries BOTH plus the percentile ceiling; the blind judge (full
# symmetric digests incl. clipped/bands/trajectories) is the verdict leg, and
# the per-genre structural checks keep genre truth. Never collapse this to
# one scalar.
_DL = "/home/chezy/Downloads"
AB_REFS = {
    "_rap": [f"{_DL}/BLP Kosher - Digital Footprint (Official Music Video).mp3",
             f"{_DL}/BLP Kosher - Hour Glass (Official Video).mp3",
             f"{_DL}/Matisyahu feat. BLP Kosher  - Anxiety (Official Music Video).mp3",
             f"{_DL}/Wadddlllttt.mp3"],
    "_all": [f"{_DL}/BLP Kosher - Digital Footprint (Official Music Video).mp3",
             f"{_DL}/BLP Kosher - Hour Glass (Official Video).mp3",
             f"{_DL}/Matisyahu feat. BLP Kosher  - Anxiety (Official Music Video).mp3",
             f"{_DL}/Wadddlllttt.mp3",
             f"{_DL}/Entheogenic - Aranyanyara.mp3",
             f"{_DL}/Yeshievishe Reid.mp3"],
}
AB_FAMILY = {g: "_rap" for g in ("trap", "phonk", "driftphonk", "memphis_rap",
                                 "boombap", "drill", "grime", "jerseyclub", "rage")}

def _ab_refs_for(genre):
    fam = AB_FAMILY.get(genre, "_all")
    refs = [p for p in AB_REFS[fam] if os.path.exists(p)]
    return fam, refs

def _pctile(value, baseline):
    """Midrank percentile of value within baseline (plain python, small N)."""
    below = sum(1 for b in baseline if b < value)
    eq = sum(1 for b in baseline if b == value)
    return round(100.0 * (below + 0.5 * eq) / len(baseline), 1)

def _ref_wav(path):
    """Transcode a reference record to a cached 44.1k wav (analyze2 reads wav)."""
    import hashlib
    cache = os.path.join(ROOT, "eval", ".ab_refs")
    os.makedirs(cache, exist_ok=True)
    out = os.path.join(cache, hashlib.md5(path.encode()).hexdigest()[:10] + ".wav")
    if not os.path.exists(out):
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", path,
                        "-ar", "44100", "-ac", "2", out], timeout=300, check=True)
    return out

def _audio_digest(wav, genre):
    """SYMMETRIC audio-only digest — the blind judge must not be able to tell
    'generated' from 'record' by digest SHAPE (no track lists, no song.json)."""
    py = VENV_PY if os.path.exists(VENV_PY) else "python3"
    a = json.loads(subprocess.run([py, os.path.join(ROOT, "tools", "analyze2.py"), wav],
                                  capture_output=True, text=True, timeout=300).stdout)
    return {"lufs": a["lufs_integrated"], "peak_dbfs": a["peak_dbfs"],
            "dbtp": a["true_peak_dbtp"], "clipped": a["clipped_samples"],
            "bands_pct": a["band_energy_pct"], "width_db": a["stereo_width_db"],
            "rms_by_quarter": a["rms_by_quarter_db"][:24],
            "centroid_by_quarter": a["centroid_by_quarter_hz"][:24]}

def judge_blind(gen_wav, ref_path, genre):
    """The BLIND leg: two unlabeled audio digests, judge must pick the real
    released record. judge_fooled = it picked ours (or refused/tied)."""
    import random
    ref_wav = _ref_wav(ref_path)
    dg, dr = _audio_digest(gen_wav, genre), _audio_digest(ref_wav, genre)
    sg, sr_ = clap_genre_sims([gen_wav, ref_wav], genre)
    if sg is not None:
        dg["clap_genre_sim"], dr["clap_genre_sim"] = sg, sr_
    gen_is_x = random.SystemRandom().random() < 0.5
    X, Y = (dg, dr) if gen_is_x else (dr, dg)
    prompt = f"""Two {genre.replace('_', ' ')} tracks as measured audio metrics (LUFS, peaks,
band balance %, stereo width, loudness/centroid trajectories by quarter-note, and CLAP
audio-embedding similarity to the genre). ONE is a professionally released real record;
the other was generated by a DAW agent. Decide which is the REAL released record.
TRACK X: {json.dumps(X)}
TRACK Y: {json.dumps(Y)}
Reply STRICT JSON only: {{"real": "X"|"Y", "confidence": 1-5, "tells": ["...", "..."]}}"""
    p = subprocess.run(["claude", "-p", prompt, "--model", "claude-haiku-4-5-20251001",
                        "--output-format", "json"],
                       capture_output=True, text=True, timeout=180, cwd=ROOT)
    verdict = None
    try:
        outer = json.loads(p.stdout)
        m = re.search(r"\{.*\}", outer.get("result", ""), re.S)
        verdict = json.loads(m.group(0)) if m else None
    except Exception:
        pass
    if not verdict or verdict.get("real") not in ("X", "Y"):
        return {"judge_fooled": None, "verdict": verdict, "gen_was": "X" if gen_is_x else "Y"}
    picked_gen = (verdict["real"] == "X") == gen_is_x
    return {"judge_fooled": bool(picked_gen), "verdict": verdict,
            "gen_was": "X" if gen_is_x else "Y", "ref": os.path.basename(ref_path)}

def ab_score(target, genre, blind=True, log=True):
    """Score a song name OR a wav path against the genre's real-record cloud."""
    if target.endswith(".wav"):
        wav, name = target, os.path.basename(target)[:-4]
    else:
        name = target
        sj, wav = os.path.join(SONGS, f"{name}.json"), os.path.join(SONGS, f"{name}.wav")
        if not os.path.exists(wav) or (os.path.exists(sj)
                                       and os.path.getmtime(wav) < os.path.getmtime(sj)):
            subprocess.run([M1, "render", sj, wav], capture_output=True, timeout=300)
    fam, refs = _ab_refs_for(genre)
    if len(refs) < 3:
        return {"error": f"family {fam} has {len(refs)} refs on disk (<3)"}
    py = VENV_PY if os.path.exists(VENV_PY) else "python3"
    p = subprocess.run([py, os.path.join(ROOT, "tools", "clap_query.py"),
                        "--ab", wav, "--refs", *refs],
                       capture_output=True, text=True, timeout=900)
    d = json.loads(p.stdout or '{"available":false,"reason":"empty"}')
    if not d.get("available"):
        return {"error": f"clap ab unavailable: {d.get('reason')}"}
    base_mean = sum(d["baseline"]) / len(d["baseline"])
    row = {"kind": "ab", "song": name, "genre": genre, "ref_family": fam,
           "refs": [os.path.basename(r) for r in d["refs"]],
           "gen_insiderness": d["gen_insiderness"], "baseline": d["baseline"],
           # the CEILING: midrank percentile inside the real-record cloud —
           # 0 until a render is literally record-coherent (unsaturable)
           "ab_cosine_pct": _pctile(d["gen_insiderness"], d["baseline"]),
           # the TEACHER: % of the records' own mutual coherence achieved —
           # continuous, ordered, uncapped (100 = as inside as the records are)
           "ab_closeness": round(100.0 * d["gen_insiderness"] / base_mean, 1),
           "t": time.time()}
    # the COMPLEMENTARY axis (measured boundary above): genre-truth beside
    # record-coherence — never read either alone.
    gs = clap_genre_sims([wav], genre)[0]
    if gs is not None:
        row["clap_genre_sim"] = gs
    if blind:
        import random
        row.update(judge_blind(wav, random.SystemRandom().choice(refs), genre))
    if log:
        os.makedirs(os.path.join(ROOT, "eval"), exist_ok=True)
        with open(os.path.join(ROOT, "eval", "history.jsonl"), "a") as f:
            f.write(json.dumps(row) + "\n")
    return row

def song_digest(name):
    """Compact structural+metric digest for the judge (symbolic + measured — no audio)."""
    sj = os.path.join(SONGS, f"{name}.json")
    song = json.load(open(sj))
    py = VENV_PY if os.path.exists(VENV_PY) else "python3"
    wav = os.path.join(SONGS, f"{name}.wav")
    a = json.loads(subprocess.run([py, os.path.join(ROOT, "tools", "analyze2.py"), wav],
                                  capture_output=True, text=True, timeout=180).stdout)
    tracks = []
    for t in song.get("tracks", []):
        notes = t.get("notes", [])
        tracks.append({"name": t["name"], "source": t.get("source", {}).get("kind"),
                       "notes": len(notes),
                       "density_per_bar": round(len(notes) / max(1.0, float(song.get("lengthBars", 1))), 1),
                       "pitch_span": (max((n["pitch"] for n in notes), default=0)
                                      - min((n["pitch"] for n in notes), default=0)),
                       "fx": [f.get("id") or f.get("type", "?") for f in t.get("fx", [])],
                       "automation": [x["target"] for x in t.get("automation", [])],
                       "sends": [s_["bus"] for s_ in t.get("sends", [])]})
    return {"bpm": song.get("bpm"), "key": song.get("key"), "bars": song.get("lengthBars"),
            "swing": song.get("swing", {}).get("amount", 0.5), "buses": [b["id"] for b in song.get("buses", [])],
            "tracks": tracks,
            "measured": {"lufs": a["lufs_integrated"], "peak": a["peak_dbfs"], "dbtp": a["true_peak_dbtp"],
                         "clipped": a["clipped_samples"], "bands": a["band_energy_pct"],
                         "width_db": a["stereo_width_db"], "rms_by_quarter": a["rms_by_quarter_db"],
                         "centroid_by_quarter": a["centroid_by_quarter_hz"]}}

def clap_genre_sims(wavs, genre):
    """CLAP text<->audio cosine per wav vs '<genre> music' (C5 step 5) — the one
    signal here measured from the RENDER'S SOUND itself, not the arrangement.
    [None]*N on any unavailability (no torch/CLAP box) — the judge goes without."""
    py = VENV_PY if os.path.exists(VENV_PY) else "python3"
    try:
        p = subprocess.run([py, os.path.join(ROOT, "tools", "clap_query.py"),
                            "--sim", f"{genre.replace('_', ' ')} music", "--audio", *wavs],
                           capture_output=True, text=True, timeout=300)
        d = json.loads(p.stdout)
        if not d.get("available"):
            return [None] * len(wavs)
        return [r["score"] for r in d["similarities"]]      # input order
    except Exception:
        return [None] * len(wavs)

# W75 (r-19 item 140): the six-dimension SYMBOLIC rubric — grounded in
# the human-validated SongEval/MusicEval/MAD axes; chain-of-thought
# BEFORE scores; strict JSON.
RUBRIC_DIMENSIONS = (
    ("structure", "Structural coherence: sections, transitions, arc"),
    ("hook", "Memorability: motif repetition WITH variation"),
    ("harmony_melody", "Harmonic-melodic musicality: key adherence, "
                       "voice-leading, tension/release from chords[]"),
    ("groove", "Groove/pocket: timing, swing, stability"),
    ("production", "Production/mix: band balance, LUFS window, PSR/LRA "
                   "(from the measured digest, never guessed)"),
    ("genre_fit", "Genre adherence vs the KG target + idiom"),
)


def _rubric_prompt(song_a, song_b, da, db, genre, sim_note=""):
    dims = "\n".join(f"  {k}: {d}" for k, d in RUBRIC_DIMENSIONS)
    return f"""You are a {genre} production judge. Two arrangements below as structural digests
(track list, densities, fx, automation, sends) + measured audio metrics + MUSIC COURT facts
(in_key_pct = melodic key conformance measured from the notes; pocket_ok = cross-track timing
coherence; arc_flags = narrative failures).{sim_note}
Score BOTH songs on the six dimensions (1-5 each):
{dims}
First reason step by step about each dimension (chain of thought), THEN output the scores.
SONG A ({song_a}): {json.dumps(da)}
SONG B ({song_b}): {json.dumps(db)}
End with STRICT JSON only on the final line:
{{"winner": "A"|"B", "margin": 1-5, "scores": {{"A": {{"structure": n, "hook": n, "harmony_melody": n, "groove": n, "production": n, "genre_fit": n}}, "B": {{...}}}}, "reasons": ["...", "...", "..."]}}"""


def judge_consistent(song_a, song_b, genre, _judge=None):
    """W75 position-bias guard: run BOTH orders; keep the verdict only
    when the winners AGREE (a judge that flips with order has no
    verdict). Returns {consistent, winner|None, rows}."""
    j = _judge or judge
    r1 = j(song_a, song_b, genre)
    r2 = j(song_b, song_a, genre)
    v1 = (r1.get("verdict") or {}).get("winner")
    v2 = (r2.get("verdict") or {}).get("winner")
    # r2's A is song_b — map back
    w1 = {"A": song_a, "B": song_b}.get(v1)
    w2 = {"A": song_b, "B": song_a}.get(v2)
    consistent = w1 is not None and w1 == w2
    return {"consistent": consistent,
            "winner": w1 if consistent else None,
            "rows": [r1, r2],
            "why": ("both orders agree" if consistent else
                    f"order flip ({w1} vs {w2}) — no verdict; a "
                    "position-biased pick is not a pick")}


def gold_exemplar_path(genre):
    """The genre's library/gold exemplar (parent-chain fallback rides
    the bank's own naming)."""
    g = str(genre or "").lower().replace("-", "_").replace(" ", "_")
    p = os.path.join(ROOT, "library", "gold", f"{g}.json")
    return p if os.path.exists(p) else None


def judge(song_a, song_b, genre):
    """LLM judge over structure+metrics (NOT raw audio — an ears-adjacent structural
    critic; clap_genre_sim is its one true-audio signal). Cheap (haiku). Appends
    verdict to history."""
    da, db = song_digest(song_a), song_digest(song_b)
    # P19 v2: the courts' MEASURED music facts ride the digests — a judge
    # with deterministic key/pocket/arc evidence beats one guessing from
    # track names (docs/SPEC_PRODUCER_MIND.md).
    try:
        import music_court as _mc
        import arc_court as _ac
        for nm, d in ((song_a, da), (song_b, db)):
            sng = json.load(open(os.path.join(SONGS, f"{nm}.json")))
            kv = _mc.court_key(sng, genre)
            d["measured"]["in_key_pct"] = kv.get("in_key_pct")
            d["measured"]["pocket_ok"] = _mc.court_pocket(sng, genre).get("ok")
            d["measured"]["arc_flags"] = [
                f.get("kind") for f in _ac.court_arc(sng, genre).get("flags", [])]
    except Exception:
        pass
    sim_a, sim_b = clap_genre_sims([os.path.join(SONGS, f"{n}.wav")
                                    for n in (song_a, song_b)], genre)
    if sim_a is not None:
        da["measured"]["clap_genre_sim"] = sim_a
    if sim_b is not None:
        db["measured"]["clap_genre_sim"] = sim_b
    sim_note = ("\nclap_genre_sim = audio-embedding similarity between the actual render and "
                f"the text '{genre.replace('_', ' ')} music' (higher = sounds more like the "
                "genre; the only field measured from the audio itself)."
                if sim_a is not None or sim_b is not None else "")
    prompt = _rubric_prompt(song_a, song_b, da, db, genre, sim_note)
    p = subprocess.run(["claude", "-p", prompt, "--model", "claude-haiku-4-5-20251001",
                        "--output-format", "json"],
                       capture_output=True, text=True, timeout=180, cwd=ROOT)
    verdict = None
    try:
        outer = json.loads(p.stdout)
        m = re.search(r"\{.*\}", outer.get("result", ""), re.S)
        verdict = json.loads(m.group(0)) if m else None
    except Exception:
        pass
    row = {"kind": "judge", "genre": genre, "a": song_a, "b": song_b,
           "verdict": verdict, "clap_genre_sim": {"a": sim_a, "b": sim_b},
           "t": time.time()}
    os.makedirs(os.path.join(ROOT, "eval"), exist_ok=True)
    with open(os.path.join(ROOT, "eval", "history.jsonl"), "a") as f:
        f.write(json.dumps(row) + "\n")
    return row

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--brief", help="genre: run the real agent on its brief")
    ap.add_argument("--model", default="claude-opus-4-8",
                    help="composer model for --brief (small-model proofs of the gold bank)")
    ap.add_argument("--check", help="song name to machine-check")
    ap.add_argument("--genre", help="genre for --check/--judge (default: derived from "
                                    "the song name, eval_<genre> -> <genre>; errors if underivable "
                                    "- the old silent default of 'trap' judged songs against the "
                                    "wrong law)", default=None)
    ap.add_argument("--judge-consistent", nargs=2,
                    metavar=("SONG_A", "SONG_B"),
                    help="W75: pairwise judge BOTH orders; verdict only "
                         "on agreement (position-bias guard)")
    ap.add_argument("--judge", nargs=2, metavar=("SONG_A", "SONG_B"),
                    help="LLM-judge two songs (structure+metrics)")
    ap.add_argument("--ab", help="R3 ruler: song name or wav path scored vs the "
                                 "genre's REAL-RECORD cloud (+ blind judge)")
    ap.add_argument("--no-blind", action="store_true",
                    help="--ab without the blind-judge LLM call")
    ap.add_argument("--no-log", action="store_true",
                    help="--ab without appending to eval/history.jsonl "
                         "(validation/degradation experiments)")
    ap.add_argument("--suite", action="store_true")
    a = ap.parse_args()
    if a.brief:
        print(json.dumps(run_brief(a.brief, model=a.model), indent=1))
    elif a.check:
        g = a.genre
        if not g:                       # derive: eval_<genre> or exact genre-named song
            cand = a.check[5:] if a.check.startswith("eval_") else a.check
            from kg import KG
            if KG().q(f"MATCH (g:Genre {{name: '{cand}'}}) RETURN g.name"):
                g = cand
            else:
                raise SystemExit(f"cannot derive genre from '{a.check}' - pass --genre "
                                 f"explicitly (refusing the old silent 'trap' default)")
        print(json.dumps(check_song(a.check, g), indent=1))
    elif a.judge:
        if not a.genre:
            raise SystemExit("--judge requires --genre (no silent default)")
    if getattr(args, "judge_consistent", None):
        if not args.genre:
            raise SystemExit("--judge-consistent requires --genre")
        out = judge_consistent(args.judge_consistent[0],
                               args.judge_consistent[1], args.genre)
        print(json.dumps({k: out[k] for k in
                          ("consistent", "winner", "why")}, indent=1))
        raise SystemExit(0)
        print(json.dumps(judge(a.judge[0], a.judge[1], a.genre), indent=1))
    elif a.ab:
        g = a.genre
        if not g:
            cand = os.path.basename(a.ab)
            cand = cand[:-4] if cand.endswith(".wav") else cand
            g = cand[5:] if cand.startswith("eval_") else None
            if not g:
                raise SystemExit("--ab needs --genre (or an eval_<genre> name)")
        print(json.dumps(ab_score(a.ab, g, blind=not a.no_blind,
                                  log=not a.no_log), indent=1))
    elif a.suite:
        for g in BRIEFS:
            if os.path.exists(os.path.join(SONGS, f"eval_{g}.json")):
                r = check_song(f"eval_{g}", g)
                print(g, r["score"], r["checks"])
