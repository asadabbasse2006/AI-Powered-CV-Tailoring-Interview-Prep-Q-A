from src.ai_cv_assistant.schemas.candidate import (
    CandidateEvidence,
    CandidateProfile,
    EvidenceType,
)
from src.ai_cv_assistant.schemas.job import (
    JobProfile,
    JobRequirement,
    RequirementCategory,
    RequirementImportance,
)
from src.ai_cv_assistant.schemas.matching import (
    CandidateJobMatch,
    MatchSummary,
)
from src.ai_cv_assistant.services.job.job_pipeline import JobPipeline


class FakeJDExtractor:
    def __init__(self, job):
        self.job = job
        self.received_text = None

    def extract(self, jd_text):
        self.received_text = jd_text
        return self.job


class FakeJDValidator:
    def __init__(self, job=None):
        self.job = job
        self.received_job = None
        self.received_text = None

    def validate(self, job, jd_text):
        self.received_job = job
        self.received_text = jd_text

        return self.job or job


class FakeMatchEngine:
    def __init__(self, result=None):
        self.result = result or CandidateJobMatch(
            results=[],
            summary=MatchSummary(
                total_requirements=0,
                strong_matches=0,
                partial_matches=0,
                no_evidence=0,
                conflicts=0,
                score=0.0,
            ),
        )

        self.received_candidate = None
        self.received_job = None

    def match(self, candidate, job):
        self.received_candidate = candidate
        self.received_job = job

        return self.result


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
                source_text="Python",
            )
        ],
        keywords=[],
    )


def create_candidate():
    return CandidateProfile(
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


def test_job_pipeline_runs_all_stages():
    job = create_job()
    candidate = create_candidate()

    extractor = FakeJDExtractor(job)
    validator = FakeJDValidator()
    matcher = FakeMatchEngine()

    pipeline = JobPipeline(
        jd_extractor=extractor,
        jd_validator=validator,
        match_engine=matcher,
    )

    jd_text = """
    Backend Developer

    We are looking for a Python developer.
    """

    result_job, result_match = pipeline.analyze(
        jd_text,
        candidate,
    )

    assert result_job == job
    assert isinstance(result_match, CandidateJobMatch)

    assert extractor.received_text == jd_text
    assert validator.received_job == job
    assert validator.received_text == jd_text

    assert matcher.received_candidate == candidate
    assert matcher.received_job == job


def test_pipeline_returns_validated_job():
    extracted_job = create_job()

    validated_job = JobProfile(
        job_id="job-validated",
        url="https://example.com/validated",
        title="Senior Backend Developer",
        company="Validated Company",
        requirements=[],
        keywords=[],
    )

    candidate = create_candidate()

    extractor = FakeJDExtractor(extracted_job)
    validator = FakeJDValidator(validated_job)
    matcher = FakeMatchEngine()

    pipeline = JobPipeline(
        jd_extractor=extractor,
        jd_validator=validator,
        match_engine=matcher,
    )

    result_job, _ = pipeline.analyze(
        "Backend Developer",
        candidate,
    )

    assert result_job == validated_job
    assert matcher.received_job == validated_job


def test_pipeline_passes_candidate_to_match_engine():
    job = create_job()
    candidate = create_candidate()

    extractor = FakeJDExtractor(job)
    validator = FakeJDValidator()
    matcher = FakeMatchEngine()

    pipeline = JobPipeline(
        jd_extractor=extractor,
        jd_validator=validator,
        match_engine=matcher,
    )

    pipeline.analyze(
        "Python Backend Developer",
        candidate,
    )

    assert matcher.received_candidate is candidate


def test_empty_jd_is_rejected():
    pipeline = JobPipeline(
        jd_extractor=FakeJDExtractor(create_job()),
        jd_validator=FakeJDValidator(),
        match_engine=FakeMatchEngine(),
    )

    candidate = create_candidate()

    try:
        pipeline.analyze("", candidate)
        assert False
    except ValueError as exc:
        assert "empty" in str(exc).lower()


def test_non_string_jd_is_rejected():
    pipeline = JobPipeline(
        jd_extractor=FakeJDExtractor(create_job()),
        jd_validator=FakeJDValidator(),
        match_engine=FakeMatchEngine(),
    )

    candidate = create_candidate()

    try:
        pipeline.analyze(123, candidate)
        assert False
    except TypeError as exc:
        assert "string" in str(exc).lower()


def test_invalid_candidate_is_rejected():
    pipeline = JobPipeline(
        jd_extractor=FakeJDExtractor(create_job()),
        jd_validator=FakeJDValidator(),
        match_engine=FakeMatchEngine(),
    )

    try:
        pipeline.analyze(
            "Backend Developer",
            None,
        )
        assert False
    except TypeError as exc:
        assert "candidate" in str(exc).lower()