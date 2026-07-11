#!/usr/bin/env python3
"""W15 THE CHOIR (voice III) — multi-singer stacks in ONE pass, no manual pitch work.

choir.py <song> <melody_track> [--bars A-B] [--syllable laa|ooh|ah] [--out <name>]
         [--stack "lead=standard@0,double=hunter:0.5,standard:0.5@0,harmony=lilith@3rd"]

Each stack voice = (name, timbre embed or blend, interval). '3rd' = DIATONIC third above
in the song's key (degree+2 in the scale — the interval breathes major/minor with the
melody, which is what a real harmony singer does). Every voice renders through the
DiffSinger pipeline on its own temp song, then all land as audio tracks (panned, staged)
in songs/<out>.json. Timbre Law holds: inputs are OUR notes; outputs are replaceable tracks.
"""
import argparse, json, os, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import sing  # noqa: E402

M1 = os.path.join(ROOT, "app/build/m1_artefacts/Release/m1")
NOTE_PC = {"C": 0, "C#": 1, "DB": 1, "D": 2, "D#": 3, "EB": 3, "E": 4, "F": 5, "F#": 6,
           "GB": 6, "G": 7, "G#": 8, "AB": 8, "A": 9, "A#": 10, "BB": 10, "B": 11}
MAJ, MIN = [0, 2, 4, 5, 7, 9, 11], [0, 2, 3, 5, 7, 8, 10]


def scale_of(key):
    parts = (key or "C minor").split()
    root = NOTE_PC.get(parts[0].upper(), 0)
    return root, (MIN if len(parts) > 1 and parts[1].lower().startswith("min") else MAJ)


