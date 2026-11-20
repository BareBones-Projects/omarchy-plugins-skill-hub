# // OMARCHY SKILL HUB
**BareBones Projects | Designed by Justin Levesque-Welsch**

Monochrome local-first manager for AI skills on Arch Linux / Omarchy. v0.2.0 provides a native Omarchy Quattro bar-widget with a separate Python local backend. It does not modify the shell theme, Waybar config, or user data.

## Install on Omarchy Quattro
The marketplace install only clones shell plugin code; it **does not run install hooks**. First install the widget:

```bash
omarchy plugin add https://github.com/BareBones-Projects/omarchy-plugins-skill-hub.git --enable
```

Then install the local backend from the checkout:

```bash
bash ~/.config/omarchy/plugins/barebones.skill-hub/bin/install.sh
```

The right-side **[ SKILLS ]** bar widget opens http://127.0.0.1:8765/. You may also open the desktop launcher **Omarchy Skill Hub**.

## Functions
- Search and create Markdown skills; enable/disable, delete and assign them to all or selected supported agents.
- Explicit sync to per-user Codex, Claude, OpenCode and Gemini skill folders. Unmanaged skills are never overwritten.
- Ollama, OpenAI and Anthropic chat tab. Configure provider in the app.
- Chromium extension in `extension/` supports selected-text review through browser context menu. Load unpacked manually.
- Clipboard desktop shortcut requires wl-clipboard or xclip.

## Validate
```bash
omarchy plugin validate ~/.config/omarchy/plugins/barebones.skill-hub
systemctl --user status omarchy-skill-hub.service
curl --fail http://127.0.0.1:8765/api/status
python -m unittest discover -s tests -v
```
Marketplace validation and a live Quattro bar-click test must run on an Omarchy machine. CI tests the Python code, installer in an isolated HOME, JSON manifest and shell scripts; it cannot claim real desktop testing.

## Remove
```bash
bash ~/.config/omarchy/plugins/barebones.skill-hub/bin/uninstall.sh
omarchy plugin remove barebones.skill-hub
```
These commands preserve application data, your provider secrets, and installed agent skills.

## Provider keys
Put `OPENAI_API_KEY=...` or `ANTHROPIC_API_KEY=...` in `~/.config/omarchy-skill-hub/provider.env`, run `chmod 600` on it, and restart the user service. Ollama needs a separately running model.

## Safety
The backend only listens on 127.0.0.1:8765. This isn't a remote ChatGPT-to-local filesystem bridge, and same-user local processes can reach it. Agent assignments require explicit sync and agent restart may be necessary. Never treat marketplace listing or static checks as a security audit. Read the source before enabling an unsandboxed shell plugin.

License: MIT.
