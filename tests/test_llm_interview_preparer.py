from typing import Any

import pytest

from src.ai_cv_assistant.schemas.candidate import (
    CandidateEvidence,
    CandidateProfile,
    EvidenceType,
    Skill,
    SkillCategory,
)
from src.ai_cv_assistant.schemas.cv import (
    CVSection,
    CVSectionType,
    CVValidationResult,
    CVValidationStatus,
    GeneratedClaim,
    TailoredCV,
)
from src.ai_cv_assistant.schemas.interview import (
    InterviewAnswer,
    InterviewCategory,
    InterviewDifficulty,
    InterviewPreparation,
    InterviewQuestion,
)
from src.ai_cv_assistant.schemas.job import (
    JobProfile,
    JobRequirement,
    RequirementCategory,
    RequirementImportance,
)
from src.ai_cv_assistant.schemas.matching import (
    CandidateJobMatch,
    MatchConfidence,
    MatchResult,
    MatchStatus,
    MatchSummary,
)
from src.ai_cv_assistant.services.interview.llm_interview_preparer import (
    LLMInterviewPreparer,
)
from src.ai_cv_assistant.services.llm.client import LLMClient


class FakeLLMClient(LLMClient):

    def __init__(self, response: dict[str, Any]):
        self.response = response
        self.last_prompt = None
        self.last_response_schema = None

    def generate_structured(
        self,
        prompt: str,
        response_schema: Any | None = None,
    ) -> dict[str, Any]:
        self.last_prompt = prompt
        self.last_response_schema = response_schema
        return self.response


@pytest.fixture
def candidate():

    return CandidateProfile(
        candidate_id="candidate-001",
        name="Asad Abbas",
        summary=(
            "Software Engineering student with Python "
            "and FastAPI experience."
        ),
        skills=[
            Skill(
                name="Python",
                category=SkillCategory.PROGRAMMING_LANGUAGE,
                evidence_ids=["evidence-001"],
            ),
            Skill(
                name="FastAPI",
                category=SkillCategory.FRAMEWORK,
                evidence_ids=["evidence-002"],
            ),
        ],
        evidence=[
            CandidateEvidence(
                evidence_id="evidence-001",
                evidence_type=EvidenceType.SKILL,
                claim="Python",
                evidence_text="Python",
            ),
            CandidateEvidence(
                evidence_id="evidence-002",
                evidence_type=EvidenceType.SKILL,
                claim="FastAPI",
                evidence_text="FastAPI",
            ),
        ],
    )


@pytest.fixture
def job():

    return JobProfile(
        job_id="job-001",
        url="https://example.com/backend",
        title="Backend Developer",
        company="Example Technologies",
        requirements=[
            JobRequirement(
                requirement_id="requirement-001",
                name="Python",
                category=RequirementCategory.TECHNICAL_SKILL,
                importance=RequirementImportance.REQUIRED,
            ),
            JobRequirement(
                requirement_id="requirement-002",
                name="FastAPI",
                category=RequirementCategory.TECHNICAL_SKILL,
                importance=RequirementImportance.PREFERRED,
            ),
        ],
    )


@pytest.fixture
def match():

    return CandidateJobMatch(
        results=[
            MatchResult(
                requirement_id="requirement-001",
                candidate_evidence_ids=["evidence-001"],
                status=MatchStatus.STRONG_MATCH,
                confidence=MatchConfidence.HIGH,
                reason="Python is directly supported.",
            ),
            MatchResult(
                requirement_id="requirement-002",
                candidate_evidence_ids=["evidence-002"],
                status=MatchStatus.STRONG_MATCH,
                confidence=MatchConfidence.HIGH,
                reason="FastAPI is directly supported.",
            ),
        ],
        summary=MatchSummary(
            total_requirements=2,
            strong_matches=2,
        ),
    )


@pytest.fixture
def tailored_cv():

    return TailoredCV(
        candidate_name="Asad Abbas",
        target_job_title="Backend Developer",
        target_company="Example Technologies",
        sections=[
            CVSection(
                section_type=CVSectionType.SKILLS,
                title="Skills",
                order=1,
                content="- Python\n- FastAPI",
                claims=[
                    GeneratedClaim(
                        claim_id="claim-001",
                        content="Python",
                        evidence_ids=["evidence-001"],
                        supported=True,
                    ),
                    GeneratedClaim(
                        claim_id="claim-002",
                        content="FastAPI",
                        evidence_ids=["evidence-002"],
                        supported=True,
                    ),
                ],
            )
        ],
        markdown=(
            "# Asad Abbas\n\n"
            "## Skills\n\n"
            "- Python\n"
            "- FastAPI"
        ),
        validation=CVValidationResult(
            status=CVValidationStatus.PASSED,
        ),
    )


