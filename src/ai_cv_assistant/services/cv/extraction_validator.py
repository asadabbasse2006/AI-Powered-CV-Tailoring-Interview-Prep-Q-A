from uuid import uuid4

from src.ai_cv_assistant.schemas.candidate import (
    CandidateEvidence,
    CandidateProfile,
    EvidenceType,
)
from src.ai_cv_assistant.schemas.extraction import CVExtractionResult
from src.ai_cv_assistant.services.cv.evidence_grounder import EvidenceGrounder


class ExtractionValidator:
    """
    Converts an LLM-generated CVExtractionResult into a trusted
    CandidateProfile.

    Extracted claims must be grounded in the original CV text
    before they are accepted.
    """

    def __init__(self, evidence_grounder: EvidenceGrounder | None = None):
        self.evidence_grounder = evidence_grounder or EvidenceGrounder()

    def validate(
        self,
        extraction: CVExtractionResult,
        cv_text: str,
    ) -> CandidateProfile:
        if not isinstance(extraction, CVExtractionResult):
            raise TypeError(
                "extraction must be a CVExtractionResult."
            )

        if not isinstance(cv_text, str):
            raise TypeError("CV text must be a string.")

        if not cv_text.strip():
            raise ValueError("CV text cannot be empty.")

        evidence: list[CandidateEvidence] = []

        self._validate_skills(
            extraction,
            cv_text,
            evidence,
        )

        self._validate_experience(
            extraction,
            cv_text,
            evidence,
        )

        self._validate_projects(
            extraction,
            cv_text,
            evidence,
        )

        return CandidateProfile(
            candidate_id=str(uuid4()),
            name=extraction.name or "Unknown Candidate",
            email=extraction.email,
            phone=extraction.phone,
            location=extraction.location,
            linkedin_url=extraction.linkedin_url,
            github_url=extraction.github_url,
            portfolio_url=extraction.portfolio_url,
            summary=extraction.summary,
            education=extraction.education,
            experience=extraction.experience,
            project=extraction.projects,
            skills=extraction.skills,
            certifications=extraction.certifications,
            achievements=extraction.achievements,
            evidence=evidence,
        )

    def _validate_skills(
        self,
        extraction: CVExtractionResult,
        cv_text: str,
        evidence: list[CandidateEvidence],
    ) -> None:
        validated_skills = []

        for skill in extraction.skills:
            evidence_text = self.evidence_grounder.ground(
                claim=skill.name,
                cv_text=cv_text,
            )

            if evidence_text is None:
                continue

            evidence_id = self._create_evidence(
                evidence=evidence,
                evidence_type=EvidenceType.SKILL,
                claim=skill.name,
                evidence_text=evidence_text,
            )

            skill.evidence_ids = [evidence_id]
            validated_skills.append(skill)

        extraction.skills = validated_skills

    def _validate_experience(
        self,
        extraction: CVExtractionResult,
        cv_text: str,
        evidence: list[CandidateEvidence],
    ) -> None:
        validated_experience = []

        for experience in extraction.experience:
            claim = f"{experience.job_title} at {experience.company}"

            evidence_text = self.evidence_grounder.ground(
                claim=experience.company,
                cv_text=cv_text,
            )

            if evidence_text is None:
                continue

            self._create_evidence(
                evidence=evidence,
                evidence_type=EvidenceType.EXPERIENCE,
                claim=claim,
                evidence_text=evidence_text,
            )

            validated_experience.append(experience)

        extraction.experience = validated_experience

    def _validate_projects(
        self,
        extraction: CVExtractionResult,
        cv_text: str,
        evidence: list[CandidateEvidence],
    ) -> None:
        validated_projects = []

        for project in extraction.projects:
            evidence_text = self.evidence_grounder.ground(
                claim=project.name,
                cv_text=cv_text,
            )

            if evidence_text is None:
                continue

            self._create_evidence(
                evidence=evidence,
                evidence_type=EvidenceType.PROJECT,
                claim=project.name,
                evidence_text=evidence_text,
            )

            validated_projects.append(project)

        extraction.projects = validated_projects

    @staticmethod
    def _create_evidence(
        evidence: list[CandidateEvidence],
        evidence_type: EvidenceType,
        claim: str,
        evidence_text: str,
    ) -> str:
        evidence_id = f"evidence-{uuid4()}"

        evidence.append(
            CandidateEvidence(
                evidence_id=evidence_id,
                evidence_type=evidence_type,
                claim=claim,
                evidence_text=evidence_text,
            )
        )

        return evidence_id