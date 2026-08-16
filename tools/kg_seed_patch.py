#!/usr/bin/env python3
"""KG SEED — PATCH DNA (wave 54; R-17 item 021, transformative).

Per-archetype numeric recipes as PatchArchetype nodes, linked
Genre-[:HAS_PATCH]->PatchArchetype — patch design becomes a KERNEL
LOOKUP, not an LLM vibe. Every number cited (r-17: Szabo thesis
JP-8000 measurements, DX7 patch sheets, Roland chorus captures).
Idempotent; --verify = query-back proofs. tools/patch_dna.py is the
live accessor (SUBGENRE_OF inheritance).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kg  # noqa: E402

PROV = "r-17 patch DNA seed w54 (2026-07-16)"

PATCHES = {
    "p808": dict(
        family="808", voice="kick_808 / sub_clean", waveform="sine",
        fundamental_hz="40-60 (tune to song key)",
        pitch_env="+12st in-key octave (+24 punchier), decay 20-80ms "
                  "(40-60 typical), EXPONENTIAL, sustain 0",
        amp_env="attack 0-5ms, decay 550-650ms, sustain 0, release ~400ms",
        extra="optional FM modulator +2-3 oct (300-800Hz) = metallic edge; "
              "saturation stage restores small-speaker audibility"),
    "drill_808": dict(
        family="808", voice="sub_808_slide", waveform="sine", inherits="p808",
        glide="mono legato + portamento 20-60 (lower=faster); slides "
              "between OVERLAPPING notes (song.json note overlap = the "
              "symbolic toggle)"),
    "reese": dict(
        family="bass", voice="reese", waveform="2 saws same octave",
        detune_cents="5-10 subtle / 15-25 standard / 30-50 neurofunk",
        filter_motion="LPF swept 200Hz->2000Hz by LFO synced 1/8 or 1/16 "
                      "(MOTION IS THE PATCH — movement court enforces)",
        beat_rate="f_beat = f0*(2^(cents/1200)-1) (the null-proof number)"),
    "supersaw": dict(
        family="lead", voice="supersaw_jp", waveform="7 saws (JP-8000 exact)",
        detune_offsets="-0.11002313,-0.06288439,-0.01952356,0,"
                       "+0.01991221,+0.06216538,+0.10745242 "
                       "(f_i = f0*(1+offset_i*curve))",
        detune_curve="Szabo 11th-order polynomial knob->spread: "
                     "10028.7312891634x^11-50818.8652045924x^10"
                     "+111363.4808729368x^9-138150.6761080548x^8"
                     "+106649.6679158292x^7-53046.9642751875x^6"
                     "+17019.9518580080x^5-3425.0836591318x^4"
                     "+404.2703938388x^3-24.1878824391x^2"
                     "+0.6717417634x+0.0030115596",
        mix_gains="center = -0.55366x+0.99785; each of 6 sides = "
                  "-0.73764x^2+1.2841x+0.044372",
        filter="HPF TRACKING f0 (kills sub-fundamental alias/mud)",
        phase="free-running, randomized per note trigger",
        modern="7 voices; detune ~7% subtle / 20% default / >50% dissonant; "
               "wide stereo spread"),
    "goa_bass": dict(
        family="bass", waveform="saw or square, single osc",
        filter_env="A0 S0 R0, decay 30-60ms (the '60ms magic', up to "
                   "~100ms for pluck), resonance ~0, env->LPF cutoff",
        groove="KBBB per beat (kick + 3 offbeat 16th bass notes)",
        sidechain="instant attack, release 100-140ms @140bpm"),
    "hoover": dict(
        family="lead", waveform="PWM saw; 3 osc octave-spaced OR 4 unison "
                                "heavily detuned; fast LFO on pulse width",
        pitch_env="downward drop of 7st (fifth) or 12st (octave), fast "
                  "decay, no sustain",
        chorus="Roland-style: delay 16ms, rate 0.22Hz, depth 50%, "
               "feedback 12%, width 50%, dry/wet 60%"),
    "fm_epiano": dict(
        family="keys", voice="fm2op (body ratio 1 idx 1.5 dec .6 + tine ratio 14 idx 5 dec .03)", waveform="FM (DX7 E.PIANO 1)",
        algorithm="5, feedback 6",
        ratios="body pair 1:1; bell/tine pair ~14:1 with fast-decay "
               "modulator env (mod index = the attack transient)",
        ratio_rule="integer C:M = harmonic/musical; non-integer (3.5:1) "
                   "= inharmonic metallic/bell"),
    "organ_bass": dict(
        family="bass", waveform="additive sine stack",
        drawbars="0.5x,1x,1.5x,2x,3x,4x,5x,6x,8x of f0; bass emphasizes "
                 "0.5x+1x (16'/8') + the fifth",
        voicing="root + fifth(+7st) + octave(+12st)"),
    "pluck": dict(
        family="lead", waveform="saw/square",
        amp_env="attack 0-5ms, decay 200-500ms, sustain 0",
        filter_env="attack 4-5ms, decay 300-350ms, sustain 0, env->cutoff",
        extra="+1/8-synced delay is part of the sound"),
    "pad": dict(
        family="pad", waveform="detuned layers +-5-10 cents (chorusing)",
        amp_env="attack 0.5-3s+, long release",
        lfo="~0.1Hz free-running on cutoff; 2+ LFOs at DIFFERENT slow "
            "rates, retrigger OFF; depth few % (fast) to 50%+ (slow)"),
    "analog_character": dict(
        family="universal",
        recipe="per-note random init phase; slow Gaussian pitch drift of "
               "a few cents (most near center); per-voice variance / "
               "round-robin — the un-digital layer every voice wants"),
}

LINKS = [
    ("trap", "p808"), ("memphis_rap", "p808"), ("memphis_phonk", "p808"),
    ("rage", "p808"), ("crunk", "p808"),
    ("uk_drill", "drill_808"), ("ny_drill", "drill_808"),
    ("chicago_drill", "p808"),          # STATIC 808 — never the glide
    ("dnb", "reese"), ("neurofunk", "reese"), ("halftime", "reese"),
    ("trance", "supersaw"), ("uplifting_trance", "supersaw"),
    ("hardstyle", "hoover"), ("rave", "hoover"), ("hardcore", "hoover"),
    ("psytrance", "goa_bass"), ("goa", "goa_bass"), ("fullon", "goa_bass"),
    ("darkpsy", "goa_bass"), ("forest", "goa_bass"),
    ("deep_house", "organ_bass"), ("organ_house", "organ_bass"),
    ("house", "pluck"), ("edm", "pluck"),
    ("ambient", "pad"), ("psybient", "pad"),
]


def seed(g):
    have = {r[0] for r in g.q("MATCH (x:Genre) RETURN x.name")}
    n_nodes = n_links = 0
    for name, attrs in PATCHES.items():
        g.upsert("PatchArchetype", name, PROV, **attrs)
        n_nodes += 1
    for genre, patch in LINKS:
        if genre not in have:
            continue
        g.link("Genre", genre, "HAS_PATCH", "PatchArchetype", patch,
               provenance=PROV)
        n_links += 1
    return n_nodes, n_links


def verify(g):
    fails = []

    def check(name, cond):
        print(f"[{'PASS' if cond else 'FAIL'}] {name}")
        if not cond:
            fails.append(name)

    row = g.q("MATCH (p:PatchArchetype {name:'supersaw'}) "
              "RETURN p.detune_offsets, p.mix_gains")
    check("supersaw carries the exact Szabo offsets + mix gains",
          row and "-0.11002313" in str(row[0][0])
          and "0.99785" in str(row[0][1]))
    row = g.q("MATCH (g:Genre {name:'uk_drill'})-[:HAS_PATCH]->(p) "
              "RETURN p.name")
    check("uk_drill -> drill_808 (the glide)",
          row and row[0][0] == "drill_808")
    row = g.q("MATCH (g:Genre {name:'chicago_drill'})-[:HAS_PATCH]->(p) "
              "RETURN p.name")
    check("chicago_drill -> STATIC p808 (never the glide)",
          row and row[0][0] == "p808")
    row = g.q("MATCH (p:PatchArchetype {name:'hoover'}) RETURN p.chorus")
    check("hoover chorus numbers (16ms/0.22Hz/50%) banked",
          row and "0.22Hz" in str(row[0][0]))
    row = g.q("MATCH (p:PatchArchetype {name:'reese'}) RETURN p.beat_rate")
    check("reese null-proof beat-rate formula banked",
          row and "2^(cents/1200)" in str(row[0][0]))
    row = g.q("MATCH (p:PatchArchetype) RETURN count(p)")
    check("11 archetypes stand", row and row[0][0] >= 11)
    # the accessor + inheritance
    import patch_dna as PD
    p = PD.patch_for("ny_drill")
    check("accessor: ny_drill resolves drill_808 directly",
          p and p.get("name") == "drill_808")
    p = PD.patch_for("sexy_drill")       # no direct link -> parent chain
    check("accessor: sexy_drill INHERITS the patch via SUBGENRE_OF",
          p and p.get("name") == "drill_808" and p.get("inherited_from"))
    check("accessor: unknown genre = None (no fake DNA)",
          PD.patch_for("zzz_nonexistent") is None)
    return fails


def main():
    g = kg.KG()
    n, l = seed(g)
    print(f"[kg_patch] {n} archetypes, {l} genre links")
    if "--verify" in sys.argv:
        n2, _ = seed(g)
        fails = verify(g)
        if fails:
            print(f"kg_patch: {len(fails)} RED — {fails}")
            return 1
        print("kg_patch: ALL GREEN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
