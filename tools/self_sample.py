#!/usr/bin/env python3
"""THE SELF-SAMPLING FACTORY (ROADMAP_0.020 W1.2): render our OWN instruments
(Faust voices or hosted VSTs) into one-shot sample kits — symbolic-native sound
upgrades. One engine render per kit (notes on a grid), sliced by numpy, trimmed,
peak-staged, written as kits/<name>/ + kit.json.

  self_sample.py drums <kitname>     build a drum kit from a voice spec (see DRUM_SPEC)
  self_sample.py melodic <kitname> <faust_voice> [--lo 36 --hi 84 --step 4]

Spec format per piece: (label, source_kind, source_id, params, midi_pitch_played,
kit_keyNote, note_len_beats, tail_beats).
"""
import argparse, json, os, subprocess, sys
import numpy as np
from scipy.io import wavfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")
KITS = os.path.join(ROOT, "kits")
BPM = 120.0                       # 1 beat = 0.5 s — easy slicing math
SPACING = 8.0                     # beats between hits (4 s: room for tails)

# SOTA Drums v2 — our own voices, loudness-staged. v2 after the judge red-flagged v1:
# stereo width baked into hats/claps/percs (fx_widen at sampling time), bright metallic
# closed hat, crash added. Kick/sub stay MONO (low-end law). fx field = track fx chain.
WIDE = [{"id": "fx_widen", "params": {"width": 1.1, "rate": 0.4}}]
WIDER = [{"id": "fx_widen", "params": {"width": 1.5, "rate": 0.3}}]
DRUM_SPEC = [
    # label      kind     id           params                        pitch key len  tail  fx
    ("kick",     "faust", "kick_psy",   {"punch": 13, "decay": 0.3},  36, 36, 0.5, 1.5, None),
    ("kick_deep","faust", "kick_punch", {},                            35, 35, 0.5, 1.5, None),
    ("snare",    "faust", "snare",      {},                            38, 38, 0.4, 1.2, WIDE),
    ("clap",     "faust", "clap_909",   {},                            39, 39, 0.4, 1.5, WIDE),
    ("hat",      "faust", "hat_metal",  {"decay": 0.09},               42, 42, 0.15, 0.5, WIDE),
    ("hat_dark", "faust", "hat",        {},                            41, 41, 0.15, 0.6, None),
    ("hat_open", "faust", "hat_metal",  {"decay": 0.6},                46, 46, 0.5, 1.5, WIDER),
    ("perc",     "faust", "hat_metal",  {"decay": 0.14},               43, 43, 0.15, 0.5, WIDE),
    ("crash",    "faust", "hat_metal",  {"decay": 1.4},                49, 49, 0.8, 2.5, WIDER),
    ("sub808",   "faust", "kick_808",   {},                            29, 33, 1.2, 1.6, None),
]

def render_grid(pieces, out_wav):
    """pieces: [(source_kind, source_id, params, pitch, len_beats, fx|None)] — one note each."""
    tracks = {}
    for i, (kind, sid, params, pitch, ln, fx) in enumerate(pieces):
        key = (kind, sid, json.dumps(params, sort_keys=True), json.dumps(fx))
        tracks.setdefault(key, []).append((i * SPACING, pitch, ln))
    song_tracks = []
    for (kind, sid, pjson, fxjson), notes in tracks.items():
        src = {"kind": kind, "id": sid}
        p = json.loads(pjson)
        if p:
            src["params"] = p
        tr = {"name": f"{sid}_{len(song_tracks)}", "source": src, "gainDb": 0,
              "notes": [{"start": s, "len": ln, "pitch": pt, "vel": 0.95} for s, pt, ln in notes]}
        fx = json.loads(fxjson)
        if fx:
            tr["fx"] = fx
        song_tracks.append(tr)
    total_beats = len(pieces) * SPACING + 4
    song = {"version": 2, "bpm": BPM, "lengthBars": int(total_beats / 4 + 1),
            "masterGainDb": 0.0, "master": [], "tracks": song_tracks}
    sj = out_wav.replace(".wav", ".json")
    json.dump(song, open(sj, "w"))
    r = subprocess.run([M1, "render", sj, out_wav], capture_output=True, text=True, timeout=600)
    if b"ok=1" not in r.stdout.encode() and "ok=1" not in r.stdout:
        raise SystemExit(f"render failed: {r.stdout[-300:]}{r.stderr[-200:]}")

