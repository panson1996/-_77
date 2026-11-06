import QtQuick

Rectangle {
    id: root

    property string initialText: ""
    property color platformColor: "#8172f5"
    property int badgeSize: 38

    width: badgeSize
    height: badgeSize
    radius: Math.max(10, badgeSize * 0.31)
    color: "transparent"
    border.width: 1
    border.color: Qt.rgba(platformColor.r, platformColor.g, platformColor.b, 0.24)
    gradient: Gradient {
        GradientStop { position: 0.0; color: Qt.rgba(root.platformColor.r, root.platformColor.g, root.platformColor.b, 0.23) }
        GradientStop { position: 1.0; color: Qt.rgba(root.platformColor.r, root.platformColor.g, root.platformColor.b, 0.08) }
    }

    Text {
        anchors.centerIn: parent
        text: root.initialText
        color: root.platformColor
        font.pixelSize: root.badgeSize * 0.39
        font.weight: Font.DemiBold
    }
}
