import json

import pytest

from src.ai_cv_assistant.services.llm.gemini_client import (
    GeminiLLMClient,
)


def test_empty_api_key_is_rejected():
    with pytest.raises(ValueError):
        GeminiLLMClient(
            api_key="",
        )


def test_empty_model_is_rejected():
    with pytest.raises(ValueError):
        GeminiLLMClient(
            api_key="test-key",
            model="",
        )


def test_empty_prompt_is_rejected():
    client = GeminiLLMClient.__new__(
        GeminiLLMClient
    )

    with pytest.raises(ValueError):
        client.generate_structured("")


def test_non_string_prompt_is_rejected():
    client = GeminiLLMClient.__new__(
        GeminiLLMClient
    )

    with pytest.raises(TypeError):
        client.generate_structured(None)


def test_invalid_json_is_rejected():
    class FakeResponse:
        text = "not valid json"

    class FakeModels:
        def generate_content(self, **kwargs):
            return FakeResponse()

    class FakeClient:
        models = FakeModels()

    client = GeminiLLMClient.__new__(
        GeminiLLMClient
    )

    client.client = FakeClient()
    client.model = "test-model"

    with pytest.raises(ValueError, match="invalid JSON"):
        client.generate_structured(
            "Extract information."
        )


def test_structured_json_is_returned():
    class FakeResponse:
        text = json.dumps(
            {
                "title": "Backend Developer",
                "company": "Example Technologies",
            }
        )

    class FakeModels:
        def generate_content(self, **kwargs):
            return FakeResponse()

    class FakeClient:
        models = FakeModels()

    client = GeminiLLMClient.__new__(
        GeminiLLMClient
    )

    client.client = FakeClient()
    client.model = "test-model"

    result = client.generate_structured(
        "Extract the job information."
    )

    assert result["title"] == "Backend Developer"
    assert result["company"] == "Example Technologies"