#!/usr/bin/env python3
"""THE VOICE MODE's ear (Chezy 2026-07-16: "voice mode just like Claude Code").

The mic button records raw PCM (arecord, 16k mono s16le — raw survives SIGKILL,
a .wav header would not); this tool wraps it and runs faster-whisper LOCALLY
(no cloud, no key) and prints ONE json line the UI parses:

    {"text": "make the drop hit harder", "language": "en", "dur": 3.4, "rtf": 0.18}

Errors also land as json ({"error": "..."}) with exit 0 — the UI must always
get a parseable verdict, never a stack trace to guess at.

    voice_dictate.py --raw take.raw [--rate 16000] [--wav take.wav] [--model small]

Model: SOTADAW_STT_MODEL env > --model > "small" (multilingual — Chezy's asks
mix English + Hebrew names). Device: cuda when torch sees one, else cpu int8.
First call downloads the model to ~/.cache/huggingface (one-time).
"""
import argparse, json, os, struct, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def fail(msg):
    print(json.dumps({"error": str(msg)[:300]}), flush=True)
    sys.exit(0)


def raw_to_wav(raw_path, wav_path, rate, channels=1, sampwidth=2):
    """Wrap headerless s16le PCM in a minimal RIFF header (no deps)."""
    data = open(raw_path, "rb").read()
    if len(data) < sampwidth * rate // 4:          # < 0.25s: nothing was said
        raise RuntimeError("recording too short")
    byte_rate = rate * channels * sampwidth
    with open(wav_path, "wb") as f:
        f.write(b"RIFF" + struct.pack("<I", 36 + len(data)) + b"WAVE")
        f.write(b"fmt " + struct.pack("<IHHIIHH", 16, 1, channels, rate,
                                      byte_rate, channels * sampwidth, sampwidth * 8))
        f.write(b"data" + struct.pack("<I", len(data)) + data)
    return len(data) / float(byte_rate)


def load_model(name):
    """cuda first (ctranslate2 float16), honest cpu int8 fallback — a busy GPU
    must degrade to slow words, never to silence."""
    from faster_whisper import WhisperModel
    for device, compute in (("cuda", "float16"), ("cpu", "int8")):
        try:
            return WhisperModel(name, device=device, compute_type=compute)
        except Exception:
            continue
    return None


def transcribe_one(model, wav, language, dur=0.0, beam=5):
    t0 = time.time()
    segments, info = model.transcribe(wav, language=language, beam_size=max(1, int(beam)),
                                      vad_filter=True,
                                      condition_on_previous_text=False)
    text = " ".join(s.text.strip() for s in segments).strip()
    took = time.time() - t0
    return {
        "text": text,
        "language": getattr(info, "language", "") or "",
        "dur": round(getattr(info, "duration", dur) or dur, 2),
        "rtf": round(took / max(0.1, getattr(info, "duration", dur) or dur or 1.0), 2),
    }


def serve(dirpath, model_name, language):
    """THE WARM EAR: the mic button spawns this the moment listening STARTS, so
    the model loads WHILE the user is speaking; each finished take then costs
    only the decode (~1s), not a 12s process+model boot. File IPC (the app's
    idiom): <dir>/voice_req.json {raw|wav, rate, gen} -> <dir>/voice_res.json
    {gen, text|error, ...}, both atomic. Exits silently after SOTADAW_STT_IDLE_S
    (default 600s) without a request — VRAM is never held hostage."""
    os.makedirs(dirpath, exist_ok=True)
    req_p = os.path.join(dirpath, "voice_req.json")
    res_p = os.path.join(dirpath, "voice_res.json")
    ppid0 = os.getppid()          # the app; when it dies (even -9) we die too
    model = load_model(model_name)
    idle_s = float(os.environ.get("SOTADAW_STT_IDLE_S", "600"))
    last = time.time()
    while time.time() - last < idle_s:
        if os.getppid() != ppid0:  # reparented = the app is gone: release the model
            break
        if not os.path.exists(req_p):
            time.sleep(0.05)
            continue
        try:
            req = json.load(open(req_p))
        except Exception:
            time.sleep(0.05)              # torn write: the rename hasn't landed
            continue
        try:
            os.remove(req_p)
        except OSError:
            pass
        last = time.time()
        out = {"gen": req.get("gen", 0)}
        try:
            if model is None:
                raise RuntimeError("could not load whisper model on cuda or cpu")
            wav, dur = req.get("wav"), 0.0
            if req.get("raw"):
                wav = os.path.splitext(req["raw"])[0] + ".wav"
                dur = raw_to_wav(req["raw"], wav, int(req.get("rate", 16000)))
            if not wav or not os.path.exists(wav):
                raise RuntimeError(f"no such file: {wav}")
            # partials ride beam 1 (the realtime lane); finals keep beam 5
            out.update(transcribe_one(model, wav, language, dur,
                                      beam=req.get("beam", 5)))
        except Exception as e:
            out["error"] = (str(e) if isinstance(e, RuntimeError)
                            else f"{type(e).__name__}: {e}")[:300]
        tmp = res_p + ".tmp"
        json.dump(out, open(tmp, "w"), ensure_ascii=False)
        os.replace(tmp, res_p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", help="headerless s16le PCM from arecord -t raw")
    ap.add_argument("--wav", help="already-wrapped wav (skips --raw wrapping)")
    ap.add_argument("--rate", type=int, default=16000)
    ap.add_argument("--model", default=os.environ.get("SOTADAW_STT_MODEL", "small"))
    ap.add_argument("--language", default=os.environ.get("SOTADAW_STT_LANG", "") or None)
    ap.add_argument("--serve", action="store_true",
                    help="warm-ear daemon: file-IPC requests in --dir")
    ap.add_argument("--dir", default=os.path.join(ROOT, "agent", "ipc"))
    a = ap.parse_args()

    if a.serve:
        serve(a.dir, a.model, a.language)
        return

    if not a.raw and not a.wav:
        fail("need --raw or --wav")
    wav = a.wav
    dur = 0.0
    if a.raw:
        if not os.path.exists(a.raw):
            fail(f"no such file: {a.raw}")
        wav = os.path.splitext(a.raw)[0] + ".wav"
        try:
            dur = raw_to_wav(a.raw, wav, a.rate)
        except RuntimeError as e:
            fail(str(e))
    elif not os.path.exists(wav):
        fail(f"no such file: {wav}")

    model = load_model(a.model)
    if model is None:
        fail("could not load whisper model on cuda or cpu")
    try:
        print(json.dumps(transcribe_one(model, wav, a.language, dur),
                         ensure_ascii=False), flush=True)
    except Exception as e:
        fail(f"transcribe failed: {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
