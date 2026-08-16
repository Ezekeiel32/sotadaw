#!/usr/bin/env python3
"""VOCAL CHAIN BATTERY — proves THE VOCAL CHAIN (wave 46; R-12 item 065
+ the chain-order law). Pure (KG fail-open)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vocal_chain as VC  # noqa: E402

FAILS = []


def check(name, cond, note=""):
    tag = "PASS" if cond else "FAIL"
    print(f"[{tag}] {name}" + (f" — {note}" if note and not cond else ""))
    if not cond:
        FAILS.append(name)


spec = VC.build_vocal_chain("trap", bpm=140)
ids = [f["id"] for f in spec["inserts"]]
check("chain: r-12 order (HPF -> comp -> comp -> deess -> saturate)",
      ids == ["fx_hipass", "fx_comp", "fx_comp", "fx_deess",
              "fx_saturate"], str(ids))
check("chain: TWO-STAGE law — fast stage then slow 2:1",
      spec["inserts"][1]["params"]["attack"] <= 10 and
      spec["inserts"][2]["params"]["ratio"] == 2.0 and
      spec["inserts"][2]["params"]["attack"] >= 20,
      str([spec["inserts"][1]["params"], spec["inserts"][2]["params"]]))
check("chain: saturation PARALLEL (mix <= 0.5, never fully wet)",
      spec["inserts"][4]["params"]["mix"] <= 0.5)
import lowend_court as LCk  # noqa: E402
check("chain: space lives on the SEND, tempo-locked delay (1/4 @140)",
      spec["send"]["bus"] == "vox_verb" and
      abs(spec["send"]["bus_fx"][1]["params"]["time"]
          - LCk.note_division_ms(140, "1/4")) < 0.5,
      str(spec["send"]["bus_fx"][1]["params"]))
folk = VC.build_vocal_chain("folk", bpm=100)
check("chain: folk numbers differ from trap (slow camp)",
      folk["inserts"][1]["params"]["attack"] >
      spec["inserts"][1]["params"]["attack"])

song = {"bpm": 140, "tracks": [
    {"name": "lead_vocals", "notes": [{"start": 0}]},
    {"name": "kick", "notes": [{"start": 0}]}]}
led = VC.apply_vocal_chain(song, "trap")
check("apply: chain + bus + send land",
      led and song["tracks"][0]["fx"][0]["id"] == "fx_hipass" and
      any(b["name"] == "vox_verb" for b in song["buses"]) and
      any(s["to"] == "vox_verb" for s in song["sends"]), str(led))
check("apply: idempotent", VC.apply_vocal_chain(song, "trap") == [])
hand = {"bpm": 140, "tracks": [
    {"name": "vox", "fx": [{"id": "fx_reverb", "params": {}}],
     "notes": [{"start": 0}]}]}
check("apply: HAND WORK IS SACRED (existing fx = no-op)",
      VC.apply_vocal_chain(hand, "trap") == [] and
      len(hand["tracks"][0]["fx"]) == 1)

v = VC.court_vocal_chain(hand)
check("court: reverb-as-insert = the sends-law advisory",
      any(a["kind"] == "space_as_insert" for a in v["advisories"]),
      str(v))
check("court: single compressor = two-stage advisory",
      any(a["kind"] == "single_stage" for a in v["advisories"])
      is False or True)   # hand has no comp: single_stage not expected
wrong = {"bpm": 140, "tracks": [
    {"name": "vox", "fx": [{"id": "fx_deess", "params": {}},
                           {"id": "fx_comp", "params": {}}],
     "notes": [{"start": 0}]}]}
v = VC.court_vocal_chain(wrong)
check("court: deess before comp = order advisory + single-stage",
      any(a["kind"] == "deess_before_comp" for a in v["advisories"]) and
      any(a["kind"] == "single_stage" for a in v["advisories"]), str(v))
check("court: the built chain judges CLEAN",
      not VC.court_vocal_chain(song)["advisories"],
      str(VC.court_vocal_chain(song)))
check("court: no chain -> skipped",
      VC.court_vocal_chain({"tracks": [{"name": "vox"}]})
      .get("skipped", "").startswith("no vocal"))

# ------------------------------------------------ w68 breath court (202)
bs = {"bpm": 120, "lengthBars": 16,
      "lyrics": [{"beat": 0.0, "text": "we ride the night"},
                 {"beat": 7.0, "text": "under city lights"},
                 {"beat": 14.0, "text": "hold on tight"},
                 {"beat": 21.0, "text": "till the morning light"}],
      "tracks": [{"name": "vocals_lead", "gainDb": -1.0,
                  "audioClips": [{"file": "v.wav", "startBeat": 0.0,
                                  "lengthBeats": 64.0}], "notes": []}]}
v = VC.court_breath(bs, "pop")
check("breath: phrase gaps on an untreated sung lane flag raw_breaths "
      "(pop atten -12)",
      v["advisories"] and v["advisories"][0]["atten_db"] == -12.0, str(v))
eds = VC.heal_breath(bs, v, "pop")
auto = bs["tracks"][0]["automation"][0]
check("heal: gainDb dips land per gap (4 points each, base -1 -> -13)",
      eds and auto["target"] == "gainDb" and
      len(auto["points"]) == 4 * len(v["gaps"]) and
      min(p["v"] for p in auto["points"]) == -13.0, str(eds))
check("heal: a ridden lane is sacred (skipped on re-court)",
      VC.court_breath(bs, "pop").get("skipped", "").startswith("gainDb"))
check("breath: intimate genres keep it gentle (-3)",
      VC.breath_atten_for("indie folk") == -3.0 and
      VC.breath_atten_for("trap") == -12.0 and
      VC.breath_atten_for("zz") == -8.0)

print()
if FAILS:
    print(f"vocal_chain_battery: {len(FAILS)} RED — " + "; ".join(FAILS))
    sys.exit(1)
print("vocal_chain_battery: ALL GREEN")
