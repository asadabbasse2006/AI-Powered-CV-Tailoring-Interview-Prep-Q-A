from abc import ABC, abstractmethod
from typing import Any


class LLMClient(ABC):

    @abstractmethod
    def generate_structured(
        self,
        prompt: str,
        response_schema: Any | None = None,
    ) -> dict[str, Any]:
        """
        Generate a structured response from an LLM.
        """
        raise NotImplementedError