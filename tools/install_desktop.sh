#!/bin/bash
# Install SOTA DAW into the Linux desktop app menu (XDG) so it launches from the
# launcher / dock / app grid -- no more typing ~/AI_SOTA_DAW/sotadaw.
#
# Points at the LIVE repo launcher (tools/sotadaw_launcher.sh via the `sotadaw`
# symlink), NOT the frozen dist/ AppImage: clicking the icon always runs the
# binary you last built. The launcher cd's to the repo root, so the app finds
# songs/ agent/ skills/ library/ and streams its output to agent/ipc/app.log.
#
# Idempotent -- safe to re-run (e.g. after get_latest.sh moves the checkout, or
# to repair the entry). Installs into the per-user XDG dirs (no sudo).
set -euo pipefail

REPO="$(cd "$(dirname "$(readlink -f "$0")")/.." && pwd)"
APPS="$HOME/.local/share/applications"
ICONS="$HOME/.local/share/icons/hicolor/256x256/apps"
LAUNCHER="$REPO/sotadaw"
BIN="$REPO/app/build/sotadaw_artefacts/Release/SOTA DAW"
ICON_SRC="$REPO/dist/AppDir/sotadaw.png"
DESK="$APPS/sotadaw.desktop"

mkdir -p "$APPS" "$ICONS"

# icon into the hicolor theme -> resolved by name (Icon=sotadaw), DE picks size
if [ -f "$ICON_SRC" ]; then
    cp -f "$ICON_SRC" "$ICONS/sotadaw.png"
else
    echo "[install_desktop] WARN: icon missing ($ICON_SRC) -- entry will use a fallback glyph" >&2
fi

# StartupWMClass MUST match the app's live WM_CLASS or the running window shows
# as a separate generic dock icon instead of grouping under this launcher.
# Verified from the running window: WM_CLASS = "SOTA DAW".
cat > "$DESK" <<DESKTOP
[Desktop Entry]
Type=Application
Version=1.0
Name=SOTA DAW
GenericName=AI Music Studio
Comment=The AI-native DAW - agent-composed, fully editable, no black boxes
Exec=$LAUNCHER
TryExec=$BIN
Icon=sotadaw
Terminal=false
Categories=AudioVideo;Audio;
Keywords=DAW;music;audio;AI;producer;studio;MIDI;
StartupNotify=true
StartupWMClass=SOTA DAW
DESKTOP
chmod +x "$DESK" 2>/dev/null || true

# refresh the menu + icon caches (best-effort; harmless if the tools are absent)
update-desktop-database "$APPS" 2>/dev/null || true
gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" 2>/dev/null || true

if command -v desktop-file-validate >/dev/null 2>&1; then
    if desktop-file-validate "$DESK"; then
        echo "[install_desktop] valid: $DESK"
    else
        echo "[install_desktop] desktop-file-validate reported issues (see above)" >&2
    fi
fi

echo "[install_desktop] DONE."
echo "  -> Open your app menu / Activities and search 'SOTA DAW'."
echo "  -> Right-click the running icon -> 'Add to Favorites' to pin it to the dock."
echo "  -> Re-run this script any time to repair the entry."
