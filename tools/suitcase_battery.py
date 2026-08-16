#!/usr/bin/env python3
"""THE SUITCASE battery — song_pack.py pack/unpack proven end to end.

The corpus motivation is real: 28 audioClips in songs/ carry ABSOLUTE paths
(7 of _gate_set_v3's point at a dead session scratchpad — those wavs are
gone forever). A bundle heals what still exists and lists what does not.

  S1 pack emits, deterministically (two packs byte-identical)
  S2 manifest truth: sha256 per asset, missing ref listed, kit + plugin deps
  S3 packed json: every EXISTING ref rewritten under assets/ (zero abs),
     the ghost ref left verbatim, voice attribution stamped structurally
  S4 unpack lands: notes exact, assets sha-match, refs point at landed files,
     dedupe (clip + slot sharing one wav -> ONE asset)
  S5 collision court: second unpack lands under _2, the first untouched
  S6 zip-slip member -> the WHOLE bundle refused, nothing lands
  S7 a plain zip (no manifest) refused
  S8 real corpus: demo_track packs clean (parseable, zero abs refs inside)
Run: python3 tools/suitcase_battery.py   (suite leg — pure, no renders)
"""
import glob
import json
import os
import struct
import subprocess
import sys
import tempfile
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "songs")
PY = sys.executable
N = {"pass": 0, "fail": 0}


def check(name, cond, detail=""):
    N["pass" if cond else "fail"] += 1
    print(("PASS " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))


def run(*args):
    return subprocess.run([PY, os.path.join(ROOT, "tools", "song_pack.py"), *args],
                          capture_output=True, text=True, timeout=120)


