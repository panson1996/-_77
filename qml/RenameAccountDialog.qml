import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "components"

Dialog {
    id: root

    property string accountId: ""
    property string currentName: ""

    function save() {
        if (!accountId)
            return
        if (controller.renameAccount(accountId, nameField.text))
            root.close()
    }

    title: ""
    modal: true
    focus: true
    width: 460
    height: 326
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
        spacing: 17

        ColumnLayout {
            Layout.fillWidth: true
            Layout.leftMargin: 24
            Layout.rightMargin: 24
            Layout.topMargin: 24
            spacing: 6
            Text { text: "修改账号备注"; color: "#f0f3f8"; font.pixelSize: 20; font.weight: Font.DemiBold }
            Text { text: "使用容易辨认的名称，不影响平台内的真实昵称。"; color: "#7e899a"; font.pixelSize: 12 }
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
                placeholderText: "留空则重新自动获取平台昵称"
                color: "#e4e8ef"
                placeholderTextColor: "#657084"
                font.pixelSize: 13
                leftPadding: 13
                selectByMouse: true
                onAccepted: root.save()
                background: Rectangle {
                    radius: 10
                    color: "#1d2430"
                    border.color: nameField.activeFocus ? "#8172f5" : "#303a49"
                    border.width: 1
                }
            }
            Text {
                Layout.fillWidth: true
                text: "清空备注后，下次成功加载页面时会再次尝试获取昵称。"
                color: "#657084"
                font.pixelSize: 10
                wrapMode: Text.WordWrap
            }
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
            AppButton { text: "保存备注"; variant: "primary"; onClicked: root.save() }
        }
    }

    onOpened: {
        nameField.text = currentName
        nameField.forceActiveFocus()
        nameField.selectAll()
    }
}
