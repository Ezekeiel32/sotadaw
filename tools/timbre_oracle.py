#!/usr/bin/env python3
"""THE BRAIN BR-C — THE TIMBRE ORACLE (docs/SPEC_THE_BRAIN.md PART II B2).

The toy-sound killer: given a SIGNATURE WINDOW (per-feature [lo, hi] bands —
the gold/DNA form), find voice zone parameters whose RENDER lands inside it.

Pieces:
- zone_space(dsp_text): the search space read straight from the .dsp — every
  hslider/nentry (name, default, lo, hi, step); performance zones (freq/gain/
  gate) excluded — they are note-driven, not timbre.
- window_distance(features, window): 0.0 inside the window; outside = sum of
  normalized hinge violations. THE METER of this whole organ.
- search(evaluate, space, ...): seeded bounded (mu+lambda) evolution strategy.
  evaluate(params)->features is INJECTED: batteries pass a synthetic model,
  the real rig passes render+measure. Stops EARLY at distance 0 (inside the
  window is DONE — renders are the currency). CMA-ES is an upgrade slot
  behind this same signature if/when the pip lands; on <=11-dim boxes
  (measured: 588 zones / 111 voices, avg 5.3, max 11) a sigma-adaptive ES
  converges in tens of evaluations.
- THE FORGE LOG (telemetry/forge_log.jsonl): every real evaluation banks
  (voice, params, features) — the amortization dataset writes itself.
  one_shot() warm-starts from the log's nearest landed neighbor.

LAWS: FLOOR LAW — the oracle ships behind the recipe baseline unless its
census distance WINS (the caller compares; this module just reports).
FAIL-OPEN: the forge log never breaks a search. DETERMINISM: same seed +
same evaluate = the same trajectory (batteries replay it).
"""
import json
import math
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEF_ROOT = os.path.dirname(HERE)

PERFORMANCE_ZONES = {"freq", "gain", "gate"}     # played, never searched
FORGE_NAME = "forge_log.jsonl"

_ZONE_RE = re.compile(
    r'(?:hslider|nentry)\s*\(\s*"([^"]+)"\s*,\s*([-\d.eE+]+)\s*,\s*([-\d.eE+]+)'
    r'\s*,\s*([-\d.eE+]+)\s*,\s*([-\d.eE+]+)\s*\)')


def zone_space(dsp_text):
    """[{name, default, lo, hi, step}] for every searchable zone in a .dsp."""
    out = []
    for m in _ZONE_RE.finditer(dsp_text or ""):
        name = m.group(1).split("/")[-1].strip()
        if name.lower() in PERFORMANCE_ZONES:
            continue
        try:
            d, lo, hi, st = (float(m.group(i)) for i in (2, 3, 4, 5))
        except ValueError:
            continue
        if hi <= lo:
            continue
        out.append({"name": name, "default": d, "lo": lo, "hi": hi, "step": st})
    return out


def voice_space(voice, root=None):
    """zone_space for instruments/<voice>.dsp. [] when unreadable."""
    root = root or DEF_ROOT
    try:
        return zone_space(open(os.path.join(root, "instruments", f"{voice}.dsp")).read())
    except OSError:
        return []


def window_distance(features, window):
    """0.0 = every feature inside its [lo, hi] band. Outside: per-feature
    hinge violation normalized by the band's half-width (so 'one band-width
    out' costs ~2.0 regardless of unit). Missing features honestly count as
    one full violation each — an unmeasured feature is never assumed in."""
    if not window:
        return 0.0
    total = 0.0
    for k, band in window.items():
        try:
            lo, hi = float(band[0]), float(band[1])
        except (TypeError, ValueError, IndexError):
            continue
        half = max((hi - lo) / 2.0, 1e-9)
        v = features.get(k) if isinstance(features, dict) else None
        if v is None:
            total += 1.0
            continue
        v = float(v)
        if v < lo:
            total += (lo - v) / half
        elif v > hi:
            total += (v - hi) / half
    return total


def _clamp(x, lo, hi):
    return lo if x < lo else hi if x > hi else x


def _quant(x, z):
    st = z.get("step") or 0.0
    if st > 0:
        x = z["lo"] + round((x - z["lo"]) / st) * st
    return _clamp(x, z["lo"], z["hi"])


