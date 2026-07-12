#!/usr/bin/env python3
"""#21c BLIND CARD E2E (UI half) — the variants event lands through the REAL
pollEvents as an anonymous playable card on the agent page; PICK rides the
real hit-scan: request.json carries pick_variant + the chips retire.
Boots the REAL binary with SOTADAW_SNAP_BLIND (rigBlindStage in ui_main).
Run: python3 tools/blind_card_e2e.py [runs]"""
import json, os, re, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "songs")
BIN = os.path.join(ROOT, "app/build/sotadaw_artefacts/Release/SOTA DAW")
NAME = "_blindcard_e2e"

def run_once():
    A = []
    ok = lambda c, m: A.append((bool(c), m))
    json.dump({"version": 2, "bpm": 120, "lengthBars": 2, "masterGainDb": 0,
               "master": [], "tracks": [{"name": "kick",
                                         "source": {"kind": "faust", "id": "kick_808"},
                                         "gainDb": -6, "pan": 0,
                                         "notes": [{"start": 0.0, "len": 0.2,
                                                    "pitch": 36, "vel": 0.9}]}]},
              open(os.path.join(SONGS, f"{NAME}.json"), "w"), indent=1)
    ipc = tempfile.mkdtemp(prefix="blindcard_ipc_")
    out = tempfile.mkdtemp(prefix="blindcard_png_")
    env = dict(os.environ, SOTADAW_SNAPSHOT="1", SOTADAW_SANDBOX="1",
               SOTADAW_SNAP_BLIND="1", SOTADAW_SONG=NAME, SOTADAW_IPC=ipc)
    try:
        p = subprocess.run([BIN, "--snapshot", out], env=env, cwd=ROOT,
                           capture_output=True, text=True, timeout=120)
        st = {}
        for l in p.stdout.splitlines():
            if l.startswith("[blind] "):
                d = dict(re.findall(r"(\w+)=(\S+)", l))
                st[int(d["stage"])] = d
        ok(p.returncode == 0, f"app exit 0 (got {p.returncode})")
        ok({1, 2}.issubset(st), f"both census stages ({sorted(st)})")
        s1, s2 = st.get(1, {}), st.get(2, {})
        ok(s1.get("n") == "2" and s1.get("labels") == "A,B",
           f"card carries 2 anonymous takes A,B (got {s1})")
        ok(s1.get("picked") == "-", "round open before the click")
        ok(s1.get("hitsPlay") == "2" and s1.get("hitsPick") == "2",
           f"every row playable + pickable (got {s1})")
        ok(s2.get("picked") == "A", f"click landed the pick (got {s2.get('picked')})")
        ok(s2.get("hitsPick") == "0" and s2.get("hitsPlay") == "0",
           f"picked card retires ALL chips (got {s2})")
        ok(s2.get("req_pick") == "1", "request.json carries pick_variant")
        ok(s2.get("req_label") == "1", "request.json carries label A")
        if any(not c for c, _ in A):
            print("--- app stdout tail ---")
            print("\n".join(p.stdout.splitlines()[-12:]))
        return A
    finally:
        for f in (f"{NAME}.json",):
            fp = os.path.join(SONGS, f)
            os.path.exists(fp) and os.remove(fp)
        shutil.rmtree(ipc, ignore_errors=True)
        shutil.rmtree(out, ignore_errors=True)

def main():
    runs = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    bad = 0
    for i in range(1, runs + 1):
        A = run_once()
        fails = [m for c, m in A if not c]
        for c, m in A:
            print(("PASS " if c else "FAIL ") + m)
        if fails:
            bad += 1
        print(f"== run {i}/{runs}: {len(A) - len(fails)}/{len(A)}")
    sys.exit(1 if bad else 0)

if __name__ == "__main__":
    main()
