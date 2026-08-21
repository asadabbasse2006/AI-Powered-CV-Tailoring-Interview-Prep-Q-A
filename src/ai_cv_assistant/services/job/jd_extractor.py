from typing import Any
from uuid import uuid4

from src.ai_cv_assistant.schemas.job import (
    JobKeyword,
    JobProfile,
    JobRequirement,
    RequirementCategory,
    RequirementImportance,
)
from src.ai_cv_assistant.services.llm.client import LLMClient


from src.ai_cv_assistant.schemas.job import JobProfile
from src.ai_cv_assistant.services.llm.client import LLMClient


class JDExtractor:

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def extract(self, jd_text: str) -> JobProfile:

        if not isinstance(jd_text, str):
            raise TypeError(
                "Job description text must be a string."
            )

        if not jd_text.strip():
            raise ValueError(
                "Job description text cannot be empty."
            )

        prompt = self._build_prompt(jd_text)

        response = self.llm_client.generate_structured(
            prompt,
            response_schema=JobProfile,
        )

        if not isinstance(response, dict):
            raise TypeError(
                "LLM response must be a dictionary."
            )

        return JobProfile.model_validate(response)

    def _build_prompt(self, jd_text: str) -> str:
        return f"""
You are an expert job-description extraction system.

Extract structured information from the job description below.

Rules:

1. Extract only information explicitly supported by the text.
2. Do not invent requirements.
3. Extract the job title and company if available.
4. Extract technical and non-technical requirements.
5. Extract important technologies and keywords.
6. Preserve the meaning of the original job description.
7. If optional information is unavailable, leave it empty.

JOB DESCRIPTION:

{jd_text}
"""

    def _build_job_profile(
        self,
        response: dict[str, Any],
    ) -> JobProfile:
        """
        Convert the raw LLM response into a JobProfile.
        """

        requirements = self._build_requirements(
            response.get("requirements", [])
        )

        keywords = self._build_keywords(
            response.get("keywords", [])
        )

        return JobProfile(
            job_id=response.get(
                "job_id",
                f"job-{uuid4()}",
            ),
            url=response.get("url"),
            title=response.get("title"),
            company=response.get("company"),
            location=response.get("location"),
            employment_type=response.get(
                "employment_type"
            ),
            description=response.get("description"),
            responsibilities=response.get(
                "responsibilities",
                [],
            ),
            requirements=requirements,
            keywords=keywords,
        )

    @staticmethod
    def _build_requirements(
        raw_requirements: Any,
    ) -> list[JobRequirement]:
        """
        Normalize raw LLM requirements.
        """

        if not isinstance(raw_requirements, list):
            return []

        requirements: list[JobRequirement] = []

        for item in raw_requirements:
            if not isinstance(item, dict):
                continue

            name = item.get("name")

            if not isinstance(name, str) or not name.strip():
                continue

            category = JDExtractor._parse_requirement_category(
                item.get("category")
            )

            importance = JDExtractor._parse_requirement_importance(
                item
            )

            requirements.append(
                JobRequirement(
                    requirement_id=item.get(
                        "requirement_id",
                        f"requirement-{uuid4()}",
                    ),
                    name=name,
                    category=category,
                    importance=importance,
                    description=item.get(
                        "description"
                    ),
                    source_text=item.get(
                        "source_text"
                    ),
                )
            )

        return requirements

    @staticmethod
    def _build_keywords(
        raw_keywords: Any,
    ) -> list[JobKeyword]:
        """
        Normalize raw LLM keywords.
        """

        if not isinstance(raw_keywords, list):
            return []

        keywords: list[JobKeyword] = []

        for item in raw_keywords:
            if not isinstance(item, dict):
                continue

            keyword = item.get("keyword")

            if not isinstance(keyword, str) or not keyword.strip():
                continue

            importance = item.get(
                "importance",
                1,
            )

            try:
                importance = int(importance)
            except (TypeError, ValueError):
                importance = 1

            keywords.append(
                JobKeyword(
                    keyword=keyword,
                    importance=importance,
                    source_text=item.get(
                        "source_text"
                    ),
                )
            )

        return keywords

    @staticmethod
    def _parse_requirement_category(
        value: Any,
    ) -> RequirementCategory:
        """
        Convert an LLM category into RequirementCategory.
        """

        if isinstance(value, RequirementCategory):
            return value

        if isinstance(value, str):
            try:
                return RequirementCategory(value)
            except ValueError:
                pass

        return RequirementCategory.OTHER

    @staticmethod
    def _parse_requirement_importance(
        item: dict[str, Any],
    ) -> RequirementImportance:
        """
        Convert the LLM's `required` field into the application's
        RequirementImportance enum.
        """

        if "importance" in item:
            value = item["importance"]

            if isinstance(
                value,
                RequirementImportance,
            ):
                return value

            if isinstance(value, str):
                try:
                    return RequirementImportance(value)
                except ValueError:
                    pass

        required = item.get("required")

        if required is True:
            return RequirementImportance.REQUIRED

        if required is False:
            return RequirementImportance.PREFERRED

        return RequirementImportance.PREFERRED