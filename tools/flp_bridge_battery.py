#!/usr/bin/env python3
"""FLP BRIDGE battery — V17 export + the resurrected V16 import, round-trip proven.

The stakes: FL Studio is the biggest producer community on earth; the bridge
must be TWO-WAY and exact. Also pinned here: the pyflp/py3.12 disease
(EventEnum on a memberless enum dies before _missing_) that had the V16
import rail silently dead — pyflp_compat.ensure() is the cure, and this
battery is the tripwire if a future pyflp/python heals or re-breaks it.

Proof surface:
  B1 export emits, deterministically (two exports byte-identical)
  B2 the PyFLP parse court accepts the file (channels + names + note structs)
  B3 round-trip note-EXACT at tick resolution: bpm exact, every track found,
     every (start,len,pitch) exact, velocity within 1/64
  B4 edge cases survive: off-grid 16ths, vel extremes, pitch clamp 0..131,
     bar-64 positions, long names (importer caps 24), one bad note skipped
  B5 no-notes song exits clean (no traceback), audio-only likewise
  B6 the compat shim: parse works WITH ensure(); the raw disease is
     documented (plain EventEnum call dies on this interpreter -> shim armed)
Run: .venv/bin/python tools/flp_bridge_battery.py   (suite leg)
"""
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
PY = os.path.join(ROOT, ".venv", "bin", "python")

N = {"pass": 0, "fail": 0}


def check(name, cond, detail=""):
    N["pass" if cond else "fail"] += 1
    print(("PASS " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))


tdir = tempfile.mkdtemp(prefix="flpbat_")
song = {
    "version": 2, "bpm": 173.33, "lengthBars": 65,
    "tracks": [
        {"name": "kick", "source": {"kind": "sample", "kit": "gm_drums"}, "gainDb": -6,
         "notes": [{"start": 0, "len": 0.25, "pitch": 36, "vel": 0.05},
                   {"start": 1.75, "len": 0.25, "pitch": 36, "vel": 1.0},
                   {"start": 256.25, "len": 0.25, "pitch": 36, "vel": 0.9}]},
        {"name": "a very long track name that overflows", "source": {"kind": "faust", "id": "pluck"},
         "gainDb": -9,
         "notes": [{"start": 0.5, "len": 0.5, "pitch": 65, "vel": 0.7},
                   {"start": 2.0625, "len": 0.1875, "pitch": 131, "vel": 0.66},
                   {"start": 3, "len": 1, "pitch": 0, "vel": 0.75},
                   {"start": "garbage", "len": 1, "pitch": 60, "vel": 0.5}]},
    ],
}
sp = os.path.join(tdir, "bridge.json")
json.dump(song, open(sp, "w"))
f1, f2 = os.path.join(tdir, "a.flp"), os.path.join(tdir, "b.flp")

r = subprocess.run([PY, os.path.join(ROOT, "tools", "flp_export.py"), sp, f1],
                   capture_output=True, text=True, timeout=60)
subprocess.run([PY, os.path.join(ROOT, "tools", "flp_export.py"), sp, f2],
               capture_output=True, text=True, timeout=60)
check("B1 export emits + deterministic", r.returncode == 0 and os.path.exists(f1)
      and open(f1, "rb").read() == open(f2, "rb").read(), r.stderr.strip()[:80])

import pyflp_compat                     # noqa: E402
pyflp_compat.ensure()
import pyflp                            # noqa: E402

p = pyflp.parse(f1)
chans = list(p.channels)
pats = list(p.patterns)
nnotes = sum(len(list(pt.notes)) for pt in pats)
check("B2 parse court: channels+names+notes", float(p.tempo) == 173.33 and p.ppq == 960
      and [c.display_name for c in chans] == ["kick", "a very long track name that overflows"]
      and nnotes == 6, f"tempo {p.tempo} chans {len(chans)} notes {nnotes}")
arrs = list(p.arrangements)
placed = [(ti, len(list(tr))) for ti, tr in enumerate(arrs[0].tracks) if len(list(tr))] if arrs else []
check("B2b real playlist: one clip per used row", placed == [(0, 1), (1, 1)], str(placed[:6]))

rt = os.path.join(tdir, "rt.json")
r = subprocess.run([PY, os.path.join(ROOT, "tools", "flp_import.py"), f1, rt],
                   capture_output=True, text=True, timeout=60)
b = json.load(open(rt)) if os.path.exists(rt) else {"tracks": []}
check("B3a import back via PLACEMENTS (no tiling fallback)",
      r.returncode == 0 and b.get("bpm") == 173.33 and "tiling" not in r.stderr,
      f"rc={r.returncode} bpm={b.get('bpm')} stderr={r.stderr.strip()[:50]}")

diffs, matched = [], 0
for ta in song["tracks"]:
    tb = next((t for t in b["tracks"] if t["name"] == ta["name"][:24]), None)
    if tb is None:
        diffs.append(f"track missing: {ta['name'][:24]}")
        continue
    good = [n for n in ta["notes"] if isinstance(n.get("start"), (int, float))]
    if len(good) != len(tb["notes"]):
        diffs.append(f"{ta['name'][:24]}: {len(good)} vs {len(tb['notes'])} notes")
        continue
    for na, nb in zip(sorted(good, key=lambda n: (n["start"], n["pitch"])),
                      sorted(tb["notes"], key=lambda n: (n["start"], n["pitch"]))):
        if (round(na["start"] * 960) != round(nb["start"] * 960)
                or round(na["len"] * 960) != round(nb["len"] * 960)
                or na["pitch"] != nb["pitch"] or abs(na["vel"] - nb["vel"]) > 1 / 64):
            diffs.append(f"{ta['name'][:24]}: {na} != {nb}")
        else:
            matched += 1
check("B3b every note exact at tick resolution", not diffs and matched == 6,
      f"{matched} matched; " + "; ".join(diffs[:2]))
check("B4 edge cases: clamp+cap+bad-note-skip",
      any(t["name"] == "a very long track name t" for t in b["tracks"])
      and any(n["pitch"] == 131 for t in b["tracks"] for n in t["notes"])
      and any(n["pitch"] == 0 for t in b["tracks"] for n in t["notes"]))

empty = os.path.join(tdir, "empty.json")
json.dump({"version": 2, "bpm": 120, "tracks": [{"name": "audio only", "audioClips": []}]},
          open(empty, "w"))
r = subprocess.run([PY, os.path.join(ROOT, "tools", "flp_export.py"), empty,
                    os.path.join(tdir, "e.flp")], capture_output=True, text=True, timeout=60)
check("B5 no-notes song exits clean", r.returncode != 0 and "Traceback" not in r.stderr,
      r.stderr.strip()[:60])

# fresh interpreter: in THIS process, parse() minted pseudo-members that mask
# the raw disease (EventEnum(199) works after any successful parse)
r = subprocess.run([PY, "-c", "from pyflp._events import EventEnum; EventEnum(199)"],
                   capture_output=True, text=True, timeout=30)
diseased = r.returncode != 0 and "TypeError" in r.stderr
shim_state = ("py3.12 disease present -> shim carried the parse" if diseased
              else "interpreter healthy (shim dormant)")
check("B6 compat shim truth: " + shim_state,
      r.returncode == 0 or diseased, r.stderr.strip()[-60:])

print(f"flp bridge battery: {N['pass']}/{N['pass'] + N['fail']}"
      + (" clean" if not N["fail"] else " RED"))
sys.exit(1 if N["fail"] else 0)
