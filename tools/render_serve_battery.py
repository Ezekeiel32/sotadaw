#!/usr/bin/env python3
"""THE WARM SERVER battery — m1 serve: the determinism SEAL + the speed truth.

Adoption law: nothing rides the warm rail until a SERVED render byte-matches a
SPAWNED one (same renderCore, one warm engine vs fresh processes) across
diverse material — faust voices, sampler kit, fx chains, swing. Also proven:
protocol resilience (bad json / missing song answered, server lives on),
multi-request reuse on ONE engine, the flag-gated client path with fallback,
and the speed delta reported honestly (warm serve vs cold spawn).

Usage: .venv/bin/python tools/render_serve_battery.py
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")

PASS, FAIL = 0, []


def ok(cond, msg):
    global PASS
    if cond:
        PASS += 1
    else:
        FAIL.append(msg)


def sha(p):
    import hashlib
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def N(start, pitch, vel=0.9, ln=0.4):
    return {"start": start, "len": ln, "pitch": pitch, "vel": vel}


def songs(d):
    a = {"version": 2, "bpm": 126, "lengthBars": 2, "masterGainDb": 0.0,
         "master": [{"id": "fx_truepeak", "params": {"ceiling": -1.2}}],
         "tracks": [{"name": "kick", "source": {"kind": "faust", "id": "hardkick"},
                     "gainDb": -4, "notes": [N(b, 36, 1.0, 0.2) for b in range(8)]},
                    {"name": "bass", "source": {"kind": "faust", "id": "bass_warm"},
                     "gainDb": -6, "fx": [{"id": "fx_filter", "params": {"cutoff": 900}}],
                     "notes": [N(b * 2, 33) for b in range(4)]}]}
    b = {"version": 2, "bpm": 96, "lengthBars": 2, "masterGainDb": 0.0, "master": [],
         "swing": {"grid": "8th", "amount": 0.62},
         "tracks": [{"name": "lead", "source": {"kind": "faust", "id": "flute_lead"},
                     "gainDb": -6, "fx": [{"id": "fx_delay", "params": {"mix": 0.3}}],
                     "notes": [N(i * 0.5, 60 + (i * 3) % 12, 0.8) for i in range(16)]}]}
    out = []
    for nm, doc in (("a", a), ("b", b)):
        p = os.path.join(d, nm + ".json")
        json.dump(doc, open(p, "w"))
        out.append(p)
    return out


def main():
    if not os.path.exists(M1):
        print("render-serve battery: SKIP (m1 not built)")
        return
    # ONE ENV WORLD (the mismatch this battery caught on its own first run):
    # m1's SEAL stamps SOTADAW_RENDER_EPOCH into the BWAV origination metadata,
    # so a server inheriting a cache-busting epoch byte-differs from a no-epoch
    # spawn — METADATA, not audio. Pin the epoch for the WHOLE battery so the
    # spawned truth, the raw server, and the flag-gated client all share it.
    os.environ["SOTADAW_RENDER_EPOCH"] = f"servebat_{os.getpid()}"
    d = tempfile.mkdtemp(prefix="serve_bat_")
    try:
        fixtures = songs(d)

        # ---- spawned truth (cold, classic rail) ----
        spawned, cold_ts = {}, []
        for p in fixtures:
            w = p.replace(".json", ".spawn.wav")
            t0 = time.monotonic()
            r = subprocess.run([M1, "render", p, w], capture_output=True, text=True,
                               timeout=300)
            cold_ts.append(time.monotonic() - t0)
            ok("ok=1" in r.stdout, f"spawned render ok ({os.path.basename(p)})")
            spawned[p] = sha(w)

        # ---- the warm server: one engine, many requests ----
        srv = subprocess.Popen([M1, "serve"], stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, text=True, bufsize=1)
        t0 = time.monotonic()
        while time.monotonic() - t0 < 30:
            ln = srv.stdout.readline()
            if "serve ready" in ln:
                break
        else:
            ok(False, "server never became ready")
            return

        def ask(song, out):
            srv.stdin.write(json.dumps({"song": song, "out": out}) + "\n")
            srv.stdin.flush()
            t1 = time.monotonic()
            while time.monotonic() - t1 < 300:
                ln = srv.stdout.readline()
                if not ln:
                    return None
                if ln.startswith('{"ok"'):
                    return json.loads(ln)
            return None

        warm_ts = []
        for p in fixtures:                    # request 1+2: THE DETERMINISM SEAL
            w = p.replace(".json", ".serve.wav")
            t1 = time.monotonic()
            rep = ask(p, w)
            warm_ts.append(time.monotonic() - t1)
            ok(rep is not None and rep.get("ok") == 1,
               f"served render ok ({os.path.basename(p)})")
            ok(sha(w) == spawned[p],
               f"DETERMINISM SEAL: served == spawned byte-exact ({os.path.basename(p)})")
            ok(rep.get("sha") == spawned[p], "the reply's sha tells the same truth")

        # ---- protocol resilience: garbage + missing song, server lives ----
        srv.stdin.write("not json at all\n")
        srv.stdin.flush()
        ln = srv.stdout.readline()
        ok(ln.startswith('{"ok":0'), f"bad json answered, not crashed ({ln.strip()})")
        rep = ask(os.path.join(d, "missing.json"), os.path.join(d, "x.wav"))
        ok(rep is not None and rep.get("ok") == 0, "missing song answered ok:0")
        w3 = fixtures[0].replace(".json", ".serve3.wav")
        rep = ask(fixtures[0], w3)
        ok(rep is not None and rep.get("ok") == 1 and sha(w3) == spawned[fixtures[0]],
           "the server still renders TRUE after garbage (engine unharmed)")
        # ---- CANCEL (protocol v2): a mid-flight render dies on request ----
        big = {"version": 2, "bpm": 120, "lengthBars": 24, "masterGainDb": 0.0,
               "master": [{"id": "fx_truepeak", "params": {"ceiling": -1.2}}],
               "tracks": [{"name": f"t{i}", "source": {"kind": "faust", "id": vid},
                           "gainDb": -8,
                           "notes": [N(b * 0.5, 40 + i * 7 + (b % 12), 0.8)
                                     for b in range(192)]}
                          for i, vid in enumerate(("bass_warm", "flute_lead", "harp"))]}
        bp = os.path.join(d, "big.json")
        json.dump(big, open(bp, "w"))
        bw = os.path.join(d, "big.wav")
        srv.stdin.write(json.dumps({"song": bp, "out": bw, "id": 9}) + "\n")
        srv.stdin.flush()
        time.sleep(0.8)                       # let it get INTO the render
        t_c = time.monotonic()
        srv.stdin.write(json.dumps({"cancel": 9}) + "\n")
        srv.stdin.flush()
        rep = None
        while time.monotonic() - t_c < 30:
            ln = srv.stdout.readline()
            if ln.startswith('{"ok"'):
                rep = json.loads(ln)
                break
        dt = time.monotonic() - t_c
        ok(rep is not None and rep.get("cancelled") == 1 and rep.get("id") == 9,
           f"CANCEL: the in-flight render died on request ({rep})")
        ok(dt < 5.0, f"CANCEL answered fast ({dt:.2f}s)")
        ok(not os.path.exists(bw), "a cancelled partial is DELETED (not a render)")
        w7 = os.path.join(d, "aftercancel.wav")
        rep = ask(fixtures[0], w7)
        ok(rep is not None and rep.get("ok") == 1 and sha(w7) == spawned[fixtures[0]],
           "the engine renders TRUE after a cancel (unharmed)")
        srv.stdin.write(json.dumps({"cancel": 12345}) + "\n")   # idle/unknown id
        srv.stdin.flush()
        ln = srv.stdout.readline()
        ok('"cancelled":0' in ln and "not active" in ln,
           f"late/unknown cancel is BENIGN ({ln.strip()})")

        srv.stdin.write("quit\n")
        srv.stdin.flush()
        ok(srv.wait(timeout=10) == 0, "quit exits clean")

        # ---- the flag-gated client rail with fallback ----
        import render_cache as RC
        os.environ["SOTADAW_RENDER_SERVE"] = "1"
        try:
            w4 = fixtures[1].replace(".json", ".client.wav")
            rep = RC.render_cached(fixtures[1], w4, quiet=True)
            ok(rep.get("sha256") == spawned[fixtures[1]] and sha(w4) == spawned[fixtures[1]],
               "render_cached rides the warm rail, same bytes")
            RC.serve_stop()
        finally:
            os.environ.pop("SOTADAW_RENDER_SERVE", None)

        # ---- the SIDECAR seam: the daemon's render path rides warm, both belts ----
        # VIRGIN fixtures per leg (a stored fixture would cache-HIT and pass the
        # warm-rail assert vacuously); truths spawned in the SAME env world.
        os.environ["SOTADAW_IPC"] = os.path.join(d, "ipc")   # isolated instance law
        os.makedirs(os.environ["SOTADAW_IPC"], exist_ok=True)
        sys.path.insert(0, os.path.join(ROOT, "agent"))
        import sidecar as sc
        ok(os.environ.get("SOTADAW_RENDER_SERVE") == "1",
           "the sidecar defaults the warm rail ON (import-time flip)")
        virgin = {}
        for nm, bpm in (("c", 121), ("dd", 133)):
            doc = json.load(open(fixtures[0]))
            doc["bpm"] = bpm
            vp = os.path.join(d, nm + ".json")
            json.dump(doc, open(vp, "w"))
            vw = vp.replace(".json", ".spawn.wav")
            subprocess.run([M1, "render", vp, vw], capture_output=True, timeout=300)
            virgin[nm] = (vp, sha(vw))
        w5 = os.path.join(d, "sidecar.wav")
        okc = sc._cached_render(0, virgin["c"][0], w5)
        ok(okc and sha(w5) == virgin["c"][1]
           and RC._SERVE.get("proc") is not None,
           "sidecar._cached_render rides WARM (resident alive), same bytes")
        RC.serve_stop()
        os.environ["SOTADAW_RENDER_SERVE"] = "0"             # the kill-switch
        w6 = os.path.join(d, "killswitch.wav")
        okd = sc._cached_render(0, virgin["dd"][0], w6)
        ok(okd and sha(w6) == virgin["dd"][1]
           and RC._SERVE.get("proc") is None,
           "kill-switch: classic rail (no resident), still byte-true")
        os.environ.pop("SOTADAW_RENDER_SERVE", None)
        os.environ.pop("SOTADAW_IPC", None)

        warm = sum(warm_ts[1:]) / max(1, len(warm_ts) - 1)   # first pays JIT warmup
        cold = sum(cold_ts) / len(cold_ts)
        print(f"  speed: cold-spawn {cold:.2f}s vs warm-serve {warm:.2f}s "
              f"({cold / max(0.01, warm):.1f}x)")
        ok(warm < cold, f"the warm rail is faster ({warm:.2f}s vs {cold:.2f}s)")
    finally:
        os.environ.pop("SOTADAW_RENDER_EPOCH", None)
        shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    main()
    for f in FAIL:
        print("FAIL:", f)
    print(f"render-serve battery: {PASS}/{PASS + len(FAIL)} {'clean' if not FAIL else 'RED'}")
    sys.exit(1 if FAIL else 0)
