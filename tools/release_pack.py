#!/usr/bin/env python3
"""THE RELEASE PACK (BEST_DAW_30 #27) — one command, a label-ready folder.

  release_pack.py <song> [--platforms spotify,apple] [--bits 16] [--out DIR]

Builds songs/<name>_release/:
  master.wav          C2PA-signed master (export_master: provenance + voice
                      attribution + mastering verdict in the manifest)
  stems/              per-track stems (m1 render-stems; spectral truth lanes
                      stripped first — the measured sidecar-bomb trap)
  <name>.mid          exact-round-trip MIDI (midi_bridge)
  <name>.dawproject   Bitwig/Cubase/Nuendo/S1 session (dawproject_export)
  credits.md          who/how/what: meta, provenance, voices, per-platform
                      loudness verdicts, THE LICENSE GATE
  song.json           the symbolic session itself (the anti-black-box receipt)

THE LICENSE GATE: license_gate(song) returns every rights row it can see (today:
voicebank attribution/commercial flags; sample licenses when the indexer knows
them). A non-commercial voice marks the pack PRIVATE-ONLY, loudly — publish
flows must consult the same gate before any public target. The pack always
BUILDS (private use is always fine); honesty is the gate, not obstruction.
"""
import argparse, json, os, shutil, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from songname import resolve as resolve_song       # the SONG-NAME LAW

SONGS = os.path.join(ROOT, "songs")
M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")
PY = os.path.join(ROOT, ".venv", "bin", "python")
if not os.path.exists(PY):
    PY = sys.executable

# voicebank rights registry (grows with #30's bank registry; keyed by the
# track-comment attribution export_master already stamps)
VOICE_RIGHTS = {
    "gahata meiji": {"attribution": "Gahata Meiji from LUNAI Project",
                     "commercial": False,
                     "why": "LUNAI voicebank: attribution required, NON-commercial"},
}


def license_gate(song):
    """-> (rows, public_ok). Every rights row visible from the symbolic session."""
    rows, public_ok = [], True
    for t in song.get("tracks", []):
        c = str(t.get("comment", ""))
        if c.startswith("voice:"):
            vname = c.split("voice:", 1)[1].strip().lower()
            hit = next((v for k, v in VOICE_RIGHTS.items() if k in vname), None)
            if hit:
                rows.append({"item": f"track '{t.get('name')}' ({c})",
                             "license": hit["why"],
                             "public_ok": hit["commercial"]})
                public_ok = public_ok and hit["commercial"]
            else:
                rows.append({"item": f"track '{t.get('name')}' ({c})",
                             "license": "voicebank rights UNKNOWN — verify before release",
                             "public_ok": False})
                public_ok = False
    for s in (song.get("provenance") or {}).get("samples", []):
        lic = str(s.get("license", "")).lower()
        ok = not any(w in lic for w in ("nc", "non-commercial", "noncommercial", "unknown"))
        rows.append({"item": f"sample {s.get('path')}", "license": s.get("license", "?"),
                     "public_ok": ok})
        public_ok = public_ok and ok
    return rows, public_ok


def _strip_spectral(song):
    """render-stems force-loads every spectral sidecar (365-570MB each — the
    measured m1 rc=-15 bomb); the pack's stems drop those lanes."""
    out = json.loads(json.dumps(song))
    out["tracks"] = [t for t in out.get("tracks", [])
                     if (t.get("source") or {}).get("kind") != "spectral"
                     and not any(t.get("name", "").endswith(suf) for suf in
                                 ("_true_low", "_true_mid", "_true_high",
                                  "_true_noise", "_true_clicks"))]
    return out


