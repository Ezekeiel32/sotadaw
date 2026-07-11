#!/usr/bin/env python3
"""THE BRIDGE: import an Ableton Live project (.als) into song.json — symbolic, editable, ours.

.als = gzipped XML (LiveSet). We extract: tempo, MIDI tracks (names, notes with
time/duration/velocity/key), and map drum-ish tracks to gm_drums, melodic to piano kit
(sources are reassignable in-app; the ARRANGEMENT is what migrates).

  als_import.py project.als songs/imported.json
Handles Live 9-12 schema variants (MidiNoteEvent under KeyTrack, Time/Duration in beats).
Audio tracks are listed but skipped (v1 imports the symbolic layer).
"""
import gzip, json, os, re, sys
import xml.etree.ElementTree as ET

def val(el, path, attr="Value", default=None):
    n = el.find(path)
    return n.get(attr) if n is not None and n.get(attr) is not None else default

def import_als(als_path, song_path):
    raw = gzip.open(als_path, "rb").read()
    root = ET.fromstring(raw)
    live = root  # <Ableton><LiveSet>...
    ls = root.find("LiveSet")
    if ls is None:
        ls = root

    # tempo: Live 9-11 LiveSet/MasterTrack/.../Tempo/Manual; Live 12 moved MasterTrack->MainTrack
    bpm = 120.0
    for mt_name in ("MasterTrack", "MainTrack"):
        mt = ls.find(mt_name)
        if mt is None:
            continue
        for tempo in mt.iter("Tempo"):
            man = tempo.find("Manual")
            if man is not None and man.get("Value"):
                bpm = float(man.get("Value"))
                break

    def _read_envelopes(el):
        """V12 automation in: FloatEvents -> points; SotadawTarget/Curves restore OUR
        exact objects; foreign envelopes (no Sotadaw carrier) surface as
        unresolved[] until real-Live Pointee wiring lands (needs a Live fixture)."""
        autos, unresolved = [], 0
        for ae in el.iter("AutomationEnvelope"):
            tgt_el = ae.find("SotadawTarget")
            target = tgt_el.get("Value") if tgt_el is not None else None
            curves = []
            cv = ae.find("SotadawCurves")
            if cv is not None and cv.get("Value"):
                try:
                    curves = [float(x) for x in cv.get("Value").split(",")]
                except ValueError:
                    curves = []
            pts = []
            for i, fe in enumerate(ae.iter("FloatEvent")):
                try:
                    p = {"beat": round(float(fe.get("Time", 0)), 4),
                         "v": round(float(fe.get("Value", 0)), 4)}
                except (TypeError, ValueError):
                    continue
                if i < len(curves) and abs(curves[i]) > 1e-9:
                    p["curve"] = curves[i]
                pts.append(p)
            if not pts:
                continue
            if target:
                autos.append({"target": target, "points": pts})
            else:
                unresolved += 1
        return autos, unresolved

    song_autos, song_unresolved = [], 0
    for mt_name in ("MasterTrack", "MainTrack"):
        mt = ls.find(mt_name)
        if mt is not None:
            song_autos, song_unresolved = _read_envelopes(mt)
            if song_autos or song_unresolved:
                break

    tracks_out, skipped_audio = [], []
    unresolved_total = song_unresolved
    tracks_el = ls.find("Tracks")
    if tracks_el is None:
        raise SystemExit("no Tracks element — not a LiveSet?")

    for tr in tracks_el:
        tag = tr.tag  # MidiTrack | AudioTrack | ReturnTrack | GroupTrack
        name = None
        nm = tr.find("Name/EffectiveName")
        if nm is None:
            nm = tr.find("Name/UserName")
        if nm is not None:
            name = nm.get("Value") or None
        src_override = None
        an = tr.find("Name/Annotation")
        if an is not None and str(an.get("Value", "")).startswith("sotadaw:source "):
            try:
                src_override = json.loads(an.get("Value")[len("sotadaw:source "):])
            except Exception:
                src_override = None
        if tag == "AudioTrack":
            skipped_audio.append(name or "audio")
            continue
        if tag != "MidiTrack":
            continue

        notes = []
        # all MidiClips on the track (arrangement + session slots), notes inside KeyTracks
        for clip in tr.iter("MidiClip"):
            try:
                clip_start = float(clip.get("Time", val(clip, "CurrentStart", default="0") or 0))
            except (TypeError, ValueError):
                clip_start = 0.0
            cs = val(clip, "CurrentStart")
            if cs is not None:
                try:
                    clip_start = float(cs)
                except ValueError:
                    pass
            loop_start = 0.0
            lsn = clip.find("Loop/LoopStart")
            if lsn is not None and lsn.get("Value"):
                loop_start = float(lsn.get("Value"))
            for kt in clip.iter("KeyTrack"):
                key = val(kt, "MidiKey", default="60")
                try:
                    pitch = int(key)
                except (TypeError, ValueError):
                    continue
                for ev in kt.iter("MidiNoteEvent"):
                    try:
                        t = float(ev.get("Time", 0))
                        d = float(ev.get("Duration", 0.25))
                        v = float(ev.get("Velocity", 100))
                    except (TypeError, ValueError):
                        continue
                    if ev.get("IsEnabled", "true").lower() == "false":
                        continue
                    start = clip_start + (t - loop_start)
                    if start < 0:
                        continue
                    notes.append({"start": round(start, 4), "len": round(max(0.05, d), 4),
                                  "pitch": pitch, "vel": round(min(1.0, v / 127.0), 3)})
        if not notes:
            continue
        notes.sort(key=lambda n: n["start"])
        tname = (name or f"midi_{len(tracks_out)+1}").strip()
        drumish = bool(re.search(r"drum|kit|beat|perc|808|kick|snare|hat", tname.lower()))
        # heuristic: GM drum range + narrow pitch set also suggests drums
        pitches = {n["pitch"] for n in notes}
        if not drumish and pitches and max(pitches) <= 60 and len(pitches) <= 8 and min(pitches) >= 35:
            drumish = True
        t_autos, t_unres = _read_envelopes(tr)
        unresolved_total += t_unres
        entry = {
            "name": tname[:24],
            "source": src_override if src_override
                      else {"kind": "sample", "kit": "gm_drums" if drumish else "piano"},
            "gainDb": -6.0,
            "notes": notes}
        if t_autos:
            entry["automation"] = t_autos
        tracks_out.append(entry)

    if not tracks_out:
        raise SystemExit("no MIDI notes found (audio-only set? unsupported schema?)")

    max_beat = max(n["start"] + n["len"] for t in tracks_out for n in t["notes"])
    song = {"version": 2, "bpm": round(bpm, 2),
            "lengthBars": max(1, int(max_beat // 4 + 1)),
            "masterGainDb": 0,
            # master-chain LAW (never type "limiter" — its ceiling is non-functional;
            # fx_truepeak = the release wall, ceiling means OUTPUT dBTP)
            "master": [{"type": "faustfx", "id": "fx_trim", "params": {"level": -6}},
                       {"type": "faustfx", "id": "fx_truepeak", "params": {"ceiling": -1.2}}],
            "tracks": tracks_out}
    if song_autos:
        song["automation"] = song_autos
    json.dump(song, open(song_path, "w"), indent=1)
    n = sum(len(t["notes"]) for t in tracks_out)
    n_env = len(song_autos) + sum(len(t.get("automation", [])) for t in tracks_out)
    msg = (f"imported {len(tracks_out)} MIDI tracks / {n} notes / {n_env} automation envelopes"
           f" @ {bpm:.1f}bpm -> {song_path}"
           + (f" ({unresolved_total} foreign envelopes unresolved — Live Pointee wiring pending)" if unresolved_total else "")
           + (f" (skipped {len(skipped_audio)} audio tracks: {', '.join(skipped_audio[:5])})" if skipped_audio else ""))
    print(msg)
    return msg

if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: als_import.py <project.als> <out_song.json>")
    import_als(sys.argv[1], sys.argv[2])
