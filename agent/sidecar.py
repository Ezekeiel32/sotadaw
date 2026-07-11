#!/usr/bin/env python3
"""SOTA DAW agent sidecar — bridges the UI to the producer agent via file IPC.

Protocol (agent/ipc/):
  UI writes  request.json   {"id": n, "type": "prompt", "text": ..., "song": name}
                            {"id": n, "type": "accept"|"reject", "song": name}
  We append  events.jsonl   {"id": n, "kind": "status|activity|proposal|analysis|error|done", ...}
  Proposals land as songs/_prop_<song>.json (+ rendered songs/_prop_<song>.wav) — the base song is
  never touched until accept. Accept = copy over base + git commit + re-render + analyze.

--mock: apply canned transforms instead of calling the LLM (zero-token loop testing).
"""
import hashlib, json, os, queue, re, shutil, signal, subprocess, sys, threading, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IPC = os.environ.get("SOTADAW_IPC") or os.path.join(ROOT, "agent", "ipc")  # override = isolated test instance (own lockfile/events/request)
SONGS = os.path.join(ROOT, "songs")
M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")
VENV_PY = os.path.join(ROOT, ".venv", "bin", "python")
MOCK = "--mock" in sys.argv
os.makedirs(IPC, exist_ok=True)
# THE WARM RAIL (b17cd1a): the resident daemon is the perfect host for `m1 serve` —
# every proposal render skips process spawn + engine init. Safe to default ON here:
# determinism-sealed (served == spawned byte-exact; gold nulls CLEAN), the client
# falls back to classic m1 on ANY trouble, and _cached_render falls back AGAIN
# around that. Kill-switch: SOTADAW_RENDER_SERVE=0. Lifecycle: Python pipes are
# CLOEXEC (PEP 446), so the sidecar's self-exec refresh closes the server's stdin
# -> serve's getline sees EOF -> the resident m1 exits clean (no orphan per exec).
os.environ.setdefault("SOTADAW_RENDER_SERVE", "1")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import surgical            # THE SCALPEL kernel: scope law + playhead NOW-context
import verbs               # THE VERB BUS registry: producer verbs on the zero-token lane
import parse_lane          # THE PARSE LANE (T1): typed asks -> kernels, zero tokens
import session_memory      # THE FACT STORE (T2): verdict-confirmed session memory
import chronicle           # THE CHRONICLE: per-project conversation memory + chat history
import ghost_stream        # TOKEN-RESOLUTION GHOSTS: notes from in-flight tool JSON (pass 5)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import psr_floors as _psr_floors   # THE PSR FLOOR single source: the universal crest brake

# W12 BYOK: in-app keys (agent/.byok, local-only, gitignored) feed the agents
# via env — no terminal needed on a fresh machine. ONE box, BOTH dialects:
# each line routes by prefix — sk-ant-* -> claude rail, sk-or-* -> OpenRouter
# rail (grok etc.). Paste one key or both (one per line) in the same dialog.
_byok = os.path.join(ROOT, "agent", ".byok")
if os.path.exists(_byok):
    for _k in open(_byok).read().split():
        if _k.startswith("sk-or-"):
            os.environ.setdefault("OPENROUTER_API_KEY", _k)
        elif _k:
            os.environ.setdefault("ANTHROPIC_API_KEY", _k)
EVENTS = os.path.join(IPC, "events.jsonl")
last_feedback = {}
last_reject = {}     # song -> {"t", "notes", "why"}: honest reject context, why VERBATIM
last_curation = {}   # song -> {"t", "held"}: hunk-dropped notes — do-not-readd law
last_verdict_t = {}  # song -> t of the last consumed accept: a double-click inside
                     # the round-trip window is BENIGN, never an error (live-user x4)

# FEEDBACK STATE SURVIVES RESTARTS: these dicts are taste the user just spent —
# a sidecar restart (crash/dev cycle) must not amnesia them. The read-time
# windows (600s/1800s in feedback_context_block) keep stale loads inert.
FEEDBACK_STATE = os.path.join(IPC, "feedback_state.json")

def save_feedback_state():
    try:
        # THE WHOLE MEMO FAMILY survives execv (2026-07-11: his 18:39 accept
        # row landed genre-less, surgical-less, prompt-less — the 17:30 refresh
        # wiped every ask-context memo between ask and verdict; last_genres
        # alone was not enough, the telemetry row proved it live)
        json.dump({"last_reject": last_reject, "last_curation": last_curation,
                   "last_genres": last_genres, "last_prompts": last_prompts,
                   "last_meta": last_meta},
                  open(FEEDBACK_STATE, "w"))
    except Exception:
        pass                                   # persistence must never kill a verdict

def load_feedback_state():
    try:
        d = json.load(open(FEEDBACK_STATE))
        last_reject.update(d.get("last_reject") or {})
        last_curation.update(d.get("last_curation") or {})
        last_genres.update(d.get("last_genres") or {})
        last_prompts.update(d.get("last_prompts") or {})
        last_meta.update(d.get("last_meta") or {})
    except Exception:
        pass

# load_feedback_state() is called AFTER the memo-dict declarations (~line 2620)
# — calling it here NameError'd on last_genres/last_prompts/last_meta (declared
# later), was silently eaten by the except, and the boot-load never happened.

def feedback_context_block(song_name, revise, now=None):
    """PURE (battery-proof): the reject/curation context for the next prompt.
    Reject context rides ONCE (popped); the curation law rides 30 min — the
    re-add risk outlives a single prompt."""
    now = now or time.time()
    out = ""
    lr = last_reject.get(song_name)
    if lr and not revise and now - lr["t"] < 600:
        last_reject.pop(song_name, None)
        why = str(lr.get("why") or "")
        why_line = (f" Their reason, VERBATIM: \"{why}\" — that is the standing complaint; fix THAT."
                    if why else "")
        out += (f"\nCONTEXT: the user REJECTED a proposal {max(1, int((now - lr['t']) / 60))} min ago "
                f"(it had {lr['notes']} notes; archived under songs/.rejected/).{why_line} If the message "
                "above reads like a reaction (\"horrible\", \"nah\", \"too much\"), it refers to THAT "
                "rejected take — the CURRENT song is the pre-proposal state; do NOT diagnose its "
                "emptiness as the thing being reviewed.\n")
    lc = last_curation.get(song_name)
    if lc and now - lc["t"] < 1800 and lc.get("held"):
        out += ("\nCURATION LAW: on the last accepted take the user HELD BACK these notes (deleted "
                "on purpose): " + "; ".join(lc["held"][:24]) + ". Do NOT re-add these exact notes — "
                "their absence is intentional taste.\n")
    return out

_EMIT_CTX = threading.local()   # per-thread current song (main lane + verdict lane)


def emit(req_id, kind, **kw):
    # CROSS-RUN SCOPING (2026-07-11): EVERY event names its song, so the UI can
    # drop foreign-run and injected events wholesale. A raw '{"kind":"accepted"}'
    # appended to the live bus by a parallel rig tore down Chezy's pending take
    # and blanked his streaming canvas (its raw 'done' fired the mirage path).
    if "song" not in kw:
        s = getattr(_EMIT_CTX, "song", "")
        if s:
            kw["song"] = s
    with open(EVENTS, "a") as f:
        f.write(json.dumps({"id": req_id, "kind": kind, "t": round(time.time(), 1), **kw}) + "\n")

def run(cmd, timeout=900):
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=ROOT)
    return p.returncode, p.stdout, p.stderr

def voice_ctx_block(text):
    """W101 (pure): the VOICE ASK router — asks that want singing get the
    vocal-topline journey injected deterministically (start_session only
    sees genre words; 'with vocals' never reaches skill tags). Returns ''
    when the ask isn't vocal.

    W129 (2026-07-11, the viral-pop instrumental): asks naming a VOCAL-LED
    genre with no explicit sing-word get a one-line NUDGE, not the full
    journey — that run fetched vocal-topline and still shipped an
    instrumental; a record in these genres usually carries a voice. The
    choice stays the agent's ('instrumental' in the ask silences it)."""
    t = str(text or "")
    if re.search(r"\b(vocal|vocals|sing|sings|singing|sung|voice|topline|"
                 r"lyric|lyrics|acapella|hum)\b", t, re.I):
        return ("\nVOICE ASK: this request wants SINGING. "
                "get_skill(\"vocal-topline\") for the workflow. THE VOICE IS "
                "THE LEVER (measured 2026-07-11: +0.05-0.09 insiderness vs no "
                "vocal, every genre — the single biggest realism move). WORDS "
                "FIRST because a real song wants real lyrics (words vs a "
                "wordless hum is a genre-dependent wash — psybient favored "
                "words, pop favored hum, both within single-seed noise): write "
                "lyrics[] one word per melody note then sing_lyrics; "
                "hum_topline(song, track=\"lead\") is the instant wordless "
                "fallback. Attribution: 'Gahata Meiji from LUNAI Project' "
                "rides every sung deliverable.\n")
    if (re.search(r"\b(pop|kpop|jpop|rnb|r&b|soul|gospel|motown|doo.?wop|"
                  r"citypop|hyperpop|ballad|anthem|anthemic)\b", t, re.I)
            and not re.search(r"\binstrumental\b", t, re.I)):
        return ("\nVOICE NUDGE: this genre is usually VOCAL-LED. A topline "
                "sells the record (measured: a voice adds +0.05-0.09 "
                "insiderness on every genre) — write lyrics[] one word per "
                "note + sing_lyrics (real words), or zero-cost "
                "hum_topline(song, track=\"lead\"); skip only if "
                "instrumental is the deliberate call (say so in your reply).\n")
    return ""


def resolve_take_genre(prop, song=None):
    """THE GENRE TRUTH for the quality rails (worldclass ledger 2026-07-12:
    the loudness pass was genre-blind on the prompt/verb/spectral/a2m lanes —
    it read only _loop.genre, so most recovered songs lifted toward the -12.5
    default with no crest/breath floors). Resolution: the take's own birth
    stamp (_loop.genre) > the song's meta/genre field (imports, arrange
    stamps) > last_genres ask-context (what the user ASKED for — set by
    MAKE/genre_pref/verdicts, persisted across restarts). None when nothing
    speaks — the pass then keeps its conservative default."""
    try:
        doc = json.load(open(os.path.join(SONGS, f"{prop}.json")))
    except Exception:
        doc = {}
    g = ((doc.get("_loop") or {}).get("genre")
         or (doc.get("meta") or {}).get("genre") or doc.get("genre"))
    if not g:
        for k in (song, re.sub(r"^_prop_", "", str(prop))):
            if k and last_genres.get(k):
                g = last_genres[k]
                break
    return g


def loudness_recovery(rid, prop, a, genre):
    """W116 THE UNIVERSAL LOUDNESS PASS (Chezy live, 2026-07-11: 'EVERY song
    from EVERY model for EVERY request'): the MAKE lane's recovery loop,
    extracted to run on EVERY proposal lane — agent-composed takes from any
    model shipped at whatever level they landed (-24.6 LUFS on the live
    take). Zero tokens, bounded at 2 extra renders, breath/PSR-guarded,
    fail-open. Lifts CLEAN takes only; re-walls after the last lift."""
    py = VENV_PY if os.path.exists(VENV_PY) else sys.executable
    if not (isinstance(a, dict) and a.get("clipped_samples") == 0):
        return a
    genre = re.sub(r"[^a-z0-9_]", "", str(genre or "").lower())
    lo, psr_floor, lra_floor = -12.5, None, 3.2
    if genre:
        try:
            q = ("import sys, json; sys.path.insert(0, r'" + os.path.join(ROOT, "tools") + "'); "
                 "from kg import KG; "
                 "w = KG().q(\"MATCH (g:Genre {name: '" + genre + "'})-[:TARGETS]->"
                 "(m:MixTarget) RETURN m.lufs_lo, m.psr_floor, m.lra_floor\"); "
                 "print(json.dumps(w[0] if w else []))")
            r = subprocess.run([py, "-c", q], capture_output=True, text=True, timeout=15)
            row = json.loads(r.stdout.strip() or "[]")
            if row and row[0] is not None:
                lo = float(row[0])
                psr_floor = row[1] if len(row) > 1 else None
                lra_floor = row[2] if len(row) > 2 and row[2] is not None else 3.2
            else:
                raise ValueError("no graph")
        except Exception:
            try:
                g = json.load(open(os.path.join(ROOT, "agent", "dna_cache.json")))["genres"][genre]
                lo = float(g["lufs_lo"])
                psr_floor = g.get("psr_floor")
                lra_floor = g.get("lra_floor", 3.2)
            except Exception:
                pass
    # UNIVERSAL CREST BRAKE (2026-07-11): the graph read above is direct, so the
    # 143 genres whose MixTarget carries no psr_floor came back None — and
    # recovery_step then SKIPS its crest budget guard, pushing them toward the
    # loudness target unbraked (acoustic/jazz/orchestral takes got squashed). The
    # pure seed resolves a published-practice family prior for every genre with
    # zero graph/subprocess cost; a real KG value already won above when present.
    if psr_floor is None and genre:
        try:
            psr_floor = _psr_floors.seed_floor(genre) or _psr_floors.DEFAULT_FLOOR
        except Exception:
            pass
    pushed = 0.0
    for _pass in range(3):
        # W116: max_push 24 — the old 8 stranded extreme-quiet agent takes
        # at -30; the PSR/breath guards are the real safety, not the cap
        delta, why = recovery_step(a, lo, psr_floor, pushed, max_push=24.0,
                                   lra_floor=lra_floor)
        if delta < 0.4:
            if why.startswith("PSR floor"):
                emit(rid, "activity", text=("loudness recovery stopped: " + why)[:200])
            break
        pj = os.path.join(SONGS, f"{prop}.json")
        doc = json.load(open(pj))
        trim = next((f for f in doc.get("master", [])
                     if f.get("id") == "fx_trim"), None)
        if trim is None:   # agent-composed masters may lack a trim: stage one
            doc.setdefault("master", []).insert(
                0, {"id": "fx_trim", "params": {"level": 0.0}})
            trim = doc["master"][0]
        trim.setdefault("params", {})["level"] = \
            round(float(trim["params"].get("level", 0.0)) + delta, 1)
        _awrite(pj, doc)
        pushed += delta
        lufs = float(a.get("lufs_integrated", 0.0))
        emit(rid, "activity",
             text=f"loudness recovery: {lufs:.1f} LUFS -> target {lo:.1f} (+{delta} dB trim; {why})")
        a = render_and_analyze(rid, prop, "proposal")
    if pushed:
        a = clip_wall(rid, prop, a)   # the lift's LAST render can clip — wall again
    # THE CREST REFUND (2026-07-12): the mirror organ. A take can be BORN
    # over-driven into the wall (the fixed +2 birth trim on an already-loud
    # genre) and ship below its crest floor while the lift loop never fires —
    # trap probe: LUFS -10.5 inside [-18,-9] with TRUE PSR 3.1 vs floor 5.0.
    # The PLR proxy above read 8.1 on that same take (quiet bars drag the
    # integrated average and hide the crush) — the refund consults the TRUE
    # PSR analyze2 already measures (tp - short_term_max, the E6 quantity).
    # It only works through a NONLINEAR wall (linear gain moves peaks and
    # loudness together): bare chains skip, fail-open. MEASURED: deep in
    # limiting a refunded dB returns ~0.23-0.34 dB PSR, so the loop iterates
    # (<=3 renders) re-deciding from the slope it just measured; a stalled
    # pass (<0.15 dB gained) means the wall is no longer the mechanism.
    if psr_floor is not None:
        try:
            refunded, slope, prev_psr, last_delta = 0.0, 0.5, None, 0.0
            for _pass in range(3):
                if not (isinstance(a, dict) and a.get("clipped_samples") == 0):
                    break
                pj = os.path.join(SONGS, f"{prop}.json")
                doc = json.load(open(pj))
                if not any(str(f.get("id", f.get("type", "")) or "").startswith(
                        ("fx_truepeak", "fx_brickwall")) for f in doc.get("master", [])):
                    break
                psr = a.get("psr")
                if psr is None:
                    break
                if prev_psr is not None:
                    gained = float(psr) - prev_psr
                    if gained < 0.15:
                        emit(rid, "activity", text=(
                            f"crest refund stalled: +{gained:.2f} dB PSR for "
                            f"-{last_delta} dB drive — the wall is not the mechanism")[:200])
                        break
                    slope = gained / last_delta
                delta, why = refund_step(psr, psr_floor, a.get("lufs_integrated"),
                                         lo, slope=slope,
                                         max_refund=min(4.0, 9.0 - refunded))
                if delta < 0.4:
                    if why.startswith("crest debt"):
                        emit(rid, "activity", text=("crest refund blocked: " + why)[:200])
                    break
                trim = next((f for f in doc.get("master", [])
                             if f.get("id") == "fx_trim"), None)
                if trim is None:
                    doc.setdefault("master", []).insert(
                        0, {"id": "fx_trim", "params": {"level": 0.0}})
                    trim = doc["master"][0]
                trim.setdefault("params", {})["level"] = \
                    round(float(trim["params"].get("level", 0.0)) - delta, 1)
                _awrite(pj, doc)
                emit(rid, "activity", text=why[:200])
                prev_psr, last_delta = float(psr), delta
                refunded += delta
                a = render_and_analyze(rid, prop, "proposal")
        except Exception:
            pass
    return a


def _awrite(path, doc, indent=1):
    """W122 THE ATOMIC WRITE (Chezy live, untitled_34): m1 caught a 685KB
    proposal MID-WRITE ("cannot parse") — every in-place json.dump is a
    torn read waiting for a concurrent renderer/UI watcher. tmp + os.replace
    = never torn (the stems_import 809c1d9 lesson, applied to every song
    writer)."""
    tmp = str(path) + ".w~"
    with open(tmp, "w") as f:
        json.dump(doc, f, indent=indent)
    os.replace(tmp, path)


def recovery_step(a, lo, psr_floor, pushed, max_push=8.0, lra_floor=None):
    """THE RECOVERY BRAIN (W8, pure): one loudness-lift decision -> (delta_db, why).
    delta 0.0 = stop. Lift toward the genre's lufs_lo floor, bounded by max_push
    total; NEVER spend crest the genre can't afford — PLR (dBTP − LUFS) is the
    proxy, and at the wall a +X trim costs ~X of it, so the lift is capped by
    the PLR budget above the genre's psr_floor (E12 physics). Below the wall
    both rise and the NEXT pass recovers the difference (the loop re-decides
    from fresh ears). Loud-but-flat is the squash no wall can undo.
    W41 THE BREATH GUARD: PSR guards crest, not macro-breathing — a lift that
    rides the wall compresses the loud sections and LRA falls (measured on the
    W40 verdict pass: gospel 4.2 -> 3.0 LU). When lra_floor is given and the
    CURRENT ears already read at/below it, stop lifting. Fail-open when the
    analysis carries no lra."""
    if not isinstance(a, dict) or a.get("clipped_samples", 1) != 0:
        return 0.0, "not clean"
    lufs = float(a.get("lufs_integrated", 0.0))
    delta = round(min(max_push - pushed, lo - lufs), 1)
    if delta < 0.4:
        return 0.0, "at target"
    if lra_floor is not None:
        try:
            lra = a.get("lra")
            # W116: the guard fires when the material is ALREADY AT THE
            # WALL (dBTP > -4: a lift there is pure gain-reduction =
            # squash). A flat-but-quiet take (dBTP -20) lifts as pure
            # gain — the old unconditional guard froze it at -38 LUFS.
            at_wall = float(a.get("true_peak_dbtp", 0.0)) > -4.0
            if (at_wall and lra is not None
                    and float(lra) <= float(lra_floor)):
                return 0.0, (f"LRA squash guard: {float(lra):.1f} LU at floor "
                             f"{float(lra_floor):.1f} — keeping the breath over loud")
        except (TypeError, ValueError):
            pass
    if psr_floor is not None:
        try:
            plr = float(a.get("true_peak_dbtp", 0.0)) - lufs
            budget = plr - float(psr_floor)
            if budget < 0.4:
                return 0.0, (f"PSR floor holds: PLR {plr:.1f} at floor "
                             f"{float(psr_floor):.1f} — staying punchy over loud")
            if delta > budget:
                return round(budget, 1), (f"lift capped by PSR floor (PLR "
                                          f"{plr:.1f}, floor {float(psr_floor):.1f})")
        except (TypeError, ValueError):
            pass
    return delta, "lift"


def refund_step(psr, psr_floor, lufs, lo, slope=0.5, max_refund=4.0):
    """THE CREST REFUND BRAIN (2026-07-12, pure): one drive-reduction decision
    -> (delta_db, why). Mirror of recovery_step: that brain stops a LIFT from
    spending crest, but a take born over-driven ships below its floor with no
    lift ever firing. MEASURED PHYSICS (trap/bossa probe): the two-stage wall
    pins output peaks regardless of drive, and deep in limiting each refunded
    drive dB returns only ~0.23-0.34 dB of true PSR while costing ~0.4-0.8 dB
    of LUFS — so the ask is debt/slope, the caller iterates with the SLOPE IT
    MEASURED last pass, and each pass is clamped by the loudness window (lufs
    stays >= lo) and max_refund. Debt with no headroom = the mix is too dense
    at birth — a composition problem the refund must not paper over."""
    try:
        psr, lufs, lo = float(psr), float(lufs), float(lo)
        floor = float(psr_floor)
    except (TypeError, ValueError):
        return 0.0, "no floor"
    debt = floor - psr
    if debt < 0.4:
        return 0.0, "punchy enough"
    slope = max(0.2, min(1.0, float(slope or 0.5)))
    delta = round(min(debt / slope, lufs - lo, max_refund), 1)
    if delta < 0.4:
        return 0.0, (f"crest debt {debt:.1f} dB but no loudness headroom "
                     f"(LUFS {lufs:.1f} at window floor {lo:.1f}) — mix too dense at birth")
    return delta, (f"crest refund: true PSR {psr:.1f} below floor {floor:.1f} — "
                   f"giving back {delta} dB of wall drive (slope {slope:.2f})")


def stage_wall(doc):
    """JSON-side release-wall law, render-free: fx_truepeak stands LAST
    (ceiling <= -1.2, legacy brickwall/limiter upgraded in place, missing wall
    appended, masterGainDb -> 0 since post-wall gain re-opens the headroom the
    wall just closed). Callable wherever a take must be playback-safe before
    any measurement — clip_wall's staging half and the stop-KEEPS lane share
    this exact law."""
    master = doc.setdefault("master", [])
    wall = next((f for f in master if f.get("id") == "fx_truepeak"), None)
    legacy = next((f for f in master
                   if f.get("id") == "fx_brickwall" or f.get("type") == "limiter"), None)
    if wall is not None:
        wall.setdefault("params", {})
        wall["params"]["ceiling"] = min(-1.2, float(wall["params"].get("ceiling", -1.2)))
        master.remove(wall)
        master.append(wall)                    # the wall stands LAST in the chain
    elif legacy is not None:
        legacy.clear()
        legacy.update({"id": "fx_truepeak", "params": {"ceiling": -1.2}})
        master.remove(legacy)
        master.append(legacy)
    else:
        master.append({"id": "fx_truepeak", "params": {"ceiling": -1.2}})
    if float(doc.get("masterGainDb", 0) or 0) != 0.0:
        doc["masterGainDb"] = 0.0
    return doc


def vocal_gap(doc):
    """THE UNFINISHED-VOICE FLAG (2026-07-11, untitled_38: 'REAL VOCALS AND
    LYRICS' — the revise removed the stale hum lane, then the stop landed
    3s before the re-sing; the accepted take had lyrics and NO voice, and
    nothing said so). lyrics staged but no sounding vocal lane = a take
    mid-vocal-surgery. Returns the honest one-liner, or None when the take
    is vocally whole (or carries no lyrics at all)."""
    ly = doc.get("lyrics")
    if not (isinstance(ly, list) and ly):
        return None
    for t in doc.get("tracks", []):
        if not isinstance(t, dict) or t.get("muted"):
            continue
        clips = [c for c in (t.get("audioClips") or []) if isinstance(c, dict)]
        if any("vocal" in os.path.basename(str(c.get("file", ""))).lower()
               for c in clips):
            return None
        nm = str(t.get("name", "")).lower()
        if nm.startswith(("vocal", "vox")) and (clips or t.get("notes")):
            return None
    return (f"{len(ly)} lyric word(s) are staged but NO vocal lane is "
            "sounding — ask to 'sing it' to finish the voice")


def adopt_voice_bindings(song, base_doc, adopted):
    """THE FOLLOWING VOICE SURVIVES ACCEPT (2026-07-11): a sung take's
    binding dir is prop-scoped (songs/_prop_<song>_vocals/) and follow.json
    points at _prop_ paths + a recorded argv naming the prop — after accept
    the re-sing rail (vocal_follow_tick globs dirs by name -> looks for the
    CONSUMED prop json) went silently dead for every accepted sung take,
    and dead bindings (vocal lane removed mid-swap before a stop) orphaned
    forever. Live bindings (their wav rides the accepted song) migrate to
    songs/<song>_vocals/ with paths + argv re-homed; dead ones are swept
    with their unreferenced prop-scoped wavs. Returns (migrated, swept)."""
    import glob as _glob
    prop_tok = f"_prop_{song}"
    pv = os.path.join(SONGS, f"{prop_tok}_vocals")
    migrated = swept = 0
    referenced = set()          # every audio path the accepted song rides
    for t in base_doc.get("tracks", []):
        if not isinstance(t, dict):
            continue
        for c in (t.get("audioClips") or []):
            isinstance(c, dict) and referenced.add(str(c.get("file", "")))
        for sl in (t.get("slots") or []):
            isinstance(sl, dict) and referenced.add(str(sl.get("audioFile", "")))
    if os.path.isdir(pv):
        try:
            binds = json.load(open(os.path.join(pv, "follow.json"))).get("bindings", [])
        except Exception:
            binds = []
        live = []
        for b in binds:
            if not isinstance(b, dict):
                continue
            old_out = str(b.get("out_wav", ""))
            new_out = adopted.get(old_out) or old_out.replace(prop_tok, song)
            if new_out in referenced and os.path.exists(os.path.join(ROOT, new_out)):
                b["out_wav"] = new_out
                sa = str(b.get("src_audio", ""))
                b["src_audio"] = adopted.get(sa) or sa.replace(prop_tok, song)
                if isinstance(b.get("argv"), list):
                    b["argv"] = [str(x).replace(prop_tok, song) for x in b["argv"]]
                live.append(b)
        if live:
            sv = os.path.join(SONGS, f"{song}_vocals")
            os.makedirs(sv, exist_ok=True)
            bp = os.path.join(sv, "follow.json")
            try:
                keep = json.load(open(bp)).get("bindings", [])
            except Exception:
                keep = []
            outs = {b.get("out_wav") for b in live}
            keep = [k for k in keep if isinstance(k, dict)
                    and k.get("out_wav") not in outs] + live
            json.dump({"bindings": keep}, open(bp, "w"), indent=1)
            migrated = len(live)
            mc = os.path.join(pv, "melody.json")
            if os.path.exists(mc) and not os.path.exists(os.path.join(sv, "melody.json")):
                shutil.move(mc, os.path.join(sv, "melody.json"))
        shutil.rmtree(pv, ignore_errors=True)
    for w in _glob.glob(os.path.join(SONGS, f"{prop_tok}_vocal*.wav")):
        rel = os.path.relpath(w, ROOT)
        if rel not in referenced:   # a still-referenced prop-named wav (a
            try:                    # failed clip adopt) is NEVER swept
                os.remove(w)
                swept += 1
            except OSError:
                pass
    return migrated, swept


def clip_wall(rid, prop, a):
    """THE CLIP WALL (ears-on-finalize, deterministic half): a proposal that CLIPS
    never ships untreated. Enforce the release-wall law on the PROP itself
    (stage_wall: fx_truepeak LAST, ceiling <= -1.2, legacy upgraded,
    masterGainDb -> 0) — then ONE re-render. Zero tokens, engine-twin of
    loudness recovery. Returns the final analysis (or the input untouched when
    the take is clean/unreadable).

    GROWN 2026-07-11 (Chezy: "EVERY SONG FROM EVERY MODEL, FOR EVERY REQUEST
    IS WORLD CLASS! AND FASTTTT!"): the same chokepoint now holds THE
    WORLD-CLASS FLOOR — every lane and every model inherits it, zero tokens,
    ~ms. Objective trap classes heal deterministically (one extra re-render);
    what can't be healed rides a "quality" event so the deck/telemetry/next
    prompt can say WHY. wall_lint keeps this total across lanes."""
    if isinstance(a, dict) and int(a.get("clipped_samples") or 0) > 0:
        pj = os.path.join(SONGS, f"{prop}.json")
        try:
            doc = json.load(open(pj))
        except Exception:
            doc = None
        if doc is not None:
            _awrite(pj, stage_wall(doc))
            emit(rid, "activity", text=f"CLIP WALL: take clipped ({a.get('clipped_samples')} samples, "
                 f"peak {a.get('peak_dbfs', '?')} dBFS) - release wall enforced + re-render")
            a = render_and_analyze(rid, prop, "proposal")
    return _worldclass_floor(rid, prop, a)


