import csv
from pathlib import Path

from lesson_converter_app.converter import (
    PLANBOOK_FIELDNAMES,
    Lesson,
    convert_facts_to_planbook,
    convert_planbook_to_facts,
    load_facts_csv,
    load_planbook_csv,
    write_planbook_csv,
)


def test_facts_to_planbook_uses_planbook_compatible_sections():
    lessons = [
        Lesson(
            lesson_name="First Day Science",
            lesson_plan="<p>Intro</p>",
            homework_notes="<p>Read pages 1-2</p>",
            label1="Goal 1",
            label2="Goal 2",
            label3="Goal 3",
            label4="Goal 4",
        )
    ]

    rows = convert_facts_to_planbook(lessons)
    assert rows[0]["Lesson Title"] == "First Day Science"
    assert rows[0]["Section 1 (Lesson)"] == "First Day Science"
    assert rows[0]["Section 2 (Homework)"] == "Read pages 1-2"
    assert rows[0]["Section 3 (Notes)"] == "Intro"
    assert rows[0]["Section 4"] == "Goal 1"
    assert rows[0]["Section 5"] == "Goal 2"
    assert rows[0]["Section 6"] == "Goal 3"
    assert rows[0]["Lesson #"] == 1

    round_trip = convert_planbook_to_facts(rows)
    assert round_trip[0].lesson_name == "First Day Science"
    assert round_trip[0].lesson_plan == "First Day Science\n\nIntro"
    assert round_trip[0].homework_notes == "Read pages 1-2"
    assert round_trip[0].label1 == "Goal 1"
    assert round_trip[0].label2 == "Goal 2"
    assert round_trip[0].label3 == "Goal 3"
    assert round_trip[0].label4 == "Goal 4"


def test_load_facts_csv_extracts_expected_columns():
    csv_text = (
        'LessonName,LessonPlan,HomeworkNotes,Label1,Label2,Label3,Label4\n'
        '"Intro","<p>Lesson</p>","<p>HW</p>","Alpha","Beta","Gamma","Delta"\n'
    )
    file_path = Path("/tmp/facts_sample.csv")
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(csv_text, encoding="utf-8")

    lessons = load_facts_csv(file_path)
    assert len(lessons) == 1
    assert lessons[0].lesson_name == "Intro"
    assert lessons[0].lesson_plan == "<p>Lesson</p>"
    assert lessons[0].homework_notes == "<p>HW</p>"
    assert lessons[0].label1 == "Alpha"
    assert lessons[0].label2 == "Beta"
    assert lessons[0].label3 == "Gamma"
    assert lessons[0].label4 == "Delta"


def test_load_planbook_csv_roundtrip_keeps_fields():
    rows = [
        {
            "Lesson #": 1,
            "Section 1 (Lesson)": "<p>Plan</p>",
            "Section 2 (Homework)": "<p>Work</p>",
            "Section 3 (Notes)": "Notes area",
            "Section 4": "L1",
            "Section 5": "L2",
            "Section 6": "L3",
            "Lesson Title": "Lesson Title",
            "Unit ID": "L4",
            "Unit Title": "",
        }
    ]
    lessons = convert_planbook_to_facts(rows)
    assert lessons[0].lesson_name == "Lesson Title"
    assert lessons[0].lesson_plan == "<p>Plan</p>\n\nNotes area"
    assert lessons[0].homework_notes == "<p>Work</p>"
    assert lessons[0].label1 == "L1"
    assert lessons[0].label2 == "L2"
    assert lessons[0].label3 == "L3"
    assert lessons[0].label4 == "L4"


def test_write_planbook_csv_uses_expected_column_order(tmp_path: Path):
    output_path = tmp_path / "planbook.csv"
    lessons = [
        Lesson(
            lesson_name="Lesson 1",
            lesson_plan="<p>Notes 1</p>",
            homework_notes="<p>Homework 1</p>",
            label1="",
            label2="",
            label3="",
            label4="",
        )
    ]

    write_planbook_csv(output_path, lessons)
    lines = output_path.read_text(encoding="utf-8-sig").splitlines()
    assert lines[0].split(",") == PLANBOOK_FIELDNAMES
