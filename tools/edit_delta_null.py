#!/usr/bin/env python3
"""THE ENGINE DELTA's proof organ (docs/ENGINE_DELTA_CAMPAIGN.md).

For every delta class the live UI claims (notes / mix / srcparam / fxparam / send /
noop / trackadd / trackremove / fxshape / srcswap / autocurve), build a (base,
mutated) song pair and run `m1 delta-null base mut a.wav b.wav`:
the delta-applied edit's render (a) and a fresh buildEdit(mutated) render (b) must be
a NULL pair (bit-exact expected; anything above -120 dBFS residual fails). For every
class the delta REFUSES (topology, chain shape, tempo, retune, removed keys, ...),
m1 must exit 2 with NO output written — refusal is loud, never wrong-but-silent.

Corpus is faust-only (no kits, no vst3 cache) so the battery is deterministic on any
machine. Renders are 24-bit (sampwidth=3) — parsed as such, per the m1 law.

Usage: .venv/bin/python tools/edit_delta_null.py            # full battery
       .venv/bin/python tools/edit_delta_null.py --keep     # keep the work dir
"""
import copy
import json
import math
import os
import struct
import subprocess
import sys
import tempfile
import wave

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M1 = os.environ.get("SOTADAW_M1", os.path.join(ROOT, "app/build/m1_artefacts/Release/m1"))

BASE = {
    "version": 2,
    "bpm": 124,
    "key": "F minor",
    "lengthBars": 2,
    "masterGainDb": 0.0,
    "swing": {"grid": "16th", "amount": 0.56},
    "master": [
        {"id": "fx_trim", "params": {"level": -2.0}},
        {"id": "fx_truepeak", "params": {"ceiling": -1.2}},
    ],
    "buses": [
        {"id": "verb", "gainDb": -2.0, "fx": [{"id": "fx_reverb", "params": {"mix": 0.3, "size": 0.5, "damp": 0.4}}]},
    ],
    "tracks": [
        {
            "name": "kick",
            "source": {"kind": "faust", "id": "kick_808", "params": {"decay": 0.5}},
            "gainDb": -1.5, "pan": 0.0,
            "notes": [{"start": b, "len": 0.5, "pitch": 36, "vel": 0.95} for b in (0, 1, 2, 3, 4, 5, 6, 7)],
        },
        {
            "name": "bass",
            "source": {"kind": "faust", "id": "bass_warm", "params": {"cutoff": 900.0, "res": 0.2}},
            "gainDb": -3.0, "pan": 0.0,
            "notes": [
                {"start": 0.0, "len": 0.75, "pitch": 41, "vel": 0.8},
                {"start": 1.5, "len": 0.5, "pitch": 41, "vel": 0.7},
                {"start": 3.5, "len": 0.5, "pitch": 44, "vel": 0.7, "chance": 0.5},
                {"start": 4.0, "len": 0.75, "pitch": 41, "vel": 0.8},
                {"start": 6.5, "len": 1.0, "pitch": 39, "vel": 0.75},
            ],
        },
        {
            "name": "lead",
            "source": {"kind": "faust", "id": "flute_lead", "params": {}},
            "gainDb": -6.0, "pan": 0.2,
            "fx": [
                {"id": "fx_filter", "params": {"cutoff": 1200.0, "res": 0.3}},
                {"id": "fx_delay", "params": {"time": 0.25, "feedback": 0.3, "mix": 0.25}},
            ],
            "sends": [{"bus": "verb", "gainDb": -12.0}],
            "notes": [
                {"start": 0.25, "len": 0.5, "pitch": 65, "vel": 0.7},   # odd 16ths: the swing
                {"start": 0.75, "len": 0.5, "pitch": 68, "vel": 0.65},  # law must survive the
                {"start": 2.25, "len": 0.75, "pitch": 72, "vel": 0.7},  # delta rewrite
                {"start": 4.75, "len": 1.0, "pitch": 70, "vel": 0.75, "chance": 0.5},
                {"start": 6.0, "len": 1.5, "pitch": 65, "vel": 0.8},
            ],
        },
    ],
}


