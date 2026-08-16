#!/usr/bin/env python3
"""BRIDGE OUT (trust-keeping): export song.json -> .dawproject
(Bitwig / Cubase / Nuendo / Studio One open exchange format).

  dawproject_export.py songs/x.json x.dawproject

Notes, tempo, per-track volume/pan, audio clips (embedded, linear warp points)
AND automation travel. "Produce in SOTA, finish anywhere."

Automation (v2): track gainDb/pan lanes + song-level masterGainDb become
<Points><Target parameter=id-of-Volume/Pan/> RealPoint lanes (a role="master"
track carries the master fader). Curve translation is ENGINE-TRUE via
tools/tracktion_curve.py (the 1:1 port of the vendored bezier the audio
thread plays): c==0 -> one linear point; c=+1 -> interpolation="hold"
(exact); c=-1 -> step-then-hold (1-tick shoulder point); other curves
densify to 8 engine-sampled linear points. fx[i].*/source.* targets have no
device twin in the open format — skipped and COUNTED in the output line.
"""
import json, math, os, sys, zipfile
from xml.sax.saxutils import escape, quoteattr

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tracktion_curve

DENSIFY = 8            # engine-sampled interior points per curved segment
TICK = 1.0 / 960.0     # the step-then-hold shoulder

def _points_xml(lane, target_id, to_native, nid):
    """One song.json automation lane -> a <Points> element, engine-true."""
    pts = sorted(({"beat": float(p.get("beat", 0)), "v": float(p.get("v", 0)),
                   "curve": float(p.get("curve", 0.0))}
                  for p in lane.get("points", []) if isinstance(p, dict)),
                 key=lambda p: p["beat"])
    if not pts:
        return "", 0
    rp = []

    def emit(beat, v, interp="linear"):
        rp.append(f'<RealPoint time="{beat:.6f}" value="{to_native(v):.6f}" '
                  f'interpolation="{interp}"/>')

    for i, p in enumerate(pts):
        if i == len(pts) - 1:
            emit(p["beat"], p["v"])
            break
        nxt = pts[i + 1]
        c = p["curve"]
        if c >= 0.999:
            emit(p["beat"], p["v"], "hold")            # exact: hold-then-step
        elif c <= -0.999:
            emit(p["beat"], p["v"])                    # step-then-hold: 1-tick shoulder
            emit(min(p["beat"] + TICK, nxt["beat"]), nxt["v"])
        elif c != 0.0:
            emit(p["beat"], p["v"])
            span = nxt["beat"] - p["beat"]
            for k in range(1, DENSIFY + 1):
                x = p["beat"] + span * k / (DENSIFY + 1)
                emit(x, tracktion_curve.curve_value(
                    x, p["beat"], p["v"], nxt["beat"], nxt["v"], c))
        else:
            emit(p["beat"], p["v"])
    return (f'<Points id="{nid()}" unit="linear">'
            f'<Target parameter="{target_id}"/>' + "".join(rp) + "</Points>"), len(rp)


def export_dawproject(song_path, out_path):
    song = json.load(open(song_path))
    bpm = float(song.get("bpm", 120))
    beats = float(song.get("lengthBars", 4)) * 4.0
    spb = 60.0 / bpm
    tracks = song.get("tracks", [])

    ids = iter(range(10000))
    nid = lambda: f"id{next(ids)}"
    db2lin = lambda v: 10.0 ** (float(v) / 20.0)
    pan2norm = lambda v: min(1.0, max(0.0, float(v) / 2.0 + 0.5))
    n_lanes = n_points = n_skipped = 0

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
        vol_id, pan_id = nid(), nid()
        struct_xml.append(
            f'<Track contentType="{content}" loaded="true" id="{tid}" name={quoteattr(str(t.get("name","track")))}{src_attr}>'
            f'<Channel audioChannels="2" role="regular" solo="false" id="{nid()}">'
            f'<Volume unit="linear" value="{gain_lin:.6f}" id="{vol_id}"/>'
            f'<Pan unit="normalized" value="{pan_norm:.4f}" id="{pan_id}"/>'
            f'</Channel></Track>')

        points = []
        for lane in t.get("automation", []) or []:
            if not isinstance(lane, dict):
                continue
            tgt = str(lane.get("target", ""))
            if tgt == "gainDb":
                xml, n = _points_xml(lane, vol_id, db2lin, nid)
            elif tgt == "pan":
                xml, n = _points_xml(lane, pan_id, pan2norm, nid)
            else:
                n_skipped += 1        # fx[i].*/source.*: no device twin in the open format
                continue
            if xml:
                points.append(xml)
                n_lanes += 1
                n_points += n

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
        if clips or points:
            lanes_xml.append(f'<Lanes track="{tid}" id="{nid()}">'
                             + (f'<Clips id="{nid()}">' + "".join(clips) + "</Clips>" if clips else "")
                             + "".join(points) + "</Lanes>")

    # a role="master" track carries the master fader so masterGainDb rides can travel
    master_lanes = [l for l in (song.get("automation") or [])
                    if isinstance(l, dict) and str(l.get("target")) == "masterGainDb"]
    n_skipped += sum(1 for l in (song.get("automation") or [])
                     if isinstance(l, dict) and str(l.get("target")) != "masterGainDb")
    if master_lanes:
        mid, mvol_id = nid(), nid()
        struct_xml.append(
            f'<Track contentType="audio" loaded="true" id="{mid}" name="Master">'
            f'<Channel audioChannels="2" role="master" solo="false" id="{nid()}">'
            f'<Volume unit="linear" value="{10.0 ** (float(song.get("masterGainDb", 0)) / 20.0):.6f}" id="{mvol_id}"/>'
            f'</Channel></Track>')
        mpoints = []
        for lane in master_lanes:
            xml, n = _points_xml(lane, mvol_id, db2lin, nid)
            if xml:
                mpoints.append(xml)
                n_lanes += 1
                n_points += n
        if mpoints:
            lanes_xml.append(f'<Lanes track="{mid}" id="{nid()}">' + "".join(mpoints) + "</Lanes>")

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
           f"/ {n_lanes} automation lanes ({n_points} pts"
           + (f", {n_skipped} fx/source lanes have no open-format twin — kept in song.json only" if n_skipped else "")
           + f") @ {bpm:.1f}bpm -> {out_path}")
    print(msg)
    return msg

if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: dawproject_export.py <song.json> <out.dawproject>")
    export_dawproject(sys.argv[1], sys.argv[2])
