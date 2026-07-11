#!/usr/bin/env python3
"""EXPORT MASTER with C2PA provenance (the 0.020 gate's last clause).

Renders the song and signs the WAV with a C2PA manifest declaring HOW it was made:
AI-composed-symbolic (SOTA DAW), every source inspectable, voice attribution included.
Self-signed dev cert (generated once into library/c2pa/); DAW-native provenance —
SB-942/ISO 22144-friendly disclosure by default.

  export_master.py <song> [out.wav] [--bits 16] [--require-pass]

--bits 16 dithers the FINAL reduction (TPDF) for CD/delivery; default 24-bit streaming
masters ship UN-dithered (S11-V64; research_mastering_sota.md §2: dither is always last).
"""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")
CERTDIR = os.path.join(ROOT, "library", "c2pa")

def ensure_cert():
    """c2pa needs a chain (not a bare self-signed cert) with digitalSignature KU +
    emailProtection EKU. Build a one-time local mini-CA + end-entity cert."""
    os.makedirs(CERTDIR, exist_ok=True)
    key, chain = os.path.join(CERTDIR, "key.pem"), os.path.join(CERTDIR, "chain.pem")
    if not (os.path.exists(key) and os.path.exists(chain)):
        d = CERTDIR
        def run(*a):
            subprocess.run(a, check=True, capture_output=True, cwd=d)
        run("openssl", "req", "-x509", "-newkey", "ec", "-pkeyopt",
            "ec_paramgen_curve:prime256v1", "-keyout", "ca.key", "-out", "ca.crt",
            "-days", "3650", "-nodes", "-subj", "/O=SOTA DAW local CA/CN=sotadaw-ca",
            "-addext", "basicConstraints=critical,CA:TRUE",
            "-addext", "keyUsage=critical,keyCertSign,cRLSign")
        run("openssl", "req", "-newkey", "ec", "-pkeyopt", "ec_paramgen_curve:prime256v1",
            "-keyout", "key.pem", "-out", "ee.csr", "-nodes",
            "-subj", "/O=SOTA DAW (local dev)/CN=sotadaw-export")
        ext = os.path.join(d, "ee.ext")
        open(ext, "w").write("keyUsage=critical,digitalSignature\n"
                             "extendedKeyUsage=emailProtection\n"
                             "basicConstraints=CA:FALSE\n")
        run("openssl", "x509", "-req", "-in", "ee.csr", "-CA", "ca.crt", "-CAkey", "ca.key",
            "-CAcreateserial", "-out", "ee.crt", "-days", "3650", "-extfile", "ee.ext")
        open(chain, "w").write(open(os.path.join(d, "ee.crt")).read()
                               + open(os.path.join(d, "ca.crt")).read())
    return key, chain

def _tpdf_dither_16(in_wav, out_wav):
    """24-bit -> 16-bit with TPDF (triangular) dither — the FINAL bit-depth reduction ONLY
    (S11-V64). Decorrelates quantization distortion into benign noise at the new LSB. Numerics
    are convention (research §7 UNVERIFIED); TPDF is the safe minimum. Never dither twice."""
    import numpy as np
    from scipy.io import wavfile
    sr, x = wavfile.read(in_wav)
    if x.dtype == np.int16:
        xf = x.astype(np.float64) / 32768.0
    elif x.dtype == np.int32:
        xf = x.astype(np.float64) / 2147483648.0     # scipy reads 24-bit PCM left-justified in int32
    else:
        xf = x.astype(np.float64)
    q = 1.0 / 32768.0                                 # 16-bit LSB
    d = (np.random.random(xf.shape) - np.random.random(xf.shape)) * q   # triangular PDF over [-q, q]
    yi = np.clip(np.round((xf + d) * 32768.0), -32768, 32767).astype(np.int16)
    wavfile.write(out_wav, sr, yi)


