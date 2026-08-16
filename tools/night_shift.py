#!/usr/bin/env python3
"""THE NIGHT SHIFT (A6-T1, docs/SPEC_TRANSCENDENCE.md) — the self-improvement
crank, closed. While the studio sleeps, the DAW converts the day's exhaust
into permanent state and drafts what the evidence says is missing.

JOBS (each fail-open, each one honest line in the report):
  verdict_ingest  — telemetry -> the knowledge graph (V35 crank, idempotent)
  gold_growth     — qualifying accepts bank into library/gold (auto-grow lane)
  constitution    — the artist model re-distills (user lines sacred inside)
  reject_pulse    — pure: window the recent rejects, bucket the WHYs
  drafter         — THE LAW DRAFTER v1: a repeated complaint bucket or a
                    collapsing genre accept-rate DRAFTS A FINDING
                    (telemetry/findings.jsonl) — machine-drafted, HUMAN-
                    ACCEPTED; the night shift lands DATA, never law
  report          — THE MORNING REPORT: <=2K chars, deltas-first, honest
                    empties (agent/ipc/morning_report.txt)

GUARDS: the stand-down gate (a LIVE user refuses the shift; the cron line
wraps in tools/gated.sh as a belt), SANDBOX-free by construction (state and
findings live under telemetry/, gitignored), the guardian suite is NOT run
here by default (--suite opts in; suites follow the collab claim law).

CLI: --run (default) | --report | --install-cron | --suite | --force
"""
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENV_PY = os.path.join(ROOT, ".venv", "bin", "python")
STATE_REL = os.path.join("telemetry", ".night_shift_state.json")
FINDINGS_REL = os.path.join("telemetry", "findings.jsonl")
REPORT_REL = os.path.join("agent", "ipc", "morning_report.txt")

WINDOW_S = 7 * 86400
# complaint buckets already covered by a standing court: a storm there is a
# CALIBRATION question; an uncovered bucket is a MISSING PRIMITIVE (the
# expressibility-triage law) — both draft, the kind differs.
_COVERED = {"bright": "sound/tilt courts", "dark": "sound/tilt courts",
            "groove": "pocket court", "key": "key court",
            "level": "loudness pass", "empty": "flow/structure courts",
            "busy": "structure court", "vocal": "vocal court",
            "length": "instruction court"}


def _bucket(why):
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    try:
        import artist_model
        return artist_model._bucket(why)
    except Exception:
        return "other"


# ------------------------------------------------------------- pure organs

def pulse(root, now=None):
    """Window the last 7 days of verdicts -> counts + WHY buckets + per-genre
    accept rates. Pure read."""
    now = now or time.time()
    tel = os.path.join(root, "telemetry", "proposals.jsonl")
    acc = rej = 0
    buckets, genres = {}, {}
    if os.path.exists(tel):
        for ln in open(tel, errors="replace"):
            try:
                r = json.loads(ln)
            except Exception:
                continue
            if not isinstance(r, dict) or "accepted" not in r:
                continue
            if now - float(r.get("t", 0)) > WINDOW_S:
                continue
            g = str(r.get("genre") or "").lower()
            ga, gr = genres.get(g, (0, 0))
            if r.get("accepted"):
                acc += 1
                genres[g] = (ga + 1, gr)
            else:
                rej += 1
                genres[g] = (ga, gr + 1)
                why = str(r.get("note") or "").strip()
                if why:
                    b = _bucket(why)
                    buckets.setdefault(b, []).append(why[:70])
    return {"accepts": acc, "rejects": rej, "buckets": buckets,
            "genres": genres}


def draft_findings(p, root, now=None):
    """THE LAW DRAFTER v1 — trip rules -> finding rows. Dedupes against
    findings already drafted for the same subject in the window."""
    now = now or time.time()
    path = os.path.join(root, FINDINGS_REL)
    seen = set()
    if os.path.exists(path):
        for ln in open(path, errors="replace"):
            try:
                r = json.loads(ln)
                if now - float(r.get("t", 0)) <= WINDOW_S:
                    seen.add((r.get("kind"), r.get("subject")))
            except Exception:
                continue
    drafts = []
    for b, quotes in sorted(p["buckets"].items()):
        if len(quotes) < 3 or ("bucket_storm", b) in seen:
            continue
        covered = _COVERED.get(b)
        drafts.append({
            "t": round(now, 1), "kind": "bucket_storm", "subject": b,
            "evidence": quotes[:5],
            "suggestion": (f"'{b}' rejected {len(quotes)}x this week though "
                           f"{covered} stands — a CALIBRATION case: wolf the "
                           "court's floors against these takes" if covered
                           else f"'{b}' rejected {len(quotes)}x with NO "
                           "standing court — the expressibility-triage law "
                           "says missing PRIMITIVE: draft kernel->court->"
                           "heal->battery")})
    for g, (ga, gr) in sorted(p["genres"].items()):
        tot = ga + gr
        if g and tot >= 4 and ga / tot < 0.4 and ("accept_collapse", g) not in seen:
            drafts.append({
                "t": round(now, 1), "kind": "accept_collapse", "subject": g,
                "evidence": [f"{ga}/{tot} accepted this week"],
                "suggestion": (f"{g} accept-rate collapsed to {ga}/{tot} — "
                               "autopsy the rejects (courts on the archived "
                               "takes), check gold/skill freshness for the "
                               "genre, ask for WHYs")})
    if drafts:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a") as f:
            for d in drafts:
                f.write(json.dumps(d) + "\n")
    return drafts


