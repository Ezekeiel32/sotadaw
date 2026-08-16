#!/usr/bin/env python3
"""AMAZING PART III — THE RELEASE GATE, assembled (v1 staging, honest).

docs/SPEC_AMAZING_EVERY_TIME.md PART III: a take may surface ONLY if the
five gates pass. v1 binds the four gates whose machinery exists today and
NAMES the fifth — every stage/skip rides the verdict's "gaps", because the
SEARCH LAW's honesty clause is absolute: the system may say "not my best
bar", it may never quietly ship mid.

  G1 CENSUS     music courts (hard = any court verdict ok:false) +
                worldclass floor_verdict hard traps
  G2 REFERENCE  the genre's gold envelope: mixtarget LUFS window, clipped=0,
                PSR floor, band ORDER. Measured-vector closeness is a
                READOUT row, not a hard gate — one exemplar is a point,
                not a cloud (STAGED until the cloud accumulates)
  G3 TASTE      CLAP -> taste_head (head, else cold floor). no-data/clap-
                unavailable = SKIP, named. A fed head/floor saying reject
                BLOCKS.
  G4 NOVELTY    corpus n-gram substantial-similarity court on the take's
                own note streams, SELF-MATCH excluded (a song may resemble
                its own history; it may never replay ANOTHER source).
                Self-clone vs the gold exemplar: NAMED GAP (gold dna
                excerpts sit under the 8-gram floor).
  G5 BLIND      not-run (judge tokens / human panel) — always NAMED.

pass = G1 & G2 & G4 pass AND G3 not an explicit reject. A take that cannot
render cannot surface (hard).
"""
import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import kick_windows as kw

PY = os.path.join(ROOT, ".venv", "bin", "python")
M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")
LUFS_GRACE = (1.0, 0.5)      # low/high grace on the mixtarget window
DBTP_HARD = -0.8             # the release wall states -1.2; past this = unwalled
PSR_GRACE = 0.5
TASTE_FLOOR = 0.5


def gold_for(genre, root=None):
    root = root or ROOT
    n = kw.norm_genre(genre)
    for cand in (n, kw.ALIAS.get(n)):
        if not cand:
            continue
        p = os.path.join(root, "library", "gold", f"{cand}.json")
        if os.path.exists(p):
            try:
                return json.load(open(p)), cand
            except Exception:
                return None, None
    return None, None


def band_rank_ok(order_str, bands):
    """mixtarget 'low>lowmid>mid' vs analyze2 band_energy_pct keys
    ('low_20_120', ...). None = unknowable (missing bands), never a guess."""
    if not order_str or not isinstance(bands, dict) or not bands:
        return None
    by_base = {str(k).split("_")[0]: v for k, v in bands.items()}
    seq = [s.strip() for s in str(order_str).split(">") if s.strip()]
    vals = [by_base.get(s) for s in seq]
    if len(vals) < 2 or any(not isinstance(v, (int, float)) for v in vals):
        return None
    return all(a >= b for a, b in zip(vals, vals[1:]))


def g1_census(song, genre, analysis):
    """Courts + worldclass floor. Hard = any court ok:false or floor hard trap."""
    hard, adv = [], 0
    try:
        import music_court as mc
        courts = mc.run_courts(song, genre, heal=False) or {}
    except Exception as e:
        courts = {}
        hard.append(f"courts unrunnable: {type(e).__name__}")
    for name in sorted(courts):
        v = courts[name]
        if not isinstance(v, dict):
            continue
        if v.get("ok") is False:
            hard.append(f"{name} court: not ok")
        adv += len(v.get("flags") or v.get("advisories") or [])
    try:
        import worldclass as wc
        fv = wc.floor_verdict(song, analysis)
    except Exception as e:
        fv = {"hard": [], "soft": []}
        hard.append(f"floor unrunnable: {type(e).__name__}")
    for h in fv.get("hard") or []:
        hard.append(f"floor:{h.get('code')}")
    return {"pass": not hard, "hard": hard, "advisories": adv,
            "floor_soft": [s.get("code") for s in fv.get("soft") or []]}


