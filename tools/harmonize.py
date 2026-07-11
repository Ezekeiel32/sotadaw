#!/usr/bin/env python3
"""HARMONIZE — compose a NEW part that plays the song's OWN voted changes.

  harmonize.py <song> <role> [--track name] [--octave N] [--rhythm feel] [--write]

The chord lane could read (chordvote), transform (reharm), and match
(remix_import). The missing verb is COMPOSE FROM: given a song whose chords are
voted, generate a bass / pad / arp track that plays those exact changes, in the
song's key, landing as an editable track. Verification is self-consistent:
chordvote on the new part must read the song's own progression back.

roles:  bass  — root on the downbeat + a fifth/octave pickup (the feel decides)
        pad   — sustained triad (root/third/fifth) per bar, low velocity
        arp   — the triad as an up/down 8th- or 16th-note figure
rhythm: straight | offbeat | roll (bass) · whole | pulse (pad) · up | updown (arp)
"""
import argparse, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from chordvote import chord_map
from reharm import parse_chord, tones
import songname

VOICE = {"bass": "bass_warm", "pad": "pad_motion", "arp": "pluck", "melody": "pluck"}
BASE = {"bass": 36, "pad": 60, "arp": 72, "melody": 67}


def bass_notes(chords, base, rhythm):
    out = []
    for c in chords:
        r, q, dom7 = parse_chord(c["chord"])
        b = (c["bar"] - 1) * 4.0
        root = base + ((r - base) % 12)
        fifth = root + 7
        if rhythm == "roll":                       # boom-bap-ish 3-hit
            for beat, p in ((0, root), (1.5, root), (2.5, fifth)):
                out.append({"start": round(b + beat, 4), "len": 0.5, "pitch": p, "vel": 0.9})
        elif rhythm == "offbeat":                  # house/reggae in the holes
            for beat in (0.5, 1.5, 2.5, 3.5):
                out.append({"start": round(b + beat, 4), "len": 0.4, "pitch": root, "vel": 0.85})
        else:                                      # straight: root each beat
            for beat in range(4):
                out.append({"start": round(b + beat, 4), "len": 0.9,
                            "pitch": root if beat != 3 else fifth, "vel": 0.9})
    return out


def pad_notes(chords, base, rhythm):
    # VOICE-LED (f137, the M1 kernel's second consumer): pads HOLD common tones and
    # move by the least distance chord-to-chord — block root-position stacks read
    # as a beginner's left hand (gospel-lane truth: motion 9 vs 21 on real loops).
    from voicing import voice_pcs
    seqs, thirds, roots = [], [], []
    for c in chords:
        r, q, dom7 = parse_chord(c["chord"])
        t = tones(r, q, dom7)
        seqs.append([t[0] % 12, t[1] % 12, t[2] % 12])
        thirds.append(t[1] % 12); roots.append(t[0] % 12)
    voiced = voice_pcs(seqs, "smooth", lo=base, hi=base + 22, thirds=thirds, roots=roots)
    out = []
    for ci, c in enumerate(chords):
        b = (c["bar"] - 1) * 4.0
        pitches = voiced[ci]
        if rhythm == "pulse":
            for beat in range(4):
                for p in pitches:
                    out.append({"start": round(b + beat, 4), "len": 0.9, "pitch": p, "vel": 0.5})
        else:                                      # whole: one sustained chord/bar
            for p in pitches:
                out.append({"start": round(b, 4), "len": 3.95, "pitch": p, "vel": 0.5})
    return out


def arp_notes(chords, base, rhythm):
    out = []
    step = 0.5
    for c in chords:
        r, q, dom7 = parse_chord(c["chord"])
        b = (c["bar"] - 1) * 4.0
        t = tones(r, q, dom7)
        tri = [base + ((t[k] - base) % 12) for k in (0, 1, 2)] + [base + 12 + ((t[0] - base) % 12)]
        seq = tri + tri[::-1][1:-1] if rhythm == "updown" else tri
        n = int(4.0 / step)
        for i in range(n):
            p = seq[i % len(seq)]
            out.append({"start": round(b + i * step, 4), "len": round(step * 0.9, 4),
                        "pitch": p, "vel": 0.7})
    return out


