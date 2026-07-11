#!/usr/bin/env python3
"""V40 THE FINISH-IT ARC — the anti-abandonment audit.

finish_audit.py <song-name-or-json> [--genre <kg_genre>] [--json] [--no-render]

"The 8-bar-loop graveyard is where creativity dies." This audits a song the way a
finisher would: structure (does it BEGIN, TRAVEL, and END?), variation (does anything
change?), motion (does anything MOVE?), and mix (do the ears sign off?) — then emits a
STAGED PLAN where every stage names the tool that executes it (edit_section,
duplicate_bars/clear_bars, automate, apply_groove, set_track_fx, the master-chain law).
Verdict ladder: SKELETON -> ALMOST -> FINISHED.
"""
import argparse, json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
M1 = os.path.join(ROOT, "app/build/m1_artefacts/Release/m1")


def load_song(arg):
    j = arg if arg.endswith(".json") else os.path.join(ROOT, "songs", f"{arg}.json")
    if not os.path.exists(j):
        sys.exit(f"no such song: {j}")
    return j, json.load(open(j))


def ensure_render(j):
    w = j[:-5] + ".wav"
    if not os.path.exists(w) or os.path.getmtime(w) < os.path.getmtime(j):
        r = subprocess.run([M1, "render", j, w], capture_output=True, text=True)
        if r.returncode != 0:
            return None
    return w


