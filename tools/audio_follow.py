#!/usr/bin/env python3
"""THE AUDIO EAR — any mic / guitar / bass / harmonica drives THE FOLLOW.

jam_live --human eats NOTES; real instruments give AUDIO. This is the bridge: a
LIGHT streaming monophonic tracker (numpy YIN per hop + energy gate + stability
segmentation) that turns a wav — a GROWING file being written live (arecord, the
app's capture, anything) or a finished take — into the song-grammar notes JSONL
the band already follows. Beats are SET-relative via --bpm/--offset-beat.

  audio_follow.py take.wav --bpm 126 --out human.jsonl                # offline
  audio_follow.py live.wav --bpm 126 --out human.jsonl --stream       # growing file
  audio_follow.py --record default --bpm 126 --out human.jsonl        # mic via arecord

Scope law (the retune lesson): YIN is the DRY/DI happy case — close-mic'd voice,
guitar DI, harmonica. Wet/bleedy sources want the fcpe rail (offline stems path);
that is the documented upgrade seam, the JSONL contract stays identical.
The growing-file reader parses the RIFF header ONCE and then streams the data
chunk by FILE SIZE — a live writer's stale header nframes is ignored on purpose.
"""
import argparse
import json
import math
import os
import struct
import subprocess
import sys
import time

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ------------------------------------------------------------------ wav stream
def wav_header(path):
    """Parse RIFF once: (sr, channels, sampwidth, data_offset). Tolerates a
    growing file (data-chunk size ignored — the stream trusts the file size)."""
    with open(path, "rb") as f:
        if f.read(4) != b"RIFF":
            raise ValueError("not RIFF")
        f.seek(8)
        if f.read(4) != b"WAVE":
            raise ValueError("not WAVE")
        sr = ch = sw = None
        while True:
            hdr = f.read(8)
            if len(hdr) < 8:
                raise ValueError("no data chunk yet")
            cid, sz = hdr[:4], struct.unpack("<I", hdr[4:])[0]
            if cid == b"fmt ":
                fmt = f.read(sz)
                ch = struct.unpack("<H", fmt[2:4])[0]
                sr = struct.unpack("<I", fmt[4:8])[0]
                sw = struct.unpack("<H", fmt[14:16])[0] // 8
            elif cid == b"data":
                if sr is None:
                    raise ValueError("data before fmt")
                return sr, ch, sw, f.tell()
            else:
                f.seek(sz + (sz & 1), 1)


def read_pcm(path, byte_off, sr, ch, sw):
    """Fresh samples past byte_off (whole frames only) -> (mono float64, new_off)."""
    size = os.path.getsize(path)
    frame_b = ch * sw
    avail = ((size - byte_off) // frame_b) * frame_b
    if avail <= 0:
        return np.zeros(0), byte_off
    with open(path, "rb") as f:
        f.seek(byte_off)
        raw = f.read(avail)
    if sw == 3:
        a = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3)
        x = (a[:, 0].astype(np.int32) | (a[:, 1].astype(np.int32) << 8)
             | (a[:, 2].astype(np.int32) << 16))
        x = np.where(x & 0x800000, x - 0x1000000, x).astype(np.float64) / 8388608.0
    elif sw == 2:
        x = np.frombuffer(raw, dtype="<i2").astype(np.float64) / 32768.0
    else:
        raise ValueError(f"sampwidth {sw} unsupported")
    return x.reshape(-1, ch).mean(axis=1), byte_off + avail


