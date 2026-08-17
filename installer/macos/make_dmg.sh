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
# live-JIT stdlib (CI drops the faust dist at ./faustdist; absent = no-op)
[ -d faustdist/share/faust ] && cp -R faustdist/share/faust "$APP/Contents/Resources/faustlibs" || true

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
# THE GUI PATH LAW (2026-08-17, Chezy: "the cc login no work on mac, only codex"):
# Finder/launchd hands an app PATH=/usr/bin:/bin:/usr/sbin:/sbin, and this wrapper
# is a NON-LOGIN bash — it never reads the user's .zprofile/.zshrc either. Every
# CLI the producer shells out to (claude, codex, git, node) lives outside that
# PATH, so a Mac with everything installed still read as "nothing installed".
export PATH="$HOME/.local/bin:$HOME/.claude/local:/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:$HOME/.bun/bin:$PATH"
WS="${SOTADAW_ROOT:-$HOME/Library/Application Support/sotadaw}"
PAY="$HERE/../Resources/sotadaw-payload"
if [ ! -d "$WS" ]; then
  mkdir -p "$WS"; cp -R "$PAY/." "$WS/"; mkdir -p "$WS/songs" "$WS/app"
  export SOTADAW_FIRST_RUN=1
fi
if [ -d "$HERE/../Resources/faustlibs" ]; then
  export SOTADAW_FAUST_LIB_PATH="$HERE/../Resources/faustlibs"
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

# signature: Developer ID when CI carries the cert (docs/SIGNING.md secrets),
# else deterministic ad-hoc (Apple Silicon requires at least ad-hoc; linker-
# applied ones don't cover our added launcher/payload)
if [ -n "${MAC_SIGN_ID:-}" ]; then
  codesign -s "$MAC_SIGN_ID" --force --deep --options runtime --timestamp "$APP"
  codesign --verify --deep --strict "$APP"
else
  codesign -s - --force --deep "$APP" 2>/dev/null || true
fi

# THE DMG IS THE MANUAL (2026-08-17, Chezy's Sequoia hit the "Not Opened" wall):
# an unsigned beta's first-open lives or dies on the instructions BESIDE the app.
# Volume = app + /Applications drag target + first-open steps for BOTH Gatekeeper
# generations (Sequoia killed right-click->Open for unnotarized apps).
DMGROOT=dist/dmgroot
rm -rf "$DMGROOT"; mkdir -p "$DMGROOT"
cp -R "$APP" "$DMGROOT/"
ln -s /Applications "$DMGROOT/Applications"
cat > "$DMGROOT/READ ME FIRST.txt" <<'RDME'
SOTA DAW — first open on macOS (unsigned beta)

1) Drag "SOTA DAW" onto the Applications folder icon beside it.

2) Open it once from Applications. macOS will say it
   "could not verify SOTA DAW" — click Done (not the bin!).

3) macOS 15 (Sequoia) and newer:
      System Settings -> Privacy & Security -> scroll down ->
      next to "SOTA DAW was blocked" click  Open Anyway  -> Open.
   macOS 13/14 (Ventura/Sonoma):
      right-click "SOTA DAW" in Applications -> Open -> Open.

   Terminal shortcut (either version), if you prefer:
      xattr -d com.apple.quarantine "/Applications/SOTA DAW.app"

This is Apple's standard wall for beta apps that are not yet
notarized ($99/yr Apple Developer ID — on the roadmap). The app
runs fully offline; every download's SHA-256 is published at
https://sotadaw.netlify.app so you can verify what you got.
RDME

# CI runners race deep-codesign vs dmg creation ("Resource busy") — settle + retry
for i in 1 2 3 4 5; do
  if hdiutil create -volname "SOTA DAW" -srcfolder "$DMGROOT" -ov -format UDZO dist/SOTA_DAW-macOS.dmg; then
    break
  fi
  [ "$i" = 5 ] && exit 1
  sleep 8
done

# notarization (no-op until the SIGNING.md secrets exist): submit + staple, so
# the first run after Chezy buys the Developer ID ships a clean-opening DMG
if [ -n "${MAC_SIGN_ID:-}" ] && [ -n "${APPLE_ID:-}" ] && [ -n "${APPLE_TEAM_ID:-}" ] && [ -n "${APPLE_APP_PASS:-}" ]; then
  xcrun notarytool submit dist/SOTA_DAW-macOS.dmg \
    --apple-id "$APPLE_ID" --team-id "$APPLE_TEAM_ID" --password "$APPLE_APP_PASS" --wait
  xcrun stapler staple dist/SOTA_DAW-macOS.dmg
fi
shasum -a 256 dist/SOTA_DAW-macOS.dmg | tee dist/SOTA_DAW-macOS.dmg.sha256
