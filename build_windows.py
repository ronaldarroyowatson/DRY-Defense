from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def main() -> None:
    command = [
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
    print("Running:", " ".join(command))
    subprocess.run(command, cwd=str(ROOT), check=True)


if __name__ == "__main__":
    main()
