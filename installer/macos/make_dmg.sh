#!/bin/bash
# SOTA DAW — macOS .app + DMG assembler (SCAFFOLD, 2026-07-12: never yet run —
# the mac binary does not exist until the CI macos job goes green).
# Unsigned: users right-click > Open on first launch. Proper path: codesign
# with a Developer ID + notarytool (needs Apple ID secrets in CI).
set -euo pipefail
cd "$(dirname "$0")/../.."
ROOT=$(pwd)
APP=dist/SOTA\ DAW.app
rm -rf "$APP" dist/SOTA_DAW-macOS.dmg
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"

# JUCE cmake usually emits the .app itself — prefer it if present
BUILT_APP=$(ls -d app/build/sotadaw_artefacts/Release/*.app 2>/dev/null | head -1 || true)
if [ -n "$BUILT_APP" ]; then
  rm -rf "$APP"
  cp -R "$BUILT_APP" "$APP"
else
  cp "app/build/sotadaw_artefacts/Release/SOTA DAW" "$APP/Contents/MacOS/SOTA DAW"
fi
cp app/build/m1_artefacts/Release/m1 "$APP/Contents/MacOS/m1" 2>/dev/null || true

tools/stage_payload.sh "$APP/Contents/Resources/sotadaw-payload"

cat > "$APP/Contents/Info.plist" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>CFBundleName</key><string>SOTA DAW</string>
  <key>CFBundleIdentifier</key><string>audio.sotadaw.app</string>
  <key>CFBundleVersion</key><string>0.9.0</string>
  <key>CFBundleExecutable</key><string>sotadaw-launch</string>
  <key>NSMicrophoneUsageDescription</key><string>Audio recording</string>
  <key>NSHighResolutionCapable</key><true/>
</dict></plist>
PLIST

# workspace-bootstrap wrapper (mirrors the proven Linux launchers)
cat > "$APP/Contents/MacOS/sotadaw-launch" <<'WRAP'
#!/bin/bash
HERE=$(cd "$(dirname "$0")" && pwd)
export SOTADAW_NO_UPLINK=1
WS="${SOTADAW_ROOT:-$HOME/Library/Application Support/sotadaw}"
PAY="$HERE/../Resources/sotadaw-payload"
if [ ! -d "$WS" ]; then
  mkdir -p "$WS"; cp -R "$PAY/." "$WS/"; mkdir -p "$WS/songs" "$WS/app"
  export SOTADAW_FIRST_RUN=1
fi
if command -v git >/dev/null && [ ! -d "$WS/.git" ]; then
  git -C "$WS" init -q && git -C "$WS" config user.name "SOTA DAW" && \
  git -C "$WS" config user.email "sotadaw@localhost" && \
  git -C "$WS" add -A && git -C "$WS" commit -qm "workspace born" || true
fi
mkdir -p "$WS/app/build/m1_artefacts/Release"
ln -sf "$HERE/m1" "$WS/app/build/m1_artefacts/Release/m1"
export SOTADAW_ROOT="$WS"
exec "$HERE/SOTA DAW" "$@"
WRAP
chmod +x "$APP/Contents/MacOS/sotadaw-launch"

hdiutil create -volname "SOTA DAW" -srcfolder "$APP" -ov -format UDZO dist/SOTA_DAW-macOS.dmg
shasum -a 256 dist/SOTA_DAW-macOS.dmg | tee dist/SOTA_DAW-macOS.dmg.sha256
