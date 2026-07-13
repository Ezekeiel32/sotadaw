#!/bin/bash
# PUBLIC PAYLOAD STAGER — the ONE source of truth for what ships to strangers.
#   tools/stage_payload.sh <dest_dir>
# Used by make_appimage.sh + make_deb.sh (+ future win/mac packagers) so the
# public-safety rules can never drift between installers.
#
# LAWS (2026-07-12 public-release lane):
#  - kits/: FACTORY WHITELIST ONLY. kits/ also holds stems separated from
#    imported copyrighted songs + Chezy's personal material — those NEVER ship.
#  - songs/: demo_track.json only.
#  - tools/: dev-channel scripts (tailnet updater/log-uplink) NEVER ship.
#  - agent/ipc, __pycache__, caches: stripped.
#  - library.json ships EMPTY (index is per-user; index_library.py rebuilds).
#  - CREDITS + THIRD_PARTY_LICENSES ship in the payload root.
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT=$(pwd)
DEST="${1:?usage: stage_payload.sh <dest_dir>}"

FACTORY_KITS=(choir epiano gm_drums lg_house_chops piano pluckbass sota_bass sota_drums sota_keys strings warmpad)
EXCLUDE_TOOLS=(get_latest.sh publish_transfer.sh first_run_check.sh send_logs.sh log_stream.sh build_focal.sh export_public_src.sh build_public_linux.sh)

rm -rf "$DEST"
mkdir -p "$DEST" "$DEST/songs" "$DEST/library/presets" "$DEST/kits"

# code payload
for d in skills agent instruments tools; do cp -r "$d" "$DEST/"; done
rm -rf "$DEST/agent/__pycache__" "$DEST/agent/ipc" "$DEST/tools/__pycache__" \
       "$DEST/tools/focal" "$DEST/skills/__pycache__" 2>/dev/null || true
for t in "${EXCLUDE_TOOLS[@]}"; do rm -f "$DEST/tools/$t"; done
find "$DEST" -name "*.pyc" -delete
find "$DEST" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# SECRETS NEVER SHIP (2026-07-13): `cp -r` copies dotfiles, and key-material
# lives dot-named — strip every hidden file wholesale; nothing shipped is
# dot-named by design.
find "$DEST" -name '.*' -type f -delete

# the voice-bank hint inside sing.py points at the dev tailnet — replace for public builds
sed -i 's|Install:  cd ~/AI_SOTA_DAW && curl -C - -O http://100\.107\.177\.113:8877/voices.tar.gz|Install: see the Voices section of the SOTA DAW site (bank is a separate, non-commercial-licensed download)|' \
  "$DEST/tools/sing.py" 2>/dev/null || true
# sidecar's log-uplink default carries the dev-box address — public builds get
# an empty default (SOTADAW_NO_UPLINK=1 rides every public launcher regardless)
sed -i 's|os.environ.get("SOTADAW_UPLINK", "http://100\.107\.177\.113:8878")|os.environ.get("SOTADAW_UPLINK", "")|' \
  "$DEST/agent/sidecar.py"

# factory kits ONLY
for k in "${FACTORY_KITS[@]}"; do
  [ -d "kits/$k" ] && cp -r "kits/$k" "$DEST/kits/" || echo "[stage] WARN missing factory kit $k"
done

# minimal user-facing data
cp songs/demo_track.json "$DEST/songs/" 2>/dev/null || true
cp library/grooves.json "$DEST/library/" 2>/dev/null || true
echo '{"samples": [], "kits": [], "instruments": [], "vsts": []}' > "$DEST/library.json"

# version stamp (workspace refresh key on upgrades)
GITSHA=$(git rev-parse --short HEAD 2>/dev/null || echo unknown)
echo "0.9.0-beta ($(date +%Y-%m-%d) g$GITSHA)" > "$DEST/VERSION"

cat > "$DEST/CREDITS.md" <<'CRED'
# SOTA DAW — Credits & Attributions

**Engine**: JUCE (juce.com) and Tracktion Engine (tracktion.com) — see
THIRD_PARTY_LICENSES.md. Faust (faust.grame.fr) compiles every instrument;
new instruments JIT-compile via libfaust's interpreter backend (GRAME, GPLv2).

**Factory sample kits** (piano, e-piano, strings, choir, warm pad, pluck bass,
GM drums): rendered from the GeneralUser GS SoundFont by S. Christian Collins
(schristiancollins.com) — thank you. sota_* kits and lg_house_chops are
first-party, synthesized by SOTA DAW's own engine.

**Time-stretch**: SoundTouch (LGPL, Olli Parviainen) and Signalsmith Stretch
(MIT, Geraint Luff). **Sync**: Ableton Link (GPLv3, Ableton AG).

**The Voice** (optional, separate download): DiffSinger community models with
the "Gahata Meiji" bank from the LUNAI Project — NON-COMMERCIAL license,
attribution required: "Gahata Meiji from LUNAI Project". The app stamps this
attribution into exported C2PA manifests automatically.

**The producer-agent** is bring-your-own-key: install Anthropic's `claude` CLI
(or set an OpenRouter key) — no account is bundled, nothing phones home.
CRED

cat > "$DEST/THIRD_PARTY_LICENSES.md" <<'LIC'
# Third-party components and licenses

| Component | License | Notes |
|---|---|---|
| JUCE 8 | AGPLv3 (free tier) | UI + plugin hosting framework |
| Tracktion Engine | GPLv3 (free tier) | audio engine (edit graph, render) |
| Faust + libfaust | GPLv2+ | DSP compiler; interpreter JIT at runtime |
| LLVM 17 | Apache-2.0 WITH LLVM-exception | dependency of libfaust |
| SoundTouch | LGPL-2.1 | tempo warp (vendored in Tracktion) |
| Signalsmith Stretch | MIT | live retune (fx_retune) |
| Ableton Link | GPLv3 | tempo sync (vendored) |
| GeneralUser GS | GeneralUser GS License v2.0 | factory kit source samples |
| ICU, libxml2, libedit, zlib, ... | various permissive | via system/bundled libs |

SOTA DAW's own source (arrangements, agent, tools, Faust instruments) is
(c) its author. This beta build is distributed free of charge. Where GPL/AGPL
components are statically or dynamically combined, the corresponding-source
obligations of those licenses apply to distribution — source is available on
request through the site while the public repository is being prepared.
LIC

# AUDIT GATE (same law as export_public_src.sh): a surviving secret-shape or
# private marker FAILS the stage — installers can only pack what passes.
# (bracketed chars: patterns must match targets but never THIS file's own text —
#  this script ships in the payload AND rides the git export, whose audit greps it)
LEAKS=$(grep -RInE --exclude=stage_payload.sh "sk-ant-[A-Za-z0-9_-]{8}|sk-or-[A-Za-z0-9_-]{8}|ghp_[A-Za-z0-9]{20}|github_pa[t]_|AKIA[0-9A-Z]{16}|BEGIN (RSA|EC|OPENSSH) PRIVATE|100\.10[7]\.|100\.11[7]\.|recep[t]orcb1|chezy[@]|hezy-Inspiro[n]|chezy-lo[q]" "$DEST" 2>/dev/null || true)
if [ -n "$LEAKS" ]; then
  echo "$LEAKS" | head -5
  echo "[stage] FATAL: private markers in payload — refusing to stage"; exit 1
fi

echo "[stage] payload staged at $DEST ($(du -sh "$DEST" | cut -f1))"
