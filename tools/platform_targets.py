#!/usr/bin/env python3
"""PER-PLATFORM DELIVERY TARGETS (SPEC S11-V62) — the streaming loudness references
pros master to. Every major service normalizes playback to a fixed integrated-LUFS
reference (ITU-R BS.1770): a master HOTTER than the ref is turned DOWN at playback, so
loudness is a target to HIT under a true-peak ceiling, not a race.

Numbers are VERIFIED (primary sources: Spotify artist docs, Apple Digital Masters) —
see docs/research_mastering_sota.md §1. CD/club/vinyl are OPEN (unverified) and are
DELIBERATELY absent — do not fabricate their targets.

  platform_target(name) -> {platform, lufs, lufs_lo, lufs_hi, dbtp_max, gain_only, note} | None
  list_platforms() -> [names]
"""

WINDOW = 1.5   # +/- LU acceptance window around the platform reference (matches auto_master's
               # reference lane). Quieter than the ref is SAFE (turned up); hotter is the risk.

# integrated-LUFS reference, true-peak ceiling (dBTP), gain-only flag, note. dBTP default
# -1.0; -2.0 where the platform enforces it (Amazon). Spotify tightens to -2 dynamically
# when the master measures hotter than -14 LUFS (handled by master_report/auto_master).
PLATFORMS = {
    "spotify":   {"lufs": -14.0, "dbtp": -1.0, "gain_only": False,
                  "note": "default 'Normal'; if master >-14 LUFS, tighten dBTP to -2 (Spotify rule)"},
    "apple":     {"lufs": -16.0, "dbtp": -1.0, "gain_only": True,
                  "note": "Apple Music/Digital Masters: GAIN-ONLY, never limits; -1 dBTP so AAC has room"},
    "youtube":   {"lufs": -14.0, "dbtp": -1.0, "gain_only": False, "note": "some sources cite ~-13"},
    "tidal":     {"lufs": -14.0, "dbtp": -1.0, "gain_only": False, "note": ""},
    "amazon":    {"lufs": -14.0, "dbtp": -2.0, "gain_only": False, "note": "Amazon Music enforces -2 dBTP"},
    "deezer":    {"lufs": -15.0, "dbtp": -1.0, "gain_only": False, "note": ""},
    "tiktok":    {"lufs": -10.0, "dbtp": -1.0, "gain_only": False, "note": "social; runs hotter -9..-12"},
    "reels":     {"lufs": -10.0, "dbtp": -1.0, "gain_only": False, "note": "Instagram Reels; -9..-12"},
    # safe cross-platform default: hit -14 so no major service turns you down hard, -1 dBTP.
    "streaming": {"lufs": -14.0, "dbtp": -1.0, "gain_only": False,
                  "note": "generic streaming: -14 LUFS clears all major refs, -1 dBTP"},
}

ALIASES = {"apple music": "apple", "applemusic": "apple", "itunes": "apple", "am": "apple",
           "yt": "youtube", "youtube music": "youtube", "ytm": "youtube",
           "amazon music": "amazon", "amazonmusic": "amazon",
           "instagram": "reels", "ig": "reels", "insta": "reels", "tik tok": "tiktok",
           "stream": "streaming", "default": "streaming", "spotify premium": "spotify"}


def platform_target(name):
    if not name:
        return None
    key = ALIASES.get(str(name).strip().lower(), str(name).strip().lower())
    p = PLATFORMS.get(key)
    if not p:
        return None
    lufs = p["lufs"]
    return {"platform": key, "lufs": lufs,
            "lufs_lo": round(lufs - WINDOW, 1), "lufs_hi": round(lufs + WINDOW, 1),
            "dbtp_max": p["dbtp"], "gain_only": p["gain_only"], "note": p["note"]}


def list_platforms():
    return sorted(PLATFORMS)


if __name__ == "__main__":
    import json, sys
    if len(sys.argv) > 1:
        print(json.dumps(platform_target(sys.argv[1]), indent=1))
    else:
        print(json.dumps({k: platform_target(k) for k in list_platforms()}, indent=1))
