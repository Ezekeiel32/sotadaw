#!/usr/bin/env python3
"""DESCRIBE_SOUND battery — zero-shot ears must name committed truth sounds.

SKIP-green when the CLAP checkpoint isn't cached (fresh box, clap_battery
convention); on this box it runs. Family sets, not exact tags: zero-shot is
allowed to say "tom drum" for a boomy kick — never "female vocals".
"""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

N = 0


def ok(cond, msg):
    global N
    N += 1
    if not cond:
        print(f"FAIL {N} — {msg}")
        sys.exit(1)
    print(f"ok {N} — {msg}")


import clap_embed
if not clap_embed.available():
    print("SKIP describe_sound battery — CLAP checkpoint not cached (fresh box)")
    sys.exit(0)

from describe_sound import describe, BANKS, bank_matrix

DRUMS = {"kick drum", "snare drum", "tom drum", "drum loop", "percussion", "808 sub bass"}
HATS = {"hi-hat cymbal", "crash cymbal", "percussion", "clap", "snare drum"}
VOCAL = {"choir", "male vocals", "female vocals", "rap vocals", "spoken word"}

kick = os.path.join(ROOT, "kits", "aranyanyara_drums", "kick.wav")
hat = os.path.join(ROOT, "kits", "aranyanyara_drums", "hat_closed.wav")
voc = os.path.join(ROOT, "songs", "_choir_lead_vocal.wav")
out = describe([kick, hat, voc], k=5)
ok(out["available"] and all(f["available"] for f in out["files"]),
   "three committed truth sounds embed clean")
f_kick, f_hat, f_voc = out["files"]

top3 = lambda f, bank: {t["tag"] for t in f["tags"][bank][:3]}
ok(f_kick["tags"]["role"][0]["tag"] in DRUMS and not (top3(f_kick, "role") & VOCAL),
   f"kick.wav named a drum, never a vocal (top: {f_kick['tags']['role'][0]['tag']})")
ok(f_hat["tags"]["role"][0]["tag"] in HATS,
   f"hat_closed.wav named in the cymbal family (top: {f_hat['tags']['role'][0]['tag']})")
ok(f_voc["tags"]["role"][0]["tag"] in VOCAL and not (top3(f_voc, "role") & DRUMS),
   f"choir vocal named a vocal, never a drum (top: {f_voc['tags']['role'][0]['tag']})")

for f in out["files"]:
    for bank in BANKS:
        scores = [t["score"] for t in f["tags"][bank]]
        assert scores == sorted(scores, reverse=True) and all(-1.01 <= s <= 1.01 for s in scores)
    assert f["sentence"]
ok(True, "shape law: every bank ranked desc, scores in [-1,1], sentence present")

again = describe([kick], k=5)
ok(again["files"][0]["tags"]["role"][0]["tag"] == f_kick["tags"]["role"][0]["tag"],
   "deterministic: same file, same top tag")

bad = describe([os.path.join(ROOT, "no_such_file.wav")], k=3)
ok(bad["available"] and bad["files"][0]["available"] is False,
   "unreadable file degrades per-file, tool stays available")

tags, T = bank_matrix()
key_cached = any(x.startswith("clap_bank_") for x in
                 os.listdir(os.path.expanduser("~/.cache/sotadaw")))
ok(key_cached and T.shape[0] == len(tags) == sum(len(v) for v in BANKS.values()),
   f"bank matrix cached to disk and complete ({T.shape[0]} prompts)")

r = subprocess.run([os.path.join(ROOT, ".venv", "bin", "python"),
                    os.path.join(ROOT, "tools", "describe_sound.py"), kick, "--json"],
                   capture_output=True, text=True, cwd=ROOT)
line = next((l for l in r.stdout.splitlines() if l.startswith("DESCRIBE_JSON ")), "")
ok(r.returncode == 0 and line and json.loads(line[14:])["available"],
   "CLI leg: DESCRIBE_JSON machine line parses, rc=0")

print(f"PASS {N}/{N} describe_sound battery")
