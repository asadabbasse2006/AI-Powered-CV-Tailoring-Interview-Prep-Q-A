import pytest

from src.ai_cv_assistant.schemas.candidate import (
    EvidenceType,
    SkillCategory,
)
from src.ai_cv_assistant.schemas.extraction import CVExtractionResult
from src.ai_cv_assistant.services.cv.extraction_validator import (
    ExtractionValidator,
)


CV_TEXT = """
Asad Abbas

Software Engineering student.

Skills:
Python
FastAPI
Django

Experience:
Software Engineering Intern
Fantech Labs

Projects:
AI CV Assistant
"""


@pytest.fixture
def validator():
    return ExtractionValidator()


def test_valid_extraction_creates_candidate_profile(validator):
    extraction = CVExtractionResult(
        name="Asad Abbas",
        email="asad@example.com",
        skills=[],
    )

    result = validator.validate(extraction, CV_TEXT)

    assert result.name == "Asad Abbas"
    assert result.email == "asad@example.com"


def test_missing_optional_fields_are_allowed(validator):
    extraction = CVExtractionResult(
        name="Asad Abbas",
    )

    result = validator.validate(extraction, CV_TEXT)

    assert result.name == "Asad Abbas"
    assert result.email is None
    assert result.phone is None
    assert result.skills == []
    assert result.evidence == []


def test_skill_receives_evidence(validator):
    extraction = CVExtractionResult(
        name="Asad Abbas",
        skills=[
            {
                "name": "Python",
                "category": SkillCategory.PROGRAMMING_LANGUAGE,
            }
        ],
    )

    result = validator.validate(extraction, CV_TEXT)

    assert len(result.skills) == 1
    assert result.skills[0].name == "Python"

    assert len(result.evidence) == 1

    evidence = result.evidence[0]

    assert evidence.evidence_type == EvidenceType.SKILL
    assert evidence.claim == "Python"
    assert evidence.evidence_id in result.skills[0].evidence_ids


def test_skill_evidence_contains_cv_text(validator):
    extraction = CVExtractionResult(
        name="Asad Abbas",
        skills=[
            {
                "name": "Python",
                "category": SkillCategory.PROGRAMMING_LANGUAGE,
            }
        ],
    )

    result = validator.validate(extraction, CV_TEXT)

    assert CV_TEXT.strip() in result.evidence[0].evidence_text


def test_multiple_skills_receive_separate_evidence(validator):
    extraction = CVExtractionResult(
        name="Asad Abbas",
        skills=[
            {
                "name": "Python",
                "category": SkillCategory.PROGRAMMING_LANGUAGE,
            },
            {
                "name": "FastAPI",
                "category": SkillCategory.FRAMEWORK,
            },
        ],
    )

    result = validator.validate(extraction, CV_TEXT)

    assert len(result.skills) == 2
    assert len(result.evidence) == 2

    evidence_ids = {
        evidence.evidence_id
        for evidence in result.evidence
    }

    assert len(evidence_ids) == 2

    for skill in result.skills:
        assert len(skill.evidence_ids) == 1
        assert skill.evidence_ids[0] in evidence_ids


def test_experience_creates_evidence(validator):
    extraction = CVExtractionResult(
        name="Asad Abbas",
        experience=[
            {
                "company": "Fantech Labs",
                "job_title": "Software Engineering Intern",
            }
        ],
    )

    result = validator.validate(extraction, CV_TEXT)

    assert len(result.experience) == 1
    assert len(result.evidence) == 1

    evidence = result.evidence[0]

    assert evidence.evidence_type == EvidenceType.EXPERIENCE
    assert "Software Engineering Intern" in evidence.claim
    assert "Fantech Labs" in evidence.claim


def test_project_creates_evidence(validator):
    extraction = CVExtractionResult(
        name="Asad Abbas",
        projects=[
            {
                "name": "AI CV Assistant",
            }
        ],
    )

    result = validator.validate(extraction, CV_TEXT)

    assert len(result.project) == 1
    assert result.project[0].name == "AI CV Assistant"

    assert len(result.evidence) == 1

    evidence = result.evidence[0]

    assert evidence.evidence_type == EvidenceType.PROJECT
    assert evidence.claim == "AI CV Assistant"


def test_candidate_fields_are_preserved(validator):
    extraction = CVExtractionResult(
        name="Asad Abbas",
        email="asad@example.com",
        phone="+92 300 1234567",
        location="Pakistan",
        summary="Software Engineering student.",
    )

    result = validator.validate(extraction, CV_TEXT)

    assert result.name == extraction.name
    assert result.email == extraction.email
    assert result.phone == extraction.phone
    assert result.location == extraction.location
    assert result.summary == extraction.summary


def test_empty_cv_text_is_rejected(validator):
    extraction = CVExtractionResult(
        name="Asad Abbas",
    )

    with pytest.raises(ValueError):
        validator.validate(extraction, "")


def test_whitespace_cv_text_is_rejected(validator):
    extraction = CVExtractionResult(
        name="Asad Abbas",
    )

    with pytest.raises(ValueError):
        validator.validate(extraction, "   ")


def test_invalid_extraction_type_is_rejected(validator):
    with pytest.raises(TypeError):
        validator.validate(
            {"name": "Asad Abbas"},
            CV_TEXT,
        )