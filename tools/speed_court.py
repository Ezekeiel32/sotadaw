#!/usr/bin/env python3
"""THE SPEED COURT (THE_UTMOST §4.4: every latency class is a named budget with teeth).

Latency is measured from EVIDENCE the house already writes — agent/ipc/events.jsonl
run clusters + telemetry/proposals.jsonl verdict rows — never from synthetic load.
A class convicts only when MEASURED here with n>=MIN_N; classes measured by other
organs (accept EditDelta, parse lane) are cited, not re-tried. Budgets are the
FLOOR under today's truth (regression alarms), not the ceiling table in the doc:
the ratchet tightens them as the roads land.

  report      human table from the live evidence files
  --selftest  deterministic kernel proof on synthetic fixtures (the suite leg)

Exit: report is always 0 (informational for humans); --selftest is the law.
"""
from __future__ import annotations
import json, os, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# class -> (budget_seconds, percentile, description)
BUDGETS = {
    "ask_run_p50":   (120.0, 50, "conversational ask -> served take (compose p50 85s today)"),
    "ask_run_p90":   (300.0, 90, "conversational ask tail"),
    "verb_run_p50":  (60.0,  50, "zero/low-token verb run (finish/groove/make lanes)"),
    "first_ink_p50": (3.0,   50, "run start -> first visible activity (ghost 0.7s today)"),
}
MIN_N = 5

# measured by other organs — cited so the table is the WHOLE speed truth
EXTERN = [
    ("accept apply",  "1.95ms live", "ENGINE DELTA (SOTADAW_PROF, memory engine-delta-shipped)"),
    ("parse lane",    "5.5ms median", "sidecar T1 kernel bench (memory parse-lane)"),
    ("MAKE stranger", "~13s",        "tools/stranger_e2e.py x3 (zero-credential)"),
]


def cluster_runs(events_path):
    """events.jsonl -> run clusters. A run: lines sharing id from its first event
    after the previous done(id) until kind=='done'. ids recycle across daemon
    lives — the done boundary is what closes a cluster, order is file order."""
    runs, open_runs = [], {}
    try:
        f = open(events_path, "r", encoding="utf-8", errors="replace")
    except OSError:
        return runs
    with f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except ValueError:
                continue  # torn concurrent append — the event wall's law, mirrored
            rid = ev.get("id")
            kind = ev.get("kind")
            t = ev.get("t")
            if rid is None or kind is None or not isinstance(t, (int, float)):
                continue
            cur = open_runs.get(rid)
            if cur is None:
                cur = {"id": rid, "t0": t, "song": ev.get("song"),
                       "first_ink": None, "duration_s": None, "served": False}
                open_runs[rid] = cur
            if cur["song"] is None and ev.get("song"):
                cur["song"] = ev.get("song")
            if cur["first_ink"] is None and kind in ("activity", "think", "proposal_progress"):
                cur["first_ink"] = max(0.0, t - cur["t0"])
            if kind in ("proposal", "proposal_progress"):
                cur["served"] = True  # a take reached the deck — this is a COMPOSE run
            # anatomy marks: where a run's wall-clock actually goes
            if kind == "proposal_progress":
                cur.setdefault("t_stream0", t)
                cur["t_streamN"] = t
            elif kind == "proposal":
                cur.setdefault("t_prop", t)
            elif kind == "activity":
                txt = str(ev.get("text", ""))
                if txt.startswith("[render]"):
                    cur.setdefault("t_render", t)
                elif txt.startswith("[meters]"):
                    cur.setdefault("t_meters", t)
            elif kind == "courts":
                cur.setdefault("t_courts", t)
            if kind == "done":
                stats = ev.get("stats") or {}
                d = stats.get("duration_s")
                cur["duration_s"] = float(d) if isinstance(d, (int, float)) else max(0.0, t - cur["t0"])
                runs.append(cur)
                del open_runs[rid]
    return runs


def load_verdict_prompts(telemetry_path):
    """(song, t) -> prompt rows for run classification (verb vs conversational)."""
    rows = []
    try:
        f = open(telemetry_path, "r", encoding="utf-8", errors="replace")
    except OSError:
        return rows
    with f:
        for line in f:
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if isinstance(r.get("prompt"), str) and r.get("song"):
                rows.append((r["song"], float(r.get("t", 0)), r["prompt"]))
    return rows


def classify(runs, verdict_rows):
    """Split PROPOSAL-SERVING runs into verb/ask via telemetry prompts. A
    telemetry row is stamped at VERDICT time, which FOLLOWS its compose run —
    so a prompt joins the nearest same-song run whose start precedes the
    verdict (never |dt|, which matches the verdict-handling cluster instead).
    Unserved clusters (janitor/verdict lanes) and unjoinable runs are never
    guessed into a class."""
    verb, ask = [], []
    for run in (r for r in runs if r["served"]):
        best = None
        for song, t, prompt in verdict_rows:
            if song != run["song"]:
                continue
            d = t - run["t0"]
            if -1.0 <= d < 3600 and (best is None or d < best[0]):
                best = (d, prompt)
        if best is None:
            continue
        (verb if best[1].startswith("[verb]") else ask).append(run)
    return verb, ask