def _worldclass_floor(rid, prop, a):
    """THE WORLD-CLASS FLOOR leg: verdict on the FINAL take, deterministic
    heals + ONE re-render, then the quality event. Never raises; never makes
    a take worse (heals are objective trap classes only)."""
    try:
        sys.path.insert(0, os.path.join(ROOT, "tools"))
        import worldclass
        pj = os.path.join(SONGS, f"{prop}.json")
        doc = json.load(open(pj))
        v = worldclass.floor_verdict(doc, a)
        healed = []
        if any(h.get("heal") for h in v["hard"]):
            fixed, healed = worldclass.heal(doc, v)
            if healed:
                tmp = pj + ".tmp"
                _awrite(tmp, fixed)
                os.replace(tmp, pj)
                emit(rid, "activity", text="WORLD-CLASS FLOOR: "
                     + "; ".join(healed) + " - re-render")
                a = render_and_analyze(rid, prop, "proposal")
                v = worldclass.floor_verdict(fixed, a)
        standing = [h["why"] for h in v["hard"]]
        emit(rid, "quality", song=prop[len("_prop_"):] if prop.startswith("_prop_")
             else prop, world_class=v["pass"], healed=healed,
             hard=standing, soft=[s["why"] for s in v["soft"]])
        if standing:
            emit(rid, "activity", text="WORLD-CLASS FLOOR: standing - "
                 + " | ".join(standing[:3]))
    except Exception:
        pass
    return a

def _cached_render(req_id, song_json, out_wav):
    """A6 THE ECONOMY (docs/THE_PHYSICS.md): a content-addressed cache in front of
    the m1 render — an unchanged take (re-audition, CLIP-WALL re-render of an
    unchanged base) is served instantly instead of re-rendered. SOTADAW_RENDER_CACHE=0
    disables. FAIL-SAFE: any cache trouble falls straight through to a direct render,
    so the live daemon can never be worse than before."""
    if os.environ.get("SOTADAW_RENDER_CACHE") != "0":
        try:
            sys.path.insert(0, os.path.join(ROOT, "tools"))
            import render_cache
            res = render_cache.render_cached(song_json, out_wav, quiet=True)
            if not res.get("error") and os.path.exists(out_wav):
                if res.get("hit"):
                    emit(req_id, "activity",
                         text="[cache] unchanged take served instantly (no re-render)")
                return True
        except Exception:
            pass
    # THE RENDER PULSE (2026-07-11, run 13 live: a max-effort take went event-
    # silent for 7+ minutes post-compose — the deck looked wedged while m1
    # rendered). Poll + pulse instead of a blocking run.
    spool = out_wav + ".renderlog"
    with open(spool, "w") as sp:            # file spool: a chatty m1 (FX_DEBUG)
        p = subprocess.Popen([M1, "render", song_json, out_wav],
                             stdout=sp, stderr=subprocess.STDOUT, text=True)
        t0, next_hb = time.time(), 45.0
        while p.poll() is None:
            time.sleep(0.5)
            el = time.time() - t0
            if el >= next_hb:
                emit(req_id, "activity", slot="heartbeat",
                     text=f"[render] still rendering ({int(el // 60)}m{int(el % 60):02d}s)…")
                next_hb += 45.0
            if el > 300:
                p.kill()
                emit(req_id, "error", text="render failed: timeout (300s)")
                return False
    try:
        tail_out = open(spool).read()[-300:]
    except OSError:
        tail_out = ""
    finally:
        try:
            os.remove(spool)
        except OSError:
            pass
    if p.returncode != 0:
        emit(req_id, "error", text=f"render failed: {tail_out}")
        return False
    return True


_hear_gen = {}   # wav path -> render generation (I4: stale tensors never emit)

def _hear_async(req_id, wav, bpm, label, gen):
    """I4 (THE TEN): the perception tensor OFF the critical path. hear.py costs
    ~1-2s per render and was serialized before the proposal event — and MAKE
    renders up to 4x per take. A daemon thread computes it; the generation guard
    drops tensors a newer render of the same wav has superseded."""
    def go():
        try:
            py = VENV_PY if os.path.exists(VENV_PY) else "python3"
            rh, oh, _ = run([py, os.path.join(ROOT, "tools", "hear.py"),
                             wav, "--bpm", str(bpm)], timeout=120)
            if _hear_gen.get(wav) != gen:
                return               # superseded mid-listen: a newer render owns the ears
            if rh == 0 and oh.strip():
                open(os.path.join(IPC, "perception.txt"), "w").write(oh)
                emit(req_id, "perception", which=label,
                     tensor="\n".join(oh.strip().splitlines()[:17]))
        except Exception:
            pass
    threading.Thread(target=go, daemon=True).start()

def render_and_analyze(req_id, song_name, label):
    sj = os.path.join(SONGS, f"{song_name}.json")
    wav = os.path.join(SONGS, f"{song_name}.wav")
    _hear_gen[wav] = _hear_gen.get(wav, 0) + 1   # any in-flight listen is now stale
    doc = {}
    try:   # empty song (fresh NEW project): coach, don't scream "render failed"
        doc = json.load(open(sj))
        if not any(t.get("notes") or t.get("audioClips") for t in doc.get("tracks", [])):
            emit(req_id, "activity", text=f"{label}: song is empty - nothing to render yet. "
                 "Add notes, or pick a genre and hit MAKE.")
            return True
    except Exception:
        pass
    emit(req_id, "activity", slot="heartbeat",
         text=f"[render] {label}: {int(float(doc.get('lengthBars') or 0)) or '?'} bars -> wav…")
    if not _cached_render(req_id, sj, wav):
        return False
    emit(req_id, "activity", slot="heartbeat", text=f"[meters] {label}: measuring…")
    py = VENV_PY if os.path.exists(VENV_PY) else "python3"
    # W117 METERS NEVER KILL A TAKE (Chezy live, untitled_34): analyze2 on a
    # 180MB wav under full box load blew the 120s timeout and the RAW
    # TimeoutExpired killed the prompt handler — the take sat rendered on
    # disk while the deck said "no pending proposal". One retry at 420s,
    # then fail-OPEN: the proposal ships meterless (a note, not a corpse).
    try:
        rc, out, _ = run([py, os.path.join(ROOT, "tools", "analyze2.py"), wav],
                         timeout=180)
    except subprocess.TimeoutExpired:
        emit(req_id, "activity", text=f"{label}: meters slow under load — retrying")
        try:
            rc, out, _ = run([py, os.path.join(ROOT, "tools", "analyze2.py"), wav],
                             timeout=420)
        except subprocess.TimeoutExpired:
            emit(req_id, "activity",
                 text=f"{label}: meters timed out (box under heavy load) — "
                      "the take is INTACT and lands without meters")
            return True
    if rc == 0:
        try:
            a = json.loads(out)
            emit(req_id, "analysis", which=label,
                 peak=a["peak_dbfs"], clipped=a["clipped_samples"], lufs=a["lufs_integrated"])
            if song_name.startswith("_prop_"):   # I3: the verdict reuses this
                last_analysis[song_name[len("_prop_"):]] = {"t": time.time(), "a": a}
            # CC3-4 PERCEPTION-NATIVE: the sound tensor rides every render event —
            # the agent (and the chat) never reason deaf. Threaded (I4): the
            # proposal event no longer waits on the ears' ASCII.
            try:
                _hear_async(req_id, wav, float(doc.get("bpm", 120) or 120), label,
                            _hear_gen[wav])
            except Exception:
                pass
            return a
        except Exception:
            pass
    return True

# ---------------- THE SECOND WEDGE (SPEC v2.1 V19b): external DAW connectors ----------------
DAW_ALLOW = ("mcp__daw__start_session,mcp__daw__list_instruments,mcp__daw__list_kits,"
             "mcp__daw__get_skill,mcp__daw__get_song,mcp__daw__update_track,mcp__daw__update_song_meta,"
             "mcp__daw__add_track,mcp__daw__set_track_fx,mcp__daw__search_library,mcp__daw__write_lyrics,"
             "mcp__daw__write_song,mcp__daw__render_song,mcp__daw__analyze_wav,mcp__daw__master_report,mcp__daw__auto_master,"
             "mcp__daw__list_plugin_params,mcp__daw__set_track_param,mcp__daw__automate,mcp__daw__set_buses,"
             "mcp__daw__duplicate_bars,mcp__daw__clear_bars,"
             "mcp__daw__locate,mcp__daw__select_notes,mcp__daw__surgical_edit,"
             "mcp__daw__apply_groove,mcp__daw__extract_groove,mcp__daw__save_preset,mcp__daw__use_preset,"
             "mcp__daw__loop_variations,mcp__daw__generate_loop,"
             "mcp__daw__sing_lyrics,mcp__daw__set_clip_slot,mcp__daw__edit_section,"
             "mcp__daw__import_als,mcp__daw__import_dawproject,mcp__daw__import_flp,"
             "mcp__daw__import_song_audio,mcp__daw__import_midi,mcp__daw__export_dawproject,mcp__daw__export_als,mcp__daw__export_midi,"
             "mcp__daw__dj_blend,mcp__daw__dj_set,mcp__daw__chop_sample,"
             "mcp__daw__hear,mcp__daw__hum_topline,mcp__daw__make_track,mcp__daw__arrange_song,mcp__daw__scene_strips,mcp__daw__scene_bounce,mcp__daw__reaper_bridge,mcp__daw__vst_presets,mcp__daw__build_loop_machine,mcp__daw__import_rekordbox,mcp__daw__get_selection")

def _daw_allow():
    """Derive the allowlist from the LIVE tool catalog so it can NEVER drift from
    the tools that exist (the firing-53 lesson: allowlist drift = the same silent
    bug class as schema drift). The static DAW_ALLOW above is the fallback if the
    import fails. FOUND 2026-07-05 live: get_song_summary/get_song_region (the
    READ LAW) + chord_map/reharmonize/harmonize/remix_import/song_structure were
    all BLOCKED because this list was hand-maintained and went stale."""
    try:
        import importlib.util as _ilu
        _sp = _ilu.spec_from_file_location("_dm_allow", os.path.join(ROOT, "agent", "daw_mcp.py"))
        _m = _ilu.module_from_spec(_sp)
        _sp.loader.exec_module(_m)
        return ",".join("mcp__daw__" + t for t in _m.TOOLS)
    except Exception:
        return DAW_ALLOW

DAW_ALLOW = _daw_allow()

CANCEL_FLAG = os.path.join(IPC, "cancel")

def claude_bin():
    """Resolve the claude CLI wherever it lives. A desktop-launched app inherits
    a PATH without ~/.local/bin — Loop Lab then crashed with a bare
    FileNotFoundError('claude') while terminal launches worked. Resolve once,
    fall back to the known install spots."""
    w = shutil.which("claude")
    if w:
        return w
    for c in (os.path.expanduser("~/.local/bin/claude"), "/usr/local/bin/claude", "/usr/bin/claude"):
        if os.path.exists(c):
            return c
    return None


# THE DAW'S OWN ANTHROPIC ACCOUNT (Chezy 2026-07-10): the Acct button arms a login
# fully separate from the user's Claude Code account. Armed = credentials exist in
# the DAW's config home; then EVERY claude spawn rides CLAUDE_CONFIG_DIR there
# (proven: an empty config dir gives "Not logged in", no ~/.claude fallback).
# Unarmed = inherit the machine's default login exactly as before.
DAW_CLAUDE_HOME = os.path.expanduser("~/.config/sotadaw/claude_home")


def daw_claude_env(**extra):
    env = dict(os.environ, **extra)
    if os.path.exists(os.path.join(DAW_CLAUDE_HOME, ".credentials.json")):
        env["CLAUDE_CONFIG_DIR"] = DAW_CLAUDE_HOME
    return env


# ---------------- LOG UPLINK (Chezy: "I need you to be able to read the log") ----------------
# The sidecar itself mirrors this machine's DAW logs to the dev box every 20s —
# no separate daemon to install, no way to forget it: if the agent runs, the
# logs flow. Own-tailnet only; silent when the receiver is unreachable.
# Disable with SOTADAW_NO_UPLINK=1 (isolated test instances set it).
UPLINK = os.environ.get("SOTADAW_UPLINK", "")

def _uplink_loop():
    import socket, urllib.request
    host = socket.gethostname().split(".")[0]
    names = ("events.jsonl", "app.log", "app_crash.log", "sidecar_crash.log")
    while True:
        for name in names:
            path = os.path.join(IPC, name)
            try:
                if os.path.exists(path):
                    with open(path, "rb") as f:
                        f.seek(max(0, os.path.getsize(path) - 120000))
                        data = f.read()
                    req = urllib.request.Request(UPLINK + "/live_" + host + "_" + name,
                                                 data=data, method="PUT")
                    urllib.request.urlopen(req, timeout=3).read()
            except Exception:
                pass
        time.sleep(20)

# ---------------- THE ACTION WIRE (agent-mode action stream) ----------------
# Every tool call the agent makes becomes a FIRST-CLASS structured event the
# instant its tool_use block streams in: family + human summary + target track.
# The UI renders it as a DAW component (family-glyph chip in the transcript) and
# pulses the agent-mode rails (fx family -> LEFT rail, master/render/ears ->
# RIGHT rail). The legacy "activity" line still rides right behind it (the
# wire/latency tools and older UIs read it); a UI that has seen one "action"
# suppresses the redundant bare pill.
ACTION_FAMILY = {
    "write_song": "song", "update_song_meta": "song", "add_track": "track",
    "update_track": "track", "set_track_param": "track", "duplicate_bars": "song",
    "clear_bars": "song", "arrange_song": "song",
    "set_track_fx": "fx", "set_buses": "master", "automate": "fx",
    "list_plugin_params": "fx", "use_as_fx": "fx",
    "surgical_edit": "notes", "select_notes": "notes", "locate": "notes",
    "generate_loop": "notes", "loop_variations": "notes", "apply_groove": "notes",
    "extract_groove": "notes", "import_midi": "song", "export_midi": "render",
    "write_instrument": "sound", "rebuild_engine": "sound", "vst_presets": "sound",
    "search_library": "sound", "capture_state": "sound",
    "render_song": "render", "export_als": "render", "export_dawproject": "render",
    "analyze_wav": "ears", "hear": "ears", "listen_live": "ears",
    "write_lyrics": "vocal", "tune_vocal": "vocal", "sing": "vocal",
    "import_song_audio": "song", "import_als": "song", "import_dawproject": "song",
    "import_flp": "song", "reaper_bridge": "song", "import_rekordbox": "dj",
    "dj_blend": "dj", "dj_set": "dj", "dj_live": "dj",
    "jam": "jam", "jam_live": "jam", "build_loop_machine": "notes",
    "get_song": "read", "get_selection": "read", "get_skill": "read",
    "start_session": "read", "use_tool": "read",
    # card_lint L1: every receipt-filing tool carries a SPECIFIC family —
    # an anonymous "tool" chip on a mutation is the streaming law eroding.
    "add_topline": "vocal", "align_lyrics": "vocal", "sing_lyrics": "vocal",
    "hum_topline": "vocal", "vocal_truth": "vocal", "a2m_correct": "notes",
    "audio_to_midi": "notes", "midi_to_audio": "render",
    "auto_master": "master", "automix": "master", "finish": "master",
    "prescribe": "master",
    "chop_sample": "notes", "harmonize": "notes", "humanize": "notes",
    "intensify": "notes", "infill_region": "notes", "loop_infill": "notes",
    "transitions": "notes",
    "chords_from_audio": "ears", "match_reference": "ears",
    "color": "fx",
    "edit_clip": "track", "freeze_track": "track", "lock_track": "track",
    "edit_section": "song", "make_track": "song", "restyle": "song",
    "time_machine": "song",
    "keep_jam": "jam", "set_clip_slot": "jam",
    "use_preset": "sound",
}

def _action_v(v):
    """One value, card-compact."""
    if isinstance(v, bool):
        return "on" if v else "off"
    if isinstance(v, float):
        return f"{v:g}"
    if isinstance(v, list):
        return f"x{len(v)}"
    if isinstance(v, dict):
        return f"{{{len(v)}}}"
    s = str(v)
    return s if len(s) <= 30 else s[:27] + "..."

def action_meta(name, inp):
    """(tool/family/summary/track) for a tool_use block — pure, total, never throws.
    The summary is the card's one-liner: the MUSICAL point of the call, not a dump."""
    short = str(name).replace("mcp__daw__", "").replace("mcp__", "@")
    inp = inp if isinstance(inp, dict) else {}
    fam = ACTION_FAMILY.get(short, "tool")
    track = str(inp.get("track") or "")
    bits = []
    try:
        if short == "write_song":
            doc = inp.get("song") or {}
            if isinstance(doc, str):
                try:
                    doc = json.loads(doc)
                except Exception:
                    doc = {}
            n_tr = len(doc.get("tracks", []) or [])
            bits.append(f"the whole song — {n_tr} tracks, "
                        f"{_action_v(doc.get('lengthBars', '?'))} bars" if n_tr
                        else "the whole song")
        elif short == "update_track":
            for k in ("gainDb", "pan", "muted", "locked"):
                if k in inp:
                    bits.append(f"{k} {_action_v(inp[k])}")
            if "notes" in inp:
                bits.append(f"notes {_action_v(inp['notes'])}")
            if "sends" in inp:
                bits.append(f"sends {_action_v(inp['sends'])}")
        elif short == "set_track_fx":
            fx = inp.get("fx")
            if isinstance(fx, list):
                ids = [str((f or {}).get("id", "?")).replace("fx_", "")
                       for f in fx if isinstance(f, dict)][:5]
                bits.append(" + ".join(ids) if ids else "chain cleared")
            else:
                bits.append("chain")
        elif short == "set_buses":
            b = inp.get("buses")
            m = inp.get("master")
            if isinstance(m, list):
                ids = [str((f or {}).get("id", "?")).replace("fx_", "")
                       for f in m if isinstance(f, dict)][:5]
                bits.append("master: " + (" > ".join(ids) if ids else "cleared"))
            if isinstance(b, list):
                bits.append(f"buses x{len(b)}")
            if "masterGainDb" in inp:
                bits.append(f"masterGainDb {_action_v(inp['masterGainDb'])}")
        elif short == "automate":
            bits.append(str(inp.get("target", "?")))
            pts = inp.get("points")
            if isinstance(pts, list):
                bits.append(f"{len(pts)}-point motion")
        elif short == "surgical_edit":
            ops = inp.get("ops")
            if isinstance(ops, list):
                bits.append(" , ".join(str((o or {}).get("op", "?"))
                                       for o in ops if isinstance(o, dict))[:40])
            sel = inp.get("select") or {}
            if isinstance(sel, dict):
                for k in ("bars", "section", "pitch", "role"):
                    if sel.get(k) is not None:
                        bits.append(f"{k} {_action_v(sel[k])}")
                track = track or str(sel.get("tracks") or sel.get("track") or "")
            if inp.get("preview"):
                bits.append("(preview)")
        elif short in ("select_notes", "locate"):
            for k in ("query", "bars", "section", "tracks", "pitch"):
                if inp.get(k) is not None:
                    bits.append(f"{k} {_action_v(inp[k])}")
        elif short == "generate_loop":
            bits.append(str(inp.get("genre", "?")))
            if inp.get("bars"):
                bits.append(f"{_action_v(inp['bars'])} bars")
            if inp.get("seed") is not None:
                bits.append(f"seed {_action_v(inp['seed'])}")
        elif short == "write_instrument":
            bits.append(str(inp.get("name", "?")) + ".dsp")
        elif short == "vst_presets":
            bits.append(str(inp.get("action", inp.get("query", "browse"))))
            if inp.get("preset"):
                bits.append(_action_v(inp["preset"]))
        elif short in ("render_song", "analyze_wav", "hear"):
            bits.append(str(inp.get("name") or inp.get("wav") or "").split("/")[-1])
        elif short == "tune_vocal":
            bits.append(str(inp.get("style", "natural")))
            if inp.get("region"):
                bits.append(f"region {_action_v(inp['region'])}")
        elif short in ("jam", "jam_live"):
            bits.append(f"{inp.get('genre', '?')} on '{inp.get('vibe', '?')}'")
        else:
            for k, v in list(inp.items())[:3]:
                if k in ("song", "notes", "state") or isinstance(v, (dict, list)):
                    continue
                bits.append(f"{k} {_action_v(v)}")
    except Exception:
        pass
    summary = "  ".join(b for b in bits if b).strip()
    return {"tool": short, "family": fam, "summary": summary[:180], "track": track[:48]}

def emit_action(req_id, blk):
    """Fire the structured action event for one tool_use block (never throws)."""
    try:
        emit(req_id, "action", **action_meta(blk.get("name", "?"), blk.get("input")))
    except Exception:
        pass

def token_stream_on():
    """TOKEN STREAM (pass 5) kill-switch: --include-partial-messages + the
    live-typing/live-ghost handlers. SOTADAW_TOKEN_STREAM=0 restores the
    per-block stream exactly."""
    return os.environ.get("SOTADAW_TOKEN_STREAM", "1") != "0"

class StreamState:
    """Per-run token-stream state (pass 5), fed stream_event lines by BOTH
    pumps. Two organs:
    - LIVE TYPING: text_delta accumulates; throttled `activity_stream` events
      carry the full accumulated text (idempotent replace — the chat card
      GROWS instead of a new card per block).
    - TOKEN GHOSTS: input_json_delta accumulates per tool block; complete note
      objects are tolerantly extracted and merged into <prop>.ghost.json (the
      exact file the canvas already watches), so notes land roughly when the
      model CONCEIVES them, not when the tool executes. Preview-only by
      construction (ghost_stream laws). Stopped blocks stay in `pending` so
      their notes never flicker off before execution lands them in the file.
    - THE MIND IS VISIBLE: thinking_delta streams into the same live-typing
      card (tag "thinking"). At max effort a run opens with MINUTES of pure
      thinking — before this, that window was dead air and reads as 'not
      streaming' (Chezy, 2026-07-10). Two sub-lanes, seam-proven 2026-07-11:
      models that stream reasoning text get the sliding TAIL; fable-5 REDACTS
      ("thinking": "" + estimated_tokens only) and gets an honest climbing
      TOKEN PULSE instead. Prose outranks reasoning: once text streams this
      message, thinking goes quiet."""
    TEXT_EVERY, TEXT_MIN_CHARS, GHOST_EVERY = 0.4, 24, 0.4
    THINK_EVERY, THINK_MIN_CHARS, THINK_TAIL = 0.5, 48, 1600

    def __init__(self, req_id, tag, song):
        self.req_id, self.tag, self.song = req_id, tag, song
        self.ts = ghost_stream.ToolStream()
        self.pending = []
        self.text = {}
        self.t_text = 0.0
        self.sent_len = 0
        self.t_ghost = 0.0
        self.think = {}
        self.t_think = 0.0
        self.sent_think = 0        # text lane: chars shipped / pulse lane: tokens shipped
        self.think_tokens = 0      # redacted lane's cumulative estimate
        self.prop = f"_prop_{song}" if song else None

    def _emit_text(self, final=False):
        if not self.text:
            return
        i = max(self.text)
        body = self.text[i]
        now = time.time()
        if not final and (now - self.t_text < self.TEXT_EVERY
                          or len(body) - self.sent_len < self.TEXT_MIN_CHARS):
            return
        if final and len(body) <= self.sent_len:
            return
        self.t_text, self.sent_len = now, len(body)
        emit(self.req_id, "activity_stream", tag=self.tag, text=body[:16000])

    def _emit_think(self):
        if self.text:
            return                      # prose outranks reasoning on the live card
        now = time.time()
        if now - self.t_think < self.THINK_EVERY:
            return
        body = self.think[max(self.think)] if self.think else ""
        if body:                        # reasoning text streams: the tail slides
            if len(body) - self.sent_think < self.THINK_MIN_CHARS:
                return
            self.sent_think = len(body)
            tail = body[-self.THINK_TAIL:]
            if len(body) > self.THINK_TAIL:
                tail = "..." + tail.lstrip()
        elif self.think_tokens >= self.sent_think + 40:   # redacted: the pulse
            self.sent_think = self.think_tokens
            tail = f"thinking... ~{self.think_tokens} tokens of reasoning"
        else:
            return
        self.t_think = now
        emit(self.req_id, "activity_stream", tag="thinking", text=tail)

    def _merge_ghost(self, final=False):
        if not self.prop:
            return
        now = time.time()
        if not final and now - self.t_ghost < self.GHOST_EVERY:
            return
        exts = list(self.pending)
        for i in list(self.ts.blocks):
            name, acc = self.ts.snapshot(i)
            if ghost_stream.tool_kind(name) and acc:
                exts.append(ghost_stream.extract_notes(name, acc))
        if not exts:
            return
        self.t_ghost = now
        pp = os.path.join(SONGS, f"{self.prop}.json")
        gp = os.path.join(SONGS, f"{self.prop}.ghost.json")
        try:
            if ghost_stream.merge_overlay(pp, gp, exts, prop_name=self.prop):
                emit(self.req_id, "proposal_progress", proposal=self.prop,
                     ghost=f"{self.prop}.ghost")
        except Exception:
            pass

    def on_stream_event(self, ev):
        e = ev.get("event") or {}
        et = e.get("type")
        if et == "message_start":
            self.ts.reset()
            self.text.clear()
            self.sent_len = 0
            self.think.clear()
            self.sent_think = 0
            self.think_tokens = 0
        elif et == "content_block_start":
            cb = e.get("content_block") or {}
            if cb.get("type") == "tool_use":
                self.ts.start(e.get("index"), cb.get("name"))
        elif et == "content_block_delta":
            d = e.get("delta") or {}
            if d.get("type") == "text_delta":
                i = e.get("index")
                self.text[i] = (self.text.get(i, "") + str(d.get("text") or ""))[:16000]
                self._emit_text()
            elif d.get("type") == "input_json_delta":
                self.ts.delta(e.get("index"), d.get("partial_json"))
                self._merge_ghost()
            elif d.get("type") == "thinking_delta":
                i = e.get("index")
                frag = str(d.get("thinking") or "")
                if frag:
                    self.think[i] = (self.think.get(i, "") + frag)[:200000]
                est = d.get("estimated_tokens")
                if isinstance(est, (int, float)) and est > self.think_tokens:
                    self.think_tokens = int(est)
                self._emit_think()
        elif et == "content_block_stop":
            i = e.get("index")
            if i in self.text:
                self._emit_text(final=True)
            name, acc = self.ts.snapshot(i)
            if ghost_stream.tool_kind(name) and acc:
                self.pending.append(ghost_stream.extract_notes(name, acc))
                self._merge_ghost(final=True)
            self.ts.stop(i)

UI_ALIVE = os.path.join(IPC, "ui_alive")


def ui_beat_age():
    try:
        return time.time() - os.path.getmtime(UI_ALIVE)
    except OSError:
        return None                 # no console ever beat here (CLIs, old UIs)


def console_was_live():
    a = ui_beat_age()
    return a is not None and a < 10.0


def console_gone(started_live):
    """RUN-LIFECYCLE LAW (Chezy 2026-07-11): a run belongs to the console that
    asked it. Console closed/crashed (beat stale) -> the run CANCELS: nothing
    keeps composing in the background, nothing lands into the next open.
    Enforced only when a console was alive at run start (CLI runs never beat)."""
    if not started_live:
        return False
    a = ui_beat_age()
    return a is not None and a > 8.0


