from enum import Enum

from pydantic import BaseModel,Field

class CVSectionType(str, Enum):
    SUMMARY = "summary"
    SKILLS = "skills"
    EXPERIENCE = "experience"
    PROJECTS = "projects"
    EDUCATION = "education"
    CERTIFICATIONS = "certifications"
    ACHIEVEMENTS = "achievements"
    OTHER = "other"

class GeneratedClaim(BaseModel):
    claim_id: str
    content: str
    evidence_ids: list[str] = Field(default_factory=list)
    supported: bool = False

    validation_reason: str | None = None

class CVSection(BaseModel):
    section_type: CVSectionType

    title: str
    order:int

    content: str | None = None
    evidence_ids: list[str] = Field(default_factory=list)
    claims: list[GeneratedClaim] = Field(default_factory=list)

class CVValidationStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    NEED_REVISION = "need_revision"

class CVValidationResult(BaseModel):
    status: CVValidationStatus
    unsupported_claim_ids: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    revision_count: int = 0

class TailoredCV(BaseModel):
    candidate_name: str
    target_job_title: str | None = None
    target_company: str | None = None
    sections: list[CVSection] = Field(default_factory=list)
    markdown: str
    validation: CVValidationResult
