#!/usr/bin/env python3
"""THE IMPORT PLAUSIBILITY COURT (2026-07-11, Chezy live: "It NEED TO BE SOUND
AWARE! ... there's no way that by accident there'll be two notes that are off
key. Or there's no way that it'll be thirty two beats of a bass drum unless
it's a double bass, but this is something a hundred percent confident about
it ... No non snap to note. No echoey, weird sounding music.")

The identity contract (source_kit) made the KIT VOICES wear their own bands;
this court judges the EVENTS. Four judges, every conviction (and every
acquittal that matters) carries a WHY receipt:

  court_key   isolated out-of-scale pitch classes are transcription
              accidents -> snapped to the nearest scale tone (melodic-
              direction aware). Pattern-supported classes (>=3 occurrences
              or >=5% of note mass) are INTENT — blue notes, borrowed
              chords — kept. Chromatic passing/neighbor tones exempt, so
              measured 808 slides survive by construction.
  court_runs  a dense same-drum run (>=12 hits, <=0.55b spacing) must
              PROVE its family on the audio: median band shares across the
              run's own stem slices, judged by source_kit's identity
              contract. A "kick" run that measures hi-dominant was a hat
              roll -> reassigned (hits duplicating the true lane are
              dropped as band-bleed doubles). A sub-true run IS double
              bass: kept, receipt states the measurement — that is the
              "hundred percent confident" Chezy demanded.
  court_snap  lane-consensus grid: when >=80% of a lane already sits on
              the straight grid (phase-aware) and triplet support is low,
              the stragglers are jitter -> snapped around the lane's own
              phase. Swing/triplet lanes untouched.
  court_echo  same-pitch tails at near-constant delay with decaying
              velocity are transcribed ECHO, not performance -> ghosts
              die, sources stay. Equal-velocity ostinatos are music and
              never touched.

Kill-switch: SOTADAW_NO_COURT=1 (checked by the stems_import wiring, not
here — the kernel stays pure). CLI (existing songs, dry by default):

    .venv/bin/python tools/import_court.py songs/<name>.json          # docket
    .venv/bin/python tools/import_court.py songs/<name>.json --apply  # + heal
"""
import json
import math
import os
import sys

import numpy as np

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)

DRUM_LANES = ("Kick", "Snare", "Hats", "Perc", "Cymbals")
MELODIC_SUFFIX = ("_sketch", "_lead", "_pad", "_chords")
# (_lead/_pad/_chords = THE STREAM SPLIT lanes, note_streams.py 2026-07-15 —
#  the 'other' bucket decomposes into voice lanes; they face the same judges)


# ---------------------------------------------------------------- receipts
def _r(court, action, why, **kw):
    d = {"court": court, "action": action, "why": why}
    d.update(kw)
    return d


def fmt(r):
    extra = " ".join(f"{k}={v}" for k, v in r.items()
                     if k not in ("court", "action", "why"))
    return f"{r['court']}: {r['action']} — {r['why']}" + (f" [{extra}]" if extra else "")


# ---------------------------------------------------------------- key court
def _key_pcs(key):
    from midi_polish import _key_pcs as kp
    return kp(key)


