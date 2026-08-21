from src.ai_cv_assistant.schemas.job import JobProfile
from src.ai_cv_assistant.services.job.jd_validator import JDValidator


def test_supported_requirement_is_kept():
    extraction = JobProfile(
        title="Backend Developer",
        requirements=[
            {
                "name": "Python",
                "category": "technical_skill",
                "required": True,
            }
        ],
        keywords=[],
    )

    jd_text = """
    Backend Developer

    We are looking for a developer
    with experience in Python.
    """

    validator = JDValidator()

    result = validator.validate(
        extraction,
        jd_text,
    )

    assert len(result.requirements) == 1
    assert result.requirements[0].name == "Python"


def test_unsupported_requirement_is_removed():
    extraction = JobProfile(
        title="Backend Developer",
        requirements=[
            {
                "name": "Python",
                "category": "technical_skill",
                "required": True,
            },
            {
                "name": "AWS",
                "category": "cloud",
                "required": True,
            },
        ],
        keywords=[],
    )

    jd_text = """
    Backend Developer

    We are looking for a developer
    with experience in Python.
    """

    validator = JDValidator()

    result = validator.validate(
        extraction,
        jd_text,
    )

    requirement_names = [
        requirement.name
        for requirement in result.requirements
    ]

    assert "Python" in requirement_names
    assert "AWS" not in requirement_names


def test_unsupported_keyword_is_removed():
    extraction = JobProfile(
        title="Backend Developer",
        requirements=[],
        keywords=[
            {
                "keyword": "FastAPI",
                "category": "technology",
            },
            {
                "keyword": "Kubernetes",
                "category": "technology",
            },
        ],
    )

    jd_text = """
    Backend Developer

    Experience with FastAPI is required.
    """

    validator = JDValidator()

    result = validator.validate(
        extraction,
        jd_text,
    )

    keywords = [
        keyword.keyword
        for keyword in result.keywords
    ]

    assert "FastAPI" in keywords
    assert "Kubernetes" not in keywords


def test_matching_is_case_insensitive():
    extraction = JobProfile(
        title="Backend Developer",
        requirements=[
            {
                "name": "Python",
                "category": "technical_skill",
                "required": True,
            }
        ],
        keywords=[],
    )

    jd_text = """
    We require PYTHON experience.
    """

    validator = JDValidator()

    result = validator.validate(
        extraction,
        jd_text,
    )

    assert len(result.requirements) == 1


def test_missing_requirement_is_removed():
    extraction = JobProfile(
        title="Backend Developer",
        requirements=[
            {
                "name": "Python",
                "category": "technical_skill",
                "required": True,
            }
        ],
        keywords=[],
    )

    jd_text = """
    Backend Developer
    """

    validator = JDValidator()

    result = validator.validate(
        extraction,
        jd_text,
    )

    assert result.requirements == []


def test_empty_jd_is_rejected():
    extraction = JobProfile(
        title="Backend Developer",
        requirements=[],
        keywords=[],
    )

    validator = JDValidator()

    try:
        validator.validate(
            extraction,
            "",
        )
    except ValueError as exc:
        assert str(exc) == (
            "Job description text cannot be empty."
        )
    else:
        raise AssertionError(
            "Expected ValueError for empty JD."
        )


def test_non_string_jd_is_rejected():
    extraction = JobProfile(
        title="Backend Developer",
        requirements=[],
        keywords=[],
    )

    validator = JDValidator()

    try:
        validator.validate(
            extraction,
            None,
        )
    except TypeError as exc:
        assert str(exc) == (
            "Job description text must be a string."
        )
    else:
        raise AssertionError(
            "Expected TypeError for non-string JD."
        )