#!/usr/bin/env python3
"""MusicXML -> song.json — THE SCORE tab's "upload notes" rail (partwise subset).

Reads .musicxml/.xml (and .mxl zip containers), builds a v2 song:
- parts -> tracks; the instrument is guessed from the part name against
  instruments/*.dsp that ACTUALLY exist (never emits a dead voice id)
- unpitched percussion -> per-role kit tracks (score-instrument names win,
  else reverse-Weinberg display position — the exact mapping our exporter
  writes, so export->import roundtrips land every role)
- ties merged into single notes, chords exact, voices via backup/forward
- key/mode, meter changes (meterMap when the world isn't straight 4/4),
  first tempo, note dynamics -> velocity

Honest exits: 2 = not a partwise MusicXML score / no notes.
Usage: musicxml_import.py in.(musicxml|xml|mxl) out.json
Prints MUSICXML_IMPORT {stats json} on success (score_battery reads it).
"""
import json
import os
import sys
import zipfile
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LETTER_PC = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
LETTER_IDX = {"C": 0, "D": 1, "E": 2, "F": 3, "G": 4, "A": 5, "B": 6}
MAJORS = {0: "C", 1: "G", 2: "D", 3: "A", 4: "E", 5: "B", 6: "F#", 7: "C#",
          -1: "F", -2: "Bb", -3: "Eb", -4: "Ab", -5: "Db", -6: "Gb", -7: "Cb"}
MINORS = {0: "A", 1: "E", 2: "B", 3: "F#", 4: "C#", 5: "G#", 6: "D#", 7: "A#",
          -1: "D", -2: "G", -3: "C", -4: "F", -5: "Bb", -6: "Eb", -7: "Ab"}
DRUM_STEP_ROLE = [(1, "kick"), (3, "floor_tom"), (5, "snare"), (6, "mid_tom"),
                  (7, "hi_tom"), (8, "ride"), (9, "hats"), (11, "crash"), (-1, "pedal_hat")]
DRUM_PITCH = {"kick": 36, "snare": 38, "clap": 39, "hats": 42, "open_hat": 46,
              "pedal_hat": 44, "ride": 51, "crash": 49, "hi_tom": 50, "mid_tom": 47,
              "floor_tom": 43, "perc": 37}


def _have():
    try:
        return {f[:-4] for f in os.listdir(os.path.join(ROOT, "instruments"))
                if f.endswith(".dsp") and not f.startswith("fx_")}
    except OSError:
        return set()


HAVE = _have()


def pick(cands, fallback="fm4_keys"):
    for c in cands:
        if c in HAVE:
            return c
    if fallback in HAVE:
        return fallback
    return sorted(HAVE)[0] if HAVE else fallback


ROLE_INST = {
    "kick": ["kick_punch", "kick_808", "hardkick"],
    "snare": ["snare", "brush_snare"],
    "clap": ["clap_909"],
    "hats": ["hat"],
    "open_hat": ["hat_metal", "hat"],
    "pedal_hat": ["hat"],
    "ride": ["ride_cymbal", "hat"],
    "crash": ["crash_noise", "rev_crash"],
    "hi_tom": ["conga", "timpani"],
    "mid_tom": ["conga", "timpani"],
    "floor_tom": ["conga", "timpani"],
    "perc": ["shaker"],
}
MEL_INST = [
    ("upright", ["upright_bass"]), ("reese", ["reese"]), ("808", ["sub_808_slide", "sub_clean"]),
    ("bass", ["bass_warm"]),
    ("rhodes", ["rhodes"]), ("wurli", ["ep_bright"]), ("piano", ["jazz_piano"]),
    ("organ", ["hammond_organ"]), ("key", ["fm4_keys"]),
    ("nylon", ["nylon_guitar"]), ("fuzz", ["fuzz_guitar"]), ("dist", ["highgain_guitar", "fuzz_guitar"]),
    ("banjo", ["banjo"]), ("guitar", ["clean_chime_guitar"]),
    ("fiddle", ["fiddle"]), ("violin", ["fiddle"]), ("cello", ["pm_string"]),
    ("string", ["pm_string", "strings_stacc"]),
    ("trumpet", ["trumpet_lead"]), ("horn", ["cine_brass"]), ("tuba", ["tuba"]), ("brass", ["brass_stab"]),
    ("sax", ["sax_reed"]), ("flute", ["flute_lead"]), ("clarinet", ["clarinet"]), ("oboe", ["duduk"]),
    ("harp", ["harp"]), ("harmonica", ["harmonica"]), ("accordion", ["accordion"]),
    ("marimba", ["marimba"]), ("vibra", ["vibraphone"]), ("bell", ["fmbell"]), ("glock", ["fmbell"]),
    ("sitar", ["sitar"]), ("oud", ["oud"]),
    ("choir", ["vox_pad"]), ("vox", ["formant_vox"]), ("voice", ["formant_vox"]), ("vocal", ["formant_vox"]),
    ("pad", ["pad_motion"]), ("pluck", ["pluck2"]), ("lead", ["lead_legato"]), ("synth", ["supersaw"]),
]


