#!/usr/bin/env python3
"""THE METAMORPHIC COURT — wave 63 (r-32 item 183): invariance tests
that need NO ground truth and NO reference corpus (the MTAM
methodology that found 16-51% error rates in commercial systems).

Musically-neutral transforms must leave the symbolic courts' verdicts
stable. A violated invariance is a COURT BUG or a non-robust
generation — either way, red:

  T1 TRANSPOSE +-N   (pitches + key + chords together) -> key court
                     sour count, flow, movement, structure UNCHANGED
  T2 TEMPO +-X%      (bpm field; beats don't move)     -> pocket/flow/
                     structure UNCHANGED
  T3 PAN MIRROR      (pan := -pan on every lane)       -> every
                     symbolic verdict UNCHANGED
  T4 LANE REORDER    (tracks list shuffled, content identical) ->
                     every symbolic verdict UNCHANGED

  run_metamorphic(song, genre) -> {violations: [...], checked: N}
"""
import copy
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

_NOTE_NAMES = ("C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A",
               "Bb", "B")


def transpose(song, semis):
    s = copy.deepcopy(song)
    for t in s.get("tracks", []) or []:
        for n in t.get("notes") or []:
            try:
                n["pitch"] = int(n["pitch"]) + semis
            except Exception:
                pass
    try:
        import theory
        k = theory.parse_key(s.get("key"))
        if k:
            pc = (int(k["tonic_pc"]) + semis) % 12
            mode = "minor" if "min" in str(k.get("mode", "")) else "major"
            s["key"] = f"{_NOTE_NAMES[pc]} {mode}"
    except Exception:
        pass
    for c in s.get("chords", []) or []:
        try:
            import theory
            ch = theory.parse_chord(c.get("chord"))
            if ch:
                root = (int(ch["root_pc"]) + semis) % 12
                tail = str(c["chord"])[_root_len(c["chord"]):]
                c["chord"] = _NOTE_NAMES[root] + tail
        except Exception:
            pass
    return s


def _root_len(sym):
    s = str(sym)
    return 2 if len(s) > 1 and s[1] in "b#" else 1


def tempo_shift(song, pct):
    s = copy.deepcopy(song)
    s["bpm"] = round(float(s.get("bpm", 120) or 120) * (1 + pct), 3)
    return s


def pan_mirror(song):
    s = copy.deepcopy(song)
    for t in s.get("tracks", []) or []:
        try:
            t["pan"] = -float(t.get("pan", 0) or 0)
        except Exception:
            pass
    return s


def lane_reorder(song):
    s = copy.deepcopy(song)
    tr = s.get("tracks", []) or []
    s["tracks"] = tr[::-1]
    return s


def _fingerprint(song, genre):
    """The stable-verdict tuple the transforms must preserve."""
    fp = {}
    try:
        import music_court as MC
        kv = MC.court_key(song, genre)
        fp["key_ok"] = bool(kv.get("ok", True))
        fp["key_sour"] = int(kv.get("sour", 0) or 0)
    except Exception:
        pass
    try:
        import flow_court as FC
        fv = FC.court_flow(song)
        fp["flow_convictions"] = len(fv.get("convictions", []) or [])
    except Exception:
        pass
    try:
        import movement_court as MV
        fp["movement"] = len(MV.court_movement(song).get(
            "advisories", []) or [])
    except Exception:
        pass
    try:
        import structure_court as SC
        sv = SC.court_structure(song, genre)
        fp["structure"] = len(sv.get("advisories", []) or [])
    except Exception:
        pass
    try:
        import symbolic_invariants as SI
        fp["parallels"] = SI.parallel_motion(song)["parallel_perfects"]
    except Exception:
        pass
    return fp


_PITCH_SENSITIVE = ("key_ok", "key_sour")


def run_metamorphic(song, genre=""):
    base = _fingerprint(song, genre)
    violations = []
    checked = 0

    def compare(tag, fp, skip=()):
        nonlocal checked
        for k, v in base.items():
            if k in skip:
                continue
            checked += 1
            if fp.get(k) != v:
                violations.append({
                    "transform": tag, "metric": k,
                    "base": v, "after": fp.get(k),
                    "why": (f"{tag}: '{k}' moved {v} -> {fp.get(k)} — a "
                            "musically-neutral transform changed a "
                            "verdict; court bug or fragile take")})

    for n in (+3, -4):
        compare(f"transpose{n:+d}", _fingerprint(transpose(song, n),
                                                 genre))
    for pct in (+0.06, -0.06):
        compare(f"tempo{pct:+.0%}", _fingerprint(tempo_shift(song, pct),
                                                 genre))
    compare("pan_mirror", _fingerprint(pan_mirror(song), genre))
    compare("lane_reorder", _fingerprint(lane_reorder(song), genre))
    return {"court": "metamorphic", "ok": not violations,
            "violations": violations, "checked": checked}


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="THE METAMORPHIC COURT (w63)")
    ap.add_argument("song")
    ap.add_argument("--genre", default="")
    a = ap.parse_args()
    v = run_metamorphic(json.load(open(a.song)), a.genre)
    print(json.dumps(v, indent=1))
    sys.exit(0 if v["ok"] else 1)
