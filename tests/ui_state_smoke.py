"""Verify QML restores account, window size, and browser layout after restart."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

from app.repository import AccountRepository

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / ".ux-state-test"


def run_app(screenshot_name: str) -> None:
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
            str(ROOT / "artifacts" / screenshot_name),
        ],
        cwd=ROOT,
        env=environment,
        check=True,
        timeout=30,
    )


def assert_preferences(expected: dict[str, str]) -> None:
    repository = AccountRepository(DATA_DIR)
    actual = {key: repository.get_preference(key) for key in expected}
    repository.close()
    assert actual == expected, {"expected": expected, "actual": actual}


def main() -> None:
    if DATA_DIR.exists():
        shutil.rmtree(DATA_DIR)
    repository = AccountRepository(DATA_DIR)
    first_id = repository.add("抖音主账号", "douyin")
    second_id = repository.add("视频号运营号", "channels")
    repository._connection.execute("UPDATE accounts SET url = 'about:blank'")
    repository._connection.commit()
    repository.set_preference("lastAccountId", second_id)
    repository.set_preference("windowWidth", "1280")
    repository.set_preference("windowHeight", "760")
    repository.set_preference("browserMaximized", "true")
    repository.close()

    run_app("ui-ux-maximized.png")
    assert_preferences(
        {
            "lastAccountId": second_id,
            "windowWidth": "1280",
            "windowHeight": "760",
            "browserMaximized": "true",
        }
    )

    repository = AccountRepository(DATA_DIR)
    repository.set_preference("lastAccountId", first_id)
    repository.set_preference("windowWidth", "1360")
    repository.set_preference("windowHeight", "820")
    repository.set_preference("browserMaximized", "false")
    repository.close()

    run_app("ui-ux-main.png")
    assert_preferences(
        {
            "lastAccountId": first_id,
            "windowWidth": "1360",
            "windowHeight": "820",
            "browserMaximized": "false",
        }
    )
    print("PASS: QML restored last account, window size, and browser maximized state")


if __name__ == "__main__":
    main()
