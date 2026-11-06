import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "components"

Dialog {
    id: root

    property string message: ""
    property string confirmText: "确认"
    property bool dangerous: false
    signal confirmed()

    title: ""
    modal: true
    focus: true
    width: 420
    height: 220
    padding: 0
    closePolicy: Popup.CloseOnEscape
    x: Math.round((parent.width - width) / 2)
    y: Math.round((parent.height - height) / 2)

    background: Rectangle { radius: 16; color: "#161c26"; border.color: "#343e4e"; border.width: 1 }

    contentItem: ColumnLayout {
        Layout.fillWidth: true
        spacing: 12
        Text { Layout.leftMargin: 24; Layout.topMargin: 24; text: root.title; color: "#f0f3f8"; font.pixelSize: 19; font.weight: Font.DemiBold }
        Text {
            Layout.fillWidth: true
            Layout.leftMargin: 24
            Layout.rightMargin: 24
            text: root.message
            color: "#929dae"
            font.pixelSize: 12
            wrapMode: Text.WordWrap
            lineHeight: 1.35
        }
        Item { Layout.fillHeight: true }
        RowLayout {
            Layout.fillWidth: true
            Layout.leftMargin: 24
            Layout.rightMargin: 24
            Layout.bottomMargin: 22
            spacing: 10
            Item { Layout.fillWidth: true }
            AppButton { text: "取消"; variant: "secondary"; onClicked: root.close() }
            AppButton {
                text: root.confirmText
                variant: root.dangerous ? "danger" : "primary"
                onClicked: { root.close(); root.confirmed() }
            }
        }
    }
}
