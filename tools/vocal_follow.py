#!/usr/bin/env python3
"""THE FOLLOWING VOICE — vocal lanes are EDITABLE MIDI; the render follows.

Chezy 2026-07-11: "THE VOCALS ARE A RE-RENDERED AUDIO?! THAT LITERALLY
DEFEATS THE POINT OF CONVERTING IT! IT NEEDS TO BE EDITABLE MIDI!"

The law this file makes true: a vocal lane's MIDI (vocals_sketch) is the
SOURCE OF TRUTH; the sounding wav is a RENDER of that MIDI. Edit the notes
and the voice re-sings them — in the ORIGINAL singer's timbre
(tools/retune.py --guide-track: WORLD resynth, formants kept, surgical
splice — every span whose pitch you did NOT touch stays bit-true record
audio; only the edited notes vocode).

Stomp-proof by design (LIVE-APP STOMP LAW): follow() rewrites ONLY the
rendered wav (atomic tmp + os.replace, loudness-matched to the outgoing
take). song.json is NEVER written by follow — there is nothing for an open
app to save over. The lane simply plays the new bytes.

    binding   songs/<name>_vocals/follow.json
              {out_wav, src_audio, src_track, backend, style, f0, melody_sha}
    check     melody_sha(current notes) vs stamped — drift = stale
    follow    stale -> re-render src_audio guided by the edited melody
              -> out_wav replaced in place

Backends:
    retune  imported record vocals (the star): retune.py --guide-track
    sing    DiffSinger takes: re-runs the recorded sing argv (sing.py owns
            its own landing; follow just re-stamps the sha)

CLI:
    vocal_follow.py <song> --check
    vocal_follow.py <song>                    # follow stale bindings
    vocal_follow.py <song> --force            # re-render even if clean
    vocal_follow.py <song> --bind TRACK OUT SRC   # stamp a binding
    vocal_follow.py <song> --mint STEM_WAV --bpm N  # melody lane from a stem

Kill switch: SOTADAW_NO_FOLLOW=1 (honored by the sidecar watcher).
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "songs")
VENVPY = os.path.join(ROOT, ".venv", "bin", "python")
if not os.path.exists(VENVPY):
    VENVPY = sys.executable
RETUNE = os.path.join(ROOT, "tools", "retune.py")
SKETCH_LANE = "vocals_sketch"


def say(msg):
    print(f"[voice-follow] {msg}", flush=True)


def vdir(name):
    return os.path.join(SONGS, f"{name}_vocals")


def bind_path(name):
    return os.path.join(vdir(name), "follow.json")


def song_path(name):
    return os.path.join(SONGS, f"{name}.json")


def _canon(notes):
    return sorted((round(float(n.get("start", 0.0)), 4),
                   int(n.get("pitch", 0)),
                   round(float(n.get("len", 0.0)), 4))
                  for n in (notes or []) if isinstance(n, dict))


def melody_sha(notes):
    """Canonical hash of the MELODY — start/pitch/len only. Velocity and
    lane cosmetics are not pitch targets; retune's guide ignores them, so
    they must not trigger a re-render."""
    return hashlib.sha256(json.dumps(_canon(notes)).encode()).hexdigest()


def edited_spans(old_canon, new_canon, pad=0.15, merge_gap=0.5):
    """THE SURGERY MAP: beat spans covering exactly the notes that changed
    (moved, retuned, added, removed — symmetric difference), padded and
    merged. Everything OUTSIDE these spans is never re-rendered — the
    record's own performance stays bit-true (E2E receipt 2026-07-11: a
    whole-take follow moved UNEDITED notes 114-337 cents toward the
    transcription; region surgery is the law that forbids that)."""
    o = set(map(tuple, old_canon or []))
    n = set(map(tuple, new_canon or []))
    spans = sorted((s - pad, s + max(l, 0.05) + pad) for (s, p, l) in o ^ n)
    merged = []
    for a, b in spans:
        if merged and a - merged[-1][1] <= merge_gap:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([max(0.0, a), b])
    return [(a, b) for a, b in merged]


def load_bindings(name):
    try:
        return json.load(open(bind_path(name))).get("bindings", [])
    except Exception:
        return []


def save_bindings(name, bindings):
    os.makedirs(vdir(name), exist_ok=True)
    tmp = bind_path(name) + ".tmp"
    json.dump({"bindings": bindings}, open(tmp, "w"), indent=1)
    os.replace(tmp, bind_path(name))


def _notes_of(song, track_name):
    for t in song.get("tracks", []):
        if t.get("name") == track_name:
            return t.get("notes", [])
    return None


def bind(name, src_track, out_wav, src_audio, backend="retune",
         style="transparent", f0="fcpe", argv=None):
    """Stamp a binding: out_wav is a RENDER of src_track's melody applied to
    src_audio. The stamped sha is the baseline — follow fires only on DRIFT
    (the user's edit), never on the raw transcription itself."""
    song = json.load(open(song_path(name)))
    notes = _notes_of(song, src_track)
    if notes is None:
        raise ValueError(f"binding refused: track '{src_track}' not in {name}")
    b = {"out_wav": out_wav, "src_audio": src_audio, "src_track": src_track,
         "backend": backend, "style": style, "f0": f0,
         "melody_sha": melody_sha(notes), "melody": _canon(notes),
         "bound_at": time.time()}
    if argv:
        b["argv"] = argv
    bindings = [x for x in load_bindings(name)
                if x.get("out_wav") != out_wav]
    bindings.append(b)
    save_bindings(name, bindings)
    say(f"bound {os.path.basename(out_wav)} <- {src_track} "
        f"({backend}, {len(notes)} notes)")
    return b


def check(name):
    """Staleness report — cheap (sha compare), honest on misses."""
    out = []
    try:
        song = json.load(open(song_path(name)))
    except Exception as e:
        return [{"stale": False, "reason": f"song unreadable: {e}"}]
    for b in load_bindings(name):
        r = {"out_wav": b.get("out_wav"), "src_track": b.get("src_track"),
             "backend": b.get("backend", "retune"), "stale": False}
        notes = _notes_of(song, b.get("src_track", ""))
        if notes is None:
            r["reason"] = "source track missing from song"
        elif not os.path.exists(os.path.join(ROOT, b.get("out_wav", ""))):
            r["reason"] = "rendered wav missing"
        elif melody_sha(notes) != b.get("melody_sha"):
            r["stale"] = True
            r["reason"] = "melody edited (sha drift)"
        else:
            r["reason"] = "clean"
        out.append(r)
    return out


def _match_loudness(new_path, ref_path):
    """Level-match the fresh render to the OUTGOING take so the lane gain
    stays true. Baked into the samples (float32) — no song.json writes.
    Fail-open: any miss leaves the render untouched."""
    try:
        import numpy as np
        import soundfile as sf
        x, sr = sf.read(new_path, dtype="float64", always_2d=True)
        r, sr2 = sf.read(ref_path, dtype="float64", always_2d=True)
        xm, rm = x.mean(axis=1), r.mean(axis=1)
        try:
            import pyloudnorm
            lx = pyloudnorm.Meter(sr).integrated_loudness(xm)
            lr = pyloudnorm.Meter(sr2).integrated_loudness(rm)
            if not (np.isfinite(lx) and np.isfinite(lr)):
                raise ValueError("silent")
            delta = lr - lx
        except Exception:
            ex = float(np.sqrt(np.mean(xm ** 2)) + 1e-12)
            er = float(np.sqrt(np.mean(rm ** 2)) + 1e-12)
            if ex < 1e-9 or er < 1e-9:
                return
            delta = 20.0 * np.log10(er / ex)
        delta = max(-12.0, min(12.0, delta))
        if abs(delta) < 0.3:
            return
        y = np.clip(x * (10.0 ** (delta / 20.0)), -1.0, 1.0)
        sf.write(new_path, y.astype("float32"), sr, subtype="FLOAT")
        say(f"level-matched render to outgoing take ({delta:+.1f}dB)")
    except Exception as e:
        say(f"level match skipped ({type(e).__name__}: {e})")


def _run_retune(name, b, in_wav, tmp_out, region=None, song_json=None):
    rp = os.path.join(vdir(name), "last_follow_report.json")
    cmd = [VENVPY, RETUNE, in_wav, tmp_out,
           "--song", song_json or song_path(name),
           "--guide-track", b["src_track"],
           "--style", b.get("style", "transparent"),
           "--f0", b.get("f0", "fcpe"), "--report", rp]
    if region:
        cmd += ["--region", f"{region[0]:.4f}", f"{region[1]:.4f}"]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
    if p.returncode != 0 or not os.path.exists(tmp_out):
        tail = (p.stderr or p.stdout or "").strip().splitlines()[-3:]
        raise RuntimeError("retune failed: " + " | ".join(tail))
    return rp


def _run_sing(name, b, in_wav, tmp_out, region=None, song_json=None):
    """DiffSinger takes: the sing rail owns rendering AND landing (stable
    wav names are rewritten in place). follow only re-runs it."""
    argv = b.get("argv")
    if not argv:
        raise RuntimeError("sing binding has no recorded argv")
    p = subprocess.run(argv, capture_output=True, text=True, timeout=3600)
    if p.returncode != 0:
        tail = (p.stderr or p.stdout or "").strip().splitlines()[-3:]
        raise RuntimeError("sing re-run failed: " + " | ".join(tail))
    return None


BACKENDS = {"retune": _run_retune, "sing": _run_sing}
MAX_SPANS = 8          # more edited spans than this = the user re-drew the
WHOLE_TAKE_FRAC = 0.5  # line (or >50% of notes changed) -> whole-take render


def _plan_spans(b, notes):
    """None = whole-take (mass edit / legacy binding without a stored
    melody); else the SURGERY MAP of edited beat spans."""
    old = b.get("melody")
    if old is None:
        return None
    spans = edited_spans(old, _canon(notes))
    if not spans or len(spans) > MAX_SPANS:
        return None
    o, cur = set(map(tuple, old)), set(map(tuple, _canon(notes)))
    edits = max(len(o - cur), len(cur - o))    # an edited note is ONE edit,
    if edits > WHOLE_TAKE_FRAC * max(len(old), len(notes), 1):   # not two
        return None
    return spans


def follow(name, force=False):
    """Re-render every stale binding — SURGICALLY: only the edited beat
    spans pass through the vocoder; everything else is copied bit-true from
    the base take. First follow REBASES onto the pristine src_audio (the
    record's own stem outranks any earlier re-render); later follows chain
    on the current take so old edits survive. Returns a report list; a
    single binding's failure is an honest record, never a raise."""
    reports = []
    song = json.load(open(song_path(name)))
    bindings = load_bindings(name)
    changed = False
    for b in bindings:
        rec = {"out_wav": b.get("out_wav"), "src_track": b.get("src_track"),
               "backend": b.get("backend", "retune")}
        notes = _notes_of(song, b.get("src_track", ""))
        if notes is None:
            rec["result"] = "skipped: source track missing"
            reports.append(rec)
            continue
        sha = melody_sha(notes)
        if sha == b.get("melody_sha") and not force:
            rec["result"] = "clean"
            reports.append(rec)
            continue
        out_abs = os.path.join(ROOT, b["out_wav"])
        work = out_abs + ".follow_work.wav"
        tmp_out = out_abs + ".follow_tmp.wav"
        t0 = time.time()
        try:
            runner = BACKENDS.get(rec["backend"])
            if runner is None:
                raise RuntimeError(f"unknown backend {rec['backend']}")
            if rec["backend"] == "sing":       # sing owns its own landing
                say(f"{name}: {b['src_track']} edited -> re-singing "
                    f"{os.path.basename(b['out_wav'])}")
                runner(name, b, None, tmp_out)
            else:
                spans = _plan_spans(b, notes)
                rebase = not b.get("rebased") and os.path.exists(
                    os.path.join(ROOT, b.get("src_audio", "")))
                base = (os.path.join(ROOT, b["src_audio"]) if rebase
                        else out_abs)
                say(f"{name}: {b['src_track']} edited -> re-rendering "
                    + os.path.basename(b['out_wav'])
                    + (f" ({len(spans)} edited span(s), rest bit-true"
                       if spans else " (whole take")
                    + (", rebased onto the record's own stem)" if rebase
                       else ")"))
                song_json = None
                if spans is not None:
                    # THE EDIT IS AUTHORITATIVE: inside an edited span the
                    # guide is ONLY the changed notes — an unchanged note
                    # overlapping the edit (transcription artifact) must not
                    # compete for the target (E2E receipt: the edited note's
                    # tail corrected -167c toward an overlapping stale C3).
                    old_set = set(map(tuple, b.get("melody") or []))
                    changed = [n for n in notes if isinstance(n, dict) and
                               (round(float(n.get("start", 0.0)), 4),
                                int(n.get("pitch", 0)),
                                round(float(n.get("len", 0.0)), 4))
                               not in old_set]
                    import copy
                    gsong = copy.deepcopy(song)
                    for gt in gsong.get("tracks", []):
                        if gt.get("name") == b["src_track"]:
                            gt["notes"] = changed
                    song_json = os.path.join(vdir(name), "_follow_guide.json")
                    os.makedirs(vdir(name), exist_ok=True)
                    json.dump(gsong, open(song_json, "w"))
                import shutil
                shutil.copyfile(base, work)
                for region in (spans or [None]):
                    rec["report"] = runner(name, b, work, tmp_out,
                                           region=region, song_json=song_json)
                    os.replace(tmp_out, work)
                if os.path.exists(out_abs) and (rebase or spans is None):
                    _match_loudness(work, out_abs)
                os.replace(work, out_abs)
                b["rebased"] = True
                if spans:
                    rec["spans"] = [[round(a, 3), round(z, 3)]
                                    for a, z in spans]
            b["melody_sha"] = sha
            b["melody"] = _canon(notes)
            b["last_follow"] = time.time()
            changed = True
            rec["result"] = "followed"
            rec["seconds"] = round(time.time() - t0, 1)
            say(f"FOLLOWED: {os.path.basename(b['out_wav'])} now sings the "
                f"edited melody ({rec['seconds']}s; unedited spans bit-true)")
        except Exception as e:
            rec["result"] = f"failed: {e}"
            say(f"follow failed honestly: {e}")
        finally:
            for leftover in (work, tmp_out,
                             os.path.join(vdir(name), "_follow_guide.json")):
                if os.path.exists(leftover):
                    try:
                        os.remove(leftover)
                    except OSError:
                        pass
        reports.append(rec)
    if changed:
        save_bindings(name, bindings)
    return reports


def land_sketch(name, notes, muted=True):
    """Land vocals_sketch as the melody edit surface — idempotent (an
    existing lane is never clobbered), atomic, and the melody is cached to
    <name>_vocals/melody.json so the sidecar watcher can re-land it if a
    live app's stale save stomps the lane (LIVE-APP STOMP LAW)."""
    sp = song_path(name)
    song = json.load(open(sp))
    os.makedirs(vdir(name), exist_ok=True)
    cache = os.path.join(vdir(name), "melody.json")
    if not os.path.exists(cache):
        json.dump({"notes": notes}, open(cache, "w"))
    if _notes_of(song, SKETCH_LANE) is not None:
        return False
    lane = {"name": SKETCH_LANE,
            "source": {"kind": "sample", "kit": "choir"},
            "gainDb": -1.5, "muted": muted, "notes": notes,
            "comment": "THE EDIT SURFACE: this MIDI is the vocal's source - "
                       "edit a note and the voice re-sings it in the "
                       "original singer's timbre (vocal_follow)"}
    idx = max((i for i, t in enumerate(song.get("tracks", []))
               if "vocal" in str(t.get("name", "")).lower()), default=-1)
    song.setdefault("tracks", []).insert(idx + 1, lane)
    tmp = sp + ".tmp"
    json.dump(song, open(tmp, "w"), indent=1)
    os.replace(tmp, sp)
    say(f"landed {SKETCH_LANE} on {name} ({len(notes)} notes, "
        f"{'muted edit surface' if muted else 'sounding'})")
    return True


def cached_melody(name):
    try:
        return json.load(open(os.path.join(vdir(name), "melody.json")))["notes"]
    except Exception:
        return None


def mint(name, stem_wav, bpm, key=None):
    """Melody lane from a vocal stem (basic-pitch via the import rail's own
    transcriber) — cached, then landed muted."""
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    from stems_import import transcribe_v2
    notes, engine = transcribe_v2(stem_wav, bpm, role="vocal", key=key)
    say(f"minted {len(notes)} melody notes from "
        f"{os.path.basename(stem_wav)} ({engine})")
    if len(notes) < 4:
        raise RuntimeError(f"stem too sparse to mint a melody ({len(notes)} notes)")
    os.makedirs(vdir(name), exist_ok=True)
    json.dump({"notes": notes},
              open(os.path.join(vdir(name), "melody.json"), "w"))
    land_sketch(name, notes, muted=True)
    return notes


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("song")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--bind", nargs=3, metavar=("TRACK", "OUT_WAV", "SRC_AUDIO"))
    ap.add_argument("--backend", default="retune", choices=sorted(BACKENDS))
    ap.add_argument("--style", default="transparent")
    ap.add_argument("--f0", default="fcpe")
    ap.add_argument("--mint", metavar="STEM_WAV")
    ap.add_argument("--bpm", type=float)
    a = ap.parse_args()
    name = os.path.splitext(os.path.basename(a.song))[0]
    if a.mint:
        if not a.bpm:
            song = json.load(open(song_path(name)))
            a.bpm = float(song.get("bpm", 120))
        mint(name, a.mint, a.bpm)
        return 0
    if a.bind:
        bind(name, a.bind[0], a.bind[1], a.bind[2],
             backend=a.backend, style=a.style, f0=a.f0)
        return 0
    if a.check:
        for r in check(name):
            print(json.dumps(r))
        return 0
    reps = follow(name, force=a.force)
    print(json.dumps(reps, indent=1))
    return 0 if all("failed" not in str(r.get("result")) for r in reps) else 1


if __name__ == "__main__":
    sys.exit(main())
