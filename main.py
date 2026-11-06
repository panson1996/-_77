"""矩阵运营台桌面入口。"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from PySide6.QtCore import QCoreApplication, QTimer, Qt, QUrl
from PySide6.QtGui import QFont, QFontDatabase, QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtWebEngineQuick import QtWebEngineQuick

from app.controller import AppController


def resource_dir() -> Path:
    """资源根目录：PyInstaller 打包后指向 _MEIPASS，否则指向脚本所在目录。"""
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    return Path(__file__).resolve().parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="矩阵运营台")
    parser.add_argument("--data-dir", help="覆盖默认的本地数据目录")
    parser.add_argument("--smoke-test", action="store_true", help="启动后自动退出，用于验证 QML")
    parser.add_argument("--screenshot", help="配合 --smoke-test 保存窗口截图")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
    QCoreApplication.setOrganizationName("MatrixDesk")
    QCoreApplication.setApplicationName("MatrixDesk")
    QCoreApplication.setApplicationVersion("0.1.0")

    app = QGuiApplication(sys.argv)
    app.setApplicationDisplayName("矩阵运营台")
    font_dir = resource_dir() / "assets" / "fonts"
    for font_file in ("NotoSansSC-Regular.ttf", "NotoSansSC-Bold.ttf"):
        QFontDatabase.addApplicationFont(str(font_dir / font_file))
    app.setFont(QFont("Noto Sans SC", 10))
    QQuickStyle.setStyle("Basic")
    QtWebEngineQuick.initialize()

    default_data_dir = (
        Path.home() / "Library" / "Application Support" / "MatrixDesk"
        if sys.platform == "darwin"
        else Path.home() / "AppData" / "Local" / "MatrixDesk"
    )
    data_dir = (
        Path(args.data_dir)
        if args.data_dir
        else Path(os.environ.get("MATRIX_DESK_DATA_DIR", ""))
        if os.environ.get("MATRIX_DESK_DATA_DIR")
        else default_data_dir
    )
    controller = AppController(data_dir)

    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("controller", controller)
    engine.rootContext().setContextProperty("accountModel", controller.accountModel)
    qml_path = resource_dir() / "qml" / "Main.qml"
    engine.load(QUrl.fromLocalFile(str(qml_path)))
    if not engine.rootObjects():
        controller.close()
        return 1

    app.aboutToQuit.connect(controller.close)

    if args.smoke_test:
        def finish() -> None:
            if args.screenshot:
                image = engine.rootObjects()[0].grabWindow()
                output = Path(args.screenshot).resolve()
                output.parent.mkdir(parents=True, exist_ok=True)
                if not image.save(str(output)):
                    print(f"截图保存失败：{output}", file=sys.stderr)
            engine.rootObjects()[0].close()

        QTimer.singleShot(2500, finish)

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
