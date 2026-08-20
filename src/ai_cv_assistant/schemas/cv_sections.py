from enum import Enum
from typing import Any

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

    def __len__(self) -> int:
        """Return the number of detected CV sections."""
        return len(self.sections)

    def __getitem__(self, index: int) -> DetectedCVSection:
        """Allow list-style indexing of detected sections."""
        return self.sections[index]

    def __iter__(self):
        """Allow iteration directly over detected sections."""
        return iter(self.sections)

    def __eq__(self, other: Any) -> bool:
        """
        Support comparison with both DetectedCV and list objects.

        This preserves compatibility with existing section-detector
        tests while retaining header_text metadata.
        """
        if isinstance(other, list):
            return self.sections == other

        return super().__eq__(other)