def wav(path, n=200):
    with open(path, "wb") as f:
        data = struct.pack("<%dh" % n, *([1000, -1000] * (n // 2)))
        f.write(b"RIFF" + struct.pack("<I", 36 + len(data)) + b"WAVEfmt "
                + struct.pack("<IHHIIHH", 16, 1, 1, 8000, 16000, 2, 16)
                + b"data" + struct.pack("<I", len(data)) + data)


tdir = tempfile.mkdtemp(prefix="sbat_")
made = [os.path.join(SONGS, "_sbat_a.wav"), os.path.join(tdir, "abs_kick.wav"),
        os.path.join(SONGS, "_sbat_vocal_take.wav"), os.path.join(SONGS, "_sbat.fxp")]
landed = []
try:
    wav(made[0])
    wav(made[1], 400)
    wav(made[2])
    open(made[3], "wb").write(b"CcnK preset blob")
    song = {
        "version": 2, "bpm": 124, "key": "F minor", "lengthBars": 8,
        "tracks": [
            {"name": "loop", "gainDb": -6,
             "audioClips": [{"file": "songs/_sbat_a.wav", "startBeat": 0, "lengthBeats": 4},
                            {"file": made[1], "startBeat": 4, "lengthBeats": 4},
                            {"file": "songs/_sbat_GHOST.wav", "startBeat": 8, "lengthBeats": 4}],
             "slots": [{"audioFile": "songs/_sbat_a.wav"}]},
            {"name": "vox", "audioClips": [{"file": "songs/_sbat_vocal_take.wav",
                                            "startBeat": 0, "lengthBeats": 8}]},
            {"name": "keys", "source": {"kind": "vst3", "id": "vst3:Surge XT",
                                        "preset": os.path.relpath(made[3], ROOT)},
             "notes": [{"start": 0, "len": 1, "pitch": 60, "vel": 0.8},
                       {"start": 1, "len": 1, "pitch": 63, "vel": 0.7}]},
            {"name": "drums", "source": {"kind": "sample", "kit": "gm_drums"},
             "notes": [{"start": 0, "len": 0.25, "pitch": 36, "vel": 0.9}]},
            "garbage-nondict-track",
        ],
        "master": [{"type": "faustfx", "id": "fx_truepeak", "params": {"ceiling": -1.2}}],
    }
    sp = os.path.join(SONGS, "_sbat_song.json")
    json.dump(song, open(sp, "w"))
    made.append(sp)

    z1, z2 = os.path.join(tdir, "one.zip"), os.path.join(tdir, "two.zip")
    r = run("pack", "_sbat_song", z1)
    run("pack", "_sbat_song", z2)
    check("S1 pack emits + deterministic", r.returncode == 0 and os.path.exists(z1)
          and open(z1, "rb").read() == open(z2, "rb").read(),
          (r.stdout + r.stderr).strip()[:90])

    z = zipfile.ZipFile(z1)
    m = json.loads(z.read("manifest.json"))
    pk = json.loads(z.read("song.json"))
    import hashlib
    sha_ok = all(hashlib.sha256(z.read(a["asset"])).hexdigest() == a["sha256"]
                 for a in m["files"])
    check("S2 manifest: sha256 truth + missing + deps",
          sha_ok and len(m["files"]) == 4 and m["missing"] == ["songs/_sbat_GHOST.wav"]
          and m["kits"] == ["gm_drums"] and m["plugins"] == ["vst3:Surge XT"],
          f"files {len(m['files'])} missing {m['missing']} kits {m['kits']}")

    refs = [c["file"] for t in pk["tracks"] if isinstance(t, dict)
            for c in t.get("audioClips", [])]
    slot_refs = [sl["audioFile"] for t in pk["tracks"] if isinstance(t, dict)
                 for sl in t.get("slots", []) if isinstance(sl, dict)]
    preset = next(t["source"]["preset"] for t in pk["tracks"]
                  if isinstance(t, dict) and t.get("name") == "keys")
    check("S3 packed json: assets/ paths, ghost verbatim, attribution stamped",
          not any(r.startswith("/") for r in refs if "GHOST" not in r)
          and sum(r.startswith("assets/") for r in refs) == 3
          and "songs/_sbat_GHOST.wav" in refs
          and slot_refs == ["assets/_sbat_a.wav"] and preset.startswith("assets/")
          and bool(pk.get("voice_license", {}).get("attribution")),
          f"refs {refs} preset {preset}")
    check("S3b dedupe: clip+slot share ONE asset",
          sum(1 for a in m["files"] if a["asset"] == "assets/_sbat_a.wav") == 1
          and refs.count("assets/_sbat_a.wav") == 1)

    r = run("unpack", z1, "_sbat_land")
    lp = os.path.join(SONGS, "_sbat_land.json")
    landed += [lp, os.path.join(SONGS, "_sbat_land_assets")]
    lb = json.load(open(lp)) if os.path.exists(lp) else {"tracks": []}
    lrefs = [c["file"] for t in lb.get("tracks", []) if isinstance(t, dict)
             for c in t.get("audioClips", [])]
    on_disk = [rr for rr in lrefs if "GHOST" not in rr
               and os.path.exists(os.path.join(ROOT, rr))]
    notes_ok = any(isinstance(t, dict) and t.get("name") == "keys"
                   and len(t.get("notes", [])) == 2 for t in lb.get("tracks", []))
    check("S4 unpack lands: notes exact + every packed ref on disk",
          r.returncode == 0 and len(on_disk) == 3 and notes_ok
          and "sha256 MISMATCH" not in r.stderr,
          (r.stdout + r.stderr).strip()[:90])

    r2 = run("unpack", z1, "_sbat_land")
    lp2 = os.path.join(SONGS, "_sbat_land_2.json")
    landed += [lp2, os.path.join(SONGS, "_sbat_land_2_assets")]
    check("S5 collision court: second unpack lands _2, first untouched",
          r2.returncode == 0 and os.path.exists(lp2)
          and json.load(open(lp))["tracks"][0]["audioClips"][0]["file"].startswith("songs/_sbat_land_assets/"))

    evil = os.path.join(tdir, "evil.zip")
    with zipfile.ZipFile(evil, "w") as ez:
        ez.writestr("manifest.json", json.dumps({"suitcase": 1, "name": "x", "files": []}))
        ez.writestr("song.json", "{}")
        ez.writestr("assets/../../evil.txt", "pwn")
    r = run("unpack", evil, "_sbat_evil")
    check("S6 zip-slip member refuses the WHOLE bundle",
          r.returncode != 0 and "REFUSED" in (r.stdout + r.stderr)
          and not os.path.exists(os.path.join(SONGS, "_sbat_evil.json"))
          and not os.path.exists(os.path.join(SONGS, "evil.txt"))
          and not os.path.exists(os.path.join(ROOT, "evil.txt")))

    plain = os.path.join(tdir, "plain.zip")
    with zipfile.ZipFile(plain, "w") as pz:
        pz.writestr("readme.txt", "not a suitcase")
    r = run("unpack", plain, "_sbat_plain")
    check("S7 non-suitcase zip refused", r.returncode != 0
          and "REFUSED" in (r.stdout + r.stderr)
          and not os.path.exists(os.path.join(SONGS, "_sbat_plain.json")))

    cz = os.path.join(tdir, "corpus.zip")
    r = run("pack", "demo_track", cz)
    ok8 = False
    if r.returncode == 0 and os.path.exists(cz):
        cm = zipfile.ZipFile(cz)
        cs = json.loads(cm.read("song.json"))
        allrefs = [str(c[k]) for c, k in
                   [(c, "file") for t in cs.get("tracks", []) if isinstance(t, dict)
                    for c in t.get("audioClips", [])]]
        ok8 = json.loads(cm.read("manifest.json")).get("suitcase") == 1 \
            and not any(rr.startswith("/") for rr in allrefs)
    check("S8 real corpus (demo_track) packs clean", ok8,
          (r.stdout + r.stderr).strip()[:80])
finally:
    for p in made + landed:
        if os.path.isdir(p):
            import shutil
            shutil.rmtree(p, ignore_errors=True)
        elif os.path.exists(p):
            os.remove(p)
    import shutil
    shutil.rmtree(tdir, ignore_errors=True)

print(f"suitcase battery: {N['pass']}/{N['pass'] + N['fail']}"
      + (" clean" if not N["fail"] else " RED"))
sys.exit(1 if N["fail"] else 0)
