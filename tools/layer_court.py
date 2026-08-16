#!/usr/bin/env python3
"""THE LAYER COURT — do these two drum samples belong together?
(wave 37; R-18 item 022.)

The r-18 kernel, numpy-only, any two mono one-shots: an 'expensive'
kick is 3 layers each OWNING one band (sub 40-80 / body 80-200 / click
1-5k, carved by SUBTRACTION); layers with DIFFERENT transient shapes
reinforce while SIMILAR transients clutter; two samples fighting the
same band cancel or muddy. Phase discipline first: align transients
(<=20ms), THEN judge.

  band_fractions(x, sr)      6-band energy fractions from the onset
                             window (sub 20-60 / low 60-120 / lowmid
                             120-300 / mid 300-1k / himid 1-5k / air 5k+)
  transient_align(a, b, sr)  envelope xcorr, |lag| <= 20ms -> tau_ms
  compat(a, b, sr)           {tau_ms, overlap, attack_sim, score,
                             owned_a, owned_b, verdict}
        overlap    = histogram intersection of band fractions (high =
                     fighting the same bands)
        attack_sim = aligned 30ms-envelope correlation (high = same
                     transient shape = clutter)
        score      = (1-overlap) blended with transient difference —
                     >0.55 complement / 0.35-0.55 workable / <0.35 fight
  The symbolic count law (<=3 functional layers, zone caps) is w14's
  groove_court.court_layering — ONE RESOLVER, not re-encoded here.
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

BANDS = ((20, 60), (60, 120), (120, 300), (300, 1000), (1000, 5000),
         (5000, 20000))
BAND_NAMES = ("sub", "low", "lowmid", "mid", "himid", "air")
COMPLEMENT, FIGHT = 0.55, 0.35


def _mono(x):
    x = np.asarray(x, dtype="float64")
    return x.mean(axis=1) if x.ndim > 1 else x


def _onset(x, sr):
    env = np.abs(x)
    w = max(int(sr * 0.002), 4)
    env = np.convolve(env, np.ones(w) / w, "same")
    th = env.max() * 0.2
    i = int(np.argmax(env > th)) if (env > th).any() else 0
    return i, env


def band_fractions(x, sr):
    """Energy fractions over the 6 bands, 150ms window from onset."""
    x = _mono(x)
    i, _ = _onset(x, sr)
    seg = x[i:i + int(0.15 * sr)]
    if len(seg) < sr // 100:
        return None
    S = np.abs(np.fft.rfft(seg * np.hanning(len(seg)))) ** 2
    freqs = np.fft.rfftfreq(len(seg), 1.0 / sr)
    e = np.array([float(S[(freqs >= lo) & (freqs < hi)].sum())
                  for lo, hi in BANDS])
    tot = float(e.sum()) or 1e-18
    return e / tot


def transient_align(a, b, sr):
    """tau_ms shifting b onto a (envelope xcorr, |lag| <= 20ms)."""
    a, b = _mono(a), _mono(b)
    ia, ea = _onset(a, sr)
    ib, eb = _onset(b, sr)
    w = int(0.05 * sr)
    # anchor BOTH windows exactly at their onsets — an asymmetric
    # pre-roll (clipped at 0) skews the lag by the difference
    sa = ea[ia:ia + w]
    sb = eb[ib:ib + w]
    n = min(len(sa), len(sb))
    if n < sr // 200:
        return 0.0
    sa, sb = sa[:n] - sa[:n].mean(), sb[:n] - sb[:n].mean()
    lim = int(0.02 * sr)
    best_l, best_v = 0, -1e18
    for lag in range(-lim, lim + 1, max(1, sr // 22050)):
        if lag >= 0:
            v = float(np.dot(sa[lag:], sb[:n - lag]))
        else:
            v = float(np.dot(sa[:n + lag], sb[-lag:]))
        if v > best_v:
            best_l, best_v = lag, v
    return round((best_l + (ib - ia)) * 1000.0 / sr, 2)


def _attack_env(x, sr, i):
    seg = np.abs(_mono(x))[i:i + int(0.03 * sr)]
    if len(seg) < 8:
        return None
    w = max(int(sr * 0.001), 2)
    env = np.convolve(seg, np.ones(w) / w, "same")
    return env / (env.max() + 1e-12)


def compat(a, b, sr):
    """The score. >0.55 complement, <0.35 fight."""
    fa, fb = band_fractions(a, sr), band_fractions(b, sr)
    if fa is None or fb is None:
        return {"skipped": "one-shot too short"}
    overlap = float(np.minimum(fa, fb).sum())
    ia, _ = _onset(_mono(a), sr)
    ib, _ = _onset(_mono(b), sr)
    ea, eb = _attack_env(a, sr, ia), _attack_env(b, sr, ib)
    attack_sim = 0.0
    if ea is not None and eb is not None:
        n = min(len(ea), len(eb))
        ca, cb = ea[:n] - ea[:n].mean(), eb[:n] - eb[:n].mean()
        den = float(np.sqrt((ca ** 2).sum() * (cb ** 2).sum())) or 1e-12
        attack_sim = float(np.dot(ca, cb) / den)
    tau = transient_align(a, b, sr)
    # complementarity: unowned bands + different transient shapes
    score = 0.65 * (1.0 - overlap) + 0.35 * (1.0 - max(attack_sim, 0.0))
    verdict = ("complement" if score > COMPLEMENT else
               "workable" if score >= FIGHT else "fight")
    return {"tau_ms": tau, "overlap": round(overlap, 3),
            "attack_sim": round(attack_sim, 3), "score": round(score, 3),
            "owned_a": BAND_NAMES[int(np.argmax(fa))],
            "owned_b": BAND_NAMES[int(np.argmax(fb))],
            "verdict": verdict,
            "why": (f"bands overlap {overlap:.0%}, transients "
                    f"{'match' if attack_sim > 0.6 else 'differ'} "
                    f"(sim {attack_sim:.2f}) — "
                    + {"complement": "each layer owns its band; stack",
                       "workable": "carve the shared band by "
                                   "subtraction, then stack",
                       "fight": "same band + same transient = cancel/"
                                "mud; pick a different layer"}[verdict])}


def band_ownership(layers, sr):
    """W53 (r-18 item 080): the invariant that makes 'layering is
    subtraction' operational — each drum layer OWNS exactly one band;
    no two active layers may both hold >45% of their energy in the
    SAME band. layers = [(name, array)]. Returns dual-claim advisories
    with the carve prescription (the non-owner carves). The mono law
    (<100Hz stays mono) already convicts at the doctor/lowend seam."""
    fracs = []
    for name, x in layers:
        f = band_fractions(x, sr)
        if f is not None:
            fracs.append((name, f))
    advisories = []
    for bi, bname in enumerate(BAND_NAMES):
        claim = [(n, float(f[bi])) for n, f in fracs if f[bi] > 0.45]
        if len(claim) < 2:
            continue
        claim.sort(key=lambda c: -c[1])
        owner = claim[0][0]
        for loser, frac in claim[1:]:
            advisories.append({
                "kind": "band_dual_claim", "band": bname,
                "owner": owner, "carve": loser,
                "fractions": {owner: round(claim[0][1], 2),
                              loser: round(frac, 2)},
                "why": (f"'{owner}' and '{loser}' both hold >45% of "
                        f"their energy in {bname} — two claimants = "
                        f"phase risk and mud; {'high' if bi <= 1 else 'low'}"
                        f"-pass '{loser}' out of {bname} (the owner "
                        "keeps the band, the loser gets carved)")})
    return {"court": "band_ownership", "ok": True,
            "advisories": advisories,
            "owned": {n: BAND_NAMES[int(np.argmax(f))] for n, f in fracs}}


# W86 (r-18 item 243): the VERIFIED transient-shaper table — small
# moves are the safe default (+1-2dB adds clarity without artifacts);
# the full window is the ceiling, never the first move.
TRANSIENT_TABLE = {
    "kick":  {"attack_db": (4.0, 7.0), "sustain_db": (-4.0, -3.0)},
    "snare": {"attack_db": (2.0, 5.0), "sustain_db": (-6.0, -3.0)},
}


def heal_punch(song, track_name, role=None):
    """AUTO-DIAL when a layered kick/snare fails the punch check:
    fx_transient lands (or nudges) attack in SAFE +2dB steps toward
    the table window, sustain to the window's gentle edge. Idempotent
    per step; capped at the table ceiling."""
    t = next((x for x in (song or {}).get("tracks", []) or []
              if isinstance(x, dict) and x.get("name") == track_name),
             None)
    if t is None:
        return []
    r = role or next((k for k in TRANSIENT_TABLE
                      if k in str(track_name).lower()), None)
    if r is None:
        return []
    win = TRANSIENT_TABLE[r]
    fx = t.setdefault("fx", [])
    ft = next((f for f in fx if str(f.get("id")) == "fx_transient"), None)
    if ft is None:
        ft = {"id": "fx_transient",
              "params": {"attack": 2.0, "sustain": win["sustain_db"][1]}}
        fx.insert(0, ft)
        return [{"kind": "punch_heal", "track": track_name, "role": r,
                 "attack": 2.0,
                 "why": (f"'{track_name}': fx_transient lands (attack "
                         f"+2dB safe first move, sustain "
                         f"{win['sustain_db'][1]:g}) — the {r} table "
                         f"ceiling is +{win['attack_db'][1]:g}")}]
    cur = float((ft.get("params") or {}).get("attack", 0) or 0)
    if cur >= win["attack_db"][1]:
        return []                       # at the ceiling — punch must
    new_a = min(cur + 2.0, win["attack_db"][1])   # come from the source
    ft.setdefault("params", {})["attack"] = new_a
    return [{"kind": "punch_heal", "track": track_name, "role": r,
             "attack": new_a,
             "why": f"'{track_name}': attack {cur:g} -> {new_a:g}dB "
                    f"(ceiling {win['attack_db'][1]:g})"}]


def layer_count_guard(layers):
    """W61 (r-18 item 214): MORE layers != better — two well-chosen
    layers beat four fighting ones, and every extra multiplies phase
    risk. Cap: 3 functional layers per drum voice family; redundant
    same-band pairs already surface via band_ownership (referenced,
    never re-encoded). layers = [name, ...]."""
    fams = {}
    for name in layers:
        nm = str(name).lower()
        fam = next((f for f in ("kick", "snare", "clap", "hat", "tom",
                                "cym", "perc") if f in nm), None)
        if fam:
            fams.setdefault(fam, []).append(name)
    advisories = []
    for fam, members in fams.items():
        if len(members) > 3:
            advisories.append({
                "kind": "layer_count", "family": fam, "count": len(members),
                "layers": members,
                "why": (f"{len(members)} '{fam}' layers ({', '.join(members)})"
                        " — the cap is 3 functional layers per drum voice; "
                        "every extra multiplies phase risk. Keep sub/body/"
                        "click (or body/crack/air), carve or drop the rest")})
    return {"court": "layer_count", "ok": True, "advisories": advisories}


def heal_layers(song, ownership=None, pairs=None):
    """W56 (r-18 item 138): the auto-heal the score prescribes —
    (a) NUDGE: a 1-20ms transient lag between two layers (from
        compat()'s tau) shifts the LATER lane's notes into alignment;
    (b) CARVE: every band_dual_claim lands symbolically on the
        non-owner — fx_hipass above a contested low band, fx_filter
        (LP) below a contested high band, an fx_bell dip in the mids
        (gutting a layer's mids with LP/HP is not carving).
    Polarity flips stay phase_court's jurisdiction (one resolver).
    Once per lane (carve_healed / nudge_healed markers). Mutates;
    returns the edit ledger."""
    edits = []
    by_name = {t.get("name"): t for t in (song or {}).get("tracks", [])
               if isinstance(t, dict)}
    bpm = float((song or {}).get("bpm", 120) or 120)
    # the band edges mirror BANDS (one table, indexed the same way)
    for adv in (ownership or {}).get("advisories", []):
        if adv.get("kind") != "band_dual_claim":
            continue
        t = by_name.get(adv.get("carve"))
        if t is None or t.get("carve_healed"):
            continue
        bi = BAND_NAMES.index(adv["band"]) if adv.get("band") in             BAND_NAMES else None
        if bi is None:
            continue
        lo, hi = BANDS[bi]
        fx = t.setdefault("fx", [])
        if bi <= 1:                       # sub/low: HP the non-owner out
            fx.insert(0, {"id": "fx_hipass",
                          "params": {"cutoff": float(hi * 0.75)}})
            move = f"fx_hipass {hi * 0.75:.0f}Hz"
        elif bi >= 4:                     # hi-mid/air: LP it out
            fx.insert(0, {"id": "fx_filter",
                          "params": {"cutoff": float(lo), "res": 0.8}})
            move = f"fx_filter LP {lo}Hz"
        else:                             # mids: a surgical bell dip
            import math as _m
            fc = _m.sqrt(lo * hi)
            fx.append({"id": "fx_bell",
                       "params": {"freq": round(fc, 1), "gain": -4.5,
                                  "q": 1.4}})
            move = f"fx_bell -4.5dB @ {fc:.0f}Hz"
        t["carve_healed"] = True
        edits.append({"kind": "band_carve", "track": adv["carve"],
                      "band": adv["band"], "move": move,
                      "why": (f"'{adv['carve']}' carved out of "
                              f"{adv['band']} ({move}) — "
                              f"'{adv['owner']}' owns the band; "
                              "layering is subtraction")})
    for pair in (pairs or []):
        name_b = pair.get("late")
        tau = float(pair.get("tau_ms", 0) or 0)
        t = by_name.get(name_b)
        if t is None or t.get("nudge_healed") or not (1.0 <= abs(tau)
                                                      <= 20.0):
            continue
        d_beats = round(-tau * bpm / 60000.0, 6)
        for n in t.get("notes") or []:
            n["start"] = round(max(float(n.get("start", 0)) + d_beats,
                                   0.0), 6)
        t["nudge_healed"] = True
        edits.append({"kind": "transient_nudge", "track": name_b,
                      "ms": -tau, "beats": d_beats,
                      "why": (f"'{name_b}' lagged its partner by "
                              f"{tau:.1f}ms — nudged into the pocket "
                              "(a 1-20ms flam reads as smear, not "
                              "groove)")})
    return edits


def main():
    import argparse
    import soundfile as sf
    ap = argparse.ArgumentParser(description="THE LAYER COURT (wave 37)")
    ap.add_argument("a")
    ap.add_argument("b")
    args = ap.parse_args()
    xa, sra = sf.read(args.a, always_2d=True, dtype="float64")
    xb, srb = sf.read(args.b, always_2d=True, dtype="float64")
    if sra != srb:
        print(json.dumps({"skipped": "sample rates differ"}))
        return 0
    print(json.dumps(compat(xa, xb, sra), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
