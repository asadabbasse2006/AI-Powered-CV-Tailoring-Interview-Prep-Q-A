import pytest

from src.ai_cv_assistant.services.cv.extraction_validator import (
    ExtractionValidator,
)


@pytest.fixture
def validator():
    return ExtractionValidator()