def search(evaluate, space, window, budget=60, seed=7, start=None,
           mu=3, lam=8, on_eval=None):
    """Bounded (mu+lambda)-ES. evaluate(params_dict) -> features_dict.
    Returns {best_params, best_features, best_distance, evals, trace}.
    Early-stops the moment a candidate lands INSIDE the window."""
    if not space:
        return {"best_params": {}, "best_features": {}, "best_distance": float("inf"),
                "evals": 0, "trace": []}
    rng = random.Random(seed)
    names = [z["name"] for z in space]
    spans = {z["name"]: (z["hi"] - z["lo"]) for z in space}

    def make(pd):
        return {z["name"]: _quant(pd.get(z["name"], z["default"]), z) for z in space}

    def run_eval(pd):
        f = evaluate(pd) or {}
        d = window_distance(f, window)
        if on_eval is not None:
            try:
                on_eval(pd, f, d)
            except Exception:
                pass
        return f, d

    pop = []
    seeds = [make(start or {})]
    seeds.append(make({}))                      # the .dsp defaults
    while len(seeds) < mu + 1:
        seeds.append(make({z["name"]: rng.uniform(z["lo"], z["hi"]) for z in space}))
    evals, trace = 0, []
    best = None
    for pd in seeds:
        if evals >= budget:
            break
        f, d = run_eval(pd)
        evals += 1
        pop.append((d, pd, f))
        trace.append(round(d, 4))
        if best is None or d < best[0]:
            best = (d, pd, f)
        if d <= 0.0:
            return {"best_params": pd, "best_features": f, "best_distance": 0.0,
                    "evals": evals, "trace": trace}
    sigma = 0.25                                # fraction of each span
    while evals < budget:
        pop.sort(key=lambda t: t[0])
        parents = pop[:mu]
        children, improved = [], False
        for _ in range(min(lam, budget - evals)):
            _d0, p0, _f0 = parents[rng.randrange(len(parents))]
            cand = make({n: p0[n] + rng.gauss(0.0, sigma * spans[n]) for n in names})
            f, d = run_eval(cand)
            evals += 1
            children.append((d, cand, f))
            trace.append(round(d, 4))
            if d < best[0]:
                best, improved = (d, cand, f), True
            if d <= 0.0:
                return {"best_params": cand, "best_features": f, "best_distance": 0.0,
                        "evals": evals, "trace": trace}
        pop = (parents + children)
        # 1/5-success-rule direction: improvement widens the step a touch,
        # a stalled generation ANNEALS hard — the window is a bullseye, and
        # renders are the currency (a growing sigma near the optimum scatters
        # forever; measured: 3-dim toy stuck at d=0.42 with the inverted rule)
        sigma = min(0.5, sigma * 1.1) if improved else max(0.005, sigma * 0.65)
    return {"best_params": best[1], "best_features": best[2],
            "best_distance": round(best[0], 6), "evals": evals, "trace": trace}


# ---------------------------------------------------------------- forge log
def forge_path(root=None):
    return os.path.join(root or DEF_ROOT, "telemetry", FORGE_NAME)


def forge_append(voice, params, features, distance=None, root=None, t=None):
    """Bank one real evaluation. Fail-open."""
    try:
        import time as _t
        row = {"t": round(float(_t.time() if t is None else t), 1), "voice": voice,
               "params": params, "features": features}
        if distance is not None:
            row["distance"] = round(float(distance), 6)
        p = forge_path(root)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "a") as f:
            f.write(json.dumps(row) + "\n")
        return True
    except Exception:
        return False


def forge_rows(voice=None, root=None, cap=5000):
    out = []
    try:
        for ln in open(forge_path(root)):
            ln = ln.strip()
            if not ln:
                continue
            try:
                r = json.loads(ln)
            except json.JSONDecodeError:
                continue
            if voice is None or r.get("voice") == voice:
                out.append(r)
    except OSError:
        pass
    return out[-cap:]


def one_shot(voice, window, root=None):
    """Warm start: the logged params whose logged FEATURES sit closest to the
    window (by the same meter). None when the log has nothing for the voice —
    an honest miss, never a guess."""
    best, best_d = None, float("inf")
    for r in forge_rows(voice, root):
        d = window_distance(r.get("features") or {}, window)
        if d < best_d:
            best, best_d = r.get("params"), d
    return (best, best_d) if best is not None else (None, None)


# ---------------------------------------------------------------- self-test
def _selftest():
    space = [{"name": "punch", "default": 0.5, "lo": 0.0, "hi": 1.0, "step": 0.01},
             {"name": "decay", "default": 1.0, "lo": 0.2, "hi": 3.0, "step": 0.01}]
    target = {"punch": 0.8, "decay": 0.42}

    def synth(pd):        # a fake voice: features are smooth functions of params
        return {"centroid_hz": 900 + 2600 * abs(pd["punch"] - target["punch"]),
                "decay_ms": 300 + 900 * abs(pd["decay"] - target["decay"])}
    window = {"centroid_hz": [800, 1100], "decay_ms": [250, 420]}
    res = search(synth, space, window, budget=80, seed=3)
    ok = res["best_distance"] <= 0.0
    print(f"selftest: landed={ok} evals={res['evals']} params={res['best_params']}")
    return 0 if ok else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    if len(sys.argv) > 1:
        sp = voice_space(sys.argv[1])
        print(json.dumps(sp, indent=1))
        print(f"{len(sp)} searchable zones", file=sys.stderr)
    else:
        print("usage: timbre_oracle.py <voice> | --selftest")