def stream_events(p, req_id, tag="agent", song=None):
    """Pump a claude -p stream-json process: forwards events, emits a heartbeat during long
    silent generations (big tool calls LOOK frozen otherwise), honors the cancel flag file.
    song set = the agent's streamed prose also lands in the CHRONICLE as `note`
    rows (the run's live findings survive the process). Returns (canceled, last_result_event)."""
    q = queue.Queue()
    def reader():
        for line in p.stdout:
            q.put(line)
        q.put(None)
    threading.Thread(target=reader, daemon=True).start()
    st = StreamState(req_id, tag, song)   # pass 5: live typing + token ghosts
    silent, last_result = 0.0, None
    t_run, next_advice = time.time(), 15 * 60.0
    started_live = console_was_live()     # run-lifecycle law: bound to ITS console
    while True:
        gone = console_gone(started_live)
        if os.path.exists(CANCEL_FLAG) or gone:
            if os.path.exists(CANCEL_FLAG):
                os.remove(CANCEL_FLAG)
            p.kill()
            emit(req_id, "status",
                 text="console closed - run canceled (nothing runs behind a closed session)"
                      if gone else "canceled by user")
            return True, last_result
        try:
            line = q.get(timeout=0.5)
        except queue.Empty:
            silent += 0.5
            elapsed = time.time() - t_run
            if silent >= 25.0:
                mins = int(elapsed // 60)
                stamp = f" ({mins} min in)" if mins else ""
                # slot lets the UI COALESCE heartbeats into ONE updating chip
                emit(req_id, "activity", slot="heartbeat",
                     text=f"{tag}: …composing a large edit{stamp}, still streaming…")
                silent = -35.0   # next heartbeat only after a full further minute of silence
            if elapsed >= next_advice:
                next_advice += 10 * 60.0
                emit(req_id, "status", slot="advice",
                     text=(f"{int(elapsed // 60)} min on one edit — on songs this large, "
                           "Stop + a SCOPED ask (drag-select the target region/tracks "
                           "first) is usually much faster"))
            continue
        if line is None:
            return False, last_result
        silent = 0.0
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        et = ev.get("type")
        if et == "stream_event":
            st.on_stream_event(ev)        # token-level: chat types, ghosts land
        elif et == "assistant":
            for blk in (ev.get("message", {}).get("content") or []):
                if blk.get("type") == "tool_use":
                    emit_action(req_id, blk)   # the ACTION WIRE: structured, first
                    emit(req_id, "activity", text=f"{tag}: {blk['name'].replace('mcp__daw__','').replace('mcp__','@')}")
                elif blk.get("type") == "text" and blk.get("text", "").strip():
                    # full text -> the ChatPanel fold law collapses long ones with
                    # "show all"; truncating HERE broke that (cut mid-sentence at 200)
                    emit(req_id, "activity", text=f"{tag}: " + blk["text"].strip()[:4000])
                    if song:
                        chronicle.append(song, "note", blk["text"])
        elif et == "result":
            last_result = ev

def build_mcp_config():
    """Merge agent/mcp.json with enabled connectors from agent/connectors.json.
    Returns (config_path, extra_allowed_tools, connector_names). Security: only
    enabled connectors mount; only their 'allow' tools are granted (['*'] = server grant)."""
    base = json.load(open(os.path.join(ROOT, "agent", "mcp.json")))
    # MACHINE-PROOF: the committed mcp.json is a template — resolve the daw server
    # to THIS repo's path + THIS box's python at runtime (the Inspiron is user
    # 'hezy'; hardcoded /home/chezy paths silently killed all MCP tools there).
    daw_py = VENV_PY if os.path.exists(VENV_PY) else "python3"
    base.setdefault("mcpServers", {})["daw"] = {
        "command": daw_py,
        "args": [os.path.join(ROOT, "agent", "daw_mcp.py")]}
    extra_allow, names = [], []
    cpath = os.path.join(ROOT, "agent", "connectors.json")
    if os.path.exists(cpath):
        try:
            for c in json.load(open(cpath)).get("connectors", []):
                if not c.get("enabled") or not c.get("name") or not c.get("command"):
                    continue
                args = [os.path.join(ROOT, a)
                        if not os.path.isabs(a) and os.path.exists(os.path.join(ROOT, a)) else a
                        for a in c.get("args", [])]
                base["mcpServers"][c["name"]] = {"command": c["command"],
                                                 "args": args,
                                                 **({"env": c["env"]} if c.get("env") else {})}
                allow = c.get("allow", ["*"])
                if allow == ["*"]:
                    extra_allow.append(f"mcp__{c['name']}")
                else:
                    extra_allow.extend(f"mcp__{c['name']}__{t}" for t in allow)
                names.append(c["name"])
        except Exception as e:
            print(f"[sidecar] connectors.json ignored: {e!r}", flush=True)
    merged = os.path.join(IPC, "mcp_merged.json")
    _awrite(merged, base)
    return merged, extra_allow, names

# ---------------- model routing (V44): trivial ops go to the fast tier ----------------
TRIVIAL_RE = re.compile(
    r"^(please |can you |)((make|turn|set|bring) (the )?[\w ]{1,24}"
    r"( a (bit|little|touch)| slightly)? (quieter|louder|softer|down|up)( by [\d.]+ ?db)?"
    r"|set (the )?(bpm|tempo) to \d+"
    r"|(mute|unmute|solo|unsolo) (the )?[\w ]{1,24}"
    r"|pan (the )?[\w ]{1,24} (left|right|center|centre)"
    r"|rename [\w ]{1,40})[.!]? *$", re.IGNORECASE)

# single-scope edit verbs: one track / one knob / one section — sonnet-fast, still smart
EDIT_RE = re.compile(
    r"\b(louder|quieter|softer|brighter|darker|wider|narrower|drier|wetter|punchier"
    r"|mute|unmute|solo|pan|nudge|shorten|lengthen|tighten|loosen|thin|thicken"
    r"|add (some |a |more |)(reverb|delay|echo|saturation|drive|compression|eq|swing|air|space)"
    r"|(remove|less|reduce|cut) (the |some |)(reverb|delay|mud|harshness|noise|low end|highs?)"
    r"|change (the )?(key|tempo|bpm|swing|sound|preset|instrument)"
    r"|transpose|velocit|humanize|quantize|swap|rename|fix the [\w ]{1,20})\b", re.I)

BIG_RE = re.compile(r"\b((make|create|compose|write|build|produce|generate)\b.{0,24}"
                    r"\b(song|beat|track|loop|groove|melody|bassline|drop|intro|arrangement)"
                    r"|arrange|remix|rework|master|full song|whole (song|track|arrangement))\b", re.I)

def pick_model(text):
    """Latency ladder: haiku for one-knob ops, sonnet for single-scope edits,
    opus only for composition/arrangement-scale asks. Slow = the #1 complaint."""
    t = text.strip()
    if len(t) < 80 and TRIVIAL_RE.match(t):
        return "claude-haiku-4-5-20251001", "15"
    big = BIG_RE.search(t)
    if len(t) < 220 and EDIT_RE.search(t) and not big:
        return "claude-sonnet-5", "18"
    # COMPOSE LANE (firing 112): opus reads-the-world before writing (measured
    # first-material 230s); sonnet obeys plan-first and starts composing. BIG asks
    # ride sonnet; opus stays one phrase away for when depth beats speed.
    if big and not re.search(r"\b(think hard(er)?|ultrathink|masterpiece|best possible|use opus)\b", t, re.I):
        return "claude-sonnet-5", "30"
    return "claude-opus-4-8", "30"


def provider_kind(model):
    """Pure provider discriminator for explicit selector/environment ids."""
    value = str(model or "").strip()
    if not value:
        return "auto"
    if value.startswith("codex:"):
        return "codex"
    if value.startswith("claude"):
        return "claude"
    return "openrouter"


def routed_model_for(text, explicit_model="", mock=False):
    """The model string persisted in provenance/telemetry for this ask."""
    return "mock" if mock else (str(explicit_model or "").strip() or pick_model(text)[0])


def parse_lane_skip_reason(explicit_model="", revise=False, pending=False,
                           lane_enabled=True):
    """Why the deterministic AUTO lane must stand down, or empty when it may run."""
    if not lane_enabled:
        return "lane_off"
    if str(explicit_model or "").strip():
        return "model_override"
    if revise:
        return "revise"
    if pending:
        return "pending_proposal"
    return ""

# ---------------- mock agent ----------------
def mock_propose(req_id, text, song_name):
    base = json.load(open(os.path.join(SONGS, f"{song_name}.json")))
    t = text.lower()
    emit(req_id, "activity", text="mock-agent: reading song + skills")
    # the ACTION WIRE rides the mock lane too — zero-token E2E for cards + rails
    emit_action(req_id, {"name": "get_song", "input": {"name": song_name}})
    changed = []
    for tr in base["tracks"]:
        kind = tr.get("source", {}).get("kind", "faust")
        sid = (tr.get("source", {}).get("id") or tr.get("source", {}).get("kit") or "")
        pitched = kind == "vst3" or sid in ("piano", "epiano", "strings", "warmpad", "choir", "pluckbass")
        if ("dark" in t or "lower" in t) and pitched:
            for n in tr["notes"]:
                n["pitch"] = max(0, n["pitch"] - 2)
            changed.append(f"{tr['name']}: transposed -2")
            emit_action(req_id, {"name": "surgical_edit",
                                 "input": {"track": tr["name"],
                                           "ops": [{"op": "shift", "semitones": -2}]}})
        if "quiet" in t or "softer" in t:
            tr["gainDb"] = tr.get("gainDb", 0) - 3
            changed.append(f"{tr['name']}: gain -3dB")
            emit_action(req_id, {"name": "update_track",
                                 "input": {"track": tr["name"], "gainDb": tr["gainDb"]}})
    if any(w in t for w in ("sweep", "filter", "automate", "build", "rise", "motion", "sidechain", "space")):
        beats = float(base.get("lengthBars", 4)) * 4
        pitched = next((tr for tr in base["tracks"]
                        if tr.get("source", {}).get("kind") != "sample"
                        and "808" not in tr["name"].lower() and "kick" not in tr["name"].lower()),
                       base["tracks"][0])
        pitched.setdefault("fx", []).insert(0, {"id": "fx_filter", "params": {"res": 2.0}})
        pitched["automation"] = [{"target": "fx[0].cutoff",
                                  "points": [{"beat": 0, "v": 200}, {"beat": beats, "v": 9000}]}]
        base["buses"] = [{"id": "verb", "gainDb": 0, "fx": [{"id": "fx_reverb", "params": {"mix": 1.0, "size": 3.0}}]}]
        pitched["sends"] = [{"bus": "verb", "gainDb": -10}]
        changed.append(f"{pitched['name']}: fx_filter sweep 200->9k + verb send (MOCK motion)")
        emit_action(req_id, {"name": "set_track_fx",
                             "input": {"track": pitched["name"], "fx": pitched["fx"]}})
        emit_action(req_id, {"name": "automate",
                             "input": {"track": pitched["name"], "target": "fx[0].cutoff",
                                       "points": pitched["automation"][0]["points"]}})
        emit_action(req_id, {"name": "set_buses", "input": {"buses": base["buses"]}})
    if "hat" in t or not changed:
        for tr in base["tracks"]:
            if "hat" in tr["name"].lower():
                beats = float(base.get("lengthBars", 4)) * 4
                b = 0.75
                while b < beats:
                    tr["notes"].append({"start": b, "len": 0.1, "pitch": 42, "vel": 0.38})
                    b += 4.0
                changed.append(f"{tr['name']}: +ghost 16ths")
    emit(req_id, "activity", text="mock-agent: " + ("; ".join(changed) or "no-op"))
    chronicle.append(song_name, "agent", "; ".join(changed) or "no-op", route="mock")
    prop = f"_prop_{song_name}"
    _awrite(os.path.join(SONGS, f"{prop}.json"), base)
    return prop

# ---------------- selection = context (SPEC §2) ----------------
def song_digest(song_path):
    """Context-pack T1 (NIGGUN adopt #1): the song's structure inlined in the prompt
    so the agent can act WITHOUT a get_song roundtrip. Full note data stays tool-fetch."""
    try:
        song = json.load(open(song_path))
    except Exception:
        return ""
    L = [f"bpm {song.get('bpm')} | key {song.get('key', '?')} | {song.get('lengthBars', '?')} bars"
         + (f" | swing {song['swing']['amount']} ({song['swing'].get('grid', '16th')})"
            if isinstance(song.get('swing'), dict) else "")]
    if song.get("sections"):
        L.append("sections: " + " ".join(f"{x.get('name')}@{x.get('startBar')}"
                                         for x in song["sections"]))
    for t in song.get("tracks", []):
        src = t.get("source", {})
        sid = src.get("id") or src.get("kit") or src.get("plugin") or src.get("kind", "?")
        notes = t.get("notes", [])
        pr = (f" p{min(n['pitch'] for n in notes)}-{max(n['pitch'] for n in notes)}"
              if notes else "")
        fx = ",".join(f.get("id") or f.get("type", "?") for f in t.get("fx", []))
        sends = ",".join(f"{sn.get('bus')}{sn.get('gainDb', 0):+.0f}" for sn in t.get("sends", []))
        L.append(f"- {t.get('name')}: {sid} {t.get('gainDb', 0):+g}dB, {len(notes)}n{pr}"
                 + (f", fx[{fx}]" if fx else "") + (f", sends[{sends}]" if sends else "")
                 + (", MUTED" if t.get("muted") else ""))
    if song.get("buses"):
        L.append("buses: " + ", ".join(f"{b.get('id')}[{','.join(f.get('id') or f.get('type','?') for f in b.get('fx', []))}]"
                                       for b in song["buses"]))
    if song.get("master"):
        L.append("master: " + " -> ".join(f.get("id") or f.get("type", "?") for f in song["master"])
                 + f" | masterGainDb {song.get('masterGainDb', 0)}")
    txt = "\n".join(L)
    return txt[:2000]


_SEMMAPS = None
def semantic_maps_block(digest):
    """Inline intent->param-cluster maps for plugins PRESENT in the song (moat corpus,
    compiled by tools/kg_seed_semantic_maps.py). Keeps prompts lean: only matched plugins."""
    global _SEMMAPS
    if _SEMMAPS is None:
        try:
            _SEMMAPS = json.load(open(os.path.join(ROOT, "agent", "semantic_maps.json")))
        except Exception:
            _SEMMAPS = {}
    hits = [pl for pl in _SEMMAPS if pl.lower() in digest.lower()]
    if not hits:
        return ""
    L = ["\nSEMANTIC PARAM MAPS (intent -> set_track_param moves for plugins in this song):"]
    for pl in hits[:3]:
        m = _SEMMAPS[pl]
        for intent, moves in m["intents"].items():
            L.append(f"- {pl} {intent}: " + "; ".join(f"{p} {d}" + (f" ({n})" if n else "")
                                                      for p, d, n in moves))
        for g in m.get("gotchas", []):
            L.append(f"- {pl} GOTCHA: {g}")
    return "\n".join(L) + "\n"


def selection_block(context, song_path):
    """Render the UI's selection descriptors (precise ADDRESSES) into the context
    block the agent reads. The UI says WHERE the user is pointing; this enriches
    it from song.json: actual notes when few, stats when many, full fx/param
    state for tracks, per-track content maps for time ranges."""
    sels = (context or {}).get("selections") or []
    if not sels:
        return ""
    try:
        song = json.load(open(song_path))
    except Exception:
        return ""
    by_name = {t.get("name"): t for t in song.get("tracks", [])}
    rng = next((s for s in sels if s.get("type") == "timeRange"), None)
    a = rng.get("startBeat") if rng else None
    b = rng.get("endBeat") if rng else None
    in_rng = lambda n: a is None or (n.get("start", 0) < b and n.get("start", 0) + n.get("len", 0.25) > a)
    bars = lambda x, y: f"bars {int(x // 4) + 1}-{int((y - 1e-9) // 4) + 1}"
    lines = []
    for s in sels:
        k = s.get("type")
        if k == "notes":
            tr = by_name.get(s.get("track"))
            if not tr:
                continue
            notes = [tr.get("notes", [])[i] for i in s.get("indices", [])
                     if 0 <= i < len(tr.get("notes", []))]
            if not notes:
                continue
            notes.sort(key=lambda n: n.get("start", 0))
            lo = min(n["start"] for n in notes)
            hi = max(n["start"] + n.get("len", 0.25) for n in notes)
            ps = [n["pitch"] for n in notes]
            head = (f"- SELECTED NOTES on '{tr['name']}': {len(notes)} notes, beats {lo:g}-{hi:g} "
                    f"({bars(lo, hi)}), pitches {min(ps)}-{max(ps)}. Note indices {s.get('indices')} "
                    f"in this track's notes[] — edit THESE.")
            if len(notes) <= 48:
                head += ("\n  (start,len,pitch,vel): "
                         + " ".join(f"({n['start']:g},{n.get('len',0.25):g},{n['pitch']},{n.get('vel',0.8):g})"
                                    for n in notes))
            lines.append(head)
        elif k == "tracks":
            for nm in s.get("names", []):
                tr = by_name.get(nm)
                if not tr:
                    continue
                src = tr.get("source", {})
                fx = tr.get("fx", [])
                seg = (f"; {sum(1 for n in tr.get('notes', []) if in_rng(n))} of them inside the "
                       f"selected time range") if a is not None else ""
                lines.append(f"- SELECTED TRACK '{nm}': source {src.get('kind', '?')}:"
                             f"{src.get('id') or src.get('kit') or src.get('name', '')}, "
                             f"gain {tr.get('gainDb', 0)}dB, pan {tr.get('pan', 0)}, "
                             f"{len(tr.get('notes', []))} notes{seg}, fx "
                             f"[{', '.join(f.get('id') or f.get('type', '?') for f in fx) or 'none'}]"
                             + (f", sends {json.dumps(tr.get('sends'))}" if tr.get("sends") else ""))
                for f in fx:
                    if f.get("params"):
                        lines.append(f"    fx {f.get('id') or f.get('type')}: {json.dumps(f['params'])}")
        elif k == "timeRange":
            occ = [(t.get("name"), sum(1 for n in t.get("notes", []) if in_rng(n)))
                   for t in song.get("tracks", [])]
            occ = [f"{n}({c})" for n, c in occ if c]
            clips = [t.get("name") for t in song.get("tracks", [])
                     if any(c.get("startBeat", 0) < b and c.get("startBeat", 0)
                            + c.get("lengthBeats", 1e9) > a for c in t.get("audioClips", []))]
            lines.append(f"- SELECTED TIME RANGE: beats {a:g}-{b:g} ({bars(a, b)}). "
                         f"Notes here: {', '.join(occ) or 'none'}"
                         + (f". Audio clips here: {', '.join(clips)}" if clips else ""))
        elif k == "library":
            if s.get("section") == "GROOVES":
                try:
                    gj = json.load(open(os.path.join(ROOT, "library", "grooves.json")))
                except Exception:
                    gj = {}
                gr = gj.get(s.get("id"), {})
                lines.append(
                    f"- SELECTED GROOVE '{s.get('id')}' ({gr.get('prov', 'unknown origin')}): "
                    f"per-16th-slot timing offsets (beat fractions) {gr.get('off')} and velocity "
                    f"weights {gr.get('vel')} — the user points at a FEEL. Apply it with "
                    f"apply_groove(track=..., groove='{s.get('id')}') (times AND accents the notes); "
                    f"prefer it over any swing{{}} setting.")
            else:
                lines.append(f"- SELECTED LIBRARY ITEM: {s.get('section')}: '{s.get('id')}' — the user "
                             f"is pointing at this sound; prefer it when adding/replacing a layer.")
        elif k == "master":
            m = song.get("master", [])
            chain = ", ".join((f.get("id") or f.get("type", "?"))
                              + (f" {json.dumps(f.get('params'))}" if f.get("params") else "")
                              for f in m) or "empty"
            lines.append(
                f"- SELECTED: THE MASTER CHAIN — [{chain}], masterGainDb {song.get('masterGainDb', 0)}. "
                f"The user wants MASTERING moves here. LAWS: fx run in array order and masterGainDb is "
                f"applied AFTER the whole chain (keep it 0; stage inside the chain with fx_trim, zone "
                f"'level' NOT 'gain'); true-peak safety = fx_brickwall, ceiling -1.5..-2 dB on sub-heavy "
                f"material; loudness problems are fixed at the SOURCES (track gains/notes), never by "
                f"normalising output. THE LOOP: edit -> master_report (renders + measures + judges vs "
                f"the genre's KG MixTarget, hints per failure) -> fix the fix_first check -> repeat "
                f"until pass:true. hear (structure) when numbers pass but feel is in question. "
                f"Edit master[] via update_song_meta/write_song.")
        elif k == "fx":
            # the rack's pointed module: scope master|bus|track + chain index
            scope = s.get("scope", "track")
            idx = int(s.get("index", -1))
            if scope == "master":
                chain, where, how = song.get("master", []), "the MASTER chain", \
                    "edit master[] via update_song_meta (keep masterGainDb 0; stage with fx_trim zone 'level')"
            elif scope == "bus":
                bus = next((b for b in song.get("buses", []) if b.get("id") == s.get("owner")), {})
                chain, where, how = bus.get("fx", []), f"bus '{s.get('owner')}'", \
                    "rewrite the bus via set_buses (all buses at once — keep the others verbatim)"
            else:
                tr = by_name.get(s.get("owner")) or {}
                chain, where, how = tr.get("fx", []), f"track '{s.get('owner')}'", \
                    "edit via set_track_fx (the whole chain, in order) or set_track_param fx[i].<param>"
            if not (0 <= idx < len(chain)):
                continue
            f = chain[idx]
            fid = f.get("id") or f.get("type", "?")
            chain_str = " -> ".join(
                ("[" + (c.get("id") or c.get("type", "?")) + "]" if i == idx
                 else (c.get("id") or c.get("type", "?"))) + (" (bypassed)" if c.get("bypass") else "")
                for i, c in enumerate(chain))
            lines.append(
                f"- SELECTED FX: '{fid}' at index {idx} on {where} — chain: {chain_str}. "
                f"Params now: {json.dumps(f.get('params') or {})}"
                + (f", preset: {f['preset']}" if f.get("preset") else "")
                + (", BYPASSED" if f.get("bypass") else "")
                + f". The user is pointing at THIS effect; {how}. Faust params are real zone "
                f"units (fx_trim's zone is 'level', dB); vst3 params are natural display units "
                f"(list_plugin_params for the exact names). \"bypass\": true disables without "
                f"losing settings.")
        elif k == "slot":
            tr = by_name.get(s.get("track"))
            sc = int(s.get("scene", -1))
            sl = (tr or {}).get("slots", [])
            sl = sl[sc] if 0 <= sc < len(sl) else None
            if sl is None:
                continue
            what = (f"audio loop '{os.path.basename(sl.get('audioFile',''))}' offset {sl.get('offsetSec',0)}s"
                    + (f" warped from {sl.get('sourceBpm')}bpm" if sl.get("sourceBpm") else "")
                    ) if sl.get("audioFile") else f"{len(sl.get('notes', []))}-note pattern"
            lines.append(f"- SELECTED LAUNCHER SLOT: track '{s.get('track')}' scene {sc + 1}"
                         f" ('{sl.get('name', '')}'): {what}, {sl.get('lengthBeats', 16)} beats — "
                         f"edit THIS slot via set_clip_slot (or spin loop_variations from it).")
    if not lines:
        return ""
    return ("\nSELECTION CONTEXT — the user is POINTING at this in the UI:\n" + "\n".join(lines)
            + "\nLAW: operate ON the selection. Touching material outside it needs the user's "
            "explicit words. When the ask is ambiguous, the selection IS the subject.\n")


# DJ-LIVE R4 (E3's realtime half of P7): while a SET is sounding (fresh ears
# frames + the last-touched song owns a .setplan.json), the advisor SPEAKS —
# one coach line per tick, deduped per (kind, deck), 2s check throttle,
# SOTADAW_DJ_LIVE=0 kills the mouth. The kernel is tools/dj_live.advise (pure).
_djlive = {"next": 0.0, "said": set(), "plan": None, "song": None}

def dj_live_tick():
    if os.environ.get("SOTADAW_DJ_LIVE") == "0":
        return
    now = time.time()
    if now < _djlive["next"]:
        return
    _djlive["next"] = now + 2.0
    try:
        ep = os.path.join(IPC, "ears.jsonl")
        if not os.path.exists(ep) or now - os.path.getmtime(ep) > 3.0:
            return
        song = None                    # the last-touched song that IS a set
        for s in reversed(list(last_prompts.keys())):
            if os.path.exists(os.path.join(SONGS, f"{s}.setplan.json")):
                song = s
                break
        if song is None:
            return
        if _djlive["song"] != song:
            _djlive.update(song=song, said=set(),
                           plan=json.load(open(os.path.join(SONGS, f"{song}.setplan.json"))))
        with open(ep, "rb") as f:
            f.seek(0, 2)
            f.seek(max(0, f.tell() - 65536))
            tail = f.read().decode("utf-8", "replace").strip().splitlines()
        frames = []
        for ln in tail[-400:]:
            try:
                fr = json.loads(ln)
                if now - float(fr.get("t", 0)) <= 40.0:
                    frames.append(fr)
            except Exception:
                continue
        if not any(f.get("playing") for f in frames):
            return
        sys.path.insert(0, os.path.join(ROOT, "tools"))
        import dj_live
        for a in dj_live.advise(frames, _djlive["plan"]):
            key = (a["kind"], a["deck"])
            if key in _djlive["said"]:
                continue
            _djlive["said"].add(key)
            emit(0, "activity", text=f"[dj-live] {a['text']}")
            break                      # one line per tick — a coach, not a firehose
    except Exception:
        pass


# ---------------------------------------------------------------------------
# THE FOLLOWING VOICE (Chezy 2026-07-11: "THE VOCALS ARE A RE-RENDERED
# AUDIO?! IT NEEDS TO BE EDITABLE MIDI!"): vocal wavs are RENDERS of a melody
# lane — bindings in songs/<name>_vocals/follow.json (tools/vocal_follow.py).
# This tick watches every bound song; when the melody drifts (user edited
# notes, save settled >=10s), the voice re-renders OFF-THREAD in the original
# singer's timbre (retune --guide-track, surgical splice: unedited spans stay
# bit-true) and rewrites ONLY the wav — song.json is never written, so the
# open app has nothing to stomp. It also re-lands a stomped vocals_sketch
# from the melody cache (LIVE-APP STOMP LAW: a stale in-app save can erase a
# lane landed from outside; the cache is the durable truth and re-landing is
# idempotent). Kill switch: SOTADAW_NO_FOLLOW=1. Failure = honest chat line
# + 10-min backoff (never a 5s vocoder respawn storm).
_FOLLOW = {"scan_t": 0.0, "busy": False, "backoff": {}, "landed_note": set()}


def vocal_follow_tick(main_busy):
    if MOCK or os.environ.get("SOTADAW_NO_FOLLOW") == "1":
        return
    now = time.time()
    if _FOLLOW["busy"] or main_busy.is_set() or now - _FOLLOW["scan_t"] < 5.0:
        return
    _FOLLOW["scan_t"] = now
    try:
        import glob
        tdir = os.path.join(ROOT, "tools")
        if tdir not in sys.path:
            sys.path.insert(0, tdir)
        import vocal_follow as vf
        binds = glob.glob(os.path.join(SONGS, "*_vocals", "follow.json"))
    except Exception:
        return
    for bp in binds:
        name = os.path.basename(os.path.dirname(bp))[:-len("_vocals")]
        sp = os.path.join(SONGS, f"{name}.json")
        try:
            if not os.path.exists(sp) or now - os.path.getmtime(sp) < 10.0:
                continue                       # missing, or a save still settling
            if now < _FOLLOW["backoff"].get(name, 0):
                continue
            song = json.load(open(sp))
            names = {t.get("name") for t in song.get("tracks", [])}
            if vf.SKETCH_LANE not in names:    # STOMP-HEAL: re-land the edit surface
                mel = vf.cached_melody(name)
                if mel and vf.land_sketch(name, mel):
                    if name not in _FOLLOW["landed_note"]:
                        _FOLLOW["landed_note"].add(name)
                        emit(0, "activity", text=(
                            f"EDITABLE VOICE: {vf.SKETCH_LANE} re-landed on {name} "
                            f"(a stale save had dropped it) - reopen the song to "
                            f"see the vocal MIDI"))
                continue                       # land bumped mtime; next scan judges
            stale = [r for r in vf.check(name) if r.get("stale")]
        except Exception:
            continue
        if not stale:
            continue
        try:                                   # earlyoom etiquette: a vocoder never
            avail = 99.0                       # starts into a tight box
            for line in open("/proc/meminfo"):
                if line.startswith("MemAvailable:"):
                    avail = int(line.split()[1]) / 1048576.0
                    break
            if avail < 2.0:
                continue
        except Exception:
            pass
        _FOLLOW["busy"] = True

        def _run(nm=name, st=stale):
            try:
                emit(0, "activity", text=(
                    f"THE VOICE FOLLOWS: {nm} vocal melody edited - re-singing "
                    f"{len(st)} take(s) in the original singer's timbre "
                    f"(unedited spans stay bit-true)"))
                reps = vf.follow(nm)
                done = [r for r in reps if r.get("result") == "followed"]
                bad = [r for r in reps if "failed" in str(r.get("result", ""))]
                if done:
                    emit(0, "activity", text=(
                        "THE VOICE FOLLOWED: "
                        + ", ".join(os.path.basename(r.get("out_wav", "?")) for r in done)
                        + f" re-sung to your MIDI ({done[0].get('seconds', '?')}s) - "
                          "press play to hear it (reopen the song if it still "
                          "sounds like the old take)"))
                if bad:
                    _FOLLOW["backoff"][nm] = time.time() + 600.0
                    emit(0, "activity", text=(
                        f"voice follow failed honestly on {nm}: "
                        + "; ".join(str(r.get("result")) for r in bad)
                        + " - will retry in 10 min"))
            except Exception as e:
                _FOLLOW["backoff"][nm] = time.time() + 600.0
                try:
                    emit(0, "activity", text=f"voice follow failed honestly on {nm}: {e}")
                except Exception:
                    pass
            finally:
                _FOLLOW["busy"] = False
        threading.Thread(target=_run, daemon=True).start()
        return                                 # one follow at a time, box-polite


def ears_now_line(max_age_s=2.5):
    """THE EARS BUS (E3 R2): the last live feature frame from agent/ipc/ears.jsonl,
    rendered as one HEARING line for the NOW block. Empty string when the bus is
    silent/stale — the prompt never carries dead sensor data."""
    try:
        p = os.path.join(IPC, "ears.jsonl")
        with open(p, "rb") as f:
            f.seek(0, 2)
            f.seek(max(0, f.tell() - 4096))
            tail = f.read().decode("utf-8", "replace").strip().splitlines()
        fr = json.loads(tail[-1])
        if time.time() - float(fr.get("t", 0)) > max_age_s or not fr.get("playing"):
            return ""
        b = fr.get("bands_db", [-120] * 4)
        names = ["low", "lowmid", "mid", "high"]
        order = sorted(range(4), key=lambda i: -b[i])
        rms = fr.get("rms_db", [-120, -120])
        return (f"you are HEARING (live master bus): rms {(rms[0]+rms[1])/2:.1f} dB, "
                f"peak {max(fr.get('peak_db', [-120])):.1f} dB, crest {fr.get('crest_db', 0):.1f} dB, "
                f"bands {names[order[0]]}-dominant "
                f"({'/'.join(f'{names[i]} {b[i]:.0f}' for i in range(4))}), beat {fr.get('beat', 0):.1f}")
    except Exception:
        return ""


def transport_block(context, song_path):
    """THE NOW: render the UI's playhead/transport state into prompt context —
    'this part right here' resolves to an exact musical moment."""
    tp = (context or {}).get("transport") or {}
    if not tp:
        return ""
    try:
        song = json.load(open(song_path))
        beat = float(tp.get("playheadBeats", 0.0))
        w = surgical.whats_at(song, beat, halo=2.0)
        state = "PLAYING" if tp.get("isPlaying") else "paused"
        lines = [f"\nTRANSPORT — the user's playhead ({state}) is at this exact moment:",
                 surgical.render_whats_at(w)]
        hearing = ears_now_line()
        if hearing:
            lines.append(hearing)
        la, lb = tp.get("loopStartBeat"), tp.get("loopEndBeat")
        if isinstance(la, (int, float)) and isinstance(lb, (int, float)) and lb > la >= 0:
            lines.append(f"loop region armed: beats {la:g}-{lb:g} (bars {la/4:g}-{lb/4:g})")
        va, vb = tp.get("viewStartBeat"), tp.get("viewEndBeat")
        if isinstance(va, (int, float)) and isinstance(vb, (int, float)) and vb > va:
            lines.append(f"visible canvas window: beats {va:g}-{vb:g} (bars {va/4:g}-{vb/4:g})")
        lines.append("When the ask says 'here'/'now'/'this part' with NO selection, THIS moment "
                     "is the anchor — locate/select_notes around it before cutting.")
        return "\n".join(lines) + "\n"
    except Exception:
        return ""


def recent_edits_block(song, k=5, max_age_s=1800):
    """THE EDIT DIGEST (BEST_DAW_30 #13c, CC4 P2's last missing context organ):
    the last few edit receipts (base + live take) ride every prompt — follow-up
    asks ('a bit more', 'not that hat move') bind to what ACTUALLY just changed
    instead of a guess. Empty when nothing recent; never throws."""
    try:
        rows = (surgical.read_receipts(song)
                + surgical.read_receipts(f"_prop_{song}"))
        now = time.time()
        rows = [r for r in rows if now - float(r.get("ts", 0)) <= max_age_s]
        rows.sort(key=lambda r: float(r.get("ts", 0)))
        rows = rows[-k:]
        if not rows:
            return ""
        def _one(r):
            ago = max(0, int(now - float(r.get("ts", now))))
            what = r.get("summary") or r.get("tool", "?")
            flds = r.get("fields") or []
            return (f"  -{ago}s {what}"
                    + (f" [{', '.join(str(x) for x in flds[:3])}]" if flds else ""))
        return ("\nRECENT EDITS (the session's last moves — 'that', 'more', "
                "'undo the last one' refer to these):\n"
                + "\n".join(_one(r) for r in rows) + "\n")
    except Exception:
        return ""


def audio_verify(rid, base_json, prop_path, claim_tracks):
    """E3 NULL RECEIPTS (docs/THE_PHYSICS.md; flag SOTADAW_AUDIO_RECEIPTS=1, default
    OFF — costs 2 stems renders per proposal): render base+prop stems, subtract;
    every stem OUTSIDE the receipted claim must null <= -90 dBFS. JSON receipts say
    what was ASKED; this says what the AIR did. Fail-open on any error."""
    da = db_ = None
    try:
        sys.path.insert(0, os.path.join(ROOT, "tools"))
        import null_bench
        tag = f"avr{os.getpid() % 100000}"
        da = os.path.join(SONGS, f"_null_{tag}_base_stems")
        db_ = os.path.join(SONGS, f"_null_{tag}_prop_stems")
        for src, d in ((base_json, da), (prop_path, db_)):
            shutil.rmtree(d, ignore_errors=True)
            subprocess.run([M1, "render-stems", src, d], capture_output=True,
                           text=True, timeout=600)
            if not os.path.isdir(d):
                return None
        v = null_bench.compare_stem_dirs(da, db_, claim=claim_tracks, bar=-90.0)
        emit(rid, "activity", text="[null] " + (v.get("summary")
             or ("audio-proven: air outside the claim did not move"
                 if v.get("surgical_audio_proven")
                 else f"air MOVED out of scope: {v.get('unclaimed_active')}")))
        return v
    except Exception as e:
        emit(rid, "activity", text=f"[null] audio receipts skipped: {e}")
        return None
    finally:
        for d in (da, db_):
            if d:
                shutil.rmtree(d, ignore_errors=True)


def adopt_stranded_take(rid, song, prop, t0):
    """THE STRANDED TAKE (2026-07-11, the 10-min GOA epic): a run that builds its
    work in <song>_full.json (the arrange_song pattern) and never lands the accept
    target leaves _prop_ absent — the finalize then double-errors ("scope check
    skipped: Errno 2" + "render failed: cannot parse") and the take strands while
    the chat claims success. Absent prop + a run-fresh _full = ADOPT it (atomic),
    receipt it as the full write it is, and say so honestly."""
    pp = os.path.join(SONGS, f"{prop}.json")
    fp = os.path.join(SONGS, f"{song}_full.json")
    try:
        if os.path.exists(pp) or not os.path.exists(fp):
            return False
        if os.path.getmtime(fp) < t0 - 2:
            return False                       # stale _full from an older session
        json.load(open(fp))                    # only a PARSEABLE take gets adopted
        tmp = pp + ".w~"
        shutil.copy(fp, tmp)
        os.replace(tmp, pp)                    # atomic: never torn (W122 law)
        surgical.coarse_receipt(prop, "arrange_song", fields=["*"],
                                summary="stranded _full take adopted as the proposal")
        emit(rid, "activity",
             text=f"[deliver] the take landed in {song}_full.json — adopted as the "
                  "proposal (Audition/Accept as usual)")
        return True
    except Exception as e:
        emit(rid, "activity", text=f"[deliver] stranded-take adoption skipped: {e}")
        return False


def corpse_court(rid, song):
    """THE CORPSE COURT (2026-07-11): a pending prop that cannot SERVE —
    json-broken or half-context (the mid-run-accept collisions left props
    with tools' partial in-memory docs) — poisons every later run and render
    on the song ('cannot parse' repeated live on untitled_36). Quarantine it
    (.corpse, evidence kept) + drop its ledger; the run rebirths from base.
    Valid pending props pass untouched."""
    pj = os.path.join(SONGS, f"_prop_{song}.json")
    if not os.path.exists(pj):
        return
    try:
        d = json.load(open(pj))
        if isinstance(d.get("tracks"), list) and d.get("bpm"):
            return                      # serving shape — a real pending take
        why = "half-context: missing tracks/bpm"
    except Exception as e:
        why = f"unparseable ({type(e).__name__})"
    try:
        os.replace(pj, pj + ".corpse")
        for sfx in (".ghost.json", ".wav"):
            p = os.path.join(SONGS, f"_prop_{song}{sfx}")
            os.path.exists(p) and os.remove(p)
        surgical.clear_receipts(f"_prop_{song}")
        emit(rid, "activity",
             text=f"[court] the pending proposal was a CORPSE ({why}) — "
                  "quarantined to .corpse; this run starts fresh from the base")
    except Exception:
        pass


def scope_check(rid, base_json, prop_path, song):
    """THE SCOPE LAW: semantic-diff the proposal vs base; every change must be covered
    by an edit receipt (surgical_edit files exact note keys, blunt tools file coarse
    ones, write_song files '*'). The verdict rides the proposal event + telemetry."""
    try:
        base = json.load(open(base_json))
        prop = json.load(open(prop_path))
        receipts = surgical.read_receipts(f"_prop_{song}")
        rep = surgical.scope_report(base, prop, receipts)
        compact = {"clean": bool(rep.get("clean")), "full_write": bool(rep.get("full_write")),
                   "summary": rep.get("summary", ""),
                   "touched_tracks": rep.get("touched_tracks", []),
                   "note_changes": rep.get("note_changes", 0),
                   "receipts": rep.get("receipts", [])[:8],
                   "out_of_scope": rep.get("out_of_scope", [])[:12]}
        if not rep.get("empty"):
            emit(rid, "activity", text="[scalpel] " + compact["summary"])
        # E3: a CLEAN receipted claim can be audio-proven (claim == touched under
        # clean receipts). Out-of-scope proposals already wear their badge — no
        # audio court can bless them, so it only runs on clean ones.
        if (os.environ.get("SOTADAW_AUDIO_RECEIPTS") == "1" and compact["clean"]
                and not compact["full_write"] and compact["touched_tracks"]):
            v = audio_verify(rid, base_json, prop_path, compact["touched_tracks"])
            if v is not None:
                compact["audio_verified"] = bool(v.get("surgical_audio_proven"))
                if v.get("unclaimed_active"):
                    compact["audio_out_of_scope"] = v["unclaimed_active"][:6]
                _record_null_verdict(song, compact, v)
        return compact
    except Exception as e:
        emit(rid, "activity", text=f"[scalpel] scope check skipped: {e}")
        return None


def _record_null_verdict(song, compact, v):
    """NullVerdict telemetry (docs/THE_PHYSICS.md E12): the audio-null court's LIVE
    verdict lands in telemetry/null_verdicts.jsonl — ingestible into KG NullVerdict
    nodes (tools/kg_seed_physics.py --verdicts). Best-effort; never blocks a proposal."""
    try:
        rec = {"t": time.time(), "song": song,
               "claim": compact.get("touched_tracks", []),
               "audio_verified": compact.get("audio_verified"),
               "out_of_scope": compact.get("audio_out_of_scope", []),
               "note_changes": compact.get("note_changes", 0),
               "residuals": {k: val.get("residual_dbfs")
                             for k, val in (v.get("tracks") or {}).items()}}
        path = os.path.join(ROOT, "telemetry", "null_verdicts.jsonl")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a") as f:
            f.write(json.dumps(rec) + "\n")
    except Exception:
        pass

# ---------------- THE RESIDENT (CC4-I1): one warm agent process per model ----------------
# The 595s-median autopsy: every prompt paid a fresh `claude -p` spawn + the 87-tool
# MCP mount + skill injection (~16s before the first word) and threw away the prompt
# cache. A resident process mounts ONCE and answers every subsequent prompt warm
# (measured: spawn+turn 2.2s vs warm turn 1.0s on bare CLI; the MCP mount amortization
# is the real prize). stream-json input keeps the turn loop; we RECYCLE the process
# after RESIDENT_MAX_PROMPTS (context growth) or on song switch/error/cancel.
# SOTADAW_RESIDENT=0 disables (cold path stays the fallback FOREVER).
RESIDENT_MAX_PROMPTS = 6

class Resident:
    def __init__(self):
        self.procs = {}          # model -> {"p": Popen, "q": Queue, "n": prompts, "song": name}

    def _spawn(self, model, mcp_config, allowed, effort=None, book=None):
        env = daw_claude_env(MCP_TIMEOUT="30000", MCP_TOOL_TIMEOUT="600000")
        cmd = [claude_bin(), "-p", "--input-format", "stream-json",
               "--output-format", "stream-json", "--verbose",
               "--model", model, "--mcp-config", mcp_config, "--strict-mcp-config",
               "--permission-mode", "dontAsk", "--allowedTools", allowed,
               "--max-turns", "60"]
        if effort:
            cmd += ["--effort", effort]     # FABLE MODE law: the effort rides the spawn
        if token_stream_on():
            cmd.append("--include-partial-messages")   # token-level events for the pumps
        if book:
            # THE CANONICAL PROMPT: the stable rulebook is SYSTEM, cached by the
            # API prefix cache — every subsequent ask on this process pays task
            # bytes only (the rules used to ride EVERY user message).
            cmd += ["--append-system-prompt", book]
        p = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, cwd=ROOT, env=env)
        q = queue.Queue()
        def reader():
            for line in p.stdout:
                q.put(line)
            q.put(None)
        threading.Thread(target=reader, daemon=True).start()
        return {"p": p, "q": q, "n": 0, "song": None, "code_mtime": self.mcp_code_mtime(),
                "effort": effort,
                "book_h": hashlib.sha1((book or "").encode()).hexdigest()}

    def kill(self, model=None):
        for m in ([model] if model else list(self.procs)):
            r = self.procs.pop(m, None)
            if r:
                try:
                    r["p"].kill()
                except Exception:
                    pass

    @staticmethod
    def mcp_code_mtime():
        """The warm lane holds a LIVE daw_mcp server; edits to it (or surgical.py)
        don't reload into a running process. mtime = the staleness truth."""
        try:
            return max(os.path.getmtime(os.path.join(ROOT, "agent", "daw_mcp.py")),
                       os.path.getmtime(os.path.join(ROOT, "agent", "surgical.py")))
        except OSError:
            return 0.0

    def ask(self, model, prompt, mcp_config, allowed, song, effort=None, book=None):
        """Send one prompt on the warm process; returns (proc_handle, queue) or None
        (caller falls back to the cold rail). Recycles on budget/song-switch/dead/
        STALE CODE (a resident older than daw_mcp.py can serve receipt-free tools)/
        EFFORT MISMATCH (--effort is a spawn flag; a fable max ask can't ride a plain
        one)/BOOK MISMATCH (the canonical rulebook is a spawn flag too — a rules edit
        or canon toggle must never serve from a stale-book process)."""
        r = self.procs.get(model)
        bh = hashlib.sha1((book or "").encode()).hexdigest()
        if r and (r["p"].poll() is not None or r["n"] >= RESIDENT_MAX_PROMPTS + 1
                  or (r["song"] and song and r["song"] != song)
                  or r.get("code_mtime", 0) < self.mcp_code_mtime()
                  or r.get("effort") != effort
                  or r.get("book_h") != bh):
            self.kill(model)
            r = None
        if r is None:
            try:
                r = self._spawn(model, mcp_config, allowed, effort, book=book)
                self.procs[model] = r
            except Exception:
                return None
        try:
            r["p"].stdin.write(json.dumps({"type": "user", "message": {
                "role": "user", "content": [{"type": "text", "text": prompt}]}}) + "\n")
            r["p"].stdin.flush()
        except Exception:
            self.kill(model)
            return None
        r["n"] += 1
        r["song"] = song if song is not None else r.get("song")
        return r

