#!/usr/bin/env python3
"""song.json <-> REAPER .rpp (the REAPER bridge — biggest Linux DAW, text format).

  reaper_bridge.py export <song.json> <out.rpp>
  reaper_bridge.py import <in.rpp> <out_song.json>

.rpp = an s-expression-ish text tree: <TAG attrs.. \n lines.. \n > with MIDI
items as delta-tick event lines "E <dticks> <status> <d1> <d2>" at a declared
PPQN (HASDATA 1 960 QN). We write notes tick-exact at 960 PPQN and read both
note-off styles (8x, or 9x vel 0). Volumes: VOLPAN linear <-> dB. Audio items:
SOURCE WAVE FILE with POSITION/LENGTH in seconds. Track order preserved.
Round-trip contract (like midi_bridge): note start/len at tick resolution,
velocity 7-bit, gainDb to VOLPAN float precision.
"""
import json, math, os, re, sys

PPQN = 960


# ---------------- rpp tree ----------------

class Node:
    def __init__(self, tag, attrs):
        self.tag, self.attrs, self.lines, self.children = tag, attrs, [], []

    def find(self, tag):
        return [c for c in self.children if c.tag == tag]


def tokenize_line(s):
    out, i, n = [], 0, len(s)
    while i < n:
        while i < n and s[i] in " \t":
            i += 1
        if i >= n:
            break
        if s[i] == '"':
            j = s.index('"', i + 1)
            out.append(s[i + 1:j]); i = j + 1
        else:
            j = i
            while j < n and s[j] not in " \t":
                j += 1
            out.append(s[i:j]); i = j
    return out


def parse_rpp(text):
    root, stack = None, []
    for raw in text.splitlines():
        s = raw.strip()
        if not s:
            continue
        if s.startswith("<"):
            toks = tokenize_line(s[1:])
            node = Node(toks[0], toks[1:])
            if stack:
                stack[-1].children.append(node)
            else:
                root = node
            stack.append(node)
        elif s == ">":
            stack.pop()
        else:
            if stack:
                stack[-1].lines.append(tokenize_line(s))
    return root


# ---------------- export ----------------

def db_to_lin(db):
    return 10 ** (db / 20.0)


def notes_to_midi_lines(notes, length_beats):
    evs = []
    for nt in notes:
        t0 = int(round(nt["start"] * PPQN))
        t1 = int(round((nt["start"] + nt["len"]) * PPQN))
        vel = max(1, min(127, int(round(nt.get("vel", 0.8) * 127))))
        pitch = int(nt["pitch"])
        evs.append((t0, 0, 0x90, pitch, vel))       # sort key 0: offs after ons at same tick? no—
        evs.append((t1, -1, 0x80, pitch, 0))        # offs first at equal tick (key -1)
    evs.sort(key=lambda e: (e[0], e[1]))
    lines, last = [], 0
    for t, _, st, d1, d2 in evs:
        lines.append(f"E {t - last} {st:02x} {d1:02x} {d2:02x}")
        last = t
    end = int(round(length_beats * PPQN))
    lines.append(f"E {max(0, end - last)} b0 7b 00")   # all-notes-off closes the item
    return lines


def export(song_path, out_path):
    song = json.load(open(song_path))
    bpm = float(song.get("bpm", 120))
    bars = float(song.get("lengthBars", 4))
    beats = bars * 4.0
    sec_per_beat = 60.0 / bpm
    L = []
    L.append('<REAPER_PROJECT 0.1 "7.0/sotadaw" 0')
    L.append(f"  TEMPO {bpm} 4 4")
    for t in song.get("tracks", []):
        name = t.get("name", "track")
        vol = db_to_lin(float(t.get("gainDb", 0)))
        pan = float(t.get("pan", 0))
        L.append("  <TRACK")
        L.append(f'    NAME "{name}"')
        L.append(f"    VOLPAN {vol:.14g} {pan:.14g} -1 -1 1")
        L.append(f"    MUTESOLO {1 if t.get('muted') else 0} 0 0")
        src = t.get("source")
        if src and src.get("kind") != "faust" or (src or {}).get("id") not in (None, "pluck"):
            payload = json.dumps(src, separators=(",", ":")).replace(chr(34), chr(39))
            L.append("    <SOTADAW_SOURCE")
            L.append(f'      DATA "{payload}"')
            L.append("    >")
        notes = t.get("notes", [])
        if notes:
            L.append("    <ITEM")
            L.append("      POSITION 0")
            L.append(f"      LENGTH {beats * sec_per_beat:.14g}")
            L.append(f'      NAME "{name}"')
            L.append("      <SOURCE MIDI")
            L.append(f"        HASDATA 1 {PPQN} QN")
            for ln in notes_to_midi_lines(notes, beats):
                L.append("        " + ln)
            L.append("      >")
            L.append("    >")
        for c in t.get("audioClips", []):
            f = c["file"]
            if not os.path.isabs(f):
                f = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(song_path)), "..", f))
            pos = float(c.get("startBeat", 0)) * sec_per_beat
            ln = float(c.get("lengthBeats", 0)) * sec_per_beat
            L.append("    <ITEM")
            L.append(f"      POSITION {pos:.14g}")
            L.append(f"      LENGTH {ln:.14g}" if ln > 0 else "      LENGTH 1")
            L.append(f"      SOFFS {float(c.get('offsetSec', 0)):.14g}")
            L.append('      <SOURCE WAVE')
            L.append(f'        FILE "{f}"')
            L.append("      >")
            L.append("    >")
        L.append("  >")
    L.append(">")
    open(out_path, "w").write("\n".join(L) + "\n")
    n = sum(len(t.get("notes", [])) for t in song.get("tracks", []))
    print(f"[reaper] exported {out_path}: {len(song.get('tracks', []))} tracks, {n} notes @ {bpm}bpm")


