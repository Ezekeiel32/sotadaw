#!/usr/bin/env python3
"""DJ LISTENER v0 — the set that hears itself (CC4 P7: "AI DJs because it can LISTEN").

  dj_listener.py <set.wav> [--bpm N] [--hop SECONDS]

Walks a rendered set in windows and judges the ENERGY JOURNEY the way a working
DJ reads a floor: loudness trajectory, spectral center (timbre fatigue), low-band
weight (the dance signal). Emits timestamped verdicts + the fix for each — the
listening half of the AI-DJ loop. v0 is OFFLINE (post-render audit of dj_set
output); the realtime ears bus rides the same verdict kernel when the engine
lane lands it.

Grounded in working-DJ energy practice: sets breathe in waves — sustained plateaus
kill floors, and energy is managed in arcs with deliberate valleys, not held at
ceiling (see stamp f140 citations: energy-flow guides on plateau avoidance and
wave-shaped pacing).

Verdicts (each -> a named fix):
  PLATEAU   >45s inside a +-1.5dB band mid-set     -> cut 8-16 bars / add riser+drop
  CLIFF     >7dB drop inside one hop (non-ending)  -> echo-out or longer blend there
  FATIGUE   centroid pinned +-8% for >60s          -> filter sweep / swap a deck
  DEAD_AIR  rms under -45dB for >2s mid-set        -> tighten the handover
  NO_PEAK   set never exceeds its own median +3dB  -> build a real peak (drop section)
Clean sets print CLEAN + the arc summary.
"""
import argparse, json, math, sys, wave

import numpy as np


def load_wav(path):
    w = wave.open(path, "rb")
    sr, sw, ch, n = w.getframerate(), w.getsampwidth(), w.getnchannels(), w.getnframes()
    raw = w.readframes(n)
    w.close()
    if sw == 3:                                    # 24-bit (m1's native) — the 1.5x trap
        a = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3)
        x = (a[:, 0].astype(np.int32) | (a[:, 1].astype(np.int32) << 8)
             | (a[:, 2].astype(np.int32) << 16))
        x = np.where(x & 0x800000, x - 0x1000000, x).astype(np.float64) / 8388608.0
    else:
        x = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0
    x = x.reshape(-1, ch).mean(axis=1)
    return x, sr


def window_features(x, sr, hop):
    n = int(sr * hop)
    feats = []
    for i in range(0, len(x) - n, n):
        seg = x[i:i + n]
        rms = 20 * math.log10(max(1e-9, float(np.sqrt(np.mean(seg ** 2)))))
        spec = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
        freqs = np.fft.rfftfreq(len(seg), 1.0 / sr)
        centroid = float((spec * freqs).sum() / max(spec.sum(), 1e-9))
        low = float(spec[freqs < 150].sum() / max(spec.sum(), 1e-9))
        feats.append(dict(t=i / sr, rms=rms, centroid=centroid, low=low))
    return feats