def export(song_name, out=None, require_pass=False, bits=24):
    song_path = os.path.join(ROOT, "songs", f"{song_name}.json")
    song = json.load(open(song_path))
    out = out or os.path.join(ROOT, "songs", f"{song_name}_master.wav")
    tmp = out + ".render.wav"
    r = subprocess.run([M1, "render", song_path, tmp], capture_output=True, text=True)
    if "ok=1" not in r.stdout + r.stderr:
        return print(f"render failed: {(r.stdout + r.stderr)[-300:]}")

    # W109 THE MEASURED CEILING: fx_truepeak's output-vs-ceiling wanders
    # with material (measured +0.56 over on a dense sung mix, -0.67 under
    # on a sparse probe — the contract is loose). A MASTER meets spec by
    # MEASUREMENT: if the render's dBTP overshoots the wall's stated
    # ceiling, lower the ceiling by the overshoot (+0.05 guard) on a COPY
    # and re-render ONCE. The song file itself is never touched.
    try:
        import analyze2 as _an
        _m0 = _an.analyze(tmp)
        _walls = [f for f in (song.get("master") or [])
                  if f.get("id") == "fx_truepeak"]
        if _walls:
            _ceil = float(_walls[-1].get("params", {}).get("ceiling", -1.2))
            _tp = float(_m0.get("true_peak_dbtp", -99.0))
            if _tp > _ceil + 0.05:
                _over = _tp - _ceil
                _fix = json.loads(json.dumps(song))
                for f in _fix["master"]:
                    if f.get("id") == "fx_truepeak":
                        f.setdefault("params", {})["ceiling"] = round(
                            _ceil - _over - 0.05, 2)
                _fixp = song_path + ".export_fix.json"
                json.dump(_fix, open(_fixp, "w"))
                r2 = subprocess.run([M1, "render", _fixp, tmp],
                                    capture_output=True, text=True)
                os.remove(_fixp)
                _m1 = _an.analyze(tmp)
                print(f"measured ceiling: dBTP {_tp:+.2f} over stated {_ceil:+.2f} "
                      f"-> wall re-aimed {_ceil - _over - 0.05:+.2f}, "
                      f"now {float(_m1.get('true_peak_dbtp', -99)):+.2f}")
    except Exception as _ce:
        print(f"measured-ceiling pass skipped ({_ce})")

    sign_src, bit_depth, dithered = tmp, 24, False

    # THE PERFECTING STAMP: judge the EXACT audio being signed and carry the verdict
    # in the provenance manifest — a master that says what it measures.
    verdict = None
    try:
        sys.path.insert(0, os.path.join(ROOT, "tools"))
        from master_report import build_report
        long_form = float(song.get("lengthBars", 0)) * 4.0 * 60.0 \
                    / max(float(song.get("bpm", 120)), 1.0) > 20 * 60   # >20min = a SET
        rep = build_report(song_path=song_path, wav=tmp,
                           genre=(song.get("_loop") or {}).get("genre"), no_render=True,
                           profile="set" if long_form else None)
        if "error" not in rep:
            verdict = {"pass": rep["pass"], "score": rep["score"], "target": rep["target"],
                       "fix_first": rep["fix_first"],
                       "lufs_integrated": rep["metrics"]["lufs"],
                       "true_peak_dbtp": rep["metrics"]["true_peak_dbtp"],
                       "clipped_samples": rep["metrics"]["clipped"]}
            print(("verdict: PASS" if rep["pass"] else f"verdict: FIX {rep['fix_first']}")
                  + f" (score {rep['score']}, {rep['target']})")
            if require_pass and not rep["pass"]:
                os.remove(tmp)
                return print("export refused (--require-pass): run auto_master / fix sources first")
    except Exception as e:
        print(f"verdict unavailable ({e}) — exporting unstamped")

    if int(bits) == 16:
        tmp16 = out + ".dither16.wav"
        try:
            _tpdf_dither_16(tmp, tmp16)
            sign_src, bit_depth, dithered = tmp16, 16, True
            print("dither: 24-bit -> 16-bit TPDF (CD/delivery; streaming masters stay 24-bit)")
        except Exception as e:
            print(f"dither failed ({e}) — shipping 24-bit")

    voices = sorted({t.get("comment") for t in song["tracks"]
                     if str(t.get("comment", "")).startswith("voice:")})
    manifest = {
        "claim_generator_info": [{"name": "SOTA DAW", "version": "0.020"}],
        "title": song_name,
        "assertions": [
            {"label": "c2pa.actions", "data": {"actions": [
                {"action": "c2pa.created",
                 "digitalSourceType": "http://cv.iptc.org/newscodes/digitalsourcetype/compositeWithTrainedAlgorithmicMedia",
                 "softwareAgent": {"name": "SOTA DAW producer-agent"}}]}},
            {"label": "org.sotadaw.symbolic_sources", "data": {
                "statement": "Fully symbolic composition: every sound derives from inspectable "
                             "sources (note lists, Faust DSP code, automation curves) in the "
                             "bundled song.json. No black-box audio generation.",
                "bpm": song.get("bpm"), "key": song.get("key"),
                "tracks": [t["name"] for t in song["tracks"]],
                "voice_attribution": voices,
                "delivery": {"bit_depth": bit_depth, "dithered_tpdf": dithered}}},
        ],
    }
    if verdict is not None:
        manifest["assertions"].append(
            {"label": "org.sotadaw.mastering_verdict", "data": {
                "statement": "Measured verdict of THIS audio at signing time "
                             "(tools/master_report.py vs the named target lane).",
                **verdict}})
    key, crt = ensure_cert()
    from c2pa import Builder, C2paSignerInfo, Signer
    signer = Signer.from_info(C2paSignerInfo(
        alg=b"es256", sign_cert=open(crt, "rb").read(), private_key=open(key, "rb").read(),
        ta_url=b"http://timestamp.digicert.com"))
    b = Builder(json.dumps(manifest))
    b.sign_file(sign_src, out, signer)
    os.remove(tmp)
    if sign_src != tmp and os.path.exists(sign_src):
        os.remove(sign_src)
    size = os.path.getsize(out)
    print(f"OK: {out} ({size//1024} KB) — C2PA-signed master "
          f"({bit_depth}-bit{'/TPDF-dithered' if dithered else ''}; AI-composed-symbolic "
          f"declared{'; ' + '; '.join(v for v in voices if v) if voices else ''})")

if __name__ == "__main__":
    argv = sys.argv[1:]
    bits = 24
    if "--bits" in argv:
        i = argv.index("--bits")
        bits = int(argv[i + 1]); del argv[i:i + 2]
    args = [a for a in argv if a != "--require-pass"]
    export(args[0], args[1] if len(args) > 1 else None,
           require_pass="--require-pass" in sys.argv, bits=bits)