def court_key(notes, key, lane=""):
    """Isolated off-key = accident (snap). Pattern-supported = intent (keep).
    Passing/neighbor tones exempt. Returns (notes, receipts)."""
    pcs = _key_pcs(key)
    if not pcs or not notes:
        return [dict(n) for n in notes], []
    ns = sorted((dict(n) for n in notes), key=lambda n: (n["start"], n["pitch"]))
    total_mass = sum(max(0.01, n["len"]) * max(0.05, n["vel"]) for n in ns) or 1.0
    off = {}
    for n in ns:
        pc = n["pitch"] % 12
        if pc not in pcs:
            c, m, tl = off.get(pc, (0, 0.0, 0.0))
            off[pc] = (c + 1, m + max(0.01, n["len"]) * max(0.05, n["vel"]),
                       tl + n["len"])
    # INTENT = repetition (>=3: "no way TWO notes are off key by accident"),
    # or one deliberately HELD note carrying real mass — never a short blip.
    intent = {pc for pc, (c, m, tl) in off.items()
              if c >= 3 or (m / total_mass >= 0.05 and tl / c >= 0.75)}
    receipts = []
    for pc in sorted(intent):
        c, m, _tl = off[pc]
        receipts.append(_r("key", "kept", f"off-scale pc {pc} is pattern-supported "
                           f"({c} occurrences, {m / total_mass:.0%} mass) — intent, "
                           "not accident", lane=lane))

    def _neighbors(i):
        p = next((ns[j] for j in range(i - 1, -1, -1)
                  if ns[j]["start"] < ns[i]["start"]), None)
        q = next((ns[j] for j in range(i + 1, len(ns))
                  if ns[j]["start"] > ns[i]["start"]), None)
        return p, q

    def _nearest_scale(pitch, toward=None):
        cands = []
        for d in range(1, 7):
            for s in (-1, +1):
                t = pitch + s * d
                if 0 <= t <= 127 and (t % 12) in pcs:
                    cands.append(t)
            if cands:
                break
        if not cands:
            return pitch
        if len(cands) == 2 and toward is not None:
            return min(cands, key=lambda t: abs(t - toward))
        return min(cands, key=lambda t: (abs(t - pitch), t < pitch))

    snapped = passing = 0
    ex = []
    for i, n in enumerate(ns):
        pc = n["pitch"] % 12
        if pc in pcs or pc in intent:
            continue
        p, q = _neighbors(i)
        if p and q:
            dp, dq = n["pitch"] - p["pitch"], q["pitch"] - n["pitch"]
            if 1 <= abs(dp) <= 2 and 1 <= abs(dq) <= 2 and (dp > 0) == (dq > 0):
                passing += 1                       # chromatic passing tone
                continue
            if p["pitch"] == q["pitch"] and 1 <= abs(dp) <= 2:
                passing += 1                       # neighbor tone
                continue
        old = n["pitch"]
        n["pitch"] = _nearest_scale(old, toward=q["pitch"] if q else None)
        if n["pitch"] != old:
            snapped += 1
            if len(ex) < 4:
                ex.append(f"{old}->{n['pitch']}@{n['start']:g}")
    if snapped:
        receipts.append(_r("key", "snapped", "isolated off-key notes are "
                           "transcription accidents, not performance — snapped to "
                           "the nearest scale tone", lane=lane, count=snapped,
                           examples=ex, key=key))
    if passing:
        receipts.append(_r("key", "exempt", "chromatic passing/neighbor tones kept "
                           "(stepwise motion is intent)", lane=lane, count=passing))
    return ns, receipts


# ---------------------------------------------------------------- runs court
def _fam_of(gm):
    from source_kit import _ID_FAMILY
    return _ID_FAMILY.get(int(gm))


def _measure_family(sub, body, hi):
    """What the audio says this hit IS (independent of its label)."""
    if sub >= 0.45:
        return "kick"
    if hi >= 0.45 and body < 0.40:
        return "hat"
    if body >= 0.30:
        return "snare"
    return "perc"


_FAM_TARGET = {"kick": (36, 33, 35), "snare": (38, 40, 34, 37),
               "hat": (42, 44, 46, 41, 26), "perc": (39,)}


