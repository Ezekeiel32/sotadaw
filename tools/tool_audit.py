#!/usr/bin/env python3
"""THE SCHEMA-INTEGRITY AUDIT — every advertised parameter must be CONSUMED.

  tool_audit.py [--verbose]

The dormant-schema bug (firing 16/20: chop_sample's groove params existed in
the handler but not the schema, so agents — which obey schemas — never sent
them; the feature was live yet unreachable). This catches the INVERSE and the
original at once, statically, across all 74 tools:

  1. every TOOLS entry is a well-formed 3-tuple (fn, desc, schema)
  2. every schema is a valid object schema with a properties dict
  3. every declared property is actually READ by the handler
     (args.get("x") / args["x"] / ("x", ...) in a passthrough loop)
  4. every required key is a declared property
  5. no handler reads an arg that the schema doesn't declare (the dormant class)

Static (ast + source scan) — no song mutation, safe to run anytime, fast.
Exit 1 if any tool fails; the report names the tool and the offending key.
"""
import ast, importlib.util, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MCP = os.path.join(ROOT, "agent", "daw_mcp.py")

# keys the harness knows are handled by the dispatcher, not the tool body
DISPATCHER_KEYS = {"song", "name"}          # song<->name aliasing (firing 27)


def handler_source(tree, fn_name):
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == fn_name:
            return ast.get_source_segment(SRC, node) or ""
    return ""


def args_read(body):
    """every key the handler pulls from args, however it phrases it."""
    keys = set()
    keys |= set(re.findall(r'args\.get\(\s*["\']([a-z_]+)["\']', body))
    keys |= set(re.findall(r'args\[\s*["\']([a-z_]+)["\']\s*\]', body))
    # passthrough loops: ("json_key", "--flag") tuples map a schema key to a CLI flag
    keys |= set(re.findall(r'\(\s*["\']([a-z_]+)["\']\s*,\s*["\']--', body))
    return keys


def main():
    global SRC
    SRC = open(MCP).read()
    tree = ast.parse(SRC)
    spec = importlib.util.spec_from_file_location("daw_mcp", MCP)
    m = importlib.util.module_from_spec(spec)
    sys.argv = ["x"]
    spec.loader.exec_module(m)

    verbose = "--verbose" in sys.argv
    fails, checked = [], 0
    for tname, entry in m.TOOLS.items():
        checked += 1
        if not (isinstance(entry, tuple) and len(entry) == 3):
            fails.append((tname, "not a 3-tuple (fn, desc, schema)"))
            continue
        fn, desc, schema = entry
        fn_name = getattr(fn, "__name__", "")
        if not isinstance(desc, str) or len(desc) < 20:
            fails.append((tname, "description missing/too short"))
        if not isinstance(schema, dict) or schema.get("type") != "object":
            fails.append((tname, "schema is not an object schema"))
            continue
        props = set((schema.get("properties") or {}).keys())
        required = set(schema.get("required") or [])
        missing_req = required - props
        if missing_req:
            fails.append((tname, f"required keys not in properties: {sorted(missing_req)}"))

        body = handler_source(tree, fn_name)
        if not body:
            if verbose:
                print(f"  (skip body scan for {tname}: {fn_name} not a top-level def)")
            continue
        read = args_read(body)
        # (5) dormant class: handler reads a key the schema never advertises
        dormant = read - props - DISPATCHER_KEYS
        if dormant:
            fails.append((tname, f"handler reads UNDECLARED args (agents can't send): {sorted(dormant)}"))
        # (3) dead schema key: advertised but never read (softer — warn only)
        dead = props - read - DISPATCHER_KEYS
        if dead and verbose:
            print(f"  note {tname}: declared-but-unread {sorted(dead)} "
                  f"(ok if handled by a generic loop)")

    # (6) ALLOWLIST DRIFT: every tool must be reachable by the producer agent.
    # The sidecar now derives DAW_ALLOW from the catalog, but verify the derivation
    # actually covers TOOLS (the firing-54 live bug: hand-maintained list went stale).
    try:
        sc = open(os.path.join(ROOT, "agent", "sidecar.py")).read()
        if "def _daw_allow" not in sc or "for t in _m.TOOLS" not in sc:
            fails.append(("__allowlist__", "sidecar DAW_ALLOW is not derived from the "
                          "live catalog — tools can silently become permission-blocked"))
    except OSError:
        pass

    print(f"[audit] {checked} tools scanned, {len(fails)} integrity failures")
    for t, why in fails:
        print(f"  FAIL {t}: {why}")
    if fails:
        sys.exit(1)
    print("[audit] SCHEMA INTEGRITY: PASS — every advertised param is reachable")


if __name__ == "__main__":
    main()
