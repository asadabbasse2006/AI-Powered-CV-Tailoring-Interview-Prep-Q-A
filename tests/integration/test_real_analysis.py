from pathlib import Path

from src.ai_cv_assistant.application import (
    create_analysis_pipeline_from_settings,
)
from src.ai_cv_assistant.config import Settings


def test_real_analysis_pipeline():
    settings = Settings()

    pipeline = create_analysis_pipeline_from_settings(
        settings
    )

    cv_path = Path("tests/fixtures/sample_cv.pdf")

    jd_text = """
    We are looking for a Python Backend Developer.

    Requirements:
    - Python
    - FastAPI
    - SQL
    - REST APIs
    - Git
    - Backend development

    Responsibilities:
    - Develop backend services.
    - Build REST APIs.
    - Work with databases.
    - Collaborate with the development team.
    """

    result = pipeline.analyze(
        cv_file_path=cv_path,
        jd_text=jd_text,
    )

    assert result.candidate is not None
    assert result.job is not None
    assert result.match is not None
    assert result.tailored_cv is not None
    assert result.interview_preparation is not None

    assert result.candidate.name
    assert result.job.title
    assert result.tailored_cv.markdown
    assert result.interview_preparation.questions