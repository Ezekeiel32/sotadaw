#!/usr/bin/env python3
"""AI SOTA DAW — MCP tool server (stdio, newline-delimited JSON-RPC, zero deps).

The agent's hands: skills (deterministically force-injected), Faust instrument authoring
(compile-validated, errors returned for self-correction), song writing, engine render, analysis.
Same tools serve `claude -p` today and the shipped Agent SDK later.
"""
import glob, hashlib, json, os, re, shutil, subprocess, sys, threading, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import surgical            # THE SCALPEL kernel: selectors, ops, receipts, scope law

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INSTRUMENTS = os.path.join(ROOT, "instruments")
SKILLS = os.path.join(ROOT, "skills")
SONGS = os.path.join(ROOT, "songs")

def _prop_fence(name):
    """THE PROP FENCE (2026-07-11): during an active proposal run the BASE name
    means THE TAKE. Run 9 live: the agent passed 'untitled_36' and clear_bars
    x10 + automate x5 mutated the BASE mid-run (proposal law broken by prompt
    convention alone), receipts keyed the base -> the scope check read the prop
    ledger and flagged 15 phantom changes. The sidecar stamps ipc/active_prop.json
    at agent-run entry (removed in its finally); while it names this song, every
    tool resolve redirects to the _prop_ twin — writes, reads and receipts
    cohere onto the take, and the base physically cannot change mid-run."""
    try:
        ipc = os.environ.get("SOTADAW_IPC") or os.path.join(ROOT, "agent", "ipc")
        f = json.load(open(os.path.join(ipc, "active_prop.json")))
        if name and name == f.get("song"):
            prop = f"_prop_{name}"
            pj = os.path.join(SONGS, prop + ".json")
            if not os.path.exists(pj):
                shutil.copy(os.path.join(SONGS, name + ".json"), pj)
            return prop
    except Exception:
        pass
    return name

def resolve_song_name(raw, default=""):
    """Song id -> on-disk basename. RAW NAME FIRST: imported songs legitimately
    carry hyphens (blpkosher-hourglassofficialvideo) and the old strip-everything
    sanitize made them unreachable by EVERY tool, read and write (live blocker,
    2026-07-09: two $2 agent runs died on 'no such song'). A raw or lowercased
    candidate wins ONLY if its .json (or its _prop_ twin) exists on disk; else
    the legacy sanitize keeps creation naming byte-stable. Path-safety: the raw
    lane admits [A-Za-z0-9._-] only and never '..' — traversal cannot ride it.
    THE PROP FENCE rides every resolve (see _prop_fence)."""
    raw = str(raw if raw is not None else default).strip()
    for cand in (raw, raw.lower()):
        if cand and ".." not in cand and re.fullmatch(r"[A-Za-z0-9._\-]{1,160}", cand) \
                and (os.path.exists(os.path.join(SONGS, cand + ".json"))
                     or os.path.exists(os.path.join(SONGS, "_prop_" + cand + ".json"))):
            return _prop_fence(cand)
    return _prop_fence(re.sub(r"[^a-z0-9_]", "", raw.lower()))

KITS = os.path.join(ROOT, "kits")
PLUGIN_CACHE = os.path.join(ROOT, "app", "plugins_cache.xml")
M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")
VENV_PY = os.path.join(ROOT, ".venv", "bin", "python")
ANALYZE = os.path.join(ROOT, "tools", "analyze2.py")
# THE WARM RAIL (b17cd1a/e5eb628): the MCP server is a long-lived host too — jam
# calibrations, keep_jam renders and every render_cached miss skip process spawn
# + engine init via the resident `m1 serve`. Same triple belt as the sidecar
# (determinism seal + client fallback + caller fallbacks); kill-switch =0;
# CLOEXEC pipes end the resident with this process.
os.environ.setdefault("SOTADAW_RENDER_SERVE", "1")

def log(*a):
    print("[daw_mcp]", *a, file=sys.stderr, flush=True)

# ---------- skills (integrity-checked, deterministic force-injection) ----------
def load_registry():
    return json.load(open(os.path.join(SKILLS, "registry.json")))

def skill_body(entry):
    path = os.path.join(SKILLS, entry["file"])
    raw = open(path, "rb").read()
    if hashlib.sha256(raw).hexdigest() != entry["sha256"]:
        raise RuntimeError(f"INTEGRITY FAILURE: {entry['file']} does not match registry sha256. "
                           f"Rebuild registry with tools/skills_build.py if the change was intentional.")
    return raw.decode("utf-8")

def select_skills(context_tags):
    """Deterministic: a skill fires iff it has tag 'always' or shares a tag with the context."""
    reg = load_registry()
    ctx = {t.lower() for t in context_tags}
    fired = []
    for name in sorted(reg["skills"]):
        e = reg["skills"][name]
        tags = {t.lower() for t in e["tags"]}
        if "always" in tags or (tags & ctx):
            fired.append((name, e))
    return fired

# ---------- helpers ----------
def list_instruments():
    return sorted(f[:-4] for f in os.listdir(INSTRUMENTS) if f.endswith(".dsp"))

def list_kits():
    out = {}
    if os.path.isdir(KITS):
        for k in sorted(os.listdir(KITS)):
            kj = os.path.join(KITS, k, "kit.json")
            if os.path.exists(kj):
                d = json.load(open(kj))
                out[k] = {"kind": d.get("kind", "?"),
                          "keys": sorted(x["keyNote"] for x in d.get("samples", []))}
    return out

def vst_names():
    names = []
    if os.path.exists(PLUGIN_CACHE):
        names = re.findall(r'name="([^"]+)"', open(PLUGIN_CACHE).read())
    return sorted(set(names))

def run(cmd, timeout=600, cwd=ROOT):
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=cwd)
    return p.returncode, p.stdout, p.stderr

def _sing_receipted(a, mode, argv, timeout_s):
    """W115: the sing rail mutates lyrics[] + vocal lanes — the SCOPE LAW
    needs the receipt (Chezy's live take flagged OUT OF SCOPE x3 because
    these were bare lambdas; receipt_lint's AST scan missed the lambda
    form)."""
    name = resolve_song_name(a["song"])
    out = run([VENV_PY if os.path.exists(VENV_PY) else "python3",
               os.path.join(ROOT, "tools", "sing.py"), mode, name] + argv,
              timeout=timeout_s)[1]
    if out and "SUNG" in out:
        _wild = ["vocals", "vocals_sung", "vocals_sketch", a.get("track", "lead")]
        if mode == "hum":     # card_lint wants LITERAL tool names (rail map)
            _rc(name, "hum_topline", fields=["meta:lyrics"], track_wild=_wild,
                summary=f"hummed onto '{a.get('track', 'lead')}'")
        else:
            _rc(name, "sing_lyrics", fields=["meta:lyrics"], track_wild=_wild,
                summary=f"sung lyrics onto '{a.get('track', 'lead')}'")
    return (out or "").strip()[-500:] or "sing failed"


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


def _rc(song_name, tool, fields=None, track_wild=None, summary=""):
    """Edit receipt -> ipc receipts.jsonl. The sidecar's SCOPE LAW checks the proposal
    diff against these (surgical_edit files exact per-note receipts itself). A receipt
    must never break the tool that files it."""
    try:
        surgical.coarse_receipt(song_name, tool, fields=fields, track_wild=track_wild,
                                summary=summary or tool)
    except Exception as e:
        log("receipt failed:", e)

SONG_SCHEMA_HINT = ('song format v2: {"version":2, "bpm", "key", "lengthBars", '
                    '"swing":{"grid":"16th","amount":0.5-0.62}, "masterGainDb":0 (keep 0), '
                    '"tempoMap":[{"bar":16,"bpm":140}] (tempo switches/arcs — holds until the next point; '
                    'warped audio + all beats follow), '
                    '"master":[{"id":"fx_trim","params":{"level":-3}},{"id":"fx_truepeak","params":{"ceiling":-1.2}}] (fx_truepeak = THE RELEASE WALL, ceiling = output dBTP, always LAST), '
                    '"buses":[{"id":"verb","gainDb":0,"fx":[{"id":"fx_reverb","params":{...}}]}], '
                    '"tracks":[{"name", "source":{"kind":"faust","id":<instrument>} | '
                    '{"kind":"sample","kit":<kit>} | {"kind":"vst3","plugin":"Dexed","params":{...}}, '
                    '"gainDb", "pan", "fx":[{"id":"fx_widen","params":{...}}], '
                    '"sends":[{"bus":"verb","gainDb":-12}], '
                    '"automation":[{"target":"gainDb"|"pan"|"fx[i].<param>"|"source.<param>", '
                    '"points":[{"beat":0,"v":0.0,"curve":0.7},{"beat":16,"v":0.9}]}] (curve -1..1: >0 late-bloom builds, <0 early-jump), '
                    '"notes":[{"start":beats,"len":beats,"pitch":midi,"vel":0..1}], '
                    '"audioClips":[{"file":wav,"startBeat","lengthBeats","offsetSec","gainDb",'
                    '"sourceBpm":<orig bpm — set it and the audio WARPS to follow the song tempo>}]}]} '
                    '(1 bar = 4 beats; automation = MOTION: filter opens, volume rides, width blooms — '
                    'points interpolate linearly, values in the param\'s real units; '
                    'use automate/list_plugin_params/set_track_param tools for surgical edits)')

def validate_scoped(song, touched_names):
    """Partition validate_song errors: blocking = song-level + TOUCHED tracks;
    pre-existing wounds on other tracks become notes (live incident: a poisoned
    UI seed blocked every unrelated per-track write)."""
    errs = validate_song(song)
    names = [t.get("name") for t in song.get("tracks", [])]
    blocking, notes = [], []
    for e in errs:
        m = re.match(r"track\[(\d+)\]", e)
        if m and 0 <= int(m.group(1)) < len(names) \
             and names[int(m.group(1))] not in (touched_names or []):
            notes.append(e)
        else:
            blocking.append(e)
    return blocking, notes


def validate_song(song):
    errs = []
    if not isinstance(song.get("bpm"), (int, float)) or not 40 <= song["bpm"] <= 220:
        errs.append("bpm must be a number 40..220")
    if not isinstance(song.get("lengthBars"), (int, float)) or song["lengthBars"] <= 0:
        errs.append("lengthBars must be > 0")
    tm = song.get("tempoMap", [])
    if not isinstance(tm, list):
        errs.append("tempoMap must be an array of {bar, bpm, curve?}")
    else:
        for i, p in enumerate(tm):
            if not isinstance(p, dict) or not isinstance(p.get("bar"), (int, float)) or p.get("bar", 0) <= 0:
                errs.append(f"tempoMap[{i}].bar must be a number > 0")
            elif not isinstance(p.get("bpm"), (int, float)) or not 40 <= p["bpm"] <= 220:
                errs.append(f"tempoMap[{i}].bpm must be 40..220")
    tracks = song.get("tracks")
    if not isinstance(tracks, list) or not tracks:
        errs.append("tracks must be a non-empty array")
        return errs
    avail = set(list_instruments())
    kits = list_kits()
    vsts = vst_names()
    sw = song.get("swing", {})
    if sw and not 0.5 <= float(sw.get("amount", 0.5)) <= 0.7:
        errs.append("swing.amount must be 0.5..0.7")
    for mi, m in enumerate(song.get("master", [])):
        if m.get("type", "faustfx") not in ("limiter", "faustfx", "eq", "comp"):
            errs.append(f"master[{mi}].type must be limiter|faustfx|eq|comp")
        mid = str(m.get("id") or "")
        if mid.startswith("vst3:"):     # vst3 inserts are legal anywhere faust fx go
            want = mid[5:].strip().lower()
            if vsts and not any(want in v.lower() for v in vsts):
                errs.append(f"master[{mi}].id '{mid}' not in scan cache {vsts}")
        elif m.get("type", "faustfx") == "faustfx" and m.get("id") not in avail:
            errs.append(f"master[{mi}].id '{m.get('id')}' not a faust instrument/fx")
    total_beats = float(song.get("lengthBars", 4)) * 4
    for ti, t in enumerate(tracks):
        src = t.get("source")
        if src is None and t.get("instrument"):
            src = {"kind": "faust", "id": t["instrument"]}
        if not isinstance(src, dict):
            errs.append(f"track[{ti}] missing source"); continue
        kind = src.get("kind", "faust")
        sid = src.get("id") or src.get("kit") or src.get("plugin")
        if kind == "faust" and sid not in avail:
            import difflib
            near = difflib.get_close_matches(str(sid), list(avail) + list(kits), 3, 0.5)
            errs.append(f"track[{ti}] faust id '{sid}' does not exist — closest real ids: "
                        f"{near or sorted(avail)[:8]} (kits need kind 'sample')")
        elif kind == "sample" and sid not in kits:
            import difflib
            near = difflib.get_close_matches(str(sid), list(kits) + list(avail), 3, 0.5)
            errs.append(f"track[{ti}] kit '{sid}' does not exist — closest: "
                        f"{near or sorted(kits)}")
        elif kind == "vst3" and vsts and not any(sid.lower() in v.lower() for v in vsts):
            errs.append(f"track[{ti}] vst3 '{sid}' not in scan cache {vsts}")
        elif kind not in ("faust", "sample", "vst3", "audio"):
            errs.append(f"track[{ti}] unknown source kind '{kind}'")
        for ci, c in enumerate(t.get("audioClips", [])):
            if not c.get("file"):
                errs.append(f"track[{ti}].audioClips[{ci}] missing file")
            elif not os.path.exists(c["file"] if os.path.isabs(c["file"]) else os.path.join(ROOT, c["file"])):
                errs.append(f"track[{ti}].audioClips[{ci}] file not found: {c['file']}")
        notes = t.get("notes")
        if not isinstance(notes, list) or not notes:
            if kind == "audio" or t.get("audioClips"):
                continue                      # audio-clip tracks don't need notes
            errs.append(f"track[{ti}] has no notes")
            continue
        for ni, nv in enumerate(notes):
            for k in ("start", "len", "pitch", "vel"):
                if not isinstance(nv.get(k), (int, float)):
                    errs.append(f"track[{ti}].notes[{ni}].{k} missing/not numeric"); break
            else:
                if nv["start"] < 0 or nv["start"] >= total_beats:
                    errs.append(f"track[{ti}].notes[{ni}].start {nv['start']} outside 0..{total_beats}")
                if nv["len"] <= 0:
                    errs.append(f"track[{ti}].notes[{ni}].len {nv['len']} must be > 0 "
                                "(a zero-length note renders as SILENCE)")
                if not 0 < nv["vel"] <= 1:
                    errs.append(f"track[{ti}].notes[{ni}].vel must be 0..1")
                if not 0 <= nv["pitch"] <= 127:
                    errs.append(f"track[{ti}].notes[{ni}].pitch must be MIDI 0..127")
    return errs

# ---------- tools ----------
# THE SESSION DIET (agent-speed): start_session used to inject 50-68KB (~13-17k
# tokens) of full skill bodies into EVERY conversation — latency + attention tax on
# each prompt. Tiering, ZERO law deletion: damage-preventer laws stay FULL inline;
# everything else becomes an essence hook + get_skill index (the fetch rail is
# core-lane). Genre asks inline only the BEST tag match; sibling genres index.
_SESSION_FULL = {"tool-guide", "mix-headroom", "fx-usage", "surgical-edits"}
# 320 -> 256 (2026-07-07): the genre campaign grows trap-family siblings (rage,
# plugg...) that all fire for a trap ask — at 320 the dark-trap payload crossed
# its 32K budget by 178 bytes. The essence is a HOOK, not the law (battery floor
# is 60 chars); 256 re-opens ~2 siblings of headroom on the same budget.
_ESSENCE_CH = 256

def _skill_essence(body):
    cut = body[:_ESSENCE_CH]
    nl = cut.rfind("\n")
    if nl > 160:
        cut = cut[:nl]
    return cut.strip()

def _vibe_route(text, k=4, timeout=90):
    """SEMANTIC GENRE ROUTING (pass 5): kg_vibe subprocess -> {"genre","score",
    "sibs"} or None. Weak routes (top cos < 0.35) return None — the semantic
    lane is ADVISORY and must never override a literal miss with noise.
    Never raises; every failure degrades to the literal path."""
    try:
        py = VENV_PY if os.path.exists(VENV_PY) else "python3"
        r = subprocess.run([py, os.path.join(ROOT, "tools", "kg_vibe.py"),
                            str(text), "--k", str(int(k))],
                           capture_output=True, text=True, timeout=timeout)
        line = next(l for l in r.stdout.splitlines() if l.startswith("VIBE_JSON "))
        d = json.loads(line[len("VIBE_JSON "):])
        if not d.get("available") or d.get("weak") or not d.get("results"):
            return None
        top = d["results"][0]
        return {"genre": str(top["genre"]), "score": top["score"],
                "sibs": ", ".join(x["genre"] for x in d["results"][1:3])}
    except Exception:
        return None

def t_start_session(args):
    genre = str(args.get("genre", "")).lower()
    ctx = set(re.split(r"[\s,/+-]+", genre)) | {genre}
    fired = select_skills(ctx)
    kits = list_kits()
    # THE KIT LINE DIET (2026-07-09): every import/battery mints source kits
    # (<song>_drums, *_id, _scratch...) — 64 on disk inflated this line to
    # 1.8K and blew the session budget while the skills were innocent. The
    # session line carries the CURATED palette; minted kits stay fully live
    # (list_kits names them; songs reference theirs directly).
    def _minted(k):
        return k.startswith("_") or k.endswith(("_bass", "_drums", "_other",
                                                "_vocals", "_id"))
    core = {k: v for k, v in kits.items() if not _minted(k)}
    kit_desc = "; ".join(f"{k}({v['kind']})" for k, v in core.items())
    if len(core) < len(kits):
        kit_desc += (f"; +{len(kits) - len(core)} imported/source kits "
                     "(list_kits)")
    always = [(n, e) for n, e in fired if "always" in {t.lower() for t in e["tags"]}]
    genred = [(n, e) for n, e in fired if (n, e) not in always]
    vibe_note = ""
    if not genred and genre.strip():
        # SEMANTIC ROUTING (pass 5): no skill tag matched the genre words — KNN
        # the vibe against the KG captions and re-fire skills on the nearest
        # real genre ("smoky late night jazz bar" -> jazz skills, not nothing).
        v = _vibe_route(genre)
        if v:
            ctx |= {v["genre"]} | set(v["genre"].split("_"))
            fired = select_skills(ctx)
            always = [(n, e) for n, e in fired
                      if "always" in {t.lower() for t in e["tags"]}]
            genred = [(n, e) for n, e in fired if (n, e) not in always]
            vibe_note = (f" [vibe-routed -> {v['genre']} (cos {v['score']}); "
                         f"near: {v['sibs']}]")
    best = None
    if genred:                                   # the ask's OWN genre rides full
        score = lambda ne: (len({t.lower() for t in ne[1]["tags"]} & ctx),
                            genre in {t.lower() for t in ne[1]["tags"]}, ne[0])
        best = max(genred, key=score)[0]
    full, indexed = [], []
    for n, e in fired:
        (full if n in _SESSION_FULL or n == best else indexed).append((n, e))
    parts = [f"# Session start — genre context: '{genre}'{vibe_note}",
             f"Faust instruments: {', '.join(list_instruments())}",
             f"Sample kits: {kit_desc}",
             f"VST3 plugins: {', '.join(vst_names()) or '(none scanned)'}",
             SONG_SCHEMA_HINT,
             f"\n{len(fired)} skill(s) fired: {len(full)} inline below + "
             f"{len(indexed)} indexed (their FULL law is one get_skill away):\n"]
    for name, e in full:
        parts.append(f"\n===== SKILL {name}@v{e['version']} =====\n{skill_body(e)}")
    if indexed:
        parts.append("\n===== SKILL INDEX — call get_skill(name) BEFORE work that "
                     "touches one (the essence below is a hook, NOT the law) =====")
        for name, e in indexed:
            parts.append(f"\n--- {name}@v{e['version']} ---\n{_skill_essence(skill_body(e))}\n"
                         f"[...full law: get_skill(\"{name}\")]")
    return "\n".join(parts)

def t_list_instruments(args):
    return json.dumps(list_instruments())

def t_get_skill(args):
    reg = load_registry()
    name = args["name"]
    if name not in reg["skills"]:
        return f"unknown skill '{name}'. available: {sorted(reg['skills'])}"
    return skill_body(reg["skills"][name])

def t_write_instrument(args):
    name = re.sub(r"[^a-z0-9_]", "", str(args["name"]).lower())
    code = args["faust_code"]
    if not name:
        return "ERROR: name must be lowercase letters/digits/underscore"
    tmp = f"/tmp/faust_validate_{name}.dsp"
    open(tmp, "w").write(code)
    rc, out, err = run(["faust", "-lang", "cpp", "-cn", "Tmp", tmp, "-o", "/dev/null"], timeout=60)
    if rc != 0:
        return f"FAUST COMPILE FAILED — fix and resubmit:\n{err.strip()}"
    open(os.path.join(INSTRUMENTS, f"{name}.dsp"), "w").write(code)
    rc2, out2, err2 = run([os.path.join(ROOT, "tools", "gen_faust.sh")], timeout=120)
    if rc2 != 0:
        return f"instrument saved but codegen failed:\n{err2[-800:]}"
    return (f"OK: instruments/{name}.dsp saved and validated. NOTE: the engine binary must be "
            f"rebuilt before this instrument is renderable — call rebuild_engine (takes ~2-4 min), "
            f"or compose with existing instruments.")

def t_rebuild_engine(args):
    rc, out, err = run(["cmake", "--build", os.path.join(ROOT, "app", "build"), "-j2"], timeout=900)
    tail = (out + err)[-1200:]
    return ("REBUILD OK\n" if rc == 0 else "REBUILD FAILED\n") + tail

_DOCTOR_HARD = {"M1", "M3", "X1", "X2", "X3", "C3"}   # objective, always-wrong; rest = taste/maturity

def _doctor_verdict(song):
    """EARS ON WRITE (Chezy: 'the agent is OBLIVIOUS to sound and music quality'):
    every full write returns its own symbolic critique in the SAME step — hard
    truths itemized (panned/widened sub, no release wall, dead-zone fx params),
    soft findings counted. Full detail stays on the doctor verb. Render ears
    (analyze/hear) remain the finalize step; this is the free 80% that never
    needed a render. Pure, ~ms, fail-open: the critic must never kill the pen."""
    try:
        tp = os.path.join(ROOT, "tools")            # the SERVER process doesn't carry
        if tp not in sys.path:                      # tools/ on its path (the proto E2E
            sys.path.insert(0, tp)                  # caught fail-open eating the import)
        import doctor as _doc
        finds = list(_doc.diagnose(song))           # X2 zone-traps live UPSTREAM in the
    except Exception:                               # doctor now (one source of truth —
        return ""                                   # the Doctor chip sees them too)
    if not finds:
        return "\nDOCTOR: clean."
    # C3 (no low end) is only a HARD truth once the arrangement is really underway
    demote = {"C3"} if len(song.get("tracks", [])) < 3 else set()
    hard = [x for x in finds if x[0] in _DOCTOR_HARD and x[0] not in demote]
    soft = [x for x in finds if x not in hard]
    line = f"\nDOCTOR: {len(hard)} hard / {len(soft)} open"
    if hard:
        line += " — " + "; ".join(f"[{c}] {w} -> {fx}" for c, w, fx in hard[:3])
        if len(hard) > 3:
            line += f"; +{len(hard) - 3} more hard"
    else:
        line += " (taste/maturity only — the doctor verb has detail)"
    return line

def _track_verdict(t):
    """EARS ON TWEAK: update_track/set_track_fx are where the traps actually ENTER
    (mix moves). Track-local hard checks only — no chord_map, ~0ms — and SILENT
    when clean: a gain nudge must not produce critique spam."""
    finds = []
    try:
        tp = os.path.join(ROOT, "tools")
        if tp not in sys.path:
            sys.path.insert(0, tp)
        import automix as _amx
        role = _amx.role(t)
    except Exception:
        role = ""
    pan = abs(float(t.get("pan", 0) or 0))
    nm = t.get("name", "?")
    if role in ("kick", "bass"):
        if pan > 1e-6:
            finds.append(f"[M1] '{nm}' (sub/kick) panned {t.get('pan')} — cancels in mono -> pan 0")
        if any(f.get("id") == "fx_widen" for f in t.get("fx", []) or []):
            finds.append(f"[M1] '{nm}' (sub) is WIDENED — mono cancellation -> strip fx_widen")
    if role == "focal" and pan > 0.2:
        finds.append(f"[M3] '{nm}' (lead/focal) panned {t.get('pan')} — focus wanders -> pan toward 0")
    for f in t.get("fx", []) or []:
        if f.get("id") == "fx_trim" and "gain" in (f.get("params") or {}):
            finds.append(f"[X2] fx_trim on '{nm}' has param 'gain' — the zone is 'level'; this trim does NOTHING")
        if f.get("type") == "limiter":
            finds.append(f"[X2] deprecated type:'limiter' on '{nm}' — ceiling non-functional -> fx_truepeak")
    return ("\nDOCTOR: " + "; ".join(finds[:3])) if finds else ""

def t_write_song(args):
    name = resolve_song_name(args["name"])
    song = args["song"]
    if isinstance(song, str):
        try:
            song = json.loads(song)
        except json.JSONDecodeError as e:
            return f"song is not valid JSON: {e}"
    errs = validate_song(song)
    if errs:
        return "SONG INVALID — fix and resubmit:\n- " + "\n- ".join(errs) + f"\n{SONG_SCHEMA_HINT}"
    path = os.path.join(SONGS, f"{name}.json")
    _awrite(path, song)
    n = sum(len(t["notes"]) for t in song["tracks"])
    _rc(name, "write_song", fields=["*"], summary=f"FULL WRITE: {len(song['tracks'])} tracks, {n} notes")
    return (f"OK: songs/{name}.json written ({len(song['tracks'])} tracks, {n} notes). "
            f"Next: render_song." + _doctor_verdict(song))

def t_update_track(args):
    """Surgically replace fields of ONE track in a song — no need to resend the whole song."""
    name = resolve_song_name(args["song"])
    path = os.path.join(SONGS, f"{name}.json")
    _ensure_prop(name, path)
    if not os.path.exists(path):
        return f"no such song '{name}'"
    song = json.load(open(path))
    tname = args["track"]
    matches = [t for t in song["tracks"] if t.get("name") == tname]
    if not matches:
        return f"no track named '{tname}' in {name}. tracks: {[t.get('name') for t in song['tracks']]}"
    t = matches[0]
    if args.get("remove") is True:
        # the suite's case #27 kill: deleting a track FORCED a full write_song
        # (float-drift on every other track). This is the scoped delete verb.
        song["tracks"] = [x for x in song["tracks"] if x.get("name") != tname]
        _awrite(path, song)
        _rc(name, "update_track", fields=[f"track:{tname}"], track_wild=[tname],
            summary=f"removed track {tname}")
        return f"OK: track '{tname}' REMOVED from songs/{name}.json. Other tracks untouched."
    if "notes" in args and args["notes"] is not None:
        notes = args["notes"]
        if isinstance(notes, str):
            try:
                notes = json.loads(notes)
            except json.JSONDecodeError as e:
                return f"notes is not valid JSON: {e}"
        t["notes"] = notes
    for k in ("gainDb", "pan"):
        if k in args and args[k] is not None:
            t[k] = args[k]
    if "muted" in args and args["muted"] is not None:
        # the scalpel suite's case #16 proved 'mute the bass' was UNWINNABLE — muted
        # was read-only across all tools; -60dB fakes don't unmute back
        t["muted"] = bool(args["muted"])
    if "sends" in args and args["sends"] is not None:
        sends = args["sends"]
        if isinstance(sends, str):
            try:
                sends = json.loads(sends)
            except json.JSONDecodeError as e:
                return f"sends is not valid JSON: {e}"
        bus_ids = {b.get("id") for b in song.get("buses", [])}
        for sd in sends:
            if sd.get("bus") not in bus_ids:
                return f"send bus '{sd.get('bus')}' not defined. buses: {sorted(bus_ids)} (set_buses first)"
        t["sends"] = sends
    errs, pre = validate_scoped(song, [tname])
    if errs:
        return "INVALID after update — fix and resubmit:\n- " + "\n- ".join(errs)
    _awrite(path, song)
    if pre:
        _pre_note = " | NOTE pre-existing issues on OTHER tracks (not yours, not blocking): " + "; ".join(pre[:3])
    else:
        _pre_note = ""
    _rc(name, "update_track",
        fields=[f"track:{tname}:{k}" for k in ("gainDb", "pan", "sends", "muted")
                if args.get(k) is not None],
        track_wild=[tname] if args.get("notes") is not None else None,
        summary=f"update_track {tname}")
    return (f"OK: track '{tname}' updated in songs/{name}.json ({len(t.get('notes', []))} notes). "
            f"Other tracks untouched. Next: render_song." + _pre_note + _track_verdict(t))

def t_get_song(args):
    name = resolve_song_name(args["song"])
    path = os.path.join(SONGS, f"{name}.json")
    if not os.path.exists(path):
        return f"no such song '{name}'"
    return open(path).read()

def t_get_song_summary(args):
    """The song WITHOUT note bodies — structure at ~1KB regardless of size."""
    name = resolve_song_name(args["song"])
    path = os.path.join(SONGS, f"{name}.json")
    if not os.path.exists(path):
        return f"no such song '{name}'"
    song = json.load(open(path))
    out = {k: song.get(k) for k in ("bpm", "key", "lengthBars", "swing",
                                    "masterGainDb", "sections", "tempoMap") if k in song}
    out["master"] = [f.get("id") or f.get("type") for f in song.get("master", [])]
    out["buses"] = [b.get("name") for b in song.get("buses", [])]
    out["tracks"] = []
    for t in song.get("tracks", []):
        notes = t.get("notes", [])
        span = (round(min(n["start"] for n in notes) / 4) + 1,
                round(max(n["start"] + n.get("len", 0) for n in notes) / 4) + 1) if notes else None
        out["tracks"].append({
            "name": t.get("name"), "source": t.get("source", {}),
            "gainDb": t.get("gainDb"), "pan": t.get("pan"),
            "muted": t.get("muted", False), "locked": t.get("locked", False),
            "fx": [f.get("id") or f.get("type") for f in t.get("fx", [])],
            "sends": t.get("sends"), "noteCount": len(notes), "barSpan": span,
            "automation": [a.get("target") for a in t.get("automation", [])],
            "audioClips": len(t.get("audioClips", []))})
    return json.dumps(out, indent=1)

def t_get_song_region(args):
    """Notes + automation WINDOWED to [from_bar, to_bar] (1-indexed, inclusive),
    optionally filtered to named tracks — the scoped read for large songs."""
    name = resolve_song_name(args["song"])
    path = os.path.join(SONGS, f"{name}.json")
    if not os.path.exists(path):
        return f"no such song '{name}'"
    song = json.load(open(path))
    b0 = (float(args.get("from_bar", 1)) - 1.0) * 4.0
    b1 = float(args.get("to_bar", song.get("lengthBars", 1e9))) * 4.0
    want = args.get("tracks")
    if isinstance(want, str):
        want = [w.strip() for w in want.split(",") if w.strip()]
    out = {"song": name, "from_bar": args.get("from_bar", 1),
           "to_bar": args.get("to_bar"), "bpm": song.get("bpm"), "tracks": []}
    for t in song.get("tracks", []):
        if want and t.get("name") not in want:
            continue
        notes = [dict(n, _idx=i) for i, n in enumerate(t.get("notes", []))
                 if b0 <= n.get("start", 0) < b1]
        autos = [{"target": a.get("target"),
                  "points": [pt for pt in a.get("points", []) if b0 <= pt.get("beat", 0) < b1]}
                 for a in t.get("automation", [])]
        out["tracks"].append({"name": t.get("name"), "noteCount": len(notes),
                              "notes": notes,
                              "automation": [a for a in autos if a["points"]]})
    return json.dumps(out, indent=1)

