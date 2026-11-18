# Contributing

Everyone taking part is expected to follow the [Code of Conduct](CODE_OF_CONDUCT.md).

## Branches

- `main` is always buildable and is protected: no force pushes, no deletion, and changes arrive through pull requests with CI passing.
- Work happens on short-lived branches cut from `main` and deleted after the merge:
  - `feat/<topic>` for new behavior
  - `fix/<topic>` for bug fixes
  - `docs/<topic>` for documentation
  - `chore/<topic>` for build, CI and repository upkeep
- Pull requests are squash-merged, so `main` keeps a linear history with one commit per change.

## Commits

- Subject line in the imperative, 72 characters or fewer: "Add CLAP parameter gestures", not "added stuff".
- One logical change per commit. Explain the why in the body when it is not obvious from the diff.

## Before you open a pull request

1. Build both targets (see the Build section of the README).
2. Render the demo song and listen to it: `app/build/m1_artefacts/Release/m1 render songs/demo_track.json out.wav`
3. Run the same checks CI runs:
   ```bash
   python -m compileall -q agent tools
   for f in instruments/*.dsp; do faust -lang cpp "$f" -o /dev/null || echo "FAILED $f"; done
   ```
4. New instruments need a render report in `instruments/certs/`.
5. Update `CHANGELOG.md` under "Unreleased".

## Releases

Releases are tagged `vMAJOR.MINOR.PATCH`, with `-beta` for pre-releases. `release.yml` builds and packages the installers for Linux, Windows and macOS.

## Reporting bugs and security issues

Use the issue templates for bugs and feature requests. For security problems, see [SECURITY.md](SECURITY.md).
