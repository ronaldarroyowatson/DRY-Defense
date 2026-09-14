from __future__ import annotations

import json
from pathlib import Path

from .converter import Lesson


def save_project(path: str | Path, lessons: list[Lesson]) -> None:
    path_obj = Path(path)
    payload = {"version": 1, "lessons": [lesson.to_project_dict() for lesson in lessons]}
    path_obj.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def load_project(path: str | Path) -> list[Lesson]:
    path_obj = Path(path)
    payload = json.loads(path_obj.read_text(encoding="utf-8"))
    lessons = payload.get("lessons", [])
    return [Lesson.from_project_dict(item) for item in lessons]