def t_update_song_meta(args):
    """Change song-level fields: bpm, swing, masterGainDb, master chain, lengthBars, key."""
    name = resolve_song_name(args["song"])
    path = os.path.join(SONGS, f"{name}.json")
    _ensure_prop(name, path)
    if not os.path.exists(path):
        return f"no such song '{name}'"
    song = json.load(open(path))
    changed = []
    for k in ("bpm", "masterGainDb", "lengthBars", "key", "swing", "master", "tempoMap"):
        if k in args and args[k] is not None:
            v = args[k]
            if isinstance(v, str) and k in ("swing", "master", "tempoMap"):
                try:
                    v = json.loads(v)
                except json.JSONDecodeError as e:
                    return f"{k} is not valid JSON: {e}"
            song[k] = v
            changed.append(k)
    errs = validate_song(song)
    if errs:
        return "INVALID after update:\n- " + "\n- ".join(errs)
    _awrite(path, song)
    _rc(name, "update_song_meta", fields=[f"meta:{k}" for k in changed],
        summary=f"meta: {', '.join(changed)}")
    return f"OK: updated {', '.join(changed)} in songs/{name}.json"

def t_add_track(args):
    """Add a new track: name + source ({kind:faust|sample|vst3, id/kit/plugin}) + optional fx/gainDb/notes."""
    name = resolve_song_name(args["song"])
    path = os.path.join(SONGS, f"{name}.json")
    _ensure_prop(name, path)
    if not os.path.exists(path):
        return f"no such song '{name}'"
    song = json.load(open(path))
    track = args["track_json"]
    if isinstance(track, str):
        try:
            track = json.loads(track)
        except json.JSONDecodeError as e:
            return f"track_json is not valid JSON: {e}"
    track.setdefault("notes", [])
    if not track["notes"]:
        track["notes"] = [{"start": 0, "len": 0.25, "pitch": 60, "vel": 0.5}]
    song["tracks"].append(track)
    errs, pre = validate_scoped(song, [track.get("name")])
    if errs:
        return "INVALID after add:\n- " + "\n- ".join(errs)
    if pre:
        pass  # pre-existing wounds elsewhere never block adding a clean track
    _awrite(path, song)
    _rc(name, "add_track", fields=[f"track:{track.get('name', '?')}"],
        summary=f"added track {track.get('name', '?')}")
    return f"OK: track '{track.get('name','?')}' added ({len(song['tracks'])} total)"

def t_keep_jam(args):
    """CAPTURE LAW full form (docs/THE_BAND_SEAT.md): a kept jam becomes MATERIAL of
    the current song — take tracks land as new 'jam:<role>' lanes, notes/automation
    beat-offset to at_bar (default: appended after the song's end as its own
    section), lengthBars extended, name collisions suffixed. Beats are tempo-
    agnostic: the song's bpm rules the feel; big deltas are called out."""
    name = resolve_song_name(args["song"])
    path = os.path.join(SONGS, f"{name}.json")
    if not os.path.exists(path):
        return f"no such song '{name}'"
    tk = re.sub(r"[^a-z0-9_.]", "", str(args["take"]).lower()).replace(".json", "")
    tpath = os.path.join(SONGS, f"{tk}.json")
    if not os.path.exists(tpath):
        return f"no such take '{tk}' (kept jams live as songs/jam_<genre>_<n>.json)"
    song = json.load(open(path))
    take = json.load(open(tpath))
    src_tracks = [t for t in take.get("tracks", []) if t.get("notes")]
    if not src_tracks:
        return f"take '{tk}' has no notes to keep"
    cur_bars = float(song.get("lengthBars", 4))
    at_bar = args.get("at_bar")
    at_bar = float(at_bar) if at_bar is not None else float(int(cur_bars + 0.999999))
    off = at_bar * 4.0
    prefix = re.sub(r"[^a-z0-9_]", "", str(args.get("prefix", "jam"))) or "jam"
    existing = {t.get("name") for t in song.get("tracks", [])}
    tbuses = {b.get("id") for b in song.get("buses", [])}
    take_bars = float(take.get("lengthBars", 0)) or max(
        float(n["start"]) + float(n.get("len", 0.25))
        for t in src_tracks for n in t["notes"]) / 4.0
    added = []
    for t in src_tracks:
        nm0 = f"{prefix}:{t.get('name', 'take')}"
        nm, k = nm0, 2
        while nm in existing:
            nm = f"{nm0}_{k}"
            k += 1
        existing.add(nm)
        nt = {"name": nm, "source": t.get("source", {"kind": "faust", "id": "keys_soft"}),
              "gainDb": t.get("gainDb", -6), "pan": t.get("pan", 0), "fx": t.get("fx", []),
              "notes": [dict(n, start=round(float(n["start"]) + off, 6)) for n in t["notes"]]}
        if t.get("automation"):
            nt["automation"] = [{"target": a.get("target"),
                                 "points": [dict(p, beat=round(float(p.get("beat", 0)) + off, 6))
                                            for p in a.get("points", [])]}
                                for a in t["automation"]]
        if t.get("sends"):
            nt["sends"] = [s for s in t["sends"] if s.get("bus") in tbuses]
        song["tracks"].append(nt)
        added.append(nm)
    song["lengthBars"] = max(cur_bars, at_bar + take_bars)
    secs = song.setdefault("sections", [])
    if not any(abs(float(s.get("startBar", -1)) - at_bar) < 1e-6 for s in secs):
        secs.append({"name": prefix, "startBar": at_bar})
        secs.sort(key=lambda s: float(s.get("startBar", 0)))
    errs, pre = validate_scoped(song, added)
    if errs:
        return "INVALID after keep_jam:\n- " + "\n- ".join(errs)
    _awrite(path, song)
    _rc(name, "keep_jam", fields=[f"track:{nm}" for nm in added], track_wild=added,
        summary=f"kept jam '{tk}' at bar {at_bar:g} ({len(added)} lanes)")
    tb, sb = float(take.get("bpm", song.get("bpm", 120))), float(song.get("bpm", 120))
    bwarn = ""
    if abs(tb - sb) > 1.0:
        bwarn = (f" NOTE: the take was played at {tb:g} bpm, this song runs {sb:g} — "
                 f"beats carry exactly, the FEEL now rides the song's tempo.")
    return (f"OK: jam '{tk}' kept INTO songs/{name}.json — {len(added)} new lane(s) "
            f"({', '.join(added)}) at bar {at_bar:g}, length now {song['lengthBars']:g} "
            f"bars, section '{prefix}' marked.{bwarn}")

def t_add_topline(args):
    """Add a vocal-hook TOPLINE melody track — the singable lead a vocalist would
    follow, written section-aware: HOOK (choruses/drops repeat the first hook
    verbatim), LIFT (chorus climbs a 5th-8ve above the verse, peaking late), TALK
    (verses denser/lower/stepwise, varied per seed), SPACE (intro/break/outro
    rest). Notes land on chord tones at strong beats. Renderable as-is (pluck);
    swap its source to a voice and add words via write_lyrics + sing to voice it."""
    name = resolve_song_name(args["song"])
    path = os.path.join(SONGS, f"{name}.json")
    _ensure_prop(name, path)
    if not os.path.exists(path):
        return f"no such song '{name}'"
    song = json.load(open(path))
    seed = int(args.get("seed", 0))
    try:
        if os.path.join(ROOT, "tools") not in sys.path:
            sys.path.insert(0, os.path.join(ROOT, "tools"))
        import topline as _topline
        notes = _topline.generate(song, seed)
    except Exception as e:
        return f"topline failed: {e}"
    if not notes:
        return ("no topline written — the song needs chorus/verse sections AND a "
                "chord field (add sections, or run harmonize/generate_loop first)")
    track = str(args.get("track", "topline"))
    song["tracks"] = [t for t in song.get("tracks", []) if t.get("name") != track]
    song["tracks"].append({"name": track, "source": {"kind": "faust", "id": "pluck"},
                           "gainDb": -8, "notes": notes})
    _awrite(path, song)
    _rc(name, "add_topline", fields=[f"track:{track}"], track_wild=[track],
        summary=f"topline {len(notes)} notes")
    return (f"OK: topline '{track}' = {len(notes)} notes (section-aware hook, seed "
            f"{seed}). Swap its source to a voice + write_lyrics + sing to voice it.")

def t_align_lyrics(args):
    """Auto-melisma: set each lyric line's melisma so its words COVER a melody
    track's notes (default 'topline') — the extra notes ride the last word as a
    sung melisma (no silent notes). Run after write_lyrics + add_topline."""
    name = resolve_song_name(args["song"])
    path = os.path.join(SONGS, f"{name}.json")
    _ensure_prop(name, path)
    if not os.path.exists(path):
        return f"no such song '{name}'"
    song = json.load(open(path))
    if not song.get("lyrics"):
        return "no lyrics to align — run write_lyrics first"
    if os.path.join(ROOT, "tools") not in sys.path:
        sys.path.insert(0, os.path.join(ROOT, "tools"))
    import align_lyrics
    track = str(args.get("track", "topline"))
    song, changed, short = align_lyrics.align(song, track)
    _awrite(path, song)
    _rc(name, "align_lyrics", fields=["meta:lyrics"], summary=f"{changed} lines")
    msg = (f"OK: aligned {changed} lyric line(s) to '{track}' (auto-melisma — words "
           f"cover the melody)")
    if short:
        msg += f"; {short} line(s) have MORE words than notes — add notes or split them"
    return msg

def _check_fx_entry(f, avail, vsts):
    """One SongFx entry -> error string or None. Legal shapes:
    {"id": "fx_*", params}, {"type": "eq"|"comp", params},
    {"id": "vst3:<name>", preset?, params?}, any + "bypass": true."""
    if f.get("type") in ("eq", "comp"):
        return None       # built-ins: eq {loFreq,loGain,hiFreq,hiGain,midFreq,midGain,midQ,midFreq2,...} / comp {threshold,ratio,attack,release,outputDb}
    fid = str(f.get("id") or "")
    if fid.startswith("vst3:"):
        want = fid[5:].strip().lower()
        if vsts and not any(want in v.lower() for v in vsts):
            return f"fx id '{fid}' not in scan cache {vsts}"
        p = f.get("preset")
        if p and not os.path.exists(p if os.path.isabs(p) else os.path.join(ROOT, p)):
            return f"fx preset not found: {p}"
        return None
    if fid not in avail:
        return (f"fx id '{fid}' not available. fx: {sorted(a for a in avail if a.startswith('fx_'))}"
                f", type eq|comp, or \"vst3:<plugin>\" (optionally with preset blob)")
    return None

def t_set_track_fx(args):
    """Set a track's FX chain: array of {id, params, bypass?} — faust fx_*, {"type":"eq"|"comp"},
    or {"id":"vst3:<name>", "preset": <blob path>}. Order matters (array = signal flow)."""
    name = resolve_song_name(args["song"])
    path = os.path.join(SONGS, f"{name}.json")
    _ensure_prop(name, path)
    if not os.path.exists(path):
        return f"no such song '{name}'"
    song = json.load(open(path))
    tname = args["track"]
    matches = [t for t in song["tracks"] if t.get("name") == tname]
    if not matches:
        return f"no track '{tname}'. tracks: {[t.get('name') for t in song['tracks']]}"
    fx = args["fx"]
    if isinstance(fx, str):
        try:
            fx = json.loads(fx)
        except json.JSONDecodeError as e:
            return f"fx is not valid JSON: {e}"
    avail = set(list_instruments())
    vsts = vst_names()
    for f in fx:
        err = _check_fx_entry(f, avail, vsts)
        if err:
            return err
    matches[0]["fx"] = fx
    _awrite(path, song)
    _rc(name, "set_track_fx", fields=[f"track:{tname}:fx"],
        summary=f"{tname} fx = {[f.get('id') or f.get('type') for f in fx]}")
    return (f"OK: {tname} fx chain = {[f.get('id') or f.get('type') for f in fx]}"
            + _track_verdict(matches[0]))

def _semantic_search(query, k=8):
    """SEMANTIC EARS (V53): CLAP text->audio neighbors via tools/clap_query.py.
    Runs as a SUBPROCESS so torch/CLAP never load into the resident MCP server.
    Best-effort — returns [] on any absence/failure (no index, no checkpoint,
    torch missing, timeout), so search silently falls back to substring."""
    if not query.strip() or os.environ.get("SOTADAW_NO_SEMANTIC"):
        return []
    if not os.path.exists(os.path.join(ROOT, "library", "embeddings.npz")):
        return []
    py = VENV_PY if os.path.exists(VENV_PY) else "python3"
    try:
        r = subprocess.run([py, os.path.join(ROOT, "tools", "clap_query.py"),
                            query, "--k", str(k)],
                           capture_output=True, text=True, timeout=90)
        d = json.loads(r.stdout or "{}")
        if d.get("available"):
            return [{"name": x.get("name"), "kind": x.get("kind"),
                     "path": x.get("path"), "category": x.get("category"),
                     "score": x.get("score")}
                    for x in d.get("results", [])]
    except Exception:
        pass
    return []


def t_search_library(args):
    """Search the indexed library by WORDS (substring, exact) and by VIBE
    (CLAP semantic neighbors, when a library/embeddings.npz index exists) —
    e.g. 'a dusty lo-fi snare' ranks the user's own sounds. Substring hits win
    exact matches; the `semantic` list surfaces sounds the words can't name."""
    lib_path = os.path.join(ROOT, "library.json")
    if not os.path.exists(lib_path):
        return "library.json missing — run tools/index_library.py"
    lib = json.load(open(lib_path))
    query = str(args.get("query", ""))
    q = query.lower().split()
    hits = {"instruments": [i for i in lib["instruments"] if any(w in i for w in q)],
            "fx": [i for i in lib["fx"] if any(w in i for w in q)],
            "kits": [k for k in lib["kits"] if any(w in k for w in q)],
            "vst3": [v for v in lib["vst3"] if any(w in v.lower() for w in q)],
            "samples": [s_ for s_ in lib["samples"]
                        if any(w in s_["name"].lower() or w in s_.get("tags", []) for w in q)][:25]}
    hits["semantic"] = _semantic_search(query)
    return json.dumps(hits, indent=1)

def t_sound_neighbors(args):
    """Find the library sounds nearest to an audio file (a render, clip, or stem)
    by CLAP timbre — the reference-match axis. Subprocess-isolated (torch stays out
    of the resident MCP server); a clear message when the CLAP index is absent."""
    wav = str(args.get("wav") or args.get("path") or "")
    if not wav:
        return "need a wav path (a render, clip, or stem)"
    p = wav if os.path.isabs(wav) else os.path.join(ROOT, wav)
    if not os.path.exists(p):
        alt = os.path.join(SONGS, os.path.basename(wav))
        p = alt if os.path.exists(alt) else p
    if not os.path.exists(p):
        return f"no such wav: {wav}"
    if not os.path.exists(os.path.join(ROOT, "library", "embeddings.npz")):
        return "no CLAP index — run tools/embed_library.py to enable semantic neighbors"
    py = VENV_PY if os.path.exists(VENV_PY) else "python3"
    try:
        r = subprocess.run([py, os.path.join(ROOT, "tools", "clap_query.py"),
                            "--audio", p, "--k", str(int(args.get("k", 8)))],
                           capture_output=True, text=True, timeout=120)
        d = json.loads(r.stdout or "{}")
        if not d.get("available"):
            return f"neighbors unavailable: {d.get('reason', '?')}"
        return json.dumps(d.get("results", []), indent=1)
    except Exception as e:
        return f"neighbors failed: {e}"

def t_chords_from_audio(args):
    """Detect a chord lane FROM AUDIO — CQT chroma read through the same
    maj/min/dom7 grammar as the symbolic vote (best on a harmonic/no-drums stem;
    drums bury chroma). Two modes: standalone (wav+bpm+bars -> chords) or FUSED
    (song+wav -> writes song.chords[] fusing the audio witness with the song's
    own symbols)."""
    wav = str(args.get("wav") or "")
    if not wav:
        return "need a wav path (a render, reference, or harmonic stem)"
    p = wav if os.path.isabs(wav) else os.path.join(ROOT, wav)
    if not os.path.exists(p):
        alt = os.path.join(SONGS, os.path.basename(wav))
        p = alt if os.path.exists(alt) else p
    if not os.path.exists(p):
        return f"no such wav: {wav}"
    if os.path.join(ROOT, "tools") not in sys.path:
        sys.path.insert(0, os.path.join(ROOT, "tools"))
    try:
        if args.get("song"):
            name = resolve_song_name(args["song"])
            spath = os.path.join(SONGS, f"{name}.json")
            if not os.path.exists(spath):
                return f"no such song '{name}'"
            song = json.load(open(spath))
            import chordvote
            ch = chordvote.chord_map(song, audio_wav=p, audio_bpm=args.get("bpm"))
            if not ch:
                return "no chords detected (audio too quiet or non-harmonic)"
            song["chords"] = ch
            _awrite(spath, song)
            _rc(name, "chords_from_audio", fields=["meta:chords"], summary=f"{len(ch)} bars")
            return (f"OK: {name}.chords = {len(ch)} bars (audio+symbols fused): "
                    + " ".join(c["chord"] for c in ch[:8]))
        import chords_audio
        ch = chords_audio.chords(p, float(args.get("bpm", 120)), int(args.get("bars", 8)))
        return json.dumps(ch, indent=1) if ch else "no chords detected"
    except Exception as e:
        return f"chords_from_audio failed: {e}"

def t_export_midi(args):
    name = resolve_song_name(args["song"])
    out = os.path.join(SONGS, f"{name}.mid")
    rc, o, e = run([VENV_PY if os.path.exists(VENV_PY) else "python3",
                    os.path.join(ROOT, "tools", "midi_bridge.py"), "export",
                    os.path.join(SONGS, f"{name}.json"), out], timeout=60)
    return (o + e).strip() or f"exported -> {out}"

def t_import_midi(args):
    src = args["midi_path"]
    if not os.path.isabs(src):
        src = os.path.join(ROOT, src)
    name = resolve_song_name(args["song"])
    rc, o, e = run([VENV_PY if os.path.exists(VENV_PY) else "python3",
                    os.path.join(ROOT, "tools", "midi_bridge.py"), "import",
                    src, os.path.join(SONGS, f"{name}.json")], timeout=60)
    if rc == 0:
        _rc(name, "import_midi", fields=["*"], summary=f"MIDI import {os.path.basename(src)}")
    return (o + e).strip()

def t_write_lyrics(args):
    """Write timestamp-aware lyrics: lines aligned to bars/beats. The agent knows WHERE every word lands."""
    name = resolve_song_name(args["song"])
    path = os.path.join(SONGS, f"{name}.json")
    _ensure_prop(name, path)
    if not os.path.exists(path):
        return f"no such song '{name}'"
    song = json.load(open(path))
    lyr = args["lyrics"]
    if isinstance(lyr, str):
        try:
            lyr = json.loads(lyr)
        except json.JSONDecodeError as e:
            return f"lyrics is not valid JSON: {e}"
    total = float(song.get("lengthBars", 4)) * 4
    for ln in lyr:
        if not isinstance(ln.get("beat"), (int, float)) or not ln.get("text"):
            return "each lyric line needs {beat: <number>, text: <string>} (beat = absolute beat position)"
        if ln["beat"] < 0 or ln["beat"] >= total:
            return f"lyric at beat {ln['beat']} outside song (0..{total})"
    song["lyrics"] = sorted(lyr, key=lambda l: l["beat"])
    _awrite(path, song)
    _rc(name, "write_lyrics", fields=["meta:lyrics"], summary=f"{len(lyr)} lyric lines")
    # W124 THE ALIGNMENT GUARD: singing aligns words to MELODY NOTE STARTS —
    # a word at a beat with no note gets mis-sung or dropped silently.
    # Warn (never block: lyrics may precede the melody) with the fix path.
    warn = ""
    mel = next((t for t in song.get("tracks", [])
                if t.get("name") == str(args.get("track", "lead")) and t.get("notes")),
               None)
    if mel is not None:
        starts = sorted(round(float(n["start"]), 4) for n in mel["notes"])
        def _hit(b):
            import bisect
            i = bisect.bisect_left(starts, b - 0.06)
            return i < len(starts) and abs(starts[i] - b) <= 0.06
        misses = [l["beat"] for l in lyr if not _hit(float(l["beat"]))]
        if misses and len(misses) * 10 > len(lyr):   # >10% off the melody
            warn = (f" WARNING: {len(misses)}/{len(lyr)} words sit on beats with NO "
                    f"'{args.get('track', 'lead')}' note (first: {misses[:4]}) — they will "
                    "mis-sing. use_tool(phrase_map) gives the exact note beats.")
        elif len(lyr) != len(starts):
            warn = (f" note: {len(lyr)} words vs {len(starts)} melody notes "
                    "(one word per note sings cleanest; phrase_map has the counts).")
    return (f"OK: {len(lyr)} lyric lines written, beat-aligned "
            f"(export_midi embeds them as MIDI lyric events).{warn}")

def t_import_als(args):
    """THE BRIDGE: import an Ableton Live .als project as a song (symbolic MIDI layer)."""
    src = args["als_path"]
    if not os.path.isabs(src):
        src = os.path.join(ROOT, src)
    if not os.path.exists(src):
        return f"no such file: {src}"
    name = resolve_song_name(args["song"])
    rc, o, e = run([sys.executable, os.path.join(ROOT, "tools", "als_import.py"),
                    src, os.path.join(SONGS, f"{name}.json")], timeout=120)
    return (o + e).strip()

def _bridge(args, key, tool, timeout=180):
    src = args[key]
    if not os.path.isabs(src):
        src = os.path.join(ROOT, src)
    if not os.path.exists(src):
        return f"no such file: {src}"
    name = resolve_song_name(args["song"])
    py = VENV_PY if os.path.exists(VENV_PY) else sys.executable
    rc, o, e = run([py, os.path.join(ROOT, "tools", tool),
                    src, os.path.join(SONGS, f"{name}.json")], timeout=timeout)
    return (o + e).strip()[-1500:]

def t_import_dawproject(args):
    """BRIDGE: import a .dawproject (Bitwig/Cubase/Nuendo/Studio One) — notes, audio clips, tempo, mixer."""
    return _bridge(args, "dawproject_path", "dawproject_import.py")

def t_import_flp(args):
    """BRIDGE: import an FL Studio .flp — channels, patterns, playlist placements."""
    return _bridge(args, "flp_path", "flp_import.py")

def t_get_selection(args):
    """What the user has SELECTED in the UI right now (selection = context)."""
    p = os.path.join(ROOT, "agent", "ipc", "context.json")
    if not os.path.exists(p):
        return "no selection — the user has not pointed at anything; operate on the whole song"
    try:
        c = json.load(open(p))
    except Exception as e:
        return f"selection unreadable: {e}"
    r = c.get("rendered") or ""
    return r.strip() or "no selection — the user has not pointed at anything; operate on the whole song"

def t_import_rekordbox(args):
    """THE PRO-DJ BRIDGE: rekordbox collection.xml -> library dj_tracks + a ready dj_set plan."""
    xml = args.get("xml", "")
    p = xml if os.path.isabs(xml) else os.path.join(ROOT, xml)
    if not os.path.exists(p):
        return f"no such file: {xml}"
    py = VENV_PY if os.path.exists(VENV_PY) else sys.executable
    cmd = [py, os.path.join(ROOT, "tools", "rekordbox_import.py"), p]
    if args.get("playlist"):
        cmd += ["--playlist", str(args["playlist"])]
    if args.get("set_name"):
        cmd += ["--set-name", re.sub(r"[^a-z0-9_]", "", str(args["set_name"]).lower())]
    rc, o, e = run(cmd, timeout=120)
    if rc != 0:
        return f"rekordbox_import failed:\n{(o + e)[-800:]}"
    return o.strip() + "\nRekordbox bpm/key/first-beat data is AUTHORITATIVE — run dj_set with the printed --bpms/--offsets/--keys instead of re-detecting."

def t_duplicate_bars(args):
    """THE ARRANGEMENT CALCULUS: copy bars [fromBar,toBar) to atBar, `times` consecutive copies —
    server-side, instant, zero tokens. HOW LONG TRACKS ARE BUILT: compose an 8-32 bar seed in
    full detail, then stamp it across the arrangement. Optional `tracks` filter (names)."""
    name, path, song = _load_song(args, mutate=True)
    if song is None:
        return f"no such song '{name}'"
    try:
        a, b = float(args["fromBar"]) * 4.0, float(args["toBar"]) * 4.0
        at = float(args["atBar"]) * 4.0
        times = max(1, min(64, int(args.get("times", 1))))
    except (KeyError, TypeError, ValueError) as e:
        return f"need numeric fromBar/toBar/atBar (+optional times): {e}"
    if not b > a:
        return "toBar must be > fromBar"
    span = b - a
    want = args.get("tracks")
    if isinstance(want, str):
        try:
            want = json.loads(want)
        except json.JSONDecodeError:
            want = [w.strip() for w in want.split(",") if w.strip()]
    copied = 0
    for t in song["tracks"]:
        if want and t.get("name") not in want:
            continue
        seed = [n for n in t.get("notes", []) if a <= n["start"] < b]
        for k in range(times):
            off = at + k * span - a
            for n in seed:
                t["notes"].append({"start": round(n["start"] + off, 4), "len": n["len"],
                                   "pitch": n["pitch"], "vel": n["vel"]})
                copied += 1
        t.get("notes", []).sort(key=lambda n: n["start"])
    end_bar = (at + times * span) / 4.0
    if float(song.get("lengthBars", 4)) < end_bar:
        song["lengthBars"] = int(end_bar + 0.999)
    _awrite(path, song)
    _rc(name, "duplicate_bars", fields=["meta:lengthBars"],
        track_wild=want or [t.get("name") for t in song["tracks"]],
        summary=f"bars {args['fromBar']}-{args['toBar']} -> {args['atBar']} x{times}")
    return (f"OK: bars {args['fromBar']}-{args['toBar']} stamped at {args['atBar']} x{times} "
            f"({copied} notes copied server-side; lengthBars={song['lengthBars']}). "
            f"Carve variation with clear_bars; add motion with automate.")

def t_clear_bars(args):
    """Delete all notes in bars [fromBar,toBar) — carve breakdowns/drops out of tiled material.
    Optional `tracks` filter (names): clear only drums for a breakdown, only melody for a drop."""
    name, path, song = _load_song(args, mutate=True)
    if song is None:
        return f"no such song '{name}'"
    try:
        a, b = float(args["fromBar"]) * 4.0, float(args["toBar"]) * 4.0
    except (KeyError, TypeError, ValueError) as e:
        return f"need numeric fromBar/toBar: {e}"
    want = args.get("tracks")
    if isinstance(want, str):
        try:
            want = json.loads(want)
        except json.JSONDecodeError:
            want = [w.strip() for w in want.split(",") if w.strip()]
    removed = 0
    for t in song["tracks"]:
        if want and t.get("name") not in want:
            continue
        before = len(t.get("notes", []))
        t["notes"] = [n for n in t.get("notes", []) if not (a <= n["start"] < b)]
        removed += before - len(t["notes"])
    _awrite(path, song)
    _rc(name, "clear_bars", track_wild=want or [t.get("name") for t in song["tracks"]],
        summary=f"cleared bars {args['fromBar']}-{args['toBar']}")
    return f"OK: cleared {removed} notes in bars {args['fromBar']}-{args['toBar']}" + (f" on {want}" if want else "")

def t_save_preset(args):
    """Capture a vst3 track's CURRENT plugin state (after your set_track_param design moves)
    as a named preset -> library/presets/<name>.preset. Reuse via use_preset on any track."""
    name, path, song = _load_song(args)
    if song is None:
        return f"no such song '{name}'"
    pname = re.sub(r"[^a-z0-9_]", "", str(args["preset_name"]).lower())
    out = os.path.join(ROOT, "library", "presets", f"{pname}.preset")
    rc, o, e = run([M1, "capture-state", path, args["track"], out], timeout=300)
    if rc != 0:
        return f"capture failed: {(o + e)[-300:]}"
    return (o.strip().splitlines() or ["captured"])[-1] + f"\nUse via use_preset(track, 'library/presets/{pname}.preset')"

def t_use_preset(args):
    """Load a captured preset onto a vst3 track (sets source.preset; state restores at build)."""
    name, path, song = _load_song(args, mutate=True)
    if song is None:
        return f"no such song '{name}'"
    tname = args["track"]
    matches = [t for t in song["tracks"] if t.get("name") == tname]
    if not matches:
        return f"no track '{tname}'"
    rel = args["preset"]
    if not os.path.exists(rel if os.path.isabs(rel) else os.path.join(ROOT, rel)):
        avail = sorted(os.listdir(os.path.join(ROOT, "library", "presets"))) if os.path.isdir(os.path.join(ROOT, "library", "presets")) else []
        return f"no such preset '{rel}'. available: {avail}"
    matches[0].setdefault("source", {})["preset"] = rel
    _awrite(path, song)
    _rc(name, "use_preset", fields=[f"track:{tname}:source"], summary=f"{tname} preset {rel}")
    return f"OK: {tname} loads preset {rel} (params can still tweak on top)"

def t_edit_clip(args):
    """PER-CLIP AUDIO EDIT — the agent twin of the hands' HB3.1 clip verbs. Thin wrapper:
    resolve the track/clip, call surgical.edit_audio_clip (the pure math), validate, write
    the proposal, file a TRACK-SCOPED receipt (mirrors update_track — the clip lives on that
    track). The scope law then allows exactly that track's clip changes."""
    name, path, song = _load_song(args, mutate=True)
    if song is None:
        return f"no such song '{name}'"
    try:
        trs = surgical.resolve_tracks(song, args.get("track"))
    except (ValueError, KeyError) as e:
        return f"EDIT_CLIP ABORT: {e}"
    if not trs:
        return f"no track matched '{args.get('track')}'"
    ti = trs[0][0]
    tname = song["tracks"][ti].get("name", f"#{ti}")
    import copy as _copy
    work = _copy.deepcopy(song)
    try:
        summary = surgical.edit_audio_clip(work, ti, int(args.get("clip", 0)),
                                           args.get("op"), args.get("value"))
    except (ValueError, KeyError, TypeError) as e:
        return f"EDIT_CLIP ABORT (nothing written): {e}"
    if args.get("preview"):
        return f"PREVIEW (not written): {summary} on '{tname}'"
    errs = validate_song(work)
    if errs:
        return "EDIT_CLIP ABORT — result would be invalid:\n- " + "\n- ".join(errs)
    _awrite(path, work)
    _rc(name, "edit_clip", fields=[f"track:{tname}"], track_wild=[tname],
        summary=f"{summary} on {tname}")
    return f"CLIP: {summary} on '{tname}' — receipt filed (scope = that track's clips)."


