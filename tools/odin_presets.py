#!/usr/bin/env python3
"""Odin2 factory presets -> playable source.params (VST-universe preset rail #2).

  odin_presets.py index          # scan the fetched soundbank -> library.json vst_presets
  odin_presets.py get "<name>"   # params dict (DISPLAY-named) the agent inlines
  odin_presets.py list [CAT]

.odin = JUCE ValueTree binary: records "PARAM id <file_id> value <f64 LE>" in
NATURAL units. File ids are abbreviated (fil1_freq); the plugin's DISPLAY names
differ (Filter1 Frequency) — the alias map below was extracted from Odin2's own
Source/AudioValueTree.h registration table (GPL). SongLoader matches display
names on processor params and converts natural->normalized via each param's own
getValueForText. Bank: 260 factory patches, 14 categories.
"""
import json, os, sys, glob, re, struct

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANK = os.path.join(ROOT, "library", "odin2", "Soundbanks")
LIB = os.path.join(ROOT, "library.json")
_REC = re.compile(rb"id\x00\x01.\x05([a-zA-Z0-9_]+)\x00value\x00\x01\x09\x04(.{8})", re.S)

ALIAS = {
 "osc1_oct": "Osc1 Octave",
 "osc1_semi": "Osc1 Semitones",
 "osc1_fine": "Osc1 Finetune",
 "osc1_vol": "Osc1 Volume",
 "osc1_reset": "Osc1 Reset",
 "osc1_position": "Osc1 Wavetble Position",
 "osc1_detune": "Osc1 Detune",
 "osc1_pos_mod": "Osc1 Position Modulation",
 "osc1_multi_position": "Osc1 Multi Position",
 "osc1_spread": "Osc1 Wavetable Spread",
 "osc1_pulsewidth": "Osc1 PulseWidth",
 "osc1_drift": "Osc1 Drift",
 "osc1_vec_x": "Osc1 Vector X",
 "osc1_vec_y": "Osc1 Vector Y",
 "osc1_arp_speed": "Osc1 Arpeggiator Speed",
 "osc1_step_1": "Osc1 Step1",
 "osc1_step_2": "Osc1 Step2",
 "osc1_step_3": "Osc1 Step3",
 "osc1_arp_on": "Osc1 Arpeggiator On",
 "osc1_step_3_on": "Osc1 Step3 On",
 "osc1_chipnoise": "Osc1 Chipnoise",
 "osc1_exp_fm": "Osc1 Exponential FM",
 "osc1_fm": "Osc1 FM/PM amount",
 "osc1_lp": "Osc1 Noise Lowpass",
 "osc1_hp": "Osc1 Noise Highpass",
 "osc2_oct": "Osc2 Octave",
 "osc2_semi": "Osc2 Semitones",
 "osc2_fine": "Osc2 Finetune",
 "osc2_vol": "Osc2 Volume",
 "osc2_reset": "Osc2 Reset",
 "osc2_sync": "Osc2 Sync",
 "osc2_position": "Osc2 Wavetable Position",
 "osc2_detune": "Osc2 Detune",
 "osc2_pos_mod": "Osc2 Position Modulation",
 "osc2_multi_position": "Osc2 Multi Position",
 "osc2_spread": "Osc2 Wavetable Spread",
 "osc2_pulsewidth": "Osc2 PulseWidth",
 "osc2_drift": "Osc2 Drift",
 "osc2_vec_x": "Osc2 Vector X",
 "osc2_vec_y": "Osc2 Vector Y",
 "osc2_arp_speed": "Osc2 Arpeggiator Speed",
 "osc2_step_1": "Osc2 Step1",
 "osc2_step_2": "Osc2 Step2",
 "osc2_step_3": "Osc2 Step3",
 "osc2_arp_on": "Osc2 Arpeggiator On",
 "osc2_step_3_on": "Osc2 Step3 On",
 "osc2_chipnoise": "Osc2 Chipnoise",
 "osc2_exp_fm": "Osc2 Exponential FM",
 "osc2_fm": "Osc2 FM/PM amount",
 "osc2_lp": "Osc2 Noise Lowpass",
 "osc2_hp": "Osc2 Noise Highpass",
 "osc3_oct": "Osc3 Octave",
 "osc3_semi": "Osc3 Semitones",
 "osc3_fine": "Osc3 Finetune",
 "osc3_vol": "Osc3 Volume",
 "osc3_reset": "Osc3 Reset",
 "osc3_sync": "Osc3 Sync",
 "osc3_position": "Osc3 Wavetable Position",
 "osc3_detune": "Osc3 Detune",
 "osc3_pos_mod": "Osc3 Position Modulation",
 "osc3_multi_position": "Osc3 Multi Position",
 "osc3_spread": "Osc3 Wavetable Spread",
 "osc3_pulsewidth": "Osc3 PulseWidth",
 "osc3_drift": "Osc3 Drift",
 "osc3_vec_x": "Osc3 Vector X",
 "osc3_vec_y": "Osc3 Vector Y",
 "osc3_arp_speed": "Osc3 Arpeggiator Speed",
 "osc3_step_1": "Osc3 Step1",
 "osc3_step_2": "Osc3 Step2",
 "osc3_step_3": "Osc3 Step3",
 "osc3_arp_on": "Osc3 Arpeggiator On",
 "osc3_step_3_on": "Osc3 Step3 On",
 "osc3_chipnoise": "Osc3 Chipnoise",
 "osc3_exp_fm": "Osc3 Exponential FM",
 "osc3_fm": "Osc3 FM/PM amount",
 "osc3_lp": "Osc3 Noise Lowpass",
 "osc3_hp": "Osc3 Noise Highpass",
 "fil1_osc1": "Filter1 Osc1 Input",
 "fil1_osc2": "Filter1 Osc2 Input",
 "fil1_osc3": "Filter1 Osc3 Input",
 "fil1_vel": "Filter1 Velocity Amount",
 "fil1_env": "Filter1 Envelope Amount",
 "fil1_kbd": "Filter1 Keyboard Follow",
 "fil1_gain": "Filter1 Gain",
 "fil1_freq": "Filter1 Frequency",
 "fil1_res": "Filter1 Resonance",
 "fil1_saturation": "Filter1 Saturation",
 "fil1_sem_transition": "Filter1 SEM Transition",
 "fil1_formant_transition": "Filter1 Formant Transition",
 "fil1_ring_mod_amount": "Filter1 RingMod Amount",
 "fil2_osc1": "Filter2 Osc1 Input",
 "fil2_osc2": "Filter2 Osc2 Input",
 "fil2_osc3": "Filter2 Osc3 Input",
 "fil2_fil1": "Filter2 Filter1 Input",
 "fil2_vel": "Filter2 Velocity Amount",
 "fil2_env": "Filter2 Envelope Amount",
 "fil2_kbd": "Filter2 Keyboard Follow",
 "fil2_gain": "Filter2 Gain",
 "fil2_freq": "Filter2 Frequency",
 "fil2_res": "Filter2 Resonance",
 "fil2_saturation": "Filter2 Saturation",
 "fil2_sem_transition": "Filter2 SEM Transition",
 "fil2_formant_transition": "Filter2 Formant Transition",
 "fil2_ring_mod_amount": "Filter2 RingMod Amount",
 "fil3_vel": "Filter3 Velocity Amount",
 "fil3_env": "Filter3 Envelope Amount",
 "fil3_kbd": "Filter3 Keyboard Follow",
 "fil3_gain": "Filter3 Gain",
 "fil3_freq": "Filter3 Frequency",
 "fil3_res": "Filter3 Resonance",
 "fil3_saturation": "Filter3 Saturation",
 "fil3_sem_transition": "Filter3 SEM Transition",
 "fil3_formant_transition": "Filter3 Formant Transition",
 "fil3_ring_mod_amount": "Filter3 RingMod Amount",
 "amp_velocity": "Amplifier Velocity",
 "amp_pan": "Amplifier Panorama",
 "amp_gain": "Amplifier Gain",
 "dist_boost": "Distortion Boost",
 "dist_drywet": "Distortion DryWet",
 "env1_attack": "AmpEnv Attack",
 "env1_decay": "AmpEnv Decay",
 "env1_sustain": "AmpEnv Sustain",
 "env1_release": "AmpEnv Release",
 "env1_loop": "AmpEnv Loop",
 "env2_attack": "FilterEnv Attack",
 "env2_decay": "FilterEnv Decay",
 "env2_sustain": "FilterEnv Sustain",
 "env2_release": "FilterEnv Release",
 "env2_loop": "FilterEnv Loop",
 "env3_attack": "ModEnv Attack",
 "env3_decay": "ModEnv Decay",
 "env3_sustain": "ModEnv Sustain",
 "env3_release": "ModEnv Release",
 "env3_loop": "ModEnv Loop",
 "env4_attack": "GlobalEnv Attack",
 "env4_decay": "GlobalEnv Decay",
 "env4_sustain": "GlobalEnv Sustain",
 "env4_release": "GlobalEnv Release",
 "env4_loop": "GlobalEnv Loop",
 "lfo1_reset": "LFO1 Reset",
 "lfo1_freq": "LFO1 Frequency",
 "lfo2_reset": "LFO2 Reset",
 "lfo2_freq": "LFO2 Frequency",
 "lfo3_reset": "LFO3 Reset",
 "lfo3_freq": "LFO3 Frequency",
 "lfo4_reset": "LFO4 Reset",
 "lfo4_freq": "LFO4 Frequency",
 "fil1_to_amp": "Filter1 To Amplifier",
 "fil2_to_amp": "Filter2 To Amplifier",
 "glide": "Glide",
 "master": "Master",
 "modwheel": "Modwheel",
 "pitchbend": "Pitchbend",
 "xy_x": "XY Pad X",
 "xy_y": "XY Pad Y",
 "delay_pingpong": "Delay PingPong",
 "delay_time": "Delay Time",
 "delay_feedback": "Delay Feedback",
 "delay_hp": "Delay Highpass Frequency",
 "delay_ducking": "Delay Ducking",
 "delay_dry": "Delay Dry",
 "delay_wet": "Delay Wet",
 "delay_on": "Delay On",
 "rev_delay": "Reverb PreDelay",
 "rev_eqgain": "Reverb EQ Gain",
 "rev_eqfreq": "Reverb EQ Freq",
 "rev_ducking": "Reverb Ducking",
 "rev_drywet": "Reverb DryWet",
 "rev_mid_hall": "Reverb Mid Hall",
 "rev_hf_damp": "Reverb High Freq Damp",
 "reverb_on": "Reverb On",
 "phaser_reset": "Phaser Reset",
 "phaser_on": "Phaser On",
 "phaser_freq": "Phaser Frequency",
 "phaser_feedback": "Phaser Feedback",
 "phaser_rate": "Phaser Rate",
 "phaser_mod": "Phaser Amount",
 "phaser_drywet": "Phaser DryWet",
 "flanger_reset": "Flanger Reset",
 "flanger_on": "Flanger On",
 "flanger_rate": "Flanger Rate",
 "flanger_feedback": "Flanger Feedback",
 "flanger_amount": "Flanger Amount",
 "flanger_drywet": "Flanger DryWet",
 "chorus_reset": "Chorus Reset",
 "chorus_on": "Chorus On",
 "chorus_rate": "Chorus Rate",
 "chorus_amount": "Chorus Amount",
 "chorus_feedback": "Chorus Feedback",
 "chorus_drywet": "Chorus DryWet",
 "unison_detune": "Unison Detune",
 "unison_width": "Unison Width",
 "step_0_on": "Arp Step 1 On",
 "step_1_on": "Arp Step 2 On",
 "step_2_on": "Arp Step 3 On",
 "step_3_on": "Arp Step 4 On",
 "step_4_on": "Arp Step 5 On",
 "step_5_on": "Arp Step 6 On",
 "step_6_on": "Arp Step 7 On",
 "step_7_on": "Arp Step 8 On",
 "step_8_on": "Arp Step 9 On",
 "step_9_on": "Arp Step 10 On",
 "step_10_on": "Arp Step 11 On",
 "step_11_on": "Arp Step 12 On",
 "step_12_on": "Arp Step 13 On",
 "step_13_on": "Arp Step 14 On",
 "step_14_on": "Arp Step 15 On",
 "step_15_on": "Arp Step 16 On",
 "step_0_mod_1": "Arp Step 1 Mod 1",
 "step_1_mod_1": "Arp Step 2 Mod 1",
 "step_2_mod_1": "Arp Step 3 Mod 1",
 "step_3_mod_1": "Arp Step 4 Mod 1",
 "step_4_mod_1": "Arp Step 5 Mod 1",
 "step_5_mod_1": "Arp Step 6 Mod 1",
 "step_6_mod_1": "Arp Step 7 Mod 1",
 "step_7_mod_1": "Arp Step 8 Mod 1",
 "step_8_mod_1": "Arp Step 9 Mod 1",
 "step_9_mod_1": "Arp Step 10 Mod 1",
 "step_10_mod_1": "Arp Step 11 Mod 1",
 "step_11_mod_1": "Arp Step 12 Mod 1",
 "step_12_mod_1": "Arp Step 13 Mod 1",
 "step_13_mod_1": "Arp Step 14 Mod 1",
 "step_14_mod_1": "Arp Step 15 Mod 1",
 "step_15_mod_1": "Arp Step 16 Mod 1",
 "step_0_mod_2": "Arp Step 1 Mod 2",
 "step_1_mod_2": "Arp Step 2 Mod 2",
 "step_2_mod_2": "Arp Step 3 Mod 2",
 "step_3_mod_2": "Arp Step 4 Mod 2",
 "step_4_mod_2": "Arp Step 5 Mod 2",
 "step_5_mod_2": "Arp Step 6 Mod 2",
 "step_6_mod_2": "Arp Step 7 Mod 2",
 "step_7_mod_2": "Arp Step 8 Mod 2",
 "step_8_mod_2": "Arp Step 9 Mod 2",
 "step_9_mod_2": "Arp Step 10 Mod 2",
 "step_10_mod_2": "Arp Step 11 Mod 2",
 "step_11_mod_2": "Arp Step 12 Mod 2",
 "step_12_mod_2": "Arp Step 13 Mod 2",
 "step_13_mod_2": "Arp Step 14 Mod 2",
 "step_14_mod_2": "Arp Step 15 Mod 2",
 "step_15_mod_2": "Arp Step 16 Mod 2",
 "step_0_transpose": "Arp Step 1 Transpose",
 "step_1_transpose": "Arp Step 2 Transpose",
 "step_2_transpose": "Arp Step 3 Transpose",
 "step_3_transpose": "Arp Step 4 Transpose",
 "step_4_transpose": "Arp Step 5 Transpose",
 "step_5_transpose": "Arp Step 6 Transpose",
 "step_6_transpose": "Arp Step 7 Transpose",
 "step_7_transpose": "Arp Step 8 Transpose",
 "step_8_transpose": "Arp Step 9 Transpose",
 "step_9_transpose": "Arp Step 10 Transpose",
 "step_10_transpose": "Arp Step 11 Transpose",
 "step_11_transpose": "Arp Step 12 Transpose",
 "step_12_transpose": "Arp Step 13 Transpose",
 "step_13_transpose": "Arp Step 14 Transpose",
 "step_14_transpose": "Arp Step 15 Transpose",
 "step_15_transpose": "Arp Step 16 Transpose",
 "arp_mod_transpose": "Arp Mod Transpose",
 "arp_on": "Arpeggiator On",
 "arp_one_shot": "Arpeggiator OneShot"
}


