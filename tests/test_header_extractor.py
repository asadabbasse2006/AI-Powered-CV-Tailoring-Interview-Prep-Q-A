import pytest

from src.ai_cv_assistant.services.cv.header_extractor import HeaderExtractor


@pytest.fixture
def extractor():
    return HeaderExtractor()


def test_extract_name(extractor):
    text = """
Asad Abbas
Software Engineer

SKILLS
Python
FastAPI
"""

    header = extractor.extract(text)

    assert header.name == "Asad Abbas"


def test_extract_email(extractor):
    text = """
Asad Abbas
asad@example.com

SKILLS
Python
"""

    header = extractor.extract(text)

    assert header.email == "asad@example.com"


def test_extract_phone(extractor):
    text = """
Asad Abbas
+92 300 1234567

SKILLS
Python
"""

    header = extractor.extract(text)

    assert header.phone == "+92 300 1234567"


def test_extract_linkedin(extractor):
    text = """
Asad Abbas
https://www.linkedin.com/in/asad-abbas

SKILLS
Python
"""

    header = extractor.extract(text)

    assert (
        header.linkedin_url
        == "https://www.linkedin.com/in/asad-abbas"
    )


def test_extract_github(extractor):
    text = """
Asad Abbas
https://github.com/asadabbasse2006

SKILLS
Python
"""

    header = extractor.extract(text)

    assert (
        header.github_url
        == "https://github.com/asadabbasse2006"
    )


def test_extract_portfolio(extractor):
    text = """
Asad Abbas
https://asadabbas.dev

SKILLS
Python
"""

    header = extractor.extract(text)

    assert header.portfolio_url == "https://asadabbas.dev"


def test_extract_multiple_contact_fields(extractor):
    text = """
Asad Abbas
Software Engineer
asad@example.com
+92 300 1234567
https://www.linkedin.com/in/asad-abbas
https://github.com/asadabbasse2006
https://asadabbas.dev

SKILLS
Python
"""

    header = extractor.extract(text)

    assert header.name == "Asad Abbas"
    assert header.email == "asad@example.com"
    assert header.phone == "+92 300 1234567"
    assert (
        header.linkedin_url
        == "https://www.linkedin.com/in/asad-abbas"
    )
    assert (
        header.github_url
        == "https://github.com/asadabbasse2006"
    )
    assert header.portfolio_url == "https://asadabbas.dev"


def test_extract_explicit_location(extractor):
    text = """
Asad Abbas
Location: Bahawalpur, Pakistan

SKILLS
Python
"""

    header = extractor.extract(text)

    assert header.location == "Bahawalpur, Pakistan"


def test_does_not_guess_location(extractor):
    text = """
Asad Abbas
Software Engineer
Python Developer

SKILLS
Python
"""

    header = extractor.extract(text)

    assert header.location is None


def test_name_is_not_email(extractor):
    text = """
asad@example.com

SKILLS
Python
"""

    header = extractor.extract(text)

    assert header.name is None


def test_name_is_not_url(extractor):
    text = """
https://github.com/asadabbasse2006

SKILLS
Python
"""

    header = extractor.extract(text)

    assert header.name is None


def test_empty_text_is_rejected(extractor):
    with pytest.raises(ValueError):
        extractor.extract("")


def test_whitespace_only_text_is_rejected(extractor):
    with pytest.raises(ValueError):
        extractor.extract("   \n\n   ")


def test_non_string_input_is_rejected(extractor):
    with pytest.raises(TypeError):
        extractor.extract(None)