RESIDENT = Resident()

_SELF_PATH = os.path.abspath(__file__)
_SELF_MTIME = os.path.getmtime(_SELF_PATH)

def _self_refresh_due():
    """True when sidecar.py on disk is newer than the RUNNING image (a committed
    ship this daemon predates). Checked ONLY between requests — never mid-flight."""
    try:
        return os.path.getmtime(_SELF_PATH) > _SELF_MTIME + 0.5
    except OSError:
        return False

# PRE-WARM (firing 111): the x3 user-path E2E convicted per-lane first-spins —
# pick_model routes asks to THREE models, so every "warm" run was actually cold
# (20-25s spawn+defer each). Boot-time warmup spawns each lane and pays the
# defer tax OFF-SCREEN: one synthetic turn batch-loads the core schemas, so the
# human's first prompt gets direct tool calls. Skipped under SOTADAW_NO_PREWARM.
WARM_MODELS = ("claude-haiku-4-5-20251001", "claude-sonnet-5", "claude-opus-4-8")
WARMUP_MSG = ("Bootstrap this session: call ToolSearch ONCE with "
              "'select:mcp__daw__start_session,mcp__daw__get_song_summary,"
              "mcp__daw__get_song_region,mcp__daw__update_track,mcp__daw__add_track,"
              "mcp__daw__set_track_fx,mcp__daw__update_song_meta,mcp__daw__automate,"
              "mcp__daw__locate,mcp__daw__select_notes,mcp__daw__surgical_edit,"
              "mcp__daw__render_song,mcp__daw__analyze_wav,mcp__daw__generate_loop,"
              "mcp__daw__arrange_song,mcp__daw__duplicate_bars,mcp__daw__clear_bars,"
              "mcp__daw__harmonize,mcp__daw__apply_groove,mcp__daw__use_tool' "
              "then reply exactly READY. Do not call any daw tool.")
# THE WARM SHAPE (BEST_DAW_30 #11a, CC4 §7.1 lever b): the first REAL ask of a
# session pays a ~60-80s one-time REASONING tax (measured f136 — not prefill).
# SOTADAW_WARMSHAPE=1 pays it off-screen: the warmup additionally THINKS through
# one canned compose-shaped plan (no tools, no song, pure reasoning) so the
# human's first ask lands warm. Default OFF — it spends tokens at every daemon
# boot, so the flip is Chezy's. Bar when on: first-ask p50 <= 1.5x warm-ask p50.
if os.environ.get("SOTADAW_WARMSHAPE") == "1":
    WARMUP_MSG = ("Bootstrap this session in two steps. 1) Think through — "
                  "internally, do NOT write the plan out and do NOT call any daw "
                  "tool — a full production plan for: 'a dark 140 BPM UK garage "
                  "track in F minor with a vocal chop hook' (sections, tracks, "
                  "voices, groove, mix moves, wall). 2) " + WARMUP_MSG[0].lower()
                  + WARMUP_MSG[1:])

def prewarm():
    if os.environ.get("SOTADAW_NO_PREWARM") == "1" or MOCK or claude_bin() is None:
        return
    try:
        mcp_config, extra_allow, _names = build_mcp_config()
        allowed = ",".join([DAW_ALLOW] + extra_allow) + ",ToolSearch"
        # prewarm with the SAME canonical book real asks will carry — a book
        # mismatch would recycle the resident on the first human ask (warmth wasted)
        book = build_book(tuple(_names)) if os.environ.get("SOTADAW_CANON", "1") != "0" else None
    except Exception:
        return
    def one(model):
        try:
            r = RESIDENT.ask(model, WARMUP_MSG, mcp_config, allowed, song=None, book=book)
            if r is None:
                return
            t0 = time.time()
            while time.time() - t0 < 120:          # drain until READY (result event)
                try:
                    line = r["q"].get(timeout=1)
                except queue.Empty:
                    continue
                if line is None:
                    return
                if '"type":"result"' in line.replace(" ", "") or '"type": "result"' in line:
                    break
            r["song"] = None                        # any song may claim the warm lane
            print(f"[sidecar] prewarmed {model.split('-')[1]} in {time.time()-t0:.0f}s", flush=True)
        except Exception as e:
            print(f"[sidecar] prewarm {model} failed: {e!r}", flush=True)
    for mdl in WARM_MODELS:
        threading.Thread(target=one, args=(mdl,), daemon=True).start()


def keep_canceled_take(req_id, song_name, prop):
    """STOP KEEPS THE TAKE (2026-07-11, caught with Chezy live): cancel used
    to DELETE the streamed proposal — half an hour of ghost-streamed work
    gone on the very button that should end the WAIT, not the WORK. If the
    proposal has tracks, keep it and arm the deck (unrendered: Audition
    plays it app-side instantly; EARS fill on the next render). Only an
    empty/absent proposal cancels clean. Returns True when a take was kept."""
    pp = os.path.join(SONGS, f"{prop}.json")
    try:
        keep = os.path.exists(pp) and bool(json.load(open(pp)).get("tracks"))
    except Exception:
        keep = False
    if keep:
        try:   # WALL AT KEEP-TIME (2026-07-11): a stop-kept take auditions
            #  through the live engine with whatever master the stream wrote —
            #  stage the release wall in the JSON now (render-free) so playback
            #  and a naive accept are never unwalled
            _awrite(pp, stage_wall(json.load(open(pp))))
        except Exception:
            pass
        emit(req_id, "proposal", song=song_name, proposal=prop)
        emit(req_id, "activity",
             text="Stop: the streamed take was KEPT on the deck (unrendered — "
                  "Audition plays it now, wall staged; EARS fill on render)")
        try:   # THE UNFINISHED-VOICE FLAG: a stop can land mid-vocal-swap
            gap = vocal_gap(json.load(open(pp)))
        except Exception:
            gap = None
        if gap:
            emit(req_id, "activity", text=f"kept take is MID-VOCAL-WORK: {gap}")
            chronicle.append(song_name, "note",
                             f"(the kept take is unfinished: {gap})")
        emit(req_id, "done", ok=True)
        chronicle.append(song_name, "note",
                         "(user hit Stop — the streamed take was KEPT on the deck)")
        return True
    if os.path.exists(pp):
        os.remove(pp)
    chronicle.append(song_name, "note",
                     "(the user hit Stop — nothing streamed yet, run canceled)")
    return False


def resolve_failed_codex_take(req_id, prop, prop_path, base_path,
                              existed_on_entry, start_data, start_receipts):
    """Resolve a nonzero Codex turn without leaving a hidden pending proposal.

    Returns ``restored`` (a pre-existing pending take + receipt scope restored),
    ``salvaged`` (fresh, agent-changed, substantial work remains visible), or
    ``discarded`` (fresh work was absent/insubstantial and all state was removed).
    Pure inference is outside this helper; its file transitions are battery-tested.
    """
    ghost_path = prop_path.replace(".json", ".ghost.json")

    def restore_receipts():
        surgical.clear_receipts(prop)
        for receipt in start_receipts:
            surgical.append_receipt(prop, receipt)

    def restore_pending():
        with open(prop_path + ".restore~", "wb") as fh:
            fh.write(start_data)
        os.replace(prop_path + ".restore~", prop_path)
        restore_receipts()
        shutil.copyfile(prop_path, ghost_path)
        emit(req_id, "proposal_progress", proposal=prop,
             ghost=f"{prop}.ghost")
        emit(req_id, "activity",
             text="Codex revision failed — restored the pending take unchanged")
        return "restored"

    def discard_fresh():
        for stale in (prop_path, ghost_path, prop_path + ".restore~"):
            try:
                os.path.exists(stale) and os.remove(stale)
            except OSError:
                pass
        surgical.clear_receipts(prop)
        emit(req_id, "activity",
             text="Codex failed before substantial work — partial take discarded")
        return "discarded"

    try:
        current_data = open(prop_path, "rb").read() if os.path.exists(prop_path) else None
        if existed_on_entry and start_data is not None:
            return restore_pending()
        agent_changed = (current_data is not None and start_data is not None
                         and current_data != start_data)
        if agent_changed:
            base, current = json.load(open(base_path)), json.loads(current_data)
            notes = lambda s: sum(len(t.get("notes", [])) for t in s.get("tracks", []))
            autos = lambda s: sum(len(t.get("automation", [])) for t in s.get("tracks", []))
            substantial = (notes(current) - notes(base) >= 8
                           or len(current.get("tracks", [])) > len(base.get("tracks", []))
                           or autos(current) > autos(base))
            if substantial:
                emit(req_id, "status",
                     text="Codex ended early but left substantial work — salvaged")
                return "salvaged"
        return discard_fresh()
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        # Corrupt/vanished state cannot remain as an invisible parse blocker.
        if existed_on_entry and start_data is not None:
            try:
                return restore_pending()
            except OSError:
                pass
        return discard_fresh()


def stream_resident(r, req_id, tag="agent", song=None):
    """Pump ONE turn off the resident's shared queue (until its `result` event).
    Same UX contract as stream_events: heartbeats, cancel flag (cancel kills the
    resident — next prompt respawns warm-path), full text -> chat fold law,
    song set = streamed prose chronicled as `note` rows."""
    st = StreamState(req_id, tag, song)   # pass 5: live typing + token ghosts
    silent, last_result = 0.0, None
    t_run = time.time()
    started_live = console_was_live()     # run-lifecycle law: bound to ITS console
    while True:
        gone = console_gone(started_live)
        if os.path.exists(CANCEL_FLAG) or gone:
            if os.path.exists(CANCEL_FLAG):
                os.remove(CANCEL_FLAG)
            RESIDENT.kill()
            emit(req_id, "status",
                 text="console closed - run canceled (nothing runs behind a closed session)"
                      if gone else "canceled by user")
            return True, None
        try:
            line = r["q"].get(timeout=0.5)
        except queue.Empty:
            silent += 0.5
            if silent >= 25.0:
                mins = int((time.time() - t_run) // 60)
                # past 15 min, say the quiet part out loud: Stop is SAFE —
                # the streamed proposal stays on the lanes as the take
                # (Chezy watched a 48-min run not knowing this, 2026-07-11)
                _hb = f"{tag}: …composing{f' ({mins} min in)' if mins else ''}, still streaming…"
                if mins >= 15:
                    _hb += " (long run — Stop keeps everything already on the lanes)"
                emit(req_id, "activity", slot="heartbeat", text=_hb)
                silent = -35.0
            continue
        if line is None:                      # process died mid-turn
            RESIDENT.kill()
            return False, None
        silent = 0.0
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        et = ev.get("type")
        if et == "stream_event":
            st.on_stream_event(ev)        # token-level: chat types, ghosts land
        elif et == "assistant":
            for blk in (ev.get("message", {}).get("content") or []):
                if blk.get("type") == "tool_use":
                    emit_action(req_id, blk)   # the ACTION WIRE: structured, first
                    emit(req_id, "activity", text=f"{tag}: {blk['name'].replace('mcp__daw__','').replace('mcp__','@')}")
                elif blk.get("type") == "text" and blk.get("text", "").strip():
                    emit(req_id, "activity", text=f"{tag}: " + blk["text"].strip()[:4000])
                    if song:
                        chronicle.append(song, "note", blk["text"])
        elif et == "result":
            return False, ev

# ---------------- real agent (claude -p) ----------------
PERSONAS = {}
try:
    PERSONAS = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "personas.json")))
except Exception:
    pass

def persona_block(name):
    """The ADHD-personas layer: request.persona -> behavioral contract in the prompt."""
    c = (PERSONAS.get(str(name or "").lower()) or {}).get("contract", "")
    return ("\n" + c + "\n") if c else ""

