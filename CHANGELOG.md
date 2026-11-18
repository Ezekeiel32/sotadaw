# Changelog

Versions follow `MAJOR.MINOR.PATCH`. Pre-releases carry `-beta`.

## Unreleased

- README: demo, feature overview, architecture diagram and repository map.
- Repository standards: contributing guide, pull request and issue templates, security policy, CI on every pull request.

## v0.9.0-beta

First public source release of the engine and the desktop app.

- **Three platforms from one tree.** Linux, Windows and macOS (universal: Intel and Apple Silicon) build from the same source. The release workflow renders a test song and starts the app on each platform before it packages the installers.
- **Live instrument compilation on all three.** New Faust instruments compile at run time on Linux, Windows and macOS.
- **Installers.** AppImage for Linux, a setup wizard for Windows with an embedded Python runtime, and a DMG for macOS.
- **Ableton Link** on all platforms.
- **Agent.** MCP server with the DAW's tools, model choice across Claude, GPT and OpenRouter, and login handling for each platform's terminal.
- **Tuning and notes.** Consensus pitch tracking, octave checks and a per-note map for audio-to-MIDI.
- **Interface.** Genre selection that follows the request, calmer chrome, and motion when a proposal is accepted.
