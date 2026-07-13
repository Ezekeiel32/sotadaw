#!/usr/bin/env python3
"""THE ONE-TEMPO LAW battery (Chezy 2026-07-13, the untitled_43 tempo split: song
bpm moved 172->186 while the vocal's unwarped clips kept pacing at 172 — the band
ran 8% faster than the singer and every pitch pass read chords from windows the
audio had drifted out of). ONE bpm for the whole song, the same number for the
user, the agent, and every clip:

  - bpm change over a clip with NO sourceBpm  -> stamped with the OLD bpm (warps)
  - explicit sourceBpm 0                       -> respected opt-out (FX/textures)
  - already-warped clips                       -> untouched
  - no bpm change                              -> nothing stamped
  - write_song lane: only PRE-EXISTING clips judged; a warp stripped in the same
    write as a tempo change is restored; brand-new clips belong to the new tempo

Hermetic: SOTADAW_IPC + SONGS sandboxed. Usage: python3 tools/one_tempo_battery.py
"""
import json, os, shutil, struct, sys, tempfile, wave

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ["SOTADAW_IPC"] = tempfile.mkdtemp(prefix="ot_battery_ipc_")
sys.path.insert(0, os.path.join(ROOT, "agent"))
import daw_mcp as dm

dm.SONGS = tempfile.mkdtemp(prefix="ot_battery_songs_")

PASS, FAIL = 0, []
def ok(cond, msg):
    global PASS
    if cond:
        PASS += 1
    else:
        FAIL.append(msg)

def wavf(name):
    p = os.path.join(dm.SONGS, name)
    w = wave.open(p, "w")
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(48000)
    w.writeframes(struct.pack("<h", 0) * 480)
    w.close()
    return p

P = lambda n: os.path.join(dm.SONGS, n + ".json")
A, B, C, N = wavf("a.wav"), wavf("b.wav"), wavf("c.wav"), wavf("new.wav")
doc = {"version": 2, "bpm": 172.0, "lengthBars": 8, "tracks": [
    {"name": "vox", "source": {"kind": "audio", "id": "v"}, "notes": [],
     "audioClips": [{"file": A, "startBeat": 0.0},
                    {"file": B, "startBeat": 8.0, "sourceBpm": 0},
                    {"file": C, "startBeat": 16.0, "sourceBpm": 90.0}]}]}
json.dump(doc, open(P("otx"), "w"))

r = dm.t_update_song_meta({"song": "otx", "bpm": 186.0})
s = json.load(open(P("otx")))
got = [c.get("sourceBpm") for c in s["tracks"][0]["audioClips"]]
ok(got == [172.0, 0, 90.0], f"meta lane: null stamped w/ old bpm, 0 + 90 kept ({got})")
ok("ONE-TEMPO LAW: 1 audio clip" in r, "meta lane: the result narrates the stamp")

r2 = dm.t_update_song_meta({"song": "otx", "masterGainDb": -1.0})
s2 = json.load(open(P("otx")))
ok([c.get("sourceBpm") for c in s2["tracks"][0]["audioClips"]] == [172.0, 0, 90.0]
   and "ONE-TEMPO" not in r2, "no bpm change -> no stamping, no narration")

# write_song lane: strip clip A's warp + change bpm in ONE write, add a new clip
doc2 = json.loads(json.dumps(s2))
doc2["bpm"] = 200.0
doc2["tracks"][0]["audioClips"][0]["sourceBpm"] = None
doc2["tracks"][0]["audioClips"].append({"file": N, "startBeat": 24.0})
r3 = dm.t_write_song({"name": "otx", "song": doc2})
s3 = json.load(open(P("otx")))
got3 = [c.get("sourceBpm") for c in s3["tracks"][0]["audioClips"]]
ok(got3[0] == 172.0, f"write lane: stripped warp RESTORED, not re-stamped ({got3[0]})")
ok(got3[1] == 0 and got3[2] == 90.0, f"write lane: opt-out + warped kept ({got3[1:3]})")
ok(got3[3] is None, f"write lane: brand-new clip belongs to the new tempo ({got3[3]})")
ok("ONE-TEMPO LAW" in r3, "write lane: narrated")

# write_song with NO bpm change never touches clips
doc3 = json.loads(json.dumps(s3))
doc3["tracks"][0]["audioClips"][3]["startBeat"] = 32.0
r4 = dm.t_write_song({"name": "otx", "song": doc3})
s4 = json.load(open(P("otx")))
ok([c.get("sourceBpm") for c in s4["tracks"][0]["audioClips"]] == got3
   and "ONE-TEMPO" not in r4, "write lane: same bpm -> untouched")

for d in (dm.SONGS, os.environ["SOTADAW_IPC"]):
    shutil.rmtree(d, ignore_errors=True)

print(f"one_tempo_battery: {PASS} passed, {len(FAIL)} failed")
for f in FAIL:
    print(f"  FAIL: {f}")
sys.exit(1 if FAIL else 0)
