#!/usr/bin/env python3
"""FLOW BATTERY — the MUSICFLOWS guardian (BEST_DAW_30 #25).

Proves the laws end-to-end through the real kernel + real daw_mcp tools + one
real m1 render:

  VALIDATION    unknown tool / auto-with-mutator / bad gate op refuse at load
  E2E GREEN     the SHIPPED import_qc flow runs a scratch song clean (render ->
                clip gate -> analyze -> finish_audit), journal written
  GATE HALTS    an impossible gate halts LOUDLY (rc 1, journal.halted)
  PROP LAW      a mutating flow runs against a minted _prop_ copy; the base is
                byte-identical after; a pending take is never clobbered
  TRIGGER LAW   kind filter + enabled flag + SOTADAW_FLOWS=0 kill all honored

Run: .venv/bin/python tools/flow_battery.py
"""
import json, os, shutil, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import musicflow as MF

SONGS = os.path.join(ROOT, "songs")
SCRATCH = "_flowbat"
fails = []


def check(tag, ok, detail=""):
    print(f"  {'ok' if ok else 'XX'} {tag} {detail}")
    if not ok:
        fails.append(tag)


def scratch_song():
    song = {"bpm": 120, "lengthBars": 2, "key": "C", "tracks": [
        {"name": "kick", "gainDb": -6.0, "pan": 0.0,
         "source": {"kind": "faust", "id": "kick_punch", "params": {}},
         "notes": [{"start": float(b), "len": 0.5, "pitch": 36, "vel": 0.8}
                   for b in range(8)]}]}
    json.dump(song, open(os.path.join(SONGS, f"{SCRATCH}.json"), "w"), indent=1)
    return song


def cleanup():
    for suf in (".json", ".wav"):
        for nm in (SCRATCH, f"_prop_{SCRATCH}"):
            p = os.path.join(SONGS, nm + suf)
            if os.path.exists(p):
                os.remove(p)
    if os.path.isdir(MF.RUNS):
        for p in os.listdir(MF.RUNS):
            j = os.path.join(MF.RUNS, p)
            try:
                if json.load(open(j)).get("song") == SCRATCH:
                    os.remove(j)
            except Exception:
                pass


