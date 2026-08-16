#!/usr/bin/env python3
"""THE BRAIN BR-D wave 2 — THE CELL PRIOR (docs/SPEC_THE_BRAIN.md PART II B1).

The markov organ was REFUSED by its own floor (2026-07-16: nearest-real-lane
interval distance 1.00 vs the un-learned baseline's 0.62 — token-level walks
scramble LINE CHARACTER even when every token is corpus-real). The refusal
named the fix: model at the PHRASE level. This organ mines the corpus into
CELLS (contiguous phrase fragments cut at rests / span / note-count seams)
and composes by RECOMBINATION: pick cells, transpose degree-wise into the
asked key, stitch with voice-leading, mutate occasionally. Interval character
comes from real phrases BY CONSTRUCTION — the floor meter (nearest real lane)
measures exactly what recombination preserves.

CELL = {"src", "span" (tiling beats, integer), "d" degrees 0..6,
        "c" chroma -1|0|1 (real accidentals KEPT, gated per target key),
        "o" octave offsets (exact reconstruction residue — intervals
        reproduce bit-true at ds=0), "on" onsets from cell start,
        "ln" lens, "v" vels}

LAWS (novelty court, CELL form — cells ARE corpus, so the theft line is
arrangement-level, matching composer_prior's substantial-similarity law):
- MAX_NOTES=12 per cell < RUN_HARD=16: no single cell is a wholesale-replay run
- adjacent cells NEVER share a source (enforced at pick)
- no source attributes > COVER_FRAC of a take's notes
- >= 2 distinct sources per take whenever the bin has them
- DETERMINISM: same model + seed + ask = byte-identical candidates
- HONEST DRYNESS: a bin under MIN_CELLS refuses ([]) — expanders stand, forever
"""
import argparse
import json
import math
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
DEF_ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import composer_prior as cp

MODEL_NAME = "composer_cells.json"
GAP_BEATS = 1.0            # a rest this long ends a phrase
MAX_SPAN = 8.0             # 2 bars — idiom-length, never a section
MAX_NOTES = 12             # < composer_prior.RUN_HARD: a cell can't be theft
MIN_NOTES = 3
MIN_CELLS = 24             # per bin — under this, refuse (expanders stand)
CAP_PER_BIN = 4000         # deterministic stride-thin above this
MUT_P = 0.35               # in-scale transpose probability per placed cell
COVER_FRAC = 0.5           # one source claiming more of a take = a copy
SAMPLE_K = 24              # candidate cells scored per placement


def _pure_scale(key_text, genre=""):
    """(pure 7-degree scale, THE COURT'S allowance set). The chroma gate must
    be allowed_pcs(key, GENRE) — the exact set the key court judges with. The
    genre-blank set admits the harmonic-minor leading tone the funk court
    convicts (measured 2026-07-16: one D#2 in E minor = the whole floor)."""
    try:
        import theory
        k = theory.parse_key(str(key_text or ""))
        if not k:
            return None, None
        scale = sorted(k["scale_pcs"])
        if len(scale) < 5:
            return None, None
        allowed = set(theory.allowed_pcs(k, str(genre or "")))
        return scale, allowed
    except Exception:
        return None, None


def _nearest_deg(pc, scale):
    d = min(range(len(scale)),
            key=lambda i: min((scale[i] - pc) % 12, (pc - scale[i]) % 12))
    diff = ((pc - scale[d] + 6) % 12) - 6
    return d, max(-1, min(1, int(diff)))