def sh(cmd, timeout=1800):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=ROOT)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def build(song_name, platforms, bits=24, out_dir=None):
    name = resolve_song(song_name)
    sp = os.path.join(SONGS, f"{name}.json")
    if not os.path.exists(sp):
        sys.exit(f"no song '{song_name}'")
    song = json.load(open(sp))
    out = out_dir or os.path.join(SONGS, f"{name}_release")
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, "stems"))
    report = {"song": name, "when": time.strftime("%F %T"), "artifacts": {}, "verdicts": {}}

    rows, public_ok = license_gate(song)

    # 1. the signed master
    master = os.path.join(out, "master.wav")
    cmd = [PY, os.path.join(ROOT, "tools", "export_master.py"), name, master]
    if int(bits) == 16:
        cmd += ["--bits", "16"]
    rc, log = sh(cmd)
    report["artifacts"]["master"] = (rc == 0 and os.path.exists(master))
    master_log = "\n".join(l for l in log.splitlines() if l.strip())[-600:]

    # 2. stems (spectral-stripped copy)
    stripped = _strip_spectral(song)
    tmp = os.path.join(SONGS, f"_rp_{name}.json")
    json.dump(stripped, open(tmp, "w"))
    try:
        rc2, _ = sh([M1, "render-stems", tmp, os.path.join(out, "stems")])
        report["artifacts"]["stems"] = (rc2 == 0 and
                                        any(f.endswith(".wav") for f in
                                            os.listdir(os.path.join(out, "stems"))))
    finally:
        os.path.exists(tmp) and os.remove(tmp)

    # 3. MIDI + 4. dawproject + 5. the symbolic session itself
    rc3, _ = sh([sys.executable, os.path.join(ROOT, "tools", "midi_bridge.py"),
                 "export", sp, os.path.join(out, f"{name}.mid")])
    report["artifacts"]["midi"] = rc3 == 0
    rc4, _ = sh([sys.executable, os.path.join(ROOT, "tools", "dawproject_export.py"),
                 sp, os.path.join(out, f"{name}.dawproject")])
    report["artifacts"]["dawproject"] = rc4 == 0
    shutil.copyfile(sp, os.path.join(out, "song.json"))

    # 6. per-platform loudness verdicts ON THE SHIPPED MASTER (reports, never
    # fabricated variants — the honest S11 law: LUFS is judged, not smashed)
    for plat in platforms:
        rp = subprocess.run([PY, os.path.join(ROOT, "tools", "master_report.py"),
                             name, "--wav", master, "--platform", plat,
                             "--no-render"], capture_output=True, text=True,
                            timeout=600, cwd=ROOT)
        try:
            j = json.JSONDecoder().raw_decode(rp.stdout[rp.stdout.index("{"):])[0]
            flat = {**j, **(j.get("platform") if isinstance(j.get("platform"), dict) else {})}
            keep = {k: flat[k] for k in ("pass", "score", "platform", "verdict",
                                         "lufs_integrated", "true_peak_dbtp",
                                         "fix_first", "delta_lu")
                    if k in flat and not isinstance(flat[k], (dict, list))}
            report["verdicts"][plat] = keep or {"raw": rp.stdout.strip()[:200]}
        except Exception:
            report["verdicts"][plat] = {"raw": (rp.stdout or rp.stderr).strip()[-200:]}

    # 7. credits.md — the human-readable face of the provenance
    prov = song.get("provenance") or {}
    voices = sorted({str(t.get("comment")) for t in song.get("tracks", [])
                     if str(t.get("comment", "")).startswith("voice:")})
    lines = [f"# {name} — release credits", "",
             f"*built {report['when']} by SOTA DAW release_pack*", "",
             f"- bpm {song.get('bpm')} · key {song.get('key', '?')} · "
             f"{song.get('lengthBars')} bars · {len(song.get('tracks', []))} tracks",
             "- composition: fully symbolic (song.json in this folder — every note, "
             "voice and mix move inspectable); no black-box audio generation", ""]
    if voices:
        lines += ["## voices", *[f"- {v}" for v in voices], ""]
    if prov.get("agents"):
        lines += ["## agents", *[f"- {a.get('model', '?')} (skills: "
                                 f"{', '.join(a.get('skills', [])[:6]) or '—'})"
                                 for a in prov["agents"]], ""]
    lines += ["## platform loudness verdicts",
              *[f"- **{p}**: {v}" for p, v in report["verdicts"].items()], "",
              "## THE LICENSE GATE",
              f"**verdict: {'PUBLIC OK' if public_ok else 'PRIVATE-ONLY'}**", ""]
    for r in rows:
        lines.append(f"- {'OK ' if r['public_ok'] else 'BLOCKS PUBLIC: '}{r['item']} — {r['license']}")
    if not rows:
        lines.append("- no rights-bearing items detected (all sounds engine-native)")
    lines += ["", "## master export log", "```", master_log, "```"]
    open(os.path.join(out, "credits.md"), "w").write("\n".join(lines) + "\n")

    report["license_gate"] = {"public_ok": public_ok, "rows": rows}
    report["out"] = out
    print(json.dumps({k: report[k] for k in ("song", "artifacts", "verdicts",
                                             "license_gate", "out")}, indent=1))
    if not public_ok:
        print("\nLICENSE GATE: PRIVATE-ONLY — see credits.md (publish flows must "
              "consult license_gate() before any public target)")
    ok = all(report["artifacts"].values())
    print(f"release pack: {'COMPLETE' if ok else 'PARTIAL — see artifacts flags'} -> {out}")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("song")
    ap.add_argument("--platforms", default="spotify")
    ap.add_argument("--bits", type=int, default=24)
    ap.add_argument("--out")
    a = ap.parse_args()
    return build(a.song, [p.strip() for p in a.platforms.split(",") if p.strip()],
                 bits=a.bits, out_dir=a.out)


if __name__ == "__main__":
    sys.exit(main())
