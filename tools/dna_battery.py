#!/usr/bin/env python3
"""dna_battery.py — the FOURTH net: loop-DNA correctness across every genre.

  dna_battery.py [--render] [--filter G]

For every grid-bearing genre: generate (fixed seed) and verify each feature
the grid CLAIMS (the feature-matrix law — no sampling bias):
  GEN      loop_gen produces a song
  KEY      lead notes all diatonic (if lead present)
  CHANGES  per-bar bass pitch-classes intersect the bar's chord tones (if chords)
  FILL     filled lanes differ in the final bar vs bar 1 (if fill)
  RENDER   (--render) m1 renders non-trivially — slower, optional
Exits nonzero on any failure. JSON checks are ground truth; audio timing is
covered by the historical spot-checks (swing probes) and stays out of the fast path.
"""
import argparse, json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from kg import KG

PY = os.path.join(ROOT, ".venv", "bin", "python")
M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")
NOTE_PC = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5,
           "F#": 6, "Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11}


def pcs_for(key):
    """ONE KERNEL: the law judges against the same parser the generator plays
    from (tools/loop_gen.key_to_pcs — mode table incl. Phrygian/Hijaz/pentatonic;
    a private battery re-parse drifted once and crashed on 'A Kurdi (Phrygian)',
    masking 25 real wrong-scale bugs behind the crash)."""
    from loop_gen import key_to_pcs
    return key_to_pcs(key)[1]


