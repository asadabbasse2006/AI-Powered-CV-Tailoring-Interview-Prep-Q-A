from pathlib import Path

import pytest

from src.ai_cv_assistant.schemas.candidate import CandidateProfile
from src.ai_cv_assistant.schemas.cv import (
    CVValidationResult,
    CVValidationStatus,
    TailoredCV,
)
from src.ai_cv_assistant.schemas.interview import InterviewPreparation
from src.ai_cv_assistant.schemas.job import JobProfile
from src.ai_cv_assistant.schemas.matching import CandidateJobMatch
from src.ai_cv_assistant.schemas.processing import (
    AnalysisResult,
    ProcessingStatus,
)
from src.ai_cv_assistant.services.analysis.analysis_pipeline import (
    AnalysisPipeline,
)


class FakeCVPipeline:
    def __init__(self, candidate):
        self.candidate = candidate
        self.received_path = None

    def process_file(self, file_path):
        self.received_path = file_path
        return self.candidate


class FakeJDPipeline:
    def __init__(self, job):
        self.job = job
        self.received_text = None

    def process(self, jd_text):
        self.received_text = jd_text
        return self.job


class FakeMatchingPipeline:
    def __init__(self, match):
        self.match = match
        self.received_candidate = None
        self.received_job = None

    def process(self, candidate, job):
        self.received_candidate = candidate
        self.received_job = job
        return self.match


class FakeCVTailor:
    def __init__(self, tailored_cv):
        self.tailored_cv = tailored_cv
        self.received_candidate = None
        self.received_job = None
        self.received_match = None

    def tailor(self, candidate, job, match):
        self.received_candidate = candidate
        self.received_job = job
        self.received_match = match
        return self.tailored_cv


class FakeInterviewPreparer:
    def __init__(self, interview_preparation):
        self.interview_preparation = interview_preparation
        self.received_candidate = None
        self.received_job = None
        self.received_match = None
        self.received_tailored_cv = None

    def prepare(
        self,
        candidate,
        job,
        match,
        tailored_cv,
    ):
        self.received_candidate = candidate
        self.received_job = job
        self.received_match = match
        self.received_tailored_cv = tailored_cv

        return self.interview_preparation


@pytest.fixture
def candidate():
    return CandidateProfile(
        candidate_id="candidate-001",
        name="Asad Abbas",
    )


@pytest.fixture
def job():
    return JobProfile(
        job_id="job-001",
        title="Backend Developer",
        company="Example Technologies",
    )


@pytest.fixture
def match():
    return CandidateJobMatch(
        results=[],
    )


@pytest.fixture
def tailored_cv():
    return TailoredCV(
        candidate_name="Asad Abbas",
        target_job_title="Backend Developer",
        target_company="Example Technologies",
        sections=[],
        markdown="# Asad Abbas",
        validation=CVValidationResult(
            status=CVValidationStatus.PASSED,
            unsupported_claim_ids=[],
            warnings=[],
            revision_count=0,
        ),
    )


@pytest.fixture
def interview_preparation():
    return InterviewPreparation(
        questions=[],
        answers=[],
    )


@pytest.fixture
def pipeline(
    candidate,
    job,
    match,
    tailored_cv,
    interview_preparation,
):
    return AnalysisPipeline(
        cv_pipeline=FakeCVPipeline(candidate),
        jd_pipeline=FakeJDPipeline(job),
        matching_pipeline=FakeMatchingPipeline(match),
        cv_tailor=FakeCVTailor(tailored_cv),
        interview_preparer=FakeInterviewPreparer(
            interview_preparation
        ),
        model_name="test-model",
    )


def test_analysis_pipeline_returns_complete_result(
    pipeline,
):
    result = pipeline.analyze(
        cv_file_path="candidate.pdf",
        jd_text="Backend Developer position.",
    )

    assert isinstance(result, AnalysisResult)

    assert result.candidate.name == "Asad Abbas"

    assert result.job.title == "Backend Developer"

    assert result.match is not None

    assert result.tailored_cv.candidate_name == "Asad Abbas"

    assert result.interview_preparation is not None


def test_analysis_pipeline_sets_completed_status(
    pipeline,
):
    result = pipeline.analyze(
        cv_file_path="candidate.pdf",
        jd_text="Backend Developer position.",
    )

    assert (
        result.metadata.status
        == ProcessingStatus.COMPLETED
    )


def test_analysis_pipeline_generates_request_id(
    pipeline,
):
    result = pipeline.analyze(
        cv_file_path="candidate.pdf",
        jd_text="Backend Developer position.",
    )

    assert result.metadata.request_id.startswith(
        "request-"
    )


def test_analysis_pipeline_records_completion_time(
    pipeline,
):
    result = pipeline.analyze(
        cv_file_path="candidate.pdf",
        jd_text="Backend Developer position.",
    )

    assert result.metadata.created_at is not None

    assert result.metadata.completed_at is not None

    assert (
        result.metadata.completed_at
        >= result.metadata.created_at
    )


def test_analysis_pipeline_records_processing_time(
    pipeline,
):
    result = pipeline.analyze(
        cv_file_path="candidate.pdf",
        jd_text="Backend Developer position.",
    )

    assert (
        result.metadata.processing_time_seconds
        is not None
    )

    assert (
        result.metadata.processing_time_seconds
        >= 0
    )


