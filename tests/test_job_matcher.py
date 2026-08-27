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
    MatchConfidence,
    MatchStatus,
)
from src.ai_cv_assistant.services.matching.job_matcher import (
    JobMatcher,
)


def create_candidate() -> CandidateProfile:
    return CandidateProfile(
        candidate_id="candidate-001",
        name="Asad Abbas",
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


def create_job(
    requirements: list[dict],
) -> JobProfile:

    return JobProfile(
        job_id="job-001",
        url="https://example.com/jobs/backend-developer",
        title="Backend Developer",
        company="Example Technologies",
        requirements=[
            JobRequirement(**requirement)
            for requirement in requirements
        ],
    )


def test_direct_skill_match():
    candidate = create_candidate()

    job = create_job(
        [
            {
                "requirement_id": "requirement-001",
                "name": "Python",
                "category": RequirementCategory.TECHNICAL_SKILL,
                "importance": RequirementImportance.REQUIRED,
            }
        ]
    )

    matcher = JobMatcher()

    result = matcher.match(candidate, job)

    assert len(result.results) == 1

    match = result.results[0]

    assert match.status == MatchStatus.STRONG_MATCH
    assert match.confidence == MatchConfidence.HIGH
    assert match.candidate_evidence_ids == [
        "evidence-001"
    ]


def test_matching_is_case_insensitive():
    candidate = create_candidate()

    job = create_job(
        [
            {
                "requirement_id": "requirement-001",
                "name": "python",
                "category": RequirementCategory.TECHNICAL_SKILL,
                "importance": RequirementImportance.REQUIRED,
            }
        ]
    )

    matcher = JobMatcher()

    result = matcher.match(candidate, job)

    assert result.results[0].status == MatchStatus.STRONG_MATCH


def test_missing_requirement_has_no_evidence():
    candidate = create_candidate()

    job = create_job(
        [
            {
                "requirement_id": "requirement-001",
                "name": "AWS",
                "category": RequirementCategory.TECHNICAL_SKILL,
                "importance": RequirementImportance.REQUIRED,
            }
        ]
    )

    matcher = JobMatcher()

    result = matcher.match(candidate, job)

    match = result.results[0]

    assert match.status == MatchStatus.NO_EVIDENCE
    assert match.confidence == MatchConfidence.LOW
    assert match.candidate_evidence_ids == []


def test_related_evidence_creates_partial_match():
    candidate = CandidateProfile(
        candidate_id="candidate-001",
        name="Asad Abbas",
        evidence=[
            CandidateEvidence(
                evidence_id="evidence-001",
                evidence_type=EvidenceType.PROJECT,
                claim="Python backend development",
                evidence_text=(
                    "Developed backend applications using Python."
                ),
            )
        ],
    )

    job = create_job(
        [
            {
                "requirement_id": "requirement-001",
                "name": "Python",
                "category": RequirementCategory.TECHNICAL_SKILL,
                "importance": RequirementImportance.REQUIRED,
            }
        ]
    )

    matcher = JobMatcher()

    result = matcher.match(candidate, job)

    match = result.results[0]

    assert match.status == MatchStatus.PARTIAL_MATCH
    assert match.confidence == MatchConfidence.MEDIUM
    assert match.candidate_evidence_ids == [
        "evidence-001"
    ]


def test_multiple_requirements_are_matched():
    candidate = create_candidate()

    job = create_job(
        [
            {
                "requirement_id": "requirement-001",
                "name": "Python",
                "category": RequirementCategory.TECHNICAL_SKILL,
                "importance": RequirementImportance.REQUIRED,
            },
            {
                "requirement_id": "requirement-002",
                "name": "FastAPI",
                "category": RequirementCategory.TECHNICAL_SKILL,
                "importance": RequirementImportance.PREFERRED,
            },
            {
                "requirement_id": "requirement-003",
                "name": "AWS",
                "category": RequirementCategory.TECHNICAL_SKILL,
                "importance": RequirementImportance.PREFERRED,
            },
        ]
    )

    matcher = JobMatcher()

    result = matcher.match(candidate, job)

    assert len(result.results) == 3

    assert (
        result.results[0].status
        == MatchStatus.STRONG_MATCH
    )

    assert (
        result.results[1].status
        == MatchStatus.STRONG_MATCH
    )

    assert (
        result.results[2].status
        == MatchStatus.NO_EVIDENCE
    )


def test_match_summary_is_calculated():
    candidate = create_candidate()

    job = create_job(
        [
            {
                "requirement_id": "requirement-001",
                "name": "Python",
                "category": RequirementCategory.TECHNICAL_SKILL,
                "importance": RequirementImportance.REQUIRED,
            },
            {
                "requirement_id": "requirement-002",
                "name": "FastAPI",
                "category": RequirementCategory.TECHNICAL_SKILL,
                "importance": RequirementImportance.PREFERRED,
            },
            {
                "requirement_id": "requirement-003",
                "name": "AWS",
                "category": RequirementCategory.TECHNICAL_SKILL,
                "importance": RequirementImportance.PREFERRED,
            },
        ]
    )

    matcher = JobMatcher()

    result = matcher.match(candidate, job)

    assert result.summary.total_requirements == 3
    assert result.summary.strong_matches == 2
    assert result.summary.partial_matches == 0
    assert result.summary.no_evidence == 1
    assert result.summary.conflicts == 0


def test_invalid_candidate_is_rejected():
    matcher = JobMatcher()

    job = create_job([])

    try:
        matcher.match(None, job)
        assert False, "Expected TypeError"
    except TypeError as exc:
        assert str(exc) == (
            "candidate must be a CandidateProfile."
        )


def test_invalid_job_is_rejected():
    matcher = JobMatcher()

    candidate = create_candidate()

    try:
        matcher.match(candidate, None)
        assert False, "Expected TypeError"
    except TypeError as exc:
        assert str(exc) == (
            "job must be a JobProfile."
        )