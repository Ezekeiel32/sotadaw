#!/usr/bin/env python3
"""Surge XT Effects factory presets -> loadable fx state blobs (the 291 rail).

  surgefx_presets.py extract <surge_src>   # parse surge source -> tools/surgefx_tables.json
  surgefx_presets.py index                 # 291 srgfx -> library.json vst_presets (fx)
  surgefx_presets.py get "<name>"          # srgfx -> blob + the fx entry to use
  surgefx_presets.py list [CAT]

THE CRACK (2026-07-03, from surge source): SurgefxAudioProcessor state =
VC2!+XML(<surgefx fxt=<type> fxp_N=<f01 float> surgevaltype_N=<2|0>
surgeval_N=<int>>) double-wrapped in the juce VST3 envelope. v2 loading reads
FLOATS from fxp_N as f01 (set_value_f01) and INTS from surgeval_N (only when
surgevaltype_N==0==vt_int; vt_float==2). .srgfx snapshots store INTERNAL val.f
naturals -> f01 = (v-min)/(max-min) with ranges from Parameter.cpp's set_type
switch. Param order: identity where posy_offset keeps i*2+offset monotonic
(true for the common effects; verified acoustically on Reverb2).
"""
import glob, json, os, re, struct, sys
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.expanduser("~/.local/share/surge-xt/fx_presets")
OUT = os.path.join(ROOT, "library", "presets", "surgefx")
TABLES = os.path.join(ROOT, "tools", "surgefx_tables.json")
LIB = os.path.join(ROOT, "library.json")
ALPHA = ".ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+"
N_FX_PARAMS = 12


def b64(d):
    bits = 0; nbits = 0; out = []
    for byte in d:
        bits |= byte << nbits; nbits += 8
        while nbits >= 6:
            out.append(ALPHA[bits & 0x3F]); bits >>= 6; nbits -= 6
    if nbits:
        out.append(ALPHA[bits & 0x3F])
    return f"{len(d)}." + "".join(out)


# ---------- extraction from surge source (run once, tables committed) ----------

def extract(src):
    # 1) fxt enum
    storage = open(os.path.join(src, "src/common/SurgeStorage.h")).read()
    em = re.search(r"enum fx_type\s*\{(.*?)\}", storage, re.S)
    fxt = {}
    n = 0
    for tok in em.group(1).split(","):
        tok = tok.strip().split("=")[0].strip()
        if tok.startswith("fxt_"):
            fxt[tok] = n; n += 1
    # 2) ctrltype ranges from Parameter.cpp's set_type switch
    pcpp = open(os.path.join(src, "src/common/Parameter.cpp")).read()
    ranges = {}
    for m in re.finditer(r"case (ct_\w+):", pcpp):
        ct = m.group(1)
        window = pcpp[m.end():m.end() + 700]
        stop = re.search(r"\bbreak;", window)
        w = window[:stop.start()] if stop else window
        vt = re.search(r"valtype = (vt_\w+)", w)
        mn = re.search(r"val_min\.f = ([-\d.e]+)", w)
        mx = re.search(r"val_max\.f = ([-\d.e]+)", w)
        mni = re.search(r"val_min\.i = ([-\d]+)", w)
        mxi = re.search(r"val_max\.i = ([-\d]+)", w)
        if ct not in ranges or vt:
            ranges[ct] = {"vt": vt.group(1) if vt else None,
                          "min": float(mn.group(1)) if mn else (float(mni.group(1)) if mni else None),
                          "max": float(mx.group(1)) if mx else (float(mxi.group(1)) if mxi else None)}
    # cascade: cases that fall through inherit the NEXT set block — leave gaps; fill common aliases
    # 3) per-effect param ctrltypes, in first-appearance order of p[SYMBOL].set_type
    effmap = {"DelayEffect": "fxt_delay", "Reverb1Effect": "fxt_reverb", "Reverb2Effect": "fxt_reverb2",
              "PhaserEffect": "fxt_phaser", "RotarySpeakerEffect": "fxt_rotaryspeaker",
              "DistortionEffect": "fxt_distortion", "ParametricEQ": "fxt_eq", "FrequencyShifterEffect": "fxt_freqshift",
              "ConditionerEffect": "fxt_conditioner", "ChorusEffect": "fxt_chorus4", "VocoderEffect": "fxt_vocoder",
              "FlangerEffect": "fxt_flanger", "RingModulatorEffect": "fxt_ringmod", "AirWindowsEffect": "fxt_airwindows",
              "NeuronEffect": "fxt_neuron", "GraphicEQ11BandEffect": "fxt_geq11", "ResonatorEffect": "fxt_resonator",
              "CombulatorEffect": "fxt_combulator", "NimbusEffect": "fxt_nimbus", "TapeEffect": "fxt_tape",
              "TreemonsterEffect": "fxt_treemonster", "WaveShaperEffect": "fxt_waveshaper",
              "MidSideToolEffect": "fxt_mstool", "SpringReverbEffect": "fxt_spring_reverb",
              "BonsaiEffect": "fxt_bonsai", "AudioInputEffect": "fxt_audio_input"}
    effects = {}
    edir = os.path.join(src, "src/common/dsp/effects")
    for f in glob.glob(f"{edir}/**/*.cpp", recursive=True) + glob.glob(f"{edir}/**/*Impl.h", recursive=True):
        body = open(f, errors="replace").read()
        cls = None
        for k in effmap:
            if k in os.path.basename(f):
                cls = k; break
        if cls is None or effmap[cls] not in fxt:
            continue
        im = re.search(r"::init_ctrltypes\(\)(.*?)\n\}", body, re.S)
        if not im:
            continue
        order = []
        seen = {}
        for pm in re.finditer(r"p\[(\w+)\]\.set_type\((ct_\w+)\)", im.group(1)):
            sym, ct = pm.group(1), pm.group(2)
            if sym not in seen:
                seen[sym] = len(order)
                order.append(ct)
            else:
                order[seen[sym]] = ct
        if order:
            effects[str(fxt[effmap[cls]])] = {"class": cls, "ctrltypes": order}
    json.dump({"fxt": fxt, "ranges": ranges, "effects": effects}, open(TABLES, "w"), indent=1)
    print(f"tables: {len(fxt)} fx types, {len(ranges)} ctrltypes, {len(effects)} effects mapped -> {TABLES}")


