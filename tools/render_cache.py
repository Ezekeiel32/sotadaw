#!/usr/bin/env python3
"""A6 — THE ECONOMY (docs/THE_PHYSICS.md §6; gap G8; law E11; rides E1 THE SEAL).

Content-addressed render cache: an unchanged take never pays for rendering twice.
Key = sha256( canonical-song-JSON x m1-binary-md5 x faust_gen-digest x
instruments/*.dsp-digest x referenced-audio-clip fingerprints x RENDER_EPOCH ).
The SEAL makes hits byte-provable: a cache copy hashes IDENTICAL to a fresh render.

Adoption is the sidecar donor's choice (spec: "wrapper API the sidecar can adopt");
the API is render_cached(song_path, out_wav) -> {"hit": bool, "sha256": ...}.

usage:
  render_cache.py render <song.json> <out.wav>     render through the cache
  render_cache.py stats | gc                       inspect / trim to budget
  render_cache.py --prove [--keep]                 10-take mock session (bar: >40% hits
                                                   + hit bytes == fresh-render bytes)
  render_cache.py --prove-stems [genre] [--keep]   W6 stem-identity + edit-win proof
                                                   (run under .venv: needs soundfile)
Budget: SOTADAW_RENDER_CACHE_GB (default 2.0 — D4 proposed value, pending Chezy).
Flags:  SOTADAW_STEM_CACHE=1 turns on the incremental STEM LAYER (per-track stems
        reused across takes; an edit re-renders only the tracks it touched).
        Assembled takes deep-null vs a fresh render (bar <= -60 dBFS peak) but are
        not byte-sealed — the classic rail stays the default.
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "songs")
M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")
CACHE = os.path.join(SONGS, ".render_cache")
GB = 2 ** 30

_DIGESTS = {}


def budget_bytes():
    """D4 — adaptive & disk-safe (Chezy: 'speed!'). Explicit SOTADAW_RENDER_CACHE_GB
    wins exactly. Otherwise: keep as much as speed wants but never crowd a tight
    disk — min(2 GB, 10% of CURRENT free space including what the cache already
    holds), floored at 256 MB, and 0 if the disk is critically full (<1 GB free)."""
    env = os.environ.get("SOTADAW_RENDER_CACHE_GB")
    if env:
        try:
            return int(float(env) * GB)
        except ValueError:
            pass
    try:
        free = shutil.disk_usage(SONGS).free
        held = _cache_bytes()                       # our own cache is reclaimable headroom
    except Exception:
        return 2 * GB
    if free + held < 1 * GB:                         # disk critically full -> no cache
        return 0
    return max(256 * 2 ** 20, min(2 * GB, int((free + held) * 0.10)))


def _file_sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _tree_digest(dirpath, exts):
    key = (dirpath, exts)
    if key in _DIGESTS:
        return _DIGESTS[key]
    h = hashlib.sha256()
    if os.path.isdir(dirpath):
        for f in sorted(os.listdir(dirpath)):
            if f.endswith(exts):
                p = os.path.join(dirpath, f)
                st = os.stat(p)
                h.update(f"{f}:{st.st_size}:{st.st_mtime_ns}".encode())
    _DIGESTS[key] = h.hexdigest()[:16]
    return _DIGESTS[key]


def _m1_md5():
    if "m1" not in _DIGESTS:
        _DIGESTS["m1"] = hashlib.md5(open(M1, "rb").read()).hexdigest()[:16]
    return _DIGESTS["m1"]


def _clip_fingerprints(song):
    fps = []
    for t in song.get("tracks", []):
        for c in t.get("audioClips", []) or []:
            p = c.get("file", "")
            if not os.path.isabs(p):
                p = os.path.join(SONGS, p)
            try:
                st = os.stat(p)
                fps.append(f"{p}:{st.st_size}:{st.st_mtime_ns}")
            except OSError:
                fps.append(f"{p}:MISSING")
    return "|".join(fps)


def _quarantine_digest():
    """Quarantined plugins render SILENT (engine skips them) — the same song
    JSON produces different audio across quarantine states, so the state must
    ride the key (found live: a stale-quarantine silent-pad wav kept HITting)."""
    try:
        raw = open(os.path.expanduser(
            "~/.config/sotadaw/plugin_quarantine.json"), "rb").read()
        return hashlib.sha256(raw).hexdigest()[:12]
    except Exception:
        return "none"


def cache_key(song_path):
    song = json.load(open(song_path))
    canonical = json.dumps(song, sort_keys=True, separators=(",", ":"))
    parts = "\x00".join([
        canonical,
        _m1_md5(),
        _tree_digest(os.path.join(ROOT, "app", "faust_gen"), (".hpp", ".h")),
        _tree_digest(os.path.join(ROOT, "instruments"), (".dsp",)),
        _clip_fingerprints(song),
        _quarantine_digest(),
        os.environ.get("SOTADAW_RENDER_EPOCH", "0"),
    ])
    return hashlib.sha256(parts.encode()).hexdigest()


def _meta_path(key):
    return os.path.join(CACHE, key + ".json")


def _wav_path(key):
    return os.path.join(CACHE, key + ".wav")


def _cache_bytes():
    if not os.path.isdir(CACHE):
        return 0
    return sum(os.path.getsize(os.path.join(CACHE, f))
               for f in os.listdir(CACHE) if f.endswith(".wav"))


def _lru_gc(budget=None):
    if budget is None:
        budget = budget_bytes()
    if not os.path.isdir(CACHE):
        return 0
    entries = []
    total = 0
    for f in os.listdir(CACHE):
        if f.endswith(".wav"):
            p = os.path.join(CACHE, f)
            m = _meta_path(f[:-4])
            last = 0.0
            try:
                last = json.load(open(m)).get("last_used", 0.0)
            except Exception:
                pass
            sz = os.path.getsize(p)
            total += sz
            entries.append((last, sz, p, m))
    entries.sort()
    evicted = 0
    while total > budget and entries:
        _, sz, p, m = entries.pop(0)
        for q in (p, m):
            if os.path.exists(q):
                os.remove(q)
        total -= sz
        evicted += 1
    return evicted


# THE WARM SERVER client (flag-gated: SOTADAW_RENDER_SERVE=1). ONE resident
# `m1 serve` keeps the engine alive; a cold render skips process spawn + engine
# init. Falls back to the classic subprocess on ANY trouble; determinism is
# sealed by tools/render_serve_battery.py (served sha == spawned sha) — the
# flag stays opt-in until callers choose the warm rail.
_SERVE = {"proc": None}


def _serve_render(song_path, out_wav, timeout=300):
    p = _SERVE.get("proc")
    if p is None or p.poll() is not None:
        try:
            p = subprocess.Popen([M1, "serve"], stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE, text=True, bufsize=1)
            t0 = time.time()
            while time.time() - t0 < 30:
                ln = p.stdout.readline()
                if not ln:
                    return None
                if "serve ready" in ln:
                    break
            else:
                return None
            _SERVE["proc"] = p
        except Exception:
            return None
    try:
        p.stdin.write(json.dumps({"song": os.path.abspath(song_path),
                                  "out": os.path.abspath(out_wav)}) + "\n")
        p.stdin.flush()
        t0 = time.time()
        while time.time() - t0 < timeout:
            ln = p.stdout.readline()
            if not ln:                       # the server died mid-request
                _SERVE["proc"] = None
                return None
            if ln.startswith('{"ok"'):
                try:
                    return json.loads(ln)
                except json.JSONDecodeError:
                    return None
        _SERVE["proc"] = None                # hung: abandon the resident
        try:
            p.kill()
        except Exception:
            pass
        return None
    except Exception:
        _SERVE["proc"] = None
        return None


def serve_stop():
    p = _SERVE.get("proc")
    if p is not None:
        try:
            p.stdin.write("quit\n")
            p.stdin.flush()
            p.wait(timeout=5)
        except Exception:
            try:
                p.kill()
            except Exception:
                pass
        _SERVE["proc"] = None


def _do_render(song_path, out_wav):
    """One render — serve rail when enabled, subprocess fallback.
    Returns (sha_hex, None) or (None, error_text)."""
    if os.environ.get("SOTADAW_RENDER_SERVE") == "1":
        rep = _serve_render(song_path, out_wav)
        if rep is not None and rep.get("ok") == 1 and os.path.exists(out_wav):
            return rep.get("sha") or _file_sha(out_wav), None
        # any trouble -> the classic rail below
    r = subprocess.run([M1, "render", song_path, out_wav], capture_output=True,
                       text=True, timeout=1200)
    out = r.stdout + r.stderr
    if "ok=1" not in out:
        return None, out[-300:]
    m = re.search(r"render_sha256=([0-9a-f]{64})", out)
    return (m.group(1) if m else _file_sha(out_wav)), None


# ---------------------------------------------------------------------------
# THE STEM LAYER (W6 — the edit-audition lever). Flag: SOTADAW_STEM_CACHE=1.
#
# Identity (machine-proven by --prove-stems): when every BUS carries only
# linear fx, sum(per-track solo renders, master stripped) == the pre-master
# mix, so the master chain applied ONCE to that float32 sum deep-nulls
# against the full render. Per-track fx (saturators, vst3, anything) are
# exempt from the linearity requirement — a track hears its own signal
# identically solo or in the mix; bus fx must distribute over the sum
# (reverb/delay/filter/trim are LTI; widen/pump are deterministic-phase LTV,
# gain modulation distributes). Master fx are NONLINEAR and welcome: they run
# once, on the sum, exactly like the live graph. Editing ONE track of N then
# costs 1 stem render + a cheap master pass instead of every voice, and
# unchanged stems are shared across takes (a proposal revision typically
# touches 1-2 tracks).
#
# HONESTY: assembled output deep-nulls (bar <= -60 dBFS peak residual) but is
# NOT byte-identical to a fresh full render (float sum order + 24-bit stem
# quantization), so the meta carries "assembled": true and the flag keeps the
# rail opt-in. The float32 sum wav is deliberate: a pre-master mix can peak
# past 0 dBFS and PCM would clip it before the wall ever saw it.
_LINEAR_BUS_FX = {"fx_reverb", "fx_delay", "fx_filter", "fx_widen",
                  "fx_trim", "fx_pump"}
_STEM_GLOBALS = ("version", "bpm", "key", "swing", "lengthBars",
                 "tempoMap", "sections", "buses")


def _stem_eligible(song):
    if not song.get("tracks"):
        return False
    # vst3 SYNTHS are render-NONDETERMINISTIC (measured: same song, spawned
    # twice, -1.3 dBFS peak difference — random oscillator phase). No summation
    # scheme can deep-null against a fresh full render, so vst3 sources are out
    # (this is also why the whole-song cache is a CONSISTENCY feature for those
    # sessions, not just speed). Audio + faust sources are deterministic.
    for t in song.get("tracks", []):
        kind = str((t.get("source") or {}).get("kind", "faust"))
        if kind not in ("faust", "audio"):
            return False
        for f in t.get("fx", []) or []:
            if str(f.get("id", "")).startswith("vst3:"):
                return False
    for b in song.get("buses", []) or []:
        for f in b.get("fx", []) or []:
            if str(f.get("id", "")) not in _LINEAR_BUS_FX:
                return False
    return True


def _abs_track(track):
    t = json.loads(json.dumps(track))
    for c in t.get("audioClips", []) or []:
        p = c.get("file", "")
        if p and not os.path.isabs(p):
            c["file"] = os.path.join(SONGS, p)
    return t


def _track_clip_fp(track):
    fps = []
    for c in track.get("audioClips", []) or []:
        p = c.get("file", "")
        if not os.path.isabs(p):
            p = os.path.join(SONGS, p)
        try:
            st = os.stat(p)
            fps.append(f"{p}:{st.st_size}:{st.st_mtime_ns}")
        except OSError:
            fps.append(f"{p}:MISSING")
    return "|".join(fps)


def _stem_key(song, track):
    g = json.dumps({k: song.get(k) for k in _STEM_GLOBALS},
                   sort_keys=True, separators=(",", ":"))
    t = json.dumps(track, sort_keys=True, separators=(",", ":"))
    parts = "\x00".join([
        "stem1", g, t,
        _m1_md5(),
        _tree_digest(os.path.join(ROOT, "app", "faust_gen"), (".hpp", ".h")),
        _tree_digest(os.path.join(ROOT, "instruments"), (".dsp",)),
        _track_clip_fp(track),
        _quarantine_digest(),
        os.environ.get("SOTADAW_RENDER_EPOCH", "0"),
    ])
    return hashlib.sha256(parts.encode()).hexdigest()


def _solo_song(song, track):
    """The track alone, buses+sends intact, master STRIPPED. Whitelist copy —
    scenes/slots/song-automation/_loop can't leak into a stem."""
    solo = {k: json.loads(json.dumps(song[k])) for k in _STEM_GLOBALS if k in song}
    solo["masterGainDb"] = 0.0
    solo["master"] = []
    solo["tracks"] = [_abs_track(track)]
    return solo