def t_edit_section(args):
    """SECTIONS AS OBJECTS: add/rename/move/remove/duplicate named arrangement sections.
    duplicate = the killer op: stamps the section's bars right after itself (all tracks +
    automation-free note copy), shifting later sections — 'double the drop' in one call."""
    name, path, song = _load_song(args, mutate=True)
    if song is None:
        return f"no such song '{name}'"
    op = str(args.get("op", "")).lower()
    secs = song.setdefault("sections", [])
    def find(nm):
        nm = str(nm).lower()
        return next((s for s in secs if str(s.get("name", "")).lower() == nm), None)
    if op == "add":
        if find(args.get("name")):
            return f"section '{args['name']}' already exists"
        secs.append({"name": str(args["name"]), "startBar": float(args.get("at_bar", 0))})
    elif op == "rename":
        s = find(args.get("name"))
        if s is None:
            return f"no section '{args.get('name')}'. have: {[x['name'] for x in secs]}"
        s["name"] = str(args["new_name"])
    elif op == "move":
        s = find(args.get("name"))
        if s is None:
            return f"no section '{args.get('name')}'"
        s["startBar"] = max(0.0, float(args["to_bar"]))
    elif op == "remove":
        s = find(args.get("name"))
        if s is None:
            return f"no section '{args.get('name')}'"
        secs.remove(s)
    elif op == "duplicate":
        s = find(args.get("name"))
        if s is None:
            return f"no section '{args.get('name')}'. have: {[x['name'] for x in secs]}"
        ordered = sorted(secs, key=lambda x: x["startBar"])
        i = ordered.index(s)
        start = float(s["startBar"])
        end = float(ordered[i + 1]["startBar"]) if i + 1 < len(ordered) else float(song.get("lengthBars", 4))
        span_bars = end - start
        if span_bars <= 0:
            return "section has zero length"
        a, b, off = start * 4.0, end * 4.0, span_bars * 4.0

        def dup_points(auto_list):
            """Shift automation points at/after the span end; copy in-span points +off."""
            for au in auto_list or []:
                pts = au.get("points", [])
                seed = [p for p in pts if a <= float(p["beat"]) < b]
                for p in pts:
                    if float(p["beat"]) >= b:
                        p["beat"] = round(float(p["beat"]) + off, 4)
                pts.extend({**p, "beat": round(float(p["beat"]) + off, 4)} for p in seed)
                pts.sort(key=lambda p: float(p["beat"]))

        for t in song["tracks"]:
            seed = [n for n in t.get("notes", []) if a <= n["start"] < b]
            shifted = [n for n in t.get("notes", []) if n["start"] >= b]
            for n in shifted:
                n["start"] = round(n["start"] + off, 4)
            for n in seed:
                t["notes"].append({"start": round(n["start"] + off, 4), "len": n["len"],
                                   "pitch": n["pitch"], "vel": n["vel"]})
            t.get("notes", []).sort(key=lambda n: n["start"])
            dup_points(t.get("automation"))
            clips = t.get("audioClips", [])
            cseed = [c for c in clips if a <= float(c.get("startBeat", 0)) < b]
            for c in clips:
                if float(c.get("startBeat", 0)) >= b:
                    c["startBeat"] = round(float(c["startBeat"]) + off, 4)
            clips.extend({**c, "startBeat": round(float(c.get("startBeat", 0)) + off, 4)}
                         for c in cseed)
        dup_points(song.get("automation"))
        lyr = song.get("lyrics", [])
        lseed = [l for l in lyr if a <= float(l.get("beat", 0)) < b]
        for l in lyr:
            if float(l.get("beat", 0)) >= b:
                l["beat"] = round(float(l["beat"]) + off, 4)
        lyr.extend({**l, "beat": round(float(l.get("beat", 0)) + off, 4)} for l in lseed)
        for x in secs:
            if float(x["startBar"]) >= end and x is not s:
                x["startBar"] = float(x["startBar"]) + span_bars
        secs.append({"name": f"{s['name']} 2", "startBar": end})
        song["lengthBars"] = float(song.get("lengthBars", 4)) + span_bars
    else:
        return "op must be add|rename|move|remove|duplicate"
    secs.sort(key=lambda x: x["startBar"])
    _awrite(path, song)
    _rc(name, "edit_section",
        fields=["meta:sections", "meta:lengthBars", "meta:lyrics", "meta:automation"],
        track_wild=[t.get("name") for t in song["tracks"]] if op in ("duplicate", "move", "remove") else None,
        summary=f"edit_section {op} '{args.get('name')}'")
    return f"OK: {op} -> sections now {[(x['name'], x['startBar']) for x in secs]}, lengthBars {song.get('lengthBars')}"

def t_set_clip_slot(args):
    """PERFORMANCE VIEW: author a launcher slot (track x scene cell) — a loopable pattern
    launched live, bar-quantised. notes[] inline, or from_bar copies arrangement bars,
    or clear:true. Scenes auto-grow."""
    name, path, song = _load_song(args, mutate=True)
    if song is None:
        return f"no such song '{name}'"
    tname = args["track"]
    tr = next((t for t in song["tracks"] if t.get("name") == tname), None)
    if tr is None:
        return f"no track '{tname}'"
    sc = int(args["scene"])
    if not 0 <= sc <= 15:
        return "scene must be 0..15"
    slots = tr.setdefault("slots", [])
    while len(slots) <= sc:
        slots.append(None)
    if args.get("clear"):
        slots[sc] = None
    else:
        length = float(args.get("length_beats", 16))
        if not 1 <= length <= 128:
            return "length_beats must be 1..128"
        if args.get("audio_file"):        # audio loop slot (optionally warped to song tempo)
            af = args["audio_file"]
            af_abs = af if os.path.isabs(af) else os.path.join(ROOT, af)
            if not os.path.exists(af_abs):
                return f"no such audio file: {af}"
            slot = {"name": str(args.get("slot_name", f"{tname} {chr(65 + sc % 26)}")),
                    "lengthBeats": length, **({"follow": str(args["follow"])} if args.get("follow") in ("next","any","stop") else {}), **({"followChance": max(0.0, min(1.0, float(args["follow_chance"])))} if args.get("follow_chance") is not None else {}), "audioFile": af,
                    "offsetSec": float(args.get("offset_sec", 0))}
            if args.get("source_bpm"):
                slot["sourceBpm"] = float(args["source_bpm"])
            slots[sc] = slot
            scenes = song.setdefault("scenes", [])
            while len(scenes) <= sc:
                scenes.append({"name": f"Scene {len(scenes) + 1}"})
            if args.get("scene_name"):
                scenes[sc]["name"] = str(args["scene_name"])
            _awrite(path, song)
            _rc(name, "set_clip_slot", fields=["meta:scenes", f"track:{tname}:slots"],
                summary=f"slot {tname} x scene {sc+1} (audio)")
            warped = f", warped from {slot['sourceBpm']}bpm" if "sourceBpm" in slot else ""
            return (f"OK: slot [{tname} x scene {sc+1}] = audio loop {os.path.basename(af)} "
                    f"/ {length} beats{warped}. Launchable in the Live view.")
        if args.get("notes"):
            notes = args["notes"]
        else:
            fb = float(args.get("from_bar", 0)) * 4.0
            notes = [dict(n, start=round(n["start"] - fb, 4)) for n in tr.get("notes", [])
                     if fb <= n["start"] < fb + length]
        for n in notes:
            if not (isinstance(n.get("start"), (int, float)) and 0 <= n["start"] < length
                    and isinstance(n.get("pitch"), int) and 0 <= n["pitch"] <= 127):
                return f"bad slot note: {n}"
        slots[sc] = {"name": str(args.get("slot_name", f"{tname} {chr(65 + sc % 26)}")),
                     "lengthBeats": length, **({"follow": str(args["follow"])} if args.get("follow") in ("next","any","stop") else {}), **({"followChance": max(0.0, min(1.0, float(args["follow_chance"])))} if args.get("follow_chance") is not None else {}), "notes": notes}
    scenes = song.setdefault("scenes", [])
    while len(scenes) <= sc:
        scenes.append({"name": f"Scene {len(scenes) + 1}"})
    if args.get("scene_name"):
        scenes[sc]["name"] = str(args["scene_name"])
    _awrite(path, song)
    _rc(name, "set_clip_slot", fields=["meta:scenes", f"track:{tname}:slots"],
        summary=f"slot {tname} x scene {sc+1}")
    desc = "cleared" if args.get("clear") else f"{len(slots[sc]['notes'])} notes / {slots[sc]['lengthBeats']} beats"
    return f"OK: slot [{tname} x scene {sc+1}] = {desc}. Launchable in the Live view (bar-quantised)."

def t_generate_loop(args):
    """THE LOOP GENERATOR (from-scratch): genre in -> complete editable loop out,
    from the KG's PatternArchetype grid + bass style + recipe voice + swing."""
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import loop_gen
    name = resolve_song_name(args.get("song"), default="loop") or "loop"
    # No seed given = a FRESH take (same genre DNA, new roll). Seed 0 as the silent
    # default froze every genre into one eternal song — "genres come out the same".
    # An explicit seed still reproduces exactly (the message carries it either way).
    seed = args.get("seed")
    seed = int(seed) if seed is not None else int.from_bytes(os.urandom(3), "big")
    out, msg = loop_gen.generate(str(args["genre"]).lower().replace(" ", "_"), name,
                                 max(1, min(16, int(args.get("bars", 4)))),
                                 seed,
                                 args.get("bpm"), args.get("key"))
    if out is None:
        return msg
    _rc(name, "generate_loop", fields=["*"], summary=f"generated {args.get('genre')} loop")
    return msg + "\nEvery note is editable — change the seed for a different take, or edit tracks directly."

def t_jam(args):
    """THE JAM — the AI band plays a genre on a VIBE by closing the loop: generate a
    phrase, HEAR it (the ears bus), decide a move toward the vibe, play the next."""
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import jam as _jam
    name = resolve_song_name(args.get("song"), default="jam") or "jam"
    seed = args.get("seed")
    seed = int(seed) if seed is not None else int.from_bytes(os.urandom(3), "big")
    human = args.get("human")                 # B3 THE FOLLOW, offline lane
    if human:
        human = human if os.path.isabs(str(human)) else os.path.join(ROOT, str(human))
    res, err = _jam.jam(str(args["genre"]).lower().replace(" ", "_"),
                        str(args.get("vibe", "wave")).lower(),
                        max(2, min(16, int(args.get("phrases", 8)))), seed, name,
                        human_path=human,
                        follow=max(0.0, min(1.0, float(args.get("follow", 0.5)))),
                        bpm=args.get("bpm"), key=args.get("key"))
    if res is None:
        return f"jam failed: {err}"
    _rc(name, "jam", fields=["*"], summary=f"AI band jammed {args.get('genre')} on {res['vibe']}")
    lines = [f"  ph{e['phrase']}: heard {e['measured']:.2f} vs vibe {e['target']:.2f} -> {e['move']}"
             for e in res["log"]]
    return (f"THE BAND jammed {args['genre']} on '{res['vibe']}' — {len(res['arc'])} phrases @ "
            f"{res['bpm']}bpm {res['key']}, ONE continuous evolving take (songs/{name}.json):\n"
            + "\n".join(lines)
            + "\nEach phrase the band HEARD itself (ears bus) and moved toward the vibe. Every note editable.")

def t_jam_live(args):
    """THE LIVE JAM — the realtime scheduler: while a phrase PLAYS, the next is
    rendered CONCURRENTLY (racing the deadline) and ready before it ends. Proves the
    band can 'just go' in realtime; returns the schedule + the continuous take."""
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import jam_live
    name = resolve_song_name(args.get("song"), default="jamlive") or "jamlive"
    seed = args.get("seed")
    seed = int(seed) if seed is not None else int.from_bytes(os.urandom(3), "big")
    human = args.get("human")                 # B3 THE FOLLOW: a growing notes file
    if human:
        human = human if os.path.isabs(str(human)) else os.path.join(ROOT, str(human))
    res, err = jam_live.jam_live(str(args["genre"]).lower().replace(" ", "_"),
                                 str(args.get("vibe", "wave")).lower(),
                                 max(2, min(12, int(args.get("phrases", 6)))), seed, name,
                                 max(1, min(4, int(args.get("bars", 2)))),
                                 human_path=human,
                                 follow=max(0.0, min(1.0, float(args.get("follow", 0.5)))),
                                 bpm=args.get("bpm"), key=args.get("key"))
    if res is None:
        return f"jam_live failed: {err}"
    _rc(name, "jam_live", fields=["*"], summary=f"realtime AI-band jam {args.get('genre')} on {res['vibe']}")
    ur = [t for t in res["timing"] if t["phrase"] < res["phrases"] - 1 and not t["ready"]]
    ideal = res["phrases"] * res["phrase_dur"]
    lines = [f"  ph{lg['phrase']}: heard {lg['measured']:.2f} vs {lg['target']:.2f} -> {lg['move']} "
             f"[gen {tm['gen_s']:.1f}s, slack {tm['slack_s']:+.1f}s]"
             for lg, tm in zip(res["log"], res["timing"])]
    return (f"THE BAND played {args['genre']} on '{res['vibe']}' LIVE — {res['phrases']} phrases x "
            f"{res['phrase_dur']:.1f}s @ {res['bpm']}bpm {res['key']}:\n" + "\n".join(lines)
            + f"\nRealtime: total {res['total_wall']:.1f}s = {ideal:.1f}s pure playback (generation "
            f"overlapped playback); {'NO underruns — the band never stalled' if not ur else str(len(ur))+' UNDERRUNS'}. "
            f"Continuous take: songs/{name}.json. Audio to speakers = the app's realtime device.")

def t_loop_variations(args):
    """THE LOOP GENERATOR: spin N instant deterministic variations of a loop region
    into launcher scenes (rotate/thin/dense/recolor/halftime/humanize)."""
    name, path, song = _load_song(args)
    if song is None:
        return f"no such song '{name}'"
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import loop_variations
    out = loop_variations.generate(path, args["track"], float(args["from_bar"]),
                                   float(args["bars"]), int(args.get("count", 6)))
    _rc(name, "loop_variations", fields=["meta:scenes", f"track:{args['track']}:slots"],
        summary=f"variations for {args['track']}")
    return out

def t_apply_groove(args):
    """GROOVE ENGINE: apply a named timing+velocity profile to a track (dilla, ukg_shuffle,
    psy_straight, dembow_lilt, boombap_56, or any extracted groove). amount 0..1.
    On-grid notes move; existing off-grid feel is preserved."""
    name, path, song = _load_song(args, mutate=True)
    if song is None:
        return f"no such song '{name}'"
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import groove
    out = groove.apply_groove(path, args["track"], args["groove"], float(args.get("amount", 1.0)))
    _rc(name, "apply_groove", track_wild=[str(args["track"])],
        summary=f"groove {args['groove']} on {args['track']}")
    return out

def t_extract_groove(args):
    """Learn a groove from a track's feel (notes) OR from AUDIO (wav_path+bpm:
    an imported drums stem, someone else's record) -> named profile reusable on anything."""
    new_name = re.sub(r"[^a-z0-9_]", "", str(args["new_name"]).lower())
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import groove
    if args.get("wav_path"):
        p = args["wav_path"]
        p = p if os.path.isabs(p) else os.path.join(ROOT, p)
        if not os.path.exists(p):
            return f"no such file: {args['wav_path']}"
        try:
            bpm = float(args["bpm"])
        except (KeyError, TypeError, ValueError):
            return "audio extraction needs bpm (the file's own tempo)"
        return groove.extract_audio(p, bpm, new_name)
    name, path, song = _load_song(args)
    if song is None:
        return f"no such song '{name}'"
    return groove.extract(path, args["track"], new_name)

def t_export_als(args):
    """BRIDGE OUT: export a song as Ableton Live .als (MIDI tracks + tempo)."""
    name, path, song = _load_song(args)
    if song is None:
        return f"no such song '{name}'"
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import als_export
    out = os.path.join(ROOT, "songs", f"{name}.als")
    return als_export.export_als(path, out) + "\nOpens in Ableton Live; round-trip law verified via als_import."

def t_export_dawproject(args):
    """BRIDGE OUT: export a song as .dawproject — opens in Bitwig/Cubase/Nuendo/Studio One
    with notes, tempo, mixer levels and embedded audio clips."""
    name, path, song = _load_song(args)
    if song is None:
        return f"no such song '{name}'"
    out = os.path.join(SONGS, f"{name}.dawproject")
    rc, o, e = run([sys.executable, os.path.join(ROOT, "tools", "dawproject_export.py"),
                    path, out], timeout=120)
    return (o + e).strip()


def t_audio_to_midi(args):
    """SPECTRAL CAPTURE: any audio -> EDITABLE MIDI that renders back to the
    same audio (tools/spectral.py). Lanes land muted; spectral_mix carries the
    audible render; lossless mode adds an integer-exact residual layer."""
    src = args["audio_path"]
    if not os.path.isabs(src):
        src = os.path.join(ROOT, src)
    if not os.path.exists(src):
        return f"no such file: {src}"
    name = resolve_song_name(args.get("song") or
                             os.path.splitext(os.path.basename(src))[0]) or "capture"
    mode = args.get("mode", "lossless")
    if mode not in ("lossless", "spectral"):
        return "mode must be 'lossless' (default; byte-exact) or 'spectral' (pure MIDI)"
    # THE CAPTURE CACHE (2026-07-11, caught LIVE): the agent re-ran a
    # 28-minute quality-max capture on the IDENTICAL stem+params. Content-
    # addressed guard: same source bytes + params = the lanes already carry
    # it — answer instantly. force:true redoes on purpose.
    import hashlib as _hl
    _h = _hl.sha256()
    with open(src, "rb") as _f:
        for _chunk in iter(lambda: _f.read(1 << 20), b""):
            _h.update(_chunk)
    _key = {"src_sha": _h.hexdigest(), "mode": mode,
            "quality": args.get("quality") or "standard",
            "bpm": args.get("bpm"), "t0": args.get("t0"), "t1": args.get("t1"),
            "prefix": args.get("prefix")}
    _keyp = os.path.join(SONGS, f"{name}_spectral", "capture_key.json")
    if not args.get("force") and os.path.exists(_keyp):
        try:
            if json.load(open(_keyp)) == _key:
                return (f"CACHED: this exact capture (same audio bytes + params) already "
                        f"ran into '{name}' — the spectral_* lanes carry it now. Edit the "
                        f"lanes and use midi_to_audio to re-render; pass force:true only "
                        f"if you really want to redo the {_key['quality']}-quality run.")
        except Exception:
            pass
    # W63 THE ASYNC CAPTURE (caught live 2026-07-11): the MCP client's ~600s
    # tool ceiling is SHORTER than a long capture — the call "failed" while
    # the subprocess kept running, the agent retried, and three 28-minute
    # captures piled up. Long captures now DETACH and return instantly; an
    # in-flight lock turns duplicate calls into progress reports; the
    # subprocess lands the lanes itself (--into) and a watcher files the
    # cache key. Short captures (regions, probes) stay synchronous.
    _statusp = os.path.join(SONGS, f"{name}_spectral", "capture_status.json")

    def _status():
        try:
            return json.load(open(_statusp))
        except Exception:
            return None

    _st = _status()
    if _st and _st.get("state") == "running":
        try:
            os.kill(int(_st.get("pid", -1)), 0)
            _alive = True
        except (OSError, ValueError):
            _alive = False
        if _alive:
            _mins = (time.time() - float(_st.get("t0", time.time()))) / 60.0
            return (f"capture ALREADY RUNNING on '{name}' ({_mins:.0f} min in, "
                    f"quality {_st.get('quality')}): the spectral lanes write "
                    f"themselves into the song when it finishes — do OTHER work "
                    f"and poll get_song_summary; do NOT re-call this tool.")
    _dur = 0.0
    try:
        import wave as _wv
        with _wv.open(src) as _w:
            _dur = _w.getnframes() / float(_w.getframerate() or 1)
    except Exception:
        _dur = 180.0                       # non-wav: assume long
    if args.get("t0") is not None or args.get("t1") is not None:
        _dur = min(_dur, max(0.0, float(args.get("t1") or _dur) - float(args.get("t0") or 0.0)))
    _factor = {"fast": 4.0, "standard": 8.0, "max": 14.0}.get(
        args.get("quality") or "standard", 8.0)
    _est = _dur * _factor
    _thresh = float(os.environ.get("SOTADAW_CAPTURE_ASYNC_THRESH", "120"))
    py = VENV_PY if os.path.exists(VENV_PY) else sys.executable
    cmd = [py, os.path.join(ROOT, "tools", "spectral.py"), "capture", src,
           "--name", name, "--mode", mode,
           "--into", os.path.join(SONGS, f"{name}.json")]
    if args.get("prefix"):
        cmd += ["--prefix", str(args["prefix"])]
    if args.get("bpm"):
        cmd += ["--bpm", str(args["bpm"])]
    if args.get("quality") in ("fast", "standard", "max"):
        cmd += ["--quality", str(args["quality"])]
    if args.get("t0") is not None:
        cmd += ["--t0", str(args["t0"])]
    if args.get("t1") is not None:
        cmd += ["--t1", str(args["t1"])]
    if _est > _thresh:
        os.makedirs(os.path.dirname(_statusp), exist_ok=True)
        _logp = _statusp.replace("capture_status.json", "capture_log.txt")
        _pr = subprocess.Popen(cmd, stdout=open(_logp, "w"),
                               stderr=subprocess.STDOUT, cwd=ROOT,
                               start_new_session=True)
        json.dump({"state": "running", "pid": _pr.pid, "t0": time.time(),
                   "quality": args.get("quality") or "standard"},
                  open(_statusp, "w"))

        def _watch(pr=_pr, keyp=_keyp, key=_key, statusp=_statusp):
            rc2 = pr.wait()
            try:
                if rc2 == 0:
                    os.makedirs(os.path.dirname(keyp), exist_ok=True)
                    _awrite(keyp, key, indent=None)
                json.dump({"state": "done" if rc2 == 0 else "failed",
                           "rc": rc2, "t1": time.time()}, open(statusp, "w"))
            except Exception:
                pass
        threading.Thread(target=_watch, daemon=True).start()
        _rc(name, "audio_to_midi", track_wild=["spectral_*"],
            fields=["meta:lengthBars", "meta:bpm", "meta:tempoMap"],
            summary=f"spectral capture STARTED async ({mode})")
        return (f"capture STARTED in the background (~{_est/60:.0f} min at "
                f"quality {args.get('quality') or 'standard'} for {_dur:.0f}s of audio). "
                f"The spectral lanes write themselves into '{name}' when done — "
                f"do OTHER work now and poll get_song_summary later (the track "
                f"list grows when it lands). Do NOT re-call audio_to_midi on "
                f"this file; a re-call just reports progress.")
    rc, o, e = run(cmd, timeout=1800)
    if rc != 0:
        return f"capture failed: {(e or o)[-400:]}"
    try:
        os.makedirs(os.path.dirname(_keyp), exist_ok=True)
        _awrite(_keyp, _key, indent=None)
        _awrite(_statusp, {"state": "done", "rc": 0, "t1": time.time()}, indent=None)
    except Exception:
        pass
    _rc(name, "audio_to_midi", track_wild=["spectral_*"],
        fields=["meta:lengthBars", "meta:bpm", "meta:tempoMap"],
        summary=f"spectral capture ({mode})")
    lines = [l for l in (o + e).splitlines()
             if l.startswith(("[spectral]", "{"))]
    return "\n".join(lines[-6:]) or (o + e)[-400:]

def t_midi_to_audio(args):
    """RE-RENDER THE CAPTURE: read the song's CURRENT spectral_* lanes (your
    edits included), deterministically re-render, swap the spectral_mix clip
    in place. Unedited notes reproduce the capture exactly; moved/transposed/
    stretched notes carry their envelopes along. Reports fidelity vs source."""
    name, path, song = _load_song(args)
    if song is None:
        return f"no such song '{name}'"
    base = os.path.join(SONGS, f"{name}_spectral")
    caps = [c for c in
            [os.path.join(base, "capture.json")]
            + sorted(glob.glob(os.path.join(base, "*", "capture.json")))
            if os.path.exists(c)]
    if not caps:
        return f"no spectral capture for '{name}' — run audio_to_midi first"
    py = VENV_PY if os.path.exists(VENV_PY) else sys.executable
    msg = []
    for capp in caps:
        cdir = os.path.dirname(capp)
        out = os.path.join(cdir, "render.wav")
        rc, o, e = run([py, os.path.join(ROOT, "tools", "spectral.py"), "render",
                        capp, out, "--song", path, "--f32"], timeout=1200)
        tag = os.path.relpath(cdir, base) if cdir != base else "mix"
        if rc != 0:
            msg.append(f"{tag}: render failed: {(e or o)[-200:]}")
            continue
        srcw = os.path.join(cdir, "source.wav")
        if os.path.exists(srcw):
            rc2, o2, _e2 = run([py, os.path.join(ROOT, "tools", "spectral.py"),
                                "verify", srcw, out, "--json"], timeout=600)
            if rc2 == 0 and o2.strip():
                msg.append(f"{tag}: " + o2.strip().splitlines()[-1])
        else:
            msg.append(f"{tag}: re-rendered")
    _rc(name, "midi_to_audio", track_wild=["spectral_*"],
        summary="spectral re-render")
    return "\n".join(msg) or "re-rendered"

def t_roundtrip_verify(args):
    """HONEST EARS for reconstruction: score render vs original — spectral
    fidelity % (mel), waveform corr @ best lag, SI-SDR, envelope corr,
    byte-exact bool. Use after midi_to_audio or on any pair of files."""
    pa, pb = args["a"], args["b"]
    pa = pa if os.path.isabs(pa) else os.path.join(ROOT, pa)
    pb = pb if os.path.isabs(pb) else os.path.join(ROOT, pb)
    for q in (pa, pb):
        if not os.path.exists(q):
            return f"no such file: {q}"
    py = VENV_PY if os.path.exists(VENV_PY) else sys.executable
    rc, o, e = run([py, os.path.join(ROOT, "tools", "spectral.py"), "verify",
                    pa, pb], timeout=900)
    return (o + e).strip()[-600:]

def t_import_song_audio(args):
    """ABSORPTION: any finished song (mp3/wav/flac) -> stems (demucs, GPU) + MIDI sketches
    (basic-pitch) + bpm/key estimates -> a fully editable session. ~10-90s."""
    src = args["audio_path"]
    if not os.path.isabs(src):
        src = os.path.join(ROOT, src)
    if not os.path.exists(src):
        return f"no such file: {src}"
    name = resolve_song_name(args["song"])
    # THE IMPORT CACHE (2026-07-11, the capture-cache's sibling): re-importing
    # the same bytes into the same session = a full demucs re-run for stems
    # that already exist. Same-key re-ask answers instantly; force:true redoes.
    import hashlib as _hl
    _h = _hl.sha256()
    with open(src, "rb") as _f:
        for _chunk in iter(lambda: _f.read(1 << 20), b""):
            _h.update(_chunk)
    _key = {"src_sha": _h.hexdigest(), "quality": args.get("quality") or "std",
            "instruments": args.get("instruments") or "original"}
    _keyp = os.path.join(SONGS, f"{name}_stems", "import_key.json")
    if not args.get("force") and os.path.exists(_keyp):
        try:
            if json.load(open(_keyp)) == _key:
                return (f"CACHED: these exact bytes were already imported into '{name}' — "
                        f"the stems + sketches are in songs/{name}_stems/ and the session "
                        f"carries them. force:true only if you really want demucs to rerun.")
        except Exception:
            pass
    py = VENV_PY if os.path.exists(VENV_PY) else sys.executable
    cmd = [py, os.path.join(ROOT, "tools", "stems_import.py"), src, name]
    if args.get("quality") == "max":
        cmd += ["--quality", "max"]
    if args.get("instruments") == "ear":
        # THE INSTRUMENT EAR (2026-07-11): the user's conversion choice —
        # closed-loop palette picks per stem instead of the record's own kits
        cmd += ["--instruments", "ear"]
    # W64: same MCP-ceiling class as the capture (W63) — a CPU-path import
    # of a full song exceeds the client's ~600s tool ceiling, "fails", and
    # invites a retry pile-up. Full songs DETACH; the in-flight lock turns
    # re-calls into progress reports; stems_import lands the session itself.
    _istp = os.path.join(SONGS, f"{name}_stems", "import_status.json")
    _ist = None
    try:
        _ist = json.load(open(_istp))
    except Exception:
        pass
    if _ist and _ist.get("state") == "running":
        try:
            os.kill(int(_ist.get("pid", -1)), 0)
            _imins = (time.time() - float(_ist.get("t0", time.time()))) / 60.0
            return (f"import ALREADY RUNNING on '{name}' ({_imins:.0f} min in): "
                    f"demucs lands the session itself when done — do OTHER work "
                    f"and poll get_song_summary; do NOT re-call this tool.")
        except (OSError, ValueError):
            pass
    _idur = 0.0
    try:
        import wave as _wv2
        with _wv2.open(src) as _w2:
            _idur = _w2.getnframes() / float(_w2.getframerate() or 1)
    except Exception:
        _idur = 300.0                       # mp3/m4a: assume full song
    if _idur > float(os.environ.get("SOTADAW_IMPORT_ASYNC_THRESH", "30")):
        os.makedirs(os.path.dirname(_istp), exist_ok=True)
        _ilogp = _istp.replace("import_status.json", "import_log.txt")
        _ipr = subprocess.Popen(cmd, stdout=open(_ilogp, "w"),
                                stderr=subprocess.STDOUT, cwd=ROOT,
                                start_new_session=True)
        json.dump({"state": "running", "pid": _ipr.pid, "t0": time.time()},
                  open(_istp, "w"))

        def _iwatch(pr=_ipr, keyp=_keyp, key=_key, statusp=_istp):
            rc2 = pr.wait()
            try:
                if rc2 == 0:
                    os.makedirs(os.path.dirname(keyp), exist_ok=True)
                    _awrite(keyp, key, indent=None)
                json.dump({"state": "done" if rc2 == 0 else "failed",
                           "rc": rc2, "t1": time.time()}, open(statusp, "w"))
            except Exception:
                pass
        threading.Thread(target=_iwatch, daemon=True).start()
        _rc(name, "import_song_audio", track_wild=["*"],
            summary="stems import STARTED async (demucs)")
        return (f"import STARTED in the background ({_idur:.0f}s of audio; "
                f"minutes on GPU, up to ~45 min on a busy CPU). The stems + "
                f"sketches land in '{name}' automatically — do OTHER work and "
                f"poll get_song_summary; a re-call just reports progress.")
    # 2700s: the CPU worst case (GPU window closed, --segment 7, long track)
    # must still LAND a session — 900s killed a 6min m4a mid-separation.
    rc, o, e = run(cmd, timeout=2700)
    if rc == 0:
        try:
            os.makedirs(os.path.dirname(_keyp), exist_ok=True)
            _awrite(_keyp, _key, indent=None)
        except Exception:
            pass
        _rc(name, "import_song_audio", track_wild=["*"],
            summary="stems import (demucs + sketches)")
    lines = [l for l in (o + e).splitlines() if l.startswith(("imported", "[stems]"))]
    return "\n".join(lines) or (o + e)[-800:]


def _detach_long(cmd, status_path, started_msg, env=None):
    """W65: the MCP-ceiling class helper — detach a self-landing subprocess,
    write a pid status file, watch it to done/failed. A caller should FIRST
    check the status file for a live 'running' pid and report progress
    instead of spawning. SOTADAW_NO_DETACH=1 forces sync (batteries)."""
    os.makedirs(os.path.dirname(status_path), exist_ok=True)
    logp = status_path.replace(".json", "_log.txt")
    pr = subprocess.Popen(cmd, stdout=open(logp, "w"), stderr=subprocess.STDOUT,
                          cwd=ROOT, start_new_session=True,
                          env=env or dict(os.environ))
    json.dump({"state": "running", "pid": pr.pid, "t0": time.time()},
              open(status_path, "w"))

    def _w(pr=pr, sp=status_path):
        rc2 = pr.wait()
        try:
            json.dump({"state": "done" if rc2 == 0 else "failed", "rc": rc2,
                       "t1": time.time()}, open(sp, "w"))
        except Exception:
            pass
    threading.Thread(target=_w, daemon=True).start()
    return started_msg


def _running_status(status_path, what, name):
    try:
        st = json.load(open(status_path))
        if st.get("state") == "running":
            os.kill(int(st.get("pid", -1)), 0)
            mins = (time.time() - float(st.get("t0", time.time()))) / 60.0
            return (f"{what} ALREADY RUNNING on '{name}' ({mins:.0f} min in) — "
                    f"it lands its results itself; do OTHER work and poll, "
                    f"do NOT re-call this tool.")
    except Exception:
        pass
    return None


def t_a2m_correct(args):
    """THE FINAL CORRECTION: closed-loop calibration of an imported MIDI product
    against the record's own stems — analysis-by-synthesis, all at the source."""
    name = resolve_song_name(args["song"])
    sp = os.path.join(SONGS, f"{name}.json")
    if not os.path.exists(sp):
        return f"no such song: {name}"
    py = VENV_PY if os.path.exists(VENV_PY) else sys.executable
    cmd = [py, os.path.join(ROOT, "tools", "a2m_correct.py"), sp,
           "--iters", str(int(args.get("iters", 2)))]
    if args.get("no_verify"):
        cmd.append("--no-verify")
    _asp = os.path.join(SONGS, f"{name}_stems", "a2m_status.json")
    _msg = _running_status(_asp, "a2m correction", name)
    if _msg:
        return _msg
    if os.environ.get("SOTADAW_NO_DETACH") != "1":
        _rc(name, "a2m_correct", fields=["*"], track_wild=["*"],
            summary="closed-loop correction STARTED async")
        return _detach_long(cmd, _asp,
                            f"a2m correction STARTED in the background (up to "
                            f"~45 min worst case): it edits '{name}' in place as "
                            f"it converges — do OTHER work and poll "
                            f"get_song_summary; a re-call reports progress.")
    rc, o, e = run(cmd, timeout=2700)
    _rc(name, "a2m_correct", fields=["*"], track_wild=["*"],
        summary="closed-loop correction vs the record's stems")
    lines = [l for l in (o + e).splitlines() if l.startswith("[correct]")]
    return "\n".join(lines) or (o + e)[-800:]

