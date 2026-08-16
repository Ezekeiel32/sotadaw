#!/usr/bin/env python3
"""THE GOLD STANDARD BANK — real full-complexity music DNA as the bar to hold.

Chezy law (2026-07-13, verbatim intent): "feed REAL fully complex music notes DNA
and sounds, generalised — not as skeleton but as EXAMPLE OF THE STANDARD the agent
needs to hold by, with the canonical prompt for context retrieval. Mastering
standard also utmost, with full examples in DNA."

Before this bank, the prompt lane carried LAWS ONLY (prose techniques + mix
numbers); the KG's real note DNA fed the zero-token generator and never a prompt.
Big models composed at the bar anyway; small models drifted thin and off-key.
Few-shot exemplars at full complexity are the lever that closes that gap.

  library/gold/<genre>.json   one banked exemplar: window of REAL notes (vel/len),
                              voiced chords, per-track stats, fx, buses, automation,
                              master chain + MEASURED numbers. Machine-checkable.
  library/gold/_index.json    every KG genre -> parent, common_key, bpm window,
                              mastering targets (KG needed at build time ONLY).

  gold_bank.py seed             bank the corpus: crate loops + eval winners + index
  gold_bank.py ingest-accepts   bank qualifying ACCEPTED takes (the taste circle's
                                note-DNA leg; auto-run from kg_ingest_telemetry)
  gold_bank.py block <genre>    print THE STANDARD block a session would carry
  gold_bank.py verify           bank invariants (gold_battery drives this too)

Retrieval: daw_mcp start_session / get_skill attach render_block(genre) beside the
genre skill. Runtime is KG-FREE (bank + index are plain files; the pocket falls
back to agent/dna_cache.json through loop_gen.genre_dna).

QUALITY GATES are the whole point: off-key, thin, or robotic takes NEVER bank —
the standard only rises (replacement needs a strictly better composite score).
"""
import json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
GOLD = os.environ.get("SOTADAW_GOLD_DIR") or os.path.join(ROOT, "library", "gold")
SONGS = os.path.join(ROOT, "songs")
BLOCK_CAP = 4400          # chars; the session diet fought for its budget — respect it

# ---------- keys and spelling ----------
NAT = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
LETTERS = "CDEFGAB"
MODES = {                  # intervals from tonic; "allow" = accepted non-scale tones
    "major":      ([0, 2, 4, 5, 7, 9, 11], set()),
    "minor":      ([0, 2, 3, 5, 7, 8, 10], {11}),      # raised 7th at cadences
    "dorian":     ([0, 2, 3, 5, 7, 9, 10], set()),
    "phrygian":   ([0, 1, 3, 5, 7, 8, 10], set()),
    "lydian":     ([0, 2, 4, 6, 7, 9, 11], set()),
    "mixolydian": ([0, 2, 4, 5, 7, 9, 10], set()),
    "harmonic":   ([0, 2, 3, 5, 7, 8, 11], set()),
    "hijaz":      ([0, 1, 4, 5, 7, 8, 10], set()),      # phrygian dominant
    "blues":      ([0, 3, 5, 6, 7, 10], {4}),           # both thirds live here
}
SHARP_N = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
FLAT_N = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]

def parse_key(key_str):
    """'D minor' / 'Ab major' / 'A minor (Hijaz color)' -> dict or None."""
    m = re.match(r"\s*([A-G])([#b]?)", str(key_str or ""))
    if not m:
        return None
    tonic_pc = (NAT[m.group(1)] + {"#": 1, "b": -1, "": 0}[m.group(2)]) % 12
    low = str(key_str).lower()
    mode = next((w for w in ("hijaz", "blues", "dorian", "phrygian", "lydian",
                             "mixolydian", "harmonic") if w in low),
                "minor" if ("min" in low or low.rstrip().endswith("m")) else "major")
    ivs, allow = MODES[mode]
    scale = {(tonic_pc + i) % 12 for i in ivs}
    names = spell_scale(m.group(1) + m.group(2), ivs)
    return {"tonic_pc": tonic_pc, "mode": mode, "scale_pcs": sorted(scale),
            "allowed_pcs": sorted(scale | {(tonic_pc + a) % 12 for a in allow}),
            "scale_names": names, "flats": any("b" in n for n in names)}

