from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

from .candidate import CandidateProfile
from .cv import TailoredCV
from .interview import InterviewPreparation
from .job import JobProfile
from .matching import CandidateJobMatch


class ProcessingStatus(str, Enum):
    RECEIVED = "received"
    PROCESSING_CV = "processing_cv"
    PROCESSING_JOB = "processing_job"
    ANALYZING = "analyzing"
    MATCHING = "matching"
    TAILORING = "tailoring"
    VALIDATING = "validating"
    GENERATING_INTERVIEW_PREP = "generating_interview_prep"
    COMPLETED = "completed"
    FAILED = "failed"


class ProcessingMetadata(BaseModel):
    request_id: str
    status: ProcessingStatus
    created_at: datetime
    completed_at: datetime | None = None
    model_name: str | None = None
    processing_time_seconds: float | None = Field(
        default=None,
        ge=0,
    )

    validation_attempts: int = Field(
        default=0,
        ge=0,
    )


class AnalysisResult(BaseModel):
    metadata: ProcessingMetadata
    candidate: CandidateProfile
    job: JobProfile
    match: CandidateJobMatch
    tailored_cv: TailoredCV
    interview_preparation: InterviewPreparation