def t_vocal_truth(args):
    """THE VOCAL TRUTH LANE: the record's own vocal re-synthesized from
    parametric spectral capture (never a chop) -> 'vocals_true' sounding."""
    name = resolve_song_name(args["song"])
    if not os.path.exists(os.path.join(SONGS, f"{name}.json")):
        return f"no such song: {name}"
    py = VENV_PY if os.path.exists(VENV_PY) else sys.executable
    cmd = [py, os.path.join(ROOT, "tools", "vocal_truth.py"), name]
    if args.get("win"):
        cmd += ["--win", str(float(args["win"]))]
    env = dict(os.environ, SOTADAW_VTRUTH_WAIT_S=str(int(args.get("wait_s", 300))))
    _vsp = os.path.join(SONGS, f"{name}_stems", "vtruth_status.json")
    _vmsg = _running_status(_vsp, "vocal truth", name)
    if _vmsg:
        return _vmsg
    if os.environ.get("SOTADAW_NO_DETACH") != "1":
        _rc(name, "vocal_truth", fields=["track:vocals_true", "track:vocals_sung"],
            summary="vocal truth STARTED async")
        return _detach_long(cmd, _vsp,
                            f"vocal truth STARTED in the background (minutes to "
                            f"~1 h worst case): 'vocals_true' lands on '{name}' "
                            f"automatically — do OTHER work and poll; a re-call "
                            f"reports progress.", env=env)
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=3600, env=env,
                       cwd=ROOT)
    _rc(name, "vocal_truth", fields=["track:vocals_true", "track:vocals_sung"],
        summary="vocals_true landed from spectral resynthesis")
    lines = [l for l in (p.stdout + p.stderr).splitlines()
             if l.startswith("[vtruth]")]
    return "\n".join(lines) or (p.stdout + p.stderr)[-800:]

def t_dj_blend(args):
    """THE AI DJ: beat-matched blend of two audio files onto one tempo grid (warp),
    phrase-aligned crossfade + fx_djfilter bass swap -> an editable song.json."""
    paths = []
    for k in ("deck_a", "deck_b"):
        p = args[k]
        if not os.path.isabs(p):
            p = os.path.join(ROOT, p)
        if not os.path.exists(p):
            return f"no such file: {args[k]}"
        paths.append(p)
    name = resolve_song_name(args["song"])
    py = VENV_PY if os.path.exists(VENV_PY) else sys.executable
    cmd = [py, os.path.join(ROOT, "tools", "dj_mix.py"), paths[0], paths[1], name]
    for k, f in (("bpm", "--bpm"), ("bpm_a", "--bpm-a"), ("bpm_b", "--bpm-b"),
                 ("blend_bars", "--blend-bars")):
        if args.get(k) is not None:
            cmd += [f, str(args[k])]
    rc, o, e = run(cmd, timeout=300)
    if rc != 0:
        return f"dj_mix failed:\n{(o + e)[-800:]}"
    return (o.strip() + "\nEvery transition point is automation in the song — edit the blend "
            "curves/swap bar directly, then render_song to hear it.")

def t_chop_sample(args):
    """THE CHOP: slice any audio into a playable sampler kit (onset or grid slicing);
    pads land chromatically from key 36."""
    src = args["audio_path"]
    if not os.path.isabs(src):
        src = os.path.join(ROOT, src)
    if not os.path.exists(src):
        return f"no such file: {args['audio_path']}"
    kit = re.sub(r"[^a-z0-9_]", "", str(args["kit"]).lower())
    py = VENV_PY if os.path.exists(VENV_PY) else sys.executable
    cmd = [py, os.path.join(ROOT, "tools", "chop.py"), src, kit]
    for k, f in (("slices", "--slices"), ("from_sec", "--from-sec"),
                 ("to_sec", "--to-sec"), ("grid", "--grid"), ("melodic", "--melodic"),
                 ("bpm", "--bpm"), ("song", "--song"), ("track", "--track")):
        if args.get(k) is not None:
            cmd += [f, str(args[k])]
    for k, f in (("groove", "--groove"), ("preview", "--preview")):
        if args.get(k):
            cmd += [f]
    rc, o, e = run(cmd, timeout=300)
    if rc == 0 and args.get("song"):
        _rc(resolve_song_name(args["song"]), "chop_sample",
            fields=[f"track:{args.get('track') or kit}"],
            track_wild=[str(args.get("track") or kit)],
            summary=f"chop groove -> {args.get('track') or kit}")
    return o.strip() if rc == 0 else f"chop failed:\n{(o + e)[-500:]}"

def t_chord_map(args):
    """CHORDS FROM THE SYMBOLS: bar-wise vote over the song's own notes."""
    name = resolve_song_name(args["song"])
    py = VENV_PY if os.path.exists(VENV_PY) else sys.executable
    cmd = [py, os.path.join(ROOT, "tools", "chordvote.py"), name]
    if args.get("write"):
        cmd += ["--write"]
    if args.get("tracks"):
        cmd += ["--tracks", str(args["tracks"])]
    rc, o, e = run(cmd, timeout=120)
    return o.strip() if rc == 0 else f"chordvote failed:\n{(o + e)[-500:]}"

def t_reharmonize(args):
    """The chord lane ACTS: rotate the cycle or set explicit target chords."""
    name = resolve_song_name(args["song"])
    py = VENV_PY if os.path.exists(VENV_PY) else sys.executable
    cmd = [py, os.path.join(ROOT, "tools", "reharm.py"), name, "--write"]
    if args.get("rotate") is not None:
        cmd += ["--rotate", str(int(args["rotate"]))]
    if args.get("to"):
        cmd += ["--to", str(args["to"])]
    if args.get("out"):
        cmd += ["--out", re.sub(r"[^a-z0-9_]", "", str(args["out"]).lower())]
    rc, o, e = run(cmd, timeout=120)
    return o.strip() if rc == 0 else f"reharm failed:\n{(o + e)[-500:]}"

def t_remix_import(args):
    """THE FULL FLIP: original <genre> track matching an import's bpm/key/chords/groove."""
    name = resolve_song_name(args["song"])
    py = VENV_PY if os.path.exists(VENV_PY) else sys.executable
    cmd = [py, os.path.join(ROOT, "tools", "remix_import.py"), name, str(args["genre"])]
    for k, f in (("out", "--out"), ("seed", "--seed"), ("bars", "--bars")):
        if args.get(k) is not None:
            cmd += [f, str(args[k])]
    if args.get("full"):
        cmd += ["--full"]
    rc, o, e = run(cmd, timeout=300)
    return o.strip() if rc == 0 else f"flip failed:\n{(o + e)[-500:]}"

def t_harmonize(args):
    """COMPOSE FROM the chord lane: a new part playing the song's own changes."""
    name = resolve_song_name(args["song"])
    py = VENV_PY if os.path.exists(VENV_PY) else sys.executable
    cmd = [py, os.path.join(ROOT, "tools", "harmonize.py"), name, str(args["role"]), "--write"]
    for k, f in (("track", "--track"), ("octave", "--octave"), ("rhythm", "--rhythm"), ("seed", "--seed")):
        if args.get(k) is not None:
            cmd += [f, str(args[k])]
    if args.get("sectioned"):
        cmd += ["--sectioned"]
    rc, o, e = run(cmd, timeout=120)
    if rc != 0:
        return f"harmonize failed:\n{(o + e)[-500:]}"
    _rc(name, "harmonize", fields=[f"track:{args.get('track') or args['role']}"],
        summary=f"harmonized {args['role']} to the chord lane")
    return o.strip()

def t_transitions(args):
    """THE GLUE: risers/impacts at section boundaries into high-energy sections."""
    name = resolve_song_name(args["song"])
    py = VENV_PY if os.path.exists(VENV_PY) else sys.executable
    cmd = [py, os.path.join(ROOT, "tools", "transitions.py"), name, "--write"]
    if args.get("track"):
        cmd += ["--track", str(args["track"])]
    if args.get("preroll") is not None:
        cmd += ["--preroll", str(args["preroll"])]
    if args.get("impacts"):
        cmd += ["--impacts"]
    if args.get("downlifters"):
        cmd += ["--downlifters"]
    if args.get("fills"):
        cmd += ["--fills"]
    rc, o, e = run(cmd, timeout=120)
    if rc != 0:
        return f"transitions failed:\n{(o + e)[-400:]}"
    _rc(name, "transitions", fields=[f"track:{args.get('track') or 'riser'}"],
        summary="risers/impacts at section boundaries")
    return o.strip()

def t_automix(args):
    """AUTOMIX: apply the KG's space+unmask laws by track role (structural)."""
    name = resolve_song_name(args["song"])
    py = VENV_PY if os.path.exists(VENV_PY) else sys.executable
    cmd = [py, os.path.join(ROOT, "tools", "automix.py"), name, "--write"]
    rc, o, e = run(cmd, timeout=120)
    if rc != 0:
        return f"automix failed:\n{(o + e)[-400:]}"
    _rc(name, "automix", fields=["*"], summary="applied structural mix laws by role")
    return o.strip()

def t_finish(args):
    """FINISH: the full auto-production chain (chords->arrange->harmonize->transitions->mix)."""
    name = resolve_song_name(args["song"])
    py = VENV_PY if os.path.exists(VENV_PY) else sys.executable
    cmd = [py, os.path.join(ROOT, "tools", "finish.py"), name]
    if args.get("out"):
        cmd += ["--out", re.sub(r"[^a-z0-9_]", "", str(args["out"]).lower())]
    rc, o, e = run(cmd, timeout=180)
    if rc != 0:
        return f"finish failed:\n{(o + e)[-400:]}"
    _rc(resolve_song_name(args.get("out") or args["song"]),
        "finish", fields=["*"], summary="full auto-production chain")
    return o.strip()

def t_humanize(args):
    """MEASURABLE humanization: microtiming + velocity (GrooVAE axes); score rises."""
    name = resolve_song_name(args["song"])
    py = VENV_PY if os.path.exists(VENV_PY) else sys.executable
    cmd = [py, os.path.join(ROOT, "tools", "expressive.py"), name]
    if args.get("measure"):
        cmd += ["--measure"]
    else:
        cmd += ["--write"]
    for k, f in (("track", "--track"), ("amount", "--amount"), ("seed", "--seed")):
        if args.get(k) is not None:
            cmd += [f, str(args[k])]
    rc, o, e = run(cmd, timeout=120)
    if rc != 0:
        return f"humanize failed:\n{(o + e)[-400:]}"
    if not args.get("measure"):
        # CONTAINMENT GRAMMAR: note changes are authorized only by track_wild —
        # fields=["track:X"] was dead grammar for notes (latent amber-flag bug)
        try:
            wild = ([str(args["track"])] if args.get("track") else
                    [t.get("name") for t in json.load(open(os.path.join(
                        ROOT, "songs", f"{name}.json"))).get("tracks", [])])
        except Exception:
            wild = []
        _rc(name, "humanize", track_wild=wild,
            summary="microtiming+velocity humanization")
    return o.strip()

def t_intensify(args):
    """INTENSIFY: shape a section's energy up/down (velocity + density)."""
    name = resolve_song_name(args["song"])
    py = VENV_PY if os.path.exists(VENV_PY) else sys.executable
    cmd = [py, os.path.join(ROOT, "tools", "intensify.py"), name, str(args["section"]),
           str(float(args["amount"])), "--write"]
    rc, o, e = run(cmd, timeout=120)
    if rc != 0:
        return f"intensify failed:\n{(o + e)[-400:]}"
    # CONTAINMENT GRAMMAR: "section:x" was dead grammar (never matched a note change);
    # the kernel's own INTENSIFY_JSON names the touched tracks — receipt exactly those.
    wild = []
    for line in o.splitlines():
        if line.startswith("INTENSIFY_JSON "):
            try:
                wild = sorted(json.loads(line.split(" ", 1)[1]).get("tracks", {}))
            except (json.JSONDecodeError, IndexError):
                pass
    _rc(name, "intensify", track_wild=wild,
        summary=f"energy {args['amount']:+} on '{args['section']}'")
    return o.strip()

def t_variations(args):
    """VARIATIONS: N distinct options for a region (propose-and-pick)."""
    name = resolve_song_name(args["song"])
    py = VENV_PY if os.path.exists(VENV_PY) else sys.executable
    cmd = [py, os.path.join(ROOT, "tools", "variations.py"), name, str(args["track"]),
           str(int(args["from_bar"])), str(int(args["to_bar"])), "--write"]
    if args.get("n") is not None:
        cmd += ["--n", str(int(args["n"]))]
    if args.get("style"):
        cmd += ["--style", re.sub(r"[^a-z0-9_]", "", str(args["style"]).lower())]
    rc, o, e = run(cmd, timeout=180)
    if rc != 0:
        return f"variations failed:\n{(o + e)[-400:]}"
    return o.strip()

def t_infill_region(args):
    """INFILL: regenerate a track's chosen bars, conditioned on surrounding context."""
    name = resolve_song_name(args["song"])
    py = VENV_PY if os.path.exists(VENV_PY) else sys.executable
    cmd = [py, os.path.join(ROOT, "tools", "infill_region.py"), name, str(args["track"]),
           str(int(args["from_bar"])), str(int(args["to_bar"])), "--write"]
    for k, f in (("seed", "--seed"), ("density", "--density"), ("duration", "--duration"), ("style", "--style")):
        if args.get(k) is not None:
            cmd += [f, str(args[k])]
    rc, o, e = run(cmd, timeout=120)
    if rc != 0:
        return f"infill failed:\n{(o + e)[-400:]}"
    _rc(name, "infill_region", fields=[f"track:{args['track']}"],
        summary=f"infilled {args['track']} bars {args['from_bar']}-{args['to_bar']}")
    return o.strip()

def t_style_profile(args):
    """STYLE: extract a producer fingerprint from songs, or score a track's match."""
    py = VENV_PY if os.path.exists(VENV_PY) else sys.executable
    action = args.get("action", "score")
    if action == "extract":
        names = [resolve_song_name(x) for x in args["songs"]]
        cmd = [py, os.path.join(ROOT, "tools", "style_profile.py"), "extract"] + names
        cmd += ["--out", re.sub(r"[^a-z0-9_]", "", str(args.get("profile", "my_style")).lower())]
    else:
        song = resolve_song_name(args["song"])
        prof = re.sub(r"[^a-z0-9_]", "", str(args.get("profile", "my_style")).lower())
        cmd = [py, os.path.join(ROOT, "tools", "style_profile.py"), "score", song, prof]
    rc, o, e = run(cmd, timeout=120)
    return o.strip() if rc == 0 else f"style_profile failed:\n{(o + e)[-400:]}"

def t_prescribe(args):
    """PRESCRIBE: doctor + auto-apply the safe fixes, then re-diagnose to prove it."""
    name = resolve_song_name(args["song"])
    py = VENV_PY if os.path.exists(VENV_PY) else sys.executable
    cmd = [py, os.path.join(ROOT, "tools", "prescribe.py"), name]
    if args.get("out"):
        cmd += ["--out", re.sub(r"[^a-z0-9_]", "", str(args["out"]).lower())]
    else:
        cmd += ["--write"]
    rc, o, e = run(cmd, timeout=120)
    if rc != 0:
        return f"prescribe failed:\n{(o + e)[-400:]}"
    # CONTAINMENT GRAMMAR: a bare summary receipt authorized NOTHING (every change
    # amber-flagged); prescribe's safe fixes touch track props/notes + master/buses.
    edited = re.sub(r"[^a-z0-9_]", "", str(args["out"]).lower()) if args.get("out") else name
    try:
        wild = [t.get("name") for t in json.load(open(os.path.join(
            ROOT, "songs", f"{edited}.json"))).get("tracks", [])]
    except Exception:
        wild = []
    _rc(name, "prescribe", fields=["buses", "master", "automation"], track_wild=wild,
        summary="auto-fixed mix/feel/master issues")
    return o.strip()

def t_doctor(args):
    """DOCTOR: symbolic critique — what's wrong + the fix tool (no render)."""
    name = resolve_song_name(args["song"])
    py = VENV_PY if os.path.exists(VENV_PY) else sys.executable
    rc, o, e = run([py, os.path.join(ROOT, "tools", "doctor.py"), name], timeout=120)
    return o.strip() if rc == 0 else f"doctor failed:\n{(o + e)[-400:]}"

def t_restyle(args):
    """RESTYLE: keep every note, swap the genre's palette + feel (role-mapped DNA voices)."""
    name = resolve_song_name(args["song"])
    py = VENV_PY if os.path.exists(VENV_PY) else sys.executable
    cmd = [py, os.path.join(ROOT, "tools", "restyle.py"), name,
           re.sub(r"[^a-z0-9_]", "", str(args["genre"]).lower()), "--write"]
    if args.get("bpm"):
        cmd += ["--bpm"]
    rc, o, e = run(cmd, timeout=120)
    if rc != 0:
        return f"restyle failed:\n{(o + e)[-400:]}"
    wild = []
    for line in o.splitlines():
        if line.startswith("RESTYLE_JSON "):
            try:
                wild = sorted(json.loads(line.split(" ", 1)[1]).get("tracks", {}))
            except (json.JSONDecodeError, IndexError):
                pass
    _rc(name, "restyle", fields=["meta:swing", "meta:bpm"], track_wild=wild,
        summary=f"restyle -> {args['genre']}")
    return o.strip()

def t_color(args):
    """COLOR: semantic axes (warmer/darker/brighter/wider) as deterministic DSP moves."""
    name = resolve_song_name(args["song"])
    py = VENV_PY if os.path.exists(VENV_PY) else sys.executable
    cmd = [py, os.path.join(ROOT, "tools", "color.py"), name, str(args["word"]),
           str(float(args.get("amount", 0.5))), "--write"]
    if args.get("track"):
        cmd += ["--track", str(args["track"])]
    rc, o, e = run(cmd, timeout=120)
    if rc != 0:
        return f"color failed:\n{(o + e)[-400:]}"
    wild = []
    for line in o.splitlines():
        if line.startswith("COLOR_JSON "):
            try:
                wild = sorted(json.loads(line.split(" ", 1)[1]).get("tracks", {}))
            except (json.JSONDecodeError, IndexError):
                pass
    _rc(name, "color", track_wild=wild, summary=f"{args['word']} {args.get('amount', 0.5)}")
    return o.strip()

def t_energy_curve(args):
    """ENERGY CURVE: per-bar energy + section means + contrast-law check (no render)."""
    name = resolve_song_name(args["song"])
    py = VENV_PY if os.path.exists(VENV_PY) else sys.executable
    cmd = [py, os.path.join(ROOT, "tools", "energy_curve.py"), name]
    if args.get("track"):
        cmd += ["--track", str(args["track"])]
    rc, o, e = run(cmd, timeout=120)
    return o.strip() if rc == 0 else f"energy_curve failed:\n{(o + e)[-400:]}"

def t_song_structure(args):
    """EARS v4b: section boundaries of any wav (Foote novelty, precision-tuned)."""
    src = args["audio_path"]
    if not os.path.isabs(src):
        src = os.path.join(ROOT, src)
    if not os.path.exists(src):
        return f"no such file: {args['audio_path']}"
    py = VENV_PY if os.path.exists(VENV_PY) else sys.executable
    cmd = [py, os.path.join(ROOT, "tools", "segment.py"), src]
    if args.get("bpm") is not None:
        cmd += ["--bpm", str(args["bpm"])]
    if args.get("vocal"):
        vp = args["vocal"]
        cmd += ["--vocal", vp if os.path.isabs(vp) else os.path.join(ROOT, vp)]
    rc, o, e = run(cmd, timeout=300)
    return o.strip() if rc == 0 else f"segment failed:\n{(o + e)[-500:]}"

def t_suggest_chords(args):
    """HARMONY ADVISOR: ranked substitutions + rewrites with theory WHYs."""
    name = resolve_song_name(args["song"])
    py = VENV_PY if os.path.exists(VENV_PY) else sys.executable
    cmd = [py, os.path.join(ROOT, "tools", "suggest_chords.py"), name]
    if args.get("genre"):
        cmd += ["--genre", str(args["genre"])]
    if args.get("k") is not None:
        cmd += ["--k", str(int(args["k"]))]
    rc, o, e = run(cmd, timeout=120)
    return o.strip() if rc == 0 else f"suggest_chords failed:\n{(o + e)[-500:]}"

def t_describe_sound(args):
    """SEMANTIC EARS SPEAK: zero-shot CLAP words for any wav."""
    src = args["audio_path"]
    if not os.path.isabs(src):
        src = os.path.join(ROOT, src)
    if not os.path.exists(src):
        return f"no such file: {args['audio_path']}"
    py = VENV_PY if os.path.exists(VENV_PY) else sys.executable
    cmd = [py, os.path.join(ROOT, "tools", "describe_sound.py"), src]
    if args.get("k") is not None:
        cmd += ["--k", str(int(args["k"]))]
    rc, o, e = run(cmd, timeout=300)
    return o.strip() if rc == 0 else f"describe_sound failed:\n{(o + e)[-500:]}"

def t_structure_transfer(args):
    """STRUCTURE TRANSFER: a reference record's section shape -> arrangement plan."""
    src = args["audio_path"]
    if not os.path.isabs(src):
        src = os.path.join(ROOT, src)
    if not os.path.exists(src):
        return f"no such file: {args['audio_path']}"
    py = VENV_PY if os.path.exists(VENV_PY) else sys.executable
    cmd = [py, os.path.join(ROOT, "tools", "structure_transfer.py"), src]
    if args.get("song"):
        cmd += ["--song", resolve_song_name(args["song"])]
    if args.get("bars") is not None:
        cmd += ["--bars", str(int(args["bars"]))]
    if args.get("vocal"):
        vp = args["vocal"]
        cmd += ["--vocal", vp if os.path.isabs(vp) else os.path.join(ROOT, vp)]
    rc, o, e = run(cmd, timeout=300)
    return o.strip() if rc == 0 else f"structure_transfer failed:\n{(o + e)[-500:]}"

def t_smart_tempo(args):
    """SMART TEMPO: a freely-played recording -> offsetSec + tempoMap (rubato conform)."""
    src = args["audio_path"]
    if not os.path.isabs(src):
        src = os.path.join(ROOT, src)
    if not os.path.exists(src):
        return f"no such file: {args['audio_path']}"
    py = VENV_PY if os.path.exists(VENV_PY) else sys.executable
    cmd = [py, os.path.join(ROOT, "tools", "smart_tempo.py"), src]
    if args.get("meter") is not None:
        cmd += ["--meter", str(int(args["meter"]))]
    if args.get("engine"):
        cmd += ["--engine", str(args["engine"])]
    rc, o, e = run(cmd, timeout=600)
    return o.strip() if rc == 0 else f"smart_tempo failed:\n{(o + e)[-500:]}"

def t_transcribe_lyrics(args):
    """THE WORDS: ASR a recorded vocal into beat-timed words/lines on the song's clock."""
    src = args["audio_path"]
    if not os.path.isabs(src):
        src = os.path.join(ROOT, src)
    if not os.path.exists(src):
        return f"no such file: {args['audio_path']}"
    py = VENV_PY if os.path.exists(VENV_PY) else sys.executable
    cmd = [py, os.path.join(ROOT, "tools", "lyrics_from_audio.py"), src]
    if args.get("song"):
        cmd += ["--song", resolve_song_name(args["song"])]
    if args.get("find"):
        cmd += ["--find", str(args["find"])]
    if args.get("language"):
        cmd += ["--language", str(args["language"])]
    if args.get("model"):
        cmd += ["--model", str(args["model"])]
    rc, o, e = run(cmd, timeout=1800)
    return o.strip() if rc == 0 else f"transcribe_lyrics failed:\n{(o + e)[-500:]}"

def t_vocal_rider(args):
    """VOCAL RIDER: stems -> bounded slewed gainDb ride for the vocal track (read-only)."""
    name = resolve_song_name(args["song"])
    py = VENV_PY if os.path.exists(VENV_PY) else sys.executable
    cmd = [py, os.path.join(ROOT, "tools", "vocal_rider.py"), name]
    if args.get("track"):
        cmd += ["--track", str(args["track"])]
    if args.get("target") is not None:
        cmd += ["--target", str(float(args["target"]))]
    if args.get("range") is not None:
        cmd += ["--range", str(float(args["range"]))]
    if args.get("stems_dir"):
        sd = args["stems_dir"]
        cmd += ["--stems", sd if os.path.isabs(sd) else os.path.join(ROOT, sd)]
    rc, o, e = run(cmd, timeout=600)
    return o.strip() if rc == 0 else f"vocal_rider failed:\n{(o + e)[-500:]}"

def t_restore_audio(args):
    """AUDIO REPAIR: QC + bounded fixes on a recording (writes a NEW wav)."""
    p = args["audio_path"]
    path = p if os.path.isabs(p) else os.path.join(ROOT, p)
    py = VENV_PY if os.path.exists(VENV_PY) else sys.executable
    cmd = [py, os.path.join(ROOT, "tools", "restore_audio.py"), path]
    if args.get("out_path"):
        o = args["out_path"]
        cmd += ["-o", o if os.path.isabs(o) else os.path.join(ROOT, o)]
    if args.get("report_only"):
        cmd += ["--report-only"]
    if args.get("denoise_db") is not None:
        cmd += ["--denoise-db", str(args["denoise_db"])]
    if args.get("hum"):
        cmd += ["--hum", str(args["hum"])]
    if args.get("dc"):
        cmd += ["--dc", str(args["dc"])]
    rc, o, e = run(cmd, timeout=900)
    return o.strip() if rc == 0 else f"restore_audio failed:\n{(o + e)[-500:]}"

def t_sidechain_bake(args):
    """KEYED SIDECHAIN: trigger notes -> duck automation plan (read-only)."""
    raw = str(args["song"])
    name = raw if "/" in raw and ".." not in raw else resolve_song_name(raw)
    py = VENV_PY if os.path.exists(VENV_PY) else sys.executable
    cmd = [py, os.path.join(ROOT, "tools", "sidechain_bake.py"), name]
    if args.get("trigger"):
        cmd += ["--trigger", str(args["trigger"])]
    if args.get("targets"):
        t = args["targets"]
        cmd += ["--targets", ",".join(t) if isinstance(t, list) else str(t)]
    for k in ("depth", "attack", "hold", "release"):
        if args.get(k) is not None:
            cmd += ["--" + k, str(float(args[k]))]
    rc, o, e = run(cmd, timeout=300)
    return o.strip() if rc == 0 else f"sidechain_bake failed:\n{(o + e)[-500:]}"

def t_find_genre(args):
    """SEMANTIC GENRE ROUTING (pass 5): vibe words -> nearest KG genres."""
    py = VENV_PY if os.path.exists(VENV_PY) else sys.executable
    rc, o, e = run([py, os.path.join(ROOT, "tools", "kg_vibe.py"),
                    str(args.get("text", "")), "--k", str(int(args.get("k", 5)))],
                   timeout=120)
    line = next((l for l in o.splitlines() if l.startswith("VIBE_JSON ")), None)
    return line[len("VIBE_JSON "):] if line else json.dumps(
        {"available": False, "reason": (o + e)[-200:]})

def t_dj_set(args):
    """AI DJ SET: N tracks -> one continuous beat-matched set with a TRAVELING grid
    (tempoMap re-anchors at each bass swap). One editable song.json."""
    paths = []
    for p in args["tracks"]:
        q = p if os.path.isabs(p) else os.path.join(ROOT, p)
        if not os.path.exists(q):
            return f"no such file: {p}"
        paths.append(q)
    if len(paths) < 2:
        return "need at least 2 tracks"
    name = resolve_song_name(args["song"])
    py = VENV_PY if os.path.exists(VENV_PY) else sys.executable
    cmd = [py, os.path.join(ROOT, "tools", "dj_set.py"), name] + paths
    if args.get("bpms"):
        cmd += ["--bpms", ",".join(str(float(b)) for b in args["bpms"])]
    if args.get("blend_bars") is not None:
        cmd += ["--blend-bars", str(int(args["blend_bars"]))]
    if args.get("auto_order", True):        # the playlist brain is the default
        cmd += ["--auto-order"]
    if args.get("audit"):                   # the set hears itself (render + listener)
        cmd += ["--audit"]
    for bk in (args.get("bridge") or []):
        cmd += ["--bridge", str(int(bk))]
    if args.get("bridge_auto"):             # probe every hop's tail; bridge where it sings
        cmd += ["--bridge-auto"]
    if args.get("arc") in ("warmup", "closer"):     # crowd-energy preset (peak = default)
        cmd += ["--arc", args["arc"]]
    rc, o, e = run(cmd, timeout=600)
    if rc != 0:
        return f"dj_set failed:\n{(o + e)[-800:]}"
    return o.strip() + "\nThe grid TRAVELS (tempoMap steps at each swap bar) — every transition is editable automation."


def _ensure_prop(name, path):
    """MUTATOR-ONLY prop genesis (2026-07-11, run id 11): a mid-run verdict consumed
    the prop; every proposal-targeted write then failed "no such song" and the agent
    'fixed' it by writing THE BASE. A mutator addressing _prop_<song> with a live
    base mints the prop from it (atomic, zero-diff = scope-clean). Readers must
    NEVER call this."""
    if os.path.exists(path) or not name.startswith("_prop_"):
        return
    base = os.path.join(SONGS, f"{name[len('_prop_'):]}.json")
    if not os.path.exists(base):
        return
    tmp = path + ".w~"
    shutil.copy(base, tmp)
    os.replace(tmp, path)

def _load_song(args, key="song", mutate=False):
    name = resolve_song_name(args[key])
    path = os.path.join(SONGS, f"{name}.json")
    if mutate:
        _ensure_prop(name, path)      # mutators mint absent props from the base
    if not os.path.exists(path):
        return name, path, None
    return name, path, json.load(open(path))

def t_list_plugin_params(args):
    """Enumerate EVERY automatable parameter in the session (faust zones, VST3 params,
    volume/pan, sends, master chain) with current value + range — the agent's knob map."""
    name, path, song = _load_song(args)
    if song is None:
        return f"no such song '{name}'"
    rc, out, err = run([M1, "list-params", path], timeout=300)
    payload = next((l for l in out.splitlines() if l.startswith("PARAMS_JSON ")), None)
    if rc != 0 or payload is None:
        return f"list-params failed (exit {rc}): {(out + err)[-500:]}"
    rows = json.loads(payload[len("PARAMS_JSON "):])
    want = args.get("track")
    if want:
        rows = [r for r in rows if r["track"] == want]
    by = {}
    for r in rows:
        by.setdefault(f"{r['track']} / {r['plugin']}", []).append(
            {"param": r["param"], "value": round(r["value"], 4),
             "range": [round(r["min"], 4), round(r["max"], 4)]})
    total = sum(len(v) for v in by.values())
    for k in by:
        if len(by[k]) > 40:
            by[k] = by[k][:40] + [{"param": f"...+{len(by[k]) - 40} more (ask with track filter)"}]
    return json.dumps({"total_params": total, "plugins": by}, indent=1)

def t_set_track_param(args):
    """Set ONE parameter statically: target 'source.<param>' | 'fx[i].<param>' | 'gainDb' | 'pan'.
    Faust params use real units (see list_plugin_params ranges); vst3 params are 0..1."""
    name, path, song = _load_song(args, mutate=True)
    if song is None:
        return f"no such song '{name}'"
    tname, target, value = args["track"], str(args["target"]), args["value"]
    if not isinstance(value, (int, float)):
        return "value must be a number"
    matches = [t for t in song["tracks"] if t.get("name") == tname]
    if not matches:
        return f"no track '{tname}'. tracks: {[t.get('name') for t in song['tracks']]}"
    t = matches[0]
    if target in ("gainDb", "pan"):
        t[target] = value
    elif target.startswith("source."):
        t.setdefault("source", {}).setdefault("params", {})[target[7:]] = value
    elif target.startswith("fx[") and "]." in target:
        idx = int(target[3:target.index("]")])
        fx = t.get("fx", [])
        if idx < 0 or idx >= len(fx):
            return f"fx[{idx}] out of range — track has {len(fx)} fx (set_track_fx first)"
        fx[idx].setdefault("params", {})[target.split("].", 1)[1]] = value
    else:
        return f"bad target '{target}' (use source.<param> | fx[i].<param> | gainDb | pan)"
    _awrite(path, song)
    _rc(name, "set_track_param",
        fields=[f"track:{tname}:{target}" if target in ("gainDb", "pan")
                else f"track:{tname}:source" if target.startswith("source.")
                else f"track:{tname}:fx"],
        summary=f"{tname}.{target} = {value}")
    return f"OK: {tname}.{target} = {value}"

