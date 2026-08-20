import re

from src.ai_cv_assistant.schemas.cv_sections import (
    CVSectionType,
    DetectedCV,
    DetectedCVSection,
)


class CVSectionDetector:
    """Detect common CV sections from cleaned text."""

    SECTION_ALIASES = {
        CVSectionType.SUMMARY: {
            "summary",
            "professional summary",
            "profile",
            "professional profile",
            "career summary",
            "objective",
            "career objective",
        },
        CVSectionType.EXPERIENCE: {
            "experience",
            "work experience",
            "professional experience",
            "employment history",
            "work history",
            "professional background",
        },
        CVSectionType.EDUCATION: {
            "education",
            "educational background",
            "academic background",
            "academic qualifications",
            "qualifications",
        },
        CVSectionType.PROJECTS: {
            "projects",
            "personal projects",
            "academic projects",
            "key projects",
            "selected projects",
        },
        CVSectionType.SKILLS: {
            "skills",
            "technical skills",
            "technical expertise",
            "technical competencies",
            "core competencies",
            "key skills",
        },
        CVSectionType.CERTIFICATIONS: {
            "certifications",
            "certificates",
            "professional certifications",
            "licenses & certifications",
        },
        CVSectionType.ACHIEVEMENTS: {
            "achievements",
            "accomplishments",
            "awards",
            "honors",
            "honors & awards",
        },
        CVSectionType.INTERESTS: {
            "interests",
            "hobbies",
            "interests & hobbies",
        },
        CVSectionType.LANGUAGES: {
            "languages",
            "language skills",
            "language proficiency",
        },
        CVSectionType.CONTACT: {
            "contact",
            "contact information",
            "personal information",
        },
    }

    def detect(self, text: str) -> DetectedCV:
        if not isinstance(text, str):
            raise TypeError("CV text must be a string.")

        if not text.strip():
            raise ValueError("CV text cannot be empty.")

        lines = text.splitlines()

        sections: list[DetectedCVSection] = []

        header_lines: list[str] = []

        current_type: CVSectionType | None = None
        current_heading: str | None = None
        current_content: list[str] = []

        order = 0

        for line in lines:
            normalized_heading = self._normalize_heading(line)

            section_type = self._identify_section(
                normalized_heading
            )

            if section_type is not None:
                if current_type is not None:
                    sections.append(
                        self._build_section(
                            section_type=current_type,
                            heading=current_heading or "",
                            content=current_content,
                            order=order,
                        )
                    )
                    order += 1

                current_type = section_type
                current_heading = line.strip()
                current_content = []

            elif current_type is not None:
                current_content.append(line)

            else:
                header_lines.append(line)

        if current_type is not None:
            sections.append(
                self._build_section(
                    section_type=current_type,
                    heading=current_heading or "",
                    content=current_content,
                    order=order,
                )
            )

        header_text = "\n".join(header_lines).strip()

        return DetectedCV(
            header_text=header_text,
            sections=sections,
        )

    @staticmethod
    def _normalize_heading(line: str) -> str:
        line = line.strip().lower()

        # Remove common heading punctuation.
        line = re.sub(r"[:\-–—]+$", "", line)

        # Normalize ampersand spacing.
        line = re.sub(r"\s*&\s*", " & ", line)

        # Collapse whitespace.
        line = re.sub(r"\s+", " ", line)

        return line.strip()

    def _identify_section(
        self,
        normalized_heading: str,
    ) -> CVSectionType | None:
        for section_type, aliases in self.SECTION_ALIASES.items():
            if normalized_heading in aliases:
                return section_type

        return None

    @staticmethod
    def _build_section(
        section_type: CVSectionType,
        heading: str,
        content: list[str],
        order: int,
    ) -> DetectedCVSection:
        cleaned_content = "\n".join(content).strip()

        return DetectedCVSection(
            section_type=section_type,
            heading=heading,
            content=cleaned_content,
            order=order,
        )