def court_runs(notes, drums_wav, bpm, available_pitches=None,
               min_run=12, max_gap_b=0.55):
    """Dense same-family drum runs must PROVE their family on the stem.
    Returns (notes, receipts). Needs the audio — no evidence, no verdict."""
    if not notes or not drums_wav or not os.path.exists(drums_wav):
        return [dict(n) for n in notes], []
    from source_kit import _band_shares, _ID_CONTRACT, _load_mono
    sr, x = _load_mono(drums_wav)
    spb = 60.0 / bpm
    ns = sorted((dict(n) for n in notes), key=lambda n: (n["start"], n["pitch"]))
    by_fam = {}
    for i, n in enumerate(ns):
        f = _fam_of(n["pitch"])
        if f:
            by_fam.setdefault(f, []).append(i)
    receipts = []
    drop = set()
    for fam, idxs in by_fam.items():
        run = []
        chains = []
        for i in idxs:
            if run and ns[i]["start"] - ns[run[-1]]["start"] > max_gap_b:
                chains.append(run)
                run = []
            run.append(i)
        chains.append(run)
        for run in chains:
            if len(run) < min_run:
                continue
            shares = []
            for i in run:
                a = max(0, int((ns[i]["start"] * spb - 0.008) * sr))
                b = min(len(x), int((ns[i]["start"] * spb + 0.10) * sr))
                if b - a >= 256:
                    shares.append(_band_shares(x[a:b], sr))
            if len(shares) < min_run // 2:
                continue
            sub, body, hi = (float(np.median([s[k] for s in shares]))
                             for k in range(3))
            span = ns[run[-1]]["start"] - ns[run[0]]["start"]
            violates, _band = _ID_CONTRACT[fam]
            if not violates(sub, body, hi):
                receipts.append(_r("runs", "verified",
                                   f"{len(run)}-hit {fam} run over {span:.0f} beats "
                                   f"measures sub={sub:.2f} body={body:.2f} "
                                   f"hi={hi:.2f} — it IS a {fam}"
                                   + (" (double bass, real)" if fam == "kick"
                                      and len(run) >= 24 else ""),
                                   at=round(ns[run[0]]["start"], 2)))
                continue
            true_fam = _measure_family(sub, body, hi)
            if true_fam == fam:
                continue
            target = next((t for t in _FAM_TARGET[true_fam]
                           if available_pitches is None
                           or t in available_pitches), None)
            moved = dupes = 0
            true_starts = np.array([ns[j]["start"] for j in by_fam.get(true_fam, [])]
                                   or [9e9])
            for i in run:
                if np.abs(true_starts - ns[i]["start"]).min() < 0.04:
                    drop.add(i)                    # band-bleed double-detection
                    dupes += 1
                elif target is not None:
                    ns[i]["pitch"] = target
                    moved += 1
                else:
                    drop.add(i)                    # no kit voice to receive it
                    dupes += 1
            receipts.append(_r("runs", "reassigned",
                               f"{len(run)}-hit run labeled {fam} measures "
                               f"sub={sub:.2f} body={body:.2f} hi={hi:.2f} on the "
                               f"stem — that is a {true_fam}, not a {fam}",
                               at=round(ns[run[0]]["start"], 2), moved=moved,
                               dropped_dupes=dupes,
                               to=target if target is not None else "dropped"))
    if drop:
        ns = [n for i, n in enumerate(ns) if i not in drop]
    return ns, receipts


# ---------------------------------------------------------------- snap court
def _wrap(x, grid):
    return (x + grid / 2) % grid - grid / 2


def court_snap(notes, lane="", grid=0.25, on_tol=0.03, fix_tol=0.11):
    """Lane-consensus snap AROUND the lane's own phase. Returns (notes, receipts)."""
    if len(notes) < 8:
        return [dict(n) for n in notes], []
    ns = [dict(n) for n in notes]
    b = np.array([n["start"] for n in ns])
    w = np.array([max(0.05, n["vel"]) for n in ns])
    ang = 2 * np.pi * (b % grid) / grid
    z = complex((w * np.cos(ang)).sum(), (w * np.sin(ang)).sum())
    phase = ((np.angle(z) % (2 * np.pi)) / (2 * np.pi) * grid) if abs(z) > 1e-9 else 0.0
    d = _wrap(b - phase, grid)
    on = np.abs(d) <= on_tol
    trip = np.abs(_wrap(b - phase, 1.0 / 6.0)) <= on_tol
    trip_only = float((trip & ~on).mean())
    support = float(on.mean())
    if support < 0.80 or trip_only >= 0.15:
        why = (f"lane is not straight-grid consensus (on-grid {support:.0%}, "
               f"triplet-only {trip_only:.0%}) — feel left alone")
        return ns, [_r("snap", "left-alone", why, lane=lane)] if support < 0.6 else []
    stragglers = [i for i in range(len(ns))
                  if on_tol < abs(d[i]) <= fix_tol]
    for i in stragglers:
        q = round((ns[i]["start"] - phase) / grid) * grid + phase
        ns[i]["start"] = round(max(0.0, q), 4)
    receipts = []
    if stragglers:
        receipts.append(_r("snap", "snapped",
                           f"{support:.0%} of the lane sits on the grid — the "
                           f"{len(stragglers)} stragglers are jitter, not feel",
                           lane=lane, count=len(stragglers),
                           phase_b=round(float(phase), 3)))
    beyond = int((np.abs(d) > fix_tol).sum())
    if beyond:
        receipts.append(_r("snap", "left-alone",
                           f"{beyond} notes sit beyond {fix_tol}b from the grid — "
                           "too far to be jitter; not moved without ears",
                           lane=lane, count=beyond))
    return ns, receipts