def g2_reference(analysis, gold, genre):
    """The genre's measured envelope. Hard on window breaches; measured
    closeness is a readout row; unknowables become named gaps."""
    hard, gaps, readout = [], [], {}
    a = analysis if isinstance(analysis, dict) else {}
    mt = (gold or {}).get("mixtarget") or {}
    lufs = a.get("lufs_integrated")
    if isinstance(mt.get("lufs_lo"), (int, float)) and \
            isinstance(lufs, (int, float)):
        lo, hi = mt["lufs_lo"] - LUFS_GRACE[0], mt["lufs_hi"] + LUFS_GRACE[1]
        readout["lufs"] = [round(lufs, 2), mt["lufs_lo"], mt["lufs_hi"]]
        if not lo <= lufs <= hi:
            hard.append(f"LUFS {lufs:.1f} outside the genre window "
                        f"[{mt['lufs_lo']}, {mt['lufs_hi']}]")
    elif not mt:
        gaps.append(f"no gold exemplar for {genre!r} — LUFS window unjudged")
    clipped = a.get("clipped_samples")
    if isinstance(clipped, (int, float)) and clipped > 0:
        hard.append(f"clipped_samples {int(clipped)} (window is 0)")
    dbtp = a.get("true_peak_dbtp")
    if isinstance(dbtp, (int, float)) and dbtp > DBTP_HARD:
        hard.append(f"true peak {dbtp:.2f} dBTP past the release wall")
    psr = a.get("psr")
    floor = mt.get("psr_floor")
    if not isinstance(floor, (int, float)):
        try:
            import dynamics_ears as de
            floor = de.psr_floor_for(genre)
        except Exception:
            floor = None
    if isinstance(floor, (int, float)) and isinstance(psr, (int, float)):
        readout["psr"] = [round(psr, 2), floor]
        if psr < floor - PSR_GRACE:
            hard.append(f"PSR {psr:.1f} under the genre floor {floor}")
    order = band_rank_ok(mt.get("band_order"), a.get("band_energy_pct"))
    if order is False:
        hard.append(f"band order breaks the genre's "
                    f"{mt.get('band_order')!r} law")
    elif order is None and mt.get("band_order"):
        gaps.append("band order unknowable (no band metrics)")
    meas = (gold or {}).get("measured") or {}
    if isinstance(meas.get("lufs"), (int, float)) and \
            isinstance(lufs, (int, float)):
        readout["measured_lufs_delta"] = round(lufs - meas["lufs"], 2)
    mb, ab = meas.get("bands"), a.get("band_energy_pct")
    if isinstance(mb, dict) and isinstance(ab, dict):
        shared = [k for k in mb if isinstance(ab.get(k), (int, float))
                  and isinstance(mb[k], (int, float))]
        if shared:
            readout["measured_bands_l1"] = round(
                sum(abs(ab[k] - mb[k]) for k in shared), 1)
    return {"pass": not hard, "hard": hard, "gaps": gaps, "readout": readout}


def g3_taste(wav, root=None, embed=None, score=None):
    """(state, score, why): state pass|fail|skip. Skip is honest, never a
    verdict — only a FED head/floor may block."""
    if not wav or not os.path.exists(wav):
        return {"state": "skip", "score": None, "why": "no rendered audio"}
    try:
        if embed is None:
            import clap_embed as ce
            if not ce.available():
                return {"state": "skip", "score": None,
                        "why": "clap unavailable — taste unjudged"}
            embed = lambda p: ce.embed_audio([p])[0]  # noqa: E731
        emb = embed(wav)
        if score is None:
            import taste_head as th
            score = th.score_emb
        p, src = score(emb, root=root)
    except Exception as e:
        return {"state": "skip", "score": None,
                "why": f"taste rail failed: {type(e).__name__}"}
    if p is None:
        return {"state": "skip", "score": None,
                "why": f"taste bank dry ({src}) — head refused, floors stand"}
    return {"state": "pass" if p >= TASTE_FLOOR else "fail",
            "score": round(float(p), 3), "src": src,
            "why": f"{src} score {p:.3f} vs floor {TASTE_FLOOR}"}


def g4_novelty(song, self_ids=(), root=None, model=None):
    """Corpus substantial-similarity court over the take's note streams."""
    import composer_prior as cp
    model = model or cp.load_model(root)
    if not model or not model.get("ngrams"):
        return {"state": "skip", "why": "no corpus index — novelty unjudged"}
    gaps = ["self-clone vs gold exemplar unjudged (dna excerpts under the "
            "8-gram floor)"]
    lanes = cp.tokenize(song)
    has_notes = any((t.get("notes") or []) for t in song.get("tracks") or [])
    if not lanes and has_notes:
        gaps.append("note streams untokenizable (keyless?) — novelty "
                    "unjudged on them")
    stolen = []
    for role, toks, _octs in lanes:
        seq = [cp._tkey(t) for t in toks]
        if len(seq) >= cp.NGRAM and cp._plagiarized(
                seq, model["ngrams"], ignore=frozenset(self_ids)):
            stolen.append(role)
    if stolen:
        return {"state": "fail", "stolen_roles": stolen, "gaps": gaps,
                "why": f"substantial similarity to a foreign source on "
                       f"{','.join(stolen)}"}
    return {"state": "pass", "gaps": gaps, "why": "no foreign replay"}


