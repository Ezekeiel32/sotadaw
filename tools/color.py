#!/usr/bin/env python3
"""COLOR — semantic sound axes as deterministic DSP moves (Tier-2 #6, v1).

  color.py <song> <word> [amount 0..1] [--track NAME] [--write]

Words (v1, all Faust-track deterministic, all mix-law safe):
  warmer   — lowpass tilt down + a touch of drive on melodic voices
  darker   — lowpass tilt down, harder, no drive
  brighter — air EQ (+hiGain @6kHz) and any existing filter opens back up
  wider    — fx_widen on pad/keys/lead roles ONLY (kick/bass/808 NEVER widen:
             the automix mono-below-120 law holds here too)

HONEST SCOPE: vst3 params-based tracks are SKIPPED with a note — the semantic
maps are directional ('cutoff -') and applying them right needs current values
+ ranges in natural units (the Odin-silencer trap); that's the agent lane's
job until a v2 reads list-params ranges. Preset-blob tracks likewise (the blob
owns params). Locked tracks untouched. Repeats CLAMP (cutoff floor/ceiling,
width cap) — ten 'warmer' clicks converge instead of destroying the sound.

Grounding: 'warm'/'bright' are the two most stable crowd descriptors (SocialFX
480+ participants; SAFE; Audealize), spectral centroid is THE brightness
correlate in the timbre literature (so the battery's centroid-ordering check
tests the perceptual claim itself), and DAFx17 built warmth/brightness as
spectrum tilts — the same mechanism used here (docs/SURFACE_LEDGER.md refs).
"""
import argparse, copy, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from chordvote import is_drum_track
from automix import role
import songname

WORDS = ("warmer", "darker", "brighter", "wider")
CUT_FLOOR, CUT_CEIL = 900.0, 16000.0
WIDTH_CAP = 1.8


def _get_fx(t, fid):
    for f in t.get("fx", []):
        if f.get("id") == fid:
            return f
    return None


def _filter_of(t, default_cut=14000.0):
    f = _get_fx(t, "fx_filter")
    if f is None:
        f = {"id": "fx_filter", "params": {"cutoff": default_cut, "res": 0.4}}
        t.setdefault("fx", []).append(f)
    f.setdefault("params", {}).setdefault("cutoff", default_cut)
    return f


def color(song, word, amount=0.5, only_track=None):
    if word not in WORDS:
        raise SystemExit(f"unknown color '{word}' — have: {', '.join(WORDS)}")
    amount = max(0.0, min(1.0, float(amount)))
    rep = {"word": word, "amount": amount, "tracks": {}, "skipped": {}}
    for t in song.get("tracks", []):
        nm = t.get("name", "?")
        if only_track and nm != only_track:
            continue
        if t.get("locked"):
            rep["skipped"][nm] = "locked"
            continue
        src = t.get("source", {}) or {}
        if src.get("kind") == "vst3" or src.get("preset") or src.get("plugin"):
            rep["skipped"][nm] = ("vst3: semantic map is directional — use the agent lane "
                                  "(natural-unit values need list-params); v2 will read ranges")
            continue
        drum = is_drum_track(t)
        r = role(t)
        moves = []
        if word in ("warmer", "darker"):
            if drum and word == "warmer":
                rep["skipped"][nm] = "drums keep their transient (warmth targets melodic voices)"
                continue
            f = _filter_of(t)
            factor = 1.0 - (0.35 if word == "warmer" else 0.55) * amount
            old = float(f["params"]["cutoff"])
            f["params"]["cutoff"] = round(max(CUT_FLOOR, old * factor), 1)
            moves.append(f"fx_filter.cutoff {old:g}->{f['params']['cutoff']:g}")
            if word == "warmer" and not drum and r not in ("kick",):
                s = _get_fx(t, "fx_saturate")
                if s is None:
                    s = {"id": "fx_saturate", "params": {"drive": 0.0}}
                    t.setdefault("fx", []).append(s)
                old_d = float(s.setdefault("params", {}).get("drive", 0.0))
                s["params"]["drive"] = round(min(0.6, old_d + 0.18 * amount), 3)
                moves.append(f"fx_saturate.drive {old_d:g}->{s['params']['drive']:g}")
        elif word == "brighter":
            f = _get_fx(t, "fx_filter")
            if f is not None and f.get("params", {}).get("cutoff"):
                old = float(f["params"]["cutoff"])
                f["params"]["cutoff"] = round(min(CUT_CEIL, old * (1.0 + 0.9 * amount)), 1)
                moves.append(f"fx_filter.cutoff {old:g}->{f['params']['cutoff']:g}")
            eq = next((x for x in t.get("fx", []) if x.get("type") == "eq"), None)
            if eq is None:
                eq = {"type": "eq", "params": {"hiFreq": 6000.0, "hiGain": 0.0}}
                t.setdefault("fx", []).append(eq)
            eq.setdefault("params", {}).setdefault("hiGain", 0.0)
            old_g = float(eq["params"]["hiGain"])
            eq["params"]["hiFreq"] = float(eq["params"].get("hiFreq", 6000.0) or 6000.0)
            eq["params"]["hiGain"] = round(min(6.0, old_g + 3.5 * amount), 2)
            moves.append(f"eq.hiGain {old_g:g}->{eq['params']['hiGain']:g}dB @{eq['params']['hiFreq']:g}Hz")
        elif word == "wider":
            if drum or r in ("kick", "bass") or "808" in nm.lower() or "sub" in nm.lower():
                rep["skipped"][nm] = "mono law: subs/kick are never widened"
                continue
            w = _get_fx(t, "fx_widen")
            if w is None:
                w = {"id": "fx_widen", "params": {"width": 1.0}}
                t.setdefault("fx", []).append(w)
            old_w = float(w.setdefault("params", {}).get("width", 1.0))
            w["params"]["width"] = round(min(WIDTH_CAP, old_w + 0.7 * amount), 3)
            moves.append(f"fx_widen.width {old_w:g}->{w['params']['width']:g}")
        if moves:
            rep["tracks"][nm] = moves
    return rep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("song"); ap.add_argument("word")
    ap.add_argument("amount", nargs="?", type=float, default=0.5)
    ap.add_argument("--track", default=None)
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    name = songname.resolve(a.song)
    path = os.path.join(ROOT, "songs", f"{name}.json")
    song = json.load(open(path))
    rep = color(song, a.word, a.amount, a.track)
    if a.write:
        json.dump(song, open(path, "w"), indent=1)
    for nm, mv in rep["tracks"].items():
        print(f"[color] {nm}: " + "; ".join(mv))
    for nm, why in rep["skipped"].items():
        print(f"[color] {nm}: SKIPPED — {why}")
    if not rep["tracks"]:
        print(f"[color] no track took '{a.word}' — see skips above")
    print("COLOR_JSON " + json.dumps(rep))


if __name__ == "__main__":
    main()
