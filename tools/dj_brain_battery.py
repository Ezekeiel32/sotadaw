#!/usr/bin/env python3
"""DJ BRAIN BATTERY — proves wave 45 (r-27 items 163/101/102). Pure.
(dj_arc_battery / dj_clash_battery stay the standing legs — this proves
the NEW kernels beside them.)"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dj_set as DS  # noqa: E402
from dj_mix import harmonic_move, harmonic_verdict  # noqa: E402

FAILS = []


def check(name, cond, note=""):
    tag = "PASS" if cond else "FAIL"
    print(f"[{tag}] {name}" + (f" — {note}" if note and not cond else ""))
    if not cond:
        FAILS.append(name)


# ---------------------------------------- 102 half/double-time bridge
c_bridge = DS.hop_cost((170.0, "8A", 0.9), (85.0, "8A", 0.9))
c_cut = DS.hop_cost((170.0, "8A", 0.9), (120.0, "8A", 0.9))
check("bridge: 170 -> 85 is a FEEL FLIP, not an echo-out cut",
      c_bridge < c_cut and c_bridge < 8.0,
      f"bridge {c_bridge:.1f} vs cut {c_cut:.1f}")
c_plain = DS.hop_cost((128.0, "8A", 0.9), (130.0, "8A", 0.9))
check("bridge: a plain 128->130 blend stays nearly free",
      c_plain < 2.0, str(c_plain))

# ------------------------------------------------- 163 the wave arc
check("wave shape: rise, breathe, finish",
      DS.arc_shape("wave", 0.3) > DS.arc_shape("wave", 0.0) and
      DS.arc_shape("wave", 0.55) < DS.arc_shape("wave", 0.35) and
      DS.arc_shape("wave", 1.0) > DS.arc_shape("wave", 0.6) and
      abs(DS.arc_shape("wave", 1.0) - 1.0) < 1e-9)
# the breather record: 68bpm = exactly halftime of 136 — the wave can
# park it MID-SET through the bridge while peak must open on it
items = [(124.0, "8A", 0.9), (128.0, "8A", 0.9), (132.0, "9A", 0.9),
         (136.0, "9A", 0.9), (68.0, "8A", 0.9), (140.0, "10A", 0.9)]
order_peak, _ = DS.plan_order(items, "peak")
order_wave, _ = DS.plan_order(items, "wave")
bpms_peak = [items[i][0] for i in order_peak]
bpms_wave = [items[i][0] for i in order_wave]
check("global shape: PEAK opens on the slow record and climbs",
      bpms_peak[0] == 68.0, str(bpms_peak))
check("global shape: WAVE parks the 68 MID-SET as the breather "
      "(the halftime bridge makes it pocket with 136) and the fastest "
      "closes",
      bpms_wave.index(68.0) in (2, 3) and bpms_wave[-1] == 140.0 and
      bpms_wave != sorted(bpms_wave), str(bpms_wave))

# ----------------------------------------- 101 tiered harmonic moves
m = harmonic_move("8A", "9A")
check("move: +1 same letter = clean, ENERGY UP",
      m["tier"] == "clean" and m["energy"] == "up", str(m))
m = harmonic_move("9A", "8A")
check("move: -1 = clean, energy DOWN",
      m["tier"] == "clean" and m["energy"] == "down", str(m))
m = harmonic_move("8A", "8B")
check("move: minor->major relative = BRIGHTEN",
      m["tier"] == "clean" and m["energy"] == "brighten", str(m))
m = harmonic_move("8A", "10A")
check("move: +2 = the risky double-boost (gray, up)",
      m["tier"] == "gray" and m["energy"] == "up", str(m))
m = harmonic_move("8A", "3B")
check("move: distant slot = clash", m["tier"] == "clash", str(m))
check("compat: the string API keeps its tokens (batteries depend on it)",
      "CLASH" in harmonic_verdict("8A", "3B") and
      "COMPATIBLE" in harmonic_verdict("8A", "9A"))

print()
if FAILS:
    print(f"dj_brain_battery: {len(FAILS)} RED — " + "; ".join(FAILS))
    sys.exit(1)
print("dj_brain_battery: ALL GREEN")
