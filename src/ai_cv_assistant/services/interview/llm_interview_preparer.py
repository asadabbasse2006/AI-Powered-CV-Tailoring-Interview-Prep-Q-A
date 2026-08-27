from src.ai_cv_assistant.schemas.candidate import CandidateProfile
from src.ai_cv_assistant.schemas.cv import TailoredCV
from src.ai_cv_assistant.schemas.interview import (
    InterviewPreparation,
)
from src.ai_cv_assistant.schemas.job import JobProfile
from src.ai_cv_assistant.schemas.matching import CandidateJobMatch
from src.ai_cv_assistant.services.llm.client import LLMClient


class LLMInterviewPreparer:
    """
    Generates interview questions and suggested answers using an LLM.

    The LLM receives:
    - candidate information
    - target job description
    - candidate-job matching results
    - tailored CV

    The service validates all references returned by the LLM so that
    generated questions and answers cannot reference nonexistent
    candidate evidence, job requirements, or interview questions.
    """

    def __init__(self, llm_client: LLMClient) -> None:
        if not isinstance(llm_client, LLMClient):
            raise TypeError(
                "llm_client must be an instance of LLMClient."
            )

        self.llm = llm_client

    def prepare(
        self,
        candidate: CandidateProfile,
        job: JobProfile,
        match: CandidateJobMatch,
        tailored_cv: TailoredCV,
    ) -> InterviewPreparation:
        """
        Generate interview preparation for a candidate and target job.
        """

        self._validate_inputs(
            candidate=candidate,
            job=job,
            match=match,
            tailored_cv=tailored_cv,
        )

        prompt = self._build_prompt(
            candidate=candidate,
            job=job,
            match=match,
            tailored_cv=tailored_cv,
        )

        response = self.llm.generate_structured(
            prompt=prompt,
            response_schema=InterviewPreparation.model_json_schema(),
        )

        # ---------------------------------------------------------
        # Validate basic LLM response structure
        # ---------------------------------------------------------

        if not isinstance(response, dict):
            raise TypeError(
                "LLM response must be a dictionary."
            )

        required_keys = {"questions", "answers"}
        missing_keys = required_keys - response.keys()

        if missing_keys:
            raise ValueError(
                "LLM response is missing required fields: "
                f"{sorted(missing_keys)}"
            )

        if not isinstance(response["questions"], list):
            raise TypeError(
                "LLM response 'questions' must be a list."
            )

        if not isinstance(response["answers"], list):
            raise TypeError(
                "LLM response 'answers' must be a list."
            )

        # ---------------------------------------------------------
        # Validate response against the InterviewPreparation schema
        # ---------------------------------------------------------

        try:
            preparation = InterviewPreparation.model_validate(
                response
            )
        except Exception as exc:
            raise ValueError(
                "LLM returned an invalid interview preparation response."
            ) from exc

        # ---------------------------------------------------------
        # Validate references returned by the LLM
        # ---------------------------------------------------------

        self._validate_references(
            preparation=preparation,
            candidate=candidate,
            job=job,
        )

        return preparation

    @staticmethod
    def _validate_inputs(
        candidate: CandidateProfile,
        job: JobProfile,
        match: CandidateJobMatch,
        tailored_cv: TailoredCV,
    ) -> None:
        """Validate all service inputs."""

        if not isinstance(candidate, CandidateProfile):
            raise TypeError(
                "candidate must be a CandidateProfile."
            )

        if not isinstance(job, JobProfile):
            raise TypeError(
                "job must be a JobProfile."
            )

        if not isinstance(match, CandidateJobMatch):
            raise TypeError(
                "match must be a CandidateJobMatch."
            )

        if not isinstance(tailored_cv, TailoredCV):
            raise TypeError(
                "tailored_cv must be a TailoredCV."
            )

    @staticmethod
    def _build_prompt(
        candidate: CandidateProfile,
        job: JobProfile,
        match: CandidateJobMatch,
        tailored_cv: TailoredCV,
    ) -> str:
        """
        Build the prompt sent to the LLM.

        The tailored CV Markdown is intentionally included as raw
        Markdown because this is the exact document the interviewer
        should review.
        """

        candidate_json = candidate.model_dump_json(
            indent=2
        )

        job_json = job.model_dump_json(
            indent=2
        )

        match_json = match.model_dump_json(
            indent=2
        )

        return f"""
You are an expert technical interviewer and interview preparation
assistant.

Your task is to generate interview questions and suggested answers
for a candidate applying to the target job.

You MUST use only information supported by the candidate profile,
candidate evidence, job requirements, matching analysis, and tailored
CV provided below.

Do NOT invent:
- skills
- work experience
- projects
- technologies
- certifications
- achievements
- responsibilities
- candidate evidence

Every interview question should be relevant to the target job and
the candidate's actual background.

Prioritize questions based on:

1. Important job requirements.
2. Strong candidate-job matches.
3. Partial matches that should be explored.
4. Skills and technologies appearing in the tailored CV.
5. Candidate projects and professional experience.
6. Areas where the interviewer may want to verify the candidate's
   actual experience.

For questions related to candidate experience, reference the relevant
candidate evidence IDs.

For questions related to job requirements, reference the relevant
job requirement ID.

For every suggested answer, use only information supported by the
candidate evidence.

Every evidence ID returned by you MUST exist in the candidate's
evidence.

Every requirement ID returned by you MUST exist in the job's
requirements.

Every answer's question_id MUST correspond to a question generated
in the same response.

Return ONLY structured data matching the provided response schema.

==================================================
CANDIDATE PROFILE
==================================================

{candidate_json}

==================================================
JOB PROFILE
==================================================

{job_json}

==================================================
CANDIDATE-JOB MATCH
==================================================

{match_json}

==================================================
TAILORED CV
==================================================

{tailored_cv.markdown}

==================================================
TASK
==================================================

Generate interview preparation containing:

- Technical questions
- Project-based questions
- Experience questions
- Behavioral questions where appropriate
- Job-specific questions
- Questions about important matched requirements

For each question:

- provide a category
- provide a difficulty
- provide the question
- explain why the question is relevant
- reference the related requirement when applicable
- reference supporting candidate evidence when applicable

For each answer:

- provide a suggested answer
- reference the candidate evidence supporting the answer
- include warnings when the candidate should avoid making unsupported
  claims

Remember:

NEVER invent candidate experience.

Only use facts supported by the supplied candidate profile and
candidate evidence.
""".strip()

    @staticmethod
    def _validate_references(
        preparation: InterviewPreparation,
        candidate: CandidateProfile,
        job: JobProfile,
    ) -> None:
        """
        Validate all IDs returned by the LLM.

        LLM output can be valid JSON while still containing
        hallucinated IDs, so this validation is mandatory.
        """

        valid_evidence_ids = {
            evidence.evidence_id
            for evidence in candidate.evidence
        }

        valid_requirement_ids = {
            requirement.requirement_id
            for requirement in job.requirements
        }

        # ---------------------------------------------------------
        # Validate questions
        # ---------------------------------------------------------

        for question in preparation.questions:

            if question.related_requirement_id is not None:
                if (
                    question.related_requirement_id
                    not in valid_requirement_ids
                ):
                    raise ValueError(
                        "unknown requirement ID: "
                        f"{question.related_requirement_id}"
                    )

            for evidence_id in question.related_evidence_ids:
                if evidence_id not in valid_evidence_ids:
                    raise ValueError(
                        "unknown evidence ID: "
                        f"{evidence_id}"
                    )

        # ---------------------------------------------------------
        # Collect valid question IDs
        # ---------------------------------------------------------

        question_ids = {
            question.question_id
            for question in preparation.questions
        }

        # ---------------------------------------------------------
        # Validate answers
        # ---------------------------------------------------------

        for answer in preparation.answers:

            if answer.question_id not in question_ids:
                raise ValueError(
                    "unknown question ID: "
                    f"{answer.question_id}"
                )

            for evidence_id in answer.evidence_ids:
                if evidence_id not in valid_evidence_ids:
                    raise ValueError(
                        "unknown evidence ID: "
                        f"{evidence_id}"
                    )
