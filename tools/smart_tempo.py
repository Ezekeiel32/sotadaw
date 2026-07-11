#!/usr/bin/env python3
"""SMART TEMPO — a freely-played recording becomes the song's grid (rubato conform).

  smart_tempo.py <audio> [--song name --write] [--meter 4] [--engine auto|beatthis|librosa]

beatgrid.py detects beats; THIS turns them into a tempoMap the engine already
speaks: bar boundaries from neural downbeats (Beat This!, the beatgrid engine),
per-bar bpm, near-equal bars merged into spans, curve 0 (ramp) across gradual
drift and curve 1 (step) at real tempo jumps. offsetSec = the first downbeat —
set it on the recording's audioClip and bar 1 IS downbeat 1. A live take stops
being "one wrong bpm number": the grid follows the human (Ableton Smart Tempo /
Logic beat-mapping class, ours lands in song.json).

Kernel (beats_to_map) is PURE — batteries drive it without a model. Engines:
beat_this (neural, GPU-elastic, downbeats) -> librosa fallback (beats only).
--write sets bpm + tempoMap on the song (chordvote --write precedent); the MCP
mount is read-only by law — the agent applies via update_song_meta.
Machine line: TEMPO_JSON {...}
"""
import argparse, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import numpy as np


# ------------------------------------------------------------------ pure kernel
def beats_to_map(beats, downbeats=None, meter=4, tol=0.02, jump=0.08):
    """beat/downbeat times (seconds) -> {offsetSec, bpm, lengthBars, tempoMap[]}.

    Bars come from downbeats when >=3 are given (meter measured per bar), else
    beats grouped by `meter` from the first beat. Per-bar bpm = beats_per_bar *
    60 / bar_len; consecutive bars whose bpm stays within `tol` (relative, vs
    the running span median) merge into one span -> ONE tempoMap entry at the
    span's start bar. curve: 0 (linear ramp) when the next span is a gradual
    drift (<`jump` relative), 1 (hold-then-step) at real jumps + on the last.
    """
    beats = np.asarray(sorted(float(b) for b in (beats or [])), dtype=float)
    if len(beats) < 8:
        return {"available": False, "reason": f"only {len(beats)} beats — too short to grid"}
    if downbeats is not None and len(downbeats) >= 3:
        bars = np.asarray(sorted(float(d) for d in downbeats), dtype=float)
        ibis = np.diff(beats)
        med_ibi = float(np.median(ibis))
        bpb = float(np.median(np.diff(bars))) / max(med_ibi, 1e-6)
        meter_est = int(round(bpb)) if 1.5 <= bpb <= 12.5 else meter
        offset = float(bars[0])
    else:
        bars = beats[::max(1, int(meter))]
        meter_est = int(meter)
        offset = float(beats[0])
        ibis = np.diff(beats)
    if len(bars) < 2:
        return {"available": False, "reason": "fewer than 2 bars detected"}

    # a downbeat OPENS a bar: close the last one with its predecessor's length
    # (repeat-last keeps the final bar merging into the last span — a synthetic
    # median close would fake a tempo entry at the end of an accelerando)
    bars = np.append(bars, 2 * bars[-1] - bars[-2])
    durs = np.diff(bars)
    bpms = meter_est * 60.0 / np.maximum(durs, 1e-6)

    # merge near-equal bars into spans (running-median tolerance)
    spans = []  # [start_bar, [bpm...]]
    for i, b in enumerate(bpms):
        if spans and abs(b - np.median(spans[-1][1])) / max(np.median(spans[-1][1]), 1e-6) <= tol:
            spans[-1][1].append(float(b))
        else:
            spans.append([i, [float(b)]])

    tempo_map = []
    for si, (start, vals) in enumerate(spans):
        bpm = round(float(np.median(vals)), 1)
        if si + 1 < len(spans):
            nxt = float(np.median(spans[si + 1][1]))
            curve = 0 if abs(nxt - bpm) / max(bpm, 1e-6) < jump else 1
        else:
            curve = 1
        tempo_map.append({"bar": int(start), "bpm": bpm, "curve": curve})

    med = float(np.median(ibis))
    iqr = float(np.percentile(ibis, 75) - np.percentile(ibis, 25))
    return {"available": True, "offsetSec": round(offset, 4),
            "bpm": tempo_map[0]["bpm"], "meter": meter_est,
            "lengthBars": int(len(durs)), "n_beats": int(len(beats)),
            "confidence": round(1.0 - min(1.0, iqr / max(med, 1e-6)), 3),
            "stable": len(tempo_map) == 1, "tempoMap": tempo_map}


