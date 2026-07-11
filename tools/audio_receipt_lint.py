#!/usr/bin/env python3
"""EB3 GUARD (wall_lint idiom) — the audio-receipt court must stay wired.

Asserts, so a refactor can't silently kill E3:
  1. sidecar.scope_check still attaches audio_verified behind SOTADAW_AUDIO_RECEIPTS
     (and only on CLEAN, non-full-write proposals — the court can't bless a badge).
  2. audio_verify still calls null_bench.compare_stem_dirs with a claim + the E3
     bar (-90).
  3. null_bench.compare_stem_dirs still exposes claim= and surgical_audio_proven.
  4. every prompt/verb-lane proposal emit still ships surgical= (the field the
     court rides on) — counted, must be >= 2 sites.
Exit 0 = law holds.
"""
import ast
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ok = True


def say(name, cond, detail=""):
    global ok
    ok &= bool(cond)
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


sc = open(os.path.join(ROOT, "agent", "sidecar.py")).read()
say("flag string present", "SOTADAW_AUDIO_RECEIPTS" in sc)
say("court gated on clean & not full_write",
    re.search(r'AUDIO_RECEIPTS[^\n]*clean[\s\S]{0,160}full_write', sc) is not None)
say("audio_verified attached", '"audio_verified"' in sc)
say("E3 bar -90 in audio_verify", re.search(r"bar=-90", sc) is not None)

nb = open(os.path.join(ROOT, "tools", "null_bench.py")).read()
tree = ast.parse(nb)
fn = next((n for n in ast.walk(tree)
           if isinstance(n, ast.FunctionDef) and n.name == "compare_stem_dirs"), None)
say("null_bench.compare_stem_dirs exists", fn is not None)
say("...with claim param", fn is not None and any(a.arg == "claim" for a in fn.args.args))
say("...emits surgical_audio_proven", "surgical_audio_proven" in nb)

emits = len(re.findall(r'emit\([^)]*"proposal"[^)]*surgical=', sc))
say("proposal emits carrying surgical= (>=2 lanes)", emits >= 2, f"{emits} sites")

print(("AUDIO-RECEIPT LAW HOLDS" if ok else "AUDIO-RECEIPT LAW BROKEN"))
sys.exit(0 if ok else 1)
