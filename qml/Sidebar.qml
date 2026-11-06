import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "components"

Rectangle {
    id: root

    property string currentPlatform: "all"
    signal platformSelected(string platform)
    signal addRequested()

    color: "#0f141f"
    border.color: "#232c3b"
    border.width: 1
    gradient: Gradient {
        GradientStop { position: 0.0; color: "#131a28" }
        GradientStop { position: 1.0; color: "#0d121c" }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 18
        spacing: 16

        RowLayout {
            Layout.fillWidth: true
            Layout.topMargin: 5
            Layout.bottomMargin: 5
            spacing: 12

            Rectangle {
                width: 44
                height: 44
                radius: 15
                border.width: 1
                border.color: "#9b8fff"
                gradient: Gradient {
                    GradientStop { position: 0.0; color: "#9586ff" }
                    GradientStop { position: 1.0; color: "#5846d1" }
                }
                Text {
                    anchors.centerIn: parent
                    text: "M"
                    color: "white"
                    font.pixelSize: 21
                    font.weight: Font.Bold
                }
            }

            Column {
                spacing: 3
                Text { text: "矩阵运营台"; color: "#f5f7fb"; font.pixelSize: 18; font.weight: Font.DemiBold }
                Text { text: "MATRIX WORKSPACE"; color: "#6f7d94"; font.pixelSize: 8; font.letterSpacing: 1.4 }
            }
        }

        AppButton {
            text: "添加账号"
            iconText: "＋"
            variant: "primary"
            implicitHeight: 42
            Layout.fillWidth: true
            onClicked: root.addRequested()
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.topMargin: 6
            Text { text: "工作空间"; color: "#718096"; font.pixelSize: 11; font.weight: Font.Medium; Layout.fillWidth: true }
            Rectangle { Layout.preferredWidth: 38; Layout.preferredHeight: 1; color: "#283244" }
        }

        Column {
            Layout.fillWidth: true
            spacing: 6

            Repeater {
                model: [
                    { key: "all", name: "全部账号", initial: "全", color: "#97a5bb" },
                    { key: "douyin", name: "抖音", initial: "抖", color: "#ff5470" },
                    { key: "channels", name: "微信视频号", initial: "视", color: "#2bd58a" },
                    { key: "xingtu", name: "巨量星图", initial: "星", color: "#9a8bff" }
                ]

                delegate: Rectangle {
                    required property var modelData
                    width: parent.width
                    height: 46
                    radius: 12
                    color: root.currentPlatform === modelData.key ? "#273146" : (navMouse.containsMouse ? "#1b2433" : "transparent")
                    border.width: root.currentPlatform === modelData.key ? 1 : 0
                    border.color: "#3b4760"

                    Rectangle {
                        visible: root.currentPlatform === modelData.key
                        width: 3
                        height: 20
                        radius: 2
                        color: "#9181ff"
                        anchors.left: parent.left
                        anchors.verticalCenter: parent.verticalCenter
                    }

                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: 11
                        anchors.rightMargin: 10
                        spacing: 11

                        PlatformBadge {
                            initialText: modelData.initial
                            platformColor: modelData.color
                            badgeSize: 29
                        }
                        Text {
                            text: modelData.name
                            color: root.currentPlatform === modelData.key ? "#f3f5fa" : "#aab5c6"
                            font.pixelSize: 13
                            font.weight: root.currentPlatform === modelData.key ? Font.Medium : Font.Normal
                            Layout.fillWidth: true
                        }
                        Rectangle {
                            width: 26
                            height: 22
                            radius: 7
                            color: root.currentPlatform === modelData.key ? "#37435b" : "#1b2331"
                            Text {
                                anchors.centerIn: parent
                                text: controller.platformCounts[modelData.key] || 0
                                color: root.currentPlatform === modelData.key ? "#c8d2e2" : "#728096"
                                font.pixelSize: 10
                            }
                        }
                    }

                    MouseArea {
                        id: navMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: root.platformSelected(modelData.key)
                    }

                    Behavior on color { ColorAnimation { duration: 140 } }
                }
            }
        }

        Item { Layout.fillHeight: true }

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 112
            radius: 15
            color: "#161f2d"
            border.color: "#2b374a"
            border.width: 1

            Column {
                anchors.fill: parent
                anchors.margins: 14
                spacing: 9
                Row {
                    spacing: 9
                    Rectangle {
                        width: 25
                        height: 25
                        radius: 8
                        color: "#173b35"
                        Text { anchors.centerIn: parent; text: "✓"; color: "#55d9ae"; font.pixelSize: 13; font.weight: Font.Bold }
                    }
                    Text { text: "本地安全运行"; color: "#d5deea"; font.pixelSize: 12; font.weight: Font.Medium; anchors.verticalCenter: parent.verticalCenter }
                }
                Text {
                    width: parent.width
                    text: "账号会话独立保存在本机，业务数据库不记录平台密码。"
                    color: "#7e8da3"
                    font.pixelSize: 11
                    wrapMode: Text.WordWrap
                    lineHeight: 1.3
                }
            }
        }

        Text {
            text: "企业内部版  ·  v0.1.0"
            color: "#536176"
            font.pixelSize: 10
            Layout.alignment: Qt.AlignHCenter
        }
    }
}
