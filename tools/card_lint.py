#!/usr/bin/env python3
"""CARD LINT — the "every single action streams as a DAW component" MACHINE LAW
(guardian leg; wall_lint/receipt_lint's sibling).

Chezy's law: EVERY action the agent takes must land as a consistent DAW UI
component, immediately. Three layers hold it, and this lint audits all three
by PARSING THE SOURCES (AST) — the law can't rot silently:

  L1 TRANSCRIPT: every receipt-filing (mutating) tool must have a SPECIFIC
     family in sidecar's ACTION_FAMILY — the fallback "tool" chip is legal
     but anonymous, and anonymous mutations are the law eroding.
  L2 RAILS/STORY: every field pattern a receipt can carry must route
     somewhere in ui_main's routeReceipt (fx rail / master rail) OR belong
     to a DOCUMENTED story (lanes ghost-diff, live grid, meta surface).
     A pattern that routes NOWHERE with no story = an invisible action.
  L3 SCHEMA: track_wild must be a LIST (or None). routeReceipt reads it via
     getArray() — a bare string silently reads as "not wild" in the UI.

Run: python3 tools/card_lint.py   (exit 0 green / 1 red)
"""
import ast
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The documented non-rail stories (each entry is a REASON, not an excuse):
STORY = {
    "*":                "whole-song proposal -> ghost diff on every lane",
    "track:<T>":        "wild/notes rewrite -> lane ghost story (MidiCards)",
    "track:<T>:slots":  "launcher cells -> the live grid story",
    "track:<T>:locked": "lane lock chip on the header",
    "meta:scenes":      "live grid scene row",
    "meta:lyrics":      "lyrics surface + vocal transcript card",
    "meta:sections":    "arrange ruler sections redraw",
    "meta:lengthBars":  "arrange ruler length + lanes extend",
    "meta:chords":      "chord field (roll header + retune grid)",
    "meta:<dyn>":       "transport/header meta truth (bpm/swing/key...)",
    "audioClips":       "lane clip visual (tune_vocal swap)",
}


def fields_patterns(node):
    """An _rc fields= AST node -> set of pattern strings.
    Formatted pieces become <T>/<dyn>; IfExp takes both branches; a ListComp
    over a literal tuple expands its constants."""
    out = set()

    def fstr(j):
        bits = []
        for v in j.values:
            if isinstance(v, ast.Constant):
                bits.append(str(v.value))
            else:
                bits.append("<T>")
        return "".join(bits)

    def one(n):
        if n is None:
            return
        if isinstance(n, ast.Constant):
            out.add(str(n.value))
        elif isinstance(n, ast.JoinedStr):
            out.add(fstr(n))
        elif isinstance(n, ast.IfExp):
            one(n.body), one(n.orelse)
        elif isinstance(n, (ast.List, ast.Tuple)):
            for e in n.elts:
                one(e)
        elif isinstance(n, ast.ListComp):
            gen = n.generators[0]
            if isinstance(gen.iter, (ast.Tuple, ast.List)) and all(
                    isinstance(e, ast.Constant) for e in gen.iter.elts):
                # e.g. [f"track:{t}:{k}" for k in ("gainDb","pan",...)]
                for e in gen.iter.elts:
                    if isinstance(n.elt, ast.JoinedStr):
                        bits = []
                        for v in n.elt.values:
                            if isinstance(v, ast.Constant):
                                bits.append(str(v.value))
                            elif (isinstance(v, ast.FormattedValue)
                                  and isinstance(v.value, ast.Name)
                                  and v.value.id == gen.target.id):
                                bits.append(str(e.value))
                            else:
                                bits.append("<T>")
                        out.add("".join(bits))
                    else:
                        one(n.elt)
            else:                    # dynamic comprehension: meta:<dyn> etc
                if isinstance(n.elt, ast.JoinedStr):
                    out.add(fstr(n.elt).replace("<T>", "<dyn>"))
                else:
                    out.add("<dyn>")
        else:
            out.add("<dyn>")
    one(node)
    # normalize track names to <T> so patterns collapse
    return {re.sub(r"^track:[^:<][^:]*", "track:<T>",
                   p.replace("track:<T>", "track:<T>")) for p in out}


