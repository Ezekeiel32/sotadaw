#!/usr/bin/env python3
"""RECEIPT LINT — every song-mutating MCP tool must file an edit receipt.

The scope law can only defend takes if mutations are receipted. This walks
agent/daw_mcp.py's AST: any `def t_*` that PERSISTS a song (save_song / a
json.dump whose target lives under songs/) must call `_rc(` (coarse receipt)
or go through agent/surgical.py (which files exact receipts itself).

Real-use origin: a take changed 3,884 notes with ZERO receipts filed
(2026-07-06 10:25, untitled_1) — the scope law flagged it but couldn't say WHO.
This lint makes receipt-free mutators impossible to reintroduce.

Usage: python3 tools/receipt_lint.py
"""
import ast, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "agent", "daw_mcp.py")

# tools that mutate NON-SONG state (presets, engine, exports) or whose writes
# are new standalone files a later import/receipt covers
EXEMPT = {
    "t_write_instrument", "t_rebuild_engine", "t_render_song", "t_export_midi",
    "t_export_als", "t_export_dawproject", "t_save_preset", "t_export_master",
    "t_extract_groove",   # writes library/grooves.json, not a song
}

def calls_in(node):
    names = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Call):
            f = n.func
            if isinstance(f, ast.Name):
                names.add(f.id)
            elif isinstance(f, ast.Attribute):
                names.add(f.attr)
                if isinstance(f.value, ast.Name):
                    names.add(f"{f.value.id}.{f.attr}")
    return names

def main():
    tree = ast.parse(open(SRC).read())
    bad = []
    n_mutators = 0
    for node in tree.body:
        if not (isinstance(node, ast.FunctionDef) and node.name.startswith("t_")):
            continue
        calls = calls_in(node)
        persists = ("save_song" in calls or "dump" in calls
                    or "json.dump" in calls or "_awrite" in calls)
        if not persists or node.name in EXEMPT:
            continue
        n_mutators += 1
        receipted = ("_rc" in calls
                     or any(c.startswith("surgical.") for c in calls)
                     or "file_receipt" in calls or "coarse_receipt" in calls)
        if not receipted:
            bad.append((node.lineno, node.name))
    for ln, name in bad:
        print(f"RECEIPT-FREE MUTATOR at daw_mcp.py:{ln}: {name}")
    print(f"receipt lint: {n_mutators - len(bad)}/{n_mutators} mutating tools receipted "
          f"{'— LAW HOLDS' if not bad else '— LAW BROKEN'}")
    sys.exit(1 if bad else 0)


def check_field_spellings():
    """THE SPELLING LAW (W115 generalized, 2026-07-11): a receipt field's
    SPELLING must be one the scope judges can match — the class bit three
    times (literal "master" vs "meta:master"; bare "masterGainDb"; bare
    "track:{nm}" vs "track:{nm}:{k}"). The judges now accept bare twins;
    this guards the grammar itself so a typo'd or novel spelling turns the
    suite red instead of false-flagging a live take.
      allowed: "*" | meta:<key> | <known bare key> | track:<...>[:<prop>]
               | bus:<name> | buses | master | audioClips | automation
    """
    bare_ok = {"*", "master", "masterGainDb", "buses", "audioClips",
               "automation", "bpm", "key", "lengthBars", "swing", "tempoMap",
               "sections", "scenes", "lyrics", "chords"}
    bad = []
    for fname in ("daw_mcp.py", "sidecar.py"):
        tree = ast.parse(open(os.path.join(ROOT, "agent", fname)).read())
        for node in ast.walk(tree):
            if not (isinstance(node, ast.keyword) and node.arg == "fields"):
                continue
            if not isinstance(node.value, (ast.List, ast.ListComp)):
                continue
            elts = node.value.elts if isinstance(node.value, ast.List) else [node.value.elt]
            for e in elts:
                if isinstance(e, ast.Constant) and isinstance(e.value, str):
                    s = e.value
                elif isinstance(e, ast.JoinedStr):  # f-string: check constant prefix
                    s = e.values[0].value if (e.values and isinstance(e.values[0], ast.Constant)) else ""
                else:
                    continue   # conditional/computed — runtime shapes, skip
                ok = (s in bare_ok or s.startswith(("meta:", "track:", "bus:"))
                      or s == "")
                if not ok:
                    bad.append(f"{fname}:{e.lineno}: unmatched field spelling {s!r}")
    if bad:
        raise AssertionError("; ".join(bad[:4]))
    return "field spellings all judge-matchable"


def check_no_bare_mutating_lambdas():
    """W115: hum_topline/sing_lyrics shipped as BARE LAMBDAS running sing.py
    (a song mutator) with no receipt — the AST scan only audited def-style
    tools. Tripwire: any TOOLS lambda whose body invokes sing.py/subprocess
    against a song must route through a _rc-bearing helper."""
    import re
    src = open(os.path.join(ROOT, "agent", "daw_mcp.py")).read()
    for m in re.finditer(r'"(\w+)":\s*\(lambda a:([^,]+(?:\([^)]*\))?[^,]*),', src):
        name, body = m.group(1), m.group(2)
        if "sing.py" in body and "_sing_receipted" not in body:
            raise AssertionError(f"{name}: bare lambda mutates via sing.py without a receipt helper")
    return "no bare mutating sing lambdas"

print(" ", check_no_bare_mutating_lambdas())
print(" ", check_field_spellings())

if __name__ == "__main__":
    main()
