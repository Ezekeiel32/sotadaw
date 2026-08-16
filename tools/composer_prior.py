#!/usr/bin/env python3
"""THE BRAIN BR-D — THE COMPOSER PRIOR (docs/SPEC_THE_BRAIN.md PART II B1).

A LEARNED note-window generator: order-2 Markov prior over musical EVENT
tokens, mined from the house corpus (songs/*.json + songs/crate — Chezy's
actual material; the D1 MIDI corpus mounts behind --midi in the quiet
window). Emits N candidate windows for AMAZING's SEARCH LAW to gate — the
prior only has to be un-mid; the gates carry correctness.

TOKEN = (slot, degree, dur_class, vel_class) per role stream:
  slot       16th-grid position inside the bar (0..15)
  degree     scale degree 0..6 (chromatic notes snap at TRAIN time — the
             prior is in-key BY CONSTRUCTION; generation maps degrees back
             through the requested key, so any key works from any corpus)
  dur_class  0 <=16th | 1 8th | 2 8th. | 3 quarter | 4 half+
  vel_class  0 soft | 1 mid | 2 hard
Octave motion is carried per-transition (mean octave delta), applied at
generation and clamped to the role's tessitura.

LAWS:
- DETERMINISM: same model + seed + ask = byte-identical candidates.
- IN-KEY BY CONSTRUCTION: emitted pitches come from degrees in the ASKED key.
- THE NOVELTY COURT (substantial-similarity form; measured 2026-07-16: 97%
  of the house corpus's 8-grams are single-source — unique loops — so a
  per-window ban yielded 0/16 and the organ starved): a candidate dies if
  ONE source covers a consecutive run >= RUN_HARD tokens (~4 bars replayed)
  OR attributes > COVER_FRAC of its windows (a re-skinned copy). Idiom-length
  cells are language; wholesale replay is theft. Walks epsilon-restart so
  ruts are escapable.
- HONEST DRYNESS: a (family, role) bin under MIN_EVENTS refuses to generate
  (returns []) — the deterministic expanders remain the floor, forever.
"""
import argparse
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEF_ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

MODEL_NAME = "composer_prior.json"
MIN_EVENTS = 200          # per (family, role) bin — under this, refuse
NGRAM = 8                 # novelty-court window unit
RUN_HARD = 16             # consecutive single-source tokens = wholesale replay
COVER_FRAC = 0.5          # one source claiming more = a re-skinned copy
EPS_RESTART = 0.08        # walk rut-escape probability per step
DUR_EDGES = (0.3, 0.6, 0.9, 1.6)   # beats -> class 0..4
VEL_EDGES = (0.45, 0.75)

ROLE_WORDS = {
    "bass": ("bass", "sub", "808"),
    "lead": ("lead", "melody", "arp", "pluck", "hook", "stab", "bell", "keys",
             "piano", "gtr", "guitar", "vox", "vocal"),
    "pad": ("pad", "chord", "string", "organ", "drone"),
}
_WITNESS_SUFFIX = ("_sketch", "_identity", "_ref", "_witness")
_WITNESS_PREFIX = ("spectral_",)

FAMILY_WORDS = {
    "house": ("house", "garage", "techno", "trance", "edm", "dance", "club",
              "amapiano", "dub_techno", "psy", "dnb", "jungle", "step"),
    "rap": ("rap", "trap", "drill", "boombap", "hiphop", "hip_hop", "memphis",
            "grime", "phonk"),
    "band": ("rock", "indie", "funk", "blues", "jazz", "soul", "pop", "punk",
             "metal", "country", "folk"),
    "ambient": ("ambient", "cinematic", "drone", "downtempo", "chill", "lofi",
                "psybient", "idm"),
}


def family_of(genre):
    g = str(genre or "").lower()
    for fam, words in FAMILY_WORDS.items():
        if any(w in g for w in words):
            return fam
    return "any"


def role_of(track_name):
    nm = str(track_name or "").lower()
    if nm.endswith(_WITNESS_SUFFIX) or nm.startswith(_WITNESS_PREFIX):
        return None
    for role, words in ROLE_WORDS.items():
        if any(w in nm for w in words):
            return role
    return None


def _dur_class(beats):
    for i, e in enumerate(DUR_EDGES):
        if beats <= e:
            return i
    return len(DUR_EDGES)


def _vel_class(v):
    for i, e in enumerate(VEL_EDGES):
        if v <= e:
            return i
    return len(VEL_EDGES)


