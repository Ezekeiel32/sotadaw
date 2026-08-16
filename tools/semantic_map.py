#!/usr/bin/env python3
"""THE SEMANTIC MAP — producer words become measurable contracts
(wave 19; R-28 items 039/040/103/104/168/169/250).

The meta-study law (r-28 finding 0): a producer term has NO fixed
meaning — it resolves by EFFECT CONTEXT. 'Warm' on an EQ = +low-mids;
'warm' on the room = long decay + LP damping; 'warm' as gear character =
2nd-harmonic saturation at 0.5-2% THD. So the vocabulary binds
(term x effect-context x scope), never term alone.

Verdicts ride Saitis' three orthogonal tone axes (item 250):
LUMINANCE = spectral centroid, MASS = low-band energy share,
TEXTURE = roughness (unmeasured by analyze2 v3 — carried as None,
never guessed). Dynamic-family words (punchy/snappy/tight) route to the
CREST kernel, hard-separated from loudness (item 104: punchy is often
the OPPOSITE of loud; the W116 loudness pass is already PSR-braked).

Agreement gate (item 103, Social-EQ + meta-study): HIGH-agreement terms
verdict silently; LOW-agreement terms (open/hard/heavy/boxy) become
AMBIGUITIES — a one-tap ask-back, not a wrong render.

Anchors are CORPUS-CALIBRATED (self-measure 2026-07-15, 30 rendered
takes): full-mix centroid p10/p50/p90 = 1058/1982/5002 Hz; width
-37..0 dB (side/mid) with corr 1.0..-0.05; crest 5.6..17.3 dB. All
verdicts are DIRECTION-vs-anchor with dead-bands — never absolute
classes (a dark take in trap is a bright take in vaporwave).

De Man band table (aggregated across ~8 reference texts, r-28 f6):
air 10-20k · presence 2-6k · clarity 2.5-4k · warm/fat 50-250 ·
muddy 200-500 (cut) · boomy 100-200 · harsh ~3k · boxy 300-800 ·
nasal 1-1.5k. Ranges are PRIORS (~1 octave spread across texts).
"""
import re

# corpus anchors (self-measure law; see module docstring)
ANCHOR_CENTROID_HZ = 1982.0
ANCHOR_WIDTH_DB = -15.0
ANCHOR_CREST_DB = 9.0
ANCHOR_LOW_PCT = 55.0
ANCHOR_ROLLOFF_HZ = 270.0   # corpus p50 (wave 22 sweep, 29 masters)
DEADBAND = 0.15                 # fraction of anchor before a verdict fires
CORR_MONO_GUARD = 0.15          # r-28 f11: negative corr = mono-cancel risk

HIGH_AGREEMENT = frozenset((
    "distant", "clear", "tinny", "low", "dry", "deep", "bright",
    "resonant", "harsh", "dark", "metallic", "soft", "warm", "muddy",
    "boomy", "airy", "thin", "full", "fat", "wide", "narrow", "punchy",
    "snappy", "tight", "smooth", "crisp", "dull", "mellow", "muffled"))
LOW_AGREEMENT = frozenset(("open", "hard", "heavy", "boxy", "nasal",
                           "vintage", "analog", "lofi", "crunchy"))

