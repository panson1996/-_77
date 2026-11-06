"""Stress account switching while checking cookie and localStorage isolation."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from app.repository import AccountRepository

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / ".account-switch-test"
page_requests: list[tuple[str, str]] = []
storage_reports: list[tuple[str, str]] = []


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        parsed = urlsplit(self.path)
        if parsed.path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return
        if parsed.path == "/report":
            query = parse_qs(parsed.query)
            storage_reports.append((query["account"][0], query.get("previous", [""])[0]))
            self.send_response(204)
            self.end_headers()
            return
        if parsed.path not in {"/a", "/b", "/c"}:
            self.send_response(404)
            self.end_headers()
            return
        account = parsed.path[1]
        page_requests.append((account, self.headers.get("Cookie", "")))
        body = f"""<!doctype html><html><head><meta charset='utf-8'><title>Account {account}</title></head>
        <body><h1>Account {account}</h1><script>
        const previous = localStorage.getItem('account_token') || '';
        fetch('/report?account={account}&previous=' + encodeURIComponent(previous));
        localStorage.setItem('account_token', '{account}');
        </script></body></html>""".encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Set-Cookie", "matrix_session=active; Path=/; HttpOnly")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        return


def run_child() -> None:
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    from PySide6.QtCore import Q_ARG, QCoreApplication, QMetaObject, QObject, QTimer, QUrl, Qt
    from PySide6.QtGui import QGuiApplication
    from PySide6.QtQml import QQmlApplicationEngine
    from PySide6.QtQuickControls2 import QQuickStyle
    from PySide6.QtWebEngineQuick import QtWebEngineQuick

    from app.controller import AppController

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
    accounts = controller._repository.list_accounts()
    account_ids = {account["name"]: account["id"] for account in accounts}
    a_id = account_ids["A"]
    b_id = account_ids["B"]
    c_id = account_ids["C"]
    stage = 0
    watchdog = QTimer()
    watchdog.setSingleShot(True)
    watchdog.setInterval(25000)

    def fail(message: str) -> None:
        print(message, file=sys.stderr)
        app.exit(2)

    def report_timeout() -> None:
        details = []
        for item in window.findChildren(QObject):
            class_name = item.metaObject().className()
            if "WebEngine" in class_name or "BrowserWorkspace" in class_name or "Loader" in class_name:
                details.append(
                    (
                        class_name,
                        item.property("url"),
                        item.property("loading"),
                        item.property("active"),
                        item.property("loadedAccountId"),
                    )
                )
        window.grabWindow().save(str(ROOT / "artifacts" / "account-switch-timeout.png"))
        fail(
            f"Timed out at stage {stage}: {page_requests} {storage_reports} "
            f"current={window.property('currentAccount')} details={details}"
        )

    watchdog.timeout.connect(report_timeout)
    watchdog.start()
    app.aboutToQuit.connect(controller.close)

    def select_account(account_id: str) -> None:
        invoked = QMetaObject.invokeMethod(
            window,
            "selectAccount",
            Qt.ConnectionType.DirectConnection,
            Q_ARG("QVariant", account_id),
        )
        if not invoked:
            fail("Could not invoke selectAccount")

    def advance() -> None:
        nonlocal stage
        a_reports = [value for account, value in storage_reports if account == "a"]
        if stage == 0 and a_reports == [""]:
            select_account(b_id)
            stage = 1
        elif stage == 1 and storage_reports == [("a", ""), ("b", "")]:
            select_account(a_id)
            stage = 2
        elif stage == 2 and a_reports == ["", "a"]:
            select_account(b_id)
            select_account(a_id)
            stage = 3
        elif stage == 3 and a_reports == ["", "a", "a"]:
            select_account(c_id)
            stage = 4
        elif stage == 4 and ("c", "") in storage_reports:
            select_account(a_id)
            stage = 5
        elif stage == 5 and a_reports == ["", "a", "a", "a"]:
            poll.stop()
            watchdog.stop()
            window.close()

    poll = QTimer()
    poll.setInterval(25)
    poll.timeout.connect(advance)
    poll.start()
    result = app.exec()
    engine.deleteLater()
    app.processEvents()
    return result


def main() -> None:
    if DATA_DIR.exists():
        shutil.rmtree(DATA_DIR)
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base_url = f"http://127.0.0.1:{server.server_port}"
    try:
        repository = AccountRepository(DATA_DIR)
        a_id = repository.add("A", "douyin")
        b_id = repository.add("B", "douyin")
        c_id = repository.add("C", "channels")
        repository._connection.execute(
            "UPDATE accounts SET url = CASE id WHEN ? THEN ? WHEN ? THEN ? ELSE ? END",
            (a_id, f"{base_url}/a", b_id, f"{base_url}/b", f"{base_url}/c"),
        )
        repository._connection.commit()
        repository.set_preference("lastAccountId", a_id)
        a_cache = repository.cache_path(a_id)
        b_cache = repository.cache_path(b_id)
        c_cache = repository.cache_path(c_id)
        assert a_cache.parent == b_cache.parent == c_cache.parent
        assert len({a_cache, b_cache, c_cache}) == 3
        repository.close()

        result = run_child()
        assert result == 0, f"Switch session exited with {result}"
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "main.py"),
                "--data-dir",
                str(DATA_DIR),
                "--smoke-test",
            ],
            cwd=ROOT,
            env={**os.environ.copy(), "QT_QPA_PLATFORM": "offscreen"},
            check=True,
            timeout=30,
        )

        a_requests = [cookie for account, cookie in page_requests if account == "a"]
        b_requests = [cookie for account, cookie in page_requests if account == "b"]
        c_requests = [cookie for account, cookie in page_requests if account == "c"]
        a_storage = [value for account, value in storage_reports if account == "a"]
        assert len(a_requests) >= 5, page_requests
        assert "matrix_session=active" not in a_requests[0], page_requests
        assert all("matrix_session=active" in cookie for cookie in a_requests[1:]), page_requests
        assert all("matrix_session=active" not in cookie for cookie in b_requests), page_requests
        assert all("matrix_session=active" not in cookie for cookie in c_requests), page_requests
        # Four visits during switching, plus one final application restart.
        assert a_storage == ["", "a", "a", "a", "a"], storage_reports
        assert all(value == "" for account, value in storage_reports if account in {"b", "c"}), storage_reports
        print("PASS: same/cross-platform account switching preserved isolated sessions and cache leaves")
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()
