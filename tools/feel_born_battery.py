#!/usr/bin/env python3
"""FEEL-BORN battery — generated loops carry their genre's KG groove at birth.

boombap -> dilla on the feel lanes (hats/snare/percs), kick stays the anchor,
byte-idempotent per seed, groove-less genres unchanged.

Usage: python3 tools/feel_born_battery.py
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import loop_gen

PASS, FAIL = 0, []
def ok(cond, msg):
    global PASS
    if cond:
        PASS += 1
    else:
        FAIL.append(msg)

def gen(genre, name, seed):
    out, msg = loop_gen.generate(genre, name, 4, seed, None, None)
    assert out, msg
    doc = json.load(open(out))
    os.remove(out)
    return doc, msg

def profile_fingerprint(notes):
    """A GROOVE (vs random humanize) is SLOT-CONSISTENT: every note in the same
    16th slot shares one deviation. Returns (consistent_nonzero_slots, slots)."""
    import collections
    slots = collections.defaultdict(set)
    for n in notes:
        grid = round(n["start"] / 0.25) * 0.25
        slots[int(round((grid % 4) / 0.25)) % 16].add(round(n["start"] - grid, 4))
    good = sum(1 for devs in slots.values() if len(devs) == 1 and abs(next(iter(devs))) > 0.003)
    return good, len(slots)

def main():
    # 1) boombap is born with dilla on the feel lanes
    doc, msg = gen("boombap", "_feel_a", 107)
    ok("groove dilla" in msg, f"birth message names the groove ({msg[-60:]})")
    felt = [t for t in doc["tracks"] if t.get("groove", {}).get("name") == "dilla"]
    ok(len(felt) >= 1, f"provenance stamped on {len(felt)} feel lane(s)")
    for t in felt:
        good, tot = profile_fingerprint(t["notes"])
        ok(good >= 3, f"'{t['name']}': {good}/{tot} slots carry the CONSISTENT profile "
                      f"deviation (a groove, not random drift)")
    kick = next((t for t in doc["tracks"] if "kick" in t["name"].lower()), None)
    if kick:
        ok(not kick.get("groove"), "kick stays the anchor (no groove provenance)")
    # 2) determinism: same seed = byte-equal
    d2, _ = gen("boombap", "_feel_b", 107)
    a = json.dumps({**doc, "_loop": None}, sort_keys=True)
    b = json.dumps({**d2, "_loop": None}, sort_keys=True)
    ok(a == b, "same seed -> byte-equal (groove is deterministic)")
    # 3) a groove-less genre is untouched by the new path
    d3, m3 = gen("ambient", "_feel_c", 106)
    ok("groove" not in m3, "groove-less genre: birth message clean")
    ok(not any(t.get("groove") for t in d3["tracks"]), "no phantom provenance")
    # 4) ukgarage rides ukg_shuffle
    d4, m4 = gen("ukgarage", "_feel_d", 105)
    ok("ukg_shuffle" in m4, f"ukgarage born with ukg_shuffle ({m4[-50:]})")

if __name__ == "__main__":
    main()
    for f in FAIL:
        print("FAIL:", f)
    print(f"feel-born battery: {PASS}/{PASS + len(FAIL)} {'clean' if not FAIL else 'RED'}")
    sys.exit(1 if FAIL else 0)
