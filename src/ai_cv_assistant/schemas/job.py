from enum import Enum

from pydantic import BaseModel,ConfigDict,HttpUrl,Field

class RequirementCategory(str, Enum):
    TECHNICAL_SKILL = "technical_skill"
    EXPERIENCE = "experience"
    EDUCATION = "education"
    RESPONSIBILITY = "responsibility"
    CERTIFICATION = "certification"
    SOFT_SKILL = "soft_skill"
    OTHER = "other"

class RequirementImportance(str, Enum):
    REQUIRED = "required"
    PREFERRED = "preferred"

class JobRequirement(BaseModel):
    requirement_id: str
    name: str

    category: RequirementCategory
    importance: RequirementImportance

    description: str | None = None
    source_text: str | None = None

class JobKeyword(BaseModel):
    keyword: str
    importance: int = Field(default=1,ge=1,le=10)
    source_text: str | None = None

class JobProfile(BaseModel):
    model_config= ConfigDict(extra="forbid")
    job_id: str | None = None
    url: HttpUrl
    title: str | None = None
    company: str | None = None
    location: str | None = None
    employment_type: str | None = None
    description: str | None = None

    responsibilities: list[str] | None = Field(default_factory=list)
    requirements: list[JobRequirement] | None = Field(default_factory=list)
    preferred_qualifications: list[str] | None = Field(default_factory=list)
    education_requirements: list[str] | None = Field(default_factory=list)
    experience_requirements: list[str] | None = Field(default_factory=list)
    keywords: list[JobKeyword] = Field(default_factory=list)

