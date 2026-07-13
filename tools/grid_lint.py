#!/usr/bin/env python3
"""THE GRID LINT (BEST_DAW_30 #1 guardian) — ONE RESOLVER law, machine-enforced.

All bar<->quarter-beat math in the LAWED agent files must route through
tools/meter.py (bar_start_q / bar_at_q / beats_in_bar). A raw `bar * 4` /
`beat / 4` site silently hard-codes 4/4 and LIES on any song with a meterMap —
the exact class this lint retires (get_song_region/comp_take/locate all did it).

  * lawed files: any bar-token + literal-4 arithmetic line = RED unless it calls
    the resolver or carries a `grid-ok:` waiver (deliberate mapless-4/4 math —
    say why on the line).
  * waived files: declared self-consistent 4/4 generators, printed honestly
    (no silent caps) — they convert when Genre.native_meter lands.

Run: python3 tools/grid_lint.py   (exit 0 green / 1 red; suite leg)
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LAWED = ["agent/daw_mcp.py", "agent/surgical.py", "agent/sidecar.py",
         "tools/midi_bridge.py",
         # the two that WRITE songs — birth (loop_gen) and form (arrange). They
         # carried the 4/4 lie deepest: `bar * 4.0` in 66 arrange sites and a
         # 16-steps-per-bar assumption through every loop_gen lane. Both now
         # ride the bar's own length (tools/meter_battery.py is the court).
         "tools/loop_gen.py", "tools/arrange.py",
         # the court that JUDGES generation must window bars by the same truth —
         # its raw `b*4` windows convicted a bit-perfect 7/8 kick of ANCHOR.
         "tools/dna_battery.py"]
WAIVED_FILES = {}

BAR_TOKEN = re.compile(r"\b\w*[Bb]ars?\w*\b")
FOUR_OP = re.compile(   # digit-preceded ops excluded so prose "4/4" never trips it
    r"(?:(?<![\w.)\]])4(?:\.0)?\s*\*)|(?:(?<![\d.])(?:\*|//?)\s*4(?:\.0)?(?![\d.\w]))")
RESOLVER = re.compile(r"bar_start_q|bar_at_q|beats_in_bar|song_meter")


def lint():
    bad = []
    for rel in LAWED:
        path = os.path.join(ROOT, rel)
        for i, line in enumerate(open(path, encoding="utf-8"), 1):
            code = line.split("#", 1)[0]
            if "grid-ok" in line or RESOLVER.search(code):
                continue
            if BAR_TOKEN.search(code) and FOUR_OP.search(code):
                bad.append(f"{rel}:{i}: {line.strip()[:100]}")
    for rel, why in WAIVED_FILES.items():
        print(f"grid_lint: WAIVED {rel} — {why}")
    if bad:
        print(f"grid_lint: {len(bad)} raw bar-math site(s) outside tools/meter.py "
              f"(route through the resolver or waive with `# grid-ok: <why>`):")
        for b in bad:
            print("  " + b)
        return 1
    print(f"grid_lint: GREEN — {len(LAWED)} lawed files, one resolver")
    return 0


if __name__ == "__main__":
    sys.exit(lint())
