"""THE ONE SONG-NAME LAW (tools twin of daw_mcp.resolve_song_name).

Imported songs legitimately carry hyphens (blpkosher-hourglassofficialvideo);
the legacy strip-everything sanitize ran BEFORE the file lookup and made them
unreachable by every CLI tool. RAW NAME FIRST: the raw (then lowercased)
candidate wins ONLY if its .json (or its _prop_ twin) exists on disk; else the
legacy sanitize keeps creation naming byte-stable. Path-safety: the raw lane
admits [A-Za-z0-9._-] only and never '..'.

Usage in a tool:  import songname; name = songname.resolve(a.song)
Out-names stay sanitized (creation law): sanitize ONLY the explicit --out.
tools/songname_lint.py is the guardian: a tool that argparses a song and
strips it raw goes red.
"""
import os
import re

SONGS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "songs")


def sanitize(raw):
    """Creation-lane naming (new files): the legacy byte-stable charset."""
    return re.sub(r"[^a-z0-9_]", "", str(raw or "").lower())


def resolve(raw, default=""):
    """Song id -> on-disk basename. Raw-first, exists-gated, sanitize fallback."""
    raw = str(raw if raw is not None else default).strip()
    for cand in (raw, raw.lower()):
        if cand and ".." not in cand and re.fullmatch(r"[A-Za-z0-9._\-]{1,160}", cand) \
                and (os.path.exists(os.path.join(SONGS, cand + ".json"))
                     or os.path.exists(os.path.join(SONGS, "_prop_" + cand + ".json"))):
            return cand
    return sanitize(raw)
