#!/usr/bin/env python3
"""TRUE-PEAK battery — fx_truepeak is a release-grade wall; fx_brickwall provably is not.

The discriminating signal (BS.1770 ISP classic): a sine at fs/4 with +45deg phase
— every SAMPLE lands at +/-0.707*A but the WAVEFORM peaks at A between samples.
A sample-peak wall sees 0.707A (-3dB blind spot); a true-peak wall must see A.

  T1 fx_brickwall @ -1.0 on the ISP sine: true peak STAYS HOT (> -0.35 dBTP)
     — the documented blindness, measured
  T2 fx_truepeak  @ -1.0 on the same sine: true peak <= -0.85 dBTP (wall holds)
  T3 transparency: material 6dB under the ceiling passes with <0.3dB RMS change
     and NO fade-in at the head (the attenuation-form init law)
  T4 musical proof: the arc's rough-mix song mastered via fx_truepeak @ -1.2:
     dBTP <= -1.0 AND LUFS beats the old -3.0-ceiling insurance path by >= 1.0dB
     (the loudness the insurance tax was costing)
Exit 1 on any failure. Uses the JIT rail (unregistered .dsp renders instantly)."""
import json, math, os, struct, subprocess, sys, wave

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "songs")
M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")

PASS, FAIL = [], []
def check(n, c, d=""):
    (PASS if c else FAIL).append(n)
    print(f"  [{'PASS' if c else 'FAIL'}] {n}" + (f" — {d}" if d else ""))


def write_sine(path, amp, seconds=3.0, sr=44100, phase=math.pi / 4):
    """fs/4 sine, +45deg: samples all +/-amp*0.7071, true peak = amp."""
    n = int(seconds * sr)
    with wave.open(path, "w") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
        frames = bytearray()
        for i in range(n):
            v = amp * math.sin(math.pi / 2 * i + phase)
            s = int(max(-32767, min(32767, round(v * 32767))))
            frames += struct.pack("<hh", s, s)
        w.writeframes(bytes(frames))


def render(master_fx, clip_wav, tag, gain_db=0.0):
    song = {"version": 2, "bpm": 120, "lengthBars": 2, "masterGainDb": 0,
            "master": master_fx,
            "tracks": [{"name": "sig", "source": {"kind": "audio"}, "gainDb": gain_db,
                        "audioClips": [{"file": clip_wav, "startBeat": 0,
                                        "lengthBeats": 8, "offsetSec": 0}]}]}
    sj = os.path.join(SONGS, f"_tpb_{tag}.json"); wav = os.path.join(SONGS, f"_tpb_{tag}.wav")
    json.dump(song, open(sj, "w"), indent=1)
    r = subprocess.run([M1, "render", sj, wav], capture_output=True, text=True, timeout=300)
    return wav if "ok=1" in (r.stdout + r.stderr) else None


def analyze(wav):
    r = subprocess.run([os.path.join(ROOT, ".venv/bin/python"),
                        os.path.join(ROOT, "tools", "analyze2.py"), wav],
                       capture_output=True, text=True, timeout=120)
    return json.loads(r.stdout)


def head_rms_db(wav, seconds=0.05):
    import soundfile as sf
    x, sr = sf.read(wav, always_2d=True)
    h = x[: int(sr * seconds)]
    t = x[int(sr * seconds): int(sr * seconds * 8)]
    rms = lambda a: 20 * math.log10(max(1e-9, float((a ** 2).mean() ** 0.5)))
    return rms(h), rms(t)


def cleanup():
    for f in os.listdir(SONGS):
        if f.startswith("_tpb_"):
            os.remove(os.path.join(SONGS, f))


