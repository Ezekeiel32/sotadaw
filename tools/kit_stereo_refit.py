#!/usr/bin/env python3
"""THE STEREO REPLICA retrofit (IMPORT_FINALE F6.1): rebuild a pre-F6
import's drum kit STEREO through the per-channel median vote, reconciling
the pitch set so no existing song note orphans (a voice the rebuild drops
folds onto its family primary, or restores wholesale from the pre-refit
backup). Then re-run tools/a2m_correct.py + tools/master_match.py so
levels/pans/master re-close against the record.
Usage: kit_stereo_refit.py <song> [<song>...]"""
import json
import math
import os
import shutil
import sys
import wave

import numpy as np

ROOT = "/home/chezy/AI_SOTA_DAW"
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import source_kit as sk                                   # noqa: E402

KITS = os.path.join(ROOT, "kits")


def wav_ch_bal(path):
    with wave.open(path) as w:
        nch = w.getnchannels()
        raw = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
    y = raw.reshape(-1, nch).astype(np.float64) / 32767.0
    if nch < 2:
        return nch, 0.0
    el = float((y[:, 0] ** 2).mean()) + 1e-12
    er = float((y[:, 1] ** 2).mean()) + 1e-12
    return nch, 10 * math.log10(el / er)


def refit(song_name):
    sp = os.path.join(ROOT, "songs", f"{song_name}.json")
    song = json.load(open(sp))
    bpm = float(song.get("bpm", 120.0))
    kits = {}
    for t in song.get("tracks", []):
        src = t.get("source", {})
        if src.get("kind") == "sample" and src.get("kit", "").endswith("_drums"):
            kits.setdefault(src["kit"], []).extend(t.get("notes", []))
    for kname, notes in kits.items():
        kdir = os.path.join(KITS, kname)
        kj = os.path.join(kdir, "kit.json")
        if not os.path.exists(kj) or not notes:
            print(f"[refit] {kname}: missing kit or no notes — skipped")
            continue
        old = json.load(open(kj))
        stem = os.path.join(ROOT, old["source"])
        if not os.path.exists(stem):
            print(f"[refit] {kname}: source stem gone ({old['source']}) — skipped")
            continue
        bak = kdir + ".prefit_bak"
        shutil.rmtree(bak, ignore_errors=True)
        shutil.copytree(kdir, bak)
        out = sk.build_source_kit(stem, notes, kname, bpm=bpm)
        if out != kname:
            print(f"[refit] {kname}: rebuild FAILED — restoring backup")
            shutil.rmtree(kdir, ignore_errors=True)
            shutil.copytree(bak, kdir)
            shutil.rmtree(bak, ignore_errors=True)
            continue
        new = json.load(open(kj))
        new_pitches = {s["keyNote"] for s in new["samples"]}
        used_pitches = {int(n["pitch"]) for n in notes}
        old_by_pitch = {s["keyNote"]: s for s in old["samples"]}
        healed = []
        for p in sorted(used_pitches - new_pitches):
            osamp = old_by_pitch.get(p)
            if osamp is None:
                continue                        # never had a voice either
            fam = osamp["file"].split("_")[0].split(".")[0]
            prim = next((s for s in new["samples"]
                         if s["file"].split("_")[0].split(".")[0] == fam
                         and s["keyNote"] == s["minNote"] == s["maxNote"]
                         and "_alt" not in s["file"]), None)
            if prim is not None:                # voice folded into primary:
                new["samples"].append({**prim, "keyNote": p, "minNote": p,
                                       "maxNote": p})
                healed.append(f"{p}->{prim['file']}")
            else:                               # whole lane dropped: restore
                src_w = os.path.join(bak, osamp["file"])
                if os.path.exists(src_w):
                    shutil.copy2(src_w, os.path.join(kdir, osamp["file"]))
                    new["samples"].append(osamp)
                    healed.append(f"{p}->{osamp['file']}(restored-mono)")
        if healed:
            json.dump(new, open(kj, "w"), indent=1)
        shutil.rmtree(bak, ignore_errors=True)
        bals = []
        for s in new["samples"]:
            p = os.path.join(kdir, s["file"])
            if os.path.exists(p):
                nch, bal = wav_ch_bal(p)
                bals.append(f"{s['file']}:ch{nch}{bal:+.1f}dB")
        print(f"[refit] {kname}: channels={new.get('channels')} "
              f"reconciled={healed or 'none'}")
        print(f"[refit]   {'  '.join(bals)}")


if __name__ == "__main__":
    for s in sys.argv[1:]:
        refit(s)