def bar_densities(song):
    bars = int(song.get("lengthBars", 0) or 0)
    dens = [0] * max(bars, 1)
    for t in song.get("tracks", []):
        for nn in t.get("notes", []):
            b = int(nn.get("start", 0) // 4)
            if 0 <= b < len(dens):
                dens[b] += 1
    return dens


def audit(song, j, genre=None, no_render=False):
    finds, plan = [], []
    bars = int(song.get("lengthBars", 0) or 0)
    dens = bar_densities(song)
    total_notes = sum(dens)
    tracks = song.get("tracks", [])

    # ---- A. STRUCTURE ----
    if bars < 16 or total_notes < 64:
        finds.append(("SKELETON", f"{bars} bars / {total_notes} notes — this is a loop, not a song"))
        plan.append("arrange_song (loop -> sectioned skeleton) or duplicate_bars to 32+ bars, then per-section edits")
    secs = song.get("sections", [])
    if len(secs) < 3:
        finds.append(("structure", f"{len(secs)} sections — no journey"))
        plan.append("edit_section: define intro / body / breakdown / outro (section chips are draggable in the UI)")
    body = [d for d in dens if d > 0]
    if bars >= 8 and body:
        avg = sum(body) / len(body)
        first_bar, last_bars = dens[0], dens[max(0, bars - 2):bars]
        if first_bar >= avg * 0.9:
            finds.append(("structure", "starts at full density — no intro"))
            plan.append("clear_bars: thin bars 0-3 to 1-2 elements (or add a filtered intro via master fx_filter automation)")
        if last_bars and max(last_bars) >= avg * 0.9:
            finds.append(("structure", "runs full-density into the wall — no ending"))
            plan.append("edit_section outro: strip to 1-2 voices in the last 4 bars + a final downbeat hit that rings out")

    # ---- A2. THE VOICE (W103): written words must SOUND ----
    lyr = song.get("lyrics") or []
    real_words = [w for w in lyr if not str(w.get("text", "")).startswith("@")]
    vocal_lanes = [t for t in tracks
                   if str(t.get("name", "")).lower().startswith("vocal")
                   and (t.get("audioClips") or [])]
    if real_words and not vocal_lanes:
        finds.append(("voice", f"{len(real_words)} lyric words written but NEVER SUNG — "
                               "the song has words and no voice"))
        plan.append("sing_lyrics(song, track='lead') renders the vocal and lands it "
                    "level-matched (voice: Gahata Meiji from LUNAI Project)")
    if lyr:
        # W125 THE DRIFT CHECK: melody edited after the lyrics were written =
        # words on beats with no note = mis-sung take on the next render
        mel = next((t for t in tracks if t.get("name") == "lead"
                    and t.get("notes")), None)
        if mel is not None:
            import bisect
            starts = sorted(round(float(n["start"]), 4) for n in mel["notes"])
            def _on_note(b):
                i = bisect.bisect_left(starts, b - 0.06)
                return i < len(starts) and abs(starts[i] - b) <= 0.06
            drifted = [w for w in lyr if not _on_note(float(w.get("beat", -1)))]
            if drifted and len(drifted) * 10 > len(lyr):
                finds.append(("voice", f"lyrics DRIFTED off the melody "
                                       f"({len(drifted)}/{len(lyr)} words on beats "
                                       "with no lead note) — they will mis-sing"))
                plan.append("re-run phrase_map + write_lyrics against the current "
                            "melody, then sing_lyrics to re-render the vocal")
    for t in vocal_lanes:
        stale = [c for c in t.get("audioClips", [])
                 if not os.path.exists(os.path.join(ROOT, str(c.get("file", ""))))
                 and not os.path.isabs(str(c.get("file", "")))]
        if stale:
            finds.append(("voice", f"'{t.get('name')}' points at {len(stale)} missing "
                                   "vocal file(s) — the take will render silent"))
            plan.append("re-sing (hum_topline / sing_lyrics) to regenerate the vocal wav")

    # ---- B. VARIATION ----
    if bars >= 16:
        chunks = [sum(dens[i:i + 8]) for i in range(0, bars - 7, 8)]
        if chunks and (max(chunks) - min(chunks)) < max(chunks) * 0.15:
            finds.append(("variation", "every 8-bar block has ~the same density — nothing ever changes"))
            plan.append("clear_bars for a breakdown block + duplicate_bars with edits for a lifted final chorus")
    n_auto = len(song.get("automation", [])) + sum(len(t.get("automation", [])) for t in tracks)
    if n_auto == 0:
        finds.append(("motion", "zero automation — static params are demos (automation-motion law)"))
        plan.append("automate: one late-bloom build (curve>0) into the biggest section + one filter/gain arc on a pad or the master")
    sw = (song.get("swing") or {}).get("amount", 0.5)
    offgrid = any(abs((nn.get("start", 0) % 0.25)) > 1e-6 for t in tracks for nn in t.get("notes", [])[:200])
    if sw <= 0.5 and not offgrid:
        finds.append(("feel", "everything is on the grid with no swing — quantized-demo feel"))
        plan.append("apply_groove (boombap_56 / dilla / genre groove from the KG) or set swing 0.54-0.60")

    # ---- C. MIX (the ears) ----
    metrics = None
    if not no_render:
        w = ensure_render(j)
        if w:
            from analyze2 import analyze
            metrics = analyze(w)
            if metrics["clipped_samples"] > 0:
                finds.append(("mix", f"{metrics['clipped_samples']} clipped samples"))
                plan.append("master-chain law: fx_trim -> fx_saturate(mix 1.0) -> fx_trim -> fx_brickwall(-1.2..-1.5); fix gains at the source")
            if metrics["true_peak_dbtp"] > -1.0:
                finds.append(("mix", f"true peak {metrics['true_peak_dbtp']} dBTP > -1.0"))
                plan.append("fx_brickwall ceiling -1.5 (sub-dominant law if low band dominates)")
            mids = metrics["band_energy_pct"]
            if mids["low_20_120"] < mids["lowmid_120_500"]:
                finds.append(("mix", "band order inverted: lowmid > low"))
                plan.append("anchor the sub (808/kick gain) or trim the pads/keys at the source")
            arc = max(metrics["rms_by_quarter_db"]) - min(metrics["rms_by_quarter_db"])
            if bars >= 32 and arc < 1.5:
                finds.append(("motion", f"loudness arc {arc:.1f} dB across quarters — the song doesn't travel"))
                plan.append("automate gainDb builds + a real breakdown (contrast IS the arrangement)")
        else:
            finds.append(("mix", "render failed — fix the song before finishing"))
    if genre and metrics:
        from reference_match import mixtarget_lane
        mt = mixtarget_lane(genre, metrics)
        for c in mt.get("checks", []):
            if not c["ok"]:
                finds.append(("mix-target", f"{genre}: {c['check']} FAILED (value {c['value']})"))
        if any(not c["ok"] for c in mt.get("checks", [])):
            plan.append(f"hit the {genre} MixTarget (see analyze_reference --genre {genre} for the delta moves)")

    # ---- verdict ----
    if any(k == "SKELETON" for k, _ in finds):
        verdict = "SKELETON"
    elif len(finds) == 0:
        verdict = "FINISHED"
    elif len(finds) <= 3:
        verdict = f"ALMOST ({len(finds)} fixes)"
    else:
        verdict = f"IN PROGRESS ({len(finds)} findings)"
    return {"verdict": verdict, "bars": bars, "notes": total_notes, "tracks": len(tracks),
            "findings": [{"area": a, "what": w} for a, w in finds],
            "staged_plan": [{"stage": i + 1, "do": p} for i, p in enumerate(dict.fromkeys(plan))],
            "metrics": {k: metrics[k] for k in ("lufs_integrated", "true_peak_dbtp", "clipped_samples")} if metrics else None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("song")
    ap.add_argument("--genre")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-render", action="store_true")
    a = ap.parse_args()
    j, song = load_song(a.song)
    out = audit(song, j, a.genre, a.no_render)
    if a.json:
        print(json.dumps(out, indent=1))
        return
    print(f"FINISH AUDIT — {os.path.basename(j)}  [{out['verdict']}]  "
          f"{out['bars']} bars, {out['tracks']} tracks, {out['notes']} notes")
    for f in out["findings"]:
        print(f"  [{f['area']}] {f['what']}")
    if out["staged_plan"]:
        print("STAGED PLAN (execute in order, one proposal per stage):")
        for s in out["staged_plan"]:
            print(f"  {s['stage']}. {s['do']}")
    else:
        print("  Nothing left — ship it (export_master for the C2PA-signed WAV).")


if __name__ == "__main__":
    main()
