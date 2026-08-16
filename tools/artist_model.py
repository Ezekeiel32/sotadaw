#!/usr/bin/env python3
"""THE ARTIST MODEL (A2-T1/T2, docs/SPEC_TRANSCENDENCE.md) — taste as code.

Distills a per-user TASTE CONSTITUTION from deterministic evidence ONLY
(Write Law 1: telemetry verdicts, chronicle verdict rows, the fact store —
NEVER model free text), renders it as a human-readable, USER-EDITABLE law
file, and serves two consumers:

  artist_block(genre)        -> <=~1.1K-char prompt rider (sidecar ctx; the
                                user's standing taste rides every ask; their
                                words in the ask ALWAYS outrank the block)
  court_constitution(song)   -> advisory verdict (avoid-term word-boundary
                                scan; no heal — taste nags, never surgery)

THE FILE: songs/.artist/constitution.md (gitignored — taste is user-owned,
local-first; it travels in THE SUITCASE, never in the repo).

OWNERSHIP LAW (v17 shape): machine lines carry stable [kind:key] ids and are
hard-overwritten wholesale on re-distill; everything the USER writes (the
"YOUR WORDS" section, or any un-id'd bullet in THE LAWS) is sacred — kept
verbatim forever and ranked ABOVE machine laws in the block. To edit a
machine law, copy it into YOUR WORDS; the machine section is machine-owned.

HONEST MISS: thresholds gate every law (a habit needs n>=3 accepts; an avoid
needs a repeated WHY or an explicit fact). Thin evidence -> no law -> empty
block -> the rider is omitted. Single WHYs surface under RECENT FEEDBACK
(labeled not-yet-law) so the user sees the system heard them.

stdlib-only; every path takes root= for battery isolation.
"""
import ast
import collections
import glob
import json
import os
import re
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONST_REL = os.path.join("songs", ".artist", "constitution.md")

# WHY bucketing — the taste-circle vocabulary (kg_ingest's buckets, inlined so
# this module stays stdlib-pure). Buckets GROUP repeated feedback; law text
# always keeps the user's words verbatim (taste-correction law).
_BUCKETS = (
    ("bright",  ("bright", "harsh", "shrill", "tinny", "sharp", "fizz")),
    ("dark",    ("dark", "dull", "muffled", "muddy", "boomy")),
    ("groove",  ("groove", "beat", "timing", "swing", "pocket", "offbeat",
                 "off-beat", "on beat", "quantiz", "rushed", "drag")),
    ("busy",    ("busy", "cluttered", "too much", "crowded", "dense")),
    ("empty",   ("empty", "thin", "sparse", "boring", "repetitive", "flat")),
    ("level",   ("loud", "quiet", "level", "volume", "clip", "distort")),
    ("key",     ("key", "off-key", "off key", "tune", "pitch", "sour")),
    ("vocal",   ("vocal", "voice", "lyric", "sing", "autotune")),
    ("length",  ("long", "short", "length", "minutes")),
    ("vibe",    ("vibe", "feel", "mood", "genre", "style")),
)


def _bucket(why):
    w = why.lower()
    for name, words in _BUCKETS:
        if any(t in w for t in words):
            return name
    return "other"


def _parse_metrics(m):
    if isinstance(m, dict):
        return m
    if isinstance(m, str) and m.strip().startswith("{"):
        try:
            v = ast.literal_eval(m)
            return v if isinstance(v, dict) else {}
        except Exception:
            return {}
    return {}


# ---------------------------------------------------------------- evidence

