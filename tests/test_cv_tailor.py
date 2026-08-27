from src.ai_cv_assistant.schemas.candidate import (
    CandidateEvidence,
    CandidateProfile,
    EvidenceType,
    Skill,
    SkillCategory,
)
from src.ai_cv_assistant.schemas.job import (
    JobProfile,
    JobRequirement,
    RequirementCategory,
    RequirementImportance,
)
from src.ai_cv_assistant.schemas.matching import (
    CandidateJobMatch,
    MatchConfidence,
    MatchResult,
    MatchStatus,
    MatchSummary,
)
from src.ai_cv_assistant.services.cv.cv_tailor import CVTailor


def create_candidate():
    return CandidateProfile(
        candidate_id="candidate-001",
        name="Asad Abbas",
        email="asad@example.com",
        summary=(
            "Software engineering student "
            "interested in backend development."
        ),
        skills=[
            Skill(
                name="Python",
                category=SkillCategory.PROGRAMMING_LANGUAGE,
                evidence_ids=["evidence-001"],
            ),
            Skill(
                name="FastAPI",
                category=SkillCategory.FRAMEWORK,
                evidence_ids=["evidence-002"],
            ),
        ],
        evidence=[
            CandidateEvidence(
                evidence_id="evidence-001",
                evidence_type=EvidenceType.SKILL,
                claim="Python",
                evidence_text="Python",
            ),
            CandidateEvidence(
                evidence_id="evidence-002",
                evidence_type=EvidenceType.SKILL,
                claim="FastAPI",
                evidence_text="FastAPI",
            ),
        ],
    )


def create_job():
    return JobProfile(
        job_id="job-001",
        url="https://example.com/job",
        title="Backend Developer",
        company="Example Technologies",
        requirements=[
            JobRequirement(
                requirement_id="requirement-001",
                name="Python",
                category=RequirementCategory.TECHNICAL_SKILL,
                importance=RequirementImportance.REQUIRED,
            ),
            JobRequirement(
                requirement_id="requirement-002",
                name="FastAPI",
                category=RequirementCategory.TECHNICAL_SKILL,
                importance=RequirementImportance.PREFERRED,
            ),
        ],
    )


def create_match():
    return CandidateJobMatch(
        results=[
            MatchResult(
                requirement_id="requirement-001",
                candidate_evidence_ids=["evidence-001"],
                status=MatchStatus.STRONG_MATCH,
                confidence=MatchConfidence.HIGH,
                reason="Direct Python evidence.",
            ),
            MatchResult(
                requirement_id="requirement-002",
                candidate_evidence_ids=["evidence-002"],
                status=MatchStatus.STRONG_MATCH,
                confidence=MatchConfidence.HIGH,
                reason="Direct FastAPI evidence.",
            ),
        ],
        summary=MatchSummary(
            total_requirements=2,
            strong_matches=2,
        ),
    )


def test_tailor_creates_targeted_cv():
    tailor = CVTailor()

    result = tailor.tailor(
        candidate=create_candidate(),
        job=create_job(),
        match=create_match(),
    )

    assert result.candidate_name == "Asad Abbas"
    assert result.target_job_title == "Backend Developer"
    assert result.target_company == "Example Technologies"


def test_tailor_keeps_supported_skills():
    result = CVTailor().tailor(
        create_candidate(),
        create_job(),
        create_match(),
    )

    skills_section = next(
        section
        for section in result.sections
        if section.title == "Skills"
    )

    assert "Python" in skills_section.content
    assert "FastAPI" in skills_section.content


def test_skill_claims_contain_evidence():
    result = CVTailor().tailor(
        create_candidate(),
        create_job(),
        create_match(),
    )

    skills_section = next(
        section
        for section in result.sections
        if section.title == "Skills"
    )

    python_claim = next(
        claim
        for claim in skills_section.claims
        if claim.content == "Python"
    )

    assert python_claim.supported is True
    assert "evidence-001" in python_claim.evidence_ids


def test_markdown_contains_candidate_information():
    result = CVTailor().tailor(
        create_candidate(),
        create_job(),
        create_match(),
    )

    assert "# Asad Abbas" in result.markdown
    assert "asad@example.com" in result.markdown
    assert "Python" in result.markdown
    assert "FastAPI" in result.markdown


def test_invalid_candidate_is_rejected():
    try:
        CVTailor().tailor(
            None,
            create_job(),
            create_match(),
        )
        assert False, "Expected TypeError"
    except TypeError as exc:
        assert str(exc) == (
            "candidate must be a CandidateProfile."
        )


def test_invalid_job_is_rejected():
    try:
        CVTailor().tailor(
            create_candidate(),
            None,
            create_match(),
        )
        assert False, "Expected TypeError"
    except TypeError as exc:
        assert str(exc) == (
            "job must be a JobProfile."
        )


def test_invalid_match_is_rejected():
    try:
        CVTailor().tailor(
            create_candidate(),
            create_job(),
            None,
        )
        assert False, "Expected TypeError"
    except TypeError as exc:
        assert str(exc) == (
            "match must be a CandidateJobMatch."
        )