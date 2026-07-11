#!/usr/bin/env python3
"""THE UNDROPPABLE LAW battery — parseSong/songToVar round-trip (m1 resave).

A UI save must never destroy what another layer wrote: chords[] (9 python
writers), lyrics (write_lyrics), and ANY future top-level annotation must
survive load -> serialize verbatim; modeled fields stay exact; no duplicate
keys; the operation is idempotent. SKIP-green when m1 isn't built (fresh box).
"""
import json, os, subprocess, sys, tempfile, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")

N = 0


def ok(cond, msg):
    global N
    N += 1
    if not cond:
        print(f"FAIL {N} — {msg}")
        sys.exit(1)
    print(f"ok {N} — {msg}")


if not os.path.exists(M1):
    print("SKIP undroppable battery — m1 not built")
    sys.exit(0)

tmp = tempfile.mkdtemp(prefix="undrop_")


def resave(src_obj, tag):
    src = os.path.join(tmp, f"{tag}_in.json")
    dst = os.path.join(tmp, f"{tag}_out.json")
    json.dump(src_obj, open(src, "w"), indent=1)
    r = subprocess.run([M1, "resave", src, dst], capture_output=True, text=True)
    assert r.returncode == 0, f"resave rc={r.returncode}: {r.stderr[-300:]}"
    return dst


def load_nodup(path):
    dups = []

    def hook(pairs):
        seen = set()
        for k, _ in pairs:
            if k in seen:
                dups.append(k)
            seen.add(k)
        return dict(pairs)

    obj = json.load(open(path), object_pairs_hook=hook)
    return obj, dups


fix = {"version": 2, "bpm": 124, "key": "F minor", "lengthBars": 4, "masterGainDb": 0,
       "chords": [{"bar": 1, "chord": "Fm", "conf": 0.9}, {"bar": 2, "chord": "Db", "conf": 0.8}],
       "lyrics": {"verse": "one two three"},
       "_future_annotation": {"anything": [1, 2, 3], "nested": {"deep": True}},
       "master": [{"id": "fx_truepeak", "params": {"ceiling": -1.2}}],
       "tracks": [{"name": "keys", "source": {"kind": "faust", "id": "pluck"}, "gainDb": -3,
                   "notes": [{"start": 0, "len": 1, "pitch": 65, "vel": 0.9}]}]}

out_path = resave(fix, "fix")
out, dups = load_nodup(out_path)
ok(not dups, f"no duplicate top-level keys in the serialization ({dups})")
ok(out.get("chords") == fix["chords"], "chords[] round-trips byte-equal (bars, labels, confidences)")
ok(out.get("lyrics") == fix["lyrics"], "lyrics round-trips byte-equal")
ok(out.get("_future_annotation") == fix["_future_annotation"],
   "an unknown FUTURE annotation round-trips verbatim (the class, not the instance)")
ok(abs(out["bpm"] - 124) < 1e-9 and out["key"] == "F minor" and abs(out["lengthBars"] - 4) < 1e-9,
   "modeled fields stay exact (bpm/key/lengthBars)")
n0, n1 = fix["tracks"][0]["notes"][0], out["tracks"][0]["notes"][0]
ok(out["tracks"][0]["name"] == "keys" and abs(n1["pitch"] - n0["pitch"]) < 1e-9,
   "track content intact through the round trip")
ok(set(fix.keys()) <= set(out.keys()), "NO top-level key of the input is dropped")

out2_path = resave(out, "fix2")
out2, dups2 = load_nodup(out2_path)
ok(not dups2 and out2 == out, "idempotent: resave(resave(x)) == resave(x)")

# MODELED keys may NORMALIZE (the serializer elides semantic defaults — straight
# swing amount<=0.5 is a no-op by applySwing and is dropped by design). The law
# under test is for UNMODELED keys: they must NEVER drop.
MODELED = {"version", "bpm", "key", "lengthBars", "masterGainDb", "swing",
           "tempoMap", "sections", "provenance", "_loop", "midiMap", "master",
           "buses", "automation", "tracks", "scenes"}
crates = sorted(glob.glob(os.path.join(ROOT, "songs", "crate", "*.json")))
ok(len(crates) > 0, "crate songs present for the real-song leg")
swing_kept = 0
for c in crates:
    src = json.load(open(c))
    o, d = load_nodup(resave(src, os.path.basename(c)[:-5]))
    assert not d, f"dup keys on {c}"
    dropped = set(src.keys()) - set(o.keys())
    assert dropped <= MODELED, f"{c}: UNMODELED key dropped: {dropped - MODELED}"
    for k in dropped:
        assert k == "swing" and float(src["swing"].get("amount", 0.5)) <= 0.5, \
            f"{c}: non-default modeled key dropped: {k}={src[k]}"
    if float((src.get("swing") or {}).get("amount", 0.5)) > 0.5:
        assert o.get("swing") == src["swing"], f"{c}: real swing lost"
        swing_kept += 1
    assert len(o["tracks"]) == len(src["tracks"]), c
    assert sum(len(t.get("notes", [])) for t in o["tracks"]) == \
           sum(len(t.get("notes", [])) for t in src["tracks"]), c
ok(swing_kept >= 2,
   f"real crate songs ({len(crates)}): unmodeled keys never drop, defaults may normalize, "
   f"non-default swing survives ({swing_kept} songs)")

plain = {"bpm": 120, "lengthBars": 4,
         "tracks": [{"name": "a", "source": {"kind": "faust", "id": "pluck"},
                     "notes": [{"start": 0, "len": 1, "pitch": 60, "vel": 0.8}]}]}
po, _ = load_nodup(resave(plain, "plain"))
ok("extras" not in po and "chords" not in po,
   "a song with no extra fields gains none (no phantom keys)")

print(f"PASS {N}/{N} undroppable battery")
