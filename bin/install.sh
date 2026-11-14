#!/usr/bin/env bash
# BareBones Projects, Designed by: Justin Levesque-Welsch
set -euo pipefail
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="${XDG_DATA_HOME:-$HOME/.local/share}/omarchy-skill-hub/runtime"
mkdir -p "$DEST" "$HOME/.config/systemd/user" "$HOME/.local/share/applications" "$HOME/.local/bin" "$HOME/.config/omarchy-skill-hub"
cp -r "$SRC/app" "$SRC/web" "$DEST/"
install -m755 "$SRC/bin/omarchy-skill-hub" "$HOME/.local/bin/omarchy-skill-hub"
cat > "$HOME/.config/systemd/user/omarchy-skill-hub.service" <<EOF
[Unit]
Description=Omarchy Skill Hub local service
After=network.target
[Service]
Type=simple
WorkingDirectory=$DEST
ExecStart=/usr/bin/python -m app.server
EnvironmentFile=-%h/.config/omarchy-skill-hub/provider.env
Restart=on-failure
NoNewPrivileges=true
ProtectSystem=strict
[Install]
WantedBy=default.target
EOF
cat > "$HOME/.local/share/applications/omarchy-skill-hub.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Omarchy Skill Hub
Comment=Manage AI agent skills
Exec=$HOME/.local/bin/omarchy-skill-hub
Icon=applications-development
Terminal=false
Categories=Development;Utility;
Actions=Clipboard;
[Desktop Action Clipboard]
Name=Create Skill from Clipboard
Exec=$HOME/.local/bin/omarchy-skill-hub --clipboard
EOF
systemctl --user daemon-reload
systemctl --user enable --now omarchy-skill-hub.service
printf '\nInstalled. Launch via app launcher: Omarchy Skill Hub\nOr open http://127.0.0.1:8765/\nFor provider keys, write ~/.config/omarchy-skill-hub/provider.env (chmod 600) and restart service.\n'
