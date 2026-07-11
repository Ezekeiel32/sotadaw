#!/usr/bin/env python3
"""THE SOUND CANNOT DIE — audio-device self-heal E2E, through the REAL app.

2026-07-11: a save-time device-busy storm made JUCE persist
audioOutputDeviceName="" into Settings.xml — every launch after booted SILENT
until Chezy manually re-picked a device. This rig proves the startup heal:

  wiped      Settings.xml holds output="" .............. app heals to a live device
                                                          (PipeWire/default bridge preferred)
  respected  Settings.xml holds a valid, working name ... app KEEPS it (no clobber)
  remembered after a heal, ui.json lastGoodAudioOut ..... the record that survives
                                                          the NEXT Settings.xml wipe
  freshbox   no Settings.xml at all ..................... first run still opens audio

Launch recipe = hands_e2e law: isolated HOME + SOTADAW_IPC, SOTADAW_NO_SIDECAR=1,
--snapshot (peerless, no window), SOTADAW_AUDIO_PROBE=1 prints one machine line
`[audioprobe] {"open":bool,"output":"name"}` from inside the ctor and exits.

Usage: tools/audio_heal_e2e.py [runs]     (default 3)
"""
import json, os, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIN = os.path.join(ROOT, "app/build/sotadaw_artefacts/Release/SOTA DAW")

SETTINGS = """<?xml version="1.0" encoding="UTF-8"?>
<PROPERTIES>
  <VALUE name="audio_device_setup">
    <DEVICESETUP deviceType="ALSA" audioOutputDeviceName="{out}"
                 audioInputDeviceName="" audioDeviceRate="44100.0" audioDeviceBufferSize="512"/>
  </VALUE>
</PROPERTIES>
"""

fails = []


def check(ok, msg):
    print(("  PASS " if ok else "  FAIL ") + msg)
    if not ok:
        fails.append(msg)


def probe(home, tag):
    """Launch the real binary against an isolated HOME; return the audioprobe dict."""
    env = dict(os.environ)
    env.update({"HOME": home, "SOTADAW_IPC": os.path.join(home, "ipc"),
                "SOTADAW_NO_SIDECAR": "1", "SOTADAW_AUDIO_PROBE": "1",
                "SOTADAW_CHRONICLE": "0"})
    os.makedirs(env["SOTADAW_IPC"], exist_ok=True)
    snap = os.path.join(home, "probe.png")
    p = subprocess.run([BIN, "--snapshot", snap], env=env, cwd=ROOT,
                       capture_output=True, text=True, timeout=150)
    line = next((l for l in p.stdout.splitlines() if l.startswith("[audioprobe] ")), None)
    check(line is not None, f"{tag}: probe line reached stdout (rc={p.returncode})")
    if line is None:
        sys.stderr.write((p.stdout or "")[-1500:] + "\n" + (p.stderr or "")[-1500:] + "\n")
        return {}
    return json.loads(line[len("[audioprobe] "):])


def seed(home, out=None):
    cfg = os.path.join(home, ".config/sotadaw")
    os.makedirs(cfg, exist_ok=True)
    if out is not None:
        with open(os.path.join(cfg, "Settings.xml"), "w") as f:
            f.write(SETTINGS.format(out=out))
    return cfg


def one_run(i):
    print(f"[audio-heal] run {i}")
    with tempfile.TemporaryDirectory(prefix="sotadaw_audioheal_") as td:
        # -- wiped: the exact poison from 2026-07-11 -------------------------
        home = os.path.join(td, "wiped"); seed(home, out="")
        r = probe(home, "wiped")
        check(bool(r.get("open")), "wiped: an output device is OPEN despite the wiped name")
        healed = r.get("output", "")
        check(bool(healed), "wiped: healed output name is non-empty")
        check("pipewire" in healed.lower() or "default" in healed.lower(),
              f"wiped: heal preferred a desktop bridge (got '{healed}')")

        # -- remembered: the heal left the wipe-survivor record -------------
        ui = os.path.join(home, ".config/sotadaw/ui.json")
        last = ""
        if os.path.exists(ui):
            with open(ui) as f:
                last = json.load(f).get("lastGoodAudioOut", "")
        check(last == healed and last != "",
              f"remembered: ui.json lastGoodAudioOut == healed name ('{last}')")

        # -- respected: a valid saved choice is never clobbered -------------
        home2 = os.path.join(td, "respected"); seed(home2, out=healed)
        r2 = probe(home2, "respected")
        check(r2.get("output") == healed and bool(r2.get("open")),
              f"respected: valid saved device kept verbatim ('{r2.get('output')}')")

        # -- freshbox: first run (no Settings.xml) opens audio --------------
        home3 = os.path.join(td, "freshbox"); seed(home3, out=None)
        r3 = probe(home3, "freshbox")
        check(bool(r3.get("open")) and bool(r3.get("output")),
              f"freshbox: first run has a live output ('{r3.get('output')}')")


if __name__ == "__main__":
    runs = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    if not os.path.exists(BIN):
        sys.exit("binary missing: " + BIN)
    for i in range(1, runs + 1):
        one_run(i)
    if fails:
        print(f"[audio-heal] RED — {len(fails)} failing check(s)")
        sys.exit(1)
    print(f"[audio-heal] GREEN x{runs} — the sound cannot die")
