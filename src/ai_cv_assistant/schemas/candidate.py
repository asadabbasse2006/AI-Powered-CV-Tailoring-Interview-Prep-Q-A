from datetime import date as Date
from enum import Enum

from pydantic import BaseModel, ConfigDict,Field,HttpUrl

class EvidenceType(str, Enum):
    SKILL = "skill"
    EXPERIENCE = "experience"
    PROJECT = "project"
    EDUCTION = "education"
    CERTIFICATION = "certification"
    ACHIEVEMENT = "achievement"
    OTHER = "other"

class ConfidenceLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Education(BaseModel):
    institution: str
    degree: str | None = None
    field_of_study: str | None = None
    start_date: Date | None = None
    end_date: Date | None = None
    is_current: bool = False
    gpa: str | None = None
    location: str | None = None

    details: list[str] = Field(default_factory=list)

class Experience(BaseModel):
    company: str
    job_title: str
    location: str | None = None
    start_date: Date | None = None
    end_date: Date | None = None
    is_current: bool = False
    description: str | None = None

    responsibilities: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    achievements: list[str] = Field(default_factory=list)

class Project(BaseModel):
    name: str
    description: str | None = None
    technologies: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
    features: list[str] = Field(default_factory=list)
    results: list[str] = Field(default_factory=list)

    repository_url: HttpUrl | None = None
    demo_url: HttpUrl | None = None

class SkillCategory(str, Enum):
    PROGRAMMING_LANGUAGE = "programming_language"
    FRAMEWORK = "framework"
    LIBRARY = "library"
    DATABASE = "database"
    CLOUD ="cloud"
    DEVOPS ="devops"
    TOOL = "tool"
    METHODOLOGY = "methodology"
    SOFT_SKILL = "soft_skill"
    OTHER = "other"

class Skill(BaseModel):
    name: str
    category: SkillCategory = SkillCategory.OTHER
    evidence_ids: list[str] = Field(default_factory=list)

class Certification(BaseModel):
    name: str
    issuing_organization: str | None = None
    issue_date: Date | None = None
    expiry_date: Date | None = None
    credential_id: str | None = None
    credential_url: HttpUrl | None = None

class Achievement(BaseModel):
    title: str
    description: str | None = None
    date: Date | None = None

class CandidateEvidence(BaseModel):
    evidence_id: str
    evidence_type: EvidenceType
    claim: str
    evidence_text: str
    source_section: str | None = None
    source_reference: str | None = None
    confidence: ConfidenceLevel = ConfidenceLevel.HIGH

class CandidateProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")
    candidate_id: str | None = None
    name: str
    email: str | None = None
    phone: str | None = None
    location: str | None = None

    linkedin_url: HttpUrl | None = None
    github_url: HttpUrl | None = None
    portfolio_url: HttpUrl | None = None

    summary: str | None = None

    education: list[Education] = Field(default_factory=list)
    experience: list[Experience] = Field(default_factory=list)
    project: list[Project] = Field(default_factory=list)
    skills: list[Skill] = Field(default_factory=list)
    certifications: list[Certification] = Field(default_factory=list)
    achievements: list[Achievement] = Field(default_factory=list)
    evidence: list[CandidateEvidence] = Field(default_factory=list)