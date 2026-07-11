#!/usr/bin/env python3
"""FINISH PIPELINE E2E BATTERY — traces docs/PIPELINE_E2E_SPEC.md, verifies 100%.

  pipeline_battery.py [--no-render]

Builds a controlled loop (kick + chords, NO bass/pad), runs finish (forcing every
stage), and asserts S1-S7. Any failure is a real bug. Symbolic checks are exact;
S6 renders once (accepts box contention). Exit 1 on any failure.
"""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
SONGS = os.path.join(ROOT, "songs")

import finish as F
import automix as M
from chordvote import chord_map
from reharm import parse_chord, tones

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))
    return cond


def controlled_input():
    """16-bar loop: kick + a chords track (Cm-Ab-Eb-Bb-ish), NO bass, NO pad."""
    prog = [0, 8, 3, 10]              # Cm, Ab, Eb, Bb-ish scale degrees as pitch classes
    tracks = [
        {"name": "kick", "source": {"kind": "faust", "id": "kick_808"}, "gainDb": -5,
         "pan": 0.3,                  # deliberately off-center -> automix must fix (S5)
         "notes": [{"start": b, "len": 0.25, "pitch": 36, "vel": 1.0} for b in range(64)]},
        {"name": "snare", "source": {"kind": "faust", "id": "snare"}, "gainDb": -6,
         "notes": [{"start": b, "len": 0.25, "pitch": 38, "vel": 0.8}
                   for b in range(1, 64, 2)]},     # backbeat -> fills have a target (S4.3)
        {"name": "chords", "source": {"kind": "faust", "id": "pluck"}, "gainDb": -8,
         "notes": []},
    ]
    # a clear triad per bar so chordvote has something unambiguous to read
    chords_tr = next(t for t in tracks if t["name"] == "chords")   # by NAME, not index
    for bar in range(16):
        r = prog[bar % 4] + 48
        for iv in (0, 3, 7):         # minor triad
            chords_tr["notes"].append({"start": bar * 4.0, "len": 3.5,
                                       "pitch": r + iv, "vel": 0.6})
    return {"version": 2, "bpm": 120, "lengthBars": 16, "masterGainDb": 0.0,
            "key": "C minor", "tracks": tracks}


