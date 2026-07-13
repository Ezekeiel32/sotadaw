#!/usr/bin/env python3
"""arrange.py — loop -> SONG SKELETON, deterministically (no LLM, no tokens).

  arrange.py <song.json> [--out name] [--form intro,build,drop,break,drop,outro]

Takes a loop song (e.g. generate_loop output) and builds a sectioned
arrangement by class-aware stripping (the scene_strips classifier):
  intro   drums-only, hats thinned          8 bars
  build   +bass, velocity ramp on hats      8 bars
  drop    everything (the loop as written)  16 bars
  break   no drums (musical moment)         8 bars
  outro   drums+bass thinning out           8 bars
Sections land in song.sections[]; a filter-open automation arc rides into
each drop (fx_filter cutoff late-bloom). Repeats honor the loop length.
"""
import argparse, copy, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import meter                               # THE WORLD GRID: the ONE bar resolver
from scene_strips import classify_track

HAT_PITCHES = {42, 44, 46}
SNARE_PITCHES = {38, 40}

def vary_rep(notes, rep, cls, loop_beats, inst=0, vkey=""):
    """Production values: no two repeats identical — WITHIN a section (rep =
    tile index) and ACROSS section instances (inst: drop2/chorus2 = 1, ...).
    Drums: odd passes thin the weakest hats + lean on backbeats; INSTANCE
    passes re-breathe the off-hats from a seeded rng (REPEAT CRIME, ledger
    dr07 2026-07-12: drop2 was onset-identical to drop with +5.6% velocity
    as the only difference). Melodic: a slow velocity phrase arc, phase-
    shifted per instance. Deterministic per (vkey, cls, inst, rep)."""
    import random as _rnd
    out = []
    prng = _rnd.Random(f"{vkey}/{cls}/{inst}/{rep}")
    for n in notes:
        v = n.get("vel", 0.8)
        p = n.get("pitch", 60)
        if cls == "drums" and (rep + inst) % 2 == 1 and p in HAT_PITCHES:
            if v < 0.5 and (int(n["start"] * 4) % 4) in (1, 3):
                continue                       # thin the weak off-hats every other pass
            if (n["start"] * 2) % 2 == 0:
                v = min(1.0, v + 0.05)         # lean on the strong eighths
        if cls == "drums" and inst >= 1 and p in HAT_PITCHES:
            if v < 0.55 and prng.random() < 0.18:
                continue                       # later instances breathe DIFFERENTLY
            v = max(0.05, v * prng.uniform(0.94, 1.08))
        if cls in ("other", "vox") and loop_beats > 0:
            import math
            v *= 0.94 + 0.08 * math.sin (2 * math.pi * (n["start"] / loop_beats
                                                        + rep * 0.25 + inst * 0.4))
        nn = dict(n); nn["vel"] = round(min(1.0, max(0.05, v)), 3)
        out.append(nn)
    return out

FORM = [("intro", 8), ("build", 8), ("drop", 16), ("break", 8), ("drop2", 8), ("outro", 8)]
# THE CLUB FORM (f155, cited): DJ intro = 16 bars of incremental layers, mixable
# 16-bar outro, twin drops — the extended-mix convention DJs can actually play.
CLUB_FORM = [("intro", 16), ("build", 8), ("drop", 16), ("break", 8),
             ("build2", 8), ("drop2", 16), ("outro", 16)]
# dr25 (2026-07-12): the PRE-CHORUS — 4 bars of rising tension before each
# of the first two choruses (the pop grammar's one missing organ; the third
# chorus arrives straight off the bridge, the classic payoff).
SONG_FORM = [("intro", 4), ("verse", 8), ("prechorus", 4), ("chorus", 8),
             ("verse2", 8), ("prechorus2", 4), ("chorus2", 8),
             ("bridge", 4), ("chorus3", 8), ("outro", 4)]
# genres that live in verse/chorus land, not drop land
SONG_FORM_GENRES = {"gospel", "soul", "country", "blues", "rock", "indie_rock",
                    "jazz", "reggae", "rocksteady", "ska", "bossanova", "citypop",
                    "jpop", "kpop", "synthpop", "bachata", "salsa", "merengue"}
# THE RAP FORM (wave 43, ledger dr24): rap is VERSE/HOOK music — 16-bar verses
# over the FULL beat (rap verses never thin to a heartbeat; the vocal carries
# the contrast, so the instrumental stays steady), 8-bar hooks at full energy,
# one stripped 4-bar bridge, no drops, no risers. The transition language is
# the family fill (hat_stutter/ghost_drag) and the hook's own arrival.
RAP_FORM = [("intro", 4), ("verse", 16), ("chorus", 8), ("verse2", 16),
            ("chorus2", 8), ("bridge", 4), ("chorus3", 8), ("outro", 4)]
# THE LOOP FORM (wave 43): beat-tape/chill cultures (lofi/downtempo/vaporwave)
# are STEADY-STATE musics — the loop IS the song. Themes cycle with texture
# variation (vary_rep provides it), nothing drops, nothing builds theatrically;
# the intro/outro taper is the only arc.
LOOP_FORM = [("intro", 4), ("theme", 16), ("theme2", 16), ("theme3", 16),
             ("outro", 4)]
# THE THROUGH-COMPOSED FORM (2026-07-11): 12 genres carry form_family
# "through_composed" in the KG — and arrange.py never read it, so a CARNATIC RAGA
# arranged intro/build/DROP/break/DROP2/outro. These musics have no drop and no
# repeated hook: they UNFOLD (alapana -> jor -> jhala; post-rock's quiet-to-wall
# crescendo; qawwali's accelerating ecstasy; free jazz's head -> collective climax).
# So: one monotonic arc — texture alone, theme enters, rhythm joins, intensify,
# climax, release. Nothing repeats, nothing drops. Drop-keyed effects (risers,
# drop sweeps, hook anticipation) simply never fire — every one is guarded.
THROUGH_FORM = [("opening", 8), ("statement", 16), ("development", 16),
                ("intensify", 16), ("climax", 16), ("resolve", 8)]
KEEP = {                     # section -> which classes play
    "intro": {"drums"},
    "build": {"drums", "bass"},
    "drop": {"drums", "bass", "vox", "other"},
    "break": {"bass", "vox", "other"},
    "outro": {"drums", "bass"},
    "verse": {"drums", "bass"},          # the hook rests in verses
    "prechorus": {"drums", "bass", "other"},   # tension: full band minus the hook
    "chorus": {"drums", "bass", "vox", "other"},
    "bridge": {"bass", "vox", "other"},  # the no-drums moment
    # through-composed: the ensemble ACCUMULATES and never sheds
    "opening": {"other"},                        # texture/melody alone — no rhythm
    "statement": {"bass", "other"},              # the theme, with its ground
    "development": {"drums", "bass", "other"},   # rhythm joins
    "intensify": {"drums", "bass", "vox", "other"},
    "climax": {"drums", "bass", "vox", "other"},
    "resolve": {"bass", "other"},                # the rhythm falls away, not the voice
    # loop family: the whole loop rides every theme — contrast lives in
    # vary_rep's texture variation + the intro/outro taper, never in stripping
    "theme": {"drums", "bass", "vox", "other"},
}
# THE BED LAW: records never go harmonically NAKED — the pad rides stripped
# sections as a quiet bed (records: filtered pad under the intro, thin pad in
# verses). Applies to color/pad lanes only; hooks and arps genuinely rest.
BED_VEL = {"intro": 0.45, "build": 0.65, "outro": 0.5, "verse": 0.6,
           "opening": 0.5, "statement": 0.62, "resolve": 0.55}   # through-composed
BED_NAMES = ("color", "pad")
# THE LRA ARC: records breathe ~6 LU across sections (measured: Entheogenic
# LRA 5.98 vs our arranged takes 3.5). Loudness lives at the SOURCE (velocity),
# never the master — every non-bed lane takes its section's energy tier, builds
# ramp INSIDE their own bounds (the old ramp normalized by the first two
# sections' span — already 1.0 by the time any classic-form build started).
SECTION_ENERGY = {"intro": 0.62, "verse": 0.82, "break": 0.74, "bridge": 0.72,
                  "prechorus": 0.88,      # dr25: above the verse, under the chorus
                  "outro": 0.85,
                  # through-composed: MONOTONIC growth to the climax, then release.
                  # (no drop tier here — "climax" is the peak and takes the source's
                  # own full velocity, like a drop does, by being absent from the map)
                  "opening": 0.45, "statement": 0.62, "development": 0.78,
                  "intensify": 0.9, "resolve": 0.6,
                  # loop family: steady-state — themes sit one hair under full
                  # so the arch law's intro/outro taper is the only contrast
                  "theme": 0.88}
# THE MOTIF LAW: records never abandon the hook — verses carry a THINNED
# variant (strong-beat skeleton, an octave down, quiet: same melody FAMILY,
# different intensity) and club builds ANTICIPATE it in their final 4 bars.
# The hook lane = the loop's lead voice; beds already have their own law.
MOTIF_NAMES = ("lead",)
MOTIF_VEL = {"verse": 0.6, "build": 0.75}
# FILL VOCABULARY: the run-up into a drop speaks the genre's language — a
# universal snare roll is a demo tell. Families: trap/drill fill with HAT
# stutters; dnb/jungle chop the break; funk/soul drag ghost ruffs; reggae/dub
# drop out (the one-drop IS space); house/techno keep the classic roll.
FILL_STYLE = {}
for _g in ("trap", "drill", "sexy_drill", "jersey_drill", "phonk", "driftphonk",
           "memphis_rap", "rage", "plugg", "pluggnb", "latin_trap", "crunk",
           "hyperpop", "digicore"):
    FILL_STYLE[_g] = "hat_stutter"
for _g in ("dnb", "jungle", "neurofunk", "breakbeat_hardcore", "breaks",
           "big_beat", "breakcore", "footwork"):
    FILL_STYLE[_g] = "break_chop"
for _g in ("funk", "soul", "gfunk", "disco", "boogie", "motown", "rnb",
           "new_jack_swing", "afrobeat", "neo_soul"):
    FILL_STYLE[_g] = "ghost_drag"
for _g in ("reggae", "rocksteady", "dub", "lovers_rock"):
    FILL_STYLE[_g] = "dropout"
# W80 THE FILL ATLAS: the census (radars 1-10) mapped every family's own
# turnaround language — 30 more genres leave the generic roll for the verb
# their records actually use. Existing verbs only; no new code paths.
for _g in ("grime", "sigilkore", "dariacore", "witch_house", "baile_funk",
           "jerseyclub", "baltimore_club", "bounce", "miami_bass",
           "ghettotech", "electro", "glitchcore", "wave", "hardwave",
           "darksynth"):
    FILL_STYLE[_g] = "hat_stutter"     # machine/808 stutter cultures
for _g in ("3step", "speed_garage", "bassline", "ukgarage", "uk_funky",
           "future_garage", "2step", "garage"):
    FILL_STYLE[_g] = "break_chop"      # the garage shuffle chop
for _g in ("bebop", "hard_bop", "swing_bigband", "modal_jazz", "free_jazz",
           "spiritual_jazz", "blues", "jazz", "jazzfusion"):
    FILL_STYLE[_g] = "ghost_drag"      # the brush/ruff drag
for _g in ("dancehall", "dub_techno"):
    FILL_STYLE[_g] = "dropout"         # the riddim/dub space
# THE CRASH GUARD (wave 43): a crash_noise cymbal at every arrival is club/pop
# language. Kit-less trad/folk song forms and mixing-desk dub never crash; rap
# and loop families keep ZERO EDM gestures (the ledger's world-class marker).
NO_CRASH_GENRES = {"flamenco", "mariachi", "tango", "klezmer", "celtic",
                   "gnawa", "forro", "samba", "bossanova", "fado", "dub"}


GRAMMAR = os.path.join(ROOT, "library", "benchmarks", "harmonix", "label_grammar.json")
POP2ARRANGE = {"intro": "intro", "verse": "build", "chorus": "drop", "build": "build",
               "bridge": "break", "break": "break", "inst": "build", "outro": "outro"}


