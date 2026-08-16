#!/usr/bin/env python3
"""VOICE CHARACTER — wave 62 (r-17 items 210/212).

212 THE ANALOG PASS: a deterministic source transform that gives ANY
Faust voice the Diva-trimmer warmth — a slow (<0.5Hz) band-limited
random pitch drift of a few cents around the played frequency. The
drift LFO free-runs, so every note lands at a different drift point =
per-note variance without per-voice plumbing. (Per-note random PHASE
is the remaining 10% — stock phasors don't take injected phase; the
drift is the audible lever, named honestly.)

210 THE ATTACK-CLASS COURT: tonal roles have envelope contracts —
a pluck with a slow attack isn't a pluck, a pad that snaps isn't a
pad. Zone-default parse (cheap, zero renders): the voice's
hslider("attack", default...) vs the role's class window; song-side
source.params overrides honored.

  analogize(dsp_path, out_path, cents)   emit <name>_analog.dsp
  court_character(dsp_path)              dead-stiff voices flagged
  court_attack_class(song)               role/envelope mismatches
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INSTR = os.path.join(ROOT, "instruments")

# role -> (attack window seconds lo, hi); None = unbounded
ATTACK_CLASSES = {
    "pluck": (0.0, 0.05),
    "pad": (0.1, None),
    "lead": (0.0, 0.08),
    "keys": (0.0, 0.06),
    "string": (0.05, None),
}
_LIVELY = ("no.noise", "no.lfnoise", "no.pink_noise", "drift", "lfnoise")


def _freq_slider_re():
    return re.compile(
        r"^(\s*freq\s*=\s*hslider\s*\(\s*\"freq\"[^;]*;)", re.M)


def analogize(dsp_path, out_path=None, cents=4.0):
    """Emit the _analog twin: freq gains a +-cents band-limited drift.
    Returns out_path, or None when the voice has no standard freq
    slider (never guesses at a voice's internals)."""
    src = open(dsp_path).read()
    m = _freq_slider_re().search(src)
    if not m or "ANALOG PASS" in src:
        return None
    line = m.group(1)
    renamed = line.replace('"freq"', '"freq"', 1).replace(
        "freq =", "freq_raw =", 1)
    inject = (renamed + "\n"
              "// ANALOG PASS (w62, r-17): Diva-trimmer drift — slow "
              "band-limited\n"
              "// random walk, +-%.1f cents; free-running = per-note "
              "variance\n"
              "freq = freq_raw * pow(2.0, (%.2f * no.lfnoise(0.37)) "
              "/ 1200.0);" % (cents, cents))
    out = _freq_slider_re().sub(lambda _: inject, src, count=1)
    name = os.path.splitext(os.path.basename(dsp_path))[0]
    out_path = out_path or os.path.join(
        os.path.dirname(dsp_path), f"{name}_analog.dsp")
    open(out_path, "w").write(out)
    return out_path


def court_character(dsp_path):
    """Dead-stiff = identical pitch/phase every note ('obviously
    digital'). Advisory: no noise/drift source anywhere in the voice."""
    try:
        src = open(dsp_path).read()
    except Exception:
        return {"court": "character", "ok": True, "skipped": "unreadable"}
    lively = any(w in src for w in _LIVELY)
    advisories = []
    if not lively:
        advisories.append({
            "kind": "dead_stiff_voice",
            "voice": os.path.basename(dsp_path),
            "why": ("no drift/noise source in the voice — every note "
                    "lands identical, the 'obviously digital' tell; "
                    "analogize() adds the Diva-trimmer drift in one "
                    "pass")})
    return {"court": "character", "ok": True, "advisories": advisories}


def _voice_attack_default(voice_id):
    p = os.path.join(INSTR, f"{voice_id}.dsp")
    try:
        src = open(p).read()
    except Exception:
        return None
    m = re.search(r"hslider\s*\(\s*\"attack\"\s*,\s*([0-9.]+)", src)
    return float(m.group(1)) if m else None


def court_attack_class(song):
    """W62 (item 210): role/envelope contracts on tonal lanes."""
    advisories = []
    for t in (song or {}).get("tracks", []) or []:
        if not isinstance(t, dict) or t.get("muted") or not t.get("notes"):
            continue
        nm = str(t.get("name", "")).lower()
        role = next((r for r in ATTACK_CLASSES if r in nm), None)
        if role is None:
            continue
        src = t.get("source") or {}
        vid = str(src.get("id", ""))
        att = None
        params = src.get("params") or {}
        if "attack" in params:
            try:
                att = float(params["attack"])
            except Exception:
                att = None
        if att is None and vid:
            att = _voice_attack_default(vid)
        if att is None:
            continue
        lo, hi = ATTACK_CLASSES[role]
        if (lo is not None and att < lo) or (hi is not None and att > hi):
            want = (f">={lo * 1000:.0f}ms" if hi is None
                    else f"<={hi * 1000:.0f}ms" if lo == 0.0
                    else f"{lo * 1000:.0f}-{hi * 1000:.0f}ms")
            advisories.append({
                "kind": "attack_class", "track": t.get("name"),
                "role": role, "attack_s": att,
                "why": (f"'{t.get('name')}' plays the {role} role with a "
                        f"{att * 1000:.0f}ms attack — the class wants "
                        f"{want}; a {role} that "
                        f"{'snaps' if role == 'pad' else 'swells'} reads "
                        "as the wrong instrument, not a style")})
    return {"court": "attack_class", "ok": True, "advisories": advisories}


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="VOICE CHARACTER (w62)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a1 = sub.add_parser("analogize")
    a1.add_argument("voice")
    a1.add_argument("--cents", type=float, default=4.0)
    a2 = sub.add_parser("court")
    a2.add_argument("song")
    a = ap.parse_args()
    if a.cmd == "analogize":
        p = a.voice if a.voice.endswith(".dsp") else \
            os.path.join(INSTR, f"{a.voice}.dsp")
        out = analogize(p, cents=a.cents)
        print(out or "no standard freq slider — untouched")
    else:
        song = json.load(open(a.song))
        print(json.dumps(court_attack_class(song), indent=1))