def pctl(values, p):
    vs = sorted(v for v in values if isinstance(v, (int, float)))
    if not vs:
        return None
    k = max(0, min(len(vs) - 1, int(round((p / 100.0) * (len(vs) - 1)))))
    return vs[k]


def judge(runs, verdict_rows):
    verb, ask = classify(runs, verdict_rows)
    inks = [r["first_ink"] for r in runs if r["served"] and r["first_ink"] is not None]
    samples = {
        "ask_run_p50":   [r["duration_s"] for r in ask],
        "ask_run_p90":   [r["duration_s"] for r in ask],
        "verb_run_p50":  [r["duration_s"] for r in verb],
        "first_ink_p50": inks,
    }
    verdicts = {}
    for name, (budget, p, desc) in BUDGETS.items():
        vals = [v for v in samples[name] if v is not None]
        if len(vals) < MIN_N:
            verdicts[name] = {"verdict": "UNMEASURED", "n": len(vals), "budget_s": budget,
                              "measured_s": None, "desc": desc}
            continue
        m = pctl(vals, p)
        verdicts[name] = {"verdict": "PASS" if m <= budget else "BREACH", "n": len(vals),
                          "budget_s": budget, "measured_s": round(m, 2), "desc": desc}
    return verdicts


def report(ipc_dir=None, telemetry_path=None):
    ipc = ipc_dir or os.environ.get("SOTADAW_IPC") or os.path.join(ROOT, "agent", "ipc")
    tel = telemetry_path or os.path.join(ROOT, "telemetry", "proposals.jsonl")
    runs = cluster_runs(os.path.join(ipc, "events.jsonl"))
    verdicts = judge(runs, load_verdict_prompts(tel))
    print(f"THE SPEED COURT — {len(runs)} runs in evidence ({os.path.join(ipc,'events.jsonl')})")
    print(f"{'class':<16}{'verdict':<12}{'measured':<12}{'budget':<10}{'n':<6}what")
    for name, v in verdicts.items():
        m = "-" if v["measured_s"] is None else f"{v['measured_s']}s"
        print(f"{name:<16}{v['verdict']:<12}{m:<12}{str(v['budget_s'])+'s':<10}{v['n']:<6}{v['desc']}")
    print("\nmeasured elsewhere (cited, not re-tried):")
    for name, val, src in EXTERN:
        print(f"  {name:<16}{val:<14}{src}")
    breaches = [n for n, v in verdicts.items() if v["verdict"] == "BREACH"]
    print("\nCOURT:", ("BREACH: " + ", ".join(breaches)) if breaches else "all measured classes inside budget")
    return 0


def anatomy(ipc_dir=None, telemetry_path=None):
    """WHERE the ask's seconds go: per-phase p50/p90 across served ask runs.
    Phases are cut at the run's own event marks — think = start->first ghost
    ink; compose = the ghost stream's span; land = stream end -> courts;
    render+meters = the post-compose machine phases; serve = meters -> the
    proposal event. Evidence-only; the fix each phase points at is named."""
    ipc = ipc_dir or os.environ.get("SOTADAW_IPC") or os.path.join(ROOT, "agent", "ipc")
    tel = telemetry_path or os.path.join(ROOT, "telemetry", "proposals.jsonl")
    runs = cluster_runs(os.path.join(ipc, "events.jsonl"))
    verb, ask = classify(runs, load_verdict_prompts(tel))
    phases = [
        ("think (start->first ink)", "t0", "t_stream0", "routing/first-token (§4 lever: stream-first)"),
        ("compose (ghost stream)", "t_stream0", "t_streamN", "model wall (§4 lever: routing + parse-lane coverage)"),
        ("land (stream->courts)", "t_streamN", "t_courts", "post-compose court entry"),
        ("courts->render", "t_courts", "t_render", "court walltime (pure python)"),
        ("render", "t_render", "t_meters", "m1 full-file render (§4.1 lever: bar-span incremental cache)"),
        ("meters->serve", "t_meters", "t_prop", "analyze + wall + recovery renders"),
    ]
    print(f"ASK ANATOMY — {len(ask)} served ask runs")
    print(f"{'phase':<28}{'p50':>8}{'p90':>9}{'n':>5}   the lever")
    for name, a, b, lever in phases:
        ds = []
        for r in ask:
            ta, tb = r.get(a), r.get(b)
            if isinstance(ta, (int, float)) and isinstance(tb, (int, float)) and tb >= ta:
                ds.append(tb - ta)
        p50 = pctl(ds, 50)
        p90 = pctl(ds, 90)
        p50s = "-" if p50 is None else f"{p50:.1f}s"
        p90s = "-" if p90 is None else f"{p90:.1f}s"
        print(f"{name:<28}{p50s:>8}{p90s:>9}{len(ds):>5}   {lever}")
    return 0


