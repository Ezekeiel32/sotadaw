#!/usr/bin/env python3
"""SOUND COURT RENDER E2E (wave 20) — the circle proof.

Renders a 4-lane song through the REAL engine (m1 render-stems), courts
the actual stems: the lawful take must pass (no wolf on real voices),
and a PLANTED crime — the pluck voice wearing a pad's name — must
convict on the measured attack class, then heal via the voice's own
attack zone. Skip-safe: no m1 -> SKIP."""
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
        print("sound_court_e2e: SKIP (no m1 binary)")
        return 0
    import sound_court as SC

    tmp = tempfile.mkdtemp(prefix="sound_e2e_")
    beats = [{"start": float(b), "len": 0.5, "pitch": 36, "vel": 0.9}
             for b in range(0, 16)]
    subn = [{"start": float(b), "len": 0.9, "pitch": 33, "vel": 0.85}
            for b in range(0, 16, 2)]
    plk = [{"start": float(b) + 0.5, "len": 0.4, "pitch": 64, "vel": 0.8}
           for b in range(0, 16, 2)]
    song = {"bpm": 120, "lengthBars": 4,
            "master": [{"id": "fx_truepeak", "params": {"ceiling": -1.2}}],
            "tracks": [
                {"name": "kick", "source": {"id": "kick_808"},
                 "notes": beats},
                {"name": "sub_808", "source": {"id": "sub_808_slide"},
                 "notes": subn},
                # THE PLANT: a pluck voice wearing a pad's name
                {"name": "dream_pad", "source": {"id": "pluck"},
                 "notes": plk},
            ]}
    sj = os.path.join(tmp, "e2e.json")
    stems = os.path.join(tmp, "stems")
    json.dump(song, open(sj, "w"), indent=1)
    r = subprocess.run([M1, "render-stems", sj, stems],
                       capture_output=True, text=True, timeout=420)
    if r.returncode != 0 or not os.path.isdir(stems):
        print(f"sound_court_e2e: RED — render-stems failed: "
              f"{r.stderr[-300:]}")
        return 1
    v = SC.court_stems(stems, song, "house")
    kick_v = next((w for k, w in v["stems"].items() if "kick" in k), {})
    sub_v = next((w for k, w in v["stems"].items() if "sub" in k), {})
    pad_v = next((w for k, w in v["stems"].items() if "pad" in k), {})
    if not kick_v.get("ok", False) or not sub_v.get("ok", False):
        print(f"sound_court_e2e: RED — lawful kick/sub convicted (wolf): "
              f"{json.dumps({'kick': kick_v, 'sub': sub_v})[:400]}")
        return 1
    att = [f for f in pad_v.get("flags", []) if f["kind"] == "attack_class"]
    if not att:
        print(f"sound_court_e2e: RED — planted pluck-as-pad NOT caught: "
              f"{json.dumps(pad_v)[:400]}")
        return 1
    feats = pad_v.get("features") or {}
    print(f"sound_court_e2e: GREEN — real stems courted: kick "
          f"{(kick_v.get('features') or {}).get('centroid_hz')}Hz/"
          f"{(kick_v.get('features') or {}).get('attack_ms')}ms ok, sub ok, "
          f"'dream_pad' convicted at {feats.get('attack_ms')}ms attack "
          f"(pad class needs >=50ms)")
    import shutil
    shutil.rmtree(tmp, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
