#!/usr/bin/env python3
"""THE OTHER RAIL battery — the harmonic bucket's decomposition laws.

Guards the 2026-07-15 goldenbrown autopsy fixes as MACHINE LAW:
  1. THE STREAM SPLIT (note_streams): partition, honesty gates, determinism
  2. THE MICROSCOPE GATE (_assist_ok): default-on with CUDA, env doors
  3. THE FAMILY (_other_family): every lane the chord prior / level law owns
  4. THE COURT knows the stream lanes (MELODIC_SUFFIX covers _lead/_pad/_chords)
  5. THE LEVEL LAW knows them (a2m_correct GROUPS)
  6. THE DEEP LISTEN is wired (starved first pass -> lower-threshold relisten)
  7. THE DRY-TWIN gate stays wired for any future cleaner use
     (full gate proofs live in mel_clean_battery)

Pure + offline (no torch, no model files, no GPU): a default suite leg.

    python3 tools/other_rail_battery.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

PASS = 0
FAIL = 0


def check(name, ok, detail=""):
    global PASS, FAIL
    if ok:
        PASS += 1
        print(f"  ok  {name}")
    else:
        FAIL += 1
        print(f"FAIL  {name}  {detail}")


def main():
    # ---------------------------------------------- 1. THE STREAM SPLIT
    import note_streams as ns
    rc = ns._selftest()
    check("note_streams selftest green", rc == 0)

    # ---------------------------------------------- 2. THE MICROSCOPE GATE
    import stems_import as si
    env0 = {k: os.environ.pop(k, None) for k in ("SOTADAW_6S", "SOTADAW_NO_6S")}
    try:
        check("microscope default-on with CUDA", si._assist_ok("cuda") is True)
        check("microscope off on CPU (slow-rung law)",
              si._assist_ok("cpu") is False)
        os.environ["SOTADAW_6S"] = "1"
        check("SOTADAW_6S=1 forces on CPU", si._assist_ok("cpu") is True)
        os.environ["SOTADAW_NO_6S"] = "1"
        check("SOTADAW_NO_6S=1 kills even forced",
              si._assist_ok("cuda") is False)
    finally:
        for k, v in env0.items():
            os.environ.pop(k, None)
            if v is not None:
                os.environ[k] = v

    # ---------------------------------------------- 3. THE FAMILY
    yes = ("other_sketch", "guitar_sketch", "piano_sketch", "keys_sketch",
           "other_lead", "guitar_pad", "piano_chords", "keys_lead")
    no = ("bass_sketch", "vocals_sketch", "drums_sketch", "Kick",
          "other", "guitar", "vocals_sung", "other_identity")
    check("family: every decomposition lane owned",
          all(si._other_family(n) for n in yes))
    check("family: nothing else claimed",
          not any(si._other_family(n) for n in no))

    # ---------------------------------------------- 4. THE COURT
    import import_court as ic
    check("court suffix covers stream lanes",
          all(x.endswith(ic.MELODIC_SUFFIX)
              for x in ("a_sketch", "a_lead", "a_pad", "a_chords")))
    song = {"key": "C major", "bpm": 120.0, "tracks": [{
        "name": "guitar_lead", "source": {"kind": "sample", "kit": "x"},
        "notes": ([{"start": float(i), "len": 0.5, "pitch": 60 + (i % 5) * 2,
                    "vel": 0.8} for i in range(24)]
                  + [{"start": 30.0, "len": 0.5, "pitch": 61, "vel": 0.8}])}]}
    docket = ic.hold_court(song, courts=("key",))
    check("court judges a _lead lane (isolated off-key snapped)",
          any(r.get("lane") == "guitar_lead" and r.get("action") == "snapped"
              for r in docket), f"{docket}")

    # ---------------------------------------------- 4b. THE LENGTH COURT
    pile = [{"start": 0.0 + i * 0.01, "len": 8.0, "pitch": 50 + i,
             "vel": 0.8} for i in range(20)]
    pile.append({"start": 4.0, "len": 0.5, "pitch": 72, "vel": 0.9})
    out, rr = ic.court_length(pile, lane="x_sketch")

    def _census(nsx, t):
        return sum(1 for n in nsx
                   if n["start"] <= t < n["start"] + n["len"])
    check("length census trims a 20-deep pileup (receipted)",
          rr and rr[0]["action"] == "trimmed"
          and _census(out, 0.2) <= 7 and _census(out, 4.0) <= 7)
    clean = [{"start": float(i), "len": 0.5, "pitch": 60, "vel": 0.8}
             for i in range(10)]
    out2, rr2 = ic.court_length(clean, lane="y_sketch")
    check("length census leaves a clean lane untouched (no receipts)",
          rr2 == [] and out2 == clean)
    tmp_song = {"key": "C major", "bpm": 120.0, "tracks": [{
        "name": "p_chords", "source": {"kind": "sample"},
        "notes": [{"start": 0.0 + i * 0.01, "len": 6.0, "pitch": 40 + i,
                   "vel": 0.8} for i in range(12)]}]}
    d8 = ic.hold_court(tmp_song, courts=("length",))
    check("chords ceiling is 8 (12-deep trims, 8 survive)",
          d8 and _census(tmp_song["tracks"][0]["notes"], 0.15) <= 9)
    src_sk = open(os.path.join(ROOT, "tools", "source_kit.py")).read()
    check("sustain law poly branch is bounded (F1)",
          "ln * 1.5 + 0.35" in src_sk)
    check("articulation law: ring semantics own the length law",
          "THE ARTICULATION LAW" in src_sk
          and src_sk.count("open_ring = glide_t <") == 1
          and "if open_ring:\n            break" in src_sk)

    # ---------------------------------------------- 5. THE LEVEL LAW
    import ast
    src = open(os.path.join(ROOT, "tools", "a2m_correct.py")).read()
    tree = ast.parse(src)
    groups_names = None
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) \
                and any(getattr(t, "id", "") == "GROUPS" for t in node.targets):
            groups_names = ast.get_source_segment(src, node.value)
    check("a2m_correct GROUPS['other'] carries the stream lanes",
          groups_names is not None
          and "guitar_sketch" in groups_names
          and '"lead", "pad", "chords"' in groups_names, f"{groups_names!r:.120}")
    check("stage separation: correction renders are master-free",
          "THE STAGE SEPARATION LAW" in src
          and 'song["master"] = []' in src)

    # ---------------------------------------------- 6. THE DEEP LISTEN
    tsrc = open(os.path.join(ROOT, "tools", "transcribe_stems.py")).read()
    check("deep listen wired in other_notes",
          "THE DEEP LISTEN" in tsrc and "onset_threshold=0.28" in tsrc
          and "cov2 >= cov + 0.08" in tsrc)
    check("deep listen tags its engine", '"+deep"' in tsrc)

    # ---------------------------------------------- 6b. THE STREAM LANDING
    # (F2: true lengths first — pass-1 kit measures the ring, split on it,
    #  per-stream kits after; here source_kit is stubbed to fail so the
    #  fallback voice lands and the split logic itself is on trial)
    import types
    stub = types.ModuleType("source_kit")

    def _no_kit(*a, **k):
        raise RuntimeError("stubbed")
    stub.build_pitched_kit = _no_kit
    real_sk = sys.modules.get("source_kit")
    sys.modules["source_kit"] = stub
    try:
        big = ([{"start": b * 4.0, "len": 1.0, "pitch": p, "vel": 0.8}
                for b in range(40) for p in (48, 52, 55)]
               + [{"start": b * 2.0 + 1.0, "len": 2.0, "pitch": 67,
                   "vel": 0.5} for b in range(60)]
               + [{"start": kx * 0.5 + 0.25, "len": 0.25,
                   "pitch": 60 + (kx % 5), "vel": 0.9} for kx in range(200)])
        lanes = si.melodic_lanes("guitar", "/nonexistent.wav", big,
                                 {"kind": "faust", "id": "pluck"},
                                 "_batt", 120.0)
        names = [t["name"] for t in lanes]
        check("melodic_lanes splits a decisive part into voice lanes",
              set(names) == {"guitar_chords", "guitar_pad", "guitar_lead"},
              f"{names}")
        check("split lanes conserve the notes",
              sum(len(t["notes"]) for t in lanes) == len(big))
        mono = [{"start": float(i), "len": 0.4, "pitch": 60, "vel": 0.8}
                for i in range(50)]
        lanes2 = si.melodic_lanes("other", "/nonexistent.wav", mono,
                                  {"kind": "sample", "kit": "piano"},
                                  "_batt", 120.0)
        check("indecisive part stays one sketch lane",
              [t["name"] for t in lanes2] == ["other_sketch"])
    finally:
        if real_sk is not None:
            sys.modules["source_kit"] = real_sk
        else:
            sys.modules.pop("source_kit", None)

    # ---------------------------------------------- 6c. THE MASTER MATCH
    import numpy as np
    import master_match as mmx
    rng = np.random.RandomState(7)
    wide = rng.randn(44100, 2) * 0.1
    m1x = mmx.measure(wide, 44100)
    narrow = np.repeat(rng.randn(44100, 1) * 0.1, 2, axis=1)
    m2x = mmx.measure(narrow, 44100)
    check("measure: decorrelated noise reads wider than mono",
          m1x["width_db"] > m2x["width_db"] + 20)
    check("measure: bands are shape-only (mean 0)",
          abs(sum(m1x["bands"])) < 0.5)
    msrc2 = open(os.path.join(ROOT, "tools", "master_match.py")).read()
    check("master chain: match EQ first, the wall LAST",
          msrc2.find('"fx_match_eq"') < msrc2.find('"fx_truepeak"')
          and '"ceiling": c["ceiling"]' in msrc2)
    check("master chain pins masterGainDb 0",
          'song["masterGainDb"] = 0.0' in msrc2)
    dsp = os.path.join(ROOT, "instruments", "fx_match_eq.dsp")
    check("fx_match_eq.dsp exists with the 8 ruler bells",
          os.path.exists(dsp) and all(
              f'"g{c}"' in open(dsp).read()
              for c in (85, 171, 344, 691, 1389, 2790, 5609, 11272)))

    # ---------------------------------------------- 6d. THE IMPORT BUDGET
    ssrc4 = open(os.path.join(ROOT, "tools", "stems_import.py")).read()
    check("stage receipts wired (import_stages.json)",
          "import_stages.json" in ssrc4 and "[stage] ledger" in ssrc4)
    check("drum microscope defers to the finisher",
          "SOTADAW_IMPORT_INLINE" in ssrc4 and "drum_land.json" in ssrc4
          and "import_finisher.py" in ssrc4)
    check("master match is the import finale",
          "SOTADAW_NO_MASTERMATCH" in ssrc4
          and "SOTADAW_IMPORT_BUDGET_S" in ssrc4)
    fsrc = open(os.path.join(ROOT, "tools", "import_finisher.py")).read()
    check("finisher carries the stomp guard + quality invariant",
          "STOMP GUARD" in fsrc and "land_drum_lanes" in fsrc)
    import json
    os.environ["SOTADAW_NO_DRUMSEP"] = "1"
    os.environ["SOTADAW_FIN_WAIT_S"] = "0"     # no RAM polling in a battery
    nm = "_batt_finisher"
    paths2 = (os.path.join(ROOT, "songs", f"{nm}.json"),
              os.path.join(ROOT, "songs", f"{nm}_stems"))
    try:
        import import_finisher as fin
        os.makedirs(paths2[1], exist_ok=True)
        json.dump({"bpm": 120, "tracks": []}, open(paths2[0], "w"))
        open(os.path.join(paths2[1], "drums.wav"), "wb").write(b"RIFF")
        rc2 = fin.upgrade_drums(nm)
        check("finisher honest exit when drumsep unavailable", rc2 == 0)
    finally:
        del os.environ["SOTADAW_NO_DRUMSEP"]
        del os.environ["SOTADAW_FIN_WAIT_S"]
        import shutil as sh2
        if os.path.exists(paths2[0]):
            os.remove(paths2[0])
        sh2.rmtree(paths2[1], ignore_errors=True)

    # ------------------------------------- 6e. THE PRODUCTION-GAP KERNELS
    # (2026-07-16 autopsy: other_sketch -18dB per-note, ~20ms early starts,
    #  digital-mono drums, Perc env-corr 0.195 = noise wearing a name)
    asrc = open(os.path.join(ROOT, "tools", "a2m_correct.py")).read()
    check("THE MELODIC EAR wired (real-render per-note truth)",
          "THE MELODIC EAR" in asrc and "_find_attack" in asrc
          and "_pitch_band" in asrc)
    check("melodic ear: lane-median error lands in gainDb, residual in vel",
          "med_db = med * VEL_DB_PER_UNIT" in asrc
          and "dv - med" in asrc)
    check("melodic ear: LEVEL ruler is band RMS, never attack peak",
          "math.log10(rms_s / rms_p)" in asrc
          and "attack-peak level-matching" in asrc)
    check("melodic ear: transient gate guards the re-anchor (crest ~10dB)",
          "pk_s > rms_s * 3.2" in asrc and "THE TRANSIENT GATE" in asrc)
    check("melodic ear: timing evidence gate (attack >= half own peak)",
          ">= 0.5 * pk_s" in asrc and "MELODIC_REACH_S = 0.050" in asrc)
    check("THE IMAGE LAW wired (stem balance -> lane pan, closed loop)",
          "THE IMAGE LAW" in asrc and "def band_balance" in asrc
          and "0.35 * (b_s - b_p)" in asrc)
    check("image law: bass exempt + pan clamped",
          '"bass") or t.get("muted")' in asrc.replace("(None, ", "")
          and "min(0.85" in asrc)
    check("image law: LANE_BAND_HZ hi==0 means to-Nyquist (Hats/Cymbals)",
          "hi = 20000.0" in asrc and '"to Nyquist"' in asrc)
    check("THE CREDIBILITY COURT convicts only with evidence",
          "THE CREDIBILITY COURT" in asrc and "c < 0.25" in asrc
          and 'len(t.get("notes", [])) < 8' in asrc and "m < 400" in asrc)
    check("THE GHOST CULL: fantasy notes die, bounded + ruler-distrust guard",
          "THE GHOST CULL" in asrc and "pk_s < 2e-5 and pk_p > 1e-3" in asrc
          and asrc.count('trust * len(t["notes"])') == 2)
    check("THE COHERENCE GATE: incoherent per-note level never rules",
          "THE COHERENCE GATE" in asrc and "mad_db0 > 3.5" in asrc)
    check("render-stems retries once under box contention",
          "one retry" in asrc.lower())
    check("THE DOUBLING GUARD: a sounding real take skips the ear",
          "THE DOUBLING GUARD" in asrc
          and 'split("_")[0] == fam0' in asrc
          and '"_stems/" not in' in asrc)
    # band_balance functional truth: a left-panned tone reads negative
    try:
        import numpy as _np
        import soundfile as _sf
        import a2m_correct as _ac
        _t = _np.arange(0, 44100) / 44100.0
        _tone = _np.sin(2 * _np.pi * 440 * _t).astype("float32")
        _f = 4410                          # 100ms fades: an abrupt edge is a
        _tone[:_f] *= _np.linspace(0, 1, _f, dtype="float32")   # broadband
        _tone[-_f:] *= _np.linspace(1, 0, _f, dtype="float32")  # click that
        _st = _np.stack([_tone, 0.1 * _tone], 1)   # rings ANY band (physics)
        _tmpb = os.path.join(ROOT, "songs", "_batt_balance.wav")
        _sf.write(_tmpb, _st, 44100)
        _b = _ac.band_balance(_tmpb, 200.0, 2000.0)
        check("band_balance reads a left image negative",
              _b is not None and _b < -0.8)
        _b2 = _ac.band_balance(_tmpb, 8000.0, 12000.0)
        check("band_balance refuses an empty band", _b2 is None)
    finally:
        if os.path.exists(_tmpb):
            os.remove(_tmpb)

    # ---------------------------------------------- 7. THE DRY-TWIN GATE
    msrc = open(os.path.join(ROOT, "tools", "mel_clean.py")).read()
    check("mel_clean carries the health gate",
          "def dry_twin_health" in msrc and "HEALTH_MIN_RETENTION_DB" in msrc)
    ssrc = open(os.path.join(ROOT, "tools", "stems_import.py")).read()
    check("other rail transcribes WET by default (verified negative)",
          'os.environ.get("SOTADAW_DRYCLEAN_OTHER") == "1"' in ssrc)
    check("decomposition law wired (dead residual -> no duplicate lane)",
          "skip_other = True" in ssrc)
    check("stream landing wired (land_melodic)",
          "def land_melodic" in ssrc and "note_streams" in ssrc)

    # ------------------------------------- 8. THE LANE LATENCY LAW (F6)
    import a2m_correct as _ac2
    src_ac = open(os.path.join(ROOT, "tools", "a2m_correct.py")).read()
    check("latency law rides the ENERGY ruler (regression court 07-17)",
          "lat_ms = lane_env_lag(env_s, env_p)" in src_ac
          and "def lane_env_lag" in src_ac)
    check("foot docket retired with the court's reason on record",
          "retired ruler" in src_ac and "aligning FEET misaligns" in src_ac)
    check("latency shift skips individually anchored notes",
          "if id(q) not in anchored" in src_ac)
    check("SILENCE COURT: relative floor vs the lane's own body",
          'np.percentile([m[1] for m in meas], 90)' in src_ac
          and "10.0 ** (-40.0 / 20.0)" in src_ac
          and "floor > 2e-5" in src_ac)
    check("SILENCE COURT rides the same trust bound",
          src_ac.index("ghosts.extend(rel)")
          < src_ac.index("if ghosts and len(ghosts) <= trust"))
    check("trust bound is coherence-earned (20% base, 35% coherent ruler)",
          "trust = 0.20" in src_ac and "trust = 0.35" in src_ac
          and src_ac.index("trust = 0.20") < src_ac.index("trust = 0.35")
          and "* VEL_DB_PER_UNIT <= 3.5" in src_ac)
    _rng2 = np.random.default_rng(5)
    _es = np.abs(_rng2.standard_normal(3000)).cumsum() % 7 \
        + _rng2.standard_normal(3000) * 0.1
    _late = np.concatenate([np.zeros(3), _es[:-3]])   # product 30ms LATE
    _early = np.concatenate([_es[4:], np.zeros(4)])   # product 40ms EARLY
    check("energy ruler: a LATE lane earns an earlier (negative) shift",
          _ac2.lane_env_lag(_es, _late) == -30.0,
          f"got {_ac2.lane_env_lag(_es, _late)}")
    check("energy ruler: an EARLY lane earns a later (positive) shift",
          _ac2.lane_env_lag(_es, _early) == 40.0,
          f"got {_ac2.lane_env_lag(_es, _early)}")
    check("energy ruler: aligned and pure-noise lanes are refused",
          _ac2.lane_env_lag(_es, _es + _rng2.standard_normal(3000) * 0.05)
          == 0.0
          and _ac2.lane_env_lag(_es, _rng2.standard_normal(3000)) == 0.0)
    check("energy ruler: thin evidence is refused (<4s)",
          _ac2.lane_env_lag(_es[:300], _late[:300]) == 0.0)

    # ------------------------------------- 9. THE STEREO REPLICA (F6)
    import math
    import tempfile
    check("median vote is channel-shaped (stereo rows)",
          "rows[0].shape[1:]" in src_sk
          and "sos[1](sos[0], s, axis=0)" in src_sk)
    check("build_source_kit: decisions mono, waveforms stereo",
          "sr, xw = _load_wav(stem_wav)" in src_sk
          and "x = xw.mean(axis=1)" in src_sk)
    check("kit doc carries channel truth", '"channels": 2 if' in src_sk)
    check("identity verdict mid-izes stereo voices",
          "identity is a MID question" in src_sk)
    import source_kit as _sk
    _st = np.zeros((2000, 2))
    _st[:, 0] = 0.5
    _fin = _sk._finish_seg(_st.copy(), 44100)
    check("finish_seg fades stereo without collapsing channels",
          _fin.shape == (2000, 2) and float(_fin[0, 0]) == 0.0
          and abs(float(_fin[1000, 0]) - 0.5) < 1e-9)
    _td = _sk._tail_discipline(np.ones((int(0.6 * 44100), 2)), 44100, 42)
    check("tail discipline broadcasts over channels",
          _td.ndim == 2 and _td.shape[1] == 2
          and float(np.abs(_td[-1]).max()) < 0.01)
    # end-to-end: hard-left hat + centered kick through the real builder
    import shutil as _sh
    _sr = 44100
    _x2 = np.zeros((int(12.0 * _sr), 2))
    _rng = np.random.default_rng(3)
    _nts, _t, _k = [], 0.25, 0
    from scipy.signal import butter as _bu, sosfilt as _sf
    _hp = _bu(4, 6000 / (_sr / 2), "high", output="sos")
    while _t + 1.0 < 12.0:
        _i0 = int(_t * _sr)
        if _k % 2 == 0:
            _n = int(0.25 * _sr)
            _b = np.sin(2 * np.pi * 55 * np.arange(_n) / _sr) \
                * np.exp(-np.linspace(0, 9, _n)) * 0.8
            _x2[_i0:_i0 + _n, 0] += _b
            _x2[_i0:_i0 + _n, 1] += _b
            _nts.append({"pitch": 36, "start": _t * 2, "len": 0.4, "vel": 0.9})
        else:
            _n = int(0.05 * _sr)
            _b = _sf(_hp, _rng.standard_normal(_n)) \
                * np.exp(-np.linspace(0, 12, _n)) * 0.35
            _x2[_i0:_i0 + _n, 0] += _b * 0.95
            _x2[_i0:_i0 + _n, 1] += _b * 0.10
            _nts.append({"pitch": 42, "start": _t * 2, "len": 0.1, "vel": 0.8})
        _t += 0.5
        _k += 1
    _x2 += _rng.standard_normal(_x2.shape) * 0.003
    _stw = os.path.join(tempfile.gettempdir(), "_orb_f6_stem.wav")
    _sk._save_wav16(_stw, _x2 * 0.9, _sr)
    _kn = "_orb_f6_probe"
    _kd = os.path.join(ROOT, "kits", _kn)
    _sh.rmtree(_kd, ignore_errors=True)
    try:
        _out = _sk.build_source_kit(_stw, _nts, _kn, bpm=120.0)
        _doc = json.load(open(os.path.join(_kd, "kit.json")))
        import wave as _wv

        def _bal(fn):
            with _wv.open(os.path.join(_kd, fn)) as _w:
                _nc = _w.getnchannels()
                _raw = np.frombuffer(_w.readframes(_w.getnframes()),
                                     dtype=np.int16)
            _y = _raw.reshape(-1, _nc).astype(np.float64)
            if _nc < 2:
                return _nc, 0.0
            return _nc, 10 * math.log10(
                (float((_y[:, 0] ** 2).mean()) + 1e-9)
                / (float((_y[:, 1] ** 2).mean()) + 1e-9))
        _files = {s["file"]: s for s in _doc["samples"]}
        _kick = next((f for f in _files if f.startswith("kick")), None)
        _hat = next((f for f in _files if f.startswith("hat")), None)
        _kc, _kb = _bal(_kick) if _kick else (0, 0.0)
        _hc, _hb = _bal(_hat) if _hat else (0, 0.0)
        check("stereo probe: kit built 2-channel",
              _out == _kn and _doc.get("channels") == 2 and _kc == 2
              and _hc == 2, f"kick ch={_kc} hat ch={_hc}")
        check("stereo probe: centered kick stays centered",
              _kick is not None and abs(_kb) < 2.0, f"L/R {_kb:+.1f}dB")
        check("stereo probe: hard-left hat keeps its image",
              _hat is not None and _hb > 8.0, f"L/R {_hb:+.1f}dB")
    finally:
        _sh.rmtree(_kd, ignore_errors=True)
        if os.path.exists(_stw):
            os.remove(_stw)

    # ------------------------------- 10. THE LONG TAIL (F6 regression court)
    src_sk2 = open(os.path.join(ROOT, "tools", "source_kit.py")).read()
    check("long-tail voices escape the iso cap (extended slice)",
          "THE LONG TAIL" in src_sk2
          and "bud > max(0.05, iso) * 1.5" in src_sk2)
    check("wet-tail gate counts in-band re-attacks after the conform",
          "re-attacks in-band" in src_sk2
          and "db[i] - db[i - 3] > 6.0" in src_sk2)
    check("gate-fire path ring-loops instead of shipping a click",
          "_ring_extend(seg[:iso_n]" in src_sk2
          and "def _ring_extend" in src_sk2)
    _sosr = _bu(4, [4000 / (_sr / 2), 12000 / (_sr / 2)], "band",
                output="sos")
    _rngr = np.random.default_rng(4)
    _nh = int(0.22 * _sr)
    _head = _sf(_sosr, _rngr.standard_normal((_nh, 2)), axis=0) \
        * np.exp(-np.linspace(0, 1.4, _nh))[:, None] * 0.5
    _ring = _sk._ring_extend(_head.copy(), _sr, 1.4, 49)
    _midr = _ring.mean(axis=1)
    _hopr = _sr // 50
    _envr = np.sqrt((_midr[:len(_midr) // _hopr * _hopr]
                     .reshape(-1, _hopr) ** 2).mean(1))
    _dbr = 20 * np.log10(np.maximum(_envr / (_envr.max() + 1e-12), 1e-6))
    _risr = sum(1 for i in range(3, len(_dbr))
                if _dbr[i] - _dbr[i - 3] > 6 and _dbr[i] > -32)
    check("ring loop: 0.22s head becomes a >1.2s smooth ring",
          len(_ring) / _sr > 1.2 and _risr == 0,
          f"len {len(_ring)/_sr:.2f}s rises {_risr}")
    _sr = 44100
    _x3 = np.zeros((int(10.0 * _sr), 2))
    _n3 = []
    _hpc = _bu(4, [6000 / (_sr / 2), 12000 / (_sr / 2)], "band", output="sos")
    _rng3 = np.random.default_rng(9)
    # ONE crash at t=2.0 ringing 1.5s
    _nc = int(1.5 * _sr)
    _ring = _sf(_hpc, _rng3.standard_normal(_nc)) \
        * np.exp(-np.linspace(0, 6, _nc)) * 0.6
    _x3[int(2.0 * _sr):int(2.0 * _sr) + _nc, 0] += _ring
    _x3[int(2.0 * _sr):int(2.0 * _sr) + _nc, 1] += _ring * 0.9
    _n3.append({"pitch": 49, "start": 4.0, "len": 2.0, "vel": 0.95})
    # kicks on beats + hats every offbeat (they invade the crash window)
    _t = 0.25
    _k3 = 0
    _hp2 = _bu(4, 7000 / (_sr / 2), "high", output="sos")
    while _t + 0.5 < 10.0:
        _i0 = int(_t * _sr)
        if _k3 % 2 == 0:
            _n = int(0.22 * _sr)
            _b = np.sin(2 * np.pi * 55 * np.arange(_n) / _sr) \
                * np.exp(-np.linspace(0, 9, _n)) * 0.8
            _x3[_i0:_i0 + _n, 0] += _b
            _x3[_i0:_i0 + _n, 1] += _b
            _n3.append({"pitch": 36, "start": _t * 2, "len": 0.4,
                        "vel": 0.9})
        else:
            _n = int(0.04 * _sr)
            _b = _sf(_hp2, _rng3.standard_normal(_n)) \
                * np.exp(-np.linspace(0, 12, _n)) * 0.3
            _x3[_i0:_i0 + _n, 0] += _b
            _x3[_i0:_i0 + _n, 1] += _b
            _n3.append({"pitch": 42, "start": _t * 2, "len": 0.1,
                        "vel": 0.8})
        _t += 0.25
        _k3 += 1
    _x3 += _rng3.standard_normal(_x3.shape) * 0.002
    _stw3 = os.path.join(tempfile.gettempdir(), "_orb_f6_longtail.wav")
    _sk._save_wav16(_stw3, _x3 * 0.9, _sr)
    _kn3 = "_orb_f6_longtail"
    _kd3 = os.path.join(ROOT, "kits", _kn3)
    _sh.rmtree(_kd3, ignore_errors=True)
    try:
        _out3 = _sk.build_source_kit(_stw3, _n3, _kn3, bpm=120.0)
        _cw = os.path.join(_kd3, "crash.wav")
        _okc = _out3 == _kn3 and os.path.exists(_cw)
        _clen = 0.0
        _lowdb = -99.0
        if _okc:
            import wave as _wv2
            with _wv2.open(_cw) as _w:
                _nc2 = _w.getnchannels()
                _raw2 = np.frombuffer(_w.readframes(_w.getnframes()),
                                      dtype=np.int16)
            _y2 = _raw2.reshape(-1, _nc2).astype(np.float64) / 32767.0
            _clen = len(_y2) / _sr
            _mid2 = _y2.mean(axis=1)
            _tail2 = _mid2[int(0.25 * _sr):]
            if len(_tail2) > 1024:
                _lo2 = _sf(_bu(4, 1200 / (_sr / 2), "low", output="sos"),
                           _tail2)
                _lowdb = 20 * math.log10(
                    (float(np.abs(_lo2).max()) + 1e-9)
                    / (float(np.abs(_mid2).max()) + 1e-9))
        check("long-tail crash escapes the click (>=0.8s, was iso ~0.25s)",
              _okc and _clen >= 0.8, f"len {_clen:.2f}s")
        check("crash tail carries no foreign low bleed (<-26dB)",
              _okc and _lowdb < -26.0, f"low tail {_lowdb:.1f}dB")
    finally:
        _sh.rmtree(_kd3, ignore_errors=True)
        if os.path.exists(_stw3):
            os.remove(_stw3)

    print(f"\n{PASS}/{PASS + FAIL} checks passed")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
