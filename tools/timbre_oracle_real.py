#!/usr/bin/env python3
"""THE BRAIN BR-C --real leg — THE TIMBRE ORACLE ON REAL AUDIO.

The toy-sound kill, proven end-to-end: a probe song plays ONE voice solo,
every ES evaluation is a REAL m1 render measured by analyze2, and the search
must land the voice inside a real-kick signature window. Every evaluation
banks to THE FORGE LOG — the amortization dataset grows with every run.

  .venv/bin/python tools/timbre_oracle_real.py                # kick_808 default
  .venv/bin/python tools/timbre_oracle_real.py <voice> --budget 30

Exit 0 = landed inside the window (distance 0.0) or beat the defaults by
>= 2x (an honest partial win is reported as one). Renders are the currency:
the budget is a hard cap (BUDGET LAW sibling).
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")
PY = os.path.join(ROOT, ".venv", "bin", "python")

# the real-kick window (DNA ENGINE indictment: toy kick centroid 6028 Hz vs
# real 1041 Hz). Features = analyze2 keys, verbatim.
KICK_WINDOW = {"spectral_centroid_hz": [300.0, 1800.0],
               "crest_factor_db": [6.0, 26.0]}


def probe_song(voice, params):
    return {"version": 2, "bpm": 120, "key": "F minor", "lengthBars": 2,
            "masterGainDb": 0,
            "master": [{"id": "fx_truepeak", "params": {"ceiling": -1.2}}],
            "tracks": [{
                "name": "probe", "gainDb": 0, "pan": 0,
                "source": {"kind": "faust", "id": voice,
                           "params": {k: round(float(v), 5)
                                      for k, v in params.items()}},
                "notes": [{"start": float(b), "len": 0.9, "pitch": 41, "vel": 1.0}
                          for b in range(8)]}]}


def make_evaluate(voice, workdir, ledger):
    sj = os.path.join(workdir, "probe.json")
    wav = os.path.join(workdir, "probe.wav")

    def evaluate(params):
        with open(sj, "w") as f:
            json.dump(probe_song(voice, params), f)
        t0 = time.time()
        r = subprocess.run([M1, "render", sj, wav], capture_output=True,
                           text=True, timeout=180)
        if r.returncode != 0 or not os.path.exists(wav):
            return {}                    # window meter counts it as a full miss
        a = subprocess.run([PY, os.path.join(HERE, "analyze2.py"), wav],
                           capture_output=True, text=True, timeout=120)
        if a.returncode != 0:
            return {}
        try:
            d = json.loads(a.stdout)
        except json.JSONDecodeError:
            return {}
        feats = {k: d.get(k) for k in
                 ("spectral_centroid_hz", "crest_factor_db", "rms_db",
                  "peak_dbfs", "lufs_integrated")}
        ledger.append((dict(params), feats, round(time.time() - t0, 1)))
        return feats
    return evaluate


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("voice", nargs="?", default="kick_808")
    ap.add_argument("--budget", type=int, default=28)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--genre", default="",
                    help="use the MEASURED genre window from "
                         "telemetry/kick_windows.json (BR-C wave 2); an "
                         "unmeasured genre falls back to the generic window "
                         "with an honest line")
    a = ap.parse_args()
    if not os.path.exists(M1):
        print("m1 binary missing — build first")
        return 2
    window = KICK_WINDOW
    if a.genre:
        import kick_windows as kw
        gw = kw.window_for(a.genre, kw.load_bank())
        if gw:
            via = gw.pop("via", None)
            window = gw
            print(f"GENRE WINDOW {a.genre}"
                  + (f" (via measured family {via})" if via else " (measured)"))
        else:
            print(f"no measured window for {a.genre!r} — generic stands "
                  f"(bank one: tools/kick_windows.py bank)")
    import timbre_oracle as to
    space = to.voice_space(a.voice)
    if not space:
        print(f"no searchable zones for {a.voice}")
        return 2
    print(f"voice {a.voice}: {len(space)} zones "
          f"{[z['name'] for z in space]} | window {window}")
    ledger = []
    with tempfile.TemporaryDirectory(prefix="oracle_real_") as wd:
        ev = make_evaluate(a.voice, wd, ledger)
        base_feats = ev({})              # the .dsp defaults = the baseline
        base_d = to.window_distance(base_feats, window)
        print(f"defaults: {base_feats} -> distance {base_d:.3f}")

        def on_eval(pd, f, d):
            to.forge_append(a.voice, pd, f, distance=d)
            print(f"  eval {len(ledger):>3}: d={d:.3f} "
                  f"centroid={f.get('spectral_centroid_hz')} "
                  f"crest={f.get('crest_factor_db')}")

        res = to.search(ev, space, window, budget=a.budget, seed=a.seed,
                        on_eval=on_eval)
        print(json.dumps({"best_distance": res["best_distance"],
                          "best_params": res["best_params"],
                          "best_features": res["best_features"],
                          "evals": res["evals"],
                          "baseline_distance": round(base_d, 3)}, indent=1))
        if res["best_distance"] <= 0.0:
            print(f"LANDED: inside the window in {res['evals']} renders "
                  f"(baseline d={base_d:.2f})")
            return 0
        if base_d > 0 and res["best_distance"] <= base_d / 2.0:
            print(f"PARTIAL WIN: {base_d:.2f} -> {res['best_distance']:.2f} "
                  f"(honest: window not reached in budget)")
            return 0
        print("NO WIN inside budget — the recipe baseline stands (floor law)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
