from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.ai_cv_assistant.api.app import app
from src.ai_cv_assistant.api.routes import get_analysis_pipeline
from src.ai_cv_assistant.schemas.processing import AnalysisResult


class FakeAnalysisPipeline:
    def __init__(self, result: AnalysisResult):
        self.result = result
        self.calls = []

    def analyze(
        self,
        cv_file_path: str | Path,
        jd_text: str,
    ) -> AnalysisResult:
        self.calls.append(
            {
                "cv_file_path": cv_file_path,
                "jd_text": jd_text,
            }
        )

        return self.result