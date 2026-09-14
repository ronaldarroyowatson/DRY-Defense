import csv
from pathlib import Path

from lesson_converter_app.converter import (
    Lesson,
    convert_facts_to_planbook,
    convert_planbook_to_facts,
    load_facts_csv,
    load_planbook_csv,
)


def test_facts_to_planbook_roundtrip_preserves_fields():
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

    file_path = Path("/tmp/facts_to_planbook.csv")
    rows = convert_facts_to_planbook(lessons)
    assert rows[0]["Lesson Title"] == "First Day Science"
    assert rows[0]["Section 1 (Lesson)"] == "<p>Intro</p>"
    assert rows[0]["Section 2 (Homework)"] == "<p>Read pages 1-2</p>"
    assert rows[0]["Section 4"] == "Goal 1"
    assert rows[0]["Section 5"] == "Goal 2"
    assert rows[0]["Section 6"] == "Goal 3"
    assert rows[0]["Lesson #"] == 1

    round_trip = convert_planbook_to_facts(rows)
    assert round_trip[0].lesson_name == "First Day Science"
    assert round_trip[0].lesson_plan == "<p>Intro</p>"
    assert round_trip[0].homework_notes == "<p>Read pages 1-2</p>"
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
    assert lessons[0].lesson_plan == "<p>Plan</p>"
    assert lessons[0].homework_notes == "<p>Work</p>"
    assert lessons[0].label1 == "L1"
    assert lessons[0].label2 == "L2"
    assert lessons[0].label3 == "L3"
    assert lessons[0].label4 == "L4"