def _master_apply_song(song, sum_wav, sum_sec):
    # clip beats OVERSHOOT the sum (the stems carry the bus tail past the last
    # bar — cutting at lengthBars*4 chopped 1.7s of reverb ring, found live);
    # max-bpm bound = always enough beats, the caller trims to the sum's frames
    bpms = [float(song.get("bpm", 120.0))]
    bpms += [float(t.get("bpm", bpms[0])) for t in song.get("tempoMap", []) or []]
    beats = float(int(sum_sec * max(bpms) / 60.0) + 2)
    mast = {k: json.loads(json.dumps(song[k]))
            for k in ("version", "bpm", "key", "lengthBars", "tempoMap")
            if k in song}
    mast["masterGainDb"] = song.get("masterGainDb", 0.0)
    mast["master"] = json.loads(json.dumps(song.get("master", [])))
    if song.get("automation"):              # song-level targets master only
        mast["automation"] = json.loads(json.dumps(song["automation"]))
    mast["tracks"] = [{"name": "stemsum", "gainDb": 0.0, "pan": 0.0,
                       "source": {"kind": "audio"},
                       "audioClips": [{"file": sum_wav, "startBeat": 0.0,
                                       "lengthBeats": beats, "offsetSec": 0.0}]}]
    return mast


def render_stem_assembled(song_path, out_wav, quiet=True, report=None, keep_sum=False):
    """The incremental rail: reuse unchanged per-track stems, render only dirty
    ones, sum in float64, master-apply once. Returns {"sha256", "stems_total",
    "stems_fresh"} or None (ineligible / any failure -> caller falls back)."""
    import numpy as np                      # lazy: the daemon imports this module
    import soundfile as sf                  # with the flag off too
    song = json.load(open(song_path))
    if not _stem_eligible(song):
        return None
    live = [t for t in song.get("tracks", [])
            if not t.get("muted") and (t.get("notes") or t.get("audioClips"))]
    if not live:
        return None
    os.makedirs(CACHE, exist_ok=True)
    tmps, fresh, stems = [], 0, []
    try:
        for i, tr in enumerate(live):
            k = _stem_key(song, tr)
            wv, mp = _wav_path(k), _meta_path(k)
            meta = {}
            if os.path.exists(mp):
                try:
                    meta = json.load(open(mp))
                except Exception:
                    meta = {}
            if not (os.path.exists(wv) and meta.get("size") == os.path.getsize(wv)):
                sp = os.path.join(SONGS, f"_stemtmp_{os.getpid()}_{i}.json")
                json.dump(_solo_song(song, tr), open(sp, "w"))
                tmps.append(sp)
                t0 = time.monotonic()
                sha, _err = _do_render(sp, wv)
                if sha is None:
                    return None
                json.dump({"kind": "stem", "track": tr.get("name", ""),
                           "song": os.path.basename(song_path),
                           "created": time.time(), "last_used": time.time(),
                           "hits": 0, "size": os.path.getsize(wv),
                           "wall_s": round(time.monotonic() - t0, 2)},
                          open(mp, "w"))
                fresh += 1
            else:
                meta["last_used"] = time.time()
                meta["hits"] = int(meta.get("hits", 0)) + 1
                json.dump(meta, open(mp, "w"))
            stems.append((tr.get("name", ""), k, wv))
        datas = [sf.read(wv, dtype="float64", always_2d=True) for _, _, wv in stems]
        if len({sr for _, sr in datas}) != 1:
            return None
        sr = datas[0][1]
        lens = [len(d) for d, _ in datas]
        if max(lens) - min(lens) > 4096:    # incoherent stem lengths -> classic rail
            return None
        acc = np.zeros((max(lens), datas[0][0].shape[1]))
        for d, _ in datas:
            acc[: len(d)] += d
        # keep_sum lives OUTSIDE the cache dir: _lru_gc treats meta-less wavs as
        # last_used=0 -> FIRST eviction — a kept sum inside CACHE died before the
        # prove rig could read it (bit 2026-07-12 on a 68-bar rap arrangement).
        sum_dir = SONGS if keep_sum else CACHE
        sum_wav = os.path.join(sum_dir, f"_stemsum_{os.getpid()}.wav")
        sf.write(sum_wav, acc.astype(np.float32), sr, subtype="FLOAT")
        if not keep_sum:
            tmps.append(sum_wav)
        mp_song = os.path.join(SONGS, f"_stemtmp_{os.getpid()}_master.json")
        json.dump(_master_apply_song(song, sum_wav, len(acc) / sr), open(mp_song, "w"))
        tmps.append(mp_song)
        sha, _err = _do_render(mp_song, out_wav)
        if sha is None:
            return None
        outd, osr = sf.read(out_wav, dtype="float64", always_2d=True)
        if len(outd) > len(acc):                # the overshoot's silent tail
            sf.write(out_wav, outd[: len(acc)], osr, subtype="PCM_24")
            sha = _file_sha(out_wav)
        if report is not None:
            report.update({"stems": stems, "sum_wav": sum_wav, "sr": sr})
        _lru_gc()
        if not quiet:
            print(f"[cache] STEMS {fresh}/{len(stems)} fresh -> assembled {out_wav}")
        return {"sha256": sha, "stems_total": len(stems), "stems_fresh": fresh}
    finally:
        for p in tmps:
            if os.path.exists(p):
                os.remove(p)


