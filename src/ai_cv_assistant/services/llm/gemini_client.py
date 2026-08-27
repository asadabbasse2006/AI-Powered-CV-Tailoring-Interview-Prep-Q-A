import json
from typing import Any

from google import genai
from google.genai import types

from src.ai_cv_assistant.services.llm.client import LLMClient


class GeminiLLMClient(LLMClient):
    """
    Gemini implementation of the application's LLM client.

    Responsible only for communication with Gemini.
    Business validation is handled by application services.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.5-flash",
    ) -> None:
        if not api_key:
            raise ValueError("Gemini API key cannot be empty.")

        if not model:
            raise ValueError("Gemini model cannot be empty.")

        self.model = model

        self.client = genai.Client(
            api_key=api_key,
        )

    def generate_structured(
        self,
        prompt: str,
        response_schema: Any | None = None,
    ) -> dict[str, Any]:

        if not isinstance(prompt, str):
            raise TypeError("Prompt must be a string.")

        if not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        config_kwargs: dict[str, Any] = {
            "temperature": 0,
        }

        if response_schema is not None:
            if hasattr(response_schema, "model_json_schema"):
                response_json_schema = (
                    response_schema.model_json_schema()
                )
            else:
                response_json_schema = response_schema

            config_kwargs.update(
                {
                    "response_mime_type": "application/json",
                    "response_json_schema": response_json_schema,
                }
            )

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                **config_kwargs,
            ),
        )

        if not response.text:
            raise ValueError(
                "Gemini returned an empty response."
            )

        try:
            result = json.loads(response.text)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "Gemini returned invalid JSON."
            ) from exc

        if not isinstance(result, dict):
            raise TypeError(
                "Gemini structured response must be a dictionary."
            )

        return result