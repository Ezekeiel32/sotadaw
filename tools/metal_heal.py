#!/usr/bin/env python3
"""THE METAL MIX-HEAL — wave 58 (r-23 item 153).

Genre-conditional (metal/rock/punk families) court + deterministic
chain heal. The r-23 anchors verbatim: rhythm guitars DOUBLE-TRACKED
hard L/R; HPF low-tuned guitars 100-140Hz; the GRIND (800Hz-1.5kHz) is
PROTECTED — the legacy scooped-mids advice is the #1 anti-authenticity
trap in modern metal; a gentle narrow dip (~950Hz) opens the snare
crack pocket; fizz notched 5-9kHz.

  court_metal_mix(song, genre)  advisories: undoubled rhythm guitar,
                                unfiltered low guitar, THE SCOOP TRAP
                                (fx_bell <=-6dB inside the grind zone)
  heal_metal_mix(song, verdict) mint the twin (notes copied, panned
                                +-0.85, the birth-doubling X/XR
                                convention), fx_hipass 120, clamp the
                                scoop to -3dB, land the pocket dip +
                                fizz notch (once-marker metal_chain)
"""
import copy
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

_METAL = ("metal", "metalcore", "deathcore", "djent", "thrash", "doom",
          "sludge", "nu_metal", "numetal", "melodeath", "black_metal",
          "death_metal", "hardcore_punk", "punk", "grunge", "hard_rock",
          "hardrock", "post_hardcore")
_GTR = ("guitar", "gtr", "riff", "rhythm", "chug", "power_chord",
        "distgtr", "dist_gtr")


def _is_metal(genre):
    g = str(genre or "").lower().replace("-", "_").replace(" ", "_")
    return any(w in g for w in _METAL) and "gospel" not in g


def _guitar_lanes(song):
    out = []
    for t in (song or {}).get("tracks", []) or []:
        if not isinstance(t, dict) or t.get("muted") or not t.get("notes"):
            continue
        nm = str(t.get("name", "")).lower()
        if nm.endswith(("_sketch", "_identity")):
            continue
        if any(w in nm for w in _GTR) and not any(
                w in nm for w in ("bass", "acoustic")):
            out.append(t)
    return out


def court_metal_mix(song, genre=""):
    if not _is_metal(genre):
        return {"court": "metal_mix", "ok": True, "advisories": [],
                "skipped": "not a metal-family genre"}
    advisories = []
    names = {t.get("name") for t in (song or {}).get("tracks", [])
             if isinstance(t, dict)}
    gtrs = _guitar_lanes(song)
    for t in gtrs:
        nm = str(t.get("name", ""))
        twin = (nm + "R" in names) or (nm.endswith("R") and
                                       nm[:-1] in names)
        if not twin and abs(float(t.get("pan", 0) or 0)) < 0.5:
            advisories.append({
                "kind": "undoubled_rhythm_guitar", "track": nm,
                "why": (f"'{nm}' rides center, un-doubled — modern metal "
                        "rhythm guitar is DOUBLE-TRACKED hard L/R; a "
                        "mono wall reads as a demo")})
        fx = t.get("fx") or []
        has_hpf = any("hipass" in str(f.get("id", "")) or
                      (str(f.get("id")) == "fx_filter" and
                       False) for f in fx)
        if not has_hpf:
            advisories.append({
                "kind": "unfiltered_low_guitar", "track": nm,
                "why": (f"'{nm}' has no high-pass — drop-tuned guitars "
                        "flood 40-100Hz and smear the kick/bass pocket; "
                        "HPF 100-140Hz is the modern-metal floor")})
    # THE SCOOP TRAP: any bell cutting >=6dB inside the grind zone,
    # wherever it sits (track / bus / master)
    def scan(owner, fx):
        for i, f in enumerate(fx or []):
            if str(f.get("id")) != "fx_bell":
                continue
            p = f.get("params") or {}
            try:
                fr, gn = float(p.get("freq", 0)), float(p.get("gain", 0))
            except Exception:
                continue
            if gn <= -6.0 and 700.0 <= fr <= 1600.0:
                advisories.append({
                    "kind": "grind_scoop_trap", "owner": owner,
                    "fx_index": i, "freq": fr, "gain": gn,
                    "why": (f"{owner}: a {gn:.0f}dB cut at {fr:.0f}Hz "
                            "guts the GRIND (800Hz-1.5kHz) — the legacy "
                            "scooped-mids advice is the #1 modern-metal "
                            "anti-authenticity trap; the grind IS the "
                            "genre")})
    for t in (song or {}).get("tracks", []) or []:
        if isinstance(t, dict):
            scan(f"track '{t.get('name')}'", t.get("fx"))
    for b in (song or {}).get("buses", []) or []:
        if isinstance(b, dict):
            scan(f"bus '{b.get('name')}'", b.get("fx"))
    scan("master", (song or {}).get("master"))
    return {"court": "metal_mix", "ok": True, "advisories": advisories}


