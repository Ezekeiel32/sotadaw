#!/usr/bin/env python3
"""COURTS LINT — machine law (wall_lint's sibling, PRODUCER MIND P21).

The MUSIC COURTS must stand at the ONE render seam: render_and_analyze in
agent/sidecar.py runs music_court.run_courts (heal=True) on proposals BEFORE
_cached_render, guarded to proposal takes only. An unmounted seam turns the
suite red — prose laws are wishes; this is the wall.

Also asserts music_court invariants: witness law present, heal ledgers
returned, conservative ok-thresholds intact.
"""
import ast
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def fail(msg):
    print(f"courts_lint: RED — {msg}")
    sys.exit(1)


def main():
    side = os.path.join(ROOT, "agent", "sidecar.py")
    src = open(side).read()
    tree = ast.parse(src)
    fn = next((n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
               and n.name == "render_and_analyze"), None)
    if fn is None:
        fail("render_and_analyze missing from sidecar.py")
    body_src = ast.get_source_segment(src, fn) or ""
    if "run_courts" not in body_src:
        fail("render_and_analyze does not run the music courts")
    if body_src.index("run_courts") > body_src.index("_cached_render"):
        fail("courts must run BEFORE the render (heals must land in the wav)")
    if "_prop_" not in body_src or "proposal" not in body_src:
        fail("courts must be guarded to PROPOSAL takes (base songs are sacred)")
    if "heal=True" not in body_src:
        fail("courts mount must heal, not just nag")

    mc = open(os.path.join(ROOT, "tools", "music_court.py")).read()
    for must, why in (
        ("_WITNESS_SUFFIX", "witness law (imported sketches are not defendants)"),
        ("def heal_key", "key heal"),
        ("def heal_pocket", "pocket heal"),
        ("def court_instruction", "instruction court"),
        ("swing_pos", "engine-swing mirror (lawful swing is not a straggler)"),
        ("import meter", "THE WORLD GRID resolver (grid_lint law)"),
        ("import melody_court", "melodic mind mount (R-2 wave 12)"),
    ):
        if must not in mc:
            fail(f"music_court.py lost {why}")

    mel = open(os.path.join(ROOT, "tools", "melody_court.py")).read()
    for must, why in (
        ("_EXEMPT", "texture-genre stand-down (ambient is not a melody crime)"),
        ("def heal_melody", "melody heal (octave folds)"),
        ("key_term=False", "outlier path must not judge pitch-class "
                           "(that is the KEY court's law)"),
        ("def clamp_tessitura", "R-2 tessitura clamp for the sing lane"),
    ):
        if must not in mel:
            fail(f"melody_court.py lost {why}")

    if "import harmony_court" not in mc:
        fail("music_court.py lost the harmony mind mount (wave 13)")
    if "import groove_court" not in mc:
        fail("music_court.py lost the groove engine mount (wave 14)")
    gc = open(os.path.join(ROOT, "tools", "groove_court.py")).read()
    for must, why in (
        ("THE WITNESS LAW", "imported drum pieces are evidence, not defendants"),
        ("def heal_swing", "swing heal (kick+bass anchored)"),
        ("HALFTIME RESOLVER", "felt-vs-notated tempo double-count law"),
        ("machine", "machine-aesthetic flat-velocity pardon"),
        ("cruzao", "crossed-clave law"),
    ):
        if must not in gc:
            fail(f"groove_court.py lost {why}")
    if "import lowend_court" not in mc:
        fail("music_court.py lost the low-end court mount (wave 15)")
    lo = open(os.path.join(ROOT, "tools", "lowend_court.py")).read()
    for must, why in (
        ("def heal_interlock", "kick-bass pileup heal (tempo-locked fx_pump)"),
        ("def sidechain_release_ms", "R-5 tempo-locked release kernel "
                                     "(never an LLM guess)"),
        ("shadow_808", "808-as-kick-tail must stay ADVISORY (real style)"),
        ("CORPUS-CALIBRATED", "R-16 self-measure law on ENV_808 windows "
                              "(Chezy 450ms + eval 1800ms drill truth)"),
        ("def heal_sub_width", "panned/widened sub heal (mono-center law)"),
        ("def court_freq_division", "psy frequency-division court "
                                    "(097: never tune the kick — carve)"),
        ("kick_carve", "the fx_bell carve heal at the bass root"),
    ):
        if must not in lo:
            fail(f"lowend_court.py lost {why}")
    side_all = src
    if "_lowend_ears_pass" not in side_all:
        fail("sidecar lost the LOW-END EARS mount (wave 16)")
    fn2 = next((n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                and n.name == "loudness_recovery"), None)
    if fn2 is None or "_lowend_ears_pass" not in (
            ast.get_source_segment(src, fn2) or ""):
        fail("loudness_recovery no longer rides the low-end ears "
             "(every-lane law: the ears live at recovery's entry)")
    le = open(os.path.join(ROOT, "tools", "lowend_ears.py")).read()
    for must, why in (
        ("_TEXTURE_EXEMPT", "texture-genre stand-down (eval_ambient winner "
                            "had a wide sub BY DESIGN)"),
        ("_is_imported", "witness law (imported records' subs are evidence)"),
        ("def heal_sub_mono", "sub-mono heal (fx_ms_eq pre-wall)"),
        ('"translation", "ok": True', "translation must stay ADVISORY "
         "(goldenbrown corpus law: a real record measures 0.0032)"),
        ("x.mean(axis=1)", "sine FFT must see the FULL band (the LP was "
                           "eating its own evidence)"),
        ("def court_sub_key", "the render-truth sub court (wave 31)"),
        ("AT ITS NOTATED", "the note is the contract — demo_track law: "
                           "a band-global f0 convicted the kick's tail"),
        ("mad < 60", "systematic detune only, never vibrato"),
        ("def court_kick_tuning", "tonal-kick tuning court (wave 32)"),
        ("THE SUSTAIN GATE", "percussive kicks exempt BY PHYSICS "
                             "(decay-vs-attack, never level-vs-noise)"),
        ("THE SCALE-TONE LAW", "diatonic set targets — root/fifth "
                               "convicted 18/90 incl. six winners "
                               "(relative-key ambiguity + legit degrees)"),
    ):
        if must not in le:
            fail(f"lowend_ears.py lost {why}")
    if "import lyric_court" not in mc:
        fail("music_court.py lost the lyric courts mount (wave 17)")
    if "lyric_court" not in src:
        fail("sidecar lost the PRE-SING lyric heal seam (wave 17: bank "
             "words must heal BEFORE the voice sings them)")
    lyc = open(os.path.join(ROOT, "tools", "lyric_court.py")).read()
    for must, why in (
        ("def bank_authored", "THE AUTHORSHIP GUARD (heals rewrite bank "
                              "words only, never a human's lyric)"),
        ("witness law", "imported records' lyrics are evidence"),
        ("LINE MODE", "multi-word entries judged as phrases "
                      "(untitled_38 corpus law)"),
        ("PROSODY_HARD_USER", "two-tier prosody floors (untitled_43's "
                              "real vocals must never convict)"),
        ('"vowel_long", "ok": True', "vowel court must stay ADVISORY "
                                     "(meaning outranks physics)"),
        ("def court_melisma", "melisma policy court (wave 23)"),
        ("def intelligibility_risk", "pre-render intelligibility "
                                     "composite (item 126)"),
    ):
        if must not in lyc:
            fail(f"lyric_court.py lost {why}")
    if "import tension" not in mc:
        fail("music_court.py lost the tension arc mount (wave 18)")
    tn = open(os.path.join(ROOT, "tools", "tension.py")).read()
    for must, why in (
        ("EARLY_EDGE = 0.25", "corpus-calibrated early-climax edge "
                              "(chezy_song_full at 0.315 must never graze)"),
        ("no narrative contract", "loop/sketch stand-down (70/243 of the "
                                  "corpus is loops — form is the contract)"),
        ("witness law", "imported records' arcs are evidence"),
        ("c >= cmax * 0.95", "the payoff is the LAST near-max beat "
                             "(double-drop law, eval_house)"),
        ("def heal_drop", "pre-drop dip heal (cut the build, never boost)"),
        ("never convict on a correlation", "shape match stays advisory "
                                           "(r~0.62-0.68 honest ceiling)"),
    ):
        if must not in tn:
            fail(f"tension.py lost {why}")
    if "import semantic_map" not in mc:
        fail("court_instruction lost the semantic tier (wave 19)")
    smp = open(os.path.join(ROOT, "tools", "semantic_map.py")).read()
    for must, why in (
        ("LOW_AGREEMENT", "the agreement gate (LOW words = ask-back, "
                          "never a wrong render)"),
        ("effect_context", "(term x effect-context x scope) binding — "
                           "the meta-study law"),
        ("CORR_MONO_GUARD", "wide verdicts must guard mono compatibility"),
        ("length|song|track", "'full' length-vs-tone disambiguation "
                              "(telemetry wolf 2026-07-15)"),
        ("never convict blind", "unmeasured correlates stay advisory"),
        ("opposite of loud", "punchy = crest kernel, hard-separated "
                             "from the loudness pass"),
    ):
        if must not in smp:
            fail(f"semantic_map.py lost {why}")
    snd = open(os.path.join(ROOT, "tools", "sound_court.py")).read()
    for must, why in (
        ("never per-proposal", "the stems court is the ON-DEMAND lane "
                               "(stems renders are expensive)"),
        ("CORPUS-CALIBRATED", "kick attack band holds the project's own "
                              "kick_808 (76ms boom, self-measure law)"),
        ("proof the zone", "attack heal only touches EXISTING params "
                           "(no blind param invention)"),
        ("BANDS, NOT POINTS", "the r-16 adversarial law"),
    ):
        if must not in snd:
            fail(f"sound_court.py lost {why}")
    if "import masking_court" not in mc:
        fail("music_court.py lost the compose-masking mount (wave 21)")
    msk = open(os.path.join(ROOT, "tools", "masking_court.py")).read()
    for must, why in (
        ("SELF-MASKING WITNESS LAW", "the target's own leakage skirts "
                                     "cannot testify against it"),
        ("THE CORPUS REWROTE", "pair-layering is orchestration (11/21 "
                               "eval winners law); only 4+ mud-zone "
                               "crowding advises"),
        ("SOURCE-FIRST, EQ-LAST", "the bounded heal ladder order"),
        ("EQ_MAX_DB, EQ_MAX_BELLS = 6.0, 3", "over-unmask caps"),
        ("never per-proposal", "the stems MSR court is the on-demand lane"),
    ):
        if must not in msk:
            fail(f"masking_court.py lost {why}")
    if "translation_court" not in side_all:
        fail("sidecar lost the TRANSLATION COURTS mount (wave 22)")
    trc = open(os.path.join(ROOT, "tools", "translation_court.py")).read()
    for must, why in (
        ("THE CORPUS OUTRANKS THE LITERATURE", "tilt/band edges are "
                                               "corpus-anchored, never "
                                               "the blog -4.5+-1"),
        ("CORR_FLOOR, CORR_NEG = 0.5, -0.2", "eval_vaporwave's -0.05 is "
                                             "a WINNER — only sustained "
                                             "negative convicts"),
        ("ONE-RESOLVER", "sub-band mono law stays lowend_ears'"),
        ("Centroid is RETIRED", "master brightness = roll-off (item 232)"),
    ):
        if must not in trc:
            fail(f"translation_court.py lost {why}")
    vcp = open(os.path.join(ROOT, "tools", "vocal_court.py")).read()
    for must, why in (
        ("def calibrate_floors", "accept-calibration kernel (item 012: "
                                 "literature seeds, accepts refine)"),
        ("red itself never moves", "the literature red line is the "
                                   "hard law"),
        ("def content_recall", "amber-zone meaning rescue"),
        ("def _soundex", "phonetic tier (threw IS through)"),
    ):
        if must not in vcp:
            fail(f"vocal_court.py lost {why}")
    har = open(os.path.join(ROOT, "tools", "harmony_court.py")).read()
    for must, why in (
        ("_LIL_DARK", "dark-electronic LIL idiom pardon (eval winners law)"),
        ("def heal_lil", "LIL mud heal"),
        ("def heal_chord_tones", "avoid-note resolution heal"),
        ("same_lane", "cross-lane LIL pairs must stay advisory "
                      "(mixing domain, not composition)"),
        ("def suggest_next", "canon progression suggestions"),
    ):
        if must not in har:
            fail(f"harmony_court.py lost {why}")
    print("courts_lint: GREEN — the music courts stand at the render seam")


if __name__ == "__main__":
    main()