# ------------------------------------------------------------------------- yin
def yin_f0(frame, sr, fmin=60.0, fmax=1000.0, thr=0.15):
    """(f0_hz, cmnd_min) — 0.0 Hz when unvoiced. Vectorized CMND YIN with
    parabolic tau refinement; the local-min descent guards the classic
    subharmonic pick at the threshold crossing."""
    x = frame.astype(np.float64)
    n = x.size
    tau_min = max(2, int(sr // fmax))
    tau_max = min(int(sr // fmin), n - 2)
    if tau_max <= tau_min + 2:
        return 0.0, 1.0
    X = np.fft.rfft(x, 2 * n)
    acf = np.fft.irfft(X * np.conj(X))[:tau_max + 1]
    e = np.concatenate(([0.0], np.cumsum(x * x)))
    taus = np.arange(tau_max + 1)
    d = e[n - taus] + (e[n] - e[taus]) - 2.0 * acf
    d = np.maximum(d, 0.0)
    cmnd = np.ones(tau_max + 1)
    cum = np.cumsum(d[1:])
    nz = cum > 1e-12
    cmnd[1:][nz] = d[1:][nz] * taus[1:][nz] / cum[nz]
    region = cmnd[tau_min:tau_max + 1]
    under = np.where(region < thr)[0]
    if under.size:
        tau = tau_min + int(under[0])
        while tau + 1 <= tau_max and cmnd[tau + 1] < cmnd[tau]:
            tau += 1
    else:
        tau = tau_min + int(np.argmin(region))
        if float(region.min()) > 0.35:
            return 0.0, float(region.min())
    if 1 <= tau < tau_max:
        a, b, c = cmnd[tau - 1], cmnd[tau], cmnd[tau + 1]
        den = a - 2.0 * b + c
        tau_f = tau + (0.5 * (a - c) / den if abs(den) > 1e-12 else 0.0)
    else:
        tau_f = float(tau)
    if tau_f <= 0:
        return 0.0, 1.0
    return sr / tau_f, float(cmnd[tau])


# ------------------------------------------------------------- note tracker
FRAME = 2048
HOP = 512


class NoteTracker:
    """Hop-fed segmentation: stability opens a note, silence/motion closes it.
    Completed notes come back in song grammar with SET-relative beats."""

    def __init__(self, sr, bpm, offset_beat=0.0, gate_db=-45.0):
        self.sr, self.bpm = sr, bpm
        self.offset = offset_beat
        self.gate = gate_db
        self.buf = np.zeros(0)
        self.pos = 0                        # absolute sample index of buf[0]
        self.cand = []                      # [(t_sec, midi_float, rms_db)]
        self.cur = None                     # open note dict
        self.quiet = 0
        self.out = []

    def _beats(self, t_sec):
        return round(self.offset + t_sec * self.bpm / 60.0, 4)

    def _close(self, t_sec):
        if self.cur is not None:
            n = self.cur
            length = self._beats(t_sec) - n["start"]
            if length >= 0.06:              # ~a 64th at 120: real, not a blip
                midi = int(round(float(np.median(n["midis"]))))
                peak = max(n["dbs"])
                vel = max(0.2, min(1.0, (peak + 40.0) / 34.0))
                self.out.append({"start": n["start"], "len": round(length, 4),
                                 "pitch": midi, "vel": round(vel, 3)})
        self.cur = None

    # ONE SEGMENTATION LAW, TWO EARS: YIN hops and fcpe frames both land here
    def frame_in (self, t_sec, voiced, midi_f, db):
        if voiced:
            self.quiet = 0
            if self.cur is not None:
                ref = float(np.median(self.cur["midis"][-8:]))
                if abs(midi_f - ref) <= 0.8:
                    self.cur["midis"].append(midi_f)
                    self.cur["dbs"].append(db)
                else:                    # the hand moved: close + re-arm
                    self._close(t_sec)
                    self.cand = [(t_sec, midi_f, db)]
            else:
                self.cand.append((t_sec, midi_f, db))
                ref = float(np.median([m for _, m, _ in self.cand[-3:]]))
                stable = [c for c in self.cand[-3:] if abs(c[1] - ref) <= 0.6]
                if len(stable) >= 3:     # ~35ms of agreement = a note is born
                    self.cur = {"start": self._beats(stable[0][0]),
                                "midis": [c[1] for c in stable],
                                "dbs": [c[2] for c in stable]}
                    self.cand = []
        else:
            self.cand = self.cand[-2:]
            self.quiet += 1
            if self.cur is not None and self.quiet >= 3:
                self._close(t_sec)

    def feed(self, samples):
        """Feed fresh mono samples; returns notes COMPLETED by this feed."""
        done_before = len(self.out)
        self.buf = np.concatenate([self.buf, samples])
        while self.buf.size >= FRAME:
            frame = self.buf[:FRAME]
            t_sec = self.pos / self.sr
            rms = float(np.sqrt(np.mean(frame * frame)))
            db = 20.0 * math.log10(rms + 1e-12)
            f0, conf = (0.0, 1.0) if db < self.gate else yin_f0(frame, self.sr)
            voiced = f0 > 0.0 and conf < 0.25
            self.frame_in (t_sec, voiced,
                           69.0 + 12.0 * math.log2(f0 / 440.0) if voiced else 0.0, db)
            self.buf = self.buf[HOP:]
            self.pos += HOP
        return self.out[done_before:]

    def flush(self):
        self._close(self.pos / self.sr)
        return self.out


# ---------------------------------------------------------------------- follow
def follow(path, bpm, out_path, offset_beat=0.0, stream=False, poll=0.1,
           idle_sec=2.0, max_sec=None, gate_db=-45.0):
    """Track `path` into `out_path` (JSONL append, one note per completed note —
    the moment it ends, not when the file does). Returns all notes."""
    t_wait0 = time.monotonic()
    while True:                              # a live writer may still be on the header
        try:
            sr, ch, sw, off = wav_header(path)
            break
        except (OSError, ValueError):
            if not stream or time.monotonic() - t_wait0 > 10.0:
                raise
            time.sleep(poll)
    tr = NoteTracker(sr, bpm, offset_beat, gate_db)
    idle = 0.0
    emitted = 0
    t0 = time.monotonic()
    with open(out_path, "a") as f:
        while True:
            x, off = read_pcm(path, off, sr, ch, sw)
            if x.size:
                idle = 0.0
                for n in tr.feed(x):
                    f.write(json.dumps(n) + "\n")
                    f.flush()
                    emitted += 1
            elif not stream:
                break
            else:
                idle += poll
                if idle >= idle_sec:
                    break
                time.sleep(poll)
            if max_sec is not None and time.monotonic() - t0 > max_sec:
                break
        for n in tr.flush()[emitted:]:       # the take's last note closes at EOF
            f.write(json.dumps(n) + "\n")
    return tr.out


def follow_fcpe(path, bpm, out_path, offset_beat=0.0, gate_db=-45.0):
    """THE WET EAR (offline takes): fcpe f0 over the WHOLE take -> the SAME note
    segmentation law as the YIN streamer. For reverby/bleedy sources where YIN
    drops notes — the retune lesson: fcpe holds ~98% on wet stems. Loads the
    neural rail (GPU with CPU fallback), so this is the FILE-mode upgrade;
    --stream keeps the light YIN ear."""
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import transcribe_stems as TS
    sr, ch, sw, off = wav_header(path)
    x, _ = read_pcm(path, off, sr, ch, sw)
    if x.size == 0:
        open(out_path, "a").close()
        return []
    # 16k mono for the model (linear resample is plenty for f0)
    n16 = int(round(len(x) * 16000.0 / sr))
    y16 = np.interp(np.linspace(0.0, len(x) - 1.0, n16),
                    np.arange(len(x)), x).astype(np.float32)
    f0, _dev = TS._fcpe_f0(y16, 60.0, 1000.0)
    f0 = TS._octave_guard(f0)
    hop_s = 0.010                                # the rail's 10ms grid
    tr = NoteTracker(sr, bpm, offset_beat, gate_db)
    for i in range(len(f0)):
        t = i * hop_s
        a0, a1 = int(t * sr), min(len(x), int((t + hop_s) * sr) + 1)
        seg = x[a0:a1]
        db = 20.0 * math.log10(float(np.sqrt(np.mean(seg * seg))) + 1e-12) if seg.size else -120.0
        v = float(f0[i])
        voiced = v > 0.0 and db >= gate_db
        tr.frame_in (t, voiced, 69.0 + 12.0 * math.log2(v / 440.0) if voiced else 0.0, db)
    notes = tr.flush()
    with open(out_path, "a") as f:
        for n in notes:
            f.write(json.dumps(n) + "\n")
    return notes


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("wav", nargs="?", help="input wav (growing or finished)")
    ap.add_argument("--record", default=None,
                    help="ALSA device: capture the mic yourself via arecord and follow it")
    ap.add_argument("--bpm", type=float, required=True)
    ap.add_argument("--out", required=True, help="human-notes JSONL (jam_live --human)")
    ap.add_argument("--offset-beat", type=float, default=0.0,
                    help="where in the SET this file's t=0 sits (negative = pre-roll)")
    ap.add_argument("--stream", action="store_true", help="the wav is GROWING: poll it")
    ap.add_argument("--gate-db", type=float, default=-45.0)
    ap.add_argument("--idle-sec", type=float, default=2.0)
    ap.add_argument("--max-sec", type=float, default=None)
    ap.add_argument("--f0", choices=("yin", "fcpe"), default="yin",
                    help="yin = light realtime ear (dry/DI); fcpe = THE WET EAR "
                         "(neural, offline takes only — not --stream)")
    a = ap.parse_args()
    if a.f0 == "fcpe" and (a.stream or a.record):
        ap.error("--f0 fcpe is the OFFLINE wet ear; --stream/--record keep the YIN ear")
    path = a.wav
    rec = None
    if a.record:
        path = a.wav or os.path.join(ROOT, "songs", ".audio_follow_live.wav")
        rec = subprocess.Popen(["arecord", "-D", a.record, "-f", "S16_LE", "-r", "44100",
                                "-c", "1", "-t", "wav", path],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        a.stream = True
    if not path:
        ap.error("give a wav or --record <device>")
    try:
        if a.f0 == "fcpe":
            notes = follow_fcpe(path, a.bpm, a.out, a.offset_beat, gate_db=a.gate_db)
        else:
            notes = follow(path, a.bpm, a.out, a.offset_beat, a.stream,
                           idle_sec=a.idle_sec, max_sec=a.max_sec, gate_db=a.gate_db)
    finally:
        if rec is not None:
            rec.terminate()
    print(f"[audio-follow] {len(notes)} notes -> {a.out}")


if __name__ == "__main__":
    main()