def t_automate(args):
    """Write an automation curve — MOTION over time. target: gainDb | pan | fx[i].<param> |
    source.<param> (track scope) or masterGainDb | master[i].<param> (song scope, omit track).
    points: [{beat, v, curve?}] in the param's real units. curve (-1..1, on the segment
    LEAVING that point): 0 linear, >0 late-bloom (hold then accelerate — THE build shape),
    <0 early-jump (fast then settle — drops/duck releases).
    Replaces any existing curve on the same target. points=[] clears it."""
    name, path, song = _load_song(args, mutate=True)
    if song is None:
        return f"no such song '{name}'"
    target = str(args["target"])
    points = args["points"]
    if isinstance(points, str):
        try:
            points = json.loads(points)
        except json.JSONDecodeError as e:
            return f"points is not valid JSON: {e}"
    total = float(song.get("lengthBars", 4)) * 4
    norm = []
    for p in points:
        beat, v = (p[0], p[1]) if isinstance(p, list) else (p.get("beat"), p.get("v"))
        if not isinstance(beat, (int, float)) or not isinstance(v, (int, float)):
            return "each point needs numeric beat and v"
        if not 0 <= beat <= total:
            return f"point beat {beat} outside song 0..{total}"
        np_ = {"beat": beat, "v": v}
        cv = p.get("curve") if isinstance(p, dict) else (p[2] if isinstance(p, list) and len(p) > 2 else None)
        if isinstance(cv, (int, float)) and cv != 0:
            np_["curve"] = max(-1.0, min(1.0, float(cv)))
        norm.append(np_)
    norm.sort(key=lambda p: p["beat"])
    tname = args.get("track")
    if tname:
        matches = [t for t in song["tracks"] if t.get("name") == tname]
        if not matches:
            return f"no track '{tname}'. tracks: {[t.get('name') for t in song['tracks']]}"
        holder = matches[0]
        if target.startswith("fx[") and "]." in target:
            idx = int(target[3:target.index("]")])
            if idx >= len(holder.get("fx", [])):
                return f"fx[{idx}] out of range — track has {len(holder.get('fx', []))} fx"
    else:
        if not (target == "masterGainDb" or target.startswith("master[")):
            return "song-scope automation targets: masterGainDb | master[i].<param> (or pass track)"
        holder = song
    autos = [a for a in holder.get("automation", []) if a.get("target") != target]
    if norm:
        autos.append({"target": target, "points": norm})
    holder["automation"] = autos
    _awrite(path, song)
    _rc(name, "automate",
        fields=[f"track:{tname}:automation" if tname else "meta:automation"],
        summary=f"automation {target} ({len(norm)} pts)")
    scope = f"track '{tname}'" if tname else "song"
    return (f"OK: {scope} automation {target} = {len(norm)} points "
            f"({norm[0]['v']} @ beat {norm[0]['beat']} -> {norm[-1]['v']} @ beat {norm[-1]['beat']})"
            if norm else f"OK: cleared automation {target} on {scope}")

def t_set_buses(args):
    """Define the song's FX buses (shared sends): [{id, gainDb, fx:[{id, params}]}].
    Route tracks into them with update_track sends=[{bus, gainDb}]."""
    name, path, song = _load_song(args, mutate=True)
    if song is None:
        return f"no such song '{name}'"
    buses = args["buses"]
    if isinstance(buses, str):
        try:
            buses = json.loads(buses)
        except json.JSONDecodeError as e:
            return f"buses is not valid JSON: {e}"
    avail = set(list_instruments())
    vsts = vst_names()
    for b in buses:
        if not b.get("id"):
            return "each bus needs an id"
        for f in b.get("fx", []):
            err = _check_fx_entry(f, avail, vsts)
            if err:
                return "bus " + err
    song["buses"] = buses
    _awrite(path, song)
    _rc(name, "set_buses", fields=["buses"], summary=f"buses = {[b['id'] for b in buses]}")
    bus_v = "".join(_track_verdict({"name": "bus:" + str(b.get("id", "?")),
                                    "fx": b.get("fx", []), "pan": 0}) for b in buses)
    return (f"OK: buses = {[b['id'] for b in buses]} (route tracks with update_track sends)"
            + bus_v)

def t_render_song(args):
    name = resolve_song_name(args["name"])   # the 57th site: keyed "name", not "song"
    song = os.path.join(SONGS, f"{name}.json")
    wav = os.path.join(SONGS, f"{name}.wav")
    if not os.path.exists(song):
        return f"no such song '{name}'. write_song first."
    # PREVIEW WINDOW (firing 119, completion-variance): self-check renders on long
    # songs were the compose loop's biggest swing (72-bar full renders x2-3 under
    # load). max_bars=N renders a leading slice for the ears loop — the FINAL full
    # render is the sidecar's job after the proposal anyway.
    mb = args.get("max_bars")
    if not mb and not args.get("full"):
        # THE PREVIEW CLAMP (BEST_DAW_30 #11b, CC4 §7.1): the 16-bar preview was
        # prompt LAW but never enforced — under load a >24-bar self-check render
        # was the compose loop's biggest swing. Server-side now: long songs
        # preview at 16 bars unless full:true (the sidecar's final render and
        # explicit full renders are untouched).
        try:
            if float(json.load(open(song)).get("lengthBars", 0)) > 24:
                mb = 16
        except Exception:
            pass
    if mb:
        try:
            doc = json.load(open(song))
            mb = max(4, int(mb))
            if float(doc.get("lengthBars", 0)) > mb:
                lim = mb * 4.0
                doc["lengthBars"] = mb
                doc["sections"] = [x for x in doc.get("sections", [])
                                   if float(x.get("startBar", 0)) < mb]
                for t in doc.get("tracks", []):
                    t["notes"] = [n for n in t.get("notes", []) if n["start"] < lim]
                    if "audioClips" in t:
                        t["audioClips"] = [c for c in t["audioClips"]
                                           if float(c.get("startBeat", 0)) < lim]
                song = os.path.join(SONGS, f"_pv_{name}.json")
                wav = os.path.join(SONGS, f"{name}.wav")   # same wav: analyze_wav path unchanged
                _awrite(song, doc)
        except Exception as e:
            return f"preview slice failed: {e}"
    rc, out, err = run([M1, "render", song, wav], timeout=300)
    if song.endswith(f"_pv_{name}.json"):
        os.path.exists(song) and os.remove(song)
    lines = "\n".join(l for l in (out + err).splitlines() if l.startswith("[m1]"))
    if rc != 0:
        return f"RENDER FAILED (exit {rc}):\n{lines or (out+err)[-800:]}"
    clamp_note = ""
    if mb and not args.get("max_bars"):
        clamp_note = (f"\nNOTE: auto-clamped to a {int(mb)}-bar PREVIEW (song is longer) — "
                      f"the ears see the opening slice; pass full:true for the whole song.")
    return f"RENDER OK -> songs/{name}.wav\n{lines}{clamp_note}\nNext: analyze_wav songs/{name}.wav"

def t_analyze_wav(args):
    path = args["path"]
    if not os.path.isabs(path):
        path = os.path.join(ROOT, path)
    if not os.path.exists(path):
        return f"no such file: {path}"
    py = VENV_PY if os.path.exists(VENV_PY) else "python3"
    rc, out, err = run([py, ANALYZE, path], timeout=120)
    return out if rc == 0 else f"ANALYZE FAILED:\n{err[-800:]}"

def t_master_report(args):
    """THE VERDICT: render (if stale) + analyze + compare against the genre's KG
    MixTarget -> pass/fix JSON with per-check deltas and source-fix hints."""
    py = VENV_PY if os.path.exists(VENV_PY) else "python3"
    cmd = [py, os.path.join(ROOT, "tools", "master_report.py")]
    if args.get("song"):
        cmd.append(str(args["song"]))
    if args.get("wav"):
        w = args["wav"]
        cmd += ["--wav", w if os.path.isabs(w) else os.path.join(ROOT, w)]
    if args.get("genre"):
        cmd += ["--genre", str(args["genre"])]
    if args.get("platform"):
        cmd += ["--platform", str(args["platform"])]
    if not args.get("song") and not args.get("wav"):
        return "need song or wav"
    rc, out, err = run(cmd, timeout=900)   # may render first
    if out.strip().startswith("{"):
        return out
    return f"MASTER REPORT FAILED:\n{(err or out)[-800:]}"


def t_auto_master(args):
    """THE CONVERGER: closed-loop mastering — normalize the chain (character kept,
    legacy limiter killed, masterGainDb folded), then iterate render->measure->adjust
    (trims/ceiling/capped eq + dark filter) until the verdict passes. Deterministic;
    touches ONLY master[] + masterGainDb."""
    py = VENV_PY if os.path.exists(VENV_PY) else "python3"
    cmd = [py, os.path.join(ROOT, "tools", "auto_master.py"), str(args["song"])]
    if args.get("genre"):
        cmd += ["--genre", str(args["genre"])]
    if args.get("platform"):
        cmd += ["--platform", str(args["platform"])]
    if args.get("reference"):
        ref = str(args["reference"])
        cmd += ["--reference", ref if os.path.isabs(ref) else os.path.join(ROOT, ref)]
    if args.get("max_iters"):
        cmd += ["--max-iters", str(int(args["max_iters"]))]
    if args.get("no_eq"):
        cmd.append("--no-eq")
    rc, out, err = run(cmd, timeout=1800)   # up to 8 renders
    if out.strip().startswith("{"):
        _rc(resolve_song_name(args["song"]), "auto_master",
            fields=["master", "meta:master", "masterGainDb", "meta:masterGainDb"],
            summary="auto-master convergence loop")
        return out
    return f"AUTO-MASTER FAILED:\n{(err or out)[-800:]}"

def t_analyze_reference(args):
    """V27: reference wav/mp3 -> gap report vs the current song (+ optional KG MixTarget lane).
    No reference given + the song has a DECK (songs/<name>.refs.json) -> judge vs
    the deck COMPOSITE (BEST_DAW_30 #7b: the standing multi-ref contract)."""
    py = VENV_PY if os.path.exists(VENV_PY) else "python3"
    if not args.get("reference") and args.get("song"):
        nm = resolve_song_name(args["song"])
        if os.path.exists(os.path.join(SONGS, f"{nm}.refs.json")):
            cmd = [py, os.path.join(ROOT, "tools", "reference_match.py"), "--deck", nm]
            if args.get("genre"):
                cmd += ["--genre", args["genre"]]
            rc, out, err = run(cmd, timeout=900)
            if rc != 0:
                return f"REFERENCE DECK FAILED:\n{(err or out)[-800:]}"
            return out.strip() + "\nTurn each gap line into ONE proposal move; re-render and re-check."
        return ("no reference given and no deck — pass reference=<wav/mp3>, or build "
                "a standing deck first: reference_deck {song, action:'add', path}")
    ref = args["reference"]
    if not os.path.isabs(ref):
        ref = os.path.join(ROOT, ref)
    if not os.path.exists(ref):
        return f"no such reference: {ref}"
    cmd = [py, os.path.join(ROOT, "tools", "reference_match.py"), ref]
    if args.get("song"):
        cmd += ["--song", args["song"]]
    elif args.get("wav"):
        cmd += ["--wav", args["wav"] if os.path.isabs(args["wav"]) else os.path.join(ROOT, args["wav"])]
    else:
        return "need song or wav for the current mix"
    if args.get("genre"):
        cmd += ["--genre", args["genre"]]
    rc, out, err = run(cmd, timeout=600)
    if rc != 0:
        return f"REFERENCE MATCH FAILED:\n{(err or out)[-800:]}"
    return out.strip() + "\nTurn each gap line into ONE proposal move; re-render and re-check."

def t_release_pack(args):
    """THE RELEASE PACK (BEST_DAW_30 #27): one call -> a label-ready folder
    (C2PA master, stems, MIDI, .dawproject, credits + THE LICENSE GATE)."""
    py = VENV_PY if os.path.exists(VENV_PY) else "python3"
    cmd = [py, os.path.join(ROOT, "tools", "release_pack.py"),
           resolve_song_name(args["song"])]
    if args.get("platforms"):
        plats = args["platforms"]
        cmd += ["--platforms", ",".join(plats) if isinstance(plats, list) else str(plats)]
    if args.get("bits"):
        cmd += ["--bits", str(args["bits"])]
    rc, out, err = run(cmd, timeout=1800)
    return out.strip() if rc == 0 else f"RELEASE PACK PARTIAL/FAILED:\n{(out + err)[-800:]}"


def t_diff_ear(args):
    """THE DIFFERENTIAL EAR (BEST_DAW_30 #22b): 'what changed?' between two
    renders as ONE measured sentence + ranked deltas + a playable Δ residue."""
    py = VENV_PY if os.path.exists(VENV_PY) else "python3"
    cmd = [py, os.path.join(ROOT, "tools", "diff_ear.py")]
    if args.get("song"):
        cmd += ["--song", resolve_song_name(args["song"])]
    elif args.get("a") and args.get("b"):
        pa = args["a"] if os.path.isabs(args["a"]) else os.path.join(ROOT, args["a"])
        pb = args["b"] if os.path.isabs(args["b"]) else os.path.join(ROOT, args["b"])
        cmd += [pa, pb]
    else:
        return "need song= (base vs pending take) or a= + b= (two wavs)"
    rc, out, err = run(cmd, timeout=300)
    return out.strip() if rc == 0 else f"DIFF EAR FAILED:\n{(err or out)[-600:]}"


def t_reference_deck(args):
    """THE REFERENCE DECK (BEST_DAW_30 #7b): manage a song's standing multi-ref
    target — 'make it sit like THESE three tracks' becomes a per-project
    contract, judged by analyze_reference with no arguments. Analysis only;
    the deck stores paths + numbers, never audio."""
    song = resolve_song_name(args["song"])
    action = str(args.get("action", "list"))
    py = VENV_PY if os.path.exists(VENV_PY) else "python3"
    cmd = [py, os.path.join(ROOT, "tools", "reference_match.py"), "--song", song]
    if action == "add":
        if not args.get("path"):
            return "add needs path=<audio file>"
        cmd += ["--deck-add", str(args["path"]), "--weight", str(args.get("weight", 1.0))]
    elif action == "remove":
        cmd += ["--deck-remove", str(args.get("path") or args.get("index", ""))]
    else:
        cmd += ["--deck-list"]
    rc, out, err = run(cmd, timeout=900)
    if rc != 0:
        return f"REFERENCE DECK FAILED:\n{(err or out)[-600:]}"
    tail = ("\nJudge the mix against it any time: analyze_reference {song} with no "
            "reference argument." if action == "add" else "")
    return out.strip() + tail


def t_match_reference(args):
    """R2 THE REFERENCE CIRCLE: gap report vs a STORED (:Reference) node — the
    record's DNA was banked at import, so the reference wav is never re-read.
    The KG client + the ears live in the venv (system python has neither):
    shell out, exactly like t_analyze_reference."""
    py = VENV_PY if os.path.exists(VENV_PY) else "python3"
    rc, out, err = run([py, os.path.join(ROOT, "tools", "reference_match.py"),
                        "--stored", str(args["reference"]),
                        "--song", str(args["song"])], timeout=900)
    if rc != 0 or not out.strip().startswith("{"):
        return f"REFERENCE MATCH FAILED:\n{(err or out)[-800:]}"
    return out.strip() + ("\nTurn each gap into ONE proposal move; groove_move "
                          "(when present) is apply_groove-ready.")

def t_time_machine(args):
    """R7: the agent's TIME MACHINE twin — the song's whole timeline (accepts +
    crash-net journal moments) as data, and any point resurrected AS A PROPOSAL
    (the base changes only on user accept; history is never rewritten)."""
    song = resolve_song_name(args["song"])
    tl = os.path.join(ROOT, "tools", "timeline.py")
    if str(args.get("action", "list")) == "restore":
        if not args.get("ref"):
            return "restore needs ref — a commit hash or journal filename from action:list"
        rc, out, err = run(["python3", tl, "restore", song, str(args["ref"])],
                           timeout=120)
        if rc == 0 and "PROPOSAL from" in out:
            _rc(song, "time_machine", fields=["*"], track_wild=["*"],
                summary=f"restored {str(args['ref'])[:24]} as the proposal")
        return (out or err)[-800:].strip() or "restore produced no output"
    rc, out, err = run(["python3", tl, "list", song, "--json", "--limit",
                        str(int(args.get("limit", 20) or 20))], timeout=120)
    if rc != 0 or not out.strip():
        return f"timeline failed:\n{(err or out)[-400:]}"
    return (out.strip()
            + "\nrefs: pass a commit hash (accept) or journal filename (take) to "
              "action:restore — it stages a PROPOSAL, never touches the base.")

def t_finish_audit(args):
    """V40: the anti-abandonment audit -> staged plan to DONE."""
    py = VENV_PY if os.path.exists(VENV_PY) else "python3"
    cmd = [py, os.path.join(ROOT, "tools", "finish_audit.py"), str(args["song"])]
    if args.get("genre"):
        cmd += ["--genre", args["genre"]]
    rc, out, err = run(cmd, timeout=600)
    if rc != 0:
        return f"FINISH AUDIT FAILED:\n{(err or out)[-800:]}"
    return out.strip() + "\nExecute the staged plan ONE stage per proposal; re-run finish_audit after each accept."

def t_publish_song(args):
    """V22: the ONE outbound audio path — finish gate -> C2PA master -> ears -> verify -> upload."""
    py = VENV_PY if os.path.exists(VENV_PY) else "python3"
    cmd = [py, os.path.join(ROOT, "tools", "publish_flow.py"), str(args["song"])]
    if args.get("genre"):
        cmd += ["--genre", args["genre"]]
    if args.get("title"):
        cmd += ["--title", str(args["title"])]
    if args.get("public"):
        cmd += ["--public"]
    if args.get("dry_run", True):          # DEFAULT DRY RUN — upload only on explicit ask
        cmd += ["--dry-run"]
    rc, out, err = run(cmd, timeout=900)
    return out.strip() if out else f"PUBLISH FAILED:\n{(err or '')[-600:]}"

def t_stem_callouts(args):
    """V28: per-track solo analysis + cross-stem masking — callouts, not stats."""
    py = VENV_PY if os.path.exists(VENV_PY) else "python3"
    cmd = [py, os.path.join(ROOT, "tools", "stem_callouts.py"), str(args["song"])]
    if args.get("sections"):
        cmd.append("--by-section")
    rc, out, err = run(cmd, timeout=900)
    if rc != 0:
        return f"STEM CALLOUTS FAILED:\n{(err or out)[-600:]}"
    return out.strip() + "\nFix at the SOURCE per callout; re-render; re-run to confirm the fight is over."

def t_beat_grid(args):
    """EARS v4: neural beat/downbeat truth on demand (imports/DJ/groove lanes)."""
    path = args["path"]
    if not os.path.isabs(path):
        path = os.path.join(ROOT, path)
    if not os.path.exists(path):
        return f"no such file: {path}"
    py = VENV_PY if os.path.exists(VENV_PY) else "python3"
    rc, out, err = run([py, os.path.join(ROOT, "tools", "beatgrid.py"), path], timeout=600)
    return out.strip() if rc == 0 else f"BEAT GRID FAILED:\n{(err or out)[-500:]}"

def t_loop_infill(args):
    """Co-creation reroll: keep what the user likes, regenerate ONE part's notes."""
    py = VENV_PY if os.path.exists(VENV_PY) else "python3"
    cmd = [py, os.path.join(ROOT, "tools", "loop_infill.py"), str(args["song"]), str(args["part"]),
           "--seed", str(int(args.get("seed", 1)))]
    if args.get("genre"):
        cmd += ["--genre", str(args["genre"])]
    rc, out, err = run(cmd, timeout=300)
    if rc == 0:
        _rc(resolve_song_name(args["song"]), "loop_infill",
            track_wild=[str(args["part"])], summary=f"reroll {args['part']}")
    return out.strip() if out else f"INFILL FAILED:\n{(err or '')[-400:]}"

def t_lock_track(args):
    """EDIT LOCKS: a USER-protective meta action — writes the BASE song directly
    (locks are not musical content; they are the user's ground rules)."""
    song = str(args["song"])
    path = os.path.join(ROOT, "songs", f"{song}.json")
    if not os.path.exists(path):
        return f"no such song: {song}"
    doc = json.load(open(path))
    want = str(args["track"])
    locked = bool(args.get("locked", True))
    hit = None
    for t in doc.get("tracks", []):
        if t.get("name") == want:
            if locked:
                t["locked"] = True
            else:
                t.pop("locked", None)
            hit = t
            break
    if hit is None:
        return f"no track '{want}' in {song} (tracks: " + ", ".join(t.get("name", "?") for t in doc.get("tracks", [])) + ")"
    _awrite(path, doc)
    _rc(song, "lock_track", fields=[f"track:{want}:locked"],
        summary=f"{want} {'locked' if locked else 'unlocked'}")
    state = "LOCKED" if locked else "unlocked"
    return (f"'{want}' is now {state}. Locked tracks are the user's ground — proposals that "
            f"touch them get that track REVERTED by the sidecar (the rest survives).")

def t_freeze_track(args):
    """V47 FREEZE: freeze IS a cached render of symbols — nothing symbolic is lost."""
    song = str(args["song"])
    track = str(args.get("track", ""))
    action = str(args.get("action", "freeze"))
    tool = os.path.join(ROOT, "tools", "freeze.py")
    if action == "check":
        rc, out, err = run(["python3", tool, "check", song], timeout=120)
        return out.strip() if rc == 0 else f"FREEZE CHECK FAILED:\n{(err or out)[-400:]}"
    if not track:
        return "MISSING ARGUMENT: track (which track to freeze/unfreeze)"
    rc, out, err = run(["python3", tool, action, song, track], timeout=600)
    if rc != 0:
        return f"FREEZE {action.upper()} FAILED:\n{(err or out)[-400:]}"
    _rc(song, "freeze_track", track_wild=track,
        summary=f"{track} {action} (cached render of symbols)")
    return out.strip() + ("\nThe track now PLAYS the cache; its symbols live in track.frozen "
                          "(gain/pan/sends stay live). unfreeze restores them bit-exact."
                          if action == "freeze" else "")

def t_session_recap(args):
    """V42: where you left off + ONE next step (persona #2: zero executive-function reopen)."""
    rc, out, err = run(["python3", os.path.join(ROOT, "tools", "recap.py")], timeout=60)
    return out.strip() if rc == 0 else f"RECAP FAILED:\n{(err or out)[-400:]}"

def t_hear(args):
    """THE SOUND TENSOR: mel-band x time ASCII heatmap — SIGHT, not statistics."""
    path = args["path"]
    if not os.path.isabs(path):
        path = os.path.join(ROOT, path)
    if not os.path.exists(path):
        return f"no such file: {path}"
    py = VENV_PY if os.path.exists(VENV_PY) else "python3"
    cmd = [py, os.path.join(ROOT, "tools", "hear.py"), path]
    if args.get("bpm"):
        cmd += ["--bpm", str(float(args["bpm"]))]
    rc, out, err = run(cmd, timeout=120)
    return out if rc == 0 else f"HEAR FAILED:\n{err[-800:]}"

def t_listen_live(args):
    """THE EARS BUS (E3 R2): tail the live master-bus feature frames the EarsTap
    plugin streams to <ipc>/ears.jsonl while anything plays or renders. READ-only
    reflexes — hear()/analyze_wav stay the deep ears."""
    secs = max(1.0, min(30.0, float(args.get("seconds", 5))))
    ipc = os.environ.get("SOTADAW_IPC") or os.path.join(ROOT, "agent", "ipc")
    p = os.path.join(ipc, "ears.jsonl")
    if not os.path.exists(p):
        return ("the ears are silent — no ears.jsonl yet. The bus streams only while "
                "the app plays or a render runs (EarsTap rides the master chain).")
    now = time.time()
    frames = []
    try:
        with open(p, "rb") as f:
            f.seek(0, 2)
            f.seek(max(0, f.tell() - 65536))
            for ln in f.read().decode("utf-8", "replace").strip().splitlines():
                try:
                    fr = json.loads(ln)
                    if now - float(fr.get("t", 0)) <= secs:
                        frames.append(fr)
                except Exception:
                    continue
    except Exception as e:
        return f"listen_live failed: {e!r}"
    live = [f for f in frames if f.get("playing")]
    if not live:
        age = (now - float(json.loads(open(p, "rb").readlines()[-1])["t"])) \
            if os.path.getsize(p) else 1e9
        return (f"the ears are silent — nothing played or rendered in the last {secs:.0f}s "
                f"(last frame {age:.0f}s ago). Start playback or a render, then listen again.")
    names = ["low", "lowmid", "mid", "high"]
    last = live[-1]
    b = last.get("bands_db", [-120] * 4)
    dom = names[max(range(4), key=lambda i: b[i])]
    rms0 = sum(live[0].get("rms_db", [-120, -120])) / 2
    rms1 = sum(last.get("rms_db", [-120, -120])) / 2
    trend = "rising" if rms1 - rms0 > 1.5 else ("falling" if rms0 - rms1 > 1.5 else "steady")
    return (f"HEARING {len(live)} live frames over {secs:.0f}s "
            f"(beats {live[0].get('beat', 0):.1f} -> {last.get('beat', 0):.1f}):\n"
            f"now: rms {rms1:.1f} dB ({trend}), peak {max(last.get('peak_db', [-120])):.1f} dB, "
            f"quick-dBTP {last.get('dbtp_q', -120):.1f}, crest {last.get('crest_db', 0):.1f} dB\n"
            f"bands: {dom}-dominant ({'/'.join(f'{names[i]} {b[i]:.0f}dB' for i in range(4))})\n"
            f"Deep ears when needed: render_song + analyze_wav (metrology) or hear (sight).")

def t_build_loop_machine(args):
    """#33: any loops -> a playable pad machine (classified tracks x build-up scenes)."""
    paths = []
    for lp in args["loops"]:
        q = lp if os.path.isabs(lp) else os.path.join(ROOT, lp)
        if not os.path.exists(q):
            return f"no such file: {lp}"
        paths.append(q)
    name = resolve_song_name(args["song"])
    py = VENV_PY if os.path.exists(VENV_PY) else sys.executable
    cmd = [py, os.path.join(ROOT, "tools", "loop_machine.py"), "build", name] + paths
    if args.get("bpm"):
        cmd += ["--bpm", str(float(args["bpm"]))]
    rc, o, e = run(cmd, timeout=300)
    if rc != 0:
        return f"loop_machine failed:\n{(o + e)[-600:]}"
    return o.strip() + "\nPads launch scenes (MIDI hands live); slots are warped to the master grid — edit any cell with set_clip_slot."

def t_vst_presets(args):
    """The 516-preset rail: search factory presets by name/category; get returns params."""
    plugin = args.get("plugin", "")
    query = str(args.get("query", "")).lower()
    mode = args.get("mode", "list")
    # mood synonyms: producers ask in feelings, patch names answer in nouns
    MOODS = {"dark": ["dark", "deep", "night", "noir", "shadow", "black"],
             "warm": ["warm", "analog", "vintage", "tape", "soft"],
             "bright": ["bright", "shine", "sparkle", "glass", "air", "crystal"],
             "aggressive": ["aggro", "hard", "dist", "grit", "acid", "monster", "rage"],
             "dreamy": ["dream", "float", "haze", "cloud", "wash", "lush"],
             "retro": ["retro", "80", "vintage", "juno", "dx", "mks", "analog"]}
    terms = [query] + MOODS.get(query.split()[0] if query else "", [])
    py = VENV_PY if os.path.exists(VENV_PY) else sys.executable
    results = []
    lib = json.load(open(os.path.join(ROOT, "library.json"))) if os.path.exists(os.path.join(ROOT, "library.json")) else {}
    for e in lib.get("vst_presets", []):
        if plugin and plugin.lower() not in e["plugin"].lower():
            continue
        hay = e["name"].lower() + " " + e["category"].lower()
        if query and not any(t in hay for t in terms):
            continue
        results.append(e)
    if mode == "list":
        by_cat = {}
        for e in results[:400]:
            by_cat.setdefault(f'{e["plugin"]}/{e["category"]}', []).append(e["name"])
        return json.dumps(by_cat, indent=1)[:4000]
    # mode == "get": first match -> params via the right tool
    if not results:
        return f"no preset matching {query!r} (plugin={plugin!r})"
    e = results[0]
    tool = ("tal_presets.py" if e["plugin"] == "TAL-NoiseMaker"
            else "surge_presets.py" if e["plugin"] == "Surge XT"
            else "surgefx_presets.py" if e["plugin"] == "Surge XT Effects"
            else "odin_presets.py")
    rc, o, err = run([py, os.path.join(ROOT, "tools", tool), "get", e["name"]], timeout=60)
    if rc != 0:
        return f"preset load failed:\n{err[-400:]}"
    # ONE-CALL APPLY: song+track set -> the sound lands on the track directly
    # (no giant params dict through write_song; the eval-friction fix)
    if args.get("song") and args.get("track"):
        try:
            data = json.loads(o[o.index("{"):])
        except Exception:
            return o.strip()
        song_name = resolve_song_name(args["song"])
        sp = os.path.join(ROOT, "songs", f"{song_name}.json")
        if not os.path.exists(sp):
            return f"no such song: {song_name}"
        sj = json.load(open(sp))
        tr = next((t for t in sj["tracks"] if t.get("name") == args["track"]), None)
        if tr is None:
            tr = {"name": args["track"], "gainDb": 0, "pan": 0, "notes": []}
            sj["tracks"].append(tr)
        if e["plugin"] == "Surge XT Effects":
            fx = tr.setdefault("fx", [])
            fx.append(dict(data["use_as_fx"]))
            what = f"fx '{e['name']}' appended to track fx chain"
        elif "params" in data:
            tr["source"] = {"kind": "vst3", "plugin": e["plugin"], "params": data["params"]}
            what = f"source = {e['plugin']} '{e['name']}' ({len(data['params'])} params)"
        else:
            tr["source"] = {"kind": "vst3", "plugin": e["plugin"], "preset": data["preset"]}
            what = f"source = {e['plugin']} preset blob '{e['name']}'"
        _awrite(sp, sj)
        _rc(song_name, "vst_presets",
            fields=[f"track:{args['track']}:fx" if e["plugin"] == "Surge XT Effects"
                    else f"track:{args['track']}:source"],
            summary=what)
        return (f"APPLIED to {song_name}/{args['track']}: {what}. "
                f"Write notes on the track; reshape named params per synth-maps (natural units).")
    return o.strip() + "\nInline 'params' into source {kind:'vst3', plugin:'" + e["plugin"] + "', params:{...}} — or pass song+track to APPLY in one call."

def t_reaper(args):
    """REAPER bridge: import .rpp -> song.json, or export song -> .rpp."""
    py = VENV_PY if os.path.exists(VENV_PY) else sys.executable
    if args.get("rpp_in"):
        rp = args["rpp_in"] if os.path.isabs(args["rpp_in"]) else os.path.join(ROOT, args["rpp_in"])
        if not os.path.exists(rp):
            return f"no such file: {args['rpp_in']}"
        name = resolve_song_name(args.get("song"), default="reaper_import")
        out = os.path.join(ROOT, "songs", f"{name}.json")
        rc, o, e = run([py, os.path.join(ROOT, "tools", "reaper_bridge.py"), "import", rp, out], timeout=120)
        return (o + e).strip() + f"\nNow assign real voices per track (imported tracks default to pluck)."
    sp = os.path.join(ROOT, "songs", f"{args['song']}.json")
    if not os.path.exists(sp):
        return f"no such song: {args['song']}"
    out = args.get("rpp_out") or os.path.join(ROOT, "songs", f"{args['song']}.rpp")
    if not os.path.isabs(out):
        out = os.path.join(ROOT, out)
    rc, o, e = run([py, os.path.join(ROOT, "tools", "reaper_bridge.py"), "export", sp, out], timeout=120)
    return (o + e).strip()

