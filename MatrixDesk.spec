# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('qml', 'qml'), ('assets', 'assets')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

# 过滤从 PATH（如 Anaconda）误收的老版本 DLL（dest 位于 _internal 根目录）：
# - icuuc.dll / icudt58.dll：Qt6Core 依赖系统自带 ICU（System32\icuuc.dll），
#   Anaconda 的 ICU 58 会因符号缺失导致 QtCore 导入失败；
# - VCRUNTIME140*.dll：剔除 Python 目录旧副本（14.42），运行时统一解析到
#   PySide6 自带的新版本（14.44），避免混用不同版本运行时。
# PySide6 子目录下的同名 DLL dest 带路径前缀，不会被此规则误伤。
_stale_binaries = {'icuuc.dll', 'icudt58.dll', 'icuin58.dll',
                  'vcruntime140.dll', 'vcruntime140_1.dll'}
for _entry in list(a.binaries):
    _dest = _entry[0].replace('\\', '/').split('/')[-1]
    if _dest.lower() in _stale_binaries and '/' not in _entry[0].replace('\\', '/'):
        print(f'Excluding stale binary: {_entry[0]} <- {_entry[1]}')
        a.binaries.remove(_entry)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MatrixDesk',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MatrixDesk',
)
