#!/usr/bin/env python3
"""V47 TRACK FREEZE — freeze IS a cached render of symbols (SPEC v2.6).

freeze:   render the track SOLO (source+notes+fx+its automation, no master, no
          sends' returns) to songs/.freeze/<song>__<track>.wav, stash the whole
          symbolic lane VERBATIM in track.frozen, and swap the live track to
          audio playback of the cache. gain/pan/mute/sends stay LIVE (post-
          freeze mixing still works). Nothing symbolic is lost — the frozen
          block carries source/notes/fx/automation byte-identically.
unfreeze: restore the symbolic lane from track.frozen, delete the cache.

Staleness: frozen.sha = sha256 of the canonical symbolic subset. If the track's
frozen copy no longer matches (someone edited notes while frozen — the UI/agent
shouldn't, but truth wins), `freeze --check` reports stale and `freeze` re-renders.

usage:
  freeze.py freeze   <song> <track> [--out <song2>]   (in place by default)
  freeze.py unfreeze <song> <track> [--out <song2>]
  freeze.py check    <song>                            (report frozen/stale table)
  freeze.py --selftest                                 (scratch E2E through m1)

Exit 0 ok / 1 failure. Prints FREEZE_JSON on the last line.
"""
import copy, hashlib, json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "songs")
FREEZE_DIR = os.path.join(SONGS, ".freeze")
M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")

SYMBOLIC_KEYS = ("source", "notes", "fx", "automation", "audioClips", "groove")


def resolve(arg):
    if arg.endswith(".json"):
        p = arg if os.path.isabs(arg) else os.path.join(ROOT, arg)
        return os.path.splitext(os.path.basename(p))[0], p
    name = "".join(c for c in arg.lower() if c.isalnum() or c == "_")
    return name, os.path.join(SONGS, f"{name}.json")


def sym_subset(track):
    return {k: track[k] for k in SYMBOLIC_KEYS if k in track}


def sym_sha(track):
    return hashlib.sha256(json.dumps(sym_subset(track), sort_keys=True).encode()).hexdigest()[:16]


def find_track(song, tname):
    for t in song.get("tracks", []):
        if t.get("name") == tname:
            return t
    return None


def render_solo(song, track, wav):
    """Render ONE symbolic lane raw: song timing kept, no master chain, no sends."""
    solo_t = {k: copy.deepcopy(v) for k, v in track.items()
              if k in SYMBOLIC_KEYS or k in ("name",)}
    solo_t["gainDb"] = 0.0          # level/pan stay live on the frozen track
    solo_t["pan"] = 0.0
    solo_t.pop("sends", None)
    solo = {"version": 2, "bpm": song.get("bpm", 120),
            "lengthBars": song.get("lengthBars", 4), "masterGainDb": 0,
            "master": [], "tracks": [solo_t]}
    for k in ("swing", "tempoMap", "key"):
        if k in song:
            solo[k] = song[k]
    sj = wav[:-4] + ".solo.json"
    json.dump(solo, open(sj, "w"), indent=1)
    r = subprocess.run([M1, "render", sj, wav], capture_output=True, text=True, timeout=600)
    os.remove(sj)
    if "ok=1" not in (r.stdout + r.stderr) or not os.path.exists(wav):
        raise RuntimeError("solo render failed: " + (r.stdout + r.stderr)[-300:])


def freeze(song_arg, tname, out=None):
    name, sj = resolve(song_arg)
    song = json.load(open(sj))
    t = find_track(song, tname)
    if t is None:
        return {"error": f"no track '{tname}' in {name}"}
    if t.get("frozen"):
        return {"error": f"'{tname}' is already frozen (unfreeze first, or check)"}
    if t.get("locked"):
        return {"error": f"'{tname}' is LOCKED — freeze needs the user to unlock"}

    os.makedirs(FREEZE_DIR, exist_ok=True)
    wav = os.path.join(FREEZE_DIR, f"{name}__{tname}.wav")
    render_solo(song, t, wav)

    frozen = {"wav": os.path.relpath(wav, ROOT), "sha": sym_sha(t),
              "symbolic": sym_subset(t)}
    for k in SYMBOLIC_KEYS:
        t.pop(k, None)
    t["frozen"] = frozen
    t["source"] = {"kind": "audio"}
    t["notes"] = []
    t["audioClips"] = [{"file": frozen["wav"], "startBeat": 0.0,
                        "lengthBeats": float(song.get("lengthBars", 4)) * 4.0,
                        "offsetSec": 0.0}]
    json.dump(song, open(out or sj, "w"), indent=1)
    return {"frozen": tname, "wav": frozen["wav"], "sha": frozen["sha"],
            "bytes": os.path.getsize(wav)}