def t_scene_bounce(args):
    """Launcher EARS: materialize scene k as a timeline render + analysis."""
    song = resolve_song_name(args["song"])
    sp = os.path.join(ROOT, "songs", f"{song}.json")
    if not os.path.exists(sp):
        return f"no such song: {song}"
    py = VENV_PY if os.path.exists(VENV_PY) else sys.executable
    cmd = [py, os.path.join(ROOT, "tools", "scene_bounce.py"), sp, str(args["scene"])]
    if args.get("bars"):
        cmd += ["--bars", str(int(args["bars"]))]
    rc, o, e = run(cmd, timeout=300)
    if rc != 0:
        return f"scene_bounce failed:\n{(o + e)[-500:]}"
    wav = [w for w in o.split() if w.endswith(".wav")]
    extra = ""
    if wav:
        rc2, o2, e2 = run([py, os.path.join(ROOT, "tools", "analyze2.py"), wav[-1]], timeout=120)
        if rc2 == 0:
            extra = "\n" + o2.strip()[:900]
    return o.strip() + extra

def t_scene_strips(args):
    """Append performance strip scenes (Drums only / No drums / Bass+Drums)."""
    song = resolve_song_name(args["song"])
    sp = os.path.join(ROOT, "songs", f"{song}.json")
    if not os.path.exists(sp):
        return f"no such song: {song}"
    py = VENV_PY if os.path.exists(VENV_PY) else sys.executable
    cmd = [py, os.path.join(ROOT, "tools", "scene_strips.py"), sp]
    if args.get("from_scene") is not None:
        cmd += ["--from-scene", str(int(args["from_scene"]))]
    rc, o, e = run(cmd, timeout=120)
    if rc != 0:
        return f"scene_strips failed:\n{(o + e)[-400:]}"
    return o.strip() + "\nVerify each with scene_bounce; pads launch them live."

def t_arrange_song(args):
    """Loop -> song skeleton: sectioned arrangement, deterministic."""
    song = resolve_song_name(args["song"])
    sp = os.path.join(ROOT, "songs", f"{song}.json")
    if not os.path.exists(sp):
        return f"no such song: {song}"
    py = VENV_PY if os.path.exists(VENV_PY) else sys.executable
    cmd = [py, os.path.join(ROOT, "tools", "arrange.py"), sp]
    if args.get("genre"):
        cmd += ["--genre", str(args["genre"])]
    if args.get("form"):
        cmd += ["--form", str(args["form"])]
    # unspecified seed = fresh sampled form each ask (seed 0 froze form='pop' into
    # ONE structure forever); explicit seed still reproduces exactly
    cmd += ["--seed", str(int(args["seed"])) if args.get("seed") is not None
            else str(int.from_bytes(os.urandom(3), "big"))]
    if args.get("out"):
        cmd += ["--out", re.sub(r"[^a-z0-9_]", "", str(args["out"]).lower())]
    rc, o, e = run(cmd, timeout=120)
    if rc != 0:
        return f"arrange failed:\n{(o + e)[-400:]}"
    _rc(resolve_song_name(args.get("out") or args["song"]),
        "arrange_song", fields=["*"], summary="arranged loop -> song")
    return o.strip() + "\nNow differentiate: automation arcs per section, a second seed's material in drop2, ear-check with render+analyze."

def t_make_track(args):
    """THE ONE CALL: genre -> generated loop -> arranged track -> rendered + analyzed."""
    genre = re.sub(r"[^a-z0-9_]", "", str(args["genre"]).lower())
    song = resolve_song_name(args.get("song") or f"{genre}_track")
    seed = int(args.get("seed", 0))
    py = VENV_PY if os.path.exists(VENV_PY) else sys.executable
    loop_name = f"_mt_{song}"
    rc, o, e = run([py, os.path.join(ROOT, "tools", "loop_gen.py"), genre, loop_name,
                    "--bars", "4", "--seed", str(seed)], timeout=120)
    if rc != 0:
        return f"loop_gen failed:\n{(o + e)[-400:]}"
    rc, o2, e2 = run([py, os.path.join(ROOT, "tools", "arrange.py"),
                      os.path.join(ROOT, "songs", f"{loop_name}.json"),
                      "--out", song, "--genre", genre], timeout=120)
    try:
        os.remove(os.path.join(ROOT, "songs", f"{loop_name}.json"))
    except OSError:
        pass
    if rc != 0:
        return f"arrange failed:\n{(o2 + e2)[-400:]}"
    wav = os.path.join(ROOT, "songs", f"{song}.wav")
    rc, o3, e3 = run([M1, "render", os.path.join(ROOT, "songs", f"{song}.json"), wav], timeout=600)
    if "ok=1" not in o3 + e3:
        return f"render failed:\n{(o3 + e3)[-300:]}"
    rc, o4, e4 = run([py, os.path.join(ROOT, "tools", "analyze2.py"), wav], timeout=180)
    _rc(song, "make_track", fields=["*"], summary=f"make_track {genre}")
    ears = ""
    if rc == 0:
        try:                       # EARS ON MAKE (W7): band truth vs the genre's
            _tp = os.path.join(ROOT, "tools")       # server path lacks tools/
            if _tp not in sys.path:                 # (the proto-E2E lesson)
                sys.path.insert(0, _tp)
            import doctor as _doc  # target — silent when clean, the house style
            _a = json.loads(o4.strip())
            _dna = json.load(open(os.path.join(ROOT, "agent", "dna_cache.json"))
                             )["genres"].get(genre, {})
            _v = _doc.band_verdict(_a[0] if isinstance(_a, list) else _a, _dna)
            if _v:
                ears = "\nEARS: " + " | ".join(_v)
        except Exception:
            ears = ""
    return (o.strip().splitlines()[-1] + "\n" + o2.strip().splitlines()[0] +
            f"\nRendered songs/{song}.wav\n" + (o4.strip()[:700] if rc == 0 else "") + ears +
            "\nNow make it YOURS: differentiate sections (automation arcs, drop2 variation), "
            "swap voices via vst_presets, apply_groove for feel. New seed = new track.")

def t_tune_vocal(args):
    """CONTEXT-TUNE (V45): song-aware pitch correction on a track's audio clip.
    Reads the ARRANGEMENT (per-beat chord field from all other tracks + scale) and
    retunes through the WORLD vocoder — formants preserved, timing untouched.
    Non-destructive: writes a new wav, swaps the clip file, keeps tuning provenance;
    always re-tunes from the ORIGINAL source (never double-processes)."""
    name, path, song = _load_song(args, mutate=True)
    if song is None:
        return f"no such song '{name}'"
    tname = args["track"]
    trs = [t for t in song.get("tracks", []) if t.get("name") == tname]
    if not trs:
        return f"no track named '{tname}'. tracks: {[t.get('name') for t in song['tracks']]}"
    clips = trs[0].get("audioClips") or []
    ci = int(args.get("clip_index", 0))
    if not clips or ci >= len(clips):
        return f"track '{tname}' has no audioClip[{ci}] — tune_vocal works on audio clips."
    clip = clips[ci]
    src = (clip.get("tuning") or {}).get("source") or clip.get("file")
    src_abs = src if os.path.isabs(src) else os.path.join(ROOT, src)
    if not os.path.exists(src_abs):
        return f"clip source missing: {src}"
    style = str(args.get("style", "natural"))
    if style not in ("tpain", "hard", "natural", "transparent"):
        return "style must be tpain|hard|natural|transparent"
    stem = re.sub(r"[^a-z0-9_]", "", os.path.splitext(os.path.basename(src))[0].lower())
    out_rel = f"songs/_tuned_{stem}_{style}.wav"
    rep_rel = f"songs/_tuned_{stem}_{style}.report.json"
    py = VENV_PY if os.path.exists(VENV_PY) else sys.executable
    cmd = [py, os.path.join(ROOT, "tools", "retune.py"), src_abs, os.path.join(ROOT, out_rel),
           "--song", path, "--track", tname, "--style", style,
           "--clip-index", str(ci), "--report", os.path.join(ROOT, rep_rel)]
    if args.get("strength") is not None:
        cmd += ["--strength", str(float(args["strength"]))]
    if args.get("guide_track"):
        cmd += ["--guide-track", str(args["guide_track"])]
    if args.get("key"):
        cmd += ["--key", str(args["key"])]
    if args.get("region") and len(args["region"]) == 2:
        cmd += ["--region", str(float(args["region"][0])), str(float(args["region"][1]))]
    rc_, out, err = run(cmd, timeout=600)
    if rc_ != 0:
        return f"TUNE FAILED:\n{(err or out)[-800:]}"
    try:
        rep = json.load(open(os.path.join(ROOT, rep_rel)))
    except Exception:
        rep = {"stats": {}, "notes": []}
    clip["file"] = out_rel
    clip["tuning"] = {"style": style, "source": src, "report": rep_rel}
    errs = validate_song(song)
    if errs:
        return "INVALID after tune — fix and resubmit:\n- " + "\n- ".join(errs)
    _awrite(path, song)
    _rc(name, "tune_vocal", fields=["audioClips"], track_wild=tname,
        summary=f"tune_vocal {style} {tname}")
    st = rep.get("stats", {})
    moves = sorted((n for n in rep.get("notes", []) if n.get("cents_moved")),
                   key=lambda n: -abs(n["cents_moved"]))[:5]
    mv = "\n".join(f"  b{n['beat0']} {n['sung']} -> {n['target_name']} ({n['cents_moved']:+.0f}c) {n['reason']}"
                   for n in moves if n.get("beat0") is not None)
    return (f"TUNED '{tname}' {style}: {st.get('corrected', '?')}/{st.get('events', '?')} notes, "
            f"median off {st.get('median_abs_cents_off', '?')}c. Clip -> {out_rel}\n"
            f"biggest moves:\n{mv}\n"
            f"original kept: {src} · full note-by-note report: {rep_rel}\n"
            f"Next: render_song + hear. Wrong note choice? re-run with guide_track "
            f"(a melody lane = explicit targets) or region [b0,b1] for surgical spans.")

# ---------- THE SCALPEL: surgical edits (agent/surgical.py kernel) ----------
def t_locate(args):
    """THE SCALPEL'S EYES: any human coordinate -> beat + what's sounding + candidates."""
    name, path, song = _load_song(args)
    if song is None:
        return f"no such song '{name}'"
    clock = surgical.TempoClock(song)
    parts = []
    beat = None
    try:
        if args.get("time") is not None:
            beat = surgical.resolve_time_point(song, {"time": args["time"]}, clock)
        elif args.get("beat") is not None:
            beat = float(args["beat"])
        elif args.get("bar") is not None:
            beat = float(args["bar"]) * 4.0
        elif args.get("section") is not None:
            sp = surgical.find_section(song, args["section"], int(args.get("occurrence", 1)))
            if not sp:
                return (f"no section '{args['section']}'. sections: "
                        f"{[(s[0], f'bars {s[1]/4:g}-{s[2]/4:g}') for s in surgical.section_spans(song)]}")
            beat = sp[1]
            parts.append(f"section '{sp[0]}' = bars {sp[1]/4:g}-{sp[2]/4:g} = beats {sp[1]:g}-{sp[2]:g}")
    except ValueError as e:
        return f"LOCATE ERROR: {e}"
    if beat is not None:
        parts.append(surgical.render_whats_at(
            surgical.whats_at(song, beat, halo=float(args.get("halo_beats", 1.0)))))
    q = str(args.get("query") or "").strip()
    if q:
        ranked = surgical.score_track_query(song, q)
        if ranked:
            # THE AMBIGUITY GATE (BEST_DAW_30 #13b, CC4 §7.3): top-2 within 15%
            # = the ask does not name ONE target. Below the gate the agent asks,
            # never guesses — a guessed target is a failed edit even if it lands.
            amb = (len(ranked) >= 2 and ranked[0][0] > 0
                   and (ranked[0][0] - ranked[1][0]) / max(ranked[0][0], 1e-9) < 0.15)
            parts.append(("AMBIGUOUS " if amb else "") + f"CANDIDATES for '{q}' (best first):")
            for score, ti, ev in ranked[:5]:
                t = song["tracks"][ti]
                sel = {"tracks": t.get("name")}
                if beat is not None:
                    sel["around"] = {"beat": round(beat, 3), "widthBeats": 4}
                parts.append(f"  {score:.1f}  '{t.get('name')}' [{surgical.track_role(t)[0]}] {ev}"
                             f"  -> selector {json.dumps(sel)}")
            if amb:
                parts.append(
                    "AMBIGUITY GATE: the top candidates are within 15% — do NOT "
                    "guess. Ask the user which one they mean (name the candidates "
                    "verbatim) and only edit after they choose. If you must show "
                    "work, dry-run select_notes on EACH candidate instead of editing.")
                try:   # the UI chip wire: atomic drop; chips render + a click answers
                    cp = os.path.join(ROOT, "agent", "ipc", "candidates.json")
                    tmpc = cp + ".w~"
                    json.dump({"song": name, "query": q, "t": time.time(),
                               "options": [{"track": song["tracks"][ti].get("name"),
                                            "role": surgical.track_role(song["tracks"][ti])[0],
                                            "score": round(sc, 2), "why": ev}
                                           for sc, ti, ev in ranked[:4]]},
                              open(tmpc, "w"))
                    os.replace(tmpc, cp)
                except Exception:
                    pass
        else:
            parts.append(f"no track matches '{q}'. tracks+roles: "
                         f"{[(t.get('name'), surgical.track_role(t)[0]) for t in song['tracks']]}")
    if not parts:
        secs = [(s[0], f"bars {s[1]/4:g}-{s[2]/4:g}") for s in surgical.section_spans(song)]
        return (f"MAP of '{name}': bpm {song.get('bpm')}, {song.get('lengthBars')} bars, "
                f"sections {secs or '(none)'}, tracks "
                f"{[(t.get('name'), surgical.track_role(t)[0], len(t.get('notes') or [])) for t in song.get('tracks', [])]}."
                f" Pass time/beat/bar/section and/or query to zoom in.")
    return "\n".join(parts)

def t_select_notes(args):
    """DRY-RUN a selector: see exactly what would be touched. Zero edits."""
    name, path, song = _load_song(args)
    if song is None:
        return f"no such song '{name}'"
    sel = args.get("selector") or {}
    if isinstance(sel, str):
        try:
            sel = json.loads(sel)
        except json.JSONDecodeError as e:
            return f"selector is not valid JSON: {e}"
    try:
        r = surgical.resolve(song, sel)
    except ValueError as e:
        return f"SELECTOR MISS: {e}"
    lines = [" · ".join(r.explain)]
    for ti, n in sorted(r.refs, key=lambda x: (float(x[1]["start"]), x[0]))[:40]:
        tn = song["tracks"][ti].get("name", f"#{ti}")
        lines.append(f"  {tn}: beat {float(n['start']):g} (bar {float(n['start'])/4:g}) "
                     f"{surgical.pitch_name(n['pitch'])} vel {float(n.get('vel', 0.8)):g} "
                     f"len {float(n.get('len', 0.25)):g}")
    if len(r.refs) > 40:
        lines.append(f"  ... +{len(r.refs) - 40} more")
    if not r.refs:
        lines.append("  (0 notes matched — loosen the selector, or locate first)")
    return "\n".join(lines)

def t_surgical_edit(args):
    """THE CUT: ops applied to EXACTLY the selector's notes; receipt filed; everything
    else untouchable (the sidecar diffs the proposal against receipts — SCOPE LAW)."""
    name, path, song = _load_song(args)
    if song is None:
        return f"no such song '{name}'"
    sel = args.get("selector") or {}
    if isinstance(sel, str):
        try:
            sel = json.loads(sel)
        except json.JSONDecodeError as e:
            return f"selector is not valid JSON: {e}"
    ops = args.get("ops") or []
    if isinstance(ops, str):
        try:
            ops = json.loads(ops)
        except json.JSONDecodeError as e:
            return f"ops is not valid JSON: {e}"
    if not isinstance(ops, list) or not ops:
        return ("ops must be a non-empty array of {op: set|shift|scale|quantize|humanize|"
                "stretch|velocity_ramp|delete|insert|replace|retrack, ...}")
    import copy as _copy
    work = _copy.deepcopy(song)
    try:
        receipt, r = surgical.apply_ops(work, sel, ops, seed=str(args.get("seed", name)))
    except (ValueError, KeyError) as e:
        return f"SURGICAL ABORT (nothing written): {e}"
    if not receipt["removed_keys"] and not receipt["added_keys"]:
        return ("SURGICAL ABORT: selector matched 0 notes — nothing written. "
                "Run select_notes to verify scope first.")
    if args.get("preview"):
        return "PREVIEW (not written): " + receipt["summary"] + "\n" + " · ".join(r.explain)
    errs = validate_song(work)
    if errs:
        return "SURGICAL ABORT — result would be invalid:\n- " + "\n- ".join(errs)
    _awrite(path, work)
    try:
        surgical.append_receipt(name, receipt)
    except Exception as e:
        log("receipt failed:", e)
    return ("CUT: " + receipt["summary"] + "\n" + " · ".join(r.explain)
            + "\nReceipt filed — the proposal diff must stay inside your receipts.")

