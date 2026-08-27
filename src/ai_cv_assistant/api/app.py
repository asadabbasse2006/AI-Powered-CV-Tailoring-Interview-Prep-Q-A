from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.ai_cv_assistant.api.routes import router
from src.ai_cv_assistant.application import (
    create_analysis_pipeline_from_settings,
)
from src.ai_cv_assistant.api.analysis_store import AnalysisStore


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """

    app = FastAPI(
        title="AI CV Assistant",
        description=(
            "AI-powered CV analysis, tailoring, "
            "and interview preparation API."
        ),
        version="0.1.0",
    )

    # ---------------------------------------------------------
    # CORS
    # ---------------------------------------------------------

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://127.0.0.1:5500",
            "http://localhost:5500",
            "http://127.0.0.1:3000",
            "http://localhost:3000",
            "http://127.0.0.1:8080",
            "http://localhost:8080",
        ],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ---------------------------------------------------------
    # Create analysis pipeline
    # ---------------------------------------------------------

    app.state.analysis_pipeline = (
        create_analysis_pipeline_from_settings()
    )

    # ---------------------------------------------------------
    # Create analysis store
    # ---------------------------------------------------------

    app.state.analysis_store = AnalysisStore()

    # ---------------------------------------------------------
    # Register routes
    # ---------------------------------------------------------

    app.include_router(router)

    return app


app = create_app()