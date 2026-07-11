# SOTA DAW — engine source (public beta)

The AI-native DAW: a producer-agent composes arrangements AND authors the
instruments themselves as Faust DSP — no black-box audio generation. Everything
the agent makes is a file: `.dsp` sources, `song.json` arrangements, git history.

**Download installers:** https://sotadaw.netlify.app
**This repo** builds the engine (`m1` renderer + `sotadaw` app) on Linux,
Windows and macOS via `.github/workflows/release.yml` — the CI runners are also
the port's verification machines (render gates + UI boot proofs on every OS).

## Build (any OS)

```
git clone https://github.com/Tracktion/tracktion_engine app/tracktion_engine
cd app/tracktion_engine && git checkout <sha in workflow> \
  && git config --file=.gitmodules submodule.modules/juce.url https://github.com/juce-framework/JUCE.git \
  && git submodule sync && git submodule update --init --recursive && cd ../..
cmake -B app/build -S app -DCMAKE_BUILD_TYPE=Release -DSOTADAW_ENABLE_JIT=OFF
cmake --build app/build --config Release -j2
app/build/m1_artefacts/Release/m1 render songs/demo_track.json out.wav
```

JIT (live-compiling new `.dsp` instruments) needs libfaust ≥ 2.69 with the
interpreter backend (`-DSOTADAW_ENABLE_JIT=ON`; Linux: `apt install libfaust-dev`-era
packages / noble's faust 2.70.3). The AOT registry (50 voices) builds everywhere.

## License

GPL-3.0 (see LICENSE) — this satisfies the corresponding-source obligations of
the JUCE (AGPLv3 free tier) and Tracktion Engine (GPLv3 free tier) engines this
app links. Factory sampled kits derive from GeneralUser GS by S. Christian
Collins (credited; see CREDITS in installers). The optional voice bank is NOT
in this repo (non-commercial license, separate download, attribution required).
