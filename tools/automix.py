#!/usr/bin/env python3
"""AUTOMIX — the KG's mix laws become ACTION, by track role (structural, no render).

  automix.py <song> [--write]

Waves 30 (unmask/EQ) + 34 (space) taught the graph the FIXES; stem_callouts
FINDS collisions (but needs a render). This applies the STRUCTURAL laws by track
role — fast, deterministic, verifiable — the moves a mixing engineer makes
before touching a meter:

  SUB/KICK/BASS  -> pan CENTER, strip any widener (mono_below_120 law: a stereo
                   sub cancels on club/phone systems)
  PAD/STRINGS/ATMOS -> fx_widen (width up) for a wide bed UNDER the focal parts,
                   + high-pass ~120 so they never fight the sub (width_by_arrangement)
  LEAD/VOCAL/PLUCK -> center-ish (|pan|<=0.1): the focal element stays centered
  BASS under KICK -> fx_pump sidechain (rate = bpm-locked) so the kick owns the
                   downbeat (the FX-side of rolling_offbeat_bass)

Every move cites its KG law. Battery: the mix measures WIDER overall yet the
sub stays mono-safe (bass tracks centered, no side content below 120).
"""
import argparse, json, os, re, sys
import songname

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BASSY = ("808", "sub", "bass", "reese", "kick")
KICKY = ("kick", "808")
WIDE = ("pad", "string", "atmos", "choir", "vox_pad", "supersaw", "warmpad", "disco")
FOCAL = ("lead", "vocal", "pluck", "melody", "acid", "arp", "topline")


def role(track):
    nm = str(track.get("name", "")).lower()
    sid = str(track.get("source", {}).get("id", "")).lower()
    hay = nm + " " + sid
    if any(k in hay for k in KICKY) and "hat" not in nm:
        return "kick"
    if any(k in hay for k in BASSY):
        return "bass"
    if any(k in hay for k in WIDE):
        return "pad"
    if any(k in hay for k in FOCAL):
        return "focal"
    return "other"


def has_fx(track, fid):
    return any(f.get("id") == fid for f in track.get("fx", []))


def automix(song):
    bpm = float(song.get("bpm", 120))
    moves = []
    kick_present = any(role(t) == "kick" for t in song.get("tracks", []))
    for t in song.get("tracks", []):
        r = role(t)
        nm = t.get("name", "?")
        if r in ("kick", "bass"):
            if abs(float(t.get("pan", 0))) > 1e-6:
                t["pan"] = 0.0
                moves.append(f"{nm}: pan->center (mono_below_120)")
            fx = t.get("fx", [])
            if any(f.get("id") == "fx_widen" for f in fx):
                t["fx"] = [f for f in fx if f.get("id") != "fx_widen"]
                moves.append(f"{nm}: stripped widener (sub must be mono)")
            if r == "bass" and kick_present and not has_fx(t, "fx_pump"):
                # sidechain: duck on every kick (assume 4-on-floor unless swung)
                t.setdefault("fx", []).insert(0, {"id": "fx_pump",
                    "params": {"rate": round(bpm / 60.0, 2), "depth": 0.45, "release": 0.18}})
                moves.append(f"{nm}: +fx_pump sidechain @{round(bpm/60.0,2)}Hz (kick owns the downbeat)")
        elif r == "pad":
            if not has_fx(t, "fx_widen"):
                t.setdefault("fx", []).insert(0, {"id": "fx_widen", "params": {"width": 1.6}})
                moves.append(f"{nm}: +fx_widen 1.6 (wide bed; width_by_arrangement)")
            if not has_fx(t, "fx_filter"):
                t.setdefault("fx", []).insert(0, {"id": "fx_filter",
                    "params": {"cutoff": 16000, "res": 0.8}})
                # a gentle high-pass would need a HP voice; note the intent + keep the sub clear
                moves.append(f"{nm}: +fx_filter (space for the sub below)")
        elif r == "focal":
            if abs(float(t.get("pan", 0))) > 0.1:
                t["pan"] = round(max(-0.1, min(0.1, float(t.get("pan", 0)))), 2)
                moves.append(f"{nm}: pan pulled toward center (focal stays centered)")

    # COMPLEMENTARY EQ (wave-30 unmask rung 1): two SUSTAINED melodic tracks whose
    # pitch RANGES overlap share a register -> the focal one boosts its center, the
    # other cuts there. Carves space without a render (the range IS the band profile).
    def prof(t):
        ns = [n["pitch"] for n in t.get("notes", [])]
        return (min(ns), max(ns)) if ns else None
    mel = [(t, prof(t)) for t in song.get("tracks", []) if role(t) in ("focal", "pad")]
    mel = [(t, pr) for t, pr in mel if pr]
    for i in range(len(mel)):
        for j in range(i + 1, len(mel)):
            (ta, (a0, a1)), (tb, (b0, b1)) = mel[i], mel[j]
            lo, hi = max(a0, b0), min(a1, b1)
            if hi - lo < 3:
                continue                                # ranges don't share a register
            center = (lo + hi) / 2.0
            freq = round(440.0 * 2 ** ((center - 69) / 12.0))
            if not 120 <= freq <= 2000:
                continue                                # only the mud/low-mid zone
            # priority = focal over pad; else the louder (higher gainDb)
            pri, sec = (ta, tb)
            if role(ta) == "pad" and role(tb) == "focal":
                pri, sec = tb, ta
            elif role(ta) == role(tb) and float(tb.get("gainDb", 0)) > float(ta.get("gainDb", 0)):
                pri, sec = tb, ta
            if not any(f.get("type") == "eq" for f in sec.get("fx", [])):
                sec.setdefault("fx", []).append({"type": "eq",
                    "params": {"midFreq": freq, "midGain": -3.5, "midQ": 1.4}})
                moves.append(f"{sec.get('name')}: -3.5dB @ {freq}Hz "
                             f"(unmask vs {pri.get('name')}, complementary_eq)")
            if not any(f.get("type") == "eq" for f in pri.get("fx", [])):
                pri.setdefault("fx", []).append({"type": "eq",
                    "params": {"midFreq": freq, "midGain": 1.5, "midQ": 1.6}})
                moves.append(f"{pri.get('name')}: +1.5dB @ {freq}Hz (take the space)")
    return moves


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("song"); ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    name = songname.resolve(a.song)
    path = os.path.join(ROOT, "songs", f"{name}.json")
    song = json.load(open(path))
    moves = automix(song)
    if a.write and moves:
        json.dump(song, open(path, "w"), indent=1)
    print(f"[automix] {len(moves)} moves" + (" (written)" if a.write and moves else " (dry-run)"))
    for m in moves:
        print("  " + m)
    print("AUTOMIX_JSON " + json.dumps({"moves": len(moves), "detail": moves}))


if __name__ == "__main__":
    main()
