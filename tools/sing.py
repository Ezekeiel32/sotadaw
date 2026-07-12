#!/usr/bin/env python3
"""THE VOICE (W2) — scaffold v0: song.json (timestamp lyrics + melody) -> DiffSinger .ds.

  sing.py status                  what's installed / runner state
  sing.py ds <song> <track>       build <song>.ds from lyrics[] + that track's melody

Voicebank: library/voices/gahata_meiji (LUNAI Project — attribution REQUIRED:
'Gahata Meiji from LUNAI Project'; non-commercial creative use per its terms of use;
the bank is user-downloaded content and is never redistributed with this software).

Pipeline (COMPLETE — .ds builder + inference runner both shipped + verified):
  lyrics+notes -> word/note alignment -> EN phonemes (dsdict-en) -> .ds JSON
  -> dur/pitch/variance/acoustic ONNX -> tgm_hifigan vocoder -> vocal WAV (WORKS)
  -> audioClips track (Timbre Law: symbolic in, replaceable track out).
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# THE VOICE UNIVERSE (BEST_DAW_30 #30): banks are a REGISTRY, not a hardcode.
# library/voices/<bank>/bank.json = {name, attribution, license{commercial,...},
# assets{...}} — any DiffSinger ONNX bank drops in beside gahata_meiji; the
# active bank resolves SOTADAW_VOICE_BANK -> default. License truth rides the
# manifest into the landing stamps, the C2PA manifest and THE LICENSE GATE.
DEFAULT_BANK = "gahata_meiji"
_FALLBACK_MANIFEST = {                      # pre-manifest banks stay working
    "name": DEFAULT_BANK, "display": "Gahata Meiji (LUNAI)",
    "attribution": "Gahata Meiji from LUNAI Project",
    "license": {"commercial": False, "attribution_required": True},
    "assets": {"acoustic": "files/acoustic.onnx", "dur": "files/dur.onnx",
               "pitch": "files/pitch.onnx", "variance": "files/variance.onnx",
               "vocoder": "tgm_hifigan/tgm_hifigan_v110.onnx",
               "dsdict_en": "configs/dsdur/dsdict-en-tgm.yaml"}}


def bank_dir(name=None):
    nm = name or os.environ.get("SOTADAW_VOICE_BANK") or DEFAULT_BANK
    return os.path.join(ROOT, "library", "voices", nm)


BANK = bank_dir()


def manifest(bank=None):
    try:
        m = json.load(open(os.path.join(bank or BANK, "bank.json")))
        return {**_FALLBACK_MANIFEST, **m} if isinstance(m, dict) else dict(_FALLBACK_MANIFEST)
    except Exception:
        return dict(_FALLBACK_MANIFEST)


def find_hook_gaps(song, track_name, max_per_hook=2, min_gap=1.5, seed=0):
    """THE ADLIB RAIL kernel (ledger dr21 tail, 2026-07-12): the room an
    answer belongs in — ONSET gaps (IOI >= min_gap beats) inside hook
    sections. IOI, not silence: held/legato tails eat the rests on paper,
    but records answer OVER the held note (the audible receipt caught the
    silence-based detector starved by a loop that breathes 1.5 beats at the
    onset level). The answer enters just after the call word lands and must
    leave 0.2 beats before the next onset. pitch = the call note (the answer
    echoes it). Pure + seeded. Cost receipt: a 2-word phrase sings in ~8s."""
    import random as _r
    secs = song.get("sections") or []
    mel = next((t for t in song.get("tracks", [])
                if t.get("name") == track_name), None)
    if not secs or not mel or not mel.get("notes"):
        return []
    notes = sorted(mel["notes"], key=lambda n: float(n.get("start", 0)))
    total = float(song.get("lengthBars", 0)) * 4.0
    hooks = []
    for i, sc in enumerate(secs):
        if str(sc.get("name", "")).rstrip("0123456789") in ("chorus", "drop", "hook", "theme"):
            b0 = float(sc.get("startBar", 0)) * 4.0
            b1 = (float(secs[i + 1].get("startBar", 0)) * 4.0
                  if i + 1 < len(secs) else total)
            hooks.append((b0, b1))
    rng = _r.Random(f"adlib/{seed}")
    out = []
    for b0, b1 in hooks:
        span = [n for n in notes if b0 <= float(n["start"]) < b1]
        gaps = []
        for a, b in zip(span, span[1:]):
            ioi = float(b["start"]) - float(a["start"])
            if ioi >= min_gap:
                enter = float(a["start"]) + min(float(a.get("len", 0.5)), 0.6)
                room = float(b["start"]) - enter - 0.2
                if room >= 0.5:
                    gaps.append((round(enter, 4), round(min(room, 2.0), 4),
                                 int(a.get("pitch", 62))))
        rng.shuffle(gaps)
        out += sorted(gaps[:max_per_hook])
    return sorted(out)


def attribution(bank=None):
    return manifest(bank).get("attribution", _FALLBACK_MANIFEST["attribution"])


def list_banks():
    """Every installed bank (a dir with bank.json OR the known asset shape)."""
    vd = os.path.join(ROOT, "library", "voices")
    out = []
    if os.path.isdir(vd):
        for d in sorted(os.listdir(vd)):
            p = os.path.join(vd, d)
            if os.path.isdir(p) and (os.path.exists(os.path.join(p, "bank.json"))
                                     or os.path.isdir(os.path.join(p, "files"))):
                out.append(d)
    return out


def assets():
    m = manifest()
    return {k: os.path.join(BANK, *rel.split("/"))
            for k, rel in m.get("assets", _FALLBACK_MANIFEST["assets"]).items()}

def status():
    a = assets()
    missing = [k for k, p in a.items() if not os.path.exists(p)]
    print(json.dumps({
        "bank": (manifest().get("display", os.path.basename(BANK)) if os.path.isdir(BANK) else "NOT INSTALLED"),
        "banks_installed": list_banks(),
        "attribution_required": attribution(),
        "assets_ok": [k for k in a if k not in missing],
        "missing": missing,
        "runner": "BUILT + verified (dur->pitch->acoustic->vocoder; f0 tracks melody, sing_battery)" if not missing
                else "download bank to library/voices/"}, indent=1))

def _skip(msg):
    """Graceful skip = one actionable line on STDOUT + rc 1. Both MCP lanes
    (sing_lyrics / hum_topline) return run()[1] — stdout ONLY — so a stderr
    sys.exit message surfaces as a blank 'sing failed'."""
    print(msg)
    sys.exit(1)

def require_bank():
    """One actionable line instead of a raw traceback when the 862MB voice bank
    (gitignored) isn't on this machine — the Inspiron's HUM press hit a bare
    FileNotFoundError. Everything except HUM/sing works without the bank."""
    missing = [k for k, p in assets().items() if not os.path.exists(p)]
    if missing:
        _skip("SINGING VOICE BANK NOT INSTALLED on this machine (862MB, not in git).\n"
              "Install: see the Voices section on the SOTA DAW site (separate non-commercial download)"
              " && tar xzf voices.tar.gz -C library/ && rm voices.tar.gz\n"
              "Only HUM + sing_lyrics need it - everything else already works.")

def _mem_avail_gb():
    """Available system RAM in GB — psutil when present, /proc/meminfo fallback;
    None = unmeasurable (never block a box we can't read)."""
    try:
        import psutil
        return psutil.virtual_memory().available / (1 << 30)
    except Exception:
        pass
    try:
        for line in open("/proc/meminfo"):
            if line.startswith("MemAvailable:"):
                return int(line.split()[1]) / (1 << 20)   # kB -> GB
    except Exception:
        pass
    return None

_SING_LOCK = None   # module-held: the flock lives for the SYNTHESIS


def _sing_release():
    """The lock guards the SYNTHESIS (models in RAM/GPU); the landing is
    JSON + file work. Release before landing — the adlib CHILD sing queued
    on its own parent's flock until the 600s wait expired, then skipped
    SILENTLY (the missing-wav branch, adlib court #2, 2026-07-12)."""
    global _SING_LOCK
    if _SING_LOCK is not None:
        try:
            import fcntl
            fcntl.flock(_SING_LOCK, fcntl.LOCK_UN)
            _SING_LOCK.close()
        except Exception:
            pass
        _SING_LOCK = None

def _cuda_preload():
    """ORT-GPU dlopens CUDA sonames it does not bundle (libcudart.so.13,
    libcudnn.so.9, …). torch's pip wheels DO bundle them (site-packages/
    nvidia/*/lib) — preload with RTLD_GLOBAL so ORT's dlopen resolves from
    the already-loaded images. LD_LIBRARY_PATH is useless here (read once at
    process start); system CUDA is not needed. Silent no-op when absent —
    the session try/except then falls back to CPU."""
    import ctypes, glob, site, sysconfig
    roots = set()
    cands = list(getattr(site, "getsitepackages", lambda: [])())
    cands.append(site.getusersitepackages())
    cands.append(sysconfig.get_paths().get("purelib"))
    for sp in cands:
        if sp and os.path.isdir(os.path.join(sp, "nvidia")):
            roots.add(os.path.join(sp, "nvidia"))
    for name in ("libcudart.so.*", "libcublasLt.so.*", "libcublas.so.*",
                 "libcufft.so.*", "libcurand.so.*", "libnvrtc.so.*",
                 "libcudnn.so.*"):          # load order matters: cudart first
        for r in sorted(roots):
            for p in sorted(glob.glob(os.path.join(r, "*", "lib", name))):
                try:
                    ctypes.CDLL(p, mode=ctypes.RTLD_GLOBAL)
                except OSError:
                    pass


def _sing_gate(need_gb=3.0):
    """OOM LAW (§7.6): the acoustic+vocoder sessions want ~3GB; under memory
    saturation the load is OOM-killed SILENTLY (no vocals, no error, f158).
    Gate the load: (1) a machine-wide flock QUEUES concurrent renders — two
    HUM presses would pay the bill twice at the same instant; (2) a memory
    preflight SKIPS with one actionable stdout line when free RAM is short.
    SOTADAW_SING_MINGB overrides the floor (<=0 disables);
    SOTADAW_SING_LOCK_WAIT caps the queue wait in seconds."""
    global _SING_LOCK
    import fcntl, time
    lockp = os.path.join(ROOT, "agent", "ipc", "sing.lock")
    os.makedirs(os.path.dirname(lockp), exist_ok=True)
    fd = open(lockp, "w")
    try:
        wait = float(os.environ.get("SOTADAW_SING_LOCK_WAIT", "600"))
    except ValueError:
        wait = 600.0
    deadline = time.time() + wait
    while True:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            break
        except OSError:
            if time.time() >= deadline:
                _skip(f"SINGING SKIPPED: another singing render holds the model lock "
                      f"(waited {wait:.0f}s). Retry when it finishes.")
            time.sleep(0.5)
    _SING_LOCK = fd
    try:
        need = float(os.environ.get("SOTADAW_SING_MINGB", need_gb))
    except ValueError:
        need = need_gb
    if need <= 0:
        return
    avail = _mem_avail_gb()
    try:
        ram_wait = float(os.environ.get("SOTADAW_SING_WAIT_S", "0"))
    except ValueError:
        ram_wait = 0.0
    if ram_wait > 0 and avail is not None and avail < need:
        # THE DETACH LAW (2026-07-09): an importing parent holds transcription
        # models while we boot — auto-sing died on ARRIVAL on every real
        # import (proven live on aranyanyara). A detached child WAITS for the
        # importer's exit to free RAM instead of dying on it.
        print(f"[sing] {avail:.1f}GB free < {need:.1f}GB — waiting up to "
              f"{ram_wait:.0f}s for RAM…", flush=True)
        rd = time.time() + ram_wait
        while avail is not None and avail < need and time.time() < rd:
            time.sleep(5.0)
            avail = _mem_avail_gb()
    if avail is not None and avail < need:
        _skip(f"SINGING SKIPPED: {avail:.1f}GB RAM free < {need:.1f}GB the voice models "
              f"need (the load would be OOM-killed silently). Free memory and retry, "
              f"or SOTADAW_SING_MINGB=0 to force.")

def load_en_dict():
    import yaml
    d = yaml.safe_load(open(assets()["dsdict_en"]))
    table = {}
    for e in d.get("entries", []):
        table[str(e["grapheme"]).lower()] = e["phonemes"]
    return table

def build_ds(song_name, track_name):
    song = json.load(open(os.path.join(ROOT, "songs", f"{song_name}.json")))
    lyr = song.get("lyrics", [])
    if not lyr:
        return print("song has no lyrics[] — write_lyrics first")
    tr = next((t for t in song["tracks"] if t.get("name") == track_name), None)
    if tr is None or not tr.get("notes"):
        return print(f"no melody notes on '{track_name}'")
    table = load_en_dict()
    spb = 60.0 / float(song.get("bpm", 120))
    notes = sorted(tr["notes"], key=lambda n: n["start"])
    words, misses = [], []
    for ln in lyr:
        for w in str(ln["text"]).lower().split():
            words.append ((float(ln["beat"]), w))
    # align: each word claims the nearest melody note at/after its beat
    ds_notes, used = [], set()
    for beat, w in words:
        cand = next((i for i, n in enumerate(notes) if i not in used and n["start"] >= beat - 0.26), None)
        if cand is None:
            continue
        used.add(cand)
        n = notes[cand]
        ph = table.get(w)
        if ph is None:
            misses.append(w)
            ph = ["SP"]
        ds_notes.append({"word": w, "ph": ph, "midi": n["pitch"],
                         "start_s": round(n["start"] * spb, 4),
                         "dur_s": round(max(0.08, n["len"] * spb), 4)})
    ds = {"lang": "en", "singer": manifest().get("name", DEFAULT_BANK),
          "attribution": attribution(),
          "bpm": song.get("bpm"), "notes": ds_notes}
    out = os.path.join(ROOT, "songs", f"{song_name}.ds")
    json.dump(ds, open(out, "w"), indent=1)
    print(f"{out}: {len(ds_notes)} sung notes; {len(set(misses))} words missing from dsdict-en "
          f"(need g2p fallback): {sorted(set(misses))[:10]}")

VOWELS = set("aa ae ah ao aw ax ay eh er ey ih iy ow oy uh uw".split())

def load_word_dict():
    """word -> bank phonemes: CMUdict ARPAbet (stress stripped) -> dsdict-en mapping."""
    import cmudict, yaml
    dsd = yaml.safe_load(open(assets()["dsdict_en"]))
    ph_map = {}
    for e in dsd.get("entries", []):
        g = str(e["grapheme"]).lower()
        ph_map[g] = [p.split("/")[-1] for p in e["phonemes"]]   # en/ay -> ay
    cmu = cmudict.dict()

    # last-resort letter rules: crude, but slang/adlibs get SUNG instead of skipped
    DIGRAPHS = [("tch", ["ch"]), ("igh", ["ay"]), ("th", ["th"]), ("sh", ["sh"]),
                ("ch", ["ch"]), ("ph", ["f"]), ("ck", ["k"]), ("ng", ["ng"]),
                ("oo", ["uw"]), ("ee", ["iy"]), ("ea", ["iy"]), ("ay", ["ey"]),
                ("ai", ["ey"]), ("ou", ["aw"]), ("ow", ["aw"]), ("oy", ["oy"]),
                ("qu", ["k", "w"])]
    LETTERS = {"a": ["ae"], "b": ["b"], "c": ["k"], "d": ["d"], "e": ["eh"], "f": ["f"],
               "g": ["g"], "h": ["hh"], "i": ["ih"], "j": ["jh"], "k": ["k"], "l": ["l"],
               "m": ["m"], "n": ["n"], "o": ["aa"], "p": ["p"], "r": ["r"], "s": ["s"],
               "t": ["t"], "u": ["ah"], "v": ["v"], "w": ["w"], "x": ["k", "s"],
               "y": ["y"], "z": ["z"]}
    def letters_to_phs(w):
        out, i = [], 0
        while i < len(w):
            for d, phs in DIGRAPHS:
                if w.startswith(d, i):
                    out.extend(phs); i += len(d); break
            else:
                out.extend(LETTERS.get(w[i], [])); i += 1
        if out and w.endswith("e") and len(w) > 2 and out[-1] == "eh":
            out.pop()                              # silent final e
        return out or ["ah"]

    class D:
        def lookup(self, w):
            prons = cmu.get(w)
            if not prons:
                return None
            out = []
            for p in prons[0]:
                base = "".join(c for c in p.lower() if not c.isdigit())
                mapped = ph_map.get(base)
                if mapped is None:
                    return None
                out.extend(mapped)
            return out
        def get(self, w):
            w = w.strip(".,!?'\"()")
            hit = self.lookup(w)
            if hit: return hit
            for v in (w + "g" if w.endswith("in") else None,   # vibin -> vibing
                      w.replace("'", ""), w.rstrip("hs"),      # yuhh -> yu, comin' variants
                      w[:-1] if len(w) > 2 and w[-1] == w[-2] else None):
                if v:
                    hit = self.lookup(v)
                    if hit: return hit
            phs = letters_to_phs(w)                # rule-based last resort: always sings
            return [p for p in phs if p in ph_map and ph_map[p]] and \
                   [q for p in phs for q in ph_map.get(p, [])] or None
    return D()

HUM_SYL = {"laa": ["l", "aa"], "ooh": ["uw"], "ah": ["aa"], "mmm": ["m"],
           "naa": ["n", "aa"], "doo": ["d", "uw"], "ey": ["ey"]}

def hum(song_name, track_name, syllable="laa", embed="standard"):
    require_bank()
    """Topline HUM: sing a neutral syllable on every note of a melody track —
    an instant wordless vocal hook for any instrumental (deterministic; the
    user swaps in real lyrics later). Writes lyrics[] then renders."""
    phs = HUM_SYL.get(syllable, HUM_SYL["laa"])
    tok = "@" + "+".join(phs)
    sp = os.path.join(ROOT, "songs", f"{song_name}.json")
    song = json.load(open(sp))
    tr = next((t for t in song["tracks"] if t.get("name") == track_name), None)
    if tr is None or not tr.get("notes"):
        return print(f"no melody notes on '{track_name}'")
    song["lyrics"] = [{"beat": float(n["start"]), "text": tok} for n in sorted(tr["notes"], key=lambda n: n["start"])]
    json.dump(song, open(sp, "w"), indent=1)
    print(f"[hum] {len(song['lyrics'])} '{syllable}' syllables over {track_name}")
    render(song_name, track_name, embed)

def render(song_name, track_name, embed="standard", steps=30):
    require_bank()
    """lyrics + melody -> Gahata Meiji sings -> songs/<song>_vocal.wav -> vocals track."""
    _cuda_preload()   # BEFORE the import: the GPU wheel dlopens libcudart at
    import numpy as np, onnxruntime as ort   # import time, not session time
    cuda = (not os.environ.get("SOTADAW_SING_CPU")
            and "CUDAExecutionProvider" in ort.get_available_providers())
    # queue concurrent renders + skip (not silently die) when RAM is short.
    # CUDA keeps the weights in VRAM: the system-RAM floor drops (measured
    # 2026-07-09: GPU run fits under 2.1GB free; the CPU load needs ~3GB).
    _sing_gate(need_gb=1.5 if cuda else 3.0)
    song_path = os.path.join(ROOT, "songs", f"{song_name}.json")
    song = json.load(open(song_path))
    lyr = song.get("lyrics", [])
    tr = next((t for t in song["tracks"] if t.get("name") == track_name), None)
    if not lyr or tr is None or not tr.get("notes"):
        return print("need lyrics[] and a melody track")
    wdict = load_word_dict()
    ph_ids = json.load(open(os.path.join(BANK, "files", "phonemes.json")))
    lang_id = json.load(open(os.path.join(BANK, "files", "languages.json")))["en"]
    spb = 60.0 / float(song.get("bpm", 120))
    SR, HOP = 44100, 512
    spf = HOP / SR

    # word/note alignment. A lyric entry may set "melisma": N — its LAST word claims
    # its note plus the next N notes (one vowel riding a pitch run: actual singing).
    notes = sorted(tr["notes"], key=lambda n: n["start"])
    words = []
    for l in lyr:
        ws = str(l["text"]).lower().split()
        for wi, w in enumerate(ws):
            words.append((float(l["beat"]), w,
                          int(l.get("melisma", 0)) if wi == len(ws) - 1 else 0))
    events, used, misses = [], set(), []   # (start_s, total_dur_s, spans[(s,d,midi)], phs, word)
    for beat, w, mel in words:
        i = next((i for i, n in enumerate(notes) if i not in used and n["start"] >= beat - 0.26), None)
        if i is None: continue
        used.add(i)
        w0 = w.strip(".,!?'\"()")
        phs = w0[1:].split("+") if w0.startswith("@") else wdict.get(w0)   # @l+aa = literal phonemes (hum)
        if phs is None: misses.append(w); continue
        span_notes = [notes[i]]
        for _ in range(max(0, mel)):       # claim the melisma run
            j = next((j for j, n in enumerate(notes)
                      if j not in used and n["start"] >= span_notes[-1]["start"]), None)
            if j is None: break
            used.add(j); span_notes.append(notes[j])
        spans = [(n["start"] * spb, max(0.08, n["len"] * spb), n["pitch"]) for n in span_notes]
        total = max(0.1, spans[-1][0] + spans[-1][1] - spans[0][0])
        events.append((spans[0][0], total, spans, phs, w))
    if not events:
        return print(f"no singable words aligned (missing from dict: {sorted(set(misses))[:8]})")
    events.sort()

    # THE CHUNK LAW (2026-07-09): the acoustic model's attention is O(F^2) in
    # frames — a whole imported song in ONE feed is a multi-GB tensor that
    # earlyoom TERMs (proven live: 410s = ~35K frames ~= 5GB, killed twice).
    # Sing PHRASE WINDOWS instead: split at breath gaps (>0.55s) once a window
    # exceeds ~40s, synth each, place at its absolute offset. Peak RAM stays
    # ~model-load; the quadratic cost collapses (10 windows ~= 10x faster CPU).
    # W100: default 15 (max window ~24s at the 1.6 cap) — the vocoder's
    # measured survival size on an 8GB-available box; 40s windows OOM'd
    # twice live. Bigger boxes raise SOTADAW_SING_CHUNK_S.
    WIN = float(os.environ.get("SOTADAW_SING_CHUNK_S", "15"))
    groups, cur = [], []
    for ev in events:
        if cur:
            gap = ev[0] - (cur[-1][0] + cur[-1][1])
            span = ev[0] - cur[0][0]
            # W100 AUTO-CHUNK: dense chants (no 0.55s breath for minutes)
            # used to ride to 3xWIN and OOM the vocoder (gospel, live).
            # Windows now force-split at ANY note boundary past 1.25xWIN —
            # the knob stays for tuning but the OOM class is closed at
            # default settings.
            if ((gap > 0.55 and span > WIN) or (gap > 0.02 and span > 1.25 * WIN)
                    or span > 1.6 * WIN):
                groups.append(cur); cur = []
        cur.append(ev)
    if cur:
        groups.append(cur)

    # phoneme sequence with SP gaps; durations in frames. TOKENS carry text timing;
    # the f0 curve is built separately from the NOTE spans (so one vowel can ride a
    # melisma pitch run — performance and text are different axes).
    toks, langs, durs = [], [], []
    def push(tok, frames):
        toks.append(ph_ids[tok]); langs.append(0 if tok in ("SP", "AP") else lang_id)
        durs.append(max(1, int(round(frames))))

    def push_en(p, frames):
        # The bank splits its inventory: language phonemes live as "en/<p>"
        # but hh/wh/cl are GLOBAL bare tokens (like AP/SP). cmudict + the
        # letter fallback emit hh freely, so a blind "en/"+p KeyError'd every
        # h-word ("heart", "high") and killed the whole take.
        if "en/" + p in ph_ids:
            toks.append(ph_ids["en/" + p]); langs.append(lang_id)
        elif p in ph_ids:
            toks.append(ph_ids[p]); langs.append(0)
        else:                        # never lose the take to one phoneme
            print(f"[sing] bank has no '{p}' -> singing 'ah'")
            toks.append(ph_ids["en/ah"]); langs.append(lang_id)
        durs.append(max(1, int(round(frames))))
    # voice can be a single embed name OR a blend "hunter:0.6,lilith:0.4" — spk
    # embeds are raw float32 vectors, so weighted mixing mints new timbres free
    def load_emb(name):
        return np.fromfile(os.path.join(BANK, "configs", "embeds", f"{name}.emb"),
                           dtype=np.float32)[:384]
    if "," in embed or ":" in embed:
        emb = np.zeros(384, np.float32)
        total = 0.0
        for part in embed.split(","):
            n, _, w = part.strip().partition(":")
            w = float(w or 1.0)
            emb += load_emb(n) * w
            total += w
        emb /= max(total, 1e-6)
    else:
        emb = load_emb(embed)
    prov = [("CUDAExecutionProvider", {}), "CPUExecutionProvider"] if cuda \
        else ["CPUExecutionProvider"]
    import time as _t; t0 = _t.time()
    try:
        ac = ort.InferenceSession(assets()["acoustic"], providers=prov)
        voc = ort.InferenceSession(assets()["vocoder"], providers=prov)
    except Exception as ce:
        # VRAM contention (the ZPE daemon can hold ~5.1/6GB) or a CPU-only
        # onnxruntime — the voice must land either way.
        if prov[0] == "CPUExecutionProvider":
            raise
        print(f"[sing] CUDA session failed ({type(ce).__name__}) -> CPU",
              flush=True)
        prov = ["CPUExecutionProvider"]
        ac = ort.InferenceSession(assets()["acoustic"], providers=prov)
        voc = ort.InferenceSession(assets()["vocoder"], providers=prov)
    print(f"[sing] engine: {ac.get_providers()[0]}", flush=True)

    end_s = max(s + d for s, d, _, _, _ in events) + 1.0
    buf = np.zeros(int(end_s * SR) + SR, dtype=np.float32)
    n_toks = n_frames = 0
    # W100 SELF-HEALING WINDOWS: a queue instead of a fixed loop — a window
    # that OOMs splits at its midpoint note and both halves re-enter the
    # queue (depth-capped by minimum length). The guard's actionable exit
    # remains only for the 1-note-window floor.
    queue = list(groups)
    total_windows = len(queue)
    gi = -1
    while queue:
        grp = queue.pop(0)
        gi += 1
        base = max(0.0, grp[0][0] - 0.35)
        toks, langs, durs = [], [], []           # push/push_en see the rebind
        cursor = base
        if grp[0][0] - base >= 0.30:
            push("AP", (grp[0][0] - base) / spf)  # breathe into the phrase
            cursor = grp[0][0]
        for start, dur, spans, phs, w in grp:
            if start > cursor + 0.02:
                gap = start - cursor
                if gap > 0.55:                   # phrase gap: breathe in before the line (AP)
                    push("SP", (gap - 0.35) / spf)
                    push("AP", 0.35 / spf)
                else:
                    push("SP", gap / spf)
            lead = [p for p in phs[:1] if p not in VOWELS]  # leading consonant steals time
            t_lead = 0.06 if lead and len(phs) > 1 else 0.0
            rest = phs[1:] if t_lead else phs
            t_each = max(0.03, (dur - t_lead) / max(1, len(rest)))
            for p in (phs[:1] if t_lead else []):
                push_en(p, t_lead / spf)
            for p in rest:
                push_en(p, t_each / spf)
            cursor = start + dur
        push("SP", 0.4 / spf)

        F = sum(durs)
        # f0 from the note-span timeline (group-relative): gaps hold the
        # neighbor pitch; vibrato per span
        f0 = np.zeros(F, dtype=np.float32)
        gspans = sorted((s - base, d, m)
                        for _, _, spans, _, _ in grp for (s, d, m) in spans)
        last_midi = gspans[0][2] if gspans else 60
        f0[:] = 440.0 * 2 ** ((last_midi - 69) / 12.0)
        for s, d, m in gspans:
            a = max(0, min(F, int(round(s / spf))))
            b = max(a, min(F, int(round((s + d) / spf))))
            hz = 440.0 * 2 ** ((m - 69) / 12.0)
            f0[a:] = hz                          # hold through any following gap...
            t = (np.arange(b - a) * spf)
            vib = (t > 0.18) * np.sin(2 * np.pi * 5.5 * t) * 0.25
            f0[a:b] *= 2 ** (vib / 12.0 * 0.25)  # ...vibrato only inside the note
        # smooth transitions (1-pole portamento — melisma steps glide musically)
        for i in range(1, F):
            f0[i] = f0[i - 1] * 0.82 + f0[i] * 0.18

        feed = {
            "tokens": np.array([toks], dtype=np.int64),
            "languages": np.array([langs], dtype=np.int64),
            "durations": np.array([durs], dtype=np.int64),
            "f0": f0[None, :],
            "tension": np.zeros((1, F), np.float32),
            "gender": np.zeros((1, F), np.float32),
            "velocity": np.ones((1, F), np.float32),
            "spk_embed": np.tile(emb, (1, F, 1)).astype(np.float32),
            "depth": np.array(0.6, np.float32),
            "steps": np.array(steps, np.int64),
        }
        try:
            mel = ac.run(None, feed)[0]
            seg = voc.run(None, {"mel": mel, "f0": f0[None, :]})[0][0]
        except Exception as e:
            if len(grp) >= 2:
                # W100: self-heal — split at the midpoint note, re-queue
                mid = len(grp) // 2
                queue[:0] = [grp[:mid], grp[mid:]]
                total_windows += 1
                gi -= 1
                print(f"[sing] window OOM at {F * spf:.0f}s — self-split "
                      f"into {mid}+{len(grp) - mid} words, retrying", flush=True)
                continue
            # W99 THE PARTIAL-VOCAL GUARD: the 1-note floor — never ship a
            # half-sung take or die as a bare traceback.
            _skip(f"sing window failed at the 1-note floor "
                  f"({type(e).__name__}: memory pressure) — free RAM and retry")
        a0 = int(round(base * SR))
        b0 = min(len(buf), a0 + len(seg))
        buf[a0:b0] += seg[:b0 - a0]              # windows only overlap in near-
        n_toks += len(toks); n_frames += F       # silent SP/AP tails: sum is clean
        print(f"[sing] window {gi + 1}/{total_windows}: {len(grp)} words, "
              f"{F} frames ({F * spf:.1f}s) @ {base:.1f}s", flush=True)
    from scipy.io import wavfile
    out = os.path.join(ROOT, "songs", f"{song_name}_vocal.wav")
    # THE LIVE-APP STOMP LAW (crash court 2026-07-12 14:38, Chezy live): the
    # UI memory-maps this wav while playing; an IN-PLACE rewrite truncates
    # the mapping under the audio thread — SEGV in MemoryMappedWavReader::
    # readSamples (symbolized). tmp + os.replace = a NEW inode; the engine's
    # map keeps the old bytes alive until it reloads. Same law as _awrite.
    _tmp_wav = out + ".w~.wav"
    wavfile.write(_tmp_wav, SR, (np.clip(buf, -1, 1) * 32767).astype(np.int16))
    os.replace(_tmp_wav, out)

    # land it in the song as a real (replaceable) audio track. On IMPORTED
    # songs 'vocals' is the muted stem REFERENCE (the record's own vocal) —
    # never clobber it: the import pre-creates 'vocals_sung' and the render
    # lands there. Non-import songs keep the classic 'vocals' landing.
    # RELOAD FRESH: synthesis takes minutes (detached on imports) — landing
    # on the copy read before it would clobber every edit made since.
    _sing_release()   # synthesis done — the child adlib sing needs its turn
    song = json.load(open(song_path))
    vt = next((t for t in song["tracks"] if t.get("name") == "vocals_sung"), None)
    if vt is None:
        cand = next((t for t in song["tracks"] if t.get("name") == "vocals"), None)
        if cand is not None and any("_stems/" in str(c.get("file", ""))
                                    for c in (cand.get("audioClips") or [])):
            # 'vocals' holds the RECORD's own stem — never land on it; mint
            # the vocals_sung lane the import would have pre-created.
            # dr19 (2026-07-12): this mint landed with ZERO fx while the
            # fresh-song path always carried comp+delay(+verb send) — the
            # import re-sing was the driest vocal in the product. Same chain.
            vt = {"name": "vocals_sung",
                  "source": {"kind": "audio", "id": "vocals_sung"},
                  "gainDb": -1.5, "notes": [],
                  "fx": [{"id": "fx_deess", "params": {"freq": 5500, "thresh": -32,
                                                        "ratio": 4}},   # dr19: FIRST
                         {"type": "comp", "params": {"threshold": -18, "ratio": 2.5,
                                                     "attack": 8, "release": 120,
                                                     "outputDb": 3}},
                         {"id": "fx_delay", "params": {"time": 0.28, "feedback": 0.22,
                                                       "mix": 0.12}}]}
            if any(b.get("id") == "verb" for b in song.get("buses", [])):
                vt["sends"] = [{"bus": "verb", "gainDb": -14}]
            song["tracks"].append(vt)
        else:
            vt = cand
    if vt is None:
        _vt_minted = True                       # W102: first landing (see below)
        vt = {"name": "vocals", "source": {"kind": "audio", "id": "vocals"}, "gainDb": -4.0, "notes": [],
              "fx": [{"id": "fx_deess", "params": {"freq": 5500, "thresh": -32,
                                                    "ratio": 4}},   # dr19: FIRST
                     {"type": "comp", "params": {"threshold": -18, "ratio": 2.5,
                                                 "attack": 8, "release": 120, "outputDb": 3}},
                     {"id": "fx_delay", "params": {"time": 0.28, "feedback": 0.22, "mix": 0.12}}]}
        if any(b.get("id") == "verb" for b in song.get("buses", [])):
            vt["sends"] = [{"bus": "verb", "gainDb": -14}]
        song["tracks"].append(vt)
    vt["audioClips"] = [{"file": os.path.relpath(out, ROOT), "startBeat": 0}]
    vt["comment"] = "voice: " + attribution()
    # THE LEVEL LAW (A2M byte-par, 2026-07-10): the sung vocal lands AT THE
    # RECORD'S OWN VOCAL LEVEL, not at a house trim. Forensics measured the
    # old -1.5 default +5.9dB over the real vocal — the loudest lane in the
    # product was the synthetic one ("VOCALS AREN'T EVEN CLOSE"). Match the
    # sung wav's LUFS to the stem's LUFS; non-import songs keep their default.
    try:
        stem_ref = next((c.get("file") for t in song["tracks"]
                         if t.get("name") == "vocals"
                         for c in (t.get("audioClips") or [])
                         if "_stems/" in str(c.get("file", ""))), None)
        if stem_ref and vt.get("name") == "vocals_sung":
            import pyloudnorm
            from scipy.io import wavfile as _wf

            def _lufs(p):
                sr_, d = _wf.read(p if os.path.isabs(p)
                                  else os.path.join(ROOT, p))
                if d.dtype.kind == "i":
                    d = d.astype(np.float64) / float(1 << (8 * d.itemsize - 1))
                if d.ndim == 2:
                    d = d.mean(axis=1)
                v = pyloudnorm.Meter(sr_).integrated_loudness(d)
                return v if np.isfinite(v) else None
            l_stem, l_sung = _lufs(stem_ref), _lufs(out)
            if l_stem is not None and l_sung is not None and l_stem > -55:
                vt["gainDb"] = round(max(-15.0, min(6.0, l_stem - l_sung)), 2)
                print(f"[sing] LEVEL LAW: sung vocal {l_sung:.1f} LUFS, record's "
                      f"vocal {l_stem:.1f} -> lane gain {vt['gainDb']:+.1f}dB",
                      flush=True)
    except Exception as le:
        print(f"[sing] level match skipped ({type(le).__name__}: {le})", flush=True)
    if vt.get("name") == "vocals_sung":
        for t in song["tracks"]:               # THE LANDING OWNS THE SWAP: the
            if t.get("name") == "vocals_sketch":   # sung lane carries the voice,
                t["muted"] = True              # the melody stays the edit surface
        # TRUTH OUTRANKS SYNTH (A2M byte-par): when the record's own re-synthesized
        # vocal ('vocals_true') exists or is on its way (SOTADAW_SING_MUTED=1 from
        # the import's finisher chain), the Meiji take lands MUTED — an alt voice,
        # never the default sound of an imported record.
        if (os.environ.get("SOTADAW_SING_MUTED") == "1"
                or any(t.get("name") == "vocals_true" for t in song["tracks"])):
            vt["muted"] = True
    # W102 THE VOICE HANDOVER: when the sung melody's own voice is a VOX
    # PROXY (formant_vox — rnb/doo_wop/bounce leads), two voices fight.
    # The real voice takes the topline; the proxy eases -6dB into a
    # whisper double (records stack exactly this). Real instruments keep
    # their level (voice + instrument = the classic double). Idempotence
    # keys on FIRST LANDING (the vocals lane was minted this run) — a
    # custom track field would drop through the UI's serializer and
    # re-arm the duck on every re-sing (the slow-rot class).
    _mel = next((t for t in song["tracks"] if t.get("name") == track_name), None)
    if (locals().get("_vt_minted") and _mel is not None
            and (_mel.get("source") or {}).get("id") == "formant_vox"):
        _mel["gainDb"] = round(float(_mel.get("gainDb", -9.0)) - 6.0, 2)
        print(f"[sing] VOICE HANDOVER: '{track_name}' is a vox proxy "
              f"(formant_vox) — eased to {_mel['gainDb']}dB whisper double",
              flush=True)
    # THE VOCAL DOUBLE (ledger dr21, 2026-07-12): pro hooks are DOUBLED — the
    # same take layered under itself. Zero new synthesis: the double track
    # re-clips the SAME rendered wav onto the HOOK spans only (chorus/drop/
    # hook/theme), lagged 0.02 beats (the ADT feel), -6 dB, centered
    # (mono-safe thickening). Constant-bpm songs only (tempoMap would break
    # the offsetSec math — fail open); verses stay single (the contrast IS
    # the lift). SOTADAW_VOCAL_DOUBLE=0 kills. Idempotent by track name.
    try:
        _secs = song.get("sections") or []
        _bpm = float(song.get("bpm") or 0)
        _hooks = []
        for _i, _s in enumerate(_secs):
            if str(_s.get("name", "")).rstrip("0123456789") in ("chorus", "drop", "hook", "theme"):
                _b0 = float(_s.get("startBar", 0)) * 4.0
                _b1 = (float(_secs[_i + 1].get("startBar", 0)) * 4.0
                       if _i + 1 < len(_secs)
                       else float(song.get("lengthBars", 0)) * 4.0)
                if _b1 > _b0:
                    _hooks.append((_b0, _b1))
        if (_hooks and _bpm > 0 and not song.get("tempoMap")
                and os.environ.get("SOTADAW_VOCAL_DOUBLE", "1") != "0"
                and not any(t.get("name") == f"{vt['name']}_dbl"
                            for t in song["tracks"])):
            _spb = 60.0 / _bpm
            _dbl = {"name": f"{vt['name']}_dbl",
                    "source": {"kind": "audio", "id": f"{vt['name']}_dbl"},
                    "gainDb": round(float(vt.get("gainDb", -4.0)) - 6.0, 2),
                    "notes": [], "muted": bool(vt.get("muted")),
                    "comment": "hook double of the sung take (same wav, re-clipped)",
                    "audioClips": [{"file": os.path.relpath(out, ROOT),
                                    "startBeat": round(_b0 + 0.02, 4),
                                    "lengthBeats": round(_b1 - _b0, 4),
                                    "offsetSec": round(_b0 * _spb, 4)}
                                   for _b0, _b1 in _hooks]}
            song["tracks"].append(_dbl)
            print(f"[sing] THE VOCAL DOUBLE: {len(_hooks)} hook span(s) doubled "
                  f"at {_dbl['gainDb']}dB (same take, 0.02-beat lag)", flush=True)
    except Exception as _de:
        print(f"[sing] vocal double skipped ({type(_de).__name__}: {_de})", flush=True)
    # THE ADLIB RAIL (ledger dr21 tail, 2026-07-12): records ANSWER their
    # hooks — 1-word interjections in the gaps ("yeah", "oh", the echo).
    # A child sing renders ONLY the answers on the same timeline (silence
    # between phrases costs nothing — phrase windows), landing an adlibs
    # track at -8 dB panned right. Words takes only, constant bpm only,
    # never recursive (SOTADAW_ADLIB_CHILD), idempotent by track name.
    # SOTADAW_ADLIBS=0 kills. Measured cost: ~8s per answer pair.
    try:
        import subprocess as _sp
        _base = os.path.splitext(os.path.basename(song_path))[0]
        if (os.environ.get("SOTADAW_ADLIBS", "1") != "0"
                and not os.environ.get("SOTADAW_ADLIB_CHILD")
                and song.get("lyrics") and not song.get("tempoMap")
                and not _base.startswith("_adlib_")
                and not any(t.get("name") == f"{vt['name']}_adlibs"
                            for t in song["tracks"])):
            _gaps = find_hook_gaps(song, track_name,
                                   seed=len(song.get("lyrics") or []))[:6]
            if _gaps:
                _aw = ["yeah", "oh", "hey", "uh"]
                _tmp = f"_adlib_{_base}"
                _tsong = {"bpm": song.get("bpm"), "lengthBars": song.get("lengthBars"),
                          "key": song.get("key", "A minor"),
                          "tracks": [{"name": "lead",
                                      "source": {"kind": "faust", "id": "pluck2"},
                                      "gainDb": -60.0,
                                      "notes": [{"start": g0, "len": gl,
                                                 "pitch": pp, "vel": 0.72}
                                                for g0, gl, pp in _gaps]}],
                          "lyrics": [{"beat": g0, "text": _aw[_i % len(_aw)]}
                                     for _i, (g0, gl, pp) in enumerate(_gaps)]}
                _tj = os.path.join(ROOT, "songs", f"{_tmp}.json")
                json.dump(_tsong, open(_tj, "w"), indent=1)
                _env = dict(os.environ)
                _env["SOTADAW_ADLIB_CHILD"] = "1"
                _rr = _sp.run([sys.executable, os.path.abspath(__file__),
                               "render", _tmp, "lead"],
                              capture_output=True, text=True, timeout=900, env=_env)
                _aw_wav = os.path.join(ROOT, "songs", f"{_tmp}_vocal.wav")
                if not os.path.exists(_aw_wav):
                    print("[sing] adlib child produced no wav: "
                          + (_rr.stdout + _rr.stderr).strip()[-160:], flush=True)
                if os.path.exists(_aw_wav):
                    _dest = os.path.join(ROOT, "songs", f"{_base}_adlibs.wav")
                    os.replace(_aw_wav, _dest)
                    song["tracks"].append({
                        "name": f"{vt['name']}_adlibs",
                        "source": {"kind": "audio", "id": f"{vt['name']}_adlibs"},
                        "gainDb": round(float(vt.get("gainDb", -4.0)) - 8.0, 2),
                        "pan": 0.3, "notes": [], "muted": bool(vt.get("muted")),
                        "comment": "hook-gap answers (voice: " + attribution() + ")",
                        "audioClips": [{"file": os.path.relpath(_dest, ROOT),
                                        "startBeat": 0}]})
                    print(f"[sing] THE ADLIB RAIL: {len(_gaps)} answer(s) in the "
                          f"hook gaps at {round(float(vt.get('gainDb', -4.0)) - 8.0, 2)}dB",
                          flush=True)
                import shutil as _sh
                for _pp in (_tj, os.path.join(ROOT, "songs", f"{_tmp}.wav")):
                    if os.path.exists(_pp):
                        os.remove(_pp)
                _fdir = os.path.join(ROOT, "songs", f"{_tmp}_vocals")
                if os.path.isdir(_fdir):
                    _sh.rmtree(_fdir)
    except Exception as _ae:
        print(f"[sing] adlib rail skipped ({type(_ae).__name__}: {_ae})", flush=True)
    json.dump(song, open(song_path, "w"), indent=1)
    try:
        # THE FOLLOWING VOICE: bind the sung take to its melody track — when
        # the user edits those notes, the sidecar watcher re-runs THIS argv
        # (sing owns its own landing) so the take always sings the MIDI.
        sys.path.insert(0, os.path.join(ROOT, "tools"))
        import vocal_follow as _vf
        _vf.bind(os.path.splitext(os.path.basename(song_path))[0], track_name,
                 os.path.relpath(out, ROOT), os.path.relpath(out, ROOT),
                 backend="sing",
                 argv=[sys.executable, os.path.abspath(sys.argv[0])] + sys.argv[1:])
        print("[sing] FOLLOWING VOICE: take bound to its melody - edit the "
              "MIDI and it re-sings", flush=True)
    except Exception as _fe:
        print(f"[sing] follow binding skipped ({type(_fe).__name__}: {_fe})",
              flush=True)
    print(f"SUNG {len(events)} words / {n_toks} phonemes / {n_frames} frames "
          f"({total_windows} phrase windows, {n_frames*spf:.1f}s sung) "
          f"in {_t.time()-t0:.0f}s -> {out} (+ 'vocals' track). "
          f"Voice: {attribution()}."
          + (f" Unsung words (not in dict): {sorted(set(misses))[:8]}" if misses else ""))

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "status":
        status()
    elif cmd == "ds" and len(sys.argv) >= 4:
        build_ds(sys.argv[2], sys.argv[3])
    elif cmd == "hum" and len(sys.argv) >= 4:
        hum(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "laa")
    elif cmd == "render" and len(sys.argv) >= 4:
        render(sys.argv[2], sys.argv[3],
               sys.argv[4] if len(sys.argv) > 4 else "standard")
