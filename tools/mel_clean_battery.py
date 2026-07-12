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
