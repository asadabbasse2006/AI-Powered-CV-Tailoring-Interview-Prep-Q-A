from src.ai_cv_assistant.services.cv.llm_extractor import CVExtractor


class FakeLLMClient:
    def __init__(self, response):
        self.response = response
        self.last_prompt = None
        self.last_response_schema = None

    def generate_structured(self, prompt, response_schema=None):
        self.last_prompt = prompt
        self.last_response_schema = response_schema
        return self.response



def test_extract_cv():
    response = {
        "name": "Asad Abbas",
        "email": "asad@example.com",
        "summary": "Software Engineering student.",
        "skills": [
            {
                "name": "Python",
                "category": "programming_language",
            }
        ],
    }

    llm = FakeLLMClient(response)
    extractor = CVExtractor(llm)

    result = extractor.extract(
        "Asad Abbas\nPython\nSoftware Engineering student."
    )

    assert result.name == "Asad Abbas"
    assert result.email == "asad@example.com"
    assert len(result.skills) == 1
    assert result.skills[0].name == "Python"

def test_cv_text_is_included_in_prompt():
    llm = FakeLLMClient(
        {
            "name": "Asad Abbas",
        }
    )

    extractor = CVExtractor(llm)

    cv_text = "Asad Abbas\nPython\nFastAPI"

    extractor.extract(cv_text)

    assert cv_text in llm.last_prompt

def test_missing_fields_are_allowed():
    llm = FakeLLMClient(
        {
            "name": "Asad Abbas",
        }
    )

    extractor = CVExtractor(llm)

    result = extractor.extract("Asad Abbas")

    assert result.name == "Asad Abbas"
    assert result.email is None
    assert result.skills == []
    assert result.education == []