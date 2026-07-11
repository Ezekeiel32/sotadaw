#!/usr/bin/env bash
# THE GATE WRAPPER (2026-07-11): run a heavy command ONLY when the user's
# session is idle. Born from a self-caught slip — an "it's small" e2e ran
# ungated beside a live 14-min take (the exact habit that caused the
# original meter-timeout incident). Prefix EVERY render/e2e/battery with
# this; the law becomes mechanical instead of willpower.
#
#   tools/gated.sh python3 tools/ghost_e2e.py 1
#
# Exit 3 = refused (user LIVE). Otherwise exec's the command.
#
# THE GATE READS THE REAL IPC, ALWAYS (2026-07-11 #5): a sandboxed rig
# exports SOTADAW_IPC for its own isolation — inheriting it here makes the
# gate read the RIG's events (a probe's own make_track chatter scored as
# "user LIVE" and stopped its own run). The user's session lives in
# agent/ipc, full stop; the wrapped command still gets the caller's env.
cd "$(dirname "$0")/.."
if SOTADAW_IPC="$PWD/agent/ipc" python3 tools/user_live.py; then
  echo "gated: user LIVE - refusing: $*" >&2
  exit 3
fi
exec "$@"
