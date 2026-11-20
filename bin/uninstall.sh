#!/usr/bin/env bash
# BareBones Projects, Designed by: Justin Levesque-Welsch
set -euo pipefail
HOME_CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}"
HOME_DATA="${XDG_DATA_HOME:-$HOME/.local/share}"
if command -v systemctl >/dev/null; then
  systemctl --user disable --now omarchy-skill-hub.service >/dev/null 2>&1 || true
fi
rm -f "$HOME_CONFIG/systemd/user/omarchy-skill-hub.service" \
  "$HOME_DATA/applications/omarchy-skill-hub.desktop" \
  "$HOME/.local/bin/omarchy-skill-hub" \
  "$HOME/.local/bin/omarchy-skill-hubctl" \
  "$HOME_DATA/icons/hicolor/scalable/apps/omarchy-skill-hub.svg"
systemctl --user daemon-reload
printf 'Backend service and launcher removed. Data, keys and agent skills retained.\n'
printf 'To remove the separate Omarchy widget: omarchy plugin remove barebones.skill-hub\n'
