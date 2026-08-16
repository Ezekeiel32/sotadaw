#!/usr/bin/env python3
"""BRIDGE OUT: song.json -> FL Studio project (.flp) — V17, the last one-way
bridge made two-way (als/dawproject/reaper already round-trip; FLP could only
arrive). FL Studio is the world's biggest producer community — sending THEM
editable projects is worldwide-product law.

  flp_export.py songs/x.json x.flp

Symbolic layer, RAW EVENT EMISSION (no template file): FLP is a TLV event
stream — header 'FLhd'(format,nchannels,ppq) + 'FLdt' + events; id<64 u8,
<128 u16, <192 u32, >=192 LEB128-varint + payload (PyFLP's parse() is the
codec truth this emitter was written against, and the parse court every
export passes through). MIDI tracks -> channel rack entries (names ride
UTF-16LE PluginID.Name). v2: ONE PATTERN PER TRACK (notes at absolute
ticks, ppq 960) + a REAL ARRANGEMENT — TrackID.Data per used playlist row
and a Playlist event placing each track's pattern on its own row at 0
(60-byte item stride ALWAYS: PyFLP sniffs format by len%60==0, so 32-byte
items would misparse whenever count%15==0). Audio clips are skipped
(symbolic layer).

Round-trip proof: tools/flp_bridge_battery.py (suite leg) — export ->
pyflp.parse court -> flp_import -> note-exact compare at tick resolution.
"""
import json
import os
import struct
import sys

PPQ = 960                      # finest VALID_PPQ — 1/3840-beat tick grid
FL_VERSION = b"20.8.4.2576"    # >= 11.5 => parsers read TEXT events as UTF-16LE

# event ids (PyFLP truth: project.py/pattern.py/channel.py/plugin.py)
EV_FLVERSION = 199             # TEXT+7, ascii
EV_TEMPO = 156                 # DWORD+28, u32 milli-bpm
EV_CHAN_NEW = 64               # WORD, u16 iid
EV_CHAN_TYPE = 21              # u8: 0 = Sampler (the default rack entry kind)
EV_CHAN_GROUP = 145            # DWORD+17, u32 display group (0 = unsorted)
EV_CHAN_NAME = 203             # PluginID.Name, TEXT+11, utf-16le
EV_GROUP_NAME = 231            # DisplayGroupID.Name — channels index groups[groupnum]
EV_PAT_NEW = 65                # WORD+1, u16 iid (1-based)
EV_PAT_NOTES = 224             # DATA+16, 24-byte note structs
EV_ARR_NEW = 99                # ArrangementID.New, u16
EV_ARR_NAME = 241              # ArrangementID.Name, utf-16le
EV_ARR_PLAYLIST = 233          # ArrangementID.Playlist, item structs
EV_TRACK_DATA = 238            # TrackID.Data — one per used playlist row
EV_ARRS_CURRENT = 100          # ArrangementsID.Current — TERMINATES the last
                               # arrangement (subtrees() only yields on a False)
PATTERN_BASE = 20480           # playlist item_index = base + pattern iid
MAX_TRACK_RVIDX = 499          # row i -> rvidx 499 - i (FL >= 12.9.1)

NOTE = struct.Struct("<IHHIHHBBBBBBBB")   # position,flags,rack,length,key,group,
                                          # fine,_u1,release,midich,pan,vel,modx,mody


def _varint(n):
    out = bytearray()
    while True:
        b = n & 0x7F
        n >>= 7
        out.append(b | (0x80 if n else 0))
        if not n:
            return bytes(out)


def _word(eid, v):
    return bytes([eid]) + struct.pack("<H", v)


def _dword(eid, v):
    return bytes([eid]) + struct.pack("<I", v)


def _data(eid, payload):
    return bytes([eid]) + _varint(len(payload)) + payload


def _text_utf16(eid, s):
    return _data(eid, str(s).encode("utf-16-le") + b"\x00\x00")