def listen(feats, hop):
    """The verdict kernel — pure, unit-tested by dj_listener_battery."""
    verdicts = []
    if len(feats) < 4:
        return verdicts
    rms = [f["rms"] for f in feats]
    cen = [f["centroid"] for f in feats]
    dur = len(feats) * hop
    active = [r for r in rms if r > -45]
    med = sorted(active)[len(active) // 2] if active else -60.0

    # PLATEAU: consecutive windows inside +-1.5dB, >45s, not the intro/outro
    run_start, run_ref = 0, rms[0]
    for i in range(1, len(rms) + 1):
        inside = i < len(rms) and abs(rms[i] - run_ref) <= 1.5
        if not inside:
            span = (i - run_start) * hop
            t0 = run_start * hop
            if span >= 45 and t0 > hop and (t0 + span) < dur - hop and run_ref > -40:
                verdicts.append(dict(kind="PLATEAU", t=round(t0, 1), span=round(span, 1),
                                     fix="cut 8-16 bars here or add a riser->drop; floors read flat energy as an exit sign"))
            if i < len(rms):
                run_start, run_ref = i, rms[i]
        else:
            run_ref = 0.7 * run_ref + 0.3 * rms[i]      # slow-follow the band center
    # CLIFF: >7dB single-hop drop before the final windows
    for i in range(1, len(rms) - 2):
        if rms[i - 1] - rms[i] > 7 and rms[i - 1] > -35:
            verdicts.append(dict(kind="CLIFF", t=round(i * hop, 1),
                                 drop=round(rms[i - 1] - rms[i], 1),
                                 fix="handover is a cliff — echo-out the outgoing deck or lengthen the blend"))
    # FATIGUE: centroid pinned +-8% for >60s on active audio
    ref, start = cen[0], 0
    for i in range(1, len(cen) + 1):
        ok = i < len(cen) and abs(cen[i] - ref) <= 0.08 * max(ref, 1) and rms[min(i, len(rms) - 1)] > -40
        if not ok:
            if (i - start) * hop >= 60:
                verdicts.append(dict(kind="FATIGUE", t=round(start * hop, 1),
                                     span=round((i - start) * hop, 1),
                                     fix="timbre pinned — ride the djfilter (bipolar sweep) or bring a brighter/darker deck"))
            if i < len(cen):
                ref, start = cen[i], i
        else:
            ref = 0.8 * ref + 0.2 * cen[i]
    # DEAD_AIR: silence mid-set
    for i in range(1, len(rms) - 1):
        if rms[i] < -45 and rms[i - 1] > -40:
            verdicts.append(dict(kind="DEAD_AIR", t=round(i * hop, 1),
                                 fix="gap in the handover — start the incoming deck before the outgoing ends"))
    # NO_PEAK: the set never rises 3dB over its own median
    if active and max(active) - med < 3.0 and dur > 120:
        verdicts.append(dict(kind="NO_PEAK",
                             fix="no real peak — arc the set: valley then a drop section +3dB over the body"))
    return verdicts


def deck_energy(x, sr):
    """W50 (item 164): a real 1-10 ENERGY score, decoupled from BPM —
    a 128 melodic-house deck and a 128 peak-techno deck must rank
    differently. Composite of level, onset density, low-end weight and
    brightness on CALIBRATED ABSOLUTE ranges (scores compare across
    decks; per-deck normalization would erase exactly the differences
    the planner needs). Pure numpy, offline-cheap."""
    if x is None or len(x) < sr:
        return None
    # 50ms sub-frame rms ladder — onsets + activity live here
    n = max(int(sr * 0.05), 1)
    m = len(x) // n
    if m < 8:
        return None
    sub = x[:m * n].reshape(m, n)
    r = np.sqrt(np.mean(sub ** 2, axis=1))
    rdb = 20 * np.log10(np.maximum(r, 1e-9))
    active = rdb > -45
    if not active.any():
        return None
    rms_active = float(np.median(rdb[active]))
    # onset density: a rise >4dB over the local 100ms floor, audible
    rises = 0
    for i in range(2, m):
        floor = min(rdb[i - 2], rdb[i - 1])
        if rdb[i] > -35 and rdb[i] - floor > 4.0:
            rises += 1
    dens = rises / (m * 0.05)
    # spectrum: up to 8 spaced 1s chunks (whole-deck FFTs cost too much)
    picks = np.linspace(0, max(len(x) - sr, 0), num=min(8, max(m // 20, 1)),
                        dtype=int)
    specs = []
    for p in picks:
        seg = x[p:p + sr]
        if len(seg) < sr // 2 or float(np.sqrt(np.mean(seg ** 2))) < 1e-4:
            continue
        specs.append(np.abs(np.fft.rfft(seg * np.hanning(len(seg)))))
    if specs:
        spec = np.mean([s[:min(len(q) for q in specs)] for s in specs],
                       axis=0)
        freqs = np.fft.rfftfreq((min(len(q) for q in specs) - 1) * 2,
                                1.0 / sr)[:len(spec)]
        centroid = float((spec * freqs).sum() / max(spec.sum(), 1e-9))
        lowfrac = float(spec[freqs < 150].sum() / max(spec.sum(), 1e-9))
    else:
        centroid, lowfrac = 800.0, 0.2
    clamp = lambda v: max(0.0, min(1.0, v))
    score = (0.35 * clamp((rms_active + 30.0) / 22.0)
             + 0.30 * clamp(dens / 3.0)
             + 0.15 * clamp(lowfrac / 0.5)
             + 0.20 * clamp((centroid - 500.0) / 3000.0))
    return int(max(1, min(10, round(1 + 9 * score))))


def parse_mik_energy(comment):
    """Mixed In Key writes 'Energy 7' into the Comments tag — when the
    pro tool already judged the deck, its number is AUTHORITATIVE
    (r-27: skip computation)."""
    import re
    m = re.search(r"[Ee]nergy\s*(\d{1,2})", str(comment or ""))
    if not m:
        return None
    return max(1, min(10, int(m.group(1))))


def arc_verdicts(feats, hop=8.0, arc="peak"):
    """W85 (r-27 item 249): GLOBAL arc verdicts on the composite-energy
    timeline (the local kernel keeps plateau/cliff/dead-air):
      PEAK_MISPLACED  main peak lands outside 0.5-0.85 of the set
      MONOTONE_CLIMB  no valley before the peak (crowd fatigue)
      NO_RELEASE      the set ENDS at its peak (journey/closer arcs
                      resolve; 'peak' arc is exempt — ending hot is
                      its design)
    Emits the target arc so the heal (reorder/insert valley) is
    deterministic."""
    if len(feats) < 8:
        return []
    rms = [f["rms"] for f in feats]
    n = len(rms)
    # smooth to set-scale moves
    k = max(n // 16, 1)
    sm = [sum(rms[max(0, i - k):i + k + 1]) /
          len(rms[max(0, i - k):i + k + 1]) for i in range(n)]
    pk = max(range(n), key=lambda i: sm[i])
    pos = pk / max(n - 1, 1)
    out = []
    if not (0.5 <= pos <= 0.9):
        out.append(dict(kind="PEAK_MISPLACED", pos=round(pos, 2),
                        target_arc=arc,
                        fix="the main peak wants the last third "
                            "(golden-section ~0.62-0.85); reorder decks "
                            "or move the biggest record later"))
    pre = sm[:pk + 1]
    if len(pre) >= 4:
        rise = max(pre) - min(pre)
        # a valley = a dip of >=25% of the total rise before the peak
        run_max = pre[0]
        deepest = 0.0
        for v in pre:
            run_max = max(run_max, v)
            deepest = max(deepest, run_max - v)
        if rise > 3.0 and deepest < 0.25 * rise:
            out.append(dict(kind="MONOTONE_CLIMB",
                            target_arc=arc,
                            fix="no valley before the peak — crowds "
                                "fatigue; breathe once (a deeper cut "
                                "2/3 in) before the final lift"))
    if arc in ("journey", "closer", "wave") and n >= 8:
        tail = sm[int(n * 0.9):]
        if tail and max(tail) >= sm[pk] - 1.0:
            out.append(dict(kind="NO_RELEASE", target_arc=arc,
                            fix=f"a '{arc}' set must RESOLVE after the "
                                "peak — land one cooler record before "
                                "the end"))
    return out


def frames_to_feats(frames, hop=8.0):
    """THE EARS BUS LIVE LANE (E3 R3): fold the 10 Hz ears.jsonl feature frames
    into the kernel's hop windows — the SAME verdicts (PLATEAU/CLIFF/FATIGUE/
    DEAD_AIR/NO_PEAK) go live with zero new analysis code. Centroid is proxied
    from the 4 band energies (band centers below); low = the low band's power
    fraction (kernel's dance signal)."""
    CENTERS = (125.0, 450.0, 1789.0, 6000.0)
    live = [f for f in frames if f.get("playing")]
    if not live:
        return []
    t0 = float(live[0].get("sec", 0.0))
    buckets = {}
    for f in live:
        buckets.setdefault(int((float(f.get("sec", 0.0)) - t0) / hop), []).append(f)
    feats = []
    for k in sorted(buckets):
        fs = buckets[k]
        rms = sum(sum(f.get("rms_db", [-120, -120])) / 2 for f in fs) / len(fs)
        pw = [0.0] * 4
        for f in fs:
            b = f.get("bands_db", [-120] * 4)
            for i in range(4):
                pw[i] += 10 ** (float(b[i]) / 10.0)
        tot = max(sum(pw), 1e-12)
        feats.append(dict(t=k * hop, rms=rms,
                          centroid=sum(p * c for p, c in zip(pw, CENTERS)) / tot,
                          low=pw[0] / tot))
    return feats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("wav", nargs="?", default=None)
    ap.add_argument("--hop", type=float, default=8.0)
    ap.add_argument("--frames", default=None,
                    help="listen to an ears.jsonl (live ears-bus frames) instead of a wav")
    a = ap.parse_args()
    if a.frames:
        frames = []
        for ln in open(a.frames):
            try:
                frames.append(json.loads(ln))
            except Exception:
                continue
        feats = frames_to_feats(frames, a.hop)
        verdicts = listen(feats, a.hop)
        dur = len(feats) * a.hop
    elif a.wav:
        x, sr = load_wav(a.wav)
        feats = window_features(x, sr, a.hop)
        verdicts = listen(feats, a.hop)
        dur = len(x) / sr
    else:
        sys.exit("need a wav or --frames <ears.jsonl>")
    if not verdicts:
        rng = (min(f['rms'] for f in feats), max(f['rms'] for f in feats)) if feats else (0, 0)
        print(f"[listener] CLEAN — {dur/60:.1f}min set, energy arc {rng[0]:.1f}..{rng[1]:.1f} dB, "
              "no plateaus/cliffs/fatigue/dead-air")
    else:
        print(f"[listener] {len(verdicts)} floor-risk moment(s) in {dur/60:.1f}min:")
        for v in verdicts:
            t = v.get("t")
            loc = f"@{int(t//60)}:{int(t%60):02d}" if t is not None else "(whole set)"
            extra = " ".join(f"{k}={v[k]}" for k in ("span", "drop") if k in v)
            print(f"  [{v['kind']}] {loc} {extra}\n        -> {v['fix']}")
    print("LISTEN_JSON " + json.dumps(verdicts))


if __name__ == "__main__":
    main()
