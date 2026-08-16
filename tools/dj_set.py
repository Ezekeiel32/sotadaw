#!/usr/bin/env python3
"""dj_set.py — AI DJ SET BUILDER: N tracks -> one continuous beat-matched set.

  dj_set.py out_name track1.wav track2.wav track3.wav ... [--blend-bars 8]
            [--bpms 126,134,120]

Every deck is warped (sourceBpm); the grid TRAVELS: a tempoMap point at each
transition re-anchors the song tempo to the incoming deck's natural bpm —
the classic DJ energy arc (128 -> 132 -> 136), engine-exact. Transition style
is picked PER HOP: within warp distance = the dj-blend recipe (4-bar phrase
alignment, staggered dB crossfade, fx_djfilter bass swap); beyond 16% tempo
distance = ECHO-OUT CUT (outgoing clip ends phrase-exact, fx_delay throw rings
the tail over the incoming deck's clean full-gain start — verified: tail
-19.9dB after the cut decaying to -48 over 3s, zero dead air). The whole set
is ONE song.json — every move editable, nothing rendered away. Steps in the
8-16% gray zone still blend but get flagged (soundtouch transparency limit).
"""
import argparse, json, math, os, sys, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stems_import import estimate_bpm
from dj_mix import wav_seconds, rms_db, deck_key, harmonic_verdict


def setplan_seconds(starts_beats, bpms, names):
    """Beats -> wall-seconds per deck entry (Mixcloud chapter grade, +-2s):
    the span between deck k-1 and k plays at deck k-1's tempo. Pure, battery-tested."""
    t, out = 0.0, []
    for k, sb in enumerate(starts_beats):
        if k:
            t += (sb - starts_beats[k - 1]) * 60.0 / max(bpms[k - 1], 1.0)
        out.append({"artist": "", "song": names[k], "start": round(t, 1)})
    return out


def hop_cost(a, b, arc="peak", pos=1.0):
    """Cost of transitioning deck a -> deck b at position pos (0..1] of the set.
    a/b = (bpm, camelot, conf). arc = the CROWD-ENERGY preset (§7.7):
      peak   — climb all night, never come down (the original law, default)
      warmup — climb GENTLY: big tempo jumps punished (opening-slot restraint)
      closer — rise through the body, LAND at the end (late downshifts free,
               late climbs punished — the last record sends them home)
    The drift buckets stay for every arc (soundtouch physics don't care about vibes)."""
    # THE HALF/DOUBLE-TIME BRIDGE (w45, r-27 item 102): 85 and 170 share
    # a pocket — effective drift is the best over feel factors {1/2,1,2},
    # with a small flat fee for the feel flip (it IS a moment).
    factors = ((1.0, 0.0), (0.5, 1.5), (2.0, 1.5))
    drift, feel_fee, f_best = min(
        ((abs(b[0] * f - a[0]) / a[0], fee, f) for f, fee in factors),
        key=lambda x: x[0])
    if drift <= 0.08:
        c = drift * 10.0 + feel_fee          # clean blend, nearly free
    elif drift <= 0.16:
        c = 5.0 + drift * 20.0 + feel_fee    # gray-zone blend (audible stretch)
    else:
        c = 8.0                              # echo-out cut: fine, but don't chain them
    # the arc judges the FEEL step: a 170->85 halftime flip keeps the
    # pocket — it is not a 50% energy crash (w45)
    step = (b[0] * f_best - a[0]) / a[0]
    if arc == "warmup":
        if step < 0:
            c += -step * 15.0
        elif step > 0.06:
            c += (step - 0.06) * 60.0        # restraint: a warm-up DJ never slams
    elif arc == "closer":
        if pos < 0.67 and step < 0:
            c += -step * 15.0                # still climb through the body...
        elif pos >= 0.67 and step > 0:
            c += step * 25.0                 # ...then land, don't spike the exit
    elif arc == "wave":                      # the festival wave (w45):
        in_breather = 0.3 <= pos <= 0.65     # downshifts FREE mid-set,
        if step < 0 and not in_breather:     # lightly held elsewhere
            c += -step * 8.0
    else:                                    # peak: energy arcs climb
        if step < 0:
            c += -step * 15.0
    hv = harmonic_verdict(a[1], b[1])
    if "CLASH" in hv:
        c += 6.0
    return c


