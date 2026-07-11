#!/usr/bin/env python3
"""COLOR battery — the semantic axes move the SOUND, not just the JSON.

Symbolic:
  K1 wider NEVER touches kick/bass/808 (mono law), does widen pads
  K2 locked tracks untouched; vst3/preset tracks honestly skipped with a note
  K3 repeats CLAMP: 10x warmer floors at CUT_FLOOR; 10x wider caps at WIDTH_CAP
  K4 brighter re-opens a darkened filter (the axes are inverses around cutoff)
  K5 unknown word errors naming the palette
EARS (renders a tiny song through m1 + analyze2):
  K6 centroid ordering: warmer < base < brighter
  K7 wider raises stereo width vs base while the bass stays un-widened
Exit 1 on any failure."""
import copy, json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "songs")
M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")
sys.path.insert(0, os.path.join(ROOT, "tools"))
from color import color, CUT_FLOOR, WIDTH_CAP

PASS, FAIL = [], []
def check(n, c, d=""):
    (PASS if c else FAIL).append(n)
    print(f"  [{'PASS' if c else 'FAIL'}] {n}" + (f" — {d}" if d else ""))


def base_song():
    return {"version": 2, "bpm": 120, "lengthBars": 2, "masterGainDb": 0,
            "tracks": [
                {"name": "kick", "source": {"kind": "faust", "id": "kick_808"}, "gainDb": -5,
                 "notes": [{"start": float(b), "len": 0.25, "pitch": 36, "vel": 0.9} for b in range(8)]},
                {"name": "bass", "source": {"kind": "faust", "id": "bass_warm"}, "gainDb": -6,
                 "notes": [{"start": b * 0.5, "len": 0.4, "pitch": 40, "vel": 0.8} for b in range(16)]},
                {"name": "pad", "source": {"kind": "faust", "id": "strings_disco"}, "gainDb": -8,
                 "notes": [{"start": 0.0, "len": 8.0, "pitch": p, "vel": 0.6} for p in (60, 64, 67)]},
                {"name": "lead", "source": {"kind": "faust", "id": "pluck"}, "gainDb": -7, "locked": True,
                 "notes": [{"start": b * 0.5, "len": 0.3, "pitch": 72 + (b % 4), "vel": 0.8} for b in range(16)]},
                {"name": "synth", "source": {"kind": "vst3", "plugin": "Dexed",
                                             "params": {"Cutoff": 0.5}}, "gainDb": -9,
                 "notes": [{"start": float(b), "len": 0.5, "pitch": 55, "vel": 0.7} for b in range(8)]}]}


def analyze(wav):
    r = subprocess.run([os.path.join(ROOT, ".venv/bin/python"),
                        os.path.join(ROOT, "tools", "analyze2.py"), wav],
                       capture_output=True, text=True, timeout=120)
    return json.loads(r.stdout)


def render(song, tag):
    sj = os.path.join(SONGS, f"_colorb_{tag}.json")
    wav = os.path.join(SONGS, f"_colorb_{tag}.wav")
    json.dump(song, open(sj, "w"), indent=1)
    r = subprocess.run([M1, "render", sj, wav], capture_output=True, text=True, timeout=300)
    return wav if "ok=1" in (r.stdout + r.stderr) else None


def cleanup():
    for f in os.listdir(SONGS):
        if f.startswith("_colorb_"):
            os.remove(os.path.join(SONGS, f))


