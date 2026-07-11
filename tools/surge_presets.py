#!/usr/bin/env python3
"""Surge XT factory patches -> loadable preset blobs (VST-universe rail #3).

  surge_presets.py index          # scan ~/.local/share/surge-xt -> library.json vst_presets
  surge_presets.py get "<name>"   # wrap the .fxp -> library/presets/surge/<name>.blob,
                                  # print the source.preset line to use
  surge_presets.py list [CAT]

THE DISCOVERY (2026-07-03): Surge XT's VST3 state = 'VC2!' + len + XML envelope
<VST3PluginState><IComponent>juce-base64(sub3 stream)</IComponent>... — and a
.fxp's chunk (after its 60-byte header) IS a sub3 stream. Wrapping any factory
.fxp in that envelope makes it a loadable source.preset blob. Verified: bass
'Attacky' 0ms/144Hz/-6dB vs pad 89ms/9370Hz — category-true.
"""
import glob, json, os, re, struct, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.expanduser("~/.local/share/surge-xt")
OUT = os.path.join(ROOT, "library", "presets", "surge")
LIB = os.path.join(ROOT, "library.json")
ALPHA = ".ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+"


def juce_b64(data):
    bits = 0; nbits = 0; out = []
    for byte in data:
        bits |= byte << nbits
        nbits += 8
        while nbits >= 6:
            out.append(ALPHA[bits & 0x3F]); bits >>= 6; nbits -= 6
    if nbits:
        out.append(ALPHA[bits & 0x3F])
    return f"{len(data)}." + "".join(out)


def wrap_fxp(fxp_path):
    chunk = open(fxp_path, "rb").read()[60:]        # strip VST2 fxp header
    xml = ('<?xml version="1.0" encoding="UTF-8"?> <VST3PluginState><IComponent>'
           + juce_b64(chunk) + "</IComponent></VST3PluginState>")
    body = xml.encode()
    return b"VC2!" + struct.pack("<I", len(body)) + body


def scan():
    out = []
    for bank in ("patches_factory", "patches_3rdparty"):
        for p in sorted(glob.glob(f"{DATA}/{bank}/**/*.fxp", recursive=True)):
            rel = os.path.relpath(p, f"{DATA}/{bank}")
            cat = rel.split(os.sep)[0]
            out.append({"plugin": "Surge XT", "name": os.path.splitext(os.path.basename(p))[0],
                        "category": cat, "path": p,
                        "bank": "factory" if bank.endswith("factory") else "3rdparty"})
    return out


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
    if cmd == "index":
        entries = scan()
        lib = json.load(open(LIB)) if os.path.exists(LIB) else {}
        others = [e for e in lib.get("vst_presets", []) if e.get("plugin") != "Surge XT"]
        lib["vst_presets"] = others + entries
        json.dump(lib, open(LIB, "w"), indent=1)
        cats = {}
        for e in entries: cats[e["category"]] = cats.get(e["category"], 0) + 1
        top = dict(sorted(cats.items(), key=lambda kv: -kv[1])[:10])
        print(f"indexed {len(entries)} Surge patches -> library.json vst_presets; top cats: {top}")
    elif cmd == "get":
        q = sys.argv[2].lower()
        for e in scan():
            if q in e["name"].lower():
                os.makedirs(OUT, exist_ok=True)
                safe = re.sub(r"[^A-Za-z0-9_ -]", "", e["name"])
                blob = os.path.join(OUT, f"{safe}.blob")
                open(blob, "wb").write(wrap_fxp(e["path"]))
                print(json.dumps({"plugin": "Surge XT", "name": e["name"],
                                  "category": e["category"],
                                  "preset": os.path.relpath(blob, ROOT),
                                  "use": {"kind": "vst3", "plugin": "Surge XT",
                                          "preset": os.path.relpath(blob, ROOT)}}, indent=1))
                break
        else:
            raise SystemExit(f"no Surge patch matching {q!r}")
    else:
        cat = sys.argv[2].lower() if len(sys.argv) > 2 else None
        for e in scan():
            if cat is None or e["category"].lower() == cat:
                print(f'{e["category"]:16} {e["name"]}')
