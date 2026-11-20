---
name: omarchy-skill-hub
description: Use when installing, configuring or troubleshooting the native Omarchy Quattro Skill Hub dropdown and its local AI skills, MCP catalog, system AI provider, or app menu integration.
---

# Omarchy Skill Hub v0.3.1

This package is a **local** Quickshell `bar-widget` for the Omarchy Quattro desktop. It does not provide browser-to-machine remote control. Install the plugin with `omarchy plugin add <GitHub repository> --enable`, then run `bash ~/.config/omarchy/plugins/barebones.skill-hub/bin/install.sh` locally to install its Python CLI bridge and desktop application icon.

Click `[ SKILLS ]` in the bar or select **Omarchy Skill Hub** from the application menu. A native anchored dropdown contains **SKILLS**, **MCP**, **AI**, and **CONFIG**. The panel uses Omarchy's active theme colors through `Commons.Color`. No browser opens.

The MCP tab manages a local catalog in `~/.config/omarchy-skill-hub/mcp.json`. It does not automatically register connections with external agents or execute unreviewed MCP servers. The System AI tab connects to the provider and model configured in local settings. For cloud providers, API keys must live in a `chmod 600` file at `~/.config/omarchy-skill-hub/provider.env`.

To validate on Omarchy, run `omarchy plugin validate ~/.config/omarchy/plugins/barebones.skill-hub`, `qmllint -I "$OMARCHY_PATH/shell" ~/.config/omarchy/plugins/barebones.skill-hub/{BarWidget,Panel}.qml`, and `omarchy-shell shell summon barebones.skill-hub '{}'`.

Core tests run offline with `python -m unittest discover -s tests -v`. Actual Quickshell rendering and marketplace approval require an Omarchy environment.
