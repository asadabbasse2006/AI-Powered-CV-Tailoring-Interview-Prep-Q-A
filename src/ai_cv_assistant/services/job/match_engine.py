from src.ai_cv_assistant.schemas.candidate import CandidateProfile
from src.ai_cv_assistant.schemas.job import JobProfile
from src.ai_cv_assistant.schemas.matching import (
    CandidateJobMatch,
    MatchConfidence,
    MatchResult,
    MatchStatus,
    MatchSummary,
)


class MatchEngine:
    """Match candidate evidence against job requirements."""

    def match(
        self,
        candidate: CandidateProfile,
        job: JobProfile,
    ) -> CandidateJobMatch:
        if not isinstance(candidate, CandidateProfile):
            raise TypeError("candidate must be a CandidateProfile.")

        if not isinstance(job, JobProfile):
            raise TypeError("job must be a JobProfile.")

        results = [
            self._match_requirement(candidate, requirement)
            for requirement in job.requirements
        ]

        return CandidateJobMatch(
            results=results,
            summary=self._build_summary(results),
        )

    def _match_requirement(self, candidate, requirement):
        required_name = self._normalize(requirement.name)

        # --------------------------------------------------
        # 1. EXACT SKILL MATCH
        # --------------------------------------------------
        for skill in candidate.skills:
            if self._normalize(skill.name) == required_name:
                return MatchResult(
                    requirement_id=requirement.requirement_id,
                    candidate_evidence_ids=list(skill.evidence_ids),
                    status=MatchStatus.STRONG_MATCH,
                    confidence=MatchConfidence.HIGH,
                    reason=(
                        f"Candidate has an exact skill match "
                        f"for {requirement.name}."
                    ),
                )

        # --------------------------------------------------
        # 2. EXACT EVIDENCE CLAIM MATCH
        # --------------------------------------------------
        exact_evidence = []

        for evidence in candidate.evidence:
            claim = self._normalize(evidence.claim)

            if claim == required_name:
                exact_evidence.append(evidence.evidence_id)

        if exact_evidence:
            return MatchResult(
                requirement_id=requirement.requirement_id,
                candidate_evidence_ids=exact_evidence,
                status=MatchStatus.STRONG_MATCH,
                confidence=MatchConfidence.HIGH,
                reason=(
                    f"Candidate evidence directly supports "
                    f"{requirement.name}."
                ),
            )

        # --------------------------------------------------
        # 3. PARTIAL EVIDENCE MATCH
        # --------------------------------------------------
        partial_evidence = []

        for evidence in candidate.evidence:
            claim = self._normalize(evidence.claim)
            evidence_text = self._normalize(evidence.evidence_text)

            if (
                required_name in claim
                or required_name in evidence_text
            ):
                partial_evidence.append(evidence.evidence_id)

        if partial_evidence:
            return MatchResult(
                requirement_id=requirement.requirement_id,
                candidate_evidence_ids=partial_evidence,
                status=MatchStatus.PARTIAL_MATCH,
                confidence=MatchConfidence.MEDIUM,
                reason=(
                    f"Candidate evidence partially supports "
                    f"{requirement.name}."
                ),
            )

        # --------------------------------------------------
        # 4. NO EVIDENCE
        # --------------------------------------------------
        return MatchResult(
            requirement_id=requirement.requirement_id,
            candidate_evidence_ids=[],
            status=MatchStatus.NO_EVIDENCE,
            confidence=MatchConfidence.LOW,
            reason=(
                f"No supporting evidence was found for "
                f"{requirement.name}."
            ),
        )

    @staticmethod
    def _normalize(value: str) -> str:
        return " ".join(value.strip().lower().split())

    @staticmethod
    def _build_summary(
        results: list[MatchResult],
    ) -> MatchSummary:
        total = len(results)

        strong_matches = sum(
            r.status == MatchStatus.STRONG_MATCH
            for r in results
        )

        partial_matches = sum(
            r.status == MatchStatus.PARTIAL_MATCH
            for r in results
        )

        no_evidence = sum(
            r.status == MatchStatus.NO_EVIDENCE
            for r in results
        )

        conflicts = sum(
            r.status == MatchStatus.CONFLICT
            for r in results
        )

        if total == 0:
            score = 0.0
        else:
            score = (
                strong_matches * 100
                + partial_matches * 50
            ) / total

        return MatchSummary(
            total_requirements=total,
            strong_matches=strong_matches,
            partial_matches=partial_matches,
            no_evidence=no_evidence,
            conflicts=conflicts,
            score=round(score, 2),
        )