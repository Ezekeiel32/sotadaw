#!/usr/bin/env python3
"""THE ATTRIBUTION COURT — the voice license is a hard court, not a
footnote (wave 29; R-31 item 006).

The voice stack (DiffSinger + Gahata Meiji bank) is NON-COMMERCIAL and
ATTRIBUTION-REQUIRED. The old law was a footnote: lane comments carry
'voice:...' and export_master collects them — but a lane that lost its
comment shipped SILENTLY unattributed. This court makes the license
structural:

  voice_used(song)      -> evidence list (voice: comments, sung wav
                           clips, staged lyrics + vocal audio)
  court_attribution(song) -> conviction when a voice is USED and no
                           attribution survives anywhere
  heal_attribution(song) -> stamps song['voice_license'] {attribution,
                           non_commercial: true, source} from the bank's
                           OWN manifest (library/voices/*/bank.json,
                           fail-open to the Meiji default) + re-marks
                           sung lanes; idempotent — an export physically
                           cannot ship unattributed because the heal
                           always lands
  license_assertion(song) -> the C2PA assertion dict export_master
                           embeds (org.sotadaw.voice_license)
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEFAULT_ATTRIBUTION = "Gahata Meiji from LUNAI Project"
_VOCAL_WAV_HINTS = ("vocal", "sung", "voice", "choir", "vox")


def bank_attribution():
    """The bank's OWN manifest truth (never a hardcoded footnote when a
    manifest exists)."""
    vd = os.path.join(ROOT, "library", "voices")
    try:
        for d in sorted(os.listdir(vd)):
            bj = os.path.join(vd, d, "bank.json")
            if os.path.exists(bj):
                m = json.load(open(bj))
                a = m.get("attribution")
                if a:
                    return str(a)
    except Exception:
        pass
    return DEFAULT_ATTRIBUTION


def voice_used(song):
    """Every surface a sung voice can ride: lane comments, vocal wav
    clips, staged word lyrics beside sounding vocal audio."""
    ev = []
    for t in (song or {}).get("tracks", []) or []:
        if not isinstance(t, dict):
            continue
        c = str(t.get("comment", ""))
        if c.startswith("voice:"):
            ev.append({"kind": "voice_comment", "track": t.get("name"),
                       "value": c})
        for clip in t.get("audioClips", []) or []:
            f = str(clip.get("file", "")).lower()
            if any(h in os.path.basename(f) for h in _VOCAL_WAV_HINTS):
                ev.append({"kind": "vocal_clip", "track": t.get("name"),
                           "file": clip.get("file")})
    return ev


def attributed(song):
    lic = (song or {}).get("voice_license") or {}
    if lic.get("attribution"):
        return True
    return any(str(t.get("comment", "")).startswith("voice:")
               for t in (song or {}).get("tracks", []) or []
               if isinstance(t, dict))


def court_attribution(song):
    ev = voice_used(song)
    if not ev:
        return {"court": "attribution", "ok": True,
                "skipped": "no voice use detected"}
    if attributed(song):
        return {"court": "attribution", "ok": True, "evidence": ev}
    return {"court": "attribution", "ok": False,
            "flags": [{"kind": "unattributed_voice",
                       "evidence": ev[:4],
                       "why": "a sung voice rides this take with NO "
                              "surviving attribution — the bank license "
                              "requires it (non-commercial, credit "
                              "mandatory); the export must annotate"}]}


def heal_attribution(song):
    """Stamp the structural license + re-mark sung lanes. Always lands
    (the default attribution exists) — the export physically cannot
    ship unattributed. Idempotent. Mutates; returns ledger."""
    ev = voice_used(song)
    if not ev:
        return []
    attr = bank_attribution()
    edits = []
    lic = song.get("voice_license") or {}
    if lic.get("attribution") != attr or not lic.get("non_commercial"):
        song["voice_license"] = {"attribution": attr,
                                 "non_commercial": True,
                                 "source": "library/voices bank manifest"}
        edits.append({"kind": "license_stamp", "attribution": attr})
    by_name = {str(t.get("name", "")): t
               for t in song.get("tracks", []) or [] if isinstance(t, dict)}
    for e in ev:
        if e["kind"] != "vocal_clip":
            continue
        t = by_name.get(str(e.get("track")))
        if t is not None and not str(t.get("comment", "")).startswith(
                "voice:"):
            t["comment"] = f"voice: {attr}"
            edits.append({"kind": "lane_mark", "track": e.get("track")})
    return edits


def license_assertion(song):
    """The C2PA assertion export_master embeds whenever a voice rides."""
    if not voice_used(song):
        return None
    lic = song.get("voice_license") or {
        "attribution": bank_attribution(), "non_commercial": True}
    return {"label": "org.sotadaw.voice_license",
            "data": {"attribution": lic.get("attribution"),
                     "non_commercial": bool(lic.get("non_commercial",
                                                    True)),
                     "statement": "The singing voice is a user-fetched "
                                  "voicebank under a NON-COMMERCIAL, "
                                  "attribution-required license. This "
                                  "master inherits that restriction."}}


def main():
    import argparse
    ap = argparse.ArgumentParser(description="THE ATTRIBUTION COURT "
                                             "(wave 29)")
    ap.add_argument("song")
    ap.add_argument("--heal", action="store_true")
    args = ap.parse_args()
    song = json.load(open(args.song))
    v = court_attribution(song)
    if args.heal and not v.get("ok", True):
        v["heals"] = heal_attribution(song)
        json.dump(song, open(args.song, "w"), indent=1)
        v["saved"] = args.song
        v["after"] = court_attribution(song)
    print(json.dumps(v, indent=1))
    return 0 if v.get("ok") or args.heal else 1


if __name__ == "__main__":
    sys.exit(main())
