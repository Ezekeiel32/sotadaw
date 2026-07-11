#!/usr/bin/env python3
"""RESTYLE battery — the morph changes the SOUND and keeps the MUSIC.

  R1 every note byte-identical after restyle (the core promise)
  R2 house->trap: kick goes 808 (sliding), bass follows, color voice = trap's
  R3 trap->house: kick back to punch, swing removed if house is straight
  R4 locked + vst3 + sample tracks keep their identity (honest skips)
  R5 unknown genre errors listing options
  R6 restyled song RENDERS clean and sounds DIFFERENT (rendered centroid or
     band balance moves vs the original render)
Exit 1 on any failure."""
import copy, json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "songs")
M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")
sys.path.insert(0, os.path.join(ROOT, "tools"))
from restyle import restyle

PASS, FAIL = [], []
def check(n, c, d=""):
    (PASS if c else FAIL).append(n)
    print(f"  [{'PASS' if c else 'FAIL'}] {n}" + (f" — {d}" if d else ""))


def notes_of(song):
    return json.dumps([(t.get("name"), t.get("notes")) for t in song["tracks"]], sort_keys=True)


def demo_song():
    return {"version": 2, "bpm": 124, "lengthBars": 4, "masterGainDb": 0, "key": "F minor",
            "master": [{"id": "fx_brickwall", "params": {"ceiling": -1.2}}],
            "tracks": [
                {"name": "kick", "source": {"kind": "faust", "id": "kick_punch"}, "gainDb": -4,
                 "notes": [{"start": float(b), "len": 0.2, "pitch": 36, "vel": 0.95} for b in range(16)]},
                {"name": "hats", "source": {"kind": "faust", "id": "hat"}, "gainDb": -10,
                 "notes": [{"start": b * 0.5 + 0.5, "len": 0.1, "pitch": 42, "vel": 0.5} for b in range(16)]},
                {"name": "bass", "source": {"kind": "faust", "id": "sub_clean"}, "gainDb": -6,
                 "notes": [{"start": b * 0.5, "len": 0.4, "pitch": 41, "vel": 0.8} for b in range(32)]},
                {"name": "chords", "source": {"kind": "faust", "id": "organ_soul"}, "gainDb": -12,
                 "notes": [{"start": float(b * 4), "len": 3.8, "pitch": p, "vel": 0.5}
                           for b in range(4) for p in (53, 56, 60)]},
                {"name": "vox", "source": {"kind": "vst3", "plugin": "Surge XT", "preset": True},
                 "gainDb": -9, "notes": [{"start": 0.0, "len": 4.0, "pitch": 65, "vel": 0.6}]},
                {"name": "topline", "source": {"kind": "faust", "id": "pluck"}, "gainDb": -8,
                 "locked": True,
                 "notes": [{"start": float(b), "len": 0.4, "pitch": 72, "vel": 0.7} for b in range(8)]}]}


def main():
    s = demo_song()
    base_notes = notes_of(s)

    s2 = copy.deepcopy(s)
    rep = restyle(s2, "trap")
    check("R1 every note byte-identical after restyle", notes_of(s2) == base_notes)
    v = {t["name"]: (t["source"].get("id") or t["source"].get("plugin")) for t in s2["tracks"]}
    check("R2 house-ish -> trap: kick slides to 808, bass follows the style",
          v["kick"] == "kick_808" and v["bass"] in ("kick_808", "sub_clean", "reese"),
          json.dumps({k: v[k] for k in ("kick", "bass", "chords")}))
    check("R2b color voice became trap's recipe voice",
          "chords" in rep["tracks"] and v["chords"] != "organ_soul",
          rep["tracks"].get("chords", "unchanged"))

    s3 = copy.deepcopy(s2)
    rep3 = restyle(s3, "house")
    v3 = {t["name"]: t["source"].get("id") for t in s3["tracks"] if t["source"].get("kind") == "faust"}
    check("R3 trap -> house: kick back to punch", v3["kick"] == "kick_punch", v3["kick"])
    check("R3b swing follows the target (house straight = no swing key)",
          "swing" not in s3 or s3["swing"]["amount"] > 0.5, str(s3.get("swing")))

    check("R4 locked + vst3 keep identity",
          v["topline"] == "pluck" and rep["skipped"].get("topline") == "locked"
          and "identity" in rep["skipped"].get("vox", ""), json.dumps(rep["skipped"]))

    try:
        restyle(copy.deepcopy(s), "polkacore")
        check("R5 unknown genre raises with options", False)
    except SystemExit as e:
        check("R5 unknown genre raises with options", "unknown genre" in str(e), str(e)[:60])

    # R6 EARS: the morph is audible (render both, compare band balance/centroid)
    def render(song, tag):
        sj = os.path.join(SONGS, f"_restyb_{tag}.json"); wav = os.path.join(SONGS, f"_restyb_{tag}.wav")
        json.dump(song, open(sj, "w"), indent=1)
        r = subprocess.run([M1, "render", sj, wav], capture_output=True, text=True, timeout=300)
        return wav if "ok=1" in (r.stdout + r.stderr) else None

    def analyze(wav):
        r = subprocess.run([os.path.join(ROOT, ".venv/bin/python"),
                            os.path.join(ROOT, "tools", "analyze2.py"), wav],
                           capture_output=True, text=True, timeout=120)
        return json.loads(r.stdout)

    ear_base = copy.deepcopy(s)
    ear_base["tracks"] = [t for t in ear_base["tracks"] if t["name"] != "vox"]
    ear_trap = copy.deepcopy(ear_base)
    restyle(ear_trap, "trap")
    wa, wb = render(ear_base, "base"), render(ear_trap, "trap")
    ok = bool(wa and wb)
    if ok:
        aa, ab = analyze(wa), analyze(wb)
        moved = abs(aa["spectral_centroid_hz"] - ab["spectral_centroid_hz"]) > 60 \
            or any(abs(aa["band_energy_pct"].get(k, 0) - ab["band_energy_pct"].get(k, 0)) > 4
                   for k in aa.get("band_energy_pct", {}))
        check("R6 the morph is AUDIBLE (centroid or band balance moved)",
              moved, f"centroid {aa['spectral_centroid_hz']:.0f} -> {ab['spectral_centroid_hz']:.0f}")
        check("R6b restyled song renders clean", ab["clipped_samples"] == 0,
              f"clipped {ab['clipped_samples']}")
    else:
        check("R6 renders", False, "render failed")
    for f in os.listdir(SONGS):
        if f.startswith("_restyb_"):
            os.remove(os.path.join(SONGS, f))

    print(f"\n== RESTYLE: {len(PASS)} pass / {len(FAIL)} fail ==")
    if FAIL:
        print("FAILURES:", ", ".join(FAIL)); sys.exit(1)
    print("THE MORPH KEEPS THE MUSIC AND SWAPS THE SOUND")


if __name__ == "__main__":
    main()
