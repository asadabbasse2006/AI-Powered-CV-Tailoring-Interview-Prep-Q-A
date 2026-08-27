from src.ai_cv_assistant.application import (
    create_analysis_pipeline,
)
from src.ai_cv_assistant.services.analysis.analysis_pipeline import (
    AnalysisPipeline,
)
from src.ai_cv_assistant.config import Settings
from src.ai_cv_assistant.application import (
    create_analysis_pipeline_from_settings,
)

def test_create_analysis_pipeline():
    pipeline = create_analysis_pipeline(
        api_key="test-api-key",
    )

    assert isinstance(
        pipeline,
        AnalysisPipeline,
    )


def test_create_analysis_pipeline_uses_requested_model():
    pipeline = create_analysis_pipeline(
        api_key="test-api-key",
        model="test-model",
    )

    assert pipeline.model_name == "test-model"


def test_create_analysis_pipeline_creates_cv_pipeline():
    pipeline = create_analysis_pipeline(
        api_key="test-api-key",
    )

    assert pipeline.cv_pipeline is not None


def test_create_analysis_pipeline_creates_jd_pipeline():
    pipeline = create_analysis_pipeline(
        api_key="test-api-key",
    )

    assert pipeline.jd_pipeline is not None


def test_create_analysis_pipeline_creates_matching_pipeline():
    pipeline = create_analysis_pipeline(
        api_key="test-api-key",
    )

    assert pipeline.matching_pipeline is not None


def test_create_analysis_pipeline_creates_cv_tailor():
    pipeline = create_analysis_pipeline(
        api_key="test-api-key",
    )

    assert pipeline.cv_tailor is not None


def test_create_analysis_pipeline_creates_interview_preparer():
    pipeline = create_analysis_pipeline(
        api_key="test-api-key",
    )

    assert pipeline.interview_preparer is not None

def test_create_analysis_pipeline_from_settings(
    monkeypatch,
):
    monkeypatch.setenv(
        "GEMINI_API_KEY",
        "test-api-key",
    )

    monkeypatch.setenv(
        "GEMINI_MODEL",
        "test-model",
    )

    settings = Settings()

    pipeline = create_analysis_pipeline_from_settings(
        settings
    )

    assert pipeline.model_name == "test-model"