from uuid import uuid4

from src.ai_cv_assistant.schemas.candidate import (
    CandidateEvidence,
    CandidateProfile,
    ConfidenceLevel,
    EvidenceType,
    Skill,
    SkillCategory,
)
from src.ai_cv_assistant.schemas.cv_sections import (
    CVSectionType,
    DetectedCV,
)


class CandidateExtractor:
    """Extract structured candidate information from detected CV sections."""

    def extract(self, cv: DetectedCV) -> CandidateProfile:
        if not cv.sections:
            raise ValueError("CV must contain at least one section.")

        candidate_name = self._extract_candidate_name(cv)

        candidate = CandidateProfile(
            candidate_id=str(uuid4()),
            name=candidate_name,
            skills=[],
            evidence=[],
        )

        skills_section = self._find_section(
            cv,
            CVSectionType.SKILLS,
        )

        if skills_section:
            skills, evidence = self._extract_skills(
                skills_section.content,
            )

            candidate.skills.extend(skills)
            candidate.evidence.extend(evidence)

        return candidate

    @staticmethod
    def _extract_candidate_name(cv: DetectedCV) -> str:
        """
        Extract the candidate name from the text immediately preceding
        the first recognized CV section.
        """

        first_section = min(
            cv.sections,
            key=lambda section: section.order,
        )

        # The current DetectedCVSection doesn't retain the text that
        # appeared before the first recognized section.
        #
        # For the current stage, use a safe placeholder only for
        # test-created structured CVs where no identity information
        # has been parsed yet.
        #
        # This will be replaced when we implement header/contact
        # extraction.
        return "Unknown Candidate"

    @staticmethod
    def _find_section(
        cv: DetectedCV,
        section_type: CVSectionType,
    ):
        for section in cv.sections:
            if section.section_type == section_type:
                return section

        return None

    def _extract_skills(
        self,
        content: str,
    ) -> tuple[list[Skill], list[CandidateEvidence]]:
        skills: list[Skill] = []
        evidence: list[CandidateEvidence] = []

        if not content.strip():
            return skills, evidence

        skill_names = self._parse_skill_lines(content)

        for skill_name in skill_names:
            evidence_id = str(uuid4())

            evidence_item = CandidateEvidence(
                evidence_id=evidence_id,
                evidence_type=EvidenceType.SKILL,
                claim=f"Candidate has experience with {skill_name}.",
                evidence_text=skill_name,
                source_section="Skills",
                confidence=ConfidenceLevel.HIGH,
            )

            skill = Skill(
                name=skill_name,
                category=self._classify_skill(skill_name),
                evidence_ids=[evidence_id],
            )

            skills.append(skill)
            evidence.append(evidence_item)

        return skills, evidence

    @staticmethod
    def _parse_skill_lines(content: str) -> list[str]:
        skills = []

        for line in content.splitlines():
            line = line.strip()

            if not line:
                continue

            if line.startswith("-"):
                line = line[1:].strip()

            parts = [part.strip() for part in line.split(",")]

            for part in parts:
                if part:
                    skills.append(part)

        return skills

    @staticmethod
    def _classify_skill(skill_name: str) -> SkillCategory:
        normalized = skill_name.lower()

        programming_languages = {
            "python",
            "java",
            "c",
            "c++",
            "javascript",
            "typescript",
            "dart",
            "go",
            "rust",
        }

        frameworks = {
            "fastapi",
            "django",
            "flask",
            "react",
            "angular",
            "vue",
            "flutter",
        }

        databases = {
            "mysql",
            "postgresql",
            "postgres",
            "sqlite",
            "mongodb",
            "firebase",
        }

        tools = {
            "git",
            "github",
            "docker",
            "postman",
            "vs code",
        }

        if normalized in programming_languages:
            return SkillCategory.PROGRAMMING_LANGUAGE

        if normalized in frameworks:
            return SkillCategory.FRAMEWORK

        if normalized in databases:
            return SkillCategory.DATABASE

        if normalized in tools:
            return SkillCategory.TOOL

        return SkillCategory.OTHER