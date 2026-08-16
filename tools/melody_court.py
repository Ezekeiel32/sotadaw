#!/usr/bin/env python3
"""THE MELODIC MIND (PRODUCER MIND backlog wave 12; R-2 research fold).

Deterministic melodic-craft kernels + a BANDS court over song.json lanes.
Every constant cites its study; the vocal is docs/research_producer_mind/r-2.json.

  lbdm_boundaries(notes)            Cambouropoulos LBDM phrase segmentation
                                    (exact math: r=|xi-xj|/(xi+xj), s=x*(rL+rR),
                                    weights pitch .25 / ioi .50 / rest .25,
                                    caps octave & whole-note; Simple-Picker
                                    peak AND S > mean + 0.5*sd)
  temperley_logp(notes, key)        two-Gaussian proximity+range x scale-degree
                                    plausibility (Temperley 2008 melody model)
  motif_economy(notes)              repetition (n-gram economy) + diversity —
                                    motif development = repetition WITHOUT loop
  interval_surprisal(notes)         mean -log2 P(interval) vs the corpus prior
                                    (Vos&Troost/Huron melodic interval shape)
  hook_score(notes, key)            FANTASTIC/IDyOM-weighted memorability
                                    composite (published beta signs, R-2)
  melodic_dimensions(notes, key)    the measured dimension vector
  court_melody(song, genre)         BANDS verdict — inverted-U [min,max] windows
                                    per genre family (R-2: 'more' is not better)
  heal_melody(song, genre, v)       octave-fold register wanderers (conservative)
  clamp_tessitura(notes, voice)     R-2 per-voice-type comfort clamp (sing lane)

The hot court path is pure stdlib. melody-features (Apache-2.0, the R-2
COURT ENGINE adoption) rides the SLOW lane via mf_features() below — eval,
calibration, gold-bank distillation; never per-proposal renders.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import theory as T  # noqa: E402

MAX_LIST = 24


def _sorted_notes(notes):
    out = []
    for n in notes or []:
        try:
            out.append({"start": float(n.get("start", 0.0)),
                        "pitch": int(n.get("pitch", 60)),
                        "len": max(float(n.get("len", n.get("length", 0.25))), 0.01),
                        "vel": float(n.get("vel", 0.8))})
        except Exception:
            continue
    return sorted(out, key=lambda n: (n["start"], n["pitch"]))


def _monophonic(notes):
    """Top-line reduction: at equal onsets keep the highest pitch (lead law)."""
    ns = _sorted_notes(notes)
    out = []
    for n in ns:
        if out and abs(n["start"] - out[-1]["start"]) < 1e-6:
            if n["pitch"] > out[-1]["pitch"]:
                out[-1] = n
            continue
        out.append(n)
    return out


# ================================================================ LBDM (R-2)
def lbdm_strengths(notes):
    """Local Boundary Detection Model strengths per note-transition.
    Returns list of S_i aligned to notes[1:] (boundary BEFORE note i+1)."""
    ns = _monophonic(notes)
    if len(ns) < 3:
        return []
    # parameter sequences per interface i (between note i and i+1)
    pitch_iv, ioi, rest = [], [], []
    for a, b in zip(ns, ns[1:]):
        pitch_iv.append(min(abs(b["pitch"] - a["pitch"]), 12.0))       # octave cap
        ioi.append(min(b["start"] - a["start"], 4.0))                  # whole-note cap
        rest.append(max(min(b["start"] - (a["start"] + a["len"]), 4.0), 0.0))

    def degrees(xs):
        r = []
        for x1, x2 in zip(xs, xs[1:]):
            s = x1 + x2
            r.append(abs(x1 - x2) / s if s > 1e-9 else 0.0)
        return r

    def strengths(xs):
        r = degrees(xs)
        out = [0.0] * len(xs)
        for i in range(len(xs)):
            rl = r[i - 1] if i - 1 >= 0 else 0.0
            rr = r[i] if i < len(r) else 0.0
            out[i] = xs[i] * (rl + rr)
        m = max(out) or 1.0
        return [x / m for x in out]

    sp, si, sr = strengths(pitch_iv), strengths(ioi), strengths(rest)
    return [0.25 * a + 0.50 * b + 0.25 * c for a, b, c in zip(sp, si, sr)]


def lbdm_boundaries(notes, k=0.5):
    """Simple-Picker: local peak AND S > mean + k*sd. Returns indices into the
    MONOPHONIC reduction — a boundary at i means 'phrase starts at note i+1'."""
    S = lbdm_strengths(notes)
    if not S:
        return []
    mean = sum(S) / len(S)
    sd = (sum((x - mean) ** 2 for x in S) / len(S)) ** 0.5
    thr = mean + k * sd
    out = []
    for i in range(len(S)):
        left = S[i - 1] if i else -1.0
        right = S[i + 1] if i + 1 < len(S) else -1.0
        if S[i] > thr and S[i] >= left and S[i] >= right:
            out.append(i)
    return out


def phrases(notes):
    """Split the monophonic top-line into LBDM phrases (lists of notes)."""
    ns = _monophonic(notes)
    if len(ns) < 4:
        return [ns] if ns else []
    cuts = set(lbdm_boundaries(ns))
    out, cur = [], []
    for i, n in enumerate(ns):
        cur.append(n)
        if i in cuts:
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


# ====================================================== Temperley model (R-2)
# Temperley 2008 probabilistic melody model (approx. published variances):
# proximity var ~7.2 (pitch ~ N(prev, 7.2)), range var ~23 (pitch ~ N(central,
# 23)); scale-degree term from the key profile. We use log-space and per-note
# normalized densities — a COMPARATIVE score, not a calibrated probability.
_PROX_VAR = 7.2
_RANGE_VAR = 23.0
# duration-weighted major/minor degree weights (Bellman-Budge shape, theory.py)
_DEG_MAJ = (16.8, 0.86, 12.95, 1.41, 13.49, 11.93, 1.25, 20.28, 1.8, 8.04, 0.62, 10.57)
_DEG_MIN = (18.16, 0.69, 12.99, 13.34, 1.07, 11.15, 1.38, 21.07, 7.49, 1.53, 0.92, 10.21)


def _norm_logpdf(x, mu, var):
    return -0.5 * math.log(2 * math.pi * var) - (x - mu) ** 2 / (2 * var)


def temperley_logp(notes, key=None, key_term=True):
    """Per-note log-plausibility list (aligned to monophonic reduction[1:]) +
    aggregate mean. Higher = more plausible melodic behavior. key_term=False
    scores proximity+range ONLY (the outlier path: pitch-class law belongs to
    the KEY court — a blue note is not a register wanderer)."""
    ns = _monophonic(notes)
    if len(ns) < 3:
        return [], 0.0
    if key is None:
        key = T.infer_key(ns)
    prof = None
    if key and key_term:
        table = _DEG_MAJ if T._is_majorish(key) else _DEG_MIN
        tot = sum(table)
        prof = [max(table[i] / tot, 1e-4) for i in range(12)]
    logs = []
    run_mean = float(ns[0]["pitch"])
    for i in range(1, len(ns)):
        p = float(ns[i]["pitch"])
        lp = _norm_logpdf(p, float(ns[i - 1]["pitch"]), _PROX_VAR)
        lp += _norm_logpdf(p, run_mean, _RANGE_VAR)
        if prof:
            rel = (ns[i]["pitch"] - key["tonic_pc"]) % 12
            lp += math.log(prof[rel])
        logs.append(lp)
        run_mean = 0.85 * run_mean + 0.15 * p
    return logs, (sum(logs) / len(logs) if logs else 0.0)


def temperley_outliers(notes, key=None, z=3.5):
    """Notes whose plausibility sits z robust-sigmas under the line's own
    MEDIAN (median + MAD — outliers cannot inflate their own yardstick) —
    the leap-happy noodle / register wanderer detector.

    PHRASE-AWARE (corpus lesson 2026-07-14: a lead that lifts the hook an
    octave is composing, not wandering): the proximity/range chain RESETS at
    LBDM phrase boundaries and each phrase's first note is never a defendant —
    only WITHIN-phrase incoherence convicts."""
    ns = _monophonic(notes)
    if len(ns) < 8:
        return []
    cuts = set(lbdm_boundaries(ns))
    scored = []                     # (note, logp) — within-phrase notes only
    phrase = []
    for i, n in enumerate(ns):
        phrase.append(n)
        if i in cuts or i == len(ns) - 1:
            if len(phrase) >= 4:
                logs, _ = temperley_logp(phrase, key, key_term=False)
                # logs align to phrase[1:]; skip the phrase-opening interval
                for j in range(1, len(logs)):
                    scored.append((phrase[j + 1], logs[j]))
            phrase = []
    if len(scored) < 6:
        return []
    logs = [lp for _, lp in scored]
    srt = sorted(logs)
    med = srt[len(srt) // 2]
    mad = sorted(abs(x - med) for x in logs)[len(logs) // 2] * 1.4826
    if mad < 0.8:
        mad = 0.8                                     # near-constant lines
    out = []
    for n, lp in scored:
        zz = (lp - med) / mad
        if zz < -z:
            out.append({"start": n["start"], "pitch": n["pitch"],
                        "name": T.midi_to_name(n["pitch"]),
                        "logp": round(lp, 2), "z": round(zz, 2)})
    # ORPHAN OPENERS: a spike big enough to mint its own LBDM boundary would
    # dodge the within-phrase chain. A real lift ESTABLISHES a register (its
    # phrase stays there); a spike is far from BOTH its own phrase body AND
    # the neighboring phrases — convict only when both hold.
    seen = {(o["start"], o["pitch"]) for o in out}

    def _med(xs):
        s = sorted(xs)
        return s[len(s) // 2] if s else None

    phs = phrases(ns)
    for pi, ph in enumerate(phs):
        neigh = []
        if pi > 0:
            neigh += [m["pitch"] for m in phs[pi - 1]]
        if pi + 1 < len(phs):
            neigh += [m["pitch"] for m in phs[pi + 1]]
        nmed = _med(neigh)
        if nmed is None:
            continue
        cands = []
        if len(ph) <= 3:
            # too short to establish a register: every far note is suspect
            for m in ph:
                mates = [x["pitch"] for x in ph if x is not m]
                if not mates or abs(m["pitch"] - _med(mates)) > 10:
                    cands.append(m)
        else:
            omed = _med([m["pitch"] for m in ph[1:]])
            if abs(ph[0]["pitch"] - omed) > 10:
                cands.append(ph[0])
        for c in cands:
            if abs(c["pitch"] - nmed) > 10 and \
                    (c["start"], c["pitch"]) not in seen:
                seen.add((c["start"], c["pitch"]))
                out.append({"start": c["start"], "pitch": c["pitch"],
                            "name": T.midi_to_name(c["pitch"]),
                            "logp": None, "z": None, "law": "orphan-opener"})
    out.sort(key=lambda o: o["start"])
    return out


# ======================================================== motif economy (R-2)
def _tokens(notes):
    """(interval-class, rhythm-class) token stream for self-similarity."""
    ns = _monophonic(notes)
    toks = []
    for a, b in zip(ns, ns[1:]):
        iv = b["pitch"] - a["pitch"]
        ivc = max(min(iv, 7), -7)                      # clamp wide leaps
        ioi = b["start"] - a["start"]
        # rhythm classes: 16th / 8th / quarter / half+ (swing-tolerant edges)
        rc = 0 if ioi < 0.375 else 1 if ioi < 0.75 else 2 if ioi < 1.5 else 3
        toks.append((ivc, rc))
    return toks


def motif_economy(notes, n=4):
    """repetition = 1 - distinct_ngrams/total (0 = through-composed,
    1 = pure loop); diversity = distinct unigram ratio. Motif development
    passes when repetition sits INSIDE the band and diversity is nonzero."""
    toks = _tokens(notes)
    if len(toks) < n + 2:
        return {"repetition": 0.0, "diversity": 1.0, "ngrams": 0}
    grams = [tuple(toks[i:i + n]) for i in range(len(toks) - n + 1)]
    distinct = len(set(grams))
    rep = 1.0 - distinct / len(grams)
    uni = len(set(toks)) / len(toks)
    return {"repetition": round(rep, 4), "diversity": round(uni, 4),
            "ngrams": len(grams)}


# ================================================== interval surprisal (R-2)
# Corpus melodic-interval prior (Vos & Troost 1989 / Huron sweep shape):
# unisons+steps dominate, tritone rare, octave more common than 7ths.
_IV_PRIOR = {0: 0.24, 1: 0.14, 2: 0.21, 3: 0.11, 4: 0.08, 5: 0.07, 6: 0.012,
             7: 0.05, 8: 0.022, 9: 0.02, 10: 0.012, 11: 0.005, 12: 0.03}
_IV_TOT = sum(_IV_PRIOR.values()) + 0.005


def interval_surprisal(notes):
    """Mean -log2 P(|interval|) against the corpus prior. LOW-but-nonzero is
    the memorability sweet spot (R-2: predictability breeds recall)."""
    ns = _monophonic(notes)
    if len(ns) < 3:
        return 0.0
    tot = 0.0
    cnt = 0
    for a, b in zip(ns, ns[1:]):
        iv = abs(b["pitch"] - a["pitch"])
        p = _IV_PRIOR.get(min(iv, 12), 0.005) / _IV_TOT
        if iv > 12:
            p *= 0.5 ** ((iv - 12) / 6.0)              # beyond-octave decay
        tot += -math.log2(max(p, 1e-6))
        cnt += 1
    return round(tot / cnt, 4)


# ============================================================ hook score (R-2)
# Published beta SIGNS as initial weights (R-2: phrase-length -0.30,
# surprisal -0.24, proximity +0.10, repetition +0.09, motif +0.08,
# primacy -0.10). Normalized dimensions; higher = more memorable.
def hook_score(notes, key=None):
    ns = _monophonic(notes)
    if len(ns) < 4:
        return 0.0
    ph = phrases(ns)
    mean_phrase = sum(len(p) for p in ph) / max(len(ph), 1)
    phrase_norm = min(mean_phrase / 16.0, 1.5)          # >16-note phrases hurt
    surp = interval_surprisal(ns) / 5.0                 # ~0..1
    steps = sum(1 for a, b in zip(ns, ns[1:]) if abs(b["pitch"] - a["pitch"]) <= 2)
    prox = steps / max(len(ns) - 1, 1)
    eco = motif_economy(ns)
    rep = eco["repetition"]
    motif = min(eco["ngrams"] and (1.0 - eco["diversity"]) or 0.0, 1.0)
    # primacy: does the FIRST phrase recur? (opening-motif return = recall)
    prim = 0.0
    if len(ph) >= 2 and len(ph[0]) >= 3:
        t0 = tuple(_tokens(ph[0])[:3])
        for p in ph[1:]:
            if len(p) >= 3 and tuple(_tokens(p)[:3]) == t0:
                prim = 1.0
                break
    score = (-0.30 * phrase_norm - 0.24 * surp + 0.10 * prox
             + 0.09 * rep + 0.08 * motif + 0.10 * prim)
    return round(score, 4)


# ===================================================== dimensions + BANDS
def melodic_dimensions(notes, key=None):
    ns = _monophonic(notes)
    if len(ns) < 4:
        return None
    ivs = [abs(b["pitch"] - a["pitch"]) for a, b in zip(ns, ns[1:])]
    leaps = sum(1 for iv in ivs if iv > 4)
    off = sum(1 for n in ns if abs(n["start"] - round(n["start"])) > 1e-6)
    pitches = [n["pitch"] for n in ns]
    eco = motif_economy(ns)
    _, tmean = temperley_logp(ns, key)
    return {"notes": len(ns),
            "leap_ratio": round(leaps / max(len(ivs), 1), 4),
            "mean_interval": round(sum(ivs) / max(len(ivs), 1), 3),
            "offbeat_ratio": round(off / len(ns), 4),
            "repetition": eco["repetition"],
            "diversity": eco["diversity"],
            "ambitus": max(pitches) - min(pitches),
            "surprisal": interval_surprisal(ns),
            "temperley": round(tmean, 3),
            "hook": hook_score(ns, key)}


# BANDS not floors (R-2: every melodic dimension is an inverted U — encode
# [min,max] windows; outside EITHER edge flags). CORPUS-CALIBRATED 2026-07-14
# (459 melodic lanes across 165 committed songs, per-role percentiles — the
# R-16 self-measure law: never trust blog numbers over your own corpus):
#   CONVICTION edges sit BEYOND the corpus p98 per lane ROLE — a court that
#   cries wolf is worse than no court (62% of the corpus flagged under the
#   first seed bands; these edges flag ~the true tail only).
#   SOFT bands (taste windows) ride as ADVISORIES, never convictions.
EXTREMES = {   # role -> dim -> [min,max]; outside = conviction evidence
    "lead":  {"leap_ratio": (0.0, 0.70), "ambitus": (2, 52),
              "surprisal": (0.0, 4.8)},
    "bass":  {"ambitus": (0, 40), "surprisal": (0.0, 5.6)},
    "arp":   {"surprisal": (0.0, 5.6)},
    "other": {"ambitus": (0, 44), "surprisal": (0.0, 5.6)},
}
SOFT_BANDS = {  # taste advisories (corpus p10..p90-class windows)
    "lead":  {"leap_ratio": (0.0, 0.45), "repetition": (0.05, 0.93),
              "ambitus": (5, 41), "surprisal": (2.0, 3.9)},
    "bass":  {"repetition": (0.05, 0.99), "ambitus": (2, 24)},
    "arp":   {"repetition": (0.30, 1.0)},
    "other": {"repetition": (0.02, 0.97), "ambitus": (3, 30)},
}
_FAM_TWEAKS = {  # family -> role -> dim -> window override (conviction layer)
    "jazz": {"lead": {"leap_ratio": (0.0, 0.80), "surprisal": (0.0, 5.4)}},
    "pop":  {"lead": {"leap_ratio": (0.0, 0.62)}},
}
_BAND_FAMILY = {
    "pop": ("pop", "kpop", "k_pop", "jpop", "city_pop", "citypop", "indie",
            "rnb", "r_b", "country", "ballad"),
    "jazz": ("jazz", "bebop", "swing", "bossa", "fusion", "neosoul", "neo_soul",
             "blues", "gospel", "soul"),
}
# genres whose melodic language is texture, not line — the court stands down
_EXEMPT = ("ambient", "drone", "noise", "experimental", "atonal", "musique",
           "meditation", "field", "psybient", "dark_ambient", "soundscape")

_ROLE_WORDS = (
    ("bass", ("bass", "808", "sub")),
    ("arp", ("arp", "arpegg", "pluck", "sequence", "seq_")),
    ("lead", ("lead", "melody", "vocal", "topline", "hook", "theme", "voice",
              "choir", "sax", "flute", "violin", "trumpet", "whistle", "solo")),
)


def lane_role(name):
    nm = str(name or "").lower()
    for role, words in _ROLE_WORDS:
        if any(w in nm for w in words):
            return role
    return "other"


def bands_for(genre, role="lead"):
    """(conviction_extremes, soft_advisory_bands) for a lane role + genre."""
    hard = dict(EXTREMES.get(role, EXTREMES["other"]))
    soft = dict(SOFT_BANDS.get(role, SOFT_BANDS["other"]))
    g = str(genre or "").lower()
    for fam, keys in _BAND_FAMILY.items():
        if any(k in g for k in keys):
            hard.update(_FAM_TWEAKS.get(fam, {}).get(role, {}))
            break
    return hard, soft


# =============================================================== THE COURT
def _lead_lanes(song):
    """Melodic lanes the melody court judges: music_court's court_role says
    'melodic' (witness/fx/drums exempt) and the lane carries enough notes."""
    import music_court as MC
    out = []
    for t in song.get("tracks", []) or []:
        if not isinstance(t, dict) or t.get("muted"):
            continue
        if MC.court_role(t) != "melodic":
            continue
        nm = str(t.get("name", "")).lower()
        if any(w in nm for w in ("chop", "slice", "stutter", "glitch", "cut")):
            continue                    # sliced-audio trigger lanes, not lines
        # chordal beds aren't melodies: skip lanes where most onsets are stacks
        ns = _sorted_notes(t.get("notes"))
        if len(ns) < 8:
            continue
        starts = {}
        for n in ns:
            starts[n["start"]] = starts.get(n["start"], 0) + 1
        stack_ratio = sum(1 for v in starts.values() if v >= 3) / max(len(starts), 1)
        if stack_ratio > 0.5:
            continue
        out.append(t)
    return out


def court_melody(song, genre=""):
    """BANDS verdict per melodic lane + verse/chorus differentiation (R-2).
    Conservative: ok=False only on HARD evidence (>=2 off-band dims on a lane,
    or >=3 temperley outliers on a lane); single-dim drifts ride as advisories.
    """
    g = str(genre or "").lower()
    if any(k in g for k in _EXEMPT):
        return {"court": "melody", "ok": True, "skipped": f"exempt genre '{genre}'"}
    lanes = _lead_lanes(song)
    if not lanes:
        return {"court": "melody", "ok": True, "skipped": "no melodic lanes"}
    key = T.parse_key(song.get("key"))
    flags, advisories, per_lane = [], [], {}
    for t in lanes:
        name = t.get("name", "?")
        dims = melodic_dimensions(t.get("notes"), key)
        if not dims:
            continue
        role = lane_role(name)
        hard, soft = bands_for(genre, role)
        per_lane[name] = dict(dims, role=role)
        off_hard, off_soft = [], []
        for table, sink in ((hard, off_hard), (soft, off_soft)):
            for dim, (lo, hi) in table.items():
                v = dims.get(dim)
                if v is None:
                    continue
                if v < lo - 1e-9 or v > hi + 1e-9:
                    sink.append({"dim": dim, "value": v, "band": [lo, hi]})
        # THE OCTAVE-PUMP EXEMPTION (eval_soca bass, 2026-07-14): a lane whose
        # intervals are heavily EXACT octaves is playing the disco/soca/synth
        # octave-bass idiom — register pops are the writing, not wandering.
        _ns = _monophonic(t.get("notes"))
        _ivs = [abs(b["pitch"] - a["pitch"]) for a, b in zip(_ns, _ns[1:])]
        octave_pump = _ivs and sum(1 for iv in _ivs if iv == 12) / len(_ivs) >= 0.25
        outs = [] if octave_pump else \
            temperley_outliers(t.get("notes"), key, z=4.5)
        # THE FOLDABLE LAW: a wanderer conviction must be HEALABLE — only
        # notes an octave-fold would actually move (>9 semitones off their
        # own phrase's register) count as conviction evidence. In-register
        # wide leaps are writing style, not register incoherence.
        if outs:
            ph_med = {}
            for ph in phrases(t.get("notes")):
                ps = sorted(m["pitch"] for m in ph)
                med = ps[len(ps) // 2]
                for m in ph:
                    ph_med[(m["start"], m["pitch"])] = med
            for o in outs:
                med = ph_med.get((o["start"], o["pitch"]))
                o["foldable"] = bool(med is None
                                     or abs(o["pitch"] - med) > 9
                                     or o.get("law") == "orphan-opener")
            per_lane[name]["outliers"] = outs[:MAX_LIST]
        foldable = [o for o in outs if o.get("foldable")]
        if off_hard:
            flags.append({"kind": "off_band", "track": name, "role": role,
                          "dims": off_hard,
                          "why": f"{name} ({role}): " + ", ".join(
                              f"{o['dim']}={o['value']} outside [{o['band'][0]}"
                              f",{o['band'][1]}]" for o in off_hard)
                          + " — beyond the corpus's own p98 for this role; "
                            "melodic dimensions are inverted-U windows"})
        if off_soft:
            advisories.append({"kind": "band_drift", "track": name,
                               "role": role, "dims": off_soft})
        n_notes = dims.get("notes", 0) or 1
        if len(foldable) >= 4 and len(outs) / n_notes <= 0.2:
            flags.append({"kind": "wanderer", "track": name,
                          "notes": foldable[:MAX_LIST],
                          "why": f"{name}: {len(outs)} notes sit far off the "
                                 "line's own register/proximity behavior "
                                 "(leap-happy noodling) — fold or re-anchor"})
    # verse/chorus differentiation (R-2): chorus must EARN its name on the
    # lead lane — higher register OR more repetitive OR more disjunct.
    vc = _verse_chorus_check(song, lanes, key)
    if vc:
        flags.append(vc)
    return {"court": "melody", "ok": not flags, "flags": flags,
            "advisories": advisories, "per_lane": per_lane}


def _sec_windows(song, kind):
    import meter as METER
    mtr = METER.song_meter(song)
    secs = sorted((s for s in song.get("sections", []) or [] if isinstance(s, dict)),
                  key=lambda s: float(s.get("startBar", 0)))
    wins = []
    for i, s in enumerate(secs):
        nm = str(s.get("name", "")).lower()
        cls = "chorus" if any(w in nm for w in ("chorus", "hook", "drop")) else \
              "verse" if "verse" in nm else "other"
        if cls != kind:
            continue
        b0 = float(s.get("startBar", 0))
        b1 = float(secs[i + 1].get("startBar", song.get("lengthBars", b0 + 8))) \
            if i + 1 < len(secs) else float(song.get("lengthBars", b0 + 8))
        wins.append((METER.bar_start_q(mtr, int(b0)), METER.bar_start_q(mtr, int(b1))))
    return wins


def _verse_chorus_check(song, lanes, key):
    ch_w = _sec_windows(song, "chorus")
    v_w = _sec_windows(song, "verse")
    if not ch_w or not v_w:
        return None
    leads = [t for t in lanes if lane_role(t.get("name")) == "lead"]
    if not leads:
        return None
    lead = max(leads, key=lambda t: len(t.get("notes") or []))
    ns = _monophonic(lead.get("notes"))

    def grab(wins):
        return [n for n in ns if any(a - 1e-6 <= n["start"] < b for a, b in wins)]
    ch, ve = grab(ch_w), grab(v_w)
    if len(ch) < 8 or len(ve) < 8:
        return None
    def mean_pitch(xs):
        return sum(n["pitch"] for n in xs) / len(xs)
    def mean_iv(xs):
        if len(xs) < 2:
            return 0.0
        ivs = [abs(b["pitch"] - a["pitch"]) for a, b in zip(xs, xs[1:])]
        return sum(ivs) / len(ivs)
    higher = mean_pitch(ch) > mean_pitch(ve) + 0.8
    more_rep = motif_economy(ch)["repetition"] > motif_economy(ve)["repetition"] + 0.04
    more_disjunct = mean_iv(ch) > mean_iv(ve) + 0.35
    if higher or more_rep or more_disjunct:
        return None
    return {"kind": "chorus_indistinct", "track": lead.get("name", "?"),
            "why": (f"chorus on '{lead.get('name', '?')}' is not higher "
                    f"({mean_pitch(ch):.1f} vs {mean_pitch(ve):.1f}), not more "
                    "repetitive, not more disjunct than the verse — the hook "
                    "must contrast (lift register, tighten the motif, or open "
                    "the intervals)")}


# ================================================================= THE HEAL
def heal_melody(song, genre="", verdict=None):
    """Conservative: octave-fold ONLY the wanderer notes (preserves pitch
    class — key court remains the pitch-class law). Mutates song; returns
    the edit ledger."""
    v = verdict or court_melody(song, genre)
    edits = []
    if v.get("skipped"):
        return edits
    wander = {}
    for f in v.get("flags", []):
        if f.get("kind") == "wanderer":
            wander[f["track"]] = {(o["start"], o["pitch"]) for o in f["notes"]}
    if not wander:
        return edits
    for t in song.get("tracks", []) or []:
        name = t.get("name", "?")
        if name not in wander:
            continue
        ns = _monophonic(t.get("notes"))
        if len(ns) < 4:
            continue
        center = sorted(n["pitch"] for n in ns)[len(ns) // 2]
        for n in t.get("notes", []) or []:
            try:
                key_ = (float(n.get("start", 0)), int(n.get("pitch", 60)))
            except Exception:
                continue
            if key_ not in wander[name]:
                continue
            p = int(n["pitch"])
            best = p
            while best - center > 7 and best - 12 >= 0:
                best -= 12
            while center - best > 7 and best + 12 <= 127:
                best += 12
            if best != p:
                n["pitch"] = best
                edits.append({"track": name, "start": key_[0],
                              "old": T.midi_to_name(p), "new": T.midi_to_name(best),
                              "kind": "octave_fold"})
    return edits


# ======================================================== tessitura (R-2)
# comfortable tessitura per voice type (R-2: women C4-A4, men A2-F4 default;
# pop ambitus cap ~1.5 octaves). MIDI windows; center = window midpoint.
TESSITURA = {
    "female":  (60, 69), "male": (45, 65),
    "soprano": (60, 84), "alto": (55, 74), "tenor": (48, 67), "bass": (40, 64),
}


def clamp_tessitura(notes, voice="female", ambitus_cap=19):
    """Transpose the WHOLE line by octaves to center it in the voice's comfort
    window, then fold outliers inward by octave until the ambitus cap holds.
    Mutates note dicts in place; returns the edit ledger."""
    ns = [n for n in notes or [] if isinstance(n, dict) and "pitch" in n]
    if not ns:
        return []
    lo, hi = TESSITURA.get(str(voice or "").lower(), TESSITURA["female"])
    center = (lo + hi) / 2.0
    pitches = sorted(int(n["pitch"]) for n in ns)
    median = pitches[len(pitches) // 2]
    shift = round((center - median) / 12.0) * 12
    edits = []
    if shift:
        for n in ns:
            n["pitch"] = int(n["pitch"]) + shift
        edits.append({"kind": "transpose", "semitones": shift})
    # fold rare outliers toward the window
    for n in ns:
        p = int(n["pitch"])
        q = p
        while q > hi + 5 and q - 12 >= 0:
            q -= 12
        while q < lo - 5 and q + 12 <= 127:
            q += 12
        if q != p:
            n["pitch"] = q
            edits.append({"kind": "fold", "old": p, "new": q})
    # ambitus cap: fold the farthest tail inward until span <= cap
    for _ in range(8):
        ps = [int(n["pitch"]) for n in ns]
        span = max(ps) - min(ps)
        if span <= ambitus_cap:
            break
        mid = (max(ps) + min(ps)) / 2.0
        tail_hi = [n for n in ns if int(n["pitch"]) == max(ps)]
        tail_lo = [n for n in ns if int(n["pitch"]) == min(ps)]
        victims = tail_hi if max(ps) - mid >= mid - min(ps) else tail_lo
        direction = -12 if victims is tail_hi else 12
        for n in victims:
            old = int(n["pitch"])
            n["pitch"] = old + direction
            edits.append({"kind": "ambitus_fold", "old": old, "new": old + direction})
    return edits


# ================================================== melody-features bridge
def mf_features(notes, bpm=120.0, which=("ambitus", "pitch_entropy",
                                         "duration_entropy")):
    """SLOW-LANE bridge to the melody-features package (R-2 court engine,
    Apache-2.0): 200+ FANTASTIC/IDyOM/jSymbolic features for eval +
    calibration. Skip-safe: returns None when the package is absent."""
    try:
        from melody_features.features import Melody
        import melody_features.features as F
    except Exception:
        return None
    ns = _monophonic(notes)
    if len(ns) < 3:
        return None
    spb = 60.0 / max(float(bpm), 1.0)
    mel = Melody({"MIDI Sequence": "inline",
                  "pitches": [n["pitch"] for n in ns],
                  "starts": [n["start"] * spb for n in ns],
                  "ends": [(n["start"] + n["len"]) * spb for n in ns]},
                 tempo=float(bpm))
    out = {}
    for name in which:
        fn = getattr(F, name, None)
        if fn is None:
            continue
        try:
            out[name] = fn(mel.pitches) if name == "ambitus" else fn(mel)
        except Exception:
            try:
                out[name] = fn(mel)
            except Exception:
                continue
    return out or None


def main():
    import argparse
    import json
    ap = argparse.ArgumentParser(description="THE MELODIC MIND (R-2)")
    ap.add_argument("song")
    ap.add_argument("--genre", default="")
    ap.add_argument("--heal", action="store_true")
    args = ap.parse_args()
    song = json.load(open(args.song))
    v = court_melody(song, args.genre)
    if args.heal and not v.get("ok", True):
        v["heals"] = heal_melody(song, args.genre, v)
        with open(args.song, "w") as f:
            json.dump(song, f, indent=1)
        v["saved"] = args.song
    print(json.dumps(v, indent=1))
    return 0 if v.get("ok") or args.heal else 1


if __name__ == "__main__":
    sys.exit(main())