def test_analysis_pipeline_passes_cv_path_to_cv_pipeline(
    candidate,
    job,
    match,
    tailored_cv,
    interview_preparation,
):
    cv_pipeline = FakeCVPipeline(candidate)

    pipeline = AnalysisPipeline(
        cv_pipeline=cv_pipeline,
        jd_pipeline=FakeJDPipeline(job),
        matching_pipeline=FakeMatchingPipeline(match),
        cv_tailor=FakeCVTailor(tailored_cv),
        interview_preparer=FakeInterviewPreparer(
            interview_preparation
        ),
    )

    pipeline.analyze(
        cv_file_path="candidate.pdf",
        jd_text="Backend Developer.",
    )

    assert cv_pipeline.received_path == "candidate.pdf"


def test_analysis_pipeline_passes_job_description(
    candidate,
    job,
    match,
    tailored_cv,
    interview_preparation,
):
    jd_pipeline = FakeJDPipeline(job)

    pipeline = AnalysisPipeline(
        cv_pipeline=FakeCVPipeline(candidate),
        jd_pipeline=jd_pipeline,
        matching_pipeline=FakeMatchingPipeline(match),
        cv_tailor=FakeCVTailor(tailored_cv),
        interview_preparer=FakeInterviewPreparer(
            interview_preparation
        ),
    )

    jd_text = "Python Backend Developer."

    pipeline.analyze(
        cv_file_path="candidate.pdf",
        jd_text=jd_text,
    )

    assert jd_pipeline.received_text == jd_text


def test_analysis_pipeline_passes_match_to_cv_tailor(
    candidate,
    job,
    match,
    tailored_cv,
    interview_preparation,
):
    cv_tailor = FakeCVTailor(tailored_cv)

    pipeline = AnalysisPipeline(
        cv_pipeline=FakeCVPipeline(candidate),
        jd_pipeline=FakeJDPipeline(job),
        matching_pipeline=FakeMatchingPipeline(match),
        cv_tailor=cv_tailor,
        interview_preparer=FakeInterviewPreparer(
            interview_preparation
        ),
    )

    pipeline.analyze(
        cv_file_path="candidate.pdf",
        jd_text="Backend Developer.",
    )

    assert cv_tailor.received_candidate is candidate
    assert cv_tailor.received_job is job
    assert cv_tailor.received_match is match


def test_analysis_pipeline_passes_tailored_cv_to_interview_preparer(
    candidate,
    job,
    match,
    tailored_cv,
    interview_preparation,
):
    interview_preparer = FakeInterviewPreparer(
        interview_preparation
    )

    pipeline = AnalysisPipeline(
        cv_pipeline=FakeCVPipeline(candidate),
        jd_pipeline=FakeJDPipeline(job),
        matching_pipeline=FakeMatchingPipeline(match),
        cv_tailor=FakeCVTailor(tailored_cv),
        interview_preparer=interview_preparer,
    )

    pipeline.analyze(
        cv_file_path="candidate.pdf",
        jd_text="Backend Developer.",
    )

    assert (
        interview_preparer.received_candidate
        is candidate
    )

    assert (
        interview_preparer.received_job
        is job
    )

    assert (
        interview_preparer.received_match
        is match
    )

    assert (
        interview_preparer.received_tailored_cv
        is tailored_cv
    )


def test_invalid_cv_path_type_is_rejected(
    pipeline,
):
    with pytest.raises(
        TypeError,
        match="cv_file_path",
    ):
        pipeline.analyze(
            cv_file_path=123,
            jd_text="Backend Developer.",
        )


def test_empty_cv_path_is_rejected(
    pipeline,
):
    with pytest.raises(
        ValueError,
        match="cv_file_path",
    ):
        pipeline.analyze(
            cv_file_path="",
            jd_text="Backend Developer.",
        )


def test_invalid_jd_type_is_rejected(
    pipeline,
):
    with pytest.raises(
        TypeError,
        match="jd_text",
    ):
        pipeline.analyze(
            cv_file_path="candidate.pdf",
            jd_text=123,
        )


def test_empty_jd_is_rejected(
    pipeline,
):
    with pytest.raises(
        ValueError,
        match="jd_text",
    ):
        pipeline.analyze(
            cv_file_path="candidate.pdf",
            jd_text="",
        )


def test_cv_pipeline_error_is_propagated(
    candidate,
    job,
    match,
    tailored_cv,
    interview_preparation,
):
    class FailingCVPipeline:
        def process_file(self, file_path):
            raise RuntimeError(
                "CV processing failed."
            )

    pipeline = AnalysisPipeline(
        cv_pipeline=FailingCVPipeline(),
        jd_pipeline=FakeJDPipeline(job),
        matching_pipeline=FakeMatchingPipeline(match),
        cv_tailor=FakeCVTailor(tailored_cv),
        interview_preparer=FakeInterviewPreparer(
            interview_preparation
        ),
    )

    with pytest.raises(
        RuntimeError,
        match="CV processing failed",
    ):
        pipeline.analyze(
            cv_file_path="candidate.pdf",
            jd_text="Backend Developer.",
        )


def test_jd_pipeline_error_is_propagated(
    candidate,
    match,
    tailored_cv,
    interview_preparation,
):
    class FailingJDPipeline:
        def process(self, jd_text):
            raise RuntimeError(
                "JD processing failed."
            )

    pipeline = AnalysisPipeline(
        cv_pipeline=FakeCVPipeline(candidate),
        jd_pipeline=FailingJDPipeline(),
        matching_pipeline=FakeMatchingPipeline(match),
        cv_tailor=FakeCVTailor(tailored_cv),
        interview_preparer=FakeInterviewPreparer(
            interview_preparation
        ),
    )

    with pytest.raises(
        RuntimeError,
        match="JD processing failed",
    ):
        pipeline.analyze(
            cv_file_path="candidate.pdf",
            jd_text="Backend Developer.",
        )