#!/usr/bin/env python3
"""THE BRAIN BR-A — THE DATA LEDGER (docs/SPEC_THE_BRAIN.md PART I).

THE LEDGER LAW: no learned organ is trained without its dataset row counted
HERE, at train time — not quoted from a doc that goes stale (the KG was
205 genres while the docs still said 131; this file exists so that class of
lie is structurally impossible).

Rows D1..D12 mirror the spec table + D13 (the bank itself). Every counter
degrades to an HONEST -1 ("unavailable"), never a guess, never a raise.
check_floors(need) is what organs call to refuse under-fed training.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEF_ROOT = os.path.dirname(HERE)


def _count_glob(root, rel, suffix=".json", exclude_underscore=False):
    d = os.path.join(root, rel)
    try:
        names = os.listdir(d)
    except OSError:
        return 0
    n = 0
    for x in names:
        if not x.endswith(suffix):
            continue
        if exclude_underscore and x.startswith("_"):
            continue
        n += 1
    return n


def _count_lines(root, rel):
    try:
        with open(os.path.join(root, rel), "rb") as f:
            return sum(1 for _ in f)
    except OSError:
        return 0


def _d1_midi_corpus(root):
    """MIDI corpus files under .venv's melody-features package (walk-counted)."""
    base = os.path.join(root, ".venv")
    if not os.path.isdir(base):
        return -1
    n = 0
    for dirpath, dirnames, filenames in os.walk(base):
        if "melody_features" not in dirpath:
            # prune wide: only descend toward the package
            dirnames[:] = [d for d in dirnames
                           if "melody" in d or "site-packages" in d or "lib" in d
                           or d.startswith("python")]
            continue
        n += sum(1 for f in filenames if f.endswith(".mid"))
    return n


def _d6_accept_commits(root):
    try:
        p = subprocess.run(["git", "log", "--oneline"], capture_output=True,
                           text=True, timeout=20, cwd=root)
        if p.returncode != 0:
            return -1
        return sum(1 for ln in p.stdout.splitlines()
                   if ln.split(" ", 1)[-1].lower().startswith("accept"))
    except Exception:
        return -1


def _d9_kg(root):
    kg = os.path.join(root, "tools", "kg.py")
    py = os.path.join(root, ".venv", "bin", "python")
    if not (os.path.exists(kg) and os.path.exists(py)):
        return -1
    try:
        p = subprocess.run([py, kg, "stats"], capture_output=True, text=True,
                           timeout=15, cwd=root)
        if p.returncode != 0:
            return -1
        stats = json.loads(p.stdout)
        return int(stats.get("Genre", -1))
    except Exception:
        return -1


def _d10_presets(root):
    try:
        d = json.load(open(os.path.join(root, "library.json")))
        return len(d.get("vst_presets") or [])
    except Exception:
        return -1


def _d11_stem_dirs(root):
    d = os.path.join(root, "songs")
    try:
        return sum(1 for x in os.listdir(d)
                   if x.endswith("_stems") and os.path.isdir(os.path.join(d, x)))
    except OSError:
        return 0


def _d12_receipts(root):
    ipc = os.environ.get("SOTADAW_IPC") or os.path.join(root, "agent", "ipc")
    try:
        with open(os.path.join(ipc, "receipts.jsonl"), "rb") as f:
            return sum(1 for _ in f)
    except OSError:
        return 0


ROWS = [
    ("D1", "MIDI corpus files (melody-features)", _d1_midi_corpus),
    ("D2", "gold exemplars", lambda r: _count_glob(r, "library/gold")),
    ("D3", "crate DNA loops", lambda r: _count_glob(r, "songs/crate")),
    ("D4", "own songs (non-underscore)",
     lambda r: _count_glob(r, "songs", exclude_underscore=True)),
    ("D5", "verdict tuples (proposals.jsonl)",
     lambda r: _count_lines(r, "telemetry/proposals.jsonl")),
    ("D6", "accepted takes (git commits)", _d6_accept_commits),
    ("D7", "eval brief outcomes", lambda r: _count_lines(r, "eval/history.jsonl")),
    ("D8", "per-song chronicles",
     lambda r: _count_glob(r, "songs/.chat", suffix=".jsonl")),
    ("D9", "KG genres (live)", _d9_kg),
    ("D10", "factory presets (vst_presets)", _d10_presets),
    ("D11", "imported stem sessions", _d11_stem_dirs),
    ("D12", "edit receipts (session ipc)", _d12_receipts),
    ("D13", "banked brain tuples",
     lambda r: _count_lines(r, "telemetry/brain_tuples.jsonl")),
]


def ledger(root=None):
    """{row_id: {"desc", "count"}} — count -1 means honestly unavailable."""
    root = root or DEF_ROOT
    out = {}
    for rid, desc, fn in ROWS:
        try:
            out[rid] = {"desc": desc, "count": int(fn(root))}
        except Exception:
            out[rid] = {"desc": desc, "count": -1}
    return out


def check_floors(need, l=None, root=None):
    """LEDGER LAW gate: need = {"D5": 100, ...}. Returns (ok, misses[]).
    An unavailable (-1) row always misses — you may not train on a guess."""
    l = l or ledger(root)
    misses = []
    for rid, floor in (need or {}).items():
        c = (l.get(rid) or {}).get("count", -1)
        if c < floor:
            misses.append(f"{rid}={c} < floor {floor}")
    return (not misses), misses


if __name__ == "__main__":
    l = ledger()
    for rid, row in l.items():
        c = row["count"]
        print(f"{rid:>4}  {c if c >= 0 else 'unavailable':>12}  {row['desc']}")
    sys.exit(0)
