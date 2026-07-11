#!/usr/bin/env python3
"""THE DRUM MICROSCOPE battery — pure/offline proofs for tools/drumsep.py and
the transcribe_stems drum-pieces path. Model files are NOT required (legs that
need them are --real only), so the guardian suite stays green on any box.

    .venv/bin/python tools/drumsep_battery.py          # pure (suite leg)
    .venv/bin/python tools/drumsep_battery.py --real   # + live OV self-ID probe
"""
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

PASS = 0
FAIL = 0


def check(name, ok, detail=""):
    global PASS, FAIL
    if ok:
        PASS += 1
        print(f"  ok  {name}")
    else:
        FAIL += 1
        print(f"FAIL  {name}  {detail}")


def env(at_s, dec_s, n, sr):
    e = np.zeros(n)
    i0 = int(at_s * sr)
    if i0 < n:
        e[i0:] = np.exp(-np.arange(n - i0) / (dec_s * sr))
    return e


def tone_hits(freq, ats, dec, n, sr, amp=0.7):
    t = np.arange(n) / sr
    y = np.zeros(n)
    for at in ats:
        y += np.sin(2 * np.pi * freq * t) * env(at, dec, n, sr) * amp
    return y


def noise_hits(rng, ats, dec, n, sr, amp=0.5, hp=None):
    y = np.zeros(n)
    for at in ats:
        y += rng.standard_normal(n) * env(at, dec, n, sr) * amp
    if hp:
        from scipy.signal import butter, sosfilt
        y = sosfilt(butter(4, hp / (sr / 2), "high", output="sos"), y)
    return y


