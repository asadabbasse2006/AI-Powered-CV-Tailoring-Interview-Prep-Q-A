import pytest

from src.ai_cv_assistant.services.llm.client import LLMClient


def test_llm_client_cannot_be_instantiated():
    with pytest.raises(TypeError):
        LLMClient()


def test_llm_client_requires_generate_structured():
    class IncompleteClient(LLMClient):
        pass

    with pytest.raises(TypeError):
        IncompleteClient()