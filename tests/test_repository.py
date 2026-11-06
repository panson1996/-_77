from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app.repository import AccountRepository


class AccountRepositoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repository = AccountRepository(self.temp_dir.name)

    def tearDown(self) -> None:
        self.repository.close()
        self.temp_dir.cleanup()

    def test_add_list_and_isolated_profiles(self) -> None:
        first = self.repository.add("  抖音   主账号  ", "douyin")
        second = self.repository.add("视频号 A", "channels")
        third = self.repository.add("抖音小号", "douyin")

        accounts = self.repository.list_accounts()
        self.assertEqual(len(accounts), 3)
        self.assertEqual(self.repository.get(first)["name"], "抖音 主账号")
        self.assertNotEqual(
            self.repository.profile_path(first), self.repository.profile_path(second)
        )
        self.assertNotEqual(
            self.repository.profile_path(first), self.repository.profile_path(third)
        )
        self.assertEqual(
            self.repository.profile_path(first).parent,
            self.repository.profile_path(third).parent,
        )
        self.assertEqual(
            self.repository.cache_path(first).parent,
            self.repository.cache_path(second).parent,
        )
        self.assertNotEqual(self.repository.cache_path(first), self.repository.cache_path(third))
        self.assertNotEqual(self.repository.cache_path(first), self.repository.cache_path(second))
        self.assertEqual(self.repository.get(second)["cachePath"], str(self.repository.cache_path(second)))
        self.assertEqual(self.repository.counts(), {"douyin": 2, "channels": 1, "xingtu": 0, "all": 3})

    def test_legacy_profile_migration_preserves_session_and_cache(self) -> None:
        account_id = self.repository.add("旧账号", "channels")
        self.repository.close()
        legacy_path = Path(self.temp_dir.name) / "profiles" / account_id
        legacy_cache = legacy_path / "cache"
        legacy_cache.mkdir(parents=True)
        (legacy_path / "Cookies").write_bytes(b"session-placeholder")
        (legacy_cache / "entry").write_bytes(b"cache-placeholder")

        self.repository = AccountRepository(self.temp_dir.name)
        profile = self.repository.profile_path(account_id)
        cache = self.repository.cache_path(account_id)
        self.assertEqual(profile.parent.name, "channels")
        self.assertEqual((profile / "Cookies").read_bytes(), b"session-placeholder")
        self.assertEqual((cache / "entry").read_bytes(), b"cache-placeholder")
        self.assertFalse(legacy_path.exists())
        self.assertFalse((profile / "cache").exists())

    def test_filter_search_and_literal_wildcards(self) -> None:
        self.repository.add("达人 100%", "douyin")
        self.repository.add("普通账号", "douyin")
        self.repository.add("视频号", "channels")

        self.assertEqual(len(self.repository.list_accounts("douyin")), 2)
        self.assertEqual(len(self.repository.list_accounts(query="100%")), 1)
        self.assertEqual(len(self.repository.list_accounts(query="%")), 1)

    def test_touch_and_session_reset(self) -> None:
        account_id = self.repository.add("测试账号", "xingtu")
        self.repository.touch(account_id)
        self.assertIsNotNone(self.repository.get(account_id)["last_opened_at"])

        profile = self.repository.profile_path(account_id)
        profile.mkdir(parents=True)
        (profile / "Cookies").write_bytes(b"test-session")
        cache = self.repository.cache_path(account_id)
        cache.mkdir()
        (cache / "entry").write_bytes(b"cache-placeholder")
        self.assertTrue(self.repository.get(account_id)["hasSession"])

        self.repository.reset_session(account_id)
        self.assertFalse(self.repository.get(account_id)["hasSession"])
        self.assertFalse(cache.exists())
        self.assertIsNotNone(self.repository.get(account_id))

    def test_delete_removes_metadata_and_profile(self) -> None:
        account_id = self.repository.add("待删除", "douyin")
        profile = self.repository.profile_path(account_id)
        profile.mkdir(parents=True)
        (profile / "session").write_text("local", encoding="utf-8")
        cache = self.repository.cache_path(account_id)
        cache.mkdir()
        (cache / "entry").write_bytes(b"cache-placeholder")

        self.repository.delete(account_id)
        self.assertIsNone(self.repository.get(account_id))
        self.assertFalse(profile.exists())
        self.assertFalse(cache.exists())

    def test_channels_entry_migration(self) -> None:
        account_id = self.repository.add("视频号", "channels")
        self.repository._connection.execute(
            "UPDATE accounts SET url = 'https://channels.weixin.qq.com/' WHERE id = ?",
            (account_id,),
        )
        self.repository._connection.commit()
        self.repository.close()
        self.repository = AccountRepository(self.temp_dir.name)

        self.assertEqual(
            self.repository.get(account_id)["url"],
            "https://channels.weixin.qq.com/login.html",
        )

    def test_blank_name_and_auto_nickname(self) -> None:
        account_id = self.repository.add(" ", "douyin")
        self.assertEqual(self.repository.get(account_id)["name"], "")
        self.assertTrue(self.repository.set_auto_name(account_id, "  登录后的   昵称  "))
        self.assertEqual(self.repository.get(account_id)["name"], "登录后的 昵称")
        self.assertFalse(self.repository.set_auto_name(account_id, "不应覆盖"))

        manual_id = self.repository.add("手动备注", "channels")
        self.assertFalse(self.repository.set_auto_name(manual_id, "平台昵称"))
        self.assertEqual(self.repository.get(manual_id)["name"], "手动备注")

    def test_rename_can_clear_and_restore_auto_naming(self) -> None:
        account_id = self.repository.add("原备注", "douyin")
        self.repository.rename(account_id, "  新   备注  ")
        self.assertEqual(self.repository.get(account_id)["name"], "新 备注")

        self.repository.rename(account_id, " ")
        self.assertEqual(self.repository.get(account_id)["name"], "")
        self.assertTrue(self.repository.set_auto_name(account_id, "新的平台昵称"))
        self.assertEqual(self.repository.get(account_id)["name"], "新的平台昵称")

        with self.assertRaises(ValueError):
            self.repository.rename(account_id, "超" * 41)
        with self.assertRaises(ValueError):
            self.repository.rename("missing", "备注")

    def test_preferences_round_trip_and_persistence(self) -> None:
        self.assertEqual(self.repository.get_preference("lastAccountId"), "")
        self.repository.set_preference("lastAccountId", "account-id")
        self.repository.set_preference("browserMaximized", "true")
        self.repository.set_preference("lastAccountId", "updated-id")
        self.repository.close()
        self.repository = AccountRepository(self.temp_dir.name)

        self.assertEqual(self.repository.get_preference("lastAccountId"), "updated-id")
        self.assertEqual(self.repository.get_preference("browserMaximized"), "true")
        with self.assertRaises(ValueError):
            self.repository.set_preference(" ", "value")

    def test_validation(self) -> None:
        with self.assertRaises(ValueError):
            self.repository.add("账号", "unknown")
        with self.assertRaises(ValueError):
            self.repository.profile_path("../outside")


if __name__ == "__main__":
    unittest.main()
