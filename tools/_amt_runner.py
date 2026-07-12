#!/usr/bin/env python3
"""YourMT3+ inference runner — EXECUTES IN .venv_mt3, never the main venv.

The space pins transformers==4.45.1 (the main venv rides 5.x for other
rails) — isolation by construction: tools/other_amt.py spawns THIS file with
.venv_mt3/bin/python. Loads the YPTF+Single (noPS) checkpoint from the
cloned HF space (~/.cache/sotadaw/yourmt3, code + LFS ckpts) with the
space's own arg vector, transcribes one wav, moves the program-labeled MIDI
to the requested path.

    .venv_mt3/bin/python tools/_amt_runner.py in.wav out.mid [cuda|cpu]
"""
import os
import sys

SPACE = os.path.expanduser("~/.cache/sotadaw/yourmt3")


def main():
    in_wav = os.path.abspath(sys.argv[1])
    out_mid = os.path.abspath(sys.argv[2])
    device = sys.argv[3] if len(sys.argv) > 3 else "cuda"
    os.chdir(SPACE)
    sys.path[:0] = [SPACE, os.path.join(SPACE, "amt", "src")]
    import torch
    if device == "cuda" and not torch.cuda.is_available():
        device = "cpu"
    from model_helper import load_model_checkpoint, transcribe
    # the app.py vector for YPTF+Single (noPS) — the ckpt in the clone
    args = ["ptf_all_cross_rebal5_mirst_xk2_edr005_attend_c_full_plus_b100@model.ckpt",
            "-p", "2024", "-enc", "perceiver-tf", "-ac", "spec",
            "-hop", "300", "-atc", "1",
            "-pr", "16" if device == "cuda" else "32"]
    model = load_model_checkpoint(args=args, device="cpu")
    model.to(device)
    try:
        mid = transcribe(model, {"filepath": in_wav, "track_name": "amt_out"})
    except torch.cuda.OutOfMemoryError:
        print("[amt] cuda OOM -> cpu retry", flush=True)
        model.to("cpu")
        torch.cuda.empty_cache()
        mid = transcribe(model, {"filepath": in_wav, "track_name": "amt_out"})
    os.replace(mid, out_mid)
    print(f"AMT-MID {out_mid}")


if __name__ == "__main__":
    main()
