import QtQuick

Rectangle {
    id: root

    property string message: ""
    visible: false
    width: Math.min(parent.width - 40, contentRow.implicitWidth + 34)
    height: 48
    radius: 14
    color: "#252f40"
    border.color: "#4a586f"
    border.width: 1
    z: 100

    function show(text) {
        message = text
        visible = true
        hideTimer.restart()
    }

    Row {
        id: contentRow
        anchors.centerIn: parent
        spacing: 10
        Rectangle { width: 8; height: 8; radius: 4; color: "#8d7dff"; anchors.verticalCenter: parent.verticalCenter }
        Text {
            id: messageText
            text: root.message
            color: "#f0f3f9"
            font.pixelSize: 12
        }
    }

    Timer {
        id: hideTimer
        interval: 3200
        onTriggered: root.visible = false
    }
}
