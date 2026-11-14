---
name: omarchy-skill-hub
description: Use when organizing, authoring, assigning, or deploying reusable AI skills across local Omarchy Linux agents through Omarchy Skill Hub.
---

# Omarchy Skill Hub

This plugin documents the local Omarchy Skill Hub application. The desktop service must be installed separately using `bin/install.sh` from the project ZIP. Do not claim the ChatGPT web plugin can directly read or modify local machine files.

## Workflow
1. Launch `Omarchy Skill Hub` from the Hyprland/Omarchy application launcher or open `http://127.0.0.1:8765` locally.
2. Use **Create Skill** to paste Markdown or plain text, set a name, and assign it to All or one supported agent.
3. Use the status toggle (green enabled, red disabled) to configure intended skill state.
4. Review the targets, then press **Sync assignments to agents** and confirm. The app does not overwrite unmanaged skills.
5. To create from selected browser text, install the included browser extension and right-click selected text. Review before saving.
6. To create from system clipboard, launch the desktop action **Create Skill from Clipboard**.
7. Configure an Ollama, OpenAI, or Anthropic default provider in settings and open **AI Chat**.

## Safety
Never copy secrets into skill instructions. Sync only user-approved agent paths. Agent capability is dependent on whether that agent supports the skill directory format; a successful file copy is not proof the agent has loaded it. API provider keys are placed in an external local `provider.env` and must never be added to Git.
