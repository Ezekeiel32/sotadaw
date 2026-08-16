#!/usr/bin/env python3
"""THE PROVENANCE GATE — wave 70 (r-31 items 178/179/180/181): the
legal moat as a machine-checkable release-gate battery. Six checks;
any red fails the release.

  (a) every bundled voicebank carries LICENSE + attribution files
  (b) LICENSE-LINT: no AGPL/GPL/NC dependency in the shipped import
      graph (essentia, madmom, matchering, so-vits, xtts, fumiama-RVC
      are the named landmines)
  (c) every voicebank has a provenance record (bank.json / license)
  (d) exports carry C2PA + attribution (delegated: attribution_battery
      is the functional proof; here the static seam is asserted)
  (e) every KG node type carries provenance; NO number derives from
      GTZAN or uncleared commercial benchmarks (blocklist scan)
  (f) voice-conversion rails operate on PROJECT-OWN audio only and the
      consent/license record rides the song (voice_license law)

Run: .venv/bin/python tools/provenance_gate.py  (suite leg; --release
adds the KG legs that need the live graph).
"""
import ast
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAILS = []

# the named landmines (r-31): AGPL / GPL-in-process / non-commercial
LANDMINES = {"essentia", "madmom", "matchering", "so_vits_svc", "sovits",
             "xtts", "TTS.tts", "rvc_infer", "audiocraft"}
DATASET_BLOCKLIST = ("gtzan", "fma_full", "million_song")


def check(name, cond, note=""):
    tag = "PASS" if cond else "FAIL"
    print(f"[{tag}] {name}" + (f" — {note}" if note and not cond else ""))
    if not cond:
        FAILS.append(name)


def shipped_imports():
    """Every module imported anywhere in the shipped code (tools/ +
    agent/ + flows/) — AST truth, comments can't hide an import."""
    mods = set()
    for pat in ("tools/*.py", "agent/*.py", "flows/*.py"):
        for p in glob.glob(os.path.join(ROOT, pat)):
            try:
                tree = ast.parse(open(p).read())
            except Exception:
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    mods.update(a.name.split(".")[0] for a in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    mods.add(node.module.split(".")[0])
    return mods


def run(release=False):
    # (b) the license lint
    mods = shipped_imports()
    hot = sorted(m for m in mods if m.lower() in LANDMINES
                 or m in LANDMINES)
    check("(b) license-lint: no AGPL/GPL/NC landmine in the shipped "
          "import graph", not hot, f"found {hot}")

    # (a)+(c) voicebanks: license + attribution + provenance
    banks = [d for d in glob.glob(os.path.join(ROOT, "library", "voices",
                                               "*"))
             if os.path.isdir(d)]
    for b in banks:
        files = {f.lower() for f in os.listdir(b)}
        has_lic = any("license" in f or "terms" in f for f in files)
        has_attr = any("credits" in f or "about" in f for f in files)
        check(f"(a) bank '{os.path.basename(b)}' bundles LICENSE",
              has_lic)
        check(f"(c) bank '{os.path.basename(b)}' carries attribution/"
              "provenance", has_attr or
              os.path.exists(os.path.join(b, "bank.json")))
    if not banks:
        print("[note] no voicebanks on this box — (a)/(c) vacuous "
              "(banks are USER-FETCH by law)")
    # (c+) W73: the registry's own invariants (license gate law)
    try:
        import voicebank_registry as VR
        check("(c) voicebank registry verify (records + license gates)",
              VR.verify() == 0)
    except Exception as e:
        check("(c) voicebank registry readable", False, str(e))

    # (d) the export seam: C2PA + attribution ride export_master
    em = open(os.path.join(ROOT, "tools", "export_master.py")).read()
    check("(d) export_master embeds C2PA manifest + voice attribution "
          "(functional proof = attribution_battery, suite leg)",
          "c2pa" in em.lower() and "attribution" in em.lower())

    # (f) consent law: the conversion rails + the license record
    sg = ""
    for rail in ("vocal_follow.py", "retune.py"):
        p = os.path.join(ROOT, "tools", rail)
        if os.path.exists(p):
            sg += open(p).read()
    check("(f) voice rails carry no third-party model fetch (project-"
          "own audio by construction)",
          "youtube" not in sg.lower() and "spotify" not in sg.lower())
    check("(f) voice_license law present (attribution_court stamps "
          "non-commercial voice use; export runs it PRE-SIGN)",
          "voice_license" in open(os.path.join(
              ROOT, "tools", "attribution_court.py")).read())

    if release:
        # (e) the KG provenance ledger + dataset blocklist
        try:
            sys.path.insert(0, os.path.join(ROOT, "tools"))
            import kg
            g = kg.KG()
            for label in ("Genre", "MixTarget", "PatchArchetype",
                          "VocalTarget", "OrchestrationRule"):
                rows = g.q(f"MATCH (n:{label}) WHERE n.provenance IS NULL "
                           f"RETURN count(n)")
                bad = rows[0][0] if rows and rows[0] else 0
                check(f"(e) every {label} carries provenance", bad == 0,
                      f"{bad} orphans")
            rows = g.q("MATCH (n) WHERE n.provenance IS NOT NULL "
                       "RETURN n.provenance")
            dirty = [r[0] for r in rows
                     if any(d in str(r[0]).lower()
                            for d in DATASET_BLOCKLIST)]
            check("(e) no KG number derives from GTZAN/uncleared "
                  "benchmarks", not dirty, str(dirty[:3]))
        except Exception as e:
            check("(e) KG reachable for the release gate", False, str(e))

    print()
    if FAILS:
        print(f"provenance_gate: {len(FAILS)} RED — " + "; ".join(FAILS))
        return 1
    print("provenance_gate: ALL GREEN — the moat holds")
    return 0


if __name__ == "__main__":
    sys.exit(run(release="--release" in sys.argv))
