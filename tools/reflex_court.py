#!/usr/bin/env python3
"""THE BRAIN BR-B — THE REFLEXES (docs/SPEC_THE_BRAIN.md PART IV).

Real-time diagnosis on streams that already exist:

R1 — LIVE COURTS on the 10 Hz EarsTap frames (agent/ipc/ears.jsonl,
     {t, playing, rms_db[2], peak_db[], crest_db, bands_db[4], beat}).
     Universal physics only — no genre context lives in a frame:
     ceiling, dead-output, crest-collapse, flatline, lowmid mud, stereo lean.
R2 — IN-FLIGHT advisory on the ghost stream: while a take STREAMS, new notes
     on melodic lanes are key-scanned (theory.py) and one honest activity
     line fires early — the end-of-run court still owns the verdict + heal.

LAWS:
- The kernel (Reflex.feed / InflightScan.feed_doc) is PURE and clocked by
  frame/doc time — batteries replay streams deterministically.
- COALESCED: one event per kind per cooldown; capped lines per run. A reflex
  that storms is a lag disease, not a feature (lag-campaign law).
- FAIL-OPEN: a reflex may never break a run, a render, or a prompt.
- ADVISORY-FIRST: R2 never mutates; heals stay at the end-of-run court.
- The audio thread is untouched — we read the tap's file, nothing more.
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
DEF_ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

STATE_NAME = "reflex_state.json"
LOG_NAME = "reflex.jsonl"

# ---------------------------------------------------------------- R1 kernel
CLIP_DB = -0.3          # master frame peak above this = at the ceiling
SILENCE_DB = -55.0      # playing but under this = dead output
CREST_MIN = 6.0         # sustained crest under this = squashed
FLAT_SPAN = 0.8         # rms span under this across FLAT_NEED = static level
MUD_MARGIN = 6.0        # lowmid above every other band by this = mud
LEAN_DB = 6.0           # |L-R| above this = stereo lean
COOLDOWN_S = 15.0       # per-kind re-fire gate

_NEED = {"ceiling": 0.2, "dead": 2.0, "crest": 3.0,
         "flatline": 8.0, "mud": 2.0, "lean": 3.0}
_SEV = {"ceiling": "hard", "dead": "hard", "crest": "advice",
        "flatline": "advice", "mud": "advice", "lean": "advice"}


class Reflex:
    """Sustained-condition state machine over live frames. feed(frame) returns
    the events that fire on THIS frame (usually [])."""

    def __init__(self):
        self.since = {}          # kind -> t when condition began
        self.last_fire = {}      # kind -> t of last event
        self.rms_hist = []       # (t, mean_rms) for flatline

    @staticmethod
    def _facts(fr):
        rms = fr.get("rms_db") or [-120.0, -120.0]
        pk = fr.get("peak_db") or [-120.0]
        bands = fr.get("bands_db") or [-120.0] * 4
        if len(bands) < 4:
            bands = list(bands) + [-120.0] * (4 - len(bands))
        return {"t": float(fr.get("t", 0.0)), "playing": bool(fr.get("playing")),
                "rms_l": float(rms[0]), "rms_r": float(rms[-1]),
                "rms": (float(rms[0]) + float(rms[-1])) / 2.0,
                "peak": max(float(x) for x in pk),
                "crest": float(fr.get("crest_db", 0.0)), "bands": bands,
                "beat": float(fr.get("beat", 0.0))}

    def _conditions(self, f):
        yield "ceiling", f["peak"] >= CLIP_DB
        # PRE-ROLL PARDON (first live wolf, 2026-07-16: 'dead output' convicted
        # at beat -0.9 — the count-in is silent BY DESIGN; a take that hasn't
        # reached beat 0.5 has nothing to answer for)
        yield "dead", f["playing"] and f["rms"] < SILENCE_DB and f["beat"] >= 0.5
        yield "crest", f["playing"] and f["rms"] > SILENCE_DB and f["crest"] < CREST_MIN
        yield "mud", (f["playing"] and f["rms"] > SILENCE_DB and
                      f["bands"][1] - max(f["bands"][0], f["bands"][2], f["bands"][3])
                      > MUD_MARGIN)
        yield "lean", (f["playing"] and f["rms"] > SILENCE_DB and
                       abs(f["rms_l"] - f["rms_r"]) > LEAN_DB)
        # flatline rides rms history, judged below
        hist = [(t, r) for (t, r) in self.rms_hist if f["t"] - t <= _NEED["flatline"]]
        hist.append((f["t"], f["rms"]))
        self.rms_hist = hist[-160:]
        flat = False
        if f["playing"] and f["rms"] > -50.0 and len(hist) >= 40:
            span = max(r for _, r in hist) - min(r for _, r in hist)
            covered = hist[-1][0] - hist[0][0]
            flat = span < FLAT_SPAN and covered >= _NEED["flatline"] * 0.9
        yield "flatline", flat

    def _line(self, kind, f):
        return {
            "ceiling": f"at the ceiling: frame peak {f['peak']:.1f} dBFS on the master",
            "dead": f"dead output while playing: rms {f['rms']:.1f} dB",
            "crest": f"squashed: crest {f['crest']:.1f} dB sustained (<{CREST_MIN:.0f})",
            "flatline": "static level: rms flat for 8s+ while playing",
            "mud": (f"lowmid-dominant: {f['bands'][1]:.0f} dB vs "
                    f"low {f['bands'][0]:.0f} / mid {f['bands'][2]:.0f} / high {f['bands'][3]:.0f}"),
            "lean": f"stereo lean: L {f['rms_l']:.1f} vs R {f['rms_r']:.1f} dB",
        }[kind]

    def feed(self, fr):
        try:
            f = self._facts(fr)
        except Exception:
            return []
        out = []
        for kind, cond in self._conditions(f):
            if not cond:
                self.since.pop(kind, None)
                continue
            t0 = self.since.setdefault(kind, f["t"])
            need = 0.0 if kind == "flatline" else _NEED[kind]
            if f["t"] - t0 < need:
                continue
            if f["t"] - self.last_fire.get(kind, -1e18) < COOLDOWN_S:
                continue
            self.last_fire[kind] = f["t"]
            out.append({"t": round(f["t"], 2), "kind": kind, "severity": _SEV[kind],
                        "beat": round(f["beat"], 1), "line": self._line(kind, f)})
        return out


# ---------------------------------------------------------------- R1 tail IO
def tail_frames(path, pos=0, ino=None, max_bytes=131072):
    """Incremental jsonl tail: returns (frames, new_pos, new_ino). Rotation /
    truncation restarts from the head. Torn lines skipped; never raises."""
    try:
        st = os.stat(path)
        if ino is not None and (st.st_ino != ino or st.st_size < pos):
            pos = 0
        with open(path, "rb") as f:
            f.seek(max(pos, max(0, st.st_size - max_bytes) if pos == 0 else pos))
            chunk = f.read()
            new_pos = f.tell()
        frames = []
        for ln in chunk.decode("utf-8", "replace").splitlines():
            ln = ln.strip()
            if not ln:
                continue
            try:
                frames.append(json.loads(ln))
            except json.JSONDecodeError:
                continue
        return frames, new_pos, st.st_ino
    except OSError:
        return [], 0, None


def _write_state(ipc, events, keep=8):
    try:
        p = os.path.join(ipc, STATE_NAME)
        cur = []
        try:
            cur = (json.load(open(p)) or {}).get("events") or []
        except Exception:
            cur = []
        cur = (cur + events)[-keep:]
        tmp = p + ".tmp"
        with open(tmp, "w") as f:
            json.dump({"t": round(time.time(), 1), "events": cur}, f)
        os.replace(tmp, p)
    except Exception:
        pass


def _log(root, events):
    try:
        tdir = os.path.join(root, "telemetry")
        os.makedirs(tdir, exist_ok=True)
        with open(os.path.join(tdir, LOG_NAME), "a") as f:
            for e in events:
                f.write(json.dumps(e) + "\n")
    except Exception:
        pass


def state_line(ipc, max_age_s=90.0, now=None):
    """The prompt rider: one line summarizing recent reflex verdicts, '' when
    quiet/stale — a prompt never carries dead sensor data (ears-bus law)."""
    try:
        d = json.load(open(os.path.join(ipc, STATE_NAME)))
        now = time.time() if now is None else now
        if now - float(d.get("t", 0)) > max_age_s:
            return ""
        ev = d.get("events") or []
        fresh = [e for e in ev if now - float(e.get("t", 0)) <= max_age_s]
        if not fresh:
            return ""
        seen, parts = set(), []
        for e in reversed(fresh):
            if e.get("kind") in seen:
                continue
            seen.add(e.get("kind"))
            parts.append(e.get("line", e.get("kind", "?")))
        return "REFLEXES flagged (live ears, last 90s): " + " · ".join(reversed(parts[:3]))
    except Exception:
        return ""


def watch(ipc, root, emit_fn=None, poll_s=0.5, stop=None):
    """The daemon loop (sidecar mounts this in a thread): tail ears.jsonl ->
    Reflex -> reflex_state.json + telemetry/reflex.jsonl (+ emit_fn). Fail-open
    forever; exits only via stop."""
    path = os.path.join(ipc, "ears.jsonl")
    rf, pos, ino = Reflex(), 0, None
    while not (stop is not None and stop.is_set()):
        try:
            frames, pos, ino = tail_frames(path, pos, ino)
            events = []
            for fr in frames:
                events.extend(rf.feed(fr))
            if events:
                _write_state(ipc, events)
                _log(root, events)
                if emit_fn is not None:
                    for e in events[:2]:            # storm gate on the bus
                        try:
                            emit_fn(e)
                        except Exception:
                            pass
        except Exception:
            pass
        time.sleep(poll_s)


# ---------------------------------------------------------------- R2 kernel
_MELODIC_WORDS = ("bass", "lead", "keys", "pad", "chord", "arp", "pluck",
                  "melody", "vox", "vocal", "string", "brass", "organ",
                  "piano", "gtr", "guitar", "sub", "stab", "bell")
# mirror of music_court's WITNESS LAW — witnesses never testify here either
_WITNESS_SUFFIX = ("_sketch", "_identity", "_ref", "_witness")
_WITNESS_PREFIX = ("spectral_",)


class InflightScan:
    """R2: key-scan the NEW notes of a streaming take. Advisory only — one
    line per threshold crossing, hard-capped per run."""

    def __init__(self, genre="", sour_threshold=5, max_lines=2, min_gap_s=20.0):
        self.genre = genre or ""
        self.threshold = sour_threshold
        self.max_lines = max_lines
        self.min_gap_s = min_gap_s
        self.seen = set()
        self.sour = []
        self.lines = 0
        self.last_line_t = -1e18
        self._allowed = None
        self._keyname = ""

    def _resolve_key(self, doc):
        try:
            import theory
            k = theory.parse_key(str(doc.get("key") or ""))
            if not k:
                return False
            self._allowed = set(theory.allowed_pcs(k, self.genre)) | \
                set(theory.soft_pcs(k, self.genre))
            self._keyname = str(doc.get("key"))
            return True
        except Exception:
            return False

    @staticmethod
    def _scannable(track):
        nm = str(track.get("name", "")).lower()
        if nm.endswith(_WITNESS_SUFFIX) or nm.startswith(_WITNESS_PREFIX):
            return False
        return any(w in nm for w in _MELODIC_WORDS)

    def feed_doc(self, doc, now=None):
        """One streamed snapshot -> None | one advisory line."""
        try:
            if not isinstance(doc, dict) or self.lines >= self.max_lines:
                return None
            if self._allowed is None and not self._resolve_key(doc):
                return None                      # no key = no scan, never guess
            import meter
            m = meter.song_meter(doc)
            for tr in doc.get("tracks") or []:
                if not self._scannable(tr):
                    continue
                tn = str(tr.get("name", ""))
                for n in tr.get("notes") or []:
                    key = (tn, round(float(n.get("start", 0)), 3),
                           int(n.get("pitch", 0)))
                    if key in self.seen:
                        continue
                    self.seen.add(key)
                    if int(n.get("pitch", 0)) % 12 not in self._allowed:
                        self.sour.append((tn, float(n.get("start", 0.0)),
                                          int(n.get("pitch", 0)),
                                          meter.bar_at_q(m, float(n.get("start", 0.0)))))
            now = time.time() if now is None else now
            if (len(self.sour) >= self.threshold
                    and now - self.last_line_t >= self.min_gap_s):
                self.lines += 1
                self.last_line_t = now
                tn, _s, pitch, bar = self.sour[-1]
                import theory
                return (f"[reflex] streaming take: {len(self.sour)} notes so far land "
                        f"outside {self._keyname} (latest {theory.midi_to_name(pitch)} "
                        f"in {tn} @bar {bar}) — the end-of-run court will verdict")
            return None
        except Exception:
            return None


if __name__ == "__main__":
    ipc = sys.argv[1] if len(sys.argv) > 1 else os.path.join(DEF_ROOT, "agent", "ipc")
    print(state_line(ipc) or "(reflexes quiet)")
