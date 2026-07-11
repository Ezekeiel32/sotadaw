#!/usr/bin/env python3
"""V27 REFERENCE MATCHING — "make it sit like THIS track."

reference_match.py <reference.(wav|mp3|flac|m4a)> (--song <name|json> | --wav <path>)
                   [--genre <kg_genre>] [--json]

Drops a reference next to the current mix and emits a GAP REPORT in this system's own
vocabulary: every delta names the concrete move (trim dB, band rebalance at the SOURCE,
fx_widen, transpose, automation arc) so the agent can turn it straight into proposals.
Optional --genre adds the KG MixTarget lane (window + band order + floors).

THE LEGAL LINE (SPEC S4-V27): references are ANALYZED, never separated or sampled —
analysis in, no stems out. Nothing of the reference's audio enters the session.
"""
import argparse, json, os, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from analyze2 import analyze  # noqa: E402

M1 = os.path.join(ROOT, "app/build/m1_artefacts/Release/m1")

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
BANDS = ["low_20_120", "lowmid_120_500", "mid_500_2k", "himid_2k_6k", "high_6k_up"]
BAND_MOVES_UP = {   # our band is BELOW the reference -> how to ADD energy there (at the source)
    "low_20_120":    "raise 808/sub gain +2..3 or lengthen kick_808 decay (0.45->0.7)",
    "lowmid_120_500":"raise keys/pad/snare-body +2..3 (or dark-filter trick: LP the pad ~400Hz + makeup, see ambient law)",
    "mid_500_2k":    "raise leads/melodic +2..4 or open pluck color / keys cutoff",
    "himid_2k_6k":   "raise snare snap / acid accent / brighten fx_saturate tone",
    "high_6k_up":    "raise hats gain/tone (tone 9500->11000, sizzle up) or open-hat velocity",
}
BAND_MOVES_DOWN = { # our band EXCEEDS the reference -> how to REMOVE energy (at the source)
    "low_20_120":    "trim 808/sub -2..4 or SHORTEN kick_808 decay (linear adsr holds ~8dB more than an exp drop)",
    "lowmid_120_500":"trim pads/keys -2..3 or LP them lower",
    "mid_500_2k":    "trim melodic sources -2..3",
    "himid_2k_6k":   "soften snare snap / lower saturate tone",
    "high_6k_up":    "trim hats -2..3 or shorten hat decay",
}


def prep_wav(path):
    """Any container ffmpeg reads -> temp wav (analysis only)."""
    if path.lower().endswith(".wav"):
        return path, None
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    tmp.close()
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", path,
                    "-ac", "2", "-ar", "44100", tmp.name], check=True)
    return tmp.name, tmp.name


