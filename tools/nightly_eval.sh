#!/bin/bash
# Nightly musicality CI: run N genre briefs through the real agent, machine-check,
# refresh the trend page. Costs real API money (~$2-3.5/brief on opus) — pick your N.
# Install (Chezy's call, not auto-installed):
#   crontab -e   ->   0 4 * * * /home/chezy/AI_SOTA_DAW/tools/nightly_eval.sh trap phonk techno
cd "$(dirname "$0")/.."
GENRES=${@:-"trap phonk techno"}
for g in $GENRES; do
  .venv/bin/python tools/eval_daw.py --brief "$g" >> eval/nightly.log 2>&1
done
.venv/bin/python tools/eval_trend.py >> eval/nightly.log 2>&1
