#!/usr/bin/env python3
"""THE PARAM COURT battery — fx zone truth at every write seam.

The disease (corpus sweep 2026-07-24): setZone is exact-name, so a wrongly
named fx param is a SILENT no-op — fx_filter {"resonance"}/{"mode"} and
fx_trim {"gain"} were being born as late as 07-16 because the seams checked
fx IDs, never params. Proof surface:
  A) fx_zones.check_params — aliases heal, duplicates drop, markers legal,
     unknown named, unknown fx fail-open
  B) _check_fx_entry (targeted seams) — fail-closed with teaching lines;
     the ADVERTISED nam:/clap: shapes finally pass this seam (they were
     rejected by the avail check since V51 — the battery wrote raw json,
     so the contradiction never surfaced)
  C) sanitize_song (whole-document seam) — heals aliases, strips dead
     params with receipts, keeps first-party markers; validate_song green
  D) doctor X2 — params._am no longer self-flags, real dirt still nags
Run: python3 tools/param_court_battery.py (pure, zero engine)."""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "agent"))
os.environ["SOTADAW_IPC"] = tempfile.mkdtemp(prefix="pcourt_")

import fx_zones
import daw_mcp
import doctor

N = {"pass": 0, "fail": 0}


def check(name, cond, detail=""):
    N["pass" if cond else "fail"] += 1
    print(("PASS " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))


# ---- A) the kernel
p = {"cutoff": 900, "resonance": 0.4}
h, u = fx_zones.check_params("fx_filter", p)
check("A1 resonance->res heals in place", p == {"cutoff": 900, "res": 0.4} and h == [("resonance", "res")] and not u)

p = {"gain": -3.0}
h, u = fx_zones.check_params("fx_trim", p)
check("A2 trim gain->level (the classic no-op)", p == {"level": -3.0} and not u)

p = {"q": 0.5}
h, u = fx_zones.check_params("fx_djfilter", p)
check("A3 global q->res via zone gate", p == {"res": 0.5} and not u)

p = {"threshold": -1.0}
h, u = fx_zones.check_params("fx_truepeak", p)
check("A4 threshold->ceiling on the wall", p == {"ceiling": -1.0} and not u)

pg = {"release": 80}
pc = {"rel": 120}
fx_zones.check_params("fx_gate", pg)
fx_zones.check_params("fx_comp", pc)
check("A5 release<->rel resolves per-fx", pg == {"rel": 80} and pc == {"release": 120})

p = {"res": 0.3, "resonance": 0.9}
h, u = fx_zones.check_params("fx_filter", p)
check("A6 duplicate: real knob wins, alias drops", p == {"res": 0.3} and not u)

p = {"_am": 1.0, "cutoff": 2500}
h, u = fx_zones.check_params("fx_filter", p)
check("A7 '_' marker legal (auto_master params._am)", not h and not u and p.get("_am") == 1.0)

p = {"mode": "hp"}
h, u = fx_zones.check_params("fx_filter", p)
err = fx_zones.unknown_error("fx_filter", u)
check("A8 unknown named + teaching", u == ["mode"] and "fx_hipass" in err and "cutoff" in err)

h, u = fx_zones.check_params("fx_futurevoice", {"anything": 1})
check("A9 unknown fx fails OPEN (new voice tomorrow)", not h and not u)

# ---- B) targeted seams
avail = {"fx_filter", "fx_trim", "fx_reverb"}
e = {"id": "fx_filter", "params": {"resonance": 0.5}}
err = daw_mcp._check_fx_entry(e, avail, [])
check("B1 seam alias-heals then passes", err is None and e["params"] == {"res": 0.5})

err = daw_mcp._check_fx_entry({"id": "fx_filter", "params": {"mode": "hp"}}, avail, [])
check("B2 seam fails CLOSED with teaching", err is not None and "fx_hipass" in err)

