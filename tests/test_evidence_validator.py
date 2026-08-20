import pytest

from src.ai_cv_assistant.schemas.candidate import (
    CandidateEvidence,
    CandidateProfile,
    EvidenceType,
    Skill,
    SkillCategory,
)

from src.ai_cv_assistant.services.cv.evidence_validator import (
    EvidenceValidationError,
    EvidenceValidator,
)

def test_valid_skill_evidence():
    candidate = CandidateProfile(
        name="Asad Abbas",
        skills=[
            Skill(
                name="Python",
                category=SkillCategory.PROGRAMMING_LANGUAGE,
                evidence_ids=["evidence-001"],
            )
        ],
        evidence=[
            CandidateEvidence(
                evidence_id="evidence-001",
                evidence_type=EvidenceType.SKILL,
                claim="Python experience",
                evidence_text="Developed applications using Python.",
            )
        ],
    )

    result = EvidenceValidator().validate(candidate)

    assert result == candidate

def test_unknown_evidence_id_is_rejected():
    candidate = CandidateProfile(
        name="Asad Abbas",
        skills=[
            Skill(
                name="Python",
                category=SkillCategory.PROGRAMMING_LANGUAGE,
                evidence_ids=["evidence-does-not-exist"],
            )
        ],
    )

    with pytest.raises(EvidenceValidationError):
        EvidenceValidator().validate(candidate)

def test_skill_without_evidence_is_rejected():
    candidate = CandidateProfile(
        name="Asad Abbas",
        skills=[
            Skill(
                name="Python",
                category=SkillCategory.PROGRAMMING_LANGUAGE,
            )
        ],
    )

    with pytest.raises(EvidenceValidationError):
        EvidenceValidator().validate(candidate)

def test_empty_evidence_text_is_rejected():
    candidate = CandidateProfile(
        name="Asad Abbas",
        skills=[
            Skill(
                name="Python",
                category=SkillCategory.PROGRAMMING_LANGUAGE,
                evidence_ids=["evidence-001"],
            )
        ],
        evidence=[
            CandidateEvidence(
                evidence_id="evidence-001",
                evidence_type=EvidenceType.SKILL,
                claim="Python experience",
                evidence_text="   ",
            )
        ],
    )

    with pytest.raises(EvidenceValidationError):
        EvidenceValidator().validate(candidate)

