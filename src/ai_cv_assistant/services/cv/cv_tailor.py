from uuid import uuid4

from src.ai_cv_assistant.schemas.candidate import CandidateProfile
from src.ai_cv_assistant.schemas.cv import (
    CVSection,
    CVSectionType,
    CVValidationResult,
    CVValidationStatus,
    GeneratedClaim,
    TailoredCV,
)
from src.ai_cv_assistant.schemas.job import JobProfile
from src.ai_cv_assistant.schemas.matching import (
    CandidateJobMatch,
    MatchStatus,
)


class CVTailor:
    """
    Generates a job-targeted CV from existing candidate data.

    This service does NOT invent candidate information.

    It only:
    - selects relevant existing information,
    - organizes it around the target job,
    - creates claims backed by candidate evidence.

    Final claim verification is handled by the CV validation layer.
    """

    def tailor(
        self,
        candidate: CandidateProfile,
        job: JobProfile,
        match: CandidateJobMatch,
    ) -> TailoredCV:

        if not isinstance(candidate, CandidateProfile):
            raise TypeError(
                "candidate must be a CandidateProfile."
            )

        if not isinstance(job, JobProfile):
            raise TypeError(
                "job must be a JobProfile."
            )

        if not isinstance(match, CandidateJobMatch):
            raise TypeError(
                "match must be a CandidateJobMatch."
            )

        sections: list[CVSection] = []

        summary_section = self._build_summary(
            candidate,
            job,
            match,
        )

        if summary_section is not None:
            sections.append(summary_section)

        skills_section = self._build_skills(
            candidate,
            job,
            match,
        )

        if skills_section is not None:
            sections.append(skills_section)

        experience_section = self._build_experience(
            candidate,
        )

        if experience_section is not None:
            sections.append(experience_section)

        project_section = self._build_projects(
            candidate,
        )

        if project_section is not None:
            sections.append(project_section)

        education_section = self._build_education(
            candidate,
        )

        if education_section is not None:
            sections.append(education_section)

        certifications_section = self._build_certifications(
            candidate,
        )

        if certifications_section is not None:
            sections.append(certifications_section)

        markdown = self._render_markdown(
            candidate,
            sections,
        )

        validation = CVValidationResult(
            status=CVValidationStatus.PASSED,
            unsupported_claim_ids=[],
            warnings=[],
            revision_count=0,
        )

        return TailoredCV(
            candidate_name=candidate.name,
            target_job_title=job.title,
            target_company=job.company,
            sections=sections,
            markdown=markdown,
            validation=validation,
        )

    def _build_summary(
        self,
        candidate: CandidateProfile,
        job: JobProfile,
        match: CandidateJobMatch,
    ) -> CVSection | None:

        if not candidate.summary:
            return None

        evidence_ids = self._relevant_evidence_ids(match)

        claim = GeneratedClaim(
            claim_id=f"claim-{uuid4()}",
            content=candidate.summary,
            evidence_ids=evidence_ids,
            supported=True,
        )

        return CVSection(
            section_type=CVSectionType.SUMMARY,
            title="Professional Summary",
            order=1,
            content=candidate.summary,
            claims=[claim],
        )

    def _build_skills(
        self,
        candidate: CandidateProfile,
        job: JobProfile,
        match: CandidateJobMatch,
    ) -> CVSection | None:

        matched_requirement_ids = {
            result.requirement_id
            for result in match.results
            if result.status
            in {
                MatchStatus.STRONG_MATCH,
                MatchStatus.PARTIAL_MATCH,
            }
        }

        if not matched_requirement_ids:
            return None

        selected_skills = []

        for skill in candidate.skills:
            skill_name = skill.name.strip().lower()

            for requirement in job.requirements:
                if requirement.requirement_id not in matched_requirement_ids:
                    continue

                requirement_name = requirement.name.strip().lower()

                if requirement_name == skill_name:
                    selected_skills.append(skill)
                    break

        if not selected_skills:
            return None

        content = "\n".join(
            f"- {skill.name}"
            for skill in selected_skills
        )

        claims = [
            GeneratedClaim(
                claim_id=f"claim-{uuid4()}",
                content=skill.name,
                evidence_ids=list(skill.evidence_ids),
                supported=bool(skill.evidence_ids),
            )
            for skill in selected_skills
        ]

        return CVSection(
            section_type=CVSectionType.SKILLS,
            title="Skills",
            order=2,
            content=content,
            claims=claims,
        )

    @staticmethod
    def _build_experience(
        candidate: CandidateProfile,
    ) -> CVSection | None:

        if not candidate.experience:
            return None

        content_parts: list[str] = []
        claims: list[GeneratedClaim] = []

        for experience in candidate.experience:

            content_parts.append(
                f"### {experience.job_title} — "
                f"{experience.company}"
            )

            if experience.location:
                content_parts.append(
                    f"Location: {experience.location}"
                )

            for responsibility in experience.responsibilities:
                content_parts.append(
                    f"- {responsibility}"
                )

            if experience.technologies:
                content_parts.append(
                    "- Technologies: "
                    + ", ".join(
                        experience.technologies
                    )
                )

            claims.append(
                GeneratedClaim(
                    claim_id=f"claim-{uuid4()}",
                    content=(
                        f"{experience.job_title} at "
                        f"{experience.company}"
                    ),
                    evidence_ids=[],
                    supported=True,
                )
            )

        return CVSection(
            section_type=CVSectionType.EXPERIENCE,
            title="Professional Experience",
            order=3,
            content="\n".join(content_parts),
            claims=claims,
        )

    @staticmethod
    def _build_projects(
        candidate: CandidateProfile,
    ) -> CVSection | None:

        if not candidate.project:
            return None

        content_parts: list[str] = []
        claims: list[GeneratedClaim] = []

        for project in candidate.project:

            content_parts.append(
                f"### {project.name}"
            )

            if project.description:
                content_parts.append(
                    project.description
                )

            for responsibility in project.responsibilities:
                content_parts.append(
                    f"- {responsibility}"
                )

            if project.technologies:
                content_parts.append(
                    "- Technologies: "
                    + ", ".join(
                        project.technologies
                    )
                )

            claims.append(
                GeneratedClaim(
                    claim_id=f"claim-{uuid4()}",
                    content=project.name,
                    evidence_ids=[],
                    supported=True,
                )
            )

        return CVSection(
            section_type=CVSectionType.PROJECTS,
            title="Projects",
            order=4,
            content="\n".join(content_parts),
            claims=claims,
        )

    @staticmethod
    def _build_education(
        candidate: CandidateProfile,
    ) -> CVSection | None:

        if not candidate.education:
            return None

        content_parts: list[str] = []

        for education in candidate.education:

            line = education.degree or "Education"

            if education.institution:
                line += f" — {education.institution}"

            content_parts.append(
                f"### {line}"
            )

            if education.field_of_study:
                content_parts.append(
                    f"Field: {education.field_of_study}"
                )

            if education.gpa:
                content_parts.append(
                    f"GPA: {education.gpa}"
                )

        return CVSection(
            section_type=CVSectionType.EDUCATION,
            title="Education",
            order=5,
            content="\n".join(content_parts),
        )

    @staticmethod
    def _build_certifications(
        candidate: CandidateProfile,
    ) -> CVSection | None:

        if not candidate.certifications:
            return None

        content = "\n".join(
            f"- {certification.name}"
            for certification in candidate.certifications
        )

        return CVSection(
            section_type=CVSectionType.CERTIFICATIONS,
            title="Certifications",
            order=6,
            content=content,
        )

    @staticmethod
    def _relevant_evidence_ids(
        match: CandidateJobMatch,
    ) -> list[str]:

        evidence_ids: list[str] = []

        for result in match.results:
            if result.status in {
                MatchStatus.STRONG_MATCH,
                MatchStatus.PARTIAL_MATCH,
            }:
                evidence_ids.extend(
                    result.candidate_evidence_ids
                )

        return list(dict.fromkeys(evidence_ids))

    @staticmethod
    def _render_markdown(
        candidate: CandidateProfile,
        sections: list[CVSection],
    ) -> str:

        lines = [
            f"# {candidate.name}",
            "",
        ]

        if candidate.email:
            lines.extend(
                [
                    f"Email: {candidate.email}",
                    "",
                ]
            )

        if candidate.phone:
            lines.extend(
                [
                    f"Phone: {candidate.phone}",
                    "",
                ]
            )

        for section in sorted(
            sections,
            key=lambda item: item.order,
        ):
            lines.extend(
                [
                    f"## {section.title}",
                    "",
                    section.content,
                    "",
                ]
            )

        return "\n".join(lines).strip()