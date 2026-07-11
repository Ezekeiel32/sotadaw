#!/usr/bin/env bash
# Apply SOTA DAW patches to the vendored (git-ignored) tracktion_engine clone.
# The clone is disposable; app/patches/*.patch are the git truth. Idempotent:
# a patch whose marker string already exists in the tree is skipped. Invoked
# automatically at cmake configure (app/CMakeLists.txt) and safe to run by hand.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TE="$ROOT/app/tracktion_engine"

if [ ! -d "$TE/modules" ]; then
  echo "[engine-patches] no vendored engine at $TE — clone it first (see CLAUDE.md build recipe)" >&2
  exit 0
fi

applied=0 skipped=0

# 0001 — signalsmith timestretch backend (SPEC V46 warp v2). Marker = the enum value.
if grep -q "signalsmith = 15" "$TE/modules/tracktion_engine/timestretch/tracktion_TimeStretch.h" 2>/dev/null; then
  skipped=$((skipped+1))
else
  git -C "$TE" apply "$ROOT/app/patches/0001-signalsmith-timestretch.patch" 2>/dev/null \
    || patch -p1 -N -d "$TE" < "$ROOT/app/patches/0001-signalsmith-timestretch.patch"
  applied=$((applied+1))
fi

# 0002 — THE SEAL (docs/THE_PHYSICS.md E1): SOTADAW_RENDER_EPOCH pins the BWAV
# origination stamp so renders hash stable. Marker = the env-var name in the file.
if grep -q "SOTADAW_RENDER_EPOCH" "$TE/modules/tracktion_engine/audio_files/tracktion_AudioFileUtils.cpp" 2>/dev/null; then
  skipped=$((skipped+1))
else
  git -C "$TE" apply "$ROOT/app/patches/0002-render-epoch-seal.patch" 2>/dev/null \
    || patch -p1 -N -d "$TE" < "$ROOT/app/patches/0002-render-epoch-seal.patch"
  applied=$((applied+1))
fi

echo "[engine-patches] applied=$applied skipped=$skipped"
