from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

FACTS_FIELDNAMES = [
    "LessonName",
    "LessonPlan",
    "HomeworkNotes",
    "Label1",
    "Label2",
    "Label3",
    "Label4",
]

PLANBOOK_FIELDNAMES = [
    "Lesson #",
    "Section 1 (Lesson)",
    "Section 2 (Homework)",
    "Section 3 (Notes)",
    "Section 4",
    "Section 5",
    "Section 6",
    "Lesson Title",
    "Unit ID",
    "Unit Title",
]


@dataclass
class Lesson:
    lesson_name: str = ""
    lesson_plan: str = ""
    homework_notes: str = ""
    label1: str = ""
    label2: str = ""
    label3: str = ""
    label4: str = ""

    @classmethod
    def from_facts_row(cls, row: dict[str, Any]) -> "Lesson":
        return cls(
            lesson_name=_normalize_text(row.get("LessonName")),
            lesson_plan=_normalize_text(row.get("LessonPlan")),
            homework_notes=_normalize_text(row.get("HomeworkNotes")),
            label1=_normalize_text(row.get("Label1")),
            label2=_normalize_text(row.get("Label2")),
            label3=_normalize_text(row.get("Label3")),
            label4=_normalize_text(row.get("Label4")),
        )

    def to_facts_row(self) -> dict[str, str]:
        return {
            "LessonName": self.lesson_name,
            "LessonPlan": self.lesson_plan,
            "HomeworkNotes": self.homework_notes,
            "Label1": self.label1,
            "Label2": self.label2,
            "Label3": self.label3,
            "Label4": self.label4,
        }

    def to_planbook_row(self, lesson_number: int) -> dict[str, str | int]:
        return {
            "Lesson #": lesson_number,
            "Section 1 (Lesson)": self.lesson_plan,
            "Section 2 (Homework)": self.homework_notes,
            "Section 3 (Notes)": "",
            "Section 4": self.label1,
            "Section 5": self.label2,
            "Section 6": self.label3,
            "Lesson Title": self.lesson_name,
            "Unit ID": self.label4,
            "Unit Title": "",
        }

    def to_project_dict(self) -> dict[str, str]:
        return asdict(self)

    @classmethod
    def from_project_dict(cls, payload: dict[str, Any]) -> "Lesson":
        return cls(
            lesson_name=_normalize_text(payload.get("lesson_name")),
            lesson_plan=_normalize_text(payload.get("lesson_plan")),
            homework_notes=_normalize_text(payload.get("homework_notes")),
            label1=_normalize_text(payload.get("label1")),
            label2=_normalize_text(payload.get("label2")),
            label3=_normalize_text(payload.get("label3")),
            label4=_normalize_text(payload.get("label4")),
        )


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).replace("\u00a0", " ").strip()


def detect_csv_format(path: str | Path) -> str:
    csv_path = Path(path)
    with csv_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.reader(csv_file)
        try:
            header = next(reader)
        except StopIteration as exc:  # pragma: no cover
            raise ValueError("CSV file is empty.") from exc

        normalized_header = [cell.strip() for cell in header]
        if set(FACTS_FIELDNAMES).issubset(normalized_header):
            return "FACTS"
        if {"Lesson #", "Lesson Title", "Section 1 (Lesson)"}.issubset(normalized_header):
            return "Planbook"
        raise ValueError(f"Unsupported CSV format in {csv_path.name}.")


def convert_file(path: str | Path) -> tuple[Path, str]:
    input_path = Path(path)
    fmt = detect_csv_format(input_path)
    if fmt == "FACTS":
        lessons = load_facts_csv(input_path)
        output_path = generate_output_path(input_path, "Planbook")
        write_planbook_csv(output_path, lessons)
        return output_path, "Planbook"

    if fmt == "Planbook":
        lessons = load_planbook_csv(input_path)
        output_path = generate_output_path(input_path, "FACTS")
        write_facts_csv(output_path, lessons)
        return output_path, "FACTS"

    raise ValueError(f"Unsupported format detected in {input_path.name}.")


def generate_output_path(input_path: str | Path, target_format: str) -> Path:
    path = Path(input_path)
    base_name = path.stem
    output_name = f"{base_name}_{target_format}.csv"
    return path.with_name(output_name)


def load_facts_csv(path: str | Path) -> list[Lesson]:
    csv_path = Path(path)
    with csv_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        return [Lesson.from_facts_row(row) for row in reader if _row_has_content(row)]


def load_planbook_csv(path: str | Path) -> list[Lesson]:
    csv_path = Path(path)
    with csv_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        return convert_planbook_to_facts(list(reader))


def convert_facts_to_planbook(lessons: Iterable[Lesson]) -> list[dict[str, str | int]]:
    rows: list[dict[str, str | int]] = []
    for index, lesson in enumerate(lessons, start=1):
        rows.append(lesson.to_planbook_row(index))
    return rows


def convert_planbook_to_facts(rows: Iterable[dict[str, Any]]) -> list[Lesson]:
    lessons: list[Lesson] = []
    for row in rows:
        if not row:
            continue
        if not _row_has_content(row):
            continue

        lesson_name = _normalize_text(row.get("Lesson Title") or row.get("LessonName"))
        if not lesson_name:
            lesson_name = _normalize_text(row.get("Lesson #") or "")

        lesson = Lesson(
            lesson_name=lesson_name,
            lesson_plan=_normalize_text(row.get("Section 1 (Lesson)") or row.get("LessonPlan")),
            homework_notes=_normalize_text(row.get("Section 2 (Homework)") or row.get("HomeworkNotes")),
            label1=_normalize_text(row.get("Section 4") or row.get("Label1")),
            label2=_normalize_text(row.get("Section 5") or row.get("Label2")),
            label3=_normalize_text(row.get("Section 6") or row.get("Label3")),
            label4=_normalize_text(row.get("Unit ID") or row.get("Label4")),
        )
        lessons.append(lesson)
    return lessons


def write_facts_csv(path: str | Path, lessons: Iterable[Lesson]) -> None:
    csv_path = Path(path)
    with csv_path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=FACTS_FIELDNAMES)
        writer.writeheader()
        for lesson in lessons:
            writer.writerow(lesson.to_facts_row())


def write_planbook_csv(path: str | Path, lessons: Iterable[Lesson]) -> None:
    csv_path = Path(path)
    rows = convert_facts_to_planbook(lessons)
    with csv_path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=PLANBOOK_FIELDNAMES)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in PLANBOOK_FIELDNAMES})


def load_project_file(path: str | Path) -> list[Lesson]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    lessons = payload.get("lessons", [])
    return [Lesson.from_project_dict(item) for item in lessons]


def save_project_file(path: str | Path, lessons: Iterable[Lesson]) -> None:
    project_path = Path(path)
    project_path.write_text(
        json.dumps({"version": 1, "lessons": [lesson.to_project_dict() for lesson in lessons]}, indent=2),
        encoding="utf-8",
    )


def _row_has_content(row: dict[str, Any]) -> bool:
    values = [str(value).strip() for value in row.values() if value is not None]
    return any(value for value in values)
