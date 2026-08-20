from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class CVSectionType(str, Enum):
    SUMMARY = "summary"
    EXPERIENCE = "experience"
    EDUCATION = "education"
    PROJECTS = "projects"
    SKILLS = "skills"
    CERTIFICATIONS = "certifications"
    ACHIEVEMENTS = "achievements"
    INTERESTS = "interests"
    LANGUAGES = "languages"
    CONTACT = "contact"
    OTHER = "other"


class DetectedCVSection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    section_type: CVSectionType
    heading: str
    content: str = ""
    order: int = Field(ge=0)

class DetectedCV(BaseModel):
    model_config = ConfigDict(extra="forbid")

    header_text: str = ""
    sections: list[DetectedCVSection] = Field(default_factory=list)