TOOLS = {
    "start_session": (t_start_session, "Start a production session. Deterministically force-injects the skill set matching the genre context plus always-on skills, and returns available instruments + the song format.",
                      {"type": "object", "properties": {"genre": {"type": "string", "description": "genre/style words, e.g. 'trap', 'dnb', 'drill'"}}, "required": ["genre"]}),
    "list_instruments": (t_list_instruments, "List available Faust instrument names usable in song tracks.",
                         {"type": "object", "properties": {}}),
    "list_kits": (lambda a: json.dumps(list_kits(), indent=1), "List sample kits with their kinds and available MIDI keys.",
                  {"type": "object", "properties": {}}),
    "get_skill": (t_get_skill, "Fetch one skill's full content by name (integrity-checked).",
                  {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}),
    "write_instrument": (t_write_instrument, "Author a NEW Faust instrument. Validates by compiling; returns compiler errors for self-correction. Must expose freq/gain/gate zones and stereo output (see faust-writing skill). PLAYS IMMEDIATELY: voices not in the AOT registry are JIT-compiled at load (libfaust interpreter) — no rebuild_engine, no restart; edits to a JIT voice re-compile on next song load.",
                         {"type": "object", "properties": {"name": {"type": "string"}, "faust_code": {"type": "string"}}, "required": ["name", "faust_code"]}),
    "rebuild_engine": (t_rebuild_engine, "Rebuild the engine so newly written instruments become renderable. SLOW (~2-4 min); only call after write_instrument.",
                       {"type": "object", "properties": {}}),
    "get_song_summary": (t_get_song_summary, "The song WITHOUT note bodies: tracks (source/gain/pan/fx/sends/noteCount/barSpan/automation targets), sections, tempoMap, master — ~1KB for ANY size. READ THIS FIRST on songs beyond ~32 bars; only fetch note data for the bars you touch (get_song_region).",
                    {"type": "object", "properties": {"song": {"type": "string"}},
                     "required": ["song"]}),
    "get_song_region": (t_get_song_region, "Notes + automation windowed to [from_bar, to_bar] (1-indexed inclusive), optional tracks filter (list or comma string). Each note carries _idx = its index in the full track (feed indices straight to select_notes/surgical_edit). THE scoped read: a 12-min song's drop section is a few KB instead of megabytes.",
                    {"type": "object", "properties": {"song": {"type": "string"},
                     "from_bar": {"type": "number"}, "to_bar": {"type": "number"},
                     "tracks": {"type": "string", "description": "comma-separated track names (optional)"}},
                     "required": ["song"]}),
    "get_song": (t_get_song, "Read a song's full JSON (use before editing).",
                 {"type": "object", "properties": {"song": {"type": "string"}}, "required": ["song"]}),
    "update_track": (t_update_track, "Surgically replace ONE track's notes/gainDb/pan/sends/muted in a song without resending the whole song. muted:true IS the mute verb (persisted, render-honored; never fake mutes with -60dB gain - it does not unmute back). Other tracks are untouched. Validates before saving.",
                     {"type": "object", "properties": {"song": {"type": "string"}, "track": {"type": "string"},
                      "notes": {"type": ["array", "string"]}, "gainDb": {"type": "number"}, "pan": {"type": "number"}, "remove": {"type": "boolean", "description": "true DELETES the track (scoped; use instead of write_song)"}, "muted": {"type": "boolean", "description": "true mutes the track (persisted; honored in renders); false unmutes"},
                      "sends": {"type": ["array", "string"], "description": "[{bus, gainDb}] — route into set_buses buses"}},
                      "required": ["song", "track"]}),
    "locate": (t_locate, "THE SCALPEL'S EYES — resolve any human coordinate into song coordinates. Give a timestamp ('1:23'), beat, bar, or section name: returns the exact beat (tempoMap-aware), the section, clock time, bpm, and WHAT IS SOUNDING there per track (notes with pitch names, active clips, live automation values, roles, muted/locked). [full laws: tool-guide skill]",
               {"type": "object", "properties": {"song": {"type": "string"},
                "time": {"type": ["string", "number"], "description": "'1:23' / '83.5s' / seconds"},
                "beat": {"type": "number"}, "bar": {"type": "number"},
                "section": {"type": "string"}, "occurrence": {"type": "integer", "description": "which repeat of the section name (1-based)"},
                "query": {"type": "string", "description": "free words describing the sound/track"},
                "halo_beats": {"type": "number", "description": "how far around the point to report (default 1)"}},
                "required": ["song"]}),
    "select_notes": (t_select_notes, "DRY-RUN a surgical selector — see the EXACT notes it matches (track, beat, bar, pitch name, vel, len) before cutting. Zero edits. Selector fields (all optional, AND-ed): tracks ('name' | ['a','b'] | {match} | {role: kick|bass|snare|hat|perc|pad|lead|keys|chords|vocal|fx}); range as beats [a,b) |… [full laws: tool-guide skill]",
                     {"type": "object", "properties": {"song": {"type": "string"},
                      "selector": {"type": ["object", "string"]}}, "required": ["song", "selector"]}),
    "surgical_edit": (t_surgical_edit, "THE CUT — apply ops to EXACTLY the selector's notes and file a receipt; every other note/track/param is untouchable (the sidecar diffs the proposal against receipts and flags anything out of scope). Ops run in order on the matched set: {op:'set', vel|pitch|len|start} absolute · {op:'shift',… [full laws: tool-guide skill]",
                      {"type": "object", "properties": {"song": {"type": "string"},
                       "selector": {"type": ["object", "string"]},
                       "ops": {"type": ["array", "string"]},
                       "preview": {"type": "boolean"},
                       "seed": {"type": "string", "description": "determinism seed for humanize"}},
                       "required": ["song", "selector", "ops"]}),
    "list_plugin_params": (t_list_plugin_params, "Enumerate EVERY automatable parameter in the session — faust zones, VST3 params, volume/pan, sends — with value + range. THE map of every knob; automate/set any of them.",
                           {"type": "object", "properties": {"song": {"type": "string"}, "track": {"type": "string", "description": "optional filter"}},
                            "required": ["song"]}),
    "set_track_param": (t_set_track_param, "Set ONE parameter statically (no motion): target source.<param> | fx[i].<param> | gainDb | pan. Real units for faust (see list_plugin_params), 0..1 for vst3.",
                        {"type": "object", "properties": {"song": {"type": "string"}, "track": {"type": "string"},
                         "target": {"type": "string"}, "value": {"type": "number"}},
                         "required": ["song", "track", "target", "value"]}),
    "automate": (t_automate, "Write an automation curve — MOTION over time (filter opens into the drop, volume rides, width blooms). target: gainDb|pan|fx[i].<param>|source.<param> (with track) or masterGainDb|master[i].<param> (song scope). points [{beat,v,curve?}] real units; curve -1..1 shapes the segment leaving the point: >0 late-bloom (BUILDS), <0 early-jump (drops), 0 linear. Replaces same-target curve; [] clears.",
                 {"type": "object", "properties": {"song": {"type": "string"}, "track": {"type": "string"},
                  "target": {"type": "string"}, "points": {"type": ["array", "string"]}},
                  "required": ["song", "target", "points"]}),
    "set_buses": (t_set_buses, "Define shared FX buses (send reverb/delay — the pro mix paradigm): [{id, gainDb, fx:[{id, params}]}]. Then route tracks via update_track sends.",
                  {"type": "object", "properties": {"song": {"type": "string"}, "buses": {"type": ["array", "string"]}},
                   "required": ["song", "buses"]}),
    "update_song_meta": (t_update_song_meta, "Change song-level fields (bpm, swing, masterGainDb, master chain, lengthBars, key, tempoMap) without touching tracks. tempoMap = tempo switches/arcs ([{bar,bpm,curve?}], holds until the next point; ALL beats + warped audio follow — DJ tempo arcs, halftime drops, ritardandos).",
                         {"type": "object", "properties": {"song": {"type": "string"}, "bpm": {"type": "number"},
                          "swing": {"type": ["object", "string"]}, "masterGainDb": {"type": "number"},
                          "lengthBars": {"type": "number"}, "key": {"type": "string"},
                          "master": {"type": ["array", "string"]},
                          "tempoMap": {"type": ["array", "string"], "description": "[{bar>0, bpm 40-220, curve?}]"}},
                          "required": ["song"]}),
    "add_track": (t_add_track, "Add a new track to a song (name, source kind faust|sample|vst3, optional gainDb/fx/notes).",
                  {"type": "object", "properties": {"song": {"type": "string"}, "track_json": {"type": ["object", "string"]}},
                   "required": ["song", "track_json"]}),
    "keep_jam": (t_keep_jam, "CAPTURE LAW (THE BAND SEAT): merge a kept jam take (songs/jam_*.json or any song) INTO the current song as new 'jam:<role>' lanes — notes/automation beat-offset to at_bar (default: appended after the song's end as its own section), lengthBars extended, collisions suffixed, sends filtered to existing buses, receipts filed. Beats are tempo-agnostic: the song's bpm rules the feel; big deltas are called out in the reply.",
                 {"type": "object", "properties": {"song": {"type": "string"}, "take": {"type": "string"},
                  "at_bar": {"type": "number"}, "prefix": {"type": "string"}},
                  "required": ["song", "take"]}),
    "set_track_fx": (t_set_track_fx, "Set a track's FX chain in signal order: faust fx (fx_reverb, fx_delay, fx_saturate, fx_softclip [drive: gentle pre-wall drum-bus glue], fx_crush [bits/srate/mix: bitcrush + sample-rate reduce — lo-fi/sigilkore grit], fx_widen, fx_ms_eq [mid/side EQ: mid_low/mid_high/side_low/side_high/width], fx_multiband [3-band comp: low/mid/high thresh+ratio, makeup], fx_comp [THE channel/bus compressor: thresh/ratio (honest N:1)/attack/release ms/makeup dB — stereo-linked; glue: thresh -24 ratio 3; snare crack: thresh -20 ratio 4 attack 5. Use INSTEAD of {\"type\":\"comp\"}, whose friendly-param wiring is dead], fx_transient [attack/sustain shaper ±12 dB: drum punch attack +6..9, tame ring/room sustain -4..-8; 0/0 = unity], fx_filter [cutoff/res], fx_flanger [stereo swept-comb motion: rate/depth/feedback/mix — psy leads, jet risers, pad shimmer], fx_pump, fx_deess [split-band sibilance tamer, FIRST in the vocal chain pre-reverb: freq/thresh/amount], fx_gate [downward expander for recorded stems: thresh/depth/rel — bleed + noise floor between phrases; thresh must clear the floor's CRESTS (peak follower), depth 0 = bypass], fx_trim, fx_djfilter, fx_brickwall, fx_truepeak [ISP release wall: ceiling = output dBTP]), built-ins ({\"type\":\"eq\"|\"comp\"}), or vst3 inserts ({\"id\":\"vst3:<name>\", \"preset\": <blob path>}), or NAM amp/pedal captures ({\"id\":\"nam:<path/to/capture.nam>\", \"params\":{\"input_db\":0,\"output_db\":0}} — library.json nam_captures; mono-sum DI), or CLAP plugins ({\"id\":\"clap:<path/to/plugin.clap>\", \"params\":{\"index\":0,\"mix\":1.0}} — library.json clap_plugins; direct C-ABI host, any .clap effect). Any entry takes \"bypass\": true (created but disabled — A/B without losing settings). Space/depth lives here.",
                     {"type": "object", "properties": {"song": {"type": "string"}, "track": {"type": "string"},
                      "fx": {"type": ["array", "string"]}}, "required": ["song", "track", "fx"]}),
    "write_lyrics": (t_write_lyrics, "Write timestamp-aware lyrics into a song: [{beat, text}] — each line lands on an exact beat. Compose them AWARE of the arrangement (hooks at drops, flow matching drum density).",
                     {"type": "object", "properties": {"song": {"type": "string"}, "lyrics": {"type": ["array", "string"]}},
                      "required": ["song", "lyrics"]}),
    "add_topline": (t_add_topline, "Add a vocal-hook TOPLINE melody track (section-aware: choruses repeat the hook [HOOK], chorus lifts a 5th-8ve above the verse and peaks late [LIFT], verses conversational/stepwise [TALK], intro/break/outro rest [SPACE]; notes land on chord tones). The singable lead for a vocal line — swap its source to a voice and add words with write_lyrics, then sing. Needs the song to have sections + a chord field (generate_loop/harmonize provide them).",
                    {"type": "object", "properties": {"song": {"type": "string"}, "track": {"type": "string"}, "seed": {"type": "integer"}},
                     "required": ["song"]}),
    "align_lyrics": (t_align_lyrics, "Auto-melisma: set each lyric line's melisma so its words COVER a melody track's notes (default 'topline') — extra notes ride the last word as a sung melisma (no silent notes). Run after write_lyrics + add_topline. Args: song, track?.",
                     {"type": "object", "properties": {"song": {"type": "string"}, "track": {"type": "string"}},
                      "required": ["song"]}),
    "search_library": (t_search_library, "Search the user's indexed musical world by WORDS and by VIBE: samples, kits, instruments, fx, VST3s. Returns substring hits plus a `semantic` list of CLAP timbre-neighbors (when a library/embeddings.npz index exists) — 'a dusty lo-fi snare' finds sounds the words can't name.",
                       {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}),
    "sound_neighbors": (t_sound_neighbors, "Find the library sounds nearest to an audio file (a render, clip, or stem) by CLAP timbre — the reference-match axis ('this render sits nearest: warmpad 36, strings 48'). Needs a CLAP index (tools/embed_library.py). Args: wav (absolute / repo-relative / a songs/ basename), k? (default 8).",
                        {"type": "object", "properties": {"wav": {"type": "string"}, "k": {"type": "integer"}}, "required": ["wav"]}),
    "chords_from_audio": (t_chords_from_audio, "Detect a chord lane FROM AUDIO (best on a harmonic/no-drums stem): CQT chroma read through the same maj/min/dom7 grammar as the symbolic chord vote. Standalone (wav + bpm + bars -> chord list) or FUSED (song + wav -> writes song.chords[], fusing the audio witness with the song's own symbols). Args: wav, bpm?, bars?, song?.",
                          {"type": "object", "properties": {"wav": {"type": "string"}, "bpm": {"type": "number"}, "bars": {"type": "integer"}, "song": {"type": "string"}}, "required": ["wav"]}),
    "export_midi": (t_export_midi, "Export a song to a Standard MIDI File (songs/<name>.mid) for use in any other DAW.",
                    {"type": "object", "properties": {"song": {"type": "string"}}, "required": ["song"]}),
    "import_als": (t_import_als, "Import an Ableton Live project (.als) as a song — the user's existing work becomes symbolic and editable here.",
                   {"type": "object", "properties": {"als_path": {"type": "string"}, "song": {"type": "string"}},
                    "required": ["als_path", "song"]}),
    "import_dawproject": (t_import_dawproject, "Import a .dawproject file (Bitwig/Cubase/Nuendo/Studio One open format): notes, audio clips, tempo, mixer levels.",
                          {"type": "object", "properties": {"dawproject_path": {"type": "string"}, "song": {"type": "string"}},
                           "required": ["dawproject_path", "song"]}),
    "get_selection": (t_get_selection, "SELECTION = CONTEXT: exactly what the user has selected in the UI right now (notes with indices, tracks with fx/param state, time range with per-track content, library item). Call this to re-anchor when an ask says 'this/these/here' — the selection IS the subject.",
                      {"type": "object", "properties": {}}),
    "import_rekordbox": (t_import_rekordbox, "THE PRO-DJ BRIDGE: import a rekordbox collection.xml (optionally one playlist, in its order) -> library.json dj_tracks with AUTHORITATIVE bpm/key(Camelot)/first-beat offsets from rekordbox's analysis, plus a ready-to-run dj_set command. The way a working DJ's real library enters the DAW.",
               {"type": "object", "properties": {"xml": {"type": "string", "description": "path to collection.xml (rekordbox: File > Export Collection in xml format)"},
                "playlist": {"type": "string", "description": "playlist name (omit = whole collection)"},
                "set_name": {"type": "string"}}, "required": ["xml"]}),
    "import_flp": (t_import_flp, "Import an FL Studio project (.flp): channels, patterns, playlist placements.",
                   {"type": "object", "properties": {"flp_path": {"type": "string"}, "song": {"type": "string"}},
                    "required": ["flp_path", "song"]}),
    "audio_to_midi": (t_audio_to_midi, "SPECTRAL CAPTURE: turn ANY audio (mp3/wav, or a region t0/t1 in seconds) into EDITABLE MIDI that renders back to the same audio. Lanes: spectral_low/mid/high partial notes (per-note bend+gain envelopes live in songs/<name>_spectral/capture.json), spectral_clicks transient snippets (move a drum hit like a note), spectral_noise band lanes, spectral_mix = the audible deterministic render. mode=lossless (default) adds spectral_residual: render+residual == the ORIGINAL FILE byte-for-byte. Real-music fidelity ~92-95% spectral (pure MIDI), synthetics 98-100. Edit lanes then call midi_to_audio to hear the edit. COST LAW: a FULL song/stem at quality max = 20-40 MINUTES of wall time (measured live) — for whole-song asks use the default standard quality, or capture just the region you need via t0/t1 (a 30s region at max = ~3-4 min). The tool is content-addressed: an identical re-ask answers instantly (never re-call it on the same file+params 'to be sure' — the lanes already carry it).",
                      {"type": "object", "properties": {"audio_path": {"type": "string"}, "song": {"type": "string"}, "mode": {"type": "string", "enum": ["lossless", "spectral"]}, "quality": {"type": "string", "enum": ["fast", "standard", "max"], "description": "fast=interactive ~3x realtime; standard = the whole-song default; max=full fidelity, 20-40 min on a full song — prefer t0/t1 regions"}, "bpm": {"type": "number"}, "t0": {"type": "number", "description": "region start (s)"}, "t1": {"type": "number", "description": "region end (s)"}},
                       "required": ["audio_path"]}),
    "midi_to_audio": (t_midi_to_audio, "Re-render a spectral capture from the song's CURRENT spectral_* lanes (edits included) and swap the spectral_mix clip. Deterministic: unedited = identical; edited notes carry their envelopes (move/transpose/stretch/velocity). Returns fidelity vs the capture source.",
                      {"type": "object", "properties": {"song": {"type": "string"}},
                       "required": ["song"]}),
    "roundtrip_verify": (t_roundtrip_verify, "Score two audio files against each other: spectral fidelity %, waveform corr, SI-SDR, envelope corr, byte-exact. The reconstruction contract, measured.",
                         {"type": "object", "properties": {"a": {"type": "string"}, "b": {"type": "string"}},
                          "required": ["a", "b"]}),
    "import_song_audio": (t_import_song_audio, "ABSORB any finished song (mp3/wav/flac): local GPU stem separation + transcription + bpm/key detection -> EDITABLE MIDI session (the MIDI sounds by default): named drum lanes (Kick/Snare/Hats/Perc/Cymbals) + bass/other sketches on the record's own pitched kits + TRUE-MIDI vocal melody auto-sung by the local DiffSinger voice (vocals_sung; edit melody + hum_topline/sing_lyrics re-sings). The 4 raw stems land MUTED + UNWARPED as byte-true A/B reference (the song grid IS the record's grid; launcher slots stay tempo-following). Ends with THE FINAL CORRECTION (a2m_correct): per-lane gains matched to the stems, drum hits re-anchored/velocity-refit/salvaged from the record. Never chops the user's own record into slices (identity/chop lanes are SOTADAW_ID_LANES=1 opt-in only). instruments: original (default) | ear — original keeps the record's own kits/timbres; ear AUDITIONS the faust palette against each stem (closed-loop probe renders, receipted in <name>_stems/ear.json) and the sketches play the measured twin instead.",
                          {"type": "object", "properties": {"audio_path": {"type": "string"}, "song": {"type": "string"},
                           "quality": {"type": "string", "enum": ["fast", "max"]}},
                           "required": ["audio_path", "song"]}),
    "a2m_correct": (t_a2m_correct, "THE FINAL CORRECTION (closed loop, zero tokens): render the imported product's stems and calibrate every MIDI lane against the record's OWN stems — group LUFS -> lane gains (kills the 'heavily limited' wall grind at the source), drum hits re-anchored to the record's onsets (<=35ms), per-hit velocities refit through the sampler dB law, MISSING hits salvaged from the stem (recall -> ~1.0). Iterates render->measure->correct; final verify scores the product vs the stem-sum record (spectral% + LUFS delta). Run after import_song_audio edits or whenever an imported song drifts from its record.",
                    {"type": "object", "properties": {"song": {"type": "string"},
                     "iters": {"type": "number", "description": "correction passes, default 2"},
                     "no_verify": {"type": "boolean", "description": "skip the final full render+score"}},
                     "required": ["song"]}),
    "vocal_truth": (t_vocal_truth, "THE VOCAL TRUTH LANE: re-synthesize the record's own vocal from parametric spectral capture (sinusoidal partials + noise bands = MIDI-shaped data — DETECTED, never a chop of the record) and land it as the sounding 'vocals_true' lane at the stem's own LUFS; the DiffSinger take mutes (truth outranks synth). Phrase-windowed + RAM-gated (survives tight boxes; lands partial rather than dying). Proof class: 96%+ spectral / SI-SDR 37dB vs the vocal stem. Needs the song's muted 'vocals' stem reference (any import_song_audio session has it).",
                    {"type": "object", "properties": {"song": {"type": "string"},
                     "win": {"type": "number", "description": "phrase-window seconds, default 30"},
                     "wait_s": {"type": "number", "description": "max seconds to wait for free RAM per window, default 300"}},
                     "required": ["song"]}),
    "dj_blend": (t_dj_blend, "THE AI DJ: beat-match two audio files (auto bpm detect) onto one tempo grid via warp, phrase-aligned crossfade + fx_djfilter bass swap -> editable song.json where every transition move is visible automation. Chain N tracks = a DJ set.",
                 {"type": "object", "properties": {"deck_a": {"type": "string"}, "deck_b": {"type": "string"},
                  "song": {"type": "string"}, "bpm": {"type": "number", "description": "target grid (default deck A)"},
                  "bpm_a": {"type": "number"}, "bpm_b": {"type": "number"},
                  "blend_bars": {"type": "number", "description": "crossfade length, default 8"}},
                  "required": ["deck_a", "deck_b", "song"]}),
    "chop_sample": (t_chop_sample, "THE CHOP (MPC workflow): slice any audio (stem, import, render) into a playable kit — onset-detected or --grid equal slices, chromatic pads from key 36, edge-faded. Then sequence pads with {\"kind\":\"sample\",\"kit\":...}. Full flip: import_song_audio -> chop_sample the stem -> play pads. THE GROOVE-BACK (one fabric): groove=true returns the source's OWN pattern as notes (slice timing + peak velocity — verified: reconstruction correlates 0.976 with the source); preview=true writes songs/_chop_<kit>.json renderable; song=<name> [track=<t>] injects the groove track straight into an arrangement — then EDIT the notes and the loop is yours (rearrange/half-time/swap pads). bpm=N overrides the neural estimate.",
                    {"type": "object", "properties": {"audio_path": {"type": "string"}, "kit": {"type": "string"},
                     "slices": {"type": "number"}, "from_sec": {"type": "number"}, "to_sec": {"type": "number"},
                     "grid": {"type": "number", "description": "equal slices instead of onsets (breakbeats)"},
                     "melodic": {"type": "number", "description": "slice # (0=longest) -> ONE slice mapped across the whole keyboard, root auto-detected — sample a note, play it melodically"},
                     "groove": {"type": "boolean", "description": "return the source's OWN pattern as notes (slice timing + velocity)"},
                     "preview": {"type": "boolean", "description": "write songs/_chop_<kit>.json reconstruction"},
                     "song": {"type": "string", "description": "inject the groove track into songs/<song>.json"},
                     "track": {"type": "string", "description": "track name for song injection (default kit name)"},
                     "bpm": {"type": "number", "description": "groove tempo (default: neural estimate)"}},
                     "required": ["audio_path", "kit"]}),
    "chord_map": (t_chord_map, "CHORDS FROM THE SYMBOLS: bar-wise chord map voted from the song's own notes (duration x velocity, bass witnesses x2.5, dominant-7 detection; muted *_sketch tracks vote on imports; drums excluded). Battery: 9/12 exact incl. the 7s on 12-bar blues (audio-HMM baseline was 2/12), 4/4 on clean triads. [full laws: tool-guide skill]",
                    {"type": "object", "properties": {"song": {"type": "string"},
                     "write": {"type": "boolean"}, "tracks": {"type": "string"}},
                     "required": ["song"]}),
    "reharmonize": (t_reharmonize, "REHARMONIZE: vote the song's chord cycle (chordvote), then rotate=N (wave-29 schema-rotation law: one cycle = N progressions, pick the start that fits the section's mood) or to='Eb,Fm,Ab,Db' (explicit per-cycle target). Retunes melodic tracks ROLE-to-role (root->root, third->third quality-aware)\u2026 [full laws: tool-guide skill]",
                    {"type": "object", "properties": {"song": {"type": "string"},
                     "rotate": {"type": "number"}, "to": {"type": "string"},
                     "out": {"type": "string"}},
                     "required": ["song"]}),
    "remix_import": (t_remix_import, "THE FULL FLIP: generate an ORIGINAL track in any genre that FITS an absorbed song — reads the import's bpm/key/voted chord cycle/learned groove, generates a fresh genre loop AT that bpm+key, reharmonizes it TO the import's chords (role-mapped minimal motion), applies the import's timing DNA to… [full laws: tool-guide skill]",
                    {"type": "object", "properties": {"song": {"type": "string"},
                     "genre": {"type": "string"}, "out": {"type": "string"},
                     "seed": {"type": "number"}, "bars": {"type": "number"},
                     "full": {"type": "boolean", "description": "arrange the flip through the IMPORT'S OWN section shape (same bar count; ears-verified structure mirror)"}},
                     "required": ["song", "genre"]}),
    "harmonize": (t_harmonize, "COMPOSE FROM THE CHORD LANE: generate a NEW bass/pad/arp track that plays the song's OWN voted chord changes, in key, as an editable track (verified: the new part re-votes the exact progression 4/4). role=bass|pad|arp; rhythm=straight|offbeat|roll (bass) / whole|pulse (pad) / up|updown (arp);… [full laws: tool-guide skill]",
                    {"type": "object", "properties": {"song": {"type": "string"},
                     "role": {"type": "string", "enum": ["bass", "pad", "arp", "melody"]},
                     "seed": {"type": "number", "description": "melody variation seed (new seed = new singable line)"},
                     "sectioned": {"type": "boolean", "description": "density FOLLOWS the arrangement — sparse in intro/verse/break, busy in drop/chorus (the 'one change per section' law; needs sections[])"},
                     "track": {"type": "string"}, "octave": {"type": "number"},
                     "rhythm": {"type": "string"}},
                     "required": ["song", "role"]}),
    "transitions": (t_transitions, "THE GLUE: auto-place risers (+optional impacts) at every section boundary INTO a high-energy section (drop/chorus/main/finale) — a bandpass-swept build in the preroll bars landing bar-exact on the downbeat (verified late-bloom: -33->-17->-13dB into the drop). [full laws: tool-guide skill]",
                    {"type": "object", "properties": {"song": {"type": "string"},
                     "track": {"type": "string"}, "preroll": {"type": "number"},
                     "impacts": {"type": "boolean"},
                     "downlifters": {"type": "boolean", "description": "filter-close the outgoing track's fx_filter into every drop->break/outro seam (verified centroid fall 2152->539Hz) — the riser's drain complement"},
                     "fills": {"type": "boolean", "description": "accelerating snare roll (8ths->16ths->32nds, velocity crescendo) in the bar before each drop — the fill that ANNOUNCES the drop"}},
                     "required": ["song"]}),
    "automix": (t_automix, "AUTOMIX: the KG mix laws become action, by track role — subs/kick pan CENTER + widener stripped (mono_below_120), pads get fx_widen + filter for a wide bed, bass gets a bpm-locked fx_pump sidechain under the kick, focal parts (lead/vocal) stay centered. [full laws: tool-guide skill]",
                    {"type": "object", "properties": {"song": {"type": "string"}},
                     "required": ["song"]}),
    "finish": (t_finish, "FINISH THE TRACK — the full auto-production chain in one call: vote chords -> arrange a bare loop into a pop form -> harmonize any MISSING bass/pad section-aware -> place risers/impacts/downlifters at the seams -> automix (center subs, widen pads, sidechain, symbolic unmask). [full laws: tool-guide skill]",
                    {"type": "object", "properties": {"song": {"type": "string"},
                     "out": {"type": "string"}},
                     "required": ["song"]}),
    "humanize": (t_humanize, "MEASURABLE HUMANIZATION (GrooVAE/GigaMIDI-grounded): adds correlated microtiming drift + metric-accent velocity to a track (the two axes GrooVAE names), with a VERIFIABLE expressiveness score (mechanical=0, human rises — battery: dead grid 0.0 -> 28.1, real groove 60.9; microtiming survives the render at 9.1ms). [full laws: tool-guide skill]",
                    {"type": "object", "properties": {"song": {"type": "string"},
                     "track": {"type": "string"}, "amount": {"type": "number"},
                     "seed": {"type": "number"}, "measure": {"type": "boolean"}},
                     "required": ["song"]}),
    "intensify": (t_intensify, "INTENSIFY (energy edit): shape a named SECTION's energy up or down in one call — amount>0 hardens (louder hits + more 16th hats/perc), amount<0 softens (quieter + thinned offbeats). 'make the drop harder' / 'soften the intro'. ONLY the named section changes; locked tracks untouched. Verified: harder raises velocity + hat density, softer lowers them, scoped.",
                    {"type": "object", "properties": {"song": {"type": "string"}, "section": {"type": "string"},
                     "amount": {"type": "number", "description": "-1..+1; >0 harder, <0 softer"}},
                     "required": ["song", "section", "amount"]}),
    "variations": (t_variations, "VARIATIONS (propose-and-pick): generate N DISTINCT options for a track's region, each pairwise-different, all playing the window chords, all scoped (nothing outside changes) — written as _<song>_var1..N proposal copies to audition/Accept. [full laws: tool-guide skill]",
                    {"type": "object", "properties": {"song": {"type": "string"}, "track": {"type": "string"},
                     "from_bar": {"type": "number"}, "to_bar": {"type": "number"},
                     "n": {"type": "number"}, "style": {"type": "string"}},
                     "required": ["song", "track", "from_bar", "to_bar"]}),
    "infill_region": (t_infill_region, "INFILL (MIDI-GPT lane, symbolic): regenerate ONE track's chosen BARS conditioned on surrounding context — the window's chords (harmony continuity), the track's own density/register elsewhere (feel continuity), and its role. ONLY the window changes; everything else byte-identical (verified:… [full laws: tool-guide skill]",
                    {"type": "object", "properties": {"song": {"type": "string"},
                     "track": {"type": "string"}, "from_bar": {"type": "number"},
                     "to_bar": {"type": "number"}, "seed": {"type": "number"},
                     "density": {"type": "number", "description": "target notes/bar override (MIDI-GPT's effective control; else follows context)"},
                     "duration": {"type": "number", "description": "note-length scale (MIDI-GPT's other effective control; 0.5=staccato, 2=legato)"},
                     "style": {"type": "string", "description": "style fingerprint name (style_profile extract) to generate in the producer's signature register+density"}},
                     "required": ["song", "track", "from_bar", "to_bar"]}),
    "style_profile": (t_style_profile, "STYLE FINGERPRINT (MIDI-RWKV personalization lane, symbolic): action=extract learns a producer's signature from their songs (tempo, chord-quality mix, density+register per role, groove/NOMML, dynamics, sections) into a reusable fingerprint; action=score rates any track 0-100 for how ON-BRAND it is,\u2026 [full laws: tool-guide skill]",
                    {"type": "object", "properties": {"action": {"type": "string", "enum": ["extract", "score"]},
                     "songs": {"type": "array", "items": {"type": "string"}, "description": "songs to learn from (extract)"},
                     "song": {"type": "string", "description": "track to score"},
                     "profile": {"type": "string", "description": "fingerprint name (default my_style)"}},
                     "required": ["action"]}),
    "prescribe": (t_prescribe, "PRESCRIBE (doctor + auto-fix): diagnose then AUTO-APPLY the safe fixes in one call — center/de-widen subs, humanize dead-mechanical parts, unmask mud, add a master limiter — then RE-DIAGNOSE to prove the issue count dropped (self-verifying: battery 6 issues -> 1, idempotent). [full laws: tool-guide skill]",
                    {"type": "object", "properties": {"song": {"type": "string"}, "out": {"type": "string"}},
                     "required": ["song"]}),
    "doctor": (t_doctor, "SONG DOCTOR: symbolic critique WITHOUT rendering — reads a song and reports fixable issues, each naming the exact fix tool: no harmony, no arrangement (->arrange/finish), doesn't breathe (->harmonize sectioned), off-center/widened sub (->automix mono law), mud collision (->automix unmask),… [full laws: tool-guide skill]",
                    {"type": "object", "properties": {"song": {"type": "string"}},
                     "required": ["song"]}),
    "restyle": (t_restyle, "RESTYLE (one-gesture style morph): keep EVERY note byte-identical, swap the SOUND + FEEL to any of the 130 KG genres — kick slides to 808 when the genre slides, bass follows the genre's bass_style voice, leads take the genre grid's lead voice, pads/chords take the recipe color voice, swing follows… [full laws: tool-guide skill]",
                {"type": "object", "properties": {"song": {"type": "string"},
                                                  "genre": {"type": "string"},
                                                  "bpm": {"type": "boolean", "description": "also move tempo into the genre's range"}},
                 "required": ["song", "genre"]}),
    "color": (t_color, "COLOR (semantic sound axes, deterministic): warmer (filter tilt + touch of drive on melodic voices) / darker (harder tilt) / brighter (air EQ +hiGain@6k, re-opens filters) / wider (fx_widen on pads/keys/lead ONLY — kick/bass/808 NEVER widen, the mono law holds). [full laws: tool-guide skill]",
              {"type": "object", "properties": {"song": {"type": "string"},
                                                "word": {"type": "string", "description": "warmer|darker|brighter|wider"},
                                                "amount": {"type": "number"},
                                                "track": {"type": "string"}},
               "required": ["song", "word"]}),
    "energy_curve": (t_energy_curve, "ENERGY CURVE (symbolic, no render): the song's per-bar energy (velocity x density; drums=onsets, melodic=sustain overlap) as a normalized curve + ASCII sparkline + per-section means, PLUS the contrast-law check — if a build sits within 15% of its drop's energy it flags the violation and prescribes… [full laws: tool-guide skill]",
                    {"type": "object", "properties": {"song": {"type": "string"},
                                                      "track": {"type": "string"}},
                     "required": ["song"]}),
    "song_structure": (t_song_structure, "EARS v4b: section boundaries of any wav (audio_path, optional bpm -> bar numbers). Foote-novelty on mel self-similarity, PRECISION-tuned (battery: every emitted boundary within ~2s of a real transition on two ground-truth songs; subtle 8-bar layer-adds may merge). [full laws: tool-guide skill]",
                    {"type": "object", "properties": {"audio_path": {"type": "string"},
                     "bpm": {"type": "number", "description": "snap boundaries to bars at this tempo"},
                     "vocal": {"type": "string", "description": "vocal stem wav path — unlocks verse/hook labels"}},
                     "required": ["audio_path"]}),
    "suggest_chords": (t_suggest_chords, "HARMONY ADVISOR (Scaler-class, symbolic): ranked per-slot substitutions + whole-progression rewrites for the song's own chord lane, each with the theory WHY — function flow T→S→D, secondary dominants (V7 of next), tritone subs, mode mixture, backdoor cadences — scored by voice-leading cost through the same kernel real parts use, optional KG genre prior. Rewrites ship a ready reharm --to line. Read-only. Args: song, genre?, k? (alts per slot, default 4).",
                    {"type": "object", "properties": {"song": {"type": "string"},
                     "genre": {"type": "string", "description": "genre prior from the KG's chord DNA"},
                     "k": {"type": "number", "description": "alternatives per slot (default 4)"}},
                     "required": ["song"]}),
    "describe_sound": (t_describe_sound, "SEMANTIC EARS SPEAK: zero-shot CLAP words for any wav — ranked role (kick/808/pad/female vocals/...), timbre (dark/punchy/lo-fi), energy and space tags + one honest sentence ('punchy, aggressive kick drum, dry'). Use on samples, stems, renders before library moves or when naming what you hear. Args: audio_path, k? (tags per bank, default 5).",
                    {"type": "object", "properties": {"audio_path": {"type": "string"},
                     "k": {"type": "number", "description": "tags per bank (default 5)"}},
                     "required": ["audio_path"]}),
    "structure_transfer": (t_structure_transfer, "STRUCTURE TRANSFER: hear a reference record's section shape (Foote novelty + labels) and map it onto the target song's bar grid — sections[] ready for song.json plus per-section energy targets and density hints (intro thin, build rising+riser, break drops drums). 'Make my song shaped like X' as a measured plan; apply via update_song_meta/duplicate_bars/clear_bars on proposal rails. Args: audio_path, song? (its lengthBars = the grid), bars?, vocal?.",
                    {"type": "object", "properties": {"audio_path": {"type": "string"},
                     "song": {"type": "string", "description": "target song — its lengthBars becomes the grid"},
                     "bars": {"type": "number", "description": "explicit target grid (overrides song)"},
                     "vocal": {"type": "string", "description": "reference vocal stem — unlocks verse/hook labels"}},
                     "required": ["audio_path"]}),
    "smart_tempo": (t_smart_tempo, "SMART TEMPO (rubato conform): neural beats/downbeats (beat_this GPU-elastic, librosa fallback) turn a freely-played recording into offsetSec + tempoMap[]{bar,bpm,curve} — near-equal bars merged, ramps vs steps decided, steady takes report ONE entry. The grid follows the human: apply via update_song_meta (bpm/tempoMap) and put offsetSec on the recording's audioClip so bar 1 IS downbeat 1. Read-only. Args: audio_path, meter? (default 4), engine? (auto|beatthis|librosa).",
             {"type": "object", "properties": {
                 "audio_path": {"type": "string"}, "meter": {"type": "integer"},
                 "engine": {"type": "string"}}, "required": ["audio_path"]}),
    "transcribe_lyrics": (t_transcribe_lyrics, "THE WORDS (ASR): transcribe a recorded vocal into beat-timed words + lines through the song's OWN clock (bpm+tempoMap, the surgical TempoClock) — faster-whisper word timestamps, GPU->CPU elastic, per-word confidence. find? answers 'where is the second yeah' in beats. Lines are write_lyrics-shaped: apply via write_lyrics. Sung/rapped ASR is imperfect — beats are the product, words are evidence. Read-only. Args: audio_path, song? (grid), find?, language?, model? (default small).",
             {"type": "object", "properties": {
                 "audio_path": {"type": "string"}, "song": {"type": "string"},
                 "find": {"type": "string"}, "language": {"type": "string"},
                 "model": {"type": "string"}}, "required": ["audio_path"]}),
    "vocal_rider": (t_vocal_rider, "VOCAL RIDER (gain-ride AI): per-half-beat vocal-vs-backing margin from the song's OWN stems (m1 render-stems, or stems_dir for imports) -> slew-limited bounded ABSOLUTE gainDb automation points for the vocal track: buried lines ride up, hot lines duck, the fader comes home in silence. stem_callouts DETECTS the level fight; this GENERATES the fix. Apply via automate (which files receipts). Read-only. Args: song, track? (auto-detects vocal-ish names), target? (margin dB, default 0), range? (max dB, default 4), stems_dir?.",
             {"type": "object", "properties": {
                 "song": {"type": "string"}, "track": {"type": "string"},
                 "target": {"type": "number"}, "range": {"type": "number"},
                 "stems_dir": {"type": "string"}}, "required": ["song"]}),
    "restore_audio": (t_restore_audio, "AUDIO REPAIR (RX-style, offline): QC report (peak/RMS, DC offset, noise floor, 50/60Hz mains hum + harmonics, hard-clip regions) + bounded fixes at the SOURCE before a recording becomes a track — zero-phase 20Hz highpass (dc), narrow notch comb (hum), STFT spectral-gate denoise (profile learned from the quietest frames; phrases untouched). Auto policy fixes ONLY what QC flags; a clean file passes through as a byte-copy. Writes <in>_restored.wav (never in-place; repair never creates clipping). Declipping deliberately NOT attempted — regions are reported. Use on imported takes/phone recordings BEFORE fx; report_only first to just look. Args: audio_path, out_path?, report_only?, denoise_db? (auto|0|N), hum? (auto|50|60|off), dc? (auto|on|off).",
             {"type": "object", "properties": {
                 "audio_path": {"type": "string"}, "out_path": {"type": "string"},
                 "report_only": {"type": "boolean"}, "denoise_db": {"type": ["string", "number"]},
                 "hum": {"type": "string", "enum": ["auto", "50", "60", "off"]},
                 "dc": {"type": "string", "enum": ["auto", "on", "off"]}}, "required": ["audio_path"]}),
    "find_genre": (t_find_genre, "SEMANTIC GENRE ROUTING: vibe/mood words -> the nearest REAL genres from the knowledge graph (MiniLM caption KNN over all 200+ Genre nodes; scores are cosine similarity, 'weak': true below 0.35 = advisory only). Use when the ask describes a FEEL with no explicit genre ('smoky late night jazz bar', 'aggressive rap with booming 808s') — returned names are valid for generate_loop/make_track/start_session genre context. Read-only. Args: text (the vibe words), k? (default 5).",
             {"type": "object", "properties": {
                 "text": {"type": "string", "description": "vibe/mood/feel words to route"},
                 "k": {"type": "integer", "description": "how many genres (default 5)"}},
              "required": ["text"]}),
    "sidechain_bake": (t_sidechain_bake, "KEYED SIDECHAIN (baked): reads the trigger track's ACTUAL note onsets — swing, breakbeats, half-time all land correctly where fx_pump's LFO (four-on-the-floor assumption) would duck on air — and returns a duck envelope (dip -depth dB over attack beats, hold, release; overlapping triggers merge deepest-first) as thinned ABSOLUTE gainDb automation points per target track. Returns the PLAN; apply via automate (which files receipts). Read-only. Args: song, trigger? (kick-ish names auto-match), targets? (list or comma string; bass/pad-ish auto), depth? (dB, default 4), attack?/hold?/release? (beats, defaults 0.05/0.05/0.4).",
             {"type": "object", "properties": {
                 "song": {"type": "string"}, "trigger": {"type": "string"},
                 "targets": {"type": ["array", "string"], "items": {"type": "string"}},
                 "depth": {"type": "number"}, "attack": {"type": "number"},
                 "hold": {"type": "number"}, "release": {"type": "number"}}, "required": ["song"]}),
    "dj_set": (t_dj_set, "AI DJ SET BUILDER: N audio tracks -> ONE continuous set. THE PLAYLIST BRAIN picks deck order by default (tempo arc + harmonic path + cut placement; pass auto_order false to keep the given order) and each hop picks its transition style: beat-matched staggered blend within warp distance, ECHO-OUT CUT… [full laws: tool-guide skill]",
               {"type": "object", "properties": {"tracks": {"type": "array", "items": {"type": "string"}}, "bridge": {"type": "array", "items": {"type": "number"}, "description": "hop indices (1=first transition) that get the acapella bridge"},
                "song": {"type": "string"}, "bpms": {"type": "array", "items": {"type": "number"}},
                "blend_bars": {"type": "number"},
                "auto_order": {"type": "boolean", "description": "planner chooses deck order (default true)"},
                "bridge_auto": {"type": "boolean", "description": "probe every hop's outgoing tail and bridge wherever a voice actually sings (no hop index needed; demucs per hop)"},
                "arc": {"type": "string", "enum": ["peak", "warmup", "closer"], "description": "crowd-energy preset for the planner: peak=climb all night (default), warmup=gentle climb, closer=rise then LAND"},
                "audit": {"type": "boolean", "description": "the set hears itself: render + dj_listener verdicts (plateau/cliff/fatigue/dead-air) after building"}},
                "required": ["tracks", "song"]}),
    "save_preset": (t_save_preset, "Capture a vst3 track's current plugin state as a named preset (OUR patch format) — design once with set_track_param, reuse forever.",
                    {"type": "object", "properties": {"song": {"type": "string"}, "track": {"type": "string"},
                     "preset_name": {"type": "string"}}, "required": ["song", "track", "preset_name"]}),
    "use_preset": (t_use_preset, "Load a captured preset onto a vst3 track (source.preset). Params can still tweak on top.",
                   {"type": "object", "properties": {"song": {"type": "string"}, "track": {"type": "string"},
                    "preset": {"type": "string"}}, "required": ["song", "track", "preset"]}),
    "phrase_map": (lambda a: run([VENV_PY if os.path.exists(VENV_PY) else "python3",
                    os.path.join(ROOT, "tools", "phrase_map.py"),
                    resolve_song_name(a["song"]), a.get("track", "lead"),
                    "--json"], timeout=60)[1] or "no melody",
                    "THE PHRASE MAP (read-only): per-section word counts + phrase shapes of a melody track — run this BEFORE writing lyrics (one word per note; shared shapes = the hook sings the same words each statement). The mechanical half of lyric writing.",
                    {"type": "object", "properties": {"song": {"type": "string"}, "track": {"type": "string"}}, "required": ["song"]}),
    "hum_topline": (lambda a: _sing_receipted(a, "hum",
                    [a.get("track", "lead"), a.get("syllable", "laa")], 300),
                    "INSTANT WORDLESS VOCAL: sing a neutral syllable (laa/ooh/ah/mmm/naa/doo/ey) on every note of a melody track (default 'lead' — generate_loop/make_track write one) — a topline hook for any instrumental, deterministic, no lyrics needed. The user swaps in real words later via write_lyrics + sing_lyrics.",
                    {"type": "object", "properties": {"song": {"type": "string"}, "track": {"type": "string"}, "syllable": {"type": "string"}}, "required": ["song"]}),
    "sing_lyrics": (lambda a: _sing_receipted(a, "render",
                    [a["track"], str(a.get("voice", "standard"))], 600),
                    "SING the song's timestamp lyrics[] over a melody track — local DiffSinger voice (Gahata Meiji from LUNAI Project, attribution embedded). voice: standard|hunter|lilith|phantom (timbre embeds). Breaths (AP) auto-inserted at phrase gaps. Output lands as a real 'vocals' audio track.",
                    {"type": "object", "properties": {"song": {"type": "string"}, "track": {"type": "string", "description": "melody track whose notes carry the words"},
                     "voice": {"type": "string", "description": "standard | hunter | lilith | phantom, OR a weighted blend minting a new timbre: 'hunter:0.6,lilith:0.4'"}},
                     "required": ["song", "track"]}),
    "edit_section": (t_edit_section, "SECTIONS AS OBJECTS: add/rename/move/remove/duplicate arrangement sections. duplicate stamps the whole section's bars right after itself across ALL tracks and shifts everything later — 'double the drop' in one call.",
                     {"type": "object", "properties": {"song": {"type": "string"}, "op": {"type": "string", "enum": ["add", "rename", "move", "remove", "duplicate"]},
                      "name": {"type": "string"}, "new_name": {"type": "string"},
                      "at_bar": {"type": "number"}, "to_bar": {"type": "number"}},
                      "required": ["song", "op", "name"]}),
    "edit_clip": (t_edit_clip, "PER-CLIP AUDIO EDIT — the hands' HB3.1 twin: move / trim_left / trim_right / fade_in / fade_out / gain / curve / clone / split / remove ONE audioClip. Left-trim keeps the audio anchored (offsetSec follows the edge); split makes two clips SHARING the file with contiguous offsets. args: track (name/idx), clip (idx, default 0), op, value (move/trims=beats, fades=beats, gain=dB, curve=linear|convex|concave|s, clone/split=beat). Track-scoped receipt; preview=true dry-runs.",
                  {"type": "object", "properties": {"song": {"type": "string"},
                   "track": {"type": ["string", "integer"]}, "clip": {"type": "integer"},
                   "op": {"type": "string"}, "value": {}, "preview": {"type": "boolean"}},
                   "required": ["song", "track", "op"]}),
    "set_clip_slot": (t_set_clip_slot, "PERFORMANCE VIEW: author a launcher slot (track x scene) — loopable pattern launched live in the Live view, bar-quantised. notes[] inline OR from_bar (copy arrangement bars). Audio slots: audio_file + offset_sec (+ source_bpm to warp the loop to the song tempo). [full laws: tool-guide skill]",
                      {"type": "object", "properties": {"song": {"type": "string"}, "track": {"type": "string"},
                       "scene": {"type": "integer"}, "follow": {"type": "string", "enum": ["next", "any", "stop"], "description": "scene-story grammar: what the launcher does when this clip finishes (engine-native follow action)"}, "follow_chance": {"type": "number", "description": "0..1 probability the follow fires (else the clip plays again) — the WF13 die; organic builds: 0.6-0.8"}, "notes": {"type": "array", "items": {"type": "object"}},
                       "from_bar": {"type": "number"}, "length_beats": {"type": "number"},
                       "slot_name": {"type": "string"}, "scene_name": {"type": "string"},
                       "audio_file": {"type": "string"}, "offset_sec": {"type": "number"},
                       "source_bpm": {"type": "number", "description": "original bpm of the audio — set it and the loop warps to the song tempo"},
                       "clear": {"type": "boolean"}}, "required": ["song", "track", "scene"]}),
    "jam": (t_jam, "THE JAM — the AI BAND plays a genre on a VIBE by closing the realtime loop: it GENERATES a phrase, HEARS what it actually sounds like (the ears bus's mid/high spectral fullness), DECIDES a move (build a layer / ease one / evolve / hold) toward the vibe, and plays the next phrase — an evolving CONTINUOUS take, not a static loop. vibe = the energy ARC the band realizes: build (sparse->full), peak (climb to a top), breakdown (full->stripped), wave (build then release), steady. The listening is REAL: the same seed under different vibes DIVERGES (build rises, breakdown falls). Realtime-feasible (gen+render << playback). Output is one editable song. B3 THE FOLLOW: pass `human` = a notes file (json array / song dict / jsonl; beats set-relative — e.g. a Rec take or audio_follow output) and the band composes AROUND it: space where it solos, its harmony/groove/energy where it plays (`follow` 0..1).",
            {"type": "object", "properties": {"genre": {"type": "string"},
             "vibe": {"type": "string", "enum": ["build", "peak", "breakdown", "wave", "steady"], "description": "the energy arc the band steers toward"},
             "song": {"type": "string", "description": "output song name"},
             "human": {"type": "string", "description": "B3 THE FOLLOW offline: a notes file (Rec take / audio_follow output) the band composes AROUND"},
             "follow": {"type": "number", "description": "0 = vibe arc alone, 1 = pure follow (default 0.5)"},
             "phrases": {"type": "number", "description": "how many 4-bar phrases to jam (2-16, default 8)"},
             "bpm": {"type": "number", "description": "B6: jam at THIS tempo (e.g. the open song's — the band enters the room's world)"},
             "key": {"type": "string", "description": "B6: jam in THIS key ('C minor') — harmonic rungs transpose, drums sacred"},
             "seed": {"type": "number"}}, "required": ["genre", "vibe"]}),
    "jam_live": (t_jam_live, "THE LIVE JAM — the REALTIME scheduler that makes the band 'just go': while a phrase PLAYS its real duration, the next phrase is rendered CONCURRENTLY (racing the deadline) and ready BEFORE it ends (no underrun), the band deciding the next move from what it HEARS during the current phrase's window. Same brain as `jam`, proven realtime: generation overlaps playback (total wall = pure playback time, not playback+gen). Returns the schedule (per-phrase gen time + slack) + the continuous take. Audio-to-speakers is the app's realtime device; this proves the generate-ahead/listen loop keeps up in real time. B3 THE FOLLOW: pass `human` = a growing notes file (json array / song dict / jsonl; beats set-relative) and the band plays WITH whoever writes it (energy bends via `follow` 0..1, busy soloists get space, voicing snaps to their harmony) — point it at the file your Rec tap writes.",
            {"type": "object", "properties": {"genre": {"type": "string"},
             "vibe": {"type": "string", "enum": ["build", "peak", "breakdown", "wave", "steady"]},
             "song": {"type": "string"}, "phrases": {"type": "number", "description": "phrases to jam (2-12, default 6)"},
             "bars": {"type": "number", "description": "bars per phrase (1-4, default 2 — faster cadence)"},
             "seed": {"type": "number"},
             "human": {"type": "string", "description": "B3 THE FOLLOW: a notes file (json/song/jsonl, set-relative beats) the band plays WITH"},
             "follow": {"type": "number", "description": "0 = vibe arc alone, 1 = pure follow (default 0.5)"},
             "bpm": {"type": "number", "description": "B6: play at THIS tempo (the room's world)"},
             "key": {"type": "string", "description": "B6: play in THIS key — harmonic rungs transpose"}},
             "required": ["genre", "vibe"]}),
    "generate_loop": (t_generate_loop, "THE LOOP GENERATOR (from scratch): genre in -> a complete, editable, loop-perfect song out in one call — drums from the genre's PatternArchetype grid (KG loop DNA, ALL 130 graph genres), bass in the genre's key by its bass_style (offbeat/roots/sliding-808/psy-rolling/sustained/log-drum), a color… [full laws: tool-guide skill]",
               {"type": "object", "properties": {"genre": {"type": "string"}, "song": {"type": "string", "description": "output song name"},
                "bars": {"type": "number", "description": "1-16, default 4"}, "seed": {"type": "number"},
                "bpm": {"type": "number"}, "key": {"type": "string", "description": "e.g. 'F minor'"}},
                "required": ["genre", "song"]}),
    "loop_variations": (t_loop_variations, "THE LOOP GENERATOR: N instant variations of a track's loop region (rotate/thin/dense/recolor/halftime/humanize — deterministic, zero-cost) landed as launcher scenes for Live-view jamming. The fastest 'give me options' move in the DAW; jam-capture keeps the winner.",
                        {"type": "object", "properties": {"song": {"type": "string"}, "track": {"type": "string"},
                         "from_bar": {"type": "number"}, "bars": {"type": "number"},
                         "count": {"type": "number", "description": "1-6, default 6"}},
                         "required": ["song", "track", "from_bar", "bars"]}),
    "apply_groove": (t_apply_groove, "Apply a groove (timing+velocity DNA) to a track: dilla, ukg_shuffle, psy_straight, dembow_lilt, boombap_56, or an extracted one. amount 0..1. THE difference between quantized and alive.",
                     {"type": "object", "properties": {"song": {"type": "string"}, "track": {"type": "string"},
                      "groove": {"type": "string"}, "amount": {"type": "number"}},
                      "required": ["song", "track", "groove"]}),
    "extract_groove": (t_extract_groove, "Learn a named groove (offsets+velocities per 16th slot) from a track's notes, OR from AUDIO via wav_path+bpm (an imported drums stem = the timing DNA of someone else's record; onset-timed to ~3ms, grid-phase auto-found) — then apply_groove it anywhere. Audio grooves also land as KG Groove nodes.",
                       {"type": "object", "properties": {"song": {"type": "string"}, "track": {"type": "string"},
                        "new_name": {"type": "string"},
                        "wav_path": {"type": "string", "description": "audio mode: drums stem/loop to learn from"},
                        "bpm": {"type": "number", "description": "audio mode: the file's own tempo"}},
                        "required": ["new_name"]}),
    "export_als": (t_export_als, "Export a song as Ableton Live .als (gzipped LiveSet: tempo + every note-bearing track as a MIDI arrangement clip) — 'produce here, finish in Live'. Round-trip verified against import_als (735/735 notes exact).",
               {"type": "object", "properties": {"song": {"type": "string"}}, "required": ["song"]}),
    "export_dawproject": (t_export_dawproject, "Export a song as .dawproject (opens in Bitwig/Cubase/Nuendo/Studio One): notes, tempo, mixer, embedded audio. 'Produce here, finish anywhere.'",
                          {"type": "object", "properties": {"song": {"type": "string"}}, "required": ["song"]}),
    "duplicate_bars": (t_duplicate_bars, "ARRANGEMENT CALCULUS (how long tracks are built): copy bars [fromBar,toBar) to atBar, `times` consecutive copies, server-side and instant. Compose an 8-32 bar seed in detail, then STAMP it — never write hundreds of literal notes. Optional tracks filter.",
                       {"type": "object", "properties": {"song": {"type": "string"}, "fromBar": {"type": "number"},
                        "toBar": {"type": "number"}, "atBar": {"type": "number"}, "times": {"type": "number"},
                        "tracks": {"type": ["array", "string"], "description": "optional track-name filter"}},
                        "required": ["song", "fromBar", "toBar", "atBar"]}),
    "clear_bars": (t_clear_bars, "Delete notes in bars [fromBar,toBar) (optional tracks filter) — carve breakdowns (clear drums) and drops (clear melody) out of stamped material.",
                   {"type": "object", "properties": {"song": {"type": "string"}, "fromBar": {"type": "number"},
                    "toBar": {"type": "number"}, "tracks": {"type": ["array", "string"]}},
                    "required": ["song", "fromBar", "toBar"]}),
    "import_midi": (t_import_midi, "Import a .mid file as a new song (tracks/notes/tempo; sources default to kits).",
                    {"type": "object", "properties": {"midi_path": {"type": "string"}, "song": {"type": "string"}},
                     "required": ["midi_path", "song"]}),
    "write_song": (t_write_song, "Validate and save a song (the arrangement, symbolic). Returns per-field errors if invalid.",
                   {"type": "object", "properties": {"name": {"type": "string"}, "song": {"type": ["object", "string"]}}, "required": ["name", "song"]}),
    "render_song": (t_render_song, "Render a saved song through the Tracktion engine to songs/<name>.wav (headless). Songs over 24 bars auto-clamp to a 16-bar preview unless full:true (the final full render after the proposal is automatic and never clamped).",
                    {"type": "object", "properties": {"name": {"type": "string"}, "max_bars": {"type": "number", "description": "render only the first N bars (fast self-check on long songs; final full render is automatic after the proposal)"}, "full": {"type": "boolean", "description": "force the WHOLE song (disables the >24-bar auto-preview clamp)"}}, "required": ["name"]}),
    "analyze_wav": (t_analyze_wav, "Measure a rendered WAV: peak dBFS, LUFS, clipping, band balance, centroid, f0. Use after every render; act on the numbers (see mix-headroom skill).",
                    {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}),
    "master_report": (t_master_report, "THE MASTERING VERDICT: render (if stale) + measure + judge against the genre's KG MixTarget in ONE call — pass/score, per-check got-vs-want (clipped, true peak, LUFS window, band order, spectral floors, phase, masterGainDb=0 law, brickwall-last law) and a SOURCE-FIX hint on every failure, ordered by what to fix first. [full laws: tool-guide skill]",
                    {"type": "object", "properties": {"song": {"type": "string"}, "genre": {"type": "string", "description": "KG MixTarget lane (default: song._loop.genre, else a generic streaming/club target)"}, "wav": {"type": "string", "description": "judge an arbitrary wav instead of a song"}, "platform": {"type": "string", "description": "deliver to a platform ref (spotify|apple|youtube|tidal|amazon|deezer|tiktok|streaming): overrides LUFS window + true-peak ceiling to its BS.1770 normalization target"}},
                     "required": []}),
    "auto_master": (t_auto_master, "AUTO-MASTER, THE CONVERGER: closed-loop mastering in one call — normalizes the chain (character inserts preserved, legacy master_limiter killed, masterGainDb folded into the input trim), then iterates render->measure->adjust (makeup/input trims for LUFS, ceiling for true peak + sub-dominant law,… [full laws: tool-guide skill]",
                    {"type": "object", "properties": {"song": {"type": "string"}, "genre": {"type": "string", "description": "KG MixTarget lane (default: song._loop.genre)"}, "platform": {"type": "string", "description": "converge to a platform ref (spotify|apple|youtube|tidal|amazon|deezer|...): sets the LUFS/dBTP target; genre still sets band balance"}, "reference": {"type": "string", "description": "wav/mp3 path: master toward this record (LUFS window + band tilt)"}, "max_iters": {"type": "number"}, "no_eq": {"type": "boolean", "description": "never touch band balance at the bus"}},
                     "required": ["song"]}),
    "analyze_reference": (t_analyze_reference, "REFERENCE MATCHING (V27): 'make it sit like THIS track' — analyze a reference wav/mp3 vs the current song and return a GAP REPORT where every delta names the concrete move (trim dB, band rebalance at the source, widen, transpose, automation arc). Optional genre adds the KG MixTarget pass/fail lane. NO reference argument + the song has a reference DECK -> judged vs the deck composite (the standing multi-ref contract). Analysis only — the reference's audio never enters the session.",
                    {"type": "object", "properties": {"reference": {"type": "string"}, "song": {"type": "string"}, "wav": {"type": "string"}, "genre": {"type": "string"}}}),
    "reference_deck": (t_reference_deck, "THE REFERENCE DECK: a song's STANDING multi-reference target ('make it sit like THESE tracks', persisted). action add {path, weight?} / remove {path|index} / list. Once built, analyze_reference {song} with no reference judges the mix against the weighted composite (band curve/LUFS/width/centroid). Paths+numbers only — no reference audio enters the session.",
                    {"type": "object", "properties": {"song": {"type": "string"}, "action": {"type": "string", "enum": ["add", "remove", "list"]}, "path": {"type": "string"}, "weight": {"type": "number"}, "index": {"type": "integer"}}, "required": ["song"]}),
    "diff_ear": (t_diff_ear, "THE DIFFERENTIAL EAR: 'what changed?' between two renders as ONE measured sentence (top audible moves: LU, bands, width, brightness, PSR crush/breath, arc) + ranked deltas + a playable B-minus-A residue wav. song= compares the base render vs the pending take's render; or pass a= b= wavs. Use after every revise to tell the user what ACTUALLY moved.",
                    {"type": "object", "properties": {"song": {"type": "string"}, "a": {"type": "string"}, "b": {"type": "string"}}}),
    "release_pack": (t_release_pack, "THE RELEASE PACK: one call -> songs/<name>_release/ with the C2PA-signed master, per-track stems, exact MIDI, .dawproject session, credits.md (provenance, voices, per-platform loudness verdicts) and THE LICENSE GATE (a non-commercial voice marks the pack PRIVATE-ONLY, loudly). platforms: list or comma string (spotify/apple/youtube/tidal/...). bits: 16 adds TPDF dither for CD delivery.",
                    {"type": "object", "properties": {"song": {"type": "string"}, "platforms": {"type": "string"}, "bits": {"type": "integer"}}, "required": ["song"]}),
    "match_reference": (t_match_reference, "R2 THE REFERENCE CIRCLE: gap report vs a STORED reference — every import_song_audio banks the record's DNA (bpm/key, sections, chords, groove, band profile, lufs/dbtp/crest) as a KG Reference node, so 'make it sound like that record I imported' needs NO wav re-read. Returns always-on numeric deltas (ref minus current: lufs/dbtp/bands/width/centroid/bpm) + thresholded gap MOVES + both structures + the record's own groove to apply_groove. Reference = song name or hash prefix; list stored ones by passing anything unknown.",
                    {"type": "object", "properties": {"song": {"type": "string"}, "reference": {"type": "string"}}, "required": ["song", "reference"]}),
    "time_machine": (t_time_machine, "R7 THE TIME MACHINE twin: list a song's whole timeline — every accept (git) + crash-net journal moments, newest first with tracks/bars stats — or restore any point AS A PROPOSAL (writes _prop_<song>.json; base untouched until user accept; history never rewritten). Use when the user says 'go back to how it was', 'yesterday's version', 'before you changed X'. action:list first, then action:restore with the ref.",
                    {"type": "object", "properties": {"song": {"type": "string"}, "action": {"type": "string", "enum": ["list", "restore"]}, "ref": {"type": "string"}, "limit": {"type": "integer"}}, "required": ["song"]}),
    "finish_audit": (t_finish_audit, "THE FINISH-IT ARC (V40): audit a song like a finisher — structure (begin/travel/END), variation, motion, feel, mix vs the ears (+ optional KG MixTarget) — and get a STAGED PLAN where every stage names the executing tool. Use when the user says 'finish it', when a song stalls as a loop, or before export. Verdicts: SKELETON / IN PROGRESS / ALMOST / FINISHED.",
                    {"type": "object", "properties": {"song": {"type": "string"}, "genre": {"type": "string"}}, "required": ["song"]}),
    "session_recap": (t_session_recap, "SESSION RECAP (V42): where you left off — recent ships, pending proposals, crash-journal recovery, stale renders, crate count — and exactly ONE suggested next step. Use at session start or when the user asks 'where was I'.",
                    {"type": "object", "properties": {}}),
    "beat_grid": (t_beat_grid, "EARS v4 THE BEAT BRAIN (Beat This!, MIT): neural beat/downbeat tracking on any audio file — bpm (±~1 on the battery), first beat/downbeat, bar count, meter, stability. Use on imported/reference audio before warping, DJ-blending, or groove extraction. Heavier than analyze_wav (loads a model) — call when grid TRUTH matters, not on every render.",
                    {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}),
    "loop_infill": (t_loop_infill, "LOOP INFILLING (co-creation reroll): regenerate ONE part's notes (drums|bass|lead|color|<track>) from the genre's KG DNA with a new seed — every other track stays byte-identical and the infilled track KEEPS the user's gain/pan/fx. Locked tracks refuse. Use when the user likes the loop but wants a different bassline/drums/etc.",
                    {"type": "object", "properties": {"song": {"type": "string"}, "part": {"type": "string"}, "seed": {"type": "number"}, "genre": {"type": "string"}}, "required": ["song", "part"]}),
    "lock_track": (t_lock_track, "EDIT LOCKS (the user's ground rules): lock/unlock a track against agent edits. A locked track is INVIOLABLE — any proposal touching it gets that track reverted by the sidecar while the rest of the proposal survives. Use when the user says 'lock X', 'don't touch X', 'X is done'. Set locked=false to release.",
                    {"type": "object", "properties": {"song": {"type": "string"}, "track": {"type": "string"}, "locked": {"type": "boolean"}}, "required": ["song", "track"]}),
    "freeze_track": (t_freeze_track, "TRACK FREEZE (V47): freeze = a CACHED RENDER OF SYMBOLS — the track's source/notes/fx/automation stash VERBATIM in track.frozen and the lane plays the cache as audio (gain/pan/sends stay live for mixing). unfreeze restores the symbols bit-exact and deletes the cache. Use to save CPU on heavy tracks or pin a sound while arranging. action: freeze | unfreeze | check (check lists frozen tracks; no track arg needed).",
                    {"type": "object", "properties": {"song": {"type": "string"}, "track": {"type": "string"}, "action": {"type": "string", "enum": ["freeze", "unfreeze", "check"]}}, "required": ["song"]}),
    "stem_callouts": (t_stem_callouts, "PER-STEM CALLOUTS (V28): render stems, analyze each track SOLO, cross-examine pairs — inaudible tracks, solo clippers, misplaced low weight, phase risk, masking fights (with the kick/808-layering exception). sections=true PINS callouts to the timeline (per-section analysis: 'melody+pad fight in… [full laws: tool-guide skill]",
                    {"type": "object", "properties": {"song": {"type": "string"}, "sections": {"type": "boolean"}}, "required": ["song"]}),
    "publish_song": (t_publish_song, "THE /PUBLISH FLOW (V22): finish gate -> C2PA-signed master -> ears on the signed file (+genre MixTarget) -> manifest verify -> SoundCloud upload. dry_run DEFAULTS TRUE (everything real except the outbound transfer); set dry_run false + ask the user before any actual upload; public only on the user's explicit word (private otherwise).",
                    {"type": "object", "properties": {"song": {"type": "string"}, "genre": {"type": "string"}, "title": {"type": "string"}, "public": {"type": "boolean"}, "dry_run": {"type": "boolean"}}, "required": ["song"]}),
    "build_loop_machine": (t_build_loop_machine, "THE LOOP MACHINE (#33): turn any pile of loop wavs into a playable pad machine — each loop classified by the sound tensor (drums/bass/melodic/perc), tracks x build-up scenes (Drums -> +Bass -> +Keys -> FULL), every slot warped to one master bpm. Pads already launch scenes via MIDI.",
               {"type": "object", "properties": {"loops": {"type": "array", "items": {"type": "string"}},
                "song": {"type": "string"}, "bpm": {"type": "number"}},
                "required": ["loops", "song"]}),
    "vst_presets": (t_vst_presets, "THE 4300-SOUND RAIL: factory presets across hosted synths (Surge XT 3559, TAL 256, Odin2 260) AND FX (Surge XT Effects 291: reverbs/delays/chorus/EQ/distortion + experimental Airwindows category — 'get' returns use_as_fx {id, preset} to drop into any fx chain) by name or category… [full laws: tool-guide skill]",
               {"type": "object", "properties": {"query": {"type": "string"}, "plugin": {"type": "string"},
                "mode": {"type": "string", "enum": ["list", "get"]},
                "song": {"type": "string", "description": "with track: ONE-CALL APPLY — land the preset on this song's track directly (not just browse/get)"},
                "track": {"type": "string", "description": "target track for one-call apply (created if absent)"}},
                "required": ["query"]}),
    "reaper_bridge": (t_reaper, "THE REAPER BRIDGE: song.json <-> .rpp (round-trip EXACT at MIDI resolution). Pass song (+optional rpp_out) to EXPORT for REAPER; pass rpp_in (+song name) to IMPORT a REAPER project as an editable session.",
               {"type": "object", "properties": {"song": {"type": "string"}, "rpp_in": {"type": "string"}, "rpp_out": {"type": "string"}},
                "required": []}),
    "make_track": (t_make_track, "THE ONE-BUTTON TRACK: genre in -> a COMPLETE arranged song out (generated loop w/ all four dimensions [rhythm/melody/harmony/fills] -> genre-aware form [drops or verse/chorus] -> rendered + analyzed). Deterministic per seed. THE fastest path from nothing to music; then differentiate. Hyperfocus persona's best friend.",
               {"type": "object", "properties": {"genre": {"type": "string"}, "song": {"type": "string"}, "seed": {"type": "number"}},
                "required": ["genre"]}),
    "arrange_song": (t_arrange_song, "LOOP -> SONG SKELETON (deterministic, zero tokens): takes any loop song (e.g. generate_loop output) and builds genre-aware form: EDM genres get intro/build/DROP/break/outro; song-form genres (gospel/soul/rock/reggae...) get verse/CHORUS/bridge — pass genre to pick by class-aware stripping — intro =… [full laws: tool-guide skill]",
               {"type": "object", "properties": {"song": {"type": "string"}, "form": {"type": "string"}, "seed": {"type": "number"}, "out": {"type": "string"}, "genre": {"type": "string"}},
                "required": ["song"]}),
    "scene_strips": (t_scene_strips, "LIVE-REMIX STAPLES: appends strip scenes to any sceneful song — 'Drums only' (breakdown), 'No drums' (the musical/acapella moment), 'Bass+Drums' (DJ skeleton). Non-destructive, idempotent, classes tracks by name then sound tensor. The fastest way to make any session PERFORMABLE.",
               {"type": "object", "properties": {"song": {"type": "string"}, "from_scene": {"type": "number"}},
                "required": ["song"]}),
    "scene_bounce": (t_scene_bounce, "HEAR A SCENE: renders launcher scene k (by index or name) as audio + analysis — slots become looped timeline material on a scratch copy. Use after authoring scene stories to VERIFY each scene sounds right (build-ups grow, drops hit).",
               {"type": "object", "properties": {"song": {"type": "string"}, "scene": {"type": "string"}, "bars": {"type": "number"}},
                "required": ["song", "scene"]}),
    "tune_vocal": (t_tune_vocal, "CONTEXT-TUNE (V45), the song-aware autotune: retunes a track's audio clip reading the ARRANGEMENT itself — per-beat chord field from every other track + scale + optional guide melody — target picked by Viterbi (chord-tone/scale/contour), resynthesized through the WORLD vocoder (formants preserved =… [full laws: tool-guide skill]",
                   {"type": "object", "properties": {"song": {"type": "string"}, "track": {"type": "string"},
                    "style": {"type": "string", "description": "tpain|hard|natural|transparent (default natural)"},
                    "strength": {"type": "number", "description": "0..1 correction amount override"},
                    "guide_track": {"type": "string", "description": "track whose notes are the target melody"},
                    "region": {"type": "array", "description": "[beat0, beat1] — only correct inside this span"},
                    "key": {"type": "string", "description": "override scale, e.g. 'F minor'"},
                    "clip_index": {"type": "number"}},
                    "required": ["song", "track"]}),
    "listen_live": (t_listen_live, "HEAR the master bus LIVE: tail the 10 Hz feature frames (rms/peak/quick-dBTP/4 bands/crest/beat) the ears bus streams while anything plays or renders. Reflexes, not metrology — use for 'what is sounding RIGHT NOW' (is it clipping? bass-heavy? building or fading?); render_song+analyze_wav/hear stay the deep ears.",
                    {"type": "object", "properties": {"seconds": {"type": "number", "description": "how far back to listen (1-30, default 5)"}}, "required": []}),
    "hear": (t_hear, "SEE the sound: mel-band x time ASCII heatmap of a WAV (top rows = highs, bottom = sub; chars = intensity; onset row + bar ruler with bpm). Reads like an image: builds fill bottom-up, a drop = full-column jump, empty top third on a lead/horn genre = spectral collapse, column fades = tails/gaps. Use WITH analyze_wav: numbers for targets, sight for structure.",
             {"type": "object", "properties": {"path": {"type": "string"}, "bpm": {"type": "number", "description": "adds the bar ruler"}}, "required": ["path"]}),
}