def mel_inst(name):
    low = name.lower()
    for kw, cands in MEL_INST:
        if kw in low:
            return pick(cands)
    return pick(["fm4_keys"])


def load_root(path):
    if path.lower().endswith(".mxl"):
        with zipfile.ZipFile(path) as z:
            target = None
            try:
                c = ET.fromstring(z.read("META-INF/container.xml"))
                rf = c.find(".//rootfile")
                if rf is not None:
                    target = rf.get("full-path")
            except KeyError:
                pass
            if target is None:
                cands = [n for n in z.namelist()
                         if n.endswith((".musicxml", ".xml")) and not n.startswith("META-INF")]
                if not cands:
                    print("mxl container holds no musicxml", file=sys.stderr)
                    sys.exit(2)
                target = cands[0]
            return ET.fromstring(z.read(target))
    return ET.parse(path).getroot()


def text(el, tag, default=None):
    t = el.find(tag)
    return t.text if t is not None and t.text is not None else default


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    src, out_path = sys.argv[1], sys.argv[2]
    try:
        root = load_root(src)
    except (ET.ParseError, zipfile.BadZipFile, OSError) as e:
        print(f"can't read {os.path.basename(src)}: {e}", file=sys.stderr)
        sys.exit(2)
    if root.tag.split("}")[-1] != "score-partwise":
        print(f"not a partwise MusicXML score (root <{root.tag}>)", file=sys.stderr)
        sys.exit(2)

    part_names = {}
    inst_names = {}
    for sp in root.iter("score-part"):
        part_names[sp.get("id")] = text(sp, "part-name", sp.get("id") or "part") or "part"
        for si in sp.iter("score-instrument"):
            inst_names[si.get("id")] = (text(si, "instrument-name", "") or "").lower()

    bpm = None
    key_fifths, key_minor = 0, False
    meter_events = {}
    tracks, order = {}, []

    def track_for(name, inst):
        if name not in tracks:
            tracks[name] = {"name": name, "inst": inst, "notes": []}
            order.append(name)
        return tracks[name]

    def role_of(note_el, abs_step):
        iid = note_el.find("instrument")
        if iid is not None and inst_names.get(iid.get("id")):
            nm = inst_names[iid.get("id")]
            for kw, role in [("bass drum", "kick"), ("kick", "kick"), ("side stick", "snare"),
                             ("snare", "snare"), ("clap", "clap"), ("open hi", "open_hat"),
                             ("pedal", "pedal_hat"), ("hi-hat", "hats"), ("hihat", "hats"),
                             ("hi hat", "hats"), ("ride", "ride"), ("crash", "crash"),
                             ("cymbal", "crash"), ("low tom", "floor_tom"), ("floor", "floor_tom"),
                             ("high tom", "hi_tom"), ("mid tom", "mid_tom"), ("tom", "mid_tom")]:
                if kw in nm:
                    return role
        step = abs_step - 30            # exporter's treble-mapped display -> kernel step
        best, bd = "perc", 99
        for st, role in DRUM_STEP_ROLE:
            if abs(st - step) < bd:
                bd, best = abs(st - step), role
        return best

    n_parts = 0
    bar_count = 0
    cur_num, cur_den = 4, 4

    for part in root.findall("part"):
        pid = part.get("id")
        pname = part_names.get(pid, pid or "part")
        n_parts += 1
        divisions = 480.0
        bar_start = 0.0
        bar_idx = 0
        pending_tie = {}
        melodic_track = None
        for meas in part.findall("measure"):
            cursor = 0.0
            last_start = 0.0
            last_dur = 0.0
            for el in meas:
                tag = el.tag.split("}")[-1]
                if tag == "attributes":
                    d = text(el, "divisions")
                    if d:
                        divisions = float(d)
                    k = el.find("key")
                    if k is not None:
                        key_fifths = int(text(k, "fifths", "0") or 0)
                        key_minor = (text(k, "mode", "") or "").strip() == "minor"
                    tm = el.find("time")
                    if tm is not None:
                        nu = int(text(tm, "beats", "4") or 4)
                        de = int(text(tm, "beat-type", "4") or 4)
                        if (nu, de) != (cur_num, cur_den) or bar_idx == 0:
                            meter_events[bar_idx] = (nu, de)
                        cur_num, cur_den = nu, de
                elif tag == "sound" and el.get("tempo") and bpm is None:
                    bpm = float(el.get("tempo"))
                elif tag == "direction":
                    snd = el.find("sound")
                    if snd is not None and snd.get("tempo") and bpm is None:
                        bpm = float(snd.get("tempo"))
                elif tag == "backup":
                    cursor -= float(text(el, "duration", "0") or 0) / divisions
                elif tag == "forward":
                    cursor += float(text(el, "duration", "0") or 0) / divisions
                elif tag == "note":
                    if el.find("grace") is not None:
                        continue
                    dur = float(text(el, "duration", "0") or 0) / divisions
                    is_chord = el.find("chord") is not None
                    start_local = last_start if is_chord else cursor
                    g_start = bar_start + start_local
                    is_rest = el.find("rest") is not None
                    if not is_chord:
                        last_start = cursor
                        last_dur = dur
                        cursor += dur
                    if is_rest or dur <= 0:
                        continue
                    dyn = el.get("dynamics")
                    vel = max(0.05, min(1.0, float(dyn) / 100.0 * 0.9)) if dyn else 0.8
                    tie_start = any(t.get("type") == "start" for t in el.findall("tie"))
                    tie_stop = any(t.get("type") == "stop" for t in el.findall("tie"))
                    unp = el.find("unpitched")
                    if unp is not None:
                        ds = text(unp, "display-step", "G") or "G"
                        do = int(text(unp, "display-octave", "5") or 5)
                        abs_step = LETTER_IDX.get(ds, 4) + 7 * do
                        role = role_of(el, abs_step)
                        tr = track_for(role, pick(ROLE_INST.get(role, ["shaker"])))
                        tr["notes"].append({"start": g_start, "len": max(0.05, dur),
                                            "pitch": DRUM_PITCH.get(role, 37), "vel": vel})
                    else:
                        p = el.find("pitch")
                        if p is None:
                            continue
                        stepL = (text(p, "step", "C") or "C").strip().upper()[:1]
                        alter = float(text(p, "alter", "0") or 0)
                        octv = int(text(p, "octave", "4") or 4)
                        midi = int(round((octv + 1) * 12 + LETTER_PC.get(stepL, 0) + alter))
                        midi = max(0, min(127, midi))
                        if melodic_track is None:
                            melodic_track = track_for(pname, mel_inst(pname))
                        tkey = (pname, midi)
                        if tie_stop and tkey in pending_tie:
                            prev = pending_tie.pop(tkey)
                            prev["len"] = max(prev["len"], g_start + dur - prev["start"])
                            if tie_start:
                                pending_tie[tkey] = prev
                            continue
                        note = {"start": g_start, "len": max(0.05, dur), "pitch": midi, "vel": vel}
                        melodic_track["notes"].append(note)
                        if tie_start:
                            pending_tie[tkey] = note
            bar_start += cur_num * 4.0 / cur_den
            bar_idx += 1
        bar_count = max(bar_count, bar_idx)

    if not any(t["notes"] for t in tracks.values()):
        print("no notes found in the score", file=sys.stderr)
        sys.exit(2)

    tonic = (MINORS if key_minor else MAJORS).get(key_fifths, "C")
    song = {"version": 2, "bpm": bpm or 120.0,
            "key": f"{tonic} {'minor' if key_minor else 'major'}",
            "lengthBars": max(bar_count, 1), "tracks": []}
    mm = [{"bar": b, "num": nd[0], "den": nd[1]} for b, nd in sorted(meter_events.items())
          if not (b == 0 and nd == (4, 4))]
    if mm:
        song["meterMap"] = mm
    for name in order:
        t = tracks[name]
        if not t["notes"]:
            continue
        t["notes"].sort(key=lambda n: (n["start"], n["pitch"]))
        song["tracks"].append({"name": t["name"][:24],
                               "source": {"kind": "faust", "id": t["inst"]},
                               "notes": t["notes"]})
    with open(out_path, "w") as f:
        json.dump(song, f, indent=1)
    stats = {"parts": n_parts, "tracks": len(song["tracks"]),
             "notes": sum(len(t["notes"]) for t in song["tracks"]),
             "bars": song["lengthBars"], "key": song["key"], "fifths": key_fifths,
             "minor": key_minor, "bpm": song["bpm"]}
    print("MUSICXML_IMPORT " + json.dumps(stats))


if __name__ == "__main__":
    main()