def _cell_of(notes, scale, src):
    """One mined cell. Octave offsets are the exact reconstruction residue:
    pitch_j == C + rec_j + 12*o_j with rec_j = scale[d_j] + c_j — a raw
    (pitch//12 - oct0) octave loses the borrow when an accidental wraps the
    pc past 11/-1 and widens the realized interval by an octave."""
    t0 = float(notes[0]["start"])
    d0, c0 = _nearest_deg(int(notes[0]["pitch"]) % 12, scale)
    rec0 = scale[d0] + c0
    base = int(notes[0]["pitch"]) - rec0
    cell = {"src": src, "d": [], "c": [], "o": [], "on": [], "ln": [], "v": []}
    end = 0.0
    for n in notes:
        p = int(n["pitch"])
        d, c = _nearest_deg(p % 12, scale)
        rec = scale[d] + c
        cell["d"].append(d)
        cell["c"].append(c)
        cell["o"].append((p - rec - base) // 12)
        on = round(float(n["start"]) - t0, 3)
        ln = round(min(float(n.get("len", 0.5)), MAX_SPAN), 3)
        cell["on"].append(on)
        cell["ln"].append(ln)
        cell["v"].append(round(float(n.get("vel", 0.8)), 2))
        end = max(end, on + ln)
    cell["span"] = float(min(MAX_SPAN, max(1.0, math.ceil(end - 1e-6))))
    return cell


def _sig(cell):
    return json.dumps([cell["d"], cell["c"], cell["o"], cell["on"],
                       cell["ln"]], separators=(",", ":"))


def cut_cells(doc, key=None):
    """[(role, [cell...])] — phrases cut at rests >= GAP_BEATS, capped at
    MAX_SPAN beats / MAX_NOTES notes. Keyless docs yield nothing (never guess)."""
    scale, _ = _pure_scale(key or doc.get("key"))
    if scale is None:
        return []
    out = []
    for tr in doc.get("tracks") or []:
        role = cp.role_of(tr.get("name"))
        if role is None:
            continue
        notes = sorted((n for n in tr.get("notes") or []
                        if isinstance(n.get("pitch"), (int, float))),
                       key=lambda n: (float(n.get("start", 0.0)),
                                      int(n["pitch"])))
        if len(notes) < MIN_NOTES:
            continue
        cells, cur, prev_end = [], [], None
        for n in notes:
            start = float(n.get("start", 0.0))
            if cur and (
                    (prev_end is not None and start - prev_end >= GAP_BEATS)
                    or start - float(cur[0].get("start", 0.0)) >= MAX_SPAN
                    or len(cur) >= MAX_NOTES):
                if len(cur) >= MIN_NOTES:
                    cells.append(cur)
                cur = []
            cur.append(n)
            prev_end = start + float(n.get("len", 0.5))
        if len(cur) >= MIN_NOTES:
            cells.append(cur)
        if cells:
            out.append((role, cells, scale))
    return out


def mine(docs_with_meta, root=None, persist=True):
    """docs_with_meta = [(doc, genre, doc_id)] -> per-(family, role) cell
    banks, sig-deduped (an idiom shared verbatim across docs banks once)."""
    model = {"bins": {}, "version": 1}
    seen = {}
    for doc, genre, doc_id in docs_with_meta:
        fam = cp.family_of(genre)
        for role, groups, scale in cut_cells(doc):
            for g in groups:
                cell = _cell_of(g, scale, doc_id)
                sig = _sig(cell)
                for f in (fam, "any"):
                    key = f"{f}/{role}"
                    if sig in seen.setdefault(key, set()):
                        continue
                    seen[key].add(sig)
                    model["bins"].setdefault(key, []).append(cell)
    for key, cells in model["bins"].items():
        if len(cells) > CAP_PER_BIN:
            stride = len(cells) / float(CAP_PER_BIN)
            model["bins"][key] = [cells[int(i * stride)]
                                  for i in range(CAP_PER_BIN)]
    if persist:
        _persist(model, root)
    return model


def _persist(model, root=None):
    p = model_path(root)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + ".tmp"
    with open(tmp, "w") as f:
        json.dump(model, f)
    os.replace(tmp, p)


def sane_model(new, old=None):
    """(ok, why) — the WRITE-IF-SANE gate for the automated re-mine rail
    (the gold bank's write-if-better law, cell form): a blind re-mine must
    never silently replace a working organ with a starved or collapsed one.
    Manual `mine` stays raw — a human is watching that path."""
    bins = new.get("bins") or {}
    for k in ("any/lead", "any/bass"):
        if len(bins.get(k) or []) < MIN_CELLS:
            return False, f"{k} under MIN_CELLS ({len(bins.get(k) or [])})"
    if old:
        for k in ("any/lead", "any/bass"):
            o = len((old.get("bins") or {}).get(k) or [])
            if o and len(bins[k]) < 0.5 * o:
                return False, f"{k} collapsed {o} -> {len(bins[k])}"
    if not generate(new, "", "A minor", 4, "lead", seed=1, n=1):
        return False, "smoke generation yielded nothing"
    return True, "sane"


def model_path(root=None):
    return os.path.join(root or DEF_ROOT, "telemetry", MODEL_NAME)


def is_stale(root=None, cooldown_s=3600, now=None):
    """True when the corpus outgrew the model AND the model is past its
    cooldown — the post-accept re-mine hook's pure gate. No model at all
    is always stale; a model younger than the cooldown never is (accept
    storms cost ONE re-mine)."""
    p = model_path(root)
    try:
        mt = os.path.getmtime(p)
    except OSError:
        return True
    now = time.time() if now is None else now
    if now - mt < cooldown_s:
        return False
    newest = 0.0
    for sub in ("songs", os.path.join("songs", "crate")):
        d = os.path.join(root or DEF_ROOT, sub)
        try:
            names = os.listdir(d)
        except OSError:
            continue
        for x in names:
            if x.endswith(".json") and not x.startswith(("_", ".")):
                try:
                    newest = max(newest,
                                 os.path.getmtime(os.path.join(d, x)))
                except OSError:
                    pass
    return newest > mt


def load_model(root=None):
    try:
        return json.load(open(model_path(root)))
    except Exception:
        return None


def _realize(cell, scale, allowed, ds, lo, hi, anchor):
    """Pitches for a cell transposed ds scale-steps, first pitch voice-led
    to the anchor, whole cell best-shifted into the tessitura, stray notes
    folded. Chroma survives only when the target key allows the pc —
    IN-KEY BY CONSTRUCTION whatever the source lane did."""
    recs = []
    for d, c in zip(cell["d"], cell["c"]):
        dd = d + ds
        rec = scale[dd % 7] + 12 * (dd // 7)
        if c and (rec + c) % 12 in allowed:
            rec += c
        recs.append(rec)
    r0 = recs[0] + 12 * cell["o"][0]
    target = anchor if anchor is not None else (lo + hi) // 2
    b = (target // 12) * 12
    first = min((b - 12 + r0, b + r0, b + 12 + r0),
                key=lambda p: abs(p - target))
    base = first - r0
    pitches = [base + rec + 12 * o for rec, o in zip(recs, cell["o"])]
    best_k, best_pen = 0, None
    for k in range(-3, 4):
        pen = sum(max(0, lo - (p + 12 * k)) + max(0, (p + 12 * k) - hi)
                  for p in pitches)
        if best_pen is None or pen < best_pen:
            best_k, best_pen = k, pen
        if pen == 0 and k == 0:
            break
    pitches = [p + 12 * best_k for p in pitches]
    for i, p in enumerate(pitches):
        while p < lo:
            p += 12
        while p > hi:
            p -= 12
        pitches[i] = p
    return pitches


def _first_pitch(cell, scale, lo, hi, anchor):
    r0 = scale[cell["d"][0] % 7] + cell["c"][0] + 12 * cell["o"][0]
    target = anchor if anchor is not None else (lo + hi) // 2
    b = (target // 12) * 12
    return min((b - 12 + r0, b + r0, b + 12 + r0),
               key=lambda p: abs(p - target))


def _compose(cells, scale, allowed, bars, role, rng):
    lo, hi = cp.TESSITURA.get(role, (48, 72))
    total = bars * 4.0
    pos, anchor, prev_src = 0.0, None, None
    notes, srcs = [], []
    while pos < total - 1e-6:
        remaining = total - pos
        idxs = (rng.sample(range(len(cells)), min(SAMPLE_K, len(cells)))
                if len(cells) > SAMPLE_K else list(range(len(cells))))
        pool = [i for i in idxs if cells[i]["src"] != prev_src]
        if not pool:
            pool = [i for i in range(len(cells))
                    if cells[i]["src"] != prev_src] or idxs
        best, best_score = None, None
        for i in pool:
            c = cells[i]
            fit = 0.0 if c["span"] <= remaining + 1e-6 \
                else 4.0 + (c["span"] - remaining)
            vl = 0.0 if anchor is None \
                else abs(_first_pitch(c, scale, lo, hi, anchor) - anchor) / 2.0
            score = vl + fit + rng.random() * 0.5
            if best_score is None or score < best_score:
                best, best_score = i, score
        cell = cells[best]
        ds = rng.choice((-2, -1, 1, 2)) if rng.random() < MUT_P else 0
        pitches = _realize(cell, scale, allowed, ds, lo, hi, anchor)
        placed = 0
        for on, ln, v, p in zip(cell["on"], cell["ln"], cell["v"], pitches):
            start = pos + on
            if start >= total - 1e-9:
                continue
            notes.append({"start": round(start, 4),
                          "len": round(min(ln, total - start), 4),
                          "pitch": int(p), "vel": v})
            placed += 1
        if placed:
            srcs.append((cell["src"], placed))
            anchor = pitches[len(cell["on"]) - 1] if placed == len(cell["on"]) \
                else pitches[placed - 1]
        prev_src = cell["src"]
        pos += cell["span"]
    return notes, srcs


def _court(notes, srcs, bars, bin_srcs):
    """Arrangement-level novelty court (see LAWS). True = the take serves."""
    if len(notes) < max(4, bars):
        return False
    for a, b in zip(srcs, srcs[1:]):
        if a[0] == b[0]:
            return False
    total = sum(n for _s, n in srcs) or 1
    cover = {}
    for s, n in srcs:
        cover[s] = cover.get(s, 0) + n
    if bin_srcs > 1:
        if max(cover.values()) > COVER_FRAC * total:
            return False
        if len(cover) < 2:
            return False
    return True


def generate(model, genre, key, bars, role, seed=1, n=4, root=None):
    """N candidate note windows: [{notes, role, seed, variant, srcs}].
    [] when the bin is dry or the key unparseable — honest, always."""
    if model is None:
        model = load_model(root)
    if model is None:
        return []
    scale, allowed = _pure_scale(key, genre)
    if scale is None:
        return []
    cells = model["bins"].get(f"{cp.family_of(genre)}/{role}")
    if not cells or len(cells) < MIN_CELLS:
        # a STARVED family bin (present but under MIN_CELLS) must not block
        # the fed family-blind fallback — 4 ambient/pad cells were truthy
        # enough to refuse two briefs the 180-cell any/pad bin could serve
        cells = model["bins"].get(f"any/{role}")
    if not cells or len(cells) < MIN_CELLS:
        return []
    bin_srcs = len({c["src"] for c in cells})
    out = []
    for ci in range(n):
        rng = random.Random((seed * 1000003 + ci * 8191) & 0x7fffffff)
        for _attempt in range(6):
            notes, srcs = _compose(cells, scale, allowed, bars, role, rng)
            if _court(notes, srcs, bars, bin_srcs):
                out.append({"role": role, "seed": seed, "variant": ci,
                            "srcs": srcs, "notes": notes})
                break
    return out


def main():
    ap = argparse.ArgumentParser(description="THE CELL PRIOR (BR-D B1 wave 2)")
    sub = ap.add_subparsers(dest="cmd")
    mi = sub.add_parser("mine", help="corpus -> telemetry/composer_cells.json")
    mi.add_argument("--cap", type=int, default=None)
    mi.add_argument("--if-stale", action="store_true",
                    help="re-mine only when the corpus outgrew the model "
                         "(1h cooldown) — the post-accept freshness hook")
    ge = sub.add_parser("generate")
    ge.add_argument("--genre", default="")
    ge.add_argument("--key", required=True)
    ge.add_argument("--bars", type=int, default=4)
    ge.add_argument("--role", default="lead", choices=("bass", "lead", "pad"))
    ge.add_argument("--seed", type=int, default=1)
    ge.add_argument("--n", type=int, default=4)
    a = ap.parse_args()
    if a.cmd == "mine":
        gated = getattr(a, "if_stale", False)
        if gated and not is_stale():
            print("cell model fresh — nothing to mine")
            return 0
        docs = cp.corpus_docs(cap=a.cap)
        if gated:
            old = load_model()
            m = mine(docs, persist=False)
            ok, why = sane_model(m, old)
            if not ok:
                print(f"REFUSED to replace the cell model: {why} — "
                      f"the working organ stands")
                return 1
            _persist(m)
        else:
            m = mine(docs)
        rep = {k: len(v) for k, v in sorted(m["bins"].items())}
        print(json.dumps({"docs": len(docs), "bins": rep}, indent=1))
        return 0
    if a.cmd == "generate":
        cands = generate(None, a.genre, a.key, a.bars, a.role,
                         seed=a.seed, n=a.n)
        print(json.dumps(cands, indent=1))
        return 0 if cands else 1
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
