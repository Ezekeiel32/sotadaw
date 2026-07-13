#!/usr/bin/env python3
"""CRASH SYMBOLIZER — app_crash.log stamps -> function names, rebuild-proof.

The crash handler (ui_main.cpp) stamps every trace with the running exe's
identity (`== CRASH <when>  exe ino=I size=S mtime=M ==`) and raw backtrace
offsets (`.../SOTA DAW(+0xOFF) [0xADDR]`). Rebuilds link a NEW inode, so by
the time anyone reads the log the crashed binary is usually gone — the 21:16
Jul-12 crash died unsymbolizable exactly this way (its maps show the exe
`(deleted)`). The launcher now PINS each launched image by hardlink into
agent/ipc/.crash_pins/<ino>_<size>_<mtime>; this tool resolves each crash
entry to its pin (or the live exe when identity matches) and addr2lines it.

Usage:
  python3 tools/crash_symbolize.py [--last N] [--log P] [--pins P] [--exe P]
  python3 tools/crash_symbolize.py --selftest   (3-case proof, exit!=0 on red)
"""
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, "agent", "ipc", "app_crash.log")
PINS = os.path.join(ROOT, "agent", "ipc", ".crash_pins")
EXE = os.path.join(ROOT, "app", "build", "sotadaw_artefacts", "Release", "SOTA DAW")

STAMP = re.compile(r"^== CRASH (.+?)\s+exe ino=(\d+) size=(\d+) mtime=(\d+) ==$")
FRAME = re.compile(r"\(\+0x([0-9a-f]+)\)")


def parse_log(path):
    """-> [{when, ino, size, mtime, frames:[(line, off|None)]}] oldest-first."""
    entries = []
    cur = None
    try:
        lines = open(path, errors="replace").read().splitlines()
    except OSError:
        return []
    for ln in lines:
        m = STAMP.match(ln.strip())
        if m:
            cur = {"when": m.group(1), "ino": int(m.group(2)),
                   "size": int(m.group(3)), "mtime": int(m.group(4)),
                   "frames": []}
            entries.append(cur)
            continue
        if ln.startswith("== CRASH"):          # pre-ino-era stamp
            cur = {"when": ln.strip("= ").strip(), "ino": None,
                   "size": None, "mtime": None, "frames": []}
            entries.append(cur)
            continue
        if cur is not None and ln.strip():
            off = FRAME.search(ln)
            is_app = "SOTA DAW" in ln or "sotadaw" in ln
            cur["frames"].append((ln.strip(),
                                  int(off.group(1), 16) if (off and is_app) else None))
    return entries


def resolve_binary(entry, pins, exe):
    """The exact image that crashed: pin first, else the live exe on identity."""
    if entry["ino"] is None:
        return None, "pre-ino-era stamp (no identity to match)"
    key = f"{entry['ino']}_{entry['size']}_{entry['mtime']}"
    pin = os.path.join(pins, key)
    if os.path.isfile(pin):
        return pin, f"pin {key}"
    try:
        st = os.stat(exe)
        if (st.st_ino == entry["ino"] and st.st_size == entry["size"]
                and int(st.st_mtime) == entry["mtime"]):
            return exe, "live exe (identity matches)"
    except OSError:
        pass
    return None, f"UNSYMBOLIZABLE — no pin {key}, live exe differs (pre-pin era?)"


def addr2line(binary, offsets):
    """[off] -> [pretty]; empty on tool/exe absence (caller prints raw)."""
    if not offsets:
        return []
    try:
        r = subprocess.run(["addr2line", "-f", "-C", "-p", "-e", binary]
                           + [hex(o) for o in offsets],
                           capture_output=True, text=True, timeout=60)
        out = r.stdout.splitlines()
        return out if len(out) == len(offsets) else []
    except Exception:
        return []


def symbolize(entry, pins, exe, out=sys.stdout):
    binary, how = resolve_binary(entry, pins, exe)
    print(f"\n== CRASH {entry['when']}  [{how}]", file=out)
    offs = [o for _, o in entry["frames"] if o is not None]
    names = addr2line(binary, offs) if binary else []
    it = iter(names)
    for raw, off in entry["frames"]:
        if off is not None and names:
            print(f"  +{hex(off):<10} {next(it)}", file=out)
        else:
            print(f"  {raw}", file=out)
    return binary is not None and bool(names)


