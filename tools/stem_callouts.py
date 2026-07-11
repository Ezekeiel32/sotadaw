#!/usr/bin/env python3
"""V28 PER-STEM CALLOUTS — the ears go track-by-track.

stem_callouts.py <song> [--json] [--keep]

Renders stems (m1 render-stems), analyzes EACH track solo, then cross-examines pairs:
who's silent, who clips alone, who's carrying mud that isn't theirs to carry, which two
tracks are fighting over the same band (masking), who has phase risk. Every callout is
addressed to a TRACK and names the move — that's what makes it a callout, not a stat.
"""
import argparse, json, os, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from analyze2 import analyze  # noqa: E402

M1 = os.path.join(ROOT, "app/build/m1_artefacts/Release/m1")
BANDS = ["low_20_120", "lowmid_120_500", "mid_500_2k", "himid_2k_6k", "high_6k_up"]
BASS_WORDS = ("808", "bass", "sub", "kick", "low", "reese")


def by_section(j, d, stems):
    """V28 finish — callouts PINNED TO THE TIMELINE: per-section stem analysis, so a
    masking fight names the bars it happens in. Arrangement-aware by construction:
    a track silent in a section is the ARRANGEMENT, not a finding."""
    import numpy as np
    from scipy.io import wavfile
    song = json.load(open(j))
    bpm = float(song.get("bpm", 120))
    secs = song.get("sections") or []
    if len(secs) < 2:
        return []
    total_beats = float(song.get("lengthBars", 8)) * 4.0
    wins = []
    for i, s in enumerate(secs):
        b0 = float(s.get("startBar", 0)) * 4.0
        b1 = float(secs[i + 1].get("startBar", 0)) * 4.0 if i + 1 < len(secs) else total_beats
        wins.append((s.get("name", f"sec{i}"), b0, b1))
    spb = 60.0 / bpm

    data = {}
    for f in stems:
        track = f.split("_", 1)[1][:-4] if "_" in f else f[:-4]
        sr, x = wavfile.read(os.path.join(d, f))
        x = x.astype(np.float64) / (32768.0 if x.dtype == np.int16 else 2147483648.0 if x.dtype == np.int32 else 1.0)
        if x.ndim > 1:
            x = x.mean(axis=1)
        data[track] = (sr, x)

    out = []
    for name, b0, b1 in wins:
        active = {}
        for track, (sr, x) in data.items():
            seg = x[int(b0 * spb * sr): int(b1 * spb * sr)]
            if len(seg) < 256:
                continue
            rms = float(np.sqrt(np.mean(seg ** 2)))
            rms_db = 20 * np.log10(rms) if rms > 1e-9 else -120.0
            if rms_db <= -45:
                continue                        # silent here = the arrangement, not a finding
            X = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
            fr = np.fft.rfftfreq(len(seg), 1 / sr)
            tot = float((X ** 2).sum()) + 1e-12
            bands = {}
            for b, (lo, hi) in zip(BANDS, ((20, 120), (120, 500), (500, 2000), (2000, 6000), (6000, sr / 2))):
                m2 = (fr >= lo) & (fr < hi)
                bands[b] = float((X[m2] ** 2).sum()) / tot * 100.0
            clipped = int(np.sum(np.abs(seg) >= 0.999))
            active[track] = {"rms_db": round(rms_db, 1), "bands": bands, "clipped": clipped,
                             "dom": max(BANDS, key=lambda bb: bands[bb])}
        bars = f"bars {int(b0 // 4) + 1}-{int(b1 // 4)}"
        for track, m in active.items():
            if m["clipped"] > 0:
                out.append({"section": name, "bars": bars, "track": track,
                            "issue": f"clips solo ({m['clipped']})",
                            "move": "this SECTION is the hot one: automate a dip here, not a global trim"})
        names = sorted(active)
        for i1 in range(len(names)):
            for i2 in range(i1 + 1, len(names)):
                t1, t2 = names[i1], names[i2]
                b = active[t1]["dom"]
                if b == "low_20_120" and all(any(w in t.lower() for w in BASS_WORDS) for t in (t1, t2)):
                    continue                    # kick/808 layering is the recipe
                if active[t2]["dom"] == b and active[t1]["bands"][b] > 55 and active[t2]["bands"][b] > 55:
                    out.append({"section": name, "bars": bars, "track": f"{t1} + {t2}",
                                "issue": f"masking fight in {b} HERE",
                                "move": "carve/sidechain/pan IN THIS SECTION (automation, not a global cut)"})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("song")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--keep", help="keep stems in this dir")
    ap.add_argument("--by-section", action="store_true",
                    help="pin callouts to the timeline (per-section stem analysis)")
    a = ap.parse_args()
    j = a.song if a.song.endswith(".json") else os.path.join(ROOT, "songs", f"{a.song}.json")
    if not os.path.exists(j):
        sys.exit(f"no such song: {j}")
    d = a.keep or tempfile.mkdtemp(prefix="stems_")
    os.makedirs(d, exist_ok=True)
    r = subprocess.run([M1, "render-stems", j, d], capture_output=True, text=True)
    stems = sorted(f for f in os.listdir(d) if f.endswith(".wav"))
    if not stems:
        sys.exit(f"render-stems produced nothing: {(r.stdout + r.stderr)[-300:]}")

    rep, callouts = {}, []
    for f in stems:
        track = f.split("_", 1)[1][:-4] if "_" in f else f[:-4]
        m = analyze(os.path.join(d, f))
        rep[track] = m
        bassy = any(w in track.lower() for w in BASS_WORDS)
        if m["rms_db"] <= -55:
            callouts.append({"track": track, "issue": "inaudible",
                             "move": "raise gainDb or delete the track — it's not earning its slot"})
            continue
        if m["clipped_samples"] > 0:
            callouts.append({"track": track, "issue": f"clips SOLO ({m['clipped_samples']} samples)",
                             "move": "source too hot: drop gainDb 3-6 or reduce voice gain zone / drive"})
        if not bassy and m["band_energy_pct"]["lowmid_120_500"] + m["band_energy_pct"]["low_20_120"] > 60:
            callouts.append({"track": track, "issue": "carrying low weight that isn't its job",
                             "move": "highpass it (fx_filter) or voice it up an octave — leave the floor to the 808"})
        if m["lr_correlation"] is not None and m["lr_correlation"] < -0.05:
            callouts.append({"track": track, "issue": f"phase risk (L/R corr {m['lr_correlation']})",
                             "move": "narrow fx_widen / recentre — this cancels in mono"})

    # masking: two audible tracks whose dominant band matches, both concentrated there
    loud = {t: m for t, m in rep.items() if m["rms_db"] > -40}
    doms = {t: max(BANDS, key=lambda b: m["band_energy_pct"][b]) for t, m in loud.items()}
    seen = set()
    for t1 in loud:
        for t2 in loud:
            if t1 >= t2 or (t1, t2) in seen:
                continue
            seen.add((t1, t2))
            b = doms[t1]
            if b == "low_20_120" and all(any(w in t.lower() for w in BASS_WORDS) for t in (t1, t2)):
                continue   # kick/808 low-band layering IS the recipe (sound-palette law), not a fight
            if doms[t2] == b and rep[t1]["band_energy_pct"][b] > 55 and rep[t2]["band_energy_pct"][b] > 55:
                callouts.append({"track": f"{t1} + {t2}", "issue": f"masking fight in {b}",
                                 "move": "carve one: EQ bell cut / different octave / pan them apart / sidechain the loser"})

    out = {"song": os.path.basename(j)[:-5], "stems": len(stems),
           "per_track": {t: {"rms_db": m["rms_db"], "clipped": m["clipped_samples"],
                             "dominant_band": doms.get(t, "quiet"),
                             "bands": m["band_energy_pct"]} for t, m in rep.items()},
           "callouts": callouts}
    if a.by_section:
        out["by_section"] = by_section(j, d, stems)
    if not a.keep:
        shutil.rmtree(d, ignore_errors=True)
    if a.json:
        print(json.dumps(out, indent=1))
        return
    print(f"STEM CALLOUTS — {out['song']} ({out['stems']} stems)")
    for t, m in out["per_track"].items():
        print(f"  {t:<10} rms {m['rms_db']:>7} dB  dominant {m['dominant_band']}")
    if not callouts:
        print("  no callouts — every track sits clean solo and nobody's fighting.")
    for c in callouts:
        print(f"  [{c['track']}] {c['issue']}\n      -> {c['move']}")
    if out.get("by_section"):
        print("PINNED TO THE TIMELINE:")
        for c in out["by_section"]:
            print(f"  [{c['section']} · {c['bars']}] {c['track']}: {c['issue']}\n      -> {c['move']}")
    elif a.by_section:
        print("  (sections: no per-section findings — the fights, if any, are global)")


if __name__ == "__main__":
    main()
