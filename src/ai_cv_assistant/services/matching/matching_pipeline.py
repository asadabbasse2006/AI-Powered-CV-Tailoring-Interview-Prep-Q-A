from src.ai_cv_assistant.schemas.candidate import CandidateProfile
from src.ai_cv_assistant.schemas.job import JobProfile
from src.ai_cv_assistant.schemas.matching import CandidateJobMatch
from src.ai_cv_assistant.services.matching.job_matcher import JobMatcher


class MatchingPipeline:
    """
    End-to-end candidate-to-job matching pipeline.

    Flow:

        CandidateProfile
              +
          JobProfile
              ↓
          JobMatcher
              ↓
        CandidateJobMatch
    """

    def __init__(self, matcher: JobMatcher):
        self.matcher = matcher

    def process(
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

        return self.matcher.match(
            candidate=candidate,
            job=job,
        )