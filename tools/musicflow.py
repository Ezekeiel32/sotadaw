#!/usr/bin/env python3
"""MUSICFLOWS (BEST_DAW_30 #25) — automation pipelines as first-class objects.

Chezy's founding spec, verbatim: "automate 'musicflows'". The CI/CD half of the
Claude-Code-for-music thesis: user-ownable pipelines that speak the SAME tool
language as the agent (steps execute agent/daw_mcp.py TOOLS directly, so the
receipt law, the prop fence, the wall law and song-name resolution all ride in
for free — a flow can never do what a tool couldn't).

  flows/<name>.flow.json
  {"name": "import_qc", "enabled": true,
   "trigger": {"kind": "on_import"},          # manual|on_import|on_accept|on_render
   "approval": "auto",                        # auto|prop (deck = prop alias, v2 wires the event)
   "steps": [
     {"tool": "render_song", "args": {"name": "$song", "max_bars": 16},
      "gate": {"metric": "last_render.clipped_samples", "op": "==", "val": 0}},
     {"tool": "analyze_wav", "args": {"path": "songs/$song.wav"}}]}

LAWS
  FLOWS PROPOSE — approval "auto" may run ONLY the read/render allowlist against
    the base; any mutating step requires approval "prop": the flow runs against
    a freshly-minted _prop_<song> copy (receipts cleared at birth, prop-lifetime
    law) and the base physically cannot change. A pending existing take is never
    clobbered (the flow refuses).
  A FAILING GATE HALTS LOUDLY — no silent partial pipelines; the run journal
    (flows/.runs/) records every step, gate and halt.
  TRIGGERS RESPECT THE KILL — SOTADAW_FLOWS=0 turns every trigger into a no-op.
  VALIDATION AT LOAD — unknown tool, auto-with-mutator, bad gate op: the flow
    refuses to load, loudly, before anything runs.

CLI
  musicflow.py list
  musicflow.py validate
  musicflow.py run <flow> --song <name> [--dry]
  musicflow.py run-trigger <kind> --song <name>
  musicflow.py --selftest        (pure checks only; flow_battery has the e2e)
"""
import json, os, shutil, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "agent"))

FLOWS = os.path.join(ROOT, "flows")
RUNS = os.path.join(FLOWS, ".runs")
SONGS = os.path.join(ROOT, "songs")
KINDS = ("manual", "on_import", "on_accept", "on_render")
OPS = {"==": lambda a, b: a == b, "!=": lambda a, b: a != b,
       ">=": lambda a, b: a >= b, "<=": lambda a, b: a <= b,
       ">": lambda a, b: a > b, "<": lambda a, b: a < b}
# read/render/report tools that never mutate song JSON — the "auto" surface
ALLOW_AUTO = {"get_song", "get_song_summary", "get_song_region", "render_song",
              "analyze_wav", "hear", "master_report", "finish_audit",
              "analyze_reference", "search_library", "session_recap",
              "list_plugin_params", "diff_ear",
              "release_pack"}   # writes a _release folder, never song state


class FlowError(Exception):
    pass


def _tools():
    import daw_mcp
    return daw_mcp


def load_flow(path):
    """Parse + validate one flow file. Raises FlowError with the reason."""
    try:
        f = json.load(open(path))
    except Exception as e:
        raise FlowError(f"{os.path.basename(path)}: unparseable ({e})")
    name = f.get("name") or os.path.basename(path).split(".flow")[0]
    f["name"] = name
    trig = (f.get("trigger") or {}).get("kind", "manual")
    if trig not in KINDS:
        raise FlowError(f"{name}: unknown trigger kind '{trig}' (want {KINDS})")
    appr = f.get("approval", "prop")
    if appr == "deck":
        appr = "prop"                    # v2 wires the deck event; prop = same safety
    if appr not in ("auto", "prop"):
        raise FlowError(f"{name}: unknown approval '{f.get('approval')}'")
    f["approval"] = appr
    steps = f.get("steps")
    if not isinstance(steps, list) or not steps:
        raise FlowError(f"{name}: steps must be a non-empty list")
    reg = _tools().TOOLS
    for i, s in enumerate(steps):
        t = s.get("tool")
        if t not in reg:
            raise FlowError(f"{name}: step {i + 1} unknown tool '{t}'")
        if appr == "auto" and t not in ALLOW_AUTO:
            raise FlowError(f"{name}: step {i + 1} tool '{t}' mutates — "
                            f"approval 'auto' allows only {sorted(ALLOW_AUTO)}")
        g = s.get("gate")
        if g and (g.get("op") not in OPS or "metric" not in g or "val" not in g):
            raise FlowError(f"{name}: step {i + 1} bad gate {g}")
    return f


