from typing import Any

from src.ai_cv_assistant.services.llm.client import LLMClient
from src.ai_cv_assistant.services.job.jd_extractor import JDExtractor


class FakeLLMClient(LLMClient):
    def __init__(self, response: dict[str, Any]):
        self.response = response
        self.last_prompt: str | None = None

    def generate_structured(
        self,
        prompt: str,
        response_schema: Any = None,
    ) -> dict[str, Any]:
        self.last_prompt = prompt
        return self.response


def test_extract_job_description():
    response = {
        "title": "Backend Developer",
        "company": "Example Technologies",
        "requirements": [
            {
                "name": "Python",
                "category": "technical_skill",
                "required": True,
            }
        ],
        "keywords": [
            {
                "keyword": "FastAPI",
                "category": "technology",
            }
        ],
    }

    llm = FakeLLMClient(response)

    extractor = JDExtractor(llm)

    result = extractor.extract(
        """
        Backend Developer

        We are looking for a Python developer
        with experience in FastAPI.
        """
    )

    assert result.title == "Backend Developer"
    assert result.company == "Example Technologies"

    assert len(result.requirements) == 1
    assert result.requirements[0].name == "Python"

    assert len(result.keywords) == 1
    assert result.keywords[0].keyword == "FastAPI"


def test_jd_text_is_included_in_prompt():
    llm = FakeLLMClient(
        {
            "title": "Backend Developer",
        }
    )

    extractor = JDExtractor(llm)

    jd_text = """
    Backend Developer
    Python
    FastAPI
    PostgreSQL
    """

    extractor.extract(jd_text)

    assert llm.last_prompt is not None
    assert jd_text in llm.last_prompt


def test_missing_fields_are_allowed():
    llm = FakeLLMClient(
        {
            "title": "Python Developer",
        }
    )

    extractor = JDExtractor(llm)

    result = extractor.extract(
        "Python Developer"
    )

    assert result.title == "Python Developer"
    assert result.company is None
    assert result.requirements == []
    assert result.keywords == []


def test_empty_jd_is_rejected():
    llm = FakeLLMClient({})

    extractor = JDExtractor(llm)

    try:
        extractor.extract("")
    except ValueError as exc:
        assert str(exc) == "Job description text cannot be empty."
    else:
        raise AssertionError(
            "Expected ValueError for empty job description."
        )


def test_whitespace_only_jd_is_rejected():
    llm = FakeLLMClient({})

    extractor = JDExtractor(llm)

    try:
        extractor.extract("   \n\t   ")
    except ValueError as exc:
        assert str(exc) == "Job description text cannot be empty."
    else:
        raise AssertionError(
            "Expected ValueError for whitespace-only job description."
        )


def test_non_string_jd_is_rejected():
    llm = FakeLLMClient({})

    extractor = JDExtractor(llm)

    try:
        extractor.extract(None)
    except TypeError as exc:
        assert str(exc) == "Job description text must be a string."
    else:
        raise AssertionError(
            "Expected TypeError for non-string job description."
        )