# ---------------- import ----------------

def midi_lines_to_notes(node):
    ppqn = PPQN
    for ln in node.lines:
        if ln and ln[0] == "HASDATA" and len(ln) >= 3:
            ppqn = int(ln[2]) if ln[2].isdigit() else int(float(ln[2]))
    t, ons, notes = 0, {}, []
    for ln in node.lines:
        if not ln or ln[0] not in ("E", "e", "Em"):
            continue
        t += int(ln[1])
        st = int(ln[2], 16)
        kind = st & 0xF0
        if kind == 0x90 and int(ln[4], 16) > 0:
            ons.setdefault(int(ln[3], 16), []).append((t, int(ln[4], 16)))
        elif kind in (0x80, 0x90):
            p = int(ln[3], 16)
            if ons.get(p):
                t0, vel = ons[p].pop(0)
                notes.append({"start": t0 / ppqn, "len": (t - t0) / ppqn,
                              "pitch": p, "vel": round(vel / 127.0, 6)})
    notes.sort(key=lambda x: (x["start"], x["pitch"]))
    return notes


def imp(rpp_path, out_path):
    root = parse_rpp(open(rpp_path, errors="replace").read())
    bpm = 120.0
    for ln in root.lines:
        if ln and ln[0] == "TEMPO":
            bpm = float(ln[1])
    sec_per_beat = 60.0 / bpm
    tracks, max_beat = [], 0.0
    for tn in root.find("TRACK"):
        name, gain, pan, muted = "track", 0.0, 0.0, False
        src_override = None
        for ln in tn.lines:
            if ln[0] == "NAME":
                name = ln[1]
            elif ln[0] == "VOLPAN":
                v = float(ln[1])
                gain = round(20 * math.log10(v), 6) if v > 1e-6 else -60.0
                pan = float(ln[2])
            elif ln[0] == "MUTESOLO":
                muted = ln[1] == "1"
            elif ln[0] == "SOTADAW_SOURCE":      # legacy line form
                try:
                    src_override = json.loads(ln[1].replace(chr(39), chr(34)))
                except Exception:
                    src_override = None
        for sc in tn.find("SOTADAW_SOURCE"):     # chunk form (REAPER-silent carrier)
            for ln2 in sc.lines:
                if ln2 and ln2[0] == "DATA":
                    try:
                        src_override = json.loads(ln2[1].replace(chr(39), chr(34)))
                    except Exception:
                        pass
        notes, clips = [], []
        for item in tn.find("ITEM"):
            pos = ln_val(item, "POSITION")
            length = ln_val(item, "LENGTH")
            soffs = ln_val(item, "SOFFS")
            for src in item.find("SOURCE"):
                if src.attrs and src.attrs[0] == "MIDI":
                    base = (pos or 0.0) / sec_per_beat
                    for nt in midi_lines_to_notes(src):
                        nt["start"] = round(nt["start"] + base, 9)
                        notes.append(nt)
                elif src.attrs and src.attrs[0] in ("WAVE", "FLAC", "MP3"):
                    f = ""
                    for l2 in src.lines:
                        if l2[0] == "FILE":
                            f = l2[1]
                    clips.append({"file": f, "startBeat": round((pos or 0) / sec_per_beat, 9),
                                  "lengthBeats": round((length or 0) / sec_per_beat, 9),
                                  "offsetSec": soffs or 0.0})
        for nt in notes:
            max_beat = max(max_beat, nt["start"] + nt["len"])
        for c in clips:
            max_beat = max(max_beat, c["startBeat"] + c["lengthBeats"])
        tr = {"name": name, "source": src_override if src_override
              else {"kind": "audio", "id": name} if clips and not notes
              else {"kind": "faust", "id": "pluck"},
              "gainDb": gain, "pan": pan, "notes": notes}
        if muted:
            tr["muted"] = True
        if clips:
            tr["audioClips"] = clips
        tracks.append(tr)
    song = {"version": 2, "bpm": bpm, "lengthBars": max(1.0, math.ceil(max_beat / 4.0)),
            "masterGainDb": 0.0, "comment": f"imported from {os.path.basename(rpp_path)}",
            "tracks": tracks}
    json.dump(song, open(out_path, "w"), indent=1)
    n = sum(len(t["notes"]) for t in tracks)
    print(f"[reaper] imported {out_path}: {len(tracks)} tracks, {n} notes @ {bpm}bpm")


def ln_val(node, key):
    for ln in node.lines:
        if ln and ln[0] == key:
            return float(ln[1])
    return None


if __name__ == "__main__":
    if sys.argv[1] == "export":
        export(sys.argv[2], sys.argv[3])
    else:
        imp(sys.argv[2], sys.argv[3])
