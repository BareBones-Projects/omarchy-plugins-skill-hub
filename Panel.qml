// BareBones Projects, Designed by: Justin Levesque-Welsch
// Native, theme-aware Quickshell popup. Uses bounded local CLI processes.
import QtQuick
import QtQuick.Controls
import Quickshell
import Quickshell.Io
import qs.Commons as Commons
import qs.Ui

Panel {
    id: root
    moduleName: "barebones.skill-hub"
    manageIpc: false
    property var anchorItem: null
    property var hostWidget: null
    property string section: "skills"
    property var skills: []
    property var servers: []
    property var agents: ["All", "Codex", "Claude Code", "OpenCode", "Gemini CLI"]
    property string provider: "ollama"
    property string model: "llama3.2"
    property string theme: "auto"
    property string feedback: "Ready"
    property string chatReply: ""
    property bool busy: false
    property string lastAction: ""
    property string pendingPayload: ""
    readonly property string bridge: Quickshell.env("HOME") + "/.local/bin/omarchy-skill-hubctl"
    readonly property color ink: Commons.Color.foreground
    readonly property color paper: Commons.Color.background

    function open() { root.controller.show(); refresh() }
    function close() { root.controller.hide() }
    function switchPanel(direction) {
        if (root.bar && typeof root.bar.switchPanelFrom === "function")
            return root.bar.switchPanelFrom(root.hostWidget || root, direction)
        return false
    }
    function request(args) {
        if (busy) return
        busy = true
        lastAction = args[0]
        root.feedback = "Working..."
        pendingPayload = JSON.stringify({"args": args})
        cli.command = [bridge, "rpc"]
        cli.running = true
    }
    function refresh() { request(["skills"]) }
    function handleResult(code) {
        busy = false
        if (code !== 0) { feedback = "Command failed. Check ~/.config/omarchy-skill-hub/ and journal logs."; return }
        var data
        try { data = JSON.parse(collector.text || "{}") }
        catch (error) { feedback = "Invalid backend response"; return }
        if (data.skills) skills = data.skills
        if (data.servers) servers = data.servers
        if (data.agents) agents = ["All"].concat(data.agents)
        if (data.provider) provider = data.provider
        if (data.model) model = data.model
        if (data.config) theme = data.config.theme || "auto"
        if (data.reply !== undefined) chatReply = String(data.reply).slice(0, 8000)
        if (data.error) feedback = data.error
        else feedback = "Ready"
        if (lastAction === "mcp-add") Qt.callLater(function() { root.request(["mcp"]) })
        else if (lastAction === "provider-set" || lastAction === "config-set") Qt.callLater(function() { root.request(["status"]) })
        else if (section === "skills" && !data.skills && !data.agents && !data.config) Qt.callLater(refresh)
    }
    onSectionChanged: {
        if (!opened) return
        if (section === "skills") request(["skills"])
        else if (section === "mcp") request(["mcp"])
        else request(["status"])
    }
    Process {
        id: cli
        stdinEnabled: true
        onStarted: cli.write(root.pendingPayload + "\n")
        stdout: StdioCollector { id: collector; waitForEnd: true }
        onExited: function(code) { root.handleResult(code) }
    }
    KeyboardPanel {
        id: popup
        anchorItem: root.anchorItem
        owner: root.hostWidget || root
        bar: root.bar
        open: root.opened
        focusTarget: popup.loadedContent
        contentWidth: popup.fittedContentWidth(Commons.Style.space(365))
        contentHeight: popup.fittedContentHeight(popup.loadedContent ? popup.loadedContent.contentHeightHint : Commons.Style.space(340))
        content: PanelKeyCatcher {
            id: catcher
            property alias contentHeightHint: content.implicitHeight
            anchors.fill: parent
            onCloseRequested: root.close()
            onTabRequested: function(direction) { root.switchPanel(direction) }
            Column {
                id: content
                width: parent.width
                spacing: 11
                Text {
                    text: "// OMARCHY SKILL HUB"
                    color: root.ink
                    textFormat: Text.PlainText
                    font.family: "monospace"
                    font.bold: true
                    font.pixelSize: 14
                }
                Row {
                    spacing: 5
                    Repeater {
                        model: ["skills", "mcp", "ai", "config"]
                        delegate: Rectangle {
                            required property string modelData
                            width: 77
                            height: 28
                            color: root.section === modelData ? root.ink : "transparent"
                            border.color: root.ink
                            border.width: 1
                            Text {
                                anchors.centerIn: parent
                                text: modelData.toUpperCase()
                                font.family: "monospace"
                                font.pixelSize: 11
                                color: root.section === modelData ? root.paper : root.ink
                            }
                            MouseArea { anchors.fill: parent; onClicked: root.section = modelData }
                        }
                    }
                }
                Rectangle { width: parent.width; height: 1; color: root.ink; opacity: 0.6 }
                Flickable {
                    id: scroller
                    width: parent.width
                    height: Math.min(420, workspace.implicitHeight + 8)
                    contentHeight: workspace.implicitHeight
                    clip: true
                    boundsBehavior: Flickable.StopAtBounds
                    Column {
                        id: workspace
                        width: parent.width
                        spacing: 9
                        // Skills: active list, quick search, agent assignment and explicit sync.
                        Column {
                            width: parent.width
                            spacing: 7
                            visible: root.section === "skills"
                            Row {
                                spacing: 8
                                Rectangle {
                                    width: 254; height: 30; color: "transparent"; border.color: root.ink
                                    TextInput { id: searchBox; anchors.fill: parent; anchors.margins: 7; color: root.ink; font.pixelSize: 12; clip: true }
                                }
                                Button { text: "SEARCH"; onClicked: root.refresh() }
                            }
                            Repeater {
                                model: root.skills.filter(function(s) { return String(s.title).toLowerCase().indexOf(searchBox.text.toLowerCase()) >= 0 })
                                delegate: Column {
                                    required property var modelData
                                    width: workspace.width
                                    spacing: 4
                                    Row {
                                        width: parent.width; spacing: 8
                                        Text { width: 240; text: modelData.title; color: root.ink; textFormat: Text.PlainText; elide: Text.ElideRight; font.pixelSize: 12 }
                                        Button { text: modelData.enabled ? "●" : "○"; onClicked: root.request(["toggle", modelData.id, modelData.enabled ? "false" : "true"]) }
                                    }
                                    Row {
                                        spacing: 6
                                        Text { text: "Agent"; color: root.ink; font.pixelSize: 11 }
                                        ComboBox {
                                            width: 190; model: root.agents
                                            currentIndex: Math.max(0, root.agents.indexOf(modelData.agents[0] || "All"))
                                            onActivated: function(index) { root.request(["assign", modelData.id, root.agents[index]]) }
                                        }
                                    }
                                    Rectangle { width: workspace.width; height: 1; color: root.ink; opacity: 0.35 }
                                }
                            }
                            Text { text: "NEW SKILL"; color: root.ink; font.bold: true; font.pixelSize: 12 }
                            TextField { id: skillTitle; width: parent.width; placeholderText: "Skill name"; maximumLength: 64 }
                            TextArea { id: skillContent; width: parent.width; height: 74; placeholderText: "Skill instructions (plain text)"; wrapMode: TextEdit.Wrap; textFormat: TextEdit.PlainText }
                            Row {
                                spacing: 8
                                Button { text: "CREATE"; enabled: skillTitle.text.length > 0 && skillContent.text.length > 0; onClicked: root.request(["create", skillTitle.text, skillContent.text, "All"]) }
                                Button { text: "SYNC TO AGENTS"; onClicked: root.request(["sync", "--confirm"]) }
                            }
                        }
                        // MCP catalog: configuration only. No arbitrary process execution from the UI.
                        Column {
                            width: parent.width; spacing: 8; visible: root.section === "mcp"
                            Text { text: "MCP CONNECTIONS"; color: root.ink; font.bold: true; font.pixelSize: 12 }
                            Repeater {
                                model: root.servers
                                delegate: Text {
                                    required property var modelData
                                    text: "○ " + modelData.name + "  [" + modelData.type + "]"
                                    color: root.ink; textFormat: Text.PlainText; font.family: "monospace"; font.pixelSize: 11
                                }
                            }
                            TextField { id: mcpName; width: parent.width; placeholderText: "MCP server name" }
                            ComboBox { id: mcpType; width: parent.width; model: ["stdio", "streamable-http"] }
                            TextField { id: mcpTarget; width: parent.width; placeholderText: mcpType.currentIndex === 0 ? "/absolute/path/to/server" : "https://example.com/mcp" }
                            Button { text: "SAVE MCP CONFIG"; onClicked: root.request(["mcp-add", mcpName.text, mcpType.currentText, mcpTarget.text]) }
                            Text { width: parent.width; text: "MCP entries are saved locally. Agent-side MCP activation is a separate, explicit setup step."; wrapMode: Text.WordWrap; color: root.ink; opacity: 0.75; font.pixelSize: 10 }
                        }
                        Column {
                            width: parent.width; spacing: 8; visible: root.section === "ai"
                            Text { text: "SYSTEM AI / DEFAULT PROVIDER"; color: root.ink; font.bold: true; font.pixelSize: 12 }
                            Text { text: root.provider + " / " + root.model; color: root.ink; textFormat: Text.PlainText; font.pixelSize: 11 }
                            TextArea { id: chatInput; width: parent.width; height: 86; placeholderText: "Message your configured provider"; wrapMode: TextEdit.Wrap; textFormat: TextEdit.PlainText }
                            Button { text: "SEND"; enabled: chatInput.text.length > 0 && !root.busy; onClicked: root.request(["chat", chatInput.text]) }
                            Text { width: parent.width; text: root.chatReply; color: root.ink; textFormat: Text.PlainText; wrapMode: Text.WordWrap; font.pixelSize: 11 }
                        }
                        Column {
                            width: parent.width; spacing: 8; visible: root.section === "config"
                            Text { text: "SYSTEM CONFIG"; color: root.ink; font.bold: true; font.pixelSize: 12 }
                            Text { text: "Theme is inherited from Omarchy's active color palette."; color: root.ink; wrapMode: Text.WordWrap; font.pixelSize: 11 }
                            Text { text: "Theme: AUTO (Omarchy palette)"; color: root.ink; font.pixelSize: 11 }
                            ComboBox { id: providerPicker; model: ["ollama", "openai", "anthropic"]; currentIndex: Math.max(0, model.indexOf(root.provider)) }
                            TextField { id: modelName; width: parent.width; text: root.model; placeholderText: "Model name" }
                            Button { text: "SAVE DEFAULT AI"; onClicked: root.request(["provider-set", providerPicker.currentText, modelName.text]) }
                            Text { text: "Settings: ~/.config/omarchy-skill-hub/config.json\nMCP: ~/.config/omarchy-skill-hub/mcp.json\nAPI keys: provider.env (mode 600)"; color: root.ink; font.pixelSize: 10 }
                        }
                    }
                }
                Text { text: root.feedback; color: root.ink; textFormat: Text.PlainText; opacity: 0.75; font.pixelSize: 10; wrapMode: Text.WordWrap; width: parent.width }
            }
        }
    }
}