# (term x effect-context) -> recipe; correlate/direction for the COURT.
# recipes are the deterministic HEAL guidance the next revision carries
# (LLM2Fx pattern: the agent applies them with measured features in hand).
VOCAB = {
    "bright": {
        "axis": "luminance", "correlate": "spectral_centroid_hz", "dir": +1,
        "contexts": {
            "eq": "lift presence/air (2-6k shelf +2..3dB, De Man); or "
                  "brighter voicing/register at the source",
            "reverb": "brighter tail: less LP damping on the space",
            "saturation": "odd-harmonic exciter, sparingly"},
        "sources": ["De Man table", "r-28 f2 centroid anchor"]},
    "dark": {
        "axis": "luminance", "correlate": "spectral_centroid_hz", "dir": -1,
        "contexts": {
            "eq": "tilt down: HF shelf -2..-4dB above ~6k, or darker "
                  "voicing (closed filter, lower register)",
            "reverb": "damped tail (LP ~4-6k on the space)"},
        "sources": ["De Man table", "r-28 f2"]},
    "warm": {
        "axis": "mass", "correlate": "low_pct", "dir": +1,
        "contexts": {
            "eq": "+low-mid body 100-500Hz +1.5..3dB (PRIMARY, r-28 f7); "
                  "gentle HF roll-off SECONDARY",
            "reverb": "longer decay + LP damping on the space",
            "saturation": "2nd-harmonic bias at 0.5-2% THD (fx_saturate "
                          "low drive, warm tone)"},
        "sources": ["r-28 f7 warm direction", "f9 THD contract"]},
    "muddy": {
        "axis": "mass", "correlate": "low_pct", "dir": +1, "unwanted": True,
        "contexts": {"eq": "CUT 200-500Hz 2..4dB on the offenders "
                           "(warm and muddy share the band — amount is "
                           "the disambiguator)"},
        "sources": ["De Man 200-500 cut"]},
    "boomy": {
        "axis": "mass", "correlate": "low_pct", "dir": +1, "unwanted": True,
        "contexts": {"eq": "cut 100-200Hz; shorten kick/808 decay"},
        "sources": ["De Man 100-200"]},
    "thin": {
        "axis": "mass", "correlate": "low_pct", "dir": -1, "unwanted": True,
        "contexts": {"eq": "add 100-250Hz body; double the bass an octave "
                           "down; check HP filters parked too high"},
        "sources": ["De Man warm/fat band"]},
    "full": {
        "axis": "mass", "correlate": "low_pct", "dir": +1,
        "contexts": {"eq": "+50-250Hz fat band, widen mid density"},
        "sources": ["De Man"]},
    "fat": {
        "axis": "mass", "correlate": "low_pct", "dir": +1,
        "contexts": {"eq": "+50-250Hz; saturate the low-mids gently",
                     "saturation": "2nd-harmonic + slight comp"},
        "sources": ["De Man"]},
    "harsh": {
        "axis": "luminance", "correlate": "spectral_centroid_hz",
        "dir": +1, "unwanted": True,
        "contexts": {"eq": "cut ~3k (2.5-4k) 2..4dB; soften attack "
                           "velocities; avoid odd-harmonic drive"},
        "sources": ["De Man ~3k harsh"]},
    "airy": {
        "axis": "luminance", "correlate": "spectral_centroid_hz", "dir": +1,
        "contexts": {"eq": "+10-20k air shelf +1.5..3dB",
                     "reverb": "bright shimmer tail"},
        "sources": ["De Man air band"]},
    "clear": {
        "axis": "luminance", "correlate": "spectral_centroid_hz", "dir": +1,
        "contexts": {"eq": "+2.5-4k clarity; CUT 200-500 mud first"},
        "sources": ["De Man clarity"]},
    "punchy": {
        "axis": "dynamics", "correlate": "crest_factor_db", "dir": +1,
        "contexts": {"dynamics": "transient PRESERVATION: comp attack "
                                 "20-30ms / release 50-100ms (let the hit "
                                 "through); NEVER more limiting — punch is "
                                 "the opposite of loud (r-28 f5)"},
        "sources": ["r-28 f5 crest kernel"]},
    "snappy": {
        "axis": "dynamics", "correlate": "crest_factor_db", "dir": +1,
        "contexts": {"dynamics": "transient attack boost; shorten decays; "
                                 "comp attack 20-30ms"},
        "sources": ["r-28 f5"]},
    "tight": {
        "axis": "dynamics", "correlate": "crest_factor_db", "dir": +1,
        "contexts": {"dynamics": "shorten releases/decays; gate the tail; "
                                 "kick+bass interlock (see lowend court)"},
        "sources": ["r-28 f5"]},
    "wide": {
        "axis": "width", "correlate": "stereo_width_db", "dir": +1,
        "contexts": {"stereo": "raise side gain ABOVE 200Hz (fx_widen / "
                               "ms_eq side_high); Haas or detune doubles; "
                               "SUB STAYS MONO; corr must stay > "
                               f"{CORR_MONO_GUARD} (mono-compat guard)"},
        "sources": ["r-28 f11: 15-55% side above 200Hz"]},
    "narrow": {
        "axis": "width", "correlate": "stereo_width_db", "dir": -1,
        "contexts": {"stereo": "reduce side gain; mono the low-mids"},
        "sources": ["r-28 f11"]},
    "dry": {
        "axis": "space", "correlate": None, "dir": -1,
        "contexts": {"reverb": "less send/decay; kill long tails"},
        "sources": ["meta-study high-agreement"]},
    "distant": {
        "axis": "space", "correlate": None, "dir": +1,
        "contexts": {"reverb": "more pre-delay+decay, darker tail, "
                               "lower direct level"},
        "sources": ["meta-study"]},
    "deep": {
        "axis": "mass", "correlate": "low_pct", "dir": +1,
        "contexts": {"eq": "+sub/low body; octave-down layer",
                     "reverb": "longer, darker space"},
        "sources": ["meta-study"]},
    "soft": {
        "axis": "luminance", "correlate": "spectral_centroid_hz", "dir": -1,
        "contexts": {"eq": "roll top gently; lower velocities; slower "
                           "attacks at the source"},
        "sources": ["meta-study"]},
    "vintage": {
        "axis": "character", "correlate": None, "dir": +1,
        "contexts": {"saturation": "2nd-harmonic 0.5-2% THD (UREI 1176 "
                                   "~0.5%); gentle HF roll; wow/flutter "
                                   "if tape is meant — odd harmonics "
                                   "read HARSH, not vintage (r-28 f9)"},
        "sources": ["r-28 f9 THD contract"]},
}
for _t in ("analog", "lofi"):
    VOCAB[_t] = dict(VOCAB["vintage"], sources=VOCAB["vintage"]["sources"])
