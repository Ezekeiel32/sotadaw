#!/usr/bin/env python3
"""maketrack_battery.py — the one-button-track flow, verified across form families.

Exercises the make_track chain (loop_gen -> arrange) for a spread of EDM-form
and song-form genres; asserts each arranges (>= 6 sections, right family) and
renders CLEAN (0 clipped). The headline feature (correction #2) as a net.
"""
import json, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import doctor as D
PY = os.path.join(ROOT, ".venv", "bin", "python")
M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")
EDM = ["techno", "house", "dnb", "trap", "dubstep"]
SONG = ["soul", "reggae", "gospel", "jazz", "rock"]


def verdict_prelude():
    """W7: the band-verdict kernel is PURE — prove it before paying for renders."""
    mud = {"band_energy_pct": {"low_20_120": 55.0, "lowmid_120_500": 33.0,
                               "mid_500_2k": 1.5, "himid_2k_6k": 0.5, "high_6k_up": 0.2}}
    v = D.band_verdict(mud, {"band_order": "low>lowmid>mid>himid>high"})
    assert any(x.startswith("MUD") for x in v), v
    assert any("PRESENCE" in x for x in v), v
    clean = {"band_energy_pct": {"low_20_120": 62.0, "lowmid_120_500": 18.0,
                                 "mid_500_2k": 12.0, "himid_2k_6k": 5.0, "high_6k_up": 3.0}}
    assert D.band_verdict(clean, {"band_order": "low>lowmid>mid>himid>high"}) == []
    wrong = {"band_energy_pct": {"low_20_120": 20.0, "lowmid_120_500": 45.0,
                                 "mid_500_2k": 25.0, "himid_2k_6k": 6.0, "high_6k_up": 4.0}}
    assert any("BAND ORDER" in x for x in D.band_verdict(wrong, {"band_order": "low>lowmid>mid"}))
    assert D.band_verdict({}, {}) == []
    assert D.band_verdict({"band_energy_pct": None}, None) == []
    assert D.band_verdict(None, None) == []
    print("  band_verdict kernel: 6 pure checks OK")

def one(genre, song_form):
    loop = os.path.join(ROOT, "songs", "_mtb_loop.json")
    out = os.path.join(ROOT, "songs", "_mtb.json")
    wav = os.path.join(ROOT, "songs", "_mtb.wav")
    subprocess.run([PY, f"{ROOT}/tools/loop_gen.py", genre, "_mtb_loop", "--bars", "4", "--seed", "3"],
                   capture_output=True)
    r = subprocess.run([PY, f"{ROOT}/tools/arrange.py", loop, "--out", "_mtb", "--genre", genre],
                       capture_output=True, text=True)
    if not os.path.exists(out):
        return f"arrange failed"
    s = json.load(open(out))
    secs = [x["name"] for x in s.get("sections", [])]
    fam_ok = ("verse" in secs) == song_form and ("drop" in secs) != song_form
    subprocess.run([M1, "render", out, wav], capture_output=True)
    a = json.loads(subprocess.run([PY, f"{ROOT}/tools/analyze2.py", wav], capture_output=True, text=True).stdout)
    clean = a.get("clipped_samples", 1) == 0
    assert isinstance(D.band_verdict(a, {"band_order": "low>lowmid>mid"}), list)  # W7: never crashes on real ears
    for f in (loop, out, wav):
        if os.path.exists(f): os.remove(f)
    ok = len(secs) >= 6 and fam_ok and clean
    return f"{'OK ' if ok else 'FAIL'} {len(secs)}sec {'song' if 'verse' in secs else 'drop'}-form clip{a.get('clipped_samples')}", ok

if __name__ == "__main__":
    verdict_prelude()
    fails = 0
    for g in EDM:
        msg, ok = one(g, False); fails += not ok
        print(f"  {g:10} {msg}")
    for g in SONG:
        msg, ok = one(g, True); fails += not ok
        print(f"  {g:10} {msg}")
    print(f"maketrack battery: {10 - fails}/10")
    sys.exit(1 if fails else 0)
