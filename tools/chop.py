#!/usr/bin/env python3
"""chop.py — THE CHOP: slice any audio into a playable sampler kit (MPC/FL heritage,
manifesto: full control over samplers). Onset-detected slices land as chromatic pads
from C2 (36) — one pad per key, sequenceable like any kit, agent- and hand-playable.

  chop.py <audio> <kit_name> [--slices 16] [--from-sec A] [--to-sec B] [--grid N]

  --grid N  = ignore onsets, cut N equal slices (breakbeat style)
  --melodic [P] = single-zone instrument instead of pads: slice P (default the
                  longest) maps across the whole keyboard, root pitch auto-detected
                  — the classic 'sample one note, play it melodically' move

Full flip workflow: import_song_audio (stems) -> chop the drums/other stem ->
play pads. Slices get 3ms/25ms edge fades (no clicks); kit.json is the standard
sampler contract (kits/<name>/), instantly available to {"kind":"sample","kit":...}.

THE GROOVE-BACK (CC3-6 fabric): --groove returns the source's OWN pattern as
notes — every slice re-triggered at its original time, velocity from its peak.
Render the notes and the loop plays back; EDIT the notes and the loop is yours
(rearrange, half-time, swap pads) — audio in, symbols out. --preview writes
songs/_chop_<kit>.json (renderable reconstruction); --song S --track T injects
the groove track straight into an arrangement. Works retroactively on any
chopped kit: timing/length/velocity live in kit.json per slice.
"""
import argparse, json, math, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_audio(path):
    import numpy as np
    import soundfile as sf
    x, sr = sf.read(path, always_2d=True)
    return x.mean(axis=1), sr, x.shape[1]


