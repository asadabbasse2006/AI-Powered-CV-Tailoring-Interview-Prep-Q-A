from pathlib import Path
import tempfile

from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
)

from src.ai_cv_assistant.schemas.processing import AnalysisResult
from src.ai_cv_assistant.services.analysis.analysis_pipeline import (
    AnalysisPipeline,
)



def get_analysis_pipeline(
    request: Request,
) -> AnalysisPipeline:
    """
    Return the application's shared analysis pipeline.

    The pipeline is created once during application startup
    and stored in app.state.
    """

    pipeline = getattr(
        request.app.state,
        "analysis_pipeline",
        None,
    )

    if pipeline is None:
        raise RuntimeError(
            "Analysis pipeline is not initialized."
        )

    return pipeline

router = APIRouter(
    prefix="/api/v1",
    tags=["Analysis"],
)


@router.post(
    "/analyze",
    response_model=AnalysisResult,
)
async def analyze_cv(
    request: Request,
    cv: UploadFile = File(...),
    job_description: str = Form(...),
) -> AnalysisResult:

    # ---------------------------------------------------------
    # Validate CV filename
    # ---------------------------------------------------------

    if not cv.filename:
        raise HTTPException(
            status_code=400,
            detail="CV file is required.",
        )

    # ---------------------------------------------------------
    # Validate PDF
    # ---------------------------------------------------------

    if not cv.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="CV must be a PDF file.",
        )

    # ---------------------------------------------------------
    # Validate job description
    # ---------------------------------------------------------

    if not job_description.strip():
        raise HTTPException(
            status_code=400,
            detail="Job description cannot be empty.",
        )

    temp_path: Path | None = None

    try:
        # -----------------------------------------------------
        # Read uploaded file
        # -----------------------------------------------------

        file_content = await cv.read()

        if not file_content:
            raise HTTPException(
                status_code=400,
                detail="Uploaded CV file is empty.",
            )

        # -----------------------------------------------------
        # Save temporary PDF
        # -----------------------------------------------------

        with tempfile.NamedTemporaryFile(
            suffix=".pdf",
            delete=False,
        ) as temp_file:

            temp_file.write(file_content)
            temp_path = Path(temp_file.name)

        # -----------------------------------------------------
        # Get pipeline
        # -----------------------------------------------------

        pipeline = get_analysis_pipeline(request)

        # -----------------------------------------------------
        # Run analysis
        # -----------------------------------------------------

        result = pipeline.analyze(
            cv_file_path=temp_path,
            jd_text=job_description.strip(),
        )

        # -----------------------------------------------------
        # Store result
        # -----------------------------------------------------

        request.app.state.analysis_store.save(result)

        return result

    except HTTPException:
        raise

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        print(f"CV analysis failed: {exc}")

        raise HTTPException(
            status_code=500,
            detail="CV analysis failed.",
        ) from exc

    finally:

        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


# =========================================================
# HEALTH
# =========================================================

@router.get(
    "/health",
    tags=["Health"],
)
async def health_check() -> dict[str, str]:

    return {
        "status": "healthy",
        "service": "AI CV Assistant",
    }


# =========================================================
# GET COMPLETE ANALYSIS
# =========================================================

@router.get(
    "/analysis/{request_id}",
    response_model=AnalysisResult,
)
async def get_analysis(
    request: Request,
    request_id: str,
) -> AnalysisResult:

    result = request.app.state.analysis_store.get(
        request_id
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Analysis not found.",
        )

    return result


# =========================================================
# GET TAILORED CV
# =========================================================

@router.get(
    "/analysis/{request_id}/cv",
)
async def get_tailored_cv(
    request: Request,
    request_id: str,
):

    result = request.app.state.analysis_store.get(
        request_id
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Analysis not found.",
        )

    return result.tailored_cv


# =========================================================
# GET INTERVIEW PREPARATION
# =========================================================

@router.get(
    "/analysis/{request_id}/interview",
)
async def get_interview_preparation(
    request: Request,
    request_id: str,
):

    result = request.app.state.analysis_store.get(
        request_id
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Analysis not found.",
        )

    return result.interview_preparation