from __future__ import annotations

import tempfile
import unittest

from app.controller import AppController


class AppControllerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.controller = AppController(self.temp_dir.name)

    def tearDown(self) -> None:
        self.controller.close()
        self.temp_dir.cleanup()

    def test_next_account_cycles_through_current_filter(self) -> None:
        self.controller.addAccount("账号一", "douyin")
        self.controller.addAccount("账号二", "channels")
        self.controller.addAccount("账号三", "xingtu")

        first = self.controller.firstAccountId()
        second = self.controller.nextAccountId(first)
        third = self.controller.nextAccountId(second)
        self.assertEqual(len({first, second, third}), 3)
        self.assertEqual(self.controller.nextAccountId(third), first)

        self.controller.setFilter("channels", "")
        only_channels = self.controller.firstAccountId()
        self.assertEqual(self.controller.nextAccountId(only_channels), only_channels)
        self.assertEqual(self.controller.nextAccountId("missing"), only_channels)

        self.controller.setFilter("douyin", "没有匹配项")
        self.assertEqual(self.controller.nextAccountId(first), "")

    def test_preferences_do_not_emit_account_refresh(self) -> None:
        emissions = []
        self.controller.accountsChanged.connect(lambda: emissions.append(True))
        self.controller.setPreference("lastAccountId", "account-id")
        self.assertEqual(self.controller.getPreference("lastAccountId"), "account-id")
        self.assertEqual(emissions, [])


if __name__ == "__main__":
    unittest.main()
