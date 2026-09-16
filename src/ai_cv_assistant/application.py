from src.ai_cv_assistant.services.analysis.analysis_pipeline import (
    AnalysisPipeline,
)
from src.ai_cv_assistant.services.cv.cv_pipeline import CVPipeline
from src.ai_cv_assistant.services.cv.cv_tailor import CVTailor
from src.ai_cv_assistant.services.cv.extraction_validator import (
    ExtractionValidator,
)
from src.ai_cv_assistant.services.cv.llm_extractor import CVExtractor
from src.ai_cv_assistant.services.cv.pdf_loader import PDFLoader
from src.ai_cv_assistant.services.cv.section_detector import (
    CVSectionDetector,
)
from src.ai_cv_assistant.services.cv.text_cleaner import TextCleaner
from src.ai_cv_assistant.services.interview.llm_interview_preparer import (
    LLMInterviewPreparer,
)
from src.ai_cv_assistant.services.job.jd_extractor import JDExtractor
from src.ai_cv_assistant.services.job.jd_pipeline import JDPipeline
from src.ai_cv_assistant.services.job.jd_validator import JDValidator
from src.ai_cv_assistant.services.llm.gemini_client import (
    GeminiLLMClient,
)
from src.ai_cv_assistant.services.matching.job_matcher import JobMatcher
from src.ai_cv_assistant.services.matching.matching_pipeline import (
    MatchingPipeline,
)

from src.ai_cv_assistant.config import Settings


def create_analysis_pipeline(
    api_key: str,
    model: str = "gemini-2.5-flash",
) -> AnalysisPipeline:

    # ---------------------------------------------------------
    # 1. Create LLM client
    # ---------------------------------------------------------

    llm_client = GeminiLLMClient(
        api_key=api_key,
        model=model,
    )

    # ---------------------------------------------------------
    # 2. Build CV processing pipeline
    # ---------------------------------------------------------

    cv_extractor = CVExtractor(
        llm_client=llm_client,
    )

    cv_pipeline = CVPipeline(
        pdf_loader=PDFLoader(),
        text_cleaner=TextCleaner(),
        section_detector=CVSectionDetector(),
        cv_extractor=cv_extractor,
        extraction_validator=ExtractionValidator(),
    )

    # ---------------------------------------------------------
    # 3. Build Job Description processing pipeline
    # ---------------------------------------------------------

    jd_extractor = JDExtractor(
        llm_client=llm_client,
    )

    jd_pipeline = JDPipeline(
        extractor=jd_extractor,
        validator=JDValidator(),
    )

    # ---------------------------------------------------------
    # 4. Build candidate-job matching pipeline
    # ---------------------------------------------------------

    matching_pipeline = MatchingPipeline(
        matcher=JobMatcher(),
    )

    # ---------------------------------------------------------
    # 5. Build CV tailoring service
    # ---------------------------------------------------------

    cv_tailor = CVTailor()

    # ---------------------------------------------------------
    # 6. Build interview preparation service
    # ---------------------------------------------------------

    interview_preparer = LLMInterviewPreparer(
        llm_client=llm_client,
    )

    # ---------------------------------------------------------
    # 7. Compose complete analysis pipeline
    # ---------------------------------------------------------

    return AnalysisPipeline(
        cv_pipeline=cv_pipeline,
        jd_pipeline=jd_pipeline,
        matching_pipeline=matching_pipeline,
        cv_tailor=cv_tailor,
        interview_preparer=interview_preparer,
        model_name=model,
    )


def create_analysis_pipeline_from_settings(
    settings: Settings | None = None,
) -> AnalysisPipeline:
    """
    Create the complete analysis pipeline using application settings.

    If settings are not provided, they are loaded from the
    environment and .env file.
    """

    if settings is None:
        settings = Settings()

    return create_analysis_pipeline(
        api_key=settings.gemini_api_key,
        model=settings.gemini_model,
    )