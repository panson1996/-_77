import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtWebEngine
import "components"

Rectangle {
    id: root

    property var account: ({})
    property string loadedAccountId: ""
    property bool maximized: false
    signal maximizeRequested()
    signal addRequested()
    signal renameRequested()
    signal deleteRequested()
    signal resetSessionRequested()
    signal notice(string message)

    color: "#0b111b"
    gradient: Gradient {
        GradientStop { position: 0.0; color: "#101827" }
        GradientStop { position: 1.0; color: "#0a1019" }
    }

    function restartBrowser() {
        browserLoader.active = false
        loadedAccountId = root.account && root.account.id ? root.account.id : ""
        if (loadedAccountId)
            browserLoader.active = true
    }

    function reloadPage() {
        if (browserLoader.item)
            browserLoader.item.reload()
    }

    function prepareForShutdown() {
        nicknameTimer.stop()
        browserLoader.active = false
        loadedAccountId = ""
    }

    function requestNickname() {
        if (!browserLoader.item || !root.account.id || root.account.name)
            return
        var accountId = root.account.id
        var script = `(function() {
            const selectors = [
                "[class*='nickname']", "[class*='nick-name']",
                "[class*='user-name']", "[class*='userName']",
                "[class*='account-name']", "[data-e2e*='nickname']"
            ];
            const blocked = ["登录", "注册", "个人中心", "账号设置", "昵称",
                "抖音创作者中心", "视频号助手", "巨量星图"];
            for (const selector of selectors) {
                for (const element of document.querySelectorAll(selector)) {
                    const text = (element.innerText || "").trim().replace(/\\s+/g, " ");
                    if (text && text.length <= 40 && !blocked.includes(text))
                        return text;
                }
            }
            return "";
        })();`
        browserLoader.item.runJavaScript(script, function(result) {
            if (typeof result === "string" && result.trim())
                controller.updateAccountName(accountId, result)
        })
    }

    onAccountChanged: {
        var nextId = root.account && root.account.id ? root.account.id : ""
        if (nextId !== loadedAccountId) {
            restartBrowser()
        } else if (nextId && !root.account.name && browserLoader.item && !browserLoader.item.loading) {
            nicknameTimer.restart()
        }
    }

    Timer {
        id: nicknameTimer
        interval: 1600
        repeat: false
        onTriggered: root.requestNickname()
    }

    Component {
        id: browserComponent

        WebEngineView {
            id: webView
            anchors.fill: parent
            url: root.account.url

            profile: WebEngineProfile {
                storageName: "matrix_" + root.account.id
                offTheRecord: false
                persistentStoragePath: root.account.profilePath
                cachePath: root.account.cachePath
                persistentCookiesPolicy: WebEngineProfile.ForcePersistentCookies
                httpCacheType: WebEngineProfile.DiskHttpCache
                httpCacheMaximumSize: 104857600
            }

            settings.javascriptCanOpenWindows: true
            settings.errorPageEnabled: true
            zoomFactor: Math.max(0.65, Math.min(1, browserLoader.width / 1200))

            onNewWindowRequested: function(request) {
                request.openIn(webView)
            }
            onLoadingChanged: function(loadRequest) {
                if (loadRequest.status === WebEngineLoadingInfo.LoadFailedStatus)
                    root.notice("页面加载失败：" + loadRequest.errorString + "，请检查网络后刷新")
                if (loadRequest.status === WebEngineLoadingInfo.LoadSucceededStatus && !root.account.name)
                    nicknameTimer.restart()
            }
        }
    }

    Rectangle {
        visible: !(root.account && root.account.id)
        anchors.centerIn: parent
        width: Math.min(parent.width - 56, 580)
        height: 474
        radius: 26
        color: "#141d2c"
        border.color: "#334159"
        border.width: 1
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#1a2436" }
            GradientStop { position: 1.0; color: "#111927" }
        }

        Rectangle {
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            height: 3
            radius: 2
            gradient: Gradient {
                orientation: Gradient.Horizontal
                GradientStop { position: 0.0; color: "#5d4bd3" }
                GradientStop { position: 0.55; color: "#9a8bff" }
                GradientStop { position: 1.0; color: "#3bc9b0" }
            }
        }

        Column {
            anchors.centerIn: parent
            width: parent.width - 64
            spacing: 17

            Row {
                anchors.horizontalCenter: parent.horizontalCenter
                spacing: 12
                PlatformBadge { initialText: "抖"; platformColor: "#ff5470"; badgeSize: 44 }
                PlatformBadge { initialText: "视"; platformColor: "#2bd58a"; badgeSize: 44 }
                PlatformBadge { initialText: "星"; platformColor: "#9a8bff"; badgeSize: 44 }
            }

            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: "MULTI-ACCOUNT WORKSPACE"
                color: "#8072e8"
                font.pixelSize: 9
                font.letterSpacing: 2.2
                font.weight: Font.Medium
            }

            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: "运营账号，一站管理"
                color: "#f3f6fb"
                font.pixelSize: 28
                font.weight: Font.DemiBold
            }

            Text {
                width: parent.width
                anchors.horizontalCenter: parent.horizontalCenter
                horizontalAlignment: Text.AlignHCenter
                text: "在一个清爽的工作台中管理抖音、视频号与巨量星图。独立会话、本地保存，让每个账号都井然有序。"
                color: "#8998ae"
                font.pixelSize: 13
                wrapMode: Text.WordWrap
                lineHeight: 1.4
            }

            AppButton {
                anchors.horizontalCenter: parent.horizontalCenter
                text: "添加第一个账号"
                iconText: "＋"
                variant: "primary"
                implicitHeight: 43
                onClicked: root.addRequested()
            }

            Rectangle { width: parent.width; height: 1; color: "#2b374b" }

            Row {
                anchors.horizontalCenter: parent.horizontalCenter
                spacing: 24
                Row {
                    spacing: 7
                    Rectangle { width: 6; height: 6; radius: 3; color: "#8f80fa"; anchors.verticalCenter: parent.verticalCenter }
                    Text { text: "独立会话"; color: "#8796ac"; font.pixelSize: 11 }
                }
                Row {
                    spacing: 7
                    Rectangle { width: 6; height: 6; radius: 3; color: "#4bd2a4"; anchors.verticalCenter: parent.verticalCenter }
                    Text { text: "按需加载"; color: "#8796ac"; font.pixelSize: 11 }
                }
                Row {
                    spacing: 7
                    Rectangle { width: 6; height: 6; radius: 3; color: "#60a5fa"; anchors.verticalCenter: parent.verticalCenter }
                    Text { text: "本地存储"; color: "#8796ac"; font.pixelSize: 11 }
                }
            }
        }
    }

    ColumnLayout {
        visible: !!(root.account && root.account.id)
        anchors.fill: parent
        spacing: 0

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 80
            color: "#121b29"
            border.color: "#283449"
            border.width: 1

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 22
                anchors.rightMargin: 20
                spacing: 13

                PlatformBadge {
                    initialText: root.account.initial || ""
                    platformColor: root.account.color || "#8172f5"
                    badgeSize: 44
                }
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 5
                    Text {
                        text: root.account.name || "待获取平台昵称"
                        color: "#f0f4f9"
                        font.pixelSize: 16
                        font.weight: Font.DemiBold
                        elide: Text.ElideRight
                        Layout.fillWidth: true
                    }
                    Row {
                        spacing: 6
                        Rectangle {
                            width: 6
                            height: 6
                            radius: 3
                            color: root.account.hasSession ? "#4bd2a4" : "#718096"
                            anchors.verticalCenter: parent.verticalCenter
                        }
                        Text {
                            text: (root.account.platformName || "") + "  ·  " + (root.account.hasSession ? "本地会话已保存" : "登录状态以平台页面为准")
                            color: "#8090a7"
                            font.pixelSize: 11
                        }
                    }
                }
                AppButton {
                    text: "重命名"
                    variant: "ghost"
                    onClicked: root.renameRequested()
                }
                AppButton {
                    text: "清除会话"
                    variant: "ghost"
                    onClicked: root.resetSessionRequested()
                }
                AppButton {
                    text: "删除账号"
                    variant: "ghost"
                    foregroundColor: "#f08394"
                    onClicked: root.deleteRequested()
                }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 62
            color: "#0e1622"
            border.color: "#202b3d"
            border.width: 1

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 16
                anchors.rightMargin: 16
                spacing: 8

                AppButton {
                    text: "←"
                    variant: "ghost"
                    enabled: browserLoader.item && browserLoader.item.canGoBack
                    Layout.preferredWidth: 38
                    onClicked: browserLoader.item.goBack()
                }
                AppButton {
                    text: "→"
                    variant: "ghost"
                    enabled: browserLoader.item && browserLoader.item.canGoForward
                    Layout.preferredWidth: 38
                    onClicked: browserLoader.item.goForward()
                }
                AppButton {
                    text: "刷新"
                    variant: "ghost"
                    enabled: browserLoader.item
                    Layout.preferredWidth: 58
                    onClicked: root.reloadPage()
                    ToolTip.visible: hovered
                    ToolTip.text: "刷新当前页面（Ctrl+R）"
                }

                TextField {
                    id: addressField
                    Layout.fillWidth: true
                    Layout.leftMargin: 5
                    implicitHeight: 38
                    readOnly: true
                    text: browserLoader.item ? browserLoader.item.url : (root.account.url || "")
                    color: "#b3c0d2"
                    placeholderTextColor: "#68778e"
                    font.pixelSize: 11
                    leftPadding: 34
                    rightPadding: 14
                    selectByMouse: true
                    background: Rectangle {
                        radius: 11
                        color: "#1a2433"
                        border.color: "#303d52"
                        border.width: 1
                    }
                    Rectangle {
                        width: 7
                        height: 7
                        radius: 4
                        color: "#4bd2a4"
                        anchors.left: parent.left
                        anchors.leftMargin: 14
                        anchors.verticalCenter: parent.verticalCenter
                    }
                }

                AppButton {
                    text: "平台首页"
                    variant: "secondary"
                    enabled: browserLoader.item
                    onClicked: browserLoader.item.url = root.account.url
                }
                AppButton {
                    text: root.maximized ? "还原" : "最大化"
                    variant: "secondary"
                    foregroundColor: "#b8adff"
                    onClicked: root.maximizeRequested()
                    ToolTip.visible: hovered
                    ToolTip.text: root.maximized ? "还原账号列表（F11）" : "最大化浏览器（F11）"
                }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "#ffffff"

            Loader {
                id: browserLoader
                anchors.fill: parent
                active: false
                asynchronous: false
                sourceComponent: browserComponent
            }

            Rectangle {
                id: loadProgressBar
                visible: browserLoader.item && browserLoader.item.loading
                anchors.left: parent.left
                anchors.top: parent.top
                height: 3
                width: parent.width * Math.max(0.03, (browserLoader.item ? browserLoader.item.loadProgress : 0) / 100)
                z: 2
                gradient: Gradient {
                    orientation: Gradient.Horizontal
                    GradientStop { position: 0.0; color: "#7565e8" }
                    GradientStop { position: 1.0; color: "#4bd2c2" }
                }
                Behavior on width { NumberAnimation { duration: 120; easing.type: Easing.OutCubic } }
            }
        }
    }

    Component.onCompleted: restartBrowser()
}