def heal_metal_mix(song, verdict=None, genre=""):
    v = verdict or court_metal_mix(song, genre)
    edits = []
    tracks = (song or {}).get("tracks", []) or []
    by_name = {t.get("name"): t for t in tracks if isinstance(t, dict)}
    # order law: filters + clamps FIRST, the twin LAST — a twin minted
    # before the HPF lands copies an unhealed chain (battery-caught)
    for adv in v.get("advisories", []):
        k = adv.get("kind")
        if k == "unfiltered_low_guitar":
            t = by_name.get(adv["track"])
            if t is None:
                continue
            fx = t.setdefault("fx", [])
            if any("hipass" in str(f.get("id", "")) for f in fx):
                continue
            fx.insert(0, {"id": "fx_hipass", "params": {"cutoff": 120.0}})
            edits.append({"kind": "guitar_hpf", "track": adv["track"],
                          "why": f"'{adv['track']}': fx_hipass 120Hz — "
                                 "the kick/bass pocket breathes"})
        elif k == "grind_scoop_trap":
            owner = adv.get("owner", "")
            coll = None
            if owner.startswith("track '"):
                coll = (by_name.get(owner[7:-1]) or {}).get("fx")
            elif owner.startswith("bus '"):
                for b in (song or {}).get("buses", []) or []:
                    if isinstance(b, dict) and \
                            f"bus '{b.get('name')}'" == owner:
                        coll = b.get("fx")
            elif owner == "master":
                coll = (song or {}).get("master")
            if not coll:
                continue
            i = int(adv.get("fx_index", -1))
            if 0 <= i < len(coll) and str(coll[i].get("id")) == "fx_bell":
                coll[i].setdefault("params", {})["gain"] = -3.0
                edits.append({"kind": "scoop_clamp", "owner": owner,
                              "why": (f"{owner}: the grind scoop clamped "
                                      "to -3dB — protect 800Hz-1.5kHz, "
                                      "shape it gently")})
    # the standard modern chain on every guitar lane, once
    for t in list(_guitar_lanes(song)):
        if t.get("metal_chain"):
            continue
        fx = t.setdefault("fx", [])
        fx.append({"id": "fx_bell", "params": {"freq": 950.0,
                                               "gain": -2.5, "q": 2.5}})
        fx.append({"id": "fx_bell", "params": {"freq": 6500.0,
                                               "gain": -3.0, "q": 2.0}})
        t["metal_chain"] = True
        edits.append({"kind": "metal_chain", "track": t.get("name"),
                      "why": (f"'{t.get('name')}': the pocket dip "
                              "(-2.5dB @950Hz, snare crack breathes) + "
                              "fizz notch (-3dB @6.5kHz)")})
    for adv in v.get("advisories", []):
        if adv.get("kind") != "undoubled_rhythm_guitar":
            continue
        t = by_name.get(adv["track"])
        if t is None or (adv["track"] + "R") in by_name:
            continue
        t["pan"] = -0.85
        twin = copy.deepcopy(t)
        twin["name"] = adv["track"] + "R"
        twin["pan"] = 0.85
        tracks.append(twin)
        by_name[twin["name"]] = twin
        edits.append({"kind": "double_track", "track": adv["track"],
                      "why": (f"'{adv['track']}' doubled -> "
                              f"'{twin['name']}', panned -0.85/+0.85 "
                              "— the wall becomes a WALL")})
    return edits


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="THE METAL MIX-HEAL (w58)")
    ap.add_argument("song")
    ap.add_argument("--genre", default="metal")
    ap.add_argument("--heal", action="store_true")
    a = ap.parse_args()
    song = json.load(open(a.song))
    v = court_metal_mix(song, a.genre)
    if a.heal:
        v["healed"] = heal_metal_mix(song, v, a.genre)
        json.dump(song, open(a.song, "w"), indent=1)
    print(json.dumps(v, indent=1))
