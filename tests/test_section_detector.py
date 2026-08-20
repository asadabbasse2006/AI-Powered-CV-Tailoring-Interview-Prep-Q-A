import pytest

from src.ai_cv_assistant.schemas.cv_sections import CVSectionType
from src.ai_cv_assistant.services.cv.section_detector import CVSectionDetector


@pytest.fixture
def detector():
    return CVSectionDetector()


def test_detect_common_sections(detector):
    text = """
John Doe

SUMMARY
Software engineer interested in backend development.

SKILLS
Python
FastAPI
Django

EXPERIENCE
Software Engineering Intern
Worked on backend services.

EDUCATION
BS Software Engineering
COMSATS University Islamabad
"""

    sections = detector.detect(text)

    assert len(sections) == 4

    assert sections[0].section_type == CVSectionType.SUMMARY
    assert sections[1].section_type == CVSectionType.SKILLS
    assert sections[2].section_type == CVSectionType.EXPERIENCE
    assert sections[3].section_type == CVSectionType.EDUCATION


def test_detect_section_content(detector):
    text = """
SKILLS
Python
FastAPI
Django
"""

    sections = detector.detect(text)

    assert len(sections) == 1

    section = sections[0]

    assert section.section_type == CVSectionType.SKILLS
    assert section.heading == "SKILLS"
    assert "Python" in section.content
    assert "FastAPI" in section.content
    assert "Django" in section.content


@pytest.mark.parametrize(
    ("heading", "expected_type"),
    [
        ("SUMMARY", CVSectionType.SUMMARY),
        ("Professional Summary", CVSectionType.SUMMARY),
        ("PROFILE", CVSectionType.SUMMARY),
        ("WORK EXPERIENCE", CVSectionType.EXPERIENCE),
        ("Professional Experience", CVSectionType.EXPERIENCE),
        ("Employment History", CVSectionType.EXPERIENCE),
        ("EDUCATION", CVSectionType.EDUCATION),
        ("Academic Background", CVSectionType.EDUCATION),
        ("PROJECTS", CVSectionType.PROJECTS),
        ("Personal Projects", CVSectionType.PROJECTS),
        ("SKILLS", CVSectionType.SKILLS),
        ("Technical Skills", CVSectionType.SKILLS),
        ("CERTIFICATIONS", CVSectionType.CERTIFICATIONS),
        ("Certificates", CVSectionType.CERTIFICATIONS),
        ("ACHIEVEMENTS", CVSectionType.ACHIEVEMENTS),
        ("Awards", CVSectionType.ACHIEVEMENTS),
        ("LANGUAGES", CVSectionType.LANGUAGES),
        ("INTERESTS", CVSectionType.INTERESTS),
    ],
)
def test_detect_section_aliases(
    detector,
    heading,
    expected_type,
):
    sections = detector.detect(
        f"{heading}\nSome section content."
    )

    assert len(sections) == 1
    assert sections[0].section_type == expected_type


def test_detect_heading_with_colon(detector):
    text = """
SKILLS:
Python
FastAPI
"""

    sections = detector.detect(text)

    assert len(sections) == 1
    assert sections[0].section_type == CVSectionType.SKILLS


def test_detect_heading_case_insensitive(detector):
    text = """
professional experience
Software Engineering Intern
"""

    sections = detector.detect(text)

    assert len(sections) == 1
    assert sections[0].section_type == CVSectionType.EXPERIENCE


def test_detect_multiple_sections_and_order(detector):
    text = """
EDUCATION
BS Software Engineering

PROJECTS
Patient Management System

SKILLS
Python
FastAPI

CERTIFICATIONS
Python Certificate
"""

    sections = detector.detect(text)

    assert len(sections) == 4

    assert sections[0].order == 0
    assert sections[1].order == 1
    assert sections[2].order == 2
    assert sections[3].order == 3


def test_unknown_headings_are_not_guessed(detector):
    text = """
John Doe

WHAT I HAVE DONE
Built several software projects.

RANDOM SECTION
Some information.
"""

    sections = detector.detect(text)

    assert sections == []


def test_empty_text_is_rejected(detector):
    with pytest.raises(ValueError):
        detector.detect("")


def test_whitespace_only_text_is_rejected(detector):
    with pytest.raises(ValueError):
        detector.detect("   \n\n   ")


def test_non_string_input_is_rejected(detector):
    with pytest.raises(TypeError):
        detector.detect(None)

def test_detect_header_text(detector):
    text = """
Asad Abbas
Software Engineer
asad@example.com

SKILLS
Python
FastAPI
"""

    cv = detector.detect(text)

    assert cv.header_text == (
        "Asad Abbas\n"
        "Software Engineer\n"
        "asad@example.com"
    )