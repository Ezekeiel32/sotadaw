#!/usr/bin/env python3
"""NUMERIC LIFT BATTERY — proof for the W117 linear-region shortcut
(sidecar._numeric_lift + the recovery loop seam + tools/wav_gain.py).

The claim: in the region recovery_step itself calls clear of the wall
(post-lift dBTP <= -4), a loudness lift is a pure sample multiply — so the
loop applies it numerically (atomic, 24-bit aware, refuse-not-clip) and
re-measures with the real ears, saving a ~16s engine render per lift. Outside
that region, or on any doubt, the loop falls back to the real render.

Three seams, all zero-render (render_and_analyze is mocked and COUNTED):
  A. quiet clean take  -> numeric path owns the lift, json+wav+ears agree
  B. hot take (near the wall) -> numeric path DECLINES, real render fires
  C. unreadable wav    -> fail-open to the real render (never a dead take)

Isolated: SOTADAW_IPC temp, scratch _prop__nlb_* names, scrubbed after.
"""
import json, os, sys, tempfile, wave
import numpy as np

IPC = tempfile.mkdtemp(prefix="nlb_ipc_")
os.environ["SOTADAW_IPC"] = IPC
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "agent"))
import sidecar  # noqa: E402

SONGS = os.path.join(ROOT, "songs")
N = [0]


def check(name, cond):
    print(("  PASS " if cond else "  FAIL ") + name)
    if not cond:
        sys.exit(1)
    N[0] += 1


def mk_wav(path, peak_dbfs):
    sr = 44100
    t = np.arange(sr * 2) / sr
    x = np.sin(2 * np.pi * 220.0 * t) * (10 ** (peak_dbfs / 20.0))
    xi = np.rint(x * 8388607.0).astype(np.int32)
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(3); w.setframerate(sr)
        w.writeframes(np.stack([(xi & 0xFF).astype(np.uint8),
                                ((xi >> 8) & 0xFF).astype(np.uint8),
                                ((xi >> 16) & 0xFF).astype(np.uint8)],
                               axis=1).tobytes())


def ears(wav):
    rc, out, _ = sidecar.run([sys.executable,
                              os.path.join(ROOT, "tools", "analyze2.py"), wav],
                             timeout=180)
    return json.loads(out)


def run_case(tag, peak_dbfs, a_override=None):
    prop = f"_prop__nlb_{tag}"
    wav = os.path.join(SONGS, prop + ".wav")
    pj = os.path.join(SONGS, prop + ".json")
    mk_wav(wav, peak_dbfs)
    json.dump({"bpm": 120, "tracks": [{"name": "lead", "notes": [
        {"start": 0, "len": 1, "pitch": 57, "vel": 0.8}]}]}, open(pj, "w"))
    a0 = dict(a_override or ears(wav))
    log = []
    sidecar._lowend_ears_pass = lambda rid, p, a, g: a   # the LIFT LOOP alone
    sidecar.render_and_analyze = lambda rid, name, label: log.append("R") or a0
    a1 = sidecar.loudness_recovery(0, prop, a0, "")
    return prop, wav, pj, a1, log


def main():
    try:
        # A. the quiet clean take — the probe that shipped the rung
        prop, wav, pj, a1, log = run_case("quiet", -26.0)
        af = ears(wav)
        trim = next((f for f in json.load(open(pj)).get("master", [])
                     if f.get("id") == "fx_trim"), None)
        check("A: lift loop never rendered", "R" not in log)
        check("A: trim staged in json", trim and trim["params"]["level"] > 0)
        check("A: wav lifted into the window (LUFS > -14)",
              float(af["lufs_integrated"]) > -14.0)
        check("A: clean after lift", af["clipped_samples"] == 0)
        check("A: returned ears are the lifted truth",
              isinstance(a1, dict)
              and abs(float(a1["lufs_integrated"]) - float(af["lufs_integrated"])) < 0.2)
        check("A: wall provably idle (dBTP <= -4)",
              float(af["true_peak_dbtp"]) <= -4.0)
        os.remove(wav); os.remove(pj)

        # B. the hot take — quiet by LUFS but peaks near the wall: the numeric
        # guard must DECLINE (tp + delta > -4) and the real render must fire
        prop, wav, pj, a1, log = run_case(
            "hot", -6.0,
            a_override={"clipped_samples": 0, "lufs_integrated": -20.0,
                        "true_peak_dbtp": -6.0, "peak_dbfs": -6.0})
        af = ears(wav)
        check("B: numeric path declined near the wall (render fired)", "R" in log)
        check("B: wav untouched by any numeric write (peak still -6)",
              abs(float(af["true_peak_dbtp"]) - -6.0) < 0.6)
        os.remove(wav); os.remove(pj)

        # C. wav gone — fail-open to the render path, never a crash
        prop = "_prop__nlb_gone"
        pj = os.path.join(SONGS, prop + ".json")
        json.dump({"bpm": 120, "tracks": [{"name": "lead", "notes": [
            {"start": 0, "len": 1, "pitch": 57, "vel": 0.8}]}]}, open(pj, "w"))
        a0 = {"clipped_samples": 0, "lufs_integrated": -20.0,
              "true_peak_dbtp": -20.0, "peak_dbfs": -20.0}
        log = []
        sidecar._lowend_ears_pass = lambda rid, p, a, g: a
        sidecar.render_and_analyze = lambda rid, name, label: log.append("R") or a0
        a1 = sidecar.loudness_recovery(0, prop, a0, "")
        check("C: missing wav = fail-open to the render path", "R" in log)
        os.remove(pj)
    finally:
        for f in os.listdir(SONGS):
            if f.startswith("_prop__nlb_"):
                os.remove(os.path.join(SONGS, f))
        import shutil
        shutil.rmtree(IPC, ignore_errors=True)
    print(f"NUMERIC LIFT BATTERY: {N[0]}/9 PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
