#!/usr/bin/env python3
"""Universal MIDI bridge — song.json <-> Standard MIDI File (format 1), zero deps.

  export: midi_bridge.py export songs/x.json out.mid
  import: midi_bridge.py import in.mid songs/x.json  [--kit gm_drums]

Export: track 0 = tempo map; one MIDI track per song track (named). Sample-drum tracks
go to channel 10 (GM convention), everything else cycles melodic channels.
Import: notes -> beats (from division), first set_tempo -> bpm, channel-10 tracks -> gm_drums,
melodic tracks -> piano kit by default (reassign sources afterwards in the app/agent)."""
import json, os, struct, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# ONE RESOLVER law (grid_lint): all bar<->quarter math lives in tools/meter.py.
# SMF ticks are QUARTER ticks, so bar_start_q is the whole quarter<->tick story.
from meter import bar_start_q as _bar_start_q

TPQ = 480  # ticks per quarter

# ---------------- writing ----------------
def vlq(n):
    out = [n & 0x7F]
    n >>= 7
    while n:
        out.append (0x80 | (n & 0x7F))
        n >>= 7
    return bytes(reversed(out))

def export_midi(song_path, midi_path):
    song = json.load(open(song_path))
    bpm = float(song.get("bpm", 120))
    tracks = song.get("tracks", [])

    chunks = []
    # tempo track: FF51 + FF58 time signatures at bar-start ticks (THE WORLD
    # GRID #1; den must be a power of two — SMF dd is log2) + beat-aligned
    # lyric meta-events (karaoke-standard FF 05). Mapless songs emit the exact
    # pre-#1 byte stream (tempo first, lyrics in beat order).
    meter = sorted((m for m in song.get("meterMap", [])
                    if int(m.get("num", 0)) > 0 and int(m.get("den", 0)) > 0
                    and int(m["den"]) & (int(m["den"]) - 1) == 0),
                   key=lambda m: int(m["bar"]))
    ev0 = [(0, 0, b"\xFF\x51\x03" + struct.pack(">I", int(60000000 / bpm))[1:])]
    for m in meter:
        tick = int(round(_bar_start_q(meter, int(m["bar"])) * TPQ))
        num, den = min(255, int(m["num"])), int(m["den"])
        ev0.append((tick, 1, b"\xFF\x58\x04"
                    + bytes([num, den.bit_length() - 1, 24, 8])))
    for ln in sorted(song.get("lyrics", []), key=lambda l: float(l["beat"])):
        tick = int(round(float(ln["beat"]) * TPQ))
        txt = str(ln["text"]).encode("latin1", "replace")[:120]
        ev0.append((tick, 2, b"\xFF\x05" + bytes([len(txt)]) + txt))
    ev0.sort(key=lambda e: (e[0], e[1]))
    ev, last_tick = b"", 0
    for tick, _, msg in ev0:
        ev += vlq(tick - last_tick) + msg
        last_tick = tick
    ev += b"\x00" + b"\xFF\x2F\x00"
    chunks.append(b"MTrk" + struct.pack(">I", len(ev)) + ev)

    melodic_ch = [c for c in range(16) if c != 9]
    mi = 0
    for t in tracks:
        src = t.get("source", {})
        is_drum = src.get("kind") == "sample" and "drum" in str(src.get("kit", src.get("id", "")))
        if is_drum:
            ch = 9
        else:
            ch = melodic_ch[mi % len(melodic_ch)]; mi += 1
        events = []  # (tick, priority, bytes)
        name = t.get("name", "track").encode()[:60]
        events.append((0, 0, b"\xFF\x03" + bytes([len(name)]) + name))
        # normalize: truncate a note at the next same-pitch onset (MIDI can't overlap same pitch/ch)
        notes = sorted(t.get("notes", []), key=lambda n: float(n["start"]))
        next_onset = {}
        for n in reversed(notes):
            pitch = int(n["pitch"])
            n["_len"] = max(0.02, min(float(n["len"]),
                            next_onset.get(pitch, 1e9) - float(n["start"]) - 0.001))
            next_onset[pitch] = float(n["start"])
        for n in notes:
            on_t = int(round(float(n["start"]) * TPQ))
            off_t = int(round((float(n["start"]) + max(0.02, float(n["_len"]))) * TPQ))
            vel = max(1, min(127, int(round(float(n.get("vel", 0.8)) * 127))))
            pitch = max(0, min(127, int(n["pitch"])))
            events.append((on_t, 1, bytes([0x90 | ch, pitch, vel])))
            events.append((off_t, 0, bytes([0x80 | ch, pitch, 0])))
        events.sort(key=lambda e: (e[0], e[1]))
        data, last = b"", 0
        for tick, _, msg in events:
            data += vlq(tick - last) + msg
            last = tick
        data += b"\x00\xFF\x2F\x00"
        chunks.append(b"MTrk" + struct.pack(">I", len(data)) + data)

    hdr = b"MThd" + struct.pack(">IHHH", 6, 1, len(chunks), TPQ)
    open(midi_path, "wb").write(hdr + b"".join(chunks))
    n = sum(len(t.get("notes", [])) for t in tracks)
    return f"exported {len(tracks)} tracks / {n} notes @ {bpm:.0f}bpm -> {midi_path}"

# ---------------- reading ----------------
def read_vlq(data, i):
    v = 0
    while True:
        b = data[i]; i += 1
        v = (v << 7) | (b & 0x7F)
        if not (b & 0x80):
            return v, i

