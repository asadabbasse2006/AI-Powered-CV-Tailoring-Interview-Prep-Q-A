from src.ai_cv_assistant.schemas.job import JobProfile
from src.ai_cv_assistant.services.job.jd_extractor import JDExtractor
from src.ai_cv_assistant.services.job.jd_validator import JDValidator


class JDPipeline:

    def __init__(
        self,
        extractor: JDExtractor,
        validator: JDValidator,
    ):
        self.extractor = extractor
        self.validator = validator

    def process(self, jd_text: str) -> JobProfile:

        if not isinstance(jd_text, str):
            raise TypeError(
                "Job description text must be a string."
            )

        jd_text = jd_text.strip()

        if not jd_text:
            raise ValueError(
                "Job description text cannot be empty."
            )

        extraction = self.extractor.extract(
            jd_text
        )

        return self.validator.validate(
            extraction,
            jd_text,
        )