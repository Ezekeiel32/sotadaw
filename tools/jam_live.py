#!/usr/bin/env python3
"""THE LIVE JAM — the realtime scheduler that makes the AI band "just go": while
phrase N PLAYS (its real wall-clock duration), phrase N+1 is rendered CONCURRENTLY
(a real m1 subprocess racing the deadline) and is ready BEFORE N ends — no underrun.
The band decides N+1 from N's ears DURING N's playback window (live feedback).

This is the realtime half of THE JAM (tools/jam.py — the proven brain). What it can
prove HEADLESS: the scheduling is realtime-sound (generate-ahead overlaps playback,
never underruns, feedback is causal within the window) and the take grows seamlessly.
What it can't prove headless: audio to speakers — that's the app's realtime device
(the ears tap the master graph identically whether it goes to a device or a file, so
the band's LISTENING is unchanged; only the output sink differs).

  jam_live.py <genre> <vibe> [--phrases 5] [--seed 0] [--bars 2]
"""
import argparse
import json
import math
import queue
import threading
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import jam                                       # the proven brain + helpers

M1, SONGS = jam.M1, jam.SONGS
read_human = jam.read_human   # the seam lives with the brain now


def PHRASE_WALL():
    """THE SEAT'S WALL LAW, finally enforced on the SPEAKERS FEED (2026-07-11
    'loud horrid sound': buses made full-ladder phrases render AT 0 dBFS with
    baked clipping — jam_live phrases are not ears-probes, they are what the
    ROOM HEARS). The constitution said it all along: 'seat phrases render
    through the same wall as every render'. Calibration wears the same wall,
    so the genre-relative energy mapping stays monotonic and consistent.
    jam.py's offline probes stay raw — nothing plays them."""
    return [{"id": "fx_truepeak", "params": {"ceiling": -1.2}}]




class _ServeRail:
    """THE WARM RAIL ON THE BANDSTAND (71360e0): one resident `m1 serve` per set
    answers phrase-miss renders without process spawn + engine init — slack GROWS
    and gen_cold SHRINKS (later JIT decides, more affordable punches/evolves).
    Cancellable protocol v2 = REPEAT-LAW compatible: cancel() is the kill.
    Fallback-total: any trouble marks the rail dead and callers use classic
    Popen. Kill-switch: SOTADAW_RENDER_SERVE=0. The resident dies with this
    process (CLOEXEC pipes)."""

    def __init__(self):
        self.p = None
        self.ready = False
        self.dead = os.environ.get("SOTADAW_RENDER_SERVE") == "0"
        self.next_id = 100
        self.submits = 0

    def boot(self):
        if self.dead or self.p is not None:
            return
        try:
            self.p = subprocess.Popen([M1, "serve"], stdin=subprocess.PIPE,
                                      stdout=subprocess.PIPE, text=True, bufsize=1)
            self.q = queue.Queue()
            threading.Thread(target=self._drain, daemon=True).start()
        except Exception:
            self.dead = True

    def _drain(self):
        # a BLOCKING readline defeated wait_reply's deadline (the pulse caught a
        # -0.3s underrun: a late reply was ACCEPTED instead of TimeoutExpired ->
        # the REPEAT LAW never fired). This thread drains stdout continuously;
        # deadlines are enforced by queue.get — no readline, no buffer traps.
        try:
            for ln in self.p.stdout:
                if ln.startswith('{"ok"') or "serve ready" in ln:
                    self.q.put(ln)
        except Exception:
            pass
        self.q.put(None)

    def _ensure_ready(self, deadline_s=25.0):
        if self.dead:
            return False
        if self.p is None:
            self.boot()
            if self.dead:
                return False
        if self.ready:
            return self.p.poll() is None
        t0 = time.monotonic()
        while time.monotonic() - t0 < deadline_s:
            try:
                ln = self.q.get(timeout=0.25)
            except queue.Empty:
                continue
            if ln is None:
                self.dead = True
                return False
            if "serve ready" in ln:
                self.ready = True
                return True
        self.dead = True
        return False

    def submit(self, pj, pw):
        if not self._ensure_ready():
            return None
        self.next_id += 1
        self.submits += 1
        rid = self.next_id
        try:
            self.p.stdin.write(json.dumps({"song": os.path.abspath(pj),
                                           "out": os.path.abspath(pw),
                                           "id": rid}) + "\n")
            self.p.stdin.flush()
            return rid
        except Exception:
            self.dead = True
            return None

    def wait_reply(self, rid, timeout=None):
        t0 = time.monotonic()
        while True:
            remaining = None if timeout is None else timeout - (time.monotonic() - t0)
            if remaining is not None and remaining <= 0:
                raise subprocess.TimeoutExpired(cmd="m1 serve", timeout=timeout)
            try:
                ln = self.q.get(timeout=min(0.25, remaining) if remaining is not None else 0.25)
            except queue.Empty:
                continue
            if ln is None:
                self.dead = True
                return {"ok": 0, "err": "rail died"}
            if ln.startswith('{"ok"'):
                try:
                    rep = json.loads(ln)
                except json.JSONDecodeError:
                    continue
                if rep.get("id") == rid:
                    return rep
                # stale reply from an earlier cancel: drained, keep reading

    def cancel(self, rid):
        try:
            self.p.stdin.write(json.dumps({"cancel": rid}) + "\n")
            self.p.stdin.flush()
            self.wait_reply(rid, timeout=30)   # drain OUR reply (cancelled or done)
        except Exception:
            self.dead = True

    def stop(self):
        if self.p is not None:
            try:
                self.p.stdin.write("quit\n")
                self.p.stdin.flush()
                self.p.wait(timeout=5)
            except Exception:
                try:
                    self.p.kill()
                except Exception:
                    pass
        self.p = None
        self.ready = False


