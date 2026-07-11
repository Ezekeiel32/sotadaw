#!/usr/bin/env python3
"""THE VERB BUS registry — producer verbs mounted on the ZERO-TOKEN direct lane.

The root cause it fixes (docs/SURFACE_LEDGER.md, measured 2026-07-05): every
producer verb shipped ONLY behind the LLM gateway — median prompt->proposal
595s in live telemetry (min 23.6s, max 1775s) — while the verb kernels
themselves run in 0.04-0.06s cold. A ~10,000x latency gap between what the
kernels can do and what the user experiences. The sidecar's zero-token lane
existed (make_track, hum_topline) but grew as bespoke if-branches; none of the
producer verbs were ever mounted on it. This registry gives the sidecar ONE
generic dispatch: request {"type":"verb","verb":"intensify","args":{...}}.

Contract per verb:
  tool     — script under tools/ (CLI subprocess, same rail daw_mcp uses)
  mutates  — True: runs against the _prop_ copy, files a receipt, locks +
             scope law apply, proposal event ships BEFORE the render (instant
             diff). False: read-only report against the BASE song.
  cli(name, args)    -> argv tail (name = _prop_<song> when mutating, else song)
  receipt(args, track_names, stdout) -> {"fields": [...], "track_wild": [...]}
             in the CONTAINMENT GRAMMAR (surgical.containment): note changes are
             authorized ONLY by track_wild or exact keys — "section:x"/"track:x"
             field strings are dead grammar the law never matches (the latent
             bug this file's birth fixed in daw_mcp too).
  timeout  — seconds

Unknown verbs ERROR at dispatch (never the silent-consume trap).
"""
import json


def _kernel_wild(tag):
    """Precise receipts: only the tracks the kernel itself reports touching
    (its <TAG>_JSON line). Falls back to all tracks if the line is missing."""
    def fn(args, track_names, stdout):
        for line in (stdout or "").splitlines():
            if line.startswith(tag + " "):
                try:
                    rep = json.loads(line.split(" ", 1)[1])
                    return {"fields": [], "track_wild": sorted(rep.get("tracks", {}))}
                except (json.JSONDecodeError, IndexError):
                    break
        return {"fields": [], "track_wild": list(track_names)}
    return fn


_intensify_wild = _kernel_wild("INTENSIFY_JSON")


REGISTRY = {
    # -------- energy / feel --------
    "intensify": dict(
        tool="intensify.py", mutates=True, timeout=60,
        cli=lambda n, a: [n, str(a["section"]), str(float(a["amount"])), "--write"],
        receipt=_intensify_wild),
    "humanize": dict(
        tool="expressive.py", mutates=True, timeout=60,
        cli=lambda n, a: [n, "--write"]
            + (["--track", str(a["track"])] if a.get("track") else [])
            + ["--amount", str(float(a.get("amount", 0.6))),
               "--seed", str(int(a.get("seed", 0)))],
        receipt=lambda a, tn, o: {"fields": [],
                                  "track_wild": [str(a["track"])] if a.get("track") else list(tn)}),
    "groove": dict(
        tool="groove.py", mutates=True, timeout=60,
        cli=lambda n, a: ["apply", n, str(a["track"]), str(a["groove"]),
                          str(float(a.get("amount", 1.0)))],
        receipt=lambda a, tn, o: {"fields": [f"track:{a['track']}:groove"],
                                  "track_wild": [str(a["track"])]}),
    "restyle": dict(
        tool="restyle.py", mutates=True, timeout=90,
        cli=lambda n, a: [n, str(a["genre"]), "--write"]
            + (["--bpm"] if a.get("bpm") else []),
        receipt=lambda a, tn, o: {"fields": ["meta:swing", "meta:bpm"],
                                  "track_wild": _kernel_wild("RESTYLE_JSON")(a, tn, o)["track_wild"]}),
    "color": dict(
        tool="color.py", mutates=True, timeout=60,
        cli=lambda n, a: [n, str(a["word"]), str(float(a.get("amount", 0.5))), "--write"]
            + (["--track", str(a["track"])] if a.get("track") else []),
        receipt=_kernel_wild("COLOR_JSON")),
    # -------- mix / production --------
    "automix": dict(
        tool="automix.py", mutates=True, timeout=60,
        cli=lambda n, a: [n, "--write"],
        receipt=lambda a, tn, o: {"fields": ["buses", "master", "automation"],
                                  "track_wild": list(tn)}),
    "prescribe": dict(
        tool="prescribe.py", mutates=True, timeout=120,
        cli=lambda n, a: [n, "--write"],
        receipt=lambda a, tn, o: {"fields": ["buses", "master", "automation"],
                                  "track_wild": list(tn)}),
    "finish": dict(
        tool="finish.py", mutates=True, timeout=180,
        cli=lambda n, a: [n],                    # finish.py writes <name> in place when --out absent
        receipt=lambda a, tn, o: {"fields": ["*"], "track_wild": []}),   # a macro: full-write truth
    "keep_jam": dict(                            # CAPTURE LAW's one-click door (BAND_SEAT):
        tool="keep_jam.py", mutates=True, timeout=90,   # the kept jam merges as a PROPOSAL
        cli=lambda n, a: [n, str(a["take"])]
            + (["--at-bar", str(int(a["at_bar"]))] if a.get("at_bar") is not None else []),
        # the kernel self-receipts its jam: lanes; the merge legitimately reshapes
        # the song's frame too — declare it or an honest merge reads OUT OF SCOPE
        receipt=lambda a, tn, o: {"fields": ["meta:lengthBars", "meta:sections"],
                                  "track_wild": []}),
    # -------- read-only reports (no proposal) --------
    "doctor": dict(
        tool="doctor.py", mutates=False, timeout=60,
        cli=lambda n, a: [n]),
    "energy_curve": dict(
        tool="energy_curve.py", mutates=False, timeout=60,
        cli=lambda n, a: [n] + (["--track", str(a["track"])] if a.get("track") else [])),
    "reference_match": dict(
        tool="reference_match.py", mutates=False, timeout=600,
        cli=lambda n, a: [str(a["reference"]), "--song", n]
            + (["--genre", str(a["genre"])] if a.get("genre") else [])),
    "memory": dict(                    # T2-S3: the session fact store, readable
        tool="session_recall.py", mutates=False, timeout=30,
        cli=lambda n, a: [n] + (["--track", str(a["track"])] if a.get("track") else [])),
}
