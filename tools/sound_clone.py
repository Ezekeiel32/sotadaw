#!/usr/bin/env python3
"""THE SOUND CLONER (BEST_DAW_30 #5) — "make me THIS sound", parameters not samples.

  sound_clone.py <target.wav> <name> [--family wt_morph] [--budget 60] [--seed 1]

Chezy's founding line, verbatim: "the agent can literally create sounds as
needed, any sound it/user wants based on the intelligence of frequencies of
this platform." The pipeline:

  1. FOOTPRINT the target on ear_pick's own ruler (5 band shares + centroid +
     sustain — the register-true metric the import ear already trusts).
  2. PICK BEFORE FORGE: search the measured voice table first; a close-enough
     existing voice is returned as-is (never mint what the library has).
  3. FORGE: past the gate, take a TEMPLATE family (its fit space = the .dsp's
     own hslider ranges, parsed — the zones ARE the search space), and run a
     seeded coordinate descent through the REAL engine (JIT rail, seconds per
     candidate) minimizing footprint distance.
  4. The product is SYMBOLIC: a fitted source dict {"kind":"faust","id":
     <template>,"params":{...}} saved to library/clones/<name>.json with the
     target's sha, both distances, and every iteration receipt. Zero samples
     copied — analysis in, parameters out (TIMBRE LAW clean).

--selftest: forge against a target rendered FROM a template with known params —
the cloner must recover a closer voice than the default (the planted-recovery
proof, no taste required).
"""
import argparse, hashlib, json, math, os, re, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import numpy as np                                    # noqa: E402
import ear_pick as EP                                 # the ruler + the table

SONGS = os.path.join(ROOT, "songs")
M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")
CLONES = os.path.join(ROOT, "library", "clones")
PICK_GATE = 0.55          # <= this footprint distance: the pick IS the sound
TEMPLATES = ("wt_morph", "fm4_keys", "supersaw", "additive_harm", "pluck")
SKIP_ZONES = {"freq", "gain"}                         # played, not designed


def parse_zones(template):
    """The .dsp's hsliders ARE the fit space: {zone: (default, lo, hi)}."""
    src = open(os.path.join(ROOT, "instruments", f"{template}.dsp")).read()
    zones = {}
    for m in re.finditer(r'hslider\("([^"]+)"\s*,\s*([-\d.]+)\s*,\s*([-\d.]+)'
                         r'\s*,\s*([-\d.]+)', src):
        nm, d, lo, hi = m.group(1), float(m.group(2)), float(m.group(3)), float(m.group(4))
        if nm not in SKIP_ZONES:
            zones[nm] = (d, lo, hi)
    return zones


def probe_notes(pitch):
    return [{"start": float(b * 2), "len": 1.5, "pitch": int(pitch), "vel": 0.85}
            for b in range(3)]


def render_fp(template, params, pitch, tag):
    """One candidate through the REAL engine -> footprint (None on failure)."""
    song = {"bpm": 120, "lengthBars": 2, "masterGainDb": 0.0,
            "tracks": [{"name": "probe", "gainDb": -6.0,
                        "source": {"kind": "faust", "id": template,
                                   "params": {k: round(float(v), 4)
                                              for k, v in params.items()}},
                        "notes": probe_notes(pitch)}]}
    pj = os.path.join(SONGS, f"_clone_{tag}.json")
    pw = pj.replace(".json", ".wav")
    json.dump(song, open(pj, "w"))
    try:
        r = subprocess.run([M1, "render", pj, pw], capture_output=True,
                           cwd=ROOT, timeout=180)
        if r.returncode != 0 or not os.path.exists(pw):
            return None
        sr, x = EP._load_mono(pw)
        return EP.footprint(x, sr)
    finally:
        for p in (pj, pw):
            os.path.exists(p) and os.remove(p)


def target_footprint(wav):
    sr, x = EP._load_mono(wav)
    fp = EP.footprint(x, sr)
    if fp is None:
        sys.exit(f"target too short/quiet to footprint: {wav}")
    # register from the spectral centroid's octave (rough but honest for probes)
    c = fp["centroid_hz"]
    pitch = 40 if c < 300 else (57 if c < 1400 else 72)
    return fp, pitch


def pick_stage(tfp, pitch):
    """The measured voice table, register-true — the SELECTIVE half (shipped)."""
    reg = "bass" if pitch < 52 else ("high" if pitch > 70 else "mid")
    try:
        table = EP._table()
    except Exception:
        return None, None
    best, bd = None, 1e9
    for voice, regs in (table or {}).items():
        fp = (regs or {}).get(reg)
        if fp:
            d = EP.distance(tfp, fp)
            if d < bd:
                best, bd = voice, d
    return best, (round(bd, 4) if best else None)


