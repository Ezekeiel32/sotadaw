#!/usr/bin/env python3
"""A7 — THE REGRESSION COURT (docs/THE_PHYSICS.md §6; law E8; rides E1 THE SEAL).

Every engine-binary change re-renders the golden corpus and nulls against sealed
references. Under THE SEAL the reference is just a sha256 manifest (tiny, git-
committable): a matching sha IS a byte-null. A mismatch re-nulls the actual wavs
to QUANTIFY the residual (dBFS) and auto-drafts a ledger entry naming the song,
the delta, and the binary md5s — so "the change sounds" is a number with a
suspect, not a vibe. Two-machine corollary (E8): LOQ gold vs Inspiron build must
sha-match or the residual measures the cross-compile drift.

usage:
  engine_null_ci.py seal [--corpus a.json,b.json,...]   establish gold (manifest + wavs)
  engine_null_ci.py check [--corpus ...]                re-render, null vs gold, draft ledger
  engine_null_ci.py --selftest [--keep]                 seal -> clean check -> planted 0.1dB
Manifest: eval/null_ci_gold.json (committed). Gold wavs: songs/.null_ci_gold/ (gitignored).
Ledger drafts: eval/null_ci_ledger.md (appended). Exit 0 = court clean.
"""
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "songs")
M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")
GOLD_WAVS = os.path.join(SONGS, ".null_ci_gold")
MANIFEST = os.path.join(ROOT, "eval", "null_ci_gold.json")
LEDGER = os.path.join(ROOT, "eval", "null_ci_ledger.md")

# One per family (the E8 corpus). Only those present on this box are used; the
# manifest records which — a missing song is a skip, not a failure.
DEFAULT_CORPUS = ["eval_funk", "eval_gospel", "eval_ukgarage", "demo_track",
                  "chezy_song", "psy_test"]


def _m1_md5():
    return hashlib.md5(open(M1, "rb").read()).hexdigest()


def _git_head():
    try:
        return subprocess.check_output(["git", "-C", ROOT, "rev-parse", "--short", "HEAD"],
                                       text=True).strip()
    except Exception:
        return "?"


