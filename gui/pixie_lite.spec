# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['pixie_lite.py'],
    pathex=['../.venv/lib/python3.12/site-packages/'],
    binaries=[],
    datas=[('assets/.env', 'assets/'), ('assets/header.html', 'assets/.'), ('assets/README.md', 'assets/'), ('assets/chat.png', 'assets/')],
    hiddenimports=['tiktoken_ext.openai_public', 'tiktoken_ext'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Pixie Lite',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['assets/chat.png']
)
