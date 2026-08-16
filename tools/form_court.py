#!/usr/bin/env python3
"""THE FORM + SIGNATURE COURTS (wave 44; R-23 item 151, R-22/R-24 items
149/156).

court_form_conformance — the song's sections[] against its family's
canonical template (ONE RESOLVER: form_plan.FORM_TEMPLATES, the same
table THE PLANNER plans with). Class-mapped LCS order similarity;
ADVISORY-only (real forms vary — the court says HOW FAR, never guilty).

court_signature — the 'signature voice' check: every genre's KG node
names its SoundRecipes and Techniques; the INSTRUMENT-tokens among them
are the genre's signature vocabulary (amapiano: log_drum; gospel:
organ/choir...). A take whose sources+lanes contain NONE of its
genre's signature tokens reads generic — advisory carrying the list.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

_CLASS = (
    ("intro", ("intro",)), ("outro", ("outro",)),
    ("hook", ("chorus", "drop", "hook", "theme", "climax")),
    ("build", ("build", "rise", "lift", "prechorus", "pre_chorus")),
    ("quiet", ("break", "bridge", "interlude", "stopdown", "breakdown")),
    ("verse", ("verse", "part", "section", "groove", "main")),
)
# instrument tokens worth calling a SIGNATURE (filters out technique
# nouns like send_reverb / shuffle_swing)
_INSTRUMENT_TOKENS = (
    "log_drum", "organ", "piano", "rhodes", "808", "guitar", "brass",
    "choir", "strings", "sax", "flute", "steel", "kalimba", "sitar",
    "koto", "erhu", "banjo", "accordion", "tabla", "conga", "timbale",
    "cowbell", "vocoder", "acid", "reese", "supersaw", "arp", "bell",
    "marimba", "oud", "bagpipe", "harmonica", "clav", "wurli",
)


def _sec_class(name):
    base = str(name or "").strip().lower().rstrip("0123456789_ ")
    for cls, keys in _CLASS:
        if any(k in base for k in keys):
            return cls
    return "verse"


def _lcs(a, b):
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m):
        for j in range(n):
            dp[i + 1][j + 1] = dp[i][j] + 1 if a[i] == b[j] else \
                max(dp[i][j + 1], dp[i + 1][j])
    return dp[m][n]


_DJ_OUTRO_OK = ("house", "techno", "trance", "psytrance", "goa", "dnb",
                "garage", "dub_techno", "minimal", "electro", "disco")


def court_outro(song, genre=""):
    """W64 (r-14 item 207): outro <=8 bars (target 4) — streaming skips
    ~50% before a fade ends; house/techno DJ tools keep their 32+ bar
    mix-outs (exempt). Advisory."""
    secs = [s for s in (song or {}).get("sections", []) or []
            if isinstance(s, dict)]
    if len(secs) < 2:
        return {"court": "outro", "ok": True, "advisories": [],
                "skipped": "needs sections"}
    g = str(genre or "").lower().replace("-", "_").replace(" ", "_")
    if any(w in g for w in _DJ_OUTRO_OK):
        return {"court": "outro", "ok": True, "advisories": [],
                "skipped": "DJ-tool genre (32+ bar mix-outs by design)"}
    secs.sort(key=lambda s: float(s.get("startBar", 0)))
    last = secs[-1]
    if _sec_class(last.get("name")) != "outro" and             "outro" not in str(last.get("name", "")).lower():
        return {"court": "outro", "ok": True, "advisories": []}
    end = float((song or {}).get("lengthBars", 0) or 0)
    span = end - float(last.get("startBar", 0))
    advisories = []
    if span > 8:
        advisories.append({
            "kind": "long_outro", "bars": int(span),
            "why": (f"the outro runs {span:.0f} bars — streaming "
                    "listeners skip before a long fade lands; 4-8 bars "
                    "and a DEFINITIVE final hit beat a fade (DJ genres "
                    "exempt)")})
    return {"court": "outro", "ok": True, "advisories": advisories}


def court_ritual(song, genre=""):
    """W88 (r-22 item 246): THE BOI-1DA RULE — something changes every
    4 bars (drop/add/fill/melodic shift). Two consecutive IDENTICAL
    4-bar blocks across every lane = the loop-tell advisory. Plus the
    intro (4-8 bars) and hook (8-16) block-size rituals for the rap
    lineages."""
    bars = int((song or {}).get("lengthBars", 0) or 0)
    tracks = [t for t in (song or {}).get("tracks", []) or []
              if isinstance(t, dict) and not t.get("muted")
              and t.get("notes")
              and not str(t.get("name", "")).startswith("_")]
    if bars < 12 or not tracks:
        return {"court": "ritual", "ok": True, "advisories": [],
                "skipped": "too little material"}

    def block_print(b0):
        sig = []
        for t in tracks:
            ons = []
            for n in t.get("notes") or []:
                try:
                    s = float(n.get("start", 0))
                except Exception:
                    continue
                if b0 * 4.0 <= s < (b0 + 4) * 4.0:
                    ons.append((round((s - b0 * 4.0) * 4) / 4.0,
                                int(n.get("pitch", 0)),
                                int(float(n.get("vel", 96)) // 16)))
            sig.append(tuple(sorted(ons)))
        return tuple(sig)

    advisories = []
    runs = []
    prev = None
    run_start = 0
    for b0 in range(0, bars - 3, 4):
        fp = block_print(b0)
        if not any(fp):
            prev = None
            continue
        if fp == prev:
            runs.append((run_start, b0 + 4))
        else:
            run_start = b0 - 4 if prev is not None else b0
        prev = fp
    if runs:
        a = min(r[0] for r in runs)
        b = max(r[1] for r in runs)
        advisories.append({
            "kind": "static_blocks", "fromBar": a, "toBar": b,
            "why": (f"bars {a}-{b}: consecutive 4-bar blocks are "
                    "IDENTICAL on every lane — the Boi-1da rule says "
                    "something changes every 4 bars (drop a lane, add "
                    "a fill, shift the melody); a loop that never "
                    "varies is the AI tell")})
    g = str(genre or "").lower()
    if any(w in g for w in ("trap", "drill", "rap", "hiphop", "hip_hop",
                            "boom", "phonk", "rage", "plugg")):
        secs = sorted((s for s in (song or {}).get("sections", []) or []
                       if isinstance(s, dict)),
                      key=lambda s: float(s.get("startBar", 0)))
        if secs:
            first = secs[0]
            if _sec_class(first.get("name")) == "intro" and len(secs) > 1:
                span = float(secs[1].get("startBar", 0)) -                     float(first.get("startBar", 0))
                if span > 8:
                    advisories.append({
                        "kind": "long_intro", "bars": int(span),
                        "why": (f"a {int(span)}-bar intro — the rap "
                                "ritual is 4-8 (the producer-tag slot); "
                                "the hook should arrive by bar 8")})
    return {"court": "ritual", "ok": True, "advisories": advisories}


def court_form_conformance(song, genre=""):
    import form_plan as FP
    secs = [s for s in (song or {}).get("sections", []) or []
            if isinstance(s, dict)]
    if len(secs) < 3:
        return {"court": "form_conformance", "ok": True, "advisories": [],
                "skipped": "needs >=3 sections"}
    fam = FP.family_for(str(genre or "") or "pop")
    tpl_classes = [_sec_class(n) for n, _ in FP.FORM_TEMPLATES[fam]]
    got_classes = [_sec_class(s.get("name")) for s in
                   sorted(secs, key=lambda s: float(s.get("startBar", 0)))]
    sim = _lcs(got_classes, tpl_classes) / max(len(tpl_classes), 1)
    advisories = []
    if sim < 0.5:
        advisories.append({
            "kind": "off_family_form", "similarity": round(sim, 2),
            "family": fam,
            "got": got_classes, "template": tpl_classes,
            "why": f"the section flow matches only {sim:.0%} of the "
                   f"{fam} family's canonical order — fine if "
                   "intentional; THE PLANNER's template is the "
                   "reference if not"})
    return {"court": "form_conformance", "ok": True,
            "advisories": advisories, "similarity": round(sim, 2),
            "family": fam}


def signature_tokens(genre):
    """The genre's instrument-token vocabulary from its KG node."""
    toks = set()
    try:
        import kg
        g = str(genre or "").lower().replace("'", "")
        rows = kg.KG().q(
            f"MATCH (x:Genre {{name: '{g}'}})-[r]->(y) "
            "WHERE type(r) IN ['USES_TECHNIQUE', 'CHARACTERIZED_BY'] "
            "RETURN y.name")
        for r in rows:
            if not (r and r[0]):
                continue
            parts = str(r[0]).lower().split("_")
            for tok in _INSTRUMENT_TOKENS:
                tp = tok.split("_")
                if any(parts[i:i + len(tp)] == tp
                       for i in range(len(parts))):
                    toks.add(tok)     # word-boundary law: 'oud' must
                                      # never match inside 'loudness' 
    except Exception:
        pass
    return toks


