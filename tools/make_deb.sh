#!/bin/bash
# PUBLIC .deb PACKAGER (2026-07-12): the standard Ubuntu install path —
# double-click in App Center (GUI wizard) or `sudo apt install ./sotadaw_*.deb`.
# Engine lives in /opt/sotadaw; each user gets a bootstrapped workspace at
# ~/.local/share/sotadaw on first launch (Time-Machine git repo included).
# Payload: tools/stage_payload.sh (public-safety whitelist).
#   tools/make_deb.sh -> dist/sotadaw_<ver>_amd64.deb (+ .sha256)
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT=$(pwd)
# containerized public builds point these at the focal build tree + a writable out
DIST="${SOTADAW_DIST:-$ROOT/dist}"
BUILD="${SOTADAW_BUILD:-$ROOT/app/build}"
FAUSTLIBS="${SOTADAW_FAUSTLIBS:-}"   # faust stdlib dir -> /opt/sotadaw/faustlibs (JIT)
VER="0.9.0+$(date +%Y%m%d)"
PKG=$DIST/debroot
rm -rf "$PKG"
mkdir -p "$PKG/DEBIAN" "$PKG/opt/sotadaw/bin" "$PKG/usr/bin" \
         "$PKG/usr/share/applications" "$PKG/usr/share/icons/hicolor/256x256/apps" \
         "$PKG/usr/share/doc/sotadaw"

# engine binaries
cp "$BUILD/sotadaw_artefacts/Release/SOTA DAW" "$PKG/opt/sotadaw/bin/sotadaw"
cp "$BUILD/m1_artefacts/Release/m1" "$PKG/opt/sotadaw/bin/m1"
strip "$PKG/opt/sotadaw/bin/sotadaw" "$PKG/opt/sotadaw/bin/m1" 2>/dev/null || true

# payload (public-safe)
tools/stage_payload.sh "$PKG/opt/sotadaw/payload"
cp "$PKG/opt/sotadaw/payload/THIRD_PARTY_LICENSES.md" "$PKG/usr/share/doc/sotadaw/copyright"

# faust stdlib for the JIT (libfaust itself is STATIC inside the binaries —
# no libfaust package dependency on any distro)
if [ -n "$FAUSTLIBS" ] && [ -d "$FAUSTLIBS" ]; then
  mkdir -p "$PKG/opt/sotadaw/faustlibs"
  cp -r "$FAUSTLIBS/." "$PKG/opt/sotadaw/faustlibs/"
fi

# per-user launcher: bootstrap workspace, keep engine payload fresh on upgrades
cat > "$PKG/usr/bin/sotadaw" <<'LAUNCH'
#!/bin/bash
set -u
ENGINE=/opt/sotadaw
PAY="$ENGINE/payload"
export SOTADAW_NO_UPLINK=1   # public build: no dev-box log uplink
export SOTADAW_FAUST_LIB_PATH="${SOTADAW_FAUST_LIB_PATH:-$ENGINE/faustlibs}"   # JIT stdlib
WS="${SOTADAW_ROOT:-${XDG_DATA_HOME:-$HOME/.local/share}/sotadaw}"
if [ ! -d "$WS" ]; then
  echo "[sotadaw] first run: creating workspace at $WS"
  mkdir -p "$WS"
  cp -r "$PAY/." "$WS/"
  mkdir -p "$WS/songs" "$WS/app"
  export SOTADAW_FIRST_RUN=1
elif ! cmp -s "$PAY/VERSION" "$WS/VERSION" 2>/dev/null; then
  echo "[sotadaw] upgrade: refreshing engine payload (your songs/library kept)"
  for d in skills agent instruments tools kits; do
    rm -rf "$WS/$d.new"; cp -r "$PAY/$d" "$WS/$d.new" && rm -rf "$WS/$d" && mv "$WS/$d.new" "$WS/$d"
  done
  cp -f "$PAY/VERSION" "$PAY/CREDITS.md" "$PAY/THIRD_PARTY_LICENSES.md" "$WS/" 2>/dev/null || true
