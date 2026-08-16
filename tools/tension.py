#!/usr/bin/env python3
"""THE TENSION KERNEL + ARC SHAPES — wave 18 (R-14 items 016/017/071,
R-20 items 026/027).

Deterministic per-beat musical tension from song.json — pure geometry +
psychoacoustics, zero tokens, zero renders. Sources (cited in
docs/research_producer_mind/r-{14,20}.json):

  Herremans-Chew spiral array (midi-miner constants: quarter-turn per
    fifth, vertical step 0.4): cloud DIAMETER (intra-chord dissonance),
    cloud MOMENTUM (harmonic-change rate), TENSILE STRAIN (distance from
    the home key's center of effect).
  Sethares roughness (b1=3.5, b2=5.75, s=0.24/(0.0207*fmin+18.96),
    amplitude=min) summed over sounding partials.
  TenseMusic combination (r~0.62-0.68 vs human ratings — the honest
    ceiling): Tension(w) = 0.32 zL + 0.16 zP + 0.16 zRgh + 0.16 zTS +
    0.12 zD + 0.05 zTmp, momentum as a spike term.
  Farbood's 6 validated arc contours (2,661 participants): ramp, arch,
    peak (inverted-V), valley (U), plateau, oscillating.
  R-14 climax law: energy maximum lands ~65-85% through; golden section
    (~61.8%) is the TURN (bridge/breakdown), not the peak. Peak in the
    first third = hard fail (hook-first pop preview exempt). EDM drop
    law: the drop is the GLOBAL max and wants an engineered 1-3dB
    pre-drop dip — impact comes from CONTRAST.

  tension_curve(song)      -> per-beat [0,1] curve + feature dict
  section_energy(song)     -> Farbood-grounded 5-param section scalars
  classify_arc(curve)      -> (family, correlation) vs the 6 contours
  court_tension_arc(song, genre)   shape/climax/range verdicts
  court_drop(song, genre) + heal_drop   EDM drop-contrast + the dip heal
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# midi-miner note_index_to_pitch_index (line-of-fifths index per pc C..B)
_PC_TO_FIFTH = [0, -5, 2, -3, 4, -1, 6, 1, -4, 3, -2, 5]
_VSTEP = 0.4          # midi-miner vertical_step
W_L, W_P, W_RGH, W_TS, W_D, W_TMP = 0.32, 0.16, 0.16, 0.16, 0.12, 0.05
W_MOM_SPIKE = 0.10    # momentum rides as a spike term atop the blend

CLIMAX_LO, CLIMAX_HI = 0.60, 0.90   # r-14: peak lands ~65-85%, ±ease
# conviction edge CORPUS-CALIBRATED (self-measure law 2026-07-15): the
# research names 'first third' but chezy_song_full (ACCEPTED, 346 bars,
# 24 sections) measures its last-near-max at 0.315 — the edge sits at
# 0.25 so real accepted form never grazes it.
EARLY_EDGE = 0.25

_HOOK_FIRST = ("pop", "kpop", "jpop", "hyperpop")   # hook-preview idiom
_TEXTURE = ("ambient", "drone", "meditation", "soundscape", "new_age",
            "field", "lowercase", "dark_ambient")


def _spiral(pc):
    k = _PC_TO_FIFTH[pc % 12]
    t = k * math.pi / 2.0
    return (math.sin(t), math.cos(t), k * _VSTEP)


def _ce(weighted_pcs):
    """Center of effect: weight-normalized mean spiral position."""
    tot = sum(w for _, w in weighted_pcs) or 1.0
    x = y = z = 0.0
    for pc, w in weighted_pcs:
        px, py, pz = _spiral(pc)
        x += px * w
        y += py * w
        z += pz * w
    return (x / tot, y / tot, z / tot)


def _dist(a, b):
    return math.sqrt(sum((i - j) ** 2 for i, j in zip(a, b)))


def cloud_diameter(pcs):
    """Max pairwise spiral distance of the sounding pitch classes."""
    pts = [_spiral(pc) for pc in set(p % 12 for p in pcs)]
    if len(pts) < 2:
        return 0.0
    return max(_dist(a, b) for i, a in enumerate(pts) for b in pts[i + 1:])


def key_ce(root_pc, minor=False):
    """Home-key center of effect ~ the tonic triad's ce (Chew-style
    approximation; battery proves in-key < out-key strain, which is the
    property the court uses)."""
    third = (root_pc + (3 if minor else 4)) % 12
    fifth = (root_pc + 7) % 12
    return _ce([(root_pc, 0.516), (fifth, 0.315), (third, 0.168)])


def sethares_roughness(freqs_amps):
    """Sethares pairwise roughness; b1=3.5 b2=5.75,
    s=0.24/(0.0207*fmin+18.96), amplitude=min."""
    r = 0.0
    n = len(freqs_amps)
    for i in range(n):
        f1, a1 = freqs_amps[i]
        for j in range(i + 1, n):
            f2, a2 = freqs_amps[j]
            fmin, fmax = (f1, f2) if f1 <= f2 else (f2, f1)
            s = 0.24 / (0.0207 * fmin + 18.96)
            d = s * (fmax - fmin)
            r += min(a1, a2) * (math.exp(-3.5 * d) - math.exp(-5.75 * d))
    return r


def _note_partials(pitch, vel, n_partials=6):
    f0 = 440.0 * 2 ** ((pitch - 69) / 12.0)
    return [(f0 * k, vel / k) for k in range(1, n_partials + 1)]


def _z(xs):
    n = len(xs)
    if n < 2:
        return [0.0] * n
    m = sum(xs) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in xs) / n) or 1.0
    return [(x - m) / sd for x in xs]


def _sounding(song):
    """Per-beat sounding notes [(pitch, vel, gain_lin, is_onset)],
    length = song beats."""
    length_beats = int(float(song.get("lengthBars", 8) or 8) * 4)
    beats = [[] for _ in range(max(length_beats, 1))]
    for t in song.get("tracks", []) or []:
        if not isinstance(t, dict) or t.get("muted"):
            continue
        g = 10 ** (float(t.get("gainDb", 0) or 0) / 20.0)
        for n in t.get("notes", []) or []:
            try:
                s = float(n.get("start", 0))
                ln = max(float(n.get("len", 0.25)), 0.05)
                p = int(n.get("pitch", 60))
                v = float(n.get("vel", 0.8))
            except Exception:
                continue
            b0, b1 = int(s), int(math.ceil(s + ln))
            for b in range(max(b0, 0), min(b1, len(beats))):
                beats[b].append((p, v, g, b == b0))
    return beats


def _tempo_at(song, beat):
    tm = song.get("tempoMap") or []
    bpm = float(song.get("bpm", 120) or 120)
    if not tm:
        return bpm
    bar = beat / 4.0
    for seg in sorted(tm, key=lambda s: float(s.get("bar", 0))):
        if float(seg.get("bar", 0)) <= bar:
            bpm = float(seg.get("bpm", bpm) or bpm)
    return bpm


def tension_curve(song, genre=""):
    """Per-beat tension in [0,1] + the raw z-scored features."""
    beats = _sounding(song)
    if not any(beats):
        return {"curve": [], "features": {}}
    try:
        import theory
        notes_all = [n for t in song.get("tracks", []) or []
                     if isinstance(t, dict) and not t.get("muted")
                     for n in t.get("notes", []) or []]
        key = theory.infer_key(notes_all, genre) if notes_all else None
    except Exception:
        key = None
    if isinstance(key, dict):
        kce = key_ce(int(key.get("tonic_pc", 0)),
                     "min" in str(key.get("mode", "")))
    else:
        kce = key_ce(0)
    L, P, D, RGH, TS, MOM, TMP = [], [], [], [], [], [], []
    prev_ce = None
    for b, cell in enumerate(beats):
        if not cell:
            L.append(0.0)
            P.append(P[-1] if P else 60.0)
            D.append(0.0)
            RGH.append(0.0)
            TS.append(TS[-1] if TS else 0.0)
            MOM.append(0.0)
            TMP.append(_tempo_at(song, b))
            continue
        L.append(sum(v * g for _, v, g, _ in cell))
        ps = sorted(p for p, _, _, _ in cell)
        P.append(ps[min(int(len(ps) * 0.85), len(ps) - 1)])
        D.append(sum(1 for *_, on in cell if on) + len(cell) * 0.25)
        partials = []
        for p, v, g, _ in cell[:12]:          # cap: O(notes) small
            partials.extend(_note_partials(p, v * g, 4))
        RGH.append(sethares_roughness(partials[:48]))
        wpcs = [(p % 12, v) for p, v, _, _ in cell]
        ce = _ce(wpcs)
        TS.append(_dist(ce, kce))
        MOM.append(_dist(ce, prev_ce) if prev_ce else 0.0)
        prev_ce = ce
        TMP.append(_tempo_at(song, b))
    zL, zP, zRgh = _z(L), _z(P), _z(RGH)
    zTS, zD, zTmp = _z(TS), _z(D), _z(TMP)
    zMom = _z(MOM)
    raw = [W_L * zL[i] + W_P * zP[i] + W_RGH * zRgh[i] + W_TS * zTS[i]
           + W_D * zD[i] + W_TMP * zTmp[i]
           + W_MOM_SPIKE * max(zMom[i], 0.0)
           for i in range(len(beats))]
    lo, hi = min(raw), max(raw)
    span = (hi - lo) or 1.0
    curve = [round((r - lo) / span, 4) for r in raw]
    return {"curve": curve,
            "features": {"L": L, "P": P, "D": D, "Rgh": RGH, "TS": TS,
                         "Mom": MOM, "Tmp": TMP}}


def section_energy(song, genre=""):
    """016: Farbood-grounded per-section scalar — the 5-parameter blend
    (density, register, harmonic tension, tempo, loudness proxy) averaged
    over each labeled section."""
    tc = tension_curve(song, genre)
    curve = tc["curve"]
    if not curve:
        return []
    secs = sorted((s for s in song.get("sections", []) or []
                   if isinstance(s, dict)),
                  key=lambda s: float(s.get("startBar", 0)))
    out = []
    for i, s in enumerate(secs):
        b0 = int(float(s.get("startBar", 0)) * 4)
        b1 = int(float(secs[i + 1].get("startBar", 0)) * 4) \
            if i + 1 < len(secs) else len(curve)
        win = curve[b0:max(b1, b0 + 1)] or [0.0]
        out.append({"name": str(s.get("name", "?")),
                    "startBar": b0 / 4.0,
                    "energy": round(sum(win) / len(win), 4)})
    return out


# ------------------------------------------------------- Farbood contours
def _contour(name, n=64):
    xs = [i / (n - 1) for i in range(n)]
    if name == "ramp":
        return xs
    if name == "arch":
        return [math.sin(math.pi * x) for x in xs]
    if name == "peak":            # inverted-V, late peak at 0.75
        return [x / 0.75 if x <= 0.75 else (1 - x) / 0.25 for x in xs]
    if name == "valley":
        return [1 - math.sin(math.pi * x) for x in xs]
    if name == "plateau":
        return [min(x / 0.15, 1.0, (1 - x) / 0.15) * 0.3 + 0.35 for x in xs]
    if name == "oscillating":
        return [0.5 + 0.5 * math.sin(2 * math.pi * 2.5 * x - math.pi / 2)
                for x in xs]
    raise ValueError(name)


ARC_FAMILIES = ("ramp", "arch", "peak", "valley", "plateau", "oscillating")


def _resample(curve, n=64):
    if len(curve) < 2:
        return [0.0] * n
    out = []
    for i in range(n):
        x = i * (len(curve) - 1) / (n - 1)
        j = int(x)
        f = x - j
        out.append(curve[j] * (1 - f) + curve[min(j + 1, len(curve) - 1)] * f)
    return out


def _pearson(a, b):
    n = len(a)
    ma, mb = sum(a) / n, sum(b) / n
    ca = [x - ma for x in a]
    cb = [x - mb for x in b]
    den = math.sqrt(sum(x * x for x in ca) * sum(x * x for x in cb)) or 1e-9
    return sum(x * y for x, y in zip(ca, cb)) / den


def classify_arc(curve):
    """(best_family, correlation) over the 6 Farbood contours."""
    if len(curve) < 8:
        return (None, 0.0)
    rs = _resample(curve)
    best, bc = None, -2.0
    for fam in ARC_FAMILIES:
        c = _pearson(rs, _contour(fam))
        if c > bc:
            best, bc = fam, c
    return (best, round(bc, 3))


# -------------------------------------------------------------- the court
def _smooth(curve, w=8):
    if len(curve) < w:
        return curve[:]
    out = []
    for i in range(len(curve)):
        a = max(0, i - w // 2)
        b = min(len(curve), i + w // 2 + 1)
        out.append(sum(curve[a:b]) / (b - a))
    return out


def court_tension_arc(song, genre=""):
    """027 shape+climax court. Convictions are the two HARD fails the
    research names (peak-in-first-third for non-hook-first genres;
    monotone decay from the door) — and ONLY for takes that declared
    FORM (sections >= 3 and >= 24 bars; corpus law 2026-07-15: a 16-bar
    loop has no narrative contract, and 70/243 of the corpus is loops).
    THE PAYOFF POSITION is the LAST near-max beat, not the first —
    double-drop form (eval_house drop1~drop2) reads early otherwise.
    Shape family match + resolution + range are advisories (r~0.62-0.68
    is the honest ceiling — never convict on a correlation)."""
    g = str(genre or "").lower().replace("-", "_").replace(" ", "_")
    if any(k in g for k in _TEXTURE):
        return {"court": "tension_arc", "ok": True,
                "skipped": "texture genre — a low plateau is the aesthetic"}
    lanes = [str(t.get("name", "")).lower()
             for t in song.get("tracks", []) or [] if isinstance(t, dict)]
    if any(nm.endswith(("_sketch", "_identity")) for nm in lanes):
        return {"court": "tension_arc", "ok": True,
                "skipped": "imported record (witness law)"}
    if lanes and all(nm.startswith("deck") for nm in lanes):
        return {"court": "tension_arc", "ok": True,
                "skipped": "dj blend — the set planner owns that arc"}
    secs = [s for s in song.get("sections", []) or [] if isinstance(s, dict)]
    bars = float(song.get("lengthBars", 0) or 0)
    if len(secs) < 3 or bars < 24:
        return {"court": "tension_arc", "ok": True,
                "skipped": "loop/sketch — no narrative contract "
                           "(needs >=3 sections and >=24 bars)"}
    tc = tension_curve(song, genre)
    curve = _smooth(tc["curve"])
    if len(curve) < 16:
        return {"court": "tension_arc", "ok": True, "skipped": "too short"}
    n = len(curve)
    cmax = max(curve)
    peak_i = max(i for i, c in enumerate(curve) if c >= cmax * 0.95)
    peak_pos = peak_i / (n - 1)
    rng = max(curve) - min(curve)
    flags, advisories = [], []
    if peak_pos < EARLY_EDGE and not any(k in g for k in _HOOK_FIRST):
        flags.append({"kind": "early_climax", "peak_pos": round(peak_pos, 3),
                      "why": f"the tension maximum lands {peak_pos:.0%} "
                             "through the song — the payoff spends itself "
                             "in the first third (r-14: peaks live at "
                             "~65-85%; golden section ~62% is the TURN)"})
    third = n // 3
    if third >= 4:
        first_third_mean = sum(curve[:third]) / third
        rest_mean = sum(curve[third:]) / (n - third)
        if first_third_mean > rest_mean + 0.15 and peak_pos < EARLY_EDGE:
            flags.append({"kind": "monotone_decay",
                          "why": "tension decays from the door and never "
                                 "recovers — the song tells its story "
                                 "backwards"})
    fam, corr = classify_arc(curve)
    if not (CLIMAX_LO <= peak_pos <= CLIMAX_HI) and peak_pos >= EARLY_EDGE:
        advisories.append({
            "kind": "climax_offside", "peak_pos": round(peak_pos, 3),
            "why": f"tension peak at {peak_pos:.0%} — the validated sweet "
                   "spot is 65-85% (final chorus / second drop)"})
    tail = curve[peak_i:]
    if len(tail) >= 4 and tail[-1] > curve[peak_i] - rng * 0.15 and \
            peak_pos < 0.95:
        advisories.append({
            "kind": "unresolved", "why": "tension never falls after the "
            "climax — resolution (the release) is what makes the build "
            "mean something (r-20: reward a RESOLVED arc)"})
    return {"court": "tension_arc", "ok": not flags, "flags": flags,
            "advisories": advisories, "family": fam, "corr": corr,
            "peak_pos": round(peak_pos, 3), "range": round(rng, 3)}


# ------------------------------------------------- 071 DROP-CONTRAST COURT
_EDM = ("edm", "house", "techno", "trance", "dubstep", "dnb",
        "drum_and_bass", "hardstyle", "big_room", "electro", "garage",
        "bass_music", "riddim", "breakbeat")


def _drop_sections(song):
    secs = sorted((s for s in song.get("sections", []) or []
                   if isinstance(s, dict)),
                  key=lambda s: float(s.get("startBar", 0)))
    return secs, [s for s in secs
                  if any(k in str(s.get("name", "")).lower()
                         for k in ("drop", "chorus"))]


def court_drop(song, genre=""):
    g = str(genre or "").lower().replace("-", "_").replace(" ", "_")
    if not any(k in g for k in _EDM):
        return {"court": "drop", "ok": True, "skipped": "not a drop genre"}
    secs, drops = _drop_sections(song)
    if not drops or len(secs) < 2:
        return {"court": "drop", "ok": True, "skipped": "no labeled drop"}
    en = section_energy(song, genre)
    if not en:
        return {"court": "drop", "ok": True, "skipped": "no tension curve"}
    by_name = {}
    for e in en:
        by_name.setdefault(e["name"], e)
    drop_names = {str(s.get("name", "")) for s in drops}
    drop_es = [e for e in en if e["name"] in drop_names]
    other_es = [e for e in en if e["name"] not in drop_names]
    if not drop_es or not other_es:
        return {"court": "drop", "ok": True, "skipped": "sections unmeasured"}
    flags = []
    dmax = max(e["energy"] for e in drop_es)
    omax = max(e["energy"] for e in other_es)
    if dmax < omax:
        loud = max(other_es, key=lambda e: e["energy"])
        flags.append({"kind": "drop_not_peak",
                      "drop_energy": dmax, "beat_by": loud["name"],
                      "why": f"the drop measures {dmax:.2f} but "
                             f"'{loud['name']}' measures {loud['energy']:.2f}"
                             " — the drop must be the GLOBAL maximum "
                             "(impact = contrast, r-14)"})
    # the engineered pre-drop dip: last pre-drop bar sits BELOW the drop
    # entry by a clear margin
    tc = tension_curve(song, genre)["curve"]
    for s in drops:
        b0 = int(float(s.get("startBar", 0)) * 4)
        if b0 < 8 or b0 + 4 > len(tc):
            continue
        pre = sum(tc[b0 - 4:b0]) / 4.0
        inside = sum(tc[b0:b0 + 4]) / 4.0
        if inside - pre < 0.08:
            flags.append({"kind": "no_predrop_dip",
                          "section": str(s.get("name", "?")),
                          "pre": round(pre, 3), "drop": round(inside, 3),
                          "why": f"'{s.get('name')}' enters at {inside:.2f} "
                                 f"from a pre-bar at {pre:.2f} — no "
                                 "engineered dip; producers cut 1-3dB /"
                                 " gap the kick+bass in the last bar so "
                                 "the drop HITS"})
    return {"court": "drop", "ok": not flags, "flags": flags}


def heal_drop(song, genre="", verdict=None):
    """Engineer the pre-drop dip: in the last bar before each flagged
    drop, scale non-riser velocities x0.7 (~-3dB) and clear kick/bass
    onsets from the final half-bar (the classic gap). CUT the build,
    never boost the drop (contrast law). Mutates; returns ledger."""
    v = verdict or court_drop(song, genre)
    if v.get("ok", True) or v.get("skipped"):
        return []
    import drum_grammar as DG
    edits = []
    for f in v.get("flags", []):
        if f.get("kind") != "no_predrop_dip":
            continue
        secs = [s for s in song.get("sections", []) or []
                if str(s.get("name", "")) == f.get("section")]
        if not secs:
            continue
        drop_beat = float(secs[0].get("startBar", 0)) * 4
        lo, hi = drop_beat - 4.0, drop_beat
        gap_lo = drop_beat - 2.0
        n_scaled = n_cleared = 0
        for t in song.get("tracks", []) or []:
            if not isinstance(t, dict) or t.get("muted"):
                continue
            nm = str(t.get("name", "")).lower()
            if any(k in nm for k in ("riser", "uplifter", "sweep", "fx",
                                     "impact", "crash")):
                continue
            role = DG.drum_role(t.get("name"))
            bassish = role == "kick" or any(k in nm for k in ("bass", "808",
                                                              "sub"))
            keep = []
            for n in t.get("notes", []) or []:
                s = float(n.get("start", 0))
                if lo <= s < hi:
                    if bassish and s >= gap_lo:
                        n_cleared += 1
                        continue          # the gap
                    n["vel"] = round(float(n.get("vel", 0.8)) * 0.7, 3)
                    n_scaled += 1
                keep.append(n)
            t["notes"] = keep
        edits.append({"kind": "predrop_dip", "section": f.get("section"),
                      "scaled": n_scaled, "cleared": n_cleared})
    return edits


# ------------------------------------------- 037 CINEMATIC COURT (w40)
_CINE = ("cinematic", "orchestral", "epic", "trailer", "soundtrack",
         "score", "filmi")


def court_cinematic(song, genre=""):
    """r-26: 3 acts with ADDITIVE layer gates + a STOPDOWN before the
    climax. ADVISORY-only (no cinematic corpus winners to calibrate
    conviction edges against — the honest posture until the bank has
    them): act-thirds must GROW in active lanes; a near-silence dip
    must precede the peak."""
    g = str(genre or "").lower().replace("-", "_").replace(" ", "_")
    if not any(k in g for k in _CINE):
        return {"court": "cinematic", "ok": True,
                "skipped": "not the cinematic family"}
    lanes_ok = [str(t.get("name", "")).lower()
                for t in song.get("tracks", []) or [] if isinstance(t, dict)]
    if any(nm.endswith(("_sketch", "_identity")) for nm in lanes_ok):
        return {"court": "cinematic", "ok": True,
                "skipped": "imported record (witness law)"}
    beats = _sounding(song)
    if len(beats) < 48:
        return {"court": "cinematic", "ok": True, "skipped": "too short"}
    n = len(beats)
    third = n // 3
    acts = [beats[:third], beats[third:2 * third], beats[2 * third:]]

    def act_density(cells):
        # the act's CHARACTERISTIC density = p75 of sounding-beat note
        # counts — robust to the stopdown's structural gap (a lone
        # heartbeat kick must not drag act three under act two)
        alive = sorted(len(c) for c in cells if c)
        if not alive:
            return 0.0
        return float(alive[min(int(len(alive) * 0.75),
                               len(alive) - 1)])
    m1, m2, m3 = (act_density(a) for a in acts)
    advisories = []
    if not (m1 <= m2 <= m3 and m3 > m1):   # never shrink; grow overall
        advisories.append({
            "kind": "not_additive",
            "acts": [round(m1, 1), round(m2, 1), round(m3, 1)],
            "why": f"act densities {m1:.1f} -> {m2:.1f} -> {m3:.1f} — "
                   "the cinematic arc ADDS layers act by act (each in "
                   "its own register); this one doesn't grow"})
    tc = _smooth(tension_curve(song, genre)["curve"])
    if len(tc) >= 16:
        cmax = max(tc)
        # the cinematic climax is STRUCTURALLY act three's max (the
        # global 95% band can cut an act-two shoulder instead)
        a3 = 2 * len(tc) // 3
        peak_i = a3 + max(range(len(tc) - a3),
                          key=lambda i: tc[a3 + i])
        pre = tc[max(0, a3 - len(tc) // 6):peak_i]
        if pre and min(pre) > 0.25 * cmax:
            advisories.append({
                "kind": "no_stopdown",
                "why": "no near-silence before the climax — the "
                       "STOPDOWN is structural (negative space makes "
                       "the hit land); drop to <=25% tension for a few "
                       "bars before the peak"})
    return {"court": "cinematic", "ok": True, "advisories": advisories}


# ---------------------------------------------------------------- aggregate
# W57 (r-20 item 144): FARBOOD TREND-SALIENCE — perceived tension
# tracks the SLOPE of features, not just their level; a change that
# CONTINUES the preceding trend direction weighs ~5x one that doesn't.
# Per-feature attentional/memory windows verbatim from TenseMusic
# (loudness 3/3s, roughness 3/4, tempo & onsets 3/20, pitch 5/12,
# tonal tension 7/12). Onset density stays a POSITIVE lever (the
# TenseMusic negative Lasso weight is a collinearity artifact — r-20
# adversarial finding). LEVEL curve keeps the court floors; the SLOPE
# curve judges whether builds actually BUILD.
FARBOOD_WINDOWS = {"L": (3.0, 3.0), "Rgh": (3.0, 4.0), "Tmp": (3.0, 20.0),
                   "D": (3.0, 20.0), "P": (5.0, 12.0), "TS": (7.0, 12.0)}


def trend_salience(series, spb, attn_s, mem_s, beta=5.0):
    """Pure kernel: trailing-window regression slope, continuation
    amplification (x beta when the slope's sign matches the PRECEDING
    window's), memory-window moving average."""
    n = len(series)
    if n < 3:
        return [0.0] * n
    w = max(int(round(attn_s / max(spb, 1e-6))), 2)
    slopes = []
    for i in range(n):
        a = max(i - w + 1, 0)
        seg = series[a:i + 1]
        m = len(seg)
        if m < 2:
            slopes.append(0.0)
            continue
        xm = (m - 1) / 2.0
        ym = sum(seg) / m
        num = sum((k - xm) * (seg[k] - ym) for k in range(m))
        den = sum((k - xm) ** 2 for k in range(m)) or 1.0
        slopes.append(num / den / max(spb, 1e-6))       # units: z per sec
    amp = []
    for i in range(n):
        prev = slopes[i - w] if i - w >= 0 else 0.0
        s = slopes[i]
        cont = (s > 0 and prev > 0) or (s < 0 and prev < 0)
        amp.append(s * beta if cont else s)
    mw = max(int(round(mem_s / max(spb, 1e-6))), 1)
    out = []
    for i in range(n):
        a = max(i - mw + 1, 0)
        out.append(sum(amp[a:i + 1]) / (i + 1 - a))
    return out


def tension_slope_curve(song, genre=""):
    """The summed per-feature trend-salience curve (per beat)."""
    tc = tension_curve(song, genre)
    f = tc.get("features") or {}
    if not f or not tc.get("curve"):
        return {"slope": [], "curve": tc.get("curve", [])}
    spb = 60.0 / float((song or {}).get("bpm", 120) or 120)
    total = None
    for k, (a_s, m_s) in FARBOOD_WINDOWS.items():
        if k not in f:
            continue
        s = trend_salience(_z(f[k]), spb, a_s, m_s)
        total = s if total is None else [t + x for t, x in zip(total, s)]
    return {"slope": total or [], "curve": tc["curve"]}


def court_trend(song, genre=""):
    """Builds must BUILD in TREND: a labeled build/rise section whose
    mean salience slope <= 0 reads flat to the ear no matter what the
    levels say (the ~0.5 -> 0.68 correlation jump lives here)."""
    secs = [s for s in (song or {}).get("sections", []) or []
            if isinstance(s, dict)]
    if len(secs) < 2:
        return {"court": "trend", "ok": True, "advisories": [],
                "skipped": "needs sections"}
    try:
        import form_court as _fc
        classes = [(_fc._sec_class(s.get("name")), s) for s in
                   sorted(secs, key=lambda s: float(s.get("startBar", 0)))]
    except Exception:
        return {"court": "trend", "ok": True, "advisories": [],
                "skipped": "no class table"}
    if not any(c == "build" for c, _ in classes):
        return {"court": "trend", "ok": True, "advisories": [],
                "skipped": "no build sections"}
    # WOLF LAW (874 corpus builds, 2026-07-16): the summed LEVEL curve
    # convicted real records — median corpus build rise = -0.02 because
    # real builds THIN the mix while tension rises (the EDM paradox:
    # drums out, riser up). Farbood's own frame judges FEATURES: a build
    # is a build when at least ONE tension lever (register, density,
    # roughness, tempo) trends UP through it. Convicted only when ALL
    # levers are flat/falling.
    tc = tension_curve(song, genre)
    feats = tc.get("features") or {}
    if not feats or not tc.get("curve"):
        return {"court": "trend", "ok": True, "advisories": [],
                "skipped": "no material"}
    zf = {k: _z(feats[k]) for k in ("P", "D", "Rgh", "Tmp")
          if k in feats}
    end_bar = float((song or {}).get("lengthBars", 0) or 0)
    advisories = []
    for i, (cls, s) in enumerate(classes):
        if cls != "build":
            continue
        a = int(float(s.get("startBar", 0)) * 4)
        b = int(float(classes[i + 1][1].get("startBar", end_bar)) * 4)             if i + 1 < len(classes) else int(end_bar * 4)
        rises = {}
        for k, z in zf.items():
            seg = z[a:min(b, len(z))]
            if len(seg) < 8:
                continue
            q = max(len(seg) // 4, 1)
            rises[k] = sum(seg[-q:]) / q - sum(seg[:q]) / q
        if not rises:
            continue
        best = max(rises, key=lambda k: rises[k])
        if rises[best] < 0.25:          # z units: no lever climbs
            advisories.append({
                "kind": "build_without_trend", "section": s.get("name"),
                "rises": {k: round(v, 3) for k, v in rises.items()},
                "why": (f"'{s.get('name')}' is labeled a build but NO "
                        "tension lever climbs through it (register/"
                        "density/roughness/tempo all flat or falling) — "
                        "the ear weighs continued direction 5x; ramp at "
                        "least one lever monotonically (rising riser "
                        "pitch, thickening rolls, opening filter)")})
    return {"court": "trend", "ok": True, "advisories": advisories}


def _lerdahl_delta(ch_a, ch_b, key_pc=0):
    """Lerdahl TPS delta = i + j + k straight from chord labels:
    i = circle-of-fifths steps between roots, j = shared-pc deficit,
    k = distance of the destination root from the key center (regional
    anchor). Chords-only — no note geometry."""
    import theory as _t
    a, b = _t.parse_chord(ch_a), _t.parse_chord(ch_b)
    if not a or not b:
        return None
    ra, rb = int(a["root_pc"]), int(b["root_pc"])
    fifths = [(ra + 7 * s) % 12 for s in range(12)]
    i = min(fifths.index(rb), 12 - fifths.index(rb))
    j = len(set(b["pcs"]) - set(a["pcs"]))
    k = min((rb - key_pc) % 12, (key_pc - rb) % 12) / 2.0
    return i + j + k


def tension_curve_chords(song, genre=""):
    """W87 (r-20 item 245): the chords[]-only Lerdahl fallback — per-bar
    tonal tension when the note geometry is sparse/absent."""
    chords = sorted((c for c in (song or {}).get("chords", []) or []
                     if isinstance(c, dict) and c.get("chord")),
                    key=lambda c: int(c.get("bar", 0)))
    if len(chords) < 3:
        return {"curve": [], "bars": []}
    try:
        import theory as _t
        k = _t.parse_key(song.get("key"))
        key_pc = int(k["tonic_pc"]) if k else 0
    except Exception:
        key_pc = 0
    vals, bars = [], []
    for a, b in zip(chords, chords[1:]):
        d = _lerdahl_delta(a["chord"], b["chord"], key_pc)
        if d is not None:
            vals.append(d)
            bars.append(int(b.get("bar", 0)))
    if not vals:
        return {"curve": [], "bars": []}
    lo, hi = min(vals), max(vals)
    span = (hi - lo) or 1.0
    return {"curve": [round((v - lo) / span, 4) for v in vals],
            "bars": bars}


def tension_lane(song, genre=""):
    """THE TENSION LANE: the curve as a MUTED utility lane whose gainDb
    automation IS the tension arc — visible on the canvas, diffable in
    the json, removable in one delete. Notes-based curve first,
    chords-only Lerdahl fallback when geometry is sparse. Mutates;
    idempotent by name."""
    tracks = (song or {}).setdefault("tracks", [])
    if any(t.get("name") == "_tension_curve" for t in tracks
           if isinstance(t, dict)):
        return []
    tc = tension_curve(song, genre)
    curve = tc.get("curve") or []
    pts = []
    if len(curve) >= 8:
        step = max(len(curve) // 64, 1)
        for i in range(0, len(curve), step):
            pts.append({"beat": float(i),
                        "v": round(-36.0 + 30.0 * curve[i], 2)})
        src_kind = "notes"
    else:
        cc = tension_curve_chords(song, genre)
        if len(cc.get("curve") or []) < 2:
            return []
        for bar, v in zip(cc["bars"], cc["curve"]):
            pts.append({"beat": (bar - 1) * 4.0,
                        "v": round(-36.0 + 30.0 * v, 2)})
        src_kind = "chords (Lerdahl fallback)"
    tracks.append({"name": "_tension_curve", "muted": True,
                   "gainDb": -60.0, "pan": 0.0, "notes": [],
                   "automation": [{"target": "gainDb", "points": pts}]})
    return [{"kind": "tension_lane", "points": len(pts),
             "source": src_kind,
             "why": (f"the tension arc rides a muted utility lane "
                     f"({len(pts)} points from {src_kind}) — SEE the "
                     "climax on the canvas; delete the lane to clear")}]


def court_tension(song, genre="", heal=False):
    out = {"tension_arc": court_tension_arc(song, genre),
           "drop": court_drop(song, genre),
           "cinematic": court_cinematic(song, genre)}
    tv = court_trend(song, genre)
    if tv.get("advisories"):
        out["trend"] = tv
    if heal:
        heals = {}
        if not out["drop"].get("ok", True):
            heals["drop"] = heal_drop(song, genre, out["drop"])
            if heals["drop"]:
                out["drop_after"] = court_drop(song, genre)
        out["heals"] = {k: v for k, v in heals.items() if v}
    out["ok"] = all(v.get("ok", True) for k, v in out.items()
                    if isinstance(v, dict) and not k.endswith("_after"))
    return out


def main():
    import argparse
    import json
    ap = argparse.ArgumentParser(description="THE TENSION KERNEL (wave 18)")
    ap.add_argument("song")
    ap.add_argument("--genre", default="")
    ap.add_argument("--curve", action="store_true")
    ap.add_argument("--lane", action="store_true",
                    help="W87: land the tension arc as a muted lane")
    ap.add_argument("--heal", action="store_true")
    args = ap.parse_args()
    song = json.load(open(args.song))
    if args.lane:
        eds = tension_lane(song, args.genre)
        if eds:
            json.dump(song, open(args.song, "w"), indent=1)
        print(json.dumps(eds, indent=1))
        raise SystemExit(0)
    if args.curve:
        tc = tension_curve(song, args.genre)
        fam, corr = classify_arc(tc["curve"])
        print(json.dumps({"family": fam, "corr": corr,
                          "curve": tc["curve"]}, indent=1))
        return 0
    v = court_tension(song, args.genre, heal=args.heal)
    if args.heal and v.get("heals"):
        with open(args.song, "w") as fh:
            json.dump(song, fh, indent=1)
        v["saved"] = args.song
    print(json.dumps(v, indent=1))
    return 0 if v["ok"] or args.heal else 1


if __name__ == "__main__":
    sys.exit(main())
