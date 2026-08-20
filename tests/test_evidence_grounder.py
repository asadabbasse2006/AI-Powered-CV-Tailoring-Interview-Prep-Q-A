import pytest

from src.ai_cv_assistant.services.cv.evidence_grounder import (
    EvidenceGrounder,
)


@pytest.fixture
def grounder():
    return EvidenceGrounder()


def test_finds_claim_in_sentence(grounder):
    cv_text = """
    Developed backend applications using Python and FastAPI.
    """

    evidence = grounder.ground(
        "Python",
        cv_text,
    )

    assert evidence == (
        "Developed backend applications using Python and FastAPI."
    )


def test_matching_is_case_insensitive(grounder):
    cv_text = """
    Developed applications using PYTHON.
    """

    evidence = grounder.ground(
        "python",
        cv_text,
    )

    assert evidence == "Developed applications using PYTHON."


def test_finds_claim_on_separate_line(grounder):
    cv_text = """
    Skills
    Python
    FastAPI
    Django
    """

    evidence = grounder.ground(
        "FastAPI",
        cv_text,
    )

    assert evidence == "FastAPI"


def test_returns_none_when_claim_is_not_supported(grounder):
    cv_text = """
    Developed applications using Python and FastAPI.
    """

    evidence = grounder.ground(
        "AWS",
        cv_text,
    )

    assert evidence is None


def test_finds_claim_in_longer_sentence(grounder):
    cv_text = """
    Built REST APIs using Python and FastAPI for backend services.
    """

    evidence = grounder.ground(
        "FastAPI",
        cv_text,
    )

    assert evidence == (
        "Built REST APIs using Python and FastAPI for backend services."
    )


def test_empty_claim_is_rejected(grounder):
    with pytest.raises(ValueError):
        grounder.ground("", "Python")


def test_whitespace_claim_is_rejected(grounder):
    with pytest.raises(ValueError):
        grounder.ground("   ", "Python")


def test_empty_cv_is_rejected(grounder):
    with pytest.raises(ValueError):
        grounder.ground("Python", "")


def test_non_string_claim_is_rejected(grounder):
    with pytest.raises(TypeError):
        grounder.ground(123, "Python")


def test_non_string_cv_is_rejected(grounder):
    with pytest.raises(TypeError):
        grounder.ground("Python", 123)