def bar_of(beat):
    return int(beat // 4)


def main():
    no_render = "--no-render" in sys.argv
    inp = controlled_input()
    in_bars = inp["lengthBars"]
    in_track_names = {t["name"] for t in inp["tracks"]}
    json.dump(inp, open(os.path.join(SONGS, "_pipe_in.json"), "w"), indent=1)
    song = json.loads(json.dumps(inp))

    print("== running finish (traces every stage) ==")
    steps = F.finish(song)
    for s in steps:
        print("   ·", s)
    json.dump(song, open(os.path.join(SONGS, "_pipe_out.json"), "w"), indent=1)

    print("== S1 HARMONY ==")
    ch = song.get("chords", [])
    check("S1.1 chords[] present, len>=input bars", len(ch) >= in_bars,
          f"{len(ch)} chords")
    revote = [c["chord"] for c in chord_map(song)]
    orig = [c["chord"] for c in ch]
    # compare the overlap (revote may cover more bars post-arrange)
    n = min(len(revote), len(orig))
    stable = sum(1 for a, b in zip(orig[:n], revote[:n]) if a == b)
    check("S1.2 re-vote reproduces chords (>=90%)", n > 0 and stable / n >= 0.9,
          f"{stable}/{n} stable")

    print("== S2 STRUCTURE ==")
    check("S2.1 lengthBars increased", float(song["lengthBars"]) > in_bars,
          f"{in_bars} -> {song['lengthBars']}")
    secs = song.get("sections", [])
    starts = [float(s["startBar"]) for s in secs]
    check("S2.2 >=2 sections", len(secs) >= 2, f"{len(secs)}")
    check("S2.3 startBars strictly increasing", starts == sorted(starts) and len(set(starts)) == len(starts))
    check("S2.4 first section at bar 0", len(starts) > 0 and starts[0] == 0.0)
    check("S2.5 all startBars < lengthBars", all(s < float(song["lengthBars"]) for s in starts))

    print("== S3 HARMONIZE ==")
    names = {t["name"] for t in song["tracks"]}
    check("S3.1 bass track added", "bass" in names and "bass" not in in_track_names)
    check("S3.2 pad track added", "pad" in names and "pad" not in in_track_names)
    bass = next((t for t in song["tracks"] if t["name"] == "bass"), None)
    if bass and ch:
        chords_by_bar = {c["bar"]: c["chord"] for c in ch}
        hit = tot = 0
        for nt in bass["notes"]:
            if abs(nt["start"] % 4) > 1e-6:
                continue                 # downbeats only
            bar = bar_of(nt["start"]) + 1
            lab = chords_by_bar.get(bar) or chords_by_bar.get(((bar - 1) % len(ch)) + 1)
            if not lab:
                continue
            r, q, d = parse_chord(lab)
            root_fifth = {r % 12, (r + 7) % 12}
            tot += 1
            hit += (nt["pitch"] % 12 in root_fifth)
        check("S3.3 bass downbeats are chord root/fifth (>=80%)", tot > 0 and hit / tot >= 0.8,
              f"{hit}/{tot}")
    else:
        check("S3.3 bass downbeats are chord root/fifth", False, "no bass/chords")
    # sectioned density gradient on a harmonized part
    def density(track, lo_bar, hi_bar):
        n = sum(1 for x in track["notes"] if lo_bar <= bar_of(x["start"]) < hi_bar)
        return n / max(hi_bar - lo_bar, 1)
    lab_bar = [(str(s.get("name", "")).lower(), float(s["startBar"])) for s in secs]
    def span(i):
        return (lab_bar[i][1], lab_bar[i + 1][1] if i + 1 < len(lab_bar) else float(song["lengthBars"]))
    busy = [i for i, (l, _) in enumerate(lab_bar) if any(k in l for k in ("drop", "main", "finale", "chorus"))]
    sparse = [i for i, (l, _) in enumerate(lab_bar) if any(k in l for k in ("intro", "break", "outro"))]
    pad = next((t for t in song["tracks"] if t["name"] == "pad"), None)
    if busy and sparse and pad:
        bl, bh = span(busy[0]); sl, sh = span(sparse[0])
        db, ds = density(pad, int(bl), int(bh)), density(pad, int(sl), int(sh))
        check("S3.4 sectioned density: busy > 1.5x sparse", ds == 0 or db > ds * 1.5,
              f"busy {db:.1f} vs sparse {ds:.1f} notes/bar")
    else:
        check("S3.4 sectioned density gradient", False, "missing busy/sparse/pad")

    print("== S4 TRANSITIONS ==")
    riser = next((t for t in song["tracks"] if t["name"] == "riser"), None)
    check("S4.1 riser track exists", riser is not None)
    if riser:
        sec_bars = set(int(s) for s in starts)
        # riser start/len are in BEATS; a section boundary is a BAR (beats/4)
        ends_ok = all(int(round((n["start"] + n["len"]) / 4.0)) in sec_bars for n in riser["notes"])
        check("S4.2 riser notes end at section boundaries", len(riser["notes"]) > 0 and ends_ok,
              f"{len(riser['notes'])} risers")
    snare = next((t for t in song["tracks"] if t["name"] in ("snare", "clap")), None)
    # fills: find a fill bar (bar before a drop) and check accel
    if snare:
        fill_ok = False
        for i, (l, sb) in enumerate(lab_bar):
            if any(k in l for k in ("drop", "main", "finale")) and sb >= 1:
                fb = int(sb) - 1
                hits = sorted(n["start"] for n in snare["notes"] if fb * 4 <= n["start"] < sb * 4)
                if len(hits) >= 8:
                    gaps = [round(hits[k + 1] - hits[k], 4) for k in range(len(hits) - 1)]
                    if all(gaps[k] >= gaps[k + 1] - 1e-9 for k in range(len(gaps) - 1)):
                        fill_ok = True
                        break
        check("S4.3 fill: >=8 accelerating snare hits in a fill bar", fill_ok)
    else:
        check("S4.3 fill present", False, "no snare/clap")
    dl_ok = any(a.get("target", "").startswith("fx[") and a["target"].endswith(".cutoff")
                and any(p.get("v", 0) >= 18000 for p in a.get("points", []))
                and any(p.get("v", 1e9) < 1000 for p in a.get("points", []))
                for t in song["tracks"] for a in t.get("automation", []))
    check("S4.4 downlifter: falling fx_filter cutoff automation", dl_ok)

    print("== S5 AUTOMIX ==")
    subs_ok = all(abs(float(t.get("pan", 0))) < 1e-6 and
                  not any(f.get("id") == "fx_widen" for f in t.get("fx", []))
                  for t in song["tracks"] if M.role(t) in ("kick", "bass"))
    check("S5.1 subs/kick centered + no widener", subs_ok)
    pads = [t for t in song["tracks"] if M.role(t) == "pad"]
    check("S5.2 pads widened", len(pads) > 0 and all(any(f.get("id") == "fx_widen" for f in t.get("fx", [])) for t in pads))

    print("== S6 INTEGRITY ==")
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("dm", os.path.join(ROOT, "agent", "daw_mcp.py"))
        dm = importlib.util.module_from_spec(spec)
        _argv = sys.argv; sys.argv = ["x"]; spec.loader.exec_module(dm); sys.argv = _argv
        errs = dm.validate_song(song)
        check("S6.1 validate_song: 0 errors", len(errs) == 0, "; ".join(errs[:3]))
    except Exception as e:
        check("S6.1 validate_song: 0 errors", False, f"exec err: {e}")
    if not no_render:
        M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")
        wav = os.path.join(SONGS, "_pipe_out.wav")
        r = subprocess.run([M1, "render", os.path.join(SONGS, "_pipe_out.json"), wav],
                           capture_output=True, text=True, timeout=600)
        rendered = "ok=1" in (r.stdout + r.stderr) and os.path.exists(wav)
        check("S6.2 renders without crash", rendered)
        if rendered:
            import numpy as np, soundfile as sf
            from scipy.signal import butter, sosfilt
            x, sr = sf.read(wav, always_2d=True)
            clipped = int((np.abs(x) >= 0.999).sum())
            check("S6.3 clipped_samples == 0", clipped == 0, f"{clipped} clipped")
            side = (x[:, 0] - x[:, 1]) / 2 if x.shape[1] > 1 else x[:, 0] * 0
            sub_side = sosfilt(butter(4, 120, "lp", fs=sr, output="sos"), side)
            sub = sosfilt(butter(4, 120, "lp", fs=sr, output="sos"), x.mean(axis=1))
            ratio = float(np.sqrt((sub_side ** 2).mean()) / (np.sqrt((sub ** 2).mean()) + 1e-9))
            check("S6.4 sub mono-safe (<0.15)", ratio < 0.15, f"side-ratio {ratio:.3f}")
    else:
        print("  (S6.2-4 render checks skipped: --no-render)")

    print("== S7 IDEMPOTENCY ==")
    before_risers = sum(1 for t in song["tracks"] if t["name"] == "riser")
    before_bars = float(song["lengthBars"])
    song2 = json.loads(json.dumps(song))
    F.finish(song2)
    after_risers = sum(1 for t in song2["tracks"] if t["name"] == "riser")
    check("S7.1 riser not duplicated on re-run", after_risers == before_risers == 1,
          f"{before_risers}->{after_risers}")
    check("S7.2 not re-arranged on re-run", float(song2["lengthBars"]) == before_bars)
    try:
        errs2 = dm.validate_song(song2)
        check("S7.3 still valid after 2nd finish", len(errs2) == 0, "; ".join(errs2[:2]))
    except Exception:
        check("S7.3 still valid after 2nd finish", False)

    for f in ("_pipe_in.json", "_pipe_out.json", "_pipe_out.wav"):
        p = os.path.join(SONGS, f)
        os.path.exists(p) and os.remove(p)

    print(f"\n== VERDICT: {len(PASS)} pass / {len(FAIL)} fail ==")
    if FAIL:
        print("FAILURES:", ", ".join(FAIL))
        sys.exit(1)
    print("PIPELINE E2E: 100% VERIFIED")


if __name__ == "__main__":
    main()
