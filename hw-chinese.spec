# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_all, copy_metadata

block_cipher = None

MAC_ICON = Path("assets/icons/app_icon.icns")


def _bundle_for(package_name: str):
    datas, binaries, hiddenimports = collect_all(package_name)
    return datas, binaries, hiddenimports


datas = []
binaries = []
hiddenimports = []

for package in ["paddleocr", "paddlex"]:
    pkg_datas, pkg_binaries, pkg_hiddenimports = _bundle_for(package)
    datas += pkg_datas
    binaries += pkg_binaries
    hiddenimports += pkg_hiddenimports

hiddenimports += ["cv2", "numpy"]

metadata_packages = [
    "paddlex",
    "paddleocr",
    "paddlepaddle",
    "beautifulsoup4",
    "einops",
    "ftfy",
    "imagesize",
    "Jinja2",
    "lxml",
    "opencv-contrib-python",
    "openpyxl",
    "premailer",
    "pyclipper",
    "pypdfium2",
    "python-bidi",
    "regex",
    "safetensors",
    "scikit-learn",
    "scipy",
    "sentencepiece",
    "shapely",
    "tiktoken",
    "tokenizers",
]

for package in metadata_packages:
    datas += copy_metadata(package)


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    exclude_binaries=False,
    name='hw-chinese',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(MAC_ICON) if sys.platform == "darwin" and MAC_ICON.exists() else None,
)

if sys.platform == "darwin":
    app = BUNDLE(
        exe,
        name='hw-chinese.app',
        icon=str(MAC_ICON) if MAC_ICON.exists() else None,
        bundle_identifier=None,
    )
