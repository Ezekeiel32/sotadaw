#!/usr/bin/env python3
"""THE LOOP GENERATOR — genre in, complete editable loop out. Knowledge-backed:
drums from the genre's PatternArchetype grid (KG), bass from its bass_style in
its common key, color pad from its SoundRecipe voice, groove/swing applied,
sub-dominant-aware master. Deterministic per seed; different seeds = different
musical choices from the same DNA.

  loop_gen.py <genre> <name> [--bars 4] [--seed 0] [--bpm N] [--key "A minor"]
"""
import argparse, json, math, os, random, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG, esc, eligible_recipe_voice

DNA_CACHE = os.path.join(ROOT, "agent", "dna_cache.json")
PALETTES_PATH = os.path.join(ROOT, "library", "palettes.json")
PLUGIN_CACHE = os.path.join(ROOT, "app", "plugins_cache.xml")
_PAL = {"loaded": False, "data": {}, "scanned": None}


def _palettes():
    """Load library/palettes.json once (offline-safe: {} if absent)."""
    if not _PAL["loaded"]:
        _PAL["loaded"] = True
        try:
            _PAL["data"] = json.load(open(PALETTES_PATH))
        except Exception:
            _PAL["data"] = {}
    return _PAL["data"]


def _plugin_installed(plugin):
    """True if a scanned VST matches `plugin` (SongLoader's containsIgnoreCase
    rule) AND it is not crash-quarantined (a quarantined source renders SILENT —
    the engine skips it with only a stderr warning; the pad must never die mute).
    Offline-safe: no scan cache -> False -> Faust fallback."""
    if _PAL["scanned"] is None:
        try:
            _PAL["scanned"] = open(PLUGIN_CACHE, encoding="utf-8",
                                   errors="ignore").read().lower()
        except Exception:
            _PAL["scanned"] = ""
        try:
            q = json.load(open(os.path.expanduser(
                "~/.config/sotadaw/plugin_quarantine.json")))
            _PAL["quarantined"] = {str(x).lower() for x in q}
        except Exception:
            _PAL["quarantined"] = set()
    if plugin.lower() in _PAL.get("quarantined", set()):
        return False
    return plugin.lower() in _PAL["scanned"]


def resolve_color_source(voice):
    """PALETTES v2: a KG vst3:<plugin> SoundRecipe voice becomes a render-
    verified factory source when the plugin is an installed INSTRUMENT (present
    in palettes.json); otherwise a Faust pad — so a reverb voice (vst3:Dragonfly)
    and offline boxes never render a SILENT color layer (the old bug: this field
    was blindly wrapped kind:"faust" -> Faust JIT miss -> dead signature synth)."""
    if isinstance(voice, str) and voice.startswith("vst3:"):
        plugin = voice[5:]
        pal = _palettes()
        entry = pal.get("by_plugin", {}).get(plugin)
        if entry and _plugin_installed(plugin):
            return dict(entry["source"])
        return {"kind": "faust", "id": pal.get("fallback_voice", "pad_motion")}
    return {"kind": "faust", "id": voice}


def genre_dna(genre):
    """Everything generate() needs, as one dict. LIVE GRAPH first (dev box =
    curation truth), baked agent/dna_cache.json second — MAKE must work
    identically on machines with no FalkorDB, no falkordb lib, no venv
    (the Inspiron lesson). SOTADAW_NO_KG=1 forces the cache (parity tests).
    Returns (dna, err) — exactly one is None."""
    if os.environ.get("SOTADAW_NO_KG") != "1":
        try:
            kg = KG()
            row = kg.q(f"MATCH (g:Genre {{name: '{esc(genre)}'}})-[:CHARACTERIZED_BY]->(p:PatternArchetype) "
                       f"WHERE p.grid IS NOT NULL RETURN p.name, p.grid, g.bpm_lo, g.bpm_hi, g.common_key")
            if not row:
                return None, (f"no executable PatternArchetype for '{genre}' — loop DNA exists for: "
                              + ", ".join(r[0] for r in kg.q(
                                  "MATCH (g:Genre)-[:CHARACTERIZED_BY]->(p:PatternArchetype) "
                                  "WHERE p.grid IS NOT NULL RETURN g.name ORDER BY g.name")))
            pname, gjson, lo, hi, gkey = row[0]
            # THE TASTE LAW (2026-07-12): first ELIGIBLE voice — drum-zone
            # recipes (snare_zones/hat_zones/kick_*) once handed boombap's
            # chord lane a SNARE. kg.eligible_recipe_voice is the one predicate
            # (cache export applies the same law — the two-path DNA rule).
            rec = [r for r in kg.q(
                       f"MATCH (g:Genre {{name: '{esc(genre)}'}})-[:CHARACTERIZED_BY]->(r:SoundRecipe) "
                       f"WHERE r.voice IS NOT NULL RETURN r.voice")
                   if r and eligible_recipe_voice(r[0])][:1]
            mix = kg.q(f"MATCH (g:Genre {{name: '{esc(genre)}'}})-[:TARGETS]->(m:MixTarget) "
                       f"RETURN m.band_order, m.lufs_lo")
            grv = kg.q(f"MATCH (g:Genre {{name: '{esc(genre)}'}})-[:HAS_GROOVE]->(gr:Groove) "
                       f"RETURN gr.name LIMIT 1")
            if not grv:   # INHERIT the parent's signature feel (one hop, like the
                # inherited techniques in kg.genre_dna): a subgenre with no own
                # groove grooves like its parent (death_metal <- metal), never a
                # dead grid. Direct edge wins; this only fills the gap.
                grv = kg.q(f"MATCH (g:Genre {{name: '{esc(genre)}'}})-[:SUBGENRE_OF]->"
                           f"(:Genre)-[:HAS_GROOVE]->(gr:Groove) RETURN gr.name LIMIT 1")
            vc = kg.q(f"MATCH (g:Genre {{name:'{esc(genre)}'}}) WHERE g.voicing IS NOT NULL "
                      "RETURN g.voicing")
            return {"archetype": pname, "grid": json.loads(gjson), "bpm_lo": lo, "bpm_hi": hi,
                    "key": gkey, "voice": rec[0][0] if rec and rec[0] else None,
                    "band_order": mix[0][0] if mix and mix[0] else None,
                    "lufs_lo": mix[0][1] if mix and mix[0] and len(mix[0]) > 1 else None,
                    "voicing": json.loads(vc[0][0]) if vc and vc[0] and vc[0][0] else None,
                    "groove": grv[0][0] if grv and grv[0] else None}, None
        except Exception:
            pass                                   # no graph on this machine -> baked DNA
    try:
        cached = json.load(open(DNA_CACHE))["genres"]
    except Exception as e:
        return None, (f"no knowledge graph AND no baked DNA ({e!r}) — "
                      "run tools/kg_export_cache.py on the dev box and ship agent/dna_cache.json")
    if genre not in cached:
        return None, f"no loop DNA for '{genre}' — available: " + ", ".join(sorted(cached))
    g = cached[genre]
    return {"archetype": g.get("archetype"), "grid": g["grid"], "bpm_lo": g.get("bpm_lo"),
            "bpm_hi": g.get("bpm_hi"), "key": g.get("key"), "voice": g.get("voice"),
            "band_order": g.get("band_order"), "lufs_lo": g.get("lufs_lo"),
            "voicing": g.get("voicing"),
            "groove": g.get("groove")}, None

NOTE_PC = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5,
           "F#": 6, "Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11}

# THE HARMONIC JOURNEY's section moves (W15) — THE ONE KERNEL: arrange applies
# these in degree space; musicality scores against the same shifted field.
# Re-implementing either side is the drifted-mirror bug.
SEC_SHIFT = {"chorus": 2, "drop": 2, "bridge": -2, "break": -2}


def journey_bar_shifts(plan, total_bars, deg_of_bar=None):
    """Per-bar degree shift for a section plan [(name, bars), ...]:
    chorus/drop +2, bridge/break -2, and the TURNAROUND -1 on the bar before
    every later drop/chorus. Exactly arrange's W15 field.
    W34 THE FIVE GOES HOME: when deg_of_bar (bar -> BASE degree, unshifted)
    is given and SOTADAW_FIVE != 0, the FINAL arrival's turnaround bar
    resolves to the absolute V (shift = 5 - base degree) — the dominant
    approach into the last statement. Kernel-owned so arrange and the ruler
    can never drift apart."""
    shifts = [0] * (total_bars + 2)
    acc = 0
    for sec, bn in plan:
        sh = SEC_SHIFT.get(sec.rstrip("0123456789"), 0)
        if sh:
            for b in range(acc, min(acc + bn, total_bars + 2)):
                shifts[b] = sh
        acc += bn
    acc = 0
    for i, (sec, bn) in enumerate(plan):
        if i > 0 and sec.rstrip("0123456789") in ("drop", "chorus"):
            shifts[acc - 1] = -1
        acc += bn
    if deg_of_bar is not None and os.environ.get("SOTADAW_FIVE", "1") != "0":
        fin, acc = None, 0
        for i, (sec, bn) in enumerate(plan):
            if i > 0 and sec.rstrip("0123456789") in ("drop", "chorus"):
                fin = acc - 1
            acc += bn
        if fin is not None and 0 <= fin < len(shifts):
            shifts[fin] = 5 - int(deg_of_bar(fin))
    return shifts


def sections_to_plan(sections, length_bars):
    """song.sections [{name,startBar}] -> [(name, bars)] plan form."""
    plan = []
    for i, s in enumerate(sections):
        b1 = sections[i + 1]["startBar"] if i + 1 < len(sections) else length_bars
        plan.append((s["name"], int(b1 - s["startBar"])))
    return plan

# ---- GENRE HARMONY/TEXTURE FAMILIES (in-code v1; graduate to KG fields once
# proven — the KG-field law wants BOTH query+cache paths, this map needs neither).
# Extensions are DIATONIC degrees (7th = deg+6, 9th = deg+1) so the KEY law holds.
EXT_SEVENTH = {"house", "deep_house", "deephouse", "tech_house", "lofi", "lofi_hiphop",
               "neo_soul", "neosoul", "jazz", "jazz_fusion", "gospel", "soul", "funk",
               "disco", "nu_disco", "nudisco", "rnb", "citypop", "bossanova", "bossa",
               "ukgarage", "garage", "2step", "amapiano", "future_funk", "futurefunk",
               "acid_jazz", "boogie", "motown", "philly_soul", "yacht_rock",
               # dr27 (2026-07-12): the BOP FAMILY was missing from its own
               # law — bebop/blues rendered plain triads (blues with no
               # dominant 7th is not blues). "jazzfusion" is the cache
               # spelling; "jazz_fusion" above never matched it.
               "bebop", "hard_bop", "modal_jazz", "spiritual_jazz", "free_jazz",
               "jazzfusion", "blues", "swing_bigband", "ethio_jazz", "swing"}
EXT_ADD9 = {"synthwave", "trance", "ambient", "chillwave", "dreampop", "synthpop",
            "berlin_school", "italo", "italo_disco", "progressive_house", "chillout",
            "downtempo", "shoegaze", "vaporwave", "melodic_techno", "hypnagogic"}
# genres whose records live on a running arpeggio texture
ARP_GENRES = {"synthwave", "trance", "italo", "italo_disco", "berlin_school",
              "synthpop", "eurodance", "progressive_house", "melodic_techno",
              "edm", "bigroom", "electro", "hi_nrg", "new_wave", "vaporwave"}
