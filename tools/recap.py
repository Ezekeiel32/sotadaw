#!/usr/bin/env python3
"""V42 SESSION RECAP — "where you left off, what's pending, one suggested next step."

recap.py [--json]

Built for persona #2: reopening the project must cost zero executive function.
Sources: git log (songs shipped), pending _prop_* proposals, the crash journal,
the crate, freshest renders. Ends with exactly ONE suggested next step.
"""
import argparse, glob, json, os, subprocess, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "songs")


def sh(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT, timeout=10).stdout.strip()
    except Exception:
        return ""


def ago(ts):
    d = time.time() - ts
    for unit, s in (("d", 86400), ("h", 3600), ("m", 60)):
        if d >= s:
            return f"{int(d // s)}{unit} ago"
    return "just now"


def collect():
    # recent song history (agent accepts + human commits touching songs/)
    log = sh(["git", "log", "--oneline", "--since=3 days ago", "--", "songs/*.json"]).splitlines()[:8]

    # pending proposals: the unfinished conversation
    pending = []
    for p in sorted(glob.glob(os.path.join(SONGS, "_prop_*.json")), key=os.path.getmtime, reverse=True):
        base = os.path.basename(p)[len("_prop_"):-len(".json")]
        pending.append({"song": base, "age": ago(os.path.getmtime(p)),
                        "auditionable": os.path.exists(p[:-5] + ".wav")})

    # crash journal: anything to recover?
    jdir = os.path.join(SONGS, ".journal")
    recovery = []
    if os.path.isdir(jdir):
        for j in sorted(glob.glob(os.path.join(jdir, "*.json")), key=os.path.getmtime, reverse=True)[:3]:
            recovery.append({"file": os.path.basename(j), "age": ago(os.path.getmtime(j))})

    # freshest work: newest song jsons + stale renders
    fresh, stale = [], []
    for j in sorted(glob.glob(os.path.join(SONGS, "*.json")), key=os.path.getmtime, reverse=True)[:12]:
        name = os.path.basename(j)[:-5]
        if name.startswith(("_", ".")):
            continue
        w = j[:-5] + ".wav"
        rendered = os.path.exists(w) and os.path.getmtime(w) >= os.path.getmtime(j)
        fresh.append({"song": name, "edited": ago(os.path.getmtime(j)), "rendered": rendered})
        if not rendered:
            stale.append(name)
        if len(fresh) >= 5:
            break

    crate = len(glob.glob(os.path.join(SONGS, "crate", "*.json")))

    # ONE next step, priority-ordered (recovery > pending verdict > stale render > finish the newest)
    if recovery:
        step = f"recover your last session: journal has {recovery[0]['file']} ({recovery[0]['age']})"
    elif pending:
        step = f"audition the pending proposal on '{pending[0]['song']}' ({pending[0]['age']}) — accept or reject it"
    elif stale:
        step = f"'{stale[0]}' changed since its last render — render + listen"
    elif fresh:
        step = f"run finish_audit on '{fresh[0]['song']}' and take stage 1"
    else:
        step = "start something: one prompt in the bar, or generate_loop in your favorite genre"

    return {"shipped_recently": log, "pending_proposals": pending, "recovery": recovery,
            "recent_songs": fresh, "crate_loops": crate, "next_step": step}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    r = collect()
    if a.json:
        print(json.dumps(r, indent=1))
        return
    print("WHERE YOU LEFT OFF")
    for l in r["shipped_recently"][:5]:
        print(f"  shipped: {l}")
    for p in r["pending_proposals"]:
        print(f"  PENDING: proposal on '{p['song']}' ({p['age']})" +
              (" — pre-rendered, one key to audition" if p["auditionable"] else ""))
    for j in r["recovery"]:
        print(f"  RECOVERY: {j['file']} ({j['age']})")
    for s in r["recent_songs"]:
        print(f"  song: {s['song']} (edited {s['edited']}{'' if s['rendered'] else ', render STALE'})")
    if r["crate_loops"]:
        print(f"  crate: {r['crate_loops']} kept loops")
    print(f"NEXT STEP -> {r['next_step']}")


if __name__ == "__main__":
    main()
