from typing import Any, Protocol

from src.ai_cv_assistant.schemas.extraction import CVExtractionResult


class LLMClient(Protocol):
    """Interface required from an LLM client."""

    def generate_structured(self, prompt: str) -> dict[str, Any]:
        ...


class CVExtractor:
    """Extract structured candidate information from CV text using an LLM."""

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def extract(self, cv_text: str) -> CVExtractionResult:
        if not isinstance(cv_text, str):
            raise TypeError("CV text must be a string.")

        if not cv_text.strip():
            raise ValueError("CV text cannot be empty.")

        prompt = self._build_prompt(cv_text)

        response = self.llm_client.generate_structured(prompt,response_schema=CVExtractionResult)

        return CVExtractionResult.model_validate(response)

    @staticmethod
    def _build_prompt(cv_text: str) -> str:
        return f"""
You are a CV information extraction system.

Your task is to extract structured information from the candidate's CV.

The CV is the ONLY source of truth.

STRICT RULES:

1. Extract information ONLY when it is supported by the CV.
2. NEVER invent skills.
3. NEVER invent work experience.
4. NEVER invent projects.
5. NEVER invent education.
6. NEVER invent certifications.
7. NEVER invent achievements.
8. NEVER invent dates.
9. NEVER invent job titles.
10. NEVER invent companies.
11. NEVER invent technologies.
12. NEVER invent performance metrics.
13. NEVER infer proficiency levels that are not explicitly stated.
14. NEVER convert a project into employment experience.
15. NEVER convert coursework into professional experience.
16. NEVER use information from your general knowledge.
17. If information is not present, return null or an empty list.
18. Preserve the meaning of the candidate's original claims.
19. Do not exaggerate the candidate's experience.
20. Do not rewrite the CV for a job.
21. This step is extraction only.

IMPORTANT:

Extraction and inference are different.

Example:

CV:
"Developed a backend application using Python and FastAPI."

Valid extraction:
- Python
- FastAPI
- Backend application

Invalid extraction:
- Django
- Flask
- AWS
- Docker
- 3 years of Python experience

The invalid information MUST NOT be added.

Return only information supported by the CV.

CV:
--------------------
{cv_text}
--------------------
""".strip()