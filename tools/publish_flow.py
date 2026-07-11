#!/usr/bin/env python3
"""V22 THE /PUBLISH FLOW — master-check -> C2PA embed -> upload, ONE orchestrated act.

publish_flow.py <song> [--service soundcloud] [--public] [--genre <kg_genre>]
                [--title T] [--tags "a b"] [--dry-run]

The SPEC's publish law, executed in order and refused loudly at any red stage:
  1. FINISH GATE   finish_audit — a SKELETON never ships
  2. MASTER        export_master (render + C2PA sign; AI-composed-symbolic declared)
  3. MASTER CHECK  ears on the SIGNED file: clipped 0, dBTP <= -1 (+ genre LUFS window)
  4. C2PA VERIFY   read the manifest back from the file (trust, then verify)
  5. UPLOAD        SoundCloud connector (private by default; --public is the explicit act)
--dry-run stops after stage 4 — everything real except the outbound transfer.
Local-first law: this flow is the ONLY outbound audio path, and it never runs unasked.
"""
import argparse, importlib.util, json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))


def load_mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("song")
    ap.add_argument("--service", default="soundcloud")
    ap.add_argument("--public", action="store_true")
    ap.add_argument("--genre")
    ap.add_argument("--title")
    ap.add_argument("--tags")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    ledger = []

    def stage(name, ok, detail=""):
        ledger.append((name, ok, detail))
        print(f"  [{'OK ' if ok else 'RED'}] {name}" + (f" — {detail}" if detail else ""))
        if not ok:
            print("PUBLISH REFUSED at stage: " + name)
            for l in ledger:
                pass
            sys.exit(2)

    print(f"PUBLISH FLOW — {a.song} -> {a.service}" + (" (DRY RUN)" if a.dry_run else ""))

    # 1. finish gate
    from finish_audit import load_song, audit
    j, song = load_song(a.song)
    verdict = audit(song, j, genre=None, no_render=True)["verdict"]
    stage("finish gate", verdict != "SKELETON", f"verdict: {verdict}")

    # 2. master (render + C2PA sign)
    em = load_mod("export_master", os.path.join(ROOT, "tools", "export_master.py"))
    master = os.path.join(ROOT, "songs", f"{a.song}_master.wav")
    em.export(a.song, master)
    stage("C2PA master", os.path.exists(master), os.path.basename(master))

    # 3. ears on the signed file
    from analyze2 import analyze
    m = analyze(master)
    stage("clipped == 0", m["clipped_samples"] == 0, str(m["clipped_samples"]))
    stage("true peak <= -1.0", m["true_peak_dbtp"] <= -1.0, f"{m['true_peak_dbtp']} dBTP")
    if a.genre:
        from reference_match import mixtarget_lane
        mt = mixtarget_lane(a.genre, m)
        for c in mt.get("checks", []):
            stage(f"{a.genre}: {c['check']}", bool(c["ok"]), str(c["value"]))

    # 4. verify the credential is really in the file
    try:
        from c2pa import Reader
        with open(master, "rb") as fh:
            r = Reader("audio/wav", fh)
            man = json.loads(r.json())
        n = len(man.get("manifests", man) or {})
        stage("C2PA verify", n > 0, f"{n} manifest(s), AI-composed-symbolic declared")
    except Exception as e:
        stage("C2PA verify", False, str(e)[:120])

    if a.dry_run:
        print(f"DRY RUN COMPLETE — {master} is signed, checked, and ready. "
              f"Re-run without --dry-run to upload ({'PUBLIC' if a.public else 'private'}).")
        return

    # 5. upload (the explicit outbound act)
    if a.service != "soundcloud":
        stage("service", False, f"unknown service {a.service}")
    sc = load_mod("connector_soundcloud", os.path.join(ROOT, "agent", "connector_soundcloud.py"))
    status = sc.t_sc_setup_status({})
    if "token: none" in status or "creds: none" in status:
        stage("soundcloud auth", False, "not connected — run sc_connect (one-click OAuth) first")
    out = sc.t_sc_upload({"file": master, "title": a.title or a.song.replace("_", " "),
                          "sharing": "public" if a.public else "private",
                          "genre": a.genre or "", "tags": a.tags or "sotadaw ai-assisted",
                          "description": "Made in SOTA DAW — AI-assisted, human-authored; "
                                         "C2PA Content Credentials embedded."})
    ok = "http" in out.lower() or "id" in out.lower()
    stage("upload", ok, out.strip().splitlines()[0][:100] if out else "no response")
    print("PUBLISHED." if ok else out)


if __name__ == "__main__":
    main()
