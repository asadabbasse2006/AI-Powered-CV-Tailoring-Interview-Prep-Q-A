from datetime import datetime
from pathlib import Path
from time import perf_counter
from uuid import uuid4

from src.ai_cv_assistant.schemas.processing import (
    AnalysisResult,
    ProcessingMetadata,
    ProcessingStatus,
)
from src.ai_cv_assistant.services.cv.cv_pipeline import CVPipeline
from src.ai_cv_assistant.services.cv.cv_tailor import CVTailor
from src.ai_cv_assistant.services.interview.llm_interview_preparer import (
    LLMInterviewPreparer,
)
from src.ai_cv_assistant.services.job.jd_pipeline import JDPipeline
from src.ai_cv_assistant.services.matching.matching_pipeline import (
    MatchingPipeline,
)


class AnalysisPipeline:

#Asad Abbas

    def __init__(
        self,
        cv_pipeline: CVPipeline,
        jd_pipeline: JDPipeline,
        matching_pipeline: MatchingPipeline,
        cv_tailor: CVTailor,
        interview_preparer: LLMInterviewPreparer,
        model_name: str | None = None,
    ) -> None:
        self.cv_pipeline = cv_pipeline
        self.jd_pipeline = jd_pipeline
        self.matching_pipeline = matching_pipeline
        self.cv_tailor = cv_tailor
        self.interview_preparer = interview_preparer
        self.model_name = model_name

    def analyze(
        self,
        cv_file_path: str | Path,
        jd_text: str,
    ) -> AnalysisResult:
        """
        Execute the complete CV and job analysis workflow.

        Args:
            cv_file_path:
                Path to the candidate's CV PDF.

            jd_text:
                Raw job-description text.

        Returns:
            AnalysisResult containing:

            - candidate profile
            - job profile
            - candidate-job match
            - tailored CV
            - interview preparation
        """

        self._validate_inputs(
            cv_file_path=cv_file_path,
            jd_text=jd_text,
        )

        request_id = f"request-{uuid4()}"

        started_at = perf_counter()
        created_at = datetime.now()

        try:
            # ---------------------------------------------------------
            # Step 1: Process candidate CV
            # ---------------------------------------------------------

            candidate = self.cv_pipeline.process_file(
                cv_file_path
            )

            # ---------------------------------------------------------
            # Step 2: Process job description
            # ---------------------------------------------------------

            job = self.jd_pipeline.process(
                jd_text
            )

            # ---------------------------------------------------------
            # Step 3: Match candidate against job
            # ---------------------------------------------------------

            match = self.matching_pipeline.process(
                candidate=candidate,
                job=job,
            )

            # ---------------------------------------------------------
            # Step 4: Tailor CV for target job
            # ---------------------------------------------------------

            tailored_cv = self.cv_tailor.tailor(
                candidate=candidate,
                job=job,
                match=match,
            )

            # ---------------------------------------------------------
            # Step 5: Generate interview preparation
            # ---------------------------------------------------------

            interview_preparation = (
                self.interview_preparer.prepare(
                    candidate=candidate,
                    job=job,
                    match=match,
                    tailored_cv=tailored_cv,
                )
            )

            # ---------------------------------------------------------
            # Step 6: Build final result
            # ---------------------------------------------------------

            completed_at = datetime.now()

            processing_time = (
                perf_counter() - started_at
            )

            metadata = ProcessingMetadata(
                request_id=request_id,
                status=ProcessingStatus.COMPLETED,
                created_at=created_at,
                completed_at=completed_at,
                model_name=self.model_name,
                processing_time_seconds=processing_time,
            )

            return AnalysisResult(
                metadata=metadata,
                candidate=candidate,
                job=job,
                match=match,
                tailored_cv=tailored_cv,
                interview_preparation=interview_preparation,
            )

        except Exception:
            raise

    @staticmethod
    def _validate_inputs(
        cv_file_path: str | Path,
        jd_text: str,
    ) -> None:
        """
        Validate inputs before starting the pipeline.
        """

        if not isinstance(
            cv_file_path,
            (str, Path),
        ):
            raise TypeError(
                "cv_file_path must be a string or pathlib.Path."
            )

        if not str(cv_file_path).strip():
            raise ValueError(
                "cv_file_path cannot be empty."
            )

        if not isinstance(jd_text, str):
            raise TypeError(
                "jd_text must be a string."
            )

        if not jd_text.strip():
            raise ValueError(
                "jd_text cannot be empty."
            )