def third_above(pitch, root, scale):
    rel = (pitch - root) % 12
    deg = min(range(7), key=lambda i: min((rel - scale[i]) % 12, (scale[i] - rel) % 12))
    up2 = deg + 2
    return pitch + (scale[up2 % 7] - scale[deg]) + 12 * (up2 // 7)


def parse_stack(spec):
    out = []
    for part in spec.split(","):
        # embed blends contain ':' and ',' — voices are NAME=EMBED@INTERVAL, so rejoin
        out.append(part)
    voices, buf = [], ""
    for part in spec.split(","):
        buf = f"{buf},{part}" if buf else part
        if "@" in buf and "=" in buf:
            name, rest = buf.split("=", 1)
            emb, _, iv = rest.rpartition("@")
            voices.append((name.strip(), emb.strip(), iv.strip()))
            buf = ""
    return voices


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("song")
    ap.add_argument("track")
    ap.add_argument("--bars")
    ap.add_argument("--syllable", default="laa")
    ap.add_argument("--out")
    ap.add_argument("--stack",
                    default="lead=standard@0,double=hunter:0.5,standard:0.5@0,harmony=lilith@3rd")
    ap.add_argument("--form",
                    help="per-section voice switching: 'A-B=voice+voice;C-D=...' in bars of the "
                         "SLICED region, e.g. '0-8=lead;8-16=lead+double+harmony' (W15 full form)")
    ap.add_argument("--adlibs", nargs="?", const="ey",
                    help="W15c AD-LIB LANE: the 4th timbre (phantom) answers in the melody's "
                         "GAPS (>=1.25 beats of silence) — short interjections, wide-panned, quiet. "
                         "Optional value = syllable (default 'ey').")
    a = ap.parse_args()

    sp = os.path.join(ROOT, "songs", f"{a.song}.json")
    song = json.load(open(sp))
    tr = next((t for t in song["tracks"] if t.get("name") == a.track), None)
    if not tr or not tr.get("notes"):
        sys.exit(f"no notes on track '{a.track}'")
    notes = sorted(tr["notes"], key=lambda n: n["start"])
    if a.bars:
        b0, b1 = (int(x) for x in a.bars.split("-"))
        notes = [dict(n, start=round(n["start"] - b0 * 4, 3)) for n in notes
                 if b0 * 4 <= n["start"] < b1 * 4]
        if not notes:
            sys.exit(f"no notes in bars {a.bars}")
    root, scale = scale_of(song.get("key"))
    voices = parse_stack(a.stack)
    form = []
    if a.form:   # W15 full form: each voice sings ONLY its sections (phrasing stays honest)
        for seg in a.form.split(";"):
            rng, _, vs = seg.partition("=")
            fb0, fb1 = (int(x) for x in rng.split("-"))
            form.append((fb0 * 4, fb1 * 4, {v.strip() for v in vs.split("+")}))
    print(f"[choir] {len(voices)} voices x {len(notes)} notes, key {song.get('key')}"
          + (f", form {a.form}" if a.form else ""))

    rendered = []
    for name, emb, iv in voices:
        vnotes = [dict(n) for n in notes]
        if form:
            vnotes = [n for n in vnotes
                      if any(lo <= n["start"] < hi and name in vv for lo, hi, vv in form)]
            if not vnotes:
                print(f"[choir] {name}: no notes in its sections — skipped")
                continue
        if iv in ("3rd", "+3rd"):
            for n in vnotes:
                n["pitch"] = third_above(n["pitch"], root, scale)
        elif iv and iv not in ("0", ""):
            for n in vnotes:
                n["pitch"] += int(iv)
        tmp_name = f"_choir_{name}"
        tmp = {"version": 2, "bpm": song.get("bpm", 120), "key": song.get("key"),
               "lengthBars": int(max(n["start"] + n["len"] for n in vnotes) // 4 + 1),
               "tracks": [{"name": a.track, "source": tr.get("source", {}),
                           "gainDb": -60, "notes": vnotes}]}
        json.dump(tmp, open(os.path.join(ROOT, "songs", f"{tmp_name}.json"), "w"), indent=1)
        sing.hum(tmp_name, a.track, a.syllable, emb)     # writes songs/_choir_<name>_vocal.wav
        wav = os.path.join(ROOT, "songs", f"{tmp_name}_vocal.wav")
        if not os.path.exists(wav):
            sys.exit(f"voice '{name}' failed to render")
        rendered.append((name, wav))

    if a.adlibs:
        # gaps >= 2 beats between melody notes become answer slots: one short
        # interjection at the gap's head, pitch = a 5th above the note just sung
        ends = sorted((n["start"], n["start"] + n["len"], n["pitch"]) for n in notes)
        adlib_notes, prev_end, prev_pitch = [], None, notes[0]["pitch"]
        span_end = max(e for _, e, _ in ends)
        for s0, e0, p0 in ends:
            if prev_end is not None and s0 - prev_end >= 1.25:
                adlib_notes.append({"start": round(prev_end + 0.25, 3), "len": 0.75,
                                    "pitch": third_above(prev_pitch, root, scale) + 2,
                                    "vel": 0.5})
            prev_end, prev_pitch = max(prev_end or 0, e0), p0
        if span_end - prev_end >= 1.0:   # tail gap: one last answer
            adlib_notes.append({"start": round(prev_end + 0.25, 3), "len": 1.0,
                                "pitch": third_above(prev_pitch, root, scale), "vel": 0.5})
        if adlib_notes:
            tmp = {"version": 2, "bpm": song.get("bpm", 120), "key": song.get("key"),
                   "lengthBars": int(max(n["start"] + n["len"] for n in adlib_notes) // 4 + 1),
                   "tracks": [{"name": a.track, "source": tr.get("source", {}),
                               "gainDb": -60, "notes": adlib_notes}]}
            json.dump(tmp, open(os.path.join(ROOT, "songs", "_choir_adlib.json"), "w"), indent=1)
            sing.hum("_choir_adlib", a.track, a.adlibs, "phantom")
            wav = os.path.join(ROOT, "songs", "_choir_adlib_vocal.wav")
            if os.path.exists(wav):
                rendered.append(("adlib", wav))
                print(f"[choir] adlib lane: {len(adlib_notes)} interjections in the gaps "
                      f"(phantom, '{a.adlibs}') at beats "
                      + ", ".join(str(n['start']) for n in adlib_notes[:6]))
        else:
            print("[choir] adlib lane: no gaps >= 2 beats — melody leaves no room to answer")

    out_name = a.out or f"{a.song}_choir"
    out = dict(song)
    if a.bars:   # demo mode: the sliced hook becomes its own short song
        b0, b1 = (int(x) for x in a.bars.split("-"))
        out = {"version": 2, "bpm": song.get("bpm"), "key": song.get("key"),
               "lengthBars": b1 - b0, "swing": song.get("swing"),
               "masterGainDb": 0, "master": song.get("master", []),
               "tracks": []}
        for t in song["tracks"]:
            ns = [dict(n, start=round(n["start"] - b0 * 4, 3)) for n in t.get("notes", [])
                  if b0 * 4 <= n.get("start", 0) < b1 * 4]
            if ns:
                out["tracks"].append(dict(t, notes=ns, automation=[]))
    PAN = {"lead": 0.0, "double": -0.35, "harmony": 0.32, "adlib": 0.45}
    GAIN = {"lead": -4.0, "double": -9.0, "harmony": -7.5, "adlib": -10.0}
    for name, wav in rendered:
        out["tracks"].append({
            "name": f"vox_{name}",
            "source": {"kind": "audio", "id": f"vox_{name}"},
            "gainDb": GAIN.get(name, -7.0), "pan": PAN.get(name, 0.0),
            "fx": [{"id": "fx_reverb", "params": {"mix": 0.16, "size": 1.9, "damp": 5200}}],
            "audioClips": [{"file": os.path.relpath(wav, ROOT), "startBeat": 0}],
            "comment": "voice: Gahata Meiji from LUNAI Project",
            "notes": []})
    op = os.path.join(ROOT, "songs", f"{out_name}.json")
    json.dump(out, open(op, "w"), indent=1)
    r = subprocess.run([M1, "render", op, op[:-5] + ".wav"], capture_output=True, text=True)
    ok = "ok=1" in r.stdout + r.stderr
    print(f"[choir] {out_name}: {len(rendered)} voices landed as tracks; render "
          f"{'OK' if ok else 'FAILED: ' + (r.stdout + r.stderr)[-200:]}")
    print(f"        stacks: " + ", ".join(f"{n} -> {os.path.basename(w)}" for n, w in rendered))


if __name__ == "__main__":
    main()