def prompt_rules(slim, arranged_note="", ghost_first="", taste_slim=""):
    """The producer rulebook, TIERED (I9, THE TEN). slim=True is the EDIT lane's
    compact book (~1/3 the bytes): every damage-preventer law verbatim, the
    compose-only domain tours (VOICE/PERFORMANCE/DJ/CHOP/LOOP-GENERATOR/long-form)
    dropped — use_tool's catalog carries them. slim only fires when the ask is
    edit-class (no arranged/ghost blocks by construction). Kill-switch:
    SOTADAW_SLIM_EDIT=0 keeps the full book on every ask.
    tools/prompt_lint.py asserts both tiers carry the laws."""
    if slim:
        return """- TOOL BOOTSTRAP: if tool schemas arrive DEFERRED, load EVERYTHING your plan needs in ONE ToolSearch call (comma-separated select list). Then act.
- Use ONLY the daw MCP tools; every long-tail tool is one use_tool(name, args) call away (unknown names return the catalog). Do NOT use ToolSearch for anything else, or Read/Edit/Bash — they are unavailable and waste time.
- First start_session (loads skills). The SONG DIGEST above already gives you the structure — for gain/pan/fx/sends/meta/automation moves act DIRECTLY from the digest. READ LAW for note data: get_song_summary (structure, ~1KB any size) then get_song_region the PROPOSAL COPY for JUST the bars you are editing (notes carry _idx for select_notes/surgical_edit). Full get_song only for small songs.
- SELECTION = CONTEXT: if a SELECTION CONTEXT block appears above, it is THE subject — "this"/"these"/"here" means the selection. Edit it and leave the rest alone.
- THE SCALPEL (scoped asks): locate (timestamps/sections/descriptions -> beats + what's sounding) -> select_notes (verify the exact match set) -> surgical_edit (ops on exactly those notes). Every cut files a receipt; the sidecar diffs the proposal against receipts and flags anything unreceipted OUT OF SCOPE. Never resend whole tracks (update_track notes) or whole songs (write_song) for a scoped ask. SELECTED NOTES ship indices: selector {"tracks":"<track>","indices":[...]} hits exactly them.
- Modify ONLY the PROPOSAL COPY: update_track (notes/gain/pan/sends/muted; remove:true deletes a track — never write_song for that), set_track_fx (the whole chain in order; fx_filter/fx_reverb/fx_delay/fx_saturate/fx_widen/fx_pump + built-ins type eq/comp), add_track, update_song_meta (bpm/swing/masterGainDb/master/key/tempoMap), set_buses + update_track sends, list_plugin_params / set_track_param / automate. Faust params are real zone units — fx_trim's zone is 'level', NOT 'gain'; vst3 params are natural display units.
- SWING-GRID LAW: a swing{} object's grid MUST match where the hats live — 8th-note hats need {"grid":"8th"}; a 16th swing never touches even-step patterns (silent no-op). apply_groove bakes feel instead.
- MISSING REFERENT LAW: if the ask names a device/part that does not exist ("open THE filter" with no filter), CREATE the sensible one and apply the intent — never silently no-op.
- EVERY QUALIFIER IS A HARD CONSTRAINT: words like "quieter", "only", "slightly", "except the vocal", "an octave up" must each be verifiably true of your edit (a change scoped "in the verse only" touches nothing outside the verse). Re-read the ask before finishing and check each qualifier off.
- TRANSPOSE MEANS NOTES: a transpose moves PITCHES — key metadata alone is not a transpose; update metadata IN ADDITION to moving notes. "Transpose everything" means MELODIC material; drum/trigger lanes keep their pitches unless drums are explicitly named.
- COPY OPERATIONS RE-APPLY QUALIFIERS: doubled/copied material inherits its source values — apply the ask's qualifiers TO THE COPY as a second step and verify (e.g. "double it quieter" = copy THEN scale the copy's velocities).
- MATCH THE SCOPE OF THE ASK: for "better/bigger" asks make bold audible moves; for narrow asks change only what was asked.
- SELF-CHECK RENDERS on songs >24 bars: render_song max_bars=16. Then render_song the PROPOSAL COPY + analyze_wav; fix clipping (clipped_samples>0); max 2 iterations.
- Be fast: aim for under ~8 tool calls on an edit-scale ask.
- End with 2-4 bullets: exactly what you changed and why it is audibly better."""
    return f"""- TOOL BOOTSTRAP: if tool schemas arrive DEFERRED, load EVERYTHING your plan needs in
  ONE ToolSearch call (comma-separated select list) — one-by-one loading wastes half a
  minute. Then act.
- Use ONLY the daw MCP tools. The visible set is the CORE (~36); every long-tail tool
  (bridges, DJ, presets, vocals, import_song_audio, prescribe/color/restyle...) is one
  call away via use_tool(name, args) — unknown names return the catalog. Do NOT use ToolSearch, Read, Edit, Bash, or any other tool — they are unavailable and waste time.
- First start_session (loads skills). The SONG DIGEST above already gives you the full structure — for gain/pan/fx/sends/meta/automation moves act DIRECTLY from the digest. READ LAW for note data: get_song_summary (structure, ~1KB any size) then get_song_region the PROPOSAL COPY from_bar..to_bar [tracks] for JUST the bars you are editing (notes carry _idx for select_notes/surgical_edit). Full get_song ONLY for whole-song rewrites on small songs — on a large song it is megabytes and wastes minutes (measured: 478x/71x smaller via summary/region).
- SELECTION = CONTEXT: if a SELECTION CONTEXT block appears above, it is THE subject — "this"/"these"/"here" in the ask means the selection. Edit the selected notes/tracks/range/groove/slot/master and leave the rest alone unless explicitly asked. get_selection re-reads it mid-run.
- THE SCALPEL (scoped asks): when the user points at a sound/moment/notes ("this note", "the hats in the drop", "at 1:23", "the 3rd kick", a selection, the playhead) — locate (resolves timestamps/sections/descriptions to beats + what's SOUNDING there) -> select_notes (verify the exact match set) -> surgical_edit (ops on exactly those notes: transpose/nudge/vel/quantize/humanize/stretch/ramp/delete/insert/replace). Every cut files a receipt; the sidecar DIFFS your whole proposal against receipts and anything unreceipted is flagged OUT OF SCOPE to the user. Do NOT resend whole tracks (update_track notes) or whole songs (write_song) for a scoped ask — that reads as blunt and slow. SELECTED NOTES ship indices: selector {{"tracks":"<track>","indices":[...]}} hits exactly them.
- Modify ONLY the proposal copy the PROPOSAL COPY with surgical tools: update_track (notes/gain/pan/sends), set_track_fx (fx_filter, fx_reverb, fx_delay, fx_saturate, fx_widen, fx_pump — SPACE and DEPTH live here; dry tracks sound like demos; PLUS built-ins: {{"type":"eq","params":{{loFreq,loGain,hiFreq,hiGain,midFreq,midGain,midQ}}}} and {{"type":"comp","params":{{threshold,ratio,attack,release,outputDb}}}} — see mix-eq skill recipes), add_track (new instrument/kit/vst3 layers; kits "sota_drums" (staged drums), "sota_keys" (rhodes zones), "sota_bass" (warm bass zones) are OURS, self-sampled from our own DSP — prefer them over gm_drums/piano), update_song_meta (bpm/swing/masterGainDb/master chain — eq/comp allowed in master too). Faust fx params are real zone units — fx_trim's zone is 'level', NOT 'gain' (a 'gain' param is a silent no-op). write_song only for full rewrites.
- THE VOICE: for hooks/vocals — write_lyrics (beat-aligned, aware of the drop) + a melody track, then hum_topline(song, "lead") = an INSTANT wordless vocal hook (laa/ooh/...) over any generated melody — no lyrics needed; sing_lyrics(song, melody_track) renders a REAL sung vocal from written words (local DiffSinger; the 'vocals' audio track is editable/replaceable like anything else). VOICE FROM A HUM: the user's hummed/recorded melody -> audio_to_midi (key-snapped melody track) -> write_lyrics -> sing_lyrics = the DAW sings THEIR tune with THEIR words.
- GROOVE IS LIFE: after writing on-grid patterns, `apply_groove` (dilla, ukg_shuffle, psy_straight, dembow_lilt, boombap_56; amount 0.6-1.0) on drums/hats — quantized-dead patterns fail bold asks. `extract_groove` learns feel from any track. SWING-GRID LAW: if you use the swing{{}} object, its grid MUST match where your hats live — 8th-note hats need {{"grid":"8th"}}; a 16th swing only shifts odd 16ths and never touches even-step patterns (silent no-op).
- THE PERFORMANCE: when the ask implies jamming/arrangement exploration, author scene STORIES with set_clip_slot (scene 0 = groove bed, 1 = build, 2 = drop, scene_name them) — the human performs them in the Live view and jam-captures; scene_bounce(song, scene) renders any scene so you can HEAR it before shipping the story; scene_strips(song) instantly adds the live-remix staples (Drums only / No drums / Bass+Drums) to any sceneful session. Audio loop slots take audio_file + source_bpm (warped to the song tempo). edit_section duplicate = 'double the drop' (moves notes, automation, clips and lyrics coherently).
- THE DJ: 'mix/blend/transition these songs' or set-building asks -> dj_blend(deck_a, deck_b, song): auto beat-match via warp (sourceBpm on every deck's audioClips), phrase-aligned crossfade, fx_djfilter bass swap — all of it visible automation you can then reshape. Imported stems are already warped: change bpm with update_song_meta and the whole session follows ('remix at 140' = one call). Full events: dj_set(tracks[]) = one continuous set with a traveling tempo grid — it PICKS deck order (tempo arc + Camelot path) and per-hop style (blend vs echo-out cut beyond 16% tempo distance). A working DJ's library enters via import_rekordbox(collection.xml): authoritative bpm/key/first-beat offsets, then dj_set with the printed values. tempoMap on any song = tempo switches/ramps (halftime drops, ritardandos) — all beats and warped audio follow.
- THE CHOP: 'flip/chop/sample this' -> chop_sample(audio, kit) slices any audio into pads (keys 36+). The classic flip: import_song_audio -> chop_sample the 'other' or 'drums' stem -> sequence pads with a new sample-kit track -> apply_groove.
- THE LOOP GENERATOR: 'start me a <genre> loop / give me a groove' -> generate_loop(genre, song, bars, seed) = a complete editable loop; arrange_song(song) then turns any loop into a SONG SKELETON (genre-aware: drops or verse/chorus); make_track(genre) does the WHOLE chain in one call (loop w/ harmony+hook+fill -> arranged -> rendered) — THE instant track, then differentiate from the KG's pattern DNA (ALL 130 graph genres: archetype drums + bass in key by style + recipe color + swing); new seed = new take. 'variations/options/flip this loop' -> loop_variations(song, track, from_bar, bars) = 6 instant launcher scenes (rotate/thin/dense/recolor/halftime/humanize). Offer these whenever the user is circling one loop — the fastest ideas-per-second tools in the DAW.
- MOTION IS MUSIC: static parameters sound like demos. Use `automate` for builds, drops and transitions — filter opens (fx_filter cutoff into the drop), volume rides (gainDb), width blooms (fx_widen width), throw sends. Use `set_buses` + update_track sends for shared reverb/delay space (pro mix paradigm; keep kick/808 DRY). Use `list_plugin_params` to see EVERY knob (faust zones AND vst3 params) with ranges; `set_track_param` sets one statically, `automate` moves it over time.
- MATCH THE SCOPE OF THE ASK: for "better/bigger/more X" asks, make BOLD, clearly audible moves — automation arcs, FX chains, new layers, rewritten parts — not just ±3dB nudges. For narrow asks, change only what was asked.
- MISSING REFERENT LAW: if the ask names a device/part that does not exist ("open THE
  filter" with no filter), CREATE the sensible one and apply the intent (add fx_filter
  then open it) — never silently no-op. Deleting a track = update_track remove:true
  (scoped), never write_song.
- EVERY QUALIFIER IS A HARD CONSTRAINT: words like "quieter", "only", "slightly", "except the vocal", "an octave up" are not decoration — each one must be verifiably true of your edit (a change scoped "in the verse only" touches nothing outside the verse). Re-read the ask before finishing and check each qualifier off.
- TRANSPOSE MEANS NOTES: a transpose moves PITCHES (surgical_edit op transpose / note
  edits) — changing the song's key METADATA alone is not a transpose (measured miss:
  a take shipped with key renamed and zero notes moved). Update key metadata IN
  ADDITION to moving notes, never instead.
- TRANSPOSE IDIOM: "transpose everything/the song" means MELODIC material — drum and
  trigger lanes (kick/snare/hat/perc/808-pitch-as-trigger) keep their pitches unless
  drums are EXPLICITLY named (retuning a kick on a global transpose reads as broken).
- COPY OPERATIONS RE-APPLY QUALIFIERS: doubled/copied/layered material inherits its source values — so the ask's qualifiers must be applied TO THE COPY as a second step ("double it quieter" = copy at +12 THEN scale the copy's velocities to ~0.6-0.75x, e.g. surgical_edit op scale on the new notes; verify the copy's vels are actually lower before finishing). Measured failure mode: 2 of 3 runs shipped copies at source velocity.
- LONG-FORM LAW (anything beyond ~32 bars): NEVER write hundreds of literal notes — you will stall. Compose an 8-16 bar SEED section in full detail (update_track/write_song on those bars only), then BUILD the arrangement server-side: `duplicate_bars` stamps the seed across sections instantly; `clear_bars` (with tracks filter) carves breakdowns (clear drums) and intros/outros; then differentiate sections with `automate` arcs (filter builds into drops) and a few surgical notes. A 6-minute track = 1 seed + ~6 stamps + 3 carves + 4 automation arcs, not 10,000 notes.
{arranged_note}{ghost_first}- SELF-CHECK RENDERS on songs >24 bars: render_song max_bars=16 (a fifth of the wall
  time; the sidecar renders the FULL song after your proposal automatically).
- Keep skill hard constraints. Then render_song the PROPOSAL COPY + analyze_wav songs/the PROPOSAL COPY.wav; fix clipping (clipped_samples>0) if present; check rms/centroid_by_quarter to confirm your automation actually MOVES; max 2 iterations.
- Be fast: aim for under ~12 tool calls unless the ask demands more.
- End with 2-4 bullets: exactly what you changed and why it is audibly better.{taste_slim}"""

def build_book(connector_names=()):
    """THE CANONICAL PROMPT (pass 5): the STABLE layer — identity + the FULL
    rulebook — shipped ONCE per spawn as the appended SYSTEM prompt, where the
    API's prefix cache (1h ephemeral on this CLI) pays for it a single time per
    process. Before this, the rules rode EVERY user message (~13K chars re-paid
    per ask, resident included). Content here must be ask- and song-independent:
    prompt_lint asserts byte-stability across asks and that every damage-
    preventer law binds in the book."""
    book = ("You are the in-app producer agent for this DAW. These rules and laws never "
            "change; THE TASK (song, ask, live context) arrives as each user message.\n"
            "Rules:\n" + prompt_rules(False)
            + "\n- THIS-RUN DIRECTIVES: a task message may OPEN with per-run directives "
              "(taste mode, pre-seeded shape, first-move law) — they override these "
              "defaults for THAT run only.\n"
              "- CONVERSATION CONTINUITY: if a '# Session start' result is already "
              "visible earlier in THIS conversation, do NOT call start_session again — "
              "those skills are loaded; act directly.\n")
    if connector_names:
        book += (f"- EXTERNAL DAW CONNECTORS MOUNTED: {', '.join(connector_names)} — their tools "
                 f"(mcp__{connector_names[0]}__*, …) drive the user's RUNNING external DAW. Use them "
                 "only when the ask concerns that DAW; our own daw tools remain primary.\n")
    return book

def assemble_prompt(canon, slim, prop, song_name, text, fb_line, persona, ctx_block,
                    dig_block, arranged_note="", ghost_first="", taste_slim="",
                    connector_names=()):
    """THE ONE PROMPT SEAM — returns (book_or_None, prompt). canon=True: book =
    stable system layer, prompt = volatile task only (run directives lead it).
    canon=False: legacy single message (book None), byte-shape preserved.
    Pure (no IO) so prompt_lint/canon checks can prove both shapes."""
    task_body = f"""=== THE TASK ===
Proposal copy (EVERY edit targets it): "{prop}"
The user is working on song "{song_name}" and asks:
"{text}"{fb_line}{persona}{ctx_block}{dig_block}"""
    if canon:
        volatile = ""
        if arranged_note or ghost_first or taste_slim:
            volatile = ("THIS-RUN DIRECTIVES (override the standing rules for this run only):\n"
                        + arranged_note + ghost_first + taste_slim + "\n\n")
        return build_book(connector_names), volatile + task_body
    prompt = ("You are the in-app producer agent for this DAW. Your rules and laws come\n"
              "first and never change; THE TASK (song, ask, live context) follows after the divider.\n"
              "Rules:\n"
              + prompt_rules(bool(slim), arranged_note, ghost_first, taste_slim)
              + "\n\n" + task_body)
    if connector_names:
        prompt += (f"\nEXTERNAL DAW CONNECTORS MOUNTED: {', '.join(connector_names)} — their tools "
                   f"(mcp__{connector_names[0]}__*, …) drive the user's RUNNING external DAW. Use them "
                   f"only when the ask concerns that DAW; our own daw tools remain primary.")
    return None, prompt

