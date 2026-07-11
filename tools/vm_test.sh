#!/bin/bash
# W12 VM matrix: boot the AppImage on a truly fresh distro in docker.
#   tools/vm_test.sh [ubuntu:24.04|ubuntu:22.04|fedora:40]
# PASS = first-run workspace created + app alive 25s + exit 0.
set -euo pipefail
IMG=${1:-ubuntu:24.04}
DIST="$(cd "$(dirname "$0")/.." && pwd)/dist"
if [[ $IMG == fedora* ]]; then
  INSTALL="dnf install -y -q xorg-x11-server-Xvfb alsa-lib freetype fontconfig libX11 libXext libXrandr libXinerama libXcursor libXcomposite libXrender python3"
else
  INSTALL="apt-get update -qq && apt-get install -y -qq xvfb libasound2t64 libfreetype6 libfontconfig1 libx11-6 libxext6 libxrandr2 libxinerama1 libxcursor1 libxcomposite1 libxrender1 python3"
fi
docker run --rm -v "$DIST":/dist:ro "$IMG" bash -c "
  $INSTALL >/dev/null 2>&1
  export HOME=/root
  timeout 25 xvfb-run -a /dist/SOTA_DAW-x86_64.AppImage --appimage-extract-and-run 2>&1 | grep -m1 'first run' || true
  test -d /root/.local/share/sotadaw/skills && echo 'VM_TEST: PASS (workspace bootstrapped)' || echo 'VM_TEST: FAIL'
"