def render_report(results, p, drafts, prev, now=None):
    """<=2K chars, deltas first, honest empties."""
    now = now or time.time()
    lines = ["MORNING REPORT — " + time.strftime("%Y-%m-%d %H:%M",
                                                 time.localtime(now))]
    d_acc = p["accepts"] - int(prev.get("accepts", 0))
    lines.append(f"verdicts (7d): {p['accepts']} accepts / {p['rejects']} "
                 f"rejects" + (f" ({'+' if d_acc >= 0 else ''}{d_acc} accepts "
                               "since last shift)" if prev else ""))
    if p["buckets"]:
        lines.append("complaints: " + ", ".join(
            f"{b} x{len(q)}" for b, q in sorted(p["buckets"].items())))
    else:
        lines.append("complaints: none typed this week (the WHY strip is "
                     "quiet — silent rejects carry no lesson)")
    for name, note in results:
        lines.append(f"{name}: {note}")
    if drafts:
        lines.append(f"DRAFTED {len(drafts)} finding(s) -> telemetry/"
                     "findings.jsonl (machine-drafted, yours to accept):")
        for d in drafts[:4]:
            lines.append(f"  - [{d['kind']}] {d['subject']}: "
                         + d["suggestion"][:110])
    else:
        lines.append("drafted findings: none (no trip rule fired — quiet is "
                     "honest)")
    out = "\n".join(lines)
    return out[:2000]


# ------------------------------------------------------------ the shift

def _sub(job, cmd, timeout):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True,
                           timeout=timeout, cwd=ROOT)
        tail = (r.stdout + r.stderr).strip().splitlines()
        return (job, ("ok — " + tail[-1][:90]) if r.returncode == 0
                else f"rc={r.returncode} — {(tail or ['?'])[-1][:90]}")
    except Exception as e:
        return (job, f"skipped ({type(e).__name__})")


def run_shift(root=None, now=None, jobs=None, force=False, suite=False):
    root = root or ROOT
    now = now or time.time()
    if not force:
        try:
            rc = subprocess.run([sys.executable,
                                 os.path.join(ROOT, "tools", "user_live.py")],
                                capture_output=True, timeout=20).returncode
            if rc == 0:
                return {"refused": "user LIVE (stand-down gate)"}
        except Exception:
            pass
    py = VENV_PY if os.path.exists(VENV_PY) else sys.executable
    results = []
    if jobs is None:
        jobs = [
            ("verdict_ingest", [py, os.path.join(ROOT, "tools",
                                                 "kg_ingest_telemetry.py")], 180),
            ("gold_growth", [py, os.path.join(ROOT, "tools", "gold_bank.py"),
                             "ingest-accepts"], 300),
        ]
        if suite:
            jobs.append(("suite", ["bash", os.path.join(
                ROOT, "tools", "ghost_suite.sh"), "--polite"], 3600))
    for job, cmd, to in jobs:
        results.append(_sub(job, cmd, to))
    try:
        sys.path.insert(0, os.path.join(root, "tools"))
        import artist_model
        r = artist_model.distill_and_write(root, now=now)
        results.append(("constitution",
                        f"ok — {r['laws']} laws, {r['user_lines']} user lines"))
    except Exception as e:
        results.append(("constitution", f"skipped ({type(e).__name__})"))
    p = pulse(root, now)
    drafts = draft_findings(p, root, now)
    spath = os.path.join(root, STATE_REL)
    prev = {}
    if os.path.exists(spath):
        try:
            prev = json.load(open(spath))
        except Exception:
            prev = {}
    report = render_report(results, p, drafts, prev, now)
    rpath = os.path.join(root, REPORT_REL)
    os.makedirs(os.path.dirname(rpath), exist_ok=True)
    tmp = rpath + ".tmp"
    open(tmp, "w").write(report + "\n")
    os.replace(tmp, rpath)
    os.makedirs(os.path.dirname(spath), exist_ok=True)
    tmp2 = spath + ".tmp"
    json.dump({"t": now, "accepts": p["accepts"], "rejects": p["rejects"]},
              open(tmp2, "w"))
    os.replace(tmp2, spath)
    return {"report": report, "drafts": len(drafts), "path": rpath}


def install_cron():
    line = (f"17 4 * * * cd {ROOT} && tools/gated.sh .venv/bin/python "
            f"tools/night_shift.py --run >> telemetry/night_shift.log 2>&1")
    cur = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    existing = cur.stdout if cur.returncode == 0 else ""
    if "night_shift.py" in existing:
        return "cron already installed"
    new = existing.rstrip() + ("\n" if existing.strip() else "") + line + "\n"
    r = subprocess.run(["crontab", "-"], input=new, text=True,
                       capture_output=True)
    return "cron installed (04:17 daily, gated)" if r.returncode == 0 \
        else f"crontab failed: {r.stderr.strip()}"


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--install-cron" in a:
        print(install_cron())
    elif "--report" in a:
        p = os.path.join(ROOT, REPORT_REL)
        print(open(p).read() if os.path.exists(p) else "(no report yet)")
    else:
        out = run_shift(force="--force" in a, suite="--suite" in a)
        print(out.get("report") or json.dumps(out))
