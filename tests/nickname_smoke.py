"""Verify that a blank account is named from the loaded platform page."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from app.repository import AccountRepository

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / ".nickname-test"


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        body = """<!doctype html><html><head><meta charset="utf-8"><title>Nickname test</title></head>
        <body style="font-family:sans-serif;padding:40px"><h1>平台首页</h1>
        <div class="user-name">运营测试昵称</div></body></html>""".encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        return


def main() -> None:
    if DATA_DIR.exists():
        shutil.rmtree(DATA_DIR)
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        repository = AccountRepository(DATA_DIR)
        account_id = repository.add("", "douyin")
        repository._connection.execute(
            "UPDATE accounts SET url = ? WHERE id = ?",
            (f"http://127.0.0.1:{server.server_port}/", account_id),
        )
        repository._connection.commit()
        repository.close()

        environment = os.environ.copy()
        environment["QT_QPA_PLATFORM"] = "offscreen"
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "main.py"),
                "--data-dir",
                str(DATA_DIR),
                "--smoke-test",
                "--screenshot",
                str(ROOT / "artifacts" / "nickname.png"),
            ],
            cwd=ROOT,
            env=environment,
            check=True,
            timeout=30,
        )

        repository = AccountRepository(DATA_DIR)
        actual_name = repository.get(account_id)["name"]
        repository.close()
        assert actual_name == "运营测试昵称", actual_name
        print(f"PASS: blank account automatically named: {actual_name}")
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()
