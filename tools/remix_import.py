#!/usr/bin/env python3
"""THE FULL FLIP — an original track that grooves like, and harmonizes with,
an absorbed song. The composition of every understanding lane:

  remix_import.py <import_song> <genre> [--out name] [--seed N] [--bars N]

  1. read the import's DNA: bpm, key, chord cycle (voted), learned groove
  2. loop_gen: a fresh <genre> loop AT the import's bpm and key
  3. reharm: retune the new loop TO the import's chord cycle (role-mapped,
     minimal motion)
  4. groove: the import's own timing DNA applied to the new loop's hats/snare
  5. verify: chordvote(new) must read the import's cycle; render must be clean

Result: not a copy — a new track in a new genre that FITS the absorbed song
(mix them, bridge them, layer them). Machine line: REMIX_JSON {...}
"""
import argparse, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import loop_gen
import groove as groove_mod
from chordvote import chord_map
from reharm import reharm, detect_cycle
import songname

SEC2ARRANGE = {"intro": "intro", "verse": "build", "hook": "drop", "drop": "drop",
               "chorus": "drop", "break": "break", "bridge": "break",
               "build": "build", "part": "build", "outro": "outro", "start": "intro"}


def structure_of(imp):
    """The import's own section shape as an arrange() form: (class, bars) pairs."""
    secs = imp.get("sections", [])
    if len(secs) < 2:
        return None
    total = float(imp.get("lengthBars", 0))
    form = []
    for i, sc in enumerate(secs):
        start = float(sc["startBar"])
        end = float(secs[i + 1]["startBar"]) if i + 1 < len(secs) else total
        bars = max(4, int(round((end - start) / 4.0) * 4))
        base = re.sub(r" \d+$", "", str(sc.get("name", "part")).lower())
        form.append((SEC2ARRANGE.get(base, "build"), bars))
    return form


def flip(import_name, genre, out=None, seed=0, bars=0, full=False, hook=False):
    imp_path = os.path.join(ROOT, "songs", f"{import_name}.json")
    imp = json.load(open(imp_path))
    bpm, key = float(imp.get("bpm", 120)), imp.get("key")
    chords = imp.get("chords") or chord_map(imp)
    labels = [c["chord"] for c in chords]
    period = min(detect_cycle(labels), 8) if labels else 0
    cycle = labels[:period]
    gname = f"import_{import_name}"
    have_groove = gname in json.load(open(os.path.join(ROOT, "library", "grooves.json")))

    out = out or f"{import_name}_x_{genre}"
    out = re.sub(r"[^a-z0-9_]", "", out.lower())
    nbars = bars or max(4, period or 4)
    print(f"[flip] DNA: {bpm}bpm, key {key}, cycle {cycle or '(none)'}, "
          f"groove {'YES' if have_groove else 'no'}")
    loop_gen.generate(genre, out, bars=nbars, seed=seed, bpm=bpm, key=key)
    out_path = os.path.join(ROOT, "songs", f"{out}.json")

    rep = {}
    if cycle:
        song = json.load(open(out_path))
        own = [c["chord"] for c in chord_map(song)]
        tiled = [cycle[i % len(cycle)] for i in range(len(own) or nbars)]
        try:
            rep = reharm(song, targets_per_cycle=tiled)
            json.dump(song, open(out_path, "w"), indent=1)
            print(f"[flip] reharmonized to the import's cycle: {tiled} "
                  f"({rep['notes_moved']} notes moved)")
        except SystemExit as e:
            print(f"[flip] reharm skipped: {e}")

    grooved = []
    if have_groove:
        song = json.load(open(out_path))
        for t in song.get("tracks", []):
            nm = t.get("name", "")
            if re.match(r"hat|snare|perc|clap", nm):
                print("[flip] " + groove_mod.apply_groove(out_path, nm, gname, 0.9))
                grooved.append(nm)

    verify = [c["chord"] for c in chord_map(json.load(open(out_path)))]
    want = set(cycle) if cycle else set()
    got = set(verify)
    chord_ok = (not want) or want.issubset(got | set(w.rstrip("7m") for w in got)) \
               or all(v.rstrip("7m") == w.rstrip("7m") for v, w in
                      zip(verify, [cycle[i % len(cycle)] for i in range(len(verify))]))
    info = {"out": out, "genre": genre, "bpm": bpm, "key": key,
            "import_cycle": cycle, "remix_chords": verify,
            "chord_match": bool(chord_ok), "grooved": grooved,
            "notes_moved": rep.get("notes_moved", 0)}
    print(f"[flip] verify: remix votes {verify} vs import cycle {cycle} "
          f"-> {'MATCH' if chord_ok else 'MISMATCH'}")
    if full:
        form = structure_of(imp)
        if form:
            import arrange as arrange_mod
            full_name = f"{out}_full"
            arrange_mod.arrange(out_path, full_name, form=form)
            info["full"] = full_name
            info["form"] = [f"{n}:{b}" for n, b in form]
            print(f"[flip] FULL: the import's own structure "
                  f"({len(form)} sections, {sum(b for _, b in form)} bars) "
                  f"-> songs/{full_name}.json")
        else:
            print("[flip] full requested but the import has no sections — loop only")
    if hook and info.get("full"):
        try:
            import sing
            song = json.load(open(out_path))
            mel = next((t["name"] for t in song["tracks"]
                        if t.get("notes") and not re.match(r"kick|snare|hat", t["name"])), None)
            if mel:
                sing.hum(out, mel, "laa", "standard")
                voc = os.path.join(ROOT, "songs", f"{out}_vocal.wav")
                if os.path.exists(voc):
                    fp = os.path.join(ROOT, "songs", f"{info['full']}.json")
                    fs = json.load(open(fp))
                    drops = [sc for sc in fs.get("sections", [])
                             if str(sc["name"]).startswith("drop")]
                    clips = [{"file": os.path.relpath(voc, ROOT),
                              "startBeat": float(sc["startBar"]) * 4.0,
                              "lengthBeats": 32.0, "offsetSec": 0.0,
                              "sourceBpm": float(song.get("bpm", 120))}
                             for sc in drops[:4]]
                    fs["tracks"].append({
                        "name": "hook_vox", "source": {"kind": "audio", "id": "hook_vox"},
                        "gainDb": 0.5, "pan": 0.0, "notes": [],
                        "fx": [{"id": "fx_djfilter", "params": {"knob": 0.41, "res": 0.7}}],
                        "audioClips": clips})
                    json.dump(fs, open(fp, "w"), indent=1)
                    info["hook"] = {"melody": mel, "drops_sung": len(clips)}
                    print(f"[flip] HOOK: '{mel}' hummed -> vocal riding "
                          f"{len(clips)} drop sections (HP'd, acapella law)")
        except Exception as he:
            print(f"[flip] hook skipped: {type(he).__name__}: {he}")
    print("REMIX_JSON " + json.dumps(info))
    return info


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("import_song")
    ap.add_argument("genre")
    ap.add_argument("--out", default=None)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--bars", type=int, default=0)
    ap.add_argument("--full", action="store_true",
                    help="arrange the flip through the IMPORT'S OWN section shape")
    ap.add_argument("--hook", action="store_true",
                    help="hum the flip's lead melody (DiffSinger) and land it on the drops")
    a = ap.parse_args()
    flip(songname.resolve(a.import_song), a.genre,
         a.out, a.seed, a.bars, a.full, a.hook)
