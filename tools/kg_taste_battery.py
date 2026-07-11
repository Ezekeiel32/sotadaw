#!/usr/bin/env python3
"""KG TASTE battery — reject WHYs become per-genre complaint data in the graph.

Pure: bucket taxonomy (first-match, stable names, silent on empty) + the
ATTRIBUTION v4 rung ladder (attribute_rows: explicit tag > normalized
word-boundary text scan > song-sticky > import Reference > song-name scan;
fixtures pin the warehouse/house boundary + that weak rungs never seed
stickiness — THE DARK POOL DRAIN's whole contract, zero graph needed).
Real (default; needs the sotadaw-kg docker): a scratch Genre `_taste_test` +
temp telemetry -> ingest() -> read back complaints/last_whys -> DETACH DELETE
the scratch node + its snapshot. No real genre is touched (attribution needs
the genre name in the prompt; only `_taste_test` appears in the fixtures).

Usage: .venv/bin/python tools/kg_taste_battery.py
"""
import json, os, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import kg_ingest_telemetry as ing
from kg import KG, esc

PASS, FAIL = 0, []
def ok(cond, msg):
    global PASS
    if cond:
        PASS += 1
    else:
        FAIL.append(msg)

def main():
    # ---- pure taxonomy ----
    ok(ing.complaint_bucket("too bright, lost the groove") == "bright",
       "first-match wins (bright beats groove)")
    ok(ing.complaint_bucket("wrong groove") == "groove", "groove keys")
    ok(ing.complaint_bucket("it is way too muddy") == "dark", "dark keys")
    ok(ing.complaint_bucket("not on beat") == "groove",
       "off-beat phrasing reaches groove (a real 2026-07 WHY sat on 'other')")
    ok(ing.complaint_bucket("hate it") == "other", "unmatched text -> other")
    ok(ing.complaint_bucket("") is None and ing.complaint_bucket(None) is None,
       "silent rejects carry no bucket")

    # ---- pure attribution: the v4 rung ladder on fixtures ----
    gs = ["house", "acid_house", "progressive_house", "deep_house", "phonk", "_untagged"]
    calls = {"n": 0}
    def ref(song):  # stateful: proves rung-4 tags are used but NEVER seed stickiness
        if song == "s1":
            calls["n"] += 1
            return "phonk" if calls["n"] == 1 else None
        return None
    rows = [
        {"song": "a", "genre": "acid_house", "prompt": "techno banger"},  # 1: explicit beats text
        {"song": "b", "prompt": "make an ACID-HOUSE loop"},   # 2: hyphen/case-normalized multi-word
        {"song": "c", "prompt": "warehouse party stomper"},   # boundary: 'warehouse' never tags house
        {"song": "d", "prompt": "progressive house please"},  # longest-first beats 'house'
        {"song": "b", "prompt": "BASS IS SHIT!"},             # 3: session follow-up rides song-sticky
        {"song": "b", "prompt": "now make it phonk"},         # mid-session pivot re-tags in text
        {"song": "b", "prompt": "louder!"},                   # sticky rides the PIVOT, not the opener
        {"song": "s1", "prompt": ""},                         # 4: import Reference lookup
        {"song": "s1", "prompt": "again"},                    # weak rung never seeded -> falls to _untagged
        {"song": "eval_deep_house_3", "prompt": ""},          # 5: song-NAME scan, last resort
    ]
    want = ["acid_house", "acid_house", "_untagged", "progressive_house",
            "acid_house", "phonk", "phonk", "phonk", "_untagged", "deep_house"]
    got = ing.attribute_rows(rows, gs, ref)
    for i, (g, w) in enumerate(zip(got, want)):
        ok(g == w, f"attribution rung fixture {i} ({rows[i].get('prompt') or rows[i]['song']}): want {w}, got {g}")

    # ---- pure rung-4 lookup: copy-suffix stem tolerance ----
    bank = {"blpkosher-hourglassofficialvideo_2": "phonk", "_ic_probe": "lofi"}
    ok(ing.match_reference("blpkosher-hourglassofficialvideo_2", bank) == "phonk",
       "reference exact hit")
    ok(ing.match_reference("blpkosher-hourglassofficialvideo", bank) == "phonk",
       "bare name finds the _2 bank (copy-suffix stem)")
    ok(ing.match_reference("blpkosher-hourglassofficialvideo_3", bank) == "phonk",
       "sibling copy _3 finds the _2 bank")
    ok(ing.match_reference("_ic_probe", bank) == "lofi", "scratch exact still hits")
    ok(ing.match_reference("untitled_2", {"untitled_5": "trap"}) is None,
       "untitled_N never stem-matches a sibling session")
    ok(ing.match_reference("_mse2e", {"_mse2e_2": "trap"}) is None,
       "scratch _names never fuzzy-match")

    # ---- real graph round-trip on a scratch genre ----
    kg = KG()
    kg.g.query("MATCH (g:Genre {name: '_taste_test'}) DETACH DELETE g")
    kg.upsert("Genre", "_taste_test", "test:kg_taste_battery", bpm_lo=0, bpm_hi=0)
    rows = [
        {"t": 1, "song": "x", "accepted": False, "note": "too bright, lost the groove",
         "prompt": "make a _taste_test loop"},
        {"t": 2, "song": "x", "accepted": False, "note": "wrong groove",
         "prompt": "another _taste_test take"},
        {"t": 3, "song": "x", "accepted": False, "note": "",
         "prompt": "_taste_test again"},
        {"t": 4, "song": "x", "accepted": True, "note": "",
         "prompt": "_taste_test yes"},
    ]
    tmp = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False)
    for r in rows:
        tmp.write(json.dumps(r) + "\n")
    tmp.close()
    old = ing.TELEMETRY
    ing.TELEMETRY = tmp.name
    try:
        ing.ingest()
    finally:
        ing.TELEMETRY = old
        os.unlink(tmp.name)
    got = kg.q("MATCH (g:Genre {name: '_taste_test'}) "
               "RETURN g.verdicts_n, g.accept_rate, g.complaints, g.last_whys")
    ok(bool(got), "scratch genre readable after ingest")
    if got:
        n, rate, comp, whys = got[0]
        ok(n == 4 and abs(float(rate) - 0.25) < 1e-6, f"verdicts 4 / rate 0.25 (got {n}/{rate})")
        ok(comp == "bright:1;groove:1", f"complaints bucketed + ranked (got '{comp}')")
        ok("too bright, lost the groove" in (whys or "") and "wrong groove" in (whys or ""),
           f"last_whys carries the raw words (got '{whys}')")
    # idempotence: second ingest of the same file = same numbers
    tmp2 = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False)
    for r in rows:
        tmp2.write(json.dumps(r) + "\n")
    tmp2.close()
    ing.TELEMETRY = tmp2.name
    try:
        ing.ingest()
    finally:
        ing.TELEMETRY = old
        os.unlink(tmp2.name)
    got2 = kg.q("MATCH (g:Genre {name: '_taste_test'}) RETURN g.verdicts_n, g.complaints")
    ok(got2 and got2[0][0] == 4 and got2[0][1] == "bright:1;groove:1", "ingest idempotent")
    # cleanup: the scratch genre + today's test snapshots never pollute the graph
    kg.g.query("MATCH (g:Genre {name: '_taste_test'}) DETACH DELETE g")
    ok(not kg.q("MATCH (g:Genre {name: '_taste_test'}) RETURN g.name"), "scratch genre scrubbed")

if __name__ == "__main__":
    main()
    for f in FAIL:
        print("FAIL:", f)
    print(f"kg-taste battery: {PASS}/{PASS + len(FAIL)} {'clean' if not FAIL else 'RED'}")
    sys.exit(1 if FAIL else 0)