def render_cached(song_path, out_wav, quiet=False):
    os.makedirs(CACHE, exist_ok=True)
    key = cache_key(song_path)
    wv, mp = _wav_path(key), _meta_path(key)
    meta = {}
    if os.path.exists(mp):
        try:
            meta = json.load(open(mp))
        except Exception:
            meta = {}
    # INTEGRITY (safe for the live daemon): a hit must match the stored byte count,
    # else the cached wav is truncated/corrupt — drop it and re-render. The seal
    # already guarantees the CONTENT matches; this catches a broken FILE.
    if os.path.exists(wv) and meta.get("size") == os.path.getsize(wv):
        shutil.copyfile(wv, out_wav)
        meta["last_used"] = time.time()
        meta["hits"] = int(meta.get("hits", 0)) + 1
        json.dump(meta, open(mp, "w"))
        if not quiet:
            print(f"[cache] HIT {key[:12]} -> {out_wav}")
        return {"hit": True, "key": key, "sha256": meta.get("sha256")}
    if os.path.exists(wv):                          # stale/corrupt entry -> purge
        for p in (wv, mp):
            if os.path.exists(p):
                os.remove(p)
    sha, assembled = None, False
    if os.environ.get("SOTADAW_STEM_CACHE") == "1":
        try:
            arep = render_stem_assembled(song_path, out_wav, quiet=quiet)
        except Exception:
            arep = None                     # ANY stem trouble -> the classic rail
        if arep is not None:
            sha, assembled = arep["sha256"], True
    if sha is None:
        sha, err = _do_render(song_path, out_wav)
        if sha is None:
            return {"hit": False, "key": key, "error": err}
    shutil.copyfile(out_wav, wv)
    json.dump({"key": key, "sha256": sha, "song": os.path.basename(song_path),
               "created": time.time(), "last_used": time.time(), "hits": 0,
               "assembled": assembled,
               "size": os.path.getsize(wv)}, open(mp, "w"))
    _lru_gc()
    if not quiet:
        print(f"[cache] MISS {key[:12]} rendered + stored")
    return {"hit": False, "key": key, "sha256": sha}


