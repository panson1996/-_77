import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "components"

Dialog {
    id: root

    signal created(string accountId)

    title: ""
    modal: true
    focus: true
    width: 470
    height: 410
    padding: 0
    closePolicy: Popup.CloseOnEscape
    x: Math.round((parent.width - width) / 2)
    y: Math.round((parent.height - height) / 2)

    background: Rectangle {
        radius: 16
        color: "#161c26"
        border.color: "#343e4e"
        border.width: 1
    }

    contentItem: ColumnLayout {
        spacing: 16

        ColumnLayout {
            Layout.fillWidth: true
            Layout.leftMargin: 24
            Layout.rightMargin: 24
            Layout.topMargin: 24
            spacing: 6
            Text { text: "添加运营账号"; color: "#f0f3f8"; font.pixelSize: 20; font.weight: Font.DemiBold }
            Text { text: "只需设置备注，登录将在平台官方页面中完成。"; color: "#7e899a"; font.pixelSize: 12 }
        }

        ColumnLayout {
            Layout.fillWidth: true
            Layout.leftMargin: 24
            Layout.rightMargin: 24
            spacing: 8
            Text { text: "平台"; color: "#b3bdca"; font.pixelSize: 12; font.weight: Font.Medium }
            ComboBox {
                id: platformCombo
                Layout.fillWidth: true
                implicitHeight: 42
                textRole: "name"
                valueRole: "value"
                model: ListModel {
                    ListElement { name: "抖音创作者中心"; value: "douyin" }
                    ListElement { name: "微信视频号助手"; value: "channels" }
                    ListElement { name: "巨量星图"; value: "xingtu" }
                }
                background: Rectangle { radius: 10; color: "#1d2430"; border.color: platformCombo.activeFocus ? "#6c5ce7" : "#303a49"; border.width: 1 }
                contentItem: Text {
                    text: platformCombo.displayText
                    color: "#e4e8ef"
                    font.pixelSize: 13
                    leftPadding: 13
                    rightPadding: 36
                    verticalAlignment: Text.AlignVCenter
                    elide: Text.ElideRight
                }
                popup: Popup {
                    y: platformCombo.height + 4
                    width: platformCombo.width
                    implicitHeight: contentItem.implicitHeight + 2
                    padding: 1
                    contentItem: ListView {
                        clip: true
                        implicitHeight: contentHeight
                        model: platformCombo.popup.visible ? platformCombo.delegateModel : null
                        currentIndex: platformCombo.highlightedIndex
                        ScrollIndicator.vertical: ScrollIndicator { }
                    }
                    background: Rectangle { radius: 10; color: "#202735"; border.color: "#394456"; border.width: 1 }
                }
            }
        }

        ColumnLayout {
            Layout.fillWidth: true
            Layout.leftMargin: 24
            Layout.rightMargin: 24
            spacing: 8
            Text { text: "账号备注（选填）"; color: "#b3bdca"; font.pixelSize: 12; font.weight: Font.Medium }
            TextField {
                id: nameField
                Layout.fillWidth: true
                implicitHeight: 42
                maximumLength: 40
                placeholderText: "留空则登录后自动获取平台昵称"
                color: "#e4e8ef"
                placeholderTextColor: "#657084"
                font.pixelSize: 13
                leftPadding: 13
                selectByMouse: true
                background: Rectangle { radius: 10; color: "#1d2430"; border.color: nameField.activeFocus ? "#6c5ce7" : "#303a49"; border.width: 1 }
            }
        }

        Text {
            Layout.leftMargin: 24
            Layout.rightMargin: 24
            Layout.fillWidth: true
            text: "登录入口：" + controller.platformUrl(platformCombo.currentValue)
            color: "#657084"
            font.pixelSize: 10
            elide: Text.ElideMiddle
        }

        Item { Layout.fillHeight: true }

        RowLayout {
            Layout.leftMargin: 24
            Layout.rightMargin: 24
            Layout.bottomMargin: 22
            Layout.fillWidth: true
            spacing: 10
            Item { Layout.fillWidth: true }
            AppButton { text: "取消"; variant: "secondary"; onClicked: root.close() }
            AppButton {
                text: "创建并打开"
                variant: "primary"
                onClicked: {
                    var accountId = controller.addAccount(nameField.text, platformCombo.currentValue)
                    if (accountId) {
                        root.close()
                        root.created(accountId)
                    }
                }
            }
        }
    }

    onOpened: {
        nameField.text = ""
        platformCombo.currentIndex = 0
        nameField.forceActiveFocus()
    }
}
