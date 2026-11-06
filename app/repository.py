"""SQLite-backed account metadata and isolated profile paths."""

from __future__ import annotations

import re
import shutil
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from app.platforms import PLATFORMS, platform_info

_ACCOUNT_ID = re.compile(r"^[a-f0-9]{16}$")


def _now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


class AccountRepository:
    """Own account metadata; browser profiles remain managed by Qt WebEngine."""

    def __init__(self, data_dir: str | Path) -> None:
        self.data_dir = Path(data_dir).resolve()
        self.profiles_dir = self.data_dir / "profiles"
        self.cache_dir = self.data_dir / "cache"
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.data_dir / "accounts.sqlite3"
        self._connection = sqlite3.connect(self.db_path)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA journal_mode=WAL")
        self._connection.execute("PRAGMA foreign_keys=ON")
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS accounts (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                platform TEXT NOT NULL,
                url TEXT NOT NULL,
                created_at TEXT NOT NULL,
                last_opened_at TEXT
            )
            """
        )
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS preferences (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )
        self._connection.execute(
            "UPDATE accounts SET url = ? WHERE platform = 'channels' AND url = ?",
            (PLATFORMS["channels"]["url"], "https://channels.weixin.qq.com/"),
        )
        self._connection.commit()
        self._migrate_profile_layout()

    def _migrate_profile_layout(self) -> None:
        """Move legacy account profiles without overwriting existing login data."""
        rows = self._connection.execute("SELECT id, platform FROM accounts").fetchall()
        for row in rows:
            account_id = row["id"]
            legacy_path = self.profiles_dir / account_id
            profile_path = self._profile_path(row["platform"], account_id)
            cache_path = self.cache_path(account_id)
            profile_path.parent.mkdir(parents=True, exist_ok=True)
            if legacy_path.is_dir() and not profile_path.exists():
                legacy_path.rename(profile_path)
            legacy_cache = profile_path / "cache"
            if legacy_cache.is_dir() and not cache_path.exists():
                legacy_cache.rename(cache_path)

    def close(self) -> None:
        self._connection.close()

    def _profile_path(self, platform: str, account_id: str) -> Path:
        platform_info(platform)
        if not _ACCOUNT_ID.fullmatch(account_id):
            raise ValueError("无效的账号标识")
        return self.profiles_dir / platform / account_id

    def profile_path(self, account_id: str) -> Path:
        """Resolve a Chrome-style account profile beneath its platform group."""
        row = self._connection.execute(
            "SELECT platform FROM accounts WHERE id = ?", (account_id,)
        ).fetchone()
        if row is None:
            if not _ACCOUNT_ID.fullmatch(account_id):
                raise ValueError("无效的账号标识")
            raise ValueError("账号不存在")
        return self._profile_path(row["platform"], account_id)

    def cache_path(self, account_id: str) -> Path:
        """Use one cache root, with a separate leaf for every account profile."""
        if not _ACCOUNT_ID.fullmatch(account_id):
            raise ValueError("无效的账号标识")
        return self.cache_dir / account_id

    def _has_session(self, account_id: str) -> bool:
        path = self.profile_path(account_id)
        return path.is_dir() and any(path.iterdir())

    def _decorate(self, row: sqlite3.Row) -> dict[str, Any]:
        account = dict(row)
        info = platform_info(account["platform"])
        account.update(
            platformName=info["name"],
            platformShortName=info["short_name"],
            color=info["color"],
            initial=info["initial"],
            profilePath=str(self._profile_path(account["platform"], account["id"])),
            cachePath=str(self.cache_path(account["id"])),
            hasSession=self._has_session(account["id"]),
        )
        return account

    def list_accounts(self, platform: str = "all", query: str = "") -> list[dict[str, Any]]:
        clauses: list[str] = []
        parameters: list[str] = []
        if platform != "all":
            platform_info(platform)
            clauses.append("platform = ?")
            parameters.append(platform)
        normalized_query = query.strip()
        if normalized_query:
            clauses.append("name LIKE ? ESCAPE '\\'")
            escaped = normalized_query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            parameters.append(f"%{escaped}%")
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        rows = self._connection.execute(
            f"""
            SELECT id, name, platform, url, created_at, last_opened_at
            FROM accounts
            {where}
            ORDER BY COALESCE(last_opened_at, created_at) DESC, name COLLATE NOCASE
            """,
            parameters,
        ).fetchall()
        return [self._decorate(row) for row in rows]

    def get(self, account_id: str) -> dict[str, Any] | None:
        row = self._connection.execute(
            "SELECT id, name, platform, url, created_at, last_opened_at FROM accounts WHERE id = ?",
            (account_id,),
        ).fetchone()
        return self._decorate(row) if row else None

    def add(self, name: str, platform: str) -> str:
        normalized_name = " ".join(name.strip().split())
        if len(normalized_name) > 40:
            raise ValueError("账号备注不能超过 40 个字符")
        info = platform_info(platform)
        account_id = uuid.uuid4().hex[:16]
        self._connection.execute(
            """
            INSERT INTO accounts (id, name, platform, url, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (account_id, normalized_name, platform, info["url"], _now()),
        )
        self._connection.commit()
        return account_id

    def rename(self, account_id: str, name: str) -> None:
        normalized_name = " ".join(name.strip().split())
        if len(normalized_name) > 40:
            raise ValueError("账号备注不能超过 40 个字符")
        cursor = self._connection.execute(
            "UPDATE accounts SET name = ? WHERE id = ?",
            (normalized_name, account_id),
        )
        if cursor.rowcount == 0:
            raise ValueError("账号不存在")
        self._connection.commit()

    def get_preference(self, key: str) -> str:
        normalized_key = key.strip()
        if not normalized_key or len(normalized_key) > 64:
            raise ValueError("无效的偏好设置键")
        row = self._connection.execute(
            "SELECT value FROM preferences WHERE key = ?",
            (normalized_key,),
        ).fetchone()
        return row["value"] if row else ""

    def set_preference(self, key: str, value: str) -> None:
        normalized_key = key.strip()
        if not normalized_key or len(normalized_key) > 64:
            raise ValueError("无效的偏好设置键")
        if len(value) > 4096:
            raise ValueError("偏好设置内容过长")
        self._connection.execute(
            """
            INSERT INTO preferences (key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """,
            (normalized_key, value),
        )
        self._connection.commit()

    def set_auto_name(self, account_id: str, nickname: str) -> bool:
        """Fill only an empty name; never replace a user's manual label."""
        normalized_name = " ".join(nickname.strip().split())
        if not normalized_name or len(normalized_name) > 40:
            return False
        cursor = self._connection.execute(
            "UPDATE accounts SET name = ? WHERE id = ? AND TRIM(name) = ''",
            (normalized_name, account_id),
        )
        self._connection.commit()
        return cursor.rowcount > 0

    def touch(self, account_id: str) -> None:
        cursor = self._connection.execute(
            "UPDATE accounts SET last_opened_at = ? WHERE id = ?",
            (_now(), account_id),
        )
        if cursor.rowcount == 0:
            raise ValueError("账号不存在")
        self._connection.commit()

    def counts(self) -> dict[str, int]:
        result = {key: 0 for key in PLATFORMS}
        rows = self._connection.execute(
            "SELECT platform, COUNT(*) AS count FROM accounts GROUP BY platform"
        ).fetchall()
        for row in rows:
            result[row["platform"]] = row["count"]
        result["all"] = sum(result.values())
        return result

    def reset_session(self, account_id: str) -> None:
        if self.get(account_id) is None:
            raise ValueError("账号不存在")
        path = self.profile_path(account_id)
        if path.exists():
            shutil.rmtree(path)
        cache_path = self.cache_path(account_id)
        if cache_path.exists():
            shutil.rmtree(cache_path)

    def delete(self, account_id: str) -> None:
        self.reset_session(account_id)
        self._connection.execute("DELETE FROM accounts WHERE id = ?", (account_id,))
        self._connection.commit()
