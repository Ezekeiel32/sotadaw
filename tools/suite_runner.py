#!/usr/bin/env python3
"""THE SUITE RUNNER — batch eval orchestration with a hard budget stop-loss.

  suite_runner.py --dry-run                     # the plan: who runs, est. cost, nothing fires
  suite_runner.py --budget 50                   # run UNCOVERED genres until ~$50 spent, then stop
  suite_runner.py --budget 400 --all            # the full first pass (Chezy's explicit OK required)
  suite_runner.py --genres reggae,soca --budget 10
  suite_runner.py --limit 5 --budget 20         # at most 5 genres

Default population: UNCOVERED genres (no history entry) — so the runner is
resume-safe by construction: re-running continues where the last run stopped.
Every run appends to eval/history.jsonl as usual; failures are isolated (one
bad genre never kills the batch); the trend page regenerates at the end.
COSTS REAL MONEY (~$2.5-5.5/brief observed). The budget flag is a HARD stop
checked before each launch — no flag, no run (explicit-spend law).
"""
import argparse, json, os, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
HIST = os.path.join(ROOT, "eval", "history.jsonl")
EST_PER_BRIEF = 3.4          # observed mean, 2026-07-03 (range 2.3-5.4)


def covered_genres():
    got = set()
    if os.path.exists(HIST):
        for line in open(HIST):
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if "score" in r and r.get("genre"):
                got.add(r["genre"])
    return got


def all_genres():
    from kg import KG
    return sorted(r[0] for r in KG().q("MATCH (g:Genre) RETURN g.name")
                  if r[0] != "_untagged")


def last_run(genre):
    out = None
    if os.path.exists(HIST):
        for line in open(HIST):
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if r.get("genre") == genre and "score" in r:
                out = r
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--genres", help="comma-separated explicit list")
    ap.add_argument("--all", action="store_true", help="every genre (not just uncovered)")
    ap.add_argument("--limit", type=int, default=None, help="max genres this run")
    ap.add_argument("--budget", type=float, default=None,
                    help="HARD dollar stop-loss (required to actually run)")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    if a.genres:
        plan = [g.strip() for g in a.genres.split(",") if g.strip()]
    else:
        pool = all_genres()
        plan = pool if a.all else [g for g in pool if g not in covered_genres()]
    if a.limit is not None:
        plan = plan[: a.limit]

    est = len(plan) * EST_PER_BRIEF
    print(f"[suite] plan: {len(plan)} genres, est ~${est:.0f} "
          f"(budget: {'$%.0f' % a.budget if a.budget else 'NONE SET'})")
    if a.dry_run:
        for g in plan:
            lr = last_run(g)
            tag = f"last {lr['score']:.2f}" if lr else "uncovered"
            print(f"  {g:22} {tag}")
        return
    if a.budget is None:
        sys.exit("[suite] refusing to spend without --budget (explicit-spend law). "
                 "Use --dry-run to see the plan.")

    spent, results = 0.0, []
    for i, g in enumerate(plan):
        if spent + EST_PER_BRIEF > a.budget:
            print(f"[suite] budget stop-loss: ${spent:.2f} spent, next brief would exceed ${a.budget:.0f}")
            break
        print(f"[suite] ({i+1}/{len(plan)}) {g} … ", end="", flush=True)
        t0 = time.time()
        p = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "eval_daw.py"),
                            "--brief", g], capture_output=True, text=True,
                           timeout=2400, cwd=ROOT)
        lr = last_run(g)
        if lr and lr.get("t", 0) > t0 - 5:
            cost = float(lr.get("cost_usd") or EST_PER_BRIEF)
            spent += cost
            results.append((g, lr["score"], cost))
            print(f"score {lr['score']:.3f}  ${cost:.2f}  (total ${spent:.2f})")
        else:
            spent += EST_PER_BRIEF            # count failures against budget too
            results.append((g, None, EST_PER_BRIEF))
            print(f"FAILED (rc {p.returncode}) — counted ${EST_PER_BRIEF:.2f} against budget")

    subprocess.run([sys.executable, os.path.join(ROOT, "tools", "eval_trend.py")],
                   capture_output=True, cwd=ROOT)
    ok = [r for r in results if r[1] is not None]
    red = [r for r in ok if r[1] < 0.857]
    print(f"\n[suite] done: {len(ok)}/{len(results)} ran, ${spent:.2f} spent, "
          f"{len(red)} below 0.857" + (f" -> {', '.join(g for g, _, _ in red)}" if red else ""))
    print("[suite] next: advisor_cycle <genre> --apply for each red; re-run me to continue coverage")


if __name__ == "__main__":
    main()
