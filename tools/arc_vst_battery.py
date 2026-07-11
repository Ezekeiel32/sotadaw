#!/usr/bin/env python3
"""ARC x VST — the producer arc must work on VST3-sourced tracks, not just Faust.
The arc operates on notes/roles/mix (source-agnostic in principle); this proves it:
role detection types VST3 tracks correctly, doctor diagnoses source-blind, and
prescribe/automix NEVER corrupt a VST3 source block. Symbolic (no render, no VSTs
installed needed) — always runs. Exit 1 on any failure."""
import copy, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import automix as M, doctor as D, prescribe as P
from chordvote import chord_map, is_drum_track

PASS, FAIL = [], []
def check(n, c, d=""):
    print(f"  [{'PASS' if c else 'FAIL'}] {n}" + (f" — {d}" if d else ""))
    (PASS if c else FAIL).append(n)


def mixed_song():
    return {"version": 2, "bpm": 120, "lengthBars": 8, "masterGainDb": 0,
            "tracks": [
                {"name": "kick", "source": {"kind": "faust", "id": "kick_808"}, "gainDb": -5, "pan": 0.3,
                 "notes": [{"start": b * 0.5, "len": 0.25, "pitch": 36, "vel": 1.0} for b in range(16)]},
                {"name": "dexbass", "source": {"kind": "vst3", "plugin": "Dexed", "preset": False,
                                               "params": {"Cutoff": 0.7}}, "gainDb": -5,
                 "notes": [{"start": b * 0.5, "len": 0.4, "pitch": 40 + (b % 3), "vel": 0.8} for b in range(16)]},
                {"name": "surgepad", "source": {"kind": "vst3", "plugin": "Surge XT", "preset": True,
                                                "presetBlob": "OPAQUE_STATE_XYZ"}, "gainDb": -8,
                 "notes": [{"start": 0, "len": 16, "pitch": p, "vel": 0.5} for p in (60, 64, 67)]}]}


def main():
    song = mixed_song()
    # role detection is source-agnostic (uses pitch/name)
    roles = {t["name"]: M.role(t) for t in song["tracks"]}
    check("VST3 bass track -> role 'bass'", roles["dexbass"] == "bass", roles["dexbass"])
    check("VST3 held-chord track -> role 'pad'", roles["surgepad"] == "pad", roles["surgepad"])
    check("faust kick still -> 'kick'", roles["kick"] == "kick")

    song["chords"] = chord_map(song)
    iss = [c for c, _, _ in D.diagnose(song)]
    check("doctor diagnoses the mixed-source song (source-blind)", len(iss) > 0, str(iss))

    # prescribe must NOT corrupt the VST3 source blocks (params, preset blob)
    before_src = {t["name"]: copy.deepcopy(t["source"]) for t in song["tracks"] if t["source"].get("kind") == "vst3"}
    s2 = copy.deepcopy(song)
    P.prescribe(s2)
    after_src = {t["name"]: t["source"] for t in s2["tracks"] if t["source"].get("kind") == "vst3"}
    check("prescribe preserves VST3 params (Dexed Cutoff intact)",
          after_src.get("dexbass", {}).get("params", {}).get("Cutoff") == 0.7,
          str(after_src.get("dexbass", {}).get("params")))
    check("prescribe preserves VST3 preset blob (Surge intact)",
          after_src.get("surgepad", {}).get("presetBlob") == "OPAQUE_STATE_XYZ")
    check("prescribe kept plugin identity", all(after_src[n]["plugin"] == before_src[n]["plugin"] for n in before_src))

    # automix must not strip a VST3 track's source when adding fx/pan
    s3 = copy.deepcopy(song)
    M.automix(s3)
    vst_survived = all(any(t["name"] == n and t["source"].get("kind") == "vst3" for t in s3["tracks"])
                       for n in before_src)
    check("automix keeps VST3 sources (adds fx without stripping source)", vst_survived)

    print(f"\n== ARC x VST: {len(PASS)} pass / {len(FAIL)} fail ==")
    if FAIL:
        print("FAILURES:", ", ".join(FAIL))
        sys.exit(1)
    print("THE PRODUCER ARC IS SOURCE-AGNOSTIC (Faust + VST3)")


if __name__ == "__main__":
    main()