def stats():
    b = budget_bytes()
    common = {"budget_gb": round(b / 2 ** 30, 3),
              "budget_adaptive": os.environ.get("SOTADAW_RENDER_CACHE_GB") is None,
              "disk_free_gb": round(shutil.disk_usage(SONGS).free / 2 ** 30, 1)}
    if not os.path.isdir(CACHE):
        return {"entries": 0, "bytes": 0, "gb": 0.0, "lifetime_hits": 0, **common}
    wavs = [f for f in os.listdir(CACHE) if f.endswith(".wav")]
    total = sum(os.path.getsize(os.path.join(CACHE, f)) for f in wavs)
    hits = 0
    for f in os.listdir(CACHE):
        if f.endswith(".json"):
            try:
                hits += int(json.load(open(os.path.join(CACHE, f))).get("hits", 0))
            except Exception:
                pass
    return {"entries": len(wavs), "bytes": total,
            "gb": round(total / 2 ** 30, 3), "lifetime_hits": hits, **common}


def prove(keep=False):
    """The EB4 bar: 10-take mock session, >40% renders skipped, hits byte-exact."""
    base = {"version": 2, "bpm": 120, "lengthBars": 2, "masterGainDb": 0,
            "master": [],
            "tracks": [
                {"name": "kick", "source": {"kind": "faust", "id": "kick_808"},
                 "gainDb": -6.0,
                 "notes": [{"start": b, "len": 0.4, "pitch": 36, "vel": 0.9}
                           for b in range(0, 8, 2)]},
                {"name": "hat", "source": {"kind": "faust", "id": "hat"},
                 "gainDb": -10.0,
                 "notes": [{"start": b * 0.5, "len": 0.1, "pitch": 70, "vel": 0.6}
                           for b in range(16)]}]}

    def variant(which):
        s = json.loads(json.dumps(base))
        if which == "hatE":
            s["tracks"][1]["gainDb"] = -8.0
        elif which == "kickE":
            s["tracks"][0]["notes"][0]["vel"] = 0.7
        elif which == "bassE":
            s["tracks"].append({"name": "bass",
                                "source": {"kind": "faust", "id": "bass_warm"},
                                "gainDb": -8.0,
                                "notes": [{"start": 0, "len": 2, "pitch": 40,
                                           "vel": 0.8}]})
        return s

    takes = ["orig", "hatE", "orig", "kickE", "kickE", "orig", "hatE", "bassE",
             "orig", "kickE"]                       # 4 unique -> 6 expected hits
    tmp = os.path.join(SONGS, "_rcache_take.json")
    out = os.path.join(SONGS, "_rcache_out.wav")
    hits = 0
    t0 = time.monotonic()
    shas = {}
    for i, tk in enumerate(takes):
        with open(tmp, "w") as f:
            json.dump(variant(tk), f, indent=1)
        r = render_cached(tmp, out, quiet=True)
        if r.get("error"):
            print("PROVE_FAIL render error", r["error"])
            return 1
        hits += 1 if r["hit"] else 0
        shas.setdefault(tk, set()).add(r.get("sha256") or _file_sha(out))
        print(f"  take {i + 1:2d} {tk:6s} {'HIT ' if r['hit'] else 'miss'} "
              f"{(r.get('sha256') or '')[:12]}", flush=True)
    dt = time.monotonic() - t0
    # byte-exactness: every take label must map to exactly ONE sha (hit == fresh)
    stable = all(len(v) == 1 for v in shas.values())
    # and a hit copy must equal a fresh direct render byte-for-byte (the seal)
    with open(tmp, "w") as f:
        json.dump(variant("orig"), f, indent=1)
    fresh = os.path.join(SONGS, "_rcache_fresh.wav")
    subprocess.run([M1, "render", tmp, fresh], capture_output=True, text=True,
                   timeout=600)
    render_cached(tmp, out, quiet=True)             # guaranteed hit
    same = _file_sha(fresh) == _file_sha(out)
    rate = hits / len(takes)
    ok = rate > 0.4 and stable and same
    print(f"[prove] hits {hits}/{len(takes)} ({rate:.0%})  label-sha-stable={stable}"
          f"  hit==fresh bytes={same}  wall={dt:.1f}s")
    print("CACHE_JSON " + json.dumps({"pass": ok, "hit_rate": rate,
                                      "stable": stable, "hit_equals_fresh": same,
                                      "stats": stats()}))
    if not keep:
        for p in (tmp, out, fresh):
            if os.path.exists(p):
                os.remove(p)
        shutil.rmtree(CACHE, ignore_errors=True)
    return 0 if ok else 1


