#!/usr/bin/env python3
"""TAL-NoiseMaker factory presets -> playable source.params (the VST-universe
preset rail, first ecosystem).

  tal_presets.py index          # scan ~/.toguaudioline -> library.json vst_presets
  tal_presets.py get "<name>"   # print the params dict for one preset (agent inlines it)
  tal_presets.py list [CAT]     # names by category

The preset XML stores params as NAMED attributes (cutoff, filterattack, ...);
SongLoader matches them to plugin parameters by normalized name ("filterattack"
== "Filter Attack") — verified acoustically: PAD preset renders 448ms attack /
779Hz centroid, BASS 10ms / 338Hz. 256 factory presets across 8 categories."""
import json, os, sys, glob
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.expanduser("~/.toguaudioline/TAL-NoiseMaker/presets")
LIB = os.path.join(ROOT, "library.json")
SKIP_ATTRS = {"programname", "unknown", "curprogram", "version", "path", "presetName"}


def parse_preset(path):
    prog = ET.parse(path).getroot().find("programs/program")
    return {k: float(v) for k, v in prog.attrib.items() if k not in SKIP_ATTRS}


def scan():
    out = []
    for p in sorted(glob.glob(f"{BASE}/**/*.noisemakerpreset", recursive=True)):
        rel = os.path.relpath(p, BASE)
        parts = rel.split(os.sep)
        cat = parts[1] if len(parts) >= 3 else "misc"   # Factory Presets/<CAT>/name
        name = os.path.splitext(os.path.basename(p))[0]
        out.append({"plugin": "TAL-NoiseMaker", "name": name, "category": cat, "path": p})
    return out


def cmd_index():
    entries = scan()
    lib = json.load(open(LIB)) if os.path.exists(LIB) else {}
    others = [e for e in lib.get("vst_presets", []) if e.get("plugin") != "TAL-NoiseMaker"]
    lib["vst_presets"] = others + entries
    json.dump(lib, open(LIB, "w"), indent=1)
    cats = {}
    for e in entries:
        cats[e["category"]] = cats.get(e["category"], 0) + 1
    print(f"indexed {len(entries)} TAL presets -> library.json vst_presets: {cats}")


def cmd_get(name):
    for e in scan():
        if name.lower() in e["name"].lower():
            print(json.dumps({"plugin": e["plugin"], "name": e["name"],
                              "category": e["category"],
                              "params": parse_preset(e["path"])}, indent=1))
            return
    raise SystemExit(f"no TAL preset matching '{name}'")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
    if cmd == "index":
        cmd_index()
    elif cmd == "get":
        cmd_get(sys.argv[2])
    else:
        cat = sys.argv[2].upper() if len(sys.argv) > 2 else None
        for e in scan():
            if cat is None or e["category"].upper() == cat:
                print(f'{e["category"]:6} {e["name"]}')