def endless_target(vibe, pe):
    """B6 THE BANDSTAND: vibe arcs for a set with NO end — build/breakdown are
    one-shot journeys (8 phrase-equivalents) that then HOLD; wave cycles forever
    (16-pe period); steady/peak are levels. pe is RELATIVE to the arc's start, so
    switching vibes mid-set restarts the arc — the vibe box becomes an instrument."""
    x = max(0.0, float(pe))
    if vibe == "steady":
        return 0.6
    if vibe == "peak":
        return 0.85
    if vibe == "build":
        return 0.2 + 0.75 * min(1.0, x / 8.0)
    if vibe == "breakdown":
        return 0.9 - 0.7 * min(1.0, x / 8.0)
    return 0.25 + 0.7 * (0.5 - 0.5 * math.cos(math.pi * x / 8.0))   # wave


def jam_live(genre, vibe, phrases=5, seed=0, name="_jamlive", bars_per=2, ipc=None,
             human_path=None, follow=0.5, bpm=None, key=None):
    if vibe not in jam.VIBES:
        return None, f"unknown vibe '{vibe}'"
    endless = int(phrases) <= 0                  # B6: 0 = play until told to stop
    ipc = ipc or os.path.join(SONGS, ".jamlive_ipc")
    os.makedirs(ipc, exist_ok=True)
    # THE SPEAKERS WIRE (additive): a live.jsonl feed the app follows — each ready
    # phrase is announced the moment its render lands, so the app's realtime audio
    # device can CHAIN-PLAY the set while this scheduler keeps its own clock. The
    # ears/listening path is untouched (graph-side; identical device-vs-file).
    feed_path = os.path.join(ipc, "live.jsonl")
    # B6 LIVE CONTROLS: two tiny control files the UI writes while the set runs —
    # `stop` = end the set at the phrase boundary (the take is KEPT: a band that
    # burns the tape when you say "we're done" is not a band); `vibe.txt` = switch
    # the arc mid-set. Both are cleared here so a stale session never steers.
    stop_path = os.path.join(ipc, "stop")
    vibe_path = os.path.join(ipc, "vibe.txt")
    for pth in (feed_path, stop_path, vibe_path):
        try:
            os.remove(pth)
        except OSError:
            pass

    def feed(ev, **kw):
        try:
            with open(feed_path, "a") as f:
                f.write(json.dumps({"ev": ev, "t": round(time.time(), 2), **kw}) + "\n")
        except OSError:
            pass

    def stop_req():
        return os.path.exists(stop_path)

    def read_vibe():
        try:
            v = open(vibe_path).read().strip().lower()
        except OSError:
            return None
        return v if v in jam.VIBES else None
    import io
    import contextlib
    with contextlib.redirect_stdout(io.StringIO()):
        __import__("loop_gen").generate(genre, name + "_seed", bars=bars_per, seed=seed)
    sp = os.path.join(SONGS, f"{name}_seed.json")
    if not os.path.exists(sp):
        return None, f"no loop DNA for '{genre}'"
    base = json.load(open(sp)); os.remove(sp)
    jam.retarget_base(base, bpm=bpm, key=key)    # the room's world wins (B6)
    bpm, key = base.get("bpm", 120), base.get("key", "A minor")
    available = [t["name"] for t in base["tracks"] if t["name"] in jam.LADDER]
    dur = bars_per * 4 * 60.0 / bpm              # a phrase's REAL playback seconds
    # the SESSION event fires BEFORE the sound-check: the moment the band knows its
    # world (bpm/key) the room knows it too — the UI shows a live "sound check"
    # instead of dead air while the calibration renders run.
    feed("session", genre=genre, vibe=vibe, bpm=bpm, key=key,
         phrases=(0 if endless else phrases), phrase_dur=round(dur, 3),
         bars_per=bars_per, human=bool(human_path), endless=endless)

    rail = _ServeRail()
    rail.boot()          # the resident boots WHILE the sound-check renders below —
                         # by the first phrase-miss it is hot (no gen_cold spike)
    # genre-relative calibration (blocking, one-time — the sound-check before the set).
    # THE SOUND-CHECK IS CACHED (START LATENCY, docs/THE_BAND_SEAT.md B5): a repeat
    # set (same genre/seed/bars/binary) opens in ~ms instead of TWO blocking m1
    # renders; cold sets store themselves. phrase_energy reads the wav (the robust
    # offline ear), so a hit measures identically to a fresh render.
    def render(active, bright, tag):
        s = jam.build_phrase_song(base, active, bright, bpm, key)
        # +1 TAIL BAR (B6): sends ride the phrases now, so each render carries one
        # bar of ring-out past its musical length — the player overlap-adds it into
        # the next phrase (no chopped-reverb seam at every join). Calibration wears
        # the same tail AND the same wall so norm() maps apples to apples.
        s["lengthBars"] = bars_per + 1
        s["master"] = PHRASE_WALL()
        os.makedirs(ipc, exist_ok=True)   # self-heal: the shared scratch dir can vanish
        pj = os.path.join(ipc, f"{tag}.json"); pw = os.path.join(ipc, f"{tag}.wav")
        json.dump(s, open(pj, "w"))
        ej = os.path.join(ipc, "ears.jsonl")
        if os.path.exists(ej):
            os.remove(ej)
        try:
            import render_cache as _rcc
            _rcc.render_cached(pj, pw, quiet=True)
        except Exception:
            pass
        if not os.path.exists(pw):        # cache rail unavailable/failed: the old way
            subprocess.run([M1, "render", pj, pw], capture_output=True, timeout=120,
                           env=dict(os.environ, SOTADAW_IPC=ipc))
        return jam.phrase_energy(pw, ej)
    e_lo = render(list(jam.FOUNDATION), 0.2, "cal_lo")
    e_hi = render(list(jam.FOUNDATION) + available, 1.0, "cal_hi")
    span = max(1.5, e_hi - e_lo)   # dB span floor (phrase_energy is dB now)
    norm = lambda r: max(0.0, min(1.0, (r - e_lo) / span))

    # THE CACHE ON THE BANDSTAND (Chezy: EXTREME CACHING for realtime speed): a jam
    # revisits phrases — HOLD moves and vibe plateaus re-ask for byte-identical
    # phrase songs. The content-addressed render cache (A6) answers those in ~ms
    # instead of ~1s of m1, so slack GROWS as the set settles. phrase_energy reads
    # the wav alone (deterministic FFT), so a hit measures identically to a render.
    try:
        import render_cache as _rc
    except Exception:
        _rc = None
    class _Hit:                                   # a ready phrase wears the proc shape
        def wait(self, timeout=None):
            return 0

    class _StoreOnWait:                           # a miss stores itself once rendered
        def __init__(self, proc, pw, key):
            self.proc, self.pw, self.key = proc, pw, key

        def wait(self, timeout=None):
            rc = self.proc.wait(timeout)
            if _rc is not None and self.key and rc == 0:
                try:
                    if os.path.getsize(self.pw) > 44:
                        import shutil as _sh
                        wv, mp = _rc._wav_path(self.key), _rc._meta_path(self.key)
                        os.makedirs(_rc.CACHE, exist_ok=True)
                        _sh.copyfile(self.pw, wv)
                        json.dump({"key": self.key, "sha256": _rc._file_sha(wv),
                                   "song": os.path.basename(self.pw), "created": time.time(),
                                   "last_used": time.time(), "hits": 0,
                                   "size": os.path.getsize(wv)}, open(mp, "w"))
                        _rc._lru_gc()
                except Exception:
                    pass
            return rc


    class _ServeKill:                             # .proc.kill() == cancel (REPEAT LAW)
        def __init__(self, rail, rid):
            self.rail, self.rid = rail, rid

        def kill(self):
            self.rail.cancel(self.rid)

    class _ServeOnWait:                           # the rail's take on _StoreOnWait
        def __init__(self, rail, rid, pw, key):
            self.rail, self.rid, self.pw, self.key = rail, rid, pw, key
            self.proc = _ServeKill(rail, rid)

        def wait(self, timeout=None):
            rep = self.rail.wait_reply(self.rid, timeout)   # raises TimeoutExpired
            rc = 0 if rep.get("ok") == 1 else 1
            if _rc is not None and self.key and rc == 0:
                try:
                    if os.path.getsize(self.pw) > 44:
                        import shutil as _sh
                        wv, mp = _rc._wav_path(self.key), _rc._meta_path(self.key)
                        os.makedirs(_rc.CACHE, exist_ok=True)
                        _sh.copyfile(self.pw, wv)
                        json.dump({"key": self.key, "sha256": _rc._file_sha(wv),
                                   "song": os.path.basename(self.pw), "created": time.time(),
                                   "last_used": time.time(), "hits": 0,
                                   "size": os.path.getsize(wv)}, open(mp, "w"))
                        _rc._lru_gc()
                except Exception:
                    pass
            return rc

    def spawn_render(active, bright, tag, pc_mask=None, bars=None, evolve=None, swing=None, prog=0, touch=None):
        """Kick off a phrase render CONCURRENTLY (non-blocking Popen). The EarsTap
        writes SOTADAW_IPC/ears.jsonl; renders are one-at-a-time (each proc.wait()
        precedes the next spawn), so the shared ears file is read cleanly, no clobber.
        Cache hits skip the process entirely (the phrase is READY the moment it is
        asked for); misses register themselves on wait(). pc_mask = THE FOLLOW's
        harmony; bars = THE CONVERSATION LAW's per-phrase length (None = default);
        evolve = THE EVOLVE LAW's pocket variation index (None = verbatim)."""
        s = jam.build_phrase_song(base, active, bright, bpm, key, pc_mask=pc_mask,
                                  evolve=evolve, swing=swing, prog=prog, touch=touch)
        s["lengthBars"] = (bars or bars_per) + 1   # +1 tail bar (see render())
        s["master"] = PHRASE_WALL()
        os.makedirs(ipc, exist_ok=True)   # self-heal: the shared scratch dir can vanish
        pj = os.path.join(ipc, f"{tag}.json"); pw = os.path.join(ipc, f"{tag}.wav")
        json.dump(s, open(pj, "w"))
        ej = os.path.join(ipc, "ears.jsonl")
        if os.path.exists(ej):
            os.remove(ej)
        ckey = None
        if _rc is not None:
            try:
                ckey = _rc.cache_key(pj)
                wv, mp = _rc._wav_path(ckey), _rc._meta_path(ckey)
                if os.path.exists(wv) and os.path.exists(mp) \
                        and json.load(open(mp)).get("size") == os.path.getsize(wv):
                    import shutil as _sh
                    _sh.copyfile(wv, pw)          # INSTANT: the band played this before
                    meta = json.load(open(mp))
                    meta["last_used"] = time.time()
                    meta["hits"] = int(meta.get("hits", 0)) + 1
                    json.dump(meta, open(mp, "w"))
                    return _Hit(), pw, ej
            except Exception:
                ckey = None
        rid = rail.submit(pj, pw)             # the warm rail (fallback-total)
        if rid is not None:
            return _ServeOnWait(rail, rid, pw, ckey), pw, ej
        proc = subprocess.Popen([M1, "render", pj, pw], stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL,
                                env=dict(os.environ, SOTADAW_IPC=ipc))
        return _StoreOnWait(proc, pw, ckey), pw, ej

    t0 = endless_target(vibe, 0.0) if endless else jam.VIBES[vibe](0, phrases)
    n0 = int(round(t0 * len(available)))
    state = {"active": list(jam.FOUNDATION) + available[:n0], "available": available,
             "level": t0, "bright": 0.3 + 0.5 * t0, "phrase": 0, "follow": follow}

    # THE FOLLOW (B3): the human's notes fold in per phrase — pre-set noodling
    # (negative beats) already steers phrase 0's harmony and energy
    human = jam.human_context(read_human(human_path), now_beat=0.0) if human_path else None
    # THE CONVERSATION LAW: phrase length follows the human's activity — a busy
    # soloist gets SHORT answers (1 bar = twice the turn-taking), a quiet room
    # gets full statements (bars_per). Hysteresis: stay short one phrase after
    # the human quiets, then relax. Solo sets never shorten (contract intact).
    bar_s = 4.0 * 60.0 / bpm                     # seconds per bar
    def conv_bars(h, streak):
        if h is not None and float(h.get("density", 0)) > 0.45:
            return 1, 0
        streak += 1
        return (bars_per if streak >= 2 else 1), streak
    quiet_streak = 2                             # solo opens with full statements
    bars0, quiet_streak = conv_bars(human, quiet_streak) if human else (bars_per, 2)
    # STARTUP: render phrase 0 (blocking) — the latency before the band starts
    t_ph0 = time.monotonic()
    proc0, pw0, ej0 = spawn_render(state["active"], state["bright"], "ph0",
                                   pc_mask=human["pitch_classes"] if human else None,
                                   bars=bars0, swing=human["swing"] if human else None,
                                   prog=jam.journey_offset(0.0, key),
                                   touch=human["energy"] if human else None)
    proc0.wait()
    gen_seed = time.monotonic() - t_ph0          # the JIT margin's first real evidence
    smoothed = norm(jam.phrase_energy(pw0, ej0))
    arc = [round(smoothed, 3)]
    feed("phrase_ready", phrase=0, wav=pw0, start_beat=0.0,
         dur_s=round(bars0 * bar_s, 3), bars=bars0, tail_s=round(bar_s, 3))

    cont = {"version": 2, "bpm": bpm, "key": key,
            "lengthBars": (bars_per if endless else phrases * bars_per),
            "masterGainDb": 0.0, "master": [{"id": "fx_truepeak", "params": {"ceiling": -1.2}}],
            "buses": base.get("buses", []), "sections": [], "tracks": []}
    trackmap = {t["name"]: {"name": t["name"], "source": t["source"], "gainDb": t.get("gainDb", -6),
                            "notes": [], "fx": t.get("fx", []), "automation": []}
                for t in base["tracks"]}
    out = os.path.join(SONGS, f"{name}.json")

    def autosave(total_b, cur_log):
        """B6: the take EXISTS on disk after every phrase — a hard kill, a crash,
        a power cut: the material survives (tmp+replace = no torn reads)."""
        snap = dict(cont)
        snap["lengthBars"] = max(1, int(math.ceil(total_b / 4.0)))
        snap["tracks"] = [tm for tm in trackmap.values() if tm["notes"]]
        secs, sb = [], 0.0
        for i, lg in enumerate(cur_log):
            secs.append({"name": f"{lg.get('vibe', vibe)} {i+1}", "startBar": sb})
            sb += lg["bars"]
        snap["sections"] = secs
        try:
            json.dump(snap, open(out + ".tmp", "w"), indent=1)
            os.replace(out + ".tmp", out)
        except OSError:
            pass

    def place(active, bright, off_beats, pc_mask=None, evolve=None, swing=None,
              limit_beats=None, prog=0, touch=None):
        s = jam.build_phrase_song(base, active, bright, bpm, key, pc_mask=pc_mask,
                                  evolve=evolve, swing=swing, prog=prog, touch=touch)
        if limit_beats is not None:
            for t in s["tracks"]:
                t["notes"] = [n for n in t.get("notes", [])
                              if float(n["start"]) < limit_beats - 1e-6]
        off = float(off_beats)
        for t in s["tracks"]:
            tm = trackmap[t["name"]]
            for nn in t.get("notes", []):
                m = dict(nn); m["start"] = nn["start"] + off
                tm["notes"].append(m)
            if t.get("fx") and not tm["fx"]:
                tm["fx"] = t["fx"]

    place(state["active"], state["bright"], 0.0,
          pc_mask=human["pitch_classes"] if human else None,
          swing=human["swing"] if human else None,
          touch=human["energy"] if human else None)
    log, timing = [], []
    clock0 = time.monotonic()                    # the SET starts NOW
    measured = smoothed
    gen_ema = gen_peak = max(0.05, gen_seed)     # seeded by ph0's MEASURED gen — the
                                                 # box teaches the margin before phrase 1
    gen_cold = max(1.0, gen_seed)                # what a NOVEL (cache-miss) phrase costs
    last_pw = pw0                                # THE REPEAT LAW's fallback material
    last_place = (state["active"], state["bright"],
                  human["pitch_classes"] if human else None, None,
                  human["swing"] if human else None)
    # WALL-ACCUMULATED WINDOWS (conversation law): phrases vary in length, so the
    # clock walks beat0 -> beat0 + bars_p*4. A solo set never shortens, making
    # every window identical to the fixed-length scheduler (contract intact).
    total_beats = None if endless else phrases * bars_per * 4.0
    cur_vibe, arc_pe0 = vibe, 0.0                # B6: the arc restarts on a live switch
    beat0, bars_p, p = 0.0, bars0, 0
    while True:
        dur_p = bars_p * bar_s
        window_start = clock0 + beat0 * (60.0 / bpm)
        window_end = window_start + dur_p        # when THIS phrase's playback ends
        beats_after = beat0 + bars_p * 4.0
        # vibe progress in PHRASE-EQUIVALENTS of the DEFAULT length: a solo set
        # sees exactly p/(phrases-1) as before; adaptive sets move continuously
        pe = beat0 / (bars_per * 4.0)
        nv = read_vibe()                         # B6: the vibe box is LIVE mid-set
        if nv is not None and nv != cur_vibe:
            cur_vibe, arc_pe0 = nv, pe
            feed("vibe_change", phrase=p, vibe=cur_vibe)
        last = stop_req() if endless else (beats_after >= total_beats - 1e-6)
        target = (endless_target(cur_vibe, pe - arc_pe0) if endless
                  else jam.VIBES[cur_vibe](pe, phrases))
        # JIT DECISION (sub-phrase reactivity): wait for the LAST RESPONSIBLE
        # MOMENT of p's window before deciding p+1 — the freshest human playing
        # and the freshest ears shape the VERY NEXT phrase, not the one after.
        # Margin law: worst OBSERVED gen +25% +0.4s (never trust a hopeful EMA —
        # the -0.2s underrun the battery caught); when gens are window-sized the
        # decide falls back to the window START = exactly the pre-JIT scheduler.
        if not last:
            margin = max(gen_peak * 1.25, gen_ema * 1.6) + 0.4
            # NOVELTY LAW (round 3 — my own leg caught -0.55s): a human in the
            # room can flip the next phrase's LENGTH (conversation law) = novel
            # content = a cache MISS the warm margin never predicted. With a
            # human present the gate must budget a COLD render.
            if human_path:
                margin = max(margin, gen_cold * 1.25 + 0.4)
            # HEADROOM GATE (the battery caught -0.2s, then -0.4s under load):
            # JIT engages ONLY when the worst-case margin fits in HALF a window —
            # otherwise decide NOW at the window start, exactly the pre-JIT
            # scheduler, and the render gets the whole window. Reactivity is a
            # bonus on top of NEVER-UNDERRUN, never a trade against it.
            if margin <= 0.5 * dur_p:
                decide_at = window_end - margin
                # THE PUNCH-IN (scheduler half): the JIT wait is exactly when a
                # sudden burst would go unheard — so the wait IS a watcher. A
                # burst (density > 0.6) mid-window renders a SPACE answer in the
                # human's harmony+feel for the next INTERIOR bar line, budget-
                # gated by gen_cold; a miss is killed and the phrase plays on
                # (never a glitch). The punch lands in the KEPT TAKE via place
                # surgery; the feed's punch_ready is the player's crossfade seam.
                punched = False
                while True:
                    now = time.monotonic()
                    if now >= decide_at:
                        break
                    if endless and stop_req():   # STOP mid-wait: decide now, end clean
                        break
                    if human_path and not punched and bars_p >= 2:
                        hb = jam.human_context(read_human(human_path),
                                               now_beat=(now - clock0) * bpm / 60.0)
                        if hb is not None and float(hb["density"]) > 0.6:
                            nb = (now - clock0) * bpm / 60.0
                            line = math.floor(nb / 4.0) * 4.0 + 4.0
                            end_b = beat0 + bars_p * 4.0
                            t_line = clock0 + line * (60.0 / bpm)
                            if line < end_b - 1e-6 \
                                    and (t_line - now) >= gen_cold * 1.25 + 0.4:
                                pbars = int(round((end_b - line) / 4.0))
                                pa = [r for r in state["active"]
                                      if r not in jam.MELODIC]
                                pr, ppw, pej = spawn_render(
                                    pa, state["bright"], f"punch{p}",
                                    pc_mask=hb["pitch_classes"], bars=pbars,
                                    swing=hb["swing"], touch=hb["energy"],
                                    prog=jam.journey_offset(beat0 / (bars_per * 4.0), key))
                                try:
                                    pr.wait(timeout=max(
                                        0.05, (t_line - 0.08) - time.monotonic()))
                                    for tm in trackmap.values():
                                        tm["notes"] = [
                                            n for n in tm["notes"]
                                            if not (line - 1e-6 <= float(n["start"])
                                                    < end_b - 1e-6)]
                                    place(pa, state["bright"], line,
                                          pc_mask=hb["pitch_classes"],
                                          swing=hb["swing"], touch=hb["energy"],
                                          limit_beats=end_b - line)
                                    feed("punch_ready", phrase=p, wav=ppw,
                                         at_beat=line, bars=pbars,
                                         dur_s=round(pbars * bar_s, 3))
                                    punched = True
                                except subprocess.TimeoutExpired:
                                    try:
                                        pr.proc.kill()
                                    except Exception:
                                        pass
                    time.sleep(min(0.12, max(0.02, decide_at - time.monotonic())))
        # THE FOLLOW: reread the human's growing take up to NOW (wall-true beats)
        if human_path:
            human = jam.human_context(read_human(human_path),
                                      now_beat=(time.monotonic() - clock0) * bpm / 60.0)
        # LIVE FEEDBACK: decide the next phrase from what we HEARD this one sound like
        move, nxt_state = jam.brain(measured, target, dict(state, phrase=p), human=human)
        feed("decide", phrase=p, heard=round(measured, 3), target=round(target, 2),
             move=move, human=human or {}, vibe=cur_vibe,
             t_in_window=round(1.0 - max(0.0, window_end - time.monotonic()) / dur_p, 3))
        if endless and not last and stop_req():
            last = True                          # STOP landed mid-window: this phrase
                                                 # was the set's last — no next spawn
        ready = True; slack = dur_p; gen_s = 0.0
        if not last:
            bars_next, quiet_streak = conv_bars(human, quiet_streak)
            if total_beats is not None:          # endless sets have no remainder cap
                bars_next = int(min(bars_next, max(1.0, (total_beats - beats_after) / 4.0)))
            ev_next = p + 1 if move == "EVOLVE" else None   # the pocket breathes
            # NEVER RISK THE GROOVE FOR AN ORNAMENT: an EVOLVE variation is novel
            # content = a certain cache miss. If the remaining window cannot
            # afford a COLD render, the fill WAITS for a phrase with headroom.
            if ev_next is not None \
                    and (window_end - time.monotonic()) < gen_cold * 1.25 + 0.4:
                ev_next = None
                feed("evolve_deferred", phrase=p + 1)
            gen0 = time.monotonic()
            prog_next = jam.journey_offset(beats_after / (bars_per * 4.0), key)
            proc, pw, ej = spawn_render(nxt_state["active"], nxt_state["bright"], f"ph{p+1}",
                                        pc_mask=human["pitch_classes"] if human else None,
                                        bars=bars_next, evolve=ev_next,
                                        swing=human["swing"] if human else None,
                                        prog=prog_next,
                                        touch=human["energy"] if human else None)
            # THE REPEAT LAW (the seat's own spec, now machinery): the render
            # races the deadline; if it is NOT ready in time the band REPEATS
            # the last phrase — silence is worse than repetition. Slack is
            # therefore >= the reserve BY CONSTRUCTION: the underrun class dies.
            repeated = False
            try:
                proc.wait(timeout=max(0.05, (window_end - 0.12) - time.monotonic()))
            except subprocess.TimeoutExpired:
                repeated = True
                try:
                    proc.proc.kill()             # _Hit never times out; only real renders
                except Exception:
                    pass
            gen_end = time.monotonic()
            gen_s = gen_end - gen0
            if not repeated:
                gen_ema = 0.6 * gen_ema + 0.4 * gen_s   # the JIT margin learns the box
                gen_peak = max(gen_peak, gen_s)
                if gen_s > 0.3:                  # a REAL render: the cold estimate learns
                    gen_cold = max(gen_cold, gen_s)
            else:                                # a timed-out render IS cold evidence
                gen_cold = max(gen_cold, gen_s)
            slack = window_end - gen_end         # >0 == ready before p ends == NO UNDERRUN
            ready = slack > 0
            if repeated:
                pw = last_pw                     # the band plays the last phrase again
                la, lb, lpc, lev, lsw = last_place
                place(la, lb, beats_after, pc_mask=lpc, evolve=lev, swing=lsw)  # repeat keeps its touch-free mirror
                feed("phrase_ready", phrase=p + 1, wav=pw,
                     start_beat=beats_after, dur_s=round(bars_next * bar_s, 3),
                     bars=bars_next, slack_s=round(slack, 2), repeat=True,
                     tail_s=round(bar_s, 3))
                # state does NOT advance: the move re-decides next window with
                # fresher ears (the brain sees the same measured energy again)
            else:
                raw = norm(jam.phrase_energy(pw, ej))
                measured = 0.5 * measured + 0.5 * raw
                arc.append(round(measured, 3))
                place(nxt_state["active"], nxt_state["bright"], beats_after,
                      pc_mask=human["pitch_classes"] if human else None, evolve=ev_next,
                      swing=human["swing"] if human else None, prog=prog_next,
                      touch=human["energy"] if human else None)
                last_pw = pw
                last_place = (nxt_state["active"], nxt_state["bright"],
                              human["pitch_classes"] if human else None, ev_next,
                              human["swing"] if human else None)
                state = nxt_state
                feed("phrase_ready", phrase=p + 1, wav=pw,
                     start_beat=beats_after, dur_s=round(bars_next * bar_s, 3),
                     bars=bars_next, slack_s=round(slack, 2),
                     tail_s=round(bar_s, 3))
        log.append({"phrase": p, "target": round(target, 2),
                    "measured": round(arc[min(p, len(arc) - 1)], 3),
                    "move": move, "bars": bars_p, "vibe": cur_vibe})
        timing.append({"phrase": p, "gen_s": round(gen_s, 2), "slack_s": round(slack, 2),
                       "ready": ready})
        autosave(beats_after, log)               # B6: the take survives ANY exit
        # "play out" the rest of this phrase's real-time window — unless the room
        # said STOP: the player owns the audible tail, done should land NOW
        rem = window_end - time.monotonic()
        if rem > 0 and not (endless and stop_req()):
            time.sleep(rem)
        if last:
            break
        beat0, bars_p = beats_after, bars_next
        p += 1
    total_wall = time.monotonic() - clock0

    cont["tracks"] = [tm for tm in trackmap.values() if tm["notes"]]
    sec_bar = 0.0
    for i, lg in enumerate(log):                 # sections follow the REAL phrase lengths
        cont["sections"].append({"name": f"{lg.get('vibe', vibe)} {i+1}", "startBar": sec_bar})
        sec_bar += lg["bars"]
    if endless:                                  # the set was as long as the room wanted
        cont["lengthBars"] = max(1, int(math.ceil(sec_bar)))
    json.dump(cont, open(out, "w"), indent=1)
    feed("done", song=out, total_wall=round(total_wall, 2), arc=arc)
    # rail truth: "off" = kill-switch/boot failure; "serve" = ARMED (misses would
    # ride it — whether any DID is cache weather, reported separately). The pulse
    # caught the old usage-based field red on a warm cache: zero misses -> rail
    # untouched -> "classic" — a state-dependent assert, not a law.
    rail_state = "off" if rail.dead else "serve"
    rail.stop()
    return {"song": out, "log": log, "timing": timing, "arc": arc, "total_wall": total_wall,
            "phrase_dur": dur, "phrases": len(log), "bpm": bpm, "key": key, "vibe": vibe,
            "rail": rail_state, "rail_misses": rail.submits}, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("genre"); ap.add_argument("vibe", choices=list(jam.VIBES))
    ap.add_argument("--phrases", type=int, default=5,
                    help="0 = ENDLESS: play until <ipc>/stop appears (B6)")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--bars", type=int, default=2); ap.add_argument("--name", default="_jamlive")
    ap.add_argument("--human", default=None,
                    help="B3 THE FOLLOW: a growing notes file (json array / song dict / "
                         "jsonl), beats SET-relative — the band plays WITH whoever writes it")
    ap.add_argument("--follow", type=float, default=0.5,
                    help="0 = the vibe arc alone, 1 = pure follow of the human's energy")
    ap.add_argument("--bpm", type=float, default=None,
                    help="override the genre DNA's tempo (jam over YOUR song's world)")
    ap.add_argument("--key", default=None,
                    help="override the DNA key ('C minor'): harmonic rungs transpose")
    a = ap.parse_args()
    res, err = jam_live(a.genre, a.vibe, a.phrases, a.seed, a.name, a.bars,
                        human_path=a.human, follow=a.follow, bpm=a.bpm, key=a.key)
    if res is None:
        sys.exit(f"jam_live failed: {err}")
    print(f"[jam-live] {a.genre} on '{a.vibe}' — REALTIME, {res['phrases']} phrases x "
          f"{res['phrase_dur']:.1f}s @ {res['bpm']}bpm {res['key']}")
    for lg, tm in zip(res["log"], res["timing"]):
        rt = f"gen {tm['gen_s']:.1f}s, slack {tm['slack_s']:+.1f}s {'OK' if tm['ready'] else 'UNDERRUN'}"
        print(f"  ph{lg['phrase']}: heard {lg['measured']:.2f} vs vibe {lg['target']:.2f} -> "
              f"{lg['move']:<16} [{rt}]")
    ideal = res["phrases"] * res["phrase_dur"]
    print(f"[jam-live] total wall {res['total_wall']:.1f}s vs {ideal:.1f}s pure playback "
          f"(gen overlapped playback) -> {res['song']}")


if __name__ == "__main__":
    main()
