#!/usr/bin/env python3
"""THE BRAIN BR-D — THE POCKET NET (docs/SPEC_THE_BRAIN.md PART II B4).

Feel, learned from the corpus: per (family, role, 16th-slot) microtiming and
velocity RESIDUALS — what remains after the grid — mined from docs whose
lanes actually breathe (off-grid onsets / velocity spread). Sampling feeds
humanize under the standing ceiling law (40-60% of natural SD, pocket_dna).

LAWS:
- RESIDUALS ONLY: the net learns what the rules can't say; swing and the
  KTH/pocket-DNA profiles remain the floor. A dry bin (< MIN_SAMPLES)
  returns None — the caller falls back to pocket_dna, forever.
- CEILING LAW: sampled offsets are clamped to CEIL_FRAC * NATURAL_SD_MS of
  the role (pocket_dna table) — learned feel may never out-drift a human.
- DETERMINISM: sample(rng) — the caller owns the seed.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEF_ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

MODEL_NAME = "pocket_net.json"
MIN_SAMPLES = 24
CEIL_FRAC = 0.6

DRUM_ROLES = {
    "kick": ("kick", "bd"),
    "snare": ("snare", "clap", "rim", "sd"),
    "hat": ("hat", "hh", "shaker", "tamb", "ride", "cym"),
    "perc": ("perc", "conga", "bongo", "tom", "cow", "block"),
}
_WITNESS_SUFFIX = ("_sketch", "_identity", "_ref", "_witness")
_WITNESS_PREFIX = ("spectral_",)


def drum_role(track_name):
    nm = str(track_name or "").lower()
    if nm.endswith(_WITNESS_SUFFIX) or nm.startswith(_WITNESS_PREFIX):
        return None
    for role, words in DRUM_ROLES.items():
        if any(w in nm for w in words):
            return role
    return None


def _family_of(genre):
    import composer_prior
    return composer_prior.family_of(genre)


def mine(docs_with_meta):
    """[(doc, genre, id)] -> model {bins: {"fam/role/slot": {n, off_ms:[mean, sd],
    vel:[mean, sd]}}}. Offsets measured vs the nearest 16th at the doc's bpm;
    a lane with NO off-grid life (all |off| < 1ms) contributes velocity only."""
    acc = {}
    for doc, genre, _id in docs_with_meta:
        try:
            bpm = float(doc.get("bpm") or 0)
        except (TypeError, ValueError):
            bpm = 0.0
        if bpm <= 0:
            continue
        ms_per_beat = 60000.0 / bpm
        fam = _family_of(genre)
        for tr in doc.get("tracks") or []:
            role = drum_role(tr.get("name"))
            if role is None:
                continue
            notes = [n for n in tr.get("notes") or []
                     if isinstance(n.get("start"), (int, float))]
            if len(notes) < 8:
                continue
            offs = []
            for n in notes:
                s = float(n["start"])
                grid = round(s * 4.0) / 4.0
                offs.append((s - grid) * ms_per_beat)
            alive = sum(1 for o in offs if abs(o) >= 1.0) >= max(4, len(offs) // 8)
            for n, off in zip(notes, offs):
                slot = int(round((float(n["start"]) % 4.0) * 4.0)) % 16
                for f in (fam, "any"):
                    key = f"{f}/{role}/{slot}"
                    b = acc.setdefault(key, {"off": [], "vel": []})
                    if alive:
                        b["off"].append(off)
                    v = n.get("vel")
                    if isinstance(v, (int, float)):
                        b["vel"].append(float(v))
    model = {"bins": {}, "version": 1}
    for key, b in acc.items():
        row = {"n": max(len(b["off"]), len(b["vel"]))}
        for name in ("off", "vel"):
            xs = b[name]
            if len(xs) >= MIN_SAMPLES:
                m = sum(xs) / len(xs)
                sd = math.sqrt(sum((x - m) ** 2 for x in xs) / len(xs))
                row[name + ("_ms" if name == "off" else "")] = [round(m, 3),
                                                                round(sd, 3)]
        if len(row) > 1:
            model["bins"][key] = row
    return model


def model_path(root=None):
    return os.path.join(root or DEF_ROOT, "telemetry", MODEL_NAME)


def save(model, root=None):
    p = model_path(root)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + ".tmp"
    with open(tmp, "w") as f:
        json.dump(model, f)
    os.replace(tmp, p)


def load_model(root=None):
    try:
        return json.load(open(model_path(root)))
    except Exception:
        return None


def _ceiling_ms(genre):
    """pocket_dna's NATURAL_SD_MS is keyed by GENRE words (jazz/swing/funk/
    default) — the ceiling follows the genre's natural human spread."""
    try:
        import pocket_dna
        g = str(genre or "").lower()
        sd = next((v for k, v in pocket_dna.NATURAL_SD_MS.items() if k in g),
                  pocket_dna.NATURAL_SD_MS.get("default", 20.0))
        return CEIL_FRAC * float(sd)
    except Exception:
        return CEIL_FRAC * 20.0


def sample(model, genre, role, slot, rng):
    """(offset_ms, vel_scale) or None when the bin is dry — the pocket_dna
    profiles stand. vel_scale multiplies the written velocity (mean-relative,
    clamped 0.7..1.3)."""
    if model is None:
        return None
    fam = _family_of(genre)
    b = (model.get("bins") or {}).get(f"{fam}/{role}/{int(slot) % 16}") \
        or (model.get("bins") or {}).get(f"any/{role}/{int(slot) % 16}")
    if not b:
        return None
    off = 0.0
    got = False
    if "off_ms" in b:
        m, sd = b["off_ms"]
        cap = _ceiling_ms(genre)
        off = max(-cap, min(cap, rng.gauss(m, sd * CEIL_FRAC)))
        got = True
    vs = 1.0
    if "vel" in b:
        m, sd = b["vel"]
        if m > 1e-6:
            vs = max(0.7, min(1.3, rng.gauss(m, sd * CEIL_FRAC) / m))
            got = True
    return (round(off, 3), round(vs, 4)) if got else None


if __name__ == "__main__":
    import composer_prior
    docs = composer_prior.corpus_docs()
    m = mine(docs)
    save(m)
    fams = {}
    for k in m["bins"]:
        fams[k.split("/")[0]] = fams.get(k.split("/")[0], 0) + 1
    print(json.dumps({"docs": len(docs), "bins": len(m["bins"]),
                      "by_family": fams}, indent=1))
