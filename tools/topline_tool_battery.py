#!/usr/bin/env python3
"""topline_tool_battery.py — proves the add_topline MCP tool (CC4 §7.6c).

tools/topline.py's kernel (HOOK/LIFT/TALK/SPACE) is proven; this asserts the
agent-tool WIRING: a multi-section song -> a 'topline' track whose chorus lifts
above the verse (LIFT) and whose choruses repeat verbatim (HOOK), plus the edit
receipt (track_wild=[topline]) and core-lane registration, and a graceful return
on a song with nothing to write over. Sandbox-isolated (own ipc dir; no
telemetry/git). Exit code IS the verdict (0 = pass, 1 = regression).
"""
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("SOTADAW_IPC", tempfile.mkdtemp(prefix="tlbat_"))
os.environ["SOTADAW_SANDBOX"] = "1"
sys.path.insert(0, os.path.join(ROOT, "agent"))
SONG = os.path.join(ROOT, "songs", "_topline_bat.json")


def build():
    return {"version": 2, "bpm": 120, "key": "A minor", "lengthBars": 32,
            "sections": [{"name": "verse", "startBar": 0}, {"name": "chorus", "startBar": 8},
                         {"name": "verse2", "startBar": 16}, {"name": "chorus2", "startBar": 24}],
            "chords": [{"bar": b, "chord": c} for b, c in
                       [(1, "Am"), (3, "F"), (5, "C"), (7, "G"), (9, "Am"), (11, "F"),
                        (13, "C"), (15, "G"), (17, "Am"), (19, "F"), (21, "C"), (23, "G"),
                        (25, "Am"), (27, "F"), (29, "C"), (31, "G")]],
            "tracks": [{"name": "pad", "source": {"kind": "faust", "id": "pad_motion"},
                        "gainDb": -10, "notes": [{"start": 0, "len": 4, "pitch": 57, "vel": 0.5}]}]}


def main():
    import daw_mcp
    print("== ADD_TOPLINE BATTERY ==")
    fails = 0
    json.dump(build(), open(SONG, "w"), indent=1)
    r = daw_mcp.t_add_topline({"song": "_topline_bat", "seed": 3})
    ok_ret = r.startswith("OK:")
    fails += not ok_ret
    print(f"  {'OK ' if ok_ret else 'XX '}return: {r[:58]}")

    d = json.load(open(SONG))
    tl = [t for t in d["tracks"] if t["name"] == "topline"]
    if tl:
        srt = sorted(tl[0]["notes"], key=lambda n: n["start"])

        def avg(lo, hi):
            ns = [n["pitch"] for n in srt if lo * 4 <= n["start"] < hi * 4]
            return sum(ns) / len(ns) if ns else 0.0
        lift = avg(8, 16) > avg(0, 8)
        c1 = [n["pitch"] for n in srt if 8 * 4 <= n["start"] < 16 * 4]
        c2 = [n["pitch"] for n in srt if 24 * 4 <= n["start"] < 32 * 4]
        hook = c1 == c2 and len(c1) > 0
        fails += (not lift) + (not hook)
        print(f"  {'OK ' if lift else 'XX '}LIFT chorus>verse ({avg(8,16):.1f}>{avg(0,8):.1f})")
        print(f"  {'OK ' if hook else 'XX '}HOOK choruses repeat ({len(c1)} notes, identical={c1==c2})")
    else:
        print("  XX no topline track written")
        fails += 2

    reg = "add_topline" in daw_mcp.TOOLS and "add_topline" in daw_mcp.CORE_TOOLS
    fails += not reg
    print(f"  {'OK ' if reg else 'XX '}registered (core lane)")

    rp = os.path.join(os.environ["SOTADAW_IPC"], "receipts.jsonl")
    recs = [json.loads(x) for x in open(rp)] if os.path.exists(rp) else []
    rec_ok = any(x.get("tool") == "add_topline" and x.get("track_wild") == ["topline"]
                 for x in recs)
    fails += not rec_ok
    print(f"  {'OK ' if rec_ok else 'XX '}receipt track_wild=[topline]")

    # graceful on an empty song (no sections/chords) — the tool must never raise
    json.dump({"version": 2, "bpm": 120, "key": "A minor", "lengthBars": 4, "tracks": []},
              open(SONG, "w"))
    try:
        r2 = daw_mcp.t_add_topline({"song": "_topline_bat"})
        guard = isinstance(r2, str) and len(r2) > 0
    except Exception as e:
        guard = False
        r2 = f"RAISED {e!r}"
    fails += not guard
    print(f"  {'OK ' if guard else 'XX '}graceful on empty song: {r2[:46]}")

    if os.path.exists(SONG):
        os.remove(SONG)
    print("PASS" if fails == 0 else f"REGRESSION ({fails})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
