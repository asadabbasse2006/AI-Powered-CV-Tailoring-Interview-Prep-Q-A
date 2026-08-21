from src.ai_cv_assistant.schemas.job import JobProfile
from src.ai_cv_assistant.services.job.jd_pipeline import JDPipeline


class FakeJDExtractor:
    def __init__(self, result: JobProfile):
        self.result = result
        self.last_text = None

    def extract(self, jd_text: str) -> JobProfile:
        self.last_text = jd_text
        return self.result


class FakeJDValidator:
    def __init__(self, result: JobProfile):
        self.result = result
        self.last_extraction = None
        self.last_text = None

    def validate(
        self,
        extraction: JobProfile,
        jd_text: str,
    ) -> JobProfile:
        self.last_extraction = extraction
        self.last_text = jd_text
        return self.result


def create_job() -> JobProfile:
    return JobProfile(
        job_id="job-001",
        url="https://example.com/job",
        title="Backend Developer",
        company="Example Technologies",
        requirements=[],
        keywords=[],
    )


def test_jd_pipeline_processes_job_description():
    extracted_job = create_job()
    validated_job = create_job()

    extractor = FakeJDExtractor(extracted_job)
    validator = FakeJDValidator(validated_job)

    pipeline = JDPipeline(
        extractor=extractor,
        validator=validator,
    )

    jd_text = """
    Backend Developer

    We are looking for a Python developer.
    Experience with FastAPI is preferred.
    """

    result = pipeline.process(jd_text)

    assert result is validated_job
    assert extractor.last_text == jd_text
    assert validator.last_extraction is extracted_job
    assert validator.last_text == jd_text


def test_empty_job_description_is_rejected():
    extractor = FakeJDExtractor(create_job())
    validator = FakeJDValidator(create_job())

    pipeline = JDPipeline(
        extractor=extractor,
        validator=validator,
    )

    try:
        pipeline.process("")
        assert False
    except ValueError as exc:
        assert str(exc) == "Job description text cannot be empty."


def test_non_string_job_description_is_rejected():
    extractor = FakeJDExtractor(create_job())
    validator = FakeJDValidator(create_job())

    pipeline = JDPipeline(
        extractor=extractor,
        validator=validator,
    )

    try:
        pipeline.process(None)
        assert False
    except TypeError as exc:
        assert str(exc) == "Job description text must be a string."