def route(pattern, tool, has_wild):
    """Mirror ui_main.cpp routeReceipt() over one field pattern."""
    p = pattern
    if p == "buses":
        return "master-rail:buses"
    if p in ("master", "masterGainDb") or p.startswith("meta:master"):
        return "master-rail:master"
    if p in ("meta:automation", "automation"):
        return "master-rail:motion"
    if p.startswith("track:"):
        if p.endswith(":fx"):
            return "fx-rail:fx"
        if p.endswith(":source"):
            return "fx-rail:sound"
        if p.endswith(":sends"):
            return "fx-rail:sends"
        if p.endswith(":automation"):
            return "fx-rail:motion"
        if p.endswith(":gainDb") or p.endswith(":pan"):
            return "fx-rail:mix"
        if p.endswith(":slots"):
            return "story"
        if p.endswith(":muted"):
            return "fx-rail:mix"          # falls to the non-wild mix default
        if tool in ("add_track", "use_preset"):
            return "fx-rail:sound"
        if has_wild:
            return "story" if "track:<T>" in STORY else "NOTHING"
        return "fx-rail:mix"
    if p in STORY:
        return "story"
    if p.startswith("meta:"):
        return "story" if "meta:<dyn>" in STORY else "NOTHING"
    return "NOTHING"


def main():
    daw = open(os.path.join(ROOT, "agent", "daw_mcp.py")).read()
    side = open(os.path.join(ROOT, "agent", "sidecar.py")).read()
    ui = open(os.path.join(ROOT, "app", "ui_main.cpp")).read()

    # sanity: the C++ routing rules this lint mirrors must still exist
    for probe in ('f == "buses"', 'f.endsWith (":fx")', 'origin", "").toString() == "hand"'):
        if probe not in ui:
            print(f"LINT STALE: routeReceipt probe missing in ui_main.cpp: {probe}")
            return 1

    fam = set(re.findall(r'"([a-z0-9_]+)":\s*"[a-z]+"',
                         side[side.index("ACTION_FAMILY"):side.index("def _action_v")]))

    tree = ast.parse(daw)
    findings, receipts = [], []
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "_rc"):
            tool = None
            if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant):
                tool = node.args[1].value
            kw = {k.arg: k.value for k in node.keywords}
            receipts.append((tool, node.lineno, kw))

    tools_seen = set()
    for tool, ln, kw in receipts:
        if not tool:
            findings.append(f"L0 daw_mcp:{ln}: _rc with non-literal tool name")
            continue
        tools_seen.add(tool)
        # L3: track_wild must be list-shaped
        tw = kw.get("track_wild")
        if tw is not None and isinstance(tw, (ast.Constant, ast.JoinedStr)):
            findings.append(f"L3 daw_mcp:{ln}: {tool} track_wild is a bare "
                            f"string — routeReceipt getArray() reads it as NOT wild")
        has_wild = tw is not None
        # L2: every field pattern routes somewhere
        pats = fields_patterns(kw.get("fields")) if "fields" in kw else set()
        if not pats and not has_wild:
            findings.append(f"L2 daw_mcp:{ln}: {tool} files a receipt with no "
                            f"fields and no track_wild — invisible everywhere")
        for p in sorted(pats):
            if route(p, tool, has_wild) == "NOTHING":
                findings.append(f"L2 daw_mcp:{ln}: {tool} field '{p}' routes "
                                f"NOWHERE (no rail, no documented story)")

    # L1: every mutating tool has a specific transcript family
    for tool in sorted(tools_seen):
        if tool not in fam:
            findings.append(f"L1 sidecar ACTION_FAMILY: mutating tool '{tool}' "
                            f"has no family — renders an anonymous 'tool' chip")

    n_pat = sum(len(fields_patterns(kw.get("fields"))) for _, _, kw in receipts
                if "fields" in kw)
    if findings:
        print("\n".join(findings))
        print(f"card lint: {len(findings)} gaps across {len(receipts)} receipts "
              f"/ {n_pat} field patterns — THE LAW LEAKS")
        return 1
    print(f"card lint: {len(receipts)} receipts / {n_pat} field patterns / "
          f"{len(tools_seen)} mutating tools all render — LAW HOLDS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