@pytest.fixture
def llm_response():

    return {
        "questions": [
            {
                "question_id": "question-001",
                "category": "technical",
                "difficulty": "medium",
                "question": (
                    "How have you used Python in your projects?"
                ),
                "reason": (
                    "Python is a required job skill."
                ),
                "related_requirement_id": "requirement-001",
                "related_evidence_ids": ["evidence-001"],
            },
            {
                "question_id": "question-002",
                "category": "technical",
                "difficulty": "medium",
                "question": (
                    "How did you use FastAPI in your projects?"
                ),
                "reason": (
                    "FastAPI is a preferred job skill."
                ),
                "related_requirement_id": "requirement-002",
                "related_evidence_ids": ["evidence-002"],
            },
        ],
        "answers": [
            {
                "question_id": "question-001",
                "suggested_answer": (
                    "I have used Python in my software projects."
                ),
                "evidence_ids": ["evidence-001"],
                "warnings": [],
            },
            {
                "question_id": "question-002",
                "suggested_answer": (
                    "I used FastAPI to develop backend APIs."
                ),
                "evidence_ids": ["evidence-002"],
                "warnings": [],
            },
        ],
    }


def test_prepare_generates_interview_preparation(
    candidate,
    job,
    match,
    tailored_cv,
    llm_response,
):
    llm = FakeLLMClient(llm_response)

    preparer = LLMInterviewPreparer(llm)

    result = preparer.prepare(
        candidate=candidate,
        job=job,
        match=match,
        tailored_cv=tailored_cv,
    )

    assert isinstance(result, InterviewPreparation)
    assert len(result.questions) == 2
    assert len(result.answers) == 2


def test_prompt_contains_tailored_cv(
    candidate,
    job,
    match,
    tailored_cv,
    llm_response,
):
    llm = FakeLLMClient(llm_response)

    preparer = LLMInterviewPreparer(llm)

    preparer.prepare(
        candidate=candidate,
        job=job,
        match=match,
        tailored_cv=tailored_cv,
    )

    assert tailored_cv.markdown in llm.last_prompt


def test_prompt_contains_job(
    candidate,
    job,
    match,
    tailored_cv,
    llm_response,
):
    llm = FakeLLMClient(llm_response)

    preparer = LLMInterviewPreparer(llm)

    preparer.prepare(
        candidate=candidate,
        job=job,
        match=match,
        tailored_cv=tailored_cv,
    )

    assert "Backend Developer" in llm.last_prompt
    assert "Example Technologies" in llm.last_prompt


def test_prompt_contains_candidate(
    candidate,
    job,
    match,
    tailored_cv,
    llm_response,
):
    llm = FakeLLMClient(llm_response)

    preparer = LLMInterviewPreparer(llm)

    preparer.prepare(
        candidate=candidate,
        job=job,
        match=match,
        tailored_cv=tailored_cv,
    )

    assert "Asad Abbas" in llm.last_prompt
    assert "Python" in llm.last_prompt
    assert "FastAPI" in llm.last_prompt


def test_response_schema_is_provided(
    candidate,
    job,
    match,
    tailored_cv,
    llm_response,
):
    llm = FakeLLMClient(llm_response)

    preparer = LLMInterviewPreparer(llm)

    preparer.prepare(
        candidate=candidate,
        job=job,
        match=match,
        tailored_cv=tailored_cv,
    )

    assert llm.last_response_schema is not None
    assert "properties" in llm.last_response_schema


def test_invalid_evidence_id_is_rejected(
    candidate,
    job,
    match,
    tailored_cv,
    llm_response,
):
    llm_response["questions"][0]["related_evidence_ids"] = [
        "fake-evidence"
    ]

    llm = FakeLLMClient(llm_response)

    preparer = LLMInterviewPreparer(llm)

    with pytest.raises(ValueError, match="unknown evidence ID"):
        preparer.prepare(
            candidate=candidate,
            job=job,
            match=match,
            tailored_cv=tailored_cv,
        )


def test_invalid_requirement_id_is_rejected(
    candidate,
    job,
    match,
    tailored_cv,
    llm_response,
):
    llm_response["questions"][0][
        "related_requirement_id"
    ] = "fake-requirement"

    llm = FakeLLMClient(llm_response)

    preparer = LLMInterviewPreparer(llm)

    with pytest.raises(ValueError, match="unknown requirement ID"):
        preparer.prepare(
            candidate=candidate,
            job=job,
            match=match,
            tailored_cv=tailored_cv,
        )


def test_invalid_answer_question_id_is_rejected(
    candidate,
    job,
    match,
    tailored_cv,
    llm_response,
):
    llm_response["answers"][0]["question_id"] = (
        "fake-question"
    )

    llm = FakeLLMClient(llm_response)

    preparer = LLMInterviewPreparer(llm)

    with pytest.raises(ValueError, match="unknown question ID"):
        preparer.prepare(
            candidate=candidate,
            job=job,
            match=match,
            tailored_cv=tailored_cv,
        )




def test_invalid_llm_response_is_rejected(
    candidate,
    job,
    match,
    tailored_cv,
):
    llm = FakeLLMClient(
        {
            "invalid": "response",
        }
    )

    preparer = LLMInterviewPreparer(llm)

    with pytest.raises(Exception):
        preparer.prepare(
            candidate=candidate,
            job=job,
            match=match,
            tailored_cv=tailored_cv,
        )