def mine(root=None):
    """All deterministic evidence, one pass. Never raises."""
    root = root or ROOT
    verdicts = []      # {t, song, accepted, genre, why, metrics}
    seen_why = set()
    tel = os.path.join(root, "telemetry", "proposals.jsonl")
    if os.path.exists(tel):
        for ln in open(tel, errors="replace"):
            try:
                r = json.loads(ln)
            except Exception:
                continue
            if not isinstance(r, dict) or "accepted" not in r:
                continue
            why = str(r.get("note") or "").strip()
            row = {"t": r.get("t", 0), "song": r.get("song", ""),
                   "accepted": bool(r.get("accepted")),
                   "genre": str(r.get("genre") or "").strip().lower(),
                   "why": why, "metrics": _parse_metrics(r.get("metrics"))}
            verdicts.append(row)
            if why:
                seen_why.add((row["song"], int(row["t"])))
    # chronicle verdict rows carry WHYs telemetry may lack (typed reasons)
    for f in glob.glob(os.path.join(root, "songs", ".chat", "*.jsonl")):
        song = os.path.basename(f)[:-6]
        try:
            for ln in open(f, errors="replace"):
                if '"verdict"' not in ln:
                    continue
                try:
                    r = json.loads(ln)
                except Exception:
                    continue
                if r.get("role") != "verdict":
                    continue
                why = str(r.get("text") or "").strip()
                if not why:
                    continue
                key = (song, int(r.get("t", 0)))
                if key in seen_why:
                    continue
                seen_why.add(key)
                verdicts.append({"t": r.get("t", 0), "song": song,
                                 "accepted": r.get("verdict") == "accept",
                                 "genre": "", "why": why, "metrics": {}})
        except Exception:
            continue
    # fact store: fold last-write-wins per (entity, rel); honor gone
    facts = {}
    for f in sorted(glob.glob(os.path.join(root, "songs", ".memory",
                                           "*.jsonl"))):
        song = os.path.basename(f)[:-6]
        try:
            for ln in open(f, errors="replace"):
                try:
                    r = json.loads(ln)
                except Exception:
                    continue
                rel = r.get("rel")
                if rel not in ("prefers", "avoid", "sweet_spot",
                               "refers_to", "alias"):
                    continue
                k = (rel, str(r.get("entity", "")))
                if r.get("gone"):
                    facts.pop(k, None)
                else:
                    facts[k] = {"rel": rel, "entity": str(r.get("entity", "")),
                                "value": str(r.get("value", "")),
                                "song": song, "t": r.get("t", 0)}
        except Exception:
            continue
    return {"verdicts": verdicts, "facts": list(facts.values())}


# ------------------------------------------------------------------- laws

