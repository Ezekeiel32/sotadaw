#!/usr/bin/env python3
"""ARC QUALITY — does the full producer arc make music that's actually GOOD?

Every other battery checks VALIDITY (0 clipped, on-chord, scoped). This checks
QUALITY BY THE EARS: a deliberately-rough loop → finish + prescribe → render →
analyze2 must certify the output is release-shaped (headroom, mono-safe, balanced
bands, no clipping) AND that the arc measurably IMPROVED the rough input.
Exit 1 on any failure."""
import importlib.util, json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "songs")
M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")
sys.path.insert(0, os.path.join(ROOT, "tools"))
import finish as F
import prescribe as P
import doctor as D
from chordvote import chord_map

PASS, FAIL = [], []
def check(n, c, d=""):
    (PASS if c else FAIL).append(n)
    print(f"  [{'PASS' if c else 'FAIL'}] {n}" + (f" — {d}" if d else ""))


def rough_loop():
    """a deliberately-rough 16-bar loop: off-center sub, mechanical parts, no
    structure, no master — the arc has real work to do."""
    prog = [0, 8, 3, 10]
    tr = [
        {"name": "kick", "source": {"kind": "faust", "id": "kick_808"}, "gainDb": -4, "pan": 0.35,
         "notes": [{"start": b, "len": 0.25, "pitch": 36, "vel": 1.0} for b in range(64)]},
        {"name": "bass", "source": {"kind": "faust", "id": "bass_warm"}, "gainDb": -5, "pan": -0.3,
         "fx": [{"id": "fx_widen", "params": {"width": 1.6}}],
         "notes": [{"start": i * 0.5, "len": 0.4, "pitch": 40, "vel": 0.8} for i in range(32)]},
        {"name": "lead", "source": {"kind": "faust", "id": "pluck"}, "gainDb": -6,
         "notes": [{"start": i * 0.5, "len": 0.4, "pitch": 60 + (i % 5), "vel": 0.8} for i in range(32)]},
        {"name": "chords", "source": {"kind": "faust", "id": "pluck"}, "gainDb": -8, "notes": []},
    ]
    for bar in range(16):
        r = prog[bar % 4] + 48
        for iv in (0, 3, 7):
            tr[3]["notes"].append({"start": bar * 4.0, "len": 3.5, "pitch": r + iv, "vel": 0.6})
    return {"version": 2, "bpm": 124, "lengthBars": 16, "masterGainDb": 0, "key": "C minor", "tracks": tr}


def analyze(wav):
    r = subprocess.run([os.path.join(ROOT, ".venv/bin/python"), os.path.join(ROOT, "tools", "analyze2.py"), wav],
                       capture_output=True, text=True, timeout=120)
    return json.loads(r.stdout)


def main():
    rough = rough_loop()
    rough["chords"] = chord_map(rough)
    rough_issues = len(D.diagnose(rough))
    print(f"== rough input: {rough_issues} doctor issues, {rough['lengthBars']} bars ==")

    song = json.loads(json.dumps(rough))
    steps = F.finish(song)
    for s in steps:
        print("   ·", s)
    rep = P.prescribe(song)
    print("   · prescribe:", rep["applied"])
    final_issues = len(D.diagnose(song))

    check("arc reduced fixable issues", final_issues < rough_issues, f"{rough_issues} -> {final_issues}")
    check("arc added structure (bars grew)", float(song["lengthBars"]) > 16, f"16 -> {song['lengthBars']}")
    comp = [c for c, _, _ in D.diagnose(song) if c.startswith("C")]
    check("arc output is compositionally complete (no C-issues)", not comp, f"{comp or 'clean'}")

    out = os.path.join(SONGS, "_arc_q.json")
    json.dump(song, open(out, "w"), indent=1)
    wav = os.path.join(SONGS, "_arc_q.wav")
    r = subprocess.run([M1, "render", out, wav], capture_output=True, text=True, timeout=600)
    if "ok=1" not in (r.stdout + r.stderr):
        check("renders", False, "render failed"); _finish()
        return
    m = analyze(wav)
    print(f"== ears: LUFS {m['lufs_integrated']}, dBTP {m['true_peak_dbtp']}, "
          f"clipped {m['clipped_samples']}, width {m['stereo_width_db']}dB, corr {m['lr_correlation']} ==")

    # THE EARS' QUALITY VERDICT
    check("Q1 zero clipped samples", m["clipped_samples"] == 0, f"{m['clipped_samples']}")
    check("Q2 true peak <= -1.0 dBTP (streaming standard)", m["true_peak_dbtp"] <= -1.0, f"{m['true_peak_dbtp']}")
    check("Q3 loudness in a musical range (-24..-6 LUFS)", -24 <= m["lufs_integrated"] <= -6, f"{m['lufs_integrated']}")
    check("Q4 mono-compatible (lr_correlation >= 0.3)", m["lr_correlation"] >= 0.3, f"{m['lr_correlation']}")
    bands = m.get("band_energy_pct", {})
    if bands:
        dom = max(bands.values())
        check("Q5 no band absurdly dominant (<78%)", dom < 78, f"max band {dom}%")
    else:
        check("Q5 band data present", False)
    check("Q6 stereo width present but sane (-30..0 dB)", -30 <= m["stereo_width_db"] <= 0, f"{m['stereo_width_db']}")

    for f in ("_arc_q.json", "_arc_q.wav"):
        p = os.path.join(SONGS, f)
        os.path.exists(p) and os.remove(p)
    print(f"\n== ARC QUALITY: {len(PASS)} pass / {len(FAIL)} fail ==")
    if FAIL:
        print("FAILURES:", ", ".join(FAIL)); sys.exit(1)
    print("THE ARC MAKES RELEASE-SHAPED MUSIC (ears-verified)")


def _finish():
    for f in ("_arc_q.json", "_arc_q.wav"):
        p = os.path.join(SONGS, f)
        os.path.exists(p) and os.remove(p)
    sys.exit(1)


if __name__ == "__main__":
    main()
