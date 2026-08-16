#!/usr/bin/env python3
"""commit_split_battery.py — proof for tools/commit_split.py (suite leg).

A synthetic two-author repo: ALPHA and BRAVO hunks interleaved in ONE
working tree (exactly the parallel-session shape that swept hunks on
2026-07-16 and twice on 2026-07-31). Proves:
  - marker staging stages ONLY the marked hunks
  - THE UNION PROOF: staged +/- lines ∪ remaining +/- lines == the full
    pre-split diff (no hunk lost, none duplicated)
  - the commit carries ALPHA only; BRAVO survives in the working tree
  - --invert cedes marked work; check maps hunks; clean/no-match paths
  - binary refusal (structural changes never ride a splitter)
Pure: tempdir repo, no network, <2s.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOL = os.path.join(ROOT, "tools", "commit_split.py")
PASS = FAIL = 0


def check(name, ok, detail=""):
    global PASS, FAIL
    PASS += ok
    FAIL += not ok
    print(f"  {'OK  ' if ok else 'FAIL'} {name}" + ("" if ok else f"  <- {detail}"))


def g(repo, *args, inp=None, ok=True):
    r = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, input=inp)
    if ok and r.returncode != 0:
        raise SystemExit(f"battery rig broke: git {' '.join(args)}: {r.stderr}")
    return r


def tool(repo, *args):
    return subprocess.run([sys.executable, TOOL, *args], cwd=repo,
                          capture_output=True, text=True)


def pm_lines(diff_text):
    """Multiset of the +/- content lines of a diff (headers excluded)."""
    out = []
    for ln in diff_text.splitlines():
        if ln.startswith(("+++", "---")):
            continue
        if ln[:1] in "+-":
            out.append(ln)
    return sorted(out)


def main():
    tmp = tempfile.mkdtemp(prefix="commit_split_bat_")
    try:
        repo = os.path.join(tmp, "repo")
        os.makedirs(repo)
        g(repo, "init", "-q")
        g(repo, "config", "user.email", "bat@sota.daw")
        g(repo, "config", "user.name", "battery")
        f = os.path.join(repo, "f.txt")
        with open(f, "w") as fh:
            fh.write("".join(f"line {i}\n" for i in range(1, 31)))
        g(repo, "add", "f.txt")
        g(repo, "commit", "-qm", "seed")

        # two authors interleave in ONE working tree
        lines = open(f).read().splitlines()
        lines[4] += "  # [ALPHA] threshold fix"
        lines[9] += "  # [BRAVO] roll resize"
        lines[27] += "  # [BRAVO] chase gate"
        lines.insert(20, "new_feature()  # [ALPHA] the added block")
        with open(f, "w") as fh:
            fh.write("\n".join(lines) + "\n")

        full = g(repo, "diff", "-U0", "HEAD", "--", "f.txt").stdout
        check("rig: 4 interleaved hunks", full.count("@@") // 1 >= 4 or full.count("@@ ") >= 4,
              full)

        # --- check verb maps ownership without touching the index
        r = tool(repo, "check", "f.txt", "--marker", "[ALPHA]", "--marker", "[BRAVO]")
        check("check: exits 0", r.returncode == 0, r.stderr)
        check("check: maps ALPHA + BRAVO hunks",
              "[ALPHA]" in r.stdout and "[BRAVO]" in r.stdout, r.stdout)
        check("check: index untouched",
              g(repo, "diff", "--cached").stdout == "", "index dirtied by check")

        # --- stage ALPHA only
        r = tool(repo, "stage", "f.txt", "--marker", "[ALPHA]")
        check("stage: exits 0", r.returncode == 0, r.stdout + r.stderr)
        cached = g(repo, "diff", "--cached", "-U0").stdout
        working = g(repo, "diff", "-U0").stdout
        check("staged = ALPHA only",
              "[ALPHA]" in cached and "[BRAVO]" not in cached, cached)
        check("working remainder = BRAVO only",
              "[BRAVO]" in working and "[ALPHA]" not in working, working)
        check("UNION PROOF: staged ∪ remaining == full diff",
              sorted(pm_lines(cached) + pm_lines(working)) == pm_lines(full),
              "hunks lost or duplicated")

        # --- the commit carries ALPHA; BRAVO survives the commit
        g(repo, "commit", "-qm", "alpha wave")
        head = g(repo, "show", "HEAD:f.txt").stdout
        check("commit carries ALPHA", "[ALPHA] threshold fix" in head
              and "[ALPHA] the added block" in head, head)
        check("commit excludes BRAVO", "[BRAVO]" not in head, head)
        wt = open(f).read()
        check("BRAVO intact in working tree",
              "[BRAVO] roll resize" in wt and "[BRAVO] chase gate" in wt, wt)

        # --- invert: cede the marked work
        r = tool(repo, "stage", "f.txt", "--invert", "--marker", "[BRAVO]")
        check("invert: nothing staged when only BRAVO remains",
              "no hunks match" in r.stdout, r.stdout)
        r = tool(repo, "stage", "f.txt", "--marker", "[BRAVO]")
        cached2 = g(repo, "diff", "--cached", "-U0").stdout
        check("second author stages their own after",
              "[BRAVO]" in cached2 and r.returncode == 0, r.stdout + cached2)
        g(repo, "commit", "-qm", "bravo wave")
        check("tree clean after both waves",
              g(repo, "diff", "HEAD").stdout == "", "residue")

        # --- clean-file + no-match honesty
        r = tool(repo, "stage", "f.txt", "--marker", "[ALPHA]")
        check("clean file: honest no-diff message",
              "no working-tree diff" in r.stdout and r.returncode == 0, r.stdout)

        # --- structural refusal: binary
        with open(f, "wb") as fh:
            fh.write(b"\x00\x01\x02BINARY\x00")
        r = tool(repo, "stage", "f.txt", "--marker", "[ALPHA]")
        check("binary change refused",
              r.returncode != 0 and "binary" in (r.stdout + r.stderr).lower(),
              r.stdout + r.stderr)

        # --- marker required (an unmarked split IS git add)
        g(repo, "checkout", "--", "f.txt")
        lines = open(f).read().splitlines()
        lines[0] += "  # [ALPHA]"
        with open(f, "w") as fh:
            fh.write("\n".join(lines) + "\n")
        r = tool(repo, "stage", "f.txt")
        check("markerless stage refused", r.returncode != 0
              and "--marker required" in (r.stdout + r.stderr), r.stdout + r.stderr)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"commit_split battery: {PASS}/{PASS + FAIL} clean")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
