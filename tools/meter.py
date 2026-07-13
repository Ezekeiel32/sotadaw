#!/usr/bin/env python3
"""THE WORLD GRID resolver (BEST_DAW_30 #1) — the ONE python bar<->quarter-beat
crossing, mirroring app/SongLoader.h Song::barStartBeat / barAtBeat / beatsInBar
EXACTLY. Notes/automation/clips stay QUARTER-BEAT absolute everywhere; only what
a BAR means changes under meterMap[] {bar,num,den} (a bar = num * 4/den quarters,
regions default 4/4 before the first entry).

LAWS (grid_lint enforces):
  * ONE RESOLVER — any other `bar * 4` / `beat / 4` site in the lawed agent
    files is a lint failure (waive deliberate 4/4-generator math with `# grid-ok:`).
  * IDENTITY — empty/absent map returns bar*4.0 / q/4.0 BIT-EXACT (single
    multiply, no accumulation): every existing mapless song behaves as yesterday.

Run: python3 tools/meter.py --selftest
"""

def song_meter(song):
    """Sorted, sanitized meterMap rows from a song dict ([] = pure 4/4).
    Mirrors the C++ parse: keep bar>=0, num>0, den>0; sort by bar."""
    rows = []
    for m in (song or {}).get("meterMap") or []:
        try:
            bar, num, den = float(m.get("bar", 0)), int(m.get("num", 0)), int(m.get("den", 0))
        except (TypeError, ValueError, AttributeError):
            continue
        if num > 0 and den > 0 and bar >= 0:
            rows.append({"bar": bar, "num": num, "den": den})
    rows.sort(key=lambda r: r["bar"])
    return rows

def bar_start_q(meter, bar):
    """Quarter-beat position where (possibly fractional) bar N starts."""
    bar = float(bar)
    if not meter:
        return bar * 4.0                      # identity law: mapless == yesterday
    q, prev, per = 0.0, 0.0, 4.0
    for mp in meter:
        mb = float(mp["bar"])
        if mb >= bar:
            break
        q += (mb - prev) * per
        prev, per = mb, float(mp["num"]) * 4.0 / float(mp["den"])
    return q + (bar - prev) * per

def bar_at_q(meter, q):
    """Fractional bar index containing quarter-beat q (bar_start_q's inverse)."""
    q = float(q)
    if not meter:
        return q / 4.0
    rq, prev, per = 0.0, 0.0, 4.0
    for mp in meter:
        mq = bar_start_q(meter, float(mp["bar"]))
        if mq >= q + 1e-9:
            break
        rq, prev = mq, float(mp["bar"])
        per = float(mp["num"]) * 4.0 / float(mp["den"])
    return prev + (q - rq) / per

def beats_in_bar(meter, bar):
    """Quarter-note beats in the bar containing `bar` (4.0 forever mapless)."""
    per = 4.0
    for mp in meter:
        if float(mp["bar"]) <= float(bar) + 1e-9:
            per = float(mp["num"]) * 4.0 / float(mp["den"])
        else:
            break
    return per

def parse_meter(s, default=(4, 4)):
    """'7/8' -> (7, 8). None/junk/non-positive -> default (the identity meter).
    The Genre.native_meter reader — loop_gen/arrange speak this one dialect."""
    try:
        num, den = str(s).split("/", 1)
        num, den = int(num.strip()), int(den.strip())
        if num > 0 and den > 0:
            return num, den
    except (ValueError, AttributeError, TypeError):
        pass
    return default

def default_groups(num, den):
    """Beat grouping in DEN units, the standard reading: compound den-8 meters
    group in 3s (6/8=3+3), aksak odd den-8 fill with 2s and END on the 3
    (7/8=2+2+3, 5/8=2+3); den-4 groups by quarter. Grids override with an
    explicit "groups" field (zeibekiko's 9/4 = 2+2+2+3 rides the grid)."""
    if den == 8 and num % 3 == 0:
        return [3] * (num // 3)
    if den == 8 and num % 2 == 1:
        return [2] * ((num - 3) // 2) + [3]
    if den == 8:
        return [2] * (num // 2)
    return [1] * num

def _selftest():
    ok = [0]
    def check(name, cond, detail=""):
        ok[0] += 0 if cond else 1
        print(("PASS " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))

    # identity law (bit-exact single ops)
    check("identity: bar_start_q([],7) == 28.0", bar_start_q([], 7) == 28.0)
    check("identity: bar_at_q([],30) == 7.5", bar_at_q([], 30) == 7.5)
    check("identity: beats_in_bar([],99) == 4.0", beats_in_bar([], 99) == 4.0)

    # the C++/bridge-proven case: 2 bars 4/4 then 7/8 -> bar 4 starts at 15.0
    m78 = [{"bar": 2, "num": 7, "den": 8}]
    check("7/8: bar_start_q(m,4) == 15.0", bar_start_q(m78, 4) == 15.0)
    check("7/8: bar_at_q inverse", abs(bar_at_q(m78, 15.0) - 4.0) < 1e-9)
    check("7/8: beats_in_bar(m,1)=4, (m,2)=3.5",
          beats_in_bar(m78, 1) == 4.0 and beats_in_bar(m78, 2) == 3.5)

    # three regions incl. den 16, fractional round-trip everywhere
    m3 = [{"bar": 0, "num": 3, "den": 4}, {"bar": 4, "num": 7, "den": 8},
          {"bar": 8, "num": 12, "den": 16}]
    for b in (0.0, 1.25, 4.0, 5.5, 8.0, 9.75, 20.0):
        q = bar_start_q(m3, b)
        check(f"3-region round-trip bar {b}", abs(bar_at_q(m3, q) - b) < 1e-9,
              f"q={q}")
    check("3-region: bar 4 = 3q*4 = 12.0", bar_start_q(m3, 4) == 12.0)
    check("3-region: bar 8 = 12 + 3.5*4 = 26.0", bar_start_q(m3, 8) == 26.0)
    check("3-region: bar 9 = 26 + 3.0", bar_start_q(m3, 9) == 29.0)

    # parse_meter + default_groups (the native_meter dialect)
    check("parse: '7/8' == (7,8)", parse_meter("7/8") == (7, 8))
    check("parse: junk/None -> (4,4)",
          parse_meter("x") == (4, 4) and parse_meter(None) == (4, 4)
          and parse_meter("0/8") == (4, 4))
    check("groups: 6/8=[3,3] 7/8=[2,2,3] 9/8=[3,3,3] 5/8=[2,3] 3/4=[1,1,1]",
          default_groups(6, 8) == [3, 3] and default_groups(7, 8) == [2, 2, 3]
          and default_groups(9, 8) == [3, 3, 3] and default_groups(5, 8) == [2, 3]
          and default_groups(3, 4) == [1, 1, 1])

    # sanitize: unsorted + junk rows drop, order restored
    s = song_meter({"meterMap": [{"bar": 4, "num": 7, "den": 8}, {"bar": 0, "num": 3, "den": 4},
                                 {"bar": 2, "num": 0, "den": 4}, {"bar": -1, "num": 4, "den": 4},
                                 "junk"]})
    check("sanitize: 2 rows sorted", [r["bar"] for r in s] == [0.0, 4.0], str(s))

    print(("SELFTEST GREEN" if not ok[0] else f"SELFTEST {ok[0]} FAILURES"))
    return ok[0]

if __name__ == "__main__":
    import sys
    sys.exit(_selftest())
