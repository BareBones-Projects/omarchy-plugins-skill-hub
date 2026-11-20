// BareBones Projects, Designed by: Justin Levesque-Welsch
import QtQuick
import qs.Commons as Commons

Item {
    id: skillHub
    implicitWidth: label.implicitWidth + 22
    implicitHeight: 30
    Accessible.name: "Open Skill Hub"
    Accessible.role: Accessible.Button
    Rectangle {
        anchors.fill: parent
        radius: 0
        color: input.containsMouse ? Commons.Color.foreground : "transparent"
        border.width: 1
        border.color: Commons.Color.foreground
    }
    Text {
        id: label
        anchors.centerIn: parent
        text: "[ SKILLS ]"
        font.family: "monospace"
        font.pixelSize: 11
        font.bold: true
        color: input.containsMouse ? Commons.Color.background : Commons.Color.foreground
    }
    MouseArea {
        id: input
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: Qt.openUrlExternally("http://127.0.0.1:8765/")
    }
}
