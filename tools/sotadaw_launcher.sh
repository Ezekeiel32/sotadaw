#!/bin/bash
# App launcher: every run's FULL output (JUCE, engine, crashes) lands in
# agent/ipc/app.log — fresh per launch, streamed to the dev box by
# log_stream.sh. The `sotadaw` symlink at repo root points here (get_latest.sh
# maintains that), so launching the app and capturing its truth are the same act.
cd "$(dirname "$(readlink -f "$0")")/.." || exit 1
mkdir -p agent/ipc
# THE LAST WORDS LAW (2026-07-13): `>` used to truncate the PREVIOUS run's log
# at every launch — an abort's `terminate called ... what(): ...` was the ONLY
# evidence for the 21:16 Jul-12 crash (SIGABRT leaves no kernel segfault line),
# and the relaunch destroyed it. One generation survives as app.log.1.
[ -s agent/ipc/app.log ] && mv -f agent/ipc/app.log agent/ipc/app.log.1
# THE CRASH PIN (2026-07-13): every rebuild links a NEW exe inode — the 21:16
# Jul-12 crash was unsymbolizable because its binary was (deleted) hours before
# anyone read app_crash.log (its maps prove it). Pin THIS launch's exact image
# by hardlink (zero bytes while the path still holds it; the data outlives any
# rebuild). tools/crash_symbolize.py resolves app_crash.log's ino/size/mtime
# stamps against these pins. Keep the 3 newest.
exe="./app/build/sotadaw_artefacts/Release/SOTA DAW"
pins="agent/ipc/.crash_pins"
if [ -f "$exe" ]; then
  mkdir -p "$pins"
  key="$(stat -c '%i_%s_%Y' "$exe" 2>/dev/null)"
  if [ -n "$key" ] && [ ! -e "$pins/$key" ]; then
    ln "$exe" "$pins/$key" 2>/dev/null || cp "$exe" "$pins/$key" 2>/dev/null
    ls -t "$pins" 2>/dev/null | tail -n +4 | while IFS= read -r old; do
      rm -f -- "$pins/$old"
    done
  fi
fi
exec "$exe" "$@" > agent/ipc/app.log 2>&1