def selftest():
    """3 cases against the REAL binary: live-exe match, pin match, honest miss."""
    import io
    import shutil
    import tempfile
    checks = []

    def ok(cond, msg):
        checks.append((bool(cond), msg))

    if not os.path.isfile(EXE):
        print("selftest SKIP: no Release binary on disk")
        return 0
    nm = subprocess.run(["nm", EXE], capture_output=True, text=True)
    m = re.search(r"^([0-9a-f]+) T main$", nm.stdout, re.M)
    ok(m, "binary carries a symtab (nm finds `T main`)")
    if not m:
        return finish(checks)
    off = int(m.group(1), 16)
    st = os.stat(EXE)
    stamp = f"== CRASH selftest  exe ino={st.st_ino} size={st.st_size} mtime={int(st.st_mtime)} =="
    frame = f"{EXE}(+{hex(off)}) [0xdeadbeef]"
    tmp = tempfile.mkdtemp(prefix="crashsym_")
    try:
        # 1) live-exe identity match
        log1 = os.path.join(tmp, "a.log")
        open(log1, "w").write(f"{stamp}\n{frame}\n")
        buf = io.StringIO()
        done = [symbolize(e, os.path.join(tmp, "nopins"), EXE, buf)
                for e in parse_log(log1)]
        ok(done == [True] and "main" in buf.getvalue(),
           f"live-exe match symbolizes `main` (got: {buf.getvalue().strip()[-60:]})")
        # 2) identity mismatch + a PIN carrying the true image
        pins = os.path.join(tmp, "pins")
        os.makedirs(pins)
        key = f"{st.st_ino + 1}_{st.st_size}_{int(st.st_mtime)}"
        try:
            os.link(EXE, os.path.join(pins, key))
        except OSError:
            shutil.copy(EXE, os.path.join(pins, key))
        log2 = os.path.join(tmp, "b.log")
        open(log2, "w").write(
            f"== CRASH selftest2  exe ino={st.st_ino + 1} size={st.st_size} "
            f"mtime={int(st.st_mtime)} ==\n{frame}\n")
        buf = io.StringIO()
        done = [symbolize(e, pins, EXE, buf) for e in parse_log(log2)]
        ok(done == [True] and "main" in buf.getvalue() and "pin " in buf.getvalue(),
           "rebuild-replaced identity resolves through the PIN")
        # 3) no pin, no match -> HONEST miss (never a wrong-binary symbolization)
        log3 = os.path.join(tmp, "c.log")
        open(log3, "w").write(
            f"== CRASH selftest3  exe ino={st.st_ino + 2} size=1 mtime=1 ==\n{frame}\n")
        buf = io.StringIO()
        done = [symbolize(e, os.path.join(tmp, "nopins"), EXE, buf)
                for e in parse_log(log3)]
        ok(done == [False] and "UNSYMBOLIZABLE" in buf.getvalue(),
           "unknown identity reads out an HONEST miss, not wrong symbols")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return finish(checks)


def finish(checks):
    for okk, msg in checks:
        print(f"  {'ok ' if okk else 'FAIL'} {msg}")
    bad = sum(1 for okk, _ in checks if not okk)
    print(f"crash-symbolize selftest: {len(checks) - bad}/{len(checks)} "
          f"{'GREEN' if not bad else 'RED'}")
    return 1 if bad else 0


def main():
    if "--selftest" in sys.argv:
        return selftest()
    args = sys.argv[1:]

    def val(flag, default):
        return args[args.index(flag) + 1] if flag in args else default
    log = val("--log", LOG)
    pins = val("--pins", PINS)
    exe = val("--exe", EXE)
    last = int(val("--last", "2"))
    entries = parse_log(log)
    if not entries:
        print(f"no crash entries in {log}")
        return 0
    for e in entries[-last:]:
        symbolize(e, pins, exe)
    return 0


if __name__ == "__main__":
    sys.exit(main())