def main():
    # ---- validation laws (pure) ----
    def bad_flow(d):
        with tempfile.NamedTemporaryFile("w", suffix=".flow.json", delete=False) as f:
            json.dump(d, f)
        try:
            MF.load_flow(f.name)
            return None
        except MF.FlowError as e:
            return str(e)
        finally:
            os.unlink(f.name)
    check("unknown tool refused",
          bad_flow({"steps": [{"tool": "no_such_tool"}]}) is not None)
    check("auto+mutator refused",
          "mutates" in (bad_flow({"approval": "auto",
                                  "steps": [{"tool": "update_track"}]}) or ""))
    check("bad gate op refused",
          bad_flow({"steps": [{"tool": "get_song",
                               "gate": {"metric": "song.bpm", "op": "~=",
                                        "val": 1}}]}) is not None)

    # ---- E2E: the SHIPPED import_qc flow on a real scratch song ----
    scratch_song()
    flows, errs = MF.load_all()
    check("shipped flows all valid", not errs, str(errs))
    iq = next((f for f, _ in flows if f["name"] == "import_qc"), None)
    check("import_qc shipped", iq is not None)
    j = MF.run_flow(iq, SCRATCH, quiet=True)
    check("import_qc runs GREEN", j["ok"],
          j.get("halted", "") or f"{len(j['steps'])} steps")
    check("clip gate evaluated",
          any(s.get("gate", {}).get("metric") == "last_render.clipped_samples"
              and s["gate"]["ok"] for s in j["steps"]))
    check("journal written", any(json.load(open(os.path.join(MF.RUNS, p))).get("song")
                                 == SCRATCH for p in os.listdir(MF.RUNS)))

    # ---- gate HALTS loudly ----
    halt = {"name": "_fb_halt", "trigger": {"kind": "manual"}, "approval": "auto",
            "steps": [{"tool": "render_song", "args": {"name": "$song", "max_bars": 2},
                       "gate": {"metric": "last_render.clipped_samples",
                                "op": "==", "val": -1}},
                      {"tool": "analyze_wav", "args": {"path": "songs/$song.wav"}}]}
    j2 = MF.run_flow(MF.load_flow(_tmp(halt)), SCRATCH, quiet=True)
    check("impossible gate HALTS", not j2["ok"] and "gate" in j2.get("halted", ""),
          j2.get("halted", ""))
    check("halt stops the pipeline", len(j2["steps"]) == 1)

    # ---- PROP LAW: mutating flow leaves the base byte-identical ----
    base_bytes = open(os.path.join(SONGS, f"{SCRATCH}.json"), "rb").read()
    mut = {"name": "_fb_mut", "trigger": {"kind": "manual"}, "approval": "prop",
           "steps": [{"tool": "update_track",
                      "args": {"song": "$song", "track": "kick", "gainDb": -9.0}}]}
    j3 = MF.run_flow(MF.load_flow(_tmp(mut)), SCRATCH, quiet=True)
    check("prop flow runs GREEN", j3["ok"], j3.get("halted", ""))
    check("base byte-identical after mutating flow",
          open(os.path.join(SONGS, f"{SCRATCH}.json"), "rb").read() == base_bytes)
    pj = os.path.join(SONGS, f"_prop_{SCRATCH}.json")
    check("take minted", os.path.exists(pj))
    if os.path.exists(pj):
        pd = json.load(open(pj))
        check("edit landed ON THE TAKE",
              pd["tracks"][0]["gainDb"] == -9.0, str(pd["tracks"][0]["gainDb"]))
    try:
        MF.run_flow(MF.load_flow(_tmp(mut)), SCRATCH, quiet=True)
        check("pending take never clobbered", False)
    except MF.FlowError as e:
        check("pending take never clobbered", "clobber" in str(e), str(e)[:60])

    # ---- TRIGGER LAW (isolated flows dir) ----
    keep = MF.FLOWS
    tmpd = tempfile.mkdtemp(prefix="fb_flows_")
    MF.FLOWS = tmpd
    try:
        json.dump({"name": "t1", "trigger": {"kind": "on_accept"}, "approval": "auto",
                   "steps": [{"tool": "get_song", "args": {"song": "$song"}}]},
                  open(os.path.join(tmpd, "t1.flow.json"), "w"))
        json.dump({"name": "t2", "enabled": False,
                   "trigger": {"kind": "on_accept"}, "approval": "auto",
                   "steps": [{"tool": "get_song", "args": {"song": "$song"}}]},
                  open(os.path.join(tmpd, "t2.flow.json"), "w"))
        js = MF.run_trigger("on_accept", SCRATCH, quiet=True)
        check("trigger kind matches + disabled skipped",
              [x["flow"] for x in js] == ["t1"], str([x["flow"] for x in js]))
        check("t1 green through the trigger", js and js[0]["ok"])
        js2 = MF.run_trigger("on_import", SCRATCH, quiet=True)
        check("non-matching trigger runs nothing", js2 == [])
        os.environ["SOTADAW_FLOWS"] = "0"
        js3 = MF.run_trigger("on_accept", SCRATCH, quiet=True)
        check("SOTADAW_FLOWS=0 kills triggers", js3 == [])
    finally:
        os.environ.pop("SOTADAW_FLOWS", None)
        MF.FLOWS = keep
        shutil.rmtree(tmpd, ignore_errors=True)

    cleanup()
    print(f"flow battery: {'clean' if not fails else 'RED ' + str(fails)}")
    return 0 if not fails else 1


def _tmp(d):
    f = tempfile.NamedTemporaryFile("w", suffix=".flow.json", delete=False)
    json.dump(d, f)
    f.close()
    return f.name


if __name__ == "__main__":
    sys.exit(main())
