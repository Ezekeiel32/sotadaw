#!/usr/bin/env python3
"""First-party telemetry -> knowledge graph (SPEC S6-V34).

Reads telemetry/proposals.jsonl (every accept/reject verdict the user ever gave,
with the prompt and the proposal's measured metrics) and writes taste signal back
into the graph:

  Genre nodes gain:  verdicts_n, accept_rate  (recomputed idempotently each run)
  a (:TelemetrySnapshot {date, rows, accepted}) node records each ingestion

Genre attribution v1: first graph-genre name appearing in the prompt text.
Rows with no genre mention aggregate onto (:Genre {name:'_untagged'}).

TASTE (v2): reject WHYs (verbatim since the feedback loop closed) bucket into
per-genre complaint counters — Genre nodes gain `complaints` ("bright:3;groove:2")
and `last_whys` (the last raw reasons) — the factory's taste data.

ATTRIBUTION v4 (2026-07-11) THE DARK POOL DRAIN: 70% of verdicts sat on
_untagged — session FOLLOW-UPS ("BASS IS SHIT!", "KEEP GOING!") never re-name
the genre the first ask declared, so the richest taste signal biased nothing.
And the v1 substring scan could NEVER match multi-word graph names
(acid_house vs the ask's "acid house") while happily tagging "house" inside
"warehouse". See attribute_rows() for the five rungs.
Run: .venv/bin/python tools/kg_ingest_telemetry.py
"""
import json, os, re, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from kg import KG, esc

TELEMETRY = os.path.join(ROOT, "telemetry", "proposals.jsonl")

# complaint taxonomy: keyword heuristics over the reject WHY (first match wins;
# buckets are STABLE names — downstream consumers key on them)
COMPLAINTS = [
    ("bright", ("bright", "harsh", "shrill", "piercing", "tinny", "sibilan")),
    ("dark",   ("dark", "muddy", "dull", "muffl")),
    ("groove", ("groove", "timing", "swing", "stiff", "robot", "quantiz", "feel",
                "on beat", "off beat", "offbeat", "off-beat", "rushed", "drags")),
    ("busy",   ("busy", "too much", "crowded", "clutter", "dense")),
    ("empty",  ("empty", "thin", "sparse", "boring", "repetitiv", "same")),
    ("level",  ("loud", "quiet", "volume", "clip")),
    ("vibe",   ("vibe", "style", "genre", "wrong", "not the")),
]

def complaint_bucket(why):
    w = (why or "").lower()
    if not w.strip():
        return None
    for name, keys in COMPLAINTS:
        if any(k in w for k in keys):
            return name
    return "other"


CORRECTIVE = re.compile(
    r"\b(?:less|too|way too|not so|stop being|quit being)\s+(?:so\s+|very\s+)?(\w{3,})")


def corrective_buckets(prompt):
    """dr18 (2026-07-12): the DOMINANT taste signal — corrections typed as
    the NEXT PROMPT ('make it less bright', 'too muddy in the low end') —
    leaked entirely; only reject notes bucketed. Mine CORRECTIVE phrasing
    only (a request FOR 'bright synthpop' is taste toward, not a complaint)
    and bucket the whole matched window through the same stable buckets."""
    out = []
    for m in CORRECTIVE.finditer((prompt or "").lower()):
        b = complaint_bucket(m.group(0))
        if b and b != "other":
            out.append(b)
    return out


def _norm(s):
    return re.sub(r"\s+", " ", re.sub(r"[-_]+", " ", (s or "").lower())).strip()


def genre_matcher(genres):
    """Longest-first word-boundary matcher over hyphen/underscore-normalized
    text. 'progressive house' outranks 'house'; 'psytrance' outranks 'goa' in
    "psytrance goa"; 'warehouse' never tags house; graph names like acid_house
    match the ask's "acid house". Short names (pop, wave) can still false-tag
    as verbs — accepted residual, strictly narrower than the old substring."""
    pairs = sorted(((g, _norm(g)) for g in genres if g != "_untagged" and _norm(g)),
                   key=lambda p: -len(p[1]))
    pats = [(g, re.compile(r"\b" + re.escape(n) + r"\b")) for g, n in pairs]

    def match(text):
        t = _norm(text)
        for g, p in pats:
            if p.search(t):
                return g
        return None
    return match


def match_reference(song, ref_genre):
    """Rung 4's lookup: exact Reference name, else copy-suffix STEM equality
    ('record' == 'record_2' == 'record_3' — re-imports bank under whichever
    copy was open, verdicts land on the others). Generic stems (untitled_N,
    _scratch names, short) never fuzzy-match: distinct sessions share those."""
    song = str(song or "")
    if song in ref_genre:
        return ref_genre[song]

    def stem(n):
        s = re.sub(r"_\d+$", "", n)
        return s if len(s) >= 6 and s != "untitled" and not s.startswith("_") else None

    s = stem(song)
    if s is None:
        return None
    for ref, g in ref_genre.items():
        if ref == s or stem(ref) == s:
            return g
    return None


