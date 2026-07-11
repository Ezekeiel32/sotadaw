#!/usr/bin/env python3
"""SUGGEST_CHORDS — the harmony ADVISOR (Scaler-class, grounded in OUR kernels).

  suggest_chords.py <song> [--genre g] [--k N] [--json]

The chord lane could be read (chordvote), transformed (reharm), composed-from
(harmonize) and infilled (infill_region). The missing verb was ADVISE: given
the song's own progression, rank per-slot substitutions and whole-progression
rewrites WITH THE THEORY WHY — function flow (T→S→D→T), secondary dominants,
tritone subs, mode mixture, backdoor cadences, chromatic mediants — each
scored by voice-leading cost through the SAME voicing kernel real parts use
(M1), plus an optional genre prior from the KG's chord DNA (waves 25/26/37,
degrees on PatternArchetype.grid.chords; best-effort, KG-less degrades clean).

Every suggestion speaks reharm's grammar ([A-G][b#]?m?7?) so applying is one
verb away: rewrites ship a ready `reharm --to` line, and reharm's own law
(chordvote must read the target back) closes the loop.

Read-only: never mutates the song. Machine line: SUGGEST_JSON {...}
"""
import argparse, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from chordvote import chord_map, PC
from reharm import parse_chord, detect_cycle
from voicing import voice_progression
import songname

MAJ_IV = [0, 2, 4, 5, 7, 9, 11]
MIN_IV = [0, 2, 3, 5, 7, 8, 10]
DEGREE = {0: "I", 1: "bII", 2: "II", 3: "bIII", 4: "III", 5: "IV", 6: "bV",
          7: "V", 8: "bVI", 9: "VI", 10: "bVII", 11: "VII"}
DEGREE_MIN = {0: "I", 1: "bII", 2: "II", 3: "III", 4: "#III", 5: "IV", 6: "bV",
              7: "V", 8: "VI", 9: "#VI", 10: "VII", 11: "#VII"}

# function flow (Riemann/Kostka core): T→S→D→T is the engine; D→S is the
# retrogression textbooks flag; everything chromatic sits neutral.
FLOW = {("T", "S"): 1.0, ("S", "D"): 1.0, ("D", "T"): 1.0,
        ("T", "D"): 0.7, ("S", "T"): 0.7, ("D", "S"): 0.25,
        ("T", "T"): 0.6, ("S", "S"): 0.6, ("D", "D"): 0.6}


def label_of(pc, minor=False, dom7=False):
    return PC[pc % 12] + ("m" if minor else "") + ("7" if dom7 else "")


def parse_key(song, chords):
    """(tonic_pc, mode) from song.key via the generation lane's parser; a song
    with no usable key infers tonic/mode from its own first chord."""
    k = str(song.get("key") or "").strip()
    if k:
        try:
            from loop_gen import key_scale
            root, iv = key_scale(k)
            return root, ("minor" if len(iv) > 2 and iv[2] == 3 else "major")
        except Exception:
            pass
    r, q, _ = parse_chord(chords[0]["chord"])
    return r, ("minor" if q == "min" else "major")


def roman_of(label, tonic, mode):
    r, q, dom7 = parse_chord(label)
    rel = (r - tonic) % 12
    name = (DEGREE_MIN if mode == "minor" else DEGREE)[rel]
    name = name if q == "maj" else name.lower()
    return name + ("7" if dom7 else "")


def func_of(label, tonic, mode):
    """Harmonic function T/S/D (X = chromatic outsider)."""
    r, q, dom7 = parse_chord(label)
    rel = (r - tonic) % 12
    if mode == "major":
        table = {(0, "maj"): "T", (9, "min"): "T", (4, "min"): "T", (3, "maj"): "T",
                 (5, "maj"): "S", (2, "min"): "S", (5, "min"): "S", (8, "maj"): "S",
                 (7, "maj"): "D", (10, "maj"): "D", (11, "min"): "D"}
    else:
        table = {(0, "min"): "T", (3, "maj"): "T", (0, "maj"): "T",
                 (8, "maj"): "S", (5, "min"): "S", (2, "min"): "S", (5, "maj"): "S",
                 (7, "maj"): "D", (7, "min"): "D", (10, "maj"): "D"}
    f = table.get((rel, q))
    if f is None and dom7:
        return "D"                       # any dominant 7th pulls somewhere
    return f or "X"


