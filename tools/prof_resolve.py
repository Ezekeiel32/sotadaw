#!/usr/bin/env python3
"""THE PROFILE READER (wave 4): fold the binary's own SIGPROF samples into a cost tree.

The box denies every external profiler (yama ptrace_scope=1 blocks gdb attach even on
own processes, kernel.perf_event_paranoid=4 blocks perf, no valgrind) — so the app
records itself: SOTADAW_PROF=<hz> arms a SIGPROF sampler in the binary; at shutdown it
dumps raw return addresses to <ipc>/prof.samples plus /proc/self/maps to <ipc>/prof.maps.
This script resolves those through addr2line and prints:
  - the leaf histogram (who was ON CPU)
  - the folded-stack histogram (who PUT them there)

usage: prof_resolve.py <ipc_dir> [--binary path] [--top N]
"""
import argparse
import collections
import subprocess
import sys
from pathlib import Path


def parse_maps(maps_path):
    """[(start, end, offset, path)] for file-backed executable mappings."""
    out = []
    for line in Path(maps_path).read_text().splitlines():
        parts = line.split()
        if len(parts) < 6 or "x" not in parts[1]:
            continue
        path = " ".join(parts[5:])
        if not path.startswith("/"):
            continue
        rng, off = parts[0], int(parts[2], 16)
        start, end = (int(x, 16) for x in rng.split("-"))
        out.append((start, end, off, path))
    return out


def is_pie(path):
    try:
        head = subprocess.run(["readelf", "-h", path], capture_output=True, text=True).stdout
        return "DYN" in head.split("Type:")[1].splitlines()[0]
    except Exception:
        return True  # modern default


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ipc_dir")
    ap.add_argument("--binary", help="resolve app frames against THIS file (a saved copy "
                                     "if the on-disk binary moved on since the run)")
    ap.add_argument("--top", type=int, default=25)
    args = ap.parse_args()
    ipc = Path(args.ipc_dir)

    maps = parse_maps(ipc / "prof.maps")
    samples = []
    for line in (ipc / "prof.samples").read_text().splitlines():
        addrs = [int(a, 16) for a in line.split() if a]
        if addrs:
            samples.append(addrs)
    if not samples:
        sys.exit("no samples")

    # map addr -> (path, link-time vaddr). For PIE/DSO: standard linkers keep
    # p_vaddr == p_offset per LOAD segment, so vaddr = addr - start + offset of
    # the CONTAINING mapping (subtracting the text start alone shifts everything
    # into one .cold symbol — the first resolve pass's lie).
    pie_cache = {}

    def locate(addr):
        for start, end, off, path in maps:
            if start <= addr < end:
                if path not in pie_cache:
                    pie_cache[path] = is_pie(path)
                return path, (addr - start + off) if pie_cache[path] else addr
        return None, None

    # batch-resolve unique addresses per module
    per_mod = collections.defaultdict(set)
    for st in samples:
        for a in st:
            path, va = locate(a)
            if path:
                per_mod[path].add((a, va))
    name_of = {}
    for path, pairs in per_mod.items():
        rpath = args.binary if (args.binary and path.endswith("SOTA DAW")) else path
        pairs = sorted(pairs)
        try:
            res = subprocess.run(
                ["addr2line", "-e", rpath, "-Cf"] + [hex(va) for _a, va in pairs],
                capture_output=True, text=True).stdout.splitlines()
        except Exception:
            res = []
        mod = Path(path).name
        for i, (a, _va) in enumerate(pairs):
            fn = res[i * 2].strip() if i * 2 < len(res) else "??"
            name_of[a] = f"{fn} [{mod}]" if fn != "??" else f"?? [{mod}]"

    def named(a):
        return name_of.get(a, "??")

    NOISE = ("onProf", "backtrace", "killpg", "__restore_rt", "??")
    leaf = collections.Counter()
    folded = collections.Counter()
    for st in samples:
        names = [named(a) for a in st]
        real = [n for n in names if not any(x in n for x in NOISE)]
        if not real:
            continue
        leaf[real[0]] += 1
        folded[";".join(reversed(real[:12]))] += 1

    total = sum(leaf.values())
    print(f"samples={len(samples)} attributed={total}\n== LEAF (on-cpu) ==")
    for fn, n in leaf.most_common(args.top):
        print(f"{100.0 * n / total:5.1f}%  {n:5d}  {fn}")
    print("\n== HOT STACKS (folded, top) ==")
    for st, n in folded.most_common(min(args.top, 12)):
        print(f"{100.0 * n / total:5.1f}%  {st}")


if __name__ == "__main__":
    main()
