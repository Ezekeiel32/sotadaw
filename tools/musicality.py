#!/usr/bin/env python3
"""MUSICALITY — the composition ruler (W14). CLAP hears texture; Chezy hears
MUSIC. This scores the INTENT layer symbolically, free, deterministic:

  strong_ct    chord tones own the strong beats (share, quarter grid)
  nct_resolve  non-chord tones RESOLVE (next note <=2 semitones AND a chord tone)
  rhythm_rep   the hook repeats its rhythm (mean Jaccard of each bar's 16th
               onset set vs bar 0 — a hook is recognisable, a walk is not)
  climax_count occurrences of the highest pitch (a melody has ONE peak)
  pc_economy   distinct pitch classes (earworms are economical)
  cadence_ct   share of 4-bar groups whose last lead note lands on a chord
               tone of its bar or the next (phrases ARRIVE somewhere)

  musicality.py <song.json>          score a song's lead lane -> MUSIC_JSON
  musicality.py --selftest           floors on the hook engine + a no-crash
                                     sweep across every lead-bearing genre

ONE-KERNEL LAW: key parsing + chord degrees come from loop_gen (key_scale,
EXT_SEVENTH) — never re-implement (the drifted-mirror lesson)."""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import loop_gen as LG

TOL = 0.08                    # humanize drift tolerance on the quarter grid


def _chord_pcs(cdeg, iv, root, seventh):
    degs = [cdeg, cdeg + 2, cdeg + 4] + ([cdeg + 6] if seventh else [])
    return {(root + iv[(d - 1) % 7]) % 12 for d in degs}


