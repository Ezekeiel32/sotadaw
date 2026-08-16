#!/usr/bin/env python3
"""THE IMPORT FINISHER (F4, docs/IMPORT_FINALE.md) — heavy truth work that
no longer blocks the landing.

--drums: THE DRUM MICROSCOPE UPGRADE. The import landed the byte-proven
band-lane drums in minutes; this pass pays the drumsep price (mdx23c, CPU
by design, ~4-6x realtime) in the background and re-lands the SAME kernel
(stems_import.land_drum_lanes) with physical pieces — toms/ride truth,
unconflated hats/cymbals, the source kit rebuilt from true labels. Then
one a2m_correct iteration re-levels/re-anchors, and the master match
refreshes the finale.

THE QUALITY INVARIANT: same models, same thresholds, same kernel — the
final state equals the old inline pipeline's; only the ARRIVAL moved.

STOMP GUARD: refuses (honestly, exit 0) when the song's drum lanes no
longer match <stems>/drum_land.json — the user edited drums while we
worked; their edits outrank our upgrade.

    .venv/bin/python tools/import_finisher.py <song> --drums
"""
import argparse
import hashlib
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
SONGS = os.path.join(ROOT, "songs")

DRUM_LANES = ("Kick", "Snare", "Hats", "Perc", "Cymbals")


def _sha(notes):
    return hashlib.sha256(json.dumps(notes, sort_keys=True).encode()).hexdigest()


def _ram_gate(min_gb=3.0, wait_s=None):
    """The importer's models may still be unloading; drumsep + kits want
    real headroom. Wait politely, proceed anyway after the window."""
    wait_s = float(os.environ.get("SOTADAW_FIN_WAIT_S", wait_s or 1200))
    t0 = time.time()
    while time.time() - t0 < wait_s:
        try:
            avail = 0.0
            for line in open("/proc/meminfo"):
                if line.startswith("MemAvailable"):
                    avail = float(line.split()[1]) / 1048576.0
                    break
            if avail >= min_gb:
                return True
        except Exception:
            return True
        time.sleep(15)
    return True


def upgrade_drums(name):
    path = os.path.join(SONGS, f"{name}.json")
    stems_dir = os.path.join(SONGS, f"{name}_stems")
    drums_wav = os.path.join(stems_dir, "drums.wav")
    stamp_p = os.path.join(stems_dir, "drum_land.json")
    if not (os.path.exists(path) and os.path.exists(drums_wav)):
        print(f"[finisher] no song/drums stem for {name} — nothing to do")
        return 0
    try:
        os.nice(10)                       # the user's session outranks us
    except OSError:
        pass
    _ram_gate()

    t0 = time.time()
    try:                                  # the expensive pass, cached forever
        import drumsep
        if drumsep.available() is None:
            print("[finisher] drumsep unavailable — band lanes stand")
            return 0
        drumsep.separate_cached(drums_wav)
    except Exception as e:
        print(f"[finisher] drumsep failed ({type(e).__name__}: {e}) — "
              f"band lanes stand")
        return 0
    print(f"[finisher] drum pieces separated in {time.time()-t0:.0f}s",
          flush=True)

    song = json.load(open(path))
    bpm = float(song.get("bpm") or 120.0)
    try:
        stamp = json.load(open(stamp_p))
    except Exception:
        stamp = None
    if stamp is not None:
        for t in song.get("tracks", []):
            nm = t.get("name")
            if nm in stamp and _sha(t.get("notes", [])) != stamp[nm]:
                print(f"[finisher] STOMP GUARD: '{nm}' was edited since the "
                      f"landing — the user's edits outrank the upgrade; "
                      f"band lanes stand")
                return 0

    import stems_import as si
    new_tracks, docket = si.land_drum_lanes(drums_wav, name, bpm)
    if not new_tracks:
        print("[finisher] pieces rail produced no lanes — band lanes stand")
        return 0

    song = json.load(open(path))          # FRESH right before the write
    gains = {t.get("name"): t.get("gainDb")
             for t in song["tracks"] if t.get("name") in DRUM_LANES}
    keep = [t for t in song["tracks"] if t.get("name") not in DRUM_LANES]
    at = next((i for i, t in enumerate(song["tracks"])
               if t.get("name") in DRUM_LANES), len(keep))
    at = min(at, len(keep))
    for t in new_tracks:                  # the correction's levels survive
        if gains.get(t["name"]) is not None:
            t["gainDb"] = gains[t["name"]]
    song["tracks"] = keep[:at] + new_tracks + keep[at:]
    json.dump(song, open(path, "w"), indent=1)
    json.dump({t["name"]: _sha(t.get("notes", [])) for t in new_tracks},
              open(stamp_p, "w"))
    print(f"[finisher] drum microscope landed: "
          f"{', '.join(t['name'] for t in new_tracks)}", flush=True)
    if docket:
        cj = os.path.join(stems_dir, "court.json")
        try:
            cur = json.load(open(cj)) if os.path.exists(cj) else []
        except Exception:
            cur = []
        json.dump(cur + docket, open(cj, "w"), indent=1)

    try:                                  # re-anchor/refit/salvage + levels
        import a2m_correct as a2c
        a2c.correct(path, iters=1, verify=False)
    except Exception as ce:
        print(f"[finisher] re-correct skipped ({type(ce).__name__}: {ce})")
    try:                                  # the finale stays true to the record
        import master_match as mm
        mm.match(path, iters=3)
    except Exception as me:
        print(f"[finisher] master refresh skipped ({type(me).__name__}: {me})")
    try:                                  # the ledger tells the whole story
        sp = os.path.join(stems_dir, "import_stages.json")
        led = json.load(open(sp)) if os.path.exists(sp) else {"stages": {}}
        led["stages"]["drum_finisher"] = round(time.time() - t0, 1)
        led["deferred_drum_pieces"] = "landed"
        json.dump(led, open(sp, "w"), indent=1)
    except Exception:
        pass
    print(f"[finisher] drum upgrade complete in {time.time()-t0:.0f}s",
          flush=True)
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("song")
    ap.add_argument("--drums", action="store_true",
                    help="run the drum microscope upgrade")
    a = ap.parse_args()
    import songname
    name = songname.resolve(a.song)
    if a.drums:
        sys.exit(upgrade_drums(name))
    print("[finisher] nothing requested (--drums?)")


if __name__ == "__main__":
    main()
