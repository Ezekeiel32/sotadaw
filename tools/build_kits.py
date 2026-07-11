#!/usr/bin/env python3
"""Build sample kits from a GM SoundFont via sf2_extract.
Produces kits/<name>/{*.wav, kit.json}. kit.json:
{ "name": ..., "samples": [ {"file","keyNote","minNote","maxNote","gainDb"} ] }
Drum kits: one sample per key (min=max=key). Pitched kits: multisampled roots with ranges
(the engine sampler repitches within [minNote,maxNote] relative to keyNote)."""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KITS = os.path.join(ROOT, "kits")
EXTRACT = os.path.join(ROOT, "tools", "sf2_extract")

SF_CANDIDATES = [
    "/tmp/claude-1000/-home-chezy-AI-SOTA-DAW/7a399a82-f024-4e63-ac18-b6fdf461d10a/scratchpad/content/GeneralUser.sf2",
    "/usr/share/sounds/sf2/default-GM.sf2",
    "/usr/share/sounds/sf2/TimGM6mb.sf2",
]
SF = next((p for p in SF_CANDIDATES if os.path.exists(p)), None)
if not SF:
    sys.exit("no soundfont found")
print("soundfont:", SF)

GM_DRUMS = {  # key: (name, holdS, maxS)
    36: ("kick", 0.05, 1.5), 37: ("rim", 0.05, 1.0), 38: ("snare", 0.05, 1.5),
    39: ("clap", 0.05, 1.5), 40: ("snare2", 0.05, 1.5), 42: ("hat_closed", 0.03, 0.8),
    44: ("hat_pedal", 0.03, 0.8), 46: ("hat_open", 0.05, 2.0), 49: ("crash", 0.05, 3.5),
    51: ("ride", 0.05, 3.0), 53: ("ride_bell", 0.05, 2.5), 54: ("tamb", 0.05, 1.2),
    43: ("tom_lo", 0.05, 1.5), 47: ("tom_mid", 0.05, 1.5), 50: ("tom_hi", 0.05, 1.5),
    56: ("cowbell", 0.05, 1.0), 69: ("cabasa", 0.05, 0.8), 70: ("maracas", 0.05, 0.8),
    75: ("clave", 0.05, 0.8), 81: ("triangle", 0.05, 2.0),
}

PITCHED = {
    # kitname: (bank, preset, roots(list of MIDI), holdS, maxS)
    "piano":     (0, 0,  list(range(24, 97, 6)), 2.0, 4.0),
    "epiano":    (0, 4,  list(range(36, 97, 6)), 2.0, 4.0),
    "strings":   (0, 48, list(range(36, 85, 6)), 2.5, 5.0),
    "warmpad":   (0, 89, list(range(36, 85, 6)), 2.5, 5.0),
    "pluckbass": (0, 33, list(range(24, 61, 6)), 1.0, 2.5),
    "choir":     (0, 52, list(range(48, 85, 6)), 2.5, 5.0),
}

def run_extract(bank, preset, key, vel, hold, mx, out):
    r = subprocess.run([EXTRACT, SF, str(bank), str(preset), str(key), str(vel),
                        str(hold), str(mx), out], capture_output=True, text=True)
    if r.returncode != 0:
        print("  FAIL", out, r.stderr.strip()[:120])
        return False
    return True

def kit_dir(name):
    d = os.path.join(KITS, name)
    os.makedirs(d, exist_ok=True)
    return d

# --- drums ---
d = kit_dir("gm_drums")
samples = []
for key, (name, hold, mx) in sorted(GM_DRUMS.items()):
    fn = f"{key}_{name}.wav"
    if run_extract(128, 0, key, 110, hold, mx, os.path.join(d, fn)):
        samples.append({"file": fn, "keyNote": key, "minNote": key, "maxNote": key, "gainDb": 0.0})
json.dump({"name": "gm_drums", "kind": "drums", "samples": samples},
          open(os.path.join(d, "kit.json"), "w"), indent=1)
print(f"gm_drums: {len(samples)} pieces")

# --- pitched multisamples ---
for kit, (bank, preset, roots, hold, mx) in PITCHED.items():
    d = kit_dir(kit)
    samples = []
    for i, root in enumerate(roots):
        lo = root - 3 if i > 0 else 0
        hi = root + 2 if i < len(roots) - 1 else 127
        fn = f"{root}.wav"
        if run_extract(bank, preset, root, 100, hold, mx, os.path.join(d, fn)):
            samples.append({"file": fn, "keyNote": root, "minNote": lo, "maxNote": hi, "gainDb": 0.0})
    json.dump({"name": kit, "kind": "pitched", "samples": samples},
              open(os.path.join(d, "kit.json"), "w"), indent=1)
    print(f"{kit}: {len(samples)} multisamples")
print("kits ->", KITS)
