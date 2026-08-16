#!/usr/bin/env python3
"""FINISH — the full auto-production chain in one verb (the campaign's capstone).

  finish.py <song> [--out name] [--no-transitions] [--no-mix]

Ten firings built the parts; this composes them in the correct order, once,
verified:
  1. chordvote   -> the song's own harmony (persist chords[])
  2. arrange     -> if it's a bare loop (no sections), give it a pop form
  3. harmonize   -> fill a MISSING bass or pad, sectioned (parts breathe)
  4. transitions -> risers/impacts/downlifters at the seams (if sectioned)
  5. automix     -> center subs, widen pads, sidechain, symbolic unmask

Each step is a no-op if already present, so finish is idempotent and safe on a
polished song. Composite battery: the output gains sections, transition energy,
per-section density, and a mono-safe mix — every subsystem's battery at once.
"""
import argparse, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from chordvote import chord_map
import harmonize as H
import transitions as T
import automix as M
import songname


def role_names(song):
    return {M.role(t) for t in song.get("tracks", [])}


def finish(song, out_name=None, genre=None):
    steps = []
    # 1. harmony — vote the loop's chords, and REMEMBER the cycle (arrange discards
    #    chords[] and strips the chords track in non-'other' sections, so we tile the
    #    cycle back across the arranged length rather than re-vote a mangled track)
    cycle = None
    if not song.get("chords"):
        ch = chord_map(song)
        if ch:
            song["chords"] = ch
            steps.append(f"chords: {len(ch)} bars voted")
    if song.get("chords"):
        from reharm import detect_cycle
        labels = [c["chord"] for c in song["chords"]]
        cyc_len = detect_cycle(labels)
        cycle = labels[:cyc_len]
    # 2. structure (arrange only if truly a bare loop — leave real arrangements alone)
    if len(song.get("sections", [])) < 2 and float(song.get("lengthBars", 0)) <= 16:
        try:
            import arrange as A
            fam = None
            if genre:
                try:
                    _c = json.load(open(os.path.join(ROOT, "agent", "dna_cache.json")))["genres"]
                    fam = (_c.get(genre) or {}).get("form_family")
                except Exception:
                    pass
            names, raw = A.sample_pop_form(seed=1)
            bpm = float(song.get("bpm", 120))
            dur = {}
            try:
                dur = json.load(open(A.GRAMMAR)).get("mean_duration_s", {})
            except Exception:
                pass
            DEF = {"intro": 15.5, "verse": 24, "chorus": 21, "build": 14.6,
                   "bridge": 23.4, "break": 9, "outro": 18.6, "inst": 20.6}
            form = [(nm, max(4, min(16, int(round(float(dur.get(rw, DEF.get(rw, 20)))
                    * bpm / 60.0 / 4.0 / 4.0) * 4)))) for nm, rw in zip(names, raw)]
            if fam == "club":       # the cited extended-mix convention (f155)
                form = list(A.CLUB_FORM)
            elif fam == "song":
                form = list(A.SONG_FORM)
            elif fam == "rap":      # wave 43: verse/hook, full beat, no drops
                form = list(A.RAP_FORM)
            elif fam == "loop":     # wave 43: the loop IS the song
                form = list(A.LOOP_FORM)
            elif fam == "through_composed":
                form = list(A.THROUGH_FORM)
            # arrange mutates a copy on disk; do it in-memory-safe by writing a temp
            tmp = os.path.join(ROOT, "songs", "_finish_arr_tmp.json")
            json.dump(song, open(tmp, "w"), indent=1)
            A.arrange(tmp, "_finish_arr_tmp", form=form)
            song.clear()
            song.update(json.load(open(tmp)))
            os.remove(tmp)
            # TILE the remembered cycle across EVERY arranged bar (firing-66 S3.4:
            # harmonize follows chords[], so chords must cover all bars, contiguous)
            if cycle:
                nb = int(round(float(song.get("lengthBars", 0))))
                song["chords"] = [{"bar": b + 1, "chord": cycle[b % len(cycle)], "conf": 0.9}
                                  for b in range(nb)]
                steps.append(f"arranged: {len(form)} sections ({song['lengthBars']} bars), "
                             f"chords tiled ({len(cycle)}-cycle -> {nb} bars)")
            else:
                steps.append(f"arranged{' CLUB' if fam=='club' else ' SONG' if fam=='song' else ''}: "
                             f"{len(form)} sections ({song['lengthBars']} bars)")
        except Exception as e:
            steps.append(f"arrange skipped: {e}")
    # 3. fill a missing harmonic role, section-aware
    roles = role_names(song)
    for role, want in (("bass", "bass"), ("pad", "pad")):
        if role not in roles and song.get("chords"):
            H.harmonize(song, want, sectioned=len(song.get("sections", [])) >= 2)
            steps.append(f"harmonized {want} (sectioned)")
    # 4. transitions
    if len(song.get("sections", [])) >= 2:
        try:
            rep = T.transitions(song, impacts=True, downlifters=True, fills=True)
            steps.append(f"transitions: {rep['risers']} risers, {rep.get('downlifters',0)} drains")
        except SystemExit as e:
            steps.append(f"transitions skipped: {e}")
    # 5. mix
    mv = M.automix(song)
    if mv:
        steps.append(f"automix: {len(mv)} moves")
    # 6. master safety — a FINISHED track must not clip (firing-66 S6.3), and the
    #    wall is now RELEASE-GRADE (firing-100): fx_truepeak keys on a 4x-oversampled
    #    BS.1770 detector with a measured 1.0dB reconstruction margin, so 'ceiling'
    #    means dBTP OF THE OUTPUT. The old path (fx_brickwall is a SAMPLE limiter,
    #    ISP-blind; we paid a -3.0 insurance ceiling + trim-neutralize) cost ~2 LUFS
    #    — battery-measured refund: -13.16 -> -11.11 LUFS at dBTP -1.27. Any legacy
    #    brickwall on the chain is UPGRADED in place; pre-wall boost trims may stay
    #    (the true wall makes them safe).
    master = song.setdefault("master", [])
    tp = next((f for f in master if f.get("id") == "fx_truepeak"), None)
    bw = next((f for f in master if f.get("id") == "fx_brickwall"), None)
    if tp is None and bw is not None:
        bw["id"] = "fx_truepeak"
        bw.setdefault("params", {})["ceiling"] = -1.2
        steps.append("master: fx_brickwall -> fx_truepeak ceiling -1.2 dBTP (release wall)")
    elif tp is None:
        master.append({"id": "fx_truepeak", "params": {"ceiling": -1.2}})
        steps.append("master: +fx_truepeak ceiling -1.2 dBTP (release wall)")
    else:
        cur = float(tp.setdefault("params", {}).get("ceiling", 0.0))
        if cur > -1.0:
            tp["params"]["ceiling"] = -1.2
            steps.append(f"master: truepeak ceiling {cur} -> -1.2 dBTP")
    song["masterGainDb"] = 0.0                # staging stays inside the chain
    return steps


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("song"); ap.add_argument("--out", default=None)
    ap.add_argument("--genre", default=None)
    a = ap.parse_args()
    name = songname.resolve(a.song)
    song = json.load(open(os.path.join(ROOT, "songs", f"{name}.json")))
    # THE HUSK GATE (2026-08-07, untitled_73): FINISH on a fresh +NEW project
    # arranged 124 bars of NOTHING, decorated it with transition furniture
    # (crash/subdrop/riser/impact), and served a take its own arc court had
    # failed ("4 gaps" = the 4 empty seed tracks). "Finish what is already
    # here" needs a HERE — an empty project refuses honestly, mutates nothing.
    if not any(t.get("notes") or t.get("audioClips") for t in song.get("tracks", [])):
        print(f"[finish] nothing to finish - every track in {name} is empty. "
              "MAKE a track first (one click, free, instant), or hum one, or "
              "tell the producer what to build - then FINISH arranges, mixes "
              "and masters what lands.")
        print("FINISH_JSON " + json.dumps({"out": None, "steps": [],
              "error": "empty_project", "hint": "make_track first"}))
        return
    steps = finish(song, genre=a.genre)
    out = re.sub(r"[^a-z0-9_]", "", a.out.lower()) if a.out else name
    json.dump(song, open(os.path.join(ROOT, "songs", f"{out}.json"), "w"), indent=1)
    print(f"[finish] {name} -> songs/{out}.json ({len(steps)} steps):")
    for s in steps:
        print("  - " + s)
    print("FINISH_JSON " + json.dumps({"out": out, "steps": steps,
          "bars": song.get("lengthBars"), "tracks": len(song.get("tracks", []))}))


if __name__ == "__main__":
    main()