# wave-2 base: curves already riding (class 7 change/removal cases start here)
AUTO_BASE = copy.deepcopy(BASE)
AUTO_BASE["tracks"][2]["automation"] = [
    {"target": "gainDb", "points": [{"beat": 0, "v": -18.0}, {"beat": 8, "v": -3.0, "curve": 0.5}]},
    {"target": "fx[0].cutoff", "points": [{"beat": 0, "v": 400.0}, {"beat": 8, "v": 4000.0}]},
]
AUTO_BASE["automation"] = [
    {"target": "masterGainDb", "points": [{"beat": 0, "v": -6.0}, {"beat": 8, "v": 0.0}]},
]


def mutate(base=None, **changes):
    s = copy.deepcopy(BASE if base is None else base)
    for path, val in changes.items():
        # tiny path DSL: "tracks.0.gainDb" etc; "__call__" values are fn(song)
        if callable(val):
            val(s)
            continue
        parts = path.split(".")
        obj = s
        for p in parts[:-1]:
            obj = obj[int(p)] if p.isdigit() else obj[p]
        last = parts[-1]
        obj[int(last) if last.isdigit() else last] = val
    return s


def read_wav(path):
    with wave.open(path, "rb") as w:
        sw, n, ch = w.getsampwidth(), w.getnframes(), w.getnchannels()
        raw = w.readframes(n)
    if sw == 3:  # 24-bit: the m1 default — parse as such or fake a 1.5x slowdown
        samples = []
        for i in range(0, len(raw), 3):
            v = raw[i] | (raw[i + 1] << 8) | (raw[i + 2] << 16)
            if v & 0x800000:
                v -= 0x1000000
            samples.append(v)
        return samples, 8388608.0, ch
    if sw == 2:
        return list(struct.unpack("<%dh" % (len(raw) // 2), raw)), 32768.0, ch
    raise SystemExit("unexpected sampwidth %d in %s" % (sw, path))


def null_verdict(a_path, b_path):
    a, fs, _ = read_wav(a_path)
    b, _, _ = read_wav(b_path)
    if len(a) != len(b):
        return False, "length mismatch %d vs %d" % (len(a), len(b))
    peak_b = max(1, max(abs(x) for x in b))
    peak_db = 20.0 * math.log10(peak_b / fs)
    if peak_db < -60.0:
        return False, "fresh render near-silent (%.1f dBFS) - trivial null" % peak_db
    diff = max(abs(x - y) for x, y in zip(a, b))
    if diff == 0:
        return True, "bit-exact"
    db = 20.0 * math.log10(diff / fs)
    return db < -120.0, "residual peak %.1f dBFS (diff=%d)" % (db, diff)


def main():
    keep = "--keep" in sys.argv
    if not os.path.exists(M1):
        raise SystemExit("m1 binary missing: %s (build first)" % M1)
    work = tempfile.mkdtemp(prefix="edit_delta_null_")
    passed = failed = 0

    def run_case(name, mut, expect_rc, expect_class=None, base=None):
        nonlocal passed, failed
        bp = os.path.join(work, name + "_base.json")
        mp = os.path.join(work, name + "_mut.json")
        ap = os.path.join(work, name + "_delta.wav")
        fp = os.path.join(work, name + "_fresh.wav")
        json.dump(BASE if base is None else base, open(bp, "w"))
        json.dump(mut, open(mp, "w"))
        r = subprocess.run([M1, "delta-null", bp, mp, ap, fp],
                           capture_output=True, text=True, cwd=ROOT)
        ok = r.returncode == expect_rc
        detail = "rc=%d (want %d)" % (r.returncode, expect_rc)
        if ok and expect_rc == 0:
            ok, why = null_verdict(ap, fp)
            detail += " " + why
            cls = [l for l in r.stdout.splitlines() if "delta applied class=" in l]
            if cls:
                detail += "  [" + cls[0].split("class=")[1].strip() + "]"
                if expect_class and expect_class not in cls[0]:
                    ok, detail = False, detail + " (wanted class %s)" % expect_class
        if ok and expect_rc == 2 and os.path.exists(ap):
            ok, detail = False, "REFUSED but wrote output - wrong-but-silent!"
        print("%s %-14s %s" % ("PASS" if ok else "FAIL", name, detail))
        if not ok and r.returncode != expect_rc:
            sys.stdout.write("".join("  | " + l + "\n" for l in (r.stdout + r.stderr).splitlines()[-8:]))
        passed, failed = passed + (1 if ok else 0), failed + (0 if ok else 1)

    # ---- delta classes: must apply AND null against a fresh build ----
    def m1_notes(s):
        s["tracks"][0]["notes"].append({"start": 3.5, "len": 0.25, "pitch": 36, "vel": 0.9})
        led = s["tracks"][2]["notes"]
        led[1]["start"] = 0.5           # moved
        led[2]["vel"] = 0.9             # velocity
        del led[4]                      # deleted
        led.append({"start": 7.0, "len": 0.75, "pitch": 74, "vel": 0.7})  # added
    run_case("notes", mutate(_=m1_notes), 0, "notes")

    def m2_mix(s):
        s["tracks"][0]["gainDb"] = -4.0
        s["tracks"][2]["pan"] = -0.3
        s["tracks"][1]["muted"] = True
        s["masterGainDb"] = -1.0
        s["buses"][0]["gainDb"] = 0.0
    run_case("mix", mutate(_=m2_mix), 0, "mix")

    def m3_src(s):
        s["tracks"][1]["source"]["params"]["cutoff"] = 500.0
        s["tracks"][1]["source"]["params"]["res"] = 0.35
        s["tracks"][0]["source"]["params"]["drive"] = 1.5   # ADDED key (zone was at default)
    run_case("srcparam", mutate(_=m3_src), 0, "srcparam")

    def m4_fx(s):
        s["tracks"][2]["fx"][0]["params"]["cutoff"] = 650.0
        s["tracks"][2]["fx"][1]["params"]["mix"] = 0.4
        s["master"][0]["params"]["level"] = -4.0
        s["buses"][0]["fx"][0]["params"]["mix"] = 0.45
    run_case("fxparam", mutate(_=m4_fx), 0, "fxparam")

    run_case("send", mutate(**{"tracks.2.sends.0.gainDb": -6.0}), 0, "send")

    def m6_noop(s):
        s["provenance"] = {"history": ["accept 42"]}
        s["sections"] = [{"name": "drop", "startBar": 0}]
        s["tracks"][0]["color"] = "#ff8800"
    run_case("noop", mutate(_=m6_noop), 0, "noop")

    def m7_combo(s):
        m1_notes(s); m2_mix(s); m3_src(s); m4_fx(s)
        s["tracks"][2]["sends"][0]["gainDb"] = -6.0
        s["tracks"][1]["name"] = "sub"
    run_case("combo", mutate(_=m7_combo), 0)

    # class 6a: append a full new track (source + fx + send + notes) at the end
    def m8_addtrack(s):
        s["tracks"].append({
            "name": "hat",
            "source": {"kind": "faust", "id": "hat", "params": {"decay": 0.3}},
            "gainDb": -8.0, "pan": -0.15,
            "fx": [{"id": "fx_filter", "params": {"cutoff": 6000.0, "res": 0.2}}],
            "sends": [{"bus": "verb", "gainDb": -15.0}],
            "notes": [{"start": b * 0.5 + 0.25, "len": 0.15, "pitch": 42, "vel": 0.6}
                      for b in range(16)],
        })
    run_case("trackadd", mutate(_=m8_addtrack), 0, "trackadd")

    def m9_addcombo(s):        # append composes with prefix deltas (the real accept shape)
        m8_addtrack(s)
        s["tracks"][0]["notes"].append({"start": 3.75, "len": 0.2, "pitch": 36, "vel": 0.85})
        s["tracks"][1]["gainDb"] = -5.0
    run_case("addcombo", mutate(_=m9_addcombo), 0)

    def m10_removetrack(s):    # remove the MIDDLE track — subsequence, not suffix
        del s["tracks"][1]
    run_case("trackremove", mutate(_=m10_removetrack), 0, "trackremove")

    def m11_removemask(s):     # removal + a masked-field change on a kept track
        del s["tracks"][1]
        s["tracks"][0]["color"] = "#00ffcc"
    run_case("removemask", mutate(_=m11_removemask), 0, "trackremove")

    def m12_addmin(s):   # the minimal append (no fx/sends) — was a falsifier before 6a
        s["tracks"].append({"name": "hat", "source": {"kind": "faust", "id": "hat"},
                            "notes": [{"start": 0.5, "len": 0.25, "pitch": 42, "vel": 0.6}]})
    run_case("trackadd_min", mutate(_=m12_addmin), 0, "trackadd")

    # ---- wave 2: class 5a fx chain shape (was falsifier f_chainshape before 5a) ----
    def m13_fxadd(s):
        s["tracks"][2]["fx"].append({"id": "fx_saturate", "params": {"drive": 2.0}})
    run_case("fxadd", mutate(_=m13_fxadd), 0, "fxshape")

    def m14_fxremove(s):
        del s["tracks"][2]["fx"][1]           # the delay goes; filter + send survive
    run_case("fxremove", mutate(_=m14_fxremove), 0, "fxshape")

    def m15_fxreorder(s):
        s["tracks"][2]["fx"].reverse()        # delay -> filter becomes filter -> delay
    run_case("fxreorder", mutate(_=m15_fxreorder), 0, "fxshape")

    def m16_fxswapid(s):                      # same slot, different fx entirely
        s["tracks"][2]["fx"][0] = {"id": "fx_widen", "params": {"width": 1.4}}
    run_case("fxswapid", mutate(_=m16_fxswapid), 0, "fxshape")

    def m17_buschain(s):                      # the bus leg of 5a
        s["buses"][0]["fx"].append({"id": "fx_widen", "params": {"width": 1.3}})
    run_case("buschain", mutate(_=m17_buschain), 0, "fxshape")

    EQ_BASE = copy.deepcopy(BASE)             # built-ins graduate through the chain rebuild:
    EQ_BASE["tracks"][2]["fx"].append({"type": "eq", "params": {"loFreq": 200.0, "loGain": 4.0}})
    def m17b_eqparam(s):
        s["tracks"][2]["fx"][2]["params"]["loGain"] = -6.0   # natural-unit param, rebuilt not set
    run_case("eqparam", mutate(EQ_BASE, _=m17b_eqparam), 0, "fxshape", base=EQ_BASE)

    # ---- wave 2: class 5b source swap (was falsifiers f_srcswap / f_keyremoved) ----
    run_case("srcswap", mutate(**{"tracks.0.source.id": "clap_909"}), 0, "srcswap")

    def m18_srckeyrm(s):
        del s["tracks"][1]["source"]["params"]["res"]   # removed key => fresh voice at defaults
    run_case("srckeyrm", mutate(_=m18_srckeyrm), 0, "srcswap")

    # ---- wave 2: class 7 automation curves (was falsifier f_automation) ----
    def m19_autoadd(s):
        s["tracks"][2]["automation"] = [{"target": "gainDb",
                                         "points": [{"beat": 0, "v": -18.0}, {"beat": 8, "v": -3.0, "curve": 0.7}]}]
    run_case("auto_add", mutate(_=m19_autoadd), 0, "autocurve")

    def m20_autochange(s):
        s["tracks"][2]["automation"][1]["points"][1]["v"] = 2500.0     # sweep top moved
        s["tracks"][2]["automation"][0]["points"][1]["curve"] = -0.5   # build becomes early-jump
        s["automation"][0]["points"][0]["v"] = -9.0                    # master ramp deeper
    run_case("auto_change", mutate(AUTO_BASE, _=m20_autochange), 0, "autocurve", base=AUTO_BASE)

    def m21_autorm(s):     # remove the RESTORABLE targets (gainDb + masterGainDb);
        s["tracks"][2]["automation"] = [a for a in s["tracks"][2]["automation"]
                                        if a["target"] != "gainDb"]    # fx sweep stays untouched
        s["automation"] = []
    run_case("auto_rm", mutate(AUTO_BASE, _=m21_autorm), 0, "autocurve", base=AUTO_BASE)

    def m22_combo5(s):     # the wave-2 accept shape: reshape + ride + notes in ONE take
        s["tracks"][2]["fx"].append({"id": "fx_saturate", "params": {"drive": 1.2}})
        s["tracks"][2]["notes"][0]["vel"] = 0.9
        s["tracks"][1]["automation"] = [{"target": "source.cutoff",
                                         "points": [{"beat": 0, "v": 500.0}, {"beat": 8, "v": 1800.0}]}]
    run_case("combo5", mutate(_=m22_combo5), 0)

    def m23_addplusauto(s):    # class 6a + class 7 compose
        m8_addtrack(s)
        s["tracks"][2]["automation"] = [{"target": "pan",
                                         "points": [{"beat": 0, "v": -0.5}, {"beat": 8, "v": 0.5}]}]
    run_case("add_autocombo", mutate(_=m23_addplusauto), 0)

    def m24_reorder(s):    # GRADUATED falsifier (wave 2): a curve-free reorder decomposes
        s["tracks"] = [s["tracks"][1], s["tracks"][0], s["tracks"][2]]  # into positional
    run_case("reorder_rw", mutate(_=m24_reorder), 0, "srcswap")         # rewrites — engine
                                                                        # track i IS song track i

    # ---- falsifiers: the delta MUST refuse (rc=2), never apply wrong ----

    def f2(s):
        s["master"] = list(reversed(s["master"]))   # master chain SHAPE: the wall lives there
    run_case("f_masterchain", mutate(_=f2), 2)

    run_case("f_tempo", mutate(bpm=128), 2)
    run_case("f_bars", mutate(lengthBars=4), 2)
    run_case("f_swing", mutate(**{"swing.amount": 0.5}), 2)

    def f4(s):
        s["buses"].append({"id": "slap", "gainDb": 0, "fx": [{"id": "fx_delay", "params": {}}]})
    run_case("f_addbus", mutate(_=f4), 2)

    def f5(s):
        s["tracks"][2]["fx"] = [{"id": "fx_retune", "params": {"amount": 1.0}},
                                {"id": "fx_delay", "params": {"time": 0.25, "feedback": 0.3, "mix": 0.25}}]
    run_case("f_retune", mutate(_=f5), 2)

    def f6(s):     # kind swap: a sampler kit is not a live-rebuildable faust voice
        s["tracks"][1]["source"] = {"kind": "sample", "id": "no_such_kit", "params": {}}
    run_case("f_srckind", mutate(_=f6), 2)

    def f7(s):     # removing a ZONE-target curve: the un-automated base is not derivable
        s["tracks"][2]["automation"] = [a for a in s["tracks"][2]["automation"]
                                        if a["target"] != "fx[0].cutoff"]
    run_case("f_auto_rmzone", mutate(AUTO_BASE, _=f7), 2, base=AUTO_BASE)

    def f8(s):     # fx[i] curves ride the doomed plugins: reshape near them refuses
        s["tracks"][2]["fx"].append({"id": "fx_saturate", "params": {"drive": 0.5}})
    run_case("f_fxauto", mutate(AUTO_BASE, _=f8), 2, base=AUTO_BASE)

    def f9(s):     # vst3 fx can be null at build => the positional law breaks
        s["tracks"][2]["fx"].append({"id": "vst3:NoSuchPlugin", "params": {}})
    run_case("f_fxvst3", mutate(_=f9), 2)

    def f10(s):
        del s["tracks"][2]["sends"][0]
        s["tracks"][2]["sends"] = []
    run_case("f_sendtopo", mutate(_=f10), 2)

    def f11(s):    # mid-list insert: pair mismatch, never a blind append
        s["tracks"].insert(1, {"name": "perc", "source": {"kind": "faust", "id": "clap_909"},
                               "notes": [{"start": 1.0, "len": 0.3, "pitch": 39, "vel": 0.8}]})
    run_case("f_insertmid", mutate(_=f11), 2)

    def f12(s):    # reorder WITH zone curves: the positional rewrite cannot move
        s["tracks"] = [s["tracks"][1], s["tracks"][0], s["tracks"][2]]   # source.* automation
    REORDER_BASE = copy.deepcopy(BASE)
    REORDER_BASE["tracks"][1]["automation"] = [{"target": "source.cutoff",
                                                "points": [{"beat": 0, "v": 600.0}, {"beat": 8, "v": 1500.0}]}]
    run_case("f_reorder_auto", mutate(REORDER_BASE, _=f12), 2, base=REORDER_BASE)

    def f13(s):    # appended track carrying automation: rebuild's job
        m8 = s["tracks"] + [{
            "name": "hat", "source": {"kind": "faust", "id": "hat"},
            "automation": [{"target": "gainDb",
                            "points": [{"beat": 0, "v": -20}, {"beat": 8, "v": 0}]}],
            "notes": [{"start": 0.5, "len": 0.15, "pitch": 42, "vel": 0.6}],
        }]
        s["tracks"] = m8
    run_case("f_addauto", mutate(_=f13), 2)

    def f14(s):    # remove-and-tweak: kept tracks must be byte-identical
        del s["tracks"][1]
        s["tracks"][0]["gainDb"] = -9.0
    run_case("f_rmtweak", mutate(_=f14), 2)

    print("\n%d/%d checks green" % (passed, passed + failed))
    if keep:
        print("work dir kept: " + work)
    elif failed == 0:
        import shutil
        shutil.rmtree(work, ignore_errors=True)
    else:
        print("work dir (for forensics): " + work)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
