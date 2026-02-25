# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec: NEUROCALIPSIS — un solo .exe portable, sin consola
# Ejecutar desde la carpeta del proyecto: pyinstaller --clean neurocalipsis.spec

from PyInstaller.utils.hooks import collect_all

block_cipher = None

# Incluir TODO el paquete pygame (módulos, DLLs, datos) para que el .exe lo encuentre
pygame_datas, pygame_binaries, pygame_hiddenimports = collect_all("pygame")

# Rutas relativas al directorio desde donde se ejecuta pyinstaller (carpeta del proyecto)
datas = [
    ("sounds", "sounds"),
    ("images", "images"),
    ("assets", "assets"),
    ("data", "data"),
] + pygame_datas

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=pygame_binaries,
    datas=datas,
    hiddenimports=[
        "pygame",
        "effects",
        "particles",
        "abilities",
        "minimap",
        "drone_sprites",
        "level_loader",
        "data.load_stats",
    ] + pygame_hiddenimports,
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
    name="Neurocalipsis",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,   # Sin ventana de consola — solo ventana del juego
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,       # Opcional: ruta a un .ico para el ejecutable
)
