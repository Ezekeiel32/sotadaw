#!/usr/bin/env python3
"""W11 FACTORY AUTONOMY (supervised): one measured lesson cycle for a genre.

  advisor_cycle.py <genre>                # dry-run: show pre-score + proposed patch
  advisor_cycle.py <genre> --apply        # apply graph patch + recompile skill (free)
  advisor_cycle.py <genre> --brief        # ALSO run the paid re-brief (~$2-4)
  advisor_cycle.py <genre> --verdict      # compare the two latest runs -> lessons.jsonl

The loop: eval fails -> patch the GRAPH (never the skill text) -> recompile ->
re-brief -> keep the lesson only if the score improved. Every verdict lands in
eval/lessons.jsonl (pre, post, patch, kept) — the factory's measured memory.
Reverts are SUPERVISED: a failed lesson prints revert guidance, never auto-deletes.
"""
import argparse, json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
HIST = os.path.join(ROOT, "eval", "history.jsonl")
LESSONS = os.path.join(ROOT, "eval", "lessons.jsonl")

MIX_TECH = [("loudness_recovery", 0.85), ("gain_staged_saturation", 0.8)]


def runs_for(genre):
    if not os.path.exists(HIST):
        return []
    out = []
    for line in open(HIST):
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if r.get("genre") == genre and "score" in r:
            out.append(r)
    return out


def propose(genre, last):
    """Failing checks -> graph patch plan [(kind, args...)]. Mirrors factory_advisor."""
    fails = [k for k, v in last.get("checks", {}).items() if not v]
    plan = []
    for f in fails:
        if "clip" in f or "lufs" in f or "peak" in f:
            for t, w in MIX_TECH:
                plan.append(("tech_edge", genre, t, w))
        elif "swing" in f or "groove" in f:
            plan.append(("note", f"link a Groove to '{genre}' (groove.py seed-kg LINKS) and re-publish"))
        else:
            plan.append(("note", f"needs a curated lesson Technique for '{f}' — human judgment"))
    # dedupe preserving order
    seen, out = set(), []
    for p in plan:
        if p not in seen:
            seen.add(p); out.append(p)
    return fails, out


def apply_plan(plan):
    """Execute tech_edge items idempotently. Returns True if the graph CHANGED."""
    from kg import KG
    kg = KG()
    changed = False
    for item in plan:
        if item[0] != "tech_edge":
            continue
        _, g, t, w = item
        pre = kg.q(f"MATCH (:Genre {{name:'{g}'}})-[u:USES_TECHNIQUE]->(:Technique {{name:'{t}'}}) RETURN u.weight")
        if pre and pre[0] and float(pre[0][0] or 0) >= w:
            print(f"  = edge {g}-USES->{t} already at weight {pre[0][0]} (staged)")
            continue
        kg.link("Genre", g, "USES_TECHNIQUE", "Technique", t, weight=w)
        print(f"  + edge {g}-USES->{t} weight {w}")
        changed = True
    return changed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("genre")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--brief", action="store_true", help="run the PAID re-brief after applying")
    ap.add_argument("--verdict", action="store_true", help="compare two latest runs -> lessons.jsonl")
    a = ap.parse_args()
    runs = runs_for(a.genre)

    if a.verdict:
        if len(runs) < 2:
            sys.exit(f"need >=2 runs of {a.genre} for a verdict (have {len(runs)})")
        pre, post = runs[-2], runs[-1]
        kept = post["score"] > pre["score"]
        v = {"genre": a.genre, "pre": pre["score"], "post": post["score"], "kept": kept,
             "pre_t": pre.get("t"), "post_t": post.get("t"),
             "fixed": [k for k, ok in post.get("checks", {}).items()
                       if ok and not pre.get("checks", {}).get(k, True)]}
        with open(LESSONS, "a") as f:
            f.write(json.dumps(v) + "\n")
        print(f"VERDICT {a.genre}: {pre['score']:.3f} -> {post['score']:.3f} "
              f"({'LESSON KEPT' if kept else 'NO GAIN — review the lesson'}); fixed: {v['fixed']}")
        if not kept:
            print("revert guidance: lower/remove the patched USES_TECHNIQUE edge weights, "
                  "re-publish the skill, and record why in the wave seed (supervised — nothing auto-deleted).")
        return

    if not runs:
        sys.exit(f"no eval history for {a.genre} — run eval_daw.py --brief {a.genre} first")
    last = runs[-1]
    fails, plan = propose(a.genre, last)
    print(f"{a.genre}: latest score {last['score']:.3f}; failing: {fails or 'none'}")
    for item in plan:
        print(f"  plan: {item}")
    if not a.apply:
        print("(dry-run — pass --apply to patch the graph + recompile)")
        return
    changed = apply_plan(plan)
    if changed:
        subprocess.run([sys.executable, os.path.join(ROOT, "tools", "skill_compiler.py"),
                        a.genre, "--publish"], check=True)
        print(f"skill re-published for {a.genre}")
    else:
        print("graph unchanged — skill NOT re-published (no version noise)")
    if a.brief:
        print("running PAID re-brief…")
        subprocess.run([sys.executable, os.path.join(ROOT, "tools", "eval_daw.py"),
                        "--brief", a.genre], check=True)
        main_verdict = subprocess.run([sys.executable, __file__, a.genre, "--verdict"])


if __name__ == "__main__":
    main()
