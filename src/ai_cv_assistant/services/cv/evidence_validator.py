from src.ai_cv_assistant.schemas.candidate import (
    CandidateEvidence,
    CandidateProfile,
)


class EvidenceValidationError(ValueError):
    """Raised when candidate evidence fails validation."""


class EvidenceValidator:
    """Validate evidence associated with a candidate profile."""

    def validate(
        self,
        candidate: CandidateProfile,
    ) -> CandidateProfile:
        self._validate_evidence_ids(candidate)
        self._validate_skill_evidence(candidate)

        return candidate

    @staticmethod
    def _validate_evidence_ids(
        candidate: CandidateProfile,
    ) -> None:
        evidence_ids = {
            evidence.evidence_id
            for evidence in candidate.evidence
        }

        for skill in candidate.skills:
            for evidence_id in skill.evidence_ids:
                if evidence_id not in evidence_ids:
                    raise EvidenceValidationError(
                        f"Skill '{skill.name}' references "
                        f"unknown evidence ID '{evidence_id}'."
                    )

    @staticmethod
    def _validate_skill_evidence(
        candidate: CandidateProfile,
    ) -> None:
        evidence_by_id = {
            evidence.evidence_id: evidence
            for evidence in candidate.evidence
        }

        for skill in candidate.skills:
            if not skill.evidence_ids:
                raise EvidenceValidationError(
                    f"Skill '{skill.name}' has no supporting evidence."
                )

            for evidence_id in skill.evidence_ids:
                evidence = evidence_by_id[evidence_id]

                if not evidence.evidence_text.strip():
                    raise EvidenceValidationError(
                        f"Evidence '{evidence_id}' has empty evidence text."
                    )