#!/usr/bin/env python3
"""#1 face leg — meterMap <-> SMF FF58 time signatures (midi_bridge).
Pure python, no engine. Proof surface:
  A) export: FF58 bytes land at the exact bar-start QUARTER ticks
  B) import: FF58 walk recovers bar-indexed meterMap (den from log2 dd)
  C) idempotency law: mid1 == mid2 through a second json round-trip
  D) mapless regression: a no-meterMap song exports the exact pre-#1 stream
  E) default suppression: a lone 4/4-at-0 FF58 imports as NO meterMap
Run: python3 tools/midi_meter_battery.py"""
import json, os, sys, tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from midi_bridge import export_midi, import_midi, _bar_start_q, TPQ

N = {"pass": 0, "fail": 0}
def check(name, cond, detail=""):
    N["pass" if cond else "fail"] += 1
    print(("PASS " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""),
          flush=True)

def song(meter, notes, lyrics=None):
    return {"version": 2, "bpm": 120, "lengthBars": 8, "masterGainDb": 0,
            "master": [], "meterMap": meter, "lyrics": lyrics or [],
            "tracks": [{"name": "kick", "source": {"kind": "sample", "kit": "gm_drums"},
                        "gainDb": -6,
                        "notes": [{"start": s, "len": 0.4, "pitch": 36, "vel": 0.9}
                                  for s in notes]}]}

def main():
    d = tempfile.mkdtemp(prefix="midimeter_")
    def wj(doc, name):
        p = os.path.join(d, name)
        json.dump(doc, open(p, "w"))
        return p

    # A) 4/4 (2 bars) -> 7/8: switch bar starts at quarter 8 = tick 3840
    sp = wj(song([{"bar": 2, "num": 7, "den": 8}], [0, 4, 8, 11.5]), "sw.json")
    mp = os.path.join(d, "sw.mid")
    export_midi(sp, mp)
    raw = open(mp, "rb").read()
    sig78 = bytes([0x58, 0x04, 7, 3, 24, 8])
    check("A: 7/8 FF58 body present (num=7 dd=3)", b"\xFF" + sig78 in raw)
    at = raw.find(b"\xFF" + sig78)
    # the delta-time before it must decode to tick 3840 from the FF51 at tick 0
    check("A: switch lands at tick 3840 (vlq 9E 00)",
          raw[at - 2:at] == bytes([0x9E, 0x00]),
          f"pre-bytes {raw[max(0, at - 2):at].hex()}")
    check("A: _bar_start_q mirrors the C++ walk",
          _bar_start_q([{"bar": 2, "num": 7, "den": 8}], 4) == 15.0)

    # B) import recovers the map exactly
    jp = os.path.join(d, "sw_rt.json")
    import_midi(mp, jp)
    rt = json.load(open(jp))
    check("B: round-trip meterMap exact",
          rt.get("meterMap") == [{"bar": 2, "num": 7, "den": 8}],
          str(rt.get("meterMap")))
    check("B: meter-aware lengthBars (2x4/4 + kicks into 7/8 = 4 bars)",
          rt["lengthBars"] == 4, str(rt["lengthBars"]))

    # C) idempotency law: export(import(mid1)) == mid1
    mp2 = os.path.join(d, "sw2.mid")
    export_midi(jp, mp2)
    jp2 = os.path.join(d, "sw_rt2.json")
    import_midi(mp2, jp2)
    mp3 = os.path.join(d, "sw3.mid")
    export_midi(jp2, mp3)
    check("C: second-pass byte-idempotent",
          open(mp2, "rb").read() == open(mp3, "rb").read())

    # D) mapless song: byte-identical to the pre-#1 exporter (golden md5)
    pre = wj({"version": 2, "bpm": 120, "lengthBars": 4, "masterGainDb": 0,
              "master": [],
              "lyrics": [{"beat": 0, "text": "gold"}, {"beat": 2.5, "text": "en"}],
              "tracks": [{"name": "kick",
                          "source": {"kind": "sample", "kit": "gm_drums"}, "gainDb": -6,
                          "notes": [{"start": 0, "len": 0.4, "pitch": 36, "vel": 0.9},
                                    {"start": 4, "len": 0.4, "pitch": 36, "vel": 0.9}]},
                         {"name": "keys", "source": {"kind": "faust", "id": "epiano"},
                          "gainDb": -8,
                          "notes": [{"start": 1, "len": 1.5, "pitch": 60, "vel": 0.7},
                                    {"start": 2.5, "len": 1.0, "pitch": 64, "vel": 0.6}]}]},
             "pre.json")
    mpre = os.path.join(d, "pre.mid")
    export_midi(pre, mpre)
    import hashlib
    got = hashlib.md5(open(mpre, "rb").read()).hexdigest()
    check("D: mapless export byte-identical to pre-#1 stream",
          got == "03b99350dadffdc93d26ff7a054cc902", got)
    check("D: no FF58 in a mapless export", b"\xFF\x58" not in open(mpre, "rb").read())

    # E) a lone 4/4-at-0 FF58 (every DAW emits one) imports as NO meterMap
    sp44 = wj(song([{"bar": 0, "num": 4, "den": 4}], [0, 4]), "s44.json")
    mp44 = os.path.join(d, "s44.mid")
    export_midi(sp44, mp44)
    check("E: 4/4-at-0 exports its FF58", b"\xFF\x58\x04\x04\x02\x18\x08"
          in open(mp44, "rb").read())
    jp44 = os.path.join(d, "s44_rt.json")
    import_midi(mp44, jp44)
    check("E: ...but imports as no meterMap (SMF default)",
          "meterMap" not in json.load(open(jp44)))

    # F) 12/16 den survives the log2 door both ways
    sp16 = wj(song([{"bar": 0, "num": 12, "den": 16}], [0, 3, 6]), "s16.json")
    mp16 = os.path.join(d, "s16.mid")
    export_midi(sp16, mp16)
    jp16 = os.path.join(d, "s16_rt.json")
    import_midi(mp16, jp16)
    check("F: 12/16 round-trips (dd=4)",
          json.load(open(jp16)).get("meterMap") == [{"bar": 0, "num": 12, "den": 16}])

    print(f"\n{N['pass']} passed, {N['fail']} failed")
    sys.exit(1 if N["fail"] else 0)

if __name__ == "__main__":
    main()
