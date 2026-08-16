#!/usr/bin/env python3
"""THE EXIT HATCH (THE_UTMOST §18.7 — the continuity clause, executable).

"If we vanish, your music doesn't" is not copy: one command emits the whole
song in every portable body the house speaks — source JSON, portable-score
MIDI (sounds like the song on generic instruments, d4e64d9), .dawproject
(Bitwig/Cubase/Nuendo/S1), .flp (FL Studio), .rpp (REAPER), and THE SUITCASE
bundle (song + every referenced audio/preset, collision-safe). A manifest
carries sha256s, what-opens-what, and the attributions that must travel
(voicebank credit is REQUIRED on sung takes). Every format is fail-open and
the manifest never lies: a bridge that fails is listed FAILED with its reason.

  exit_hatch.py <song> [--out DIR] [--render] [--skip flp,als,...]
  exit_hatch.py --selftest        # fixture song through every bridge (suite leg)

The escape hatch is the lock-in: people stay where leaving is easy.
"""
from __future__ import annotations
import hashlib, json, os, shutil, subprocess, sys, tempfile, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
try:
    from songname import resolve_song_name
except Exception:
    resolve_song_name = None

VENVPY = os.path.join(ROOT, ".venv", "bin", "python")
PY = VENVPY if os.path.exists(VENVPY) else sys.executable
COVENANT = "If this software vanishes, your music doesn't. Everything below opens elsewhere, today."


def _run(cmd, timeout=180):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=ROOT)
        if r.returncode != 0:
            tail = (r.stderr or r.stdout or "").strip().splitlines()
            return False, (tail[-1][:200] if tail else f"exit {r.returncode}")
        return True, ""
    except subprocess.TimeoutExpired:
        return False, f"timeout {timeout}s"
    except OSError as e:
        return False, str(e)[:200]


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def attributions(doc):
    """The credits that MUST travel (voicebank law: sung takes carry Meiji)."""
    out = []
    a = doc.get("attribution")
    if isinstance(a, str) and a.strip():
        out.append(a.strip())
    elif isinstance(a, list):
        out += [str(x).strip() for x in a if str(x).strip()]
    sung = any("sung" in (t.get("name") or "") for t in doc.get("tracks", []) or [])
    sung = sung or bool(doc.get("lyrics"))
    if sung and not any("Gahata" in x for x in out):
        out.append("Voice: Gahata Meiji from LUNAI Project (non-commercial voicebank — "
                   "commercial release requires replacing the sung stems)")
    return out


def emit(song, out_dir=None, render=False, skip=()):
    name = resolve_song_name(song) if resolve_song_name else song
    src = os.path.join(ROOT, "songs", f"{name}.json")
    if not os.path.exists(src):
        print(f"no such song: {src}")
        return 2
    doc = json.load(open(src))
    out = os.path.abspath(out_dir or os.path.join(ROOT, "songs", f"{name}_exit"))
    os.makedirs(out, exist_ok=True)

    rows = []  # (filename, what, opens_in, ok, why)

    def land(fname, what, opens_in, ok, why=""):
        rows.append((fname, what, opens_in, ok, why))
        mark = "OK " if ok else "FAIL"
        print(f"  [{mark}] {fname:<28} {what}" + (f"  ({why})" if why else ""))

    j = os.path.join(out, f"{name}.json")
    shutil.copyfile(src, j)
    land(f"{name}.json", "the song itself (open format, human-readable)",
         "any text editor; the GPL engine renders it", True)

    fmts = {
        "mid": (f"{name}.mid", [PY, "tools/midi_bridge.py", "export", src,
                                os.path.join(out, f"{name}.mid"), "--portable"],
                "portable score — THE SONG on generic instruments", "any DAW ever made"),
        "dawproject": (f"{name}.dawproject", [PY, "tools/dawproject_export.py", src,
                                              os.path.join(out, f"{name}.dawproject")],
                       "full arrangement bridge", "Bitwig, Cubase, Nuendo, Studio One"),
        "flp": (f"{name}.flp", [PY, "tools/flp_export.py", src, os.path.join(out, f"{name}.flp")],
                "FL Studio project (note-exact)", "FL Studio 21+"),
        "rpp": (f"{name}.rpp", [PY, "tools/reaper_bridge.py", "export", src,
                                os.path.join(out, f"{name}.rpp")],
                "REAPER project (round-trip exact)", "REAPER"),
    }
    for key, (fname, cmd, what, opens_in) in fmts.items():
        if key in skip:
            continue
        ok, why = _run(cmd)
        ok = ok and os.path.getsize(os.path.join(out, fname)) > 0 if ok else False
        land(fname, what, opens_in, ok, why)

    if "bundle" not in skip:
        bundle = os.path.join(out, f"{name}_bundle.zip")
        ok, why = _run([PY, "tools/song_pack.py", "pack", name, bundle], timeout=300)
        ok = ok and os.path.exists(bundle) and os.path.getsize(bundle) > 0
        land(f"{name}_bundle.zip", "THE SUITCASE: song + every referenced audio/preset",
             "any SOTA DAW machine (import_bundle), or unzip by hand", ok, why)

    if render:
        m1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")
        wav = os.path.join(out, f"{name}.wav")
        ok, why = _run([m1, "render", src, wav], timeout=600)
        land(f"{name}.wav", "rendered master (24-bit)", "anything with speakers",
             ok and os.path.exists(wav), why)

    creds = attributions(doc)
    man = os.path.join(out, "EXIT_MANIFEST.md")
    with open(man, "w") as f:
        f.write(f"# {name} — the exit\n\n{COVENANT}\n\n")
        f.write(f"emitted {time.strftime('%Y-%m-%d %H:%M')} by the exit hatch "
                f"(tools/exit_hatch.py)\n\n")
        f.write("| file | what | opens in | sha256 |\n|---|---|---|---|\n")
        for fname, what, opens_in, ok, why in rows:
            p = os.path.join(out, fname)
            digest = _sha(p)[:16] if ok and os.path.exists(p) else f"FAILED: {why or 'not emitted'}"
            f.write(f"| {fname} | {what} | {opens_in} | {digest} |\n")
        if creds:
            f.write("\n## attribution that must travel\n\n")
            for c in creds:
                f.write(f"- {c}\n")
        f.write("\n## provenance\n\nThe song's full edit history lives in the project's "
                "local git (every keep = a commit; `tools/song_blame.py blame " + name +
                "` answers who wrote every note). C2PA-signed masters come from "
                "`tools/export_master.py`.\n")
    failed = [r for r in rows if not r[3]]
    print(f"exit -> {out}  ({len(rows) - len(failed)}/{len(rows)} formats landed"
          + (f", {len(failed)} FAILED — manifest names them" if failed else "") + ")")
    return 1 if failed else 0


