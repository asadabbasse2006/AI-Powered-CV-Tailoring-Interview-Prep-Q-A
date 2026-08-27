from src.ai_cv_assistant.config import Settings


def test_settings_loads_gemini_api_key(
    monkeypatch,
):
    monkeypatch.setenv(
        "GEMINI_API_KEY",
        "test-api-key",
    )

    settings = Settings()

    assert settings.gemini_api_key == "test-api-key"


def test_settings_uses_default_gemini_model(
    monkeypatch,
):
    monkeypatch.setenv(
        "GEMINI_API_KEY",
        "test-api-key",
    )

    settings = Settings()

    assert (
        settings.gemini_model
        == "gemini-3.1-flash-lite"
    )


def test_settings_loads_custom_gemini_model(
    monkeypatch,
):
    monkeypatch.setenv(
        "GEMINI_API_KEY",
        "test-api-key",
    )

    monkeypatch.setenv(
        "GEMINI_MODEL",
        "custom-model",
    )

    settings = Settings()

    assert settings.gemini_model == "custom-model"