def load_all():
    flows, errs = [], []
    if not os.path.isdir(FLOWS):
        return flows, errs
    for p in sorted(os.listdir(FLOWS)):
        if not p.endswith(".flow.json"):
            continue
        try:
            flows.append((load_flow(os.path.join(FLOWS, p)), p))
        except FlowError as e:
            errs.append(str(e))
    return flows, errs


def _subst(obj, song):
    if isinstance(obj, str):
        return obj.replace("$song", song)
    if isinstance(obj, dict):
        return {k: _subst(v, song) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_subst(v, song) for v in obj]
    return obj


def _metric(metric, last_wav, target_song, cache):
    """Resolve a gate metric: last_render.<analyze2 key> | song.<field>."""
    scope, _, key = metric.partition(".")
    if scope == "last_render":
        if not last_wav or not os.path.exists(last_wav):
            raise FlowError(f"gate wants {metric} but nothing rendered yet")
        if last_wav not in cache:
            from analyze2 import analyze
            cache[last_wav] = analyze(last_wav)
        if key not in cache[last_wav]:
            raise FlowError(f"gate metric '{key}' not in analysis "
                            f"(have: {sorted(cache[last_wav])[:12]}...)")
        return cache[last_wav][key]
    if scope == "song":
        doc = json.load(open(os.path.join(SONGS, f"{target_song}.json")))
        if key == "tracks_n":
            return len(doc.get("tracks", []))
        if key not in doc:
            raise FlowError(f"gate metric song.{key} not in song json")
        return doc[key]
    raise FlowError(f"gate metric scope '{scope}' unknown (last_render|song)")


def run_flow(flow, song, dry=False, quiet=False):
    """Execute one validated flow for one song. Returns the journal dict."""
    say = (lambda *a: None) if quiet else print
    dm = _tools()
    target = song
    journal = {"flow": flow["name"], "song": song, "when": time.strftime("%F %T"),
               "approval": flow["approval"], "steps": [], "ok": True}
    if flow["approval"] == "prop" and not dry:
        prop = f"_prop_{song}"
        pj = os.path.join(SONGS, f"{prop}.json")
        bj = os.path.join(SONGS, f"{song}.json")
        if not os.path.exists(bj):
            raise FlowError(f"no song '{song}'")
        if os.path.exists(pj):
            raise FlowError(f"a pending take exists for '{song}' — a flow never "
                            f"clobbers an unconsumed proposal (decide it first)")
        shutil.copyfile(bj, pj)
        import surgical
        surgical.clear_receipts(song)        # prop-lifetime law: fresh ledger at birth
        target = prop
        journal["prop"] = prop
        say(f"[flow] {flow['name']}: minted take {prop} (base untouched)")
    last_wav, acache = None, {}
    for i, s in enumerate(flow["steps"]):
        args = _subst(dict(s.get("args") or {}), target)
        rec = {"tool": s["tool"], "args": args}
        say(f"[flow] {flow['name']} step {i + 1}/{len(flow['steps'])}: {s['tool']}")
        t0 = time.time()
        if dry:
            rec["dry"] = True
            journal["steps"].append(rec)
            continue
        try:
            out = str(dm.TOOLS[s["tool"]][0](args))
        except Exception as e:
            out = f"TOOL EXCEPTION: {e}"
        rec["secs"] = round(time.time() - t0, 2)
        rec["result_head"] = out[:200]
        bad = out.startswith(("TOOL EXCEPTION", "no such")) or "FAILED" in out[:80]
        rec["ok"] = not bad
        if s["tool"] == "render_song" and not bad:
            nm = dm.resolve_song_name(args.get("name", target))
            last_wav = os.path.join(SONGS, f"{nm}.wav")
            acache.pop(last_wav, None)       # re-render invalidates the ears
        g = s.get("gate")
        if g and not bad:
            try:
                got = _metric(g["metric"], last_wav, target, acache)
                ok = OPS[g["op"]](got, g["val"])
            except FlowError as e:
                got, ok = f"({e})", False
            rec["gate"] = {"metric": g["metric"], "op": g["op"],
                           "want": g["val"], "got": got, "ok": ok}
            if not ok:
                journal["ok"] = False
                journal["halted"] = f"step {i + 1} gate: {g['metric']} {g['op']} " \
                                    f"{g['val']} but got {got}"
                journal["steps"].append(rec)
                say(f"[flow] {flow['name']} HALTED: {journal['halted']}")
                break
        journal["steps"].append(rec)
        if bad:
            journal["ok"] = False
            journal["halted"] = f"step {i + 1} {s['tool']} failed: {out[:120]}"
            say(f"[flow] {flow['name']} HALTED: {journal['halted']}")
            break
    if not dry:
        os.makedirs(RUNS, exist_ok=True)
        jp = os.path.join(RUNS, f"{flow['name']}_{time.strftime('%Y%m%d_%H%M%S')}.json")
        json.dump(journal, open(jp, "w"), indent=1)
        say(f"[flow] {flow['name']}: {'ok' if journal['ok'] else 'HALTED'} "
            f"-> {os.path.relpath(jp, ROOT)}")
    return journal


