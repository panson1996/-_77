"""Verify sidebar platform selection also switches the active browser account."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtCore import Q_ARG, QCoreApplication, QMetaObject, QUrl, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtWebEngineQuick import QtWebEngineQuick

from app.controller import AppController
from app.repository import AccountRepository

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / ".platform-switch-test"


def main() -> None:
    if DATA_DIR.exists():
        shutil.rmtree(DATA_DIR)
    repository = AccountRepository(DATA_DIR)
    douyin_id = repository.add("抖音主账号", "douyin")
    channels_id = repository.add("视频号运营号", "channels")
    repository._connection.execute("UPDATE accounts SET url = 'about:blank'")
    repository._connection.commit()
    repository.set_preference("lastAccountId", channels_id)
    repository.close()

    QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
    app = QGuiApplication([])
    QQuickStyle.setStyle("Basic")
    QtWebEngineQuick.initialize()
    controller = AppController(DATA_DIR)
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("controller", controller)
    engine.rootContext().setContextProperty("accountModel", controller.accountModel)
    engine.load(QUrl.fromLocalFile(str(ROOT / "qml" / "Main.qml")))
    assert engine.rootObjects(), "QML failed to load"
    window = engine.rootObjects()[0]

    def select_platform(platform: str) -> None:
        invoked = QMetaObject.invokeMethod(
            window,
            "selectPlatform",
            Qt.ConnectionType.DirectConnection,
            Q_ARG("QVariant", platform),
        )
        assert invoked, f"Could not invoke selectPlatform({platform})"

    try:
        assert window.property("currentAccountId") == channels_id
        select_platform("douyin")
        assert window.property("currentPlatform") == "douyin"
        assert window.property("currentAccountId") == douyin_id, window.property("currentAccountId")

        # Repeating the same platform selection must also repair a mismatched account.
        window.setProperty("currentAccountId", channels_id)
        select_platform("douyin")
        assert window.property("currentAccountId") == douyin_id

        select_platform("channels")
        assert window.property("currentAccountId") == channels_id
        select_platform("xingtu")
        assert window.property("currentAccountId") == ""
        assert not window.property("currentAccount").toVariant()

        select_platform("all")
        assert window.property("currentAccountId") in {douyin_id, channels_id}
        app.processEvents()
        image = window.grabWindow()
        output = ROOT / "artifacts" / "platform-switch-fixed.png"
        assert image.save(str(output)), "Failed to save screenshot"
        print("PASS: platform selection switches browser account and handles empty platforms")
    finally:
        window.close()
        engine.deleteLater()
        app.processEvents()
        controller.close()


if __name__ == "__main__":
    main()
