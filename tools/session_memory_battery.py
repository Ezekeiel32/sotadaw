#!/usr/bin/env python3
"""SESSION MEMORY BATTERY — proof for agent/session_memory.py (T2-S1).

Pure, isolated (SOTADAW_IPC temp = the store namespaces away from live memory),
zero tokens. Proves the v17 laws the module claims: hard-overwrite revision with
tombstones (LAW 2), gone-retraction, last-write-wins folding over an append-only
file, garbage tolerance, the recall block's cap/order/age/honest-miss, the
last_edit ring, per-song + project namespacing — and THE SEAM: a written
refers_to fact makes a previously-unparseable ask compile in parse_lane and
land on the right track.
"""
import json, os, shutil, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IPC = tempfile.mkdtemp(prefix="sessmem_ipc_")
os.environ["SOTADAW_IPC"] = IPC
sys.path.insert(0, os.path.join(ROOT, "agent"))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import session_memory as sm                   # noqa: E402
import parse_lane, surgical                   # noqa: E402
from scalpel_suite import base_song, T        # noqa: E402

FAILS = []


def check(cond, label):
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}")
    if not cond:
        FAILS.append(label)


def main():
    S = "unit_song"
    T0 = 1_000_000.0

    # -------- namespacing under the isolation override
    check(sm.memory_dir().startswith(IPC), "store namespaces under SOTADAW_IPC")

    # -------- round trip + validation
    sm.write_fact(S, "squelchy one", "refers_to", "bass", prov="accepted edit", t=T0)
    got = sm.read_facts(S).get(("squelchy one", "refers_to"))
    check(got and got["value"] == "bass" and got["prov"] == "accepted edit",
          "write -> read round trip")
    for bad in (lambda: sm.write_fact(S, "x", "vibes", 1),
                lambda: sm.write_fact(S, "  ", "alias", "y"),
                lambda: sm.write_fact(S, "x", "alias", object())):
        try:
            bad()
            check(False, "invalid write rejected")
        except (ValueError, TypeError):
            check(True, "invalid write rejected")

    # -------- LAW 2: hard revision, tombstone, single live fact
    row = sm.write_fact(S, "squelchy one", "refers_to", "reese",
                        prov="re-established", t=T0 + 60)
    check(row.get("replaced", {}).get("value") == "bass",
          "revision tombstones the old value onto the new row")
    facts = sm.read_facts(S)
    live = [k for k in facts if k == ("squelchy one", "refers_to")]
    check(len(live) == 1 and facts[live[0]]["value"] == "reese",
          "hard overwrite: ONE live fact per (entity, rel), newest wins")

    # -------- retraction + re-establishment
    sm.retract(S, "squelchy one", "refers_to", prov="user: no", t=T0 + 120)
    check(("squelchy one", "refers_to") not in sm.read_facts(S),
          "gone-tombstone deletes the fact")
    sm.write_fact(S, "squelchy one", "refers_to", "bass", prov="confirmed again",
                  t=T0 + 180)
    check(sm.read_facts(S)[("squelchy one", "refers_to")]["value"] == "bass",
          "re-establishment after retraction works")

    # -------- garbage tolerance (append-only file survives corruption)
    with open(os.path.join(sm.memory_dir(), f"{S}.jsonl"), "a") as f:
        f.write("NOT JSON {{{\n")
        f.write(json.dumps({"entity": "x", "rel": "not_a_rel", "value": 1}) + "\n")
    check(sm.read_facts(S)[("squelchy one", "refers_to")]["value"] == "bass",
          "garbage + unknown-rel lines are skipped, store keeps working")

    # -------- last_edit ring
    for i in range(5):
        sm.remember_edit(S, "hats", f"edit {i}", t=T0 + 200 + i)
    ring = sm.read_facts(S)[("hats", "last_edit")]["value"]
    check(ring == ["edit 4", "edit 3", "edit 2"],
          f"last_edit ring keeps newest {sm.LAST_EDIT_KEEP}, newest first ({ring})")

    # -------- recall block: cap, order, age, honest miss
    check(sm.recall_block("empty_song") == "", "no facts -> EMPTY block (honest miss)")
    for i in range(20):
        sm.write_fact(S, f"e{i}", "sweet_spot", i, prov="receipt", t=T0 + 300 + i)
    blk = sm.recall_block(S, now=T0 + 400)
    lines = blk.strip().splitlines()
    check(len(lines) == 1 + sm.RECALL_CAP, f"recall capped at {sm.RECALL_CAP} lines")
    check("e19" in lines[1] and "ago" in lines[1], "newest first, age rendered")
    sm.write_fact(sm.PROJECT, "crash cymbals", "avoid", "never", prov="reject note",
                  t=T0 + 500)
    check("crash cymbals" in sm.recall_block(S, now=T0 + 600),
          "project prefs ride the song recall")

    # -------- per-song + project isolation
    check(("squelchy one", "refers_to") not in sm.read_facts("other_song"),
          "songs do not leak facts into each other")
    check(("crash cymbals", "avoid") in sm.read_facts(sm.PROJECT),
          "project namespace holds its own facts")

    # -------- THE SEAM: a fact makes the unparseable parseable (T2 -> T1)
    song = base_song()
    ask = "make the squelchy one 3db louder"
    miss, why = parse_lane.compile_debug(ask, song)
    check(miss is None, f"bare ask honestly misses ({why})")
    plan = parse_lane.compile(ask, song, facts=sm.alias_facts(S))
    check(plan is not None, "with the refers_to fact the SAME ask compiles")
    if plan:
        import copy
        prop = copy.deepcopy(song)
        surgical.clear_receipts()
        parse_lane.apply_plan(prop, plan, song_name="_sessmem")
        rep = surgical.scope_report(song, prop, surgical.read_receipts("_sessmem"))
        check(abs(T(prop, "bass")["gainDb"] - (T(song, "bass")["gainDb"] + 3)) < 0.01
              and rep.get("clean"),
              "the fact-resolved edit lands on the right track, scope-clean")
    check(sm.alias_facts(S).get("squelchy one") == "bass"
          and "hats" not in sm.alias_facts(S),
          "alias_facts exposes string refers_to/alias only (rings excluded)")

    # -------- confirm_verdict (the S2 accept hook, pure)
    S2 = "verdict_song"
    ok = sm.confirm_verdict(S2, {"touched_tracks": ["hats", "lead"],
                                 "receipts": ["hats: scale vel x0.7 [32->32 notes]"]},
                            {"pluck": "lead"}, "make the hats quieter", t=T0 + 700)
    f2 = sm.read_facts(S2)
    check(ok and f2[("hats", "last_edit")]["value"][0].startswith("hats: scale")
          and ("lead", "last_edit") in f2
          and f2.get(("pluck", "refers_to"), {}).get("value") == "lead",
          "confirm_verdict writes last_edit rings + refers_to from an accept")
    check(sm.confirm_verdict(S2, None, None, "") is True
          and sm.confirm_verdict(S2, {"touched_tracks": object()}, None, "") is False,
          "confirm_verdict never raises (empty ok, garbage swallowed)")

    # -------- parse_lane plans carry non-trivial resolutions (S2's raw material)
    song2 = base_song()
    p1 = parse_lane.compile("quantize the pluck", song2)
    check(p1 is not None and p1.get("resolutions") == {"pluck": "lead"},
          "non-trivial phrase->track resolution recorded on the plan")
    p2 = parse_lane.compile("mute the hats", song2)
    check(p2 is not None and p2.get("resolutions") == {},
          "trivial name match records NO resolution")

    # -------- the retarget grammar (S4) at kernel level
    h = {"last_plan": {"ask": "make the hats quieter in the verse only",
                       "pattern": "gain",
                       "summary": "hats: velocity x0.7079 in 'verse' (32 notes)",
                       "actions": [{"kind": "surgical",
                                    "selector": {"tracks": ["hats"], "section": "verse"},
                                    "ops": [{"op": "scale", "vel": 0.7079}]}],
                       "track": "hats"}}
    song3 = base_song()
    pr = parse_lane.compile("do that to the snare too", song3, history=h)
    check(pr is not None and pr["actions"][0]["selector"]["tracks"] == ["snare"],
          "retarget swaps the stored plan onto the new track (kernel)")
    check(parse_lane.primary_track(pr) == "snare", "primary_track follows the retarget")
    check(parse_lane.compile("do that to the snare too", song3) is None,
          "retarget without history misses (kernel)")
    check(parse_lane.compile("what did we change on the hats", song3) is not None,
          "history question compiles to the memory verb")
    check(parse_lane.compile("what did we change in the hook", song3) is None,
          "section-form history question stays cloud (RECALL carries it)")

    # --- avoid_from_reject (pass 5): the reject WHY survives the 30-min
    # feedback window as a bucketed avoid fact (same kernel as KG complaints)
    song4 = "avoidsong"
    check(sm.avoid_from_reject(song4, "way too busy in the chorus, too many hats"),
          "bucketed reject WHY writes an avoid fact")
    f = sm.read_facts(song4).get(("busy", "avoid"))
    check(f is not None and "too many hats" in str(f["value"]),
          "avoid fact lands in the busy bucket, words verbatim")
    check("busy [avoid]" in sm.recall_block(song4),
          "RECALL carries the standing objection")
    check(not sm.avoid_from_reject(song4, "   "), "empty WHY writes nothing")
    sm.avoid_from_reject(song4, "still too busy everywhere")
    f2 = sm.read_facts(song4).get(("busy", "avoid"))
    check(f2 is not None and f2["value"] == "still too busy everywhere"
          and f2.get("replaced") is not None,
          "LAW 2: newest complaint per bucket, old one tombstoned")

    n = len(FAILS)
    print(f"\n== SESSION MEMORY BATTERY: {'ALL GREEN' if n == 0 else f'{n} FAILURE(S)'} ==")
    for f in FAILS:
        print("  - " + f)
    return 1 if n else 0


if __name__ == "__main__":
    try:
        rc = main()
    finally:
        shutil.rmtree(IPC, ignore_errors=True)
    sys.exit(rc)