# ------------------------------------------------------------------- engines
def detect(path, engine="auto", cpu=False):
    """-> (beats, downbeats|None, engine_name). Raises on total failure."""
    if engine in ("auto", "beatthis"):
        try:
            from beat_this.inference import File2Beats
            device = "cpu"
            if not cpu:
                try:
                    import torch
                    device = "cuda" if torch.cuda.is_available() else "cpu"
                except Exception:
                    pass
            f2b = File2Beats(checkpoint_path="final0", device=device, dbn=False)
            beats, downbeats = f2b(path)
            if len(beats) >= 8:
                return list(map(float, beats)), list(map(float, downbeats)), f"beat_this:{device}"
        except Exception as e:
            if engine == "beatthis":
                raise RuntimeError(f"beat_this unavailable: {e}")
    import librosa
    y, sr = librosa.load(path, sr=22050, mono=True)
    _, bt = librosa.beat.beat_track(y=y, sr=sr, units="time", trim=False)
    return list(map(float, bt)), None, "librosa"


def conform(path, meter=4, engine="auto", cpu=False, tol=0.02):
    try:
        beats, downbeats, eng = detect(path, engine=engine, cpu=cpu)
    except Exception as e:
        return {"available": False, "reason": f"beat detection failed: {e}"}
    out = beats_to_map(beats, downbeats, meter=meter, tol=tol)
    out["engine"] = eng
    out["file"] = os.path.basename(path)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("audio")
    ap.add_argument("--song", default=None, help="song to conform (--write applies)")
    ap.add_argument("--write", action="store_true", help="write bpm + tempoMap into --song")
    ap.add_argument("--meter", type=int, default=4)
    ap.add_argument("--tol", type=float, default=0.02)
    ap.add_argument("--engine", default="auto", choices=["auto", "beatthis", "librosa"])
    ap.add_argument("--cpu", action="store_true")
    a = ap.parse_args()
    out = conform(a.audio, meter=a.meter, engine=a.engine, cpu=a.cpu, tol=a.tol)
    if out.get("available"):
        tm = out["tempoMap"]
        print(f"[smart_tempo] {out['file']} via {out['engine']}: {out['n_beats']} beats, "
              f"{out['lengthBars']} bars in {out['meter']}/4, first downbeat {out['offsetSec']}s, "
              f"confidence {out['confidence']}")
        if out["stable"]:
            print(f"  STEADY {tm[0]['bpm']} bpm — one entry, the grid is flat")
        else:
            for e in tm[:24]:
                print(f"  bar {e['bar']:4}  {e['bpm']:6.1f} bpm  {'ramp' if e['curve'] == 0 else 'step'}")
            if len(tm) > 24:
                print(f"  ... {len(tm) - 24} more entries")
        if a.song and a.write:
            import songname
            name = songname.resolve(a.song)
            sp = os.path.join(ROOT, "songs", f"{name}.json")
            song = json.load(open(sp))
            song["bpm"] = out["bpm"]
            if out["stable"]:
                song.pop("tempoMap", None)
            else:
                song["tempoMap"] = out["tempoMap"]
            json.dump(song, open(sp, "w"), indent=1)
            print(f"  WROTE bpm={out['bpm']}" + ("" if out["stable"] else
                  f" + tempoMap ({len(out['tempoMap'])} entries)") + f" -> songs/{name}.json")
    print("TEMPO_JSON " + json.dumps(out))


if __name__ == "__main__":
    main()
