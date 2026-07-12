#!/usr/bin/env python3
"""VOICING — the voice-leading kernel (M1: the 'a musician voiced this' delta).

Every chord emitter in the campaign placed ROOT-POSITION BLOCK TRIADS at a fixed
octave. Real players voice-lead: hold common tones, move the rest by the least
distance, spread by style, keep 3rds out of the mud. ONE kernel, every harmony
tool composes it.

  voice_progression(labels, style, lo, hi)   # chord symbols (A-G[b#][m][7])
  voice_pcs(pcs_seq, style, lo, hi)          # raw pitch-class sets (loop_gen lane)

Styles:
  smooth  minimal-motion inversions (default; pitch-class preserving)
  triad   packed root position (pop/house stabs — the old behavior, kept honest)
  shell   root low + 3rd & 7th voice-led (jazz/neo-soul/gospel; maj->maj7,
          min->b7, dom7->b7 — the idiomatic sevenths)
  drop2   smooth close voicing with the 2nd-from-top dropped an octave (strings/pads)
  open    root + 5th + 10th (wide cinematic)

LAWS: no 3rd below MIDI 43 (~the G2 mud line — raised an octave if the leading
would put it there; roots may go low); deterministic (same input = same output);
distinct pitches only.

Grounding: voice-leading-as-minimal-motion is the formal core of Tymoczko's
geometry-of-music program (chords = points, voice leadings = paths, efficiency =
distance) — docs/SURFACE_LEDGER.md carries the cites.
"""
import itertools, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from reharm import parse_chord

MUD_THIRD = 43          # no 3rds below this (roots/fifths allowed)


def chord_pcs(label):
    """label -> (ordered pcs [root, 3rd, 5th, (7th)], third_pc)."""
    r, q, dom7 = parse_chord(label)
    third = (r + (3 if q == "min" else 4)) % 12
    pcs = [r, third, (r + 7) % 12]
    if dom7:
        pcs.append((r + 10) % 12)
    return pcs, third


def seventh_for(label):
    """The idiomatic 7th: maj->maj7, min->b7, dom7->b7."""
    r, q, dom7 = parse_chord(label)
    return (r + 10) % 12 if (dom7 or q == "min") else (r + 11) % 12


def _realize(pc, lo, hi):
    return [p for p in range(lo, hi + 1) if p % 12 == pc]


def _cost(a, b):
    return sum(abs(x - y) for x, y in zip(sorted(a), sorted(b)))


def _lead(pcs, prev, lo, hi, third_pc=None):
    """Choose octaves for each pc minimizing motion from prev (register law kept)."""
    pools = []
    for pc in pcs:
        floor = max(lo, MUD_THIRD) if pc == third_pc else lo
        pool = _realize(pc, floor, hi) or _realize(pc, lo, hi + 12)
        pools.append(pool)
    best, best_c = None, None
    for combo in itertools.product(*pools):
        if len(set(combo)) != len(combo):
            continue
        c = _cost(combo, prev) if prev else (max(combo) - min(combo)) \
            + abs(sum(combo) / len(combo) - (lo + hi) / 2)
        if best_c is None or c < best_c or (c == best_c and sorted(combo) < sorted(best)):
            best, best_c = combo, c
    return sorted(best)


STYLE_ALIASES = {"rootless_chromatic": "shell", "gospel_block": "smooth",
                 "quartal_open": "open", "quartal_pedal_pentatonic": "open",
                 "modal_vibraphone": "open", "bright_extended": "drop2",
                 "lush_extended": "drop2", "open_arpeggio": "open",
                 "glassy_gospel": "smooth", "streetcorner_stack": "smooth"}

def resolve_style(style):
    """THE STYLE TRUTH (ledger dr08/dr27, 2026-07-12): ~73 curated voicing
    style strings from the genre-expansion waves were DEAD — voice_pcs knew
    five words and silently smoothed everything else, discarding the curation
    intent of a third of the taxonomy. Named aliases map the explicit
    intents; the keyword ladder catches the poetic tail; smooth remains the
    honest default (it IS the voice-led core)."""
    s = str(style or "smooth").lower()
    if s in ("triad", "open", "drop2", "shell", "smooth"):
        return s
    if s in STYLE_ALIASES:
        return STYLE_ALIASES[s]
    for kw, real in (("rootless", "shell"), ("quartal", "open"),
                     ("extended", "drop2"), ("lush", "drop2"),
                     ("block", "smooth"), ("stack", "smooth"),
                     ("powerchord", "triad"), ("chug", "triad"),
                     ("riff", "triad"), ("arpeggio", "open"),
                     ("open", "open")):
        if kw in s:
            return real
    return "smooth"

