from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_NAME = "LessonConverter"
DESKTOP_SHORTCUT = Path.home() / "Desktop" / f"{APP_NAME}.lnk"
INSTALL_DIR = Path.home() / "AppData" / "Local" / "LessonConverter"
BATCH_LAUNCHER = INSTALL_DIR / "launch_lesson_converter.bat"
ICON_PATH = ROOT / "assets" / "lesson_converter_icon.ico"


def ensure_assets() -> None:
    icon_dir = ROOT / "assets"
    icon_dir.mkdir(exist_ok=True)
    if not ICON_PATH.exists():
        # create a tiny default icon file as placeholder if no real icon exists
        try:
            import base64

            data = base64.b64decode(
                "iVBORw0KGgoAAAANSUhEUgAAAJAAAAB6CAYAAAAF" \
                "v6y2AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJ0UkG" \
                "goAAAABJRU5ErkJggg=="
            )
            ICON_PATH.write_bytes(data)
        except Exception:
            pass


def install() -> None:
    ensure_assets()
    INSTALL_DIR.mkdir(parents=True, exist_ok=True)

    build_dir = ROOT / "dist"
    exe_path = build_dir / f"{APP_NAME}.exe"
    if not exe_path.exists():
        raise FileNotFoundError(f"Missing built executable: {exe_path}")

    shutil.copy2(exe_path, INSTALL_DIR / f"{APP_NAME}.exe")
    if ICON_PATH.exists():
        shutil.copy2(ICON_PATH, INSTALL_DIR / "lesson_converter_icon.ico")

    launcher = "@echo off\r\n"
    launcher += f'"{INSTALL_DIR / APP_NAME}.exe" "%*"\r\n'
    BATCH_LAUNCHER.write_text(launcher, encoding="utf-8")

    # create desktop shortcut using powershell if available
    powershell_script = f"""
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut('{DESKTOP_SHORTCUT}')
$Shortcut.TargetPath = '{BATCH_LAUNCHER}'
$Shortcut.WorkingDirectory = '{INSTALL_DIR}'
$Shortcut.IconLocation = '{INSTALL_DIR / 'lesson_converter_icon.ico'}'
$Shortcut.Save()
"""
    subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", powershell_script], check=False)

    print(f"Installed to {INSTALL_DIR}")
    print(f"Desktop shortcut created at {DESKTOP_SHORTCUT}")


def uninstall() -> None:
    if INSTALL_DIR.exists():
        shutil.rmtree(INSTALL_DIR)
    if DESKTOP_SHORTCUT.exists():
        DESKTOP_SHORTCUT.unlink()
    print("Uninstalled LessonConverter.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].lower() == "uninstall":
        uninstall()
    else:
        install()
