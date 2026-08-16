#!/usr/bin/env python3
"""commit_split.py — MY-HUNKS-ONLY staging for parallel sessions.

THE SWEEP CLASS (2026-07-16 + twice on 2026-07-31): session A runs
`git add <shared file>` and session B's in-flight working-tree hunks ride
A's commit. The cure everyone kept hand-rolling (the co-edit survival
playbook: diff vs HEAD, keep only your-marker hunks, git apply --cached)
is now a tool.

Usage:
  tools/commit_split.py stage <file> --marker "SPOKEN DESK" [--marker X2]
      Stage ONLY the hunks whose added/removed lines mention a marker;
      every other hunk stays working-tree-only. Then `git commit` (no -a!).
  tools/commit_split.py stage <file> --invert --marker "ROLL"
      Stage every hunk EXCEPT the marked ones (ceding marked work).
  tools/commit_split.py check <file>
      Print the hunk map (which markers own which hunks) without staging.

Mechanism: `git diff -U0 HEAD -- file` -> parse @@ hunks -> filter ->
re-emit a zero-context patch -> `git apply --cached --unidiff-zero`.
The UNION PROOF holds by construction: staged subset + remaining working
diff = the full diff (no hunk lost, no hunk duplicated) — and the battery
(tools/commit_split_battery.py, suite leg) proves it on a synthetic
two-author repo every run.

Scope law: text hunks only — renames/mode flips/binary refuse loudly
(stage those whole, with their owner's ack, like always).
"""
import argparse
import os
import re
import subprocess
import sys


def run(args, cwd=None, check=True, inp=None):
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True, input=inp)
    if check and r.returncode != 0:
        sys.stderr.write(r.stdout + r.stderr)
        raise SystemExit(f"commit_split: `{' '.join(args)}` failed rc={r.returncode}")
    return r


HUNK_RE = re.compile(r"^@@ -\d+(?:,\d+)? \+\d+(?:,\d+)? @@")


def parse_patch(text):
    """-> (header_lines, [ [hunk lines...] ]). Zero-context (-U0) diffs only."""
    lines = text.splitlines(keepends=True)
    header, hunks, cur = [], [], None
    for ln in lines:
        if HUNK_RE.match(ln):
            cur = [ln]
            hunks.append(cur)
        elif cur is None:
            header.append(ln)
        else:
            cur.append(ln)
    return header, hunks


def refuse_structural(header):
    joined = "".join(header)
    for bad in ("rename from", "rename to", "old mode", "new mode",
                "GIT binary patch", "Binary files"):
        if bad in joined:
            raise SystemExit(f"commit_split: structural/binary change ({bad!r}) — "
                             "stage that whole file deliberately, not through a splitter")


def hunk_matches(hunk, markers):
    body = "".join(ln for ln in hunk[1:] if ln[:1] in "+-")
    return any(m in body for m in markers)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("verb", choices=["stage", "check"])
    ap.add_argument("file")
    ap.add_argument("--marker", action="append", default=[],
                    help="substring identifying YOUR hunks (repeatable)")
    ap.add_argument("--invert", action="store_true",
                    help="stage the UNMARKED hunks instead (cede marked work)")
    ap.add_argument("--repo", default=None, help="repo root (default: cwd's repo)")
    a = ap.parse_args()

    repo = a.repo or run(["git", "rev-parse", "--show-toplevel"]).stdout.strip()
    rel = os.path.relpath(os.path.abspath(a.file), repo)
    diff = run(["git", "diff", "-U0", "HEAD", "--", rel], cwd=repo).stdout
    if not diff.strip():
        print(f"commit_split: {rel} has no working-tree diff vs HEAD")
        return 0
    header, hunks = parse_patch(diff)
    refuse_structural(header)

    if a.verb == "check":
        for i, h in enumerate(hunks):
            owns = [m for m in a.marker if hunk_matches(h, [m])] if a.marker else []
            tag = ",".join(owns) if owns else "-"
            print(f"  hunk {i + 1}: {h[0].strip()}  [{tag}]")
        print(f"commit_split: {len(hunks)} hunk(s) in {rel}")
        return 0

    if not a.marker:
        raise SystemExit("commit_split stage: at least one --marker required "
                         "(an unmarked split IS `git add` — the disease)")
    keep = [h for h in hunks
            if hunk_matches(h, a.marker) != a.invert]
    if not keep:
        print("commit_split: no hunks match — nothing staged")
        return 0
    patch = "".join(header) + "".join("".join(h) for h in keep)
    run(["git", "apply", "--cached", "--unidiff-zero", "-"], cwd=repo, inp=patch)
    print(f"commit_split: staged {len(keep)}/{len(hunks)} hunk(s) of {rel} "
          f"({'inverted ' if a.invert else ''}markers: {', '.join(a.marker)}); "
          "the rest stays working-tree-only — commit WITHOUT -a")
    return 0


if __name__ == "__main__":
    sys.exit(main())