def melody_notes(chords, base, rhythm, seed=0):
    """A SINGABLE lead over the changes: chord tones on strong beats, scale
    passing tones between, rests for breath, a contour that arcs — deterministic
    per (song, seed). NOT an arpeggio: the melody moves stepwise where it can and
    leaps to a chord tone at each bar so it always resolves harmonically.
    rhythm: flowing (8ths w/ rests) | sparse (quarter+half phrases) | busy (16ths)."""
    import random
    rng = random.Random(f"melody:{seed}:{len(chords)}")
    out = []
    MAJ = [0, 2, 4, 5, 7, 9, 11]                     # scale steps from the key root
    step = {"sparse": 1.0, "busy": 0.25}.get(rhythm, 0.5)
    prev = None
    for ci, c in enumerate(chords):
        r, q, dom7 = parse_chord(c["chord"])
        b = (c["bar"] - 1) * 4.0
        t = tones(r, q, dom7)
        chord_pcs = [t[k] % 12 for k in t]
        scale = [(r + s) % 12 for s in ([0, 2, 3, 5, 7, 8, 10] if q == "min" else MAJ)]
        beat = 0.0
        while beat < 4.0 - 1e-6:
            strong = abs(beat - round(beat)) < 1e-6 and int(round(beat)) % 2 == 0
            if not strong and rng.random() < (0.35 if rhythm != "busy" else 0.18):
                beat += step; prev = None       # a rest — breath (busy breathes less)
                continue
            oct0 = (base // 12) * 12            # true octave anchor (base is a pitch,
            if strong or prev is None:           # NOT a pitch class — the +7 bug)
                cands = [oct0 + pc + 12 * o for pc in chord_pcs for o in (0, 1, 2)]
            else:                                # a scale step from prev (stepwise motion)
                cands = [oct0 + pc + 12 * o for pc in scale for o in (0, 1, 2)]
            if prev is not None:
                cands.sort(key=lambda p: abs(p - prev) + (3 if abs(p - prev) > 7 else 0))
                pitch = cands[min(len(cands) - 1, rng.randint(0, 2))]
            else:
                pitch = min(cands, key=lambda p: abs(p - (base + 7)))
            dur = step * (2 if (rhythm == "sparse" and strong) else 1) * 0.92
            out.append({"start": round(b + beat, 4), "len": round(dur, 4),
                        "pitch": int(pitch), "vel": round(0.7 + 0.15 * strong, 3)})
            prev = pitch
            beat += step * (2 if (rhythm == "sparse" and strong) else 1)
    return out


GEN = {"bass": bass_notes, "pad": pad_notes, "arp": arp_notes, "melody": melody_notes}

# the "one change per section" prototype law: a part's DENSITY follows the
# arrangement. label -> (melody/arp feel, bass feel, pad feel). Substring-matched.
SECTION_FEEL = [
    (("intro", "start"),       ("sparse",  "straight", "whole")),
    (("break", "breakdown", "quiet"), ("sparse", "straight", "whole")),
    (("build", "rise", "pre"), ("flowing", "offbeat",  "pulse")),
    (("drop", "chorus", "hook", "main", "peak", "finale"), ("busy", "roll", "pulse")),
    (("verse",),               ("flowing", "straight", "whole")),
    (("outro",),               ("sparse",  "straight", "whole")),
]


def feel_for(label, role):
    l = str(label).lower()
    idx = {"melody": 0, "arp": 0, "bass": 1, "pad": 2}.get(role, 0)
    for keys, feels in SECTION_FEEL:
        if any(k in l for k in keys):
            return feels[idx]
    return None


def harmonize(song, role, track_name=None, octave=0, rhythm=None, seed=0, sectioned=False):
    chords = song.get("chords") or chord_map(song)
    if not chords:
        raise SystemExit("no chords voteable — this song has no harmonic content to follow")
    base = BASE[role] + 12 * octave
    default_rhythm = {"bass": "straight", "pad": "whole", "arp": "up",
                      "melody": "flowing"}[role]
    sections = song.get("sections", [])
    if sectioned and len(sections) >= 2:
        # generate each section with the feel its label implies (arrangement breathes)
        bounds = [(float(sc["startBar"]), sc.get("name", "")) for sc in
                  sorted(sections, key=lambda x: float(x["startBar"]))]
        span = [(bounds[i][0], bounds[i + 1][0] if i + 1 < len(bounds)
                 else float(song.get("lengthBars", chords[-1]["bar"])), bounds[i][1])
                for i in range(len(bounds))]
        notes, feels_used = [], []
        for start_bar, end_bar, label in span:
            seg = [c for c in chords if start_bar < c["bar"] <= end_bar or
                   (c["bar"] - 1 >= start_bar and c["bar"] - 1 < end_bar)]
            if not seg:
                continue
            feel = feel_for(label, role) or default_rhythm
            feels_used.append(f"{label.strip()}={feel}")
            part = (melody_notes(seg, base, feel, seed) if role == "melody"
                    else GEN[role](seg, base, feel))
            notes += part
    else:
        feels_used = None
        if role == "melody":
            notes = melody_notes(chords, base, rhythm or default_rhythm, seed)
        else:
            notes = GEN[role](chords, base, rhythm or default_rhythm)
    tname = track_name or role
    song["tracks"] = [t for t in song.get("tracks", []) if t.get("name") != tname]
    song["tracks"].append({"name": tname, "source": {"kind": "faust", "id": VOICE[role]},
                           "gainDb": -8 if role != "bass" else -5, "pan": 0.0, "notes": notes})
    return {"role": role, "track": tname, "notes": len(notes),
            "chords": [c["chord"] for c in chords[:8]],
            "sectioned": feels_used}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("song"); ap.add_argument("role", choices=list(GEN))
    ap.add_argument("--track", default=None)
    ap.add_argument("--octave", type=int, default=0)
    ap.add_argument("--rhythm", default=None)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--sectioned", action="store_true", help="density follows the arrangement (verse sparse, drop busy)")
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    name = songname.resolve(a.song)
    path = os.path.join(ROOT, "songs", f"{name}.json")
    song = json.load(open(path))
    rep = harmonize(song, a.role, a.track, a.octave, a.rhythm, a.seed, a.sectioned)
    if a.write:
        json.dump(song, open(path, "w"), indent=1)
        rep["written"] = f"songs/{name}.json"
    print(f"[harmonize] {a.role} '{rep['track']}': {rep['notes']} notes over "
          f"{' '.join(rep['chords'])}"
          + (f" -> {rep['written']}" if a.write else " (dry-run; --write to keep)"))
    print("HARMONIZE_JSON " + json.dumps(rep))


if __name__ == "__main__":
    main()
