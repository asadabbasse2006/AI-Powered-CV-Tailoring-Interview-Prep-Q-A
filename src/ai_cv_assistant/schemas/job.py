from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator


class RequirementCategory(str, Enum):
    """Categories used to classify job requirements."""

    TECHNICAL_SKILL = "technical_skill"
    EXPERIENCE = "experience"
    EDUCATION = "education"
    RESPONSIBILITY = "responsibility"
    CERTIFICATION = "certification"
    SOFT_SKILL = "soft_skill"
    CLOUD = "cloud"
    OTHER = "other"


class RequirementImportance(str, Enum):
    """Importance of a job requirement."""

    REQUIRED = "required"
    PREFERRED = "preferred"


class JobRequirement(BaseModel):
    """A structured requirement extracted from a job description."""

    model_config = ConfigDict(extra="forbid")

    requirement_id: str = Field(
        default_factory=lambda: f"requirement-{uuid4()}"
    )

    name: str

    category: RequirementCategory

    importance: RequirementImportance = (
        RequirementImportance.PREFERRED
    )

    description: str | None = None
    source_text: str | None = None

    @model_validator(mode="before")
    @classmethod
    def normalize_required_field(cls, data):
        """
        Support the simplified LLM extraction format:

        {
            "name": "Python",
            "category": "technical_skill",
            "required": True
        }

        and convert it into the canonical importance field.
        """

        if not isinstance(data, dict):
            return data

        data = dict(data)

        if "required" in data and "importance" not in data:
            data["importance"] = (
                RequirementImportance.REQUIRED
                if data.pop("required")
                else RequirementImportance.PREFERRED
            )
        else:
            data.pop("required", None)

        return data


class JobKeyword(BaseModel):
    """A keyword extracted from a job description."""

    model_config = ConfigDict(extra="forbid")

    keyword: str

    importance: int = 1

    category: str | None = None

    source_text: str | None = None


class JobProfile(BaseModel):
    """Structured representation of a job description."""

    model_config = ConfigDict(extra="forbid")

    job_id: str = Field(
        default_factory=lambda: f"job-{uuid4()}"
    )

    url: str | None = None

    title: str | None = None
    company: str | None = None
    location: str | None = None

    employment_type: str | None = None

    description: str | None = None

    responsibilities: list[str] = Field(
        default_factory=list
    )

    requirements: list[JobRequirement] = Field(
        default_factory=list
    )

    keywords: list[JobKeyword] = Field(
        default_factory=list
    )