"""Create isolated local accounts for the WebEngine startup smoke test."""

from __future__ import annotations

import shutil
import sqlite3
import sys
from pathlib import Path

from app.repository import AccountRepository


def main() -> None:
    data_dir = Path(sys.argv[1])
    if data_dir.exists():
        shutil.rmtree(data_dir)
    repository = AccountRepository(data_dir)
    first = repository.add("抖音测试账号", "douyin")
    second = repository.add("视频号测试账号", "channels")
    connection = sqlite3.connect(repository.db_path)
    connection.execute("UPDATE accounts SET url = 'about:blank'")
    connection.commit()
    connection.close()
    print(first)
    print(second)
    repository.close()


if __name__ == "__main__":
    main()
