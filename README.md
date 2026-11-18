# SOTA DAW

A digital audio workstation with an AI producer built in. You describe the track; the agent writes the arrangement and builds the instruments it needs as Faust DSP code. Nothing comes out as opaque generated audio. Every result is a file you can open and edit (`.dsp` instrument sources, `song.json` arrangements), and every change is tracked in git.

This repository holds the source of the engine and the desktop app. Installers for Linux, Windows and macOS are at **[sotadaw.netlify.app](https://sotadaw.netlify.app)**.

## What's inside

- **Engine and app (C++20):** built on Tracktion Engine and JUCE, with two targets: `m1`, a command-line renderer, and `sotadaw`, the desktop app.
- **Instruments as code:** 134 Faust instruments and effects in `instruments/`. The built-in set is compiled ahead of time; new instruments are compiled live with the Faust JIT. Each verified instrument has a render report in `instruments/certs/` (peak level, clipping, attack, sustain).
- **Producer agent (Python):** `agent/` holds the agent and an MCP server that gives an LLM the DAW's tools: writing songs, authoring Faust instruments with compile errors fed back for self-correction, rendering and analysis. `skills/` holds the versioned prompt skills it uses for arrangement and sound design.
- **Plugin hosting:** VST3, CLAP and Neural Amp Modeler (NAM).
- **Sampled kits:** drums, piano, electric piano, strings, choir and more in `kits/`.
- **Cross-platform CI:** `.github/workflows/release.yml` builds on Linux, Windows and macOS, renders a test song and checks that the app starts on each, then packages the installers.

## Build

Requires CMake, a C++20 compiler and the Tracktion Engine source:

```bash
git clone https://github.com/Tracktion/tracktion_engine app/tracktion_engine
cd app/tracktion_engine
git checkout <TRACKTION_SHA from .github/workflows/release.yml>
git config --file=.gitmodules submodule.modules/juce.url https://github.com/juce-framework/JUCE.git
git submodule sync && git submodule update --init --recursive
cd ../..
cmake -B app/build -S app -DCMAKE_BUILD_TYPE=Release -DSOTADAW_ENABLE_JIT=OFF
cmake --build app/build --config Release -j2
app/build/m1_artefacts/Release/m1 render songs/demo_track.json out.wav
```

To compile new instruments live, build with `-DSOTADAW_ENABLE_JIT=ON`. This needs libfaust 2.69 or newer with the interpreter backend (on Ubuntu 24.04, the packaged Faust 2.70.3 works).

## Optional extras

The app and the agent run without any extras. Stem separation and audio-to-MIDI need a Python environment:

```bash
python3 -m venv .venv
.venv/bin/pip install demucs basic-pitch soundfile
```

The singing voice uses the Gahata Meiji DiffSinger voice bank, a separate download under a non-commercial license that requires attribution ("Gahata Meiji from LUNAI Project"). The app adds that credit to exports.

## License

GPL-3.0 (see `LICENSE`). This meets the source obligations of the free tiers of JUCE (AGPLv3) and Tracktion Engine (GPLv3), which the app links. The sampled kits are derived from GeneralUser GS by S. Christian Collins, credited in the installers. The voice bank is not part of this repository.
