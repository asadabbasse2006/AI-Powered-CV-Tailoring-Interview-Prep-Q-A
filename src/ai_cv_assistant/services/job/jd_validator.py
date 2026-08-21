from src.ai_cv_assistant.schemas.job import JobProfile


class JDValidator:
    """
    Validates an extracted JobProfile against the original
    job-description text.

    Only requirements and keywords explicitly supported by the
    original JD are retained.
    """

    def validate(
        self,
        extraction: JobProfile,
        jd_text: str,
    ) -> JobProfile:
        if not isinstance(extraction, JobProfile):
            raise TypeError(
                "extraction must be a JobProfile."
            )

        if not isinstance(jd_text, str):
            raise TypeError(
                "Job description text must be a string."
            )

        if not jd_text.strip():
            raise ValueError(
                "Job description text cannot be empty."
            )

        normalized_text = jd_text.lower()

        self._validate_requirements(
            extraction,
            normalized_text,
        )

        self._validate_keywords(
            extraction,
            normalized_text,
        )

        return extraction

    def _validate_requirements(
        self,
        extraction: JobProfile,
        normalized_text: str,
    ) -> None:
        validated_requirements = []

        for requirement in extraction.requirements:
            if self._claim_exists(
                requirement.name,
                normalized_text,
            ):
                validated_requirements.append(
                    requirement
                )

        extraction.requirements = validated_requirements

    def _validate_keywords(
        self,
        extraction: JobProfile,
        normalized_text: str,
    ) -> None:
        validated_keywords = []

        for keyword in extraction.keywords:
            if self._claim_exists(
                keyword.keyword,
                normalized_text,
            ):
                validated_keywords.append(
                    keyword
                )

        extraction.keywords = validated_keywords

    @staticmethod
    def _claim_exists(
        claim: str,
        normalized_text: str,
    ) -> bool:
        if not isinstance(claim, str):
            return False

        claim = claim.strip().lower()

        if not claim:
            return False

        return claim in normalized_text