def court_signature(song, genre=""):
    toks = signature_tokens(genre)
    if not toks:
        return {"court": "signature", "ok": True, "advisories": [],
                "skipped": "no signature tokens banked for this genre"}
    blob = " ".join(
        (str(t.get("name", "")) + " "
         + str((t.get("source") or {}).get("id", "")))
        for t in (song or {}).get("tracks", []) or []
        if isinstance(t, dict)).lower()
    blob_parts = re.split(r"[^a-z0-9]+", blob)
    present = set()
    for t in toks:
        tp = t.split("_")
        boundary = any(blob_parts[i:i + len(tp)] == tp
                       for i in range(len(blob_parts)))
        # the compact fallback (logdrumlead) is for COMPOUND tokens
        # only — on short tokens it reopens the 'oud'-in-'loudness' hole
        compact = len(tp) > 1 and t.replace("_", "") in \
            blob.replace("_", "").replace(" ", "")
        if boundary or compact:
            present.add(t)
    advisories = []
    if not present:
        advisories.append({
            "kind": "no_signature_voice", "expected": sorted(toks),
            "why": f"none of the genre's signature voices "
                   f"({', '.join(sorted(toks))}) appear in the take — "
                   "the arrangement reads generic; land at least one"})
    return {"court": "signature", "ok": True, "advisories": advisories,
            "present": sorted(present), "expected": sorted(toks)}


if __name__ == "__main__":
    import sys as _s
    song = json.load(open(_s.argv[1]))
    g = _s.argv[2] if len(_s.argv) > 2 else ""
    print(json.dumps({"form": court_form_conformance(song, g),
                      "signature": court_signature(song, g)}, indent=1))