def selftest():
    ok = [0]
    def check(name, cond):
        print(("  PASS " if cond else "  FAIL ") + name)
        if not cond:
            sys.exit(1)
        ok[0] += 1
    name = "_exit_selftest"
    src = os.path.join(ROOT, "songs", f"{name}.json")
    fixture = {
        "bpm": 120, "lengthBars": 2, "key": "C minor",
        "tracks": [
            {"name": "kick", "source": {"kind": "faust", "name": "kick_808"},
             "gainDb": 0, "pan": 0,
             "notes": [{"start": 0.0, "len": 0.5, "pitch": 36, "vel": 1.0},
                       {"start": 4.0, "len": 0.5, "pitch": 36, "vel": 0.9}]},
            {"name": "vocals_sung", "source": {"kind": "faust", "name": "formant_vox"},
             "gainDb": -3, "pan": 0,
             "notes": [{"start": 2.0, "len": 1.0, "pitch": 60, "vel": 0.8}]},
        ],
    }
    with tempfile.TemporaryDirectory() as td:
        try:
            json.dump(fixture, open(src, "w"))
            rc = emit(name, out_dir=td)
            files = set(os.listdir(td))
            check("hatch exits 0 (every format landed)", rc == 0)
            check("json + manifest present", {f"{name}.json", "EXIT_MANIFEST.md"} <= files)
            check("portable MIDI landed", os.path.getsize(os.path.join(td, f"{name}.mid")) > 50)
            check("dawproject landed", os.path.getsize(os.path.join(td, f"{name}.dawproject")) > 100)
            check("flp landed", os.path.getsize(os.path.join(td, f"{name}.flp")) > 100)
            check("rpp landed", os.path.getsize(os.path.join(td, f"{name}.rpp")) > 100)
            check("suitcase landed", os.path.getsize(os.path.join(td, f"{name}_bundle.zip")) > 100)
            man = open(os.path.join(td, "EXIT_MANIFEST.md")).read()
            check("covenant printed", "your music doesn't" in man)
            check("voicebank attribution travels on sung takes", "Gahata Meiji" in man)
            check("manifest carries hashes", man.count("| ") > 10 and "FAILED" not in man)
        finally:
            for junk in (src, os.path.join(ROOT, "songs", f"{name}_exit")):
                if os.path.isdir(junk):
                    shutil.rmtree(junk, ignore_errors=True)
                elif os.path.exists(junk):
                    os.remove(junk)
    print(f"EXIT HATCH SELFTEST: {ok[0]}/10 PASS")
    return 0 if ok[0] == 10 else 1


def main():
    if "--selftest" in sys.argv:
        return selftest()
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    flags = sys.argv[1:]
    out = flags[flags.index("--out") + 1] if "--out" in flags and flags.index("--out") + 1 < len(flags) else None
    skip = ()
    if "--skip" in flags and flags.index("--skip") + 1 < len(flags):
        skip = tuple(flags[flags.index("--skip") + 1].split(","))
    return emit(args[0], out_dir=out, render="--render" in flags, skip=skip)


if __name__ == "__main__":
    sys.exit(main())
