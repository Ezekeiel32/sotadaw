#!/usr/bin/env python3
"""Index the user's musical world into library.json: their sample folders, our kits,
Faust instruments, FX, and scanned VST3s — one searchable catalog for UI + agent.

  index_library.py [extra_dirs...]        rebuild library.json
Default scan roots: ~/Music, ~/Samples, ~/Downloads/samples (if they exist) + kits/.
"""
import json, os, re, struct, sys, wave

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "library.json")

def wav_seconds(path):
    try:
        with wave.open(path, "rb") as w:
            return round(w.getnframes() / max(1, w.getframerate()), 3)
    except Exception:
        return None

def tags_from_path(path):
    words = re.split(r"[\\/_\-\s.()\[\]]+", path.lower())
    vocab = {"kick", "snare", "clap", "hat", "hihat", "open", "closed", "perc", "shaker", "crash",
             "ride", "tom", "808", "bass", "sub", "loop", "oneshot", "one", "shot", "vocal", "vox",
             "fx", "riser", "impact", "piano", "keys", "pad", "lead", "pluck", "bell", "string",
             "brass", "guitar", "trap", "drill", "house", "techno", "dnb", "lofi", "ambient", "dark"}
    return sorted(set(w for w in words if w in vocab))

def scan_samples(roots):
    out = []
    for root in roots:
        root = os.path.expanduser(root)
        if not os.path.isdir(root):
            continue
        for dirpath, _, files in os.walk(root):
            if any(part.startswith(".") for part in dirpath.split(os.sep)):
                continue
            for f in files:
                if f.lower().endswith((".wav", ".aif", ".aiff", ".flac", ".mp3", ".ogg")):
                    p = os.path.join(dirpath, f)
                    entry = {"path": p, "name": os.path.splitext(f)[0],
                             "tags": tags_from_path(p)}
                    if f.lower().endswith(".wav"):
                        d = wav_seconds(p)
                        if d: entry["seconds"] = d
                    out.append(entry)
                    if len(out) >= 20000:
                        return out
    return out

def build(extra):
    kits = {}
    kdir = os.path.join(ROOT, "kits")
    if os.path.isdir(kdir):
        for k in sorted(os.listdir(kdir)):
            kj = os.path.join(kdir, k, "kit.json")
            if os.path.exists(kj):
                d = json.load(open(kj))
                kits[k] = {"kind": d.get("kind", "?"), "pieces": len(d.get("samples", []))}
    instruments = sorted(f[:-4] for f in os.listdir(os.path.join(ROOT, "instruments")) if f.endswith(".dsp"))
    vsts = []
    pc = os.path.join(ROOT, "app", "plugins_cache.xml")
    if os.path.exists(pc):
        vsts = sorted(set(re.findall(r'name="([^"]+)"', open(pc).read())))
    roots = ["~/Music", "~/Samples", "~/Downloads/samples"] + list(extra)
    samples = scan_samples(roots)
    # THE NAM RAIL (V51): .nam amp/pedal captures are session objects — index them.
    # Scan library/nam + the user's roots + the vendored starter captures.
    nam_captures = []
    nam_roots = [os.path.join(ROOT, "library", "nam"),
                 os.path.join(ROOT, "app", "third_party", "nam-core", "example_models")] \
        + [os.path.expanduser(r) for r in roots]
    seen = set()
    for nr in nam_roots:
        if not os.path.isdir(nr):
            continue
        for dirpath, _, files in os.walk(nr):
            for f in sorted(files):
                if f.lower().endswith(".nam"):
                    p = os.path.join(dirpath, f)
                    if p in seen:
                        continue
                    seen.add(p)
                    nam_captures.append({"name": f[:-4],
                                         "path": os.path.relpath(p, ROOT) if p.startswith(ROOT) else p,
                                         "kind": "nam_capture"})
            if len(nam_captures) >= 2000:
                break
    # CLAP HOSTING (V50): .clap plugins are session inserts — index them.
    clap_plugins = []
    clap_roots = [os.path.join(ROOT, "library", "clap"),
                  os.path.expanduser("~/.clap"), "/usr/lib/clap", "/usr/local/lib/clap"] \
        + [os.path.expanduser(r) for r in roots]
    cseen = set()
    for cr in clap_roots:
        if not os.path.isdir(cr):
            continue
        for dirpath, _, files in os.walk(cr):
            for f in sorted(files):
                if f.lower().endswith(".clap"):
                    p = os.path.join(dirpath, f)
                    if p in cseen:
                        continue
                    cseen.add(p)
                    clap_plugins.append({"name": f[:-5],
                                         "path": os.path.relpath(p, ROOT) if p.startswith(ROOT) else p,
                                         "kind": "clap"})
            if len(clap_plugins) >= 2000:
                break
    lib = {"samples": samples, "kits": kits,
           "instruments": [i for i in instruments if not i.startswith("fx_") and i != "master_limiter"],
           "fx": [i for i in instruments if i.startswith("fx_") or i == "master_limiter"],
           "vst3": vsts, "nam_captures": nam_captures, "clap_plugins": clap_plugins,
           "scanned_roots": [os.path.expanduser(r) for r in roots]}
    # rails other tools own (vst_presets from the preset scripts, dj_tracks from
    # rekordbox_import, ...) must survive a rescan — carry forward unknown keys
    if os.path.exists(OUT):
        try:
            for k, v in json.load(open(OUT)).items():
                if k not in lib:
                    lib[k] = v
        except Exception:
            pass
    json.dump(lib, open(OUT, "w"), indent=1)
    return lib

if __name__ == "__main__":
    lib = build(sys.argv[1:])
    print(f"library.json: {len(lib['samples'])} samples, {len(lib['kits'])} kits, "
          f"{len(lib['instruments'])} instruments, {len(lib['fx'])} fx, {len(lib['vst3'])} vst3, "
          f"{len(lib.get('nam_captures', []))} nam captures, {len(lib.get('clap_plugins', []))} clap")
