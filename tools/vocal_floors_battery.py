#!/usr/bin/env python3
"""VOCAL FLOORS BATTERY — proves wave 24 (item 012 accept-calibration +
content-recall; item 013 VocalTarget routing). Pure, no models."""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vocal_court as VC  # noqa: E402
import kg_seed_vocal as KV  # noqa: E402

FAILS = []


def check(name, cond, note=""):
    tag = "PASS" if cond else "FAIL"
    print(f"[{tag}] {name}" + (f" — {note}" if note and not cond else ""))
    if not cond:
        FAILS.append(name)


# ---------------------------------------------- calibration kernel (012)
recs = [{"lang": "en", "wer": w, "accepted": True}
        for w in (0.08, 0.12, 0.15, 0.18, 0.22, 0.25)]
f = VC.calibrate_floors(recs)
check("calibrate: 6 clean accepts tighten the en flag toward p75+0.05",
      "en" in f and 0.25 <= f["en"]["flag"] <= 0.30, str(f))
recs = [{"lang": "en", "wer": w, "accepted": True}
        for w in (0.40, 0.45, 0.48, 0.52)]
f = VC.calibrate_floors(recs)
check("calibrate: tolerant accepts loosen the flag but NEVER past red-0.05",
      f["en"]["flag"] <= VC.LANG_FLOORS["en"][1] - 0.05, str(f))
f = VC.calibrate_floors([{"lang": "en", "wer": 0.1, "accepted": True}] * 3)
check("calibrate: <4 accepts = no override (literature holds)",
      "en" not in f, str(f))
f = VC.calibrate_floors([{"lang": "en", "wer": 0.9, "accepted": False}] * 8)
check("calibrate: rejects never calibrate", "en" not in f)

# persisted floors round-trip, bounds enforced on read
old_path = VC.FLOORS_PATH
tmp = tempfile.mkdtemp(prefix="vf_")
VC.FLOORS_PATH = os.path.join(tmp, "vocal_floors.json")
json.dump({"en": {"flag": 0.28}}, open(VC.FLOORS_PATH, "w"))
check("calibrated_floors: persisted override read (0.28, red stays lit)",
      VC.calibrated_floors("en") == (0.28, 0.55))
json.dump({"en": {"flag": 0.9}}, open(VC.FLOORS_PATH, "w"))
check("calibrated_floors: insane override clamped under red-0.05",
      VC.calibrated_floors("en")[0] <= 0.5)
os.remove(VC.FLOORS_PATH)
check("calibrated_floors: no file = literature",
      VC.calibrated_floors("ru") == VC.LANG_FLOORS["ru"])
VC.FLOORS_PATH = old_path

# ------------------------------------------------ content recall (012)
intended = VC._norm_words("golden fire burning through the night sky")
heard = VC._norm_words("golden fire burnin threw the night sky")
r = VC.content_recall(intended, heard)
check("content_recall: near-miss transcript keeps meaning (>=0.7)",
      r is not None and r >= 0.7, str(r))
heard_bad = VC._norm_words("the a of in and")
check("content_recall: stopword soup recalls nothing",
      VC.content_recall(intended, heard_bad) == 0.0)
check("content_recall: stopword-only intent = None (no divide-by-zero)",
      VC.content_recall(VC._norm_words("the and of"), heard) is None)

# ------------------------------------------------ error taxonomy (127)
tax = VC.error_taxonomy(
    VC._norm_words("golden fire burning bright tonight"),
    VC._norm_words("olden hire burning brought tonight"))
check("taxonomy: consonant-onset misses lead (golden->olden, fire->hire)",
      tax["misses"]["consonant_onset"] >= 2, str(tax["misses"]))
check("taxonomy: vowel-center miss classified (bright->brought)",
      tax["misses"]["vowel_center"] >= 1, str(tax["misses"]))
check("taxonomy: the heal plan is ORDERED — consonants first, surgical "
      "re-render last",
      tax["heal_plan"][0].startswith("1) consonants") and
      "surgical" in tax["heal_plan"][-1], str(tax["heal_plan"]))
tax2 = VC.error_taxonomy(VC._norm_words("fire light"), 
                         VC._norm_words("fire light"))
check("taxonomy: perfect transcript = zero misses",
      sum(tax2["misses"].values()) == 0)