def distill(evidence, now=None):
    """Evidence -> machine laws (stable ids) + recent feedback lines."""
    now = now or time.time()
    laws, recent = [], []
    vs = evidence.get("verdicts", [])
    accepted = [v for v in vs if v["accepted"]]

    # 1. measured habits per genre (the user's own accepted numbers)
    by_genre = collections.defaultdict(list)
    for v in accepted:
        if v["genre"]:
            by_genre[v["genre"]].append(v)
    for g, rows in sorted(by_genre.items()):
        lufs = sorted(m for m in
                      (r["metrics"].get("lufs_integrated") for r in rows)
                      if isinstance(m, (int, float)))
        if len(lufs) >= 3:
            med = lufs[len(lufs) // 2]
            p25 = lufs[len(lufs) // 4]
            p75 = lufs[(3 * len(lufs)) // 4]
            laws.append({"id": f"lufs:{g}", "kind": "habit",
                         "text": (f"my accepted {g} lands ~{med:.1f} LUFS "
                                  f"(n={len(lufs)}, middle {p25:.1f}..{p75:.1f})"
                                  " — start masters there"),
                         "n": len(lufs)})
        keys = collections.Counter(
            str(r["metrics"].get("key_estimate") or "").strip().lower()
            for r in rows if r["metrics"].get("key_estimate"))
        keys.pop("", None)
        if sum(keys.values()) >= 4:
            top, cnt = keys.most_common(1)[0]
            if cnt / sum(keys.values()) >= 0.5:
                laws.append({"id": f"key:{g}", "kind": "habit",
                             "text": (f"most of my accepted {g} sits in "
                                      f"{top} ({cnt}/{sum(keys.values())})"),
                             "n": cnt})

    # 2. avoid laws from repeated reject WHYs (verbatim words ride)
    whys = [v for v in vs if v["why"] and not v["accepted"]]
    buckets = collections.defaultdict(list)
    for v in whys:
        buckets[_bucket(v["why"])].append(v["why"])
    for b, quotes in sorted(buckets.items()):
        uniq = list(dict.fromkeys(quotes))
        if len(quotes) >= 2:
            q = " / ".join(f'"{u[:60]}"' for u in uniq[:3])
            laws.append({"id": f"avoid:{b}", "kind": "avoid",
                         "text": f"I have rejected takes for this ({b}): {q}"
                                 " — do not repeat it",
                         "n": len(quotes)})
        else:
            recent.append(f'{b}: "{uniq[0][:70]}" (1x — repeats become law)')

    # 3. explicit facts (the user said so — strongest evidence class)
    for f in evidence.get("facts", []):
        ent = re.sub(r"[^a-z0-9_ .:-]", "", f["entity"].lower())[:40]
        val = f["value"][:60]
        if f["rel"] == "avoid":
            laws.append({"id": f"never:{ent}", "kind": "avoid",
                         "text": f"never: {ent}"
                                 + (f" ({val})" if val else ""), "n": 1})
        elif f["rel"] in ("prefers", "sweet_spot"):
            laws.append({"id": f"prefer:{ent}", "kind": "prefer",
                         "text": f"prefer: {ent}"
                                 + (f" = {val}" if val else ""), "n": 1})
        elif f["rel"] in ("refers_to", "alias"):
            laws.append({"id": f"vocab:{ent}", "kind": "vocab",
                         "text": f'when I say "{ent}" I mean {val}'
                                 f" (established on {f['song']})", "n": 1})

    # 4. home genres (where the taste data actually lives)
    homes = [(g, len(r)) for g, r in by_genre.items() if len(r) >= 5]
    if homes:
        homes.sort(key=lambda x: -x[1])
        laws.append({"id": "home:*", "kind": "home",
                     "text": "home genres by accepted takes: " + ", ".join(
                         f"{g} ({n})" for g, n in homes[:5]),
                     "n": sum(n for _, n in homes)})
    return laws, recent


# ------------------------------------------------- render / parse / merge

_HDR = """# THE ARTIST CONSTITUTION — your taste, as code
This file is DISTILLED from your own verdicts (accepts, rejects + WHYs,
things you told the agent to remember). It rides every ask you send.
- Your words in an ask ALWAYS outrank this file.
- Lines under YOUR WORDS are yours forever — the machine never touches them.
- THE LAWS section is machine-owned (stable [ids], re-distilled from
  evidence). To edit one, copy it into YOUR WORDS — your copy outranks.
- Delete any YOUR WORDS line to retire it.
"""

_M_LINE = re.compile(r"^- \[([a-z]+:[^\]]*)\] (.*?)(?:  \(n=\d+\))?$")


def render_md(laws, recent, user_laws, user_words):
    out = [_HDR, "## YOUR WORDS (yours, never machine-touched)"]
    out += [f"- {w}" for w in user_words] or []
    out.append("")
    out.append("## THE LAWS (machine-distilled; edit via YOUR WORDS)")
    for lw in sorted(laws, key=lambda l: (l["kind"], l["id"])):
        out.append(f"- [{lw['id']}] {lw['text']}  (n={lw['n']})")
    for ul in user_laws:      # un-id'd bullets a user typed here: promoted
        out.append(f"- {ul}")
    out.append("")
    if recent:
        out.append("## RECENT FEEDBACK (not yet law — repeats become law)")
        out += [f"- {r}" for r in recent]
        out.append("")
    return "\n".join(out) + "\n"


def parse_md(text):
    """-> (machine_laws {id: text}, user_laws [..], user_words [..])."""
    machine, user_laws, user_words = {}, [], []
    section = ""
    for ln in text.splitlines():
        s = ln.strip()
        if s.startswith("## "):
            # THE LAWS first: its header says "edit via YOUR WORDS", so a
            # words-first check would swallow the whole machine section
            section = ("laws" if "THE LAWS" in s else
                       "words" if "YOUR WORDS" in s else
                       "recent" if "RECENT" in s else "")
            continue
        if not s.startswith("- "):
            continue
        if section == "words":
            user_words.append(s[2:])
        elif section == "laws":
            m = _M_LINE.match(s)
            if m:
                machine[m.group(1)] = m.group(2)
            else:
                user_laws.append(s[2:])
    return machine, user_laws, user_words


def distill_and_write(root=None, now=None):
    """mine -> distill -> merge (user lines sacred) -> atomic write."""
    root = root or ROOT
    path = os.path.join(root, CONST_REL)
    user_laws, user_words = [], []
    if os.path.exists(path):
        try:
            _, user_laws, user_words = parse_md(open(path).read())
        except Exception:
            pass
    laws, recent = distill(mine(root), now=now)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    open(tmp, "w").write(render_md(laws, recent, user_laws, user_words))
    os.replace(tmp, path)
    return {"path": path, "laws": len(laws), "user_lines":
            len(user_laws) + len(user_words), "recent": len(recent)}


# --------------------------------------------------------------- consumers

def _load(root=None):
    """-> (machine {id: text}, user_lines [..]) from disk; ({}, []) if none."""
    path = os.path.join(root or ROOT, CONST_REL)
    if not os.path.exists(path):
        return {}, []
    try:
        machine, user_laws, user_words = parse_md(open(path).read())
        return machine, user_words + user_laws
    except Exception:
        return {}, []


def artist_block(genre="", root=None, budget=1100):
    """The prompt rider. Empty string when the constitution is empty
    (honest miss — the block is omitted, never filler)."""
    machine, user_lines = _load(root)
    if not machine and not user_lines:
        return ""
    g = (genre or "").strip().lower()
    if not g and "home:*" in machine:
        # no resolved genre yet: the user's HOME genre habits are the
        # default taste context (their top-accepted genre)
        m = re.search(r"takes: ([a-z0-9_]+)", machine["home:*"])
        if m:
            g = m.group(1)
    lines = [f"* {u}" for u in user_lines[:6]]          # user outranks
    order = (["vocab:", "never:", "avoid:", "prefer:"]
             + ([f"lufs:{g}", f"key:{g}"] if g else [])
             + ["home:*"])
    added = set()
    for pref in order:
        for lid, text in sorted(machine.items()):
            if lid in added:
                continue
            if lid == pref or (pref.endswith(":") and lid.startswith(pref)):
                # genre-scoped habits only ride for THEIR genre
                if (lid.split(":")[0] in ("lufs", "key")
                        and g and not lid.endswith(":" + g)):
                    continue
                lines.append(f"- {text}")
                added.add(lid)
    if not lines:
        return ""
    head = ("ARTIST CONSTITUTION (this user's standing taste, distilled from "
            "their own verdicts — obey it; the ask's own words outrank it):")
    out = head
    for ln in lines:
        if len(out) + len(ln) + 1 > budget:
            break
        out += "\n" + ln
    return out


def court_constitution(song, genre="", root=None):
    """A2-T2 advisory: explicit avoid-terms vs the take's surface (track
    names + source ids). Word-boundary law ('oud' never matches 'loudness').
    No heal — taste advises, never operates."""
    machine, user_lines = _load(root)
    terms = []
    for lid, text in machine.items():
        if lid.startswith("never:"):
            terms.append(lid.split(":", 1)[1].strip())
    for u in user_lines:
        m = re.match(r"(?:never|no|avoid)[:\s]+([a-z0-9_ .-]{2,40})$",
                     u.strip().lower())
        if m:
            terms.append(m.group(1).strip())
    terms = [t for t in dict.fromkeys(terms) if len(t) >= 3]
    if not terms:
        return {"skipped": True}
    surface = []
    for tr in (song.get("tracks") or []):
        surface.append(str(tr.get("name", "")).lower())
        src = tr.get("source") or {}
        surface.append(str(src.get("id", "")).lower())
    hay = " ".join(surface)
    hits = []
    for t in terms:
        pat = r"\b" + re.escape(t).replace(r"\ ", r"[ _-]") + r"\b"
        if re.search(pat, hay):
            hits.append(t)
    return {"ok": not hits, "hits": hits,
            "msg": ("constitution: take contains what you told me to avoid: "
                    + ", ".join(hits)) if hits else "constitution: clean"}


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] == "--write":
        print(json.dumps(distill_and_write(), indent=1))
    elif args[0] == "--show":
        p = os.path.join(ROOT, CONST_REL)
        print(open(p).read() if os.path.exists(p)
              else "(no constitution yet — run --write)")
    elif args[0] == "--block":
        print(artist_block(args[1] if len(args) > 1 else "") or
              "(empty — no laws yet)")
    elif args[0] == "--court":
        doc = json.load(open(args[1]))
        print(json.dumps(court_constitution(
            doc, args[2] if len(args) > 2 else ""), indent=1))
    else:
        print(__doc__)
