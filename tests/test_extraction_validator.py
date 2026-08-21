import pytest

from src.ai_cv_assistant.schemas.candidate import SkillCategory
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

Education:
BS Software Engineering
COMSATS University Islamabad
""".strip()


def test_unsupported_skill_is_rejected(validator):
    extraction = CVExtractionResult(
        name="Asad Abbas",
        skills=[
            {
                "name": "Python",
                "category": SkillCategory.PROGRAMMING_LANGUAGE,
            },
            {
                "name": "AWS",
                "category": SkillCategory.CLOUD,
            },
        ],
    )

    result = validator.validate(
        extraction,
        CV_TEXT,
    )

    skill_names = [
        skill.name
        for skill in result.skills
    ]

    assert "Python" in skill_names
    assert "AWS" not in skill_names


def test_unsupported_skill_does_not_create_evidence(validator):
    extraction = CVExtractionResult(
        name="Asad Abbas",
        skills=[
            {
                "name": "AWS",
                "category": SkillCategory.CLOUD,
            }
        ],
    )

    result = validator.validate(
        extraction,
        CV_TEXT,
    )

    assert result.skills == []
    assert result.evidence == []


def test_skill_evidence_is_specific_to_claim(validator):
    extraction = CVExtractionResult(
        name="Asad Abbas",
        skills=[
            {
                "name": "Python",
                "category": SkillCategory.PROGRAMMING_LANGUAGE,
            }
        ],
    )

    result = validator.validate(
        extraction,
        CV_TEXT,
    )

    evidence = result.evidence[0]

    assert evidence.claim == "Python"
    assert evidence.evidence_text == "Python"
    assert evidence.evidence_text != CV_TEXT.strip()