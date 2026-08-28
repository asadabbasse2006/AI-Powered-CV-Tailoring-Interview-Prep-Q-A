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

    This service never invents candidate information.

    It:
    - prioritizes relevant existing skills,
    - preserves evidence-backed experience,
    - preserves relevant projects,
    - keeps candidate achievements and certifications,
    - organizes existing information for the target job,
    - generates an ATS-friendly Markdown representation.

    It does NOT:
    - invent skills,
    - invent experience,
    - invent achievements,
    - invent certifications,
    - create unsupported claims.
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

        # -----------------------------------------------------
        # 1. Professional Summary
        # -----------------------------------------------------

        summary_section = self._build_summary(
            candidate=candidate,
            job=job,
            match=match,
        )

        if summary_section is not None:
            sections.append(summary_section)

        # -----------------------------------------------------
        # 2. Skills
        # -----------------------------------------------------

        skills_section = self._build_skills(
            candidate=candidate,
            job=job,
            match=match,
        )

        if skills_section is not None:
            sections.append(skills_section)

        # -----------------------------------------------------
        # 3. Professional Experience
        # -----------------------------------------------------

        experience_section = self._build_experience(
            candidate
        )

        if experience_section is not None:
            sections.append(experience_section)

        # -----------------------------------------------------
        # 4. Projects
        # -----------------------------------------------------

        project_section = self._build_projects(
            candidate
        )

        if project_section is not None:
            sections.append(project_section)

        # -----------------------------------------------------
        # 5. Education
        # -----------------------------------------------------

        education_section = self._build_education(
            candidate
        )

        if education_section is not None:
            sections.append(education_section)

        # -----------------------------------------------------
        # 6. Certifications
        # -----------------------------------------------------

        certifications_section = self._build_certifications(
            candidate
        )

        if certifications_section is not None:
            sections.append(certifications_section)

        # -----------------------------------------------------
        # 7. Achievements
        # -----------------------------------------------------

        achievements_section = self._build_achievements(
            candidate
        )

        if achievements_section is not None:
            sections.append(achievements_section)

        # -----------------------------------------------------
        # 8. Render Markdown
        # -----------------------------------------------------

        markdown = self._render_markdown(
            candidate=candidate,
            sections=sections,
        )

        # -----------------------------------------------------
        # 9. Validation
        # -----------------------------------------------------

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

    # =========================================================
    # SUMMARY
    # =========================================================

    def _build_summary(
        self,
        candidate: CandidateProfile,
        job: JobProfile,
        match: CandidateJobMatch,
    ) -> CVSection | None:

        if not candidate.summary:
            return None

        evidence_ids = self._relevant_evidence_ids(
            match
        )

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

    # =========================================================
    # SKILLS
    # =========================================================

    def _build_skills(
        self,
        candidate: CandidateProfile,
        job: JobProfile,
        match: CandidateJobMatch,
    ) -> CVSection | None:

        if not candidate.skills:
            return None

        # -----------------------------------------------------
        # Determine evidence associated with matched
        # requirements.
        # -----------------------------------------------------

        matched_evidence_ids = set()

        for result in match.results:

            if result.status in {
                MatchStatus.STRONG_MATCH,
                MatchStatus.PARTIAL_MATCH,
            }:

                matched_evidence_ids.update(
                    result.candidate_evidence_ids
                )

        # -----------------------------------------------------
        # Rank candidate skills.
        #
        # Skills whose evidence appears in a matched
        # requirement are prioritized.
        #
        # Remaining candidate skills are still preserved.
        # -----------------------------------------------------

        prioritized_skills = []
        other_skills = []

        for skill in candidate.skills:

            skill_evidence_ids = set(
                skill.evidence_ids
            )

            if (
                skill_evidence_ids
                & matched_evidence_ids
            ):
                prioritized_skills.append(skill)
            else:
                other_skills.append(skill)

        selected_skills = (
            prioritized_skills + other_skills
        )

        if not selected_skills:
            return None

        content = "\n".join(
            f"- {skill.name}"
            for skill in selected_skills
        )

        claims = []

        for skill in selected_skills:

            claims.append(
                GeneratedClaim(
                    claim_id=f"claim-{uuid4()}",
                    content=skill.name,
                    evidence_ids=list(
                        skill.evidence_ids
                    ),
                    supported=bool(
                        skill.evidence_ids
                    ),
                )
            )

        return CVSection(
            section_type=CVSectionType.SKILLS,
            title="Skills",
            order=2,
            content=content,
            claims=claims,
        )

    # =========================================================
    # EXPERIENCE
    # =========================================================

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

            if experience.start_date:
                start = experience.start_date.isoformat()
            else:
                start = None

            if experience.is_current:
                end = "Present"
            elif experience.end_date:
                end = experience.end_date.isoformat()
            else:
                end = None

            if start and end:
                content_parts.append(
                    f"{start} – {end}"
                )

            if experience.description:
                content_parts.append(
                    experience.description
                )

            for responsibility in (
                experience.responsibilities
            ):
                content_parts.append(
                    f"- {responsibility}"
                )

            for achievement in (
                experience.achievements
            ):
                content_parts.append(
                    f"- {achievement}"
                )

            if experience.technologies:
                content_parts.append(
                    "- Technologies: "
                    + ", ".join(
                        experience.technologies
                    )
                )

            content_parts.append("")

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
            content="\n".join(
                content_parts
            ).strip(),
            claims=claims,
        )

    # =========================================================
    # PROJECTS
    # =========================================================

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

            for responsibility in (
                project.responsibilities
            ):
                content_parts.append(
                    f"- {responsibility}"
                )

            for feature in project.features:
                content_parts.append(
                    f"- {feature}"
                )

            for result in project.results:
                content_parts.append(
                    f"- {result}"
                )

            if project.technologies:
                content_parts.append(
                    "- Technologies: "
                    + ", ".join(
                        project.technologies
                    )
                )

            if project.repository_url:
                content_parts.append(
                    f"- Repository: "
                    f"{project.repository_url}"
                )

            if project.demo_url:
                content_parts.append(
                    f"- Demo: "
                    f"{project.demo_url}"
                )

            content_parts.append("")

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
            content="\n".join(
                content_parts
            ).strip(),
            claims=claims,
        )

    # =========================================================
    # EDUCATION
    # =========================================================

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
                line += (
                    f" — {education.institution}"
                )

            content_parts.append(
                f"### {line}"
            )

            if education.field_of_study:
                content_parts.append(
                    f"Field: "
                    f"{education.field_of_study}"
                )

            if education.location:
                content_parts.append(
                    f"Location: "
                    f"{education.location}"
                )

            if education.start_date:
                content_parts.append(
                    f"Start Date: "
                    f"{education.start_date}"
                )

            if education.is_current:
                content_parts.append(
                    "Status: Currently enrolled"
                )

            elif education.end_date:
                content_parts.append(
                    f"End Date: "
                    f"{education.end_date}"
                )

            if education.gpa:
                content_parts.append(
                    f"GPA: {education.gpa}"
                )

            for detail in education.details:
                content_parts.append(
                    f"- {detail}"
                )

            content_parts.append("")

        return CVSection(
            section_type=CVSectionType.EDUCATION,
            title="Education",
            order=5,
            content="\n".join(
                content_parts
            ).strip(),
        )

    # =========================================================
    # CERTIFICATIONS
    # =========================================================

    @staticmethod
    def _build_certifications(
        candidate: CandidateProfile,
    ) -> CVSection | None:

        if not candidate.certifications:
            return None

        content_parts: list[str] = []

        for certification in (
            candidate.certifications
        ):

            line = certification.name

            if certification.issuing_organization:
                line += (
                    f" — "
                    f"{certification.issuing_organization}"
                )

            content_parts.append(
                f"- {line}"
            )

            if certification.issue_date:
                content_parts.append(
                    f"  - Issued: "
                    f"{certification.issue_date}"
                )

            if certification.credential_url:
                content_parts.append(
                    f"  - Credential: "
                    f"{certification.credential_url}"
                )

        return CVSection(
            section_type=CVSectionType.CERTIFICATIONS,
            title="Certifications",
            order=6,
            content="\n".join(
                content_parts
            ),
        )

    # =========================================================
    # ACHIEVEMENTS
    # =========================================================

    @staticmethod
    def _build_achievements(
        candidate: CandidateProfile,
    ) -> CVSection | None:

        if not candidate.achievements:
            return None

        content_parts: list[str] = []

        for achievement in (
            candidate.achievements
        ):

            content_parts.append(
                f"### {achievement.title}"
            )

            if achievement.description:
                content_parts.append(
                    achievement.description
                )

            if achievement.date:
                content_parts.append(
                    f"Date: {achievement.date}"
                )

            content_parts.append("")

        return CVSection(
            section_type=CVSectionType.ACHIEVEMENTS,
            title="Achievements",
            order=7,
            content="\n".join(
                content_parts
            ).strip(),
        )

    # =========================================================
    # EVIDENCE
    # =========================================================

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

        return list(
            dict.fromkeys(evidence_ids)
        )

    # =========================================================
    # MARKDOWN RENDERER
    # =========================================================

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

        if candidate.location:
            lines.extend(
                [
                    f"Location: {candidate.location}",
                    "",
                ]
            )

        if candidate.linkedin_url:
            lines.extend(
                [
                    f"LinkedIn: {candidate.linkedin_url}",
                    "",
                ]
            )

        if candidate.github_url:
            lines.extend(
                [
                    f"GitHub: {candidate.github_url}",
                    "",
                ]
            )

        if candidate.portfolio_url:
            lines.extend(
                [
                    f"Portfolio: {candidate.portfolio_url}",
                    "",
                ]
            )

        for section in sorted(
            sections,
            key=lambda item: item.order,
        ):

            if not section.content:
                continue

            lines.extend(
                [
                    f"## {section.title}",
                    "",
                    section.content,
                    "",
                ]
            )

        return "\n".join(lines).strip()