# ---------------------------------------------------------------- echo court
def court_echo(notes, lane="", decay=0.60, gap_lo=0.20, gap_hi=2.0,
               gap_jitter=0.06):
    """Chains of >=2 decaying same-pitch followers at near-constant delay are
    transcribed echo. A single very weak follower (<0.25 vel) close behind its
    source is a reverb ghost. Returns (notes, receipts)."""
    ns = sorted((dict(n) for n in notes), key=lambda n: n["start"])
    by_pitch = {}
    for i, n in enumerate(ns):
        by_pitch.setdefault(n["pitch"], []).append(i)
    drop = set()
    chains = ghosts = 0
    for p, idxs in by_pitch.items():
        k = 0
        while k < len(idxs):
            i = idxs[k]
            tail = []
            j = k
            while j + 1 < len(idxs):
                a, bb = ns[idxs[j]], ns[idxs[j + 1]]
                g = bb["start"] - a["start"]
                if not (gap_lo <= g <= gap_hi and bb["vel"] <= decay * a["vel"]):
                    break
                if tail and abs(g - tail[-1][1]) > gap_jitter:
                    break
                tail.append((idxs[j + 1], g))
                j += 1
            if len(tail) >= 2:                     # delay taps: constant gap, decaying
                for t, _g in tail:
                    drop.add(t)
                chains += 1
                k = j + 1
                continue
            if len(tail) == 1:
                t, g = tail[0]
                if ns[t]["vel"] <= 0.25 and g <= 0.8 and \
                        ns[t]["vel"] <= 0.4 * ns[i]["vel"]:
                    drop.add(t)                    # reverb ghost
                    ghosts += 1
                    k = j + 1
                    continue
            k += 1
    receipts = []
    if chains or ghosts:
        receipts.append(_r("echo", "culled",
                           "same-pitch decaying tails at constant delay are the "
                           "record's echo/reverb transcribed as notes — the "
                           "sources stay, the ghosts die", lane=lane,
                           chains=chains, ghosts=ghosts, dropped=len(drop)))
    ns = [n for i, n in enumerate(ns) if i not in drop]
    return ns, receipts


def court_length(notes, lane="", ceiling=6):
    """THE LENGTH COURT census (F1.3, docs/IMPORT_FINALE.md): a lane where
    many long notes sound at once is a WASH, not a part ('choir of the same
    instrument' — Chezy 2026-07-15). At every onset the sounding count must
    stay <= ceiling; violations trim the LONGEST remaining tails back to the
    offending moment (+ a 0.05b release) so the articulation stays and the
    pileup dies. Deterministic one-sweep; receipts like every court."""
    if not notes:
        return notes, []
    ns = sorted((dict(n) for n in notes),
                key=lambda n: (float(n.get("start", 0.0)),
                               int(n.get("pitch", 0))))
    trimmed = 0
    worst = 0
    for i, n in enumerate(ns):
        t = float(n["start"])
        active = [m for m in ns[:i]
                  if float(m["start"]) + float(m["len"]) > t + 1e-6]
        worst = max(worst, len(active) + 1)
        over = len(active) + 1 - ceiling
        if over <= 0:
            continue
        # longest remaining tail past t pays first
        active.sort(key=lambda m: float(m["start"]) + float(m["len"]),
                    reverse=True)
        for m in active[:over]:
            new_len = max(0.05, t - float(m["start"]) + 0.05)
            if new_len < float(m["len"]) - 1e-6:
                m["len"] = round(new_len, 4)
                trimmed += 1
    if not trimmed:
        return notes, []
    rr = [{"court": "length", "action": "trimmed", "lane": lane,
           "count": trimmed,
           "why": f"polyphony census hit {worst} simultaneous voices "
                  f"(ceiling {ceiling}) — the longest tails gave way; a lane "
                  f"is a playable part, not a wash"}]
    return ns, rr


