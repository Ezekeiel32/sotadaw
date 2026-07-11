#!/usr/bin/env python3
"""VOICEBANK REGISTRY battery (BEST_DAW_30 #30) — banks are manifests, not hardcodes.

Proves: manifest truth on the real bank, per-call + env bank resolution, a
drop-in second bank appears in the registry, and THE LICENSE GATE flips
public_ok on a commercial-clean bank. Pure/local. Run: python3 tools/voicebank_battery.py
"""
import json, os, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import sing
import release_pack as RP

FAKE = os.path.join(ROOT, "library", "voices", "_fakebank")
fails = []


def check(tag, ok, detail=""):
    print(f"  {'ok' if ok else 'XX'} {tag} {detail}")
    if not ok:
        fails.append(tag)


def main():
    m = sing.manifest()
    check("real bank manifest truth",
          m["attribution"] == "Gahata Meiji from LUNAI Project"
          and m["license"]["commercial"] is False, m.get("display", "?"))
    a = sing.assets()
    check("manifest assets map to bank paths",
          all(p.startswith(sing.BANK) for p in a.values())
          and set(a) >= {"acoustic", "vocoder", "dsdict_en"})

    os.makedirs(FAKE, exist_ok=True)
    json.dump({"name": "_fakebank", "display": "Test Voice X (clean)",
               "attribution": "Test Voice X", "engine": "diffsinger",
               "license": {"commercial": True, "attribution_required": False,
                           "terms": "test bank: commercial OK"},
               "assets": {"acoustic": "files/a.onnx"}},
              open(os.path.join(FAKE, "bank.json"), "w"))
    try:
        check("per-call bank resolution",
              sing.attribution(bank=FAKE) == "Test Voice X")
        check("registry lists the drop-in", "_fakebank" in sing.list_banks())
        r = subprocess.run([sys.executable, "-c",
                            "import sys; sys.path.insert(0, 'tools'); import sing; "
                            "print(sing.BANK); print(sing.attribution())"],
                           capture_output=True, text=True, cwd=ROOT,
                           env={**os.environ, "SOTADAW_VOICE_BANK": "_fakebank"})
        lines = r.stdout.strip().splitlines()
        check("env switches the ACTIVE bank",
              len(lines) == 2 and lines[0].endswith("_fakebank")
              and lines[1] == "Test Voice X", str(lines))
        rights = RP.voice_rights()
        check("license gate registry carries the manifest",
              rights.get("test voice x", {}).get("commercial") is True,
              str(rights.get("test voice x")))
        rows, ok_pub = RP.license_gate({"tracks": [
            {"name": "vocals", "comment": "voice: Test Voice X"}]})
        check("commercial-clean voice -> PUBLIC OK", ok_pub and rows[0]["public_ok"])
        rows2, ok2 = RP.license_gate({"tracks": [
            {"name": "vocals", "comment": "voice: Gahata Meiji from LUNAI Project"}]})
        check("NC voice still blocks public", not ok2 and not rows2[0]["public_ok"])
    finally:
        shutil.rmtree(FAKE, ignore_errors=True)
    check("cleanup: fake bank gone", "_fakebank" not in sing.list_banks())
    print(f"voicebank battery: {'clean' if not fails else 'RED ' + str(fails)}")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
