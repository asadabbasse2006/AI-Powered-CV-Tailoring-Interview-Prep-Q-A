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

from src.ai_cv_assistant.services.job.match_engine import MatchEngine

def create_candidate(
    skills: list[str] | None = None,
) -> CandidateProfile:
    if skills is None:
        skills = ["Python", "FastAPI"]

    candidate_skills = [
        Skill(
            name=skill,
            category=SkillCategory.PROGRAMMING_LANGUAGE,
            evidence_ids=[f"evidence-{skill.lower()}"],
        )
        for skill in skills
    ]

    evidence = [
        CandidateEvidence(
            evidence_id=f"evidence-{skill.lower()}",
            evidence_type=EvidenceType.SKILL,
            claim=skill,
            evidence_text=skill,
        )
        for skill in skills
    ]

    return CandidateProfile(
        candidate_id="candidate-001",
        name="Asad Abbas",
        skills=candidate_skills,
        evidence=evidence,
    )
def create_job(
    requirements: list[str] | None = None,
) -> JobProfile:
    if requirements is None:
        requirements = ["Python", "FastAPI", "Docker"]

    job_requirements = [
        JobRequirement(
            requirement_id=f"requirement-{index}",
            name=requirement,
            category=RequirementCategory.TECHNICAL_SKILL,
            importance=RequirementImportance.REQUIRED,
            source_text=requirement,
        )
        for index, requirement in enumerate(requirements, start=1)
    ]

    return JobProfile(
        job_id="job-001",
        url="https://example.com/job",
        title="Backend Developer",
        company="Example Technologies",
        requirements=job_requirements,
        keywords=[],
    )


def test_partial_match_is_detected():
    candidate = CandidateProfile(
        candidate_id="candidate-001",
        name="Asad Abbas",
        evidence=[
            CandidateEvidence(
                evidence_id="evidence-001",
                evidence_type=EvidenceType.PROJECT,
                claim="FastAPI backend development",
                evidence_text=(
                    "Developed backend APIs using FastAPI."
                ),
            )
        ],
    )

    job = JobProfile(
        job_id="job-001",
        url="https://example.com/job",
        title="Backend Developer",
        requirements=[
            JobRequirement(
                requirement_id="requirement-001",
                name="backend",
                category=RequirementCategory.TECHNICAL_SKILL,
                importance=RequirementImportance.REQUIRED,
            )
        ],
    )

    engine = MatchEngine()

    result = engine.match(candidate, job)

    assert result.results[0].status == MatchStatus.PARTIAL_MATCH
    assert result.results[0].confidence == MatchConfidence.MEDIUM
    assert result.results[0].candidate_evidence_ids == [
        "evidence-001"
    ]


def test_exact_match_has_higher_confidence_than_partial_match():
    candidate = CandidateProfile(
        candidate_id="candidate-001",
        name="Asad Abbas",
        evidence=[
            CandidateEvidence(
                evidence_id="evidence-001",
                evidence_type=EvidenceType.SKILL,
                claim="Python",
                evidence_text="Python",
            )
        ],
    )

    job = JobProfile(
        job_id="job-001",
        url="https://example.com/job",
        title="Backend Developer",
        requirements=[
            JobRequirement(
                requirement_id="requirement-001",
                name="Python",
                category=RequirementCategory.TECHNICAL_SKILL,
                importance=RequirementImportance.REQUIRED,
            )
        ],
    )

    engine = MatchEngine()

    result = engine.match(candidate, job)

    assert result.results[0].status == MatchStatus.STRONG_MATCH
    assert result.results[0].confidence == MatchConfidence.HIGH

def test_match_score_is_calculated():
    engine = MatchEngine()

    result = engine.match(
        create_candidate(),
        create_job(),
    )

    assert result.summary.score == 66.67


def test_perfect_match_has_score_100():
    candidate = create_candidate()

    job = JobProfile(
        job_id="job-001",
        url="https://example.com/job",
        title="Backend Developer",
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
                importance=RequirementImportance.REQUIRED,
            ),
        ],
    )

    engine = MatchEngine()

    result = engine.match(candidate, job)

    assert result.summary.score == 100.0


def test_no_evidence_has_score_zero():
    candidate = CandidateProfile(
        candidate_id="candidate-001",
        name="Asad Abbas",
    )

    job = create_job()

    engine = MatchEngine()

    result = engine.match(candidate, job)

    assert result.summary.score == 0.0