def main():
    real = "--real" in sys.argv
    sr = 44100
    dur = 4.0
    n = int(sr * dur)
    rng = np.random.default_rng(11)

    # -------------------------------------------------- module honesty
    os.environ["SOTADAW_NO_DRUMSEP"] = "1"
    import drumsep
    import transcribe_stems as ts
    check("kill switch: available() is None", drumsep.available() is None)
    check("PIECES_OV is the pinned 5", drumsep.PIECES_OV ==
          ("kick", "snare", "toms", "hh", "cymbals"))
    got = ts._drum_piece_signals("/nonexistent/drums.wav", sr, n, 1.0)
    check("piece signals honest None under kill switch", got is None)
    del os.environ["SOTADAW_NO_DRUMSEP"]

    # -------------------------------------------------- pieces lane law (fake stems)
    bpm = 120.0
    kick = tone_hits(55, np.arange(0.0, dur - 0.3, 0.5), 0.08, n, sr, 0.8)
    snare = (tone_hits(190, np.arange(0.25, dur - 0.3, 1.0), 0.05, n, sr, 0.5)
             + noise_hits(rng, np.arange(0.25, dur - 0.3, 1.0), 0.04, n, sr,
                          0.35, hp=1500))
    toms = (tone_hits(90, (0.75,), 0.16, n, sr, 0.7)
            + tone_hits(130, (1.75,), 0.16, n, sr, 0.7)
            + tone_hits(185, (2.75,), 0.16, n, sr, 0.7))
    hh = noise_hits(rng, np.arange(0.0, dur - 0.2, 0.25), 0.015, n, sr, 0.4,
                    hp=7000)
    hh += noise_hits(rng, (3.5,), 0.22, n, sr, 0.4, hp=7000)   # one OPEN hat
    cym = noise_hits(rng, (1.9,), 0.9, n, sr, 0.5, hp=3000)    # crash: long ring
    sigs = {"kick": kick, "snare": snare, "toms": toms, "hh": hh,
            "cymbals": cym}
    notes, rec = ts._drum_notes_pieces(sigs, False, "fake", sr, bpm, 2500)
    by = {}
    for nt in notes:
        by.setdefault(nt["pitch"], []).append(nt)
    check("engine tag names the microscope",
          rec["engine"].startswith("drum-pieces:fake"), rec["engine"])
    check("kick lane heard (>=7 of 8)", len(by.get(36, [])) >= 7,
          f"{len(by.get(36, []))}")
    check("snare lane heard", len(by.get(38, [])) >= 3, f"{len(by.get(38, []))}")
    check("TOM fundamental binning: 90Hz -> 43", len(by.get(43, [])) == 1,
          f"{sorted((p, len(v)) for p, v in by.items())}")
    check("TOM fundamental binning: 130Hz -> 47", len(by.get(47, [])) == 1)
    check("TOM fundamental binning: 185Hz -> 50", len(by.get(50, [])) == 1)
    check("closed hats heard", len(by.get(42, [])) >= 10, f"{len(by.get(42, []))}")
    check("the open hat classified 46", len(by.get(46, [])) >= 1)
    check("the crash classified 49 (ring law)", len(by.get(49, [])) >= 1)
    kmax = max(nt["vel"] for nt in by.get(36, []))
    check("ceiling law: loudest kick wears ~vel 1.0", kmax >= 0.97, f"{kmax}")

    # ride vs crash: regular short-ring pattern -> 51
    ride = noise_hits(rng, np.arange(0.1, dur - 0.4, 0.5), 0.06, n, sr, 0.5,
                      hp=3000)
    sigs_r = {"kick": kick, "snare": snare, "toms": np.zeros(n), "hh": hh,
              "cymbals": ride}
    notes_r, _ = ts._drum_notes_pieces(sigs_r, False, "fake", sr, bpm, 2500)
    rides = [nt for nt in notes_r if nt["pitch"] == 51]
    crashes = [nt for nt in notes_r if nt["pitch"] == 49]
    check("ride pattern lands 51 not 49", len(rides) >= 5 and len(crashes) <= 1,
          f"ride={len(rides)} crash={len(crashes)}")

    # dust law: a -52dBFS tick on the kick piece lands NO note (it dies at
    # the onset detector or the -46dBFS dust floor — either court is fine)
    dusty = dict(sigs)
    dusty["kick"] = kick + tone_hits(55, (3.9,), 0.05, n, sr, amp=10 ** (-52 / 20.0))
    notes_d, rec_d = ts._drum_notes_pieces(dusty, False, "fake", sr, bpm, 2500)
    k_at_39 = [nt for nt in notes_d if nt["pitch"] == 36
               and abs(nt["start"] - 3.9 / (60.0 / bpm)) < 0.05]
    check("a -52dB tick lands no note", len(k_at_39) == 0, f"{len(k_at_39)}")

    # hh_derived coincidence: cymbal event = the hat itself -> skipped
    hp_hh = hh.copy()
    sigs_h = {"kick": kick, "snare": snare, "toms": np.zeros(n), "hh": hp_hh,
              "cymbals": hp_hh * 0.8}
    notes_h, _ = ts._drum_notes_pieces(sigs_h, True, "fake", sr, bpm, 2500)
    dbl = [nt for nt in notes_h if nt["pitch"] == 51]
    check("derived-hh coincidence skip (no phantom rides)", len(dbl) <= 1,
          f"{len(dbl)}")

    # empty separation -> honest None (caller falls back to bands)
    quiet = {k: np.zeros(n) for k in sigs}
    check("silent pieces -> None (band fallback)",
          ts._drum_notes_pieces(quiet, False, "fake", sr, bpm, 2500) is None)

    # -------------------------------------------------- band fallback intact
    import soundfile as sf
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        wav = os.path.join(td, "drums.wav")
        mix = kick + snare + hh
        sf.write(wav, (mix / (np.abs(mix).max() or 1)) * 0.8, sr)
        os.environ["SOTADAW_NO_DRUMSEP"] = "1"
        nb, rb = ts.drum_notes(wav, bpm)
        del os.environ["SOTADAW_NO_DRUMSEP"]
        check("band path serves under kill switch",
              rb["engine"].startswith("band-lanes") and len(nb) > 10,
              rb["engine"])

    # -------------------------------------------------- table completeness
    import source_kit as sk
    emitted = (36, 38, 42, 43, 46, 47, 49, 50, 51)
    for gm in emitted:
        ok = all(gm in tbl for tbl in
                 (sk.LANE_NAME, sk.LANE_MAX_S, sk.LANE_BAND_HZ,
                  sk.SUB_BAND_HZ, sk.TAIL_S))
        check(f"source_kit tables complete for GM {gm}", ok)
    fam = all(g in sk._ID_FAMILY for g in (43, 47, 50, 51))
    check("identity families cover toms+ride", fam)
    check("tom contract registered", "tom" in sk._ID_CONTRACT)
    # the silent-pitch killer: gm_drums MUST voice every emitted pitch
    gmk = os.path.join(ROOT, "kits", "gm_drums")
    have = {int(f.split("_")[0]) for f in os.listdir(gmk)
            if f[0].isdigit() and f.endswith(".wav")}
    missing = [g for g in emitted if g not in have]
    check("gm_drums voices every emitted pitch", not missing, f"{missing}")

    # -------------------------------------------------- LEN_S coverage
    check("LEN_S covers every emitted pitch",
          all(g in ts.LEN_S for g in emitted))

    # -------------------------------------------------- --real: live self-ID
    if real:
        import drumsep as ds
        mode = ds.available()
        if mode is None:
            print("  (skip --real: no model on this box)")
        else:
            K = os.path.join(ROOT, "kits", "gm_drums")

            def load(p):
                y, s2 = sf.read(p, always_2d=True)
                return y.mean(axis=1)

            def place(smp, ats, nn):
                y = np.zeros(nn)
                for at in ats:
                    i0 = int(at * sr)
                    m = min(len(smp), nn - i0)
                    y[i0:i0 + m] += smp[:m]
                return y

            n2 = int(sr * 8.0)
            srcs = {
                "kick": place(load(os.path.join(K, "36_kick.wav")),
                              np.arange(0.1, 7.5, 0.5), n2),
                "snare": place(load(os.path.join(K, "38_snare.wav")),
                               np.arange(0.35, 7.5, 1.0), n2),
                "hh": place(load(os.path.join(K, "42_hat_closed.wav")),
                            np.arange(0.1, 7.6, 0.25), n2),
                "cymbals": place(load(os.path.join(K, "49_crash.wav")),
                                 (0.6, 4.6), n2),
                "toms": place(load(os.path.join(K, "47_tom_mid.wav")),
                              (1.4, 3.4, 5.4), n2),
            }
            mix = sum(srcs.values())
            pk = np.abs(mix).max() or 1.0
            x = np.stack([mix, mix], axis=1) / pk * 0.7
            pieces = ds.separate_pieces(x, sr)
            for nm in ("kick", "snare", "toms", "hh", "cymbals"):
                if nm not in pieces:
                    continue
                ym = pieces[nm].mean(axis=1)
                cors = {s: float(np.corrcoef(ym, ss / pk * 0.7)[0, 1])
                        for s, ss in srcs.items()}
                best = max(cors, key=cors.get)
                check(f"--real self-ID: slot '{nm}' routes '{best}'",
                      best == nm, f"{cors}")

    print(f"\n{PASS}/{PASS + FAIL} checks passed")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
