"""Qt models and the small API exposed to QML."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from PySide6.QtCore import QAbstractListModel, QByteArray, QModelIndex, Property, QObject, Qt, Signal, Slot

from app.platforms import PLATFORMS, platform_info
from app.repository import AccountRepository


class AccountModel(QAbstractListModel):
    IdRole = Qt.ItemDataRole.UserRole + 1
    NameRole = Qt.ItemDataRole.UserRole + 2
    PlatformRole = Qt.ItemDataRole.UserRole + 3
    PlatformNameRole = Qt.ItemDataRole.UserRole + 4
    PlatformShortNameRole = Qt.ItemDataRole.UserRole + 5
    UrlRole = Qt.ItemDataRole.UserRole + 6
    ColorRole = Qt.ItemDataRole.UserRole + 7
    InitialRole = Qt.ItemDataRole.UserRole + 8
    LastOpenedRole = Qt.ItemDataRole.UserRole + 9
    HasSessionRole = Qt.ItemDataRole.UserRole + 10
    ProfilePathRole = Qt.ItemDataRole.UserRole + 11

    _ROLE_NAMES = {
        IdRole: b"accountId",
        NameRole: b"name",
        PlatformRole: b"platform",
        PlatformNameRole: b"platformName",
        PlatformShortNameRole: b"platformShortName",
        UrlRole: b"url",
        ColorRole: b"accentColor",
        InitialRole: b"initial",
        LastOpenedRole: b"lastOpenedAt",
        HasSessionRole: b"hasSession",
        ProfilePathRole: b"profilePath",
    }

    _ROLE_KEYS = {
        IdRole: "id",
        NameRole: "name",
        PlatformRole: "platform",
        PlatformNameRole: "platformName",
        PlatformShortNameRole: "platformShortName",
        UrlRole: "url",
        ColorRole: "color",
        InitialRole: "initial",
        LastOpenedRole: "last_opened_at",
        HasSessionRole: "hasSession",
        ProfilePathRole: "profilePath",
    }

    def __init__(self, repository: AccountRepository) -> None:
        super().__init__()
        self._repository = repository
        self._accounts: list[dict[str, Any]] = []
        self._platform = "all"
        self._query = ""

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: N802
        return 0 if parent.isValid() else len(self._accounts)

    def roleNames(self) -> dict[int, QByteArray]:  # noqa: N802
        return self._ROLE_NAMES

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid() or not 0 <= index.row() < len(self._accounts):
            return None
        key = self._ROLE_KEYS.get(role)
        return self._accounts[index.row()].get(key) if key else None

    def set_filter(self, platform: str, query: str) -> None:
        self._platform = platform
        self._query = query
        self.refresh()

    def refresh(self) -> None:
        self.beginResetModel()
        self._accounts = self._repository.list_accounts(self._platform, self._query)
        self.endResetModel()


class AppController(QObject):
    accountsChanged = Signal()
    errorOccurred = Signal(str)
    noticeOccurred = Signal(str)

    def __init__(self, data_dir: str | Path) -> None:
        super().__init__()
        self._repository = AccountRepository(data_dir)
        self._model = AccountModel(self._repository)
        self._counts = self._repository.counts()
        self._model.refresh()

    @Property(QObject, constant=True)
    def accountModel(self) -> AccountModel:
        return self._model

    @Property("QVariantMap", notify=accountsChanged)
    def platformCounts(self) -> dict[str, int]:
        return self._counts

    @Property(str, constant=True)
    def dataLocation(self) -> str:
        return str(self._repository.data_dir)

    def _changed(self) -> None:
        self._model.refresh()
        self._counts = self._repository.counts()
        self.accountsChanged.emit()

    @Slot(str, str)
    def setFilter(self, platform: str, query: str) -> None:
        try:
            self._model.set_filter(platform, query)
            self.accountsChanged.emit()
        except ValueError as exc:
            self.errorOccurred.emit(str(exc))

    @Slot(str, str, result=str)
    def addAccount(self, name: str, platform: str) -> str:
        try:
            account_id = self._repository.add(name, platform)
            self._changed()
            self.noticeOccurred.emit("账号已添加，现在可以登录平台")
            return account_id
        except (ValueError, OSError) as exc:
            self.errorOccurred.emit(str(exc))
            return ""

    @Slot(str, str, result=bool)
    def renameAccount(self, account_id: str, name: str) -> bool:
        try:
            self._repository.rename(account_id, name)
            self._changed()
            self.noticeOccurred.emit("账号备注已更新" if name.strip() else "备注已清空，将重新自动获取平台昵称")
            return True
        except (ValueError, OSError) as exc:
            self.errorOccurred.emit(str(exc))
            return False

    @Slot(str, result="QVariantMap")
    def getAccount(self, account_id: str) -> dict[str, Any]:
        return self._repository.get(account_id) or {}

    @Slot(result=str)
    def firstAccountId(self) -> str:
        accounts = self._repository.list_accounts(self._model._platform, self._model._query)
        return accounts[0]["id"] if accounts else ""

    @Slot(str, result=str)
    def nextAccountId(self, current_id: str) -> str:
        accounts = self._repository.list_accounts(self._model._platform, self._model._query)
        account_ids = [account["id"] for account in accounts]
        if not account_ids:
            return ""
        if current_id not in account_ids:
            return account_ids[0]
        return account_ids[(account_ids.index(current_id) + 1) % len(account_ids)]

    @Slot(str, result=str)
    def getPreference(self, key: str) -> str:
        try:
            return self._repository.get_preference(key)
        except (ValueError, OSError) as exc:
            self.errorOccurred.emit(str(exc))
            return ""

    @Slot(str, str)
    def setPreference(self, key: str, value: str) -> None:
        try:
            self._repository.set_preference(key, value)
        except (ValueError, OSError) as exc:
            self.errorOccurred.emit(f"保存设置失败：{exc}")

    @Slot(str, str)
    def updateAccountName(self, account_id: str, nickname: str) -> None:
        try:
            if self._repository.set_auto_name(account_id, nickname):
                self._changed()
        except (ValueError, OSError) as exc:
            self.errorOccurred.emit(f"获取平台昵称失败：{exc}")

    @Slot(str)
    def touchAccount(self, account_id: str) -> None:
        try:
            self._repository.touch(account_id)
            self._changed()
        except ValueError as exc:
            self.errorOccurred.emit(str(exc))

    @Slot(str, result=str)
    def platformUrl(self, platform: str) -> str:
        try:
            return platform_info(platform)["url"]
        except ValueError:
            return ""

    @Slot(str)
    def resetSession(self, account_id: str) -> None:
        try:
            self._repository.reset_session(account_id)
            self._changed()
            self.noticeOccurred.emit("本地会话已清除，账号记录仍保留")
        except (ValueError, OSError) as exc:
            self.errorOccurred.emit(f"清除会话失败：{exc}")

    @Slot(str)
    def deleteAccount(self, account_id: str) -> None:
        try:
            self._repository.delete(account_id)
            self._changed()
            self.noticeOccurred.emit("账号及本地会话已删除")
        except (ValueError, OSError) as exc:
            self.errorOccurred.emit(f"删除失败：{exc}")

    def close(self) -> None:
        self._repository.close()
