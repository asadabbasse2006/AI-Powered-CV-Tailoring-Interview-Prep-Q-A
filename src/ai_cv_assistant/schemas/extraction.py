from pydantic import BaseModel, ConfigDict, Field

from src.ai_cv_assistant.schemas.candidate import (
    Achievement,
    Certification,
    Education,
    Experience,
    Project,
    Skill,
)


class CVExtractionResult(BaseModel):
    """
    Structured information extracted from a CV by an LLM.

    This represents the LLM's interpretation of the CV.
    It is not yet considered fully trusted candidate data.
    """

    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None

    linkedin_url: str | None = None
    github_url: str | None = None
    portfolio_url: str | None = None

    summary: str | None = None

    education: list[Education] = Field(default_factory=list)
    experience: list[Experience] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)
    skills: list[Skill] = Field(default_factory=list)
    certifications: list[Certification] = Field(default_factory=list)
    achievements: list[Achievement] = Field(default_factory=list)