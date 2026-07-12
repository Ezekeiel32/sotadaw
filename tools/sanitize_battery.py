#!/usr/bin/env python3
"""SANITIZE-AT-WRITE battery (ledger dr16, 2026-07-12) — the write boundary
heals what a weak model can emit: NaN/Infinity fields (json.loads ACCEPTS
them; the engine then corpses the whole song), exact stacked duplicates
(+6 dB phase doubling that SHIPS as audio), negative starts, vel>1,
pitch off the wire. Pure kernel proofs + the wiring law. Exit 0 = green.
"""
import math, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "agent"))
import daw_mcp as M                                                          # noqa: E402

PASS, FAIL = [], []


def ck(n, c, d=""):
    (PASS if c else FAIL).append(n)
    print(f"  [{'PASS' if c else 'FAIL'}] {n}" + (f" — {d}" if d else ""))


nan, inf = float("nan"), float("inf")

# 1. non-finite fields heal, non-finite notes drop
s, rec = M.sanitize_song({"tracks": [{"name": "x", "gainDb": nan, "pan": inf,
                                      "notes": [{"start": nan, "len": 1, "pitch": 60, "vel": 0.8},
                                                {"start": 0, "len": 1, "pitch": 60, "vel": 0.8}]}]})
t = s["tracks"][0]
ck("non-finite gainDb/pan healed to 0", t["gainDb"] == 0.0 and t["pan"] == 0.0)
ck("non-finite-start note dropped, clean note kept", len(t["notes"]) == 1)
ck("receipts written", len(rec) >= 2, str(rec))

# 2. the +6 dB stack: exact duplicates merge, louder wins
s, rec = M.sanitize_song({"tracks": [{"name": "x", "notes": [
    {"start": 1.0, "len": 0.5, "pitch": 64, "vel": 0.5},
    {"start": 1.0, "len": 0.5, "pitch": 64, "vel": 0.9},
    {"start": 1.0, "len": 0.5, "pitch": 67, "vel": 0.6}]}]})
ns = s["tracks"][0]["notes"]
ck("stacked duplicate merged (2 remain)", len(ns) == 2, str(ns))
ck("the louder duplicate wins", any(n["vel"] == 0.9 for n in ns))

# 3. clamps: negative start, len<=0, vel>1, pitch off the wire
s, _ = M.sanitize_song({"tracks": [{"name": "x", "notes": [
    {"start": -2.0, "len": 0.0, "pitch": 300, "vel": 4.0}]}]})
n = s["tracks"][0]["notes"][0]
ck("negative start -> 0", n["start"] == 0.0)
ck("len<=0 -> 0.1", n["len"] == 0.1)
ck("pitch clamped to 127", n["pitch"] == 127)
ck("vel clamped to 1.0", n["vel"] == 1.0)

# 4. clean songs pass untouched (no false healing)
clean = {"tracks": [{"name": "x", "gainDb": -6.0,
                     "notes": [{"start": 0.0, "len": 1.0, "pitch": 60, "vel": 0.8},
                               {"start": 1.0, "len": 1.0, "pitch": 62, "vel": 0.7}]}]}
s, rec = M.sanitize_song(clean)
ck("clean song: zero receipts, notes untouched",
   not rec and len(s["tracks"][0]["notes"]) == 2)

# 5. wiring law: write_song consults the kernel
ck("wired into t_write_song", "sanitize_song" in M.t_write_song.__code__.co_names)
ck("wired into t_update_track", "sanitize_song" in M.t_update_track.__code__.co_names)

print(f"\n== SANITIZE: {len(PASS)} pass / {len(FAIL)} fail ==")
sys.exit(0 if not FAIL else 1)
