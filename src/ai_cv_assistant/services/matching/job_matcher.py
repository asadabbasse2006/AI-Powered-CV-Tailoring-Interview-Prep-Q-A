from src.ai_cv_assistant.schemas.candidate import CandidateProfile
from src.ai_cv_assistant.schemas.job import JobProfile
from src.ai_cv_assistant.schemas.matching import (
    CandidateJobMatch,
    MatchConfidence,
    MatchResult,
    MatchStatus,
    MatchSummary,
)


class JobMatcher:
    """
    Matches a validated CandidateProfile against a JobProfile.

    Matching is evidence-based:
    - Strong match: candidate has direct evidence for the requirement.
    - Partial match: candidate has related evidence.
    - No evidence: no supporting candidate evidence exists.
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
                candidate,
                requirement,
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
        requirement,
    ) -> MatchResult:

        candidate_skills = {
            skill.name.strip().lower(): skill
            for skill in candidate.skills
        }

        requirement_name = requirement.name.strip().lower()

        skill = candidate_skills.get(requirement_name)

        if skill is not None:
            return MatchResult(
                requirement_id=requirement.requirement_id,
                candidate_evidence_ids=list(
                    skill.evidence_ids
                ),
                status=MatchStatus.STRONG_MATCH,
                confidence=MatchConfidence.HIGH,
                reason=(
                    f"Candidate has direct evidence for "
                    f"{requirement.name}."
                ),
            )

        related_evidence_ids = self._find_related_evidence(
            candidate,
            requirement_name,
        )

        if related_evidence_ids:
            return MatchResult(
                requirement_id=requirement.requirement_id,
                candidate_evidence_ids=related_evidence_ids,
                status=MatchStatus.PARTIAL_MATCH,
                confidence=MatchConfidence.MEDIUM,
                reason=(
                    f"Candidate has related evidence for "
                    f"{requirement.name}, but no direct skill match "
                    f"was found."
                ),
            )

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
    def _find_related_evidence(
        candidate: CandidateProfile,
        requirement_name: str,
    ) -> list[str]:

        matched_ids: list[str] = []

        for evidence in candidate.evidence:
            claim = evidence.claim.lower()
            evidence_text = evidence.evidence_text.lower()

            if (
                requirement_name in claim
                or requirement_name in evidence_text
            ):
                matched_ids.append(evidence.evidence_id)

        return matched_ids

    @staticmethod
    def _build_summary(
        results: list[MatchResult],
    ) -> MatchSummary:

        strong_matches = sum(
            result.status == MatchStatus.STRONG_MATCH
            for result in results
        )

        partial_matches = sum(
            result.status == MatchStatus.PARTIAL_MATCH
            for result in results
        )

        no_evidence = sum(
            result.status == MatchStatus.NO_EVIDENCE
            for result in results
        )

        conflicts = sum(
            result.status == MatchStatus.CONFLICT
            for result in results
        )

        return MatchSummary(
            total_requirements=len(results),
            strong_matches=strong_matches,
            partial_matches=partial_matches,
            no_evidence=no_evidence,
            conflicts=conflicts,
        )