def vl_cost(seq):
    """Total voice motion (semitones) through the smooth voicing of seq."""
    v = voice_progression(list(seq), "smooth", lo=48, hi=76)
    return sum(sum(abs(a - b) for a, b in zip(sorted(x), sorted(y)))
               for x, y in zip(v, v[1:]))


def genre_degree_prior(genre, tonic, mode):
    """Scale-degree pcs the genre's KG chord DNA uses (best-effort; {} if KG down)."""
    if not genre:
        return {}
    try:
        from kg import KG
        view = KG().genre_view(genre)
        iv = MIN_IV if mode == "minor" else MAJ_IV
        out = {}
        for p in (view or {}).get("patterns", []):
            grid = p.get("grid")
            grid = json.loads(grid) if isinstance(grid, str) else (grid or {})
            for pair in grid.get("chords") or []:
                deg = int(pair[1])
                if 1 <= deg <= 7:
                    out[(tonic + iv[deg - 1]) % 12] = deg
        return out
    except Exception:
        return {}


def candidates(slot, cycle, tonic, mode, prior):
    """Ranked alternatives for cycle[slot] with theory WHYs."""
    p = len(cycle)
    cur = cycle[slot]
    prev = cycle[(slot - 1) % p]
    nxt = cycle[(slot + 1) % p]
    nr, nq, _ = parse_chord(nxt)
    iv = MIN_IV if mode == "minor" else MAJ_IV
    cands = {}                                   # label -> set of whys

    def add(label, why):
        if label == cur:
            return
        try:
            parse_chord(label)                   # grammar law: only speakable chords
        except SystemExit:
            return
        cands.setdefault(label, []).append(why)

    for i, semi in enumerate(iv):                # diatonic set (dim degree skipped)
        pc = (tonic + semi) % 12
        if mode == "major":
            if i == 6:
                continue
            minor = i in (1, 2, 5)
        else:
            if i == 1:
                continue
            minor = i in (0, 3, 4)
        add(label_of(pc, minor), "diatonic " + roman_of(label_of(pc, minor), tonic, mode))
    add(label_of((nr + 7) % 12, dom7=True), f"V7 of next ({nxt}) — tonicizes it")
    add(label_of((nr + 1) % 12, dom7=True), f"tritone sub of V7/{nxt} — chromatic bass slide")
    if mode == "major":
        for pc, name in (((tonic + 5) % 12, "iv"), ((tonic + 8) % 12, "bVI"),
                         ((tonic + 10) % 12, "bVII"), ((tonic + 3) % 12, "bIII")):
            add(label_of(pc, minor=(name == "iv")), f"{name} borrowed from {PC[tonic]} minor (mode mixture)")
        if (nr - tonic) % 12 == 0 and nq == "maj":
            add(label_of((tonic + 10) % 12, dom7=True), "backdoor dominant (bVII7 → I)")
    else:
        add(label_of((tonic + 7) % 12), "harmonic-minor V (raised leading tone)")
        add(label_of((tonic + 7) % 12, dom7=True), "harmonic-minor V7 (strongest pull home)")
        add(label_of((tonic + 5) % 12), "dorian IV (brighter minor color)")
    cr, cq, cd7 = parse_chord(cur)
    if cq == "maj" and not cd7:
        add(label_of(cr, dom7=True), "same-root dominant color (blues pull toward its IV)")
    add(label_of((cr + (3 if cq == "min" else 9)) % 12, minor=(cq == "maj")),
        "relative swap (shares two tones)")
    if cq == "maj":
        for d in (3, 4, 8, 9):
            add(label_of((cr + d) % 12), "chromatic mediant (film color)")

    base_vl = vl_cost([prev, cur, nxt])
    fp = func_of(prev, tonic, mode)
    fn = func_of(nxt, tonic, mode)
    out = []
    for label, whys in cands.items():
        r, q, dom7 = parse_chord(label)
        fc = func_of(label, tonic, mode)
        flow = 0.5 * FLOW.get((fp, fc), 0.45) + 0.5 * FLOW.get((fc, fn), 0.45)
        if dom7 and (r - nr) % 12 == 7:
            flow = max(flow, 1.15)               # secondary dominant into next
        if dom7 and (r - nr) % 12 == 1:
            flow = max(flow, 1.05)               # tritone approach into next
        cost = vl_cost([prev, label, nxt])
        vl_gain = (base_vl - cost) / 12.0
        score = flow + 0.35 * max(-1.0, min(1.0, vl_gain))
        if r % 12 in prior:
            score += 0.15
            whys = whys + [f"genre DNA uses degree {prior[r % 12]}"]
        if any("chromatic mediant" in w for w in whys):
            score -= 0.1
        out.append({"chord": label, "roman": roman_of(label, tonic, mode),
                    "function": fc, "why": whys, "score": round(score, 3),
                    "vl_cost": cost})
    out.sort(key=lambda a: (-a["score"], a["chord"]))
    return out


