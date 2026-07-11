#!/bin/bash
# App launcher: every run's FULL output (JUCE, engine, crashes) lands in
# agent/ipc/app.log — fresh per launch, streamed to the dev box by
# log_stream.sh. The `sotadaw` symlink at repo root points here (get_latest.sh
# maintains that), so launching the app and capturing its truth are the same act.
cd "$(dirname "$(readlink -f "$0")")/.." || exit 1
mkdir -p agent/ipc
exec "./app/build/sotadaw_artefacts/Release/SOTA DAW" "$@" > agent/ipc/app.log 2>&1