def import_midi(midi_path, song_path, drum_kit="gm_drums", melodic_kit="piano"):
    data = open(midi_path, "rb").read()
    assert data[:4] == b"MThd", "not a MIDI file"
    _, fmt, ntrks, division = struct.unpack(">IHHH", data[4:14])
    assert division & 0x8000 == 0, "SMPTE time not supported"
    i = 14
    bpm = 120.0
    meter_raw = []   # (tick, num, den) from FF58 across all tracks
    out_tracks = []
    for _ in range(ntrks):
        assert data[i:i+4] == b"MTrk"
        length = struct.unpack(">I", data[i+4:i+8])[0]
        end = i + 8 + length
        j = i + 8
        tick = 0
        running = None
        name = None
        active = {}   # (ch,pitch) -> (start_tick, vel)
        notes = []
        channels = set()
        while j < end:
            delta, j = read_vlq(data, j)
            tick += delta
            b0 = data[j]
            if b0 == 0xFF:
                mtype = data[j+1]; mlen, k = read_vlq(data, j+2); body = data[k:k+mlen]; j = k + mlen
                if mtype == 0x51 and mlen == 3:
                    bpm = 60000000.0 / int.from_bytes(body, "big")
                elif mtype == 0x58 and mlen >= 2 and body[0] > 0:
                    meter_raw.append((tick, body[0], 1 << body[1]))
                elif mtype == 0x03 and name is None:
                    name = body.decode("latin1", "ignore").strip()
                continue
            if b0 in (0xF0, 0xF7):
                mlen, k = read_vlq(data, j+1); j = k + mlen; continue
            if b0 & 0x80:
                status = b0; j += 1; running = status
            else:
                status = running
            ch = status & 0x0F
            hi = status & 0xF0
            if hi in (0x80, 0x90, 0xA0, 0xB0, 0xE0):
                d1, d2 = data[j], data[j+1]; j += 2
            elif hi in (0xC0, 0xD0):
                d1, d2 = data[j], 0; j += 1
            else:
                j += 1; continue
            if hi == 0x90 and d2 > 0:
                active[(ch, d1)] = (tick, d2); channels.add(ch)
            elif hi == 0x80 or (hi == 0x90 and d2 == 0):
                st = active.pop((ch, d1), None)
                if st:
                    notes.append({"start": round(st[0] / division, 4),
                                  "len": round(max(1, tick - st[0]) / division, 4),
                                  "pitch": d1, "vel": round(st[1] / 127.0, 3)})
        i = end
        if notes:
            notes.sort(key=lambda n: n["start"])
            is_drum = channels == {9} or (9 in channels and len(channels) == 1)
            out_tracks.append({
                "name": name or ("drums" if is_drum else f"midi_{len(out_tracks)+1}"),
                "source": {"kind": "sample", "kit": drum_kit if is_drum else melodic_kit},
                "gainDb": -6.0,
                "notes": notes})
    # FF58 -> meterMap: walk regions in tick space (a bar of the running meter
    # is num*4/den QUARTER ticks); skip restatements of the running meter; a
    # lone 4/4-at-0 is the SMF default, not a map. Dedupe ticks (track 0 wins).
    meter = []
    if meter_raw:
        meter_raw.sort(key=lambda x: x[0])
        seen, bar, ptick, num, den = set(), 0.0, 0, 4, 4
        for tick, n2, d2 in meter_raw:
            if tick in seen:
                continue
            seen.add(tick)
            bar += (tick - ptick) / (num * 4.0 / den * division)  # grid-ok: tick-space FF58 walk (pre-song)
            ptick = tick
            if (n2, d2) != (num, den):
                num, den = n2, d2
                meter.append({"bar": int(round(bar)), "num": num, "den": den})
    max_beat = max((n["start"] + n["len"] for t in out_tracks for n in t["notes"]), default=16)
    if meter:
        import math
        bar, pq, bpb = 0, 0.0, 4.0
        for mp in meter:
            mq = _bar_start_q(meter, int(mp["bar"]))
            if mq > max_beat:
                break
            bar, pq, bpb = int(mp["bar"]), mq, float(mp["num"]) * 4.0 / float(mp["den"])  # grid-ok: region walk beside bar_start_q
        length_bars = max(1, int(math.ceil(bar + (max_beat - pq) / bpb - 1e-9)))
    else:
        length_bars = max(1, int(max_beat // 4 + 1))  # grid-ok: mapless import = 4/4
    song = {"version": 1, "bpm": round(bpm, 2), "lengthBars": length_bars,
            "masterGainDb": 0,
            # master-chain LAW (never type "limiter" — its ceiling is non-functional;
            # fx_truepeak = the release wall, ceiling means OUTPUT dBTP)
            "master": [{"type": "faustfx", "id": "fx_trim", "params": {"level": -6}},
                       {"type": "faustfx", "id": "fx_truepeak", "params": {"ceiling": -1.2}}],
            "tracks": out_tracks}
    if meter:
        song["meterMap"] = meter
    json.dump(song, open(song_path, "w"), indent=1)
    n = sum(len(t["notes"]) for t in out_tracks)
    return f"imported {len(out_tracks)} tracks / {n} notes @ {bpm:.1f}bpm -> {song_path} (sources default to kits; reassign as needed)"

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "export":
        print(export_midi(sys.argv[2], sys.argv[3]))
    elif cmd == "import":
        print(import_midi(sys.argv[2], sys.argv[3]))
    else:
        sys.exit("usage: midi_bridge.py export <song.json> <out.mid> | import <in.mid> <song.json>")