def current_wav(song, wav):
    if wav:
        return os.path.abspath(wav)
    j = song if song.endswith(".json") else os.path.join(ROOT, "songs", f"{song}.json")
    if not os.path.exists(j):
        sys.exit(f"no such song: {j}")
    w = j[:-5] + ".wav"
    if not os.path.exists(w) or os.path.getmtime(w) < os.path.getmtime(j):
        r = subprocess.run([M1, "render", j, w], capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit(f"render failed: {r.stderr[-400:]}")
    return w


def key_gap(ref_key, cur_key):
    if not ref_key or not cur_key or ref_key == cur_key:
        return None
    try:
        rn, rmode = ref_key.split()
        cn, cmode = cur_key.split()
        d = (NOTE_NAMES.index(rn) - NOTE_NAMES.index(cn)) % 12
        d = d - 12 if d > 6 else d
        move = f"transpose {d:+d} semitones" if d else "same tonic"
        if rmode != cmode:
            move += f" + mode differs (ref {rmode}, ours {cmode}) — check the 3rd/6th degrees"
        return {"metric": "key", "ref": ref_key, "cur": cur_key, "move": move}
    except ValueError:
        return {"metric": "key", "ref": ref_key, "cur": cur_key, "move": "re-check keys by ear (detector is weak on subs)"}


def predicted_params(song_arg, ref, cur):
    """v2 — THE DIFF-MST SPIRIT, deterministic: per-band LUFS deltas become NAMED
    PARAMETER VALUES ("keys: gainDb -9 -> -6.4"), allocated to the tracks whose SOLO
    STEMS own each band (render-stems + per-stem analysis), clamped ±6 dB. Interpretable
    by construction — every number is a knob the user can drag back."""
    import subprocess, tempfile, shutil as sh
    j = song_arg if song_arg.endswith(".json") else os.path.join(ROOT, "songs", f"{song_arg}.json")
    song = json.load(open(j))
    rb, cb = ref.get("band_lufs"), cur.get("band_lufs")
    if not rb or not cb:
        return []
    d = tempfile.mkdtemp(prefix="refmatch_")
    try:
        r = subprocess.run([M1, "render-stems", j, d], capture_output=True, text=True)
        stems = sorted(f for f in os.listdir(d) if f.endswith(".wav"))
        if not stems:
            return []
        gains = {t.get("name"): float(t.get("gainDb", 0)) for t in song.get("tracks", [])}
        locked = {t.get("name") for t in song.get("tracks", []) if t.get("locked")}
        dom = {}                       # band -> [(track, band_share)]
        for f in stems:
            track = f.split("_", 1)[1][:-4] if "_" in f else f[:-4]
            m = analyze(os.path.join(d, f))
            if m["rms_db"] <= -55:
                continue
            for b in BANDS:
                share = m["band_energy_pct"][b]
                if share >= 30.0:
                    dom.setdefault(b, []).append((track, share))
        moves = []
        for b in BANDS:
            rv, cv = rb.get(b), cb.get(b)
            if rv is None or cv is None:
                continue
            delta = rv - cv            # band-LUFS dB gap (positive = we are short)
            if abs(delta) < 1.5 or b not in dom:
                continue
            owners = sorted(dom[b], key=lambda t: -t[1])[:2]
            tot = sum(s for _, s in owners)
            for track, share in owners:
                if track in locked:
                    moves.append({"track": track, "param": "gainDb", "skipped": "LOCKED"})
                    continue
                step = max(-6.0, min(6.0, delta * (share / tot)))
                if abs(step) < 0.8 or track not in gains:
                    continue
                moves.append({"track": track, "param": "gainDb", "band": b,
                              "from": gains[track], "to": round(gains[track] + step, 1),
                              "delta_db": round(step, 1),
                              "why": f"band {b}: ref {rv} vs ours {cv} LUFS; '{track}' owns {round(share)}% of its solo energy"})
        return moves
    finally:
        sh.rmtree(d, ignore_errors=True)


def gap_report(ref, cur):
    gaps = []
    dl = ref["lufs_integrated"] - cur["lufs_integrated"]
    if abs(dl) >= 1.0:
        gaps.append({"metric": "loudness_lufs", "ref": ref["lufs_integrated"],
                     "cur": cur["lufs_integrated"], "delta": round(dl, 2),
                     "move": f"{'raise' if dl > 0 else 'lower'} the makeup fx_trim before fx_brickwall by ~{abs(round(dl,1))} dB "
                             f"(input-trim into fx_saturate if the wall is already saturated)"})
    if cur["true_peak_dbtp"] > -1.0:
        gaps.append({"metric": "true_peak", "ref": ref["true_peak_dbtp"], "cur": cur["true_peak_dbtp"],
                     "move": "fx_brickwall ceiling -1.5 (sub-dominant law: -1.5..-2.0 when low band dominates)"})
    for b in BANDS:
        rv, cv = ref["band_energy_pct"][b], cur["band_energy_pct"][b]
        d = rv - cv
        if abs(d) >= 5.0:
            move = BAND_MOVES_UP[b] if d > 0 else BAND_MOVES_DOWN[b]
            gaps.append({"metric": f"band.{b}", "ref": rv, "cur": cv, "delta": round(d, 1), "move": move})
    rc, cc = ref["spectral_centroid_hz"], cur["spectral_centroid_hz"]
    if cc and (rc / max(cc, 1) > 1.3 or rc / max(cc, 1) < 0.7):
        bright = rc > cc
        gaps.append({"metric": "centroid_hz", "ref": rc, "cur": cc,
                     "move": ("brighten: hats/tone up, pluck color up, filter cutoffs up" if bright
                              else "darken: LP the top sources, saturate tone down, hats tone down")})
    dw = ref["stereo_width_db"] - cur["stereo_width_db"]
    if abs(dw) >= 6:
        gaps.append({"metric": "width_db", "ref": ref["stereo_width_db"], "cur": cur["stereo_width_db"],
                     "move": ("fx_widen on melodic tracks/buses + spread pans (keep low mono)" if dw > 0
                              else "narrow: reduce fx_widen width / recentre pans")})
    kg_ = key_gap(ref.get("key_estimate"), cur.get("key_estimate"))
    if kg_:
        gaps.append(kg_)
    r_arc = max(ref["rms_by_quarter_db"]) - min(ref["rms_by_quarter_db"])
    c_arc = max(cur["rms_by_quarter_db"]) - min(cur["rms_by_quarter_db"])
    if r_arc - c_arc >= 2.5:
        gaps.append({"metric": "dynamic_arc_db", "ref": round(r_arc, 1), "cur": round(c_arc, 1),
                     "move": "the reference MOVES more: add automation builds (curve>0 late-bloom) + a breakdown/drop contrast"})
    return gaps


def stored_report(ref_key, song):
    """R2 THE REFERENCE CIRCLE: gap report vs a KG-banked (:Reference) node —
    the record's DNA was captured at import, so the reference wav is never
    re-read. Runs under .venv (falkordb + the ears live here, NOT in the
    system python that hosts daw_mcp)."""
    import kg as kgmod
    try:
        k = kgmod.KG()
    except Exception as e:
        return {"error": f"knowledge graph unreachable ({e}) — docker start sotadaw-kg"}
    node = k.reference_view(str(ref_key))
    if node is None:
        names = sorted(x[0] for x in k.q("MATCH (n:Reference) RETURN n.name"))
        return {"error": f"no stored reference '{ref_key}'", "stored": names,
                "hint": "import_song_audio banks one automatically; "
                        "analyze_reference matches a raw wav directly"}
    prof = json.loads(node.get("band_profile_json") or "{}")
    bands = prof.get("band_energy_pct") or {}
    if any(b not in bands for b in BANDS) or node.get("lufs") is None:
        return {"error": f"stored reference '{node.get('name')}' is missing its "
                         f"band profile/lufs — re-import the record to re-bank it"}
    ref = {"lufs_integrated": node["lufs"], "true_peak_dbtp": node.get("dbtp"),
           "band_energy_pct": bands,
           "spectral_centroid_hz": prof.get("spectral_centroid_hz") or 0,
           "stereo_width_db": prof.get("stereo_width_db") or 0,
           "key_estimate": node.get("key") or None,
           "rms_by_quarter_db": prof.get("rms_by_quarter_db") or [0.0]}
    try:
        cur = analyze(current_wav(song, None))
    except SystemExit as e:                      # current_wav exits on missing song
        return {"error": str(e)}
    j = song if song.endswith(".json") else os.path.join(ROOT, "songs", f"{song}.json")
    sdoc = json.load(open(j)) if os.path.exists(j) else {}
    # ALWAYS-ON numeric deltas (ref minus current) — the gaps below are the
    # thresholded MOVES; these are the raw numbers even when the mix already sits.
    deltas = {"lufs_db": round(ref["lufs_integrated"] - cur["lufs_integrated"], 2),
              "dbtp_db": round((ref["true_peak_dbtp"] or 0) - cur["true_peak_dbtp"], 2),
              "centroid_hz": round(ref["spectral_centroid_hz"] - cur["spectral_centroid_hz"]),
              "width_db": round(ref["stereo_width_db"] - cur["stereo_width_db"], 1),
              "bpm": round(float(node.get("bpm") or 0) - float(sdoc.get("bpm") or 0), 1)}
    for b, rv in bands.items():
        deltas[f"band.{b}_pct"] = round(rv - cur["band_energy_pct"].get(b, 0.0), 1)
    ref_secs = json.loads(node.get("sections_json") or "[]")
    out = {"reference": {"name": node.get("name"),
                         "hash": str(node.get("source_file_hash"))[:10],
                         "bpm": node.get("bpm"), "key": node.get("key"),
                         "lufs": node.get("lufs"), "dbtp": node.get("dbtp"),
                         "crest": node.get("crest"), "sections": len(ref_secs),
                         "chord_bars": len(json.loads(node.get("chords_json") or "[]")),
                         "groove": node.get("groove_name") or None,
                         "sounds_like": node.get("sounds_like")},
           "deltas_ref_minus_current": deltas,
           "gaps": gap_report(ref, cur),
           "structure": {"ref_sections": [(s.get("name"), s.get("startBar"))
                                          for s in ref_secs[:12]],
                         "current_sections": [(s.get("name"), s.get("startBar"))
                                              for s in (sdoc.get("sections") or [])[:12]]}}
    if node.get("groove_name"):
        out["groove_move"] = (f"apply_groove '{node['groove_name']}' on drums/hats "
                              f"= the record's own timing DNA")
    return out


def mixtarget_lane(genre, cur):
    try:
        import kg as kgmod
        c = kgmod.connect()
        res = c.query(f"MATCH (g:Genre {{name:'{genre}'}})-[:TARGETS]->(m:MixTarget) RETURN properties(m)")
        if not res.result_set:
            return {"genre": genre, "error": "no MixTarget in KG"}
        m = res.result_set[0][0]
        checks = []
        lo, hi = m.get("lufs_lo"), m.get("lufs_hi")
        L = cur["lufs_integrated"]
        checks.append({"check": f"lufs in [{lo},{hi}]", "value": L, "ok": lo <= L <= hi})
        checks.append({"check": "clipped == 0", "value": cur["clipped_samples"], "ok": cur["clipped_samples"] == 0})
        order = m.get("band_order", "")
        if order:
            keys = {"low": "low_20_120", "lowmid": "lowmid_120_500", "mid": "mid_500_2k"}
            names = order.split(">")
            vals = [cur["band_energy_pct"][keys[n]] for n in names if n in keys]
            checks.append({"check": f"band order {order}", "value": vals,
                           "ok": all(vals[i] > vals[i+1] for i in range(len(vals)-1))})
        for floor_key, band in (("mid_floor_pct", "mid_500_2k"), ("himid_floor_pct", "himid_2k_6k")):
            if m.get(floor_key) is not None:
                v = cur["band_energy_pct"][band]
                checks.append({"check": f"{band} >= {m[floor_key]}%", "value": v, "ok": v >= m[floor_key]})
        return {"genre": genre, "target": m, "checks": checks}
    except Exception as e:  # KG down -> reference lane still works
        return {"genre": genre, "error": f"KG unavailable: {e}"}


# ---------------- THE REFERENCE DECK (BEST_DAW_30 #7b) ----------------
# "make it sit like THESE tracks" as a STANDING per-project contract, not a
# one-off report: songs/<name>.refs.json = [{"path", "weight"}]; the composite
# (weighted band curve / LUFS / width / centroid / quarter-arc) becomes the
# reference; every ref's analysis is content-cached (path+mtime+size) so the
# deck re-judges in milliseconds. THE LEGAL LINE holds: analysis in, never
# audio out — the deck stores numbers and paths, zero samples.
SONGS_DIR = os.path.join(ROOT, "songs")
REFCACHE = os.path.join(SONGS_DIR, ".refcache")
DECK_MEAN_KEYS = ("lufs_integrated", "true_peak_dbtp",
                  "spectral_centroid_hz", "stereo_width_db")


def deck_path(song):
    return os.path.join(SONGS_DIR, f"{song}.refs.json")


def deck_load(song):
    try:
        rows = json.load(open(deck_path(song)))
        return rows if isinstance(rows, list) else []
    except Exception:
        return []


def deck_save(song, rows):
    p = deck_path(song)
    tmp = p + ".w~"
    json.dump(rows, open(tmp, "w"), indent=1)
    os.replace(tmp, p)


def ref_analysis_cached(path):
    import hashlib
    st = os.stat(path)
    key = hashlib.sha1(f"{os.path.abspath(path)}|{st.st_mtime_ns}|{st.st_size}"
                       .encode()).hexdigest()[:16]
    cp = os.path.join(REFCACHE, key + ".json")
    if os.path.exists(cp):
        try:
            return json.load(open(cp))
        except Exception:
            pass
    wav, tmp = prep_wav(os.path.abspath(path))
    try:
        a_ = analyze(wav)
    finally:
        if tmp:
            os.unlink(tmp)
    os.makedirs(REFCACHE, exist_ok=True)
    tw = cp + ".w~"
    json.dump(a_, open(tw, "w"), default=str)
    os.replace(tw, cp)
    return a_


def deck_composite(song):
    """-> (composite ref-dict for gap_report, per-ref table). (None, []) if empty."""
    rows = deck_load(song)
    if not rows:
        return None, []
    tw = sum(max(0.0, float(r.get("weight", 1))) for r in rows) or 1.0
    acc = {k: [0.0, 0.0] for k in DECK_MEAN_KEYS}      # [weighted sum, weight seen]
    comp = {"band_energy_pct": {b: 0.0 for b in BANDS}}
    quarters, keys, per = [0.0] * 4, [], []
    for r in rows:
        a_ = ref_analysis_cached(r["path"] if os.path.isabs(r["path"])
                                 else os.path.join(ROOT, r["path"]))
        w = max(0.0, float(r.get("weight", 1))) / tw
        per.append({"path": r["path"], "weight": r.get("weight", 1),
                    "lufs": round(float(a_["lufs_integrated"]), 2),
                    "centroid_hz": round(float(a_["spectral_centroid_hz"]))})
        for k in DECK_MEAN_KEYS:
            v = a_.get(k)
            if v is not None:              # some analyses lack dbtp — skip, don't die
                acc[k][0] += w * float(v)
                acc[k][1] += w
        for b in BANDS:
            comp["band_energy_pct"][b] += w * float(a_["band_energy_pct"][b])
        rq = a_.get("rms_by_quarter_db") or [0.0] * 4
        for i in range(4):
            quarters[i] += w * float(rq[i])
        keys.append(a_.get("key_estimate"))
    comp["band_energy_pct"] = {b: round(v, 2) for b, v in comp["band_energy_pct"].items()}
    for k in DECK_MEAN_KEYS:
        comp[k] = round(acc[k][0] / acc[k][1], 2) if acc[k][1] > 0 else 0.0
    comp["rms_by_quarter_db"] = quarters
    comp["key_estimate"] = keys[0] if keys and all(k == keys[0] for k in keys) else None
    comp["file"] = f"DECK({len(rows)} refs)"
    return comp, per


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("reference", nargs="?")
    ap.add_argument("--stored", help="R2: match vs a KG-banked Reference "
                                     "(name or hash prefix) — no wav re-read")
    ap.add_argument("--song")
    ap.add_argument("--wav")
    ap.add_argument("--genre")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--deck", metavar="SONG",
                    help="judge SONG's mix against its reference DECK composite")
    ap.add_argument("--deck-add", metavar="AUDIO", help="add a ref to --song's deck")
    ap.add_argument("--deck-remove", metavar="N_OR_PATH")
    ap.add_argument("--deck-list", action="store_true")
    ap.add_argument("--weight", type=float, default=1.0)
    a = ap.parse_args()
    if a.deck_add or a.deck_remove or a.deck_list:
        if not a.song:
            sys.exit("deck edits need --song <name>")
        rows = deck_load(a.song)
        if a.deck_add:
            p = os.path.abspath(a.deck_add)
            if not os.path.exists(p):
                sys.exit(f"no such audio: {p}")
            rows = [r for r in rows if os.path.abspath(r["path"]) != p]
            rows.append({"path": p, "weight": a.weight})
            deck_save(a.song, rows)
            ref_analysis_cached(p)          # pay the analysis now, judge free later
        elif a.deck_remove:
            try:
                idx = int(a.deck_remove) - 1
                rows = [r for i, r in enumerate(rows) if i != idx]
            except ValueError:
                rows = [r for r in rows
                        if a.deck_remove not in (r["path"], os.path.basename(r["path"]))]
            deck_save(a.song, rows)
        print(json.dumps({"song": a.song, "deck":
                          [{"i": i + 1, "path": r["path"], "weight": r.get("weight", 1)}
                           for i, r in enumerate(deck_load(a.song))]}, indent=1))
        return
    if a.deck:
        comp, per = deck_composite(a.deck)
        if comp is None:
            sys.exit(f"'{a.deck}' has no reference deck — add refs with --deck-add")
        cur = analyze(current_wav(a.deck, None))
        out = {"deck": per, "reference": {k: comp[k] for k in
               ("file", "lufs_integrated", "true_peak_dbtp", "band_energy_pct",
                "spectral_centroid_hz", "stereo_width_db", "key_estimate")},
               "current": {k: cur[k] for k in
               ("file", "lufs_integrated", "true_peak_dbtp", "band_energy_pct",
                "spectral_centroid_hz", "stereo_width_db", "key_estimate")},
               "gaps": gap_report(comp, cur)}
        try:
            out["predicted_params"] = predicted_params(a.deck, comp, cur)
        except Exception as e:
            out["predicted_params"] = [{"error": str(e)[:200]}]
        if a.genre:
            out["mixtarget"] = mixtarget_lane(a.genre, cur)
        if a.json:
            print(json.dumps(out, indent=1))
            return
        print(f"REFERENCE DECK REPORT  {comp['file']}  cur={os.path.basename(out['current']['file'])}")
        for r in per:
            print(f"  deck: {os.path.basename(r['path'])} w={r['weight']} "
                  f"lufs {r['lufs']} centroid {r['centroid_hz']}Hz")
        if not out["gaps"]:
            print("  no gaps >= threshold — the mix already sits like the deck.")
        for g in out["gaps"]:
            print(f"  [{g['metric']}] ref={g.get('ref')} cur={g.get('cur')}"
                  + (f" delta={g['delta']}" if "delta" in g else ""))
            print(f"      -> {g['move']}")
        return
    if a.stored:
        if not a.song:
            sys.exit("--stored needs --song <name> for the current mix")
        print(json.dumps(stored_report(a.stored, a.song), indent=1, default=str))
        return
    if not a.reference:
        sys.exit("need a reference audio file (or --stored <name>)")
    if not a.song and not a.wav:
        sys.exit("need --song <name> or --wav <path> for the current mix")

    ref_path, tmp = prep_wav(os.path.abspath(a.reference))
    try:
        ref = analyze(ref_path)
        cur = analyze(current_wav(a.song, a.wav))
    finally:
        if tmp:
            os.unlink(tmp)

    out = {"reference": {k: ref[k] for k in ("file", "lufs_integrated", "true_peak_dbtp", "band_energy_pct",
                                             "spectral_centroid_hz", "stereo_width_db", "key_estimate")},
           "current": {k: cur[k] for k in ("file", "lufs_integrated", "true_peak_dbtp", "band_energy_pct",
                                           "spectral_centroid_hz", "stereo_width_db", "key_estimate")},
           "gaps": gap_report(ref, cur)}
    if a.song:   # v2: named parameter predictions (needs the song for stems + gains)
        try:
            out["predicted_params"] = predicted_params(a.song, ref, cur)
        except Exception as e:
            out["predicted_params"] = [{"error": str(e)[:200]}]
    if a.genre:
        out["mixtarget"] = mixtarget_lane(a.genre, cur)

    if a.json:
        print(json.dumps(out, indent=1))
        return
    print(f"REFERENCE GAP REPORT  ref={os.path.basename(a.reference)}  cur={os.path.basename(out['current']['file'])}")
    if not out["gaps"]:
        print("  no gaps >= threshold — the mix already sits like the reference.")
    for g in out["gaps"]:
        ref_v, cur_v = g.get("ref"), g.get("cur")
        print(f"  [{g['metric']}] ref={ref_v} cur={cur_v}" + (f" delta={g['delta']}" if "delta" in g else ""))
        print(f"      -> {g['move']}")
    pp = out.get("predicted_params") or []
    if pp:
        print("PREDICTED PARAMS (v2 — named values, drag any of them back):")
        for m in pp:
            if m.get("skipped"):
                print(f"  {m['track']}: SKIPPED ({m['skipped']})")
            elif m.get("error"):
                print(f"  (prediction unavailable: {m['error']})")
            else:
                print(f"  {m['track']}.{m['param']}: {m['from']} -> {m['to']}  ({m['delta_db']:+} dB)  [{m['why']}]")
    mt = out.get("mixtarget")
    if mt:
        print(f"KG MIXTARGET LANE ({mt['genre']}):" + (f" {mt['error']}" if "error" in mt else ""))
        for c in mt.get("checks", []):
            print(f"  {'OK ' if c['ok'] else 'MISS'} {c['check']}  (value: {c['value']})")


if __name__ == "__main__":
    main()