def forge(tfp, pitch, template, budget, seed, log):
    zones = parse_zones(template)
    params = {k: d for k, (d, lo, hi) in zones.items()}
    base_fp = render_fp(template, params, pitch, "base")
    if base_fp is None:
        return None, None, []
    best_d = EP.distance(tfp, base_fp)
    receipts = [{"round": 0, "zone": "(defaults)", "distance": best_d}]
    rng = np.random.default_rng(seed)
    order = list(zones)
    spent, rounds = 1, 0
    while spent < budget:
        rounds += 1
        improved = False
        rng.shuffle(order)
        for z in order:
            if spent >= budget:
                break
            d0, lo, hi = zones[z]
            cur = params[z]
            span = (hi - lo) / (2.0 ** min(rounds, 4))     # shrink per round
            cands = [max(lo, cur - span), min(hi, cur + span)]
            for cv in cands:
                if abs(cv - cur) < 1e-9 or spent >= budget:
                    continue
                fp = render_fp(template, {**params, z: cv}, pitch,
                               f"{z[:6]}{spent}")
                spent += 1
                if fp is None:
                    continue
                d = EP.distance(tfp, fp)
                if d < best_d - 1e-4:
                    best_d, params[z], improved = d, cv, True
                    receipts.append({"round": rounds, "zone": z,
                                     "value": round(cv, 4), "distance": d})
                    log(f"  r{rounds} {z} -> {cv:.3f}  d {d:.4f}")
        if not improved:
            break
    return params, best_d, receipts


def clone(wav, name, family=None, budget=60, seed=1, quiet=False):
    log = (lambda *a: None) if quiet else print
    tfp, pitch = target_footprint(os.path.abspath(wav))
    tsha = hashlib.sha256(open(wav, "rb").read()).hexdigest()[:16]
    pick, pick_d = pick_stage(tfp, pitch)
    log(f"[clone] target centroid {tfp['centroid_hz']:.0f}Hz sustain "
        f"{tfp.get('sustain', 0):.2f} | pick: {pick} d={pick_d}")
    if pick is not None and pick_d is not None and pick_d <= PICK_GATE and not family:
        out = {"name": name, "verdict": "PICK", "source":
               {"kind": "faust", "id": pick}, "distance": pick_d,
               "pick": {"voice": pick, "distance": pick_d},
               "target": {"wav": os.path.abspath(wav), "sha16": tsha},
               "when": time.strftime("%F %T")}
        _save(out)
        return out
    template = family or _template_for(tfp)
    log(f"[clone] FORGE on template '{template}' (budget {budget} renders)")
    params, d, receipts = forge(tfp, pitch, template, budget, seed, log)
    if params is None:
        sys.exit(f"forge failed: template '{template}' would not render")
    out = {"name": name, "verdict": "FORGED", "source":
           {"kind": "faust", "id": template,
            "params": {k: round(float(v), 4) for k, v in params.items()}},
           "distance": d, "pick": {"voice": pick, "distance": pick_d},
           "target": {"wav": os.path.abspath(wav), "sha16": tsha},
           "iterations": receipts, "seed": seed,
           "when": time.strftime("%F %T")}
    _save(out)
    log(f"[clone] {name}: FORGED d={d:.4f} (pick was {pick_d}) -> "
        f"library/clones/{name}.json")
    return out


def _template_for(tfp):
    """Sustainy -> wavetable pad space; plucky bright -> FM; else supersaw."""
    sus = tfp.get("sustain", 1.0)
    if sus >= 0.85:
        return "wt_morph"
    if tfp["centroid_hz"] > 900:
        return "fm4_keys"
    return "wt_morph"


def _save(out):
    os.makedirs(CLONES, exist_ok=True)
    p = os.path.join(CLONES, f"{out['name']}.json")
    tmp = p + ".w~"
    json.dump(out, open(tmp, "w"), indent=1)
    os.replace(tmp, p)


def selftest():
    """Planted recovery: target = wt_morph at wave=1.8 (bright). The forge from
    defaults (wave 0.5) must land measurably closer than the defaults."""
    tgt = os.path.join(SONGS, "_clone_self_target.wav")
    song = {"bpm": 120, "lengthBars": 2, "masterGainDb": 0.0,
            "tracks": [{"name": "t", "gainDb": -6.0,
                        "source": {"kind": "faust", "id": "wt_morph",
                                   "params": {"wave": 1.8, "cutoff": 11000}},
                        "notes": probe_notes(57)}]}
    pj = tgt.replace(".wav", ".json")
    json.dump(song, open(pj, "w"))
    ok = False
    try:
        r = subprocess.run([M1, "render", pj, tgt], capture_output=True, timeout=180)
        assert r.returncode == 0
        tfp, pitch = target_footprint(tgt)
        d_default = EP.distance(tfp, render_fp("wt_morph",
                                {k: d for k, (d, lo, hi) in parse_zones("wt_morph").items()},
                                pitch, "selfdef"))
        params, d_fit, _ = forge(tfp, pitch, "wt_morph", budget=24, seed=3,
                                 log=lambda *a: None)
        print(f"  default d={d_default:.4f} -> fitted d={d_fit:.4f} "
              f"(wave -> {params.get('wave'):.2f}, planted 1.8)")
        ok = d_fit < d_default * 0.6 and abs(params.get("wave", 0) - 1.8) < 0.7
        print(f"sound_clone selftest: {'OK (planted brightness recovered)' if ok else 'FAIL'}")
    finally:
        for p in (pj, tgt):
            os.path.exists(p) and os.remove(p)
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("wav", nargs="?")
    ap.add_argument("name", nargs="?")
    ap.add_argument("--family", choices=TEMPLATES)
    ap.add_argument("--budget", type=int, default=60)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not (a.wav and a.name):
        sys.exit("need <target.wav> <name> (or --selftest)")
    out = clone(a.wav, a.name, family=a.family, budget=a.budget, seed=a.seed,
                quiet=a.json)
    if a.json:
        print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