DUR_BEATS = (0.25, 0.5, 0.75, 1.0, 2.0)
VEL_MEANS = (0.35, 0.62, 0.88)


def tokenize(doc, key=None):
    """[(role, [token...]), ...] token=(slot, degree, dur, vel); octave deltas
    ride a parallel list. Chromatic pitches snap to the nearest degree HERE —
    the prior speaks scale degrees only."""
    try:
        import theory
        k = theory.parse_key(str(key or doc.get("key") or ""))
        if not k:
            return []
        # the PURE scale (7 degrees) — allowed_pcs carries genre-allowance
        # extras (8+ pcs) and would leak degree indices past 6
        scale = sorted(k["scale_pcs"])
        if len(scale) < 5:
            return []
    except Exception:
        return []
    out = []
    for tr in doc.get("tracks") or []:
        role = role_of(tr.get("name"))
        if role is None:
            continue
        notes = sorted((n for n in tr.get("notes") or []
                        if isinstance(n.get("pitch"), (int, float))),
                       key=lambda n: float(n.get("start", 0.0)))
        if len(notes) < 8:
            continue
        toks, octs, prev_pitch = [], [], None
        for n in notes:
            pitch = int(n["pitch"])
            pc = pitch % 12
            deg = min(range(len(scale)),
                      key=lambda i: min((scale[i] - pc) % 12, (pc - scale[i]) % 12))
            start = float(n.get("start", 0.0))
            slot = int(round((start % 4.0) * 4.0)) % 16
            toks.append((slot, deg,
                         _dur_class(float(n.get("len", 0.5))),
                         _vel_class(float(n.get("vel", 0.8)))))
            # LEAP TRUTH: od = octaves between the MINIMAL-MOTION realization
            # of this pc (nearest to the previous pitch) and the ACTUAL pitch
            # — the exact quantity generation adds back on top of minimal
            # motion (pitch//12 deltas double-counted steps like B3->C4 and
            # a mean+coin-flip erased the corpus's 19% octave-jump tail)
            if prev_pitch is None:
                octs.append(0)
            else:
                base = (prev_pitch // 12) * 12 + (scale[deg % len(scale)])
                near = min((base - 12, base, base + 12),
                           key=lambda p: abs(p - prev_pitch))
                octs.append(max(-2, min(2, int(round((pitch - near) / 12.0)))))
            prev_pitch = pitch
        out.append((role, toks, octs))
    return out


def _tkey(t):
    return f"{t[0]}.{t[1]}.{t[2]}.{t[3]}"


def train(docs_with_meta, root=None, persist=True):
    """docs_with_meta = [(doc, genre, doc_id)]. Builds per-(family, role)
    order-2 transition counts + the novelty 8-gram index. Returns the model."""
    model = {"bins": {}, "ngrams": {}, "version": 1}
    for doc, genre, doc_id in docs_with_meta:
        fam = family_of(genre)
        for role, toks, octs in tokenize(doc):
            for f in (fam, "any"):
                b = model["bins"].setdefault(f"{f}/{role}", {
                    "events": 0, "trans": {}, "starts": {}, "oct": {}})
                b["events"] += len(toks)
                for i in range(len(toks)):
                    tk = _tkey(toks[i])
                    if i == 1:
                        # starts are PAIRS — the walk's first context must be
                        # a real corpus context or the chain never engages
                        pair = _tkey(toks[0]) + "|" + tk
                        b["starts"][pair] = b["starts"].get(pair, 0) + 1
                    if i < 2:
                        continue
                    ctx = _tkey(toks[i - 2]) + "|" + _tkey(toks[i - 1])
                    d = b["trans"].setdefault(ctx, {})
                    d[tk] = d.get(tk, 0) + 1
                    o = b["oct"].setdefault(ctx, {})
                    ok = str(octs[i])
                    o[ok] = o.get(ok, 0) + 1
            # novelty index: rides the raw stream, family-blind
            seq = [_tkey(t) for t in toks]
            for i in range(len(seq) - NGRAM + 1):
                h = "|".join(seq[i:i + NGRAM])
                s = model["ngrams"].setdefault(h, [])
                if doc_id not in s and len(s) < 4:
                    s.append(doc_id)
    if persist:
        p = model_path(root)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        tmp = p + ".tmp"
        with open(tmp, "w") as f:
            json.dump(model, f)
        os.replace(tmp, p)
    return model


def model_path(root=None):
    return os.path.join(root or DEF_ROOT, "telemetry", MODEL_NAME)


def load_model(root=None):
    try:
        return json.load(open(model_path(root)))
    except Exception:
        return None


def _parse_tok(s):
    a = s.split(".")
    return (int(a[0]), int(a[1]), int(a[2]), int(a[3]))


TESSITURA = {"bass": (28, 48), "lead": (55, 84), "pad": (48, 72)}


def _plagiarized(seq_keys, ngrams, ignore=()):
    """Substantial similarity: True on a consecutive single-source run of
    >= RUN_HARD tokens, or one source covering > COVER_FRAC of windows.
    `ignore` = doc_ids that never count as foreign (THE SELF-MATCH TRAP:
    a mined song judged against an index containing itself is not a thief
    of its own history — the release gate passes the take's own ids)."""
    n_win = len(seq_keys) - NGRAM + 1
    if n_win <= 0:
        return False
    run_limit = RUN_HARD - NGRAM + 1          # windows spanning RUN_HARD tokens
    cover, run, prev = {}, {}, None
    for i in range(n_win):
        h = "|".join(seq_keys[i:i + NGRAM])
        srcs = ngrams.get(h)
        d = (srcs[0] if (srcs is not None and len(srcs) == 1
                         and srcs[0] not in ignore) else None)
        if d is not None:
            cover[d] = cover.get(d, 0) + 1
            run[d] = run.get(d, 0) + 1 if prev == d else 1
            if run[d] >= run_limit:
                return True
        prev = d
    return any(c > COVER_FRAC * n_win for c in cover.values())


def generate(model, genre, key, bars, role, seed=1, n=4, root=None):
    """N candidate note windows: [{notes: [...], role, seed}]. [] when the
    bin is dry or the key unparseable — honest, the expanders stand."""
    if model is None:
        model = load_model(root)
    if model is None:
        return []
    try:
        import theory
        k = theory.parse_key(str(key or ""))
        if not k:
            return []
        scale = sorted(k["scale_pcs"])     # pure scale mirror of tokenize
    except Exception:
        return []
    b = (model["bins"].get(f"{family_of(genre)}/{role}")
         or model["bins"].get(f"any/{role}"))
    if not b or b["events"] < MIN_EVENTS or not b["starts"]:
        return []
    lo, hi = TESSITURA.get(role, (48, 72))
    starts = sorted(b["starts"].items())
    total = sum(c for _, c in starts)

    def _weighted(items, tot, rng):
        r = rng.random() * tot
        acc = 0.0
        for tk, c in items:
            acc += c
            if r <= acc:
                return tk
        return items[-1][0]

    out = []
    for ci in range(n):
        rng = random.Random((seed * 1000003 + ci * 8191) & 0x7fffffff)
        for _attempt in range(6):          # novelty-court resample loop
            # 1) walk in TOKEN space (the stream is what the court judges)
            stream = _weighted(starts, total, rng).split("|")
            oct_moves = [0, 0]
            want = bars * 32
            while len(stream) < want:
                ctx = stream[-2] + "|" + stream[-1]
                d = b["trans"].get(ctx)
                if d and rng.random() < EPS_RESTART:
                    d = None                   # rut escape: fresh corpus pair
                if d:
                    nxt = _weighted(sorted(d.items()), sum(d.values()), rng)
                    om = b["oct"].get(ctx)
                    od = 0
                    if om:                     # learned leap categorical
                        od = int(_weighted(sorted(om.items()),
                                           sum(om.values()), rng))
                    stream.append(nxt)
                    oct_moves.append(od)
                else:                       # unseen context: fresh corpus pair
                    pair = _weighted(starts, total, rng).split("|")
                    stream.extend(pair)
                    oct_moves.extend([0, 0])
            # 2) emit notes from the stream — MINIMAL MOTION realization
            # (the degree-wrap bug: corpus step B->C is deg 6->0 + oct +1;
            # realizing degrees in a held octave turned steps into -11 leaps
            # and pushed the prior's interval histogram FURTHER from the
            # corpus than uniform random, measured 1.15 vs 0.74)
            beat, bar_len = 0.0, float(bars) * 4.0
            notes = []
            prev_pitch, prev_slot, stacked = None, None, 0
            for tk, od in zip(stream, oct_moves):
                slot, deg, dc, vc = _parse_tok(tk)
                # SLOT-DELTA placement: the groove lives in inter-onset
                # deltas, not absolute slots — a Markov walk stitches slots
                # non-monotonically and absolute placement burned a whole bar
                # per backwards hop (measured: 10 notes emitted from a
                # 128-token stream, every leap token unreached)
                if prev_slot is None:
                    start = slot * 0.25
                else:
                    ioi = ((slot - prev_slot) % 16) * 0.25
                    if ioi == 0.0:
                        stacked += 1
                        if stacked >= 2:       # chord cap: never a pillar
                            ioi, stacked = 0.25, 0
                    else:
                        stacked = 0
                    start = beat + ioi
                prev_slot = slot
                if start >= bar_len:
                    break
                pc = scale[deg % len(scale)]
                if prev_pitch is None:
                    pitch = ((lo + hi) // 2 // 12) * 12 + pc
                    while pitch < lo:
                        pitch += 12
                    while pitch > hi:
                        pitch -= 12
                else:
                    base = (prev_pitch // 12) * 12 + pc
                    near = min((base - 12, base, base + 12),
                               key=lambda p: abs(p - prev_pitch))
                    # LEAP DIRECTION FOLD: an octave move that would leave the
                    # tessitura flips direction instead of folding back onto
                    # its own start (the fold was erasing every leap into an
                    # interval-0 — measured 0.29 repeat mass vs corpus 0.09)
                    pitch = near + 12 * od
                    if not (lo <= pitch <= hi):
                        pitch = near - 12 * od
                    if not (lo <= pitch <= hi):
                        pitch = near
                    while pitch < lo:
                        pitch += 12
                    while pitch > hi:
                        pitch -= 12
                prev_pitch = pitch
                dur = DUR_BEATS[min(dc, len(DUR_BEATS) - 1)]
                notes.append({"start": round(start, 4),
                              "len": round(min(dur, bar_len - start), 4),
                              "pitch": int(pitch),
                              "vel": round(VEL_MEANS[min(vc, 2)], 3)})
                beat = start
            if len(notes) >= max(4, bars) and not _plagiarized(stream,
                                                               model.get("ngrams") or {}):
                out.append({"role": role, "seed": seed, "variant": ci,
                            "notes": notes})
                break
    return out


# ---------------------------------------------------------------- corpus CLI
def corpus_docs(root=None, include_midi=False, cap=None):
    """[(doc, genre, doc_id)] from songs/ + crate. _-prefixed and witness
    songs excluded. MIDI corpus lane rides --midi (quiet window)."""
    root = root or DEF_ROOT
    out = []
    for sub in ("songs", os.path.join("songs", "crate")):
        d = os.path.join(root, sub)
        try:
            names = sorted(os.listdir(d))
        except OSError:
            continue
        for x in names:
            if not x.endswith(".json") or x.startswith("_") or x.startswith("."):
                continue
            p = os.path.join(d, x)
            if not os.path.isfile(p):
                continue
            try:
                doc = json.load(open(p))
            except Exception:
                continue
            if not isinstance(doc, dict) or not doc.get("tracks"):
                continue
            genre = str(doc.get("genre") or doc.get("style") or x)
            out.append((doc, genre, f"{sub}/{x}"))
            if cap and len(out) >= cap:
                return out
    return out


def main():
    ap = argparse.ArgumentParser(description="THE COMPOSER PRIOR (BR-D B1)")
    sub = ap.add_subparsers(dest="cmd")
    tr = sub.add_parser("train", help="mine the house corpus -> telemetry/composer_prior.json")
    tr.add_argument("--cap", type=int, default=None)
    ge = sub.add_parser("generate")
    ge.add_argument("--genre", default="")
    ge.add_argument("--key", required=True)
    ge.add_argument("--bars", type=int, default=4)
    ge.add_argument("--role", default="lead", choices=("bass", "lead", "pad"))
    ge.add_argument("--seed", type=int, default=1)
    ge.add_argument("--n", type=int, default=4)
    a = ap.parse_args()
    if a.cmd == "train":
        docs = corpus_docs(cap=a.cap)
        m = train(docs)
        rep = {k: v["events"] for k, v in m["bins"].items()}
        print(json.dumps({"docs": len(docs), "bins": rep,
                          "ngrams": len(m["ngrams"])}, indent=1))
        return 0
    if a.cmd == "generate":
        cands = generate(None, a.genre, a.key, a.bars, a.role, seed=a.seed, n=a.n)
        print(json.dumps(cands, indent=1))
        return 0 if cands else 1
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
