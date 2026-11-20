# // OMARCHY SKILL HUB v0.3.1

**BareBones Projects • Designed by Justin Levesque-Welsch**

Native popup for **Omarchy Quattro** (Quickshell) with Skills, MCP, System AI, and Configuration. Clicking `[ SKILLS ]` in the Omarchy bar opens a `KeyboardPanel` anchored beneath the bar. **No browser launch or localhost web service is needed.** The App Menu includes the matching monochrome SVG icon and desktop entry.

## Install from the review branch

Until PR #2 is merged, install using the `release/quattro-skill-hub-v0.2.0` branch only after it has been updated with this version. Alternatively, download the v0.3.1 ZIP, unpack it, and invoke the local installer below.

```bash
omarchy plugin add https://github.com/BareBones-Projects/omarchy-plugins-skill-hub.git --enable
bash ~/.config/omarchy/plugins/barebones.skill-hub/bin/install.sh
omarchy plugin validate ~/.config/omarchy/plugins/barebones.skill-hub
omarchy-shell shell summon barebones.skill-hub '{}'
```

Omarchy plugins **do not execute installers automatically**. The separate `install.sh` copies the local Python backend and the `.desktop` entry into user-owned paths. The plugin alone provides the bar UI; the backend adds CLI operations. No root access, browser, embedded web server, global AI config overwrite, or standalone Quickshell process is used.

## Native popup tabs

- **SKILLS:** Search/filter, create skill, toggle active state, assign to Codex/Claude Code/OpenCode/Gemini CLI or All, and explicitly sync to agent folders. Unmanaged SKILL.md files are never overwritten.
- **MCP:** Display manually configured MCP servers and add stdio or HTTPS MCP server definitions to the Skill Hub catalog. **Saving a catalog entry does not start a server or register it with an agent.** MCP activation in each agent is a separate step.
- **AI:** Chat with the configured Ollama, OpenAI or Anthropic model. Cloud providers send text to their selected APIs. API credentials aren't shown in the UI.
- **CONFIG:** Auto-adapt to Omarchy's active `Commons.Color` theme, and configure the default AI provider and model. Only Omarchy theme colors are rendered, avoiding global shell theme modifications.

## File layout

| Path | Purpose |
| --- | --- |
| `~/.config/omarchy/plugins/barebones.skill-hub/` | Native Quattro plugin (managed by `omarchy plugin`) |
| `~/.local/share/omarchy-skill-hub/runtime/app/` | Installed local Python logic |
| `~/.local/bin/omarchy-skill-hub` | App Menu command to summon Quickshell panel |
| `~/.local/bin/omarchy-skill-hubctl` | Local CLI bridge for panel actions |
| `~/.local/share/applications/omarchy-skill-hub.desktop` | Omarchy apps launcher |
| `~/.local/share/icons/hicolor/scalable/apps/omarchy-skill-hub.svg` | Black/white launcher icon |
| `~/.config/omarchy-skill-hub/config.json` | Local theme/provider preference |
| `~/.config/omarchy-skill-hub/mcp.json` | Skill Hub MCP catalog (mode 0600) |
| `~/.config/omarchy-skill-hub/provider.env` | API keys; **chmod 600** |
| `~/.local/share/omarchy-skill-hub/skills.sqlite3` | User skills and assignments |

For provider API keys, create the file manually:

```bash
mkdir -p ~/.config/omarchy-skill-hub
chmod 700 ~/.config/omarchy-skill-hub
printf 'OPENAI_API_KEY=your-api-key\n' > ~/.config/omarchy-skill-hub/provider.env
chmod 600 ~/.config/omarchy-skill-hub/provider.env
```

Do not commit credentials. Local Ollama requires a running Ollama service and a pulled model.

## Testing

```bash
python -m unittest discover -s tests -v
bash -n bin/*.sh bin/omarchy-skill-hub bin/omarchy-skill-hubctl
python -m compileall -q app
omarchy plugin validate ~/.config/omarchy/plugins/barebones.skill-hub
qmllint -I "$OMARCHY_PATH/shell" BarWidget.qml Panel.qml
```

The first three commands can run in ordinary Linux CI. The last two require **Omarchy Quattro** and its imports. Test opening and closing via bar clicks, Escape, `omarchy-shell shell summon`, and app-menu launcher before publication.

## Uninstall

```bash
bash ~/.config/omarchy/plugins/barebones.skill-hub/bin/uninstall.sh
omarchy plugin remove barebones.skill-hub
```

User skills, config, MCP catalog, and API secrets are intentionally retained. The legacy localhost web service is disabled and its user unit removed by the uninstaller, if present.

**License:** MIT.
