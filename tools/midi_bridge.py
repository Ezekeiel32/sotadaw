#!/usr/bin/env python3
"""Universal MIDI bridge — song.json <-> Standard MIDI File (format 1), zero deps.

  export: midi_bridge.py export songs/x.json out.mid
  import: midi_bridge.py import in.mid songs/x.json  [--kit gm_drums]

Export: track 0 = tempo map; one MIDI track per song track (named). Sample-drum tracks
go to channel 10 (GM convention), everything else cycles melodic channels.
Import: notes -> beats (from division), first set_tempo -> bpm, channel-10 tracks -> gm_drums,
melodic tracks -> piano kit by default (reassign sources afterwards in the app/agent).

AUTOMATION (v2): track gainDb/pan lanes ride as CC7/CC10 streams. MIDI CC is a
STEP function, so curve=+1.0 (hold-then-step) is its NATIVE semantic — 2 events,
exact; every other curve densifies through tools/tracktion_curve (the engine's
own bezier) into 16 steps, consecutive-equal values deduped. Volume taper is the
GM 40*log10 law (foreign players render the fade correctly); cc0 = -96 dB floor,
+dB has no CC7 form (capped at 0 = cc127, counted). Import lands CC7/CC10 back
as hold-point lanes (the literal truth of what a MIDI player does); the value
maps are exact inverses, so the bridge stays byte-idempotent after pass one.
fx[i].*/source.* targets have no SMF form — skipped and counted, never silently.
"""
import json, math, os, struct, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# ONE RESOLVER law (grid_lint): all bar<->quarter math lives in tools/meter.py.
# SMF ticks are QUARTER ticks, so bar_start_q is the whole quarter<->tick story.
from meter import bar_start_q as _bar_start_q

TPQ = 480  # ticks per quarter
CC_DENSIFY = 16   # engine-sampled steps per non-hold automation segment
CC_FLOOR_DB = -96.0   # cc 0 <-> -96 dB (exact-inverse pair; keeps idempotence)

def _db_to_cc(v):
    v = float(v)
    if v <= CC_FLOOR_DB + 0.1:
        return 0
    return max(0, min(127, int(round(127.0 * 10.0 ** (min(0.0, v) / 40.0)))))

def _cc_to_db(cc):
    return CC_FLOOR_DB if cc == 0 else round(40.0 * math.log10(cc / 127.0), 3)

def _pan_to_cc(v):
    return max(0, min(127, 64 + int(round(float(v) * 63.5))))

def _cc_to_pan(cc):
    return round(max(-1.0, min(1.0, (cc - 64) / 63.5)), 4)

def _cc_events(lane, ch, cc, conv):
    """One automation lane -> deduped CC step events, engine-true shapes."""
    from tracktion_curve import curve_value
    pts = sorted(({"beat": float(p.get("beat", 0)), "v": float(p.get("v", 0)),
                   "curve": float(p.get("curve", 0.0))}
                  for p in lane.get("points", []) if isinstance(p, dict)),
                 key=lambda p: p["beat"])
    raw = []
    for i, p in enumerate(pts):
        raw.append((p["beat"], p["v"]))
        if i == len(pts) - 1:
            break
        nxt = pts[i + 1]
        span = nxt["beat"] - p["beat"]
        if p["curve"] < 0.999 and span > 1e-9:      # hold needs NO interior steps
            for k in range(1, CC_DENSIFY + 1):
                x = p["beat"] + span * k / (CC_DENSIFY + 1)
                raw.append((x, curve_value(x, p["beat"], p["v"],
                                           nxt["beat"], nxt["v"], p["curve"])))
    evs, last = [], None
    for beat, v in raw:
        val = conv(v)
        if val == last:
            continue
        last = val
        evs.append((int(round(beat * TPQ)), 0, bytes([0xB0 | ch, cc, val])))
    return evs

# ---------------- writing ----------------
def vlq(n):
    out = [n & 0x7F]
    n >>= 7
    while n:
        out.append (0x80 | (n & 0x7F))
        n >>= 7
    return bytes(reversed(out))