def _render(song_json, out_wav):
    r = subprocess.run([M1, "render", song_json, out_wav], capture_output=True,
                       text=True, timeout=900)
    out = r.stdout + r.stderr
    if "ok=1" not in out:
        return None
    m = re.search(r"render_sha256=([0-9a-f]{64})", out)
    if m:
        return m.group(1)
    h = hashlib.sha256()
    with open(out_wav, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def _residual_dbfs(a_wav, b_wav):
    try:
        import numpy as np
        import soundfile as sf
        a = sf.read(a_wav, always_2d=True, dtype="float64")[0]
        b = sf.read(b_wav, always_2d=True, dtype="float64")[0]
        n = min(len(a), len(b))
        ch = min(a.shape[1], b.shape[1])
        r = (a[:n, :ch] - b[:n, :ch]).mean(axis=1)
        rms = float(np.sqrt(np.mean(r ** 2))) if n else 0.0
        return round(20 * math.log10(rms), 2) if rms > 1e-10 else -200.0, \
            int(len(a) - len(b))
    except Exception as e:
        return None, str(e)


def _corpus(argv):
    if "--corpus" in argv:
        names = argv[argv.index("--corpus") + 1].split(",")
    else:
        names = DEFAULT_CORPUS
    return [n for n in names
            if os.path.exists(os.path.join(SONGS, f"{n}.json"))]


def _quarantine_state():
    """Quarantined plugins render BYPASSED — a different quarantine at check
    time vs seal time makes a vst3-bearing corpus song 'sound' with no engine
    change at all (demo_track, 2026-07-10: gold sealed under a stale Surge
    crash-quarantine read -14.56 dBFS residual once the quarantine healed)."""
    try:
        q = json.load(open(os.path.expanduser(
            "~/.config/sotadaw/plugin_quarantine.json")))
        return sorted(q) if isinstance(q, list) else q
    except Exception:
        return []


def seal(argv, gold_dir=GOLD_WAVS, manifest=MANIFEST):
    os.makedirs(gold_dir, exist_ok=True)
    os.makedirs(os.path.dirname(manifest), exist_ok=True)
    entries = {}
    for name in _corpus(argv):
        sj = os.path.join(SONGS, f"{name}.json")
        gw = os.path.join(gold_dir, f"{name}.wav")
        sha = _render(sj, gw)
        if sha is None:
            print(f"  [skip] {name}: render failed")
            continue
        entries[name] = {"sha256": sha, "bytes": os.path.getsize(gw)}
        print(f"  [gold] {name}  {sha[:16]}")
    doc = {"m1_md5": _m1_md5(), "git_head": _git_head(),
           "render_epoch": os.environ.get("SOTADAW_RENDER_EPOCH", "0"),
           "plugin_quarantine": _quarantine_state(),
           "corpus": entries}
    json.dump(doc, open(manifest, "w"), indent=1)
    print(f"[seal] {len(entries)} golden refs -> {manifest}")
    return doc


def check(argv, gold_dir=GOLD_WAVS, manifest=MANIFEST, draft=True):
    if not os.path.exists(manifest):
        print("[check] no manifest — run 'seal' first")
        return {"error": "no manifest"}
    gold = json.load(open(manifest))
    cur_md5 = _m1_md5()
    same_binary = cur_md5 == gold["m1_md5"]
    if "plugin_quarantine" in gold and gold["plugin_quarantine"] != _quarantine_state():
        print(f"  [warn] quarantine drift: gold sealed with {gold['plugin_quarantine']}, "
              f"now {_quarantine_state()} — vst3-bearing songs will legitimately sound")
    results, offenders = {}, []
    tmp = os.path.join(SONGS, "_nullci_cur.wav")
    for name, ref in gold["corpus"].items():
        sj = os.path.join(SONGS, f"{name}.json")
        if not os.path.exists(sj):
            results[name] = {"status": "song-missing"}
            continue
        sha = _render(sj, tmp)
        if sha is None:
            results[name] = {"status": "render-failed"}
            offenders.append(name)
            continue
        if sha == ref["sha256"]:
            results[name] = {"status": "NULL", "sha_match": True}
        else:
            gw = os.path.join(gold_dir, f"{name}.wav")
            resid, ln = (_residual_dbfs(gw, tmp) if os.path.exists(gw)
                         else (None, "gold-wav-absent"))
            status = "SOUNDS" if (resid is None or resid > -120.0) else "NULL(sub-120)"
            results[name] = {"status": status, "sha_match": False,
                             "residual_dbfs": resid, "len_delta": ln,
                             "cur_sha": sha[:16], "ref_sha": ref["sha256"][:16]}
            if status == "SOUNDS":
                offenders.append(name)
    if os.path.exists(tmp):
        os.remove(tmp)
    clean = not offenders
    verdict = {"pass": clean, "same_binary": same_binary,
               "gold_head": gold["git_head"], "gold_md5": gold["m1_md5"][:12],
               "cur_head": _git_head(), "cur_md5": cur_md5[:12],
               "offenders": offenders, "results": results}
    if offenders and draft:
        _draft_ledger(verdict, gold)
    for name, r in results.items():
        print(f"  {r['status']:14s} {name}"
              + (f"  resid {r.get('residual_dbfs')} dBFS" if r.get("residual_dbfs") is not None else ""))
    print(f"[check] {'CLEAN' if clean else f'{len(offenders)} OFFENDER(S)'} "
          f"| gold {gold['git_head']}/{gold['m1_md5'][:8]} vs cur {_git_head()}/{cur_md5[:8]}"
          f" | same_binary={same_binary}")
    return verdict


def _draft_ledger(verdict, gold):
    os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
    lines = [f"\n## NULL-CI NON-NULL — gold {verdict['gold_head']} vs cur {verdict['cur_head']}\n",
             f"- binaries: gold md5 {verdict['gold_md5']} vs cur md5 {verdict['cur_md5']} "
             f"(same_binary={verdict['same_binary']})\n",
             f"- suspect commit range: `git log {verdict['gold_head']}..{verdict['cur_head']}`\n"]
    for name in verdict["offenders"]:
        r = verdict["results"][name]
        lines.append(f"- **{name}**: residual {r.get('residual_dbfs')} dBFS "
                     f"(cur {r.get('cur_sha')} vs ref {r.get('ref_sha')}) — the change SOUNDS.\n")
    lines.append("- E8: residual > -120 dBFS means the engine's audio moved; explain why or revert.\n")
    with open(LEDGER, "a") as f:
        f.writelines(lines)
    print(f"[ledger] drafted {len(verdict['offenders'])} entry(ies) -> {LEDGER}")


def selftest(keep=False):
    """seal -> clean check nulls -> a planted +0.1 dB render is CAUGHT + ledgered."""
    checks, fails = [], []

    def ck(nm, ok, detail=""):
        checks.append({"name": nm, "ok": bool(ok), "detail": detail})
        if not ok:
            fails.append(nm)
        print(("  ok " if ok else "FAIL ") + f"{nm}  {detail}", flush=True)

    gd = os.path.join(SONGS, "_nullci_selftest_gold")
    mf = os.path.join(SONGS, "_nullci_selftest_manifest.json")
    led_bak = None
    if os.path.exists(LEDGER):
        led_bak = LEDGER + ".bak"
        shutil.copy(LEDGER, led_bak)
    try:
        corpus = [n for n in ("eval_funk", "psy_test")
                  if os.path.exists(os.path.join(SONGS, f"{n}.json"))][:1] or ["eval_funk"]
        argv = ["--corpus", ",".join(corpus)]
        g = seal(argv, gold_dir=gd, manifest=mf)
        ck("seal produced gold refs", bool(g["corpus"]), f"{len(g['corpus'])} songs")

        v = check(argv, gold_dir=gd, manifest=mf, draft=False)
        ck("clean re-render NULLs (sha-match under the seal)",
           v["pass"] and all(r.get("sha_match") for r in v["results"].values()
                             if r.get("status") == "NULL"),
           f"offenders {v['offenders']}")

        # PLANT: a song whose render differs by +0.1 dB master trim — the signature
        # of a subtle engine regression. Overwrite one corpus song's JSON, re-check.
        name = corpus[0]
        sj = os.path.join(SONGS, f"{name}.json")
        orig = open(sj).read()
        song = json.loads(orig)
        song.setdefault("master", []).append({"id": "fx_trim", "params": {"level": -0.1}})
        open(sj, "w").write(json.dumps(song, indent=1))
        try:
            led_before = os.path.getsize(LEDGER) if os.path.exists(LEDGER) else 0
            v2 = check(argv, gold_dir=gd, manifest=mf, draft=True)
            led_after = os.path.getsize(LEDGER) if os.path.exists(LEDGER) else 0
            r = v2["results"][name]
            ck("planted +0.1 dB is CAUGHT (residual > -120, status SOUNDS)",
               name in v2["offenders"] and r["status"] == "SOUNDS",
               f"residual {r.get('residual_dbfs')} dBFS")
            ck("the residual is ~-0.1dB-order (not a full break, not a false null)",
               r.get("residual_dbfs") is not None and -60 < r["residual_dbfs"] < -10,
               f"{r.get('residual_dbfs')} dBFS")
            ck("ledger auto-drafted the offender", led_after > led_before
               and name in open(LEDGER).read(), f"+{led_after - led_before} bytes")
        finally:
            open(sj, "w").write(orig)          # restore the corpus song verbatim
        result = {"pass": not fails, "failing": fails, "checks": checks}
    finally:
        shutil.rmtree(gd, ignore_errors=True)
        for p in (mf, os.path.join(SONGS, "_nullci_cur.wav")):
            if os.path.exists(p):
                os.remove(p)
        if led_bak and not keep:                # restore ledger (drop selftest drafts)
            shutil.move(led_bak, LEDGER)
        elif led_bak:
            os.remove(led_bak)
    print("NULLCI_JSON " + json.dumps(result))
    print(f"\n== ENGINE NULL-CI: {len(checks) - len(fails)} pass / {len(fails)} fail ==")
    return 0 if not fails else 1


def main():
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    if a[0] == "--selftest":
        return selftest("--keep" in a)
    if a[0] == "seal":
        seal(a[1:])
        return 0
    if a[0] == "check":
        v = check(a[1:])
        return 0 if v.get("pass") else 1
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