def main():
    isp = os.path.join(SONGS, "_tpb_isp.wav")
    write_sine(isp, 0.999)

    # T1 the blindness, measured
    w = render([{"id": "fx_brickwall", "params": {"ceiling": -1.0}}], isp, "bw")
    if not w:
        check("T1 render", False, "brickwall render failed"); cleanup(); sys.exit(1)
    a1 = analyze(w)
    check("T1 fx_brickwall is ISP-BLIND (true peak stays hot at -1.0 ceiling)",
          a1["true_peak_dbtp"] > -0.35, f"{a1['true_peak_dbtp']} dBTP")

    # T2 the wall holds
    w = render([{"id": "fx_truepeak", "params": {"ceiling": -1.0}}], isp, "tp")
    if not w:
        check("T2 render", False, "truepeak render failed (JIT?)"); cleanup(); sys.exit(1)
    a2 = analyze(w)
    check("T2 fx_truepeak HOLDS the true-peak ceiling on the ISP sine",
          a2["true_peak_dbtp"] <= -0.85, f"{a2['true_peak_dbtp']} dBTP")

    # T3 transparency + no fade-in
    quiet = os.path.join(SONGS, "_tpb_quiet.wav")
    write_sine(quiet, 0.35)                        # ~ -9dB peaks, far under -1
    wq0 = render([], quiet, "q0")
    wq1 = render([{"id": "fx_truepeak", "params": {"ceiling": -1.0}}], quiet, "q1")
    aq0, aq1 = analyze(wq0), analyze(wq1)
    check("T3 transparent under the ceiling (<0.3dB RMS delta)",
          abs(aq0["rms_db"] - aq1["rms_db"]) < 0.3,
          f"{aq0['rms_db']} -> {aq1['rms_db']} dB")
    h, t = head_rms_db(wq1)
    check("T3b no fade-in at the head (attenuation-form init)",
          h > t - 1.0, f"head {h:.2f} vs body {t:.2f} dB")

    # T4 the loudness win on MUSIC: rough dense mix, old insurance vs new wall
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    from arc_quality import rough_loop
    dense = rough_loop()
    for t_ in dense["tracks"]:
        t_.pop("fx", None); t_["pan"] = 0
    dense["masterGainDb"] = 0
    def master(song, chain, tag):
        s = json.loads(json.dumps(song)); s["master"] = chain
        sj = os.path.join(SONGS, f"_tpb_{tag}.json"); wv = os.path.join(SONGS, f"_tpb_{tag}.wav")
        json.dump(s, open(sj, "w"), indent=1)
        r = subprocess.run([M1, "render", sj, wv], capture_output=True, text=True, timeout=600)
        return analyze(wv) if "ok=1" in (r.stdout + r.stderr) else None
    old = master(dense, [{"id": "fx_trim", "params": {"level": 6.0}},
                         {"id": "fx_brickwall", "params": {"ceiling": -3.0}}], "old")
    new = master(dense, [{"id": "fx_trim", "params": {"level": 6.0}},
                         {"id": "fx_truepeak", "params": {"ceiling": -1.2}}], "new")
    if not old or not new:
        check("T4 renders", False); cleanup(); sys.exit(1)
    check("T4 music: fx_truepeak holds <= -1.0 dBTP where it counts",
          new["true_peak_dbtp"] <= -1.0, f"{new['true_peak_dbtp']} dBTP")
    check("T4b the insurance tax refunded (>= 1.0 LUFS louder than the -3.0 path)",
          new["lufs_integrated"] >= old["lufs_integrated"] + 1.0,
          f"{old['lufs_integrated']} -> {new['lufs_integrated']} LUFS")
    check("T4c still clean (0 clipped)", new["clipped_samples"] == 0,
          f"{new['clipped_samples']}")

    cleanup()
    print(f"\n== TRUE-PEAK: {len(PASS)} pass / {len(FAIL)} fail ==")
    if FAIL:
        print("FAILURES:", ", ".join(FAIL)); sys.exit(1)
    print("THE WALL IS RELEASE-GRADE (ISP-proof, transparent, loudness refunded)")


if __name__ == "__main__":
    main()
