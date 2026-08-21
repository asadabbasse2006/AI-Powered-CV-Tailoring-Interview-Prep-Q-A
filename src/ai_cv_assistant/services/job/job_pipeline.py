from src.ai_cv_assistant.schemas.candidate import CandidateProfile
from src.ai_cv_assistant.schemas.job import JobProfile
from src.ai_cv_assistant.schemas.matching import CandidateJobMatch
from src.ai_cv_assistant.services.job.jd_extractor import JDExtractor
from src.ai_cv_assistant.services.job.jd_validator import JDValidator
from src.ai_cv_assistant.services.job.match_engine import MatchEngine


class JobPipeline:
    """
    Orchestrates job-description extraction, validation,
    and candidate-job matching.
    """

    def __init__(
        self,
        jd_extractor: JDExtractor,
        jd_validator: JDValidator,
        match_engine: MatchEngine,
    ):
        self.jd_extractor = jd_extractor
        self.jd_validator = jd_validator
        self.match_engine = match_engine

    def analyze(
        self,
        jd_text: str,
        candidate: CandidateProfile,
    ) -> tuple[JobProfile, CandidateJobMatch]:
        """
        Extract and validate a job description, then match
        the candidate against the validated job.
        """

        if not isinstance(jd_text, str):
            raise TypeError(
                "Job description text must be a string."
            )

        if not jd_text.strip():
            raise ValueError(
                "Job description text cannot be empty."
            )

        if not isinstance(candidate, CandidateProfile):
            raise TypeError(
                "candidate must be a CandidateProfile."
            )

        # Step 1: Extract structured job data.
        extracted_job = self.jd_extractor.extract(jd_text)

        # Step 2: Validate the extracted job data.
        validated_job = self.jd_validator.validate(
            extracted_job,
            jd_text,
        )

        # Step 3: Match candidate against the validated job.
        match_result = self.match_engine.match(
            candidate,
            validated_job,
        )

        return validated_job, match_result