def parse_preset(path):
    raw = open(path, "rb").read()
    out = {}
    for m in _REC.finditer(raw):
        fid = m.group(1).decode()
        val = struct.unpack("<d", m.group(2))[0]
        out[ALIAS.get(fid, fid)] = round(val, 6)
    return out


def scan():
    out = []
    for p in sorted(glob.glob(f"{BANK}/**/*.odin", recursive=True)):
        parts = os.path.relpath(p, BANK).split(os.sep)
        cat = parts[1] if len(parts) >= 3 else "misc"
        out.append({"plugin": "Odin2", "name": os.path.splitext(os.path.basename(p))[0],
                    "category": cat, "path": p})
    return out


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
    if cmd == "index":
        entries = scan()
        lib = json.load(open(LIB)) if os.path.exists(LIB) else {}
        others = [e for e in lib.get("vst_presets", []) if e.get("plugin") != "Odin2"]
        lib["vst_presets"] = others + entries
        json.dump(lib, open(LIB, "w"), indent=1)
        cats = {}
        for e in entries: cats[e["category"]] = cats.get(e["category"], 0) + 1
        print(f"indexed {len(entries)} Odin2 presets -> library.json vst_presets: {cats}")
    elif cmd == "get":
        for e in scan():
            if sys.argv[2].lower() in e["name"].lower():
                print(json.dumps({"plugin": "Odin2", "name": e["name"], "category": e["category"],
                                  "params": parse_preset(e["path"])}, indent=1)); break
        else:
            raise SystemExit(f"no Odin2 preset matching {sys.argv[2]!r}")
    else:
        cat = sys.argv[2] if len(sys.argv) > 2 else None
        for e in scan():
            if cat is None or e["category"].lower() == cat.lower():
                print(f'{e["category"]:18} {e["name"]}')