def slice_and_write(grid_wav, kit_dir, labels_keys_tails, peak_target_db=-3.0):
    sr, x = wavfile.read(grid_wav)
    if x.dtype.kind == "i":
        x = x.astype(np.float32) / np.iinfo(x.dtype).max
    if x.ndim == 1:
        x = x[:, None]
    spacing_smp = int(SPACING * (60.0 / BPM) * sr)
    entries = []
    for i, (label, key_note, min_n, max_n, tail_beats) in enumerate(labels_keys_tails):
        seg = x[i * spacing_smp: i * spacing_smp + int((tail_beats + 2.0) * (60.0 / BPM) * sr)]
        mono = np.abs(seg).max(axis=1)
        # trim leading silence (keep 32-sample pre-roll) and trailing below -66 dB
        nz = np.where(mono > 1e-3)[0]
        if len(nz) == 0:
            print(f"  !! {label}: silent — skipped"); continue
        start = max(0, nz[0] - 32)
        end = nz[-1] + int(0.02 * sr)
        seg = seg[start:end]
        # peak-stage to target + 10ms fade-out
        peak = np.abs(seg).max()
        if peak > 1e-6:
            seg = seg * (10 ** (peak_target_db / 20.0) / peak)
        fade = min(len(seg), int(0.01 * sr))
        seg[-fade:] *= np.linspace(1, 0, fade)[:, None]
        fn = f"{label}.wav"
        wavfile.write(os.path.join(kit_dir, fn), sr, (seg * 32767).astype(np.int16))
        entries.append({"file": fn, "keyNote": key_note, "minNote": min_n, "maxNote": max_n,
                        "gainDb": 0.0})
        print(f"  {label}: {len(seg)/sr:.2f}s @ key {key_note}")
    return entries

def build_drums(kitname):
    kit_dir = os.path.join(KITS, kitname)
    os.makedirs(kit_dir, exist_ok=True)
    tmp = os.path.join(kit_dir, "_grid.wav")
    render_grid([(k, s, p, pitch, ln, fx) for (_, k, s, p, pitch, _, ln, _, fx) in DRUM_SPEC], tmp)
    entries = slice_and_write(
        tmp, kit_dir,
        [(lbl, key, key, key, tail) for (lbl, _, _, _, _, key, _, tail, _) in DRUM_SPEC])
    # 808 responds across a range (sampler repitches)
    for e in entries:
        if e["file"] == "sub808.wav":
            e["minNote"], e["maxNote"] = 24, 40
    json.dump({"kind": "drums", "samples": entries}, open(os.path.join(kit_dir, "kit.json"), "w"), indent=1)
    os.remove(tmp); os.remove(tmp.replace(".wav", ".json"))
    print(f"kit '{kitname}': {len(entries)} pieces -> kits/{kitname}/")

def build_melodic(kitname, voice, lo, hi, step):
    kit_dir = os.path.join(KITS, kitname)
    os.makedirs(kit_dir, exist_ok=True)
    pitches = list(range(lo, hi + 1, step))
    tmp = os.path.join(kit_dir, "_grid.wav")
    render_grid([("faust", voice, {}, p, 2.0, None) for p in pitches], tmp)
    spec = []
    for i, p in enumerate(pitches):
        min_n = p - step // 2 if i > 0 else 0
        max_n = p + (step - step // 2) - 1 if i < len(pitches) - 1 else 127
        spec.append((f"p{p}", p, min_n, max_n, 2.5))
    entries = slice_and_write(tmp, kit_dir, spec, peak_target_db=-6.0)
    json.dump({"kind": "melodic", "samples": entries}, open(os.path.join(kit_dir, "kit.json"), "w"), indent=1)
    os.remove(tmp); os.remove(tmp.replace(".wav", ".json"))
    print(f"kit '{kitname}': {len(entries)} zones from {voice} -> kits/{kitname}/")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["drums", "melodic"])
    ap.add_argument("kitname")
    ap.add_argument("voice", nargs="?")
    ap.add_argument("--lo", type=int, default=36)
    ap.add_argument("--hi", type=int, default=84)
    ap.add_argument("--step", type=int, default=4)
    a = ap.parse_args()
    if a.mode == "drums":
        build_drums(a.kitname)
    else:
        if not a.voice:
            raise SystemExit("melodic needs a faust voice name")
        build_melodic(a.kitname, a.voice, a.lo, a.hi, a.step)
