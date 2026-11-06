"""Seed one real platform account for compatibility troubleshooting."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

from app.repository import AccountRepository


def main() -> None:
    data_dir = Path(sys.argv[1])
    platform = sys.argv[2]
    if data_dir.exists():
        shutil.rmtree(data_dir)
    repository = AccountRepository(data_dir)
    account_id = repository.add(f"{platform} 兼容性测试", platform)
    print(account_id)
    repository.close()


if __name__ == "__main__":
    main()