def detect_onsets(x, sr, max_slices):
    import numpy as np
    hop = 512
    n = (len(x) // hop) * hop
    if n < hop * 8:
        return [0]
    frames = x[:n].reshape(-1, hop)
    env = np.sqrt((frames ** 2).mean(axis=1))
    strength = np.maximum(0, np.diff(env, prepend=env[0]))
    if strength.max() <= 0:
        return [0]
    order = np.argsort(strength)[::-1]
    min_gap = int(0.12 * sr / hop)
    picked = []
    for i in order:
        if strength[i] < 0.1 * strength.max():
            break
        if all(abs(i - j) >= min_gap for j in picked):
            picked.append(int(i))
        if len(picked) >= max_slices:
            break
    if not picked:
        return [0]
    # backtrack each onset to the local energy valley (catch the transient head)
    starts = []
    for i in sorted(picked):
        j = i
        while j > 0 and env[j - 1] < env[j]:
            j -= 1
        starts.append(j * hop)
    return sorted(set(starts))


def detect_root(seg, sr):
    """Dominant pitch (60-1200Hz FFT peak, harmonic-folded) -> nearest MIDI note."""
    import numpy as np
    S = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
    f = np.fft.rfftfreq(len(seg), 1 / sr)
    lo, hi = np.searchsorted(f, 60), np.searchsorted(f, 1200)
    pk = f[lo + int(np.argmax(S[lo:hi]))]
    sub = pk / 2.0                       # fold down if the fundamental is quieter
    if lo < np.searchsorted(f, sub) and S[np.searchsorted(f, sub)] > 0.3 * S[np.searchsorted(f, pk)]:
        pk = sub
    import math
    return int(round(69 + 12 * math.log2(pk / 440.0))), round(float(pk), 1)


def chop(audio, kit_name, slices=16, from_sec=0.0, to_sec=None, grid=None, melodic=None):
    import numpy as np
    import soundfile as sf
    src = audio if os.path.isabs(audio) else os.path.join(ROOT, audio)
    if not os.path.exists(src):
        return f"no such file: {audio}"
    x, sr, _ = load_audio(src)
    a = int(from_sec * sr)
    b = int(to_sec * sr) if to_sec else len(x)
    x = x[a:b]
    if len(x) < sr // 4:
        return "audio region too short"
    if grid:
        starts = [int(k * len(x) / grid) for k in range(grid)]
    else:
        starts = detect_onsets(x, sr, slices)
    if len(starts) < 2:
        return "no onsets found — try --grid 8"
    starts = starts[:slices]
    kit_dir = os.path.join(ROOT, "kits", kit_name)
    os.makedirs(kit_dir, exist_ok=True)
    if melodic is not None:                      # single-zone melodic instrument
        import numpy as np
        import soundfile as sf
        segs = [(s_, (starts[k + 1] if k + 1 < len(starts) else len(x)))
                for k, s_ in enumerate(starts)]
        idx = (int(melodic) - 1) if int(melodic) > 0 else int(np.argmax([e - s_ for s_, e in segs]))
        idx = max(0, min(idx, len(segs) - 1))
        s_, e = segs[idx]
        seg = x[s_:min(e, s_ + int(4.0 * sr))].copy()
        fi, fo = int(0.003 * sr), min(int(0.025 * sr), len(seg) // 4)
        seg[:fi] *= np.linspace(0, 1, fi)
        seg[-fo:] *= np.linspace(1, 0, fo)
        root, hz = detect_root(seg, sr)
        sf.write(os.path.join(kit_dir, "zone.wav"),
                 (np.clip(seg, -1, 1) * 32767).astype("<i2"), sr, subtype="PCM_16")
        json.dump({"kind": "melodic", "source": os.path.relpath(src, ROOT) if src.startswith(ROOT) else src,
                   "samples": [{"file": "zone.wav", "keyNote": root, "minNote": 0,
                                "maxNote": 127, "gainDb": 0.0}]},
                  open(os.path.join(kit_dir, "kit.json"), "w"), indent=1)
        return (f"OK: melodic kit '{kit_name}' from slice {idx + 1} — root {root} ({hz}Hz), "
                f"playable across the whole keyboard: {{\"kind\":\"sample\",\"kit\":\"{kit_name}\"}}")
    samples = []
    fade_in, cap = int(0.003 * sr), int(4.0 * sr)
    for k, s in enumerate(starts):
        e = starts[k + 1] if k + 1 < len(starts) else len(x)
        e = min(e, s + cap)
        seg = x[s:e].copy()
        if len(seg) < fade_in * 2:
            continue
        fo = min(int(0.025 * sr), len(seg) // 4)
        seg[:fade_in] *= np.linspace(0, 1, fade_in)
        seg[-fo:] *= np.linspace(1, 0, fo)
        fn = f"pad_{k+1:02d}.wav"
        sf.write(os.path.join(kit_dir, fn), (np.clip(seg, -1, 1) * 32767).astype("<i2"), sr,
                 subtype="PCM_16")
        note = 36 + k
        peak = float(np.abs(seg).max()) + 1e-9
        vel = min(1.0, max(0.55, 1.0 + (20.0 * math.log10(peak)) / 48.0))
        samples.append({"file": fn, "keyNote": note, "minNote": note, "maxNote": note,
                        "gainDb": 0.0, "sliceSec": round(s / sr + from_sec, 4),
                        "lenSec": round(len(seg) / sr, 4), "vel": round(vel, 2)})
    kit = {"kind": "chops", "source": os.path.relpath(src, ROOT) if src.startswith(ROOT) else src,
           "fromSec": from_sec, "samples": samples}
    json.dump(kit, open(os.path.join(kit_dir, "kit.json"), "w"), indent=1)
    pads = ", ".join(f"{36+k}={s['sliceSec']}s" for k, s in enumerate(samples[:6]))
    return (f"OK: kit '{kit_name}' = {len(samples)} pads from {os.path.basename(src)} "
            f"(keys 36..{35+len(samples)}; {pads}{'…' if len(samples) > 6 else ''}). "
            f"Use {{\"kind\":\"sample\",\"kit\":\"{kit_name}\"}} and sequence the pads.")


def groove_notes(kit_name, bpm):
    """The source pattern as notes, from kit.json alone (works on any chopped
    kit, retroactively): slice timing -> start, slice length -> len, peak -> vel."""
    kit = json.load(open(os.path.join(ROOT, "kits", kit_name, "kit.json")))
    if kit.get("kind") != "chops":
        raise SystemExit(f"'{kit_name}' is not a chops kit")
    t0 = float(kit.get("fromSec", 0.0))
    spb = 60.0 / bpm
    notes = []
    for s in kit["samples"]:
        if "sliceSec" not in s:
            continue
        notes.append({"start": round((float(s["sliceSec"]) - t0) / spb, 4),
                      "len": round(float(s.get("lenSec", spb)) / spb, 4),
                      "pitch": int(s["keyNote"]),
                      "vel": float(s.get("vel", 0.9))})
    return notes


def groove_track(kit_name, track_name, bpm):
    return {"name": track_name, "source": {"kind": "sample", "kit": kit_name},
            "gainDb": 0.0, "pan": 0.0, "notes": groove_notes(kit_name, bpm)}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("audio"); ap.add_argument("kit")
    ap.add_argument("--slices", type=int, default=16)
    ap.add_argument("--from-sec", type=float, default=0.0)
    ap.add_argument("--to-sec", type=float, default=None)
    ap.add_argument("--grid", type=int, default=None)
    ap.add_argument("--melodic", type=int, nargs="?", const=0, default=None,
                    help="slice number (default: longest) -> whole-keyboard instrument")
    ap.add_argument("--bpm", type=float, default=None, help="groove tempo (default: neural estimate)")
    ap.add_argument("--groove", action="store_true",
                    help="emit the source's own pattern as notes (CHOP_JSON line)")
    ap.add_argument("--preview", action="store_true",
                    help="write songs/_chop_<kit>.json reconstruction song")
    ap.add_argument("--song", default=None, help="inject groove track into songs/<S>.json")
    ap.add_argument("--track", default=None, help="track name for --song (default: kit name)")
    a = ap.parse_args()
    print(chop(a.audio, a.kit, a.slices, a.from_sec, a.to_sec, a.grid, a.melodic))
    if (a.groove or a.preview or a.song) and a.melodic is None:
        bpm = a.bpm
        if bpm is None:
            from stems_import import estimate_bpm
            src = a.audio if os.path.isabs(a.audio) else os.path.join(ROOT, a.audio)
            bpm, conf = estimate_bpm(src)
            print(f"[chop] groove bpm {round(bpm, 2)} (conf {round(conf, 2)})")
        kit_name = a.kit
        notes = groove_notes(kit_name, bpm)
        total_beats = max((n["start"] + n["len"] for n in notes), default=4.0)
        if a.preview:
            song = {"version": 2, "bpm": round(bpm, 2),
                    "lengthBars": max(1, math.ceil(total_beats / 4.0)),
                    "masterGainDb": 0.0,
                    "tracks": [groove_track(kit_name, a.track or kit_name, bpm)]}
            p = os.path.join(ROOT, "songs", f"_chop_{kit_name}.json")
            json.dump(song, open(p, "w"), indent=1)
            print(f"[chop] preview -> songs/_chop_{kit_name}.json (render with m1)")
        if a.song:
            sp = os.path.join(ROOT, "songs", f"{a.song}.json")
            song = json.load(open(sp))
            tname = a.track or kit_name
            song["tracks"] = [t for t in song.get("tracks", []) if t.get("name") != tname]
            song["tracks"].append(groove_track(kit_name, tname, bpm))
            json.dump(song, open(sp, "w"), indent=1)
            print(f"[chop] groove track '{tname}' injected into songs/{a.song}.json")
        print("CHOP_JSON " + json.dumps({"kit": kit_name, "bpm": round(bpm, 2),
                                         "slices": len(notes),
                                         "lengthBeats": round(total_beats, 2)}))