def spell_scale(tonic_name, ivs):
    if len(ivs) != 7:                                   # hexatonic (blues): flat map
        t = (NAT[tonic_name[0]] + {"#": 1, "b": -1}.get(tonic_name[1:2], 0)) % 12
        return [FLAT_N[(t + i) % 12] for i in ivs]
    li, acc = LETTERS.index(tonic_name[0]), {"#": 1, "b": -1}.get(tonic_name[1:2], 0)
    t_pc, out = NAT[tonic_name[0]] + acc, []
    for i, iv in enumerate(ivs):
        letter = LETTERS[(li + i) % 7]
        d = ((t_pc + iv) - NAT[letter]) % 12
        d = d - 12 if d > 6 else d
        out.append(letter + {0: "", 1: "#", 2: "##", -1: "b", -2: "bb"}.get(d, "?"))
    return out

def note_name(pitch, flats=False):
    return (FLAT_N if flats else SHARP_N)[pitch % 12] + str(pitch // 12 - 1)

# ---------- roles and chords ----------
DRUMISH = {"kick", "kicks", "snare", "snares", "clap", "claps", "hat", "hats", "hh",
           "shaker", "perc", "percs", "percussion", "drums", "drum", "cym", "cymbal",
           "cymbals", "ride", "tom", "toms", "rim", "rims", "crash", "clave",
           "cowbell", "conga", "bongo", "tamb", "tambourine", "breaks", "break"}
DRUM_VOICES = ("kick", "snare", "hat", "openhat", "clap", "rim", "ride", "tom",
               "cymbal", "shaker", "crash", "clave", "cowbell", "conga", "perc")

def track_role(t):
    """'drums' tracks are exempt from the key law (kit pitches = drum map)."""
    name = re.sub(r"[^a-z]", "", str(t.get("name", "")).lower())
    src = t.get("source") or {}
    voice = str(src.get("id") or "").lower()
    base = voice[5:] if voice.startswith("vst3:") else voice
    if any(w in name for w in DRUMISH if len(w) > 2) or name in DRUMISH:
        return "drums"
    if any(base == d or base.startswith(d + "_") for d in DRUM_VOICES):
        return "drums"
    if src.get("kind") == "kit" and not any(w in name for w in
                                            ("bass", "808", "keys", "piano", "lead")):
        return "drums"
    return "melodic"

CHORD_Q = [({0, 4, 7, 11, 2}, "maj9"), ({0, 3, 7, 10, 2}, "m9"), ({0, 4, 7, 10, 2}, "9"),
           ({0, 4, 7, 11}, "maj7"), ({0, 3, 7, 10}, "m7"), ({0, 4, 7, 10}, "7"),
           ({0, 3, 6, 10}, "m7b5"), ({0, 4, 7, 9}, "6"), ({0, 3, 7, 9}, "m6"),
           ({0, 4, 7, 2}, "add9"), ({0, 3, 7, 2}, "madd9"), ({0, 4, 7}, ""),
           ({0, 3, 7}, "m"), ({0, 3, 6}, "dim"), ({0, 4, 8}, "aug"),
           ({0, 5, 7}, "sus4"), ({0, 2, 7}, "sus2")]

def chord_name(pitches, flats=False):
    """Simultaneous pitches -> 'Dm7' (root sought across inversions) or None."""
    pcs = sorted({p % 12 for p in pitches})
    for root in pcs:
        rel = {(p - root) % 12 for p in pcs}
        for q, label in CHORD_Q:
            if rel == q:
                return (FLAT_N if flats else SHARP_N)[root] + label
    return None

# ---------- meter helpers (the ONE bar<->beat resolver) ----------
def _meter():
    import meter
    return meter

def _fmt(x):
    s = f"{round(float(x), 2):g}"
    return s[1:] if s.startswith("0.") else ("-" + s[2:] if s.startswith("-0.") else s)

def _vel(v):
    return "^" + _fmt(v)

# ---------- distill: song.json -> gold exemplar ----------
def _fx_sig(fxl):
    out = []
    for f in fxl or []:
        fid = f.get("id") or f.get("type") or "?"
        ps = f.get("params") or {}
        inner = ",".join(f"{k} {_fmt(v)}" for k, v in sorted(ps.items())
                         if isinstance(v, (int, float)))[:64]
        out.append(f"{fid}({inner})" if inner else str(fid))
    return out

def distill(song, genre, source, measured=None, mixtarget=None):
    """A song that PASSED the ears -> a compact machine-checkable exemplar.
    Returns (gold, why_rejected) — exactly one is None. Gates are strict on
    purpose: the bank teaches the standard, so junk must never enter it."""
    M = _meter()
    MT = M.song_meter(song)
    tracks = [t for t in song.get("tracks", []) if t.get("notes")]
    if len(tracks) < 3:
        return None, f"only {len(tracks)} note tracks (<3)"
    key = parse_key(song.get("key"))
    if key is None:
        return None, f"unparseable key {song.get('key')!r}"
    if any(w in genre for w in ("blues", "jazz", "funk", "soul", "rock")):
        # blue notes are the genre's grammar, not off-key drift (eval_blues at
        # 63% "in key" was CORRECT blues — the gate must know the family)
        t = key["tonic_pc"]
        key = dict(key, allowed_pcs=sorted(set(key["allowed_pcs"])
                                           | {(t + 3) % 12, (t + 6) % 12, (t + 10) % 12}))
    bpm = float(song.get("bpm") or 0)
    if not 40 <= bpm <= 220:
        return None, f"bpm {bpm} out of range"
    length_bars = int(song.get("lengthBars") or 8)
    total_notes = sum(len(t["notes"]) for t in tracks)
    if total_notes < 32:
        return None, f"{total_notes} notes total (<32) — too thin to be a standard"

    # per-track truth: role, in-key %, density, velocity variety
    gold_tracks, worst_key, melodic_seen = [], 1.0, False
    for t in tracks:
        role = track_role(t)
        notes = sorted(t["notes"], key=lambda n: (n["start"], n["pitch"]))
        pcs = [n["pitch"] % 12 for n in notes]
        in_key = (sum(1 for p in pcs if p in key["allowed_pcs"]) / len(pcs)) if pcs else 1.0
        if role == "melodic":
            melodic_seen = True
            worst_key = min(worst_key, in_key)
        vels = {round(n.get("vel", 1.0), 2) for n in notes}
        starts = {}
        for n in notes:
            starts.setdefault(round(n["start"], 3), []).append(n)
        chordal = sum(len(g) for g in starts.values() if len(g) >= 3) / len(notes)
        gold_tracks.append({
            "name": t.get("name", "?"), "role": role,
            "voice": (t.get("source") or {}).get("id")
                     or (t.get("source") or {}).get("kind") or "?",
            "gainDb": t.get("gainDb", 0), "pan": t.get("pan", 0),
            "fx": _fx_sig(t.get("fx")), "chordal": round(chordal, 2),
            "notes_per_bar": round(len(notes) / max(1.0, length_bars), 2),
            "vel_lo": min((n.get("vel", 1.0) for n in notes), default=1.0),
            "vel_hi": max((n.get("vel", 1.0) for n in notes), default=1.0),
            "vel_variety": len(vels), "in_key_pct": round(in_key, 3),
            "pitch_lo": min(n["pitch"] for n in notes),
            "pitch_hi": max(n["pitch"] for n in notes),
            "_notes": notes,
        })
    if not melodic_seen:
        return None, "no melodic track — a standard needs harmony to teach"
    if worst_key < 0.75:
        return None, f"melodic track only {worst_key:.0%} in key — OFF-KEY DNA never banks"
    if mixtarget and mixtarget.get("bpm_lo") and not (
            float(mixtarget["bpm_lo"]) * 0.8 <= bpm <= float(mixtarget["bpm_hi"]) * 1.2):
        return None, f"bpm {bpm} outside the genre's window {mixtarget['bpm_lo']}-{mixtarget['bpm_hi']}"

    # window = the densest W contiguous bars (arrangements bloom late; ties -> later)
    W = min(8, length_bars)
    counts = [0] * max(1, length_bars)
    for gt in gold_tracks:
        for n in gt["_notes"]:
            b = int(M.bar_at_q(MT, n["start"]))
            if 0 <= b < length_bars:
                counts[b] += 1
    best_s = 0
    for s in range(0, max(1, length_bars - W + 1)):
        if sum(counts[s:s + W]) >= sum(counts[best_s:best_s + W]):
            best_s = s
    win = {"startBar": best_s, "bars": W}

    for gt in gold_tracks:                       # bar-bucketed window notes + DNA text
        by_bar = {}
        for n in gt["_notes"]:
            b = int(M.bar_at_q(MT, n["start"]))
            if best_s <= b < best_s + W:
                by_bar.setdefault(b, []).append(n)
        gt["bar_counts"] = [len(by_bar.get(b, [])) for b in range(best_s, best_s + W)]
        show = 2 if gt["role"] == "drums" else (W if gt["chordal"] >= 0.5 else 4)
        lines = []
        for b in range(best_s, best_s + min(show, W)):
            ns = by_bar.get(b, [])
            if gt["chordal"] >= 0.5 and ns:      # chord track: voicings, not note soup
                groups = {}
                for n in ns:
                    groups.setdefault(round(n["start"], 3), []).append(n)
                cells = []
                for st in sorted(groups)[:4]:
                    g = groups[st]
                    ps = sorted(n["pitch"] for n in g)
                    nm = chord_name(ps, key["flats"]) if len(ps) >= 3 else None
                    stack = "".join(note_name(p, key["flats"]) for p in ps[:5])
                    beat = _fmt(st - M.bar_start_q(MT, b))
                    cells.append(f"@{beat} {nm}={stack}" if nm else f"@{beat} {stack}")
                lines.append(f"b{b} " + " ".join(cells))
            else:
                toks = [f"{note_name(n['pitch'], key['flats'])}"
                        f"@{_fmt(n['start'] - M.bar_start_q(MT, b))}"
                        f"+{_fmt(n['len'])}{_vel(n.get('vel', 1))}" for n in ns[:10]]
                if len(ns) > 10:
                    toks.append(f"+{len(ns) - 10} more")
                lines.append(f"b{b} " + " ".join(toks) if toks else f"b{b} (rest)")
        gt["dna"] = " | ".join(lines)
        del gt["_notes"]

    autol = []
    for a in song.get("automation", []) or []:
        pts = a.get("points") or []
        if not pts:
            continue
        b0, b1 = (int(M.bar_at_q(MT, pts[0].get("beat", 0))),
                  int(M.bar_at_q(MT, pts[-1].get("beat", 0))))
        curves = [p.get("curve", 0) for p in pts]
        shape = ("late-bloom" if sum(curves) > 0 else
                 "early-jump" if sum(curves) < 0 else "linear")
        autol.append(f"{a.get('target')} {_fmt(pts[0].get('v', 0))}->"
                     f"{_fmt(pts[-1].get('v', 0))} bars {b0}-{b1} ({shape})")
    buses = [f"{b.get('id') or b.get('name')}: " + " -> ".join(_fx_sig(b.get("fx")))
             for b in song.get("buses") or [] if b]
    sections = [f"{s.get('name', '?')}@{s.get('startBar', s.get('bar', '?'))}"
                for s in song.get("sections") or []]

    mel = [gt for gt in gold_tracks if gt["role"] == "melodic"]
    score = round(
        0.5 * (sum(gt["in_key_pct"] for gt in mel) / len(mel))
        + 0.2 * min(1.0, sum(gt["notes_per_bar"] for gt in mel) / len(mel) / 3.0)
        + 0.1 * bool(sections) + 0.1 * bool(autol) + 0.05 * bool(buses)
        + 0.05 * min(1.0, sum(gt["vel_variety"] for gt in gold_tracks)
                     / (4.0 * len(gold_tracks))), 3)

    return {"genre": genre, "source": source, "score": score,
            "bpm": bpm, "key": song.get("key"), "key_parsed": key,
            "lengthBars": length_bars, "swing": song.get("swing"),
            "sections": sections, "window": win, "tracks": gold_tracks,
            "buses": buses, "automation": autol,
            "master": _fx_sig(song.get("master")),
            "masterGainDb": song.get("masterGainDb", 0),
            "measured": measured, "mixtarget": mixtarget}, None

# ---------- the bank ----------
def _gold_path(genre):
    return os.path.join(GOLD, re.sub(r"[^a-z0-9_]", "", genre.lower()) + ".json")

def load_gold(genre):
    try:
        return json.load(open(_gold_path(genre)))
    except Exception:
        return None

def load_index():
    try:
        return json.load(open(os.path.join(GOLD, "_index.json")))
    except Exception:
        return {"genres": {}}

def bank(gold):
    """Write-if-better: the standard only rises."""
    old = load_gold(gold["genre"])
    if old and old.get("score", 0) + 0.02 >= gold["score"]:
        return False, (f"kept existing {old.get('source')} "
                       f"(score {old.get('score')} vs {gold['score']})")
    os.makedirs(GOLD, exist_ok=True)
    tmp = _gold_path(gold["genre"]) + ".tmp"
    json.dump(gold, open(tmp, "w"), indent=1)
    os.replace(tmp, _gold_path(gold["genre"]))
    return True, f"banked {gold['source']} (score {gold['score']})"

# ---------- THE STANDARD block (what the session carries) ----------
def _pocket_lines(genre):
    """The genre's 1-bar loop DNA from the graph/cache — the FLOOR, rendered
    honestly (steps are 16ths unless the grid says otherwise)."""
    try:
        import loop_gen
        dna, err = loop_gen.genre_dna(genre)
        if err or not dna:
            return []
        g = dna.get("grid") or {}
        cells = []
        for k in sorted(g):
            v = g[k]
            if isinstance(v, list) and v and all(isinstance(x, (int, float)) for x in v):
                vel = g.get("vel", {}).get(k) if isinstance(g.get("vel"), dict) else None
                vr = ""
                if isinstance(vel, dict) and vel:
                    vv = [float(x) for x in vel.values()]
                    vr = f" vel {_fmt(min(vv))}-{_fmt(max(vv))}"
                cells.append(f"{k} {','.join(str(int(x)) for x in v[:20])}{vr}")
        out = []
        if cells:
            out.append("POCKET (1-bar loop DNA, 16th steps — the floor, not the ceiling): "
                       + " · ".join(cells[:7]))
        ch = g.get("chords")
        if ch:
            out.append("progression (scale degrees per bar): "
                       + " ".join(str(int(c[1])) for c in ch[:8])
                       + (f" · groove {dna['groove']}" if dna.get("groove") else "")
                       + (f" · meter {dna['native_meter']}" if dna.get("native_meter") else ""))
        return out
    except Exception:
        return []

def _mastering_lines(genre, gold, idx_entry):
    mt = (gold or {}).get("mixtarget") or (idx_entry or {}).get("mastering") or {}
    ms = (gold or {}).get("measured") or {}
    out = [f"MASTERING STANDARD ({genre}):"]
    if gold and gold.get("master"):
        chain = " -> ".join(gold["master"])
        if "fx_brickwall" in chain:
            chain += "   [legacy wall shown — TODAY write fx_truepeak(ceiling -1.2) LAST]"
        out.append(f"  gold chain: {chain} · masterGainDb {_fmt(gold.get('masterGainDb', 0))}")
    tgt = []
    if mt.get("lufs_lo") is not None:
        tgt.append(f"LUFS {mt['lufs_lo']}..{mt['lufs_hi']}")
    if mt.get("band_order"):
        tgt.append(f"bands {mt['band_order']}")
    if mt.get("psr_floor") is not None:
        tgt.append(f"PSR >= {mt['psr_floor']}")
    tgt.append("true peak <= -1.2 dBTP · clipped 0")
    out.append("  TARGETS: " + " · ".join(tgt))
    if ms:
        got = [f"LUFS {ms['lufs']}" if ms.get("lufs") is not None else "",
               f"dBTP {ms.get('dbtp')}" if ms.get("dbtp") is not None else "",
               f"PSR {ms.get('psr')}" if ms.get("psr") is not None else "",
               f"clipped {ms.get('clipped')}" if ms.get("clipped") is not None else ""]
        line = " · ".join(x for x in got if x)
        if line:
            out.append("  MEASURED on this gold: " + line)
    out.append("  LAW: reach loudness with track gains + fx_trim INTO the wall; "
               "fx_truepeak(ceiling <= -1.2) is ALWAYS the last master fx; "
               "masterGainDb stays 0; no parked dark filters on the master.")
    return out

_UNIVERSAL = ("COMPLEXITY FLOOR (no gold banked for this genre yet — the laws still bind): "
              "melodic lanes >= 2 notes/bar with REAL velocity shapes (accents + ghosts, "
              "never one flat value); chords VOICED (7ths/9ths, inversions, voice-led "
              "movement — no parallel root triads); a counter-phrase answering the lead; "
              "drums breathe (fills at 4/8-bar turnarounds, velocity waves on hats); "
              "sections CONTRAST (layers enter/exit, at least one automation build).")

def render_block(genre, cap=BLOCK_CAP):
    """THE STANDARD block for a genre — '' when nothing at all is known."""
    genre = re.sub(r"[^a-z0-9_]", "", str(genre or "").lower())
    if not genre:
        return ""
    idx = load_index().get("genres", {})
    entry = idx.get(genre)
    gold, inherited = load_gold(genre), None
    hop, seen = genre, set()
    while gold is None:                          # walk the parent chain for a bank hit
        hop = (idx.get(hop) or {}).get("parent")
        if not hop or hop in seen:
            break
        seen.add(hop)
        gold = load_gold(hop)
        if gold:
            inherited = hop
    pocket = _pocket_lines(genre)
    if gold is None and not pocket and entry is None:
        return ""                                # truly unknown: stay silent, fail open

    L = [f"===== THE STANDARD — {genre} GOLD DNA (hold this bar) ====="]
    if gold:
        src = f"{gold['source']}, score {gold['score']}"
        L.append(f"LAW: below is a REAL take that PASSED the ears ({src})"
                 + (f", inherited from parent genre '{inherited}'" if inherited else "")
                 + ". Match its DENSITY, velocity SHAPES (accents+ghosts), VOICED chords,"
                   " phrase arcs and SPACE — with YOUR OWN notes. Copying its pitches"
                   " verbatim = a rejected take. This is the FLOOR of acceptable.")
        kp = gold.get("key_parsed") or {}
        if kp:
            lead = " (leading tone allowed at cadences)" if kp.get("mode") == "minor" else ""
            L.append(f"KEY LAW — NO OFF-KEY NOTES: {gold['key']} = "
                     f"{' '.join(kp.get('scale_names', []))}{lead}. Every melodic pitch "
                     f"from this set; drums exempt. Set YOUR song's key and obey it the same way.")
        sw = gold.get("swing")
        swtxt = (f" · swing {sw.get('grid')} {sw.get('amount')}"
                 if isinstance(sw, dict) and sw.get("amount") else "")
        L.append(f"{_fmt(gold['bpm'])}bpm · {gold['lengthBars']} bars{swtxt}"
                 + (f" · sections {' '.join(gold['sections'])}" if gold.get("sections") else "")
                 + f" · window shown: bars {gold['window']['startBar']}-"
                   f"{gold['window']['startBar'] + gold['window']['bars'] - 1}")
        mel = [t for t in gold["tracks"] if t["role"] == "melodic"]
        drm = [t for t in gold["tracks"] if t["role"] == "drums"]
        for t in mel:
            fx = (", " + ", ".join(t["fx"])) if t.get("fx") else ""
            L.append(f"- {t['name']} [{t['voice']} {_fmt(t['gainDb'])}dB{fx}] "
                     f"{t['notes_per_bar']}n/bar vel {_fmt(t['vel_lo'])}-{_fmt(t['vel_hi'])} "
                     f"{note_name(t['pitch_lo'])}-{note_name(t['pitch_hi'])} "
                     f"{round(t['in_key_pct'] * 100)}% in-key"
                     + (" [CHORDS]" if t["chordal"] >= 0.5 else ""))
            L.append(f"    {t['dna']}")
        if drm:
            L.append("DRUM DNA (2 bars each — the pattern breathes at fills):")
            for t in drm:
                L.append(f"- {t['name']} [{t['voice']} {_fmt(t['gainDb'])}dB] "
                         f"vel {_fmt(t['vel_lo'])}-{_fmt(t['vel_hi'])}: {t['dna']}")
        varl = " · ".join(f"{t['name']} {'|'.join(str(c) for c in t['bar_counts'])}"
                          for t in (drm[:2] + mel[:2]))
        if varl:
            L.append(f"VARIATION (notes/bar across the window): {varl} — bars must "
                     "DIFFER; unbroken copy-paste loops are a rejected take.")
        if gold.get("automation"):
            L.append("AUTOMATION: " + " · ".join(gold["automation"][:4]))
        else:
            L.append("AUTOMATION: (none on this gold — you still write at least one "
                     "motion curve; builds live here)")
        if gold.get("buses"):
            L.append("BUSES: " + " · ".join(gold["buses"][:3])
                     + " — space rides SENDS; kick/808 stay DRY.")
    else:
        L.append(_UNIVERSAL)
        ck = (entry or {}).get("common_key")
        if ck:
            kp = parse_key(ck if isinstance(ck, str) and ck[0].isupper() else f"A {ck}")
            if kp:
                L.append(f"KEY LAW — NO OFF-KEY NOTES: suggested {ck}; whatever key you "
                         f"declare, EVERY melodic pitch stays in its scale (drums exempt).")
    L += pocket
    L += _mastering_lines(genre, gold, entry)
    L.append("=====")
    txt = "\n".join(L)
    if len(txt) > cap:                            # trim DNA lines from the tail first
        keep, size = [], 0
        for ln in L:
            if size + len(ln) + 1 > cap - 60 and ln.startswith("    "):
                continue
            keep.append(ln)
            size += len(ln) + 1
        # the tail suffix is 21 chars; [:cap-20] minted cap+1 (off-by-one
        # exposed 2026-07-14 when grown banks hit the boundary exactly) AND
        # a blind byte-chop could amputate the MASTERING STANDARD line —
        # trim WHOLE LINES from the tail, keeping the mastering + closing.
        suffix = "\n[gold trimmed]\n====="
        while keep and len("\n".join(keep)) + len(suffix) > cap:
            drop = next((i for i in range(len(keep) - 1, 0, -1)
                         if not keep[i].startswith(("MASTERING", "====="))),
                        None)
            if drop is None:
                break
            keep.pop(drop)
        txt = "\n".join(keep)
        if len(txt) + len(suffix) <= cap:
            txt += suffix
        else:
            txt = txt[:cap - len(suffix)] + suffix
    return txt

# ---------- seeding + the taste-circle leg ----------
def _kg_index():
    """KG -> _index.json (build-time only). Every genre: parent, key, bpm, mastering."""
    from kg import KG
    kg = KG()
    idx = {}
    for (name, props) in kg.q("MATCH (g:Genre) RETURN g.name, properties(g)"):
        idx[name] = {"parent": None, "common_key": (props or {}).get("common_key"),
                     "bpm_lo": (props or {}).get("bpm_lo"),
                     "bpm_hi": (props or {}).get("bpm_hi"), "mastering": None}
    for (child, parent) in kg.q("MATCH (a:Genre)-[:SUBGENRE_OF]->(b:Genre) "
                                "RETURN a.name, b.name"):
        if child in idx:
            idx[child]["parent"] = parent
    for (gname, m) in kg.q("MATCH (g:Genre)-[:TARGETS]->(m:MixTarget) "
                           "RETURN g.name, properties(m)"):
        if gname in idx and m:
            idx[gname]["mastering"] = {k: m.get(k) for k in
                                       ("lufs_lo", "lufs_hi", "band_order",
                                        "psr_floor", "clipped_samples")
                                       if m.get(k) is not None}
    return idx

def _mixtarget_for(genre, idx):
    e = idx.get(genre) or {}
    mt = dict(e.get("mastering") or {})
    if e.get("bpm_lo"):
        mt["bpm_lo"], mt["bpm_hi"] = e["bpm_lo"], e["bpm_hi"]
    return mt or None

def _measure(wav):
    """analyze2 on a rendered wav -> the numbers the mastering standard quotes."""
    try:
        py = os.path.join(ROOT, ".venv", "bin", "python")
        r = subprocess.run([py if os.path.exists(py) else "python3",
                            os.path.join(ROOT, "tools", "analyze2.py"), wav],
                           capture_output=True, text=True, timeout=180)
        d = json.loads(re.search(r"\{.*\}", r.stdout, re.S).group(0))
        return {"lufs": d.get("lufs_integrated"), "dbtp": d.get("true_peak_dbtp"),
                "clipped": d.get("clipped_samples"), "psr": d.get("psr"),
                "bands": d.get("band_energy_pct")}
    except Exception:
        return None

def seed(render_crate=True):
    os.makedirs(GOLD, exist_ok=True)
    idx = _kg_index()
    json.dump({"genres": idx}, open(os.path.join(GOLD, "_index.json"), "w"), indent=0)
    print(f"index: {len(idx)} genres ({sum(1 for e in idx.values() if e['mastering'])} "
          f"with mastering targets)")
    # eval winners: best score per genre, song still on disk, metrics ride along
    best = {}
    try:
        for line in open(os.path.join(ROOT, "eval", "history.jsonl")):
            try:
                d = json.loads(line)
            except Exception:
                continue
            if d.get("kind") == "judge" or d.get("score") is None:
                continue
            g = d.get("genre")
            if g and (g not in best or d["score"] > best[g]["score"]):
                best[g] = d
    except FileNotFoundError:
        pass
    for g, d in sorted(best.items()):
        if d["score"] < 0.8:
            continue
        p = os.path.join(SONGS, f"{d['song']}.json")
        if not os.path.exists(p):
            continue
        m = d.get("metrics") or {}
        measured = {"lufs": m.get("lufs"), "dbtp": m.get("dbtp"),
                    "clipped": m.get("clipped"), "bands": m.get("bands")}
        gold, why = distill(json.load(open(p)), g, f"eval:{d['song']}",
                            measured=measured, mixtarget=_mixtarget_for(g, idx))
        print(f"  eval {g:16s} " + (bank(gold)[1] if gold else f"REJECTED: {why}"))
    # crate loops: curated flagship DNA (render for measured numbers when possible)
    crate = os.path.join(SONGS, "crate")
    for f in sorted(os.listdir(crate)) if os.path.isdir(crate) else []:
        m = re.match(r"([a-z0-9_]+?)_\d+\.json$", f)
        if not m:
            continue
        g = m.group(1)
        measured = None
        if render_crate:
            m1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")
            wav = os.path.join(GOLD, f".seed_{g}.wav")
            try:
                subprocess.run([m1, "render", os.path.join(crate, f), wav],
                               capture_output=True, timeout=300)
                measured = _measure(wav)
            finally:
                if os.path.exists(wav):
                    os.unlink(wav)
        gold, why = distill(json.load(open(os.path.join(crate, f))), g, f"crate:{f[:-5]}",
                            measured=measured, mixtarget=_mixtarget_for(g, idx))
        print(f"  crate {g:15s} " + (bank(gold)[1] if gold else f"REJECTED: {why}"))

def ingest_accepts(telemetry=None, songs_dir=None):
    """ACCEPTED takes -> gold candidates (the taste circle's note-DNA leg).
    Called from kg_ingest_telemetry after every verdict batch; quality gates +
    write-if-better keep the bank monotonically rising. Never raises."""
    telemetry = telemetry or os.path.join(ROOT, "telemetry", "proposals.jsonl")
    songs_dir = songs_dir or SONGS
    idx = load_index().get("genres", {})
    latest = {}
    try:
        for line in open(telemetry):
            try:
                d = json.loads(line)
            except Exception:
                continue
            if d.get("accepted") and d.get("genre") and d.get("song"):
                latest[(d["song"], d["genre"])] = d
    except FileNotFoundError:
        return []
    out = []
    for (song_name, genre), d in sorted(latest.items()):
        p = os.path.join(songs_dir, f"{song_name}.json")
        if not os.path.exists(p):
            continue
        try:
            gold, why = distill(json.load(open(p)), genre, f"accept:{song_name}",
                                mixtarget=_mixtarget_for(genre, idx))
            if gold:
                did, msg = bank(gold)
                out.append(f"{genre}: {msg}")
            else:
                out.append(f"{genre}: gate refused {song_name}: {why}")
        except Exception as e:
            out.append(f"{genre}: {e!r}")
    return out

def verify():
    """Bank invariants (gold_battery drives this and adds session-seam checks)."""
    errs, idx = [], load_index()
    if not idx.get("genres"):
        errs.append("no _index.json — run seed on the dev box")
    files = [f for f in sorted(os.listdir(GOLD)) if f.endswith(".json")
             and not f.startswith("_")] if os.path.isdir(GOLD) else []
    if not files:
        errs.append("empty bank")
    for f in files:
        try:
            g = json.load(open(os.path.join(GOLD, f)))
        except Exception as e:
            errs.append(f"{f}: unparseable {e!r}")
            continue
        mel = [t for t in g.get("tracks", []) if t["role"] == "melodic"]
        if not mel:
            errs.append(f"{f}: no melodic track")
        for t in mel:
            if t["in_key_pct"] < 0.75:
                errs.append(f"{f}: {t['name']} {t['in_key_pct']:.0%} in key")
        if not any(t.get("dna") for t in g.get("tracks", [])):
            errs.append(f"{f}: no DNA text")
        blk = render_block(g["genre"])
        if not blk or len(blk) > BLOCK_CAP:
            errs.append(f"{f}: block {len(blk)} chars (cap {BLOCK_CAP})")
        for must in ("THE STANDARD", "MASTERING STANDARD", "verbatim", "KEY LAW"):
            if blk and must not in blk:
                errs.append(f"{f}: block missing '{must}'")
    return errs, len(files)

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "verify"
    if cmd == "seed":
        seed(render_crate="--no-render" not in sys.argv)
    elif cmd == "ingest-accepts":
        for line in ingest_accepts():
            print(line)
    elif cmd == "block":
        print(render_block(sys.argv[2]))
    elif cmd == "verify":
        errs, n = verify()
        for e in errs:
            print("FAIL:", e)
        print(f"gold bank: {n} exemplars, {'clean' if not errs else 'RED'}")
        sys.exit(1 if errs else 0)