def check_genre(genre, grid, do_render):
    tmp = os.path.join(ROOT, "songs", "_dnabat.json")
    r = subprocess.run([PY, os.path.join(ROOT, "tools", "loop_gen.py"), genre, "_dnabat",
                        "--bars", "4", "--seed", "3"], capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(tmp):
        return ["GEN"]
    song = json.load(open(tmp))
    pcs = pcs_for(song.get("key", "A minor"))
    fails = []
    tracks = {t["name"]: t for t in song["tracks"]}
    if grid.get("lead"):
        lead = tracks.get("lead")
        if not lead or any(n["pitch"] % 12 not in pcs for n in lead["notes"]):
            fails.append("KEY")
    if grid.get("chords"):
        # W87: a take may substitute middle chords (function-preserving) —
        # judge the bass against the TAKE's field, the truth it composed in
        prog = (song.get("_loop") or {}).get("chords") or grid["chords"]
        span = max(b for b, _ in prog) + 1
        bass = tracks.get("bass")
        if bass:
            for bar in range(min(4, span)):
                d = 1
                for b0, dd in sorted(prog):
                    if bar % span >= b0:
                        d = dd
                i = d - 1
                chord = {pcs[i % 7], pcs[(i + 2) % 7], pcs[(i + 4) % 7],
                         (pcs[i % 7] + 7) % 12, (pcs[i % 7] + 10) % 12, (pcs[i % 7] + 5) % 12}
                broots = {n["pitch"] % 12 for n in bass["notes"] if bar * 4 <= n["start"] < (bar + 1) * 4}
                if broots and not (broots & chord):
                    fails.append("CHANGES")
                    break
    if grid.get("bass_style") and grid.get("bass_style") != "none":
        # THE SUB FAMINE law (worldclass ledger 2026-07-12): bass_style "sub"
        # was unhandled in bass_notes and 12 genres (plugg/rage/jersey_drill…)
        # silently birthed with ZERO bass lane. A style the generator does not
        # speak must turn the suite red, never ship an empty low end.
        if "bass" not in tracks or not tracks["bass"].get("notes"):
            fails.append("BASS")
    # THE TASTE LAW (wave 44, Chezy live 2026-07-12: "weird sounding and
    # off-putting" instrument picks): a MELODIC lane never speaks in a
    # drum-zone voice — the census caught boombap's chord lane playing a
    # SNARE, ukgarage's a HAT, hard_techno's a KICK (first-non-null recipe
    # voice picked zone recipes). kg.eligible_recipe_voice is the predicate.
    from kg import eligible_recipe_voice
    for t in song["tracks"]:
        if t.get("name", "").startswith(("lead", "color", "keys", "chords", "arp", "pad")):
            vid = (t.get("source") or {}).get("id")
            if vid and not eligible_recipe_voice(vid):
                fails.append(f"TASTE({t['name']}={vid})")
                break
    if grid.get("fill"):
        # a fill passes if ANY filled lane differs in the final bar (adding a
        # lane counts; keeping kick identical while snare rolls is valid design)
        any_diff = False
        for lane in ("kick", "snare", "hat"):
            if grid["fill"].get(lane) is None:
                continue
            tr = tracks.get(lane)
            if tr is None:
                continue
            b1 = sorted(round(n["start"] % 4, 3) for n in tr["notes"] if 0 <= n["start"] < 4)
            b4 = sorted(round(n["start"] % 4, 3) for n in tr["notes"] if 12 <= n["start"] < 16)
            if b1 != b4:
                any_diff = True
                break
        if not any_diff:
            fails.append("FILL")
    if do_render:
        wav = os.path.join(ROOT, "songs", "_dnabat.wav")
        r = subprocess.run([M1, "render", tmp, wav], capture_output=True, text=True, timeout=300)
        if "ok=1" not in r.stdout + r.stderr or os.path.getsize(wav) < 50000:
            fails.append("RENDER")
        if os.path.exists(wav):
            os.remove(wav)
    os.remove(tmp)
    return fails


def main(do_render, flt):
    kg = KG()
    rows = kg.q("MATCH (g:Genre)-[:CHARACTERIZED_BY]->(p:PatternArchetype) "
                "WHERE p.grid IS NOT NULL RETURN g.name, p.grid ORDER BY g.name")
    # THE ATLAS LAWS (groove wave 2026-07-09): grooves are the identity organ.
    # A dangling groove name applies as SILENT no-feel (apply_groove returns an
    # error string loop_gen ignores) — that class of rot must turn the suite red.
    import groove as groove_mod
    from kg_seed_grooves import ATLAS, STRAIGHT_ON_PURPOSE
    store = groove_mod.store()
    links = kg.q("MATCH (g:Genre)-[:HAS_GROOVE]->(gr:Groove) RETURN g.name, gr.name")
    atlas_bad = []
    dangling = sorted({gr for _, gr in links if gr not in store})
    if dangling:
        atlas_bad.append(f"ATLAS dangling groove names: {dangling}")
    linked = {g for g, _ in links}
    unconsidered = sorted({g for g, _ in rows}
                          - set(ATLAS) - STRAIGHT_ON_PURPOSE - linked)
    if unconsidered:
        atlas_bad.append(f"ATLAS unconsidered genres: {unconsidered}")
    if len(linked) < 150:
        atlas_bad.append(f"ATLAS coverage regressed: {len(linked)} genres < 150")
    for gname in sorted({gr for _, gr in links if gr in store}):
        offs, vels = store[gname].get("off", []), store[gname].get("vel", [])
        if len(offs) != 16 or len(vels) != 16 or any(abs(o) > 0.2 for o in offs) \
           or any(not (0 < v <= 1.2) for v in vels):
            atlas_bad.append(f"ATLAS profile insane: {gname}")
    # GROOVE INHERITANCE PARITY (2026-07-11): a subgenre with no direct groove
    # inherits its parent's feel one hop, in BOTH the live query and the cache
    # (the two-path law). Prove they AGREE — else a groove edit that skips a
    # cache re-export silently ships stiff generation on the no-graph machines.
    inh = kg.q("MATCH (g:Genre)-[:SUBGENRE_OF]->(:Genre)-[:HAS_GROOVE]->(gr:Groove) "
               "WHERE NOT (g)-[:HAS_GROOVE]->() RETURN g.name, gr.name")
    try:
        _cache = json.load(open(os.path.join(ROOT, "agent", "dna_cache.json")))["genres"]
    except Exception:
        _cache = {}
    import loop_gen as _lg
    for gname, parent_groove in inh:
        live = (_lg.genre_dna(gname)[0] or {}).get("groove")
        if live != parent_groove:
            atlas_bad.append(f"GROOVE inherit (live) {gname}: want {parent_groove} got {live}")
        cached = _cache.get(gname, {}).get("groove")
        if _cache and cached != parent_groove:
            atlas_bad.append(f"GROOVE inherit (cache stale — re-export) {gname}: "
                             f"want {parent_groove} got {cached}")
    if inh:
        print(f"  groove inheritance: {len(inh)} subgenres inherit a parent feel, "
              f"live+cache parity {'HELD' if not any('GROOVE' in m for m in atlas_bad) else 'BROKEN'}")
    # FORM INHERITANCE (2026-07-11): same one-hop rule for song STRUCTURE — a
    # subgenre with no form_family arranges like its parent (jungle -> dnb's club
    # form: 7 sections with the second build, not the generic 6). arrange.py reads
    # form_family from the CACHE only, so a missing re-export = generic arrangements.
    finh = kg.q("MATCH (g:Genre)-[:SUBGENRE_OF]->(p:Genre) WHERE g.form_family IS NULL "
                "AND p.form_family IS NOT NULL RETURN g.name, p.form_family")
    for gname, pform in finh:
        if _cache and _cache.get(gname, {}).get("form_family") != pform:
            atlas_bad.append(f"FORM inherit (cache stale — re-export) {gname}: want {pform} "
                             f"got {_cache.get(gname, {}).get('form_family')}")
    if finh:
        print(f"  form inheritance: {len(finh)} subgenres inherit a parent form_family, "
              f"cache parity {'HELD' if not any('FORM' in m for m in atlas_bad) else 'BROKEN'}")
    for msg in atlas_bad:
        print("  " + msg)
    seen, bad = set(), []
    for genre, grid_s in rows:
        if genre in seen or (flt and flt not in genre):
            continue
        seen.add(genre)
        grid = json.loads(grid_s)
        fails = check_genre(genre, grid, do_render)
        feats = "".join(c for c, k in (("L", "lead"), ("C", "chords"), ("F", "fill")) if grid.get(k))
        if fails:
            bad.append((genre, fails))
            print(f"  {genre:20} [{feats:3}] FAIL: {','.join(fails)}")
    print(f"dna battery: {len(seen) - len(bad)}/{len(seen)} clean"
          + (f" — failures: {[b[0] for b in bad]}" if bad else "")
          + (" | ATLAS LAWS BROKEN" if atlas_bad else " | atlas laws hold"))
    sys.exit(1 if bad or atlas_bad else 0)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--render", action="store_true")
    ap.add_argument("--filter", default=None)
    a = ap.parse_args()
    main(a.render, a.filter)
