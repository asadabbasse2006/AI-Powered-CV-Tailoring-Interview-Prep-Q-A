import pytest

from src.ai_cv_assistant.services.cv.text_cleaner import TextCleaner


@pytest.fixture
def text_cleaner():
    return TextCleaner()


def test_clean_normalizes_line_endings(text_cleaner):
    text = "John Doe\r\nSoftware Engineer\rExperience"

    result = text_cleaner.clean(text)

    assert result == "John Doe\nSoftware Engineer\nExperience"


def test_clean_removes_excessive_spaces(text_cleaner):
    text = "Python     FastAPI        Django"

    result = text_cleaner.clean(text)

    assert result == "Python FastAPI Django"


def test_clean_converts_tabs_to_spaces(text_cleaner):
    text = "Skills:\tPython\tFastAPI"

    result = text_cleaner.clean(text)

    assert result == "Skills: Python FastAPI"


def test_clean_normalizes_bullets(text_cleaner):
    text = (
        "Experience\n"
        "• Developed REST APIs\n"
        "● Built backend services\n"
        "▪ Worked with Python"
    )

    result = text_cleaner.clean(text)

    expected = (
        "Experience\n"
        "- Developed REST APIs\n"
        "- Built backend services\n"
        "- Worked with Python"
    )

    assert result == expected


def test_clean_removes_excessive_blank_lines(text_cleaner):
    text = (
        "John Doe\n\n\n\n"
        "Experience\n\n\n"
        "Software Engineer"
    )

    result = text_cleaner.clean(text)

    expected = (
        "John Doe\n\n"
        "Experience\n\n"
        "Software Engineer"
    )

    assert result == expected


def test_clean_strips_outer_whitespace(text_cleaner):
    text = "   John Doe\nSoftware Engineer   "

    result = text_cleaner.clean(text)

    assert result == "John Doe\nSoftware Engineer"


def test_clean_preserves_content(text_cleaner):
    text = (
        "Experience\n"
        "Developed REST APIs using Python and FastAPI.\n"
        "Built CRUD functionality."
    )

    result = text_cleaner.clean(text)

    assert "Developed REST APIs using Python and FastAPI." in result
    assert "Built CRUD functionality." in result


def test_clean_rejects_empty_text(text_cleaner):
    with pytest.raises(ValueError):
        text_cleaner.clean("")


def test_clean_rejects_whitespace_only_text(text_cleaner):
    with pytest.raises(ValueError):
        text_cleaner.clean("     \n\n   ")


def test_clean_rejects_non_string_input(text_cleaner):
    with pytest.raises(TypeError):
        text_cleaner.clean(None)