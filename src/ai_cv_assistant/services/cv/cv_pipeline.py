from pathlib import Path

from src.ai_cv_assistant.schemas.candidate import CandidateProfile
from src.ai_cv_assistant.schemas.extraction import CVExtractionResult
from src.ai_cv_assistant.services.cv.extraction_validator import (
    ExtractionValidator,
)
from src.ai_cv_assistant.services.cv.llm_extractor import CVExtractor
from src.ai_cv_assistant.services.cv.pdf_loader import PDFLoader
from src.ai_cv_assistant.services.cv.section_detector import CVSectionDetector
from src.ai_cv_assistant.services.cv.text_cleaner import TextCleaner


class CVPipeline:
    """
    Orchestrates the complete CV processing workflow.

    Pipeline:

        PDF
          ↓
        PDFLoader
          ↓
        TextCleaner
          ↓
        CVSectionDetector
          ↓
        CVExtractor
          ↓
        ExtractionValidator
          ↓
        CandidateProfile

    The pipeline keeps extraction and validation separate.
    LLM-generated information is not considered trusted until
    it has been validated against the original CV text.
    """

    def __init__(
        self,
        pdf_loader: PDFLoader | None = None,
        text_cleaner: TextCleaner | None = None,
        section_detector: CVSectionDetector | None = None,
        cv_extractor: CVExtractor | None = None,
        extraction_validator: ExtractionValidator | None = None,
    ):
        self.pdf_loader = pdf_loader or PDFLoader()
        self.text_cleaner = text_cleaner or TextCleaner()
        self.section_detector = (
            section_detector or CVSectionDetector()
        )
        self.cv_extractor = cv_extractor
        self.extraction_validator = (
            extraction_validator or ExtractionValidator()
        )

    def process_text(self, cv_text: str) -> CandidateProfile:
        """
        Process CV text and return a trusted CandidateProfile.
        """

        if not isinstance(cv_text, str):
            raise TypeError("CV text must be a string.")

        if not cv_text.strip():
            raise ValueError("CV text cannot be empty.")

        # Step 1: Clean the extracted text.
        cleaned_text = self.text_cleaner.clean(cv_text)

        # Step 2: Detect CV structure.
        detected_cv = self.section_detector.detect(cleaned_text)

        # Step 3: Extract structured information using the LLM.
        if self.cv_extractor is None:
            raise ValueError(
                "CVExtractor must be provided when processing CV text."
            )

        extraction = self.cv_extractor.extract(cleaned_text)

        if not isinstance(extraction, CVExtractionResult):
            raise TypeError(
                "CVExtractor must return a CVExtractionResult."
            )

        # Step 4: Ground and validate the LLM extraction.
        candidate_profile = self.extraction_validator.validate(
            extraction=extraction,
            cv_text=cleaned_text,
        )

        return candidate_profile

    def process_file(
        self,
        file_path: str | Path,
    ) -> CandidateProfile:
        """
        Load a PDF CV and process it into a trusted CandidateProfile.
        """

        if not isinstance(file_path, (str, Path)):
            raise TypeError(
                "file_path must be a string or pathlib.Path."
            )

        # Step 1: Extract text from PDF.
        raw_text = self.pdf_loader.extract_text(file_path)

        # Step 2 onward: Process extracted text.
        return self.process_text(raw_text)