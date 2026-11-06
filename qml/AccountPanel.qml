import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "components"

Rectangle {
    id: root

    property string platform: "all"
    property string currentAccountId: ""
    signal accountSelected(string accountId)

    color: "#111823"
    border.color: "#253043"
    border.width: 1
    gradient: Gradient {
        GradientStop { position: 0.0; color: "#141c29" }
        GradientStop { position: 1.0; color: "#101722" }
    }

    function applyFilter() {
        controller.setFilter(root.platform, searchField.text)
    }

    function focusSearch() {
        forceActiveFocus()
        searchField.forceActiveFocus()
        searchField.selectAll()
    }

    onPlatformChanged: applyFilter()

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 18
        spacing: 14

        ColumnLayout {
            Layout.fillWidth: true
            Layout.topMargin: 3
            spacing: 5
            Text { text: "账号管理"; color: "#f2f5fa"; font.pixelSize: 20; font.weight: Font.DemiBold }
            Text { text: "选择账号，进入对应运营平台"; color: "#74839a"; font.pixelSize: 11 }
        }

        TextField {
            id: searchField
            Layout.fillWidth: true
            Layout.topMargin: 4
            implicitHeight: 42
            placeholderText: "搜索账号备注或昵称…"
            color: "#e4eaf3"
            placeholderTextColor: "#68778e"
            font.pixelSize: 12
            leftPadding: 38
            rightPadding: 13
            selectByMouse: true
            onTextChanged: root.applyFilter()
            background: Rectangle {
                radius: 12
                color: searchField.activeFocus ? "#1e2838" : "#192230"
                border.color: searchField.activeFocus ? "#8172f5" : "#2c384b"
                border.width: 1
                Behavior on border.color { ColorAnimation { duration: 140 } }
            }
            Item {
                width: 16
                height: 16
                anchors.left: parent.left
                anchors.leftMargin: 13
                anchors.verticalCenter: parent.verticalCenter
                Rectangle {
                    width: 10
                    height: 10
                    radius: 5
                    color: "transparent"
                    border.color: "#8291a8"
                    border.width: 1.5
                    anchors.left: parent.left
                    anchors.top: parent.top
                }
                Rectangle {
                    width: 6
                    height: 2
                    radius: 1
                    color: "#8291a8"
                    rotation: 45
                    anchors.right: parent.right
                    anchors.bottom: parent.bottom
                    anchors.rightMargin: 1
                    anchors.bottomMargin: 2
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.topMargin: 2
            Text { text: "账号列表"; color: "#8c9bb1"; font.pixelSize: 11; font.weight: Font.Medium; Layout.fillWidth: true }
            Rectangle {
                width: 30
                height: 23
                radius: 8
                color: "#222d3e"
                Text { anchors.centerIn: parent; text: accountList.count; color: "#a8b6ca"; font.pixelSize: 10; font.weight: Font.Medium }
            }
        }

        ListView {
            id: accountList
            Layout.fillWidth: true
            Layout.fillHeight: true
            model: accountModel
            clip: true
            spacing: 9
            boundsBehavior: Flickable.StopAtBounds
            ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }

            delegate: Rectangle {
                width: ListView.view.width
                height: 86
                radius: 14
                color: root.currentAccountId === accountId ? "#293349" : (cardMouse.containsMouse ? "#1d2737" : "#18212f")
                border.color: root.currentAccountId === accountId ? "#7566d9" : "#2a3548"
                border.width: 1

                Rectangle {
                    visible: root.currentAccountId === accountId
                    width: 3
                    height: 38
                    radius: 2
                    color: "#9a8bff"
                    anchors.left: parent.left
                    anchors.verticalCenter: parent.verticalCenter
                }

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 13
                    anchors.rightMargin: 13
                    spacing: 12

                    PlatformBadge { initialText: initial; platformColor: accentColor; badgeSize: 43 }

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 5
                        Text {
                            text: name || "待获取平台昵称"
                            color: "#edf1f7"
                            font.pixelSize: 13
                            font.weight: Font.Medium
                            elide: Text.ElideRight
                            Layout.fillWidth: true
                        }
                        Text {
                            text: platformShortName
                            color: "#8796ac"
                            font.pixelSize: 11
                            elide: Text.ElideRight
                            Layout.fillWidth: true
                        }
                        Row {
                            spacing: 6
                            Rectangle {
                                width: 6
                                height: 6
                                radius: 3
                                color: hasSession ? "#4bd2a4" : "#65748a"
                                anchors.verticalCenter: parent.verticalCenter
                            }
                            Text {
                                text: hasSession ? "会话已保存" : "等待首次登录"
                                color: hasSession ? "#78c9af" : "#6e7d93"
                                font.pixelSize: 10
                            }
                        }
                    }
                }

                MouseArea {
                    id: cardMouse
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: root.accountSelected(accountId)
                }

                Behavior on color { ColorAnimation { duration: 140 } }
                Behavior on border.color { ColorAnimation { duration: 140 } }
            }
        }

        Column {
            parent: accountList
            visible: accountList.count === 0
            anchors.centerIn: parent
            spacing: 12
            Rectangle {
                anchors.horizontalCenter: parent.horizontalCenter
                width: 54
                height: 54
                radius: 18
                color: "#1e293a"
                border.color: "#334159"
                border.width: 1
                Text { anchors.centerIn: parent; text: "＋"; color: "#8190a8"; font.pixelSize: 23 }
            }
            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: searchField.text ? "没有匹配的账号" : "当前分类还没有账号"
                color: "#8b9ab0"
                font.pixelSize: 12
            }
        }
    }

    Component.onCompleted: applyFilter()
}