# --------------------------------------- integrated intelligibility (125)
i_hi = VC.intelligibility(0.4, 0.85, {"misses": {"consonant_onset": 3,
                                                 "vowel_center": 0,
                                                 "missing": 0}})
check("intelligibility: high recall + onset-only misses scores "
      "understood (>=0.62)", i_hi is not None and i_hi >= 0.62, str(i_hi))
i_lo = VC.intelligibility(0.5, 0.35, {"misses": {"consonant_onset": 0,
                                                 "vowel_center": 0,
                                                 "missing": 5}})
check("intelligibility: low recall + MISSING words scores lost (<0.5)",
      i_lo is not None and i_lo < 0.5, str(i_lo))
check("intelligibility: onset slips cost less than missing words "
      "(the r-11 75% law)",
      VC.intelligibility(0.4, 0.6, {"misses": {"consonant_onset": 4,
                                               "vowel_center": 0,
                                               "missing": 0}})
      > VC.intelligibility(0.4, 0.6, {"misses": {"consonant_onset": 0,
                                                 "vowel_center": 0,
                                                 "missing": 4}}))
check("intelligibility: None recall = None (no fake score)",
      VC.intelligibility(0.4, None) is None)
check("intelligibility: no taxonomy = neutral error quality",
      abs(VC.intelligibility(0.2, 0.9) -
          (0.5 * 0.9 + 0.35 * 0.8 + 0.15)) < 1e-9)

# --------------------------------------------- w67: the two guards (200)
src_vc = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "vocal_court.py")).read()
check("prompt-cheat guard (STRUCTURAL): transcribe never feeds "
      "initial_prompt/reference lyrics into the decode",
      "initial_prompt=" not in src_vc)

# --------------------------------------------- w67: phoneme coverage (195)
import sing_lang as SL
try:
    inv = SL.bank_inventory()
    have_bank = bool(inv)
except Exception:
    have_bank = False
if have_bank:
    ns = sorted(inv)[0]
    good = list(sorted(inv[ns]))[:4]
    v = SL.court_phoneme_coverage(good, ns)
    check("coverage: bank-known phonemes pass", v["ok"], str(v))
    v2 = SL.court_phoneme_coverage(good + ["qqx", "zzq"], ns)
    check("coverage: alien phonemes convict BEFORE the vocoder",
          not v2["ok"] and "qqx" in v2["missing"], str(v2))
    check("coverage: SP/AP breath tokens never convict",
          SL.court_phoneme_coverage(["SP", "AP"] + good, ns)["ok"])
else:
    print("[skip] coverage checks (no voicebank on this box)")

# ------------------------------------------------ VocalTarget routing (013)
check("route: drill/reggaeton -> trap family (hard-tune camp)",
      KV.preset_for("uk drill") == "trap" and
      KV.preset_for("reggaeton") == "trap")
check("route: soul -> gospel family (slow comp, hall, stacks)",
      KV.preset_for("northern soul") == "gospel")
check("route: unknown genre -> pop default", KV.preset_for("zzz") == "pop")
p = KV.PRESETS["trap"]
check("preset law: trap = fast comp camp (attack<=10ms, ratio>=4)",
      p["comp_attack_ms"] <= 10 and p["comp_ratio"] >= 4)
p = KV.PRESETS["folk"]
check("preset law: folk = slow camp + transparent tune + dry",
      p["comp_attack_ms"] >= 20 and p["tune_style"] == "transparent" and
      p["reverb_decay_s"] <= 1.5)
check("preset law: saturation is PARALLEL everywhere (mix<=0.5, "
      "never fully wet)",
      all(v["sat_mix"] <= 0.5 for v in KV.PRESETS.values()))
check("preset law: doubles sit -3..-10 under the lead",
      all(-10 <= v["double_level_db"] <= -3 for v in KV.PRESETS.values()))
check("preset law: ad-libs capped at 3 per section (more = mud)",
      all(v["adlib_per_section"] <= 3 for v in KV.PRESETS.values()))

print()
if FAILS:
    print(f"vocal_floors_battery: {len(FAILS)} RED — " + "; ".join(FAILS))
    sys.exit(1)
print("vocal_floors_battery: ALL GREEN")
