# // Omarchy Skill Hub

**BareBones Projects, Designed by: Justin Levesque-Welsch**

Local-first skill manager for **Arch Linux / Omarchy (Hyprland)**. Skills appear in a searchable list with a green/red status dot on the right. Create skills from text, choose an agent or all agents, sync with explicit confirmation, and chat with a configured AI provider.

## Features

- Searchable skill inventory, individual enable/disable toggle with green/red dot, skill deletion, agent assignment dropdown, and copy/paste skill creation.
- Explicit sync into `~/.claude/skills`, `~/.agents/skills` (Codex), `~/.config/opencode/skills`, and `~/.gemini/skills`. Existing unmanaged files are never overwritten.
- Browser right-click on selected text: install the unpacked Chromium MV3 extension from `extension/` via `chrome://extensions` > Developer mode > Load unpacked. It opens a review editor; it does not automatically execute or save selected content. Firefox requires separate WebExtension packaging.
- Desktop launcher action **Create Skill from Clipboard**. Requires `wl-paste` (install `wl-clipboard`) or `xclip`. This is a clipboard-based system action, not a universal right-click menu installed across every Linux desktop application.
- AI Chat tab for local Ollama (`http://127.0.0.1:11434`) or API providers OpenAI/Anthropic. Configure provider and model in Settings.
- Ready for custom Waybar/Omarchy panel entries: run `omarchy-skill-hub` as the command for a clickable launcher. Waybar changes are **not** applied automatically.

## API credentials

For OpenAI or Anthropic API access, create `~/.config/omarchy-skill-hub/provider.env` containing `OPENAI_API_KEY=...` or `ANTHROPIC_API_KEY=...` and run:

```bash
chmod 600 ~/.config/omarchy-skill-hub/provider.env
systemctl --user restart omarchy-skill-hub.service
```

This file is never included in the archive. Ollama requires a separately running local Ollama instance with the selected model installed.

## Security and limitations

- Local HTTP service binds only to `127.0.0.1:8765`. No remote access or external server is provided. Other same-user processes can access the loopback API; do not run this on an untrusted multi-user desktop.
- Sync prompts for explicit approval, only overwrites hub-owned `SKILL.md` files, and does not grant arbitrary system-root access. **System-wide** here means assigning across all configured per-user agents, not installing to `/usr/share` or every program on the OS.
- Provider requests send chat text to the selected provider. Browser-selected text is inserted in an editor for review.
- Supported agents may need restart or manual refresh to load new skills. Assignment does not verify agent activation.
- Omarchy menu bar / Waybar launcher integration is manual and depends on your current config; the .desktop app appears in standard application launchers.
- Not a ChatGPT web-to-local filesystem bridge. The private ChatGPT plugin bundles workflow guidance, while the desktop app performs local file operations.

## Development

```bash
python -m unittest discover -s tests -v
python -m app.server
```

Remove service and launcher with `bash bin/uninstall.sh`. App data, installed agent skills, and keys are retained intentionally.

## License

MIT. Copyright (c) 2026 BareBones Projects. Designed by: Justin Levesque-Welsch.
