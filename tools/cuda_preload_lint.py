#!/usr/bin/env python3
"""THE CUDA PRELOAD LINT — machine law for the dead-rail class of 2026-07-12.

basic-pitch picks its inference backend by TRYING each one and catching ImportError:

    try:    import onnxruntime; ONNX_PRESENT = True
    except ImportError: ONNX_PRESENT = False     # <-- swallows EVERYTHING

The onnxruntime that serves it here is a CUDA build (onnxruntime-gpu shadows the cpu
wheel in ~/.local) whose libcudart.so.13 ships inside the nvidia wheels — NOT on the
dynamic loader path. Imported bare it raises ImportError; the probe reads that as
"onnxruntime is not installed"; all four backends go False; _default_model_type never
binds; the import dies on `NameError: _default_model_type` that names nothing you can
search for. A missing CUDA lib wearing a "no backend" mask — it killed audio_to_midi,
hum and import_song_audio's MIDI sketches, silently, for as long as nobody ran the
opt-in --full suite leg.

torch preloads libcudart (which is exactly why sing.py's CUDA voice never broke and
this rail never worked). THE LAW: torch imports BEFORE basic_pitch. This lint is fast
(AST only — no models, no GPU), so it can hold the line in the DEFAULT suite where the
real basic-pitch leg cannot.

    python3 tools/cuda_preload_lint.py             # lint the tree (rc 0 = green)
    python3 tools/cuda_preload_lint.py --selftest  # prove it catches a planted violation
"""
import ast
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCAN = ("tools", "agent")


def _imports(tree):
    """[(lineno, root_module, enclosing_function_or_None)] for every import."""
    out = []

    class V(ast.NodeVisitor):
        def __init__(self):
            self.fn = None

        def visit_FunctionDef(self, node):
            prev, self.fn = self.fn, node
            self.generic_visit(node)
            self.fn = prev

        visit_AsyncFunctionDef = visit_FunctionDef

        def visit_Import(self, node):
            for a in node.names:
                out.append((node.lineno, a.name.split(".")[0], self.fn))

        def visit_ImportFrom(self, node):
            if not node.level:          # absolute imports only
                out.append((node.lineno, (node.module or "").split(".")[0], self.fn))

    V().visit(tree)
    return out


def violations(path):
    """Lines where basic_pitch is imported with no torch loaded before it."""
    try:
        tree = ast.parse(open(path, encoding="utf-8").read())
    except (SyntaxError, UnicodeDecodeError):
        return []
    imps = _imports(path and tree)
    bp = [(ln, fn) for ln, mod, fn in imps if mod == "basic_pitch"]
    if not bp:
        return []
    torch = [(ln, fn) for ln, mod, fn in imps if mod == "torch"]
    bad = []
    for ln, fn in bp:
        # a torch import counts if it runs BEFORE this one: module-level (fn is None)
        # always does; otherwise it must sit in the same function body, above it.
        if not any(t_ln < ln and (t_fn is None or t_fn is fn) for t_ln, t_fn in torch):
            bad.append(ln)
    return bad


def scan():
    bad = {}
    for top in SCAN:
        for dirpath, _dirs, files in os.walk(os.path.join(ROOT, top)):
            for f in files:
                if not f.endswith(".py"):
                    continue
                p = os.path.join(dirpath, f)
                v = violations(p)
                if v:
                    bad[os.path.relpath(p, ROOT)] = v
    return bad


def selftest():
    import tempfile
    ok = True
    cases = [
        ("bare basic_pitch (the 07-12 bug)",
         "def t():\n    from basic_pitch.inference import predict\n", True),
        ("torch preloaded in-function (the law)",
         "def t():\n    import torch\n    from basic_pitch.inference import predict\n", False),
        ("torch preloaded module-level",
         "import torch\ndef t():\n    from basic_pitch.inference import predict\n", False),
        ("torch AFTER basic_pitch (too late)",
         "def t():\n    from basic_pitch.inference import predict\n    import torch\n", True),
        ("torch in a DIFFERENT function (never runs)",
         "def a():\n    import torch\ndef t():\n    from basic_pitch.inference import predict\n", True),
        ("no basic_pitch at all",
         "import os\n", False),
    ]
    for name, src, should_flag in cases:
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as fh:
            fh.write(src)
            p = fh.name
        flagged = bool(violations(p))
        os.unlink(p)
        good = flagged == should_flag
        ok &= good
        print(f"  {'ok  ' if good else 'FAIL'} {name}: "
              f"{'flagged' if flagged else 'clean'} (want {'flagged' if should_flag else 'clean'})")
    print("selftest:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    bad = scan()
    if bad:
        print("CUDA PRELOAD LINT: RED — basic_pitch imported with no torch before it")
        for f, lines in sorted(bad.items()):
            print(f"  {f}: line(s) {', '.join(map(str, lines))}")
        print("\n  fix: `import torch` above the basic_pitch import (it preloads libcudart;")
        print("       without it the backend probe silently reports 'no backend').")
        sys.exit(1)
    print("CUDA PRELOAD LINT: green (every basic_pitch import has torch before it)")
    sys.exit(0)
