# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None
project_root = os.path.abspath(SPECPATH)

# 1. Collect all data files and folders seen in your project tree
added_datas = [
    (os.path.join(project_root, 'assets'), 'assets'),
    (os.path.join(project_root, 'models'), 'models'),
    (os.path.join(project_root, 'pages'), 'pages'),
    (os.path.join(project_root, 'utils'), 'utils'),
    (os.path.join(project_root, 'widgets'), 'widgets'),
    (os.path.join(project_root, 'backend'), 'backend'),
]

# If database exists, include it as well
if os.path.exists(os.path.join(project_root, 'database')):
    added_datas.append((os.path.join(project_root, 'database'), 'database'))

# 2. Collect all submodules from packages
hidden_imports = (
    collect_submodules('pages') +
    collect_submodules('models') +
    collect_submodules('utils') +
    collect_submodules('widgets') +
    collect_submodules('backend') +
    collect_submodules('sklearn') +
    [
        'sklearn.utils._typedefs',
        'joblib',
        'numpy',
        'PyQt5',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
    ]
)

a = Analysis(
    ['main.py'],
    pathex=[project_root],
    binaries=[],
    datas=added_datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['node_modules', 'mobile', 'tests', 'build', 'dist'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='BudgetWise AI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No background terminal window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(project_root, 'assets', 'BudgetWise_AI_logo.png'),
)