def voice_pcs(pcs_seq, style="smooth", lo=48, hi=76, thirds=None, roots=None):
    """Raw lane: pcs_seq = list of pc-lists (per chord). thirds/roots parallel lists
    of the third/root pc per chord (register law + shell need them; None = best effort)."""
    style = resolve_style(style)
    out, prev = [], None
    for i, pcs in enumerate(pcs_seq):
        third = thirds[i] if thirds else None
        root = roots[i] if roots else pcs[0]
        if style == "triad":
            v = _lead(pcs, None, lo, hi, third)
        elif style == "open":
            r = _realize(root, lo, min(lo + 12, hi))[0]
            fifth = (root + 7) % 12
            tenth = third if third is not None else pcs[1 % len(pcs)]
            # narrow lo..hi windows can starve the (r+1, hi) span — fall back an
            # octave up, same idiom as _lead's pool fallback (found live: a raised
            # register floor pushed r within 3 semitones of hi -> IndexError)
            v = sorted({r, (_realize(fifth, r + 1, hi) or _realize(fifth, r + 1, hi + 12))[0],
                        (_realize(tenth, r + 13, hi + 12) or _realize(tenth, r + 13, hi + 24))[0]})
            # THE EXTENSION KEEP (dr08): pcs beyond root/third/fifth — the 7th/
            # 9th the genre asked for — were silently DISCARDED here. Realize
            # them into the upper span: an open-voiced 9th stays a 9th.
            _core = {root % 12, fifth % 12, tenth % 12}
            for _ext in pcs:
                if _ext % 12 not in _core:
                    _e = _realize(_ext, r + 13, hi + 12) or _realize(_ext, r + 13, hi + 24)
                    if _e and _e[0] not in v:
                        v = sorted(v + [_e[0]])
        elif style == "drop2":
            close = _lead(pcs if len(pcs) >= 4 else pcs + [root], prev, lo, hi, third)
            dropped = close[-2] - 12
            rest = close[:-2] + [close[-1]]
            while dropped in rest and dropped >= lo - 12:   # collision -> keep dropping
                dropped -= 12
            v = sorted(rest + [dropped]) if dropped >= lo - 12 else close
        else:                                   # smooth / shell share the leading core
            v = _lead(pcs, prev, lo, hi, third)
        out.append(v)
        prev = v
    return out


def voice_progression(labels, style="smooth", lo=48, hi=76):
    style = resolve_style(style)
    seqs, thirds, roots = [], [], []
    for lb in labels:
        pcs, third = chord_pcs(lb)
        r = pcs[0]
        if style == "shell":
            pcs = [r, third, seventh_for(lb)]
        thirds.append(third); roots.append(r); seqs.append(pcs)
    if style == "shell":
        # root planted low, upper pair voice-led above it
        out, prev = [], None
        for pcs, third in zip(seqs, thirds):
            r = _realize(pcs[0], max(28, lo - 12), lo + 11)[0]
            upper = _lead(pcs[1:], prev, lo, hi, third)
            out.append(sorted([r] + upper))
            prev = upper
        return out
    return voice_pcs(seqs, style, lo, hi, thirds, roots)


def motion(voicings):
    """Total voice movement across the progression (the battery's ruler)."""
    return sum(_cost(voicings[i], voicings[i + 1]) for i in range(len(voicings) - 1))


if __name__ == "__main__":
    labels = sys.argv[1:] or ["C", "Am", "F", "G7"]
    for st in ("triad", "smooth", "shell", "drop2", "open"):
        vs = voice_progression(labels, st)
        print(f"{st:>6}: motion {motion(vs):>3}  " +
              "  ".join("[" + ",".join(str(p) for p in v) + "]" for v in vs))