def sample_pop_form(seed=0, max_sections=11):
    """A pop FORM sampled from the Harmonix label grammar (912 human structures):
    Markov walk over the measured bigrams, mapped onto arrange's section classes.
    Deterministic per seed. Falls back to the classic form if no grammar file."""
    import random
    if not os.path.exists(GRAMMAR):
        return ["intro", "build", "drop", "break", "drop", "outro"]
    g = json.load(open(GRAMMAR))
    big = {}
    for k, c in g["bigrams"].items():
        a, b = k.split(">")
        if a in POP2ARRANGE and b in POP2ARRANGE:
            big.setdefault(a, []).append((b, c))
    rng = random.Random(seed)
    cur, out = "intro", ["intro"]
    while len(out) < max_sections:
        nxt = big.get(cur)
        if not nxt:
            break
        labels, weights = zip(*nxt)
        cur = rng.choices(labels, weights=weights)[0]
        if cur == "outro" and len(out) < 4:
            continue                            # too early to leave
        if len(out) >= 2 and out[-1] == out[-2] == cur:
            continue                            # cap same-label runs at 2 (triple
        out.append(cur)                         # intros are data noise, not form)
        if cur == "outro":
            break
    if out[-1] != "outro":
        out.append("outro")
    return [POP2ARRANGE[l] for l in out], out


DNA_CACHE = os.path.join(ROOT, "agent", "dna_cache.json")


def form_family_for(genre):
    """KG form_family via the baked cache. FAIL-CLOSED (ledger 2026-07-12 CRIT):
    any read/parse failure returns None and the router lands on SONG_FORM —
    a torn/rewriting cache must never hand every genre the EDM drop form."""
    try:
        c = json.load(open(DNA_CACHE))["genres"]
        ff = (c.get(genre) or {}).get("form_family")
        return ff if isinstance(ff, str) and ff else None
    except Exception:
        return None


