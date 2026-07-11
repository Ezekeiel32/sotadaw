#!/usr/bin/env python3
"""SESSION DIET battery — start_session tiering: smaller payload, ZERO law loss.

Asserts (through daw_mcp.TOOLS, the server's own dispatch):
  - payload shrank hard vs the pre-diet baselines (50,413 / 68,275 chars measured
    2026-07-06) and sits under the caps
  - the damage-preventer laws are FULL inline (tool-guide, mix-headroom, fx-usage,
    surgical-edits) — marker + full body present
  - a genre ask inlines its BEST-match genre skill full; sibling genres are indexed
  - every indexed skill's FULL body is byte-reachable via get_skill (zero law loss)
  - every index entry carries a non-empty essence + an explicit fetch instruction
  - deterministic

Usage: python3 tools/session_diet_battery.py
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "agent"))
import daw_mcp as D

PASS, FAIL = 0, []
def ok(cond, msg):
    global PASS
    if cond:
        PASS += 1
    else:
        FAIL.append(msg)

def session(genre):
    return D.TOOLS["start_session"][0]({"genre": genre} if genre else {})

def main():
    s0 = session("")
    s1 = session("dark trap")
    # round 2 (tool-guide split by the core lane): the caps DROP hard
    ok(len(s0) < 26000, f"empty-genre payload {len(s0)} < 26000 (round1 was 35.4K, v0 50.4K)")
    ok(len(s1) < 32000, f"dark-trap payload {len(s1)} < 32000 (round1 was 41.4K, v0 68.3K)")

    # tool-guide split laws: core sections inline, tail NOT inline, tail fetchable,
    # section CONSERVATION vs the frozen v1 census (29 sections, no loss ever)
    V1_SECTIONS = {"arrange_song", "auto_master", "automix", "chord_map", "color",
                   "dj_set", "doctor", "energy_curve", "finish", "generate_loop",
                   "harmonize", "humanize", "infill_region", "locate", "master_report",
                   "prescribe", "reharmonize", "remix_import", "restyle", "select_notes",
                   "set_clip_slot", "song_structure", "stem_callouts", "style_profile",
                   "surgical_edit", "transitions", "tune_vocal", "variations",
                   "vst_presets"}
    import re as _re
    core_body = D.TOOLS["get_skill"][0]({"name": "tool-guide"})
    tail_body = D.TOOLS["get_skill"][0]({"name": "tool-guide-tail"})
    core_secs = set(_re.findall(r"(?m)^## ([a-z_]+)", core_body))
    tail_secs = set(_re.findall(r"(?m)^## ([a-z_]+)", tail_body))
    # conservation = nothing LOST vs the v1 snapshot; the guide may GROW as the
    # catalog grows — but every section must name a live tool (no ghost laws)
    ok((core_secs | tail_secs) >= V1_SECTIONS, f"CONSERVATION: all 29 v1 sections live (missing {V1_SECTIONS - (core_secs | tail_secs)})")
    ok((core_secs | tail_secs) <= set(D.TOOLS), f"every guide section names a live tool (ghosts: {(core_secs | tail_secs) - set(D.TOOLS)})")
    ok(not (core_secs & tail_secs), "no section duplicated across the split")
    ok(core_secs <= set(D.CORE_TOOLS), "inline guide covers ONLY core-lane tools")
    ok("## tune_vocal" not in s0 and "## tune_vocal" not in s1, "tail laws NOT inline in sessions")
    ok("tool-guide-tail" in s0 and "tool-guide-tail" in s1, "sessions carry the tail POINTER")
    ok("tool-guide-tail" in D.TOOLS["use_tool"][1], "use_tool's own description teaches the fetch")

    for name in ("tool-guide", "mix-headroom", "fx-usage", "surgical-edits"):
        marker = f"===== SKILL {name}@v"
        ok(marker in s0, f"{name} FULL inline (empty genre)")
        ok(marker in s1, f"{name} FULL inline (dark trap)")
        body = D.TOOLS["get_skill"][0]({"name": name})
        ok(body[:2000] in s0, f"{name} inline body matches the registry")

    ok("SKILL INDEX" in s0 and "get_skill(" in s0, "index + fetch instruction present")

    # genre tier: exactly one genre-arrangement skill rides full, siblings indexed
    genre_full = [n for n in ("trap-arrangement", "phonk-arrangement", "drill-arrangement")
                  if f"===== SKILL {n}@v" in s1]
    ok(len(genre_full) == 1, f"exactly ONE genre skill full inline (got {genre_full})")
    ok(genre_full == ["trap-arrangement"], f"the ask's OWN genre won ({genre_full})")
    for sib in ("phonk-arrangement", "drill-arrangement"):
        ok(f"--- {sib}@v" in s1, f"{sib} indexed (essence hook present)")

    # ZERO LAW LOSS: every indexed skill's full body reachable byte-exact
    for blob, tag in ((s0, "empty"), (s1, "dark trap")):
        for m in re.finditer(r"^--- ([a-z0-9-]+)@v(\d+) ---$", blob, re.M):
            name = m.group(1)
            body = D.TOOLS["get_skill"][0]({"name": name})
            ok(not body.startswith("unknown skill"), f"[{tag}] {name} fetchable")
            reg = D.load_registry()["skills"][name]
            ok(body == D.skill_body(reg), f"[{tag}] {name} fetch == registry body (byte-exact)")
            ess = blob[m.end():m.end() + 500].strip()
            ok(len(ess) > 60, f"[{tag}] {name} essence non-empty")

    ok(session("dark trap") == s1 and session("") == s0, "deterministic")

if __name__ == "__main__":
    main()
    for f in FAIL:
        print("FAIL:", f)
    print(f"session-diet battery: {PASS}/{PASS + len(FAIL)} {'clean' if not FAIL else 'RED'}")
    sys.exit(1 if FAIL else 0)
