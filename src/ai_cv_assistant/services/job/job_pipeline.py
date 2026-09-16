from src.ai_cv_assistant.schemas.candidate import CandidateProfile
from src.ai_cv_assistant.schemas.job import JobProfile
from src.ai_cv_assistant.schemas.matching import CandidateJobMatch

from src.ai_cv_assistant.services.job.jd_pipeline import JDPipeline
from src.ai_cv_assistant.services.matching.match_engine import MatchEngine


class JobPipeline:
    """
    Orchestrates job-posting processing and candidate-job matching.

    Flow:

        Job URL
            ↓
        JDPipeline
            ↓
        JobProfile
            ↓
        MatchEngine
            ↓
        CandidateJobMatch
    """

    def __init__(
        self,
        jd_pipeline: JDPipeline,
        match_engine: MatchEngine,
    ):
        self.jd_pipeline = jd_pipeline
        self.match_engine = match_engine

    def analyze(
        self,
        job_url: str,
        candidate: CandidateProfile,
    ) -> tuple[JobProfile, CandidateJobMatch]:
        """
        Fetch and process a job posting URL, then match the
        candidate against the resulting JobProfile.
        """

        if not isinstance(job_url, str):
            raise TypeError(
                "job_url must be a string."
            )

        job_url = job_url.strip()

        if not job_url:
            raise ValueError(
                "job_url cannot be empty."
            )

        if not isinstance(candidate, CandidateProfile):
            raise TypeError(
                "candidate must be a CandidateProfile."
            )

        # ---------------------------------------------------------
        # Step 1: Fetch, extract and validate job posting
        # ---------------------------------------------------------

        job = self.jd_pipeline.process(
            job_url
        )

        # ---------------------------------------------------------
        # Step 2: Match candidate against job
        # ---------------------------------------------------------

        match = self.match_engine.match(
            candidate=candidate,
            job=job,
        )

        return job, match