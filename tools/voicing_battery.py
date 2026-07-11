#!/usr/bin/env python3
"""VOICING battery — the kernel voices like a player, provably.

  V1 pitch-class truth: smooth voicings carry exactly the chord's pcs
  V2 minimal motion: smooth beats packed root-position blocks on classic
     progressions (I-vi-IV-V both modes), and by a real margin (<=60%)
  V3 common tones HELD: C->Am keeps two shared pitches in place
  V4 register law: no 3rd below MIDI 43 even when the register is forced low;
     shell roots MAY go below (roots are exempt)
  V5 determinism: same input -> identical output, twice
  V6 style geometry: shell = low root + 3rd&7th pair; drop2 spans wider than
     smooth and has NO duplicate pitches (the collision bug, locked); open >= 15
     semitone span
  V7 every style yields distinct pitches, all inside sane MIDI (21..108)
Exit 1 on any failure. Pure symbolic."""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from voicing import voice_progression, motion, chord_pcs, seventh_for

PASS, FAIL = [], []
def check(n, c, d=""):
    (PASS if c else FAIL).append(n)
    print(f"  [{'PASS' if c else 'FAIL'}] {n}" + (f" — {d}" if d else ""))


def pcs_of(v):
    return {p % 12 for p in v}


def main():
    prog = ["C", "Am", "F", "G7"]
    sm = voice_progression(prog, "smooth")
    tr = voice_progression(prog, "triad")

    check("V1 smooth voicings carry exactly the chord pcs",
          all(pcs_of(v) == set(chord_pcs(lb)[0]) for v, lb in zip(sm, prog)))

    m_sm, m_tr = motion(sm), motion(tr)
    prog2 = ["Cm", "Ab", "Eb", "Bb"]
    m_sm2, m_tr2 = motion(voice_progression(prog2, "smooth")), motion(voice_progression(prog2, "triad"))
    check("V2 smooth motion <= 60% of block motion (both modes)",
          m_sm <= 0.6 * m_tr and m_sm2 <= 0.6 * m_tr2,
          f"maj {m_sm} vs {m_tr}; min {m_sm2} vs {m_tr2}")

    held = set(sm[0]) & set(sm[1])
    check("V3 C->Am holds >= 2 common tones in place", len(held) >= 2, str(sorted(held)))

    low = voice_progression(prog, "smooth", lo=36, hi=60)
    ok_third = all(p >= 43 for v, lb in zip(low, prog) for p in v
                   if p % 12 == chord_pcs(lb)[1])
    check("V4 register law: no 3rd below 43 in a forced-low register", ok_third,
          str(low))
    sh = voice_progression(prog, "shell")
    check("V4b shell roots may sit low (root exemption real)",
          any(v[0] < 43 for v in sh), str([v[0] for v in sh]))

    check("V5 deterministic", voice_progression(prog2, "smooth") == voice_progression(prog2, "smooth")
          and voice_progression(prog, "drop2") == voice_progression(prog, "drop2"))

    ok_shell = all(pcs_of(v) == {chord_pcs(lb)[0][0], chord_pcs(lb)[1], seventh_for(lb)}
                   for v, lb in zip(sh, prog))
    check("V6 shell = root + 3rd + idiomatic 7th exactly", ok_shell,
          str(sh))
    d2 = voice_progression(prog, "drop2")
    span = lambda vs: sum(max(v) - min(v) for v in vs) / len(vs)
    check("V6b drop2 spans wider than smooth, no duplicate pitches",
          span(d2) > span(sm) and all(len(set(v)) == len(v) for v in d2),
          f"span {span(d2):.1f} vs {span(sm):.1f}")
    op = voice_progression(prog, "open")
    check("V6c open >= 15 semitone span each", all(max(v) - min(v) >= 15 for v in op))

    all_v = [v for st in ("triad", "smooth", "shell", "drop2", "open")
             for v in voice_progression(prog2, st)]
    check("V7 all styles: distinct pitches, sane MIDI",
          all(len(set(v)) == len(v) and all(21 <= p <= 108 for p in v) for v in all_v))

    print(f"\n== VOICING: {len(PASS)} pass / {len(FAIL)} fail ==")
    if FAIL:
        print("FAILURES:", ", ".join(FAIL)); sys.exit(1)
    print("THE KERNEL VOICES LIKE A PLAYER (minimal motion, laws held)")


if __name__ == "__main__":
    main()