VOCAB["mellow"] = dict(VOCAB["soft"])
VOCAB["muffled"] = dict(VOCAB["dark"], unwanted=True)
VOCAB["dull"] = dict(VOCAB["dark"], unwanted=True)
VOCAB["crisp"] = dict(VOCAB["bright"])
# LOW-agreement words carry a DEFAULT reading (the recipe the take rides
# if the user doesn't answer the ask-back) — never a confident verdict.
VOCAB["boxy"] = {
    "axis": "mass", "correlate": None, "dir": +1, "unwanted": True,
    "contexts": {"eq": "cut 300-800Hz (De Man boxy band) on the "
                       "offending lane"},
    "sources": ["De Man 300-800", "Social-EQ low agreement"]}
VOCAB["nasal"] = {
    "axis": "luminance", "correlate": None, "dir": +1, "unwanted": True,
    "contexts": {"eq": "cut ~1-1.5k (De Man nasal band)"},
    "sources": ["De Man 1-1.5k"]}
VOCAB["open"] = {
    "axis": "width", "correlate": None, "dir": +1,
    "contexts": {"eq": "lift air 10k+ / reduce 300-800 congestion",
                 "stereo": "more side above 200Hz",
                 "reverb": "shorter pre-delay, brighter early space"},
    "sources": ["Social-EQ low agreement"]}
VOCAB["heavy"] = {
    "axis": "mass", "correlate": None, "dir": +1,
    "contexts": {"eq": "+low-mid mass; layer the low octave",
                 "saturation": "denser drive on the low-mids",
                 "dynamics": "slower comp release, thicker sustain"},
    "sources": ["Social-EQ low agreement"]}

_SCOPES = (
    ("vocal", ("vocal", "vox", "voice", "singer", "topline")),
    ("drums", ("drum", "kick", "snare", "hat", "perc", "kit")),
    ("bass", ("bass", "808", "sub", "low end", "lowend")),
    ("lead", ("lead", "synth", "melody", "keys", "pad", "guitar", "piano")),
    ("master", ("master", "mix", "overall", "whole", "everything", "track",
                "song", "it")),
)
_CTX_WORDS = (
    ("reverb", ("reverb", "room", "space", "hall", "echo", "tail",
                "ambience", "verb")),
    ("saturation", ("saturat", "distort", "drive", "tape", "tube", "gear",
                    "grit", "crunch", "character")),
    ("dynamics", ("compress", "punch", "transient", "attack", "dynamics",
                  "slam", "smack")),
    ("stereo", ("wide", "width", "stereo", "narrow", "mono", "image",
                "spread")),
)
_MORE = ("more", "extra", "very", "super", "really", "make it", "add")
_LESS = ("less", "not too", "too", "reduce", "remove", "kill the", "no ")


