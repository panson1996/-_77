# 矩阵运营台

基于 **Python 3.14＋PySide6＋QML＋Qt WebEngine＋SQLite** 的公司内部多账号运营工具原型。

## 启动

直接双击 `run.bat`。启动脚本使用本机环境：

```text
C:\Users\p\AppData\Local\Programs\Python\Python314\python.exe
```

也可以在项目目录运行：

```bat
"C:\Users\p\AppData\Local\Programs\Python\Python314\python.exe" main.py
```

## 已实现

- 抖音创作者中心、微信视频号助手、巨量星图的账号入口。
- 账号新增、平台筛选、备注搜索、删除。
- 每个账号独立的 `WebEngineProfile`，明确关闭无痕模式，类似 Chrome 的多用户档案。
- Cookie、LocalStorage、IndexedDB 按“平台／账号”分目录持久化，同平台账号也不共享登录数据。
- 普通 HTTP 缓存使用统一根目录，每个账号使用独立子目录，清除账号不会影响其他账号。
- 单活动页面：切换账号时销毁上一个网页，但保留其本地会话。
- 浏览器前进、后退、刷新、平台首页和弹窗登录支持。
- 清除单个账号会话、确认对话框、操作提示。
- 本地 SQLite 元数据、中文界面和随项目加载的 Noto Sans SC 字体。

## 使用方式

1. 点击“添加账号”。
2. 选择平台；内部备注可以留空，登录后将尝试从平台页面自动获取昵称，手动备注不会被覆盖。
3. 在内置官方页面中扫码或手动登录，不需要在软件中填写平台密码。
4. 下次启动后点击同一账号，恢复其浏览器会话。
5. “清除会话”只删除登录数据；“删除账号”同时删除账号记录和会话。

登录状态始终以平台实际页面为准。平台要求重新扫码或验证时，按页面提示操作。

## 本地数据

默认位置：

```text
C:\Users\p\AppData\Local\MatrixDesk\
├── accounts.sqlite3
├── cache\                 # 所有平台共用的缓存根目录
│   └── 账号 ID\           # 账号独立的 HTTP 缓存
└── profiles\
    ├── douyin\            # 抖音账号档案
    │   └── 账号 ID\
    ├── channels\          # 视频号账号档案
    │   └── 账号 ID\
    └── xingtu\            # 星图账号档案
        └── 账号 ID\
```

首次启动新版本时会自动迁移旧的账号目录；已有登录数据不会被主动清空。

可以用参数指定其他目录：

```bat
run.bat --data-dir "D:\运营数据\MatrixDesk"
```

业务数据库不导出或重复保存 Cookie。浏览器 Profile 属于登录凭证，应仅允许当前 Windows 用户访问，不要同步到公共目录或提交到代码仓库。当前版本未提供会话导出、跨机迁移和加密备份。

## 验证

```bat
"C:\Users\p\AppData\Local\Programs\Python\Python314\python.exe" -m unittest discover -s tests -v
```

端到端会话测试：

```bat
set PYTHONPATH=.
"C:\Users\p\AppData\Local\Programs\Python\Python314\python.exe" tests\webengine_session_smoke.py
```

该测试只启动本机临时 HTTP 页面，验证 Cookie 重启后恢复且不同账号相互隔离，不访问真实运营平台。

## 当前边界

这是第一版功能原型，不是已经验收的生产系统。真实三平台的扫码登录、跳转、上传下载及风控兼容性仍需使用公司账号逐项验证。当前不包含自动绕过验证、批量平台操作、员工权限、安装包和自动更新。

Qt／PySide6 按其许可条款使用；Noto Sans SC 字体许可位于 `assets/fonts/OFL.txt`。
