"""End-to-end proof of persistent and isolated Qt WebEngine profiles."""

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
DATA_ROOT = ROOT / ".session-test"
received_cookies: list[str] = []
storage_reports: dict[str, list[str]] = {"local": [], "idb": []}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        parsed = urlsplit(self.path)
        if parsed.path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return
        if parsed.path == "/report":
            query = parse_qs(parsed.query)
            storage_reports[query["kind"][0]].append(query.get("value", [""])[0])
            self.send_response(204)
            self.end_headers()
            return
        received_cookies.append(self.headers.get("Cookie", ""))
        body = b"""<!doctype html><html><head><meta charset='utf-8'><title>Session test</title></head>
        <body style='font-family:sans-serif;background:#f6f7fb;padding:40px'>
        <h1>Local session test</h1><p>Browser storage test.</p><script>
        const previous = localStorage.getItem('matrix_test') || '';
        fetch('/report?kind=local&value=' + encodeURIComponent(previous));
        localStorage.setItem('matrix_test', 'persisted');
        const request = indexedDB.open('matrix_test', 1);
        request.onupgradeneeded = event => event.target.result.createObjectStore('session');
        request.onsuccess = event => {
            const db = event.target.result;
            const transaction = db.transaction('session', 'readwrite');
            const store = transaction.objectStore('session');
            const get = store.get('token');
            get.onsuccess = () => {
                fetch('/report?kind=idb&value=' + encodeURIComponent(get.result || ''));
                store.put('persisted', 'token');
            };
        };
        </script></body></html>"""
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Set-Cookie", "matrix_session=persisted; Path=/; Max-Age=3600")
        self.send_header("Set-Cookie", "matrix_session_only=active; Path=/; HttpOnly")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        return


def seed_account(data_dir: Path, name: str, url: str) -> str:
    repository = AccountRepository(data_dir)
    account_id = repository.add(name, "douyin")
    repository._connection.execute("UPDATE accounts SET url = ?", (url,))
    repository._connection.commit()
    repository.close()
    return account_id


def run_app(data_dir: Path, screenshot: Path | None = None) -> None:
    command = [
        sys.executable,
        str(ROOT / "main.py"),
        "--data-dir",
        str(data_dir),
        "--smoke-test",
    ]
    if screenshot:
        command.extend(["--screenshot", str(screenshot)])
    environment = os.environ.copy()
    environment["QT_QPA_PLATFORM"] = "offscreen"
    subprocess.run(command, cwd=ROOT, env=environment, check=True, timeout=30)


def main() -> None:
    if DATA_ROOT.exists():
        shutil.rmtree(DATA_ROOT)
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{server.server_port}/"

    try:
        first_dir = DATA_ROOT / "first"
        first_id = seed_account(first_dir, "持久化测试", url)
        run_app(first_dir)

        # Recreate the legacy on-disk layout between real browser launches.
        current_profile = first_dir / "profiles" / "douyin" / first_id
        legacy_profile = first_dir / "profiles" / first_id
        current_profile.rename(legacy_profile)
        current_cache = first_dir / "cache" / first_id
        current_cache.rename(legacy_profile / "cache")
        run_app(first_dir, ROOT / "artifacts" / "session.png")

        second_dir = DATA_ROOT / "second"
        second_id = seed_account(second_dir, "隔离测试", url)
        run_app(second_dir)

        assert len(received_cookies) == 3, received_cookies
        for cookie_name in ("matrix_session=persisted", "matrix_session_only=active"):
            assert cookie_name not in received_cookies[0], received_cookies
            assert cookie_name in received_cookies[1], received_cookies
            assert cookie_name not in received_cookies[2], received_cookies

        assert storage_reports["local"] == ["", "persisted", ""], storage_reports
        assert storage_reports["idb"] == ["", "persisted", ""], storage_reports

        first_profile = first_dir / "profiles" / "douyin" / first_id
        second_profile = second_dir / "profiles" / "douyin" / second_id
        first_cache = first_dir / "cache" / first_id
        second_cache = second_dir / "cache" / second_id
        assert first_profile.is_dir() and any(first_profile.iterdir())
        assert second_profile.is_dir() and any(second_profile.iterdir())
        assert first_profile != second_profile
        assert first_cache.is_dir() and second_cache.is_dir()
        assert first_cache.parent.name == second_cache.parent.name == "cache"
        assert first_cache != second_cache
        assert not (first_profile / "cache").exists()
        assert not (second_profile / "cache").exists()
        print("PASS: cookies, localStorage, and IndexedDB persisted and remained isolated")
        print(f"First profile: {first_profile}")
        print(f"Second profile: {second_profile}")
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()
