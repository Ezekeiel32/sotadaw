#!/usr/bin/env python3
"""BRIDGE OUT (trust-keeping): export song.json -> .dawproject
(Bitwig / Cubase / Nuendo / Studio One open exchange format).

  dawproject_export.py songs/x.json x.dawproject

Notes, tempo, per-track volume/pan, and audio clips (embedded into the archive
with linear warp points) travel. "Produce in SOTA, finish anywhere."
"""
import json, math, os, sys, zipfile
from xml.sax.saxutils import escape, quoteattr

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def export_dawproject(song_path, out_path):
    song = json.load(open(song_path))
    bpm = float(song.get("bpm", 120))
    beats = float(song.get("lengthBars", 4)) * 4.0
    spb = 60.0 / bpm
    tracks = song.get("tracks", [])

    ids = iter(range(10000))
    nid = lambda: f"id{next(ids)}"

    struct_xml, lanes_xml, audio_files = [], [], []
    for t in tracks:
        tid = nid()
        name = escape(str(t.get("name", "track")))
        kind = (t.get("source") or {}).get("kind", "faust")
        gain_lin = 10.0 ** (float(t.get("gainDb", 0)) / 20.0)
        pan_norm = min(1.0, max(0.0, float(t.get("pan", 0)) / 2.0 + 0.5))
        content = "audio" if kind == "audio" else "notes"
        # sotadaw:source carries the full source spec (vst3 params/presets etc.):
        # standard readers ignore unknown attributes; our importer restores it.
        src = t.get("source") or {}
        src_attr = ""
        if src.get("kind") not in (None, "faust") or src.get("id") not in (None, "pluck"):
            src_attr = f' sotadaw:source={quoteattr(json.dumps(src, separators=(",", ":")))}'
        struct_xml.append(
            f'<Track contentType="{content}" loaded="true" id="{tid}" name={quoteattr(str(t.get("name","track")))}{src_attr}>'
            f'<Channel audioChannels="2" role="regular" solo="false" id="{nid()}">'
            f'<Volume unit="linear" value="{gain_lin:.6f}" id="{nid()}"/>'
            f'<Pan unit="normalized" value="{pan_norm:.4f}" id="{nid()}"/>'
            f'</Channel></Track>')

        clips = []
        notes = t.get("notes", [])
        if notes:
            note_xml = "".join(
                f'<Note time="{float(n["start"]):.4f}" duration="{max(0.05, float(n["len"])):.4f}" '
                f'channel="0" key="{int(n["pitch"])}" vel="{min(1.0, max(0.0, float(n["vel"]))):.3f}" rel="0.5"/>'
                for n in notes)
            clips.append(f'<Clip time="0.0" duration="{beats:.4f}" playStart="0.0" name={quoteattr(str(t.get("name","clip")))}>'
                         f'<Notes id="{nid()}">{note_xml}</Notes></Clip>')
        for ac in t.get("audioClips", []):
            f = ac.get("file", "")
            src = f if os.path.isabs(f) else os.path.join(ROOT, f)
            if not os.path.exists(src):
                continue
            arcname = "audio/" + os.path.basename(f)
            audio_files.append((src, arcname))
            start = float(ac.get("startBeat", 0))
            len_b = float(ac.get("lengthBeats", 0)) or (beats - start)
            off = float(ac.get("offsetSec", 0))
            # two linear warp points define a 1:1 (no-stretch) mapping
            clips.append(
                f'<Clip time="{start:.4f}" duration="{len_b:.4f}" playStart="0.0">'
                f'<Warps contentTimeUnit="seconds" timeUnit="beats" id="{nid()}">'
                f'<Audio file="{escape(arcname)}" channels="2" duration="{len_b * spb + off:.4f}" '
                f'sampleRate="44100" algorithm="stretch" id="{nid()}"/>'
                f'<Warp time="0.0" contentTime="{off:.4f}"/>'
                f'<Warp time="{len_b:.4f}" contentTime="{off + len_b * spb:.4f}"/>'
                f'</Warps></Clip>')
        if clips:
            lanes_xml.append(f'<Lanes track="{tid}" id="{nid()}"><Clips id="{nid()}">'
                             + "".join(clips) + "</Clips></Lanes>")

    title = os.path.splitext(os.path.basename(song_path))[0]
    project = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<Project version="1.0" xmlns:sotadaw="https://sotadaw.local/ns">'
        '<Application name="SOTA DAW" version="0.4"/>'
        f'<Transport><Tempo unit="bpm" value="{bpm:.2f}" min="20" max="999" id="{nid()}"/>'
        f'<TimeSignature numerator="4" denominator="4" id="{nid()}"/></Transport>'
        '<Structure>' + "".join(struct_xml) + '</Structure>'
        f'<Arrangement id="{nid()}"><Lanes timeUnit="beats" id="{nid()}">'
        + "".join(lanes_xml) +
        '</Lanes></Arrangement></Project>')
    metadata = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                f'<MetaData><Title>{escape(title)}</Title></MetaData>')

    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("project.xml", project)
        z.writestr("metadata.xml", metadata)
        for src, arc in audio_files:
            z.write(src, arc)
    n = sum(len(t.get("notes", [])) for t in tracks)
    msg = (f"exported {len(tracks)} tracks / {n} notes / {len(audio_files)} audio files "
           f"@ {bpm:.1f}bpm -> {out_path}")
    print(msg)
    return msg

if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: dawproject_export.py <song.json> <out.dawproject>")
    export_dawproject(sys.argv[1], sys.argv[2])
