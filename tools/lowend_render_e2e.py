#!/usr/bin/env python3
"""LOW-END RENDER E2E (wave 16) — the circle proof for THE LOW-END EARS.

Plants the crime the SYMBOLIC court cannot see: two opposite-panned low
pads at DIFFERENT pitches (no 'sub' in any name, no widen fx — symbolic
lowend_court stays green) -> renders through the REAL engine (m1) ->
the ears must convict wide_sub on the wav -> heal_sub_mono lands the
master fx_ms_eq (pre-wall) -> ONE re-render -> the ears must pass.

Skip-safe: missing m1 binary -> SKIP (exit 0 with notice).
"""
import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")


def main():
    if not os.path.exists(M1):
        print("lowend_render_e2e: SKIP (no m1 binary)")
        return 0
    import lowend_court as LC
    import lowend_ears as LE

    tmp = tempfile.mkdtemp(prefix="lowend_e2e_")
    notes_a = [{"start": float(b), "len": 3.8, "pitch": 33, "vel": 0.9}
               for b in range(0, 16, 4)]                       # A1 left
    notes_b = [{"start": float(b), "len": 3.8, "pitch": 34, "vel": 0.9}
               for b in range(0, 16, 4)]                       # Bb1 right
    song = {
        "bpm": 120, "lengthBars": 4,
        "master": [{"id": "fx_truepeak", "params": {"ceiling": -1.2}}],
        "tracks": [
            {"name": "pad_left", "pan": -1.0, "gainDb": -3,
             "source": {"id": "sub_808_slide"}, "notes": notes_a},
            {"name": "pad_right", "pan": 1.0, "gainDb": -3,
             "source": {"id": "sub_808_slide"}, "notes": notes_b},
        ]}
    sym = LC.court_lowend(song, "house")
    if not sym["ok"]:
        print(f"lowend_render_e2e: RED — the plant must EVADE the symbolic "
              f"court (it flagged: {json.dumps(sym)[:200]})")
        return 1
    sj = os.path.join(tmp, "wide.json")
    wav = os.path.join(tmp, "wide.wav")
    json.dump(song, open(sj, "w"), indent=1)
    r = subprocess.run([M1, "render", sj, wav], capture_output=True,
                       text=True, timeout=420)
    if r.returncode != 0 or not os.path.exists(wav):
        print(f"lowend_render_e2e: RED — render failed: {r.stderr[-300:]}")
        return 1
    v = LE.court_ears(wav, song, "house", heal=True)
    sm = v["sub_mono"]
    if sm.get("ok", True) or not any(f["kind"] == "wide_sub"
                                     for f in sm.get("flags", [])):
        print(f"lowend_render_e2e: RED — planted stereo sub NOT convicted "
              f"on the real render: {json.dumps(sm)[:240]}")
        return 1
    if not (v.get("heals") or {}).get("sub_mono"):
        print("lowend_render_e2e: RED — no heal landed")
        return 1
    if song["master"][0].get("id") != "fx_ms_eq":
        print(f"lowend_render_e2e: RED — heal must insert fx_ms_eq BEFORE "
              f"the wall: {json.dumps(song['master'])[:200]}")
        return 1
    json.dump(song, open(sj, "w"), indent=1)
    wav2 = os.path.join(tmp, "healed.wav")
    r = subprocess.run([M1, "render", sj, wav2], capture_output=True,
                       text=True, timeout=420)
    if r.returncode != 0 or not os.path.exists(wav2):
        print(f"lowend_render_e2e: RED — heal re-render failed: "
              f"{r.stderr[-300:]}")
        return 1
    v2 = LE.court_sub_mono(wav2, song, "house")
    m0 = sm.get("metrics", {})
    m1_ = v2.get("metrics", {})
    if not v2.get("ok", True):
        print(f"lowend_render_e2e: RED — healed render still wide: "
              f"{json.dumps(v2)[:240]}")
        return 1
    import shutil
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"lowend_render_e2e: GREEN — stereo sub convicted on the real "
          f"render (corr {m0.get('sub_corr')}, side {m0.get('side_ratio', m0.get('sub_side_ratio'))}) "
          f"-> ms_eq heal -> re-render passes "
          f"(corr {m1_.get('sub_corr', 'quiet')}, side {m1_.get('sub_side_ratio', '-')})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
