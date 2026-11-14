#!/usr/bin/env bash
# BareBones Projects, Designed by: Justin Levesque-Welsch
set -euo pipefail
systemctl --user disable --now omarchy-skill-hub.service || true
rm -f "$HOME/.config/systemd/user/omarchy-skill-hub.service" "$HOME/.local/share/applications/omarchy-skill-hub.desktop" "$HOME/.local/bin/omarchy-skill-hub"
systemctl --user daemon-reload
printf 'Launcher and service removed. Skill database, runtime and installed agent skills retained for safety.\n'
