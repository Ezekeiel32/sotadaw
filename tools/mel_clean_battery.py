#!/usr/bin/env python3
"""DRY TRUTH battery — pure/offline proofs for tools/mel_clean.py (#51).

Model files are NOT required (the live legs are --real only, and --real
skips honestly without CUDA), so the guardian suite stays green anywhere.

    .venv/bin/python tools/mel_clean_battery.py          # pure (suite leg)
    .venv/bin/python tools/mel_clean_battery.py --real   # + live dereverb legs (GPU)
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


def main():
    real = "--real" in sys.argv

    # -------------------------------------------------- registry + honesty
    os.environ["SOTADAW_NO_DRYCLEAN"] = "1"
    import mel_clean as mc
    check("registry has the three cleaners",
          set(mc.MODELS) == {"dereverb", "denoise", "aspiration"})
    for m, spec in mc.MODELS.items():
        check(f"registry[{m}] pins ckpt bytes + target names",
              spec.get("bytes", 0) > 1e8 and spec.get("target")
              and spec.get("residual"))
    check("kill switch: available() False",
          mc.available("dereverb", need_gpu=False) is False)
    del os.environ["SOTADAW_NO_DRYCLEAN"]
    check("unknown model -> False", mc.available("nope") is False)

    # missing files -> honest False (empty MSS dir override)
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        old = mc.MSS_DIR
        mc.MSS_DIR = td
        check("missing files -> available False",
              mc.available("dereverb", need_gpu=False) is False)
        check("clean_cached honest None when unavailable",
              mc.clean_cached("/nonexistent.wav") is None)
        mc.MSS_DIR = old

    # -------------------------------------------- THE DRY-TWIN HEALTH LAW
    # (2026-07-15 goldenbrown autopsy: anvuew dereverb is VOCAL-target — on
    # an instrumental 'other' stem it returns ~silence; three imports
    # transcribed a -81dB corpse. A twin that lost the music is refused.)
    sr = 44100
    t = np.linspace(0, 2, sr * 2, endpoint=False)
    wet = (0.3 * np.sin(2 * np.pi * 440 * t)).astype(np.float64)
    ok, h = mc.dry_twin_health(wet, wet * 0.5, sr)
    check("health: -6dB twin passes", ok and abs(h["retention_db"] + 6) < 1,
          f"{h}")
    ok, h = mc.dry_twin_health(wet, wet * 0.001, sr)
    check("health: -60dB twin rejected", not ok, f"{h}")
    ok, _ = mc.dry_twin_health(wet * 0.0, wet * 0.0, sr)
    check("health: silent stem judges nothing", ok)
    check("aspiration exempt from body gate",
          mc.MODELS["aspiration"].get("expect_body") is False)
    check("dereverb/denoise expect body",
          mc.MODELS["dereverb"].get("expect_body") is True
          and mc.MODELS["denoise"].get("expect_body") is True)

    import json
    import soundfile as sf
    with tempfile.TemporaryDirectory() as td:
        wavp = os.path.join(td, "other.wav")
        sf.write(wavp, np.stack([wet, wet], 1).astype(np.float32), sr,
                 subtype="FLOAT")
        corpse = os.path.join(td, "other_dry.wav")
        sf.write(corpse, np.zeros((len(wet), 2), np.float32), sr,
                 subtype="FLOAT")
        got = mc.clean_cached(wavp, "dereverb", say=lambda *a, **k: None)
        check("cached corpse judged once -> refused + evicted",
              got is None and not os.path.exists(corpse))
        v = json.load(open(corpse + ".verdict.json"))
        check("rejection verdict persisted (no GPU re-pay)",
              v.get("ok") is False and v.get("retention_db", 0) < -50)
        got2 = mc.clean_cached(wavp, "dereverb", say=lambda *a, **k: None)
        check("standing rejection honored", got2 is None)

        healthy = os.path.join(td, "voc.wav")
        sf.write(healthy, np.stack([wet, wet], 1).astype(np.float32), sr,
                 subtype="FLOAT")
        twin = os.path.join(td, "voc_dry.wav")
        sf.write(twin, np.stack([wet, wet], 1).astype(np.float32) * 0.5, sr,
                 subtype="FLOAT")
        got3 = mc.clean_cached(healthy, "dereverb", say=lambda *a, **k: None)
        check("healthy cached twin passes the gate", got3 == twin)

        nuked2 = os.path.join(td, "n.wav")
        sf.write(nuked2, np.stack([wet, wet], 1).astype(np.float32), sr,
                 subtype="FLOAT")
        twin2 = os.path.join(td, "n_dry.wav")
        sf.write(twin2, np.zeros((len(wet), 2), np.float32), sr,
                 subtype="FLOAT")
        os.environ["SOTADAW_NO_DRYGATE"] = "1"
        got4 = mc.clean_cached(nuked2, "dereverb", say=lambda *a, **k: None)
        del os.environ["SOTADAW_NO_DRYGATE"]
        check("SOTADAW_NO_DRYGATE=1 bypasses (old law)", got4 == twin2)

    # vendored arch imports + constructs from each present yaml (cheap dims)
    sys.path.insert(0, os.path.join(ROOT, "third_party", "bs_roformer"))
    try:
        from mel_band_roformer import MelBandRoformer
        net = MelBandRoformer(dim=32, depth=1, stereo=True, num_stems=1,
                              time_transformer_depth=1,
                              freq_transformer_depth=1, num_bands=60,
                              sample_rate=44100, stft_n_fft=2048,
                              stft_hop_length=441, stft_win_length=2048,
                              mask_estimator_depth=1)
        n_params = sum(p.numel() for p in net.parameters())
        check("vendored MelBandRoformer constructs", n_params > 1000,
              f"{n_params}")
    except Exception as e:
        check("vendored MelBandRoformer constructs", False, f"{e}")

    # -------------------------------------------------- --real (GPU) legs
    if real:
        import torch
        if not (mc.available("dereverb", need_gpu=True)
                and torch.cuda.is_available()):
            print("  (skip --real: no dereverb model or no CUDA)")
        else:
            import soundfile as sf
            stem = os.path.join(ROOT, "songs", "opptical_stems", "vocals.wav")
            if not os.path.exists(stem):
                print("  (skip --real: no real stem on this box)")
            else:
                SR = 44100
                x0, sr = sf.read(stem, always_2d=True)
                seg = x0[int(20 * SR):int(28 * SR), :2]
                tgt, res = mc.clean(seg, SR, model="dereverb",
                                    device="cuda", precision="fp16")
                closure = float(np.abs(seg - (tgt + res)).max())
                check("--real closure law exact", closure < 1e-9,
                      f"{closure:.2e}")
                e_in = float(np.mean(seg ** 2))
                e_rm = float(np.mean(res ** 2))
                check("--real removes real ambience (not identity)",
                      e_rm > e_in * 1e-4,
                      f"in {e_in:.2e} removed {e_rm:.2e}")
                check("--real target quieter than input",
                      float(np.mean(tgt ** 2)) <= e_in * 1.02)

    print(f"\n{PASS}/{PASS + FAIL} checks passed")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
