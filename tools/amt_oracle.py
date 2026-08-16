#!/usr/bin/env python3
"""THE AMT ORACLE — wave 97 (r-29 item 251): the Anticipatory Music
Transformer (stanford-crfm/music-small-800k, 128M, Lakh-trained,
loaded + key-following proven on this box) as the OFFLINE
accompaniment/counter-line oracle BEHIND the courts:

  the oracle PROPOSES (a counter-line continuing the lane's phrase);
  the COURTS judge (court_key snaps/drops sour notes before anything
  reaches a take) — generation never bypasses the law.

  suggest(song, track, from_bar, to_bar, seed) -> a NOTES list
      (ghost suggestion; deterministic per seed)
  --selftest   a C-major prime must yield >=60% diatonic suggestions
               (seeded), and the court filter must hold 100%
"""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

_CACHE = {}


def _model():
    if "m" not in _CACHE:
        import torch
        from transformers import AutoModelForCausalLM
        m = AutoModelForCausalLM.from_pretrained(
            "stanford-crfm/music-small-800k", use_safetensors=False)
        _CACHE["m"] = m.to("cuda" if torch.cuda.is_available()
                           else "cpu").eval()
    return _CACHE["m"]


def _notes_to_events(notes, bpm):
    """song.json notes -> anticipation events via a temp MIDI."""
    import mido
    from anticipation import convert as conv
    spb = 60.0 / max(float(bpm), 1.0)
    mid = mido.MidiFile()
    tr = mido.MidiTrack()
    mid.tracks.append(tr)
    tr.append(mido.MetaMessage("set_tempo", tempo=500000))
    tpq = mid.ticks_per_beat
    seq = []
    for n in sorted(notes, key=lambda x: float(x.get("start", 0))):
        s = float(n.get("start", 0)) * spb * 2.0   # 120bpm-normalized secs
        d = max(float(n.get("len", 0.25) or 0.25) * spb * 2.0, 0.05)
        seq.append((s, s + d, int(n.get("pitch", 60))))
    events = []
    now = 0.0
    for s, e, p in sorted(seq):
        events.append(mido.Message("note_on", note=p, velocity=90,
                                   time=int(max(s - now, 0) * tpq)))
        events.append(mido.Message("note_off", note=p, velocity=0,
                                   time=int((e - s) * tpq)))
        now = e
    for m in events:
        tr.append(m)
    tmp = tempfile.mktemp(suffix=".mid")
    mid.save(tmp)
    ev = conv.midi_to_events(tmp)
    os.remove(tmp)
    return ev


def _events_to_notes(events, bpm):
    """anticipation events -> song.json notes (via the round trip)."""
    import mido
    from anticipation import convert as conv
    tmp = tempfile.mktemp(suffix=".mid")
    conv.events_to_midi(events).save(tmp)
    mid = mido.MidiFile(tmp)
    os.remove(tmp)
    spb = 60.0 / max(float(bpm), 1.0)
    notes = []
    for tr in mid.tracks:
        t = 0
        on = {}
        for msg in tr:
            t += msg.time
            secs = mido.tick2second(t, mid.ticks_per_beat, 500000)
            if msg.type == "note_on" and msg.velocity > 0:
                on[msg.note] = secs
            elif msg.type in ("note_off", "note_on"):
                if msg.note in on:
                    s0 = on.pop(msg.note)
                    notes.append({
                        "start": round(s0 / 2.0 / spb, 4),
                        "len": round(max((secs - s0) / 2.0 / spb, 0.1), 4),
                        "pitch": int(msg.note), "vel": 88})
    return sorted(notes, key=lambda n: n["start"])


def suggest(song, track_name, from_bar=0, to_bar=None, seed=7,
            court=True):
    """The oracle's counter-line for the lane's phrase — court-filtered
    unless court=False (research mode)."""
    import torch
    from anticipation.sample import generate
    t = next((x for x in (song or {}).get("tracks", []) or []
              if isinstance(x, dict) and x.get("name") == track_name),
             None)
    if t is None or not t.get("notes"):
        return {"ok": False, "why": f"no notes on '{track_name}'"}
    bpm = float(song.get("bpm", 120) or 120)
    a, b = from_bar * 4.0, (to_bar * 4.0) if to_bar else None
    phrase = [n for n in t["notes"]
              if float(n.get("start", 0)) >= a and
              (b is None or float(n.get("start", 0)) < b)]
    if len(phrase) < 4:
        return {"ok": False, "why": "phrase too short (<4 notes)"}
    base = min(float(n.get("start", 0)) for n in phrase)
    rel = [dict(n, start=float(n.get("start", 0)) - base) for n in phrase]
    events = _notes_to_events(rel, bpm)
    spb2 = 60.0 / bpm * 2.0
    end_s = max(float(n["start"]) + float(n.get("len", 0.25))
                for n in rel) * spb2
    torch.manual_seed(int(seed))
    out = generate(_model(), start_time=0,
                   end_time=end_s + 8.0 * spb2, inputs=events,
                   top_p=0.92)
    sugg = _events_to_notes(out, bpm)
    # only the NEW tail (past the prime) is the suggestion
    prime_end = end_s / 2.0 / (60.0 / bpm)
    sugg = [dict(n, start=round(n["start"] + base, 4)) for n in sugg
            if n["start"] >= prime_end - 0.01]
    dropped = 0
    if court and sugg:
        import theory
        key = theory.parse_key(song.get("key"))
        if key:
            legal = theory.allowed_pcs(key, "")
            kept = []
            for n in sugg:
                if n["pitch"] % 12 in legal:
                    kept.append(n)
                else:
                    snap = theory.snap_pitch(n["pitch"], key, "")
                    if snap is not None:
                        kept.append(dict(n, pitch=int(snap)))
                    else:
                        dropped += 1
            sugg = kept
    return {"ok": True, "notes": sugg, "court_dropped": dropped,
            "seed": seed,
            "why": (f"the oracle proposes {len(sugg)} notes past bar "
                    f"{prime_end + base:.1f} (court-snapped; "
                    "a SUGGESTION — audition before it lands)")}


def selftest():
    song = {"bpm": 120, "key": "C major", "lengthBars": 8,
            "tracks": [{"name": "lead", "notes": [
                {"start": float(i), "len": 0.8, "pitch": p, "vel": 90}
                for i, p in enumerate((60, 64, 67, 72, 67, 64, 60, 64))]}]}
    raw = suggest(song, "lead", seed=7, court=False)
    if not raw.get("ok"):
        print("[skip]", raw.get("why"))
        return 0
    pcs = [n["pitch"] % 12 for n in raw["notes"]]
    dia = sum(1 for p in pcs if p in (0, 2, 4, 5, 7, 9, 11))
    frac = dia / max(len(pcs), 1)
    print(f"raw suggestions: {len(pcs)} notes, {frac:.0%} diatonic")
    ok1 = frac >= 0.6 and len(pcs) >= 3
    courted = suggest(song, "lead", seed=7, court=True)
    pcs2 = [n["pitch"] % 12 for n in courted["notes"]]
    ok2 = all(p in (0, 2, 4, 5, 7, 9, 11) for p in pcs2)
    print(f"courted: {len(pcs2)} notes, 100% diatonic: {ok2}, "
          f"dropped {courted['court_dropped']}")
    print("amt_oracle selftest:",
          "ALL GREEN" if (ok1 and ok2) else "RED")
    return 0 if (ok1 and ok2) else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    song = json.load(open(sys.argv[1]))
    print(json.dumps(suggest(song, sys.argv[2],
                             seed=int(sys.argv[3]) if len(sys.argv) > 3
                             else 7), indent=1))