def score(song, genre=None):
    genre = genre or (song.get("_loop") or {}).get("genre") or ""
    dna, err = LG.genre_dna(genre)
    if dna is None:
        return {"error": err}
    grid = dna.get("grid") or {}
    prog = ((song.get("_loop") or {}).get("chords")   # W87: the TAKE's field
            or grid.get("chords") or [[0, 1]])
    span = max(b for b, _ in prog) + 1
    root, iv = LG.key_scale(song.get("key") or dna.get("key") or "A minor")
    seventh = genre.lower() in LG.EXT_SEVENTH

    # W32 THE JOURNEY-AWARE FIELD: arranged songs carry sections[]; the ruler
    # scores against the SAME shifted field arrange composed into (chorus +2,
    # bridge/break -2, turnaround -1 — LG.journey_bar_shifts, the one kernel).
    # Birth loops have no sections -> shifts all 0 (unchanged behavior).
    secs = song.get("sections") or []

    def base_deg(bar):
        d = 1
        for b0, dd in sorted(prog):
            if bar % span >= b0:
                d = dd
        return d

    _shifts = (LG.journey_bar_shifts(
        LG.sections_to_plan(secs, song.get("lengthBars", 0)),
        int(song.get("lengthBars", 0)),
        deg_of_bar=base_deg) if secs else [])           # W34: the V-cadence field

    def deg_at(bar):
        return base_deg(bar) + (_shifts[bar] if bar < len(_shifts) else 0)

    lead = next((t for t in song.get("tracks", [])
                 if t.get("name") == "lead" and t.get("notes")), None)
    if lead is None:
        return {"lead": False}
    ns = sorted(lead["notes"], key=lambda n: n["start"])
    # W81: a modulated final span is a NEW KEY, not off-key notes — normalize
    # back before scoring (arrange stamps "_modulation" when it lifts)
    _mod = song.get("_modulation") or {}
    _msemi = int(_mod.get("semitones", 0) or 0)
    _mfrom = float(_mod.get("fromBeat", 0) or 0)
    if _msemi:
        ns = [dict(n, pitch=n["pitch"] - _msemi)
              if n["start"] >= _mfrom - 1e-6 else n for n in ns]

    strong, strong_ct = 0, 0
    ncts, resolved = 0, 0
    for i, n in enumerate(ns):
        bar = int(n["start"] // 4)
        cpcs = _chord_pcs(deg_at(bar), iv, root, seventh)
        is_ct = n["pitch"] % 12 in cpcs
        frac = n["start"] % 1.0
        if frac < TOL or frac > 1.0 - TOL:          # quarter-grid strong
            strong += 1
            strong_ct += 1 if is_ct else 0
        if not is_ct:
            ncts += 1
            if i + 1 < len(ns):
                m = ns[i + 1]
                mbar = int(m["start"] // 4)
                m_ct = m["pitch"] % 12 in _chord_pcs(deg_at(mbar), iv, root, seventh)
                if m_ct and abs(m["pitch"] - n["pitch"]) <= 2:
                    resolved += 1

    onsets = {}
    for n in ns:
        onsets.setdefault(int(n["start"] // 4), set()).add(
            int(round((n["start"] % 4.0) * 4)) % 16)
    bars_l = sorted(onsets)
    rep = []
    if bars_l:
        b0 = onsets[bars_l[0]]
        for b in bars_l[1:]:
            u = len(b0 | onsets[b])
            rep.append(len(b0 & onsets[b]) / u if u else 1.0)
    top = max(n["pitch"] for n in ns)
    groups = {}
    for n in ns:
        groups.setdefault(int(n["start"] // 16), n)   # keeps the LAST (sorted later)
    cad, cad_ct = 0, 0
    for gk in sorted(groups):
        last = max((n for n in ns if int(n["start"] // 16) == gk),
                   key=lambda n: n["start"])
        bar = int(last["start"] // 4)
        ok_now = last["pitch"] % 12 in _chord_pcs(deg_at(bar), iv, root, seventh)
        ok_next = last["pitch"] % 12 in _chord_pcs(deg_at(bar + 1), iv, root, seventh)
        cad += 1
        cad_ct += 1 if (ok_now or ok_next) else 0

    return {"lead": True, "notes": len(ns),
            "strong_ct": round(strong_ct / strong, 3) if strong else None,
            "nct_resolve": round(resolved / ncts, 3) if ncts else 1.0,
            "rhythm_rep": round(sum(rep) / len(rep), 3) if rep else 1.0,
            "climax_count": sum(1 for n in ns if n["pitch"] == top),
            "pc_economy": len({n["pitch"] % 12 for n in ns}),
            "cadence_ct": round(cad_ct / cad, 3) if cad else None}


def selftest():
    import random
    genres = ("trap", "house", "synthwave", "jazz", "dnb", "reggae")
    fails = []
    for g in genres:
        LG.generate(g, f"_mus_{g}", bars=4, seed=7)
        s = json.load(open(os.path.join(ROOT, "songs", f"_mus_{g}.json")))
        r = score(s, g)
        os.remove(os.path.join(ROOT, "songs", f"_mus_{g}.json"))
        if not r.get("lead"):
            print(f"  {g:10s} (no lead lane — language)")
            continue
        line = (f"  {g:10s} strong_ct {r['strong_ct']} resolve {r['nct_resolve']} "
                f"rep {r['rhythm_rep']} climax x{r['climax_count']} "
                f"pcs {r['pc_economy']} cadence {r['cadence_ct']}")
        bad = []
        if r["strong_ct"] is not None and r["strong_ct"] < 0.7:
            bad.append("strong_ct<0.7")
        if r["rhythm_rep"] < 0.55:
            bad.append("rep<0.55")
        if r["climax_count"] > 3:
            bad.append("climax>3")
        if r["cadence_ct"] is not None and r["cadence_ct"] < 0.5:
            bad.append("cadence<0.5")
        print(line + ("   XX " + ",".join(bad) if bad else ""))
        if bad:
            fails.append((g, bad))
    # no-crash sweep: every lead-bearing genre generates under the hook engine
    d = json.load(open(os.path.join(ROOT, "agent", "dna_cache.json")))["genres"]
    lead_genres = [g for g in sorted(d)
                   if isinstance(d[g].get("grid"), dict) and d[g]["grid"].get("lead")]
    crashed = []
    for g in lead_genres:
        try:
            LG.generate(g, "_mus_sweep", bars=4, seed=3)
        except Exception as e:
            crashed.append((g, repr(e)[:80]))
    p = os.path.join(ROOT, "songs", "_mus_sweep.json")
    if os.path.exists(p):
        os.remove(p)
    print(f"  sweep: {len(lead_genres) - len(crashed)}/{len(lead_genres)} "
          f"lead genres generate clean")
    for g, e in crashed[:5]:
        print(f"    CRASH {g}: {e}")
    ok = not fails and not crashed
    print(f"musicality battery: {'clean' if ok else 'RED ' + str(fails[:3])}")
    return 0 if ok else 1


def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        return 0
    if a[0] == "--selftest":
        return selftest()
    song = json.load(open(a[0]))
    print("MUSIC_JSON " + json.dumps(score(song)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
