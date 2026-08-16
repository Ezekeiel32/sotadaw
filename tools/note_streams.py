#!/usr/bin/env python3
"""THE STREAM SPLIT — one polyphonic transcription -> musical voice lanes.

The 'other' stem is a BUCKET (usually more than one lead plus pads/chords —
Chezy's words, 2026-07-15), and a single note-wall lane is uneditable as
music even when every note is right. This kernel partitions a transcribed
note list into the streams a musician would name:

    chords  co-onset blocks (>=3 notes attacking together)
    pad     sustained notes (>= PAD_LEN beats) outside those blocks
    lead    the fast melodic surface (everything else — runs, arps, lines)

HONESTY GATES: a stream only becomes a lane when the split is DECISIVE
(>= MIN_NOTES notes and >= MIN_SHARE of the lane's mass); indecisive
streams fold back into the dominant one, and a lane that doesn't split
stays exactly one lane. The output is a PARTITION — every input note lands
in exactly one stream, none invented, none lost (the selftest asserts it).

Pure + deterministic (no I/O, no randomness): battery-safe.
"""
import sys

CHORD_TOL = 0.09          # beats: attacks within this cluster as one block
PAD_LEN = 1.5             # beats: a note this long is texture, not a run
MIN_NOTES = 24            # a lane needs this many notes to exist
MIN_SHARE = 0.12          # ...and this share of the source lane's mass


def split_streams(notes, min_notes=MIN_NOTES, min_share=MIN_SHARE):
    """Partition notes -> [(stream, notes), ...] in chords/pad/lead order.
    Single-stream inputs return [("all", notes)] (the caller keeps one lane)."""
    if not notes:
        return []
    order = sorted(range(len(notes)),
                   key=lambda i: (notes[i].get("start", 0.0),
                                  notes[i].get("pitch", 0)))
    # 1) co-onset clusters
    clusters, cur, cur_t = [], [], None
    for i in order:
        t = float(notes[i].get("start", 0.0))
        if cur and t - cur_t > CHORD_TOL:
            clusters.append(cur)
            cur = []
        if not cur:
            cur_t = t
        cur.append(i)
    if cur:
        clusters.append(cur)

    chords, rest = [], []
    for cl in clusters:
        (chords if len(cl) >= 3 else rest).extend(cl)
    # 2) sustained texture vs the fast surface
    pad = [i for i in rest if float(notes[i].get("len", 0.0)) >= PAD_LEN]
    lead = [i for i in rest if float(notes[i].get("len", 0.0)) < PAD_LEN]

    streams = [("chords", chords), ("pad", pad), ("lead", lead)]
    total = len(notes)
    keep = [(nm, ix) for nm, ix in streams
            if len(ix) >= min_notes and len(ix) / total >= min_share]
    if len(keep) <= 1:
        return [("all", [notes[i] for i in order])]
    # fold indecisive remainders into the dominant kept stream
    kept_ix = {i for _, ix in keep for i in ix}
    orphans = [i for i in order if i not in kept_ix]
    if orphans:
        dom = max(keep, key=lambda p: len(p[1]))
        dom[1].extend(orphans)
    out = []
    for nm, ix in keep:
        ix_sorted = sorted(ix, key=lambda i: (notes[i].get("start", 0.0),
                                              notes[i].get("pitch", 0)))
        out.append((nm, [notes[i] for i in ix_sorted]))
    return out


def _selftest():
    ok = True

    def check(name, cond):
        nonlocal ok
        print(("  ok  " if cond else "FAIL  ") + name)
        ok = ok and cond

    # synthetic lane: 40 chord blocks + 60 pads + 200 run notes
    notes = []
    for b in range(40):                       # chords on every 4th beat
        for p in (48, 52, 55):
            notes.append({"start": b * 4.0, "len": 1.0, "pitch": p, "vel": 0.8})
    for b in range(60):                       # sustained pad line
        notes.append({"start": b * 2.0 + 1.0, "len": 2.0, "pitch": 67,
                      "vel": 0.5})
    for k in range(200):                      # fast arp surface
        notes.append({"start": k * 0.5 + 0.25, "len": 0.25,
                      "pitch": 60 + (k % 5), "vel": 0.9})
    got = dict(split_streams(notes))
    check("three decisive streams emit",
          set(got) == {"chords", "pad", "lead"})
    check("partition conserves mass (none lost, none invented)",
          sum(len(v) for v in got.values()) == len(notes))
    check("chords hold the co-onset blocks",
          len(got.get("chords", [])) == 120)
    check("pads are the sustains", len(got.get("pad", [])) == 60)
    check("lead is the fast surface", len(got.get("lead", [])) == 200)

    # indecisive: a plain monophonic line stays ONE lane
    mono = [{"start": i * 0.5, "len": 0.4, "pitch": 60 + i % 7, "vel": 0.8}
            for i in range(100)]
    got2 = split_streams(mono)
    check("monophonic line stays single", [nm for nm, _ in got2] == ["all"])
    check("single keeps every note", len(got2[0][1]) == len(mono))

    check("empty input -> no streams", split_streams([]) == [])

    # determinism
    a = split_streams(notes)
    b = split_streams(list(notes))
    check("deterministic", a == b)

    # orphan folding: chords + lead decisive, 3 pads fold into dominant
    small = ([{"start": b * 4.0, "len": 1.0, "pitch": p, "vel": 0.8}
              for b in range(30) for p in (48, 52, 55)]
             + [{"start": i * 0.5, "len": 0.25, "pitch": 62, "vel": 0.9}
                for i in range(90)]
             + [{"start": 200.0 + i, "len": 3.0, "pitch": 70, "vel": 0.4}
                for i in range(3)])
    got3 = dict(split_streams(small))
    check("indecisive pads fold (no 3-note lane)",
          "pad" not in got3
          and sum(len(v) for v in got3.values()) == len(small))
    print("SELFTEST " + ("GREEN" if ok else "RED"))
    return 0 if ok else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print(__doc__)