def export_flp(song_path, flp_path):
    song = json.load(open(song_path))
    bpm = float(song.get("bpm") or 120.0)
    tracks = [t for t in song.get("tracks", [])
              if isinstance(t, dict) and t.get("notes")]
    if not tracks:
        raise SystemExit("no MIDI tracks with notes to export (audio clips are v2)")

    ev = bytearray()
    ev += _data(EV_FLVERSION, FL_VERSION + b"\x00")          # MUST precede any TEXT
    ev += _dword(EV_TEMPO, max(10_000, min(999_000, round(bpm * 1000))))
    ev += _text_utf16(EV_GROUP_NAME, "unsorted")             # groups[0] for every channel

    per_track, total = [], 0
    for iid, t in enumerate(tracks):
        ev += _word(EV_CHAN_NEW, iid)
        ev += bytes([EV_CHAN_TYPE, 0])                       # Sampler rack entry
        ev += _dword(EV_CHAN_GROUP, 0)
        ev += _text_utf16(EV_CHAN_NAME, str(t.get("name") or f"channel_{iid + 1}")[:60])
        notes = []
        for n in t.get("notes", []):
            try:
                pos = max(0, round(float(n["start"]) * PPQ))
                ln = max(1, round(float(n.get("len", 0.25)) * PPQ))
                key = max(0, min(131, int(n["pitch"])))       # FL key range 0..131
                vel = max(1, min(128, round(float(n.get("vel", 0.78)) * 128)))
            except Exception:
                continue                                      # one bad note never kills the file
            notes.append((pos, 0, iid, ln, key, 0, 120, 0, 64, 0, 64, vel, 64, 64))
        notes.sort(key=lambda x: (x[0], x[4]))
        per_track.append(notes)
        total += len(notes)

    if not total:
        raise SystemExit("no exportable notes")
    span = max(p + ln for ns in per_track for p, _, _, ln, *_ in ns)
    span = max(span, round(float(song.get("lengthBars") or 0) * 4 * PPQ))
    for iid, notes in enumerate(per_track):                  # pattern iid = track iid + 1
        ev += _word(EV_PAT_NEW, iid + 1)
        if notes:
            ev += _data(EV_PAT_NOTES, b"".join(NOTE.pack(*n) for n in notes))

    # the arrangement: each track's pattern on its own playlist row at 0
    ev += _word(EV_ARR_NEW, 0)
    ev += _text_utf16(EV_ARR_NAME, "Arrangement")
    ITEM = struct.Struct("<IHHIHH2sH4sff")
    items = b"".join(
        ITEM.pack(0, PATTERN_BASE, PATTERN_BASE + iid + 1, span,
                  MAX_TRACK_RVIDX - iid, 0, b"\x78\x00", 64,
                  bytes((64, 100, 128, 128)), 0.0, 0.0) + b"\x00" * 28
        for iid, notes in enumerate(per_track) if notes)     # 60-byte stride (format sniff)
    ev += _data(EV_ARR_PLAYLIST, items)
    for iid in range(len(per_track)):                        # one Track model per used row
        ev += _data(EV_TRACK_DATA, struct.pack("<IIIB", iid + 1, 0, 0, 1))
    ev += _word(EV_ARRS_CURRENT, 0)                          # closes the arrangement

    with open(flp_path, "wb") as f:
        f.write(struct.pack("<4sIh2H", b"FLhd", 6, 0, len(tracks), PPQ))
        f.write(b"FLdt" + struct.pack("<I", len(ev)) + bytes(ev))
    msg = (f"exported {len(tracks)} tracks / {total} notes @ {bpm:g}bpm "
           f"(ppq {PPQ}, pattern-per-track + playlist) -> {flp_path}")
    print(msg)
    return msg


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: flp_export.py <song.json> <out.flp>")
    export_flp(sys.argv[1], sys.argv[2])
