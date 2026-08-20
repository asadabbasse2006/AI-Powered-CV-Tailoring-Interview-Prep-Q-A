from enum import Enum

from pydantic import BaseModel, Field


class InterviewCategory(str, Enum):
    TECHNICAL = "technical"
    PROJECT = "project"
    EXPERIENCE = "experience"
    BEHAVIORAL = "behavioral"
    JOB_SPECIFIC = "job_specific"
    GAP = "gap"


class InterviewDifficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class InterviewQuestion(BaseModel):
    question_id: str
    category: InterviewCategory
    difficulty: InterviewDifficulty
    question: str
    reason: str | None = None
    related_requirement_id: str | None = None
    related_evidence_ids: list[str] = Field(default_factory=list)


class InterviewAnswer(BaseModel):
    question_id: str
    suggested_answer: str
    evidence_ids: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class InterviewPreparation(BaseModel):
    questions: list[InterviewQuestion] = Field(default_factory=list)
    answers: list[InterviewAnswer] = Field(default_factory=list)