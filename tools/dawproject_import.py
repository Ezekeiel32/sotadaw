#!/usr/bin/env python3
"""BRIDGE: import a DAWproject (.dawproject — Bitwig/Cubase/Nuendo/Studio One open
exchange format) into song.json. Symbolic layer: tempo, tracks, note clips (with
playStart/loop offsets, nested clip lanes), audio clips (extracted from the archive),
channel volume/pan, AND automation.

  dawproject_import.py project.dawproject songs/out.json

Format: a ZIP with project.xml; Lanes timeUnit=beats; Note time/duration in beats
relative to clip start; vel/rel are 0..1 floats. Volume unit=linear (0..2).

Automation (v2): <Points><Target parameter=ID/> lanes resolve through the
Structure's Volume/Pan element ids -> track automation[] targets gainDb/pan
(values converted back to dB / -1..1); a role="master" channel's Volume lane
lands as song-level masterGainDb automation with values capped at 0 dB (the
master chain law: the wall regulates, masterGainDb only ever ducks).
RealPoint interpolation "hold" -> point curve 1.0 (the engine's exact
hold-then-step); "linear"/absent -> 0.
"""
import json, math, os, re, sys, zipfile
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def import_dawproject(dp_path, song_path):
    zf = zipfile.ZipFile(dp_path)
    xml_name = next((n for n in zf.namelist() if n.endswith("project.xml")), None)
    if xml_name is None:
        raise SystemExit("no project.xml in archive — not a dawproject?")
    root = ET.fromstring(zf.read(xml_name))

    bpm = 120.0
    tempo = root.find("./Transport/Tempo")
    if tempo is not None and tempo.get("value"):
        bpm = float(tempo.get("value"))

    # structure: track id -> {name, volume dB, pan}; parameter-element id ->
    # (track id, automation target) so <Points><Target parameter=.../> resolves
    tracks_meta = {}
    order = []
    param_map = {}                       # Volume/Pan element id -> (tid, target)
    for tr in root.iter("Track"):
        tid = tr.get("id")
        if tid is None:
            continue
        ch = tr.find("Channel")
        is_master = (ch is not None and ch.get("role") == "master")
        if not is_master:
            meta = {"name": tr.get("name") or f"track_{len(tracks_meta)+1}",
                    "contentType": tr.get("contentType", "notes"), "gainDb": 0.0, "pan": 0.0}
            srcv = tr.get("{https://sotadaw.local/ns}source") or tr.get("sotadaw:source")
            if srcv:
                try:
                    meta["source"] = json.loads(srcv)
                except Exception:
                    pass
        if ch is not None:
            vol = ch.find("Volume")
            if vol is not None:
                if vol.get("id"):
                    param_map[vol.get("id")] = ("master" if is_master else tid, "gainDb")
                if not is_master and vol.get("value"):
                    v = float(vol.get("value"))
                    meta["gainDb"] = round(20.0 * math.log10(max(1e-4, v)), 2)
            pan = ch.find("Pan")
            if pan is not None:
                if pan.get("id"):
                    param_map[pan.get("id")] = ("master" if is_master else tid, "pan")
                if not is_master and pan.get("value"):
                    p = float(pan.get("value"))
                    # normalized 0..1 (0.5 = center) is the common encoding
                    meta["pan"] = round((p - 0.5) * 2.0, 3) if 0.0 <= p <= 1.0 else round(p, 3)
        if is_master:
            continue                     # the master strip is a fader, not a lane of ours
        tracks_meta[tid] = meta
        order.append(tid)

    notes_by_track = {tid: [] for tid in tracks_meta}
    audio_by_track = {tid: [] for tid in tracks_meta}
    assets_dir = os.path.splitext(song_path)[0] + "_assets"

    def collect_clip(clip, base_beats, track_id):
        """Accumulate a <Clip>'s content at absolute position base_beats + clip time."""
        t = float(clip.get("time", 0))
        play_start = float(clip.get("playStart", 0))
        dur = clip.get("duration")
        start = base_beats + t
        end = start + float(dur) if dur is not None else None
        for notes_el in clip.findall("Notes"):
            for nv in notes_el.iter("Note"):
                try:
                    nt = float(nv.get("time", 0)) - play_start
                    nd = float(nv.get("duration", 0.25))
                    key = int(nv.get("key", 60))
                    vel = float(nv.get("vel", 0.78))
                except (TypeError, ValueError):
                    continue
                if nt < 0:
                    continue
                abs_start = start + nt
                if end is not None and abs_start >= end:
                    continue
                notes_by_track[track_id].append(
                    {"start": round(abs_start, 4), "len": round(max(0.05, nd), 4),
                     "pitch": key, "vel": round(min(1.0, max(0.05, vel)), 3)})
        for warps in clip.findall("Warps"):
            audio = warps.find("Audio")
            if audio is None or not audio.get("file"):
                continue
            f = audio.get("file")
            member = next((n for n in zf.namelist() if n.endswith(f) or n == f), None)
            offset = 0.0
            first_warp = warps.find("Warp")
            if first_warp is not None and first_warp.get("contentTime"):
                offset = float(first_warp.get("contentTime"))
            entry = {"startBeat": round(start, 4), "offsetSec": round(offset, 4)}
            if end is not None:
                entry["lengthBeats"] = round(end - start, 4)
            if member:
                os.makedirs(assets_dir, exist_ok=True)
                dst = os.path.join(assets_dir, os.path.basename(f))
                with open(dst, "wb") as out:
                    out.write(zf.read(member))
                entry["file"] = os.path.relpath(dst, ROOT)
            else:
                entry["file"] = f    # external reference; resolved if it exists
            audio_by_track[track_id].append(entry)
        # nested content lanes (clip-in-clip looping): recurse with our start as base
        for inner_clips in clip.findall("Clips"):
            for inner in inner_clips.findall("Clip"):
                collect_clip(inner, start, track_id)

    auto_by_track = {}                   # tid ("master" incl.) -> [automation lanes]
    n_capped = 0

    def collect_points(points_el):
        nonlocal n_capped
        target = points_el.find("Target")
        pid = target.get("parameter") if target is not None else None
        hit = param_map.get(pid or "")
        if hit is None:
            return
        tid, tgt = hit
        pts = []
        for rp in points_el.iter("RealPoint"):
            try:
                beat = float(rp.get("time", 0))
                raw = float(rp.get("value", 0))
            except (TypeError, ValueError):
                continue
            if tgt == "gainDb":
                v = round(20.0 * math.log10(max(1e-4, raw)), 3)
                if tid == "master" and v > 0.0:
                    v, n_capped = 0.0, n_capped + 1   # master chain law: only ever ducks
            else:
                v = round((raw - 0.5) * 2.0, 4) if 0.0 <= raw <= 1.0 else round(raw, 4)
            p = {"beat": round(beat, 6), "v": v}
            if rp.get("interpolation") == "hold":
                p["curve"] = 1.0                      # the engine's exact hold-then-step
            pts.append(p)
        if pts:
            lane = {"target": "masterGainDb" if tid == "master" else tgt,
                    "points": sorted(pts, key=lambda p: p["beat"])}
            auto_by_track.setdefault(tid, []).append(lane)

    arrangement = root.find("Arrangement")
    if arrangement is not None:
        for lanes in arrangement.iter("Lanes"):
            tid = lanes.get("track")
            if tid is None:
                continue
            for points_el in lanes.findall("Points"):
                collect_points(points_el)
            if tid not in tracks_meta:
                continue
            for clips in lanes.findall("Clips"):
                for clip in clips.findall("Clip"):
                    collect_clip(clip, 0.0, tid)

    drum_re = re.compile(r"drum|kit|beat|perc|808|kick|snare|hat", re.I)
    tracks_out = []
    for tid in order:
        meta = tracks_meta[tid]
        notes = sorted(notes_by_track[tid], key=lambda n: n["start"])
        clips = audio_by_track[tid]
        auto = auto_by_track.get(tid, [])
        if not notes and not clips and not auto:
            continue
        t = {"name": meta["name"][:24], "gainDb": meta["gainDb"], "pan": meta["pan"], "notes": notes}
        if auto:
            t["automation"] = auto
        if meta.get("source"):                      # sotadaw round-trip: the exact source spec
            t["source"] = meta["source"]
            if clips:
                t["audioClips"] = clips
            tracks_out.append(t)
            continue
        if clips:
            t["source"] = {"kind": "audio", "id": meta["name"][:16].lower() or "audio"}
            t["audioClips"] = clips
        else:
            drumish = bool(drum_re.search(meta["name"]))
            pitches = {n["pitch"] for n in notes}
            if not drumish and pitches and max(pitches) <= 60 and len(pitches) <= 8 and min(pitches) >= 35:
                drumish = True
            t["source"] = {"kind": "sample", "kit": "gm_drums" if drumish else "piano"}
        tracks_out.append(t)

    if not tracks_out:
        raise SystemExit("no notes or audio clips found (unsupported schema variant?)")

    max_beat = 4.0
    for t in tracks_out:
        for n in t["notes"]:
            max_beat = max(max_beat, n["start"] + n["len"])
        for c in t.get("audioClips", []):
            max_beat = max(max_beat, c["startBeat"] + c.get("lengthBeats", 4.0))
    for lanes in auto_by_track.values():             # a ride past the last note still needs world
        for lane in lanes:
            if lane["points"]:
                max_beat = max(max_beat, lane["points"][-1]["beat"])
    song = {"version": 2, "bpm": round(bpm, 2),
            "lengthBars": max(1, int(max_beat // 4 + 1)),
            "masterGainDb": 0,
            # master-chain LAW (never type "limiter" — its ceiling is non-functional;
            # fx_truepeak = the release wall, ceiling means OUTPUT dBTP)
            "master": [{"type": "faustfx", "id": "fx_trim", "params": {"level": -6}},
                       {"type": "faustfx", "id": "fx_truepeak", "params": {"ceiling": -1.2}}],
            "tracks": tracks_out}
    if auto_by_track.get("master"):
        song["automation"] = auto_by_track["master"]
    json.dump(song, open(song_path, "w"), indent=1)
    n_notes = sum(len(t["notes"]) for t in tracks_out)
    n_audio = sum(len(t.get("audioClips", [])) for t in tracks_out)
    n_lanes = sum(len(v) for v in auto_by_track.values())
    n_apts = sum(len(l["points"]) for v in auto_by_track.values() for l in v)
    msg = (f"imported {len(tracks_out)} tracks / {n_notes} notes / {n_audio} audio clips "
           f"/ {n_lanes} automation lanes ({n_apts} pts"
           + (f", {n_capped} master pts capped to 0dB" if n_capped else "")
           + f") @ {bpm:.1f}bpm -> {song_path}")
    print(msg)
    return msg

if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: dawproject_import.py <project.dawproject> <out_song.json>")
    import_dawproject(sys.argv[1], sys.argv[2])
