#!/usr/bin/env python3
"""BRIDGE OUT: song.json -> Ableton Live .als — "produce here, finish in Live".

Emits a gzipped LiveSet (Live 11/12 schema shape as parsed from real sets by
our own als_import.py): tempo, one MidiTrack per note-bearing track, one
arrangement MidiClip spanning the song, notes grouped into KeyTracks.
Audio tracks are skipped (listed) — the SYMBOLIC layer migrates, v1.

  als_export.py songs/x.json x.als
Round-trip law: als_import(als_export(song)) must preserve bpm, track count,
note count, pitch multiset and start times (velocities quantize to /127).
"""
import gzip, json, os, sys
import xml.etree.ElementTree as ET


def _sub(parent, tag, **attrs):
    e = ET.SubElement(parent, tag)
    for k, v in attrs.items():
        e.set(k, str(v))
    return e


def export_als(song_path, als_path):
    song = json.load(open(song_path))
    bpm = float(song.get("bpm", 120))
    length_beats = float(song.get("lengthBars", 8)) * 4.0

    root = ET.Element("Ableton", {
        "MajorVersion": "5", "MinorVersion": "12.0_12049",
        "SchemaChangeCount": "3", "Creator": "SOTA DAW", "Revision": ""})
    ls = _sub(root, "LiveSet")
    # tempo lives on the main track (Live 12 name; importer also reads MasterTrack)
    main = _sub(ls, "MainTrack")
    dc = _sub(main, "DeviceChain")
    mixer = _sub(dc, "Mixer")
    tempo = _sub(mixer, "Tempo")
    _sub(tempo, "Manual", Value=f"{bpm:.6f}")

    def _envelopes(parent, autos):
        """V18 automation out: FloatEvents carry the points (Live-shaped); Sotadaw*
        children carry target + per-point curves for OUR exact round-trip (Live
        ignores unknown elements; real-Live Pointee wiring lands with a fixture)."""
        if not autos:
            return 0
        env_root = _sub(parent, "AutomationEnvelopes")
        envs = _sub(env_root, "Envelopes")
        for ai, a in enumerate(autos):
            pts = a.get("points") or []
            if not pts:
                continue
            ae = _sub(envs, "AutomationEnvelope", Id=str(ai))
            et = _sub(ae, "EnvelopeTarget")
            _sub(et, "PointeeId", Value="0")
            auto = _sub(ae, "Automation")
            evs = _sub(auto, "Events")
            for pi, p in enumerate(sorted(pts, key=lambda q: float(q.get("beat", 0)))):
                _sub(evs, "FloatEvent", Id=str(pi + 1),
                     Time=f"{float(p.get('beat', 0)):.6f}",
                     Value=f"{float(p.get('v', 0)):.6f}")
            _sub(ae, "SotadawTarget", Value=str(a.get("target", "")))
            _sub(ae, "SotadawCurves",
                 Value=",".join(f"{float(p.get('curve', 0)):.4f}"
                                for p in sorted(pts, key=lambda q: float(q.get("beat", 0)))))
        return len(autos)

    env_count = _envelopes(main, song.get("automation") or [])

    tracks_el = _sub(ls, "Tracks")
    skipped, exported = [], 0
    for ti, t in enumerate(song.get("tracks", [])):
        notes = t.get("notes") or []
        name = str(t.get("name", f"track_{ti+1}"))
        if not notes:
            skipped.append(name)
            continue
        mt = _sub(tracks_el, "MidiTrack", Id=str(10 + ti))
        nm = _sub(mt, "Name")
        _sub(nm, "EffectiveName", Value=name)
        _sub(nm, "UserName", Value=name)
        src = t.get("source") or {}
        if src.get("kind") not in (None, "faust") or src.get("id") not in (None, "pluck"):
            # Live's track info-text: visible as a note in Ableton, restorable by us
            _sub(nm, "Annotation", Value="sotadaw:source " + json.dumps(src, separators=(",", ":")))
        tdc = _sub(mt, "DeviceChain")
        seq = _sub(tdc, "MainSequencer")
        ct = _sub(seq, "ClipTimeable")
        arr = _sub(ct, "ArrangerAutomation")
        events = _sub(arr, "Events")
        clip = _sub(events, "MidiClip", Id="0", Time="0")
        _sub(clip, "CurrentStart", Value="0")
        _sub(clip, "CurrentEnd", Value=f"{length_beats:.4f}")
        loop = _sub(clip, "Loop")
        _sub(loop, "LoopStart", Value="0")
        _sub(loop, "LoopEnd", Value=f"{length_beats:.4f}")
        _sub(loop, "StartRelative", Value="0")
        _sub(loop, "LoopOn", Value="true")
        cn = _sub(clip, "Name")
        cn.set("Value", name)
        notes_el = _sub(clip, "Notes")
        kts = _sub(notes_el, "KeyTracks")
        by_pitch = {}
        for n in notes:
            by_pitch.setdefault(int(n["pitch"]), []).append(n)
        nid = 1
        for ki, (pitch, ns) in enumerate(sorted(by_pitch.items())):
            kt = _sub(kts, "KeyTrack", Id=str(ki))
            kn = _sub(kt, "Notes")
            for n in sorted(ns, key=lambda x: float(x["start"])):
                _sub(kn, "MidiNoteEvent",
                     Time=f"{float(n['start']):.6f}",
                     Duration=f"{max(0.05, float(n.get('len', 0.25))):.6f}",
                     Velocity=str(max(1, min(127, round(float(n.get('vel', 0.8)) * 127)))),
                     IsEnabled="true", NoteId=str(nid))
                nid += 1
            _sub(kt, "MidiKey", Value=str(pitch))
        env_count += _envelopes(mt, t.get("automation") or [])
        exported += 1

    xml = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    with gzip.open(als_path, "wb") as f:
        f.write(xml)
    return (f"{als_path}: {exported} MIDI tracks @ {bpm:.0f}bpm, {env_count} automation envelopes"
            + (f" (skipped no-note/audio: {', '.join(skipped[:6])})" if skipped else ""))


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    print(export_als(sys.argv[1], sys.argv[2]))