def _scope_of(text, term_pos):
    """Nearest scope word to the term (window +-40 chars), else master."""
    lo, hi = max(0, term_pos - 40), term_pos + 40
    win = text[lo:hi]
    best = "master"
    bestd = 999
    for scope, keys in _SCOPES:
        for k in keys:
            i = win.find(k)
            if i >= 0:
                d = abs((lo + i) - term_pos)
                if d < bestd:
                    best, bestd = scope, d
    return best


def _context_of(text, term_pos):
    lo, hi = max(0, term_pos - 50), term_pos + 50
    win = text[lo:hi]
    for ctx, keys in _CTX_WORDS:
        if any(k in win for k in keys):
            return ctx
    return "eq"


def _direction_mod(text, term_pos):
    """'less bright' / 'too bright' flip the requested direction."""
    pre = text[max(0, term_pos - 24):term_pos]
    if any(w in pre for w in _LESS):
        return -1
    return +1


def contract(ask, genre="", song=None):
    """Item 039: the three-tier contract. Hard targets stay the
    instruction court's law (this fills the schema for callers);
    semantic goals + references + ambiguities are THIS map's law."""
    text = str(ask or "").lower()
    goals, ambiguities = [], []
    seen = set()
    for term, spec in VOCAB.items():
        # comparative morphology incl. y->i ('dry' matches 'drier',
        # 'muddy' matches 'muddier')
        pat = rf"\b{re.escape(term)}(er|est|ish|ness)?\b"
        if term.endswith("y"):
            pat = (rf"\b(?:{re.escape(term)}(ish|ness)?"
                   rf"|{re.escape(term[:-1])}i(?:er|est))\b")
        for m in re.finditer(pat, text):
            key = (term, m.start() // 60)
            if key in seen:
                continue
            # 'full' the LENGTH word is not 'full' the TONE word
            # (telemetry wolf 2026-07-15: 'full length' / 'FULL 10
            # MINUTE' / 'full song' were the majority of matches)
            if term == "full" and re.match(
                    r"\s*[-–]?\s*(length|song|track|version|album|set|"
                    r"arrangement|mix\b|\d)", text[m.end():]):
                continue
            # ESTABLISHED COMPOUND GENRE NAMES only ('deep house' is a
            # genre, not a mass ask) — never a blanket adjective+genre
            # guard: 'punchy techno' and 'bright house' ARE tone asks,
            # and 'dark trap' carries real tone intent alongside the
            # style (the battery's own case drew this line)
            nxt = re.match(r"\s+([a-z]+)", text[m.end():])
            if nxt and (term, nxt.group(1)) in {
                    ("deep", "house"), ("hard", "techno"),
                    ("hard", "house"), ("hard", "trance"),
                    ("heavy", "metal"), ("hard", "rock"),
                    ("dark", "ambient")}:
                continue
            seen.add(key)
            scope = _scope_of(text, m.start())
            ctx = _context_of(text, m.start())
            want_dir = spec["dir"] * _direction_mod(text, m.start())
            if spec.get("unwanted"):
                # naming a flaw asks for its REMOVAL: "muddy" => less mass
                want_dir = -abs(spec["dir"])
            goal = {"term": term, "scope": scope, "effect_context": ctx,
                    "axis": spec["axis"], "correlate": spec["correlate"],
                    "direction": want_dir,
                    "agreement": ("high" if term in HIGH_AGREEMENT
                                  else "low"),
                    "recipe": spec["contexts"].get(
                        ctx, next(iter(spec["contexts"].values()))),
                    "sources": spec["sources"]}
            if goal["agreement"] == "low":
                ambiguities.append({
                    "term": term, "scope": scope,
                    "resolved_by": f"defaulted to {ctx} reading",
                    "ask_back": True,
                    "why": f"'{term}' is a LOW-agreement word (Social-EQ) "
                           "— confirm the intent or it rides the default"})
            goals.append(goal)
    refs = []
    for m in re.finditer(r"(?:like|in the style of|sounds? like)\s+"
                         r"([a-z0-9' ]{2,32}?)(?:[,.;]|$| but| with| and )",
                         text):
        refs.append({"like": m.group(1).strip(),
                     "extract": ["spectral_balance", "lufs", "lra",
                                 "width", "tempo", "key"]})
    return {"semantic_goals": goals, "references": refs,
            "ambiguities": ambiguities}


def _low_pct(analysis):
    bands = (analysis or {}).get("band_energy_pct") or {}
    tot = 0.0
    for k, v in bands.items():
        kl = k.lower()
        if ("sub" in kl or "low" in kl) and "mid" not in kl:
            try:
                tot += float(v)
            except Exception:
                pass
    return tot if bands else None


def saitis_axes(analysis):
    """Item 250: the 3 orthogonal tone axes. texture stays None until a
    roughness meter exists — never guessed."""
    a = analysis or {}
    return {"luminance_hz": a.get("spectral_centroid_hz"),
            "mass_low_pct": _low_pct(a),
            "texture_roughness": None}


def verdict_semantics(goals, analysis, genre=""):
    """Verdict each measurable goal vs the corpus anchors (direction with
    dead-band). Unmeasurable axes return got='unmeasured' and stay ok
    (advisory posture — never convict blind)."""
    a = analysis or {}
    out = []
    for g in goals:
        cor = g.get("correlate")
        want = f"{g['term']} ({'+' if g['direction'] > 0 else '-'}"\
               f"{g['axis']})"
        if not cor:
            out.append({"kind": f"semantic:{g['term']}", "want": want,
                        "got": "unmeasured", "ok": True,
                        "note": g["recipe"]})
            continue
        # item 232 (wave 22): at MASTER scope, brightness verdicts on
        # 85% ROLL-OFF when measured — sub mass drags centroid the WRONG
        # way on full mixes (electronic reads darker than rock by
        # centroid while being brighter by roll-off).
        if cor == "spectral_centroid_hz" and g.get("scope") == "master" \
                and a.get("rolloff_85_hz") is not None:
            cor = "rolloff_85_hz"
        got = a.get(cor) if cor != "low_pct" else _low_pct(a)
        if got is None:
            out.append({"kind": f"semantic:{g['term']}", "want": want,
                        "got": "unmeasured", "ok": True,
                        "note": g["recipe"]})
            continue
        anchor = {"spectral_centroid_hz": ANCHOR_CENTROID_HZ,
                  "stereo_width_db": ANCHOR_WIDTH_DB,
                  "crest_factor_db": ANCHOR_CREST_DB,
                  "rolloff_85_hz": ANCHOR_ROLLOFF_HZ,
                  "low_pct": ANCHOR_LOW_PCT}[cor]
        band = abs(anchor) * DEADBAND
        if g["direction"] > 0:
            ok = float(got) >= anchor - band
        else:
            ok = float(got) <= anchor + band
        row = {"kind": f"semantic:{g['term']}", "want": want,
               "got": round(float(got), 1), "ok": bool(ok),
               "note": g["recipe"] if not ok else ""}
        # the mono-compat guard rides every WIDE verdict (r-28 f11)
        if g["term"] == "wide" and a.get("lr_correlation") is not None \
                and float(a["lr_correlation"]) < CORR_MONO_GUARD:
            row["ok"] = False
            row["note"] = ("L/R correlation "
                           f"{float(a['lr_correlation']):.2f} < "
                           f"{CORR_MONO_GUARD} — width built on phase "
                           "cancels in mono; " + row.get("note", ""))
        out.append(row)
    return out


def main():
    import argparse
    import json
    ap = argparse.ArgumentParser(description="THE SEMANTIC MAP (wave 19)")
    ap.add_argument("ask")
    ap.add_argument("--genre", default="")
    ap.add_argument("--analysis", default=None,
                    help="path to an analyze2 json to verdict against")
    args = ap.parse_args()
    c = contract(args.ask, args.genre)
    if args.analysis:
        a = json.load(open(args.analysis))
        c["verdicts"] = verdict_semantics(c["semantic_goals"], a, args.genre)
        c["saitis"] = saitis_axes(a)
    print(json.dumps(c, indent=1))
    return 0


if __name__ == "__main__":
    main()