# ---------- synthesis ----------

TEMPLATE = ('<?xml version="1.0" encoding="UTF-8"?> <surgefx streamingVersion="2" {body} '
            'fxt="{fxt}" oscpin="53290" oscin="0"/>')


def natural_to_f01(v, ct, ranges):
    r = ranges.get(ct) or {}
    mn, mx = r.get("min"), r.get("max")
    if mn is None or mx is None or mx <= mn:
        if ct == "ct_percent": mn, mx = 0.0, 1.0
        elif ct == "ct_percent_bipolar": mn, mx = -1.0, 1.0
        else: return max(0.0, min(1.0, float(v)))
    return max(0.0, min(1.0, (float(v) - mn) / (mx - mn)))


def synth_state(srgfx_path, tables):
    snap = ET.parse(srgfx_path).getroot().find("snapshot")
    fxt = snap.get("type")
    eff = tables["effects"].get(fxt)
    parts = []
    for i in range(N_FX_PARAMS):
        pv = snap.get(f"p{i}")
        ct = (eff["ctrltypes"][i] if eff and i < len(eff["ctrltypes"]) else None)
        vt = tables["ranges"].get(ct, {}).get("vt") if ct else None
        deact = snap.get(f"p{i}_deactivated") == "1"
        if pv is None or ct is None:
            parts.append(f'fxp_{i}="0.0" surgevaltype_{i}="2" surgeval_{i}="0" fxp_param_features_{i}="0"')
            continue
        if vt in ("vt_int", "vt_bool"):
            parts.append(f'fxp_{i}="0.0" surgevaltype_{i}="0" surgeval_{i}="{int(float(pv))}" '
                         f'fxp_param_features_{i}="{4 if deact else 0}"')
        else:
            f01 = natural_to_f01(pv, ct, tables["ranges"])
            parts.append(f'fxp_{i}="{f01:.6f}" surgevaltype_{i}="2" surgeval_{i}="0" '
                         f'fxp_param_features_{i}="{4 if deact else 0}"')
    xml = TEMPLATE.format(body=" ".join(parts), fxt=fxt)
    inner = b"VC2!" + struct.pack("<I", len(xml.encode())) + xml.encode()
    outer = ('<?xml version="1.0" encoding="UTF-8"?> <VST3PluginState><IComponent>'
             + b64(inner) + "</IComponent></VST3PluginState>").encode()
    return b"VC2!" + struct.pack("<I", len(outer)) + outer


def scan():
    out = []
    for p in sorted(glob.glob(f"{DATA}/**/*.srgfx", recursive=True)):
        cat = os.path.relpath(p, DATA).split(os.sep)[0]
        out.append({"plugin": "Surge XT Effects", "name": os.path.splitext(os.path.basename(p))[0],
                    "category": cat, "path": p, "fx": True})
    return out


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
    if cmd == "extract":
        extract(sys.argv[2])
    elif cmd == "index":
        entries = scan()
        lib = json.load(open(LIB)) if os.path.exists(LIB) else {}
        others = [e for e in lib.get("vst_presets", []) if e.get("plugin") != "Surge XT Effects"]
        lib["vst_presets"] = others + entries
        json.dump(lib, open(LIB, "w"), indent=1)
        cats = {}
        for e in entries: cats[e["category"]] = cats.get(e["category"], 0) + 1
        print(f"indexed {len(entries)} Surge fx presets: {dict(sorted(cats.items(), key=lambda kv: -kv[1])[:8])}")
    elif cmd == "get":
        tables = json.load(open(TABLES))
        q = sys.argv[2].lower()
        for e in scan():
            if q in e["name"].lower():
                os.makedirs(OUT, exist_ok=True)
                safe = re.sub(r"[^A-Za-z0-9_ -]", "", e["name"])
                blob = os.path.join(OUT, f"{safe}.blob")
                open(blob, "wb").write(synth_state(e["path"], tables))
                print(json.dumps({"plugin": "Surge XT Effects", "name": e["name"],
                                  "category": e["category"],
                                  "use_as_fx": {"id": "vst3:Surge XT Effects",
                                                "preset": os.path.relpath(blob, ROOT)}}, indent=1))
                break
        else:
            raise SystemExit(f"no Surge fx preset matching {q!r}")
    else:
        cat = sys.argv[2].lower() if len(sys.argv) > 2 else None
        for e in scan():
            if cat is None or e["category"].lower() == cat:
                print(f'{e["category"]:16} {e["name"]}')
