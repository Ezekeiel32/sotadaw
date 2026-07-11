#!/usr/bin/env python3
"""SONG-NAME LINT (guardian leg) — the hyphen class can never come back.

Law: no tool may strip a song-name ARGUMENT with the legacy sanitize before
lookup; resolution goes through songname.resolve (tools) / resolve_song_name
(daw_mcp). Creation-lane names (--out, prefixes, kits, genres, presets) keep
sanitize — this lint targets exactly the INPUT-resolution patterns that made
imported hyphenated songs unreachable (2026-07-09/10: two $2 agent runs died,
then 19 more CLIs + _load_song found still broken).

Byte-exact grep law (wall_lint style) + ONE AST law for daw_mcp.py: a function
may not feed a legacy-sanitized variable into a SONGS-joined "<var>.json" path
(the t_render_song class, 2026-07-10: keyed args["name"] so every grep for
"song" keys missed it — the SHAPE is the law, not the key name).
"""
import ast
import glob
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The forbidden shapes: legacy sanitize applied to a song INPUT.
BAD = [
    're.sub(r"[^a-z0-9_]", "", a.song',
    're.sub(r"[^a-z0-9_]", "", str(args["song"])',
    're.sub(r"[^a-z0-9_]", "", str(args.get("song")',
    're.sub(r"[^a-z0-9_]", "", a.import_song',
    're.sub(r"[^a-z0-9_]", "", (a.out or name)',      # out-fallback re-strips resolved names
    're.sub(r"[^a-z0-9_]", "", str(args.get("out") or name)',
]


def _legacy_sanitize_call(node):
    """Call is re.sub(r'[^a-z0-9_]', ...) — the legacy strip."""
    return (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and node.func.attr == "sub" and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "re" and node.args
            and isinstance(node.args[0], ast.Constant)
            and node.args[0].value == "[^a-z0-9_]")


def ast_song_read_law(path):
    """daw_mcp shape law: sanitized var -> os.path.join(SONGS, f'{var}.json') is RED."""
    reds = []
    try:
        tree = ast.parse(io.open(path, encoding="utf-8").read())
    except (OSError, SyntaxError):
        return reds
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        dirty = set()
        for node in ast.walk(fn):
            if (isinstance(node, ast.Assign) and _legacy_sanitize_call(node.value)):
                dirty |= {t.id for t in node.targets if isinstance(t, ast.Name)}
        if not dirty:
            continue
        for node in ast.walk(fn):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "join"):
                names = [a.id for a in node.args if isinstance(a, ast.Name)]
                if "SONGS" not in names:
                    continue
                for a in node.args:
                    if isinstance(a, ast.JoinedStr):
                        uses = {v.value.id for v in a.values
                                if isinstance(v, ast.FormattedValue)
                                and isinstance(v.value, ast.Name)}
                        lit = "".join(v.value for v in a.values
                                      if isinstance(v, ast.Constant))
                        if (uses & dirty) and ".json" in lit:
                            reds.append(
                                f"{os.path.relpath(path)}:{node.lineno}: {fn.name}: "
                                f"legacy-sanitized var feeds a SONGS/*.json read — "
                                f"use resolve_song_name")
    return reds


def main():
    reds = []
    files = sorted(glob.glob(os.path.join(ROOT, "tools", "*.py"))
                   + glob.glob(os.path.join(ROOT, "agent", "*.py")))
    for path in files:
        if os.path.basename(path) in ("songname_lint.py",):
            continue
        try:
            src = io.open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for pat in BAD:
            if pat in src:
                line = next((i + 1 for i, l in enumerate(src.split("\n")) if pat in l), 0)
                reds.append(f"{os.path.relpath(path, ROOT)}:{line}: legacy sanitize on a "
                            f"song input — use songname.resolve / resolve_song_name")
    reds += ast_song_read_law(os.path.join(ROOT, "agent", "daw_mcp.py"))
    n_files = len(files)
    if reds:
        print(f"songname lint: RED ({len(reds)} site(s) across {n_files} files)")
        for r in reds:
            print("FAIL:", r)
        return 1
    print(f"songname lint: clean ({n_files} files swept, 0 legacy song-input sanitizes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