def arc_shape(arc, t):
    """The GLOBAL tempo-percentile target at position t (w45, item 163):
    plan_order aims the whole set at a SHAPE, not just cheap hops.
    peak/warmup rise; closer rises then lands; WAVE is the festival
    rise-fall-rise."""
    t = max(0.0, min(1.0, t))
    if arc == "wave":
        if t < 0.35:
            return 0.2 + (t / 0.35) * 0.6          # first crest
        if t < 0.6:
            return 0.8 - ((t - 0.35) / 0.25) * 0.35  # the breather
        return 0.45 + ((t - 0.6) / 0.4) * 0.55     # the finish
    if arc == "warmup":
        return 0.1 + 0.6 * t
    if arc == "closer":
        return (0.2 + t * 1.0) if t < 0.67 else (0.87 - (t - 0.67) * 0.9)
    return 0.15 + 0.85 * t                          # peak: climb all night


SHAPE_W = 4.0


# W50 (item 165): the per-genre-pair TRANSITION CATALOG — style keys on
# WHO is talking to WHOM, not just tempo drift. Bars are the pro norms:
# four-floor families converse in long layered blends (32-64), trance
# meets breakdown-to-breakdown, dnb/hip-hop/open-format cut short and
# hard, cross-family rides the echo-out (or the halftime bridge the
# w45 optimizer already knows). PHYSICS OUTRANKS: >16% tempo distance
# stays an echo-out cut whatever the table says.
_FAMILIES = {
    "house": ("house", "garage", "ukg", "disco", "funky", "deep",
              "progressive_house", "afro"),
    "techno": ("techno", "electro", "minimal", "industrial", "schranz"),
    "trance": ("trance", "psytrance", "goa", "fullon", "psy"),
    "dnb": ("dnb", "drum_and_bass", "drum-n-bass", "jungle", "breakcore",
            "halftime"),
    "openformat": ("hip_hop", "hiphop", "rap", "trap", "grime", "drill",
                   "pop", "rnb", "reggaeton", "dancehall", "open"),
}
TRANSITIONS = {  # (fam_a, fam_b) -> (style, blend_bars, note)
    ("house", "house"): ("blend", 32, "long layered blend, bass-swap at the midpoint"),
    ("techno", "techno"): ("blend", 32, "long layered blend, gentle EQ"),
    ("house", "techno"): ("blend", 24, "four-floor cousins — layered blend"),
    ("trance", "trance"): ("blend", 32, "breakdown-to-breakdown preferred (32+ bars)"),
    ("house", "trance"): ("blend", 24, "ride the build"),
    ("techno", "trance"): ("blend", 24, "ride the build"),
    ("dnb", "dnb"): ("blend", 8, "short 8-16 bar switch or double-drop"),
    ("openformat", "openformat"): ("echo_out", 4, "cut on the downbeat, echo throw"),
    ("dnb", "openformat"): ("echo_out", 4, "hard cut"),
}


def _family(genre):
    g = str(genre or "").lower().replace("-", "_").replace(" ", "_")
    if not g:
        return None
    for fam, words in _FAMILIES.items():
        if any(w in g for w in words):
            return fam
    return None


def choose_transition(genre_a, genre_b):
    """(style, blend_bars, note) from the catalog, or None -> tempo law."""
    fa, fb = _family(genre_a), _family(genre_b)
    if fa is None or fb is None:
        return None
    hit = TRANSITIONS.get((fa, fb)) or TRANSITIONS.get((fb, fa))
    if hit:
        return hit
    return ("echo_out", 8, f"cross-family {fa}->{fb}: echo-out cut")


def plan_order(items, arc="peak", energies=None):
    """items = [(bpm, camelot, conf), ...] -> (best order indices, cost).
    Exhaustive for <=8 decks (event scale), greedy+2opt beyond. The cost
    = pairwise hops + THE GLOBAL SHAPE term: each slot's tempo
    percentile vs arc_shape(pos) (w45 — min-adjacent-cost alone lets a
    'wave' set climb monotonically)."""
    import itertools
    n = len(items)
    # W50 (item 164): the GLOBAL SHAPE ranks by measured ENERGY when the
    # ears provided it — bpm is the fallback, never the meaning (a 128
    # melodic deck and a 128 peak deck must rank apart)
    if energies and len(energies) == n and all(e is not None for e in energies):
        keyf = lambda i: (energies[i], items[i][0])
    else:
        keyf = lambda i: items[i][0]
    ranks = {i: r / max(1, n - 1) for r, i in enumerate(
        sorted(range(n), key=keyf))}

    def cost_of(order):
        c = sum(hop_cost(items[order[k - 1]], items[order[k]],
                         arc, k / max(1, n - 1))
                for k in range(1, n))
        c += sum(abs(ranks[order[k]] - arc_shape(arc, k / max(1, n - 1)))
                 for k in range(n)) * SHAPE_W
        return c
    if n <= 8:
        best = min(itertools.permutations(range(n)), key=cost_of)
        return list(best), cost_of(best)
    order = sorted(range(n), key=lambda i: items[i][0])   # greedy: tempo-ascending
    improved = True
    while improved:                                        # 2-opt polish
        improved = False
        for i in range(1, n - 1):
            for j in range(i + 1, n):
                cand = order[:i] + order[i:j + 1][::-1] + order[j + 1:]
                if cost_of(cand) < cost_of(order):
                    order, improved = cand, True
    return order, cost_of(order)