def assemble(census, reference, taste, novelty, song_name="", genre="",
             gold_name=None, extra_gaps=()):
    """Pure verdict core: the pass law + the honest-gap ledger."""
    gaps = list(extra_gaps)
    gaps += reference.get("gaps") or []
    gaps += novelty.get("gaps") or []
    if taste.get("state") == "skip":
        gaps.append(f"G3 TASTE skipped: {taste.get('why')}")
    if novelty.get("state") == "skip":
        gaps.append(f"G4 NOVELTY skipped: {novelty.get('why')}")
    gaps.append("G5 BLIND not-run (judge/panel machinery is staged)")
    ok = (bool(census.get("pass")) and bool(reference.get("pass"))
          and taste.get("state") != "fail" and novelty.get("state") != "fail")
    return {"song": song_name, "genre": genre, "gold": gold_name,
            "gates": {"census": census, "reference": reference,
                      "taste": taste, "novelty": novelty,
                      "blind": {"state": "not-run"}},
            "pass": ok, "gaps": gaps}


def gate_chip(verdict):
    """Compact chip for events/decks: the five gates in one row of fields."""
    g = (verdict or {}).get("gates") or {}
    hard = (((g.get("census") or {}).get("hard")) or []) + \
           (((g.get("reference") or {}).get("hard")) or [])
    return {"pass": bool((verdict or {}).get("pass")),
            "hard": len(hard), "hard_top": [str(h)[:80] for h in hard[:3]],
            "gaps": len((verdict or {}).get("gaps") or []),
            "taste": (g.get("taste") or {}).get("score"),
            "novelty": (g.get("novelty") or {}).get("state") or "skip"}


def _self_ids(song_path):
    """THE SELF-MATCH PARDON must cover the PROP TWIN's base: a _prop_ take
    judged against an index holding its own base song is not a thief of its
    own material."""
    base = os.path.basename(song_path)
    stem = base[len("_prop_"):] if base.startswith("_prop_") else base
    return {f"songs/{base}", f"songs/crate/{base}",
            f"songs/{stem}", f"songs/crate/{stem}"}


def _render(song_path, wav):
    r = subprocess.run([PY, os.path.join(HERE, "render_cache.py"), "render",
                        song_path, wav], capture_output=True, text=True,
                       timeout=600)
    if r.returncode == 0 and os.path.exists(wav):
        return True
    r = subprocess.run([M1, "render", song_path, wav], capture_output=True,
                       text=True, timeout=600)
    return r.returncode == 0 and os.path.exists(wav)


def gate_take(song_path, wav=None, genre=None, root=None, render=True):
    root = root or ROOT
    try:
        song = json.load(open(song_path))
    except Exception as e:
        return {"pass": False, "error": f"song unreadable: {e}"}
    g = str(genre or song.get("genre") or song.get("style") or "")
    gold, gold_name = gold_for(g, root)
    extra = []
    tmpwav = None
    if wav is None and render:
        tmpwav = song_path[:-5] + "_gate.wav" if song_path.endswith(".json") \
            else song_path + "_gate.wav"
        if _render(song_path, tmpwav):
            wav = tmpwav
        else:
            extra.append("RENDER FAILED — a take that cannot render cannot "
                         "surface")
    analysis = {}
    if wav and os.path.exists(wav):
        try:
            import analyze2
            analysis = analyze2.analyze(wav)
        except Exception as e:
            extra.append(f"ears failed on the render: {type(e).__name__}")
    base = os.path.basename(song_path)
    self_ids = _self_ids(song_path)
    v = assemble(
        g1_census(song, g, analysis or None),
        g2_reference(analysis, gold, g),
        g3_taste(wav, root=root),
        g4_novelty(song, self_ids=self_ids, root=root),
        song_name=base, genre=g, gold_name=gold_name, extra_gaps=extra)
    if extra:
        v["pass"] = False
    if tmpwav and os.path.exists(tmpwav):
        try:
            os.remove(tmpwav)
        except OSError:
            pass
    return v


def main():
    ap = argparse.ArgumentParser(description="THE RELEASE GATE (AMAZING PIII)")
    ap.add_argument("song")
    ap.add_argument("--wav", default=None)
    ap.add_argument("--genre", default=None)
    ap.add_argument("--no-render", action="store_true")
    a = ap.parse_args()
    v = gate_take(a.song, wav=a.wav, genre=a.genre, render=not a.no_render)
    print(json.dumps(v, indent=1))
    if v.get("error"):
        return 2
    return 0 if v["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
