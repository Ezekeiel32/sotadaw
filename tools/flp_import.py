#!/usr/bin/env python3
"""BRIDGE: import an FL Studio project (.flp) into song.json via PyFLP.

  flp_import.py project.flp songs/out.json

Symbolic layer v1: tempo, channels->tracks, playlist pattern placements -> absolute
notes (ticks/PPQ -> beats). Drum-named channels map to gm_drums with the right GM key
(FL sampler channels usually hold one sound played at a constant pitch). If the
playlist yields nothing (or the schema resists), falls back to tiling patterns
sequentially so the material ALWAYS lands. Audio/automation lanes: next pass.
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

GM_KEY = [
    (re.compile(r"kick|bd\b|boom", re.I), 36),
    (re.compile(r"snare|sn\b|snr", re.I), 38),
    (re.compile(r"clap", re.I), 39),
    (re.compile(r"open.?hat|oh\b|open", re.I), 46),
    (re.compile(r"hat|hh\b|hi.?hat", re.I), 42),
    (re.compile(r"crash", re.I), 49),
    (re.compile(r"ride", re.I), 51),
    (re.compile(r"tom", re.I), 45),
    (re.compile(r"shaker|shk", re.I), 70),
    (re.compile(r"perc|rim|snap", re.I), 37),
    (re.compile(r"cow", re.I), 56),
]
DRUM_RE = re.compile(r"kick|snare|clap|hat|crash|ride|tom|perc|shaker|rim|cymbal|drum|808", re.I)

def gm_key_for(name):
    for rx, key in GM_KEY:
        if rx.search(name):
            return key
    return None

def import_flp(flp_path, song_path):
    import pyflp
    project = pyflp.parse(flp_path)
    bpm = float(getattr(project, "tempo", 120.0) or 120.0)
    ppq = int(getattr(project, "ppq", 96) or 96)

    def chan_name(ch, i):
        for attr in ("display_name", "name"):
            v = getattr(ch, attr, None)
            if v:
                return str(v)
        return f"channel_{i+1}"

    channels, chan_names = {}, {}
    try:
        for i, ch in enumerate(project.channels):
            iid = getattr(ch, "iid", i)
            channels[iid] = ch
            chan_names[iid] = chan_name(ch, i)
    except Exception as e:
        print(f"[flp] channel scan degraded: {e!r}", file=sys.stderr)

    def pattern_notes(pat):
        """[(channel_iid, start_ticks, len_ticks, key, vel)] within the pattern."""
        out = []
        try:
            for n in pat.notes:
                iid = getattr(n, "rack_channel", None)
                if iid is None:
                    iid = getattr(getattr(n, "channel", None), "iid", 0)
                key = int(getattr(n, "key", 60) or 60)
                vel = getattr(n, "velocity", None)
                vel = float(vel) / 128.0 if isinstance(vel, (int, float)) else 0.78
                out.append((iid, float(n.position or 0), float(n.length or ppq // 4),
                            key, max(0.05, min(1.0, vel))))
        except Exception as e:
            print(f"[flp] pattern '{getattr(pat, 'name', '?')}' notes degraded: {e!r}", file=sys.stderr)
        return out

    patterns = {}
    try:
        for pat in project.patterns:
            patterns[getattr(pat, "index", len(patterns))] = pattern_notes(pat)
    except Exception as e:
        print(f"[flp] pattern scan degraded: {e!r}", file=sys.stderr)

    # playlist placements (arrangement 0)
    notes_by_chan = {}
    placed = 0
    try:
        arrangements = list(getattr(project, "arrangements", []) or [])
        arr = arrangements[0] if arrangements else None
        if arr is not None:
            for tr in arr.tracks:
                for item in tr:
                    if bool(getattr(item, "muted", False)):
                        continue
                    pat = getattr(item, "pattern", None)
                    if pat is None:
                        continue
                    pidx = getattr(pat, "index", None)
                    content = patterns.get(pidx) if pidx is not None else pattern_notes(pat)
                    if not content:
                        continue
                    pos = float(getattr(item, "position", 0) or 0)
                    length = float(getattr(item, "length", 0) or 0)
                    for iid, nt, nl, key, vel in content:
                        if length > 0 and nt >= length:
                            continue                     # item trims the pattern
                        notes_by_chan.setdefault(iid, []).append(
                            {"start": round((pos + nt) / ppq, 4),
                             "len": round(max(0.05, nl / ppq), 4),
                             "pitch": key, "vel": round(vel, 3)})
                        placed += 1
    except Exception as e:
        print(f"[flp] playlist scan degraded: {e!r}", file=sys.stderr)

    if placed == 0:
        # fallback: tile patterns one after another so nothing is lost
        print("[flp] no playlist placements found — tiling patterns sequentially", file=sys.stderr)
        cursor = 0.0
        for pidx in sorted(patterns):
            content = patterns[pidx]
            if not content:
                continue
            span = max(nt + nl for _, nt, nl, _, _ in content) / ppq
            span = max(4.0, round(span / 4.0 + 0.499) * 4.0)
            for iid, nt, nl, key, vel in content:
                notes_by_chan.setdefault(iid, []).append(
                    {"start": round(cursor + nt / ppq, 4), "len": round(max(0.05, nl / ppq), 4),
                     "pitch": key, "vel": round(vel, 3)})
            cursor += span

    tracks_out = []
    for iid in sorted(notes_by_chan):
        notes = sorted(notes_by_chan[iid], key=lambda n: n["start"])
        if not notes:
            continue
        name = chan_names.get(iid, f"channel_{iid}")
        gm = gm_key_for(name)
        if gm is not None:
            for n in notes:
                n["pitch"] = gm                    # FL sampler channel = one sound; pin to its GM key
            src = {"kind": "sample", "kit": "gm_drums"}
        elif DRUM_RE.search(name):
            src = {"kind": "sample", "kit": "gm_drums"}
        else:
            src = {"kind": "sample", "kit": "piano"}
        tracks_out.append({"name": str(name)[:24], "source": src, "gainDb": -6.0, "notes": notes})

    if not tracks_out:
        raise SystemExit("no notes recovered from this .flp (send it to the dev — schema variant)")

    max_beat = max(n["start"] + n["len"] for t in tracks_out for n in t["notes"])
    song = {"version": 2, "bpm": round(bpm, 2),
            "lengthBars": max(1, int(max_beat // 4 + 1)),
            "masterGainDb": 0,
            # master-chain LAW (never type "limiter" — its ceiling is non-functional;
            # fx_truepeak = the release wall, ceiling means OUTPUT dBTP)
            "master": [{"type": "faustfx", "id": "fx_trim", "params": {"level": -6}},
                       {"type": "faustfx", "id": "fx_truepeak", "params": {"ceiling": -1.2}}],
            "tracks": tracks_out}
    json.dump(song, open(song_path, "w"), indent=1)
    n = sum(len(t["notes"]) for t in tracks_out)
    msg = f"imported {len(tracks_out)} channels / {n} notes @ {bpm:.1f}bpm (ppq {ppq}) -> {song_path}"
    print(msg)
    return msg

if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: flp_import.py <project.flp> <out_song.json>")
    import_flp(sys.argv[1], sys.argv[2])
