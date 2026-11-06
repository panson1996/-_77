import QtQuick
import QtQuick.Controls

Button {
    id: control

    property string variant: "secondary"
    property string iconText: ""
    property color foregroundColor: variant === "secondary" ? "#d4dce9" : "#ffffff"

    implicitWidth: Math.max(42, contentItem.implicitWidth + leftPadding + rightPadding)
    implicitHeight: 40
    hoverEnabled: true
    leftPadding: 15
    rightPadding: 15
    topPadding: 0
    bottomPadding: 0

    contentItem: Item {
        implicitWidth: contentRow.implicitWidth
        implicitHeight: contentRow.implicitHeight

        Row {
            id: contentRow
            anchors.centerIn: parent
            spacing: 7

            Text {
                visible: control.iconText.length > 0
                text: control.iconText
                color: control.enabled ? control.foregroundColor : "#697386"
                font.pixelSize: 16
                font.weight: Font.Medium
                anchors.verticalCenter: parent.verticalCenter
            }

            Text {
                visible: control.text.length > 0
                text: control.text
                color: control.enabled ? control.foregroundColor : "#697386"
                font.pixelSize: 12
                font.weight: Font.Medium
                anchors.verticalCenter: parent.verticalCenter
            }
        }
    }

    background: Rectangle {
        radius: 11
        scale: control.down ? 0.98 : 1.0
        border.width: control.variant === "secondary" ? 1 : 0
        border.color: control.activeFocus ? "#8f82ff" : (control.hovered ? "#465168" : "#303a4c")
        gradient: control.variant === "primary" && control.enabled ? primaryGradient : null
        color: {
            if (!control.enabled)
                return "#202631"
            if (control.variant === "primary")
                return "transparent"
            if (control.variant === "danger")
                return control.down ? "#a92e43" : (control.hovered ? "#dd4b64" : "#c53c55")
            if (control.variant === "ghost")
                return control.hovered || control.down ? "#222b3a" : "transparent"
            return control.down ? "#252f40" : (control.hovered ? "#2a3547" : "#202938")
        }

        Gradient {
            id: primaryGradient
            GradientStop { position: 0.0; color: control.down ? "#6655dc" : (control.hovered ? "#9485ff" : "#8373fa") }
            GradientStop { position: 1.0; color: control.down ? "#4e3fc1" : (control.hovered ? "#6d5ce4" : "#5d4bd3") }
        }

        Behavior on color { ColorAnimation { duration: 140 } }
        Behavior on border.color { ColorAnimation { duration: 140 } }
        Behavior on scale { NumberAnimation { duration: 80 } }
    }
}
