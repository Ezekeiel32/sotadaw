#!/usr/bin/env python3
"""STRUCTURE_TRANSFER — a reference record's SHAPE becomes an arrangement plan.

  structure_transfer.py <ref_audio> [--song name] [--bars N] [--min-gap 8]

segment.py hears WHERE a record changes (Foote novelty) and label_sections
names the parts; this tool turns that into something a song can WEAR: the
reference's sections mapped proportionally onto the target's bar grid (4-bar
snapped, monotonic, tiny spans merged), each with a measured energy target
(section RMS / record peak) and honest density hints. "Make my song shaped
like X" becomes a measured journey, not a vibe.

Read-only by law: prints the plan (sections[] ready for song.json + per-section
moves); the agent applies via update_song_meta / duplicate_bars / clear_bars on
proposal rails. Machine line: STRUCT_JSON {...}
"""
import argparse, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import numpy as np
from hear import load_wav
from segment import mel_frames, novelty_curve, boundaries, label_sections


def section_energy(x, sr, edges_s):
    peak = 1e-12
    rms = []
    for a, b in zip(edges_s[:-1], edges_s[1:]):
        seg = x[int(a * sr):int(b * sr)]
        r = float(np.sqrt((seg ** 2).mean())) if len(seg) > sr // 2 else 0.0
        rms.append(r)
        peak = max(peak, r)
    return [round(r / peak, 3) for r in rms]


def density_hint(name, energy):
    base = str(name).rstrip("0123456789 ").strip()
    if base in ("break",):
        return {"density": "low", "drop_drums": True}
    if base in ("intro", "outro"):
        return {"density": "low", "thin": True}
    if base in ("build",):
        return {"density": "rising", "riser": True}
    if base in ("drop", "hook", "peak"):
        return {"density": "high"}
    return {"density": "high" if energy >= 0.82 else ("mid" if energy >= 0.5 else "low")}


def plan(ref_path, target_bars=64, min_gap_s=8.0, vocal_path=None):
    try:
        sr, x = load_wav(ref_path)
    except Exception as e:
        return {"available": False, "reason": f"unreadable reference: {e}"}
    if len(x) < sr * 20:
        return {"available": False, "reason": "reference under 20s — no structure to hear"}
    F, hop_s = mel_frames(x, sr)
    nov = novelty_curve(F, hop_s=hop_s)
    bounds = boundaries(nov, hop_s=hop_s, min_gap_s=min_gap_s)
    dur = len(x) / sr
    edges_s = [0.0] + [t for t, _ in bounds] + [dur]
    labels = label_sections(x, sr, [t for t, _ in bounds], vocal_path=vocal_path)
    energy = section_energy(x, sr, edges_s)

    # proportional map onto the bar grid: 4-bar snap, monotonic, merge tiny spans
    raw = [round(a / dur * target_bars / 4.0) * 4 for a in edges_s[:-1]] + [target_bars]
    sections, moves = [], []
    for i in range(len(labels)):
        s, e = raw[i], raw[i + 1]
        if e - s < 4:                      # a span the grid can't hold merges away
            continue
        if sections and s <= sections[-1]["startBar"]:
            continue
        sections.append({"name": labels[i], "startBar": int(s)})
        moves.append({"section": labels[i], "bars": [int(s), int(e)],
                      "energy": energy[i], **density_hint(labels[i], energy[i])})
    for i, sec in enumerate(sections):     # bars spans from the FINAL section list
        end = sections[i + 1]["startBar"] if i + 1 < len(sections) else target_bars
        moves[i]["bars"] = [sec["startBar"], int(end)]
    return {"available": True, "reference": os.path.basename(ref_path),
            "duration_s": round(dur, 1), "ref_sections": len(labels),
            "target_bars": int(target_bars), "sections": sections, "moves": moves,
            "energy_arc": energy}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ref")
    ap.add_argument("--song", default=None, help="target song (its lengthBars = the grid)")
    ap.add_argument("--bars", type=int, default=None)
    ap.add_argument("--min-gap", type=float, default=8.0)
    ap.add_argument("--vocal", default=None, help="reference vocal stem (labels gain verse/hook)")
    a = ap.parse_args()
    bars = a.bars
    if a.song and not bars:
        import songname
        name = songname.resolve(a.song)
        song = json.load(open(os.path.join(ROOT, "songs", f"{name}.json")))
        bars = int(round(float(song.get("lengthBars", 64))))
    out = plan(a.ref, target_bars=bars or 64, min_gap_s=a.min_gap, vocal_path=a.vocal)
    if out.get("available"):
        print(f"[structure] {out['reference']} {out['duration_s']}s -> "
              f"{len(out['sections'])} sections on a {out['target_bars']}-bar grid")
        for m in out["moves"]:
            extra = " drop drums" if m.get("drop_drums") else (" riser" if m.get("riser") else "")
            print(f"  bars {m['bars'][0]:3}-{m['bars'][1]:3}  {m['section']:<10} "
                  f"energy {m['energy']:.2f}  density {m['density']}{extra}")
    print("STRUCT_JSON " + json.dumps(out))


if __name__ == "__main__":
    main()