def _deck_stems(path):
    """W92 (item 166): demucs 4 stems ONCE per deck, cached by content
    hash — every hop that touches this deck reuses them. Returns
    {drums,bass,vocals,other: wav} or None (fail-open to EQ blends)."""
    import hashlib
    try:
        h = hashlib.md5(open(path, "rb").read(1 << 20)).hexdigest()[:16]
    except Exception:
        return None
    cdir = os.path.join(ROOT, "songs", ".stemcache", h)
    names = ("drums", "bass", "vocals", "other")
    if all(os.path.exists(os.path.join(cdir, n + ".wav"))
           for n in names):
        return {n: os.path.join(cdir, n + ".wav") for n in names}
    try:
        import torch
        from demucs.separate import main as demucs_main
        dev = "cuda" if torch.cuda.is_available() else "cpu"
        work = cdir + "_work"
        os.makedirs(work, exist_ok=True)
        demucs_main(["-n", "htdemucs", "-d", dev, "-o", work, path])
        base = os.path.splitext(os.path.basename(path))[0]
        src_dir = os.path.join(work, "htdemucs", base)
        os.makedirs(cdir, exist_ok=True)
        for n in names:
            os.replace(os.path.join(src_dir, n + ".wav"),
                       os.path.join(cdir, n + ".wav"))
        import shutil as _sh
        _sh.rmtree(work, ignore_errors=True)
        return {n: os.path.join(cdir, n + ".wav") for n in names}
    except Exception as e:
        print(f"[dj_set] stems unavailable for {os.path.basename(path)} "
              f"({e}) — EQ blend stands")
        return None


def stem_bass_swap(song, hop_k, stems_out, stems_in, swap_beat):
    """TRUE bass-swap: the two decks around a blend split into stem
    lanes; the OUTGOING bass mutes AT the swap beat, the incoming bass
    enters there — physics, not a filter approximation. Mutates."""
    def split(track, stems, tag):
        clips = track.get("audioClips") or []
        if not clips:
            return []
        lanes = []
        for n, wav in stems.items():
            ln = {"name": f"{track['name']}_{n}",
                  "source": {"kind": "audio", "id": f"{track['name']}_{n}"},
                  "gainDb": track.get("gainDb", 0.0), "pan": 0.0,
                  "fx": [dict(f) for f in (track.get("fx") or [])],
                  "notes": [],
                  "audioClips": [dict(c, file=wav) for c in clips],
                  "automation": [dict(a) for a in
                                 (track.get("automation") or [])]}
            lanes.append(ln)
        track["muted"] = True                 # the mono deck steps back
        return lanes
    tracks = song.get("tracks", [])
    out_t = next((t for t in tracks
                  if t.get("name") == f"deck_{chr(97 + hop_k - 1)}"), None)
    in_t = next((t for t in tracks
                 if t.get("name") == f"deck_{chr(97 + hop_k)}"), None)
    if out_t is None or in_t is None:
        return []
    new_lanes = split(out_t, stems_out, "out") + split(in_t, stems_in, "in")
    tracks.extend(new_lanes)
    edits = [{"kind": "stem_split", "hop": hop_k, "lanes": len(new_lanes)}]
    ob = next((t for t in new_lanes
               if t["name"] == f"deck_{chr(97 + hop_k - 1)}_bass"), None)
    ib = next((t for t in new_lanes
               if t["name"] == f"deck_{chr(97 + hop_k)}_bass"), None)
    if ob is not None:
        g = float(ob.get("gainDb", 0) or 0)
        ob.setdefault("automation", []).append(
            {"target": "gainDb",
             "points": [{"beat": swap_beat - 0.1, "v": g},
                        {"beat": swap_beat, "v": -60.0}]})
    if ib is not None:
        g = float(ib.get("gainDb", 0) or 0)
        ib.setdefault("automation", []).append(
            {"target": "gainDb",
             "points": [{"beat": swap_beat - 0.1, "v": -60.0},
                        {"beat": swap_beat, "v": g}]})
    edits.append({"kind": "bass_swap", "beat": swap_beat,
                  "why": (f"hop {hop_k}: the outgoing BASS STEM mutes at "
                          f"beat {swap_beat:g} and the incoming enters — "
                          "true low-end handover, not an EQ shadow")})
    return edits


