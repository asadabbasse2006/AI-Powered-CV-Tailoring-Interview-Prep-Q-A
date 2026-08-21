from pathlib import Path

import pytest

from src.ai_cv_assistant.schemas.candidate import CandidateProfile
from src.ai_cv_assistant.schemas.extraction import CVExtractionResult
from src.ai_cv_assistant.services.cv.cv_pipeline import CVPipeline


class FakePDFLoader:
    def __init__(self, text: str):
        self.text = text
        self.called_with = None

    def extract_text(self, file_path):
        self.called_with = file_path
        return self.text


class FakeTextCleaner:
    def __init__(self):
        self.called_with = None

    def clean(self, text: str) -> str:
        self.called_with = text
        return text.strip()


class FakeSectionDetector:
    def __init__(self):
        self.called_with = None

    def detect(self, text: str):
        self.called_with = text

        return {
            "header_text": "",
            "sections": [],
        }


class FakeCVExtractor:
    def __init__(self, result: CVExtractionResult):
        self.result = result
        self.called_with = None

    def extract(self, cv_text: str) -> CVExtractionResult:
        self.called_with = cv_text
        return self.result


class FakeExtractionValidator:
    def __init__(self):
        self.extraction = None
        self.cv_text = None

    def validate(
        self,
        extraction: CVExtractionResult,
        cv_text: str,
    ) -> CandidateProfile:
        self.extraction = extraction
        self.cv_text = cv_text

        return CandidateProfile(
            candidate_id="candidate-1",
            name=extraction.name or "Unknown Candidate",
            email=extraction.email,
            phone=extraction.phone,
            location=extraction.location,
            linkedin_url=extraction.linkedin_url,
            github_url=extraction.github_url,
            portfolio_url=extraction.portfolio_url,
            summary=extraction.summary,
            education=extraction.education,
            experience=extraction.experience,
            project=extraction.projects,
            skills=extraction.skills,
            certifications=extraction.certifications,
            achievements=extraction.achievements,
            evidence=[],
        )


@pytest.fixture
def extraction():
    return CVExtractionResult(
        name="Asad Abbas",
        email="asad@example.com",
        summary="Software Engineering student.",
        skills=[
            {
                "name": "Python",
                "category": "programming_language",
            }
        ],
    )


@pytest.fixture
def services(extraction):
    pdf_loader = FakePDFLoader(
        "Asad Abbas\nPython\nSoftware Engineering student."
    )

    text_cleaner = FakeTextCleaner()
    section_detector = FakeSectionDetector()
    cv_extractor = FakeCVExtractor(extraction)
    extraction_validator = FakeExtractionValidator()

    return (
        pdf_loader,
        text_cleaner,
        section_detector,
        cv_extractor,
        extraction_validator,
    )


@pytest.fixture
def pipeline(services):
    (
        pdf_loader,
        text_cleaner,
        section_detector,
        cv_extractor,
        extraction_validator,
    ) = services

    return CVPipeline(
        pdf_loader=pdf_loader,
        text_cleaner=text_cleaner,
        section_detector=section_detector,
        cv_extractor=cv_extractor,
        extraction_validator=extraction_validator,
    )


def test_process_text_returns_candidate_profile(
    pipeline,
):
    result = pipeline.process_text(
        "  Asad Abbas\nPython\nSoftware Engineering student.  "
    )

    assert isinstance(result, CandidateProfile)
    assert result.name == "Asad Abbas"
    assert result.email == "asad@example.com"
    assert result.skills[0].name == "Python"


def test_process_text_cleans_text_before_extraction(
    services,
):
    (
        pdf_loader,
        text_cleaner,
        section_detector,
        cv_extractor,
        extraction_validator,
    ) = services

    pipeline = CVPipeline(
        pdf_loader=pdf_loader,
        text_cleaner=text_cleaner,
        section_detector=section_detector,
        cv_extractor=cv_extractor,
        extraction_validator=extraction_validator,
    )

    cv_text = "  Asad Abbas\nPython  "

    pipeline.process_text(cv_text)

    assert text_cleaner.called_with == cv_text
    assert cv_extractor.called_with == cv_text.strip()


def test_process_text_runs_section_detector(
    services,
):
    (
        pdf_loader,
        text_cleaner,
        section_detector,
        cv_extractor,
        extraction_validator,
    ) = services

    pipeline = CVPipeline(
        pdf_loader=pdf_loader,
        text_cleaner=text_cleaner,
        section_detector=section_detector,
        cv_extractor=cv_extractor,
        extraction_validator=extraction_validator,
    )

    cv_text = "Asad Abbas\nPython"

    pipeline.process_text(cv_text)

    assert section_detector.called_with == cv_text


def test_process_text_passes_extraction_to_validator(
    services,
    extraction,
):
    (
        pdf_loader,
        text_cleaner,
        section_detector,
        cv_extractor,
        extraction_validator,
    ) = services

    pipeline = CVPipeline(
        pdf_loader=pdf_loader,
        text_cleaner=text_cleaner,
        section_detector=section_detector,
        cv_extractor=cv_extractor,
        extraction_validator=extraction_validator,
    )

    cv_text = "Asad Abbas\nPython"

    pipeline.process_text(cv_text)

    assert extraction_validator.extraction is extraction
    assert extraction_validator.cv_text == cv_text


def test_process_file_loads_pdf(
    pipeline,
    services,
):
    (
        pdf_loader,
        text_cleaner,
        section_detector,
        cv_extractor,
        extraction_validator,
    ) = services

    pdf_path = Path("sample_cv.pdf")

    result = pipeline.process_file(pdf_path)

    assert result.name == "Asad Abbas"
    assert pdf_loader.called_with == pdf_path


def test_process_text_rejects_non_string_input(
    pipeline,
):
    with pytest.raises(TypeError, match="CV text must be a string"):
        pipeline.process_text(None)


def test_process_text_rejects_empty_text(
    pipeline,
):
    with pytest.raises(
        ValueError,
        match="CV text cannot be empty",
    ):
        pipeline.process_text("   ")


def test_process_file_rejects_invalid_path_type(
    pipeline,
):
    with pytest.raises(
        TypeError,
        match="file_path must be a string or pathlib.Path",
    ):
        pipeline.process_file(123)


def test_process_text_requires_llm_extractor(
    services,
):
    (
        pdf_loader,
        text_cleaner,
        section_detector,
        cv_extractor,
        extraction_validator,
    ) = services

    pipeline = CVPipeline(
        pdf_loader=pdf_loader,
        text_cleaner=text_cleaner,
        section_detector=section_detector,
        cv_extractor=None,
        extraction_validator=extraction_validator,
    )

    with pytest.raises(
        ValueError,
        match="CVExtractor must be provided",
    ):
        pipeline.process_text("Asad Abbas")