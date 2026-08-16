#!/usr/bin/env python3
"""MASKING RENDER E2E (wave 21) — the unmask circle through the REAL
engine. A pad wall + a quiet lead in the same register render to stems;
the MSR court must convict the lead; heal_masking runs the bounded
ladder (level duck + pan split + fx_bell cuts on the masker); ONE
re-render must LOWER the lead's NormalizedMask without thinning it
(over-unmask guard: the maskee's own energy must not fall).
Skip-safe: no m1 -> SKIP."""
import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")


def main():
    if not os.path.exists(M1):
        print("masking_e2e: SKIP (no m1 binary)")
        return 0
    import masking_court as MK

    tmp = tempfile.mkdtemp(prefix="mask_e2e_", dir=os.path.join(ROOT))
    try:
        pad_notes = []
        for b in range(0, 16, 2):
            for p in (64, 67, 71):          # dense wall around the lead
                pad_notes.append({"start": float(b), "len": 2.0,
                                  "pitch": p, "vel": 0.95})
        lead_notes = [{"start": float(b) + 0.5, "len": 1.2, "pitch": 65,
                       "vel": 0.1} for b in range(0, 16, 2)]
        song = {"bpm": 120, "lengthBars": 4,
                "tracks": [
                    {"name": "pad_wall", "source": {"id": "pad_motion"},
                     "gainDb": 3.0, "pan": 0.0, "notes": pad_notes},
                    {"name": "lead", "source": {"id": "pluck"},
                     "gainDb": -8.0, "pan": 0.0, "notes": lead_notes}]}
        sj = os.path.join(tmp, "mask.json")
        stems = os.path.join(tmp, "stems")
        json.dump(song, open(sj, "w"), indent=1)
        r = subprocess.run([M1, "render-stems", sj, stems],
                           capture_output=True, text=True, timeout=420)
        if r.returncode != 0 or not os.path.isdir(stems):
            print(f"masking_e2e: RED — render failed: {r.stderr[-250:]}")
            return 1
        v = MK.court_masking_stems(stems)
        lead_key = next((k for k in v.get("per_stem", {}) if "lead" in k),
                        None)
        m_before = (v.get("per_stem") or {}).get(lead_key, 0.0)
        if v.get("ok", True) or not any("lead" in f["track"]
                                        for f in v.get("flags", [])):
            print(f"masking_e2e: RED — planted buried lead NOT convicted: "
                  f"{json.dumps(v)[:300]}")
            return 1
        edits = MK.heal_masking(song, v, stems)
        if not any(e["kind"] == "bell_cut" for e in edits):
            print(f"masking_e2e: RED — no bell landed: {edits}")
            return 1
        json.dump(song, open(sj, "w"), indent=1)
        stems2 = os.path.join(tmp, "stems2")
        r = subprocess.run([M1, "render-stems", sj, stems2],
                           capture_output=True, text=True, timeout=420)
        if r.returncode != 0:
            print(f"masking_e2e: RED — heal re-render failed: "
                  f"{r.stderr[-250:]}")
            return 1
        v2 = MK.court_masking_stems(stems2)
        m_after = (v2.get("per_stem") or {}).get(lead_key, 1.0)
        if not (m_after < m_before - 0.03):
            print(f"masking_e2e: RED — mask did not drop: {m_before} -> "
                  f"{m_after}")
            return 1
        # over-unmask guard: the maskee's own level must not fall
        import soundfile as sf
        import numpy as np

        def rms(d):
            f = next(x for x in os.listdir(d) if "lead" in x)
            y, _ = sf.read(os.path.join(d, f), always_2d=True)
            return float(np.sqrt(np.mean(y ** 2)))
        r0, r1 = rms(stems), rms(stems2)
        if r1 < r0 * 0.7:
            print(f"masking_e2e: RED — the heal thinned the maskee: "
                  f"{r0:.4f} -> {r1:.4f}")
            return 1
        print(f"masking_e2e: GREEN — buried lead convicted (M={m_before}) "
              f"-> ladder heal ({[e['kind'] for e in edits]}) -> "
              f"re-render M={m_after}, maskee intact")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
