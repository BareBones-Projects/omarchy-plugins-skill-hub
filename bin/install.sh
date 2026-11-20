#!/usr/bin/env bash
# BareBones Projects, Designed by: Justin Levesque-Welsch
set -euo pipefail
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOME_CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}"
HOME_DATA="${XDG_DATA_HOME:-$HOME/.local/share}"
DEST="$HOME_DATA/omarchy-skill-hub/runtime"
UNIT_DIR="$HOME_CONFIG/systemd/user"
BIN_DIR="$HOME/.local/bin"
mkdir -p "$DEST" "$UNIT_DIR" "$HOME_DATA/applications" "$BIN_DIR" "$HOME_CONFIG/omarchy-skill-hub"
cp -R "$SRC/app" "$SRC/web" "$DEST/"
install -m755 "$SRC/bin/omarchy-skill-hub" "$BIN_DIR/omarchy-skill-hub"
cat > "$UNIT_DIR/omarchy-skill-hub.service" <<EOT
[Unit]
Description=BareBones Omarchy Skill Hub (loopback only)
After=network.target
[Service]
Type=simple
WorkingDirectory=$DEST
ExecStart=/usr/bin/python -m app.server
EnvironmentFile=-$HOME_CONFIG/omarchy-skill-hub/provider.env
Restart=on-failure
NoNewPrivileges=true
ProtectSystem=strict
[Install]
WantedBy=default.target
EOT
cat > "$HOME_DATA/applications/omarchy-skill-hub.desktop" <<EOT
[Desktop Entry]
Type=Application
Name=Omarchy Skill Hub
Comment=Manage and assign local AI skills
Exec=$BIN_DIR/omarchy-skill-hub
Icon=applications-development
Terminal=false
Categories=Development;Utility;
Actions=Clipboard;
[Desktop Action Clipboard]
Name=Create Skill from Clipboard
Exec=$BIN_DIR/omarchy-skill-hub --clipboard
EOT
systemctl --user daemon-reload
systemctl --user enable --now omarchy-skill-hub.service
printf '\nBackend installed at %s\nWeb UI: http://127.0.0.1:8765/\n' "$DEST"
printf 'Omarchy Quattro widget: run omarchy plugin add <repository-url> --enable\n'