def prove_stems(genre="trap", keep=False):
    """The W6 bar — the stem identity + the edit win, on a REAL generated loop:
      A  sum(solo stems)          nulls vs the pre-master full render (linearity)
      B  assembled (master-apply) nulls vs the full render (the wall ran once)
      C  after a 1-track edit, assembly still nulls AND re-rendered exactly 1 stem
    Also prints per-stem band ownership — who owns the mix's lowmid (the band-
    truth table the mud campaign reads). Probe files: songs/_w6stem*."""
    import numpy as np
    import soundfile as sf
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import arrange
    import loop_gen

    # the ARRANGED song is the honest subject: proposal renders are full
    # arrangements, and a 4-bar loop's render is too cheap for stems to beat
    # (fixed 2-render overhead vs one ~1s render — measured 0.3x, the wrong way)
    name = "_w6stem"
    loop_gen.generate(genre, name, bars=4, seed=7)
    arrange.arrange(os.path.join(SONGS, name + ".json"), out_name=name + "_arr",
                    genre=genre)
    sp = os.path.join(SONGS, name + "_arr.json")
    song = json.load(open(sp))
    scratch0 = os.path.join(SONGS, name + ".json")

    def read(p):
        return sf.read(p, dtype="float64", always_2d=True)[0]

    def null_db(a, b):
        n = min(len(a), len(b))
        d = a[:n] - b[:n]
        pk = float(np.max(np.abs(d))) if n else 1.0
        return (20.0 * np.log10(pk) if pk > 0 else -200.0), abs(len(a) - len(b))

    scratch = [sp, scratch0]
    try:
        full = os.path.join(SONGS, name + "_ren.wav")
        scratch.append(full)
        t0 = time.monotonic()
        sha, err = _do_render(sp, full)
        t_full = time.monotonic() - t0
        if sha is None:
            print("PROVE_FAIL full render", (err or "")[:200])
            return 1
        # premaster REFERENCE through fx_trim -12: a bare-master mix peaks past
        # 0 dBFS and CLIPS at the 24-bit write (measured -3 dB fake fail) — the
        # trim keeps the reference honest; the sum is scaled to match
        pre_song = json.loads(json.dumps(song))
        pre_song["master"] = [{"id": "fx_trim", "params": {"level": -12.0}}]
        pre_song["masterGainDb"] = 0.0
        pp = os.path.join(SONGS, name + "_pre.json")
        pre = os.path.join(SONGS, name + "_pre.wav")
        scratch += [pp, pre]
        json.dump(pre_song, open(pp, "w"))
        if _do_render(pp, pre)[0] is None:
            print("PROVE_FAIL premaster render")
            return 1

        rep = {}
        asm = os.path.join(SONGS, name + "_asm.wav")
        scratch.append(asm)
        t0 = time.monotonic()
        r1 = render_stem_assembled(sp, asm, quiet=True, report=rep, keep_sum=True)
        t_build = time.monotonic() - t0
        if r1 is None:
            print("PROVE_FAIL assembly ineligible/failed")
            return 1
        scratch.append(rep["sum_wav"])
        a_db, a_len = null_db(read(rep["sum_wav"]) * (10.0 ** (-12.0 / 20.0)),
                              read(pre))
        b_db, b_len = null_db(read(asm), read(full))

        # the band-truth table rides the same stems for free
        edges = ((20, 120, "low"), (120, 500, "lowmid"), (500, 2000, "mid"),
                 (2000, 6000, "himid"), (6000, None, "high"))
        rows = []
        for nm, _k, wv in rep["stems"]:
            d = read(wv).mean(axis=1)
            spec = np.abs(np.fft.rfft(d)) ** 2
            fr = np.fft.rfftfreq(len(d), 1.0 / rep["sr"])
            rows.append((nm, [float(spec[(fr >= lo) & (fr < (hi or 1e9))].sum())
                              for lo, hi, _ in edges]))
        mix_lowmid = sum(r[1][1] for r in rows) or 1.0
        print("[prove-stems] LOWMID OWNERSHIP (120-500Hz, share of the mix's lowmid):")
        for nm, bands in sorted(rows, key=lambda r: -r[1][1]):
            tot = sum(bands) or 1.0
            print(f"  {nm:>10s}  {100 * bands[1] / mix_lowmid:5.1f}% of mix | own: " +
                  " ".join(f"{lab} {100 * b / tot:4.1f}%"
                           for (_lo, _hi, lab), b in zip(edges, bands)))

        # the EDIT: one track moves -> exactly one stem re-renders
        song2 = json.loads(json.dumps(song))
        tgt = next(t for t in song2["tracks"] if t.get("notes") and not t.get("muted"))
        tgt["gainDb"] = float(tgt.get("gainDb", 0.0)) + 1.5
        sp2 = os.path.join(SONGS, name + "_e.json")
        asm2 = os.path.join(SONGS, name + "_easm.wav")
        full2 = os.path.join(SONGS, name + "_efull.wav")
        scratch += [sp2, asm2, full2]
        json.dump(song2, open(sp2, "w"))
        t0 = time.monotonic()
        r2 = render_stem_assembled(sp2, asm2, quiet=True)
        t_edit = time.monotonic() - t0
        t0 = time.monotonic()
        if _do_render(sp2, full2)[0] is None:
            print("PROVE_FAIL edited full render")
            return 1
        t_full2 = time.monotonic() - t0
        c_db, c_len = null_db(read(asm2), read(full2))

        ok = (a_db <= -60 and b_db <= -60 and c_db <= -60
              and r2 is not None and r2["stems_fresh"] == 1
              and a_len == 0 and b_len == 0 and c_len == 0)
        print(f"[prove-stems] null A sum-vs-premaster {a_db:7.1f} dBFS  "
              f"B asm-vs-full {b_db:7.1f}  C edit {c_db:7.1f}  "
              f"(len deltas {a_len}/{b_len}/{c_len} frames)")
        print(f"[prove-stems] full {t_full:5.1f}s | first assembly {t_build:5.1f}s "
              f"({r1['stems_fresh']}/{r1['stems_total']} stems) | edit: assembly "
              f"{t_edit:5.1f}s vs fresh full {t_full2:5.1f}s -> "
              f"{t_full2 / max(0.01, t_edit):4.1f}x  fresh_stems="
              f"{r2['stems_fresh'] if r2 else '-'}")
        print("STEMS_JSON " + json.dumps({
            "pass": bool(ok), "genre": genre,
            "null_db": {"sum_vs_premaster": round(a_db, 1),
                        "asm_vs_full": round(b_db, 1), "edit": round(c_db, 1)},
            "t_full_s": round(t_full, 1), "t_build_s": round(t_build, 1),
            "t_edit_s": round(t_edit, 1), "t_edit_full_s": round(t_full2, 1),
            "edit_speedup": round(t_full2 / max(0.01, t_edit), 2),
            "stems": r1["stems_total"],
            "edit_fresh_stems": r2["stems_fresh"] if r2 else -1}))
        return 0 if ok else 1
    finally:
        serve_stop()
        if not keep:
            for p in scratch:
                if os.path.exists(p):
                    os.remove(p)


def main():
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    if a[0] == "--prove":
        return prove("--keep" in a)
    if a[0] == "--prove-stems":
        g = next((x for x in a[1:] if not x.startswith("--")), "trap")
        return prove_stems(g, "--keep" in a)
    if a[0] == "stats":
        print("CACHE_JSON " + json.dumps(stats()))
        return 0
    if a[0] == "gc":
        n = _lru_gc()
        print("CACHE_JSON " + json.dumps({"evicted": n, **stats()}))
        return 0
    if a[0] == "render" and len(a) >= 3:
        r = render_cached(a[1], a[2])
        print("CACHE_JSON " + json.dumps(r))
        return 0 if not r.get("error") else 1
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