def arrange(song_path, out_name=None, form=None, genre=None, seed=0):
    song = json.load(open(song_path))
    # THE WORLD GRID (BEST_DAW_30 #1): _BQ = the bar's quarter-beats. Every
    # bar<->beat crossing below rides it, so a 7/8 loop ARRANGES in 7/8 —
    # sections, journeys, drops, fills and automation all land on real
    # barlines. Mapless songs give _BQ = 4.0 and every formula is bit-for-bit
    # what it was (the identity law; tools/meter_battery.py is the court).
    # UNIFORM meters only: loop_gen stamps one meterMap row at bar 0. A
    # mid-song meter change survives the copy but is not yet re-planned —
    # that's the follow-on wave.
    _BQ = meter.beats_in_bar(meter.song_meter(song), 0)
    loop_beats = float(song.get("lengthBars", 4)) * _BQ
    g = (genre or str(song.get("comment", "")).split("loop:")[-1].strip()
         or (song.get("_loop") or {}).get("genre", "")).lower()   # _loop = birth provenance

    fam = form_family_for(g)
    if fam == "pop" and not form:
        # W43 pop-seed law (ledger HIGH): every make_track sampled the SAME
        # fixed-seed skeleton at a flat 8 bars. The take's seed now rides in,
        # and the grammar's own mean section durations set the bar counts —
        # the identical mapping finish.py and the CLI --form pop already use.
        _res = sample_pop_form(seed)
        classes = _res[0] if isinstance(_res, tuple) else _res   # (classes, labels) tuple
        raw = _res[1] if isinstance(_res, tuple) else list(classes)
        try:
            _dur = json.load(open(GRAMMAR)).get("mean_duration_s", {})
        except Exception:
            _dur = {}
        _DEF = {"intro": 15.5, "verse": 24.0, "chorus": 21.1, "build": 14.6,
                "bridge": 23.4, "break": 9.0, "outro": 18.6, "inst": 20.6}
        _bpm = float(song.get("bpm", 120))
        seen, plan = {}, []
        for base, rw in zip(classes, raw):
            sec_s = float(_dur.get(rw, _DEF.get(rw, 20.0)))
            bars = max(4, min(16, int(round(sec_s * _bpm / 60.0 / _BQ / 4.0) * 4)))  # grid-ok: /_BQ crossed to bars; the /4*4 quantizes to 4-BAR PHRASES (form, not meter)
            seen[base] = seen.get(base, 0) + 1
            plan.append((base if seen[base] == 1 else f"{base}{seen[base]}", bars))
    else:
        # FAIL-CLOSED ROUTER (wave 43): an unassigned genre gets the safe
        # verse/chorus form — never the EDM drop+riser betrayal. The legacy
        # drop FORM survives only as an explicit `form` argument.
        plan = form or (CLUB_FORM if fam == "club"
                        else THROUGH_FORM if fam == "through_composed"
                        else RAP_FORM if fam == "rap"
                        else LOOP_FORM if fam == "loop"
                        else SONG_FORM)
    total_bars = sum(b for _, b in plan)
    out = copy.deepcopy(song)
    out["lengthBars"] = total_bars
    out["sections"] = []
    classes = {t.get("name", ""): classify_track(t) for t in song["tracks"]}
    _has_verse = any(s.rstrip("0123456789") == "verse" for s, _ in plan)
    _outro_speaks = os.environ.get("SOTADAW_OUTRO", "1") != "0"
    _vb_on = os.environ.get("SOTADAW_VERSEBAND", "1") != "0"
    # W25: the verse SITS BACK — the deeper energy tier is half of the verse-
    # band law (the skeleton thin below is the other half); together they buy
    # the LRA contrast records breathe with (measured: thin alone +0.2 LU)
    _sec_energy = dict(SECTION_ENERGY)
    if _vb_on and _has_verse and fam != "rap":
        # rap exemption (wave 43): rap verses ride the SAME beat as the hook —
        # the vocal carries the contrast; <=2 LU intro-to-body is the bar
        _sec_energy["verse"] = 0.72
    # W28 THE DYNAMIC ARCH: records breathe ~6 LU; we measured 3.6-4.4.
    # Quiet ends quieter (verse/intro sink another x0.89), loud end louder
    # (the FINAL arrival leans in x1.06, post-pass below). Orthogonal flag —
    # stacks multiplicatively on the verse-band tier. SOTADAW_ARCH=0 kills.
    _arch_on = os.environ.get("SOTADAW_ARCH", "1") != "0"
    if _arch_on:
        _sec_energy["intro"] = round(_sec_energy.get("intro", 0.62) * 0.89, 3)
        if _has_verse and fam != "rap":          # rap: steady verses (wave 43)
            _sec_energy["verse"] = round(_sec_energy.get("verse", 0.82) * 0.89, 3)

    for t in out["tracks"]:
        src_notes = t.get("notes", [])
        cls = classes[t.get("name", "")]
        new_notes = []
        cursor_bar = 0
        for sec, bars in plan:
            secbase = sec.rstrip("0123456789")
            name_l = t.get("name", "").lower()
            allowed = cls in KEEP[secbase] or cls in KEEP.get(sec, set())
            bed_scale = None
            motif = None                   # None | "verse" | "build" (the thinned hook)
            if not allowed and secbase in BED_VEL and any(w in name_l for w in BED_NAMES):
                allowed, bed_scale = True, BED_VEL[secbase]   # the bed law
            elif not allowed and secbase in MOTIF_VEL and any(w in name_l for w in MOTIF_NAMES):
                allowed, motif = True, secbase                # the motif law
            if secbase == "intro" and cls == "drums" and not any(w in name_l for w in ("kick", "hat")):
                allowed = False            # real intros strip to kick+hat
            if allowed:
                sec_beats = bars * _BQ
                reps = int(sec_beats // loop_beats) or 1
                sec_end = (cursor_bar + bars) * _BQ
                song_end = total_bars * _BQ
                # REPEAT CRIME (dr07): which INSTANCE of this section base is
                # this (drop=0, drop2=1, chorus3=2)? Later instances vary.
                _inst = 0
                if sec != secbase:
                    try:
                        _inst = int(sec[len(secbase):]) - 1
                    except ValueError:
                        _inst = 0
                _rv_on = os.environ.get("SOTADAW_REPEATVAR", "1") != "0"
                for r in range(reps):
                    base = cursor_bar * _BQ + r * loop_beats
                    rep_notes = vary_rep(src_notes, r, cls, loop_beats,
                                         inst=_inst if _rv_on else 0, vkey=sec)
                    for n in rep_notes:
                        if n["start"] >= loop_beats:
                            continue
                        if base + n["start"] >= sec_end or base + n["start"] >= song_end:
                            continue                 # clamp to section AND song bounds
                                                     # (the out-of-bounds boundary bug, firing 66)
                        v = n.get("vel", 0.8)
                        oct_shift = 0
                        if motif is not None:
                            # thinned hook: strong-beat skeleton only, an octave
                            # down in verses (a whisper of the chorus, not a copy);
                            # tolerance covers the birth humanize drift (~0.02)
                            frac = n["start"] % 1.0
                            if 0.08 < frac < 0.92:
                                continue
                            if motif == "build" and base + n["start"] < sec_end - 16.0:
                                continue             # builds ANTICIPATE: last 4 bars only
                            v *= MOTIF_VEL[motif]
                            if motif == "verse":
                                oct_shift = -12
                        if bed_scale is not None:
                            v *= bed_scale           # beds carry their own (deeper) tier
                        elif motif is None and secbase in _sec_energy:
                            v *= _sec_energy[secbase]      # the LRA arc rides the source
                        if sec == "intro" and cls == "drums" and n.get("pitch", 60) in (42, 44, 46):
                            if (n["start"] * 4) % 2 == 1:
                                continue               # thin hats: drop odd 16ths
                            if base + n["start"] < bars * 2.0:
                                continue               # staircase: hats join at the midpoint
                        # REPEAT CRIME (dr07): verse2+ SUBTRACTS — the bed
                        # thins for the section's first half ("we have been
                        # here before, listen closer"); lead/bass/drums carry.
                        if (_rv_on and _inst >= 1 and secbase == "verse"
                                and cls == "other"
                                and any(w in name_l for w in ("color", "arp", "pad"))
                                and base + n["start"] < cursor_bar * _BQ + bars * _BQ * 0.5):
                            continue
                        if secbase in ("build", "prechorus"):
                            # ramp INSIDE this section's own bounds (any buildN; the old
                            # form normalized by plan[:2] = already 1.0 at build's start)
                            prog = (base + n["start"] - cursor_bar * _BQ) / max(1.0, bars * _BQ)
                            v = min(1.0, v * (0.62 + 0.38 * min(1.0, prog)))
                        if secbase == "drop" and sec != "drop":
                            v = min(1.0, v * 1.06)   # later drops HIT harder (escalation law)
                        if sec == "outro":
                            # W23: club outros SUBTRACT (staged exits, post-
                            # pass) — a fade is a demo tell. Song forms keep
                            # the gentle ramp under the tag.
                            if not (_outro_speaks and not _has_verse):
                                done = (base + n["start"] - (total_bars - plan[-1][1]) * _BQ) / (plan[-1][1] * _BQ)
                                v = max(0.15, v * (1.0 - 0.6 * max(0.0, done)))
                        nn = dict(n)
                        nn["start"] = round(base + n["start"], 4)
                        nn["vel"] = round(v, 3)
                        if oct_shift:
                            nn["pitch"] = max(24, nn.get("pitch", 60) + oct_shift)
                        new_notes.append(nn)
            cursor_bar += bars
        t["notes"] = new_notes

    # ---- THE HARMONIC JOURNEY (W15): a loop repeated 14x is not a song. ----
    # Sections move in DEGREE SPACE — every melodic lane remaps by the same
    # scale-degree shift, so pitches stay IN KEY by construction and the hook
    # engine's internal aim survives (relative intervals preserved):
    #   chorus/drop  +2 degrees (the third-up lift — relative-major brightness)
    #   bridge/break -2 degrees (the third-down surprise — the iv color)
    #   cadence bar  -1 degree on the bar BEFORE every drop (the step-down
    #                turnaround the whole band plays into the hit)
    #   final drop   lead +12 (the last-chorus-lifts-an-octave law)
    # Drums untouched. Additive + fail-open: the journey must never kill arrange.
    try:
        sys.path.insert(0, os.path.join(ROOT, "tools"))
        import loop_gen as _lg
        _root, _iv = _lg.key_scale(out.get("key") or "A minor")
        _pc_idx = {(_root + _iv[i]) % 12: i for i in range(7)}

        def _shift_pitch(p, degshift):
            idx = _pc_idx.get(p % 12)
            if idx is None:                          # off-scale (shouldn't exist)
                return p
            base = p - _iv[idx]
            nidx = idx + degshift
            return base + 12 * (nidx // 7) + _iv[nidx % 7]

        _SEC_SHIFT = _lg.SEC_SHIFT                   # THE ONE KERNEL (W32):
        _dnaJ, _ = _lg.genre_dna(g)
        _progJ = ((out.get("_loop") or {}).get("chords") or ((_dnaJ or {}).get("grid") or {}).get("chords") or [[0, 1]])
        _spanJ = max(b for b, _ in _progJ) + 1

        def _base_deg(bar):
            d = 1
            for b0, dd in sorted(_progJ):
                if bar % _spanJ >= b0:
                    d = dd
            return d

        _bar_shift = _lg.journey_bar_shifts(plan, total_bars,   # ruler shares it
                                            deg_of_bar=_base_deg)   # + W34 V-cadence
        _last_drop, _acc = None, 0
        for _sec, _bn in plan:
            if _sec.rstrip("0123456789") in ("drop", "chorus"):
                _last_drop = (_acc, _bn)
            _acc += _bn
        for t in out["tracks"]:
            if classes.get(t.get("name", "")) == "drums":
                continue
            for n in t.get("notes", []):
                _sh = _bar_shift[min(int(n["start"] // _BQ), total_bars)]
                if _sh:
                    n["pitch"] = int(max(24, min(103, _shift_pitch(n["pitch"], _sh))))
            if _last_drop and t.get("name", "").lower().startswith("lead"):
                _lb, _nb = _last_drop
                for n in t.get("notes", []):
                    if _lb * _BQ <= n["start"] < (_lb + _nb) * _BQ and n["pitch"] <= 88:
                        n["pitch"] += 12
    except Exception:
        pass

    # ---- W29: THE SECOND STATEMENT — long arrivals answer themselves ----
    # A 16-bar drop tiles the same 4-bar hook 4x (the last placement
    # photocopier at the section scale). Records restate: in the SECOND HALF
    # of every >=8-bar drop/chorus, the lead's WEAK-position chord tones
    # rotate within the triad (root->3rd->5th->root, nearest octave fold,
    # never above the section's own peak) — same rhythm, same anchors, a
    # varied answer. In key by construction (degree-space rotation on the
    # journey-shifted field). SOTADAW_SECOND=0 kills.
    try:
        if os.environ.get("SOTADAW_SECOND", "1") != "0":
            _dna9, _ = _lg.genre_dna(g)
            _prog9 = ((out.get("_loop") or {}).get("chords") or ((_dna9 or {}).get("grid") or {}).get("chords") or [[0, 1]])
            _span9 = max(b for b, _ in _prog9) + 1

            def _deg9(bar):
                d = 1
                for b0, dd in sorted(_prog9):
                    if bar % _span9 >= b0:
                        d = dd
                return d

            _acc9b = 0
            for _sec, _bn in plan:
                _isarr = _sec.rstrip("0123456789") in ("drop", "chorus")
                _s0, _s1 = _acc9b * _BQ, (_acc9b + _bn) * _BQ
                _acc9b += _bn
                if not _isarr or _bn < 8:
                    continue
                _mid = _s0 + (_s1 - _s0) / 2.0
                for t in out["tracks"]:
                    if not t.get("name", "").lower().startswith("lead"):
                        continue
                    _sect = [n for n in t.get("notes", [])
                             if _s0 <= n["start"] < _s1]
                    if not _sect:
                        continue
                    _peak = max(n["pitch"] for n in _sect)
                    for n in _sect:
                        if n["start"] < _mid:
                            continue
                        _fr = n["start"] % 1.0
                        if _fr < 0.08 or _fr > 0.92:
                            continue                 # anchors stay (strong_ct law)
                        _bj = min(int(n["start"] // _BQ), total_bars)
                        _cd = _deg9(_bj) + _bar_shift[_bj]
                        _tri = [(_root + _iv[(_cd + o - 1) % 7]) % 12
                                for o in (0, 2, 4)]
                        _pc = n["pitch"] % 12
                        if _pc not in _tri:
                            continue                 # NCTs keep their resolve path
                        _npc = _tri[(_tri.index(_pc) + 1) % 3]
                        _cand = _npc + 12 * ((n["pitch"] - _npc + 6) // 12)
                        if 24 <= _cand <= _peak:
                            n["pitch"] = int(_cand)
    except Exception:
        pass

    # ---- W36: THE PICKUP — song forms enter on the "and-a-ONE" ----
    # Song intros opened cold. Records PICK UP: a short ascending V-field
    # figure in the intro's last beat leads the band into verse 1 (W34's
    # dominant at the START). Three 8ths on the V triad, quiet, aimed to
    # land UNDER the verse register (it leads, never peaks). Song forms
    # only (club intros tease instead, W30). SOTADAW_PICKUP=0 kills.
    try:
        if (os.environ.get("SOTADAW_PICKUP", "1") != "0" and _has_verse
                and plan[0][0] == "intro"):
            _i_end2 = plan[0][1] * _BQ
            lead_trP = next((t for t in out["tracks"]
                             if t.get("name", "").lower() == "lead"
                             and t.get("notes")), None)
            if lead_trP is not None:
                _v1 = [n for n in lead_trP["notes"]
                       if _i_end2 <= n["start"] < _i_end2 + 16.0]
                if _v1:
                    _ceil = sorted(n["pitch"] for n in _v1)[len(_v1) // 2]
                    _vtri = sorted((_root + _iv[(5 + o - 1) % 7]) % 12
                                   for o in (0, 2, 4))
                    picks = []
                    for pc in _vtri:
                        p = pc + 12 * ((_ceil - 4 - pc) // 12)
                        while p >= _ceil:            # fold by OCTAVE — clamping
                            p -= 12                  # mangles the pitch class
                        while p < 36:
                            p += 12
                        if 36 <= p < _ceil:
                            picks.append(int(p))
                    picks = sorted(set(picks))[:3]
                    if len(picks) >= 2:
                        # triplet pickup, strictly INSIDE the last intro beat
                        # (a note AT the downbeat belongs to the verse and
                        # would take the pocket's lay-back — the 16.03 bug)
                        lead_trP["notes"].extend(
                            {"start": round(_i_end2 - 1.0 + j / 3.0, 4),
                             "len": 0.28, "pitch": p,
                             "vel": round(0.5 + 0.04 * j, 3)}
                            for j, p in enumerate(picks))
                        lead_trP["notes"].sort(key=lambda n: n["start"])
    except Exception:
        pass

    # ---- W30: THE INTRO TEASE — the record whispers its hook first ----
    # Club intros were drums + a dark bed for 16 bars. Records HINT: the
    # hook's opening phrase appears once in the intro's last 4 bars, an
    # octave down at half velocity — and the drop-arc filter is CLOSED
    # through the intro, so the tease lands muffled by construction (the
    # classic dark-hint-then-reveal). Club forms only (>=8-bar intro, no
    # verse); the phrase is copied from the FIRST arrival so it teases
    # exactly what the drop delivers. SOTADAW_TEASE=0 kills.
    try:
        if (os.environ.get("SOTADAW_TEASE", "1") != "0" and not _has_verse
                and plan[0][0] == "intro" and plan[0][1] >= 8):
            _i_end = plan[0][1] * _BQ
            _arr0, _accT = None, 0
            for _sec, _bn in plan:
                if _sec.rstrip("0123456789") in ("drop", "chorus"):
                    _arr0 = _accT * _BQ
                    break
                _accT += _bn
            lead_tr3 = next((t for t in out["tracks"]
                             if t.get("name", "").lower() == "lead"
                             and t.get("notes")), None)
            if _arr0 is not None and lead_tr3 is not None:
                _ph = [n for n in lead_tr3["notes"]
                       if _arr0 <= n["start"] < _arr0 + 8.0]
                _t0 = _i_end - 16.0
                tease = []
                for n in _ph:
                    m = dict(n)
                    m["start"] = round(_t0 + (n["start"] - _arr0), 4)
                    m["pitch"] = max(24, n["pitch"] - 12)
                    m["vel"] = round(n["vel"] * 0.5, 3)
                    if m["start"] < _i_end - 0.25:
                        tease.append(m)
                lead_tr3["notes"].extend(tease)
                lead_tr3["notes"].sort(key=lambda n: n["start"])
    except Exception:
        pass

    # ---- W31: THE REVEAL — the hook rests in breaks so its return HITS ----
    # Club breaks played the FULL hook over bass+pads = a drums-less drop
    # that spends the drop's reveal early. The lead (and its double) now
    # RESTS through break sections; color+bass carry the harmony, and the
    # hook's return at the next drop is the payoff. Club forms only (song-
    # form bridges FEATURE the lead by design). SOTADAW_REVEAL=0 kills.
    try:
        if os.environ.get("SOTADAW_REVEAL", "1") != "0" and not _has_verse:
            _bsp, _accR = [], 0
            for _sec, _bn in plan:
                if _sec.rstrip("0123456789") == "break":
                    _bsp.append((_accR * _BQ, (_accR + _bn) * _BQ))
                _accR += _bn
            if _bsp:
                for t in out["tracks"]:
                    if not t.get("name", "").lower().startswith("lead"):
                        continue
                    t["notes"] = [n for n in t.get("notes", [])
                                  if not any(a <= n["start"] < b for a, b in _bsp)]
    except Exception:
        pass


    # ---- W16: THE COUNTER-MELODY — the chorus earns an ANSWER voice ----
    # Records CONVERSE: the hook calls, a second voice answers IN THE GAPS —
    # never on top (it only plays where the lead is silent, interval algebra
    # below guarantees it). Chorus/drop sections only: arrival candy; its
    # absence everywhere else makes the drop bigger. Derived AFTER the journey
    # so it answers the SHIFTED chord field, in degree space (in key by
    # construction). Opposite pan = the stereo conversation. Fail-open.
    try:
        if os.environ.get("SOTADAW_COUNTER", "1") != "0":
            lead_tr = next(t for t in out["tracks"]
                           if t.get("name", "").lower().startswith("lead")
                           and t.get("notes"))
            _dna, _e = _lg.genre_dna(g)
            _prog = ((out.get("_loop") or {}).get("chords") or ((_dna or {}).get("grid") or {}).get("chords") or [[0, 1]])
            _pspan = max(b for b, _ in _prog) + 1

            def _deg_at(bar):
                d = 1
                for b0, dd in sorted(_prog):
                    if bar % _pspan >= b0:
                        d = dd
                return d

            _spans, _acc = [], 0
            for _sec, _bn in plan:
                if _sec.rstrip("0123456789") in ("chorus", "drop"):
                    _spans.append((_acc * _BQ, (_acc + _bn) * _BQ, 1.0))
                # W37: THE SECOND VERSE ANSWERS — verse 1 recites bare, verse
                # 2+ gains the counter softly (x0.72): the classic build
                # across verses. SOTADAW_COUNTER2=0 keeps verses bare.
                elif (_sec.rstrip("0123456789") == "verse" and _sec != "verse"
                      and os.environ.get("SOTADAW_COUNTER2", "1") != "0"):
                    _spans.append((_acc * _BQ, (_acc + _bn) * _BQ, 0.72))
                _acc += _bn
            cnotes = []
            # W85 THE COUNTER VARIES: the census read 2 unique cells / 8
            # windows — the answer alternated exactly TWO shapes by gap
            # parity, so every chorus repeat spoke the same cells. Six
            # chord-tone shapes now rotate by (statement, gap) arithmetic
            # (pure function: deterministic, no rng, court-stable).
            _SHAPES = ((4, 2, 0), (0, 2, 4), (4, 0, 2),
                       (0, 4, 2), (2, 4, 0), (2, 0, 4))
            for _si, (s0, s1, _vmul) in enumerate(_spans):
                starts_in = [n for n in lead_tr["notes"] if s0 <= n["start"] < s1]
                if not starts_in:
                    continue
                anchor = min(n["start"] for n in starts_in)   # the lead speaks first
                meds = sorted(n["pitch"] for n in starts_in)
                center = meds[len(meds) // 2] + 9             # answers sit a 6th above
                busy = sorted((max(n["start"], anchor),
                               min(n["start"] + max(0.1, n.get("len", 0.5)), s1))
                              for n in lead_tr["notes"]
                              if n["start"] < s1
                              and n["start"] + max(0.1, n.get("len", 0.5)) > anchor)
                merged = []
                for a, b in busy:
                    if merged and a <= merged[-1][1] + 1e-6:
                        merged[-1] = (merged[-1][0], max(merged[-1][1], b))
                    else:
                        merged.append((a, b))
                free, cur = [], anchor
                for a, b in merged:
                    if a - cur >= 0.95:               # a 2-note answer fits a 1-beat breath
                        free.append((cur, a))
                    cur = max(cur, b)
                if (s1 - 0.5) - cur >= 0.95:
                    free.append((cur, s1 - 0.5))
                k, gcount = 0, {}
                for fa, fb in free:
                    t0 = int(fa * 2.0 + 0.9999) / 2.0         # snap UP to the 8th grid
                    cnt = 3 if t0 + 1.45 <= fb else (2 if t0 + 0.95 <= fb else 0)
                    gp = int(t0 // 16)
                    if not cnt or gcount.get(gp, 0) >= 2:     # breathe: <=2 answers / 4 bars
                        continue
                    gcount[gp] = gcount.get(gp, 0) + 1
                    offs = _SHAPES[(_si * 3 + k) % len(_SHAPES)][:cnt]
                    for j, off in enumerate(offs):
                        tt = t0 + 0.5 * j
                        bj = min(int(tt // _BQ), total_bars)
                        cd = _deg_at(bj) + _bar_shift[bj] + off
                        pc = (_root + _iv[(cd - 1) % 7]) % 12
                        pitch = pc + 12 * int(round((center - pc) / 12.0))
                        while pitch > 100:            # fold by OCTAVE — a value clamp
                            pitch -= 12               # would mangle the pitch class
                        while pitch < 48:
                            pitch += 12
                        cnotes.append({"start": round(tt, 4), "len": 0.45,
                                       "pitch": int(pitch),
                                       "vel": round((0.5 + 0.03 * j) * _vmul, 3)})
                    k += 1
            if cnotes:
                lv_id = ((lead_tr.get("source") or {}).get("id") or "")
                # W27 THE COUNTER ATLAS: the answer voice speaks the family's
                # language (census 2026-07-10: a BELL answered black_metal).
                # Explicit picks outrank the seventh/bell default; collision
                # with the lead's own voice falls marimba -> fmbell.
                _CTR_ATLAS = {
                    "black_metal": "clean_chime_guitar",
                    "doom_metal": "clean_chime_guitar",
                    "post_metal": "clean_chime_guitar",
                    "stoner_rock": "clean_chime_guitar",
                    "sludge_metal": "clean_chime_guitar",
                    "djent": "clean_chime_guitar",
                    "metalcore": "clean_chime_guitar",
                    "nu_metal": "clean_chime_guitar",
                    "krautrock": "clean_chime_guitar",
                    "modal_jazz": "vibraphone", "spiritual_jazz": "vibraphone",
                    "jazz": "vibraphone", "bigband": "vibraphone",
                    "bebop": "vibraphone", "cool_jazz": "vibraphone",
                    "amapiano": "kalimba", "gqom": "kalimba",
                    "afro_house": "kalimba", "afrobeat": "kalimba",
                    "kwaito": "kalimba", "soukous": "kalimba",
                    "dembow": "marimba", "reggaeton": "marimba",
                    "dancehall": "marimba", "baile_funk": "marimba",
                    "bachata": "marimba", "salsa": "marimba",
                }
                cv = _CTR_ATLAS.get(g) or (
                    "vibraphone" if g in _lg.EXT_SEVENTH else "fmbell")
                if cv == lv_id:
                    cv = "marimba" if cv != "marimba" else "fmbell"
                lp = float(lead_tr.get("pan", 0.0) or 0.0)
                out["tracks"].append({
                    "name": "counter",
                    "gainDb": round(float(lead_tr.get("gainDb", -9.0)) - 4.0, 2),
                    "pan": -0.14 if lp >= 0 else 0.14,
                    "source": {"kind": "faust", "id": cv},
                    "sends": [dict(s) for s in (lead_tr.get("sends") or [])],
                    "notes": cnotes})
                classes["counter"] = "other"
    except Exception:
        pass

    # ---- W18: THE VERSE RECITES — verse content beyond subtraction ----
    # The motif law thins the hook to strong beats an octave down, but a -12
    # photocopy keeps the hook's exact contour: it reads as a QUIET CHORUS.
    # Real verses RECITE: a simple chord-frame chant (root/3rd/5th by beat
    # position) that saves the melody for the chorus. Rhythm inherited from
    # the motif skeleton (the song's rhythmic DNA); pitches re-aimed onto the
    # bar's chord — journey shifts included — folded into a tight octave
    # around the verse register; each verse cadences home to the root.
    # Builds keep the REAL hook (they tease the drop's melody). Fail-open.
    try:
        if os.environ.get("SOTADAW_VERSE", "1") != "0":
            _vspans, _acc = [], 0
            for _sec, _bn in plan:
                if _sec.rstrip("0123456789") == "verse":
                    _vspans.append((_acc * _BQ, (_acc + _bn) * _BQ))
                _acc += _bn
            if _vspans:
                _dna2, _ = _lg.genre_dna(g)
                _prog2 = ((out.get("_loop") or {}).get("chords") or ((_dna2 or {}).get("grid") or {}).get("chords") or [[0, 1]])
                _span2 = max(b for b, _ in _prog2) + 1

                def _deg2(bar):
                    d = 1
                    for b0, dd in sorted(_prog2):
                        if bar % _span2 >= b0:
                            d = dd
                    return d

                for t in out["tracks"]:
                    if not t.get("name", "").lower().startswith("lead"):
                        continue
                    for s0, s1 in _vspans:
                        vs = [n for n in t.get("notes", []) if s0 <= n["start"] < s1]
                        if not vs:
                            continue
                        _meds = sorted(n["pitch"] for n in vs)
                        _med = _meds[len(_meds) // 2]
                        _last = max(vs, key=lambda n: n["start"])
                        for n in vs:
                            _bj = min(int(n["start"] // _BQ), total_bars)
                            _cd = _deg2(_bj) + _bar_shift[_bj]
                            _off = (0, 2, 4, 2)[int(n["start"] % _BQ) % 4]
                            if n is _last:
                                _off = 0             # the phrase cadences home
                            _pc = (_root + _iv[(_cd + _off - 1) % 7]) % 12
                            _p = _pc + 12 * int(round((_med - _pc) / 12.0))
                            while _p > _med + 7:
                                _p -= 12
                            while _p < _med - 8:
                                _p += 12
                            n["pitch"] = int(_p)
    except Exception:
        pass

    # ---- W24: THE POCKET — verses lay back, choruses sit on top ----
    # The performance layer records have and grids don't: the singer relaxes
    # BEHIND the beat in verses (~20ms at 90bpm), deepest in the bridge; the
    # chorus arrives ON TOP. Deterministic constant per section (uniform
    # shift preserves the line's internal feel); note ENDS stay fixed (len
    # absorbs the shift) so nothing collides downstream. Shifts stay inside
    # the ruler's strong-beat tolerance (0.03/0.045 < TOL 0.08) and inside
    # the 16th-grid rounding window — the POCKET is felt, never "late".
    # Lead-family lanes only (the voice, not the band). SOTADAW_POCKET=0.
    try:
        if os.environ.get("SOTADAW_POCKET", "1") != "0" and _has_verse:
            _PKT = {"verse": 0.03, "bridge": 0.045}
            _acc7 = 0
            for _sec, _bn in plan:
                _lay = _PKT.get(_sec.rstrip("0123456789"))
                _s0, _s1 = _acc7 * _BQ, (_acc7 + _bn) * _BQ
                _acc7 += _bn
                if not _lay:
                    continue
                for t in out["tracks"]:
                    if not t.get("name", "").lower().startswith("lead"):
                        continue
                    for n in t.get("notes", []):
                        if _s0 <= n["start"] < _s1:
                            n["start"] = round(n["start"] + _lay, 4)
                            n["len"] = round(max(0.05, n["len"] - _lay), 4)
    except Exception:
        pass

    # ---- W89 THE PRE-CHORUS RISE: the answer voice CLIMBS into the chorus ----
    # Song forms ramp energy tiers into the chorus but nothing RISES — the
    # classic pre-chorus device is an ascending approach line that targets
    # the hook's entry from below (vel climbing, quarters into eighths,
    # landing a step under the hook's first note one beat before the
    # arrival — inside the W86 hole by design). Rides the counter lane
    # (the conversation lifts the chorus in); verse-having forms only.
    # SOTADAW_PRERISE=0 kills.
    try:
        if (os.environ.get("SOTADAW_PRERISE", "1") != "0"
                and (_has_verse or fam == "pop")):
            # pop's Harmonix grammar maps verses to "build" — the genre
            # that INVENTED the pre-chorus has no literal verse sections
            _leadR9 = next((t for t in out["tracks"]
                            if t.get("name") == "lead" and t.get("notes")), None)
            _ctrR9 = next((t for t in out["tracks"]
                           if t.get("name") == "counter"), None)
            _dsR9, _accR9 = [], 0
            for _sec, _bn in plan:
                if _sec.rstrip("0123456789") in ("chorus", "drop"):
                    _dsR9.append(_accR9 * _BQ)
                _accR9 += _bn
            if _leadR9 and _dsR9:
                _rroot, _riv = _lg.key_scale(out.get("key") or "A minor")
                _rise_added = []
                for ds in _dsR9:
                    if ds < 8.0:
                        continue
                    tgt = next((n["pitch"] for n in
                                sorted(_leadR9["notes"], key=lambda n: n["start"])
                                if n["start"] >= ds - 0.5), None)
                    if tgt is None:
                        continue
                    # 6 diatonic steps ending one scale step under the target
                    _scale = sorted({(_rroot + iv) % 12 for iv in _riv})
                    def _snap(p):
                        while p % 12 not in _scale:
                            p -= 1
                        return p
                    seq = []
                    pcur = _snap(tgt - 1)
                    for _k in range(6):
                        seq.append(pcur)
                        pcur = _snap(pcur - 1)
                    seq = seq[::-1]                     # ascending, ends under tgt
                    offs = (-8.0, -6.0, -4.0, -3.0, -2.0, -1.5)
                    for j, (off, pit) in enumerate(zip(offs, seq)):
                        _rise_added.append({"start": round(ds + off, 4),
                                            "len": 0.7 if off <= -4 else 0.4,
                                            "pitch": int(pit),
                                            "vel": round(0.5 + 0.056 * j, 3)})
                # the rise only APPENDS to a counter W16 already granted —
                # creating one would override the conditional law (synthwave's
                # unbreathing lead correctly has NO answer voice; its
                # form_family is "pop" so the fam gate alone is too wide)
                if _rise_added and _ctrR9 is not None:
                    _ctrR9["notes"].extend(_rise_added)
    except Exception:
        pass

    # ---- W88 THE BREAKDOWN MOMENT: the break gains its own texture ----
    # W31 made breaks REST (the payoff law) — but records fill the space
    # with a MOMENT heard nowhere else: the hook's opening phrase quoted
    # HALF-TIME, an octave up, quiet and washed in the space bus (dub does
    # exactly this with echoes). A new 'breath' lane (never lead*: the
    # W31 rest law stands untouched); the drop's return still pays because
    # the quote whispers. Every break >= 4 bars with a hook. Song-form
    # bridges keep their W39 feature instead. SOTADAW_BREATH=0 kills.
    try:
        if os.environ.get("SOTADAW_BREATH", "1") != "0" and not _has_verse:
            _bsp2, _accB = [], 0
            for _sec, _bn in plan:
                if _sec.rstrip("0123456789") == "break" and _bn >= 4:
                    _bsp2.append((_accB * _BQ, (_accB + _bn) * _BQ))
                _accB += _bn
            _leadB = next((t for t in out["tracks"]
                           if t.get("name") == "lead" and t.get("notes")), None)
            _ctrB = next((t for t in out["tracks"]
                          if t.get("name") == "counter"), None)
            if _bsp2 and _leadB:
                _dsB, _accD = [], 0
                for _sec, _bn in plan:
                    if _sec.rstrip("0123456789") == "drop":
                        _dsB.append(_accD * _BQ)
                    _accD += _bn
                _src0 = min(_dsB) if _dsB else 0.0
                _phrase = sorted((n for n in _leadB["notes"]
                                  if _src0 <= n["start"] < _src0 + 8.0),
                                 key=lambda n: n["start"])[:6]
                bnotes = []
                for a, b in _bsp2:
                    if not _phrase:
                        break
                    t0 = _phrase[0]["start"]
                    for n in _phrase:
                        st = a + 1.0 + (n["start"] - t0) * 2.0
                        if st + 0.2 >= b:
                            break
                        bnotes.append({"start": round(st, 4),
                                       "len": round(min(n.get("len", 0.5) * 2.0,
                                                        b - st - 0.1), 4),
                                       "pitch": int(n["pitch"]) + 12,
                                       "vel": 0.42})
                if bnotes:
                    _bvoice = ((_ctrB.get("source") or {}).get("id")
                               if _ctrB else None) or "vibraphone"
                    _lpB = float(_leadB.get("pan", 0.0) or 0.0)
                    out["tracks"].append({
                        "name": "breath",
                        "gainDb": round(float(_leadB.get("gainDb", -9.0)) - 5.0, 2),
                        "pan": 0.18 if _lpB >= 0 else -0.18,
                        "source": {"kind": "faust", "id": _bvoice},
                        "sends": [{"bus": "space", "gainDb": -6.0}],
                        "notes": bnotes})
                    classes["breath"] = "other"
    except Exception:
        pass

    # ---- W39: THE BRIDGE FEATURES — the instrumental eight ----
    # Song-form bridges played the hook (-2 shifted) on the same lead voice:
    # a photocopy with different pitches. Records HAND THE MELODY OVER — the
    # answer voice restates it while the lead rests (the instrumental
    # bridge). Notes MOVE lead -> counter (0.85x, pocket lay-back kept);
    # only when the song HAS a counter lane (conditional law: gospel's
    # dense recite has none and keeps its lead bridge). SOTADAW_BRIDGEFEAT=0.
    try:
        if os.environ.get("SOTADAW_BRIDGEFEAT", "1") != "0" and _has_verse:
            _ctrT = next((t for t in out["tracks"]
                          if t.get("name") == "counter"), None)
            _brsp, _accB = [], 0
            for _sec, _bn in plan:
                if _sec.rstrip("0123456789") == "bridge":
                    _brsp.append((_accB * _BQ, (_accB + _bn) * _BQ))
                _accB += _bn
            if _ctrT is not None and _brsp:
                for t in out["tracks"]:
                    if t.get("name", "").lower() != "lead":
                        continue
                    moved = [n for n in t.get("notes", [])
                             if any(a <= n["start"] < b for a, b in _brsp)]
                    if not moved:
                        continue
                    t["notes"] = [n for n in t["notes"] if n not in moved]
                    for n in moved:
                        m = dict(n)
                        m["vel"] = round(n["vel"] * 0.85, 3)
                        _ctrT["notes"].append(m)
                _ctrT["notes"].sort(key=lambda n: n["start"])
    except Exception:
        pass

    # ---- W25: THE VERSE BAND — the kit strips to its skeleton in verses ----
    # Integration listening: gospel LRA 3.7 vs the ~6 LU records breathe —
    # sections don't contrast because the band plays FULL in verses (kick on
    # every beat under a reciting vocal). Real bands sit back: verse kick =
    # the heartbeat (beats 1 & 3), verse snare = the backbeat only (ghost
    # ruffs rest until the chorus). Choruses get the full kit BACK — that
    # return IS the lift. Runs before transitions, so fills/turnarounds
    # still punctuate the thinned bed. Song forms only. SOTADAW_VERSEBAND=0.
    try:
        if _vb_on and _has_verse and fam != "rap":   # rap verses keep the FULL
            _acc8 = 0                                # beat (wave 43, ledger dr24)
            for _sec, _bn in plan:
                _isv = _sec.rstrip("0123456789") == "verse"
                _s0, _s1 = _acc8 * _BQ, (_acc8 + _bn) * _BQ
                _acc8 += _bn
                if not _isv:
                    continue
                for t in out["tracks"]:
                    if classes.get(t.get("name", "")) != "drums":
                        continue
                    nm_l = t.get("name", "").lower()
                    if "kick" in nm_l:
                        kept = [n for n in t["notes"]
                                if not (_s0 <= n["start"] < _s1)
                                or (lambda fr: fr < 0.08 or abs(fr - 2.0) < 0.08
                                    or fr > 3.92)(n["start"] % _BQ)]
                        # never strip a verse to NO kick (odd meters/edge DNA)
                        if any(_s0 <= n["start"] < _s1 for n in kept):
                            t["notes"] = kept
                    elif any(n.get("pitch") in SNARE_PITCHES
                             for n in t.get("notes", [])):
                        t["notes"] = [
                            n for n in t["notes"]
                            if not (_s0 <= n["start"] < _s1
                                    and n.get("pitch") in SNARE_PITCHES)
                            or (lambda fr: abs(fr - 1.0) < 0.08
                                or abs(fr - 3.0) < 0.08)(n["start"] % _BQ)]
    except Exception:
        pass

    # ---- TRANSITIONS: the difference between a loop and a record ----
    names_all = [nm for nm, _ in plan]
    drop_starts = []
    acc = 0
    for nm, bars in plan:
        if nm.rstrip("0123456789") in ("drop", "chorus") and acc > 0:
            drop_starts.append(acc * _BQ)
        acc += bars
    snare_tr = next((t for t in out["tracks"]
                     if classes[t.get("name", "")] == "drums"
                     and any(n.get("pitch") in SNARE_PITCHES for n in t.get("notes", []))), None)
    hat_trs = [t for t in out["tracks"]
               if classes[t.get("name", "")] == "drums"
               and any(n.get("pitch") in HAT_PITCHES for n in t.get("notes", []))]
    # THE RISER LAW (drop forms only — no EDM sweeps into a gospel chorus):
    # bandpass-noise riser rides the last 2 bars into every drop, sweep timed to
    # land AT the downbeat; a ringing crash marks the arrival. Records mark their
    # transitions; loops that just "arrive" read as demos.
    drop_only, acc2 = [], 0
    for nm, bars_ in plan:
        if nm.rstrip("0123456789") == "drop" and acc2 > 0:
            drop_only.append(acc2 * _BQ)
        acc2 += bars_
    bpm_ = float(song.get("bpm", 120))
    # W20 TRANSITION VARIETY: the FIRST drop earns the riser; later drops
    # arrive DIFFERENTLY — a reverse-cymbal swell rising through THE GAP into
    # the slam (records never spend the same transition twice in a row).
    # SOTADAW_TRANSVAR=0 = every drop keeps the legacy riser.
    _tvar = os.environ.get("SOTADAW_TRANSVAR", "1") != "0"
    # THE GESTURE GUARD (wave 43, ledger HIGH): riser/reverse-cymbal sweeps are
    # CLUB-family language. They were keyed on the raw section name alone, so an
    # explicit drop-form on flamenco still got an EDM whoosh. Family, not name.
    if drop_only and fam == "club":
        sweep_s = round(8.0 * 60.0 / bpm_, 2)
        _riser_ds = drop_only[:1] if _tvar else drop_only
        riser_tr = {"name": "riser", "gainDb": -10.0, "pan": 0.0,
                    "source": {"kind": "faust", "id": "riser",
                               "params": {"sweep": min(20.0, sweep_s), "range": 24.0, "q": 1.5}},
                    "sends": [{"bus": "space", "gainDb": -8.0}],
                    "notes": [{"start": round(ds - 8.0, 4), "len": 7.9, "pitch": 55,
                               "vel": 0.72} for ds in _riser_ds if ds >= 8.0]}
        if riser_tr["notes"]:
            out["tracks"].append(riser_tr)
        if _tvar and drop_only[1:]:
            _sw = round(2.0 * 4.0 * 60.0 / bpm_ / 4.0, 2)   # 2 beats in seconds
            rev_tr = {"name": "revcrash", "gainDb": -13.0, "pan": -0.1,
                      "source": {"kind": "faust", "id": "rev_crash",
                                 "params": {"swell": min(6.0, _sw), "bright": 3200.0}},
                      "sends": [{"bus": "space", "gainDb": -10.0}],
                      "notes": [{"start": round(ds - 2.0, 4), "len": 1.98,
                                 "pitch": 49, "vel": 0.8}
                                for ds in drop_only[1:] if ds >= 2.0]}
            if rev_tr["notes"]:
                out["tracks"].append(rev_tr)
    # crash marks every arrival (drop AND chorus — a cymbal is genre-universal);
    # plus the OPENING SPLASH: records enter on a cymbal, demos start cold;
    # W20: break/bridge entries get a SOFT splash (the downshift marker)
    _soft_marks = []
    if _tvar:
        _acc3 = 0
        for nm, bars_ in plan:
            if nm.rstrip("0123456789") in ("break", "bridge") and _acc3 > 0:
                _soft_marks.append(_acc3 * _BQ)
            _acc3 += bars_
    _crash_ok = (fam in ("club", "pop")
                 or (fam in (None, "song") and g not in NO_CRASH_GENRES))
    if (drop_starts or _soft_marks) and _crash_ok:
        out["tracks"].append({"name": "crash", "gainDb": -14.0, "pan": 0.15,
                              "source": {"kind": "faust", "id": "crash_noise",
                                         "params": {"decay": 2.2}},
                              "sends": [{"bus": "space", "gainDb": -12.0}],
                              "notes": [{"start": 0.0, "len": 3.0, "pitch": 49, "vel": 0.6}]
                                       + [{"start": round(ds, 4), "len": 3.5,
                                           "pitch": 49, "vel": 0.9} for ds in drop_starts]
                                       + [{"start": round(bs, 4), "len": 3.0,
                                           "pitch": 49, "vel": 0.5} for bs in _soft_marks]})
    # THE FINAL CHORUS LIFT (REPEAT CRIME dr07/dr25, 2026-07-12): the LAST
    # chorus of a >=3-chorus form earns the classic escalation — the lead
    # doubled an octave up at reduced velocity (a new layer arriving reads
    # as intent; a byte-copied third chorus reads as a loop). Deterministic,
    # additive-only, and the base hook notes stay untouched (hook-sacred).
    if os.environ.get("SOTADAW_REPEATVAR", "1") != "0":
        _cur, _chorspans = 0, []
        for _nm, _b in plan:               # sections land in out[] later (1638);
            if _nm.rstrip("0123456789") == "chorus":   # the plan IS the truth here
                _chorspans.append((_cur * _BQ, (_cur + _b) * _BQ))
            _cur += _b
        if len(_chorspans) >= 3:
            _c0, _c1 = _chorspans[-1]
            _ld = next((t for t in out["tracks"]
                        if t.get("name", "").lower() == "lead" and t.get("notes")), None)
            if _ld is not None:
                _dbl = [dict(n, pitch=n["pitch"] + 12,
                             vel=round(max(0.05, n["vel"] * 0.55), 3))
                        for n in _ld["notes"]
                        if _c0 <= n["start"] < _c1 and n["pitch"] + 12 <= 103]
                if _dbl:
                    _ld["notes"] = sorted(_ld["notes"] + _dbl,
                                          key=lambda n: (n["start"], n["pitch"]))
    # fill default by FAMILY (wave 43, ledger HIGH): club/pop/unknown keep the
    # classic roll; rap defaults to its stutter culture; unmapped song genres
    # get the brush drag EXCEPT kit-less folk (a machine snare roll on a
    # flamenco record is the demo tell); loop/through-composed add nothing.
    _fill_def = ("roll" if fam in ("club", "pop", None)
                 else "hat_stutter" if fam == "rap"
                 else ("ghost_drag" if g not in NO_CRASH_GENRES else None)
                 if fam == "song" else None)
    fill = FILL_STYLE.get(g, _fill_def)
    # W38 THE LAST FILL: the final arrival earns the longest run-up — its
    # fill starts a bar EARLIER (additions land in [ds-12, ds-8), before the
    # LONG VOID eats the tail); every earlier arrival keeps the standard
    # fill. Family language: roll gains a quarter-note tier, stutter gains a
    # low 8th ramp, chop gains sparse early chops, drag gains a second ruff;
    # dropout stays silence. SOTADAW_LASTFILL=0 kills.
    _lastfill_on = os.environ.get("SOTADAW_LASTFILL", "1") != "0"
    _final_ds = drop_starts[-1] if drop_starts else None
    for ds in drop_starts:
        if _lastfill_on and ds == _final_ds and ds >= 12.0:
            if fill == "roll" and snare_tr is not None:
                sp0 = next((n["pitch"] for n in snare_tr["notes"]
                            if n.get("pitch") in SNARE_PITCHES), 38)
                snare_tr["notes"].extend(
                    {"pitch": sp0, "start": round(ds - 12.0 + i, 4),
                     "len": 0.6, "vel": round(0.35 + 0.05 * i, 3)}
                    for i in range(4))
            elif fill == "hat_stutter" and hat_trs:
                hp0 = next((n["pitch"] for n in hat_trs[0]["notes"]
                            if n.get("pitch") in HAT_PITCHES), 42)
                hat_trs[0]["notes"].extend(
                    {"pitch": hp0, "start": round(ds - 12.0 + i * 0.5, 4),
                     "len": 0.15, "vel": round(0.34 + 0.02 * i, 3)}
                    for i in range(8)
                    if not any(abs(n["start"] - (ds - 12.0 + i * 0.5)) < 0.2
                               and n.get("pitch") in HAT_PITCHES
                               for n in hat_trs[0]["notes"]))
            elif fill == "break_chop" and snare_tr is not None:
                sp0 = next((n["pitch"] for n in snare_tr["notes"]
                            if n.get("pitch") in SNARE_PITCHES), 38)
                snare_tr["notes"].extend(
                    {"pitch": sp0, "start": round(ds - 12.0 + o, 4),
                     "len": 0.15, "vel": v}
                    for o, v in ((1.25, 0.4), (2.75, 0.44), (3.5, 0.48))
                    if not any(abs(n["start"] - (ds - 12.0 + o)) < 0.2
                               and n.get("pitch") in SNARE_PITCHES
                               for n in snare_tr["notes"]))
            elif fill == "ghost_drag" and snare_tr is not None:
                sp0 = next((n["pitch"] for n in snare_tr["notes"]
                            if n.get("pitch") in SNARE_PITCHES), 38)
                snare_tr["notes"].extend(
                    {"pitch": sp0, "start": round(ds - 8.0 - o, 4),
                     "len": 0.1, "vel": v}
                    for o, v in ((0.375, 0.3), (0.25, 0.36), (0.125, 0.44))
                    if not any(abs(n["start"] - (ds - 8.0 - o)) < 0.15
                               and n.get("pitch") in SNARE_PITCHES
                               for n in snare_tr["notes"]))
        if fill == "hat_stutter" and hat_trs:
            # trap/drill language: the fill lives on the HATS — 16th ramp then
            # 32nd stutter burst into the wall; the snare keeps its backbeat.
            ht = hat_trs[0]
            hp = next((n["pitch"] for n in ht["notes"] if n.get("pitch") in HAT_PITCHES), 42)
            burst = [{"pitch": hp, "start": round(ds - _BQ + i * 0.25, 4),
                      "len": 0.12, "vel": round(0.5 + 0.03 * i, 3)} for i in range(int(_BQ * 2))]
            burst += [{"pitch": hp, "start": round(ds - _BQ * 0.5 + i * 0.125, 4),
                       "len": 0.1, "vel": round(0.62 + 0.022 * i, 3)} for i in range(int(_BQ * 4))]
            ht["notes"] = [n for n in ht["notes"]
                           if not (ds - _BQ <= n["start"] < ds and n.get("pitch") in HAT_PITCHES)]
            ht["notes"].extend(burst)
        elif fill == "break_chop" and snare_tr is not None:
            # dnb/jungle: displaced snare chops (the Amen turnaround), not a ramp
            sp = next((n["pitch"] for n in snare_tr["notes"] if n.get("pitch") in SNARE_PITCHES), 38)
            chops = [{"pitch": sp, "start": round(ds - _BQ + o, 4), "len": 0.2,
                      "vel": v} for o, v in ((0.0, 0.7), (0.75, 0.62), (1.25, 0.66),
                                             (2.0, 0.74), (2.75, 0.68), (3.25, 0.72),
                                             (3.5, 0.8), (3.75, 0.9)) if o < _BQ]
            snare_tr["notes"] = [n for n in snare_tr["notes"]
                                 if not (ds - _BQ <= n["start"] < ds and n.get("pitch") in SNARE_PITCHES)]
            snare_tr["notes"].extend(chops)
        elif fill == "ghost_drag" and snare_tr is not None:
            # funk/soul: keep the groove; a ghost ruff drags into the downbeat
            sp = next((n["pitch"] for n in snare_tr["notes"] if n.get("pitch") in SNARE_PITCHES), 38)
            snare_tr["notes"].extend(
                {"pitch": sp, "start": round(ds - o, 4), "len": 0.1, "vel": v}
                for o, v in ((0.375, 0.35), (0.25, 0.42), (0.125, 0.5)))
        elif fill == "dropout":
            pass                                     # reggae: the one-drop IS the fill
        elif snare_tr is not None:                   # the classic roll (house/techno land)
            sp = next((n["pitch"] for n in snare_tr["notes"] if n.get("pitch") in SNARE_PITCHES), 38)
            roll = []
            for i in range(int(_BQ * 2)):                       # bar -2: eighths, rising
                roll.append({"pitch": sp, "start": round(ds - 2 * _BQ + i * 0.5, 4),
                             "len": 0.4, "vel": round(0.4 + 0.05 * i, 3)})
            for i in range(int(_BQ * 4)):                      # bar -1: sixteenths into the wall
                roll.append({"pitch": sp, "start": round(ds - _BQ + i * 0.25, 4),
                             "len": 0.2, "vel": round(0.55 + 0.028 * i, 3)})
            snare_tr["notes"] = [n for n in snare_tr["notes"]
                                 if not (ds - 2 * _BQ <= n["start"] < ds and n.get("pitch") in SNARE_PITCHES)]
            snare_tr["notes"].extend(roll)
        if fill not in ("hat_stutter", "dropout"):
            for t in hat_trs:                        # pull the air out: last half-bar
                t["notes"] = [n for n in t["notes"]
                              if not (ds - 2.0 <= n["start"] < ds and n.get("pitch") in HAT_PITCHES)]
        for t in out["tracks"]:                      # slam the downbeat
            for n in t.get("notes", []):
                if abs(n["start"] - ds) < 0.05:
                    n["vel"] = 1.0
    # THE GAP: one beat of near-silence before every LATER drop (the first drop
    # keeps its full run-up) — tension physics records use constantly; the riser
    # sweeps through the hole, the downbeat SLAMS out of it. The snare roll is
    # trimmed to end where the gap begins.
    # W86 THE ARRIVAL STEP: the census measured first drops at -0.1..+0.3dB
    # (records step +2.5-5) — the FIRST drop was the one arrival WITHOUT a
    # hole (drop_only[1:]). Every arrival now earns the cut... SLAM.
    # Part 2, THE BASS RESERVATION: the hole alone moved trap/house 0.1dB —
    # the pre-window rides at full level because the BASS plays through the
    # build. Records reserve it (the bass's RETURN is the drop): bass-class
    # notes rest through the last 4 build bars before every arrival; tails
    # truncate at the reservation line. SOTADAW_BASSRESERVE=0 kills.
    if os.environ.get("SOTADAW_BASSRESERVE", "1") != "0":
        for ds in drop_only:
            rl = ds - 16.0
            if rl < 0:
                continue
            for t in out["tracks"]:
                if classes.get(t.get("name", "")) != "bass":
                    continue
                # the W34 V-cadence downbeat SURVIVES the reservation —
                # records rest the bass except the ONE dominant hit that
                # sets the arrival up (the battery caught the conflict)
                _cad = next((n for n in sorted(t.get("notes", []),
                                               key=lambda n: n["start"])
                             if ds - _BQ <= n["start"] <= ds - _BQ + 1.0), None)
                t["notes"] = [n for n in t.get("notes", [])
                              if n is _cad
                              or not (rl <= n["start"] < ds - 0.05)]
                for n in t["notes"]:
                    if (n is not _cad and n["start"] < rl
                            and n["start"] + n.get("len", 0.5) > rl):
                        n["len"] = round(max(0.1, rl - n["start"]), 4)
    for ds in drop_only:
        for t in out["tracks"]:
            if t.get("name") in ("riser", "revcrash"):
                continue                    # the swell PLAYS THROUGH the hole
            t["notes"] = [n for n in t.get("notes", [])
                          if not (ds - 1.0 <= n["start"] < ds - 0.05)]
            for n in t["notes"]:            # W86: tails RING through a hole
                if n["start"] < ds - 1.0 and n["start"] + n.get("len", 0.5) > ds - 1.0:
                    n["len"] = round(max(0.1, ds - 1.0 - n["start"]), 4)
    # THE LONG VOID: the FINAL drop earns a 2-beat hole (records give the last
    # chorus the biggest setup — roll... cut... void... SLAM; riser sweeps through)
    if len(drop_only) >= 2:
        ds = drop_only[-1]
        for t in out["tracks"]:
            if t.get("name") in ("riser", "revcrash"):
                continue                    # the swell PLAYS THROUGH the hole
            t["notes"] = [n for n in t.get("notes", [])
                          if not (ds - 2.0 <= n["start"] < ds - 0.05)]
            for n in t["notes"]:            # W86: the long void silences tails too
                if n["start"] < ds - 2.0 and n["start"] + n.get("len", 0.5) > ds - 2.0:
                    n["len"] = round(max(0.1, ds - 2.0 - n["start"]), 4)
    # THE END: records END (final downbeat hit + ring-out), demos fade to thin.
    end_beat = (total_bars - 1) * _BQ
    for t in out["tracks"]:
        nm = t.get("name", "")
        if nm == "crash":
            t["notes"].append({"start": end_beat, "len": 3.8, "pitch": 49, "vel": 0.85})
        elif classes.get(nm) == "bass" and t.get("notes"):
            root = min(n["pitch"] for n in t["notes"])
            t["notes"].append({"start": end_beat, "len": 3.5, "pitch": root, "vel": 0.85})
        elif classes.get(nm) == "drums" and "kick" in nm.lower() and t.get("notes"):
            t["notes"].append({"start": end_beat, "len": 0.3,
                               "pitch": t["notes"][0].get("pitch", 36), "vel": 0.9})
    # ---- W17: THE TURNAROUND — drums DEVELOP per phrase, never photocopy ----
    # Census receipt (2026-07-10): kick/snare/ghost = ONE unique cell across a
    # whole record. Real drummers mark every 4-bar phrase's LAST bar in the
    # genre's own language (FILL_STYLE doubles as the family map):
    #   hat_stutter (trap/drill)  kick PICKUP into the next phrase — spot
    #                             alternates by phrase parity (no two alike)
    #   break_chop  (dnb)         one displaced quiet snare chop
    #   ghost_drag  (funk/soul)   a ghost-snare breath, every other phrase
    #   roll        (house/tech)  clap/snare double every other phrase; the
    #                             KICK IS SACRED (four-on-floor never varies)
    #   dropout     (reggae)      nothing — the one-drop IS the language
    # Turnarounds only fire where drums CONTINUE (a pickup needs a landing);
    # fill/gap run-ups, outro and the END bar belong to transitions. Fail-open.
    try:
        if os.environ.get("SOTADAW_TURNAROUND", "1") != "0" and fill != "dropout":
            _excl = [(ds - 8.0, ds) for ds in drop_starts]
            _outro_b0 = ((total_bars - plan[-1][1]) * _BQ
                         if plan[-1][0].rstrip("0123456789") == "outro" else None)
            _drum_trs = [t for t in out["tracks"]
                         if classes.get(t.get("name", "")) == "drums" and t.get("notes")]
            _kick_tr = next((t for t in _drum_trs if "kick" in t.get("name", "").lower()), None)
            _clap_tr = next((t for t in _drum_trs if "clap" in t.get("name", "").lower()), None)

            def _zone_free(b):
                if any(a - 1e-6 <= b < z for a, z in _excl):
                    return False
                if _outro_b0 is not None and b >= _outro_b0:
                    return False
                return b < (total_bars - 1) * _BQ        # the END bar is sacred

            def _med_vel(tr):
                vs = sorted(n.get("vel", 0.8) for n in tr["notes"])
                return vs[len(vs) // 2] if vs else 0.7

            def _modal_pitch(tr):
                cnt = {}
                for n in tr["notes"]:
                    cnt[n["pitch"]] = cnt.get(n["pitch"], 0) + 1
                return max(cnt, key=cnt.get)

            def _spot_free(tr, at):
                return not any(abs(n["start"] - at) < 0.2 for n in tr["notes"])

            for _gi in range(total_bars // 4):   # grid-ok: 4-BAR phrase groups (the turnaround), not a bar->beat crossing
                _b1 = (_gi * 4 + 4) * _BQ                # end of the turnaround bar
                if not (_zone_free(_b1 - 0.5) and _zone_free(_b1 - 0.25)):
                    continue
                if not any(any(_b1 <= n["start"] < _b1 + 1.0 for n in t["notes"])
                           for t in _drum_trs):
                    continue                             # no landing = no pickup
                if fill == "hat_stutter" and _kick_tr is not None:
                    if sum(1 for n in _kick_tr["notes"]
                           if _gi * 16.0 <= n["start"] < _b1) < 2:
                        continue                         # breakdown groups stay silent
                    _at = _b1 - (0.5 if _gi % 2 == 0 else 0.25)
                    if _spot_free(_kick_tr, _at):
                        _kick_tr["notes"].append(
                            {"start": round(_at, 4), "len": 0.2,
                             "pitch": _modal_pitch(_kick_tr),
                             "vel": round(_med_vel(_kick_tr) * 0.62, 3)})
                elif fill == "break_chop" and snare_tr is not None:
                    # the chop lands where the break leaves room — candidates
                    # alternate by parity so no two turnarounds displace alike
                    _cands = ((0.75, 1.25) if _gi % 2 == 0 else (0.375, 1.75))
                    _at = next((_b1 - c for c in _cands
                                if _spot_free(snare_tr, _b1 - c)), None)
                    if (_at is not None
                            and sum(1 for n in snare_tr["notes"]
                                    if _gi * 16.0 <= n["start"] < _b1) >= 2):
                        snare_tr["notes"].append(
                            {"start": round(_at, 4), "len": 0.15,
                             "pitch": _modal_pitch(snare_tr),
                             "vel": round(_med_vel(snare_tr) * 0.5, 3)})
                elif fill == "ghost_drag" and snare_tr is not None and _gi % 2 == 1:
                    _at = _b1 - 0.375
                    if _spot_free(snare_tr, _at):
                        snare_tr["notes"].append(
                            {"start": round(_at, 4), "len": 0.1,
                             "pitch": _modal_pitch(snare_tr), "vel": 0.35})
                elif fill == "roll" and _gi % 2 == 1:
                    _tr = _clap_tr or snare_tr           # kick NEVER (sacred four-on-floor)
                    _at = _b1 - 0.5
                    if (_tr is not None
                            and sum(1 for n in _tr["notes"]
                                    if _gi * 16.0 <= n["start"] < _b1) >= 2
                            and _spot_free(_tr, _at)):
                        _tr["notes"].append(
                            {"start": round(_at, 4), "len": 0.15,
                             "pitch": _modal_pitch(_tr),
                             "vel": round(_med_vel(_tr) * 0.55, 3)})
    except Exception:
        pass

    # ---- W26: THE CHORUS LIFTS — the addition layer verses don't have ----
    # The other half of the LRA contrast (W25 sat the verse back; this
    # raises the chorus): records mark the chorus with ADDED fabric — a ride
    # wash on the 8ths and a clap doubling the backbeat. Pure addition (new
    # lanes; every existing lane byte-untouched); chorus/final-chorus only;
    # skipped when the song already carries a ride or clap lane (no
    # doubling); song forms only. SOTADAW_CHORUSLIFT=0 kills.
    try:
        if (os.environ.get("SOTADAW_CHORUSLIFT", "1") != "0" and _has_verse
                and _vb_on):
            _csp2, _acc9 = [], 0
            for _sec, _bn in plan:
                if _sec.rstrip("0123456789") == "chorus":
                    _csp2.append((_acc9 * _BQ, (_acc9 + _bn) * _BQ))
                _acc9 += _bn
            _names_l = {t.get("name", "").lower() for t in out["tracks"]}
            if _csp2 and "ride" not in _names_l:
                ride_notes = [
                    {"start": round(a + i * 0.5, 4), "len": 0.4, "pitch": 51,
                     "vel": round(0.38 + (0.04 if i % 2 == 0 else 0.0), 3)}
                    for a, b in _csp2 for i in range(int((b - a) * 2))]
                out["tracks"].append({
                    "name": "ride", "gainDb": -16.0, "pan": 0.3,
                    "source": {"kind": "faust", "id": "ride_cymbal"},
                    "sends": [{"bus": "space", "gainDb": -14.0}],
                    "notes": ride_notes})
                classes["ride"] = "drums"
            if _csp2 and "clap" not in _names_l:
                clap_notes = [
                    {"start": round(a + bb, 4), "len": 0.3, "pitch": 39,
                     "vel": 0.58}
                    for a, b in _csp2
                    for bb in [x + o for x in range(0, int(b - a), 4)
                               for o in (1.0, 3.0)]
                    if a + bb < b]
                out["tracks"].append({
                    "name": "clap", "gainDb": -13.0, "pan": 0.08,
                    "source": {"kind": "faust", "id": "clap_909"},
                    "sends": [{"bus": "space", "gainDb": -13.0}],
                    "notes": clap_notes})
                classes["clap"] = "drums"
    except Exception:
        pass

    # ---- W28: THE FINAL LEAN-IN — the last arrival plays the hardest ----
    # The loud half of THE DYNAMIC ARCH (quiet half rides _sec_energy above):
    # every lane leans in x1.06 (capped 1.0) across the FINAL chorus/drop
    # span — the band digs in for the last statement. Velocity only;
    # placement byte-identical. SOTADAW_ARCH=0 kills both halves.
    try:
        if _arch_on:
            _fin, _accA = None, 0
            for _sec, _bn in plan:
                if _sec.rstrip("0123456789") in ("chorus", "drop"):
                    _fin = (_accA * _BQ, (_accA + _bn) * _BQ)
                _accA += _bn
            if _fin:
                for t in out["tracks"]:
                    for n in t.get("notes", []):
                        if _fin[0] <= n["start"] < _fin[1]:
                            n["vel"] = round(min(1.0, n["vel"] * 1.06), 3)
    except Exception:
        pass

    # ---- W35: THE SUB DROP — the impact one-shot at the final arrival ----
    # The modern record's landing marker: a sine falling ~an octave under
    # the FINAL drop/chorus downbeat only (once per record — overuse is the
    # amateur tell). MONO SUB LAW: centered, dry, no sends. Only fires when
    # the arrival isn't the song's first bar. SOTADAW_SUBDROP=0 kills.
    try:
        if os.environ.get("SOTADAW_SUBDROP", "1") != "0":
            _fin2, _accS = None, 0
            for _sec, _bn in plan:
                if _sec.rstrip("0123456789") in ("chorus", "drop") and _accS > 0:
                    _fin2 = _accS * _BQ
                _accS += _bn
            if _fin2 is not None:
                out["tracks"].append({
                    "name": "subdrop", "gainDb": -8.0, "pan": 0.0,
                    "source": {"kind": "faust", "id": "subdrop",
                               "params": {"fall": 0.8, "ratio": 0.45}},
                    "notes": [{"start": round(_fin2, 4), "len": 2.0,
                               "pitch": 33, "vel": 0.9}]})
                classes["subdrop"] = "bass"
    except Exception:
        pass

    # ---- W21: THE HAT FABRIC — the texture changes with the section ----
    # Census receipt (2026-07-10): ONE unique hat cell across a whole record.
    # Records re-weave the fabric per section:
    #   verse       thin to the 8th grid (drop the e/a 16ths), slightly softer
    #               — the tight verse fabric that makes the chorus OPEN up
    #   drop2+/chorus2+  ACCENT INVERSION: offbeat 8ths lift over downbeats
    #               (velocity only — the "second drop floats" feel)
    # First drop/chorus keeps the reference fabric. SOTADAW_HATFAB=0 kills.
    try:
        if os.environ.get("SOTADAW_HATFAB", "1") != "0":
            _acc4 = 0
            for _sec, _bn in plan:
                _base = _sec.rstrip("0123456789")
                _s0, _s1 = _acc4 * _BQ, (_acc4 + _bn) * _BQ
                _acc4 += _bn
                if _base == "verse":
                    # adaptive thin: 16th fabrics lose the e/a; fabrics that
                    # are ALREADY 8ths lose the offbeat instead (-> quarters)
                    _sec_hats = [n for t in out["tracks"]
                                 if classes.get(t.get("name", "")) == "drums"
                                 for n in t["notes"]
                                 if n.get("pitch") in HAT_PITCHES
                                 and _s0 <= n["start"] < _s1]
                    _has16 = any((round((n["start"] % 1.0) * 4) % 4) in (1, 3)
                                 for n in _sec_hats)
                    _rest = (1, 3) if _has16 else (2,)
                    for t in out["tracks"]:
                        if classes.get(t.get("name", "")) != "drums":
                            continue
                        kept = []
                        for n in t["notes"]:
                            if (n.get("pitch") in HAT_PITCHES
                                    and _s0 <= n["start"] < _s1):
                                fr = round((n["start"] % 1.0) * 4) % 4
                                if fr in _rest:
                                    continue          # the fabric BREATHES
                                n = dict(n)
                                n["vel"] = round(n["vel"] * 0.92, 3)
                            kept.append(n)
                        t["notes"] = kept
                elif _base in ("drop", "chorus") and _sec != _base:
                    for t in out["tracks"]:
                        if classes.get(t.get("name", "")) != "drums":
                            continue
                        for n in t["notes"]:
                            if (n.get("pitch") in HAT_PITCHES
                                    and _s0 <= n["start"] < _s1):
                                fr = n["start"] % 1.0
                                if 0.42 < fr < 0.58:
                                    n["vel"] = round(min(1.0, n["vel"] * 1.12), 3)
                                elif fr < 0.08 or fr > 0.92:
                                    n["vel"] = round(n["vel"] * 0.96, 3)
    except Exception:
        pass

    # ---- W22: THE ARP BREATHES — the first drop restrains, later drops open ----
    # Census: 16 arp notes/bar at EVERY drop, identical rate — the fabric
    # never escalates. Records hold the first statement back and let the
    # later arrivals earn the full 16ths: the FIRST drop/chorus loses the
    # e/a 16ths on arp lanes (8th restraint, slightly softer); every later
    # drop keeps the full weave. Single-arrival forms untouched (nothing to
    # escalate toward). arp doubles transform identically (mirror preserved).
    # SOTADAW_ARPFAB=0 kills.
    try:
        if os.environ.get("SOTADAW_ARPFAB", "1") != "0":
            _arr = [(_sec, _bn) for _sec, _bn in plan]
            _n_arrivals = sum(1 for _sec, _ in _arr
                              if _sec.rstrip("0123456789") in ("drop", "chorus"))
            if _n_arrivals >= 2:
                _acc5 = 0
                for _sec, _bn in _arr:
                    _base = _sec.rstrip("0123456789")
                    if _base in ("drop", "chorus"):
                        if _sec == _base:            # the FIRST arrival only
                            _s0, _s1 = _acc5 * _BQ, (_acc5 + _bn) * _BQ
                            _win = [n for t in out["tracks"]
                                    if t.get("name", "").lower().startswith("arp")
                                    for n in t["notes"] if _s0 <= n["start"] < _s1]
                            _h16 = any((round((n["start"] % 1.0) * 4) % 4) in (1, 3)
                                       for n in _win)
                            _rest2 = (1, 3) if _h16 else (2,)   # born-8th arps -> quarters
                            for t in out["tracks"]:
                                if not t.get("name", "").lower().startswith("arp"):
                                    continue
                                kept = []
                                for n in t["notes"]:
                                    if _s0 <= n["start"] < _s1:
                                        fr = round((n["start"] % 1.0) * 4) % 4
                                        if fr in _rest2:
                                            continue     # restraint breathes
                                        n = dict(n)
                                        n["vel"] = round(n["vel"] * 0.95, 3)
                                    kept.append(n)
                                t["notes"] = kept
                        break                        # later arrivals stay full
                    _acc5 += _bn
    except Exception:
        pass

    # ---- W23: THE OUTRO SPEAKS — records END, demos fade ----
    # Club forms SUBTRACT: steady energy, then hats leave at the halfway
    # bar, then everything but kick/bass/crash leaves for the last 2 bars —
    # the mixable DJ tail (velocity fade killed above). Song forms get THE
    # TAG: the hook's final phrase restated once by the lead over the
    # outro's first bars (records say the title one more time), riding
    # UNfaded above the ramped band. SOTADAW_OUTRO=0 = legacy fade.
    try:
        if _outro_speaks and plan[-1][0].rstrip("0123456789") == "outro":
            _ob = plan[-1][1]
            _o0, _o1 = (total_bars - _ob) * _BQ, total_bars * _BQ
            if not _has_verse:
                _half = _o0 + (_o1 - _o0) / 2.0
                _last2 = max(_o0, _o1 - 8.0)
                for t in out["tracks"]:
                    if classes.get(t.get("name", "")) != "drums":
                        continue
                    _iskick = "kick" in t.get("name", "").lower()
                    t["notes"] = [
                        n for n in t["notes"]
                        if n["start"] < _half
                        or (n["start"] < _last2
                            and n.get("pitch") not in HAT_PITCHES)
                        or (_iskick and n["start"] >= _last2)]
            else:
                _csp = None
                _acc6 = 0
                for _sec, _bn in plan:            # the LAST chorus span
                    if _sec.rstrip("0123456789") == "chorus":
                        _csp = (_acc6 * _BQ, (_acc6 + _bn) * _BQ)
                    _acc6 += _bn
                lead_tr2 = next((t for t in out["tracks"]
                                 if t.get("name", "").lower() == "lead"
                                 and t.get("notes")), None)
                if _csp and lead_tr2 is not None:
                    _tag_len = min(16.0, _o1 - _o0)
                    _src0 = _csp[1] - _tag_len
                    tag = []
                    for n in lead_tr2["notes"]:
                        if _src0 <= n["start"] < _csp[1]:
                            m = dict(n)
                            m["start"] = round(_o0 + (n["start"] - _src0), 4)
                            if m["start"] + m.get("len", 0.5) > _o1 - 0.5:
                                m["len"] = round(max(0.1, _o1 - 0.5 - m["start"]), 4)
                            m["vel"] = round(n["vel"] * 0.72, 3)
                            try:
                                # the tag comes HOME: undo the chorus's +2
                                # journey shift so it sits on the tonic field
                                m["pitch"] = int(max(24, min(103,
                                    _shift_pitch(m["pitch"], -_SEC_SHIFT["chorus"]))))
                            except Exception:
                                pass
                            if m["start"] < _o1 - 0.5:
                                tag.append(m)
                    lead_tr2["notes"].extend(tag)
    except Exception:
        pass

    for t in out["tracks"]:
        t.get("notes", []).sort(key=lambda n: n["start"])

    # ---- SPACE: one shared reverb return; melodic content sends into it ----
    if not out.get("buses"):
        out["buses"] = [{"id": "space", "gainDb": 0.0,
                         "fx": [{"id": "fx_reverb",
                                 "params": {"size": 1.8, "damp": 5500.0, "mix": 1.0}}]}]
        send_db = {"other": -12.0, "vox": -10.0, "bass": -26.0}
        for t in out["tracks"]:
            cls = classes.get(t.get("name", ""))    # late-born tracks aren't in classes{}
            if cls in send_db and not t.get("sends"):
                t["sends"] = [{"bus": "space", "gainDb": send_db[cls]}]

    bar = 0
    for sec, bars in plan:
        out["sections"].append({"name": sec, "startBar": bar})
        bar += bars
    # the drop arc: filter opens into the first drop (late-bloom curve)
    names = [nm for nm, _ in plan]
    target = "drop" if "drop" in names else ("chorus" if "chorus" in names else None)
    drop_start = (sum(b for nm, b in plan[:names.index(target)]) * _BQ) if target else 0.0
    lead = next((t for t in out["tracks"]                  # .get: riser/crash/counter are
                 if classes.get(t.get("name", "")) == "other"), None)   # born after classes{}
    if lead is not None:
        fx = lead.setdefault("fx", [])
        if not any(f.get("id") == "fx_filter" for f in fx):
            fx.insert(0, {"id": "fx_filter", "params": {"cutoff": 18000, "mode": 0}})
        lead.setdefault("automation", []).append(
            {"target": "fx[0].cutoff",
             "points": [{"beat": max(0.0, drop_start - 16), "v": 500, "curve": 0.6},
                        {"beat": drop_start, "v": 18000}]})

    # ---- W33: THE DELAY THROW — the last phrase echoes into the gap ----
    # The mixer's oldest move: the hook's final bar before every arrival/
    # break rides its delay mix up (0.18 -> 0.45) and snaps back at the
    # boundary — the echo tail carries into the space. Automation only
    # (zero note changes); fires only where the lead actually PLAYS the
    # approach bar; targets the lead's own fx_delay by INDEX SCAN (never
    # positional guessing). SOTADAW_THROW=0 kills.
    try:
        if os.environ.get("SOTADAW_THROW", "1") != "0":
            _tb, _accW = [], 0
            for _sec, _bn in plan:
                if _accW > 0 and _sec.rstrip("0123456789") in ("drop", "chorus",
                                                               "break", "bridge"):
                    _tb.append(_accW * _BQ)
                _accW += _bn
            for t in out["tracks"]:
                if not t.get("name", "").lower().startswith("lead"):
                    continue
                _di = next((i for i, f in enumerate(t.get("fx", []))
                            if isinstance(f, dict) and f.get("id") == "fx_delay"), None)
                if _di is None:
                    continue
                _base = float((t["fx"][_di].get("params") or {}).get("mix", 0.18))
                pts, _prev = [], -1e9
                for b in _tb:
                    _cand = [n for n in t.get("notes", []) if b - 8.0 <= n["start"] < b]
                    if not _cand:
                        continue                     # the lead must PLAY the approach
                    _lastn = max(_cand, key=lambda n: n["start"])
                    _ls = max(_lastn["start"] - 0.3, _prev + 0.05)
                    _le = min(_lastn["start"] + max(0.4, _lastn.get("len", 0.5)) + 0.1,
                              b + 1.0)
                    if _le <= _ls + 0.1:
                        continue
                    # the throw RIDES THROUGH the boundary — snapping back at
                    # the bar kills the echo it threw (mix gates the wet out);
                    # it settles 2 beats into the new section instead
                    pts += [{"beat": round(_ls, 4), "v": _base},
                            {"beat": round(_le, 4), "v": 0.45, "curve": 0.4},
                            {"beat": round(b + 2.0, 4), "v": 0.45},
                            {"beat": round(b + 2.5, 4), "v": _base}]
                    _prev = b + 2.5
                if pts:
                    t.setdefault("automation", []).append(
                        {"target": f"fx[{_di}].mix", "points": pts})
    except Exception:
        pass

    # the BED opens with the song: color pads ride dark through the intro and
    # bloom into the first drop (their birth chain leads with fx_filter)
    if drop_start > 0:
        for t in out["tracks"]:
            nm = t.get("name", "").lower()
            if t is lead or not any(w in nm for w in BED_NAMES):
                continue
            tfx = t.get("fx", [])
            if tfx and tfx[0].get("id") == "fx_filter":
                open_v = float(tfx[0].get("params", {}).get("cutoff", 6500))
                # W91 THE PAD BREATHES: after the bloom, the bed's filter
                # rides a slow triangle (8-bar halves, -18% at the trough) to
                # the end — a static pad over 60 bars is the deadness tell;
                # records' pads always move. Deterministic, engine-verified
                # rail (the bloom proved fx[0].cutoff). SOTADAW_PADBREATH=0.
                _pts91 = [{"beat": 0.0, "v": max(500.0, open_v * 0.14), "curve": 0.5},
                          {"beat": drop_start, "v": open_v}]
                if os.environ.get("SOTADAW_PADBREATH", "1") != "0":
                    _b91, _hi91 = drop_start + 8 * _BQ, True
                    while _b91 < total_bars * _BQ - 2 * _BQ:
                        _pts91.append({"beat": round(_b91, 4),
                                       "v": round(open_v * (0.82 if _hi91 else 1.0), 2)})
                        _hi91 = not _hi91
                        _b91 += 8 * _BQ
                t.setdefault("automation", []).append(
                    {"target": "fx[0].cutoff", "points": _pts91})
    # ---- W81 THE MODULATION: the final chorus LIFTS A WHOLE STEP ----
    # The truck-driver lift — pop/gospel/motown/eurodance records' classic
    # song-scale device our forms never made. Every PITCHED lane (bass and
    # vox included: a key change moves the band) rises +2 semitones from the
    # final arrival THROUGH the end (once a record goes up, it stays up —
    # the outro tag rides the new key). Drums exempt (non-pitched). The
    # ruler reads the "_modulation" field and normalizes before scoring
    # (the W32 share-the-kernel law). SOTADAW_MODULATE=0 kills.
    MODULATE_GENRES = {"pop", "kpop", "jpop", "gospel", "soul", "motown",
                       "doo_wop", "eurobeat", "hi_nrg", "eurodance",
                       "italo_disco", "nightcore"}
    _mod_on = os.environ.get("SOTADAW_MODULATE", "1") != "0"
    if _mod_on and g in MODULATE_GENRES and len(drop_starts) >= 2:
        _mod_from = drop_starts[-1]
        for t in out["tracks"]:
            _nm = t.get("name", "").lower()
            if (classes.get(t.get("name", "")) == "drums"
                    or _nm in ("crash", "riser", "revcrash")):
                continue   # noise one-shots don't ride a key change
            for n in t.get("notes", []):
                if n["start"] >= _mod_from - 1e-6:
                    n["pitch"] = int(n["pitch"]) + 2
        out["_modulation"] = {"fromBeat": round(_mod_from, 4), "semitones": 2}

    # ---- W90 THE FINAL LIFT CHOIR: the last chorus doubles an octave up ----
    # The "everyone sings" device stacked on the W81 lift: the hook's final
    # statement gains an octave-up double on its own lane (lead's voice,
    # center, -4dB, vel x0.85) from the final arrival to the outro. Same
    # family as the modulation (the final-chorus-is-biggest cultures).
    # Copies are made AFTER modulation/void/hole passes so they inherit the
    # lifted key and the carved space exactly. SOTADAW_FINALCHOIR=0 kills.
    if (os.environ.get("SOTADAW_FINALCHOIR", "1") != "0"
            and g in MODULATE_GENRES and len(drop_starts) >= 2):
        _fc_from = drop_starts[-1]
        _fc_end = _fc_from + 32.0
        _leadFC = next((t for t in out["tracks"]
                        if t.get("name") == "lead" and t.get("notes")), None)
        if _leadFC:
            _fc_notes = [{"start": n["start"], "len": n.get("len", 0.5),
                          "pitch": int(n["pitch"]) + 12,
                          "vel": round(n.get("vel", 0.7) * 0.85, 3)}
                         for n in _leadFC["notes"]
                         if _fc_from - 1e-6 <= n["start"] < _fc_end]
            if _fc_notes:
                out["tracks"].append({
                    "name": "lead_oct",
                    "gainDb": round(float(_leadFC.get("gainDb", -9.0)) - 4.0, 2),
                    "pan": 0.0,
                    "source": dict(_leadFC.get("source") or
                                   {"kind": "faust", "id": "pluck2"}),
                    "sends": [dict(x) for x in (_leadFC.get("sends") or [])],
                    "notes": _fc_notes})
                classes["lead_oct"] = "other"

    name = out_name or (os.path.splitext(os.path.basename(song_path))[0] + "_full")
    outp = os.path.join(ROOT, "songs", f"{name}.json")
    json.dump(out, open(outp, "w"), indent=1)
    print(f"[arrange] {outp}: {total_bars} bars, sections " +
          " -> ".join(s for s, _ in plan) + f" (loop {loop_beats:.0f} beats, classes {classes})")
    return outp


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("song")
    ap.add_argument("--out", default=None)
    ap.add_argument("--genre", default=None)
    ap.add_argument("--form", default=None,
                    help="comma list (intro,build,drop,...) or 'pop' = sample a real "
                         "form from the Harmonix label grammar (912 human structures)")
    ap.add_argument("--seed", type=int, default=0, help="pop-form sample seed")
    a = ap.parse_args()
    form = None
    if a.form == "pop":
        names, raw = sample_pop_form(a.seed)
        _s0 = json.load(open(a.song))
        bpm = float(_s0.get("bpm", 120))
        _bq = meter.beats_in_bar(meter.song_meter(_s0), 0)   # seconds -> the song's OWN bars
        dur = json.load(open(GRAMMAR)).get("mean_duration_s", {})
        DEF = {"intro": 15.5, "verse": 24.0, "chorus": 21.1, "build": 14.6,
               "bridge": 23.4, "break": 9.0, "outro": 18.6, "inst": 20.6}
        form = []
        for nm, rw in zip(names, raw):
            sec_s = float(dur.get(rw, DEF.get(rw, 20.0)))
            bars = max(4, min(16, int(round(sec_s * bpm / 60.0 / _bq / 4.0) * 4)))  # grid-ok: same as the in-arrange site — /_bq is the meter, /4*4 is the phrase
            form.append((nm, bars))
        print(f"[arrange] pop form (grammar seed {a.seed}): {' '.join(raw)}")
        print(f"[arrange] mapped: " + " ".join(f"{n}:{b}" for n, b in form))
    elif a.form:
        form = []
        for x in a.form.split(","):
            x = x.strip()
            if not x:
                continue
            nm, _, b = x.partition(":")
            form.append((nm, int(b) if b else (16 if nm == "drop" else 8)))
    arrange(a.song, a.out, form=form, genre=a.genre, seed=a.seed)
