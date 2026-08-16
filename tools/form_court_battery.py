#!/usr/bin/env python3
"""FORM COURT BATTERY — proves the form-conformance + signature courts
(wave 44; items 151/156/149). Pure (signature tokens monkeypatched —
the KG path is exercised by the wolf, not the battery)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import form_court as FC  # noqa: E402

FAILS = []


def check(name, cond, note=""):
    tag = "PASS" if cond else "FAIL"
    print(f"[{tag}] {name}" + (f" — {note}" if note and not cond else ""))
    if not cond:
        FAILS.append(name)


def song_with(names):
    return {"sections": [{"name": n, "startBar": i * 4}
                         for i, n in enumerate(names)],
            "tracks": [{"name": "kick", "notes": [{"start": 0}]}]}


v = FC.court_form_conformance(
    song_with(["intro", "verse", "chorus", "verse 2", "chorus 2",
               "bridge", "chorus 3", "outro"]), "pop")
check("form: canonical pop flow reads high similarity, no advisory",
      v["similarity"] >= 0.6 and not v["advisories"], str(v))
v = FC.court_form_conformance(
    song_with(["drop", "drop 2", "drop 3"]), "pop")
check("form: drop-only 'pop' = off-family advisory",
      v["advisories"] and v["advisories"][0]["kind"] == "off_family_form",
      str(v))
check("form: <3 sections skipped",
      FC.court_form_conformance(song_with(["intro", "verse"]), "pop")
      .get("skipped", "").startswith("needs"))
check("form: class mapper (drop=hook, stopdown=quiet, part=verse)",
      FC._sec_class("drop 2") == "hook" and
      FC._sec_class("stopdown") == "quiet" and
      FC._sec_class("part 3") == "verse")

# signature court with a controlled vocabulary
orig = FC.signature_tokens
FC.signature_tokens = lambda g: {"log_drum", "organ"}
s = {"tracks": [{"name": "log drum", "source": {"id": "log_drum_lead"}},
                {"name": "kick", "source": {"id": "kick_punch"}}]}
v = FC.court_signature(s, "amapiano")
check("signature: log_drum present -> clean + listed",
      not v["advisories"] and "log_drum" in v["present"], str(v))
s2 = {"tracks": [{"name": "kick", "source": {"id": "kick_punch"}},
                 {"name": "pad", "source": {"id": "pad_motion"}}]}
v = FC.court_signature(s2, "amapiano")
check("signature: no signature voice = advisory carrying the list",
      v["ok"] and v["advisories"] and
      v["advisories"][0]["kind"] == "no_signature_voice" and
      "log_drum" in v["advisories"][0]["expected"], str(v))
s3 = {"tracks": [{"name": "loudness police", "source": {"id": "x"}}]}
v = FC.court_signature(s3, "grime")
FC.signature_tokens = lambda g: {"oud"}
v = FC.court_signature(s3, "grime")
check("signature: 'oud' never matches inside 'loudness' (boundary law)",
      v["advisories"] and "oud" in v["advisories"][0]["expected"], str(v))
FC.signature_tokens = orig
check("signature: unbanked genre skipped",
      FC.court_signature(s3, "zzz_nogenre").get("skipped", "")
      .startswith("no signature"))

# ------------------------------------------------ 207 outro (w64)
lo = {"lengthBars": 40, "sections": [{"name": "verse", "startBar": 0},
                                     {"name": "outro", "startBar": 24}],
      "tracks": []}
v = FC.court_outro(lo, "pop")
check("outro: a 16-bar pop outro flags long_outro",
      any(a["kind"] == "long_outro" for a in v["advisories"]), str(v))
check("outro: 4-8 bars = the streaming shape (silent)",
      not FC.court_outro({"lengthBars": 28, "sections": [
          {"name": "verse", "startBar": 0},
          {"name": "outro", "startBar": 24}], "tracks": []},
          "pop")["advisories"])
check("outro: DJ genres keep their 32-bar mix-outs (exempt)",
      FC.court_outro(lo, "deep house").get("skipped", "").startswith("DJ"))

# ------------------------------------------------ 246 the ritual (w88)
def _bn(bar, n=4):
    return [{"start": bar * 4 + i, "len": 0.5, "pitch": 36, "vel": 96}
            for i in range(n)]
static = {"bpm": 140, "lengthBars": 16, "tracks": [
    {"name": "kick", "notes": sum([_bn(b) for b in range(16)], [])}]}
check("ritual(246): 16 identical bars = the loop tell (static_blocks)",
      any(a["kind"] == "static_blocks"
          for a in FC.court_ritual(static, "trap")["advisories"]))
varied = {"bpm": 140, "lengthBars": 16, "tracks": [
    {"name": "kick", "notes": sum(
        [_bn(b, n=4 if (b // 4) % 2 == 0 else 3) for b in range(16)],
        [])}]}
check("ritual: the Boi-1da rule satisfied (per-4-bar change) passes",
      not FC.court_ritual(varied, "trap")["advisories"])
li = {"bpm": 140, "lengthBars": 32,
      "sections": [{"name": "intro", "startBar": 0},
                   {"name": "hook", "startBar": 12}],
      "tracks": [{"name": "kick", "notes": sum(
          [_bn(b, n=4 if b % 4 else 3) for b in range(32)], [])}]}
check("ritual: a 12-bar rap intro breaches the 4-8 tag slot",
      any(a["kind"] == "long_intro"
          for a in FC.court_ritual(li, "trap")["advisories"]))

print()
if FAILS:
    print(f"form_court_battery: {len(FAILS)} RED — " + "; ".join(FAILS))
    sys.exit(1)
print("form_court_battery: ALL GREEN")
