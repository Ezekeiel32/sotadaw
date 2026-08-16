#!/usr/bin/env python3
"""THE VOICEBANK REGISTRY — wave 73 (r-9 item 196): quality banks are
mostly NON-COMMERCIAL and non-redistributable, so they are USER-FETCH
by law. The registry is the catalog + THE LICENSE GATE:

  list                     what exists, licenses up front
  gate <id>                prints the license terms and REFUSES install
                           guidance until --accept-license names the id
  installed                banks on disk vs their registry records
  verify                   every installed bank has a registry record
                           (or a local license file) + the commercial
                           flag matches attribution_court's law

No network here — fetching is the user's act (the ZERO-BUNDLE law);
this tool makes the legal state machine-checkable before and after.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REG = os.path.join(ROOT, "library", "voicebank_registry.json")
VOICES = os.path.join(ROOT, "library", "voices")


def load():
    return json.load(open(REG))


def bank(bid):
    return next((b for b in load()["banks"] if b["id"] == bid), None)


def gate(bid, accepted=False):
    b = bank(bid)
    if b is None:
        return {"ok": False, "why": f"unknown bank '{bid}'"}
    if not accepted:
        return {"ok": False, "gate": "license",
                "license": b["license"],
                "attribution_required": b["attribution_required"],
                "commercial_ok": b["commercial_ok"],
                "why": (f"'{b['name']}' is {b['license']} — rerun with "
                        "--accept-license to confirm you accept the "
                        "terms; attribution "
                        f"'{b['attribution_required']}' will ride every "
                        "export's C2PA manifest")}
    return {"ok": True, "bank": b,
            "next": (f"fetch from {b['home']} into library/voices/"
                     f"{b['id']}/ — the license gate is recorded; "
                     "attribution_court stamps every export")}


def installed():
    out = []
    if not os.path.isdir(VOICES):
        return out
    for d in sorted(os.listdir(VOICES)):
        p = os.path.join(VOICES, d)
        if not os.path.isdir(p):
            continue
        files = {f.lower() for f in os.listdir(p)}
        out.append({"id": d, "registered": bank(d) is not None,
                    "has_license_file": any("license" in f or "terms" in f
                                            for f in files)})
    return out


def verify():
    fails = []
    for b in installed():
        if not (b["registered"] or b["has_license_file"]):
            fails.append(f"bank '{b['id']}' has neither a registry "
                         "record nor a local license file")
    for b in load()["banks"]:
        if b.get("commercial_ok") is False and \
                not b.get("attribution_required"):
            fails.append(f"registry '{b['id']}': non-commercial without "
                         "an attribution string")
    for f in fails:
        print(f"[FAIL] {f}")
    if not fails:
        print(f"[PASS] {len(installed())} installed bank(s) licensed + "
              f"{len(load()['banks'])} registry records sound")
    return 1 if fails else 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
    if cmd == "list":
        for b in load()["banks"]:
            mark = "$" if b["commercial_ok"] else "NC"
            print(f"  [{mark:>2}] {b['id']:<22} {b['license']}")
    elif cmd == "gate":
        print(json.dumps(gate(sys.argv[2],
                               "--accept-license" in sys.argv), indent=1))
    elif cmd == "installed":
        print(json.dumps(installed(), indent=1))
    elif cmd == "verify":
        sys.exit(verify())
