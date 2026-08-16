#!/usr/bin/env python3
"""THE ARC COURT (PRODUCER MIND P6, docs/SPEC_PRODUCER_MIND.md).

The song must BREATHE. untitled_48 ('make a new pop hit') measured LRA 1.88
over 2:14 — verse and chorus at the same energy, no story. This court reads
the ARRANGEMENT's energy profile (no render needed) + the rendered take's
dynamics (when analysis is at hand) and verdicts the narrative:

  chorus_lift   hook-class sections must RISE over verse-class (energy ratio)
  dead_intro    the hook must arrive inside the genre's patience window
  flatline      adjacent sections at indistinguishable energy = no story
  lra_floor     rendered LRA under the genre-family floor = crushed/static

Verdict-only v1 (heals = composition changes; they land with R-14 research
numbers). Conservative: songs without sections are exempt (loops are loops).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import meter as METER  # noqa: E402

HOOK_CLASS = {"chorus", "drop", "hook", "theme"}
VERSE_CLASS = {"verse", "groove", "section", "main"}
INTRO_CLASS = {"intro"}
QUIET_CLASS = {"break", "breakdown", "bridge", "outro", "interlude"}

# genre-family LRA floors (rendered takes; bootstrap — R-14 refines).
# Keys route by substring like lyric_bank.FAMILY; first hit wins.
# W83 (item 235, r-8 cross-verified): the floor = a STOP-LIFTING line
# ~1-2 LU under the culture's published LRA. Classical publishes 10-20
# LU -> floor 7.5; jazz 6; ambient 5; quiet-loud rock 4.5; club/pop
# stay on the validated defaults.
LRA_FLOORS = (
    (("classical", "orchestral", "cinematic", "soundtrack", "filmi"), 7.5),
    (("jazz", "bigband", "swing", "bebop"), 6.0),
    (("ambient", "psybient", "chill", "downtempo", "drone", "meditation"), 5.0),
    (("grunge", "post_rock", "postrock", "shoegaze", "indie_rock"), 4.5),
    (("techno", "house", "trance", "edm", "dnb", "drum", "hardstyle",
      "dubstep", "garage", "gqom", "footwork"), 2.2),
    (("trap", "drill", "phonk", "grime", "rap", "hiphop", "boombap"), 2.5),
    ((), 3.0),                                    # everything else (pop-class)
)


def lra_floor_for(genre):
    g = str(genre or "").lower()
    for keys, floor in LRA_FLOORS:
        if any(k in g for k in keys):
            return floor
    return 3.0


def _sec_class(name):
    base = str(name or "").strip().lower().rstrip("0123456789_ ")
    for cls, names in (("hook", HOOK_CLASS), ("verse", VERSE_CLASS),
                       ("intro", INTRO_CLASS), ("quiet", QUIET_CLASS)):
        if base in names:
            return cls
    if any(w in base for w in ("build", "rise", "lift")):
        return "build"
    return "other"


def energy_profile(song):
    """Per-bar arrangement energy: sum over sounding notes of vel*dur, with a
    register lift (higher = brighter = more energy) and an active-lane bonus.
    Pure JSON math — the composition's own story, before any render."""
    mtr = METER.song_meter(song)
    length = int(float(song.get("lengthBars", 8) or 8))
    bars = [0.0] * max(length, 1)
    lanes = [set() for _ in range(max(length, 1))]
    for ti, t in enumerate(song.get("tracks", []) or []):
        if t.get("muted"):
            continue
        for n in t.get("notes", []) or []:
            try:
                b = int(METER.bar_at_q(mtr, float(n.get("start", 0))))
                if not (0 <= b < length):
                    continue
                vel = float(n.get("vel", 0.8))
                dur = min(float(n.get("len", n.get("length", 0.25))), 4.0)
                reg = 0.75 + 0.5 * min(max((int(n.get("pitch", 60)) - 36) / 60.0, 0.0), 1.0)
                bars[b] += vel * dur * reg
                lanes[b].add(ti)
            except Exception:
                continue
        for c in t.get("audioClips", []) or []:
            try:
                b0 = int(METER.bar_at_q(mtr, float(c.get("startBeat", 0))))
                b1 = int(METER.bar_at_q(mtr, float(c.get("startBeat", 0))
                                        + float(c.get("lengthBeats", 4))))
                for b in range(max(b0, 0), min(b1 + 1, length)):
                    bars[b] += 1.5
                    lanes[b].add(ti)
            except Exception:
                continue
    prof = [bars[b] * (1.0 + 0.15 * len(lanes[b])) for b in range(length)]
    peak = max(prof) or 1.0
    return [round(p / peak, 4) for p in prof]


