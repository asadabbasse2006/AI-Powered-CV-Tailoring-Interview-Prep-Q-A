from src.ai_cv_assistant.schemas.candidate import (
    ConfidenceLevel,
    EvidenceType,
    SkillCategory,
)
from src.ai_cv_assistant.schemas.cv_sections import (
    CVSectionType,
    DetectedCV,
    DetectedCVSection,
)
from src.ai_cv_assistant.services.cv.candidate_extractor import CandidateExtractor


def test_extract_skills():
    cv = DetectedCV(
        sections=[
            DetectedCVSection(
                section_type=CVSectionType.SKILLS,
                heading="Skills",
                content=(
                    "Python\n"
                    "FastAPI\n"
                    "Django\n"
                    "MySQL"
                ),
                order=0,
            )
        ]
    )

    extractor = CandidateExtractor()

    candidate = extractor.extract(cv)

    assert len(candidate.skills) == 4

    skill_names = {
        skill.name
        for skill in candidate.skills
    }

    assert skill_names == {
        "Python",
        "FastAPI",
        "Django",
        "MySQL",
    }


def test_skill_categories():
    cv = DetectedCV(
        sections=[
            DetectedCVSection(
                section_type=CVSectionType.SKILLS,
                heading="Technical Skills",
                content=(
                    "Python\n"
                    "FastAPI\n"
                    "MySQL\n"
                    "Git"
                ),
                order=0,
            )
        ]
    )

    extractor = CandidateExtractor()

    candidate = extractor.extract(cv)

    skills = {
        skill.name: skill.category
        for skill in candidate.skills
    }

    assert skills["Python"] == SkillCategory.PROGRAMMING_LANGUAGE
    assert skills["FastAPI"] == SkillCategory.FRAMEWORK
    assert skills["MySQL"] == SkillCategory.DATABASE
    assert skills["Git"] == SkillCategory.TOOL


def test_skill_evidence_is_created():
    cv = DetectedCV(
        sections=[
            DetectedCVSection(
                section_type=CVSectionType.SKILLS,
                heading="Skills",
                content="Python\nFastAPI",
                order=0,
            )
        ]
    )

    extractor = CandidateExtractor()

    candidate = extractor.extract(cv)

    assert len(candidate.evidence) == 2

    for evidence in candidate.evidence:
        assert evidence.evidence_type == EvidenceType.SKILL
        assert evidence.confidence == ConfidenceLevel.HIGH
        assert evidence.evidence_id


def test_skill_evidence_is_linked():
    cv = DetectedCV(
        sections=[
            DetectedCVSection(
                section_type=CVSectionType.SKILLS,
                heading="Skills",
                content="Python\nFastAPI",
                order=0,
            )
        ]
    )

    extractor = CandidateExtractor()

    candidate = extractor.extract(cv)

    evidence_ids = {
        evidence.evidence_id
        for evidence in candidate.evidence
    }

    for skill in candidate.skills:
        assert len(skill.evidence_ids) == 1
        assert skill.evidence_ids[0] in evidence_ids


def test_comma_separated_skills():
    cv = DetectedCV(
        sections=[
            DetectedCVSection(
                section_type=CVSectionType.SKILLS,
                heading="Skills",
                content="Python, FastAPI, Django, MySQL",
                order=0,
            )
        ]
    )

    extractor = CandidateExtractor()

    candidate = extractor.extract(cv)

    assert len(candidate.skills) == 4


def test_missing_skills_section():
    cv = DetectedCV(
        sections=[
            DetectedCVSection(
                section_type=CVSectionType.EDUCATION,
                heading="Education",
                content="BS Software Engineering",
                order=0,
            )
        ]
    )

    extractor = CandidateExtractor()

    candidate = extractor.extract(cv)

    assert candidate.skills == []
    assert candidate.evidence == []


def test_empty_cv_is_rejected():
    cv = DetectedCV(sections=[])

    extractor = CandidateExtractor()

    try:
        extractor.extract(cv)
        assert False, "Expected ValueError"
    except ValueError:
        pass