# ---------- JSON-RPC over stdio ----------
def reply(id_, result=None, error=None):
    msg = {"jsonrpc": "2.0", "id": id_}
    if error is not None:
        msg["error"] = error
    else:
        msg["result"] = result
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()

# ---- THE CORE LANE (firing 111, the defer-tax kill): the CLI defers schemas by
# server tool COUNT. Advertise only the core (<= ~36) by default; the LONG TAIL
# stays callable through the use_tool proxy (same handlers, receipts, validators).
# SOTADAW_TOOL_LANE=full restores the old behavior (probes, audits, exotic rigs).
CORE_TOOLS = {
    "start_session", "get_selection", "get_song", "get_song_summary", "get_song_region",
    "write_song", "update_track", "update_song_meta", "add_track", "set_track_fx",
    "list_instruments", "list_kits", "get_skill", "search_library",
    "locate", "select_notes", "surgical_edit", "duplicate_bars", "clear_bars",
    "automate", "set_buses", "list_plugin_params", "set_track_param",
    "render_song", "analyze_wav", "hear", "master_report",
    "generate_loop", "arrange_song", "apply_groove", "harmonize", "chord_map",
    "write_lyrics", "edit_section", "doctor",
}

def t_use_tool(args):
    """Proxy into the LONG TAIL (bridges, DJ, presets, vocals, verbs...) without
    advertising 87 schemas. name + args dict; identical handlers/receipts run."""
    name = str(args.get("name", ""))
    if name in ("use_tool",):
        return "no recursion"
    if name not in TOOLS:
        return ("unknown tool '" + name + "'. Long-tail catalog: "
                + ", ".join(sorted(n for n in TOOLS if n not in CORE_TOOLS)))
    inner = args.get("args") or {}
    if isinstance(inner, str):
        try:
            inner = json.loads(inner)
        except json.JSONDecodeError as e:
            return f"args is not valid JSON: {e}"
    return TOOLS[name][0](inner)

TOOLS["use_tool"] = (t_use_tool,
    "Call any LONG-TAIL tool not in the visible set (DAW bridges als/dawproject/flp/"
    "reaper/rekordbox, dj_blend/dj_set, vst_presets/use_preset, sing_lyrics/hum_topline/"
    "tune_vocal, import_song_audio, loop_variations, prescribe/automix/humanize/"
    "intensify/color/restyle/energy_curve, export_*...). name = tool, args = its "
    "arguments object. Unknown names return the full catalog. LAW: before big moves "
    "with a long-tail tool, get_skill(\"tool-guide-tail\") — its FULL laws live there.",
    {"type": "object", "properties": {"name": {"type": "string"},
                                      "args": {"type": "object"}},
     "required": ["name"]})
CORE_TOOLS.add("use_tool")
CORE_TOOLS.add("audio_to_midi")
CORE_TOOLS.add("midi_to_audio")
CORE_TOOLS.add("add_topline")
CORE_TOOLS.add("align_lyrics")
CORE_TOOLS.add("sound_neighbors")
CORE_TOOLS.add("chords_from_audio")
CORE_TOOLS.add("listen_live")
CORE_TOOLS.add("jam")
CORE_TOOLS.add("keep_jam")
CORE_TOOLS.add("jam_live")

def lane_tools():
    if os.environ.get("SOTADAW_TOOL_LANE", "core") == "full":
        return TOOLS
    return {n: TOOLS[n] for n in TOOLS if n in CORE_TOOLS}

def main():
    log("server up, root =", ROOT)
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        method, id_ = req.get("method"), req.get("id")
        if method == "initialize":
            reply(id_, {"protocolVersion": req["params"].get("protocolVersion", "2024-11-05"),
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "sotadaw", "version": "0.1.0"}})
        elif method == "notifications/initialized":
            pass
        elif method == "ping":
            reply(id_, {})
        elif method == "tools/list":
            reply(id_, {"tools": [{"name": n, "description": d, "inputSchema": s}
                                   for n, (f, d, s) in lane_tools().items()]})
        elif method == "tools/call":
            name = req["params"]["name"]
            args = req["params"].get("arguments") or {}
            if name not in TOOLS:
                reply(id_, {"content": [{"type": "text", "text": f"unknown tool {name}"}], "isError": True})
                continue
            entry = TOOLS[name]
            schema = entry[2] if len(entry) > 2 else {}
            props = list((schema.get("properties") or {}).keys())
            # ARG FORGIVENESS: song<->name confusion is the #1 model stumble
            # (live: 'render_song wants a different key'; a KeyError repr read
            # as 'the render path is broken'). Alias instead of crashing.
            req_keys = schema.get("required") or []
            if "name" in req_keys and "name" not in args and "song" in args:
                args["name"] = args.pop("song")
            if "song" in req_keys and "song" not in args and "name" in args:
                args["song"] = args.pop("name")
            missing = [k for k in req_keys if k not in args]
            if missing:
                reply(id_, {"content": [{"type": "text", "text":
                    f"MISSING ARGUMENT(S) {missing} for {name}. This tool's arguments "
                    f"are: {', '.join(props) or '(none)'}. Re-call with these exact "
                    f"names — do NOT conclude the tool is broken."}], "isError": True})
                continue
            try:
                text = TOOLS[name][0](args)
                reply(id_, {"content": [{"type": "text", "text": text}], "isError": False})
            except KeyError as e:
                log("tool arg error:", name, repr(e))
                reply(id_, {"content": [{"type": "text", "text":
                    f"ARGUMENT ERROR in {name}: missing key {e}. Arguments are: "
                    f"{', '.join(props) or '(none)'} — re-call with exact names; "
                    f"the tool itself is fine."}], "isError": True})
            except Exception as e:
                log("tool error:", name, repr(e))
                reply(id_, {"content": [{"type": "text", "text": f"TOOL ERROR: {e!r}"}], "isError": True})
        elif id_ is not None:
            reply(id_, error={"code": -32601, "message": f"method not found: {method}"})

if __name__ == "__main__":
    main()