def selftest():
    ok = 0
    def check(name, cond):
        nonlocal ok
        print(("  PASS " if cond else "  FAIL ") + name)
        if not cond:
            sys.exit(1)
        ok += 1
    with tempfile.TemporaryDirectory() as td:
        ev = os.path.join(td, "events.jsonl")
        # two runs on recycled id 1 (daemon rebirth) + one torn line + one slow ask run
        lines = [
            {"id": 1, "kind": "status", "t": 100.0, "song": "a"},
            {"id": 1, "kind": "activity", "t": 100.5, "song": "a"},
            {"id": 1, "kind": "proposal", "t": 130.0, "song": "a", "proposal": "_prop_a"},
            {"id": 1, "kind": "done", "t": 130.1, "song": "a", "stats": {"duration_s": 30.0}},
            {"id": 1, "kind": "status", "t": 200.0, "song": "b"},
            {"id": 1, "kind": "proposal_progress", "t": 201.0, "song": "b"},
            {"id": 1, "kind": "done", "t": 350.0, "song": "b", "stats": {"duration_s": 150.0}},
        ]
        with open(ev, "w") as f:
            for l in lines:
                f.write(json.dumps(l) + "\n")
            f.write('{"torn": \n')  # concurrent-append tear must not poison the court
        runs = cluster_runs(ev)
        check("id-recycle clusters to 2 runs", len(runs) == 2)
        check("durations from done.stats", [r["duration_s"] for r in runs] == [30.0, 150.0])
        check("first ink measured", abs(runs[0]["first_ink"] - 0.5) < 1e-9 and abs(runs[1]["first_ink"] - 1.0) < 1e-9)
        # classification: a = verb, b = ask; below MIN_N everything is UNMEASURED
        vrows = [("a", 100.0, "[verb] finish {}"), ("b", 200.0, "make it huge")]
        verb, ask = classify(runs, vrows)
        check("verb/ask split by prompt", len(verb) == 1 and len(ask) == 1 and verb[0]["song"] == "a")
        v = judge(runs, vrows)
        check("n<MIN_N stays UNMEASURED (never convicts thin evidence)",
              all(x["verdict"] == "UNMEASURED" for x in v.values()))
        # fatten the evidence: 6 fast asks PASS, then plant a regression -> BREACH
        fast = [{"id": 9, "kind": "status", "t": 1000.0 + i * 10, "song": f"s{i}"} for i in range(6)]
        with open(ev, "a") as f:
            for i, l in enumerate(fast):
                f.write(json.dumps(l) + "\n")
                f.write(json.dumps({"id": 9, "kind": "proposal", "t": l["t"] + 39, "song": l["song"],
                                    "proposal": "_prop_" + l["song"]}) + "\n")
                f.write(json.dumps({"id": 9, "kind": "done", "t": l["t"] + 40, "song": l["song"],
                                    "stats": {"duration_s": 40.0}}) + "\n")
        runs = cluster_runs(ev)
        vrows += [(f"s{i}", 1000.0 + i * 10, "an ask") for i in range(6)]
        v = judge(runs, vrows)
        check("6 fast asks -> ask_run_p50 PASS", v["ask_run_p50"]["verdict"] == "PASS")
        # a minority of slow runs must NOT flip a p50 court; a majority must
        with open(ev, "a") as f:
            for i in range(7):
                f.write(json.dumps({"id": 7, "kind": "status", "t": 2000.0 + i, "song": f"z{i}"}) + "\n")
                f.write(json.dumps({"id": 7, "kind": "proposal", "t": 2400.0 + i, "song": f"z{i}",
                                    "proposal": f"_prop_z{i}"}) + "\n")
                f.write(json.dumps({"id": 7, "kind": "done", "t": 2500.0 + i, "song": f"z{i}",
                                    "stats": {"duration_s": 500.0}}) + "\n")
        vrows += [(f"z{i}", 2000.0 + i, "another ask") for i in range(7)]
        v = judge(cluster_runs(ev), vrows)
        check("majority 500s regression convicts p50", v["ask_run_p50"]["verdict"] == "BREACH")
        check("percentile kernel exact", pctl([1, 2, 3, 4, 5], 50) == 3 and pctl([], 50) is None)
    print(f"SPEED COURT SELFTEST: {ok}/8 PASS")
    return 0 if ok == 8 else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    if "anatomy" in sys.argv:
        sys.exit(anatomy())
    sys.exit(report())
