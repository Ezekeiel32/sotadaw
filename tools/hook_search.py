#!/usr/bin/env python3
"""THE MARRIAGE (B1 mount wave 3) — cell CONTOUR on DNA RHYTHM inside loop_gen.

loop_gen's constitution: the DNA owns the RHYTHM (genre identity), the take
owns the MELODIC PATH. This module upgrades the path with the SEARCH LAW:
the canonical hook take competes against (a) K fresh path rolls on the SAME
rhythm and (b) a CONTOUR TRANSPLANT — the canonical take re-pitched to
follow a real corpus cell's degree contour between held anchors. The judge
is search_law's courts + corpus meter under THE INCUMBENT LAW: the
canonical take stands unless a variant is strictly better. Every variant
shares the DNA rhythm bit-exact (onsets/lens/vels untouched) — the sealed
genre-identity laws cannot be violated by construction of the candidates.

improve(canonical, regen, genre, key, scale_abs, seed, role="lead")
  regen(sub_seed) -> a fresh hook take on the SAME rhythm (loop_gen passes
  a closure over hook_notes with random.Random(sub_seed) so the shared rng
  is never re-consumed — downstream rolls stay exactly where they were).
Returns (notes, why_or_None) — why only when the canonical was displaced.
Never raises. Kill-switch: SOTADAW_HOOKSEARCH=0.
"""
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

K_ROLLS = 2


def _lin(pitch, scale_abs):
    n = len(scale_abs)
    pc = pitch % 12
    idx = min(range(n), key=lambda i: min((scale_abs[i] - pc) % 12,
                                          (pc - scale_abs[i]) % 12))
    return (pitch // 12) * n + idx


def _pitch(lin, scale_abs):
    n = len(scale_abs)
    return 12 * (lin // n) + scale_abs[lin % n]


def _cell_deltas(genre, seed, role="lead", root=None):
    """A real corpus cell's degree-step contour (linear-degree deltas) —
    from the COMMITTED bank, never the living model (THE GIT-TRUTH LAW,
    2026-07-17: this ran inside the SEALED generator while the freshness
    rail re-mined telemetry/composer_cells.json under it; even the cell
    INDEX depended on the mutable bin length — every accept could break
    generation_court. library/contours.json carries the delta pools now;
    --bank-contours re-curates + reseals, explicitly)."""
    import composer_prior as cp
    import search_law as sl
    fams = ((sl._bank(root) or {}).get("cell_deltas") or {}).get(role) or {}
    pool = fams.get(cp.family_of(genre)) or fams.get("any")
    if not pool:
        return None
    rng = random.Random(seed)
    return list(pool[rng.randrange(len(pool))]) or None


def transplant(notes, deltas, scale_abs):
    """Re-pitch the canonical take to follow a corpus contour. RHYTHM IS
    SACRED: starts/lens/vels are copied bit-exact. Anchors (first + last
    note of each bar) hold the engine's own pitch — the hook's intent
    survives; the path between anchors walks the corpus contour, diatonic
    by construction, clamped to the take's own register."""
    if not notes or not deltas:
        return None
    order = sorted(range(len(notes)), key=lambda i: notes[i]["start"])
    by_bar = {}
    for i in order:
        by_bar.setdefault(int(notes[i]["start"] // 4.0), []).append(i)
    anchors = set()
    for _bar, idxs in by_bar.items():
        anchors.add(idxs[0])
        anchors.add(idxs[-1])
    lins = [_lin(n["pitch"], scale_abs) for n in notes]
    lo, hi = min(lins) - 2, max(lins) + 2
    out = [dict(n) for n in notes]
    cur, di = None, 0
    for j, i in enumerate(order):
        if i in anchors or j == 0:
            cur = lins[i]
            continue
        cur = max(lo, min(hi, cur + deltas[di % len(deltas)]))
        di += 1
        out[i]["pitch"] = int(_pitch(cur, scale_abs))
    return out


def improve(canonical, regen, genre, key, scale_abs, seed, role="lead",
            root=None):
    if os.environ.get("SOTADAW_HOOKSEARCH", "1") == "0" or not canonical:
        return canonical, None
    try:
        import search_law as sl
        # GIT-TRUTH judges only: banked lane hists, never the living
        # corpus (sl._judges) — the sealed path may not read telemetry
        lanes = (sl._bank(root) or {}).get("lane_hists") or {}
        cands = [("canonical", canonical)]
        for i in range(K_ROLLS):
            try:
                v = regen((seed * 1_000_003 + 7919 * (i + 1)) & 0x7fffffff)
                if v:
                    cands.append((f"roll{i + 1}", v))
            except Exception:
                pass
        deltas = _cell_deltas(genre, seed, role=role, root=root)
        tv = transplant(canonical, deltas, scale_abs) if deltas else None
        if tv:
            cands.append(("cell-contour", tv))
        if len(cands) == 1:
            return canonical, None
        scored = [(tag, notes, sl._score(notes, genre, key, role, lanes))
                  for tag, notes in cands]
        inc = scored[0][2]
        best = None
        for tag, notes, s in scored[1:]:
            if (s["key_bad"], s["adv"], s["dist"]) < \
                    ((best[2]["key_bad"], best[2]["adv"], best[2]["dist"])
                     if best else (9, 9999, 99.9)):
                best = (tag, notes, s)
        if best is None:
            return canonical, None
        bs = best[2]
        beats = (bs["key_bad"] < inc["key_bad"]
                 or (bs["key_bad"] == inc["key_bad"] and bs["adv"] < inc["adv"])
                 or (bs["key_bad"] == inc["key_bad"] and bs["adv"] == inc["adv"]
                     and bs["dist"] + sl.DIST_MARGIN < inc["dist"]))
        if beats:
            return best[1], (f"SEARCH LAW: {role} path took {best[0]} "
                             f"(adv {bs['adv']} vs {inc['adv']}, corpus-dist "
                             f"{bs['dist']} vs {inc['dist']}; rhythm = DNA, "
                             f"untouched)")
        return canonical, None
    except Exception:
        return canonical, None