# sidechain-pump genres (gated additionally on an actual 4-on-floor kick grid)
PUMP_GENRES = {"house", "deep_house", "deephouse", "tech_house", "techno", "trance",
               "edm", "bigroom", "electro", "electro_house", "eurodance", "synthwave",
               "future_funk", "futurefunk", "french_house", "frenchhouse", "nu_disco",
               "nudisco", "melodic_techno", "progressive_house", "hardstyle", "italo",
               "italo_disco", "slap_house", "amapiano"}
# HARMONIC-RHYTHM LAW: the color lane ARTICULATES per genre family — house/disco
# families chop offbeat-8th stabs (the organ/piano stab IS the genre), reggae
# families skank on 2 & 4 (the afterbeat chop), everything else holds pads.
STAB_GENRES = {"house", "deep_house", "deephouse", "tech_house", "chicago_house",
               "jackin_house", "french_house", "frenchhouse", "filter_house",
               "garage_house", "acid_house", "tribal_house", "funky_house",
               "gospel_house", "piano_house", "slap_house", "electro_house",
               "disco", "nu_disco", "nudisco", "hi_nrg", "eurodance",
               "ukgarage", "garage", "2step", "speed_garage", "bassline",
               "uk_funky", "ska", "boogie"}
# W61 THE CHUG: metal-family rhythm guitars run a constant 8th wall (palm-
# muted power chords) — the held-bed articulation read as sparse pads.
# (doom/sludge/post/stoner ride SUSTAINED riffs — the held bed IS their
# wall; the chug fits the fast families)
CHUG_GENRES = {"metal", "djent", "metalcore", "nu_metal", "black_metal",
               "death_metal", "grunge", "punk", "post_punk"}
SKANK_GENRES = {"reggae", "roots_reggae", "rocksteady", "dub", "lovers_rock",
                "reggae_fusion",
                # W72: dancehall rides the same afterbeat skank (its riddims
                # are reggae's children); its color voice arrives by seed
                "dancehall"}
# vocal-chop cultures: the pitched vocal stab IS the genre furniture
CHOP_GENRES = {"house", "deephouse", "deep_house", "ukgarage", "garage", "2step",
               "speed_garage", "bassline", "future_garage", "garage_house",
               "french_house", "filter_house", "jackin_house", "uk_funky"}
# stage law: every lane gets a HOME on the stereo stage at birth (kick/snare/bass
# center — the mono spine); numbers are modest, mono-compat proven by lr_correlation.
LANE_PAN = {"hat": 0.22, "openhat": -0.18, "ride": 0.30, "rim": -0.20,
            "clap": 0.08, "ghost": -0.12, "lead": 0.08, "arp": -0.18}


def four_on_floor(kick_steps):
    """Data-true 4-on-the-floor: the grid itself says so (no genre guessing)."""
    return {0, 4, 8, 12} <= {int(s) % 16 for s in (kick_steps or [])}


# voices with a detune zone -> (left value, right value); the two sides run
# genuinely DIFFERENT oscillator spreads = real double-tracking decorrelation
# (two instances with identical params render the identical signal = mono +6dB).
DOUBLE_DETUNE = {"supersaw": (0.014, 0.026), "supersaw_fat": (0.014, 0.026),
                 "pad_motion": (0.005, 0.011), "keys_dark": (0.003, 0.006)}
DOUBLE_ALT = {"pluck2": ("tone", 4600.0, 5800.0),  # no detune: timbre-split L/R
              # W68: the Leslie split — each side a different rotor speed
              # (house organ was MONO; a pair decorrelates over time)
              "organ_soul": ("speed", 4.8, 6.6),
              # W73: the hammond has a literal leslie zone — the whole
              # skank family (reggae/dub/rocksteady/dancehall fallback)
              # was shipping a MONO organ bed
              "hammond_organ": ("leslie", 0.35, 0.7),
              # W70 THE ENSEMBLE SPLITS: records-true pairs ONLY —
              # double-tracked guitars (the wall), detuned ensembles,
              # synth plucks, choir stacks, synth bells/pads. Solo horns/
              # keys/mallets (sax_reed, flute, rhodes, marimba, oud...)
              # stay MONO by genre truth (the reggaeton law).
              # "pluck" deliberately ABSENT: it voices solo-player guitars
              # (bachata requinto, bossa nylon, bluegrass flatpick) — a
              # doubled pair is genre-false there (the reggaeton law).
              "highgain_guitar": ("mids", -0.35, 0.25),  # two-amp trick
              "fuzz_guitar": ("scoop", 0.4, 0.7),
              "guitar_grit": ("damp", 5800.0, 8400.0),
              "clean_chime_guitar": ("chorus", 0.35, 0.65),
              "strings_disco": ("lush", 0.0028, 0.005),
              "strings_stacc": ("bite", 0.12, 0.26),
              "sax_section": ("vibrato", 0.013, 0.024),
              "formant_vox": ("breath", 0.08, 0.2),
              "fmbell": ("bright", 1.0, 1.5),
              "vox_pad": ("shimmer", 0.03, 0.06)}

# THE COLOR CHARACTER (W12): the pad's knobs are a genre statement — same
# voice, family-set zones (the chop-lane params precedent; measured spread
# −17%..+14% centroid + 5.6x sweep-rate range on pad_motion). stereo_double
# overrides ONLY detune afterward (decorrelation law outranks). Unlisted
# genres keep the voice defaults — zero churn outside these families.
_PAD_OPEN = ("house", "deephouse", "chicago_house", "disco", "nu_disco",
             "garage_house", "piano_house", "gospel_house", "boogie")
_PAD_TIGHT = ("techno", "hard_techno", "minimal_techno", "ebm", "industrial",
              "detroit_techno")
_PAD_BLOOM = ("ambient", "berlin_school", "drone", "chillout", "downtempo",
              "dungeon_synth", "post_rock", "shoegaze", "dreampop")
_PAD_DUSK = ("dub", "reggae", "rocksteady", "roots_reggae", "triphop",
             "dub_techno", "lovers_rock", "trap", "drill", "phonk",
             "memphis_rap", "hiphop", "boombap")
_PAD_RETRO = ("synthwave", "darksynth", "trance", "italo_disco", "eurodance",
              "synthpop", "new_wave")


def color_character(genre, voice):
    """Per-family zone params for the color lane; {} = keep the voice defaults."""
    g = (genre or "").lower()
    if voice == "pad_motion":
        if g in _PAD_OPEN:
            return {"depth": 2600.0, "motion": 0.16, "detune": 0.012}
        if g in _PAD_TIGHT:
            return {"depth": 1300.0, "motion": 0.28, "detune": 0.006}
        if g in _PAD_BLOOM:
            return {"depth": 3200.0, "motion": 0.05, "detune": 0.016, "drift": 0.04}
        if g in _PAD_DUSK:
            return {"depth": 950.0, "motion": 0.07, "detune": 0.010}
        if g in _PAD_RETRO:
            return {"depth": 2400.0, "motion": 0.09, "detune": 0.014}
    if voice == "keys_dark":
        if g in ("jazz", "bebop", "neo_soul", "soul", "motown", "rnb", "blues"):
            return {"cutoff": 950.0, "sub": 0.35, "detune": 0.006}    # warm, round
        if g in _PAD_DUSK:
            return {"cutoff": 520.0, "sweep": 1400.0}                 # darker still
    return {}


