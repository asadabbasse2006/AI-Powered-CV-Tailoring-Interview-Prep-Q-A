from src.ai_cv_assistant.schemas.job import JobProfile
from src.ai_cv_assistant.services.job.jd_extractor import JDExtractor
from src.ai_cv_assistant.services.job.jd_validator import JDValidator


class JDPipeline:
    """
    Complete job-description processing pipeline.

    Flow:

        raw JD text
            ↓
        LLM extraction
            ↓
        JobProfile
            ↓
        validation
            ↓
        validated JobProfile
    """

    def __init__(
        self,
        extractor: JDExtractor,
        validator: JDValidator,
    ):
        self.extractor = extractor
        self.validator = validator

    def process(self, jd_text: str) -> JobProfile:
        if not isinstance(jd_text, str):
            raise TypeError("Job description text must be a string.")

        if not jd_text.strip():
            raise ValueError(
                "Job description text cannot be empty."
            )

        extraction = self.extractor.extract(jd_text)

        return self.validator.validate(
            extraction,
            jd_text,
        )