def _deck_boundaries(path, bpm, offset_s=0.0):
    """W80 (item 038): the deck's REAL structural seams (Foote novelty
    via segment.py), as beats from the deck's first downbeat. Cached
    per (file md5, bpm) — segmentation is offline-cheap but not free."""
    import hashlib
    cache_dir = os.path.join(ROOT, "songs", ".segcache")
    os.makedirs(cache_dir, exist_ok=True)
    try:
        h = hashlib.md5((open(path, "rb").read(1 << 20)
                         + str(round(bpm, 2)).encode())).hexdigest()[:16]
    except Exception:
        return []
    cp = os.path.join(cache_dir, h + ".json")
    if os.path.exists(cp):
        try:
            return json.load(open(cp))
        except Exception:
            pass
    try:
        sys.path.insert(0, os.path.join(ROOT, "tools"))
        import segment as SEG
        res = SEG.segment(path, bpm=bpm)
        secs = [float(b[0] if isinstance(b, (tuple, list)) else b)
                for b in (res.get("boundaries") or [])]
    except Exception:
        secs = []
    beats = [round((s - offset_s) * bpm / 60.0, 3) for s in secs
             if s > offset_s]
    json.dump(beats, open(cp, "w"))
    return beats


def _snap_cut(blind_cut, boundaries, lens, window_beats=32.0):
    """Snap the blind 16-bar cut to the NEAREST detected seam within
    the window; keep phrase sanity (>=16 beats in, inside the deck)."""
    if not boundaries:
        return blind_cut, None
    best = None
    for b in boundaries:
        if 16.0 <= b <= lens and abs(b - blind_cut) <= window_beats:
            if best is None or abs(b - blind_cut) < abs(best - blind_cut):
                best = b
    if best is None:
        return blind_cut, None
    return round(best / 4.0) * 4.0, best      # bar-rounded seam


def extract_vocal_tail(path, start_s, dur_s, tag, win_s=None):
    """The deck's LAST SUNG PHRASE: demucs two-stems over the final span, then
    slide an 8-bar window and keep the loudest-voiced one (a DJ cuts where the
    voice ends, not where the file does). None when nothing sings (RMS gate)."""
    import subprocess, tempfile
    import numpy as np, soundfile as sf
    work = tempfile.mkdtemp(prefix="bridge_")
    tail = os.path.join(work, "tail.wav")
    r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(max(0.0, start_s)),
                        "-t", str(dur_s), "-i", path, "-ar", "44100", "-ac", "2", tail],
                       capture_output=True)
    if r.returncode != 0 or not os.path.exists(tail):
        return None
    import torch
    from demucs.separate import main as demucs_main
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    try:
        demucs_main(["-n", "htdemucs", "--two-stems", "vocals", "-d", dev, "-o", work,
                     "--filename", "{stem}.{ext}", tail])
    except (RuntimeError, Exception) as e:                     # OOM etc -> cpu
        if dev == "cpu":
            return None
        torch.cuda.empty_cache()
        demucs_main(["-n", "htdemucs", "--two-stems", "vocals", "-d", "cpu", "-o", work,
                     "--filename", "{stem}.{ext}", tail])
    voc = os.path.join(work, "htdemucs", "vocals.wav")
    if not os.path.exists(voc):
        return None
    x, sr = sf.read(voc, always_2d=True)
    if win_s and len(x) > int(win_s * sr):          # slide: loudest-voiced window wins
        w, hop = int(win_s * sr), int(2.0 * sr)
        best_i, best_r = 0, -1.0
        for i in range(0, len(x) - w + 1, hop):
            r = float(np.sqrt((x[i:i + w] ** 2).mean()))
            if r > best_r:
                best_i, best_r = i, r
        x = x[best_i:best_i + w]
    rms_db_v = 20.0 * np.log10(float(np.sqrt((x ** 2).mean())) + 1e-12)
    if rms_db_v < -35.0:
        return None
    fade = int(0.01 * sr)
    x[:fade] *= np.linspace(0, 1, fade)[:, None]
    x[-fade:] *= np.linspace(1, 0, fade)[:, None]
    out = os.path.join(ROOT, "songs", f"_bridge_{tag}_vocal.wav")
    sf.write(out, x, sr, subtype="PCM_16")
    return out


