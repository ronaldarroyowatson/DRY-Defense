from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main() -> None:
    build = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--windowed",
        "--name",
        "LessonConverter",
        str(ROOT / "lesson_converter_app" / "main.py"),
    ]
    subprocess.run(build, cwd=str(ROOT), check=True)

    install = [
        sys.executable,
        str(ROOT / "installer" / "install_lesson_converter.py"),
    ]
    subprocess.run(install, cwd=str(ROOT), check=True)


if __name__ == "__main__":
    main()