def real_propose(req_id, text, song_name, ctx_block="", persona_name="", model_override=None, revise=False, genre_pref_hint="", effort=None, seed_skeleton=False):
    prop = f"_prop_{song_name}"
    prop_path = os.path.join(SONGS, f"{prop}.json")
    prop_existed_on_entry = os.path.exists(prop_path)
    arranged_note = ""
    # FEEDBACK IS NOT REJECTION: a revise request iterates the PENDING proposal in
    # place — the base is never copied over it; the take survives the conversation.
    revise = bool(revise) and os.path.exists(prop_path)
    if not revise:
        shutil.copy(os.path.join(SONGS, f"{song_name}.json"), prop_path)
        # PRE-SEED THE SHAPE (firing 113): on compose-class asks the CANVAS must move
        # in seconds — from CODE, not tokens. If the song has no real arrangement yet,
        # stamp a genre-shaped section skeleton on the PROP immediately; the ghost
        # watcher streams it (<2s), the agent FILLS INTO it. Receipted (scope law).
        # THE SEED IS A CHOICE (Chezy law 2026-07-11): opt-in via the UI SEED chip
        # (rides the request) — never stamped on every song; heavy models compose
        # free, cheap models opt into guided structure.
        if seed_skeleton and BIG_RE.search(str(text or "")):
            try:
                doc = json.load(open(prop_path))
                # (f134 autopsy) precompute the genre: when a DNA seed will run, the
                # FINISH capstone owns sections — an early stamp made finish skip
                # arrange ("real arrangement" honor) and shipped 8-bar 'produced' takes
                _cache_g = json.load(open(os.path.join(ROOT, "agent", "dna_cache.json")))["genres"]
                _tl = str(text).lower()
                _gname_pre = next((g for g in sorted(_cache_g, key=len, reverse=True)
                                   if g.replace("_", " ") in _tl or g in _tl), None)                     or (str(genre_pref_hint).strip().lower()
                        if str(genre_pref_hint).strip().lower() in _cache_g else None)
                if not _gname_pre:
                    # SEMANTIC ROUTING (pass 5): the ask names no literal genre —
                    # KNN its vibe against the KG captions (kg_vibe, MiniLM) and
                    # seed the nearest KNOWN dna genre. Weak routes (cos < 0.35)
                    # are advisory-only and never seed.
                    try:
                        py_v = VENV_PY if os.path.exists(VENV_PY) else "python3"
                        _rcv, _outv, _ = run([py_v, os.path.join(ROOT, "tools", "kg_vibe.py"),
                                              str(text), "--k", "6"], timeout=90)
                        _lv = next((l for l in _outv.splitlines()
                                    if l.startswith("VIBE_JSON ")), "")
                        _dv = json.loads(_lv[len("VIBE_JSON "):]) if _lv else {}
                        if _dv.get("available") and not _dv.get("weak"):
                            _gname_pre = next((x["genre"] for x in _dv["results"]
                                               if x["genre"] in _cache_g), None)
                            if _gname_pre:
                                emit(req_id, "activity",
                                     text=f"[shape] vibe-routed: no literal genre in the ask -> "
                                          f"{_gname_pre} (cos {_dv['results'][0]['score']})")
                    except Exception:
                        pass
                if not _gname_pre and len(doc.get("sections") or []) < 2:
                    bars = int(float(doc.get("lengthBars", 8)) or 8)
                    t_low = str(text).lower()
                    poppy = any(w in t_low for w in ("pop", "verse", "chorus", "ballad",
                                                     "rnb", "r&b", "song with vocals"))
                    if bars >= 24:
                        arc = ([("intro", 0), ("verse", 4), ("chorus", 12), ("verse 2", 16),
                                ("chorus 2", 24 * bars // 32), ("outro", bars - 4)] if poppy else
                               [("intro", 0), ("build", 4), ("drop", 8), ("break", bars // 2),
                                ("drop 2", bars // 2 + 4), ("outro", bars - 4)])
                    elif bars >= 8:
                        arc = [("intro", 0), ("build", bars // 4), ("drop", bars // 2),
                               ("outro", bars - max(2, bars // 8))]
                    else:
                        arc = [("groove", 0), ("turn", max(2, bars - 2))]
                    seen_b = set()
                    doc["sections"] = [{"name": n, "startBar": float(b)} for n, b in arc
                                       if b < bars and not (b in seen_b or seen_b.add(b))]
                    _awrite(prop_path, doc)
                    surgical.coarse_receipt(prop, "preseed", fields=["meta:sections"],
                                            summary="shape pre-seeded (sidecar, t=0)")
                    emit(req_id, "activity",
                         text="[shape] pre-seeded " + str(len(doc["sections"])) + " sections ("
                              + " ".join(n for n, _ in arc) + ") — the agent fills into them")
                # PRE-SEED TRACKS (firing 114): if the ask (or the genre box) names a
                # KNOWN genre and the song is sparse, drop the genre's DNA loop onto
                # the prop at t=0 and tile it across the skeleton — REAL notes on the
                # canvas in ~2s; the agent edits material instead of a void.
                sparse = sum(len(t.get("notes", [])) for t in doc.get("tracks", [])) < 100
                if sparse:
                    try:
                        sys.path.insert(0, os.path.join(ROOT, "tools"))
                        import loop_gen as _lg
                        gname = _gname_pre
                        if gname:
                            import tempfile as _tf
                            tmp = "_seed_" + song_name
                            _out, _msg = _lg.generate(gname, tmp, bars=4,
                                                      seed=int(time.time()) % 9973)
                            seeddoc = json.load(open(_out))
                            os.remove(_out)
                            bars_total = int(float(doc.get("lengthBars", 8)) or 8)
                            have = {t.get("name") for t in doc.get("tracks", [])}
                            added = []
                            for st in seeddoc.get("tracks", []):
                                if st["name"] in have or not st.get("notes"):
                                    continue
                                # f120 regression catch: vst3 voices in the SEED sent
                                # the compose agent down the 260-param exploration lane
                                # (2/3 hangs, 0 renders). The AGENT lane seeds a faust
                                # stand-in; MAKE keeps the true vst3 palette (proven).
                                if str((st.get("source") or {}).get("id", "")).startswith("vst3:"):
                                    st = dict(st, source={"kind": "faust", "id": "strings_disco"})
                                tiled = []
                                for rep in range(max(1, bars_total // 4)):
                                    for n in st["notes"]:
                                        if n["start"] + rep * 16.0 < bars_total * 4.0:
                                            m = dict(n); m["start"] = round(n["start"] + rep * 16.0, 4)
                                            tiled.append(m)
                                st = dict(st, notes=tiled)
                                doc["tracks"].append(st)
                                added.append(st["name"])
                            if added:
                                if not doc.get("swing") and seeddoc.get("swing"):
                                    doc["swing"] = seeddoc["swing"]
                                _awrite(prop_path, doc)
                                surgical.coarse_receipt(prop, "preseed_tracks",
                                                        fields=["meta:swing"], track_wild=added,
                                                        summary=f"{gname} DNA seeded (sidecar t=0)")
                                emit(req_id, "activity",
                                     text=f"[shape] {gname} DNA on the canvas: +{len(added)} tracks "
                                          f"({', '.join(added)}) tiled across {bars_total} bars — edit, don't start from zero")
                                # PRE-SEED L3 (f131, p50 was 237s OPEN): run the same
                                # deterministic ARRANGE rail MAKE uses — the agent
                                # receives a full genre-aware FORM (carved intros/
                                # drops/sections) in ~2s and only DIFFERENTIATES.
                                try:
                                    py2 = VENV_PY if os.path.exists(VENV_PY) else "python3"
                                    ra = run([py2, os.path.join(ROOT, "tools", "finish.py"),
                                              prop, "--out", prop, "--genre", gname],
                                             timeout=120)
                                    if ra[0] == 0:
                                        adoc = json.load(open(prop_path))
                                        surgical.coarse_receipt(prop, "preseed_arrange",
                                                                fields=["*"],
                                                                summary=f"arranged skeleton ({gname}, sidecar t=0)")
                                        emit(req_id, "activity",
                                             text=f"[shape] ARRANGED: {int(float(adoc.get('lengthBars',0)))} bars, "
                                                  f"sections {' '.join(s0.get('name','') for s0 in adoc.get('sections',[]))} "
                                                  "— differentiate and finish, the form is standing")
                                        _arr_bars = int(float(adoc.get('lengthBars', 0)))
                                        _arr_secs = ' '.join(s0.get('name','') for s0 in adoc.get('sections', []))
                                        arranged_note = (
                                            "TASTE MODE - THE TRACK IS PRODUCED (deterministic finish: form + "
                                            "harmony + transitions + mix laws + master wall are STANDING; "
                                            f"{_arr_bars} bars, sections {_arr_secs}, {len(adoc.get('tracks',[]))} seeded tracks; "
                                            "sub-90s completions happen when these rules hold):\n"
                                            "- Everything standing is DONE. Your job is TASTE: make 2-4 BOLD "
                                            "differentiating moves maximum (hook personality via surgical edits, ONE "
                                            "automation arc, a sound swap if the ask implies it) - then stop.\n"
                                            "- write_song is FORBIDDEN this run.\n"
                                            "- Self-check renders MUST use render_song max_bars=16.\n"
                                            "- Budget: <=8 tool calls, then render + finish. The skeleton is already musical; "
                                            "speed IS the deliverable.\n")
                                except Exception as _ar:
                                    emit(req_id, "activity", text=f"[shape] arrange seed skipped: {_ar}")
                    except Exception as _pt:
                        emit(req_id, "activity", text=f"[shape] track seed skipped: {_pt}")
            except Exception as _ps:
                emit(req_id, "activity", text=f"[shape] pre-seed skipped: {_ps}")
    else:
        # every conversational iteration is HISTORY: snapshot the take being revised
        # into git (Time Machine rails) before the agent reshapes it
        tdir = os.path.join(SONGS, ".takes", song_name)
        os.makedirs(tdir, exist_ok=True)
        take = os.path.join(tdir, f"{int(time.time())}_superseded.json")
        shutil.copy(prop_path, take)
        run_git(["git", "add", "--", take])
        run_git(["git", "commit", "-q", "-m",
             f"revise take on {song_name}: {str(text)[:60]}", "--only", "--", take])
    fb = last_feedback.pop(song_name, "")
    persona = persona_block(persona_name)
    fb_line = f"\nThe user REJECTED your previous proposal with feedback: \"{fb}\" — address it.\n" if fb else ""
    if revise:
        fb_line += (f"\nFEEDBACK IS NOT REJECTION: a PENDING proposal already exists at \"{prop}\" and the "
                    "user's message above is feedback ON THAT PENDING TAKE (they did NOT reject it). Revise "
                    "the proposal IN PLACE — keep its material, fix what the feedback names, never reset it "
                    "to the base.\n")
    fb_line += feedback_context_block(song_name, revise)   # reject WHY + curation law
    digest = song_digest(os.path.join(SONGS, f"{prop}.json"))
    dig_block = f"\nSONG DIGEST (live structure of \"{prop}\" — trust it):\n{digest}\n" if digest else ""
    dig_block += semantic_maps_block(digest)
    # GHOST-STREAM-FIRST (CC4 #6, firing 109): on compose-class asks the human must
    # SEE direction in seconds, not after the first minute of reads. The plan IS the
    # arrangement skeleton, so blocking it out first is musically real, not theater.
    ghost_first = ""
    if BIG_RE.search(str(text)):
        ghost_first = ("- A SHAPE MAY BE PRE-SEEDED: if the digest shows sections the user did not "
                       "write, the sidecar stamped a skeleton at t=0 — FILL INTO IT (rename/move "
                       "sections freely; they are scaffolding, not law).\n"
                       "- FIRST MOVE, before any deep reads: block out the SHAPE so the canvas "
                       "shows direction within seconds — ONE call (update_song_meta sections=[...] "
                       "for the intended form, or add_track for the first new layer). THEN read "
                       "what you need and fill. The ghost canvas streams your file writes live; "
                       "a human watching a blank canvas for a minute assumes failure.\n")
    taste_slim = ""
    if arranged_note:
        taste_slim = ("\n(TASTE RUN: the long rulebook is waived — the laws that bind: "
                      "scope receipts, locked tracks, qualifiers are hard constraints, "
                      "preview renders max_bars=16, <=8 calls. Do NOT call start_session "
                      "or get_song_summary — the SONG DIGEST above IS the truth and the "
                      "seed already encodes the genre; your first call should be an EDIT. "
                      "Act, verify, finish.)")
    # I9 (THE TEN): edit-class asks ride the SLIM rulebook — every damage-preventer
    # law verbatim, the compose-only domain tours dropped (~1/3 the bytes = faster
    # first token on the most common ask class). Compose/taste/revise keep FULL.
    slim = (os.environ.get("SOTADAW_SLIM_EDIT", "1") != "0" and not revise
            and not arranged_note and len(str(text).strip()) < 220
            and EDIT_RE.search(str(text)) and not BIG_RE.search(str(text)))
    mcp_config, extra_allow, connector_names = build_mcp_config()
    # THE CANONICAL PROMPT (pass 5): stable book -> system prompt (cached once
    # per spawn), volatile task -> the message. SOTADAW_CANON=0 = legacy shape.
    canon = os.environ.get("SOTADAW_CANON", "1") != "0"
    book, prompt = assemble_prompt(canon, slim, prop, song_name, text, fb_line,
                                   persona, ctx_block, dig_block, arranged_note,
                                   ghost_first, taste_slim, tuple(connector_names))
    env = daw_claude_env(MCP_TIMEOUT="30000", MCP_TOOL_TIMEOUT="600000")
    model, max_turns = pick_model(text)
    # EXPLICIT PROVIDER RAILS: codex:<slug> uses the machine's saved Codex login;
    # other non-Claude ids remain OpenRouter.  The namespace is intentional: a
    # raw gpt-* OpenRouter id must never silently spend Codex subscription quota.
    _or_model = (model_override or os.environ.get("SOTADAW_MODEL", "").strip()
                 or ("x-ai/grok-4.3" if re.search(r"\bgrok\b", text, re.I) else ""))
    if _or_model.startswith("openrouter:"):
        _or_model = _or_model.split(":", 1)[1]
    if provider_kind(_or_model) == "codex":
        emit(req_id, "status", text=f"CODEX RAIL: {_or_model.split(':', 1)[1]} is producing"
             + (f" at {effort} effort" if effort else ""))
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import codex_agent
        try:
            codex_start_data = open(prop_path, "rb").read()
        except OSError:
            codex_start_data = None
        codex_start_receipts = surgical.read_receipts(prop)
        _watch_stop = threading.Event()
        def _watch_codex_prop():
            pp = os.path.join(SONGS, f"{prop}.json")
            seen, last_emit = 0.0, 0.0
            while not _watch_stop.wait(0.7):
                try:
                    st = os.stat(pp)
                    if st.st_mtime <= seen or time.time() - last_emit < 1.0:
                        continue
                    data = open(pp, "rb").read()
                    json.loads(data)             # only whole snapshots reach the UI
                    gp = os.path.join(SONGS, f"{prop}.ghost.json")
                    with open(gp + ".tmp", "wb") as gh:
                        gh.write(data)
                    os.replace(gp + ".tmp", gp)
                    seen, last_emit = st.st_mtime, time.time()
                    emit(req_id, "proposal_progress", proposal=prop,
                         ghost=f"{prop}.ghost")
                except (OSError, json.JSONDecodeError):
                    continue
        _watch_thread = threading.Thread(target=_watch_codex_prop, daemon=True)
        _watch_thread.start()
        started_live = console_was_live()
        def _codex_cancel_reason():
            gone = console_gone(started_live)
            if not os.path.exists(CANCEL_FLAG) and not gone:
                return ""
            if os.path.exists(CANCEL_FLAG):
                try:
                    os.remove(CANCEL_FLAG)
                except OSError:
                    pass
            return ("console closed - run canceled (nothing runs behind a closed session)"
                    if gone else "canceled by user")
        try:
            result = codex_agent.run(
                ((book + "\n\n" + prompt) if book else prompt), _or_model,
                mcp_config=mcp_config,
                allowed_tools=",".join([DAW_ALLOW] + extra_allow),
                effort=effort,
                on_event=lambda kind, t: emit(req_id, kind, text=t),
                on_action=lambda name, args: emit_action(
                    req_id, {"name": name, "input": args}),
                cancel_check=_codex_cancel_reason,
                extra_env={"SOTADAW_IPC": IPC})
        except Exception as e:
            emit(req_id, "error", text=f"codex rail crashed: {type(e).__name__}: {e}")
            result = {"ok": False, "canceled": False, "final": ""}
        finally:
            _watch_stop.set()
            _watch_thread.join(timeout=2)
        if result.get("canceled"):
            keep_canceled_take(req_id, song_name, prop)
            return None
        prop_path = os.path.join(SONGS, f"{prop}.json")
        base_path = os.path.join(SONGS, f"{song_name}.json")
        if not result.get("ok"):
            outcome = resolve_failed_codex_take(
                req_id, prop, prop_path, base_path, prop_existed_on_entry,
                codex_start_data, codex_start_receipts)
            if outcome == "salvaged":
                chronicle.append(song_name, "note",
                                 "(Codex run ended early; substantial partial take salvaged)")
                return prop
            chronicle.append(song_name, "note", "(run failed on the Codex rail)")
            return None
        final = str(result.get("final") or "")
        if final:
            chronicle.append(song_name, "agent", final, route=_or_model)
        return prop
    if _or_model and provider_kind(_or_model) == "openrouter":
        emit(req_id, "status", text=f"OPENROUTER RAIL: {_or_model} is producing")
        try:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            import openrouter_agent
            final = openrouter_agent.run(
                ((book + "\n\n" + prompt) if book else prompt), _or_model,
                on_event=lambda kind, t: emit(req_id, kind, text=t),
                max_turns=int(max_turns))
        except Exception as e:
            emit(req_id, "error", text=f"openrouter rail crashed: {type(e).__name__}: {e}")
            final = None
        prop_path = os.path.join(SONGS, f"{prop}.json")
        base_path = os.path.join(SONGS, f"{song_name}.json")
        if final is None:
            os.path.exists(prop_path) and open(prop_path).read() == open(base_path).read() \
                and os.remove(prop_path)
            chronicle.append(song_name, "note", "(run failed on the OpenRouter rail)")
            return None
        if final:
            emit(req_id, "activity", text="agent done: " + final[:2000])
            chronicle.append(song_name, "agent", final, route=_or_model)
        return prop
    if _or_model:
        model = _or_model                       # claude-* override rides the CLI rail
        emit(req_id, "status", text=f"MODEL OVERRIDE: {model} is producing"
             + (f" at {effort} effort" if effort else ""))
    elif model != "claude-opus-4-8":
        emit(req_id, "status", text=f"routing to fast model ({model.split('-')[1]}) for this small ask")
    if claude_bin() is None:
        emit(req_id, "error", text="AGENT BLOCKED: claude CLI not found on this machine. "
             "Install: npm i -g @anthropic-ai/claude-code, then run: claude  (to log in). "
             "The MAKE button still works without it.")
        return None
    # THE RESIDENT LANE (CC4-I1): warm process answers instantly; ANY failure falls
    # through to the proven cold rail below. Same ghost watcher, same salvage laws.
    if os.environ.get("SOTADAW_RESIDENT", "1") != "0":
        # THE CONVERSATIONS LAW: a warm resident holds ONE conversation's context —
        # switching chats must never leak the other chat's turns. The claim key is
        # song~conv, so a conv switch recycles the lane exactly like a song switch.
        res_key = song_name
        try:
            _cc = chronicle.active_conv(song_name)
            if _cc != "main":
                res_key = f"{song_name}~{_cc}"
        except Exception:
            pass
        rh = RESIDENT.ask(model, prompt, mcp_config, ",".join([DAW_ALLOW] + extra_allow), res_key, effort=effort, book=book)
        if rh is not None:
            warm = "warm" if rh["n"] > 1 else "first-spin"
            emit(req_id, "status", text=f"resident agent ({model.split('-')[1]}, {warm}) working…")
            _watch_stop = threading.Event()
            def _watch_prop_r():
                pp = os.path.join(SONGS, f"{prop}.json")
                seen, last_emit = 0.0, 0.0
                while not _watch_stop.wait(0.7):
                    try:
                        st = os.stat(pp)
                    except OSError:
                        continue
                    if st.st_mtime <= seen or time.time() - last_emit < 1.0:
                        continue
                    try:
                        with open(pp, "rb") as fh:
                            data = fh.read()
                        json.loads(data)
                    except Exception:
                        continue
                    gp = os.path.join(SONGS, f"{prop}.ghost.json")
                    with open(gp + ".tmp", "wb") as gh:
                        gh.write(data)
                    os.replace(gp + ".tmp", gp)
                    seen, last_emit = st.st_mtime, time.time()
                    emit(req_id, "proposal_progress", proposal=prop, ghost=f"{prop}.ghost")
            threading.Thread(target=_watch_prop_r, daemon=True).start()
            try:
                canceled, res = stream_resident(rh, req_id, "agent", song=song_name)
            finally:
                _watch_stop.set()
            if canceled:
                keep_canceled_take(req_id, song_name, prop)
                return None
            if res is not None:
                txt = (res.get("result") or "")[:2000]
                if "session limit" in txt.lower() or "usage limit" in txt.lower():
                    emit(req_id, "error", text="Claude session limit reached — try again after reset.")
                    chronicle.append(song_name, "note", "(run died: Claude session limit)")
                    return None
                cost = res.get("total_cost_usd")
                if cost is not None:
                    emit(req_id, "activity", text=f"cost: ${cost:.3f} · {res.get('num_turns', '?')} turns")
                emit(req_id, "activity", text="agent done: " + txt)
                chronicle.append(song_name, "agent", txt, route=model)
                return prop
            emit(req_id, "activity", text="resident died mid-turn — falling back to the cold rail")
    cold_cmd = [claude_bin(), "-p", prompt, "--model", model,
                "--mcp-config", mcp_config, "--strict-mcp-config",
                "--permission-mode", "dontAsk",
                "--allowedTools", ",".join([DAW_ALLOW] + extra_allow),
                "--max-turns", max_turns, "--output-format", "stream-json", "--verbose"]
    if effort:
        cold_cmd += ["--effort", effort]        # FABLE MODE law rides the cold rail too
    if token_stream_on():
        cold_cmd.append("--include-partial-messages")   # token-level events for the pump
    if book:
        # canonical book on the cold rail: consecutive cold spawns within the
        # cache TTL share system+book+tools as one cached prefix
        cold_cmd += ["--append-system-prompt", book]
    p = subprocess.Popen(
        cold_cmd,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=ROOT, env=env)
    # GHOST STREAM (the Cursor law: the buffer shows edits AS THEY STREAM): the agent
    # mutates the _prop_ file tool-by-tool; watch it and emit proposal_progress so the
    # UI draws the diff GROWING live. Only parseable snapshots ship (mid-write JSON is
    # skipped, next tick catches it); >=1s throttle; nothing is ever applied by this.
    _watch_stop = threading.Event()
    def _watch_prop():
        pp = os.path.join(SONGS, f"{prop}.json")
        seen, last_emit = 0.0, 0.0
        while not _watch_stop.wait(0.7):
            try:
                st = os.stat(pp)
            except OSError:
                # PROP RESURRECTION (2026-07-11, run id 11): a mid-run verdict
                # consumed the prop under the composer — the agent then probed,
                # found no prop, and wrote THE BASE. Re-stage from the (freshly
                # accepted) base so the accept target always exists mid-run.
                try:
                    bsrc = os.path.join(SONGS, f"{song_name}.json")
                    if os.path.exists(bsrc):
                        shutil.copy(bsrc, pp + ".w~")
                        os.replace(pp + ".w~", pp)
                        emit(req_id, "activity",
                             text="[guard] the proposal file vanished mid-run "
                                  "(verdict consumed it) — re-staged from the base")
                except Exception:
                    pass
                continue
            if st.st_mtime <= seen or time.time() - last_emit < 1.0:
                continue
            try:
                with open(pp, "rb") as fh:
                    data = fh.read()
                json.loads(data)
            except Exception:
                continue
            # ATOMIC GHOST SNAPSHOT: the UI reads THIS file, never the live prop —
            # the live file tears mid-write exactly when the take gets big
            # (the stuck "+0/-0" bug). os.replace = never torn.
            gp = os.path.join(SONGS, f"{prop}.ghost.json")
            with open(gp + ".tmp", "wb") as gh:
                gh.write(data)
            os.replace(gp + ".tmp", gp)
            seen, last_emit = st.st_mtime, time.time()
            emit(req_id, "proposal_progress", proposal=prop, ghost=f"{prop}.ghost")
    _watch_thread = threading.Thread(target=_watch_prop, daemon=True)
    _watch_thread.start()
    canceled, res = stream_events(p, req_id, "agent", song=song_name)
    _watch_stop.set()
    _watch_thread.join(timeout=2)
    if canceled:
        keep_canceled_take(req_id, song_name, prop)
        return None
    if res is not None:
        txt = (res.get("result") or "")[:2000]
        if "session limit" in txt.lower() or "usage limit" in txt.lower():
            emit(req_id, "error", text="Claude session limit reached — try again after reset.")
            chronicle.append(song_name, "note", "(run died: Claude session limit)")
            return None
        cost = res.get("total_cost_usd")
        if cost is not None:
            emit(req_id, "activity", text=f"cost: ${cost:.3f} · {res.get('num_turns', '?')} turns")
        emit(req_id, "activity", text="agent done: " + txt)
        chronicle.append(song_name, "agent", txt, route=model)
    p.wait()
    if p.returncode != 0:
        # salvage ONLY substantial work — meta-only changes (bpm/bars/buses with no new
        # music) are the corpse of an interrupted run, never a proposal
        base_path = os.path.join(SONGS, f"{song_name}.json")
        prop_path = os.path.join(SONGS, f"{prop}.json")
        try:
            if os.path.exists(prop_path) and open(prop_path).read() != open(base_path).read():
                b, pr = json.load(open(base_path)), json.load(open(prop_path))
                notes = lambda s: sum(len(t.get("notes", [])) for t in s.get("tracks", []))
                autos = lambda s: sum(len(t.get("automation", [])) for t in s.get("tracks", []))
                if (notes(pr) - notes(b) >= 8
                        or len(pr.get("tracks", [])) > len(b.get("tracks", []))
                        or autos(pr) > autos(b)):
                    emit(req_id, "status",
                         text="agent hit its turn limit but left substantial work — salvaged")
                    chronicle.append(song_name, "note",
                                     "(run hit its turn limit; the partial take was salvaged)")
                    return prop
                os.remove(prop_path)
                emit(req_id, "error",
                     text="agent was interrupted before composing anything — discarded (nothing worth auditioning)")
                return None
        except (OSError, json.JSONDecodeError):
            pass
        emit(req_id, "error", text=f"agent exited {p.returncode}")
        return None
    return prop

# ---------------- loop lab ----------------
def mock_loops(req_id, text, song_name, bars, count):
    base = json.load(open(os.path.join(SONGS, f"{song_name}.json")))
    bpm = base.get("bpm", 140)
    names = []
    t = text.lower()
    for i in range(count):
        beats = bars * 4
        tracks = []
        if "hat" in t or "drum" in t or not any(w in t for w in ("bass", "melod", "chord", "pad")):
            notes = []
            b = 0.0
            step = [0.25, 0.5, 0.25, 0.125][i % 4]
            while b < beats:
                notes.append({"start": round(b, 3), "len": 0.1, "pitch": 42, "vel": 0.4 + 0.3 * ((int(b * 4) + i) % 3 == 0)})
                b += step
            tracks.append({"name": "hats", "source": {"kind": "faust", "id": "hat_metal"}, "gainDb": -8, "notes": notes})
        if "bass" in t or "808" in t:
            roots = [29, 32, 34, 36]
            notes = [{"start": float(j), "len": 0.9, "pitch": roots[(j + i) % 4], "vel": 0.9} for j in range(int(beats))]
            tracks.append({"name": "808", "source": {"kind": "faust", "id": "kick_808"}, "gainDb": -2, "notes": notes})
        if not tracks:
            tracks.append({"name": "perc", "source": {"kind": "faust", "id": "clap_909"}, "gainDb": -8,
                           "notes": [{"start": float(j) + 0.5 * (i % 2), "len": 0.2, "pitch": 39, "vel": 0.7} for j in range(int(beats))]})
        loop = {"version": 1, "bpm": bpm, "lengthBars": bars, "masterGainDb": -2,
                "master": [{"id": "fx_brickwall", "params": {"ceiling": -1.2}}], "tracks": tracks}
        name = f"_loop_{i+1}"
        _awrite(os.path.join(SONGS, f"{name}.json"), loop)
        names.append(name)
    return names

def slice_seed(base, seed_bars):
    """Extract the song's material inside [a,b) bars as loop-seed tracks (notes rebased to 0)."""
    a, b = float(seed_bars[0]) * 4.0, float(seed_bars[1]) * 4.0
    out = []
    for tr in base.get("tracks", []):
        notes = [{"start": round(n["start"] - a, 3), "len": n["len"],
                  "pitch": n["pitch"], "vel": n["vel"]}
                 for n in tr.get("notes", []) if a <= n["start"] < b]
        if notes:
            out.append({"name": tr["name"], "source": tr.get("source", {}), "notes": notes})
    return out

def real_loops(req_id, text, song_name, bars, count, seed=None, model=None, effort=None):
    base = json.load(open(os.path.join(SONGS, f"{song_name}.json")))
    bpm = base.get("bpm", 140)
    key = base.get("key", "")
    seed_block = ""
    if seed:
        seed_block = ("\nSEED MATERIAL (the user selected this in the arrangement — make variations "
                      "OF THIS, keep its identity recognizable):\n"
                      + json.dumps(seed)[:4000] + "\n")
    prompt = f"""You are the LOOP LAB of the DAW. The user wants {count} DIFFERENT {bars}-bar loop variations:
"{text}"{seed_block}
Context: current song is {bpm} bpm{f', key {key}' if key else ''}. Loops must be at {bpm} bpm and lengthBars={bars}.
Rules:
- Use ONLY daw MCP tools; no ToolSearch/Read/Bash. Call start_session once (loads skills), then for i in 1..{count}: write_song name "_loop_<i>" — a SMALL song (1-4 tracks, faust/sample sources per the sound-palette skill) that loops PERFECTLY (notes fill exactly {bars*4} beats, strong groove per genre skills).
- Make the {count} variations genuinely DIFFERENT (density, pattern, sound choice) — not tweaks.{' With seed material: vary rhythm/voicing/density per variation but keep the seed motif audible.' if seed else ''}
- Do NOT render; the host renders. Finish with one line summarizing the {count} vibes."""
    if provider_kind(model) == "codex":
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import codex_agent
        mcp_config = build_mcp_config()[0]
        loop_allow = ("mcp__daw__start_session,mcp__daw__get_skill,"
                      "mcp__daw__search_library,mcp__daw__write_song")
        started_live = console_was_live()
        def _loop_cancel_reason():
            gone = console_gone(started_live)
            if not os.path.exists(CANCEL_FLAG) and not gone:
                return ""
            if os.path.exists(CANCEL_FLAG):
                try:
                    os.remove(CANCEL_FLAG)
                except OSError:
                    pass
            return ("console closed - run canceled (nothing runs behind a closed session)"
                    if gone else "canceled by user")
        result = codex_agent.run(
            prompt, model, mcp_config=mcp_config, allowed_tools=loop_allow,
            effort=effort,
            on_event=lambda kind, t: emit(req_id, kind, text=t),
            on_action=lambda name, args: emit_action(
                req_id, {"name": name, "input": args}),
            cancel_check=_loop_cancel_reason,
            extra_env={"SOTADAW_IPC": IPC})
        if result.get("canceled") or not result.get("ok"):
            for i in range(count):
                for ext in (".json", ".wav"):
                    stale = os.path.join(SONGS, f"_loop_{i+1}{ext}")
                    try:
                        os.path.exists(stale) and os.remove(stale)
                    except OSError:
                        pass
            return None if result.get("canceled") else []
        if result.get("final"):
            chronicle.append(song_name, "agent", result["final"], route=model)
        return [f"_loop_{i+1}" for i in range(count)
                if os.path.exists(os.path.join(SONGS, f"_loop_{i+1}.json"))]
    if claude_bin() is None:     # same coaching as the prompt path — never a bare crash
        emit(req_id, "error", text="AGENT BLOCKED: claude CLI not found - Loop Lab needs it. "
             "Install: npm i -g @anthropic-ai/claude-code (MAKE + HUM still work without).")
        return []                     # caller iterates the result
    env = daw_claude_env(MCP_TIMEOUT="30000", MCP_TOOL_TIMEOUT="600000")
    # firing-112 policy: compose-class rides sonnet (opus read-the-world cost
    # 230s to first material) — unless a claude-* model override. OpenRouter picks
    # do not have a Loop Lab rail yet; Codex picks returned through the branch above.
    lane_model = model if (model or "").startswith("claude") else "claude-sonnet-5"
    loop_cmd = [claude_bin(), "-p", prompt, "--model", lane_model,
                "--mcp-config", build_mcp_config()[0], "--strict-mcp-config",
                "--permission-mode", "dontAsk",
                "--allowedTools", "mcp__daw__start_session,mcp__daw__get_skill,mcp__daw__search_library,mcp__daw__write_song",
                "--max-turns", "20", "--output-format", "stream-json", "--verbose"]
    if effort:
        loop_cmd += ["--effort", effort]
    if token_stream_on():
        loop_cmd.append("--include-partial-messages")   # loop-lab chat types live too
    pr = subprocess.Popen(
        loop_cmd,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=ROOT, env=env)
    stream_events(pr, req_id, "loop-lab")
    pr.wait()
    return [f"_loop_{i+1}" for i in range(count)
            if os.path.exists(os.path.join(SONGS, f"_loop_{i+1}.json"))]

def handle_loops(req):
    rid = req.get("id", 0)
    song = req.get("song", "")
    bars = int(req.get("bars", 2))
    count = max(1, min(6, int(req.get("count", 4))))
    text = req.get("text", "drum loop")
    ctx_block = selection_block(req.get("context"), os.path.join(SONGS, f"{song}.json"))
    if ctx_block:
        text += "\n" + ctx_block      # selection = context in the Loop Lab too
    pb = persona_block(req.get("persona", ""))
    if pb:
        text += "\n" + pb             # personas shape the Loop Lab too
    seed = None
    if req.get("seedBars"):
        try:
            base = json.load(open(os.path.join(SONGS, f"{song}.json")))
            seed = slice_seed(base, req["seedBars"]) or None
            if seed:
                bars = max(1, int(round(float(req["seedBars"][1]) - float(req["seedBars"][0]))))
                emit(rid, "status", text=f"loop lab: seeding from bars {req['seedBars'][0]}-{req['seedBars'][1]} ({sum(len(t['notes']) for t in seed)} notes)")
        except Exception:
            seed = None
    # clear stale loops
    for f in os.listdir(SONGS):
        if f.startswith("_loop_"):
            os.remove(os.path.join(SONGS, f))
    emit(rid, "status", text=f"loop lab: generating {count}x {bars}-bar variations…")
    chronicle.append(song, "user", "[loop lab] " + str(req.get("text", ""))[:200])
    names = (mock_loops(rid, text, song, bars, count) if MOCK
             else real_loops(rid, text, song, bars, count, seed,
                             req.get("model"), req.get("effort")))
    if names is None:                 # Stop is terminal; never publish partial loops
        emit(rid, "done", ok=False)
        return
    items = []
    for n in names:
        sj = os.path.join(SONGS, f"{n}.json")
        wav = os.path.join(SONGS, f"{n}.wav")
        rc, _, _ = run([M1, "render", sj, wav], timeout=120)
        if rc == 0:
            items.append(n)
            emit(rid, "activity", text=f"loop {n} rendered")
    if items:
        chronicle.append(song, "event",
                         f"LOOP LAB: {len(items)} variations rendered and ready")
        emit(rid, "loops", song=song, items=items)
    else:
        emit(rid, "error", text="loop lab produced nothing usable")
    emit(rid, "done", ok=bool(items))

# ---------------- first-party telemetry (SPEC S6-V34): every verdict is training signal
last_prompts = {}
last_meta = {}   # song -> {persona, model} recorded at prompt time (V37 provenance feed)
last_genres = {}   # song -> genre ask-context (ATTRIBUTION v3, 2026-07-11: 82% of
                   # verdicts landed _untagged — working songs name their genre in
                   # the ASK [genre_pref / MAKE genre], never in the accept; memo it
                   # so every telemetry row carries it and taste feeds REAL genres)
last_analysis = {}   # song -> {"t", "a"} — the proposal render's analyze2 dict (I3,
                     # THE TEN): the accept/reject verdict reuses it instead of
                     # re-running analyze2 inside the click (was ~1-3s of dead lag)

load_feedback_state()   # boot-load HERE, below every memo dict it fills (the
                        # line-86 call NameError'd on these, silently — no boot
                        # load ever ran; his 18:39 accept row proved it live)

def enforce_locks(base_json, prop_json, rid=0):
    """EDIT LOCKS (Beyond-SOTA Stage-1 threshold, the LAW as mechanism): a track with
    "locked": true is the user's ground — if a proposal touches it, that track is
    RESTORED from the base verbatim (the rest of the proposal survives). Returns the
    list of restored track names."""
    try:
        base = json.load(open(base_json))
        prop = json.load(open(prop_json))
    except Exception:
        return []
    locked = {t.get("name"): t for t in base.get("tracks", []) if t.get("locked")}
    if not locked:
        return []
    restored = []
    out_tracks = []
    prop_names = set()
    for t in prop.get("tracks", []):
        nm = t.get("name")
        prop_names.add(nm)
        if nm in locked:
            if json.dumps(t, sort_keys=True) != json.dumps(locked[nm], sort_keys=True):
                restored.append(nm)
            out_tracks.append(locked[nm])          # base verbatim, always
        else:
            out_tracks.append(t)
    for nm, t in locked.items():                   # a DELETED locked track comes back
        if nm not in prop_names:
            restored.append(nm)
            out_tracks.append(t)
    if restored:
        prop["tracks"] = out_tracks
        _awrite(prop_json, prop)
        emit(rid, "activity", text="LOCK HELD: restored " + ", ".join(f"'{n}'" for n in restored)
             + " — locked tracks are yours; the agent may not touch them")
    return restored

def stamp_provenance(song, base_json, note):
    """V37: the accepted song carries its own history — provenance:{agents,samples,lineage}.
    Written BEFORE the accept commit so git preserves every stamp even if a later
    engine-side save drops unknown keys (SongLoader round-trip = V37b on the queue)."""
    try:
        doc = json.load(open(base_json))
        prov = doc.get("provenance") or {}
        prompt = last_prompts.get(song, "")
        meta = last_meta.get(song, {})
        phash = hashlib.sha256(prompt.encode()).hexdigest()[:16] if prompt else ""
        now = time.strftime("%Y-%m-%dT%H:%M:%S")
        agents = prov.get("agents") or []
        if not agents or agents[-1].get("promptHash") != phash:
            agents.append({"model": meta.get("model", "mock" if MOCK else "claude"),
                           "persona": meta.get("persona", ""), "promptHash": phash, "at": now})
        lineage = (prov.get("lineage") or [])[-199:]
        lineage.append({"t": round(time.time(), 1), "event": "accept",
                        "prop": f"_prop_{song}", "promptHash": phash, "note": note})
        samples = []
        for t in doc.get("tracks", []):
            src = t.get("source") or {}
            if src.get("kind") == "sample" and src.get("kit"):
                samples.append({"kit": src["kit"], "license": "bundled"})
            for c in t.get("audioClips") or []:
                if c.get("file"):
                    samples.append({"path": c["file"], "license": "user-library/unverified"})
        seen, dedup = set(), []
        for s in samples:
            k = json.dumps(s, sort_keys=True)
            if k not in seen:
                seen.add(k); dedup.append(s)
        doc["provenance"] = {"agents": agents[-50:], "lineage": lineage, "samples": dedup}
        _awrite(base_json, doc)
    except Exception as e:
        emit(0, "activity", text=f"provenance stamp skipped: {e}")

# SANDBOX LAW: rigs boot the real app, the app watchdog boots a REAL sidecar,
# and IPC isolation alone does NOT contain git/telemetry side effects (the
# _ghost_e2e junk-commit + 10 poisoned telemetry rows, 2026-07-07). With
# SOTADAW_SANDBOX=1: verdicts flow, files move, but NOTHING reaches the repo's
# history or the taste data.
SANDBOX = os.environ.get("SOTADAW_SANDBOX") == "1"

GIT_LOCK = threading.Lock()   # the verdict side-lane commits beside the main lane


def run_git(cmd, timeout=900):
    if SANDBOX:
        return (0, "", "")
    with GIT_LOCK:
        return run(cmd, timeout=timeout)

def log_telemetry(song, accepted, note):
    if SANDBOX:
        return
    row = {"t": round(time.time(), 1), "song": song, "accepted": accepted, "note": note,
           "prompt": last_prompts.get(song, "")}
    if last_genres.get(song):
        row["genre"] = last_genres[song]    # ATTRIBUTION v3: explicit > text-scan
    srep = (last_meta.get(song) or {}).get("surgical")
    if srep:
        row["surgical"] = {k: srep.get(k) for k in
                           ("clean", "full_write", "note_changes", "touched_tracks")}
    try:
        # I3 (THE TEN): the proposal render already measured this take — reuse it.
        # A verdict click must never pay a fresh analyze2 subprocess (~1-3s of lag
        # between the click and 'accepted'). Cold fallback kept for stale/missing.
        cached = last_analysis.get(song)
        a = None
        if cached and time.time() - cached["t"] < 1800:
            a = cached["a"]
        else:
            wav = os.path.join(SONGS, f"_prop_{song}.wav")
            if os.path.exists(wav):
                py = VENV_PY if os.path.exists(VENV_PY) else "python3"
                rc, out, _ = run([py, os.path.join(ROOT, "tools", "analyze2.py"), wav], timeout=120)
                if rc == 0:
                    a = json.loads(out)
        if isinstance(a, dict):
            row["metrics"] = {k: a.get(k) for k in
                              ("peak_dbfs", "lufs_integrated", "clipped_samples",
                               "key_estimate", "spectral_centroid_hz")}
    except Exception:
        pass
    tdir = os.path.join(ROOT, "telemetry")
    os.makedirs(tdir, exist_ok=True)
    with open(os.path.join(tdir, "proposals.jsonl"), "a") as f:
        f.write(json.dumps(row) + "\n")
    # V35 crank: every verdict feeds the graph NOW (fire-and-forget; ingest is
    # idempotent and exits harmlessly if FalkorDB is down — taste updates itself).
    try:
        py = VENV_PY if os.path.exists(VENV_PY) else "python3"
        subprocess.Popen([py, os.path.join(ROOT, "tools", "kg_ingest_telemetry.py")],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

def log_ask(song, text, route, miss=""):
    """T1-R1 (ZPE roadmap §4.4): every typed ask -> telemetry/asks.jsonl with its
    route (parse | mock | model name). Gitignored, not uplinked — the coverage
    evidence that decides whether the parse grammar grows. `miss` (I2, THE TEN)
    carries WHY the lane declined ('no_pattern', 'gain:track_ambiguous:…',
    'lane_off', 'pending_proposal', 'revise', 'lane_error:…') — the R5 growth
    gate needs reasons, not just a route column."""
    try:
        tdir = os.path.join(ROOT, "telemetry")
        os.makedirs(tdir, exist_ok=True)
        row = {"t": round(time.time(), 1), "song": song,
               "text": str(text)[:300], "route": route}
        if miss:
            row["miss"] = str(miss)[:120]
        with open(os.path.join(tdir, "asks.jsonl"), "a") as f:
            f.write(json.dumps(row) + "\n")
    except Exception:
        pass

# ---------------- THE VERB BUS (SURFACE LAW fix 1) ----------------
def handle_verb(req):
    """Deterministic producer verbs on the ZERO-TOKEN lane — request
    {"type":"verb","verb":"intensify","args":{...},"song":...}. Same proposal
    discipline as the LLM lane (copy -> receipt -> locks -> scope law -> ghost
    diff), but the proposal event ships BEFORE the render: the diff is on the
    lanes in well under a second (kernels measured 0.04-0.06s vs the prompt
    lane's 595s median). Unknown verbs ERROR — never the silent-consume trap."""
    rid = req.get("id", 0)
    song = req.get("song", "")
    verb = str(req.get("verb", ""))
    args = req.get("args") or {}
    spec = verbs.REGISTRY.get(verb)
    if spec is None:
        emit(rid, "error", text=f"unknown verb '{verb}' — have: {', '.join(sorted(verbs.REGISTRY))}")
        emit(rid, "done", ok=False)
        return
    # the ACTION WIRE covers the zero-token lane too ("EVERY single action")
    _vfam = {"doctor": "ears", "energy_curve": "ears", "reference_match": "ears",
             "memory": "read", "prescribe": "fx", "automix": "fx",
             "color": "sound", "restyle": "sound", "finish": "song"}
    emit(rid, "action", tool=verb, family=_vfam.get(verb, "notes"),
         summary=(", ".join(f"{k} {_action_v(v)}" for k, v in list(args.items())[:3])
                  or "zero-token lane"),
         track=str(args.get("track") or ""))
    base_json = os.path.join(SONGS, f"{song}.json")
    if not os.path.exists(base_json):
        emit(rid, "error", text=f"no song {song}")
        emit(rid, "done", ok=False)
        return
    py = VENV_PY if os.path.exists(VENV_PY) else "python3"
    t0 = time.time()
    if not spec["mutates"]:
        # read-only report against the BASE song — no proposal, no copy
        try:
            tail = spec["cli"](song, args)
        except (KeyError, TypeError, ValueError) as e:
            emit(rid, "error", text=f"{verb}: bad args {json.dumps(args)[:120]} ({e})")
            emit(rid, "done", ok=False)
            return
        rc, out, err = run([py, os.path.join(ROOT, "tools", spec["tool"])] + tail,
                           timeout=spec["timeout"])
        if rc != 0:
            emit(rid, "error", text=f"{verb}: {(out + err)[-400:]}")
            emit(rid, "done", ok=False)
            return
        # human report only — machine tails (DOCTOR_JSON etc.) stay off the chat
        human = "\n".join(l for l in out.strip().splitlines()
                          if not re.match(r"[A-Z_]+_JSON ", l))
        emit(rid, "verb_report", verb=verb, song=song, text=human[-4000:],
             ms=int((time.time() - t0) * 1000))
        chronicle.append(song, "agent",
                         f"[{verb}] " + (human.strip().splitlines()[0] if human.strip()
                                         else "report delivered"), route="verb")
        emit(rid, "done", ok=True)
        return
    prop = f"_prop_{song}"
    prop_json = os.path.join(SONGS, f"{prop}.json")
    corpse_court(rid, song)             # a broken pending prop must not block verbs forever
    if os.path.exists(prop_json):
        emit(rid, "error", text="a proposal is already pending — Accept/Reject it first")
        emit(rid, "done", ok=False)
        return
    shutil.copy(base_json, prop_json)
    pw = os.path.join(SONGS, f"{prop}.wav")
    os.path.exists(pw) and os.remove(pw)          # no lying waveform (the previewHistory law)
    surgical.clear_receipts(prop)                 # fresh prop = fresh ledger (THIS song only)
    try:
        tail = spec["cli"](prop, args)
    except (KeyError, TypeError, ValueError) as e:
        os.remove(prop_json)
        emit(rid, "error", text=f"{verb}: bad args {json.dumps(args)[:120]} ({e})")
        emit(rid, "done", ok=False)
        return
    rc, out, err = run([py, os.path.join(ROOT, "tools", spec["tool"])] + tail,
                       timeout=spec["timeout"])
    if rc != 0:
        os.path.exists(prop_json) and os.remove(prop_json)
        emit(rid, "error", text=f"{verb}: {(out + err)[-400:]}")
        emit(rid, "done", ok=False)
        return
    try:
        tnames = [t.get("name") for t in json.load(open(base_json)).get("tracks", [])]
        rcpt = spec["receipt"](args, tnames, out)
        surgical.coarse_receipt(prop, verb, fields=rcpt.get("fields"),
                                track_wild=rcpt.get("track_wild"),
                                summary=f"verb bus: {verb}")
    except Exception:
        pass
    enforce_locks(base_json, prop_json, rid)
    try:   # a verb no-op is HONEST (already satisfied) — not the LLM lane's empty-diff failure
        if json.load(open(base_json)) == json.load(open(prop_json)):
            os.remove(prop_json)
            emit(rid, "activity", text=f"[{verb}] no changes needed — the song already satisfies it")
            emit(rid, "done", ok=True)
            return
    except Exception:
        pass
    srep = scope_check(rid, base_json, prop_json, song)
    last_prompts[song] = f"[verb] {verb} {json.dumps(args, sort_keys=True)[:100]}"
    last_meta[song] = {"persona": "", "model": "verb-bus", "surgical": srep}
    # INSTANT DIFF: the proposal event ships NOW — the UI shows the ghost diff and
    # auditions the JSON live; the wav/meters land when the render below finishes.
    emit(rid, "proposal", song=song, proposal=prop, surgical=srep or {},
         verb=verb, ms=int((time.time() - t0) * 1000))
    chronicle.append(song, "agent",
                     f"[{verb}] " + (out.strip().splitlines()[0] if out.strip()
                                     else "take on the lanes"), route="verb")
    if out.strip():
        emit(rid, "activity", text=f"[{verb}] " + out.strip().splitlines()[0][:300])
    a = render_and_analyze(rid, prop, "proposal")
    a0 = a
    a = clip_wall(rid, prop, a)    # wall FIRST (ledger 2026-07-12: recovery lifts
    a2 = loudness_recovery(rid, prop, a,   # only CLEAN takes — the inverted order
                           resolve_take_genre(prop, song))   # shipped clipped takes under-loud
    if a2 is not a0:               # wall or lift edited the doc; the lanes see the
        try:                       # walled master via a progress refresh
            gp = prop_json.replace(".json", ".ghost.json")
            shutil.copy(prop_json, gp)
            emit(rid, "proposal_progress", proposal=prop, ghost=f"{prop}.ghost")
        except Exception:
            pass
    emit(rid, "done", ok=True)

# ---------------- request handling ----------------
def handle(req):
    rid = req.get("id", 0)
    rtype = req.get("type")
    song = req.get("song", "")
    _EMIT_CTX.song = song      # every emit in this request carries its song (scoping law)
    base_json = os.path.join(SONGS, f"{song}.json")
    prop = f"_prop_{song}"
    prop_json = os.path.join(SONGS, f"{prop}.json")

    if rtype == "loops":
        handle_loops(req)
        return

    if rtype == "verb":
        # the UI gesture IS the ask — chronicle it (parse-lane verbs already
        # chronicled their typed ask on the prompt path)
        chronicle.append(song, "user",
                         f"[{req.get('verb', '?')}] "
                         + json.dumps(req.get("args") or {}, sort_keys=True)[:160])
        handle_verb(req)     # THE VERB BUS: zero-token producer verbs, instant diff
        return

    if rtype == "audio_to_midi":
        # THE DOCK LAW (Chezy live, 2026-07-05): MAKE with an AUDIO track selected =
        # the OPPOSITE of HUM — turn the selected stem into editable MIDI, zero
        # tokens (basic-pitch), landing as a normal proposal ("<track>_midi").
        if not os.path.exists(base_json):
            emit(rid, "error", text=f"no song {song}")
            return
        want = str(req.get("track", "")).strip()
        doc = json.load(open(base_json))
        tr = next((t for t in doc.get("tracks", []) if t.get("name") == want), None)
        clips = (tr or {}).get("audioClips") or []
        if tr is None or not clips:
            emit(rid, "error", text=f"'{want}' has no audio to transcribe — select an audio stem track")
            emit(rid, "done", ok=False)
            return
        wavp = clips[0].get("file", "")
        if not os.path.isabs(wavp):
            wavp = os.path.join(ROOT, wavp)
        mode = str(req.get("mode", "notes"))
        if mode in ("spectral", "lossless"):
            # SPECTRAL CAPTURE on the zero-token lane: the stem becomes
            # reconstruction MIDI (tools/spectral.py) with LIVE progress —
            # [prog] json lines stream up as status events while it runs.
            emit(rid, "status", text=f"spectral capture of '{want}' ({mode}) starting…")
            shutil.copy(base_json, prop_json)
            surgical.clear_receipts(prop)   # fresh prop = fresh ledger (THIS song only)
            py = VENV_PY if os.path.exists(VENV_PY) else "python3"
            cname = re.sub(r"[^a-z0-9_]", "", f"{song}_{want}".lower())
            cmd = [py, os.path.join(ROOT, "tools", "spectral.py"), "capture", wavp,
                   "--name", cname, "--mode", mode,
                   "--bpm", str(doc.get("bpm", 120) or 120), "--into", prop_json]
            pr = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT, text=True)
            last_emit, tail = 0.0, []
            for line in pr.stdout:
                line = line.rstrip()
                tail = (tail + [line])[-8:]
                if line.startswith("[prog] "):
                    try:
                        j = json.loads(line[7:])
                        now = time.time()
                        if now - last_emit >= 1.0 or j.get("pct", 0) >= 99.9:
                            last_emit = now
                            eta = j.get("eta_s", -1)
                            emit(rid, "progress", pct=round(float(j.get("pct", 0)), 1),
                                 text=(f"{j.get('stage', '')}: {j.get('msg', '')}"
                                       + (f" (~{eta:.0f}s left)"
                                          if eta and eta > 0 else "")))
                    except (ValueError, KeyError):
                        pass
            pr.wait()
            if pr.returncode != 0:
                emit(rid, "error",
                     text="spectral capture failed: " + " / ".join(tail[-3:]))
                emit(rid, "done", ok=False)
                return
            emit(rid, "activity", text="[make] " + next(
                (l for l in reversed(tail) if l.startswith("[spectral] capture")),
                "spectral capture done"))
            chronicle.append(song, "event",
                             f"SPECTRAL CAPTURE: '{want}' became reconstruction MIDI lanes")
            try:   # receipt the landing — a later REVISE re-scopes the whole prop
                _bn = {t.get("name") for t in json.load(open(base_json)).get("tracks", [])}
                _new = [t.get("name") for t in json.load(open(prop_json)).get("tracks", [])
                        if t.get("name") not in _bn]
                surgical.coarse_receipt(prop, "spectral_capture",
                                        fields=["meta:lengthBars"], track_wild=_new,
                                        summary=f"spectral capture of '{want}' -> {len(_new)} lanes")
            except Exception:
                pass
            emit(rid, "proposal", song=song, proposal=prop)
            a = render_and_analyze(rid, prop, "proposal")
            a0 = a
            a = clip_wall(rid, prop, a)   # wall first — recovery lifts CLEAN takes
            a2 = loudness_recovery(rid, prop, a, resolve_take_genre(prop, song))
            if a2 is not a0:
                try:                   # event shipped pre-render: refresh lanes
                    shutil.copy(prop_json, prop_json.replace(".json", ".ghost.json"))
                    emit(rid, "proposal_progress", proposal=prop, ghost=f"{prop}.ghost")
                except Exception:
                    pass
            emit(rid, "done", ok=True)
            return
        emit(rid, "status", text=f"transcribing '{want}' to MIDI (basic-pitch, zero tokens)…")
        try:
            # basic_pitch lives in the VENV — the daemon may run under system
            # python (Chezy hit ModuleNotFoundError LIVE, 2026-07-11). Run the
            # transcription as a venv subprocess like every other heavy rail;
            # in-process only when the venv is absent (Inspiron law).
            if os.path.exists(VENV_PY):
                _tr = subprocess.run(
                    [VENV_PY, "-c",
                     "import json,sys; sys.path.insert(0, sys.argv[3]); "
                     "from stems_import import transcribe; "
                     "print(json.dumps(transcribe(sys.argv[1], float(sys.argv[2]))))",
                     wavp, str(float(doc.get("bpm", 120) or 120)),
                     os.path.join(ROOT, "tools")],
                    capture_output=True, text=True, timeout=900)
                if _tr.returncode != 0:
                    raise RuntimeError((_tr.stderr or "").strip().splitlines()[-1]
                                       if (_tr.stderr or "").strip() else "venv transcribe failed")
                notes = json.loads(_tr.stdout.strip().splitlines()[-1])
            else:
                sys.path.insert(0, os.path.join(ROOT, "tools"))
                from stems_import import transcribe
                notes = transcribe(wavp, float(doc.get("bpm", 120) or 120))
        except Exception as e:
            emit(rid, "error", text=f"transcription failed: {type(e).__name__}: {e}")
            emit(rid, "done", ok=False)
            return
        if not notes:
            emit(rid, "error", text=f"basic-pitch heard no clean notes in '{want}' — "
                 "dense/percussive stems transcribe poorly; try chop_sample via the agent instead")
            emit(rid, "done", ok=False)
            return
        # KEY-SNAP (f127, the hum law): raw transcription is rarely IN KEY — a hummed
        # or bled melody lands between scale tones. Snap each pitch to the nearest
        # tone of the song's key (octave-preserving); the raw pitch survives in
        # "rawPitch" so nothing is destroyed. Off unless the song declares a key.
        key = str(doc.get("key") or "").strip()
        if key and req.get("snap", True):
            try:
                sys.path.insert(0, os.path.join(ROOT, "tools"))
                from loop_gen import key_to_pcs
                _, pcs = key_to_pcs(key)
                snapped = 0
                for n in notes:
                    pc = n["pitch"] % 12
                    if pc not in pcs:
                        best = min(pcs, key=lambda q: min((q - pc) % 12, (pc - q) % 12))
                        delta = ((best - pc + 6) % 12) - 6
                        n["rawPitch"] = n["pitch"]
                        n["pitch"] = n["pitch"] + delta
                        snapped += 1
                if snapped:
                    emit(rid, "activity",
                         text=f"[make] key-snap: {snapped}/{len(notes)} notes pulled into {key} "
                              "(rawPitch kept on each)")
            except Exception as _ks:
                emit(rid, "activity", text=f"[make] key-snap skipped: {_ks}")
        shutil.copy(base_json, prop_json)
        surgical.clear_receipts(prop)   # fresh prop = fresh ledger (THIS song only)
        pdoc = json.load(open(prop_json))
        low = want.lower()
        voice = "sub_clean" if "bass" in low else "piano"
        pdoc["tracks"].append({"name": f"{want}_midi", "source": {"kind": "faust", "id": voice},
                               "gainDb": -8.0, "notes": notes})
        _awrite(prop_json, pdoc)
        surgical.coarse_receipt(prop, "audio_to_midi", fields=[],
                                track_wild=[f"{want}_midi"],
                                summary=f"'{want}' transcribed to {len(notes)} notes")
        emit(rid, "activity", text=f"[make] '{want}' -> {len(notes)} editable notes on '{want}_midi' "
             "(mute the audio stem to A/B them)")
        chronicle.append(song, "event",
                         f"AUDIO->MIDI: '{want}' -> {len(notes)} editable notes on '{want}_midi'")
        emit(rid, "proposal", song=song, proposal=prop)
        a = render_and_analyze(rid, prop, "proposal")
        a0 = a
        a = clip_wall(rid, prop, a)    # wall first (sketch + audio stem doubled =
        a2 = loudness_recovery(rid, prop, a,   # clip risk); recovery lifts CLEAN takes
                               resolve_take_genre(prop, song))
        if a2 is not a0:
            try:                       # event shipped pre-render: refresh the lanes
                shutil.copy(prop_json, prop_json.replace(".json", ".ghost.json"))
                emit(rid, "proposal_progress", proposal=prop, ghost=f"{prop}.ghost")
            except Exception:
                pass
        emit(rid, "done", ok=True)
        return

    if rtype == "hum_topline":
        # ZERO-TOKEN wordless vocal: hum() sings every note of the melody track,
        # lands as a normal PROPOSAL (vocals track + lyrics[] in the copy).
        if not os.path.exists(base_json):
            emit(rid, "error", text=f"no song {song}")
            return
        shutil.copy(base_json, os.path.join(SONGS, f"{prop}.json"))
        doc = json.load(open(os.path.join(SONGS, f"{prop}.json")))
        want = str(req.get("track", "")).strip()
        tr = next((t for t in doc.get("tracks", []) if t.get("name") == want), None)
        if tr is None:
            tr = next((t for t in doc.get("tracks", [])
                       if t.get("name") in ("lead", "melody", "hook") and t.get("notes")), None)
        if tr is None:
            # a hummable lead is MELODIC, not a drone: >=8 notes and mean len < 2
            # beats (4 whole-note pads were winning this and getting hummed - f158)
            def _melodic(t):
                ns = t.get("notes") or []
                return (len(ns) >= 8 and sum(n.get("len", 1) for n in ns) / len(ns) < 2.0
                        and t.get("source", {}).get("kind") != "audio"
                        and not any(w in t.get("name", "").lower() for w in
                                    ("kick", "snare", "hat", "clap", "perc", "808", "bass", "ride", "ghost", "pad")))
            tr = max((t for t in doc.get("tracks", []) if _melodic(t)),
                     key=lambda t: len(t.get("notes", [])), default=None)
        if tr is None:
            # NO LEAD? WRITE ONE (f158): the topline kernel (hook/lift/talk/space
            # laws, battery 6/6) generates a section-aware melody on the prop —
            # then we sing THAT. Zero tokens. Kernel-empty still errors (+scrap).
            py0 = VENV_PY if os.path.exists(VENV_PY) else sys.executable
            rt = subprocess.run([py0, os.path.join(ROOT, "tools", "topline.py"),
                                 prop, "--write", "--seed", str(int(time.time()) % 9973)],
                                capture_output=True, text=True, timeout=120)
            doc = json.load(open(os.path.join(SONGS, f"{prop}.json")))
            tr = next((t for t in doc.get("tracks", []) if t.get("name") == "topline"
                       and t.get("notes")), None)
            if tr is not None:
                surgical.coarse_receipt(prop, "topline", fields=[],
                                        track_wild=["topline"],
                                        summary="topline kernel (hum had no lead)")
                emit(rid, "activity",
                     text=f"[hum] no lead found — wrote a section-aware topline "
                          f"({len(tr['notes'])} notes, hook law) and singing THAT")
        if tr is None:
            os.path.exists(os.path.join(SONGS, f"{prop}.json")) and os.remove(os.path.join(SONGS, f"{prop}.json"))
            emit(rid, "error", text="no melody track to hum — and the topline kernel came up empty on this song")
            emit(rid, "done", ok=False)
            return
        syl = re.sub(r"[^a-z]", "", str(req.get("syllable", "laa"))) or "laa"
        emit(rid, "status", text=f"humming '{syl}' over {tr['name']} ({len(tr.get('notes', []))} notes) — zero tokens…")
        py = VENV_PY if os.path.exists(VENV_PY) else sys.executable
        r1 = subprocess.run([py, os.path.join(ROOT, "tools", "sing.py"), "hum", prop, tr["name"], syl],
                            capture_output=True, text=True, timeout=600)
        if (r1.returncode != 0 or "[hum]" not in (r1.stdout + r1.stderr)) \
                and "Traceback" not in (r1.stdout + r1.stderr):
            # GPU-init hiccup class (warning-only failures): one retry, then CPU lane
            emit(rid, "activity", text=f"[hum] first sing attempt came back empty (rc={r1.returncode}) — retrying on the CPU lane")
            env2 = dict(os.environ, SOTADAW_SING_CPU="1")
            r1 = subprocess.run([py, os.path.join(ROOT, "tools", "sing.py"), "hum", prop, tr["name"], syl],
                                capture_output=True, text=True, timeout=900, env=env2)
        if r1.returncode != 0 or "[hum]" not in (r1.stdout + r1.stderr):
            _out = (r1.stdout + r1.stderr).strip()
            os.path.exists(os.path.join(SONGS, f"{prop}.json")) and os.remove(os.path.join(SONGS, f"{prop}.json"))
            emit(rid, "error", text="hum: " + (_out if len(_out) <= 400 else _out[-400:]))
            emit(rid, "done", ok=False)
            return
        emit(rid, "activity", text=[l for l in r1.stdout.splitlines() if l.strip()][-1][:160])
        a = render_and_analyze(rid, prop, "proposal")
        a = clip_wall(rid, prop, a)    # the hum lane obeys the wall law too —
        a = loudness_recovery(rid, prop, a,          # and walls FIRST, so recovery
                              resolve_take_genre(prop, song))   # lifts a CLEAN take
        if a:
            chronicle.append(song, "event",
                             f"HUM: wordless '{syl}' vocal over {tr['name']} landed as a take")
            emit(rid, "proposal", song=song, proposal=prop)
        else:   # ORPHAN LAW: no proposal event -> no invisible pending
            os.path.exists(os.path.join(SONGS, f"{prop}.json")) and os.remove(os.path.join(SONGS, f"{prop}.json"))
        emit(rid, "done", ok=True)
        return

    if rtype == "make_track":
        # ZERO-TOKEN one-button track: deterministic loop_gen -> arrange lands as a
        # normal PROPOSAL over the open song (Audition/Accept just work).
        if not os.path.exists(base_json):
            emit(rid, "error", text=f"no song {song}")
            return
        genre = re.sub(r"[^a-z0-9_]", "", str(req.get("genre", "house")).lower())
        last_genres[song] = genre           # ATTRIBUTION v3: the verdict knows its genre
        seed = int(req.get("seed", 0))
        emit(rid, "status", text=f"making a {genre} track (seed {seed}) — no tokens, all DNA…")
        py = VENV_PY if os.path.exists(VENV_PY) else sys.executable
        tmp = f"_mt_{song}"
        r1 = subprocess.run([py, os.path.join(ROOT, "tools", "loop_gen.py"), genre, tmp,
                             "--bars", "4", "--seed", str(seed)], capture_output=True, text=True)
        if r1.returncode != 0:
            emit(rid, "error", text=("loop_gen: " + (r1.stdout + r1.stderr).strip()[-200:]))
            emit(rid, "done", ok=False)
            return
        emit(rid, "activity", text=r1.stdout.strip().splitlines()[-1][:160])
        r2 = subprocess.run([py, os.path.join(ROOT, "tools", "arrange.py"),
                             os.path.join(SONGS, f"{tmp}.json"), "--out", prop, "--genre", genre,
                             "--seed", str(seed)],   # wave 43: pop forms vary per take
                            capture_output=True, text=True)
        try:
            os.remove(os.path.join(SONGS, f"{tmp}.json"))
        except OSError:
            pass
        if r2.returncode != 0:
            emit(rid, "error", text=("arrange: " + (r2.stdout + r2.stderr).strip()[-200:]))
            emit(rid, "done", ok=False)
            return
        emit(rid, "activity", text=r2.stdout.strip().splitlines()[0][:160])
        # W104 MAKE SINGS -> W130 MAKE SINGS WORDS (measured 2026-07-11:
        # arr+WORDS 0.5899/80.3 beats arr+hum 0.5741/78.1, the board's crown;
        # the loop-level ladder agreed earlier) — vocals:true sings REAL
        # seeded words over the arranged lead, still zero tokens. Fail-open
        # LADDER: words -> hum -> instrumental unchanged.
        if req.get("vocals"):
            _sung, rv = False, None
            try:
                _tp = os.path.join(ROOT, "tools")
                _tp not in sys.path and sys.path.insert(0, _tp)
                import lyric_bank
                _pj = os.path.join(SONGS, f"{prop}.json")
                _d = json.load(open(_pj))
                _lead = next((t for t in _d.get("tracks", [])
                              if t.get("name") == "lead" and t.get("notes")), None)
                _ly = lyric_bank.lyrics_for(genre, (_lead or {}).get("notes"), seed)
                if _ly:
                    _d["lyrics"] = _ly
                    _awrite(_pj, _d)
                    _first = " ".join(w["text"] for w in _ly[:5])
                    emit(rid, "status", text=f"singing real words over the lead "
                         f"('{_first}…') — still zero tokens…")
                    rv = subprocess.run([py, os.path.join(ROOT, "tools", "sing.py"),
                                         "render", prop, "lead", "standard"],
                                        capture_output=True, text=True, timeout=1200)
                    if rv.returncode == 0:
                        _sung = True
                        _tail = (rv.stdout.strip().splitlines() or ["sung"])[-1]
                        emit(rid, "activity", text=_tail[:160])
                        chronicle.append(song, "event",
                                         f"MAKE SINGS WORDS: '{_first}…' on the {genre} "
                                         "take (voice: Gahata Meiji from LUNAI Project)")
            except Exception:
                pass
            if not _sung:
                _syl = {"gospel": "oh", "soul": "oh", "rnb": "oh", "motown": "oh",
                        "doo_wop": "oh", "lofi": "mmm", "triphop": "mmm",
                        "house": "ey", "techno": "ey", "gqom": "ah",
                        "amapiano": "ah"}.get(genre, "ooh")
                emit(rid, "status", text=f"singing '{_syl}' over the lead — still zero tokens…")
                rv = subprocess.run([py, os.path.join(ROOT, "tools", "sing.py"),
                                     "hum", prop, "lead", _syl],
                                    capture_output=True, text=True, timeout=1200)
                if rv.returncode == 0:
                    _tail = (rv.stdout.strip().splitlines() or ["sung"])[-1]
                    emit(rid, "activity", text=_tail[:160])
                    chronicle.append(song, "event",
                                     f"MAKE SINGS: '{_syl}' topline on the {genre} take "
                                     "(voice: Gahata Meiji from LUNAI Project)")
                else:
                    emit(rid, "activity",
                         text=("voice skipped: " + (rv.stdout + rv.stderr).strip()[-120:]))
        a = render_and_analyze(rid, prop, "proposal")
        a = clip_wall(rid, prop, a)            # clip first; loudness only lifts CLEAN takes
        a = loudness_recovery(rid, prop, a, genre)   # W116: the universal pass
        # EARS ON MAKE (W7): band truth vs the genre target rides the take's
        # activity feed — silent when clean, fail-open (never kills the MAKE)
        try:
            tp = os.path.join(ROOT, "tools")
            if tp not in sys.path:
                sys.path.insert(0, tp)
            import doctor as _doc
            dna = json.load(open(os.path.join(ROOT, "agent", "dna_cache.json"))
                            )["genres"].get(genre, {})
            for line in _doc.band_verdict(a if isinstance(a, dict) else {}, dna):
                emit(rid, "activity", text=("EARS: " + line)[:200])
        except Exception:
            pass
        if a:
            chronicle.append(song, "event",
                             f"MAKE: a {genre} track (seed {seed}) landed as a take")
            emit(rid, "proposal", song=song, proposal=prop)
        emit(rid, "done", ok=True)
        return

    if rtype == "prompt":
        if not os.path.exists(base_json):
            emit(rid, "error", text=f"no song {song}")
            return
        explicit_model = str(req.get("model") or "").strip()
        routed_model = routed_model_for(req.get("text", ""), explicit_model, MOCK)
        last_prompts[song] = req.get("text", "")
        if str(req.get("genre_pref", "")).strip():
            last_genres[song] = str(req["genre_pref"]).strip().lower()
        last_meta[song] = {"persona": req.get("persona", ""),
                           "model": routed_model}
        # selection = context: enrich the UI's selection addresses from song.json,
        # inject into the prompt AND persist for the get_selection MCP tool.
        ctx_block = (selection_block(req.get("context"), base_json)
                     + transport_block(req.get("context"), base_json)
                     + recent_edits_block(song))
        if os.path.isdir(os.path.join(SONGS, song + "_stems")):
            # IMPORT AWARENESS: route the agent to the import-mix journey + the
            # banked Reference DNA ("like the original" is a tool call, not a vibe)
            ctx_block += ("\nIMPORTED RECORD: this song came from stems_import (stems + "
                          "sketch lanes). get_skill(\"import-mix\") BEFORE mix/fx work; "
                          "use_tool(match_reference, {\"song\": \"" + song + "\", "
                          "\"reference\": \"" + song + "\"}) reports per-band gaps vs the "
                          "ORIGINAL record (its DNA was banked at import).\n")
        # W101 VOICE AWARENESS (the vocal ctx law, mirroring import-mix)
        ctx_block += voice_ctx_block(req.get("text", ""))
        try:   # T2-S3 RECALL: the project's established facts ride EVERY prompt
            _rec = session_memory.recall_block(song)
            if _rec:
                ctx_block += "\n" + _rec
        except Exception:
            pass
        try:   # THE CHRONICLE: the project's prior CONVERSATION rides every prompt
            #  (built BEFORE this ask's own row lands — the ask is THE TASK, not memory)
            _conv = chronicle.conversation_block(song)
            if _conv:
                ctx_block += "\n" + _conv
        except Exception:
            pass
        chronicle.append(song, "user", req.get("text", ""),
                         revise=bool(req.get("revise")))
        try:
            json.dump({"song": song, "selections": (req.get("context") or {}).get("selections", []),
                       "transport": (req.get("context") or {}).get("transport"),
                       "rendered": ctx_block},
                      open(os.path.join(IPC, "context.json"), "w"), indent=1)
        except Exception:
            pass
        gp = str(req.get("genre_pref", "")).strip()
        if gp:   # THE DOCK LAW: the genre box is a standing USER PREFERENCE, not a command
            ctx_block += (f"\nUSER GENRE PREFERENCE: {gp} — when the ask leaves style open, "
                          "lean this way (sounds, groove, mix targets). An explicit style in "
                          "the ask always wins.\n")
        if ctx_block:
            emit(rid, "activity", text="[ctx] " + ctx_block.strip().splitlines()[1][:120])
        try:   # locked tracks enter the prompt as LAW (saves wasted agent work)
            _locked = [t.get("name") for t in json.load(open(base_json)).get("tracks", [])
                       if t.get("locked")]
            if _locked:
                ctx_block += ("\nLOCKED TRACKS (LAW — do not modify, the sidecar reverts any "
                              "change): " + ", ".join(_locked) + "\n")
        except Exception:
            pass
        # THE PARSE LANE (T1-R3, ZPE_TRANSFER_ROADMAP §4): compile the typed ask
        # into the exact kernels BEFORE any model — zero tokens, instant proposal.
        # Precision-first: any doubt = honest miss, and the cloud rail below runs
        # byte-identically. Pending proposals / revises stay on the LLM rail
        # (that's where conversation lives). SOTADAW_PARSE=0 kills the lane.
        plan = None
        parse_miss = parse_lane_skip_reason(
            explicit_model, bool(req.get("revise")),
            os.path.exists(os.path.join(SONGS, f"_prop_{song}.json")),
            os.environ.get("SOTADAW_PARSE", "1") != "0")
        if not parse_miss:
            try:
                plan, parse_miss = parse_lane.compile_debug(
                    req.get("text", ""),
                    json.load(open(base_json)),
                    req.get("context"),
                    facts=session_memory.alias_facts(song),
                    history=session_memory.history(song))
            except Exception as _pe:
                plan, parse_miss = None, f"lane_error:{_pe}"
                emit(rid, "activity", text=f"[parse] lane error ({_pe}) — cloud rail takes it")
        log_ask(song, req.get("text", ""),
                "parse" if plan else routed_model,
                miss="" if plan else parse_miss)
        if plan is not None and plan.get("verb"):
            act = next(a for a in plan["actions"] if a["kind"] == "verb")
            emit(rid, "activity",
                 text=f"[parse] {plan['summary']} ({plan['ms']}ms) — verb bus takes it")
            handle_verb({"id": rid, "song": song, "verb": act["verb"], "args": act["args"]})
            if plan.get("resolutions"):    # an accept will CONFIRM these (T2-S2)
                last_meta.setdefault(song, {})["parse_resolutions"] = plan["resolutions"]
            try:   # S4: a shipped EDIT plan is the retarget grammar's raw material
                if act["verb"] != "memory" and \
                        os.path.exists(os.path.join(SONGS, f"_prop_{song}.json")):
                    session_memory.write_fact(
                        song, "_session", "last_plan",
                        {"ask": req.get("text", ""), "pattern": plan.get("pattern"),
                         "summary": plan.get("summary"), "actions": plan.get("actions"),
                         "track": parse_lane.primary_track(plan)},
                        prov="parse hit (verb)")
            except Exception:
                pass
            return
        if plan is not None:
            prop = f"_prop_{song}"
            prop_json = os.path.join(SONGS, f"{prop}.json")
            _t0p = time.time()
            try:
                shutil.copy(base_json, prop_json)
                pw = os.path.join(SONGS, f"{prop}.wav")
                os.path.exists(pw) and os.remove(pw)   # no lying waveform
                surgical.clear_receipts(prop)   # fresh prop = fresh ledger (THIS song only)
                pdoc = json.load(open(prop_json))
                parse_lane.apply_plan(pdoc, plan, song_name=prop)
                _awrite(prop_json, pdoc)
                # the ACTION WIRE covers the parse lane too (5.5ms edits stream)
                try:
                    emit(rid, "action", tool="parse", family="notes",
                         summary=str(plan.get("summary", ""))[:180],
                         track=str(parse_lane.primary_track(plan) or ""))
                except Exception:
                    pass
                emit(rid, "activity",
                     text=f"[parse] {plan['summary']} ({plan['ms']}ms compile)")
                chronicle.append(song, "agent", f"[instant edit] {plan['summary']}",
                                 route="parse")
                last_meta[song] = {"persona": req.get("persona", ""),
                                   "model": "parse-lane",
                                   "parse_resolutions": plan.get("resolutions") or {}}
                enforce_locks(base_json, prop_json, rid)
                if json.load(open(base_json)) == json.load(open(prop_json)):
                    os.remove(prop_json)   # locks may have reverted the whole edit
                    emit(rid, "error", text="[parse] the edit dissolved (locked "
                                            "tracks?) — say it in words instead")
                    emit(rid, "done", ok=False)
                    return
                srep = scope_check(rid, base_json, prop_json, song)
                last_meta.setdefault(song, {})["surgical"] = srep
                # INSTANT DIFF (verb-bus law): the proposal event ships NOW; the
                # wav/meters land when the render below finishes.
                emit(rid, "proposal", song=song, proposal=prop, surgical=srep or {},
                     parsed=True, resolutions=plan.get("resolutions") or {},
                     ms=int((time.time() - _t0p) * 1000))
                try:   # S4: the last EDIT plan is itself a deterministic fact
                    session_memory.write_fact(
                        song, "_session", "last_plan",
                        {"ask": req.get("text", ""), "pattern": plan.get("pattern"),
                         "summary": plan.get("summary"), "actions": plan.get("actions"),
                         "track": parse_lane.primary_track(plan)},
                        prov="parse hit")
                except Exception:
                    pass
                a = render_and_analyze(rid, prop, "proposal")
                a2 = clip_wall(rid, prop, a)   # the parse lane obeys the wall law too
                if a2 is not a:
                    try:               # event shipped pre-render: refresh the lanes
                        shutil.copy(prop_json, prop_json.replace(".json", ".ghost.json"))
                        emit(rid, "proposal_progress", proposal=prop, ghost=f"{prop}.ghost")
                    except Exception:
                        pass
                emit(rid, "done", ok=True)
                return
            except Exception as _pex:
                try:   # the lane never blocks an ask: scrub, then cloud rail
                    os.path.exists(prop_json) and os.remove(prop_json)
                except Exception:
                    pass
                emit(rid, "activity",
                     text=f"[parse] execute failed ({_pex}) — cloud rail takes it")
        emit(rid, "status", text=("mock" if MOCK else "agent") + " working…")
        # THE PROPOSAL-LIFETIME LAW (2026-07-11, the rhodes_aurora/sunrise/
        # vocals_peak false flags): a revise/pending ask re-enters an existing
        # proposal that CARRIES prior runs' receipted edits — clearing here made
        # every earlier edit read as unreceipted on the next scope check. The
        # ledger lives as long as the prop FILE (flag-independent: pending props
        # ride the LLM rail with or without revise), and clears touch only THIS
        # song's lines (a fresh ask on song B must not orphan song A's ledger).
        corpse_court(rid, song)         # a broken pending prop never poisons the run
        if not os.path.exists(os.path.join(SONGS, f"_prop_{song}.json")):
            surgical.clear_receipts(f"_prop_{song}")
        t_ask = time.time()
        # THE PROP FENCE (2026-07-11, run 9 live: the agent passed the BASE name
        # and clear_bars x10 + automate x5 mutated untitled_36.json MID-RUN —
        # prompt convention was the only wall). While this file names the song,
        # daw_mcp redirects every base-name resolve to the _prop_ twin: the base
        # physically cannot change during a run, and receipts key the prop.
        _fence = os.path.join(IPC, "active_prop.json")
        try:
            _awrite(_fence, {"song": song, "rid": rid, "t": time.time()})
        except Exception:
            pass
        try:
            result = (mock_propose(rid, req.get("text", ""), song)
                      if MOCK else real_propose(rid, req.get("text", ""), song, ctx_block, req.get("persona", ""), req.get("model"),
                                                revise=bool(req.get("revise")),
                                                genre_pref_hint=req.get("genre_pref", ""),
                                                effort=req.get("effort"),
                                                seed_skeleton=bool(req.get("seed_skeleton"))))
        finally:
            try:
                os.path.exists(_fence) and os.remove(_fence)
            except Exception:
                pass
        if result is None:
            emit(rid, "done", ok=False)
            return
        adopt_stranded_take(rid, song, result, t_ask)   # the arrange-pattern miss self-delivers
        enforce_locks(base_json, os.path.join(SONGS, f"{result}.json"), rid)   # THE GUARD
        try:   # EMPTY-DIFF HONESTY: a proposal identical to the base is a FAILURE,
            #  not a card with an Accept button (seen live: 337-bar song, the agent
            #  burned its turns moving JSON and changed nothing).
            if json.load(open(base_json)) == json.load(open(os.path.join(SONGS, f"{result}.json"))):
                # ...and the corpse LEAVES with the verdict (2026-07-09: an identical
                # _prop_ left behind restored as a phantom pending proposal on app
                # relaunch AND parse-miss'd every next ask as 'pending_proposal')
                for _sfx in (".json", ".ghost.json", ".wav"):
                    _pp = os.path.join(SONGS, f"{result}{_sfx}")
                    os.path.exists(_pp) and os.remove(_pp)
                emit(rid, "error",
                     text=("the edit came back with NO changes — the ask is likely too "
                           "large for one pass on a song this size. Drag-select the "
                           "target region/tracks first (scoped context), or split the ask."))
                emit(rid, "done", ok=False)
                return
        except Exception:
            pass
        srep = scope_check(rid, base_json, os.path.join(SONGS, f"{result}.json"), song)
        last_meta.setdefault(song, {})["surgical"] = srep
        a = render_and_analyze(rid, result, "proposal")
        a = clip_wall(rid, result, a)          # a CLIPPED take never ships untreated —
        a = loudness_recovery(rid, result, a,  # and walls FIRST so recovery can lift it
                              resolve_take_genre(result, song))   # W116 + genre truth
        # THE NOSEDIVE GUARD (f138, from Chezy's 'barely audible' accept): a take
        # moving loudness >6dB either way vs the CURRENT song gets called out
        # BEFORE the accept decision — his 3d0f743 accept would have been caught.
        try:
            base_wav = os.path.join(SONGS, f"{song}.wav")
            if isinstance(a, dict) and os.path.exists(base_wav):
                py = VENV_PY if os.path.exists(VENV_PY) else "python3"
                rcb, outb, _ = run([py, os.path.join(ROOT, "tools", "analyze2.py"),
                                    base_wav], timeout=120)
                if rcb == 0:
                    base_lufs = float(json.loads(outb)["lufs_integrated"])
                    drop = float(a.get("lufs_integrated", base_lufs)) - base_lufs
                    if abs(drop) > 6.0:
                        emit(rid, "activity",
                             text=f"[ears] LOUDNESS {'NOSEDIVE' if drop < 0 else 'SURGE'} "
                                  f"WARNING: this take is {abs(drop):.1f} dB "
                                  f"{'quieter' if drop < 0 else 'louder'} than your song "
                                  f"({base_lufs:.1f} -> {a['lufs_integrated']:.1f} LUFS). "
                                  "If that is not what you asked for, Reject and say so.")
        except Exception as _ng:
            emit(rid, "activity", text=f"[ears] nosedive guard skipped: {_ng}")
        if a:
            emit(rid, "proposal", song=song, proposal=result, surgical=srep or {})
        emit(rid, "done", ok=True)

    elif rtype in ("finish", "recap", "publish"):
        # ZERO-TOKEN product flows (V40/V42/V22): the UI gets buttons the moment the
        # face lane wires them; each runs its tool and emits the text as an event.
        py = VENV_PY if os.path.exists(VENV_PY) else "python3"
        if rtype == "finish":
            cmd = [py, os.path.join(ROOT, "tools", "finish_audit.py"), song or "?"]
            if req.get("genre"):
                cmd += ["--genre", str(req["genre"])]
        elif rtype == "recap":
            cmd = ["python3", os.path.join(ROOT, "tools", "recap.py")]
        else:  # publish from the UI path is ALWAYS dry-run — the outbound act stays
            #    a spoken decision in the chat (local-first law)
            cmd = [py, os.path.join(ROOT, "tools", "publish_flow.py"), song or "?", "--dry-run"]
            if req.get("genre"):
                cmd += ["--genre", str(req["genre"])]
        emit(rid, "status", text=rtype + "…")
        rc, out, err = run(cmd, timeout=900)
        if rc == 0 and out.strip():
            emit(rid, rtype, song=song, text=out.strip()[-4000:])
        else:
            emit(rid, "error", text=f"{rtype} failed: {(err or out)[-400:]}")
        emit(rid, "done", ok=(rc == 0))

    elif rtype == "accept":
        if not os.path.exists(prop_json):
            if time.time() - last_verdict_t.get(song, 0) < 60:
                emit(rid, "status", text="already accepted - that second click cost nothing")
                emit(rid, "done", ok=True)
            else:
                # benign click-race, not an error-red moment (he hit this twice
                # live 2026-07-11: verdict on a scrubbed/quarantined/stopped take)
                corpse = os.path.exists(prop_json + ".corpse")
                emit(rid, "status",
                     text=("nothing pending — the last take was quarantined as "
                           "broken (.corpse kept); ask again for a fresh one"
                           if corpse else
                           "nothing pending — that take was already resolved "
                           "(or its run stopped before a take landed)"))
                emit(rid, "done", ok=False)
            return
        last_verdict_t[song] = time.time()
        log_telemetry(song, True, req.get("note", ""))
        # T2-S2: the accept is the deterministic event that CONFIRMS this run's
        # links -> session facts (last_edit rings + parse-lane refers_to).
        _m = last_meta.get(song) or {}
        session_memory.confirm_verdict(song, _m.get("surgical"),
                                       _m.get("parse_resolutions"),
                                       last_prompts.get(song, ""))
        held = req.get("held_back") or []
        if held:   # HELD-BACK CONSUMED: the do-not-readd law rides the next prompts
            last_curation[song] = {"t": time.time(), "held": [str(x) for x in held][:24]}
            save_feedback_state()
        chronicle.append(song, "verdict", req.get("note", ""),
                         verdict="accept", held=len(held))
        shutil.copy(prop_json, base_json)
        # W106 THE ASSET ADOPTION: prop-scoped audio (the sung take's wav)
        # must not keep its _prop_ name past accept — the NEXT take's sing
        # would OVERWRITE that filename and rot the accepted song's audio;
        # scratch sweepers could orphan it. Adopt to a stable name and
        # re-point the clip before the provenance stamp.
        try:
            bj = json.load(open(base_json))
            _adopted = 0
            _amap = {}          # original rel path -> adopted rel path

            def _adopt(holder, key):
                nonlocal _adopted
                f = str(holder.get(key, ""))
                if f"_prop_{song}" not in os.path.basename(f):
                    return
                src = os.path.join(ROOT, f)
                if not os.path.exists(src):
                    return
                if f in _amap:                    # same wav on 2 clips: one move
                    holder[key] = _amap[f]
                    return
                new = os.path.join(
                    os.path.dirname(f),
                    os.path.basename(f).replace(f"_prop_{song}", song))
                stem, ext = os.path.splitext(new)
                k = 2
                while os.path.exists(os.path.join(ROOT, new)) and new != f:
                    new = f"{stem}_{k}{ext}"
                    k += 1
                shutil.move(src, os.path.join(ROOT, new))
                holder[key] = new
                _amap[f] = new
                _adopted += 1

            for t in bj.get("tracks", []):
                for c in (t.get("audioClips") or []):
                    _adopt(c, "file")
                for sl in (t.get("slots") or []):   # launcher cells too
                    if isinstance(sl, dict) and sl.get("audioFile"):
                        _adopt(sl, "audioFile")
            if _adopted:
                _awrite(base_json, bj)
                emit(rid, "activity",
                     text=f"adopted {_adopted} take asset(s) to stable names")
            # THE FOLLOWING VOICE SURVIVES ACCEPT + orphan sweep (2026-07-11)
            _mig, _swept = adopt_voice_bindings(song, bj, _amap)
            if _mig or _swept:
                emit(rid, "activity",
                     text=f"voice bindings: {_mig} adopted to {song}_vocals"
                          + (f", {_swept} orphan wav(s) swept" if _swept else ""))
            _gap = vocal_gap(bj)
            if _gap:   # untitled_38 2026-07-11: 'REAL VOCALS' accepted voiceless, silently
                emit(rid, "activity",
                     text=f"heads-up — the accepted take is missing its voice: {_gap}")
                chronicle.append(song, "note",
                                 f"(accepted take is missing its voice: {_gap})")
        except Exception as _ae:
            emit(rid, "activity", text=f"asset adoption skipped: {_ae}")
        stamp_provenance(song, base_json, req.get("note", ""))   # V37: before the commit
        os.remove(prop_json)
        _g = os.path.join(SONGS, f"{prop}.ghost.json")
        os.path.exists(_g) and os.remove(_g)
        pw = os.path.join(SONGS, f"{prop}.wav")
        if req.get("cherry"):
            # per-item accept: the proposal wav was rendered BEFORE the merge —
            # it lies about the merged json. Re-render the truth.
            os.path.exists(pw) and os.remove(pw)
            emit(rid, "status", text="cherry-picked accept — re-rendering the merged song…")
            render_and_analyze(rid, song, "merged")
        elif os.path.exists(pw):
            shutil.move(pw, os.path.join(SONGS, f"{song}.wav"))
        # stage ONLY the accepted song's files — `git add songs` swept the user's
        # unrelated in-progress edits + untracked renders into agent-authored
        # commits (bit 2026-07-03: 14 files incl. user WIP; reset + fixed).
        # THE RENDER STAYS OUT OF HISTORY (2026-07-11): the mixdown wav is a
        # derived artifact (m1 render is deterministic from the json; Time
        # Machine restore reads ONLY the json) — committing it grew the pack
        # to 2 GiB (untitled_36's 168MB wav landed 4x in one afternoon). The
        # wav still lands on disk for playback; history carries the truth
        # (json), not the print.
        to_stage = [base_json]
        run_git(["git", "add", "--"] + to_stage)
        run_git(["git", "-c", "user.name=agent", "-c", "user.email=agent@sotadaw",
             "commit", "-q", "-m", f"accept proposal on {song}: {req.get('note','(ui)')}",
             "--only", "--"] + to_stage)
        emit(rid, "status", text="proposal accepted + committed")
        emit(rid, "accepted", song=song)
        # MUSICFLOWS on_accept (BEST_DAW_30 #25): every enabled on_accept flow
        # runs against the freshly-accepted base, detached — journals land in
        # flows/.runs; SOTADAW_FLOWS=0 kills inside the runner; a flow failure
        # can never touch the verdict path.
        try:
            _fpy = VENV_PY if os.path.exists(VENV_PY) else sys.executable
            subprocess.Popen([_fpy, os.path.join(ROOT, "tools", "musicflow.py"),
                              "run-trigger", "on_accept", "--song", song],
                             stdout=open(os.path.join(IPC, "flows_stdout.log"), "a"),
                             stderr=subprocess.STDOUT, start_new_session=True)
        except Exception:
            pass
        emit(rid, "done", ok=True)

    elif rtype == "reject":
        why = str(req.get("reason") or req.get("note") or "")   # REASON consumed, verbatim
        log_telemetry(song, False, why)
        if os.path.exists(prop_json):
            # NEVER destroy a take — and no shadow stores: rejected takes go into GIT
            # on the Time Machine's own rails (songs/.takes/<song>/, scoped commit).
            # Preview/restore rides the exact same `git show` -> proposal machinery.
            try:
                doc = json.load(open(prop_json))
                nnotes = sum(len(t.get("notes", [])) for t in doc.get("tracks", []))
            except Exception:
                nnotes = -1
            tdir = os.path.join(SONGS, ".takes", song)
            os.makedirs(tdir, exist_ok=True)
            take = os.path.join(tdir, f"{int(time.time())}_rejected.json")
            shutil.copy(prop_json, take)
            run_git(["git", "add", "--", take])
            run_git(["git", "commit", "-q", "-m",
                 f"reject take on {song}: {(why or '(no note)')[:60]} [{nnotes} notes]",
                 "--only", "--", take])
            last_reject[song] = {"t": time.time(), "notes": nnotes, "why": why}
            save_feedback_state()
            # T2 (pass 5): the WHY survives the 30-min window as an `avoid`
            # fact (same bucket kernel as the KG complaints) -> RECALL lines
            session_memory.avoid_from_reject(song, why)
            os.remove(prop_json)
        g = os.path.join(SONGS, f"{prop}.ghost.json")
        os.path.exists(g) and os.remove(g)
        pw = os.path.join(SONGS, f"{prop}.wav")
        if os.path.exists(pw):
            os.remove(pw)
        last_feedback[song] = why
        chronicle.append(song, "verdict", why, verdict="reject")
        emit(rid, "status", text="proposal rejected — the take is in version control (Time Machine)")
        emit(rid, "rejected", song=song)
        emit(rid, "done", ok=True)

    else:
        # the typeless-request trap, CLOSED: unknown types used to be consumed
        # SILENTLY (documented gotcha; cost real debugging round-trips). Now: truth.
        emit(rid, "error", text=f"unknown request type '{rtype}' — known: prompt, verb, loops, "
             "make_track, hum_topline, finish, recap, publish, accept, reject")
        emit(rid, "done", ok=False)

# ---------------- THE JANITOR (I6, THE TEN) ----------------
def _app_running():
    try:
        return subprocess.run(["pgrep", "-f", r"sotadaw_artefacts/Release/SOTA DAW"],
                              capture_output=True).returncode == 0
    except Exception:
        return True                    # can't tell -> assume running (never rotate blind)

def janitor():
    """Boot-time scrub of the workshop floor. Conservative by law:
    (1) recording orphans in the repo ROOT (*_Take_*.wav — Tracktion wave-input
        originals used to land in CWD) older than 1h MOVE to
        songs/.recordings/legacy/ (never destroyed);
    (2) stale render scratch in songs/ older than 24h is deleted (_pv_* preview
        slices, _mt_*/_seed_* seed temps, _null_*_stems dirs — all regenerable);
    (3) events/ears .jsonl over 8MB rotate to their last 512KB — ONLY when no
        DAW app is running (the UI's tail offset resets to 0 on shrink and
        would REPLAY the whole log as fresh events).
    Test instances (SOTADAW_IPC override) and sandbox runs skip entirely."""
    if os.environ.get("SOTADAW_IPC") or SANDBOX:
        return
    now = time.time()
    try:   # (1) root recording orphans
        legacy = os.path.join(SONGS, ".recordings", "legacy")
        moved = 0
        for f in os.listdir(ROOT):
            if re.fullmatch(r".+_Take_\d+\.wav", f):
                p = os.path.join(ROOT, f)
                if os.path.isfile(p) and now - os.path.getmtime(p) > 3600:
                    os.makedirs(legacy, exist_ok=True)
                    shutil.move(p, os.path.join(legacy, f))
                    moved += 1
        if moved:
            emit(0, "activity", text=f"[janitor] {moved} stray recording take(s) moved "
                 "from the repo root into songs/.recordings/legacy")
    except Exception:
        pass
    try:   # (2) stale scratch in songs/
        gone = 0
        for f in os.listdir(SONGS):
            p = os.path.join(SONGS, f)
            try:
                stale = now - os.path.getmtime(p) > 86400
            except OSError:
                continue
            if not stale:
                continue
            if re.fullmatch(r"(_pv_|_mt_|_seed_).+\.(json|wav)", f) and os.path.isfile(p):
                os.remove(p); gone += 1
            elif re.fullmatch(r"_null_.+_stems", f) and os.path.isdir(p):
                shutil.rmtree(p, ignore_errors=True); gone += 1
        if gone:
            emit(0, "activity", text=f"[janitor] {gone} stale scratch file(s) swept from songs/")
    except Exception:
        pass
    try:   # (3) log rotation, app-absent only
        if not _app_running():
            for name in ("events.jsonl", "ears.jsonl"):
                p = os.path.join(IPC, name)
                if os.path.exists(p) and os.path.getsize(p) > 8 * 1024 * 1024:
                    with open(p, "rb") as f:
                        f.seek(-512 * 1024, 2)
                        tail = f.read()
                    nl = tail.find(b"\n")
                    with open(p + ".tmp", "wb") as f:
                        f.write(tail[nl + 1:])
                    os.replace(p + ".tmp", p)
                    print(f"[sidecar] janitor rotated {name} (kept last 512KB)", flush=True)
    except Exception:
        pass

def _pipe_proof_stdio():
    """EPIPE-PROOF STDIO (the 2026-07-09 22:09 crash): the sidecar's launcher
    (app or terminal) can die and take the stdout pipe with it; the reborn
    daemon's first banner print then killed the whole brain (BrokenPipeError
    at '[sidecar] up'). A daemon must never die because nobody is listening:
    writes fall back to ipc/sidecar_stdout.log and serving continues."""
    import io

    class W(io.TextIOBase):
        def __init__(self, base):
            self.base = base

        def write(self, s):
            try:
                return self.base.write(s)
            except Exception:
                try:
                    self.base = open(os.path.join(IPC, "sidecar_stdout.log"), "a")
                    return self.base.write(s)
                except Exception:
                    return len(s)

        def flush(self):
            try:
                self.base.flush()
            except Exception:
                pass

    sys.stdout = W(sys.stdout)
    sys.stderr = W(sys.stderr)


def main():
    _pipe_proof_stdio()               # survive an orphaned stdout (launcher died)
    # (warm-rail setdefault lives at module import — one law, one site)
    # single-instance lock: two sidecars sharing one mailbox = races
    lock = os.path.join(IPC, "sidecar.pid")
    if os.path.exists(lock):
        try:
            old_pid = int(open(lock).read().strip())
            if old_pid == os.getpid():
                raise ProcessLookupError("self-refresh: the lock is OURS (execv rebirth)")
            os.kill(old_pid, 0)
            # pid alive is NOT enough — after days, pids get REUSED by strangers
            # (a stale lock wearing a living pid respawn-looped the app watchdog).
            # The owner must actually BE a sidecar.
            cmdline = open(f"/proc/{old_pid}/cmdline", "rb").read().decode(errors="ignore")
            if "sidecar.py" not in cmdline:
                raise ProcessLookupError("pid reused by a non-sidecar")
            print(f"[sidecar] another sidecar (pid {old_pid}) owns {IPC}; exiting", flush=True)
            return
        except (ValueError, ProcessLookupError, PermissionError, OSError):
            pass  # stale lock (or our own after execv)
    open(lock, "w").write(str(os.getpid()))

    def _die(_sig, _frm):
        # THE CONVERSATIONS LAW (Chezy 2026-07-11): closing the app ENDS the
        # session — NOTHING continues in the background. The old law SIGKILLed
        # this daemon, which ORPHANED the resident model processes (live claude
        # sessions kept running in the dark). Reap them, drop the lock, exit now.
        try:
            RESIDENT.kill()
        except Exception:
            pass
        try:
            save_feedback_state()
        except Exception:
            pass
        try:
            if os.path.exists(lock):
                os.remove(lock)
        except Exception:
            pass
        os._exit(0)
    signal.signal(signal.SIGTERM, _die)
    signal.signal(signal.SIGINT, _die)
    print(f"[sidecar] up (mock={MOCK}) ipc={IPC}", flush=True)
    janitor()                                   # I6: sweep the floor before work
    if not os.environ.get("SOTADAW_NO_UPLINK") and not MOCK:
        threading.Thread(target=_uplink_loop, daemon=True).start()
    # readiness truth into the transcript: the user must NEVER wonder if the brain is there
    if MOCK:
        emit(0, "status", text="agent online (mock mode - zero tokens)")
    elif claude_bin() is None:
        emit(0, "error", text="AGENT BLOCKED: claude CLI not found - chat prompts will not work. "
             "Install: npm i -g @anthropic-ai/claude-code, then run: claude (log in). "
             "MAKE + all direct editing still work.")
    else:
        try:    # dynamic count — the hardcoded "53" survived three tool additions
            import importlib.util as _ilu
            _spec = _ilu.spec_from_file_location("_dm", os.path.join(ROOT, "agent", "daw_mcp.py"))
            _dm = _ilu.module_from_spec(_spec)
            _spec.loader.exec_module(_dm)
            emit(0, "status", text=f"agent online - {len(_dm.TOOLS)} tools ready")
        except Exception:
            emit(0, "status", text="agent online")
    prewarm()                                   # pay the defer tax off-screen
    req_path = os.path.join(IPC, "request.json")
    # THE HEARTBEAT (the 23:30 lying chip): a POSITIVE liveness signal — the UI
    # was doing /proc forensics on the lockfile pid and could stick OFFLINE
    # while the daemon streamed a whole run. A 1s daemon thread touches
    # ipc/alive (it must beat THROUGH long handle() runs, not between them);
    # the watchdog gets ground truth that survives execv windows, pid reuse
    # and cmdline read quirks. Dies with the process; execv restarts it.
    alive_path = os.path.join(IPC, "alive")

    def _beat_loop():
        while True:
            try:
                with open(alive_path, "a"):
                    os.utime(alive_path, None)
            except Exception:
                pass
            time.sleep(1.0)
    threading.Thread(target=_beat_loop, daemon=True).start()

    # THE VERDICT SIDE-LANE (Chezy 2026-07-11, "accepting takes hours"): handle()
    # blocks through whole runs, so a verdict written mid-run sat unconsumed —
    # and the next prompt OVERWROTE it (the accept silently vanished; the deck
    # said "Accepting..." forever). This thread consumes accept/reject WHILE the
    # main lane is busy: verdicts are file+git work only (they never spawn runs),
    # and run_git is lock-serialized against the main lane.
    # SAME-SONG GUARD (2026-07-11, run 6 live): an accept consumed MID-RUN of a
    # request on the SAME song pulled the prop from under it — the run died on
    # 'cannot parse' and left a half-context corpse the next run inherited.
    # Same-song verdicts DEFER (request.json stays; the main loop takes it when
    # the run ends). Other-song verdicts still flow instantly.
    busy = threading.Event()
    busy_song = {"name": None}

    def _verdict_lane():
        while True:
            time.sleep(0.5)
            if not busy.is_set() or not os.path.exists(req_path):
                continue
            try:
                peek = json.load(open(req_path))
            except Exception:
                continue                    # half-written: the writer is mid-flight
            if peek.get("type") not in ("accept", "reject"):
                continue
            if peek.get("song") and peek.get("song") == busy_song["name"]:
                continue                    # same-song: defer until the run ends
            vwork = req_path + ".verdict"
            try:
                os.replace(req_path, vwork)
                vreq = json.load(open(vwork))
            except Exception:
                continue                    # the main lane won the grab — fine
            try:
                handle(vreq)
            except Exception:
                import traceback
                vtb = [l.strip() for l in traceback.format_exc().strip().splitlines()]
                emit(vreq.get("id", 0), "error",
                     text=f"sidecar exception on '{vreq.get('type')}' "
                          f"({vreq.get('song', '?')}): " + " | ".join(vtb[-3:]))
                emit(vreq.get("id", 0), "done", ok=False)
            finally:
                os.path.exists(vwork) and os.remove(vwork)
    threading.Thread(target=_verdict_lane, daemon=True).start()

    while True:
        if os.path.exists(req_path):
            work = req_path + ".working"
            try:
                os.replace(req_path, work)
                req = json.load(open(work))
            except Exception as e:
                if os.path.exists(req_path) or os.path.exists(work):
                    emit(0, "error", text=f"bad request: {e!r}")
                os.path.exists(work) and os.remove(work)
                time.sleep(0.2)
                continue
            try:
                busy_song["name"] = req.get("song") or None
                busy.set()
                handle(req)
            except Exception:
                # name the REQUEST and the LINE — "sidecar exception: FileNotFoundError"
                # with no context cost a whole debugging round-trip on the Inspiron
                import traceback
                tb = [l.strip() for l in traceback.format_exc().strip().splitlines()]
                emit(req.get("id", 0), "error",
                     text=f"sidecar exception on '{req.get('type')}' ({req.get('song', '?')}): "
                          + " | ".join(tb[-3:]))
                emit(req.get("id", 0), "done", ok=False)
            finally:
                busy.clear()
                busy_song["name"] = None
                os.path.exists(work) and os.remove(work)
        elif _self_refresh_due():
            # SELF-REFRESH (idle only): new sidecar code landed on disk — exec into
            # it. execv PRESERVES the PID (lockfile stays true); feedback state is
            # already disk-persistent; residents are reaped (children would outlive
            # the exec image). The daemon upgrades itself between requests.
            emit(0, "status", text="sidecar self-refresh: new code landed - reloading (state persists)")
            try:
                RESIDENT.kill()
            except Exception:
                pass
            try:
                save_feedback_state()
            except Exception:
                pass
            if os.name == "nt":
                # PORT_SPEC.md: Windows execv re-quotes argv badly; skip live
                # self-refresh — staleness heals on the next app launch.
                continue
            os.execv(sys.executable, [sys.executable, _SELF_PATH] + sys.argv[1:])
        dj_live_tick()                  # R4: the coach speaks while a set sounds
        vocal_follow_tick(busy)         # THE FOLLOWING VOICE: edited vocal MIDI re-sings
        time.sleep(0.25)

if __name__ == "__main__":
    try:
        main()
    except Exception:
        # LAST GASP: a sidecar must never die silently — the Inspiron spent a day
        # in a mute respawn loop. Full truth to a file, one line to the chat.
        import traceback
        tb = traceback.format_exc()
        try:
            os.makedirs(IPC, exist_ok=True)
            open(os.path.join(IPC, "sidecar_crash.log"), "w").write(tb)
            emit(0, "error", text="SIDECAR CRASHED: " + tb.strip().splitlines()[-1][:160]
                 + " — full traceback in agent/ipc/sidecar_crash.log")
        except Exception:
            pass
        raise