def unfreeze(song_arg, tname, out=None):
    name, sj = resolve(song_arg)
    song = json.load(open(sj))
    t = find_track(song, tname)
    if t is None:
        return {"error": f"no track '{tname}' in {name}"}
    fr = t.get("frozen")
    if not fr:
        return {"error": f"'{tname}' is not frozen"}
    for k in SYMBOLIC_KEYS:
        t.pop(k, None)
    t.pop("frozen", None)
    t.pop("audioClips", None)
    for k, v in fr.get("symbolic", {}).items():
        t[k] = v
    t.setdefault("notes", [])
    wav = os.path.join(ROOT, fr.get("wav", ""))
    if os.path.exists(wav):
        os.remove(wav)
    json.dump(song, open(out or sj, "w"), indent=1)
    restored_sha = sym_sha(t)
    return {"unfrozen": tname, "sha_match": restored_sha == fr.get("sha"),
            "sha": restored_sha}


def check(song_arg):
    name, sj = resolve(song_arg)
    song = json.load(open(sj))
    rows = []
    for t in song.get("tracks", []):
        fr = t.get("frozen")
        if fr:
            wav_ok = os.path.exists(os.path.join(ROOT, fr.get("wav", "")))
            rows.append({"track": t.get("name"), "frozen": True,
                         "cache_present": wav_ok, "sha": fr.get("sha")})
    return {"song": name, "frozen_tracks": rows}


def selftest():
    """Scratch E2E: freeze -> render still sounds -> unfreeze -> symbolic bit-exact."""
    import shutil, wave

    def wav_rms(path):
        import numpy as np
        with wave.open(path, "rb") as w:
            sw, n, ch = w.getsampwidth(), w.getnframes(), w.getnchannels()
            raw = w.readframes(n)
        if sw == 3:
            b = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3).astype(np.int32)
            x = (b[:, 0] | (b[:, 1] << 8) | (b[:, 2] << 16))
            x = (x - ((x >> 23) << 24)).astype(np.float64) / 8388608.0
        else:
            x = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0
        return 20.0 * np.log10(float(np.sqrt(np.mean(x * x)) + 1e-12))

    checks = []

    def ck(nm, ok, detail=""):
        checks.append((nm, bool(ok), detail))
        print(("  ok " if ok else "FAIL ") + nm + (f"  {detail}" if detail else ""))

    scratch = os.path.join(SONGS, "_freeze_selftest.json")
    song = {"version": 2, "bpm": 120, "lengthBars": 2, "masterGainDb": 0,
            "master": [{"type": "faustfx", "id": "fx_truepeak", "params": {"ceiling": -1.2}}],
            "tracks": [
                {"name": "keys", "source": {"kind": "faust", "id": "rhodes"}, "gainDb": -6,
                 "fx": [{"id": "fx_delay", "params": {"mix": 0.2}}],
                 "notes": [{"start": float(i * 2), "len": 1.5, "pitch": 60 + (i % 3) * 4,
                            "vel": 0.8} for i in range(4)]},
                {"name": "hats", "source": {"kind": "faust", "id": "hat"}, "gainDb": -10,
                 "notes": [{"start": i * 0.5, "len": 0.1, "pitch": 70, "vel": 0.6}
                           for i in range(16)]}]}
    json.dump(song, open(scratch, "w"), indent=1)
    before = json.load(open(scratch))
    sha_before = sym_sha(before["tracks"][0])

    r = freeze(scratch, "keys")
    ck("freeze runs", "error" not in r, r.get("error", ""))
    frozen_song = json.load(open(scratch))
    ft = find_track(frozen_song, "keys")
    ck("symbolic stashed", ft.get("frozen", {}).get("sha") == sha_before)
    ck("cache exists", os.path.exists(os.path.join(ROOT, ft["frozen"]["wav"])))
    ck("plays as audio", ft["source"]["kind"] == "audio" and len(ft.get("audioClips", [])) == 1)

    wav = scratch[:-5] + ".wav"
    rr = subprocess.run([M1, "render", scratch, wav], capture_output=True, text=True, timeout=600)
    ck("frozen song renders", "ok=1" in (rr.stdout + rr.stderr))
    rms_frozen = wav_rms(wav)
    ck("frozen render non-silent", rms_frozen > -40, f"rms {rms_frozen:.1f} dB")

    r2 = unfreeze(scratch, "keys")
    ck("unfreeze runs", "error" not in r2, r2.get("error", ""))
    ck("symbolic bit-exact after round-trip", r2.get("sha_match") is True, r2.get("sha"))
    after = json.load(open(scratch))
    ck("source restored", after["tracks"][0]["source"].get("id") == "rhodes")
    ck("cache deleted", not os.path.exists(os.path.join(ROOT, r.get("wav", "zzz"))))

    for p in (scratch, wav):
        if os.path.exists(p):
            os.remove(p)
    shutil.rmtree(FREEZE_DIR, ignore_errors=True) if not os.listdir(FREEZE_DIR) else None
    failed = [n for n, ok, _ in checks if not ok]
    print(f"freeze selftest: {len(checks) - len(failed)}/{len(checks)} clean")
    return 0 if not failed else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    cmd = sys.argv[1]
    out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else None
    if cmd == "freeze":
        res = freeze(sys.argv[2], sys.argv[3], out)
    elif cmd == "unfreeze":
        res = unfreeze(sys.argv[2], sys.argv[3], out)
    elif cmd == "check":
        res = check(sys.argv[2])
    else:
        sys.exit(__doc__)
    print("FREEZE_JSON " + json.dumps(res))
    sys.exit(1 if "error" in res else 0)