def build_set(name, paths, bpms=None, blend_bars=8, auto_order=False, bridges=None,
              offsets=None, camelots=None, audit=False, arc="peak", bridge_auto=False,
              genres=None, comments=None, energy=True, phrase_cuts=False,
              stems=False):
    paths = [os.path.abspath(p) for p in paths]
    n = len(paths)
    if n < 2:
        return None, "need at least 2 tracks"
    genres = (list(genres) + [None] * n)[:n] if genres else [None] * n
    comments = (list(comments) + [None] * n)[:n] if comments else [None] * n
    if bpms is None:
        bpms = []
        for p in paths:
            b, _ = estimate_bpm(p)
            bpms.append(b)
    offsets = offsets or [0.0] * n          # first-beat offset per deck (rekordbox Inizio)
    lens = [(wav_seconds(p) - offsets[i]) * bpms[i] / 60.0 for i, p in enumerate(paths)]
    if camelots:                             # authoritative keys (e.g. rekordbox) skip detection
        keys = [(None, c if c and c != "-" else None, 1.0) for c in camelots]
    else:
        keys = [deck_key(p) for p in paths]  # (key, camelot, conf) per deck
    energies = [None] * n
    if energy:
        try:
            from dj_listener import deck_energy, parse_mik_energy, load_wav
            for i, p in enumerate(paths):
                energies[i] = parse_mik_energy(comments[i])   # MIK = authoritative
                if energies[i] is None:
                    x, sr = load_wav(p)
                    energies[i] = deck_energy(x, sr)
        except Exception as e:
            print(f"[dj_set] energy ears unavailable ({e}) — bpm ranks")
    reorder_note = None
    if auto_order:                          # the playlist brain: tempo arc + harmony
        items = [(bpms[i], keys[i][1], keys[i][2]) for i in range(n)]
        given_cost = sum(hop_cost(items[k - 1], items[k], arc, k / max(1, n - 1))
                         for k in range(1, n))
        order, best_cost = plan_order(items, arc, energies=energies)
        if order != list(range(n)):
            paths = [paths[i] for i in order]
            bpms = [bpms[i] for i in order]
            lens = [lens[i] for i in order]
            keys = [keys[i] for i in order]
            offsets = [offsets[i] for i in order]
            energies = [energies[i] for i in order]
            genres = [genres[i] for i in order]
            comments = [comments[i] for i in order]
            reorder_note = (f"auto-order[{arc}]: {'-'.join(chr(65 + i) for i in order)} "
                            f"(cost {given_cost:.1f} -> {best_cost:.1f})")
    ref = rms_db(paths[0])
    trims = [max(-12.0, min(12.0, ref - rms_db(p))) for p in paths]        # gain-match all decks
    blend = blend_bars * 4.0
    rel = lambda p: os.path.relpath(p, ROOT) if p.startswith(ROOT) else p

    tracks, tempo_map, sections, warnings = [], [], [], []
    bridge_cache = {}
    if bridge_auto:                         # ACAPELLA AUTO-SELECT (§7.7): probe every
        bridges = list(bridges or [])       # hop's outgoing tail with the builder's own
        for k in range(1, n):               # cut law; wherever a voice sings, that hop
            if k in bridges:                # bridges (demucs per hop — offline set cost)
                continue
            j = k - 1
            cut_local = max(16.0, math.floor(lens[j] / 16.0) * 16.0)
            t0 = offsets[j] + max(0.0, cut_local - 96.0) * 60.0 / bpms[j]
            probe_dur = min(cut_local, 96.0) * 60.0 / bpms[j] + 1.0
            voc = extract_vocal_tail(paths[j], t0, probe_dur, f"{name}_{k}",
                                     win_s=32.0 * 60.0 / bpms[j])
            if voc is not None:
                bridges.append(k)
                bridge_cache[k] = voc       # never demucs the same hop twice
                warnings.append(f"transition {k}: bridge-auto — deck {chr(65 + j)}'s "
                                f"tail sings, its voice carries over")
    # transition style per deck entry: beat-matched blend when tempos are close,
    # ECHO-OUT CUT beyond 16% (the dj-blend law: soundtouch can't hide that stretch)
    styles = [None] + ["echo_out" if abs(bpms[k] - bpms[k - 1]) / bpms[k - 1] > 0.16
                       else "blend" for k in range(1, n)]
    blends = [blend_bars * 4.0] * n           # per-hop blend length (beats)
    for k in range(1, n):                     # W50: the genre-pair CATALOG
        hit = choose_transition(genres[k - 1], genres[k])
        if hit is None:
            continue
        style, bars, note = hit
        drift = abs(bpms[k] - bpms[k - 1]) / bpms[k - 1]
        if drift > 0.16:                      # physics outranks the table
            styles[k] = "echo_out"
            continue
        styles[k] = style
        blends[k] = bars * 4.0
        warnings.append(f"transition {k}: catalog "
                        f"{_family(genres[k - 1])}->{_family(genres[k])}: "
                        f"{style} {bars} bars — {note}")
    for bk in (bridges or []):                      # THE ACAPELLA BRIDGE (explicit per hop):
        if 1 <= bk < n:                             # outgoing cuts, its VOICE carries over
            styles[bk] = "bridge"
    seams = [(_deck_boundaries(paths[i], bpms[i], offsets[i])
              if phrase_cuts else []) for i in range(n)]
    starts, cut_len = [0.0], {}
    for k in range(1, n):
        if styles[k] in ("echo_out", "bridge"):     # outgoing ends at its last whole phrase,
            blind = max(16.0, math.floor(lens[k - 1] / 16.0) * 16.0)
            snapped, seam = _snap_cut(blind, seams[k - 1], lens[k - 1]) \
                if phrase_cuts else (blind, None)
            if seam is not None and abs(snapped - blind) >= 4.0:
                warnings.append(f"transition {k}: cut snapped to the "
                                f"deck's REAL seam (bar "
                                f"{snapped / 4.0:.0f} vs blind "
                                f"{blind / 4.0:.0f}) — blends land on "
                                "musical boundaries")
            cut = starts[k - 1] + snapped
            starts.append(cut)                      # incoming starts clean AT the cut
            cut_len[k - 1] = cut - starts[k - 1]
        else:
            prev_end = starts[k - 1] + lens[k - 1]
            b_start = max(starts[k - 1] + 16.0,
                          math.floor((prev_end - blends[k]) / 16.0) * 16.0)
            starts.append(b_start)
    total = starts[-1] + lens[-1]

    for k, p in enumerate(paths):
        clip = {"file": rel(p), "startBeat": starts[k], "sourceBpm": round(bpms[k], 2)}
        if offsets[k]:
            clip["offsetSec"] = round(offsets[k], 3)   # skip pre-downbeat silence/pickup
        if k in cut_len:
            clip["lengthBeats"] = round(cut_len[k], 3)
        d = {"name": f"deck_{chr(97 + k)}", "source": {"kind": "audio", "id": f"deck_{chr(97 + k)}"},
             "gainDb": round(trims[k], 1),
             "fx": [{"id": "fx_djfilter", "params": {"knob": 0.0, "res": 1.1}}],
             "notes": [],
             "audioClips": [clip],
             "automation": []}
        gain_pts, knob_pts = [], []
        g = round(trims[k], 1)                      # trim lives INSIDE the fade values:
        if k > 0 and styles[k] == "blend":          # a gainDb curve overrides static gain
            a, b = starts[k], min(starts[k] + blends[k], starts[k] + lens[k])
            swap = min(max(a + round(blends[k] / 8.0) * 4.0, a + 4.0), b - 4.0)
            gain_pts += [{"beat": a, "v": round(-21 + g, 1)}, {"beat": swap, "v": g}]
            knob_pts += [{"beat": a, "v": 0.62}, {"beat": swap - 0.25, "v": 0.62},
                         {"beat": swap, "v": 0.0}]
            tempo_map.append({"bar": swap / 4.0, "bpm": round(bpms[k], 2)})
            drift = abs(bpms[k] - bpms[k - 1]) / bpms[k - 1]
            if drift > 0.08:
                warnings.append(f"transition {k}: tempo step {bpms[k-1]:.0f}->{bpms[k]:.0f} "
                                f"({drift*100:.0f}% > 8% soundtouch transparency)")
        elif k > 0:                                 # echo-out/bridge entry: clean slam at the cut
            gain_pts.append({"beat": starts[k], "v": g})
            tempo_map.append({"bar": starts[k] / 4.0, "bpm": round(bpms[k], 2)})
        if k > 0:
            hv = harmonic_verdict(keys[k - 1][1], keys[k][1])
            if "CLASH" in hv:
                # AUTO-FIX (§7.7): the djfilter bass-kill was PRESCRIBED in the
                # warning, now APPLIED — deepen the incoming deck's entry filter so
                # the clashing roots don't collide over the overlap (EQ bass-swap is
                # the DJ remedy for a key clash). Blend entries only (knob ride
                # exists); slam/echo entries have no bass to swap.
                fixed = False
                for pt in knob_pts:
                    if pt.get("v", 0) > 0:
                        pt["v"] = max(pt["v"], 0.85)
                        fixed = True
                warnings.append(f"transition {k}: {hv}"
                                + (" -> auto djfilter bass-kill (0.85)" if fixed
                                   else " (slam/echo entry — bass-kill n/a)"))
        if k < n - 1 and styles[k + 1] == "blend":  # fade out over the next deck's entry
            a = starts[k + 1]
            b = min(a + blends[k + 1], starts[k] + lens[k])
            swap = min(max(a + round(blends[k + 1] / 8.0) * 4.0, a + 4.0), b - 4.0)
            if not gain_pts or gain_pts[-1]["beat"] < swap:
                gain_pts.append({"beat": swap, "v": g})   # hold full until the swap
            gain_pts.append({"beat": b, "v": -60})
            knob_pts += [{"beat": swap, "v": 0.0}, {"beat": swap + 0.25, "v": 0.5}]
        elif k < n - 1 and styles[k + 1] == "bridge":   # bridge exit: the VOICE is the tail
            if not gain_pts:
                gain_pts.append({"beat": starts[k], "v": g})
        elif k < n - 1:                             # echo-out exit: throw the tail, hold gain
            cut = starts[k + 1]                     # (the delay rings past the clip end;
            dt = round(0.75 * 60000.0 / bpms[k])    #  cutting gainDb would kill the tail)
            d["fx"].append({"id": "fx_delay", "params": {"time": dt, "feedback": 0.6, "mix": 0.0}})
            d["automation"].append({"target": "fx[1].mix",
                                    "points": [{"beat": max(starts[k], cut - 8.0), "v": 0.0},
                                               {"beat": cut - 0.5, "v": 0.55}]})
            if not gain_pts:
                gain_pts.append({"beat": starts[k], "v": g})
        if gain_pts:
            if k == 0 and gain_pts[0]["beat"] > 0:
                gain_pts.insert(0, {"beat": 0, "v": g})
            d["automation"].append({"target": "gainDb", "points": gain_pts})
        if knob_pts:
            d["automation"].append({"target": "fx[0].knob", "points": knob_pts})
        tracks.append(d)
        sections.append({"name": f"deck {chr(65 + k)} ({bpms[k]:.0f})", "startBar": int(starts[k] // 4)})

    for k in range(1, n):                            # build bridge vocal overlays
        if styles[k] != "bridge":
            continue
        j = k - 1
        cut_local = cut_len[j]                       # beats of outgoing actually played
        span_beats = 32.0                            # 8 bars of voice ride the incoming deck
        probe_beats = 96.0                           # search the last 24 played bars for the
        t0 = offsets[j] + max(0.0, cut_local - probe_beats) * 60.0 / bpms[j]
        probe_dur = min(cut_local, probe_beats) * 60.0 / bpms[j] + 1.0
        voc = bridge_cache.get(k) or extract_vocal_tail(paths[j], t0, probe_dur,
                                                        f"{name}_{k}",
                                                        win_s=span_beats * 60.0 / bpms[j])
        if voc is None:
            warnings.append(f"transition {k}: bridge requested but deck {chr(65+j)} has no "
                            f"audible vocal in its tail — fell back to a plain cut")
            continue
        vt = {"name": f"bridge_{chr(97+j)}{chr(97+k)}",
              "source": {"kind": "audio", "id": f"bridge_{k}"},
              "gainDb": round(trims[j] + 1.0, 1), "notes": [],
              "fx": [{"id": "fx_djfilter", "params": {"knob": 0.41, "res": 0.7}}],
              "audioClips": [{"file": rel(voc), "startBeat": starts[k],
                              "lengthBeats": span_beats, "sourceBpm": round(bpms[j], 2)}],
              "automation": [{"target": "gainDb",
                              "points": [{"beat": starts[k], "v": round(trims[j] + 1.0, 1)},
                                         {"beat": starts[k] + span_beats - 8.0,
                                          "v": round(trims[j] + 1.0, 1)},
                                         {"beat": starts[k] + span_beats, "v": -60}]}]}
        tracks.append(vt)
        sections.append({"name": "BRIDGE (voice carries)", "startBar": int(starts[k] // 4)})

    if stems:                       # W92: TRUE bass-swap on blend hops
        for k in range(1, n):
            if styles[k] != "blend":
                continue
            so = _deck_stems(paths[k - 1])
            si = _deck_stems(paths[k])
            if not (so and si):
                continue
            a = starts[k]
            swap = min(max(a + round(blends[k] / 8.0) * 4.0, a + 4.0),
                       min(a + blends[k], starts[k - 1] + lens[k - 1])
                       - 4.0)
            for e in stem_bass_swap(
                    {"tracks": tracks}, k, so, si, round(swap, 3)):
                warnings.append(f"stems: {e.get('why', e['kind'])}"
                                if e.get("why") else
                                f"stems: {e['kind']} x{e.get('lanes', '')}")
    song = {"version": 2, "bpm": round(bpms[0], 2), "lengthBars": int(math.ceil(total / 4.0)),
            "masterGainDb": 0.0, "tempoMap": tempo_map,
            "master": [{"id": "fx_brickwall", "params": {"ceiling": -1.0}}],
            "sections": sections, "tracks": tracks}
    out = os.path.join(ROOT, "songs", f"{name}.json")
    json.dump(song, open(out, "w"), indent=1)
    # THE SET PLAN (f144): the tracklist manifest — publish_mixcloud --sections
    # consumes it directly, so a set upload arrives CHAPTERED with zero manual work.
    stems = [os.path.splitext(os.path.basename(p))[0].replace("_", " ") for p in paths]
    setplan = setplan_seconds(starts, bpms, stems)
    for i, ch in enumerate(setplan):          # W50: per-deck energy in the manifest
        if i < n and energies[i] is not None:
            ch["energy"] = energies[i]
        if i < n and genres[i]:
            ch["genre"] = genres[i]
    sp_path = os.path.join(ROOT, "songs", f"{name}.setplan.json")
    json.dump(setplan, open(sp_path, "w"), indent=1)
    print(f"[dj_set] setplan: {sp_path} ({len(setplan)} chapters)")
    plan = (" -> ".join(f"{chr(65+k)}:{bpms[k]:.0f}bpm/{keys[k][1] or '?'}"
                        + (f"/E{energies[k]}" if energies[k] is not None else "")
                        + f"@bar{int(starts[k]//4)}"
                        + (f"[{styles[k]}]" if k else "") for k in range(n))
            + f" | {song['lengthBars']} bars, {len(tempo_map)} tempo moves")
    if reorder_note:
        plan = reorder_note + "\n[dj_set] " + plan
    for w in warnings:
        plan += f"\n[dj_set] WARN {w}"
    print(f"[dj_set] {out}\n[dj_set] {plan}")
    if audit:
        # THE SELF-AUDITING SET (f145): render + let the set HEAR ITSELF — the
        # dj_listener verdict kernel (plateau/cliff/fatigue/dead-air/no-peak)
        # rides the same output the planner prints. Zero tokens, one flag.
        wav = os.path.join(ROOT, "songs", f"{name}.wav")
        m1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")
        r = subprocess.run([m1, "render", out, wav], capture_output=True, text=True,
                           timeout=1800)
        if r.returncode == 0 and os.path.exists(wav):
            rl = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "dj_listener.py"),
                                 wav], capture_output=True, text=True, timeout=600)
            for line in rl.stdout.strip().splitlines():
                print(f"[audit] {line}")
        else:
            print(f"[audit] render failed - set json stands, audit skipped: {(r.stdout+r.stderr)[-160:]}")
    return out, plan


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("tracks", nargs="+")
    ap.add_argument("--blend-bars", type=int, default=8)
    ap.add_argument("--bpms", type=str, default=None, help="comma-separated, skips detection")
    ap.add_argument("--auto-order", action="store_true",
                    help="let the planner choose deck order (tempo arc + harmonic path)")
    ap.add_argument("--offsets", type=str, default=None,
                    help="comma-separated first-beat offset (sec) per deck (rekordbox Inizio)")
    ap.add_argument("--bridge", type=int, action="append", default=None,
                    help="hop index (1=first transition): outgoing deck's VOICE carries "
                         "over the incoming deck (acapella bridge; needs a vocal tail)")
    ap.add_argument("--bridge-auto", action="store_true",
                    help="probe every hop's outgoing tail (demucs per hop) and bridge "
                         "wherever a voice actually sings — no hop index needed")
    ap.add_argument("--arc", choices=("peak", "warmup", "closer"), default="peak",
                    help="crowd-energy preset for --auto-order: peak=climb all night "
                         "(default), warmup=gentle climb, closer=rise then LAND")
    ap.add_argument("--keys", type=str, default=None,
                    help="comma-separated Camelot per deck ('-' = unknown); skips detection")
    ap.add_argument("--audit", action="store_true", help="render + dj_listener verdicts")
    ap.add_argument("--genres", type=str, default=None,
                    help="comma-separated per-deck genres -> W50 transition catalog")
    ap.add_argument("--comments", type=str, default=None,
                    help="semicolon-separated per-deck comment tags (MIK 'Energy 7' honored)")
    ap.add_argument("--stems", action="store_true",
                    help="W92: demucs 4 stems per deck (cached) + TRUE "
                         "bass-swap on blend hops")
    ap.add_argument("--phrase-cuts", action="store_true",
                    help="W80: snap cuts to Foote-detected structural "
                         "seams (cached per deck)")
    ap.add_argument("--no-energy", action="store_true",
                    help="skip the 1-10 energy ears (bpm ranks the arc)")
    a = ap.parse_args()
    bpms = [float(x) for x in a.bpms.split(",")] if a.bpms else None
    offsets = [float(x) for x in a.offsets.split(",")] if a.offsets else None
    camelots = a.keys.split(",") if a.keys else None
    build_set(a.name, a.tracks, bpms, a.blend_bars, a.auto_order,
              bridges=a.bridge, offsets=offsets, camelots=camelots, audit=a.audit,
              arc=a.arc, bridge_auto=a.bridge_auto,
              genres=[g.strip() or None for g in a.genres.split(",")]
              if a.genres else None,
              comments=[c.strip() or None for c in a.comments.split(";")]
              if a.comments else None,
              energy=not a.no_energy, phrase_cuts=a.phrase_cuts,
              stems=a.stems)
