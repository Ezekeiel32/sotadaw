#!/usr/bin/env python3
"""P2/P4 gate (PORT_SPEC.md): a render is REAL AUDIO or the job is red.
Usage: ci_wav_gate.py <wav> [min_secs]  — 24-bit law: branch on sampwidth."""
import sys, wave

wav_path = sys.argv[1]
min_secs = float(sys.argv[2]) if len(sys.argv) > 2 else 5.0
w = wave.open(wav_path, "rb")
n, sw, ch, sr = w.getnframes(), w.getsampwidth(), w.getnchannels(), w.getframerate()
raw = w.readframes(min(n, sr * 10))
peak = 0
if sw == 3:
    for i in range(0, len(raw) - 2, 3 * ch):
        peak = max(peak, abs(int.from_bytes(raw[i:i + 3], "little", signed=True)))
    full = float(2 ** 23)
elif sw == 2:
    import struct
    vals = struct.unpack("<%dh" % (len(raw) // 2), raw)
    peak = max(abs(v) for v in vals)
    full = float(2 ** 15)
else:
    sys.exit(f"unexpected sampwidth {sw}")
secs = n / sr
print(f"secs={secs:.2f} sr={sr} ch={ch} sampwidth={sw} peak={peak/full:.4f}")
assert secs >= min_secs, f"render too short ({secs:.2f}s < {min_secs}s)"
assert peak / full > 0.05, "render is (near) silent"
print("WAV GATE: REAL AUDIO")
