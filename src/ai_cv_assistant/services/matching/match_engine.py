from src.ai_cv_assistant.schemas.candidate import CandidateProfile
from src.ai_cv_assistant.schemas.job import JobProfile, JobRequirement
from src.ai_cv_assistant.schemas.matching import (
    CandidateJobMatch,
    MatchConfidence,
    MatchResult,
    MatchStatus,
    MatchSummary,
)


class MatchEngine:
    """
    Deterministically matches a validated candidate against a job.

    The engine only uses information already present in the
    CandidateProfile and JobProfile. It does not invent experience
    or use an LLM to infer unsupported skills.
    """

    def match(
        self,
        candidate: CandidateProfile,
        job: JobProfile,
    ) -> CandidateJobMatch:

        if not isinstance(candidate, CandidateProfile):
            raise TypeError(
                "candidate must be a CandidateProfile."
            )

        if not isinstance(job, JobProfile):
            raise TypeError(
                "job must be a JobProfile."
            )

        results: list[MatchResult] = []

        for requirement in job.requirements:
            result = self._match_requirement(
                candidate=candidate,
                requirement=requirement,
            )

            results.append(result)

        summary = self._build_summary(results)

        return CandidateJobMatch(
            results=results,
            summary=summary,
        )

    def _match_requirement(
        self,
        candidate: CandidateProfile,
        requirement: JobRequirement,
    ) -> MatchResult:

        exact_matches = self._find_exact_evidence(
            candidate=candidate,
            requirement_name=requirement.name,
        )

        if exact_matches:
            return MatchResult(
                requirement_id=requirement.requirement_id,
                candidate_evidence_ids=[
                    evidence.evidence_id
                    for evidence in exact_matches
                ],
                status=MatchStatus.STRONG_MATCH,
                confidence=MatchConfidence.HIGH,
                reason=(
                    f"Direct evidence found for "
                    f"'{requirement.name}'."
                ),
            )

        partial_matches = self._find_partial_evidence(
            candidate=candidate,
            requirement_name=requirement.name,
        )

        if partial_matches:
            return MatchResult(
                requirement_id=requirement.requirement_id,
                candidate_evidence_ids=[
                    evidence.evidence_id
                    for evidence in partial_matches
                ],
                status=MatchStatus.PARTIAL_MATCH,
                confidence=MatchConfidence.MEDIUM,
                reason=(
                    f"Related candidate evidence was found for "
                    f"'{requirement.name}', but no direct evidence "
                    "was found."
                ),
            )

        return MatchResult(
            requirement_id=requirement.requirement_id,
            candidate_evidence_ids=[],
            status=MatchStatus.NO_EVIDENCE,
            confidence=MatchConfidence.LOW,
            reason=(
                f"No candidate evidence found for "
                f"'{requirement.name}'."
            ),
        )

    @staticmethod
    def _normalize(value: str) -> str:
        return " ".join(value.lower().strip().split())

    def _find_exact_evidence(
        self,
        candidate: CandidateProfile,
        requirement_name: str,
    ):
        requirement = self._normalize(requirement_name)

        matches = []

        for evidence in candidate.evidence:
            claim = self._normalize(evidence.claim)
            evidence_text = self._normalize(
                evidence.evidence_text
            )

            if (
                requirement == claim
                or requirement == evidence_text
            ):
                matches.append(evidence)

        return matches

    def _find_partial_evidence(
        self,
        candidate: CandidateProfile,
        requirement_name: str,
    ):
        requirement = self._normalize(requirement_name)

        matches = []

        for evidence in candidate.evidence:
            claim = self._normalize(evidence.claim)
            evidence_text = self._normalize(
                evidence.evidence_text
            )

            if (
                requirement in claim
                or requirement in evidence_text
                or claim in requirement
            ):
                matches.append(evidence)

        return matches

    @staticmethod
    def _build_summary(
        results: list[MatchResult],
    ) -> MatchSummary:

        total = len(results)

        if total == 0:
            score = 0.0
        else:
            points = 0.0

            for result in results:
                if result.status == MatchStatus.STRONG_MATCH:
                    points += 1.0

                elif result.status == MatchStatus.PARTIAL_MATCH:
                    points += 0.5

                elif result.status == MatchStatus.NO_EVIDENCE:
                    points += 0.0

                elif result.status == MatchStatus.CONFLICT:
                    points -= 0.5

            score = max(0.0, min(100.0, (points / total) * 100))

        return MatchSummary(
            total_requirements=total,
            strong_matches=sum(
                result.status == MatchStatus.STRONG_MATCH
                for result in results
            ),
            partial_matches=sum(
                result.status == MatchStatus.PARTIAL_MATCH
                for result in results
            ),
            no_evidence=sum(
                result.status == MatchStatus.NO_EVIDENCE
                for result in results
            ),
            conflicts=sum(
                result.status == MatchStatus.CONFLICT
                for result in results
            ),
            score=score,
        )