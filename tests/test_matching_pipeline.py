from src.ai_cv_assistant.schemas.candidate import (
    CandidateProfile,
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
    MatchStatus,
)
from src.ai_cv_assistant.services.matching.matching_pipeline import (
    MatchingPipeline,
)


class FakeJobMatcher:
    def __init__(self, result: CandidateJobMatch):
        self.result = result
        self.last_candidate = None
        self.last_job = None

    def match(
        self,
        candidate: CandidateProfile,
        job: JobProfile,
    ) -> CandidateJobMatch:
        self.last_candidate = candidate
        self.last_job = job
        return self.result


def create_candidate() -> CandidateProfile:
    return CandidateProfile(
        candidate_id="candidate-001",
        name="Asad Abbas",
        skills=[
            Skill(
                name="Python",
                category=SkillCategory.PROGRAMMING_LANGUAGE,
                evidence_ids=["evidence-001"],
            )
        ],
    )


def create_job() -> JobProfile:
    return JobProfile(
        job_id="job-001",
        url="https://example.com/jobs/backend-developer",
        title="Backend Developer",
        company="Example Technologies",
        requirements=[
            JobRequirement(
                requirement_id="requirement-001",
                name="Python",
                category=RequirementCategory.TECHNICAL_SKILL,
                importance=RequirementImportance.REQUIRED,
            )
        ],
    )


def create_match_result() -> CandidateJobMatch:
    from src.ai_cv_assistant.schemas.matching import (
        MatchResult,
        MatchSummary,
    )

    return CandidateJobMatch(
        results=[
            MatchResult(
                requirement_id="requirement-001",
                candidate_evidence_ids=["evidence-001"],
                status=MatchStatus.STRONG_MATCH,
                confidence=MatchConfidence.HIGH,
                reason="Direct Python evidence found.",
            )
        ],
        summary=MatchSummary(
            total_requirements=1,
            strong_matches=1,
        ),
    )


def test_matching_pipeline_processes_candidate_and_job():
    candidate = create_candidate()
    job = create_job()
    expected_result = create_match_result()

    matcher = FakeJobMatcher(expected_result)

    pipeline = MatchingPipeline(
        matcher=matcher,
    )

    result = pipeline.process(
        candidate=candidate,
        job=job,
    )

    assert result is expected_result
    assert matcher.last_candidate is candidate
    assert matcher.last_job is job


def test_matching_pipeline_returns_candidate_job_match():
    candidate = create_candidate()
    job = create_job()
    expected_result = create_match_result()

    matcher = FakeJobMatcher(expected_result)

    pipeline = MatchingPipeline(matcher)

    result = pipeline.process(candidate, job)

    assert isinstance(
        result,
        CandidateJobMatch,
    )

    assert result.summary.total_requirements == 1
    assert result.summary.strong_matches == 1


def test_matching_pipeline_rejects_invalid_candidate():
    matcher = FakeJobMatcher(
        create_match_result()
    )

    pipeline = MatchingPipeline(matcher)

    try:
        pipeline.process(
            candidate=None,
            job=create_job(),
        )
        assert False, "Expected TypeError"
    except TypeError as exc:
        assert str(exc) == (
            "candidate must be a CandidateProfile."
        )


def test_matching_pipeline_rejects_invalid_job():
    matcher = FakeJobMatcher(
        create_match_result()
    )

    pipeline = MatchingPipeline(matcher)

    try:
        pipeline.process(
            candidate=create_candidate(),
            job=None,
        )
        assert False, "Expected TypeError"
    except TypeError as exc:
        assert str(exc) == (
            "job must be a JobProfile."
        )


def test_matching_pipeline_does_not_call_matcher_for_invalid_candidate():
    matcher = FakeJobMatcher(
        create_match_result()
    )

    pipeline = MatchingPipeline(matcher)

    try:
        pipeline.process(
            candidate=None,
            job=create_job(),
        )
        assert False, "Expected TypeError"
    except TypeError:
        pass

    assert matcher.last_candidate is None
    assert matcher.last_job is None