def hook_notes(cell, lead_bars, iv, root, base_oct, deg_at, bars, rng,
               seventh=False):
    """THE HOOK ENGINE (W14): melody with INTENT instead of a seeded walk —
    the human verdict on 13 mix-waves was "still sucks"; the gap was HERE.
    The genre's cell (grid lead steps) keeps its RHYTHM — identity — but the
    pitches are AIMED: chord tones own the strong beats, weak notes approach
    the next anchor by step (passing tones fill thirds), each phrase CADENCES
    onto its chord and the B phrase onto the NEXT group's chord (the pull that
    makes a loop breathe), ONE climax per 4-phrase plan reaches the window top
    (records put the peak late), and the performance layer rides the contour
    (crescendo into the peak, phrase-final breath, legato through stepwise
    runs). Plan A A' A B = call, varied call, call, answer (B inverts the
    contour). Scale-degree arithmetic only — the KEY law holds by
    construction. Deterministic per rng. Returns note dicts."""
    cell = sorted(([int(st), max(1, min(15, int(dg))), float(ln)]
                   for st, dg, ln in cell), key=lambda e: e[0])
    if not cell:
        return []
    phrase16 = lead_bars * 16
    n_groups = max(1, bars // lead_bars)
    shape = rng.choice(("arch", "ramp", "valley"))
    lo_d, hi_d = 1, 11                          # melodies live within ~a tenth
    climax_phrase = 3 if n_groups >= 4 else n_groups - 1
    kinds = ("A", "A2", "A", "B")

    def contour(x):
        if shape == "arch":
            return math.sin(math.pi * x)
        if shape == "ramp":
            return x
        return 1.0 - 0.8 * math.sin(math.pi * x)   # valley: high ends, dip mid

    def ctones(cdeg):
        base = [cdeg, cdeg + 2, cdeg + 4] + ([cdeg + 6] if seventh else [])
        out = set()
        for d in base:
            for k in (-7, 0, 7):
                if lo_d <= d + k <= hi_d + 1:
                    out.add(d + k)
        return sorted(out)

    def nearest(cands, target, top=None):
        pool = [c for c in cands if top is None or c <= top] or cands
        return min(pool, key=lambda c: (abs(c - target), c))

    notes = []
    for g in range(n_groups):
        kind = kinds[g % 4] if n_groups >= 2 else "A"
        ev = [list(e) for e in cell]
        if kind == "A2" and len(ev) >= 3:       # ONE variation, not a reroll
            i = 1 + (g // 4 + len(ev)) % (len(ev) - 2)
            ev[i][1] = max(1, min(15, ev[i][1] + rng.choice((-2, 2))))
        bar0 = g * lead_bars

        def plan_pos(st):
            return (g % 4 + st / phrase16) / float(min(4, n_groups))

        # pass 1 — ANCHORS: strong beats + the phrase final take chord tones
        anchors = {}
        for i, (st, dg, ln) in enumerate(ev):
            final = i == len(ev) - 1
            if not (st % 4 == 0 or final):
                continue
            h = contour(plan_pos(st))
            if kind == "B":
                h = 1.0 - h                     # the ANSWER inverts the call
            tdeg = lo_d + h * (hi_d - lo_d)
            bar = bar0 + st // 16
            cdeg = deg_at(bar + lead_bars) if (final and kind == "B") else deg_at(bar)
            anchors[i] = nearest(ctones(cdeg), tdeg, top=hi_d - 2)
        # THE CLIMAX: one anchor in the late phrase owns the window top
        if anchors and n_groups >= 2 and g % 4 == climax_phrase % 4:
            ci = max(anchors, key=lambda i: anchors[i])
            anchors[ci] = max(ctones(deg_at(bar0 + ev[ci][0] // 16)))
        # pass 2 — weak notes APPROACH the next anchor (passing tones fill thirds)
        a_idx = sorted(anchors)
        for i, (st, dg, ln) in enumerate(ev):
            if i in anchors:
                continue
            nxt = next((j for j in a_idx if j > i), None)
            prv = max((j for j in a_idx if j < i), default=None)
            if nxt is not None:
                t = anchors[nxt]
                if prv is not None and abs(anchors[prv] - t) == 2:
                    ev[i][1] = (anchors[prv] + t) // 2
                else:
                    ev[i][1] = max(lo_d, min(hi_d, t + rng.choice((-1, 1))))
            elif prv is not None:
                ev[i][1] = max(lo_d, min(hi_d, anchors[prv] + rng.choice((-1, 1))))
        for i in anchors:
            ev[i][1] = anchors[i]
        # THE BREATH LAW (ledger dr03 + the adlib court, 2026-07-12): dense
        # cells sang WALL-TO-WALL (54 notes over a drop, biggest rest 1.0
        # beat — the audible receipt caught the adlib rail starved; 262
        # relentless words is the robotic tell). A real phrase ENDS: its
        # tail keeps the ANCHOR (the cadence the engine aimed) plus at most
        # ONE pickup — the other trailing passing notes become the singer's
        # breath. Dense cells only; the window scales with the phrase
        # (1 beat for 1-bar cells, 1.5 for longer). Skip-set, not deletion:
        # anchors stay index-true. SOTADAW_BREATH=0 kills.
        _breath_skip = set()
        if len(ev) >= 8 and os.environ.get("SOTADAW_BREATH", "1") != "0":
            _win = phrase16 - (4 if lead_bars == 1 else 6)
            _tail = [i for i, e in enumerate(ev)
                     if e[0] >= _win and i not in anchors]
            _breath_skip = set(_tail[:-1])
        # emit through the PERFORMANCE layer
        for i, (st, dg, ln) in enumerate(ev):
            beat = bar0 * 4 + st * 0.25
            if beat >= bars * 4.0 or i in _breath_skip:
                continue
            h = contour(plan_pos(st))
            if kind == "B":
                h = 1.0 - h
            v = 0.72 * (0.86 + 0.16 * h)
            if i in anchors and anchors[i] >= hi_d - 1:
                v += 0.06                        # the climax leans in
            if i == len(ev) - 1:
                v *= 0.92                        # phrase-final breath
            v = max(0.2, min(1.0, v * rng.uniform(0.96, 1.04)))
            length = ln * 0.25
            if i + 1 < len(ev):
                gap = (ev[i + 1][0] - st) * 0.25
                if 0 < gap <= 0.5 and abs(ev[i + 1][1] - dg) <= 2:
                    length = gap * 0.92          # legato through stepwise runs
            if i == len(ev) - 1:
                length *= 0.8
            d = dg - 1
            pitch = base_oct + root + iv[d % 7] + 12 * (d // 7)
            notes.append({"start": round(beat, 4), "len": round(max(0.05, length), 4),
                          "pitch": int(pitch), "vel": round(v, 3)})
    return notes


def find_vocal_kit(rng, base=None):
    """SAMPLE CHOPS (W13): discover a pitched vocal kit among the user's own
    import kits. Returns (name, min_key, max_key) or None (stranger boxes carry
    no kits — the caller falls back to formant_vox). Deterministic per seed;
    `_id` identity kits and open-ended kits are skipped."""
    base = base or os.path.join(ROOT, "kits")
    out = []
    try:
        for d in sorted(os.listdir(base)):
            # underscore kits are SCRATCH (other sessions' diagnostics, may
            # vanish) — only stable kits qualify as chop material
            if "vocal" not in d or d.endswith("_id") or d.startswith(("_", ".")):
                continue
            try:
                k = json.load(open(os.path.join(base, d, "kit.json")))
            except Exception:
                continue
            if k.get("kind") == "pitched" and len(k.get("samples", [])) >= 3:
                keys = [int(s.get("keyNote", 60)) for s in k["samples"]]
                out.append((d, min(keys), max(keys)))
    except OSError:
        pass
    return rng.choice(out) if out else None


def rhythm_take(steps, rng):
    """W84: bounded rhythm variation of a hook cell (see callsite law)."""
    if len(steps) < 4 or os.environ.get("SOTADAW_RHYTHMTAKE", "1") == "0":
        return steps
    out = sorted(([int(s[0]), int(s[1]), int(s[2])] for s in steps),
                 key=lambda s: s[0])
    _cap = max(1, len(out) // 3)
    _n_ops = 0 if rng.random() < 0.25 else rng.randint(1, _cap)
    # purity is an explicit 25% (randint(0,1) made HALF of all small-cell
    # takes pure — house/gospel measured 2/6 unique rhythms)
    for _ in range(_n_ops):
        for _try in range(6):                        # an op RETRIES until it
            if len(out) < 4:                         # lands (short cells kept
                break                                # no-oping silently)
            i = rng.randrange(1, len(out) - 1)      # anchors sacred
            op = rng.random()
            st, deg, ln = out[i]
            prev_end = out[i - 1][0] + out[i - 1][2]
            next_st = out[i + 1][0]
            if op < 0.5:                             # shift one 16th
                landed = False
                for d in rng.sample((-1, 1), 2):
                    if prev_end <= st + d and st + d + ln <= next_st:
                        out[i][0] = st + d
                        landed = True
                        break
                if landed:
                    break
            elif op < 0.75 and ln >= 2:              # split a long note
                half = ln // 2
                out[i][2] = half
                out.insert(i + 1, [st + half, deg, ln - half])
                break
            elif i + 1 < len(out) - 1 and next_st == st + ln:   # merge
                out[i][2] = ln + out[i + 1][2]
                del out[i + 1]
                break
    return [tuple(s) for s in out]


def stereo_double(tr, bpm, spread=0.8):
    # W67 (blind-judge tell, 2026-07-11): +-0.45 summed to corr 0.91 /
    # width -13.4dB on synthwave — "dangerously mono". Records hard-pan
    # double-tracks; +-0.8 restores the wall. Bass/kick stay center (sub law).
    """THE DOUBLE LAW: one mono synth lane -> an L/R pair with different voice
    params + ~11ms right-side lag (records double-track; demos pan one mono take).
    Returns [L, R]. Each side drops 2.5dB (decorrelated sum ~= the original)."""
    L, R = json.loads(json.dumps(tr)), json.loads(json.dumps(tr))
    vid = (tr.get("source") or {}).get("id")
    for side, sgn in ((L, -1), (R, +1)):
        side["pan"] = sgn * spread
        side["gainDb"] = tr.get("gainDb", 0) - 2.5
    if vid in DOUBLE_DETUNE:
        lo, hi = DOUBLE_DETUNE[vid]
        L["source"].setdefault("params", {})["detune"] = lo
        R["source"].setdefault("params", {})["detune"] = hi
    elif vid in DOUBLE_ALT:
        z, lo, hi = DOUBLE_ALT[vid]
        L["source"].setdefault("params", {})[z] = lo
        R["source"].setdefault("params", {})[z] = hi
    lag = round(0.011 * bpm / 60.0, 4)             # ~11ms in beats
    for n in R.get("notes", []):
        n["start"] = round(n["start"] + lag, 4)
    R["name"] = tr["name"] + "R"
    return [L, R]

# lane -> (faust voice, midi pitch, base vel, note len beats)
# kick_punch_tight (W9): the parent's 45ms/5.5x body sweep parked half its
# energy in 120-500Hz (solo 2.4:1 low:lowmid; records ~8.5:1). The tight mint
# (16ms/3.8x, heavier fundamental tail) measures 8.5:1 with IDENTICAL attack
# energy — the mud carve happens in the voice, not the EQ. JIT until the next
# build-window tick promotes it AOT (new .dsp = normal rebuild, no nuke).
LANES = {"kick": ("kick_punch_tight", 36, 0.95, 0.2), "snare": ("snare", 38, 0.9, 0.2),
         "clap": ("clap_909", 39, 0.85, 0.2), "rim": ("snare", 37, 0.6, 0.12),
         "hat": ("hat", 42, 0.55, 0.1), "openhat": ("hat_metal", 46, 0.6, 0.3),
         "ride": ("hat_metal", 51, 0.5, 0.2), "ghost": ("snare", 38, 0.3, 0.12),
         # THE WORLD KIT (ledger dr01/dr28, 2026-07-12): the latin/afro family
         # collapsed to kick+snare+hat — no clave, no congas, no shakers. New
         # lanes activate only when a genre's grid carries their steps; GM
         # pitches (75 claves, 56 cowbell, 70 maracas) so MIDI export is true.
         "shaker": ("shaker", 70, 0.5, 0.1), "clave": ("clave", 75, 0.75, 0.1),
         "conga": ("conga", 63, 0.7, 0.15), "cowbell": ("cowbell", 56, 0.65, 0.15)}
# W93: the bright families whose records carry the air band (never the
# dark-identity cultures — trap/amapiano/gqom taught that lesson)
AIR_GENRES = {"pop", "house", "deephouse", "kpop", "jpop", "eurodance",
              "italo_disco", "disco", "trance", "hi_nrg", "nightcore",
              "happy_hardcore", "hyperpop", "dariacore", "bigroom",
              "future_bass", "eurobeat", "french_house", "tech_house",
              "progressive_house", "citypop", "new_jack_swing", "freestyle",
              # W94b: the bright-choir/Motown-sparkle cultures (critic:
              # gospel "presence gutted" — its records SHINE)
              "gospel", "soul", "motown", "doo_wop", "funk"}
SLIDING_KICK = "kick_808"          # sliding-808 genres: the kick voice doubles as the bass

# THE MODE TABLE (12-TET; every row a standard mapping). Non-western entries are
# the accepted 12-TET approximations: Kurdi/Ousak/Bhairavi ~ Phrygian, Hijaz =
# Phrygian dominant, Bayati ~ natural minor (its half-flat 2nd has no 12-TET
# home), slendro/tizita ~ anhemitonic pentatonic. Pentatonics are PADDED to 7
# degree-slots (1,2,3,3,4,5,5) so every existing degree law (d%7) stays valid.
MODE_IV = {
    "minor":      [0, 2, 3, 5, 7, 8, 10],
    "major":      [0, 2, 4, 5, 7, 9, 11],
    "phrygian":   [0, 1, 3, 5, 7, 8, 10],
    "kurdi":      [0, 1, 3, 5, 7, 8, 10],
    "ousak":      [0, 1, 3, 5, 7, 8, 10],
    "bhairavi":   [0, 1, 3, 5, 7, 8, 10],
    "andalusi":   [0, 1, 3, 5, 7, 8, 10],
    "dorian":     [0, 2, 3, 5, 7, 9, 10],
    "lydian":     [0, 2, 4, 6, 7, 9, 11],
    "mixolydian": [0, 2, 4, 5, 7, 9, 10],
    "hijaz":      [0, 1, 4, 5, 7, 8, 10],
    "bayati":     [0, 2, 3, 5, 7, 8, 10],
    "harmonic":   [0, 2, 3, 5, 7, 8, 11],
    "penta_major": [0, 2, 4, 4, 7, 9, 9],
    "penta_minor": [0, 3, 5, 5, 7, 10, 10],
    "slendro":    [0, 2, 4, 4, 7, 9, 9],
    "tizita":     [0, 2, 4, 4, 7, 9, 9],
}


def key_scale(key):
    """Parse ANY curated key string into (root_pc, 7-slot interval list).
    Handles the graph's real shapes: 'F minor (Phrygian)' [paren mode OVERRIDES],
    'D Phrygian dominant (Hijaz)', 'A Kurdi (Phrygian)', 'C harmonic minor',
    'D pentatonic (slendro approx.)', 'G major (pentatonic)', 'pantonal (C pedal)'
    [root rescued from the hint]. Color hints ('maj7 color', 'club: minor',
    'emo axis') are ignored. Before this, 'F minor (Phrygian)' fell back to
    root A natural minor — 25 genres played the wrong scale (dna_battery's
    crash at arabesk was hiding it)."""
    base, _, hint = key.partition("(")
    hint = hint.rstrip(")").strip().lower()
    toks = base.strip().split()
    root = None
    for t in toks:
        cand = t[0].upper() + t[1:] if t else t
        if cand in NOTE_PC:
            root = NOTE_PC[cand]
            break
    if root is None:                        # 'pantonal (C pedal)' — hint carries it
        for t in hint.replace("(", " ").split():
            cand = t[0].upper() + t[1:] if t else t
            if cand in NOTE_PC:
                root = NOTE_PC[cand]
                break
    if root is None:
        root = 9
    base_l = base.lower()
    def mode_in(text, exclude=()):
        if "phrygian dominant" in text or "hijaz" in text:
            return MODE_IV["hijaz"]
        if "harmonic" in text and "anti" not in text:
            return MODE_IV["harmonic"]
        if "pentatonic" in text or "slendro" in text or "tizita" in text:
            return MODE_IV["penta_minor" if "minor" in base_l else "penta_major"]
        for m, iv in MODE_IV.items():
            if m in exclude or (m == "harmonic" and "anti" in text):
                continue
            if m in text:
                return iv
        return None
    # priority: a SPECIFIC mode in the base ('C harmonic minor') > a mode word in
    # the hint ('F minor (Phrygian)' -> phrygian) > the base's plain minor/major
    iv = mode_in(base_l, exclude=("minor", "major")) \
        or mode_in(hint, exclude=("minor", "major")) \
        or mode_in(base_l) or MODE_IV["minor"]
    return root, iv


def key_to_pcs(key):
    root, iv = key_scale(key)
    return root, [(root + i) % 12 for i in iv]

def bass_notes(style, root, pcs, bars, rng, kick_steps, spb16=0.25, bar_degrees=None):
    """A seeded bass line in the key. Returns (voice, notes).
    bar_degrees: per-bar scale degree (1-based) — the bass FOLLOWS THE CHANGES."""
    def base_for(bar):
        deg = 1
        if bar_degrees:
            deg = bar_degrees[bar % len(bar_degrees)]
        pc = pcs[(deg - 1) % 7]
        b = 36 + (pc % 12)
        return b - 12 if b > 43 else b
    base = base_for(0)
    n = lambda s, l, p, v: {"start": round(s * spb16, 4), "len": round(l * spb16, 4),
                            "pitch": p, "vel": round(v, 3)}
    notes, total = [], bars * 16
    fifth, four, seven = base + 7, base + 5, base + 10
    def harm(i):
        b = base_for(i // 16)
        return b, b + 7, b + 5, b + 10
    if style == "offbeat":
        for i in range(2, total, 4):
            b_, f_, _, _ = harm(i)
            notes.append(n(i, 1.6, b_ if rng.random() < 0.8 else f_, 0.85))
    elif style == "roots":
        for bar in range(bars):
            b = bar * 16
            b_, f_, q_, s_ = harm(b)
            pool = [b_, b_, f_, q_]
            notes.append(n(b, 3.5, b_, 0.9))
            notes.append(n(b + 6, 1.5, rng.choice(pool), 0.7))
            notes.append(n(b + 10, 2.0, rng.choice(pool), 0.8))
            if rng.random() < 0.5:
                notes.append(n(b + 14, 1.5, rng.choice([s_, f_]), 0.6))
    elif style == "sliding":                   # the 808 IS the bassline
        # W19: notes LEGATO-OVERLAP inside the bar (0.4-16th lap) — the mono
        # engine ignores the old note's off once a new note owns the voice,
        # and sub_808_slide's smoothed freq turns every hand-off into the
        # FL-porta GLIDE. The bar's last note keeps its tail (the 808
        # breathes at bar seams). SOTADAW_SLIDE808=0 = legacy discrete kicks.
        slide_on = os.environ.get("SOTADAW_SLIDE808", "1") != "0"
        for bar in range(bars):
            b = bar * 16
            b_, f_, q_, _ = harm(b)
            pool = [b_, b_, b_ - 5, q_, f_ - 12 if f_ - 12 > 24 else f_]
            picks = sorted(rng.sample([0, 6, 10, 12], k=3))
            for i, s in enumerate(picks):
                ln = 5.0 if i == 0 else 3.0
                if slide_on and i + 1 < len(picks):
                    ln = (picks[i + 1] - s) + 0.4
                notes.append(n(b + s, ln, rng.choice(pool), 0.9))
    elif style == "psy_rolling":               # bass on every 16th EXCEPT the kicks
        kicks = {k % 16 for k in kick_steps}
        for bar in range(bars):
            for i in range(16):
                if i % 4 != 0 or i not in kicks and i % 4 == 0:
                    if i % 4 != 0:
                        notes.append(n(bar * 16 + i, 0.9, harm(bar * 16)[0], 0.8))
    elif style == "wub":                       # W94: the dnb pocket — the
        # reese MOVES (critic round: "bass near-extinct, 0.4 notes/bar").
        # Syncopated stabs locked to the break's pocket with a long anchor
        # on bar 1 of each pair: hold... wub-wub — jump-up/rolling middle
        # ground, ~2.5 notes/bar of real movement.
        for bar in range(bars):
            b = bar * 16
            b_, f_, q_, s_ = harm(b)
            if bar % 2 == 0:
                notes.append(n(b, 10.0, b_, 0.85))          # the anchor hold
                notes.append(n(b + 11, 2.0, rng.choice([b_, q_]), 0.7))
                notes.append(n(b + 14, 1.6, rng.choice([f_, s_]), 0.72))
            else:
                notes.append(n(b, 2.5, b_, 0.8))
                notes.append(n(b + 3, 1.5, rng.choice([b_, f_]), 0.68))
                notes.append(n(b + 6, 3.0, rng.choice([q_, b_]), 0.78))
                notes.append(n(b + 10, 2.0, rng.choice([f_, s_]), 0.7))
                notes.append(n(b + 13, 2.5, b_, 0.75))
    elif style == "sustained":                 # reese/wobble holds
        for bar in range(0, bars, 2):
            b_, _, q_, _ = harm(bar * 16)
            p = rng.choice([b_, b_ - 2 if b_ - 2 > 24 else b_, q_])
            notes.append(n(bar * 16, 30.0 if bars - bar >= 2 else 14.0, p, 0.8))
    elif style == "sub":                       # the 808 SUB is the floor
        # (worldclass ledger 2026-07-12: "sub" was UNHANDLED — plugg/rage/
        # jersey_drill/digicore, 12 genres, birthed with ZERO bass lane.)
        # Deeper and stiller than "sliding" (3 rolling hits/bar): one long
        # root anchor per bar, then ONE late-bar move that legato-overlaps
        # into the next downbeat — the hand-off IS the 808 glide (W19).
        slide_on = os.environ.get("SOTADAW_SLIDE808", "1") != "0"
        for bar in range(bars):
            b = bar * 16
            b_, f_, q_, s_ = harm(b)
            hold = rng.choice([10, 11, 12])
            move = rng.choice([q_, f_ - 12 if f_ - 12 > 24 else f_, s_, b_])
            notes.append(n(b, hold + (0.4 if slide_on else 0.0), b_, 0.88))
            notes.append(n(b + hold, (16 - hold) + (0.4 if slide_on else 0.0),
                           move, 0.8))
    elif style == "walking":                   # jazz/bigband quarters w/ approach tones
        for bar in range(bars):
            b = bar * 16
            b_, f_, _, _ = harm(b)
            nb, _, _, _ = harm((bar + 1) * 16)     # approach the NEXT bar's root
            walk = [b_, rng.choice([b_ + 4, b_ + 5]), f_,
                    rng.choice([nb + 1, nb - 1, nb + 2])]
            for i, p_ in enumerate(walk):
                notes.append(n(b + i * 4, 3.6, p_, 0.8 if i else 0.85))
    elif style == "tumbao":                    # THE TUMBAO (ledger dr28: salsa
        # bass hit the DOWNBEAT — the exact opposite of the culture). The bass
        # lands on the AND-OF-2 (the fifth) and BEAT 4 (the NEXT bar's root,
        # anticipated, ringing over the barline). The downbeat stays empty —
        # that is where the clave lives.
        for bar in range(bars):
            b = bar * 16
            b_, f_, q_, s_ = harm(b)
            nb = harm(((bar + 1) % bars) * 16)[0]
            notes.append(n(b + 6, 5.5, f_, 0.82))
            notes.append(n(b + 12, 7.5, nb, 0.88))
    elif style == "log":                       # log drum answers in the kick's holes
        holes = [3, 9, 14]
        for bar in range(bars):
            b = bar * 16
            b_, f_, q_, s_ = harm(b)
            pool = [f_, f_, s_, q_]
            for h in holes:
                if rng.random() < 0.85:
                    notes.append(n(b + h, 1.6, rng.choice(pool), 0.85))
    # THE TURNAROUND: records breathe at the loop seam — the last 16th walks
    # into the loop-top root (chromatic leading tone, or the step above). The
    # walking style already approaches; sustained/log hold their role.
    if style in ("offbeat", "roots", "sliding", "psy_rolling", "sub") and notes:
        lim = (total - 1) * spb16
        appr = base_for(0) + rng.choice((-1, 2))
        notes = [x for x in notes if x["start"] < lim - 1e-6]
        for x in notes:                             # no overlap into the pickup
            if x["start"] + x["len"] > lim:
                x["len"] = round(max(0.1, lim - x["start"]), 4)
        notes.append(n(total - 1, 1.0, appr, 0.78))
    slide_voice = ("sub_808_slide"             # W19: the gliding melodic 808
                   if os.environ.get("SOTADAW_SLIDE808", "1") != "0" else SLIDING_KICK)
    voice = {"offbeat": "sub_clean", "roots": "bass_warm", "sliding": slide_voice, "walking": "bass_warm",
             "psy_rolling": "sub_clean", "sustained": "reese", "log": "log_drum",
             "wub": "reese", "sub": slide_voice,
             "tumbao": "upright_bass"}.get(style, "bass_warm")
    return voice, notes

def generate(genre, name, bars=4, seed=0, bpm=None, key=None):
    dna, err = genre_dna(genre)
    if dna is None:
        return None, err
    pname, grid = dna["archetype"], dna["grid"]
    rng = random.Random(f"{genre}/{seed}")   # name-independent: same genre+seed reproduces exactly
    # W87 THE PROGRESSION TAKES: one genre = one progression FOREVER was
    # the harmonic photocopier (the W84 census, harmony axis). A take may
    # substitute middle chords WITHIN their diatonic function (tonic 1<->6,
    # subdominant 4<->2, dominant 5<->7); the FIRST chord (tonal home) and
    # the LAST (the cadence W34 leans on) are sacred. Purity 30%. The
    # take's progression rides grid locally (every birth lane reads it) and
    # song._loop.chords (arrange + ruler prefer it). SOTADAW_PROGTAKE=0.
    _prog0 = grid.get("chords")
    if (_prog0 and len(_prog0) >= 3
            and os.environ.get("SOTADAW_PROGTAKE", "1") != "0"
            and rng.random() >= 0.30):
        _FN = {1: 6, 6: 1, 4: 2, 2: 4, 5: 7, 7: 5}
        _pt = [list(c) for c in _prog0]
        _mid = list(range(1, len(_pt) - 1))
        rng.shuffle(_mid)
        for _i in _mid[: (1 if len(_pt) <= 4 else 2)]:
            _sub = _FN.get(int(_pt[_i][1]))
            if _sub:
                _pt[_i][1] = _sub
        if _pt != [list(c) for c in _prog0]:
            grid = dict(grid)
            grid["chords"] = [tuple(c) for c in _pt]
    # THE DRUM TAKE (ledger dr01-d, 2026-07-12): the kick backbone was 100%
    # seed-invariant — every take of a genre shared ONE drum programming
    # forever. A take may now make ONE bounded kick move (add a syncopation
    # hit / shift or drop a non-anchor hit), riding the PATTERN so bars stay
    # consistent (per-bar life is the breathing bar's job). NEVER: slot 0
    # (the downbeat), a pure four-on-floor identity (house's kick IS
    # [0,4,8,12]), or an exact-cell world genre (clave/cowbell/conga in the
    # grid = the cell is law). SOTADAW_DRUMTAKE=0 kills.
    _ks0 = list(grid.get("kick") or [])
    if (_ks0 and os.environ.get("SOTADAW_DRUMTAKE", "1") != "0"
            and not set(_ks0) <= {0, 4, 8, 12}
            and not any(k in grid for k in ("clave", "cowbell", "conga"))
            and rng.random() < 0.55):
        _ks = list(_ks0)
        _kk = [s for s in _ks if s % 16 != 0]
        _move = rng.random()
        if _move < 0.45:
            _free = [s for s in (3, 6, 7, 10, 11, 14) if s not in _ks]
            if _free and len(_ks) <= 6:
                _ks = sorted(_ks + [rng.choice(_free)])
        elif _move < 0.75 and _kk:
            _v = rng.choice(_kk)
            _cand = _v + rng.choice((-1, 1))
            if 0 < _cand < 16 and _cand not in _ks:
                _ks = sorted([s for s in _ks if s != _v] + [_cand])
        elif len(_kk) >= 2:
            _ks = [s for s in _ks if s != rng.choice(_kk)]
        if _ks != _ks0:
            grid = dict(grid)
            grid["kick"] = _ks
    # the take lives SOMEWHERE in the genre's honest tempo range — the frozen
    # midpoint made every unseeded techno loop exactly the same BPM forever
    lo_b, hi_b = float(dna["bpm_lo"] or 120), float(dna["bpm_hi"] or 120)
    bpm = float(bpm or round(rng.uniform(min(lo_b, hi_b), max(lo_b, hi_b))))
    key = key or dna["key"] or "A minor"
    pat_bars = int(grid.get("bars", 1))
    root, pcs = key_to_pcs(key)

    tracks = []
    vel_maps = grid.get("vel", {})
    ACCENT = {0: 1.0, 2: 0.7, 1: 0.5, 3: 0.5}   # 16th-position accents (i%4)
    # THE FILL: an optional grid variant stamped on the LAST bar of every 4
    # (and the final bar of the loop) — the turnaround that makes loops breathe.
    fill = grid.get("fill") or {}
    fill_vel = fill.get("vel", {})
    for lane, (voice, pitch, bvel, ln) in LANES.items():
        steps = grid.get(lane)
        if not steps and fill.get(lane) is None:
            continue                       # lane absent in base AND fill
        steps = steps or []                # fill-only lane: empty base, fill stamps the last bar
        vmap = vel_maps.get(lane, {})
        fsteps = fill.get(lane)
        fmap = fill_vel.get(lane, {})
        notes = []
        for bar in range(0, bars, pat_bars):
            for s in steps:
                beat = bar * 4 + s * 0.25
                if beat >= bars * 4:
                    continue
                v = float(vmap.get(str(s), bvel * ACCENT.get(s % 4, 0.7) / ACCENT[0]))
                v = max(0.15, min(1.0, v * rng.uniform(0.94, 1.06)))   # human hands
                notes.append({"start": round(beat, 4), "len": ln, "pitch": pitch, "vel": round(v, 3)})
        # THE FILL post-pass: replace this lane's turnaround bars with the fill
        # variant (16-step, pat_bars-agnostic). dr01 (2026-07-12): the comment
        # promised "the LAST bar of every 4" but stamped only the absolute
        # final bar — an 8/16-bar birth never breathed mid-phrase. Now every
        # 4th bar turns around; mid-phrase fills sit back (0.85x), the final
        # one announces at full weight.
        _fill_bars = set()
        if fsteps is not None and bars >= 2:
            _fill_bars = {b for b in range(3, bars, 4)} | {bars - 1}
            notes = [nt for nt in notes if int(nt["start"] // 4) not in _fill_bars]
            for fb in sorted(_fill_bars):
                damp = 1.0 if fb == bars - 1 else 0.85
                for s in fsteps:
                    beat = fb * 4.0 + s * 0.25
                    if beat >= bars * 4:
                        continue
                    v = float(fmap.get(str(s), bvel * ACCENT.get(s % 4, 0.7) / ACCENT[0]))
                    v = max(0.15, min(1.0, v * damp * rng.uniform(0.94, 1.06)))
                    notes.append({"start": round(beat, 4), "len": ln, "pitch": pitch, "vel": round(v, 3)})
        # THE BREATHING BAR (worldclass ledger dr01, 2026-07-12): a 4-bar loop
        # was ONE bar cloned — pattern, velocity AND count identical bar to
        # bar, the #1 preset-demo tell on all 204 genres. Feel lanes breathe:
        # per-bar velocity re-roll + at most ONE onset dropped or gained per
        # bar (never the bar's first hit). Bar 0 is the identity bar, the
        # fill bar owns its own shape, kick/snare/clap stay the backbone.
        # Deterministic per (genre, seed, lane, bar) — takes reproduce, and
        # seeds now differ on feel lanes too (the seed-invariance finding).
        _chop_set = set(grid.get("chop_lanes") or ())
        if ((lane in ("hat", "openhat", "ride", "ghost", "rim", "shaker")
                or lane in _chop_set) and notes
                and lane not in (grid.get("steady_lanes") or ())
                and os.environ.get("SOTADAW_BARVARY", "1") != "0"):
            # (clave/cowbell/conga stay STEADY always; steady_lanes lets a
            # grid pin MORE — bossa's rim IS the clave. A varied clave is a
            # wrong clave, not a human one. chop_lanes is the OPPOSITE gate:
            # THE CHOP TAKE (ledger dr23, 2026-07-12) — breaks-family snares
            # re-chop per bar, backbeat anchors (2&4) sacred.)
            for _bar in range(1, bars):
                _b0 = _bar * 4.0
                if _bar in _fill_bars:
                    continue                     # every fill bar owns its shape
                _brng = random.Random(f"{genre}/{seed}/{lane}/bar{_bar}")
                _bn = [n for n in notes if _b0 <= n["start"] < _b0 + 4.0]
                if not _bn:
                    continue
                for n in _bn:
                    n["vel"] = round(max(0.15, min(1.0, n["vel"] * _brng.uniform(0.9, 1.1))), 3)
                if lane in _chop_set:
                    # the chop move-set: never a backbeat anchor (2&4 = slot
                    # s%8==4 in 16ths-of-bar terms: beat offsets 1.0/3.0)
                    _free = [n for n in _bn
                             if abs((n["start"] - _b0) - 1.0) > 1e-6
                             and abs((n["start"] - _b0) - 3.0) > 1e-6]
                    _roll = _brng.random()
                    if _roll < 0.40 and _free:
                        _v = _brng.choice(_free)            # re-CHOP: shift one
                        _cand = round(_v["start"] + _brng.choice((-0.25, 0.25)), 4)
                        if (_b0 <= _cand < _b0 + 4.0
                                and all(abs(n["start"] - _cand) > 1e-6 for n in _bn)):
                            _v["start"] = _cand
                    elif _roll < 0.70 and _free:
                        _src = _brng.choice(_free)          # chop STUTTER double
                        _cand = round(_src["start"] + 0.25, 4)
                        if (_cand < _b0 + 4.0
                                and all(abs(n["start"] - _cand) > 1e-6 for n in _bn)):
                            notes.append(dict(_src, start=_cand,
                                              vel=round(max(0.15, _src["vel"] * 0.55), 3)))
                    elif len(_free) >= 2:
                        notes.remove(_brng.choice(_free))   # chop OUT
                    continue
                _roll = _brng.random()
                if _roll < 0.45 and len(_bn) >= 3:
                    notes.remove(_brng.choice(_bn[1:]))     # breathe OUT
                elif _roll < 0.80:
                    _src = _brng.choice(_bn)                # breathe IN
                    _cand = round(_src["start"] + _brng.choice((-0.25, 0.25)), 4)
                    if (_b0 <= _cand < _b0 + 4.0
                            and all(abs(n["start"] - _cand) > 1e-6 for n in _bn)):
                        notes.append(dict(_src, start=_cand,
                                          vel=round(max(0.15, _src["vel"] * 0.7), 3)))
            notes.sort(key=lambda n: n["start"])
        if notes:
            # THE AIR NUDGE (band balance law): real records carry ~3x our energy
            # above 6kHz; hats/rides are the air organ — sub-dominant genres lift
            # them 2dB (the mud fix's other half: presence up, not just lowmid down)
            _air = 2 if (lane in ("hat", "openhat", "ride")
                         and str(dna.get("band_order") or "").startswith("low")) else 0
            # W49/W62: per-genre lane voice + curated gain staging from the
            # grid blob ("<lane>_voice"/"<lane>_gain_db" — whole-blob = both
            # KG paths by construction; curated per genre, never blanket).
            _v49 = grid.get(f"{lane}_voice") or voice
            _g49 = {"kick": -2, "snare": -5, "clap": -6, "hat": -13,
                    "openhat": -12, "ride": -12, "rim": -9, "ghost": -8,
                    "shaker": -15, "clave": -10, "conga": -8,
                    "cowbell": -13}.get(lane, -8) + _air
            if grid.get(f"{lane}_gain_db") is not None:
                _g49 = float(grid[f"{lane}_gain_db"])
            if grid.get(f"{lane}_pitch") is not None:   # W62: pitched percs
                _p62 = int(grid[f"{lane}_pitch"])       # (the dundun speaks
                for n in notes:                          # at 150-400Hz, not
                    n["pitch"] = _p62                    # the kick's floor)
            tr = {"name": lane, "source": {"kind": "faust", "id": _v49},
                  "gainDb": _g49,
                  "notes": notes}
            if LANE_PAN.get(lane):
                tr["pan"] = LANE_PAN[lane]
            tracks.append(tr)
    # THE LEAD (melody DNA): grid.lead = {"steps": [[step16, scale_degree, len16], ...],
    # "octave": 5, "voice": "pluck2"} — degrees (1-based, 8=octave up) resolve in the
    # song key; the hook repeats each pattern span like the drums do.
    lead = grid.get("lead")
    if lead and lead.get("steps"):
        # W76: curated lead voice rides the grid blob without replacing the
        # hook cell (darksynth's mono-reese lead = the first customer)
        lv = grid.get("lead_voice") or lead.get("voice", "pluck2")
        base_oct = int(lead.get("octave", 5)) * 12
        lead_bars = int(lead.get("bars", 1))       # phrase length: steps may span 0..16*bars-1
        _, iv = key_scale(key or "A minor")    # the hook plays the DECLARED mode
        # SEEDED HOOK PATH: the DNA owns the RHYTHM (genre identity), the take owns
        # the MELODIC PATH. Anchor steps (phrase start + cadence) hold; each other
        # step may swap (~1/3) to a chord tone of its bar's chord or a scale
        # neighbor — always diatonic (dna_battery's KEY law), same walk on every
        # phrase repeat (a hook repeats itself; only TAKES differ). Before this,
        # every take of a genre sang the identical hook forever.
        prog_l = grid.get("chords") or [[0, 1]]
        span_l = max(b for b, _ in prog_l) + 1
        def _ldeg_at(bar):
            d = 1
            for b0, dd in sorted(prog_l):
                if bar % span_l >= b0:
                    d = dd
            return d
        # THE HOOK ENGINE (W14): the old seeded walk noodled — see hook_notes.
        # The grid cell keeps the genre's RHYTHM; the pitches get INTENT
        # (anchors/approaches/climax/cadence) + the performance layer.
        # W84 THE RHYTHM TAKES: the DNA cell anchors the genre's rhythm;
        # a take may re-speak it in the grid's own language — non-anchor
        # onsets (never the phrase head or cadence tail) may shift one
        # 16th, split, or merge; <=1/3 of onsets, deterministic per seed,
        # n_ops can be 0 (pure-DNA takes remain). Census before this:
        # 4 seeds = 4 melodies but ONE rhythm forever. SOTADAW_RHYTHMTAKE=0.
        _steps84 = rhythm_take(lead["steps"], rng)
        lnotes = hook_notes(_steps84, max(pat_bars, lead_bars), iv, root,
                            base_oct, _ldeg_at, bars, rng,
                            seventh=genre.lower() in EXT_SEVENTH)
        if lnotes:
            _lgg = grid.get("lead_gain_db")    # W67: per-genre melodic staging
            ltrack = {"name": "lead", "source": {"kind": "faust", "id": lv},
                      "gainDb": (float(_lgg) if _lgg is not None else -9),
                      "pan": LANE_PAN["lead"], "notes": lnotes}
            if lv in DOUBLE_DETUNE or lv in DOUBLE_ALT:   # wide doubled lead
                # W68: the gate now honors DOUBLE_ALT too (pluck2/organ leads
                # shipped MONO while the arp gate checked both maps)
                tracks.extend(stereo_double(ltrack, bpm, spread=0.75))  # W67 wide
            else:
                tracks.append(ltrack)
    bstyle = grid.get("bass_style", "roots")
    if bstyle != "none":
        prog_b = grid.get("chords") or [[0, 1]]
        span_b = max(b for b, _ in prog_b) + 1
        bar_degs = []
        for b in range(span_b):
            d = 1
            for b0, dd in sorted(prog_b):
                if b >= b0:
                    d = dd
            bar_degs.append(d)
        bvoice, bnotes = bass_notes(bstyle, root, pcs, bars, rng, grid.get("kick", []), bar_degrees=bar_degs)
        # W47: per-genre bass VOICE override (grid JSON field "bass_voice" —
        # rides the whole-blob grid through BOTH KG-query and cache paths, so
        # the KG-field law is satisfied by construction). Curation truth in
        # tools/kg_seed_lowmid_curation.py; the style->voice map stays the
        # default for the other 200 genres.
        bvoice = grid.get("bass_voice") or bvoice
        _bg = grid.get("bass_gain_db")            # W67: per-genre bass staging
        _bos = grid.get("bass_octave_shift")      # W75: acid lines ride E2-E3,
        if _bos:                                  # not the sub floor
            for n in bnotes:
                n["pitch"] += 12 * int(_bos)
        if bnotes:
            _bsrc = {"kind": "faust", "id": bvoice}
            if isinstance(grid.get("bass_params"), dict):   # W75: curated zone
                _bsrc["params"] = dict(grid["bass_params"])  # truth (303 squeal)
            # THE WOBBLE SYNC LAW (ledger dr29, 2026-07-12): wobble.dsp carries
            # its own LFO but a Hz rate can't know the take's tempo — an
            # unsynced wobble is the bedroom tell. cycles-per-beat rides the
            # grid (dubstep 2 = the 1/8 wobble; halve for the riddim lope);
            # an explicit curated rate always wins.
            if _bsrc["id"] == "wobble" and "rate" not in _bsrc.get("params", {}):
                _cpb = float(grid.get("wobble_cpb") or 2.0)
                _bsrc.setdefault("params", {})["rate"] = round(bpm / 60.0 * _cpb, 2)
            tracks.append({"name": "bass", "source": _bsrc,
                           "gainDb": (float(_bg) if _bg is not None else -5), "notes": bnotes})
    # color layer: the genre's first recipe voice holds root-chord pads
    cvoice = grid.get("color_voice") or dna.get("voice")   # W71: curated
    # color voice rides the grid blob (KG-field law by construction) —
    # the rail the voiceless-fallback comment promised.
    if not cvoice:
        # THE VOICELESS FALLBACK: 63/202 grid genres have no SoundRecipe voice and
        # were born harmonically NAKED (reggae with no skank organ, chicago house
        # with no stab). Family-true defaults until the KG curation wave lands;
        # genres outside these families stay sparse ON PURPOSE (minimal/dembow/
        # footwork language is absence).
        g_l0 = genre.lower()
        cvoice = ("hammond_organ" if g_l0 in SKANK_GENRES else
                  "organ_soul" if g_l0 in STAB_GENRES else
                  "pad_motion" if (g_l0 in EXT_ADD9 or g_l0 in ARP_GENRES) else
                  "keys_dark" if g_l0 in EXT_SEVENTH else None)
    if cvoice:
        if cvoice not in (SLIDING_KICK, "log_drum"):
            prog = grid.get("chords") or [[0, 1]]
            span = max(b for b, _ in prog) + 1
            def deg_at(bar):
                d = 1
                for b0, dd in sorted(prog):
                    if bar % span >= b0:
                        d = dd
                return d
            def triad_pcs(deg):
                i = deg - 1
                return [pcs[i % 7] % 12, pcs[(i + 2) % 7] % 12, pcs[(i + 4) % 7] % 12]
            # VOICE-LED (firing 101, the M1 kernel): same pitch classes, but the
            # voicings HOLD common tones and move by the least distance bar to bar
            # — block-triad jumps read as a beginner's left hand; this reads played.
            # EXTENSION LAW: seventh-language genres (house/soul/jazz families) get
            # the DIATONIC 7th; airy synth families get the add9 — block triads are
            # the beginner tell. Degrees only, so every added tone stays in key.
            from voicing import voice_pcs
            g_l = genre.lower()
            def chord_pcs_of(deg):
                base = triad_pcs(deg)
                i = deg - 1
                if g_l in EXT_SEVENTH:
                    base.append(pcs[(i + 6) % 7] % 12)
                elif g_l in EXT_ADD9:
                    base.append(pcs[(i + 1) % 7] % 12)
                return base
            per_bar = [chord_pcs_of(deg_at(b)) for b in range(bars)]
            _vc = dna.get("voicing") or {}
            _hi = int(_vc.get("hi", 70)) + (2 if len(per_bar[0]) > 3 else 0)
            # THE BAND BALANCE LAW (measured 2026-07-10 vs a real record):
            # our lowmid ran 31.6% vs the record's 9.7% — pad fundamentals at
            # 130-190Hz stack ON the bass harmonics. Sub-dominant genres voice
            # the color ABOVE the mud band (arranger's left-hand rule: don't
            # double the bass register); the curated ceiling is untouched.
            _lo = int(_vc.get("lo", 48))
            # 'low>' with the separator: 'lowmid>...' also startswith('low')
            # (that ambiguity floored lowmid-led genres and starved narrow
            # voicing windows — the open style IndexError, 2026-07-10)
            if str(dna.get("band_order") or "").startswith("low>"):
                _lo = max(_lo, min(53, _hi - 15))
            voiced = voice_pcs(per_bar, _vc.get("style", "smooth"),
                               lo=_lo, hi=_hi,
                               thirds=[t[1] for t in per_bar], roots=[t[0] for t in per_bar])
            # articulation rides the family: chop where the genre chops
            if g_l in SKANK_GENRES:                # the afterbeat chop on 2 & 4
                cnotes = [{"start": round(b * 4.0 + off, 4), "len": 0.55, "pitch": p,
                           "vel": 0.55 if off == 1.0 else 0.5}
                          for b in range(bars) for off in (1.0, 3.0) for p in voiced[b]]
            elif g_l in STAB_GENRES:               # offbeat-8th stabs (the house organ)
                cnotes = [{"start": round(b * 4.0 + off, 4), "len": 0.4, "pitch": p,
                           "vel": v}
                          for b in range(bars)
                          for off, v in ((0.5, 0.46), (1.5, 0.4), (2.5, 0.48), (3.5, 0.4))
                          for p in voiced[b]]
            elif g_l in CHUG_GENRES:               # W61: the metal WALL — power-
                # chord chugs (root+5th, the two LOWEST voiced pcs; short
                # palm-mute lens, accents lean). W82 THE SUBFAMILY RHYTHMS:
                # straight 8ths were the whole family's voice — but metal
                # GALLOPS (eighth + two sixteenths), metalcore BREAKS DOWN
                # (half-time syncopation with space), djent SYNCOPATES
                # (3+3+3+3+4 sixteenth groupings). Offsets in beats; accent
                # rides the group head.
                _chug_pat = {
                    "metal":     [(0.0, 1), (0.5, 0), (0.75, 0),
                                  (1.0, 1), (1.5, 0), (1.75, 0),
                                  (2.0, 1), (2.5, 0), (2.75, 0),
                                  (3.0, 1), (3.5, 0), (3.75, 0)],   # the gallop
                    "metalcore": [(0.0, 1), (0.75, 0), (1.5, 1),
                                  (2.5, 0), (3.0, 1), (3.75, 0)],   # the breakdown
                    "djent":     [(0.0, 1), (0.75, 1), (1.5, 1),
                                  (2.25, 1), (3.0, 1), (3.5, 0),
                                  (3.75, 0)],                       # 3+3+3+3+4
                }.get(g_l, [(i * 0.5, 1 - (i % 2)) for i in range(8)])
                cnotes = [{"start": round(b * 4.0 + off, 4), "len": 0.32,
                           "pitch": p,
                           "vel": 0.55 if acc else 0.48}
                          for b in range(bars) for off, acc in _chug_pat
                          for p in sorted(voiced[b])[:2]]
            else:                                  # the held bed (pads breathe whole bars)
                cnotes = [{"start": float(b * 4), "len": 3.9, "pitch": p, "vel": 0.4}
                          for b in range(bars) for p in voiced[b]]
            csrc = resolve_color_source(cvoice)
            # MEASURED (2026-07-09, synthwave A/B): a DOUBLED faust pad beats the
            # mono vst3 factory pad on the record-ruler (0.6206 vs 0.5965) at 2.7x
            # less render cost (TAL was 73% of the whole render). Decorrelated
            # doubling > preset timbre for the PAD role; vst3 color stays behind
            # SOTADAW_VST_COLOR=1 for timbre-first sessions.
            if csrc.get("kind") == "vst3" and os.environ.get("SOTADAW_VST_COLOR") != "1":
                csrc = {"kind": "faust", "id": "pad_motion"}
            cc = color_character(genre, csrc.get("id")) if csrc.get("kind") == "faust" else {}
            if cc:
                csrc.setdefault("params", {}).update(cc)
            # W61: per-genre color staging from the grid blob (the wall
            # genres run their rhythm guitar HOT; pads stay at -14)
            _cg = grid.get("color_gain_db")
            _cos = grid.get("color_octave_shift")   # W74: voice the bed into
            if _cos:                                # the band the genre needs
                for n in cnotes:                    # (the VOICE SPECTRUM MAP:
                    n["pitch"] += 12 * int(_cos)    # jazz_piano at C4 = 80%
            ctrack = {"name": "color", "source": csrc,
                      "gainDb": float(_cg) if _cg is not None else -14,
                      "pan": 0.2, "notes": cnotes}
            cid = ctrack["source"].get("id")
            if ctrack["source"].get("kind") == "faust" and (cid in DOUBLE_DETUNE or cid in DOUBLE_ALT):
                tracks.extend(stereo_double(ctrack, bpm))
            else:
                tracks.append(ctrack)
    # ---- THE ARP LANE (texture law): arp-language genres get a running chord-tone
    # arpeggio — the missing signature texture (synthwave/trance/italo records run
    # on it). Chord tones only (diatonic by construction); 16ths under 132bpm,
    # 8ths above; up/updown pattern is a TAKE choice. Sits low (-13dB), panned
    # opposite the color pad, filtered dark — texture, not a second lead.
    if genre.lower() in ARP_GENRES:
        prog_a = grid.get("chords") or [[0, 1]]
        span_a = max(b for b, _ in prog_a) + 1
        def adeg_at(bar):
            d = 1
            for b0, dd in sorted(prog_a):
                if bar % span_a >= b0:
                    d = dd
            return d
        step_a = 0.25 if bpm <= 132 else 0.5
        updown = rng.random() < 0.45
        avoice = "supersaw" if genre.lower() in ("trance", "bigroom", "edm") else "pluck2"
        anotes = []
        for bar in range(bars):
            i = adeg_at(bar) - 1
            tones = [48 + pcs[i % 7], 48 + pcs[(i + 2) % 7], 48 + pcs[(i + 4) % 7],
                     60 + pcs[i % 7]]
            tones = [p + 12 if p < 48 else p for p in tones]
            seq = tones + (tones[-2:0:-1] if updown else [])
            t, k = bar * 4.0, 0
            while t < (bar + 1) * 4.0 - 1e-6:
                on_beat = abs(t - round(t)) < 1e-6
                anotes.append({"start": round(t, 4), "len": round(step_a * 0.9, 4),
                               "pitch": int(seq[k % len(seq)]),
                               "vel": 0.62 if on_beat else 0.5})
                t += step_a
                k += 1
        _agg = grid.get("arp_gain_db")         # W67: per-genre melodic staging
        atrack = {"name": "arp", "source": {"kind": "faust", "id": avoice},
                  "gainDb": (float(_agg) if _agg is not None else -13),
                  "pan": LANE_PAN["arp"], "notes": anotes}
        if avoice in DOUBLE_DETUNE or avoice in DOUBLE_ALT:
            tracks.extend(stereo_double(atrack, bpm, spread=0.85))  # W67 wide
        else:
            tracks.append(atrack)

    # ---- DEFAULT LIFE (CC4-I2, firing 108): quantized-dead is the demo tell.
    # Every voice is born with FEEL via the proven humanize kernel (GrooVAE axes:
    # correlated micro-drift + metric-accent velocity; magnitudes land ~10ms max
    # at 120bpm = inside the 10-30ms real-performance PD range, under the ~30ms
    # detection threshold, and exaggeration REDUCES groove — Frontiers 2016 +
    # Sci.Reports 2019 + the Porcaro hi-hat study; refs in stamp 108), role-lawful: kick stays
    # THE ANCHOR (untouched), bass locks to it (vel-only), hats/perc breathe most,
    # backbeats lean. Deterministic per seed. DNA checks assert pitch-classes and
    # fill-shape, not micro-positions - verified compatible.
    try:
        from expressive import humanize as _hum
        import random as _rnd
        _hseed = (seed * 7919 + 13) & 0xffff
        for t in tracks:
            nm = t["name"].lower()
            if "kick" in nm or not t.get("notes"):
                continue
            if any(k in nm for k in ("hat", "perc", "shaker", "ride", "open")):
                t["notes"] = _hum(t["notes"], 0.35, seed=_hseed)
            elif any(k in nm for k in ("snare", "clap")):
                t["notes"] = _hum(t["notes"], 0.22, seed=_hseed + 1)
            elif "bass" in nm or "808" in nm or "sub" in nm:
                _r = _rnd.Random(_hseed + 2)          # vel-only: bass locks the kick
                for n in t["notes"]:
                    n["vel"] = round(max(0.2, min(1.0, n["vel"] + _r.uniform(-0.05, 0.05))), 3)
            else:
                t["notes"] = _hum(t["notes"], 0.18, seed=_hseed + 3)
    except Exception as _he:
        print(f"[loop] default-life skipped: {_he}", flush=True)

    # ---- CLASS-AWARE FX DRESSING (fx-usage law, at birth) ----
    # Raw voices sound like demos. Every lane gets its production chain here so
    # MAKE/generate_loop are produced from the first render. Zone names verified
    # against the .dsp truth (fx_filter is LP-ONLY: hats clean up via eq shelf).
    dotted8 = round(0.75 * 60.0 / bpm, 4)
    # BAND TRUTH (W6, stem-attributed): the mix's 120-500Hz is owned by
    # kick/bass/lead; records run kick low:lowmid ~8:1 where ours ran 1.7:1
    # (the 808 pitch-drop box) and the lead sat 84% own-lowmid with nothing
    # above (dull patch, not register — C4-D#5 fundamentals ARE lowmid). The
    # classic first-hour mixer moves, applied at birth: box-cut bells on
    # kick+bass, presence shelf on the lead, rumble-shelf off the pads. EQ
    # rides AFTER fx_saturate (a cut before it just gets regenerated) and
    # APPENDS on lanes whose fx[0] is an automation target (arrange's bloom).
    CLASS_FX = {
        "kick":    [{"type": "eq", "params": {"midFreq": 300.0, "midGain": -3.5, "midQ": 1.1}},
                    {"type": "comp", "params": {"threshold": -18.0, "ratio": 3.0,
                                                "attack": 12.0, "release": 90.0, "outputDb": 1.0}}],
        "snare":   [{"id": "fx_comp", "params": {"thresh": -18.0, "ratio": 3.0,
                                                 "attack": 4.0, "release": 90.0,
                                                 "makeup": 1.5}},
                    {"type": "eq", "params": {"midFreq": 2800.0, "midGain": 2.5, "midQ": 0.9,
                                              "loFreq": 120.0, "loGain": -1.5}}],
        "clap":    [{"type": "eq", "params": {"midFreq": 2400.0, "midGain": 2.0, "midQ": 0.8}}],
        "hat":     [{"type": "eq", "params": {"loFreq": 350.0, "loGain": -7.0}},
                    {"id": "fx_widen", "params": {"width": 1.15, "rate": 0.15}}],
        "openhat": [{"type": "eq", "params": {"loFreq": 350.0, "loGain": -7.0}},
                    {"id": "fx_widen", "params": {"width": 1.25, "rate": 0.12}}],
        "ride":    [{"type": "eq", "params": {"loFreq": 400.0, "loGain": -6.0}}],
        "bass":    [{"id": "fx_saturate", "params": {"drive": 1.6, "mix": 0.35, "tone": 3200.0}},
                    # W95 THE GLUE: gentle comp AFTER the saturator locks the
                    # foundation (critic round: "saturate != glue" — true)
                    {"id": "fx_comp", "params": {"thresh": -20.0, "ratio": 2.5,
                                                 "attack": 12.0, "release": 160.0,
                                                 "makeup": 2.5}},
                    {"id": "fx_filter", "params": {"cutoff": 9000.0, "res": 0.1}},
                    {"type": "eq", "params": {"midFreq": 380.0, "midGain": -2.0, "midQ": 1.0}}],
        "lead":    [{"id": "fx_delay", "params": {"time": dotted8, "feedback": 0.3, "mix": 0.18}},
                    {"id": "fx_widen", "params": {"width": 1.25, "rate": 0.14}},
                    {"type": "eq", "params": {"midFreq": 300.0, "midGain": -2.0, "midQ": 0.9,
                                              "hiFreq": 2800.0, "hiGain": 2.5}}],
        "color":   [{"id": "fx_filter", "params": {"cutoff": 6500.0, "res": 0.15}},
                    {"id": "fx_widen", "params": {"width": 1.4, "rate": 0.1}},
                    {"type": "eq", "params": {"loFreq": 150.0, "loGain": -4.0}}],
        "arp":     [{"id": "fx_filter", "params": {"cutoff": 5200.0, "res": 0.12}},
                    {"id": "fx_widen", "params": {"width": 1.6, "rate": 0.2}}],
    }
    def base_name(nm):
        return nm[:-1] if nm.endswith("R") else nm    # stereo doubles share class fx
    # (W44 lowmid-led rebalance HONEST-KILLED 2026-07-10: a blanket +-dB
    # shift across the 68 lowmid-led genres distorted share-based verdicts —
    # band_energy_pct is RELATIVE, so cutting low re-normalizes mud UP — and
    # +-2dB can't move a 60-point low dominance. The family needs KG-level
    # curation: per-genre voicing windows and bass style/voice. Receipts in
    # GENERATION_UPLIFT item 80.)
    # W43 THE ORGAN MUD CUT (breadth census 2026-07-10): organ/dark-keys color
    # voices stack fundamentals in 120-500Hz — jazz 33%, reggae 36%, bossanova
    # 38%, afrobeat 37% lowmid vs records ~10%. Those voices earn a box-cut
    # bell at birth; pad-family colors (already voiced above the mud) don't.
    _ORGAN_DARK = {"hammond_organ", "organ_soul", "keys_dark", "jazz_piano",
                   "rhodes", "clav_funk"}
    _mudcut_on = os.environ.get("SOTADAW_MUDCUT", "1") != "0"
    for t in tracks:
        chain = CLASS_FX.get(base_name(t["name"]))
        if chain and not t.get("fx"):
            t["fx"] = json.loads(json.dumps(chain))   # deep copy per track
            if (_mudcut_on and base_name(t["name"]) == "color"
                    and (t.get("source") or {}).get("id") in _ORGAN_DARK):
                t["fx"].append({"type": "eq",
                                "params": {"midFreq": 320.0, "midGain": -3.5,
                                           "midQ": 0.9}})
            # THE MEASURED OWNER (census probe): bass_warm's 2nd/3rd
            # harmonics ARE the 120-500 mud — but ONLY where the genre
            # doesn't WANT lowmid leading (W45 calibration: jazz/bossa/gospel
            # families live at 25-40% lowmid by identity; cutting their bass
            # warmth serves a mis-calibrated metric, not the music). Reggae-
            # class (low-led targets) keeps the cut.
            if (_mudcut_on and base_name(t["name"]) == "bass"
                    and not str(dna.get("band_order") or "").startswith("lowmid")
                    and (t.get("source") or {}).get("id") in
                    ("bass_warm", "upright_bass")):
                t["fx"].append({"type": "eq",
                                "params": {"midFreq": 250.0, "midGain": -4.0,
                                           "midQ": 0.8}})
    # ---- THE CHOP LANE (vocal texture): house/garage records live on pitched
    # vocal chops; a chopless take reads instrumental-demo. formant_vox stabs on
    # the classic off-positions, chord-tone pitched, wet into the space bus.
    # Gated behind the experiment flag until the record-ruler proves it.
    if genre.lower() in CHOP_GENRES and os.environ.get("SOTADAW_NO_CHOPS") != "1":
        prog_c = grid.get("chords") or [[0, 1]]
        span_c = max(b for b, _ in prog_c) + 1
        def cdeg_at(bar):
            d = 1
            for b0, dd in sorted(prog_c):
                if bar % span_c >= b0:
                    d = dd
            return d
        chnotes = []
        positions = [(1.5, 0.78), (2.75, 0.66), (3.75, 0.7)] if rng.random() < 0.5 else \
                    [(0.75, 0.72), (1.5, 0.66), (2.5, 0.78)]
        for bar in range(bars):
            i = cdeg_at(bar) - 1
            tones = [60 + pcs[i % 7], 60 + pcs[(i + 4) % 7], 67 + pcs[i % 7]]
            for off, v in positions:
                if rng.random() < 0.85:
                    chnotes.append({"start": round(bar * 4.0 + off, 4),
                                    "len": 0.6, "pitch": int(rng.choice(tones)),
                                    "vel": round(v + rng.uniform(-0.04, 0.04), 3)})
        if chnotes:
            # SAMPLE CHOPS (W13): a REAL pitched vocal kit from the user's own
            # imports beats the synthesized formant every time one exists —
            # the sampler chord-pitches slices per note (Todd Edwards physics,
            # ±clamped to the kit's key span). Stranger boxes have no kits and
            # fall back to formant_vox (the zero-credential MAKE law). Kit
            # slices are wavs = deterministic renders. SOTADAW_SAMPLE_CHOPS=0
            # kills the sample path only.
            ckit = find_vocal_kit(rng) \
                if os.environ.get("SOTADAW_SAMPLE_CHOPS") != "0" else None
            if ckit:
                kname, klo, khi = ckit
                for nn in chnotes:
                    p = nn["pitch"]
                    while p > khi + 2:
                        p -= 12
                    while p < klo - 2:
                        p += 12
                    nn["pitch"] = int(max(klo - 2, min(khi + 2, p)))
                chop_src = {"kind": "sample", "kit": kname}
            else:
                chop_src = {"kind": "faust", "id": "formant_vox",
                            "params": {"vowel": round(rng.choice((0.05, 0.3, 0.75)), 2),
                                       "breath": 0.2, "attack": 0.008,
                                       "release": 0.18, "vibrato": 0.004}}
            tracks.append({"name": "chops", "source": chop_src,
                           "gainDb": -8, "pan": -0.22,
                           "fx": [{"id": "fx_filter", "params": {"cutoff": 5200.0, "res": 0.1}},
                                  {"id": "fx_widen", "params": {"width": 1.3}}],
                           "notes": chnotes})

    # ---- THE PUMP LAW: 4-on-floor pump genres duck the sustained layers against
    # the kick (rate = one duck per beat). The kick's pocket is the genre's ENGINE;
    # born-static pads are the demo tell. Data-gated: the grid must actually stomp.
    if genre.lower() in PUMP_GENRES and four_on_floor(grid.get("kick")):
        pump = {"id": "fx_pump", "params": {"rate": round(bpm / 60.0, 3),
                                            "depth": 0.42, "release": 0.22}}
        for t in tracks:
            if base_name(t["name"]) in ("color", "arp"):
                t.setdefault("fx", []).append(json.loads(json.dumps(pump)))

    # ---- SPACE AT BIRTH: one shared reverb return, melodic lanes send into it.
    # A bone-dry loop is the other demo tell; drums stay dry (the tight spine).
    # SPACE CHARACTER: the room IS a genre statement — dub swims in a dark long
    # tail, techno stays in a tight room, ambient opens a hall, house gets the
    # brighter plate-ish return. One knob-set per family, defaults for the rest.
    g_sp = genre.lower()
    if g_sp in ("dub", "reggae", "rocksteady", "roots_reggae", "triphop",
                "dub_techno", "lovers_rock"):
        sp_size, sp_damp = 2.4, 3800.0          # the dark king-tubby tail
    elif g_sp in ("ambient", "berlin_school", "drone", "chillout", "downtempo",
                  "dungeon_synth", "post_rock", "shoegaze", "dreampop"):
        sp_size, sp_damp = 3.0, 6000.0          # the hall
    elif g_sp in ("techno", "hard_techno", "minimal_techno", "ebm", "industrial",
                  "detroit_techno"):
        sp_size, sp_damp = 1.15, 4600.0         # the warehouse stays TIGHT
    elif g_sp in ("house", "deephouse", "chicago_house", "disco", "nu_disco",
                  "garage_house", "piano_house", "gospel_house", "boogie"):
        sp_size, sp_damp = 1.6, 6800.0          # brighter, plate-ish
    elif g_sp in ("jazz", "soul", "gospel", "bebop", "neo_soul", "motown",
                  "rnb", "blues"):
        sp_size, sp_damp = 1.35, 5000.0         # the room
    elif g_sp in ("trap", "drill", "phonk", "memphis_rap", "hiphop", "boombap",
                  "sexy_drill", "jersey_drill"):
        sp_size, sp_damp = 1.45, 4200.0         # dark + tight: the verb hides
    else:
        sp_size, sp_damp = 1.6, 5500.0
    buses = [{"id": "space", "gainDb": 0.0,
              "fx": [{"id": "fx_reverb", "params": {"size": sp_size, "damp": sp_damp, "mix": 1.0}},
              {"id": "fx_widen", "params": {"width": 1.5, "rate": 0.1}}]}]
    SEND_DB = {"color": -9.0, "lead": -10.0, "arp": -11.0, "snare": -14.0, "clap": -14.0,
               # W92 THE DRUM GLUE: the tick family was BONE DRY — the
               # "pasted on top" tell (critic round 2026-07-11). A breath of
               # the genre's own room, never a wash; the kick stays dry (sub law)
               "hat": -16.0, "openhat": -15.0, "ride": -15.0,
               "rim": -15.0, "ghost": -16.0}
    for t in tracks:
        nm = t["name"][:-1] if t["name"].endswith("R") else t["name"]
        if nm in SEND_DB:
            t["sends"] = [{"bus": "space", "gainDb": SEND_DB[nm]}]
    sub_dom = bool(dna.get("band_order") and str(dna["band_order"]).startswith("low"))
    # BIRTH LOUDNESS PRIOR (the single-render MAKE law): trim 2.0 lands takes at
    # ~-13.6 LUFS (measured, 3 genres +/-0.3). Genres whose MixTarget floor sits
    # ABOVE that (techno-family lo=-12) pre-stage the difference here so
    # make_track's loudness-recovery pass exits WITHOUT its extra render. The
    # truepeak wall absorbs the hotter drive; recovery stays as the corrector.
    trim = 2.0
    if dna.get("lufs_lo") is not None:
        trim = round(2.0 + max(0.0, min(4.0, float(dna["lufs_lo"]) + 13.6)), 1)
    song = {"version": 2, "bpm": bpm, "lengthBars": bars, "key": key,
            "swing": {"grid": grid.get("swing_grid", "16th"), "amount": float(grid.get("swing", 0.5))},
            "masterGainDb": 0.0,
            "buses": buses,
            # THE RELEASE WALL from birth: fx_truepeak is the real ISP wall
            # (fx_brickwall is sample-blind — takes shipped at -0.78 dBTP through it).
            # W93 THE AIR: bright-family records carry a 9k+ sheen ours
            # lacked (critic + judge both named the dead-highs class). A
            # gentle master shelf BEFORE the wall, curated genres only —
            # the amapiano law stands (darkness is identity elsewhere).
            "master": ([{"id": "fx_trim", "params": {"level": trim}}]
                       + ([{"type": "eq", "params": {"hiFreq": 9000.0, "hiGain": 2.5}}]
                          if (genre.lower() in AIR_GENRES
                              and os.environ.get("SOTADAW_AIR", "1") != "0") else [])
                       + [{"id": "fx_truepeak",
                           "params": {"ceiling": -1.5 if sub_dom else -1.2}}]),
            "_loop": {"genre": genre, "seed": seed,
                      # W87: the TAKE's progression (arrange + ruler read it)
                      "chords": [list(c) for c in (grid.get("chords") or [])]},
            "tracks": tracks}
    out = os.path.join(ROOT, "songs", f"{name}.json")
    json.dump(song, open(out, "w"), indent=1)
    # THE FEEL IS BORN IN: the genre's KG groove profile lands on the feel-carrier
    # lanes at birth (hats/percs/snare — kick and bass stay the anchor). Post-
    # humanize drift (~0.02) sits under apply_groove's 0.03 grid tolerance, so
    # the PROFILE timing replaces the random micro-drift exactly where it counts.
    gname = dna.get("groove")
    felt = []
    if gname:
        try:
            import groove as _groove
            for t in tracks:
                nm = t["name"].lower()
                if any(k in nm for k in ("hat", "perc", "shak", "snare", "clap", "ride", "tamb")):
                    r = _groove.apply_groove(out, t["name"], gname, 0.85)
                    if str(r).startswith("OK"):
                        felt.append(t["name"])
        except Exception:
            pass
    total = sum(len(t["notes"]) for t in tracks)
    feel = f", groove {gname} on {len(felt)} lanes" if felt else ""
    extras = [x for x, on in (("arp", any(t["name"] == "arp" for t in tracks)),
                              ("pump", any(any(f.get("id") == "fx_pump" for f in t.get("fx", []))
                                           for t in tracks)),
                              ("7ths" if genre.lower() in EXT_SEVENTH else "add9",
                               genre.lower() in EXT_SEVENTH | EXT_ADD9)) if on]
    feel += (", " + "+".join(extras)) if extras else ""
    return out, (f"{genre} loop '{name}': {bars} bars @ {bpm:.0f}bpm in {key}, "
                 f"{len(tracks)} tracks / {total} notes (archetype {pname}, bass {bstyle}, "
                 f"swing {grid.get('swing', 0.5)}, seed {seed}{feel})")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("genre"); ap.add_argument("name")
    ap.add_argument("--bars", type=int, default=4)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--bpm", type=float, default=None)
    ap.add_argument("--key", default=None)
    a = ap.parse_args()
    out, msg = generate(a.genre, a.name, a.bars, a.seed, a.bpm, a.key)
    print(msg if out is None else f"{out}\n{msg}")
    sys.exit(1 if out is None else 0)
