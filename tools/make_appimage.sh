#!/bin/bash
# W5 SHIP IT (v2, public-release lane 2026-07-12): package SOTA DAW as a
# PORTABLE AppImage — bundles libfaust/LLVM/ICU etc so a clean machine needs
# NO packages beyond a desktop (X11, ALSA, fontconfig, glibc >= 2.38) + python3
# for the agent tools. Payload comes from tools/stage_payload.sh (public-safety
# whitelist — factory kits only, no dev-channel scripts).
#   tools/make_appimage.sh -> dist/SOTA_DAW-x86_64.AppImage (+ .sha256)
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT=$(pwd)
DIST=$ROOT/dist
APPDIR=$DIST/AppDir
rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/bin" "$APPDIR/usr/lib" "$APPDIR/usr/share/sotadaw-payload"

# binaries (the app artefact has a space in its name; ship it as plain 'sotadaw')
cp "app/build/sotadaw_artefacts/Release/SOTA DAW" "$APPDIR/usr/bin/sotadaw"
cp app/build/m1_artefacts/Release/m1 "$APPDIR/usr/bin/"
strip "$APPDIR/usr/bin/sotadaw" "$APPDIR/usr/bin/m1" 2>/dev/null || true

# ---- bundle shared libs: full ldd closure MINUS the base-system set ----------
# Kept on system: glibc family + C++ runtime (floor: Ubuntu 24.04-era), ALSA
# (device configs are system property), fontconfig (config lives in /etc/fonts).
EXCLUDE_RE='^(linux-vdso|ld-linux|libc\.so|libm\.so|libstdc\+\+|libgcc_s|libasound|libfontconfig)'
for bin in "$APPDIR/usr/bin/sotadaw" "$APPDIR/usr/bin/m1"; do
  ldd "$bin" | awk '/=>/ {print $1" "$3}' | while read -r name path; do
    [ -f "$path" ] || continue
    base=$(basename "$name")
    if ! echo "$base" | grep -qE "$EXCLUDE_RE"; then
      cp -n "$path" "$APPDIR/usr/lib/$base" 2>/dev/null || true
    fi
  done
done
echo "[appimage] bundled libs: $(ls "$APPDIR/usr/lib" | wc -l) ($(du -sh "$APPDIR/usr/lib" | cut -f1))"

# ---- workspace payload (the user's editable home — copied out on first run) --
tools/stage_payload.sh "$APPDIR/usr/share/sotadaw-payload"

cat > "$APPDIR/AppRun" <<'RUN'
#!/bin/bash
HERE=$(dirname "$(readlink -f "$0")")
export LD_LIBRARY_PATH="$HERE/usr/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export SOTADAW_NO_UPLINK=1   # public build: no dev-box log uplink
WS="${SOTADAW_ROOT:-${XDG_DATA_HOME:-$HOME/.local/share}/sotadaw}"
PAY="$HERE/usr/share/sotadaw-payload"
if [ ! -d "$WS" ]; then
  echo "[sotadaw] first run: creating workspace at $WS"
  mkdir -p "$WS"
  cp -r "$PAY/." "$WS/"
  mkdir -p "$WS/songs" "$WS/app"
  export SOTADAW_FIRST_RUN=1
elif ! cmp -s "$PAY/VERSION" "$WS/VERSION" 2>/dev/null; then
  echo "[sotadaw] upgrade: refreshing engine payload (songs/library kept)"
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
# m1 must run with the AppImage's bundled libs: regenerate the workspace shim
# each launch (the squashfs mount path changes per run).
mkdir -p "$WS/app/build/m1_artefacts/Release"
cat > "$WS/app/build/m1_artefacts/Release/m1" <<SHIM
#!/bin/bash
export LD_LIBRARY_PATH="$HERE/usr/lib\${LD_LIBRARY_PATH:+:\$LD_LIBRARY_PATH}"
exec "$HERE/usr/bin/m1" "\$@"
SHIM
chmod +x "$WS/app/build/m1_artefacts/Release/m1"
export SOTADAW_ROOT="$WS"
exec "$HERE/usr/bin/sotadaw" "$@"
RUN
chmod +x "$APPDIR/AppRun"

cat > "$APPDIR/sotadaw.desktop" <<'DESK'
[Desktop Entry]
Type=Application
Name=SOTA DAW
Comment=The AI-native DAW - agent-composed, fully editable, no black boxes
Exec=sotadaw
Icon=sotadaw
Categories=AudioVideo;Audio;
Terminal=false
DESK

command -v convert >/dev/null && convert -size 256x256 xc:'#15161a' \
  -fill '#e8b84b' -font DejaVu-Sans-Bold -pointsize 130 -gravity center -annotate +0-8 'S' \
  -fill '#9aa0a8' -pointsize 22 -annotate +0+78 'SOTA DAW' "$APPDIR/sotadaw.png" \
  || cp app/icon.png "$APPDIR/sotadaw.png" 2>/dev/null || true

# appimagetool (cached in dist/)
AIT=$DIST/appimagetool-x86_64.AppImage
if [ ! -x "$AIT" ]; then
  curl -sL -o "$AIT" \
    "https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage"
  chmod +x "$AIT"
fi
ARCH=x86_64 "$AIT" --appimage-extract-and-run --comp zstd "$APPDIR" "$DIST/SOTA_DAW-x86_64.AppImage" 2>&1 | tail -2
sha256sum "$DIST/SOTA_DAW-x86_64.AppImage" | tee "$DIST/SOTA_DAW-x86_64.AppImage.sha256"
ls -lh "$DIST/SOTA_DAW-x86_64.AppImage"
