from pathlib import Path

import fitz
import pytest

from src.ai_cv_assistant.services.cv.pdf_loader import (
    PDFExtractionError,
    PDFLoader,
)

@pytest.fixture
def pdf_loader():
    return PDFLoader()


@pytest.fixture
def sample_pdf(tmp_path: Path) -> Path:
    pdf_path = tmp_path / "sample_cv.pdf"

    document = fitz.open()

    page = document.new_page()

    page.insert_text(
        (72, 72),
        "Asad Abbas\n"
        "Software Engineer\n\n"
        "Skills\n"
        "Python, FastAPI, Django\n\n"
        "Experience\n"
        "Software Engineering Intern\n"
        "Developed REST APIs using Python and FastAPI.",
    )

    document.save(pdf_path)
    document.close()

    return pdf_path


def test_extract_text_from_pdf(
    pdf_loader: PDFLoader,
    sample_pdf: Path,
):
    text = pdf_loader.extract_text(sample_pdf)

    assert text
    assert "Asad Abbas" in text
    assert "Software Engineer" in text
    assert "Python" in text
    assert "FastAPI" in text


def test_pdf_file_not_found(
    pdf_loader: PDFLoader,
    tmp_path: Path,
):
    missing_file = tmp_path / "missing.pdf"

    with pytest.raises(PDFExtractionError):
        pdf_loader.extract_text(missing_file)


def test_non_pdf_file_rejected(
    pdf_loader: PDFLoader,
    tmp_path: Path,
):
    text_file = tmp_path / "cv.txt"
    text_file.write_text("This is not a PDF.")

    with pytest.raises(PDFExtractionError):
        pdf_loader.extract_text(text_file)


def test_empty_pdf_rejected(
    pdf_loader: PDFLoader,
    tmp_path: Path,
):
    pdf_path = tmp_path / "empty.pdf"

    document = fitz.open()
    document.new_page()
    document.save(pdf_path)
    document.close()

    with pytest.raises(PDFExtractionError):
        pdf_loader.extract_text(pdf_path)


def test_scanned_like_pdf_rejected(
    pdf_loader: PDFLoader,
    tmp_path: Path,
):
    pdf_path = tmp_path / "image_only.pdf"

    document = fitz.open()
    document.new_page()
    document.save(pdf_path)
    document.close()

    with pytest.raises(PDFExtractionError):
        pdf_loader.extract_text(pdf_path)