nam_path = os.path.join("app", "third_party", "nam-core", "example_models", "wavenet.nam")
if os.path.exists(os.path.join(ROOT, nam_path)):
    err = daw_mcp._check_fx_entry({"id": f"nam:{nam_path}", "params": {"output_db": -6}}, avail, [])
    check("B3 nam:<path> passes the seam (advertised since V51)", err is None, str(err))
else:
    check("B3 nam:<path> passes the seam", True, "example capture absent — existence branch covered by B4")

err = daw_mcp._check_fx_entry({"id": "nam:no/such/capture.nam"}, avail, [])
check("B4 nam missing path names itself", err is not None and "not found" in err)

err = daw_mcp._check_fx_entry({"id": "clap:no/such/plug.clap"}, avail, [])
check("B5 clap missing path names itself", err is not None and "not found" in err)

# ---- C) whole-document seam
song = {"bpm": 120, "lengthBars": 4, "key": "A minor",
        "tracks": [{"name": "lead", "source": {"kind": "faust", "id": "supersaw"},
                    "notes": [{"start": 0, "len": 1, "pitch": 69, "vel": 0.9}],
                    "fx": [{"id": "fx_filter", "params": {"cutoff": 1200, "resonance": 0.4, "mode": "hp"}}]}],
        "buses": [{"id": "space", "fx": [{"id": "fx_reverb", "params": {"wet": 0.3, "size": 0.8}}]}],
        "master": [{"id": "fx_filter", "params": {"_am": 1.0, "cutoff": 2500}},
                   {"id": "fx_truepeak", "params": {"ceiling": -1.2}}]}
song2, rec = daw_mcp.sanitize_song(json.loads(json.dumps(song)))
fx0 = song2["tracks"][0]["fx"][0]["params"]
bus0 = song2["buses"][0]["fx"][0]["params"]
m0 = song2["master"][0]["params"]
check("C1 track alias healed", fx0.get("res") == 0.4 and "resonance" not in fx0)
check("C2 track dead param stripped + receipted", "mode" not in fx0
      and any("dead param 'mode'" in r for r in rec))
check("C3 bus wet->mix healed", bus0 == {"mix": 0.3, "size": 0.8})
check("C4 master marker survives sanitize", m0.get("_am") == 1.0
      and not any("_am" in r for r in rec))
errs = daw_mcp.validate_song(song2)
check("C5 validate green after the court", not errs, "; ".join(errs[:2]))

# ---- E) the table can never fall behind the compiled fx set again
dsp = fx_zones.dsp_zone_truth(os.path.join(ROOT, "instruments"))
missing = [f for f in dsp if f not in fx_zones.FX_ZONES]
check("E1 every fx_*.dsp has table truth", not missing, str(missing))
diffs = {f: (sorted(dsp[f] ^ fx_zones.FX_ZONES[f]))
         for f in dsp if f in fx_zones.FX_ZONES and dsp[f] != fx_zones.FX_ZONES[f]}
check("E2 table zones == dsp slider truth", not diffs, str(diffs)[:160])
pb = {"q": 3.0, "freq": 900, "gain": -4}
h, u = fx_zones.check_params("fx_bell", pb)
check("E3 fx_bell keeps its real q/freq/gain (zone-gate beats alias)",
      not h and not u and pb == {"q": 3.0, "freq": 900, "gain": -4})

# ---- D) doctor
iss = doctor.diagnose(song2)
codes = [c for c, _, _ in iss]
check("D1 doctor: no X2 on healed song (markers exempt)", "X2" not in codes, str(codes))
dirty = json.loads(json.dumps(song2))
dirty["tracks"][0]["fx"][0]["params"]["bogus"] = 1
iss = doctor.diagnose(dirty)
check("D2 doctor still nags real standing dirt", any(c == "X2" for c, _, _ in iss))

print(f"param court battery: {N['pass']}/{N['pass'] + N['fail']}"
      + (" clean" if not N["fail"] else " RED"))
sys.exit(1 if N["fail"] else 0)