# ---------------------------------------------------------------- orchestrator
def hold_court(song, drums_wav=None,
               courts=("key", "snap", "echo", "length", "runs"),
               kit_pitches=None):
    """Judge a song dict IN PLACE. Melodic courts on *_sketch lanes; the runs
    court on the named drum lanes (re-splitting reassigned hits between them).
    Returns the docket (list of receipts)."""
    docket = []
    key = song.get("key") or ""
    for t in song.get("tracks", []):
        nm = t.get("name") or ""
        if not nm.endswith(MELODIC_SUFFIX) or not t.get("notes"):
            continue
        ns = t["notes"]
        if "key" in courts:
            ns, rr = court_key(ns, key, lane=nm)
            docket += rr
        if "echo" in courts:
            ns, rr = court_echo(ns, lane=nm)
            docket += rr
        if "snap" in courts:
            ns, rr = court_snap(ns, lane=nm)
            docket += rr
        if "length" in courts:
            ns, rr = court_length(ns, lane=nm,
                                  ceiling=8 if nm.endswith("_chords") else 6)
            docket += rr
        t["notes"] = ns
    if "runs" in courts and drums_wav:
        lanes = [t for t in song.get("tracks", [])
                 if t.get("name") in DRUM_LANES and t.get("notes")
                 and (t.get("source") or {}).get("kind") == "sample"]
        if lanes:
            flat = [n for t in lanes for n in t["notes"]]
            flat, rr = court_runs(flat, drums_wav, float(song.get("bpm") or 120.0),
                                  available_pitches=kit_pitches)
            docket += rr
            if any(r["action"] == "reassigned" for r in rr):
                lane_of = lambda p: ("Kick" if p in (33, 35, 36) else
                                     "Snare" if p in (34, 37, 38, 40) else
                                     "Hats" if p in (26, 41, 42, 44, 46) else
                                     "Cymbals" if p in (49, 51, 52, 55, 57, 59)
                                     else "Perc")
                split = {}
                for n in flat:
                    split.setdefault(lane_of(int(n["pitch"])), []).append(n)
                kit_src = dict(lanes[0]["source"])
                have = {t["name"]: t for t in lanes}
                for lname, lns in split.items():
                    if lname in have:
                        have[lname]["notes"] = lns
                    else:
                        song["tracks"].append({"name": lname, "source": kit_src,
                                               "gainDb": -1.5, "muted": False,
                                               "notes": lns})
                for lname, t in have.items():
                    if lname not in split:
                        t["notes"] = []
    return docket


def _kit_pitches_of(song):
    """keyNotes available in the drum lanes' sample kit (so reassignment never
    targets a voice the kit can't sound)."""
    for t in song.get("tracks", []):
        src = t.get("source") or {}
        if t.get("name") in DRUM_LANES and src.get("kind") == "sample":
            kj = os.path.join(ROOT, "kits", src.get("kit", ""), "kit.json")
            if os.path.exists(kj):
                try:
                    kd = json.load(open(kj))
                    return {int(s["keyNote"]) for s in kd.get("samples", [])}
                except Exception:
                    return None
    return None


# ---------------------------------------------------------------- CLI
def main(argv):
    import argparse
    ap = argparse.ArgumentParser(description="Judge an imported song's MIDI "
                                 "plausibility (dry by default).")
    ap.add_argument("song")
    ap.add_argument("--apply", action="store_true",
                    help="write the healed song (backs up .json.precourt)")
    ap.add_argument("--courts", default="key,snap,echo,runs")
    a = ap.parse_args(argv)
    path = a.song if os.path.exists(a.song) else os.path.join(
        ROOT, "songs", a.song + ".json")
    song = json.load(open(path))
    name = os.path.splitext(os.path.basename(path))[0]
    drums = os.path.join(ROOT, "songs", f"{name}_stems", "drums.wav")
    docket = hold_court(song, drums_wav=drums if os.path.exists(drums) else None,
                        courts=tuple(a.courts.split(",")),
                        kit_pitches=_kit_pitches_of(song))
    if not docket:
        print("[court] clean — no convictions, nothing to say")
        return 0
    for r in docket:
        print("[court] " + fmt(r))
    acts = sum(1 for r in docket if r["action"] in
               ("snapped", "reassigned", "culled"))
    if a.apply and acts:
        bak = path + ".precourt"
        if not os.path.exists(bak):
            import shutil
            shutil.copyfile(path, bak)
        tmp = path + ".tmp"
        json.dump(song, open(tmp, "w"), indent=1)
        os.replace(tmp, path)
        print(f"[court] APPLIED -> {path} (backup {bak})")
    elif acts:
        print(f"[court] dry run — {acts} convictions would change the song "
              "(--apply to heal)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
