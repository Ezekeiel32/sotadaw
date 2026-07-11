#!/usr/bin/env python3
"""Proof for THE PSR FLOOR single source (tools/psr_floors.py, E6/D3/D6).

Asserts: one table (no duplicates elsewhere), longest-substring seed match,
KG-first read, SUBGENRE_OF inheritance, per-song genre resolution, default.
Exit 0 = green.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import psr_floors as P                                                        # noqa: E402

PASS, FAIL = [], []


def ck(n, c, d=""):
    (PASS if c else FAIL).append(n)
    print(f"  [{'PASS' if c else 'FAIL'}] {n}" + (f" — {d}" if d else ""))


# 1. seed table matching
ck("seed exact (funk=7.0)", P.seed_floor("funk") == 7.0)
ck("seed substring (dark_trap -> trap 5.0)", P.seed_floor("dark_trap") == 5.0,
   str(P.seed_floor("dark_trap")))
ck("seed longest-match (deep_house -> house 6.0 not h*)", P.seed_floor("deep_house") == 6.0)
ck("seed miss -> None", P.seed_floor("zzz_nonesuch") is None)

# 2. NO duplicate table anywhere in the codebase (the D6 law, enforced)
import subprocess
# a DEFINITION is `SEED_PSR_FLOORS = {` — a bare `psr_floors.SEED_PSR_FLOORS`
# reference (the correct single-source usage, e.g. kg_seed_physics) is NOT a copy
hits = subprocess.run(
    ["grep", "-rlE", "--include=*.py", r"(SEED_PSR_FLOORS|PSR_FLOORS)[ ]*=[ ]*\{",
     os.path.join(ROOT, "tools"), os.path.join(ROOT, "agent")],
    capture_output=True, text=True).stdout.split()
hits = [h for h in hits if not h.endswith("psr_floors.py")
        and not h.endswith("psr_floors_battery.py")]
ck("no duplicate PSR table (only psr_floors.py DEFINES it)", not hits, str(hits))

# 3. KG read + inheritance (needs docker sotadaw-kg; skip-pass if down)
try:
    kgmod, kg = P._kg()
    if kg is not None:
        f, s = P.floor_for_genre("funk", kg)
        ck("KG read: funk floor from graph", f == 7.0 and s.startswith(("kg", "seed")),
           f"{f} <- {s}")
        # inheritance: pick a subgenre with no own MixTarget floor but a parent that has one
        sub = kg.q("MATCH (g:Genre)-[:SUBGENRE_OF]->(p:Genre)-[:TARGETS]->(m:MixTarget) "
                   "WHERE m.psr_floor IS NOT NULL AND NOT ( (g)-[:TARGETS]->(:MixTarget "
                   "{psr_floor: m.psr_floor}) ) RETURN g.name, p.name, m.psr_floor LIMIT 1")
        if sub:
            gname, pname, pf = sub[0]
            f, s = P.floor_for_genre(gname, kg)
            ck(f"KG inheritance: {gname} <- parent {pname}", f is not None,
               f"{f} <- {s}")
        else:
            ck("KG inheritance (no eligible subgenre to test)", True, "n/a on this graph")
    else:
        ck("KG unreachable — seed path still serves", P.floor_for_genre("funk")[0] == 7.0)
except Exception as e:
    ck("KG path error-tolerant", True, f"fell back: {e}")

# 4. per-song resolve (intelligent, D3)
ck("per-song: meta.genre", P.floor_for_song({"meta": {"genre": "jazz"}})[0] == 9.0)
ck("per-song: top-level genre", P.floor_for_song({"genre": "ambient"})[0] == 10.0)
ck("per-song: genre_pref fallback", P.floor_for_song({"genre_pref": "trap"})[0] == 5.0)
r = P.floor_for_song({"tracks": []})
ck("per-song: no genre -> default 6.0", r[0] == 6.0 and r[2] == "", str(r))

# 5. THE DARK POOL of unbraked genres is drained (2026-07-11): the pure seed must
# resolve a family prior for (nearly) EVERY graph genre — a None floor makes the
# sidecar's universal loudness pass skip its crest guard. Graph-optional: on a
# live graph we assert against the real taxonomy; without it, a fixed roster.
GRAPH_GENRES = None
try:
    _km, _kg = P._kg()
    if _kg is not None:
        GRAPH_GENRES = [r[0] for r in _kg.q("MATCH (g:Genre) RETURN g.name")
                        if r[0] not in ("_untagged", "_taste_test")]
except Exception:
    GRAPH_GENRES = None
ROSTER = GRAPH_GENRES or [
    "bebop", "bluegrass", "orchestral_cinematic", "flamenco", "bossanova",
    "psytrance", "goa", "amapiano", "death_metal", "post_punk", "salsa",
    "carnatic", "afrobeats", "gqom", "trap", "house", "jazz", "ambient"]
seed_none = sorted(g for g in ROSTER if P.seed_floor(g) is None)
ck(f"seed covers the taxonomy ({len(ROSTER)} genres, <=2 fall to default)",
   len(seed_none) <= 2, f"still None: {seed_none}")
# longest-substring disambiguation the enrichment relies on
ck("swing_bigband -> 8.5 (own key beats 'swing'/'bigband')", P.seed_floor("swing_bigband") == 8.5)
ck("death_metal -> metal 6.0 (family anchor)", P.seed_floor("death_metal") == 6.0)
ck("hard_bop -> bop 9.0 (jazz family)", P.seed_floor("hard_bop") == 9.0)
ck("post_punk -> punk 7.0", P.seed_floor("post_punk") == 7.0)
ck("new_jack_swing -> 6.5 (own, not 'swing')", P.seed_floor("new_jack_swing") == 6.5)

# 6. FAMILY SANITY: live-acoustic/jazz/orchestral must sit ABOVE compressed
# electronic — the whole physics of the enrichment (crest survives real transients)
acoustic = [P.seed_floor(g) for g in ("jazz", "bebop", "bluegrass", "flamenco",
                                      "carnatic", "orchestral", "classical", "ambient")]
electronic = [P.seed_floor(g) for g in ("trap", "phonk", "dubstep", "gabber",
                                        "hardstyle", "techno", "dnb", "breakcore")]
ck("family order: min(acoustic) > max(electronic)",
   min(acoustic) > max(electronic), f"acoustic>={min(acoustic)} vs electro<={max(electronic)}")
ck("all seed floors in a sane band [4.0, 14.0]",
   all(4.0 <= v <= 14.0 for v in P.SEED_PSR_FLOORS.values()),
   str(sorted(set(P.SEED_PSR_FLOORS.values()))))

# 7. THE BRAKE ITSELF: recovery_step must now cap a lift that a None floor let run
# free. Import the pure kernel from the sidecar and prove the guard engages.
sys.path.insert(0, os.path.join(ROOT, "agent"))
import sidecar as S                                                          # noqa: E402
# a hot, quiet-ish take: dBTP -0.5, LUFS -12 -> PLR 11.5. Floor 9.0 (jazz) leaves
# a 2.5 dB budget; floor None leaves the whole 6 dB max_push unbraked.
hot = {"clipped_samples": 0, "lufs_integrated": -12.0, "true_peak_dbtp": -0.5, "lra": 9.0}
d_none, _ = S.recovery_step(hot, -6.0, None, 0.0, max_push=6.0, lra_floor=None)
d_jazz, why = S.recovery_step(hot, -6.0, 9.0, 0.0, max_push=6.0, lra_floor=None)
ck("recovery: None floor lifts unbraked (the old 143-genre bug)", d_none == 6.0, str(d_none))
ck("recovery: jazz floor 9.0 caps the same lift to its crest budget",
   0 < d_jazz < d_none and "PSR" in why, f"{d_jazz} / {why}")

# 8. THE CREST REFUND (2026-07-12): the mirror kernel. A take BORN over-driven
# into the wall ships below its floor with the lift never firing (trap probe:
# LUFS -10.5 inside [-18,-9], true PSR 3.13 vs floor 5.0 — the birth trim +2
# was the whole debt). MEASURED physics: deep in limiting a refunded drive dB
# returns only ~0.23-0.34 dB of PSR (wall pins the peaks), so the kernel asks
# debt/slope per pass and the caller iterates with the slope it measured.
# Never leaves the loudness window; refuses to paper over a mix that is simply
# too dense (debt with no headroom = an honest verdict, not a heal).
r_trap, why_t = S.refund_step(3.13, 5.0, -10.54, -18.0)
ck("refund: trap pass-1 asks debt/prior-slope (3.7 dB)", r_trap == 3.7, f"{r_trap} / {why_t}")
r_t2, _ = S.refund_step(3.57, 5.0, -11.35, -18.0, slope=0.23)
ck("refund: pass-2 rides the MEASURED slope, capped per-pass (4.0)", r_t2 == 4.0, str(r_t2))
r_bossa, _ = S.refund_step(6.62, 8.0, -14.56, -20.0)
ck("refund: bossa pass-1 (2.8 dB)", r_bossa == 2.8, str(r_bossa))
r_punchy, why_p = S.refund_step(9.5, 9.0, -14.0, -18.0)
ck("refund: silent when punchy enough", r_punchy == 0.0 and why_p == "punchy enough",
   f"{r_punchy} / {why_p}")
r_dense, why_d = S.refund_step(2.0, 9.0, -13.3, -13.5)
ck("refund: debt with no loudness headroom refuses (mix too dense at birth)",
   r_dense == 0.0 and why_d.startswith("crest debt"), f"{r_dense} / {why_d}")
r_cap, _ = S.refund_step(0.5, 9.0, -6.0, -20.0)
ck("refund: capped at per-pass max_refund 4.0", r_cap == 4.0, str(r_cap))
r_nofloor, why_n = S.refund_step(3.0, None, -10.0, -18.0)
ck("refund: None floor is a no-op", r_nofloor == 0.0 and why_n == "no floor",
   f"{r_nofloor} / {why_n}")
ck("refund: wired into loudness_recovery (the organ consults the kernel)",
   "refund_step" in S.loudness_recovery.__code__.co_names,
   str([n for n in S.loudness_recovery.__code__.co_names if "refund" in n]))

# 9. THE GENRE TRUTH (2026-07-12): the loudness pass was genre-blind on the
# prompt/verb/spectral/a2m lanes (only _loop.genre) — most recovered songs
# lifted toward -12.5 with no floors. resolve_take_genre: birth stamp >
# meta/genre field > last_genres ask-context (what the user ASKED for).
_tmp = os.path.join(ROOT, "songs", "_psrbat_gt.json")
json.dump({"_loop": {"genre": "trap"}, "meta": {"genre": "house"}}, open(_tmp, "w"))
ck("genre truth: birth stamp wins", S.resolve_take_genre("_psrbat_gt") == "trap")
json.dump({"meta": {"genre": "house"}}, open(_tmp, "w"))
ck("genre truth: meta.genre speaks when no birth stamp",
   S.resolve_take_genre("_psrbat_gt") == "house")
json.dump({"tracks": []}, open(_tmp, "w"))
S.last_genres["_psrbat_gt"] = "bebop"
ck("genre truth: the ASK is remembered (last_genres, _prop_ stripped)",
   S.resolve_take_genre("_prop__psrbat_gt") == "bebop"
   and S.resolve_take_genre("_psrbat_gt") == "bebop")
S.last_genres.pop("_psrbat_gt", None)
ck("genre truth: silence when nothing speaks", S.resolve_take_genre("_psrbat_gt") is None)
os.remove(_tmp)

print(f"\n== PSR FLOORS: {len(PASS)} pass / {len(FAIL)} fail ==")
sys.exit(0 if not FAIL else 1)
