import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: root

    property string currentPlatform: "all"
    property string currentAccountId: ""
    property var currentAccount: ({})
    property string pendingAction: ""
    property string pendingAccountId: ""
    property bool browserMaximized: false
    property bool uiReady: false
    property bool shuttingDown: false

    visible: true
    width: 1440
    height: 900
    minimumWidth: 1120
    minimumHeight: 700
    title: "矩阵运营台"
    color: "#0c1118"
    font.family: "Noto Sans SC"

    function savePreferences() {
        if (!uiReady)
            return
        controller.setPreference("lastAccountId", currentAccountId)
        controller.setPreference("windowWidth", String(width))
        controller.setPreference("windowHeight", String(height))
        controller.setPreference("browserMaximized", String(browserMaximized))
    }

    function schedulePreferenceSave() {
        if (uiReady)
            preferenceSaveTimer.restart()
    }

    function toggleBrowserMaximized() {
        browserMaximized = !browserMaximized
    }

    function focusAccountSearch() {
        if (browserMaximized)
            browserMaximized = false
        Qt.callLater(accountPanel.focusSearch)
    }

    function selectNextAccount() {
        var accountId = controller.nextAccountId(currentAccountId)
        if (accountId)
            selectAccount(accountId)
    }

    function selectPlatform(platform) {
        currentPlatform = platform
        accountPanel.applyFilter()
        var account = currentAccountId ? controller.getAccount(currentAccountId) : ({})
        if (account.id && (platform === "all" || account.platform === platform)) {
            currentAccount = account
            return
        }
        selectAccount(controller.firstAccountId())
    }

    function refreshCurrentAccount() {
        var account = currentAccountId ? controller.getAccount(currentAccountId) : ({})
        if (!account.id) {
            currentAccountId = controller.firstAccountId()
            account = currentAccountId ? controller.getAccount(currentAccountId) : ({})
        }
        currentAccount = account
    }

    function selectAccount(accountId) {
        if (!accountId) {
            currentAccountId = ""
            currentAccount = ({})
            return
        }
        currentAccountId = accountId
        currentAccount = controller.getAccount(accountId)
        if (uiReady)
            controller.setPreference("lastAccountId", accountId)
        controller.touchAccount(accountId)
    }

    function openRenameDialog() {
        if (!currentAccountId)
            return
        renameAccountDialog.accountId = currentAccountId
        renameAccountDialog.currentName = currentAccount.name || ""
        renameAccountDialog.open()
    }

    function askConfirmation(action, accountId) {
        pendingAction = action
        pendingAccountId = accountId
        if (action === "delete") {
            confirmDialog.title = "删除这个账号？"
            confirmDialog.message = "将删除账号备注以及该账号在本机保存的全部浏览器会话。此操作无法撤销。"
            confirmDialog.confirmText = "删除账号"
            confirmDialog.dangerous = true
        } else {
            confirmDialog.title = "清除本地会话？"
            confirmDialog.message = "保留账号记录，但删除 Cookie、缓存及其他浏览器数据。下次打开时需要重新登录。"
            confirmDialog.confirmText = "清除会话"
            confirmDialog.dangerous = false
        }
        confirmDialog.open()
    }

    onCurrentAccountIdChanged: schedulePreferenceSave()
    onWidthChanged: schedulePreferenceSave()
    onHeightChanged: schedulePreferenceSave()
    onBrowserMaximizedChanged: schedulePreferenceSave()
    onClosing: function(close) {
        savePreferences()
        if (shuttingDown)
            return
        close.accepted = false
        shuttingDown = true
        browserWorkspace.prepareForShutdown()
        shutdownTimer.start()
    }

    Connections {
        target: controller
        function onAccountsChanged() { root.refreshCurrentAccount() }
        function onErrorOccurred(message) { toast.show(message) }
        function onNoticeOccurred(message) { toast.show(message) }
    }

    RowLayout {
        anchors.fill: parent
        spacing: 0

        Sidebar {
            visible: !root.browserMaximized
            Layout.fillHeight: true
            Layout.preferredWidth: 218
            currentPlatform: root.currentPlatform
            onPlatformSelected: function(platform) { root.selectPlatform(platform) }
            onAddRequested: addAccountDialog.open()
        }

        AccountPanel {
            id: accountPanel
            visible: !root.browserMaximized
            Layout.fillHeight: true
            Layout.preferredWidth: 304
            platform: root.currentPlatform
            currentAccountId: root.currentAccountId
            onAccountSelected: function(accountId) { root.selectAccount(accountId) }
        }

        BrowserWorkspace {
            id: browserWorkspace
            Layout.fillWidth: true
            Layout.fillHeight: true
            account: root.currentAccount
            maximized: root.browserMaximized
            onMaximizeRequested: root.toggleBrowserMaximized()
            onAddRequested: addAccountDialog.open()
            onRenameRequested: root.openRenameDialog()
            onDeleteRequested: root.askConfirmation("delete", root.currentAccountId)
            onResetSessionRequested: root.askConfirmation("reset", root.currentAccountId)
            onNotice: function(message) { toast.show(message) }
        }
    }

    Shortcut {
        sequence: "F11"
        onActivated: root.toggleBrowserMaximized()
    }
    Shortcut {
        sequence: "Ctrl+R"
        onActivated: browserWorkspace.reloadPage()
    }
    Shortcut {
        sequence: "Ctrl+Tab"
        onActivated: root.selectNextAccount()
    }
    Shortcut {
        sequence: "Ctrl+F"
        onActivated: root.focusAccountSearch()
    }

    AddAccountDialog {
        id: addAccountDialog
        onCreated: function(accountId) {
            root.currentPlatform = "all"
            accountPanel.applyFilter()
            root.selectAccount(accountId)
        }
    }

    RenameAccountDialog {
        id: renameAccountDialog
    }

    ConfirmDialog {
        id: confirmDialog
        onConfirmed: {
            if (!root.pendingAccountId)
                return
            if (root.pendingAction === "delete") {
                deleteTimer.accountId = root.pendingAccountId
                root.currentAccount = ({})
                deleteTimer.start()
            } else if (root.pendingAction === "reset") {
                resetTimer.accountId = root.pendingAccountId
                root.currentAccount = ({})
                resetTimer.start()
            }
        }
    }

    Timer {
        id: shutdownTimer
        interval: 500
        repeat: false
        onTriggered: root.close()
    }

    Timer {
        id: preferenceSaveTimer
        interval: 400
        repeat: false
        onTriggered: root.savePreferences()
    }

    Timer {
        id: deleteTimer
        property string accountId: ""
        interval: 500
        onTriggered: controller.deleteAccount(accountId)
    }

    Timer {
        id: resetTimer
        property string accountId: ""
        interval: 500
        onTriggered: controller.resetSession(accountId)
    }

    Toast {
        id: toast
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 24
    }

    Component.onCompleted: {
        currentAccountId = controller.getPreference("lastAccountId")
        var savedWidth = Number(controller.getPreference("windowWidth"))
        var savedHeight = Number(controller.getPreference("windowHeight"))
        if (isFinite(savedWidth) && savedWidth >= minimumWidth && savedWidth <= 7680)
            width = savedWidth
        if (isFinite(savedHeight) && savedHeight >= minimumHeight && savedHeight <= 4320)
            height = savedHeight
        browserMaximized = controller.getPreference("browserMaximized") === "true"
        refreshCurrentAccount()
        if (currentAccountId)
            controller.touchAccount(currentAccountId)
        uiReady = true
        savePreferences()
    }
}