def run_trigger(kind, song, quiet=False):
    """Run every enabled flow whose trigger matches. Contained per-flow."""
    if os.environ.get("SOTADAW_FLOWS", "1") == "0":
        return []
    out = []
    flows, errs = load_all()
    for e in errs:
        print(f"[flow] SKIP invalid: {e}", file=sys.stderr)
    for f, _p in flows:
        if not f.get("enabled", True) or (f.get("trigger") or {}).get("kind") != kind:
            continue
        try:
            out.append(run_flow(f, song, quiet=quiet))
        except FlowError as e:
            print(f"[flow] {f['name']} refused: {e}", file=sys.stderr)
            out.append({"flow": f["name"], "song": song, "ok": False,
                        "halted": str(e), "steps": []})
    return out


def selftest():
    """Pure checks (no renders — flow_battery owns the e2e)."""
    ok = True

    def chk(tag, cond):
        nonlocal ok
        print(f"  {'ok' if cond else 'XX'} {tag}")
        ok = ok and cond
    chk("subst", _subst({"a": ["$song", 1]}, "x") == {"a": ["x", 1]})
    for op, a, b, want in (("==", 0, 0, True), (">=", -13.9, -14, True),
                           ("<", 2, 2, False)):
        chk(f"op {op}", OPS[op](a, b) is want)
    import tempfile
    bad = {"name": "t", "steps": [{"tool": "write_song", "args": {}}],
           "approval": "auto", "trigger": {"kind": "manual"}}
    with tempfile.NamedTemporaryFile("w", suffix=".flow.json", delete=False) as f:
        json.dump(bad, f)
    try:
        load_flow(f.name)
        chk("auto+mutator refused", False)
    except FlowError:
        chk("auto+mutator refused", True)
    os.unlink(f.name)
    return 0 if ok else 1


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["list", "validate", "run", "run-trigger"],
                    nargs="?", default="list")
    ap.add_argument("what", nargs="?")
    ap.add_argument("--song")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.cmd in ("list", "validate"):
        flows, errs = load_all()
        for f, p in flows:
            print(f"  {f['name']:<20} {f['trigger']['kind']:<10} "
                  f"{f['approval']:<5} {len(f['steps'])} steps "
                  f"{'ENABLED' if f.get('enabled', True) else 'disabled'}  ({p})")
        for e in errs:
            print(f"  INVALID: {e}")
        return 1 if errs and a.cmd == "validate" else 0
    if not a.song:
        print("--song required", file=sys.stderr)
        return 2
    if a.cmd == "run":
        flows, _ = load_all()
        f = next((f for f, _p in flows if f["name"] == a.what), None)
        if not f:
            print(f"no flow '{a.what}' (have: {[x[0]['name'] for x in flows]})",
                  file=sys.stderr)
            return 2
        j = run_flow(f, a.song, dry=a.dry)
        return 0 if j["ok"] else 1
    if a.cmd == "run-trigger":
        if a.what not in KINDS:
            print(f"unknown trigger '{a.what}'", file=sys.stderr)
            return 2
        js = run_trigger(a.what, a.song)
        return 0 if all(j["ok"] for j in js) else 1


if __name__ == "__main__":
    sys.exit(main())