def main():
    s = base_song()

    # K1 mono law
    s1 = copy.deepcopy(s)
    rep = color(s1, "wider", 1.0)
    tr = {t["name"]: t for t in s1["tracks"]}
    def widened(t):
        return any(f.get("id") == "fx_widen" for f in t.get("fx", []))
    check("K1 wider skips kick+bass (mono law), widens the pad",
          not widened(tr["kick"]) and not widened(tr["bass"]) and widened(tr["pad"])
          and "mono law" in rep["skipped"].get("bass", ""), json.dumps(rep["skipped"]))

    # K2 locked + vst3 honesty
    check("K2 locked lead untouched; vst3 synth skipped with the agent-lane note",
          "lead" in rep["skipped"] and rep["skipped"]["lead"] == "locked"
          and "vst3" in rep["skipped"].get("synth", ""),
          rep["skipped"].get("synth", "")[:60])
    check("K2b locked track fx byte-identical",
          json.dumps(tr["lead"].get("fx")) == json.dumps(next(
              t for t in s["tracks"] if t["name"] == "lead").get("fx")))

    # K3 clamps
    s3 = copy.deepcopy(s)
    for _ in range(10):
        color(s3, "warmer", 1.0)
        color(s3, "wider", 1.0)
    t3 = {t["name"]: t for t in s3["tracks"]}
    cut = next(f for f in t3["pad"]["fx"] if f.get("id") == "fx_filter")["params"]["cutoff"]
    wid = next(f for f in t3["pad"]["fx"] if f.get("id") == "fx_widen")["params"]["width"]
    check("K3 ten repeats clamp (cutoff floor, width cap)",
          cut >= CUT_FLOOR and wid <= WIDTH_CAP, f"cutoff {cut}, width {wid}")

    # K4 brighter re-opens a darkened filter
    s4 = copy.deepcopy(s)
    color(s4, "darker", 0.8)
    dark_cut = next(f for f in {t["name"]: t for t in s4["tracks"]}["pad"]["fx"]
                    if f.get("id") == "fx_filter")["params"]["cutoff"]
    color(s4, "brighter", 0.8)
    bright_cut = next(f for f in {t["name"]: t for t in s4["tracks"]}["pad"]["fx"]
                      if f.get("id") == "fx_filter")["params"]["cutoff"]
    check("K4 brighter re-opens a darkened filter", bright_cut > dark_cut * 1.3,
          f"{dark_cut} -> {bright_cut}")

    # K5 unknown word
    try:
        color(copy.deepcopy(s), "sparklier")
        check("K5 unknown word raises with the palette", False)
    except SystemExit as e:
        check("K5 unknown word raises with the palette", "warmer" in str(e), str(e)[:60])

    # EARS: drop the vst3 track (may not be installed) + unlock lead for rendering truth
    ear = copy.deepcopy(s)
    ear["tracks"] = [t for t in ear["tracks"] if t["name"] != "synth"]
    warm = copy.deepcopy(ear); color(warm, "warmer", 0.9)
    bright = copy.deepcopy(ear); color(bright, "brighter", 0.9)
    wide = copy.deepcopy(ear); color(wide, "wider", 1.0)
    wb, ww, wbr, wwd = render(ear, "base"), render(warm, "warm"), render(bright, "bright"), render(wide, "wide")
    if not all((wb, ww, wbr, wwd)):
        check("K6 renders", False, "a render failed")
        cleanup(); sys.exit(1)
    ab, aw, abr, awd = analyze(wb), analyze(ww), analyze(wbr), analyze(wwd)
    check("K6 EARS centroid ordering: warmer < base < brighter",
          aw["spectral_centroid_hz"] < ab["spectral_centroid_hz"] < abr["spectral_centroid_hz"],
          f"{aw['spectral_centroid_hz']:.0f} < {ab['spectral_centroid_hz']:.0f} < {abr['spectral_centroid_hz']:.0f}")
    check("K7 EARS wider raises stereo width vs base",
          awd["stereo_width_db"] > ab["stereo_width_db"] + 1.0,
          f"{ab['stereo_width_db']} -> {awd['stereo_width_db']} dB")
    wide_tr = {t["name"]: t for t in wide["tracks"]}
    check("K7b the bass carries no widener in the wide render",
          not any(f.get("id") == "fx_widen" for f in wide_tr["bass"].get("fx", [])))

    cleanup()
    print(f"\n== COLOR: {len(PASS)} pass / {len(FAIL)} fail ==")
    if FAIL:
        print("FAILURES:", ", ".join(FAIL)); sys.exit(1)
    print("SEMANTIC AXES MOVE THE SOUND (ears-verified, mix-law safe)")


if __name__ == "__main__":
    main()