def export_midi(song_path, midi_path, portable=False):
    song = json.load(open(song_path))
    receipts = None
    if portable:
        # THE PORTABLE SCORE (Chezy 2026-08-03 "BY THE BOOK... STILL BE THE
        # SAME ORIGINAL SONG in a generic DAW"): project through the producer
        # pass (dewave/degun/pocket/gate/density/velocity + GM identity)
        # before emitting bytes. The in-DAW lanes are untouched. DEFAULT OFF
        # here: the bare function keeps the byte-idempotence law every
        # bridge battery rides; user doors (CLI --portable, daw_mcp) opt in.
        try:
            import midi_producer
            song, receipts = midi_producer.produce(song)
        except Exception as pe:
            print(f"[midi] producer pass skipped ({pe}) -> raw export",
                  flush=True)
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
    cc_skipped = 0
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
        if portable and not is_drum:
            # GM identity: a generic DAW must hear bass as bass, choir as
            # vocals — not thirteen grand pianos (portable-gated so the raw
            # byte-idempotence contract stays exact).
            import midi_producer as _mp
            events.append((0, 0, bytes([0xC0 | ch,
                                        _mp.program_of(t.get("name", ""))])))
        for lane in t.get("automation", []) or []:
            if not isinstance(lane, dict):
                continue
            tgt = str(lane.get("target", ""))
            if tgt == "gainDb":
                events += _cc_events(lane, ch, 7, _db_to_cc)
            elif tgt == "pan":
                events += _cc_events(lane, ch, 10, _pan_to_cc)
            else:
                cc_skipped += 1          # fx[i].*/source.*: no SMF form
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
    if receipts:
        moved = sum(1 for r in receipts.values()
                    if r["before"] != r["after"])
        wb = sum(r["before"]["wavy"] for r in receipts.values())
        wa = sum(r["after"]["wavy"] for r in receipts.values())
        print(f"[midi] PORTABLE SCORE: {moved} lanes produced "
              f"(wavy {wb}->{wa}, velocities in musical bands, GM programs "
              f"stamped)", flush=True)
    n = sum(len(t.get("notes", [])) for t in tracks)
    n_cc = sum(1 for t in tracks for l in t.get("automation", []) or []
               if isinstance(l, dict) and str(l.get("target")) in ("gainDb", "pan"))
    return (f"exported {len(tracks)} tracks / {n} notes"
            + (f" / {n_cc} automation lanes as CC7/CC10" if n_cc else "")
            + (f" ({cc_skipped} fx/source lanes have no SMF form)" if cc_skipped else "")
            + f" @ {bpm:.0f}bpm -> {midi_path}")

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
        cc_lanes = {}   # cc number (7|10) -> [(tick, value)]
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
            if hi == 0xB0 and d1 in (7, 10):
                cc_lanes.setdefault(d1, []).append((tick, d2))
            elif hi == 0x90 and d2 > 0:
                active[(ch, d1)] = (tick, d2); channels.add(ch)
            elif hi == 0x80 or (hi == 0x90 and d2 == 0):
                st = active.pop((ch, d1), None)
                if st:
                    notes.append({"start": round(st[0] / division, 4),
                                  "len": round(max(1, tick - st[0]) / division, 4),
                                  "pitch": d1, "vel": round(st[1] / 127.0, 3)})
        i = end
        autos = []
        for ccn in sorted(cc_lanes):
            pts = []
            for tk, val in cc_lanes[ccn]:
                p = {"beat": round(tk / division, 4),
                     "v": _cc_to_db(val) if ccn == 7 else _cc_to_pan(val),
                     "curve": 1.0}          # CC is a step stream: hold IS its truth
                pts.append(p)
            if pts:
                pts[-1].pop("curve")
                autos.append({"target": "gainDb" if ccn == 7 else "pan", "points": pts})
        if notes or autos:
            notes.sort(key=lambda n: n["start"])
            is_drum = channels == {9} or (9 in channels and len(channels) == 1)
            tr = {"name": name or ("drums" if is_drum else f"midi_{len(out_tracks)+1}"),
                  "source": {"kind": "sample", "kit": drum_kit if is_drum else melodic_kit},
                  "gainDb": -6.0,
                  "notes": notes}
            if autos:
                tr["automation"] = autos
            out_tracks.append(tr)
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
    for t in out_tracks:                 # a CC ride past the last note still needs world
        for lane in t.get("automation", []) or []:
            if lane["points"]:
                max_beat = max(max_beat, lane["points"][-1]["beat"])
    if meter:
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
    n_cc = sum(len(t.get("automation", []) or []) for t in out_tracks)
    return (f"imported {len(out_tracks)} tracks / {n} notes"
            + (f" / {n_cc} CC automation lanes" if n_cc else "")
            + f" @ {bpm:.1f}bpm -> {song_path} (sources default to kits; reassign as needed)")

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "export":
        portable = "--portable" in sys.argv
        args = [a for a in sys.argv[2:] if a != "--portable"]
        print(export_midi(args[0], args[1], portable=portable))
    elif cmd == "import":
        print(import_midi(sys.argv[2], sys.argv[3]))
    else:
        sys.exit("usage: midi_bridge.py export <song.json> <out.mid> "
                 "[--portable] | import <in.mid> <song.json>\n"
                 "  --portable = THE PORTABLE SCORE producer pass (dewave/"
                 "velocity/GM identity) — the .mid plays as THE SONG on "
                 "generic instruments; bare export stays byte-faithful")
