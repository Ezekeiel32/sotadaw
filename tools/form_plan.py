#!/usr/bin/env python3
"""THE PLANNER — text becomes typed attributes + a form plan BEFORE any
note lands (wave 33; R-29 items 042/105, MuseCoco pattern).

r-29: replace the text->music jump with text -> TYPED ATTRIBUTES ->
plan -> notes. The composer receives (a) the ask's hard targets and
semantic goals as a typed line (ONE RESOLVER: hard targets are read
back out of court_instruction itself — the same court that will verdict
the take; semantics from semantic_map), and (b) a FORM PLAN: the
genre-family's canonical section layout (r-14 templates) scaled to the
asked length on the 4-bar grid. The plan is the CONTRACT — the
instruction court verdicts the finished take against the same parse.

GATES (the block must never spam): fresh GENERATIVE asks only (make/
compose/write/arrange a new piece), never tweaks, never revises, never
songs that already declared sections (respect standing form).
Session-diet law: the block stays under 900 chars.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# r-14 canonical forms (bars at reference scale; scaled to the ask)
FORM_TEMPLATES = {
    "pop": (("intro", 4), ("verse", 8), ("prechorus", 4), ("chorus", 8),
            ("verse_2", 8), ("prechorus_2", 4), ("chorus_2", 8),
            ("bridge", 8), ("chorus_3", 8), ("outro", 4)),
    "trap": (("intro", 4), ("hook", 8), ("verse", 12), ("hook_2", 8),
             ("verse_2", 12), ("hook_3", 8), ("outro", 4)),
    "edm": (("intro", 16), ("breakdown", 8), ("build", 8), ("drop", 16),
            ("break", 16), ("build_2", 8), ("drop_2", 16), ("outro", 16)),
    "journey": (("intro", 16), ("part", 16), ("part_2", 16), ("lift", 16),
                ("part_3", 16), ("outro", 16)),
    "live": (("intro", 4), ("verse", 16), ("chorus", 8), ("verse_2", 16),
             ("chorus_2", 8), ("bridge", 8), ("chorus_3", 8),
             ("outro", 4)),
    # r-26: 3 acts, ADDITIVE layer gates, a STOPDOWN (near-silence)
    # before the climax — negative space is structural
    "cinematic": (("intro", 8), ("build", 16), ("build_2", 16),
                  ("stopdown", 4), ("climax", 16), ("outro", 8)),
}
_FAMILY = (
    ("cinematic", ("cinematic", "orchestral", "epic", "trailer",
                   "soundtrack", "score", "filmi")),
    ("journey", ("ambient", "psy", "goa", "drone", "meditation", "chill",
                 "downtempo", "berlin", "dub_techno")),
    ("edm", ("edm", "house", "techno", "trance", "dnb", "dubstep",
             "garage", "hardstyle", "electro", "big_room", "gabber")),
    ("trap", ("trap", "drill", "phonk", "grime", "rap", "hiphop",
              "hip_hop", "boombap", "memphis", "reggaeton",
              "dancehall")),
    ("live", ("rock", "metal", "punk", "folk", "country", "jazz", "blues",
              "soul", "funk", "gospel", "indie")),
)
_GENERATIVE = re.compile(
    r"\b(make|compose|write|create|arrange|produce|build)\b.{0,40}"
    r"\b(song|track|beat|tune|piece|loop|banger|anthem|instrumental)\b"
    r"|\bfull[- ]length\b|\bwhole song\b|\bfull song\b", re.I | re.S)


def family_for(genre_or_ask):
    g = str(genre_or_ask or "").lower()
    for fam, keys in _FAMILY:
        if any(k in g for k in keys):
            return fam
    return "pop"


def wants_plan(ask, song=None, revise=False):
    """The gate: fresh generative asks with no standing form."""
    if revise or not _GENERATIVE.search(str(ask or "")):
        return False
    if song and (song.get("sections") or []):
        return False
    return True


def hard_targets(ask, genre=""):
    """ONE RESOLVER: read the wants back out of the instruction court
    itself (the same parse that will verdict the take)."""
    out = {}
    try:
        import music_court
        iv = music_court.court_instruction(ask, {"tracks": []}, None, genre)
        for c in iv.get("contracts", []):
            k = str(c.get("kind", ""))
            if k in ("bpm", "key", "bars", "duration"):
                out[k] = c.get("want")
    except Exception:
        pass
    return out


def scaled_form(family, total_bars):
    """The family template scaled to total_bars on the 4-bar grid."""
    tpl = FORM_TEMPLATES[family]
    ref = sum(b for _, b in tpl)
    out, acc = [], 0
    for i, (name, b) in enumerate(tpl):
        if i == len(tpl) - 1:
            bars = max(total_bars - acc, 4)
        else:
            bars = max(4, int(round(b * total_bars / ref / 4.0)) * 4)
            bars = min(bars, max(total_bars - acc - 4 * (len(tpl) - i - 1),
                                 4))
        out.append((name, bars))
        acc += bars
        if acc >= total_bars and i < len(tpl) - 1:
            break
    return out


def _bars_for(ask_targets, bpm, genre):
    if "bars" in ask_targets:
        try:
            return max(int(ask_targets["bars"]), 16)
        except Exception:
            pass
    dur = str(ask_targets.get("duration", ""))
    m = re.match(r"(\d+)", dur)
    if m and "full" not in dur:
        secs = int(m.group(1))
        return max(int(round(secs * bpm / 60.0 / 4.0 / 4.0)) * 4, 16)
    if "full" in dur:
        return 96
    fam = family_for(genre)
    return {"pop": 64, "trap": 56, "edm": 104, "journey": 96,
            "live": 72, "cinematic": 68}[fam]


def plan_block(ask, genre="", song=None, revise=False):
    """The typed block (<=900 chars) or '' when the gate holds it."""
    if not wants_plan(ask, song, revise):
        return ""
    targets = hard_targets(ask, genre)
    g = genre or ""
    fam = family_for(g + " " + str(ask or ""))
    bpm = 120.0
    if "bpm" in targets:
        try:
            bpm = float(targets["bpm"])
        except Exception:
            pass
    total = _bars_for(targets, bpm, g + " " + str(ask or ""))
    form = scaled_form(fam, total)
    goals = []
    try:
        import semantic_map
        c = semantic_map.contract(ask, g)
        goals = [f"{x['term']}@{x['scope']}" for x in c["semantic_goals"]][:5]
    except Exception:
        pass
    lines = ["", "THE PLAN (typed from your ask — the instruction court "
                 "verdicts the take against THIS):"]
    tline = "  targets: " + ", ".join(
        f"{k}={v}" for k, v in targets.items()) if targets else ""
    if tline.strip():
        lines.append(tline)
    if goals:
        lines.append("  semantic: " + ", ".join(goals))
    try:                          # wave 47: the emotion prior (item 086)
        import emotion_prior
        ep = emotion_prior.emotion_prior(ask)
        if ep:
            lines.append(ep["plan_line"])
    except Exception:
        pass
    lines.append(f"  form ({fam}, {sum(b for _, b in form)} bars — write "
                 "sections[] to MATCH): "
                 + " | ".join(f"{n} {b}" for n, b in form))
    if fam == "cinematic":
        lines.append("  law: ADDITIVE layers act by act (intro <=2 "
                     "lanes; each act adds in its OWN register); the "
                     "STOPDOWN drops to near-silence before the climax.")
    else:
        lines.append("  law: hit the targets EXACTLY; sections quantize "
                     "to the 4-bar grid; the hook answers early.")
    block = "\n".join(lines) + "\n"
    return block if len(block) <= 900 else block[:897] + "…\n"


if __name__ == "__main__":
    import sys as _s
    print(plan_block(" ".join(_s.argv[1:]) or
                     "make a dark trap song at 142bpm in F minor",
                     ""))