def cycle_score(cycle, tonic, mode):
    fs = [func_of(c, tonic, mode) for c in cycle]
    flow = sum(FLOW.get((fs[i], fs[(i + 1) % len(fs)]), 0.45) for i in range(len(fs)))
    lr, _, _ = parse_chord(cycle[-1])
    cad = 0.3 if ((lr - tonic) % 12 == 7 and fs[-1] == "D") else 0.0
    return flow / max(1, len(fs)) + cad


def classify_cadence(last, first, tonic, mode):
    lr, lq, ld7 = parse_chord(last)
    fr, _, _ = parse_chord(first)
    rel_l, rel_f = (lr - tonic) % 12, (fr - tonic) % 12
    if rel_f == 0:
        if rel_l == 7:
            return "authentic (V→I)" if (lq == "maj" or ld7) else "minor-v cadence (modal)"
        if rel_l == 5:
            return "plagal (IV→I)"
        if rel_l == 10:
            return "backdoor (bVII→I)" if ld7 else "subtonic close (VII→i)"
    if rel_l == 7 and rel_f in (8, 9):
        return "deceptive (V→vi)"
    if func_of(last, tonic, mode) == "D":
        return "half (rests on the dominant)"
    return "open (no classical close)"


def suggest(song, genre=None, k=4):
    chords = song.get("chords") or chord_map(song)
    if not chords:
        return {"available": False, "reason": "no chords — vote first (chordvote) or the song has no melodic notes"}
    labels = [c["chord"] for c in chords]
    p = detect_cycle(labels)
    cycle = labels[:p]
    tonic, mode = parse_key(song, chords)
    prior = genre_degree_prior(genre, tonic, mode)
    # ONE entry per unique harmonic CONTEXT (prev, current, next) — a 300-bar
    # near-static song asks the same question once, not 300 times.
    ctx_order, ctx_slots = [], {}
    for i in range(p):
        key3 = (cycle[(i - 1) % p], cycle[i], cycle[(i + 1) % p])
        if key3 not in ctx_slots:
            ctx_order.append(key3)
            ctx_slots[key3] = []
        ctx_slots[key3].append(i)
    slots = []
    for key3 in ctx_order:
        idxs = ctx_slots[key3]
        i = idxs[0]
        bars = [c["bar"] for j, c in enumerate(chords) if j % p in set(idxs[:16])]
        slots.append({"slot": i, "slots": idxs[:16], "bars": bars[:8],
                      "current": cycle[i],
                      "roman": roman_of(cycle[i], tonic, mode),
                      "function": func_of(cycle[i], tonic, mode),
                      "alts": candidates(i, cycle, tonic, mode, prior)[:k]})
    rewrites = []
    if p > 1:
        rots = sorted(((cycle_score(cycle[r:] + cycle[:r], tonic, mode), r)
                       for r in range(1, p)), key=lambda t: (-t[0], t[1]))
        for sc, r in rots[:2]:
            rw = cycle[r:] + cycle[:r]
            rewrites.append({"name": f"rotation+{r}", "chords": rw, "score": round(sc, 3),
                             "why": "schema rotation (wave-29 law: one schema, start anywhere)"})
    best_swap, best_gain = None, 0.0
    for s in slots:
        for a in s["alts"]:
            colored = any(("mixture" in w) or ("V7 of next" in w) or ("tritone" in w)
                          or ("backdoor" in w) for w in a["why"])
            if colored and a["score"] > best_gain:
                rw = list(cycle)
                rw[s["slot"]] = a["chord"]
                best_swap = {"name": "color_one", "chords": rw,
                             "score": round(a["score"], 3),
                             "why": f"slot {s['slot']} {s['current']}→{a['chord']}: " + a["why"][0]}
                best_gain = a["score"]
    if best_swap:
        rewrites.append(best_swap)
    for rw in rewrites:
        rw["reharm"] = "python3 tools/reharm.py <song> --to \"" + ",".join(rw["chords"]) + "\""
    return {"available": True, "key": {"tonic": PC[tonic], "mode": mode},
            "cycle_bars": p, "progression": cycle,
            "roman": [roman_of(c, tonic, mode) for c in cycle],
            "cadence": classify_cadence(cycle[-1], cycle[0], tonic, mode),
            "slots": slots, "rewrites": rewrites}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("song")
    ap.add_argument("--genre", default=None)
    ap.add_argument("--k", type=int, default=4)
    ap.add_argument("--json", action="store_true", help="full JSON only")
    a = ap.parse_args()
    name = songname.resolve(a.song)
    song = json.load(open(os.path.join(ROOT, "songs", f"{name}.json")))
    out = suggest(song, a.genre, a.k)
    out["song"] = name
    if not a.json and out.get("available"):
        key = out["key"]
        runs = []
        for c, r in zip(out["progression"], out["roman"]):
            if runs and runs[-1][0] == (c, r):
                runs[-1][1] += 1
            else:
                runs.append([(c, r), 1])
        prog = "  ".join(f"{c}({r})" + (f"x{n}" if n > 1 else "") for (c, r), n in runs[:16])
        if len(runs) > 16:
            prog += f"  … +{len(runs) - 16} more runs"
        print(f"[suggest] {name}: {key['tonic']} {key['mode']}  cycle {out['cycle_bars']} bars  "
              + prog + f"  cadence: {out['cadence']}")
        for s in out["slots"][:12]:
            alts = "  ".join(f"{a['chord']}[{a['score']}] {a['why'][0]}" for a in s["alts"][:2])
            many = f" (x{len(s['slots'])} slots)" if len(s.get("slots", [])) > 1 else ""
            print(f"  slot {s['slot']}{many} {s['current']} ({s['roman']},{s['function']}) -> {alts}")
        if len(out["slots"]) > 12:
            print(f"  … +{len(out['slots']) - 12} more contexts (see SUGGEST_JSON)")
        for rw in out["rewrites"]:
            print(f"  rewrite {rw['name']}: {','.join(rw['chords'][:16])}"
                  + ("…" if len(rw["chords"]) > 16 else "") + f" — {rw['why']}")
    print("SUGGEST_JSON " + json.dumps(out))


if __name__ == "__main__":
    main()
