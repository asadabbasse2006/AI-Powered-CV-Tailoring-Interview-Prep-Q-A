from src.ai_cv_assistant.schemas.processing import AnalysisResult


class AnalysisStore:
    """
    Temporary in-memory storage for analysis results.

    This is suitable for development and frontend integration.
    A persistent database can replace this later.
    """

    def __init__(self) -> None:
        self._results: dict[str, AnalysisResult] = {}

    def save(self, result: AnalysisResult) -> None:
        self._results[result.metadata.request_id] = result

    def get(self, request_id: str) -> AnalysisResult | None:
        return self._results.get(request_id)

    def delete(self, request_id: str) -> bool:
        return self._results.pop(request_id, None) is not None