fi
# Time Machine: accepted takes are git commits — make sure the workspace is a repo
if command -v git >/dev/null && [ ! -d "$WS/.git" ]; then
  git -C "$WS" init -q 2>/dev/null && \
  git -C "$WS" config user.name "SOTA DAW" && \
  git -C "$WS" config user.email "sotadaw@localhost" && \
  git -C "$WS" add -A 2>/dev/null && \
  git -C "$WS" commit -qm "workspace born" 2>/dev/null || true
fi
# engine binary reachable at the workspace-conventional path — a SHIM, not a
# symlink, so agent-spawned m1 also inherits the JIT stdlib path
mkdir -p "$WS/app/build/m1_artefacts/Release"
cat > "$WS/app/build/m1_artefacts/Release/m1" <<'M1SHIM'
#!/bin/bash
export SOTADAW_FAUST_LIB_PATH="${SOTADAW_FAUST_LIB_PATH:-/opt/sotadaw/faustlibs}"
exec /opt/sotadaw/bin/m1 "$@"
M1SHIM
chmod +x "$WS/app/build/m1_artefacts/Release/m1"
export SOTADAW_ROOT="$WS"
exec "$ENGINE/bin/sotadaw" "$@"
LAUNCH
chmod 755 "$PKG/usr/bin/sotadaw"

cat > "$PKG/usr/share/applications/sotadaw.desktop" <<'DESK'
[Desktop Entry]
Type=Application
Name=SOTA DAW
GenericName=Digital Audio Workstation
Comment=The AI-native DAW - agent-composed, fully editable, no black boxes
Exec=/usr/bin/sotadaw
Icon=sotadaw
Categories=AudioVideo;Audio;Music;
Keywords=DAW;music;audio;AI;producer;
Terminal=false
DESK

cp "$ROOT/app/icon.png" "$PKG/usr/share/icons/hicolor/256x256/apps/sotadaw.png" 2>/dev/null \
  || { command -v convert >/dev/null && convert -size 256x256 xc:'#15161a' \
  -fill '#e8b84b' -font DejaVu-Sans-Bold -pointsize 130 -gravity center -annotate +0-8 'S' \
  -fill '#9aa0a8' -pointsize 22 -annotate +0+78 'SOTA DAW' \
  "$PKG/usr/share/icons/hicolor/256x256/apps/sotadaw.png"; } || true

SIZE_KB=$(du -sk "$PKG" --exclude=DEBIAN | cut -f1)
cat > "$PKG/DEBIAN/control" <<CTRL
Package: sotadaw
Version: $VER
Section: sound
Priority: optional
Architecture: amd64
Installed-Size: $SIZE_KB
Depends: libasound2t64 | libasound2, libfontconfig1, libfreetype6, libcurl4t64 | libcurl4, libx11-6, libxext6, libxrandr2, libxinerama1, libxcursor1, libxcomposite1, libxrender1, python3, git
Recommends: python3-venv, fonts-dejavu-core
Maintainer: SOTA DAW <sotadaw@localhost>
Homepage: https://sotadaw.netlify.app
Description: AI-native digital audio workstation
 The agent authors both the arrangement and the instruments themselves
 (as Faust DSP code) - no black-box audio generation. Everything the AI
 makes is symbolic, inspectable, diffable. Works fully offline as a
 classic DAW; bring your own Anthropic/OpenRouter key for the producer
 agent. Ubuntu 20.04+ and equivalents (amd64).
CTRL

cat > "$PKG/DEBIAN/postinst" <<'POST'
#!/bin/sh
set -e
command -v update-desktop-database >/dev/null && update-desktop-database -q /usr/share/applications || true
command -v gtk-update-icon-cache >/dev/null && gtk-update-icon-cache -q /usr/share/icons/hicolor || true
exit 0
POST
chmod 755 "$PKG/DEBIAN/postinst"

OUT="$DIST/sotadaw_${VER}_amd64.deb"
dpkg-deb --build --root-owner-group -Zxz "$PKG" "$OUT" > /dev/null
sha256sum "$OUT" | tee "$OUT.sha256"
ls -lh "$OUT"