def attribute_rows(rows, genres, ref_lookup=None):
    """v4 rungs, strongest first, one chronological pass:
      1 explicit row['genre'] (the sidecar stamps asks since v3)
      2 text scan of prompt+note (normalized, word-boundary, longest-first)
      3 song-sticky: the song's latest rung-1/2 tag rides its later verdicts
        (forward only; a mid-session pivot re-names in text and re-tags —
        weaker rungs never seed stickiness, so a song-name guess can't spread)
      4 import Reference SOUNDS_LIKE (banked at import)
      5 song-NAME scan (eval_house et al) — last resort, never propagates
    Pure: rows in, genre names out (kg_taste_battery proves it fixture-only)."""
    match = genre_matcher(genres)
    gset = set(genres)
    sticky = {}
    out = []
    for row in rows:
        song = str(row.get("song", ""))
        explicit = str(row.get("genre", "")).strip().lower()
        g = explicit if explicit in gset else None
        if g is None:
            g = match(str(row.get("prompt", "") or "") + " " + str(row.get("note", "") or ""))
        if g is not None:
            sticky[song] = g
        else:
            g = sticky.get(song)
            if g is None and ref_lookup is not None:
                g = ref_lookup(song)
            if g is None:
                g = match(song)
        out.append(g or "_untagged")
    return out

def ingest():
    if not os.path.exists(TELEMETRY):
        print("no telemetry yet (telemetry/proposals.jsonl) — verdicts accumulate as the app is used")
        return
    kg = KG()
    genres = [r[0] for r in kg.q("MATCH (g:Genre) RETURN g.name")]

    # Rung 4 (v2 2026-07-10, copy-suffix-tolerant v4): imports never NAME their
    # genre in the prompt, so their verdicts drowned in _untagged while e.g.
    # phonk had verdicts_n=None. The Reference node banked at import carries
    # SOUNDS_LIKE; the verdict teaches THAT genre's skill. One query, pure after.
    try:
        refs = {r[0]: r[1] for r in kg.q(
            "MATCH (r:Reference)-[:SOUNDS_LIKE]->(g:Genre) RETURN r.name, g.name")}
    except Exception:
        refs = {}
    song_genre = lambda song: match_reference(song, refs)

    all_rows = []
    for line in open(TELEMETRY):
        try:
            all_rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    stats = {}
    rows = len(all_rows)
    for row, genre in zip(all_rows, attribute_rows(all_rows, genres, song_genre)):
        s = stats.setdefault(genre, {"n": 0, "y": 0, "c": {}, "whys": []})
        s["n"] += 1
        s["y"] += 1 if row.get("accepted") else 0
        if not row.get("accepted"):
            b = complaint_bucket(row.get("note", ""))
            if b:
                s["c"][b] = s["c"].get(b, 0) + 1
                s["whys"] = (s["whys"] + [str(row.get("note", ""))[:80]])[-3:]
        # dr18: corrective language in the PROMPT is taste signal regardless
        # of the eventual verdict (a revise that says 'less bright' teaches
        # even when its take is later accepted)
        for b in corrective_buckets(row.get("prompt", "")):
            s["c"][b] = s["c"].get(b, 0) + 1
            s["whys"] = (s["whys"] + [str(row.get("prompt", ""))[:80]])[-3:]

    kg.upsert("Genre", "_untagged", "telemetry:ingest", bpm_lo=0, bpm_hi=0)
    for genre, s in stats.items():
        rate = round(s["y"] / s["n"], 3) if s["n"] else None
        comp = ";".join(f"{k}:{v}" for k, v in
                        sorted(s["c"].items(), key=lambda kv: -kv[1]))
        whys = " | ".join(s["whys"])[:300]
        kg.g.query(f"MATCH (g:Genre {{name: '{esc(genre)}'}}) "
                   f"SET g.verdicts_n = {s['n']}, g.accept_rate = {rate}, "
                   f"g.complaints = '{esc(comp)}', g.last_whys = '{esc(whys)}'")
    total_y = sum(s["y"] for s in stats.values())
    snap = time.strftime("%Y-%m-%d %H:%M")
    kg.upsert("TelemetrySnapshot", snap, "telemetry:ingest", rows=rows, accepted=total_y)
    print(f"ingested {rows} verdicts ({total_y} accepted) across {len(stats)} genres:",
          {g: f"{s['y']}/{s['n']}" for g, s in stats.items()})

    # THE CRANK TRIGGER (BEST_DAW_30 #4c): a genre whose complaint bucket hits 3
    # has told us the same thing three times — file advisor PROPOSALS immediately
    # (factory_advisor is free + proposals-only: a human or a supervised
    # advisor_cycle run applies them; never an autopilot). SOTADAW_ADVISOR=0 kills.
    flagged = sorted(g for g, s in stats.items()
                     if g != "_untagged" and s["c"] and max(s["c"].values()) >= 3)
    if flagged and os.environ.get("SOTADAW_ADVISOR", "1") != "0":
        import subprocess
        r = subprocess.run([sys.executable,
                            os.path.join(ROOT, "tools", "factory_advisor.py")],
                           capture_output=True, text=True, timeout=120)
        tail = (r.stdout or r.stderr).strip().splitlines()
        print(f"crank: complaint threshold hit on {flagged} -> factory_advisor "
              f"({'ok' if r.returncode == 0 else 'rc ' + str(r.returncode)}: "
              f"{tail[-1][:120] if tail else 'no output'})")

if __name__ == "__main__":
    ingest()
    # THE GOLD LEG (2026-07-13): accepted takes are the truest standard — after
    # every verdict batch, qualifying accepts distill into library/gold (strict
    # gates + write-if-better inside gold_bank; the bank only rises). The sidecar
    # already spawns this script post-verdict, so the circle closes for free.
    try:
        import gold_bank
        for line in gold_bank.ingest_accepts():
            print("gold:", line)
    except Exception as e:
        print(f"gold leg skipped: {e!r}")