def section_energies(song, prof=None):
    prof = prof or energy_profile(song)
    secs = sorted((s for s in song.get("sections", []) or []
                   if isinstance(s, dict)), key=lambda s: float(s.get("startBar", 0)))
    out = []
    for i, s in enumerate(secs):
        b0 = int(float(s.get("startBar", 0)))
        b1 = int(float(secs[i + 1].get("startBar", len(prof)))) if i + 1 < len(secs) \
            else len(prof)
        window = prof[b0:max(b1, b0 + 1)] or [0.0]
        out.append({"name": s.get("name", "?"), "class": _sec_class(s.get("name")),
                    "startBar": b0, "bars": max(b1 - b0, 1),
                    "energy": round(sum(window) / len(window), 4)})
    return out


def _has_vocals(song):
    """A sounding vocal lane (notes or audio) — the hook-patience law's
    streaming evidence is measured on SUNG records only."""
    for t in song.get("tracks", []) or []:
        blob = (str(t.get("name", "")) + " "
                + str((t.get("source") or {}).get("id", ""))).lower()
        if any(w in blob for w in ("vocal", "vox", "choir", "sing", "voice")):
            if t.get("notes") or t.get("audioClips"):
                return True
    return False


def court_arc(song, genre="", analysis=None):
    """The narrative verdict. Songs without sections (or <2) are exempt."""
    secs = section_energies(song)
    if len(secs) < 2:
        return {"court": "arc", "ok": True, "skipped": "no sections (loop)"}
    flags = []
    hooks = [s for s in secs if s["class"] == "hook"]
    verses = [s for s in secs if s["class"] == "verse"]
    if hooks and verses:
        h = sum(s["energy"] for s in hooks) / len(hooks)
        v = sum(s["energy"] for s in verses) / len(verses)
        if v > 0 and h / max(v, 1e-6) < 1.12:
            flags.append({"kind": "flat_chorus",
                          "why": f"hook sections at {h:.2f} vs verses {v:.2f} "
                                 f"(lift x{h / max(v, 1e-6):.2f} < 1.12) — the "
                                 "chorus must RISE (density/velocity/register/"
                                 "layers), or the song has no payoff"})
    intro = next((s for s in secs if s["class"] == "intro"), None)
    if intro and hooks:
        first_hook_bar = min(s["startBar"] for s in hooks)
        bpm = float(song.get("bpm", 120) or 120)
        hook_s = first_hook_bar * 4.0 * 60.0 / bpm
        # R-14 (researched 2026-07-14): streaming-era hook arrival — top-10k
        # median 7.2s, 83% inside 12s, +38% skip past a 20s intro; club forms
        # (32-bar intros are the idiom) and journey genres keep long patience.
        g = str(genre).lower()
        if any(k in g for k in ("ambient", "psy", "goa", "cinematic",
                                "orchestral", "classical", "soundtrack",
                                "drone", "meditation", "dub_")):
            patience = 90.0
        elif any(k in g for k in ("techno", "house", "trance", "dnb", "drum",
                                  "dub", "minimal", "garage", "edm")):
            patience = 60.0
        elif any(k in g for k in ("indie", "rock", "folk", "bluegrass",
                                  "americana", "country", "jazz", "soul",
                                  "blues")):
            patience = 30.0
        else:                       # pop/hiphop/rnb streaming truth
            patience = 20.0
        # the 20/30s numbers are VOCAL-pop streaming truth (skip stats on sung
        # records); an instrumental theme is a journey by construction — a
        # bluegrass/orchestral film cue got nagged at pop patience while its
        # hook landed at 60s exactly like the record's (untitled_65)
        if not _has_vocals(song):
            patience = max(patience, 60.0)
        if hook_s > patience:
            flags.append({"kind": "late_hook",
                          "why": f"first hook lands at {hook_s:.0f}s "
                                 f"(> {patience:.0f}s patience for this genre; "
                                 "streaming truth: pop hooks land ~6-12s, +38% "
                                 "skips past a 20s intro) — tighten the intro "
                                 "or seed a hook teaser"})
    # R-14: section lengths quantize to 2/4/8/12/16 bars in 4/4 across popular
    # forms — a 7-bar verse is almost always an accident, not prog ambition.
    odd = [s for s in secs if s["bars"] not in (1, 2, 4, 6, 8, 12, 16, 24, 32)
           and s is not secs[-1]]
    if len(odd) >= 2:
        flags.append({"kind": "odd_sections",
                      "why": "section lengths "
                             + ", ".join(f"{s['name']}={s['bars']}b" for s in odd[:3])
                             + " — popular forms quantize to 2/4/8/12/16 bars; "
                               "check for off-by-one section boundaries"})
    flat_run = 0
    for a, b in zip(secs, secs[1:]):
        if abs(a["energy"] - b["energy"]) < 0.06 and a["class"] == b["class"]:
            continue
        if abs(a["energy"] - b["energy"]) < 0.06:
            flat_run += 1
    if flat_run >= max(2, len(secs) // 3):
        flags.append({"kind": "flatline",
                      "why": f"{flat_run} section changes with no energy change "
                             "— sections must MEAN something (thin a verse, "
                             "mute layers, drop an element at the turn)"})
    if analysis and analysis.get("lra") is not None:
        floor = lra_floor_for(genre)
        lra = float(analysis["lra"])
        if lra < floor:
            flags.append({"kind": "lra_floor",
                          "why": f"rendered LRA {lra:.2f} < {floor} floor for "
                                 f"'{genre or 'default'}' — the mix is one flat "
                                 "block; write builds/breakdowns into levels, "
                                 "don't crush the master"})
    # item 070 (wave 27): the RENDERED chorus lift — judged on SHORT-TERM
    # level (rms_by_quarter windows), NEVER integrated LUFS (r-14 f3: the
    # loudness war flattens integrated section loudness while short-term
    # still lifts; 1-2 LU moderate, 3-6 significant). Advisory-grade
    # companion to the symbolic flat_chorus above.
    rq = (analysis or {}).get("rms_by_quarter_db")
    if rq and hooks and verses and isinstance(rq, (list, tuple)) \
            and len(rq) >= 8:
        try:
            bpm = float(song.get("bpm", 120) or 120)
            beats_total = float(song.get("lengthBars", 8) or 8) * 4
            q_per_beat = len(rq) / max(beats_total, 1.0)

            def sec_rms(s):
                q0 = int(s["startBar"] * 4 * q_per_beat)
                q1 = int((s["startBar"] + s["bars"]) * 4 * q_per_beat)
                win = [float(v) for v in rq[q0:max(q1, q0 + 1)]
                       if v is not None]
                return sum(win) / len(win) if win else None
            h_rms = [v for v in (sec_rms(s) for s in hooks)
                     if v is not None]
            v_rms = [v for v in (sec_rms(s) for s in verses)
                     if v is not None]
            if h_rms and v_rms:
                lift_db = (sum(h_rms) / len(h_rms)
                           - sum(v_rms) / len(v_rms))
                if lift_db < 0.5:
                    flags.append({
                        "kind": "flat_chorus_rendered",
                        "lift_db": round(lift_db, 2),
                        "why": f"RENDERED short-term lift {lift_db:+.1f}dB "
                               "hook-vs-verse (real hits lift 1-2dB "
                               "moderate, 3-6 significant — measured on "
                               "short-term windows, never integrated)"})
        except Exception:
            pass
    return {"court": "arc", "ok": not flags, "flags": flags,
            "sections": secs}


def heal_late_hook(song, verdict=None, genre=""):
    """Item 069's HEAL — the verdict's own second suggestion: SEED A
    HOOK TEASER. Additive and safe (cutting intro bars rewrites form):
    copy the hook's first 2 bars of the LEAD melody to the song's very
    top on a low-gain teaser lane wearing the lead's own voice.
    Mutates; returns ledger. Idempotent.

    CORPUS-GATED (wolf 2026-07-15: the advisory-edge verdict fires on
    53% of sectioned songs — club 32-bar intros are the idiom and a heal
    acting there is teaser SPAM): the heal moves only on the FLAGRANT
    class — hook past 2x the genre patience — and never on imported
    records (witness law)."""
    v = verdict or court_arc(song, genre)
    if not any(f.get("kind") == "late_hook" for f in v.get("flags", [])):
        return []
    for t in song.get("tracks", []) or []:
        nm = str((t or {}).get("name", "")).lower() \
            if isinstance(t, dict) else ""
        if nm.endswith(("_sketch", "_identity")):
            return []                     # imported record: witness law
    secs0 = section_energies(song)
    hooks0 = [s for s in secs0 if s["class"] == "hook"]
    if not hooks0:
        return []
    bpm = float(song.get("bpm", 120) or 120)
    hook_s = min(s["startBar"] for s in hooks0) * 4.0 * 60.0 / bpm
    g = str(genre or "").lower()
    if not g:
        return []          # unknown genre could be an untagged journey:
    if any(k in g for k in ("ambient", "psy", "goa", "cinematic",  # nag only
                            "orchestral", "drone", "meditation", "dub_",
                            "lofi", "chill", "downtempo")):
        return []          # journey family: patience IS the aesthetic —
    if any(k in g for k in ("techno", "house", "trance", "dnb", "drum",
                            "dub", "minimal", "garage", "edm")):
        patience = 60.0    # (you don't tease a meditation; nag only)
    elif any(k in g for k in ("indie", "rock", "folk", "country", "jazz",
                              "soul", "blues")):
        patience = 30.0
    else:
        patience = 20.0
    if hook_s <= 3.0 * patience:
        return []                         # advisory-grade lateness: nag only
    tracks = song.get("tracks", []) or []
    if any(str(t.get("name", "")) == "hook_teaser" for t in tracks
           if isinstance(t, dict)):
        return []
    secs = section_energies(song)
    hook = next((s for s in secs if s["class"] == "hook"), None)
    lead = None
    for t in tracks:
        if not isinstance(t, dict) or t.get("muted"):
            continue
        nm = str(t.get("name", "")).lower()
        if nm.endswith(("_sketch", "_identity")):
            continue
        if any(w in nm for w in ("lead", "vocal", "vox", "topline",
                                 "melody")) and (t.get("notes") or []):
            if lead is None or len(t["notes"]) > len(lead["notes"]):
                lead = t
    if hook is None or lead is None:
        return []
    h0 = hook["startBar"] * 4.0
    window = [n for n in lead["notes"]
              if h0 <= float(n.get("start", 0)) < h0 + 8.0]
    if len(window) < 3:
        return []
    import copy as _copy
    teaser_notes = []
    for n in window:
        c = _copy.deepcopy(n)
        c["start"] = round(float(n["start"]) - h0, 4)
        c["vel"] = round(float(n.get("vel", 0.8)) * 0.85, 3)
        teaser_notes.append(c)
    song.setdefault("tracks", []).append({
        "name": "hook_teaser",
        "source": _copy.deepcopy(lead.get("source") or {}),
        "gainDb": -6.0, "pan": 0.0, "notes": teaser_notes})
    return [{"kind": "hook_teaser", "notes": len(teaser_notes),
             "from_bar": hook["startBar"],
             "why": "the hook now answers in the first seconds (streaming "
                    "law) without cutting a bar of the form"}]


def main():
    import argparse
    ap = argparse.ArgumentParser(description="THE ARC COURT (P6)")
    ap.add_argument("song")
    ap.add_argument("--genre", default="")
    ap.add_argument("--wav", default=None, help="measure LRA from this render")
    args = ap.parse_args()
    sj = args.song if args.song.endswith(".json") else \
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "songs", f"{args.song}.json")
    song = json.load(open(sj))
    analysis = None
    if args.wav:
        import subprocess
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        py = os.path.join(root, ".venv", "bin", "python")
        r = subprocess.run([py, os.path.join(root, "tools", "analyze2.py"),
                            args.wav], capture_output=True, text=True, timeout=420)
        if r.returncode == 0:
            analysis = json.loads(r.stdout)
    v = court_arc(song, args.genre, analysis)
    print(json.dumps(v, indent=1))
    return 0 if v["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
