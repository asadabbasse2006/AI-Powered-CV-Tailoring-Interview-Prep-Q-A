from datetime import date, datetime

from src.ai_cv_assistant.schemas.candidate import (
    Achievement,
    CandidateEvidence,
    CandidateProfile,
    Certification,
    ConfidenceLevel,
    Education,
    EvidenceType,
    Experience,
    Project,
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
    JobKeyword,
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
from src.ai_cv_assistant.schemas.processing import (
    AnalysisResult,
    ProcessingMetadata,
    ProcessingStatus,
)


def test_education_schema():
    education = Education(
        institution="COMSATS University Islamabad",
        degree="BS Software Engineering",
        field_of_study="Software Engineering",
        start_date=date(2024, 9, 1),
        is_current=True,
        gpa="3.50",
        location="Sahiwal, Pakistan",
    )

    assert education.institution == "COMSATS University Islamabad"
    assert education.degree == "BS Software Engineering"
    assert education.is_current is True
    assert education.gpa == "3.50"


def test_experience_schema():
    experience = Experience(
        company="Fantech Labs",
        job_title="Software Engineering Intern",
        location="Pakistan",
        start_date=date(2026, 7, 6),
        is_current=True,
        description="Worked on backend development.",
        responsibilities=[
            "Developed REST APIs",
            "Worked with Python",
        ],
        technologies=[
            "Python",
            "FastAPI",
        ],
    )

    assert experience.company == "Fantech Labs"
    assert experience.job_title == "Software Engineering Intern"
    assert "Python" in experience.technologies
    assert len(experience.responsibilities) == 2


def test_project_schema():
    project = Project(
        name="Patient Management System",
        description="A backend application for managing patient records.",
        technologies=[
            "Python",
            "FastAPI",
        ],
        responsibilities=[
            "Developed CRUD APIs",
            "Implemented API endpoints",
        ],
    )

    assert project.name == "Patient Management System"
    assert "FastAPI" in project.technologies
    assert len(project.responsibilities) == 2


def test_skill_schema():
    skill = Skill(
        name="FastAPI",
        category=SkillCategory.FRAMEWORK,
        evidence_ids=["evidence-001"],
    )

    assert skill.name == "FastAPI"
    assert skill.category == SkillCategory.FRAMEWORK
    assert "evidence-001" in skill.evidence_ids


def test_candidate_evidence_schema():
    evidence = CandidateEvidence(
        evidence_id="evidence-001",
        evidence_type=EvidenceType.PROJECT,
        claim="FastAPI development experience",
        evidence_text=(
            "Developed a Patient Management System using FastAPI."
        ),
        source_section="Projects",
        source_reference="Patient Management System",
        confidence=ConfidenceLevel.HIGH,
    )

    assert evidence.evidence_id == "evidence-001"
    assert evidence.evidence_type == EvidenceType.PROJECT
    assert evidence.confidence == ConfidenceLevel.HIGH
    assert "FastAPI" in evidence.evidence_text


def test_candidate_profile_schema():
    candidate = CandidateProfile(
        candidate_id="candidate-001",
        name="Asad Abbas",
        email="asadse2006@gmail.com",
        location="Pakistan",
        summary="Software engineering student interested in backend development.",
        education=[
            Education(
                institution="COMSATS University Islamabad",
                degree="BS Software Engineering",
                is_current=True,
            )
        ],
        experience=[
            Experience(
                company="Fantech Labs",
                job_title="Software Engineering Intern",
                is_current=True,
            )
        ],
        project=[
            Project(
                name="Patient Management System",
                technologies=["Python", "FastAPI"],
            )
        ],
        skills=[
            Skill(
                name="Python",
                category=SkillCategory.PROGRAMMING_LANGUAGE,
            ),
            Skill(
                name="FastAPI",
                category=SkillCategory.FRAMEWORK,
            ),
        ],
        certifications=[
            Certification(
                name="Python Certificate",
                issuing_organization="Google",
            )
        ],
        achievements=[
            Achievement(
                title="Programming Competition Participant",
            )
        ],
        evidence=[
            CandidateEvidence(
                evidence_id="evidence-001",
                evidence_type=EvidenceType.PROJECT,
                claim="FastAPI experience",
                evidence_text="Developed a project using FastAPI.",
            )
        ],
    )

    assert candidate.name == "Asad Abbas"
    assert len(candidate.education) == 1
    assert len(candidate.experience) == 1
    assert len(candidate.project) == 1
    assert len(candidate.skills) == 2
    assert len(candidate.certifications) == 1
    assert len(candidate.achievements) == 1
    assert len(candidate.evidence) == 1


def test_job_requirement_schema():
    requirement = JobRequirement(
        requirement_id="requirement-001",
        name="FastAPI",
        category=RequirementCategory.TECHNICAL_SKILL,
        importance=RequirementImportance.REQUIRED,
        description="Experience developing APIs using FastAPI.",
        source_text="Experience building REST APIs using FastAPI.",
    )

    assert requirement.name == "FastAPI"
    assert requirement.category == RequirementCategory.TECHNICAL_SKILL
    assert requirement.importance == RequirementImportance.REQUIRED
    assert "FastAPI" in requirement.source_text


def test_job_keyword_schema():
    keyword = JobKeyword(
        keyword="FastAPI",
        importance=10,
        source_text="Experience developing REST APIs using FastAPI.",
    )

    assert keyword.keyword == "FastAPI"
    assert keyword.importance == 10


def test_job_profile_schema():
    job = JobProfile(
        job_id="job-001",
        url="https://example.com/jobs/backend-developer",
        title="Backend Developer",
        company="Fantech Labs",
        location="Okara, Pakistan",
        employment_type="Full-time",
        description="Backend development role.",
        responsibilities=[
            "Develop REST APIs",
            "Maintain backend services",
        ],
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
        keywords=[
            JobKeyword(
                keyword="Python",
                importance=10,
            ),
            JobKeyword(
                keyword="FastAPI",
                importance=9,
            ),
        ],
    )

    assert job.title == "Backend Developer"
    assert job.company == "Fantech Labs"
    assert len(job.requirements) == 2
    assert len(job.keywords) == 2


def test_match_result_schema():
    match = MatchResult(
        requirement_id="requirement-001",
        candidate_evidence_ids=["evidence-001"],
        status=MatchStatus.STRONG_MATCH,
        confidence=MatchConfidence.HIGH,
        reason="Candidate has direct FastAPI project experience.",
    )

    assert match.requirement_id == "requirement-001"
    assert match.status == MatchStatus.STRONG_MATCH
    assert match.confidence == MatchConfidence.HIGH
    assert "evidence-001" in match.candidate_evidence_ids


def test_match_summary_schema():
    summary = MatchSummary(
        total_requirements=5,
        strong_matches=3,
        partial_matches=1,
        no_evidence=1,
        conflicts=0,
    )

    assert summary.total_requirements == 5
    assert summary.strong_matches == 3
    assert summary.partial_matches == 1
    assert summary.no_evidence == 1
    assert summary.conflicts == 0


def test_candidate_job_match_schema():
    match = CandidateJobMatch(
        results=[
            MatchResult(
                requirement_id="requirement-001",
                candidate_evidence_ids=["evidence-001"],
                status=MatchStatus.STRONG_MATCH,
                confidence=MatchConfidence.HIGH,
                reason="Direct evidence found.",
            )
        ],
        summary=MatchSummary(
            total_requirements=1,
            strong_matches=1,
        ),
    )

    assert len(match.results) == 1
    assert match.summary.strong_matches == 1


def test_generated_claim_schema():
    claim = GeneratedClaim(
        claim_id="claim-001",
        content="Developed REST APIs using FastAPI.",
        evidence_ids=["evidence-001"],
        supported=True,
        validation_reason="Claim is directly supported by the candidate's CV.",
    )

    assert claim.claim_id == "claim-001"
    assert claim.supported is True
    assert "evidence-001" in claim.evidence_ids


def test_cv_section_schema():
    section = CVSection(
        section_type=CVSectionType.EXPERIENCE,
        title="Professional Experience",
        order=2,
        content="Software Engineering Intern at Example Company.",
        claims=[
            GeneratedClaim(
                claim_id="claim-001",
                content="Developed REST APIs using FastAPI.",
                evidence_ids=["evidence-001"],
                supported=True,
            )
        ],
    )

    assert section.section_type == CVSectionType.EXPERIENCE
    assert section.title == "Professional Experience"
    assert section.order == 2
    assert len(section.claims) == 1


def test_cv_validation_schema():
    validation = CVValidationResult(
        status=CVValidationStatus.PASSED,
        unsupported_claim_ids=[],
        warnings=[],
        revision_count=0,
    )

    assert validation.status == CVValidationStatus.PASSED
    assert validation.revision_count == 0
    assert len(validation.unsupported_claim_ids) == 0


def test_tailored_cv_schema():
    cv = TailoredCV(
        candidate_name="Asad Abbas",
        target_job_title="Backend Developer",
        target_company="Fantech Labs",
        sections=[
            CVSection(
                section_type=CVSectionType.SUMMARY,
                title="Professional Summary",
                order=1,
                content=(
                    "Software engineering student with "
                    "Python and FastAPI experience."
                ),
            )
        ],
        markdown=(
            "# Asad Abbas\n\n"
            "## Professional Summary\n\n"
            "Software engineering student with Python and FastAPI experience."
        ),
        validation=CVValidationResult(
            status=CVValidationStatus.PASSED,
        ),
    )

    assert cv.candidate_name == "Asad Abbas"
    assert cv.target_job_title == "Backend Developer"
    assert len(cv.sections) == 1
    assert cv.validation.status == CVValidationStatus.PASSED
    assert "# Asad Abbas" in cv.markdown


def test_interview_question_schema():
    question = InterviewQuestion(
        question_id="question-001",
        category=InterviewCategory.PROJECT,
        difficulty=InterviewDifficulty.MEDIUM,
        question="How did you implement the FastAPI project?",
        reason="The job requires FastAPI experience.",
        related_requirement_id="requirement-001",
        related_evidence_ids=["evidence-001"],
    )

    assert question.question_id == "question-001"
    assert question.category == InterviewCategory.PROJECT
    assert question.difficulty == InterviewDifficulty.MEDIUM
    assert "FastAPI" in question.question


def test_interview_answer_schema():
    answer = InterviewAnswer(
        question_id="question-001",
        suggested_answer=(
            "I developed a Patient Management System using FastAPI "
            "with CRUD functionality."
        ),
        evidence_ids=["evidence-001"],
        warnings=[],
    )

    assert answer.question_id == "question-001"
    assert "FastAPI" in answer.suggested_answer
    assert "evidence-001" in answer.evidence_ids


def test_interview_preparation_schema():
    preparation = InterviewPreparation(
        questions=[
            InterviewQuestion(
                question_id="question-001",
                category=InterviewCategory.TECHNICAL,
                difficulty=InterviewDifficulty.MEDIUM,
                question="What is FastAPI?",
            )
        ],
        answers=[
            InterviewAnswer(
                question_id="question-001",
                suggested_answer=(
                    "FastAPI is a modern Python web framework "
                    "for building APIs."
                ),
            )
        ],
    )

    assert len(preparation.questions) == 1
    assert len(preparation.answers) == 1


def test_processing_metadata_schema():
    metadata = ProcessingMetadata(
        request_id="request-001",
        status=ProcessingStatus.COMPLETED,
        created_at=datetime.now(),
        completed_at=datetime.now(),
        model_name="test-model",
        processing_time_seconds=5.2,
        validation_attempts=1,
    )

    assert metadata.request_id == "request-001"
    assert metadata.status == ProcessingStatus.COMPLETED
    assert metadata.processing_time_seconds == 5.2
    assert metadata.validation_attempts == 1


def test_complete_analysis_result():
    candidate = CandidateProfile(
        candidate_id="candidate-001",
        name="Asad Abbas",
        skills=[
            Skill(
                name="Python",
                category=SkillCategory.PROGRAMMING_LANGUAGE,
                evidence_ids=["evidence-001"],
            )
        ],
        evidence=[
            CandidateEvidence(
                evidence_id="evidence-001",
                evidence_type=EvidenceType.SKILL,
                claim="Python experience",
                evidence_text="Developed applications using Python.",
            )
        ],
    )

    job = JobProfile(
        job_id="job-001",
        url="https://example.com/jobs/backend-developer",
        title="Backend Developer",
        company="Fantech Labs",
        requirements=[
            JobRequirement(
                requirement_id="requirement-001",
                name="Python",
                category=RequirementCategory.TECHNICAL_SKILL,
                importance=RequirementImportance.REQUIRED,
                source_text="Strong Python programming skills.",
            )
        ],
    )

    match = CandidateJobMatch(
        results=[
            MatchResult(
                requirement_id="requirement-001",
                candidate_evidence_ids=["evidence-001"],
                status=MatchStatus.STRONG_MATCH,
                confidence=MatchConfidence.HIGH,
                reason="Python is directly supported by candidate evidence.",
            )
        ],
        summary=MatchSummary(
            total_requirements=1,
            strong_matches=1,
        ),
    )

    tailored_cv = TailoredCV(
        candidate_name="Asad Abbas",
        target_job_title="Backend Developer",
        target_company="Fantech Labs",
        sections=[
            CVSection(
                section_type=CVSectionType.SKILLS,
                title="Skills",
                order=1,
                content="Python",
            )
        ],
        markdown="# Asad Abbas\n\n## Skills\n\n- Python",
        validation=CVValidationResult(
            status=CVValidationStatus.PASSED,
        ),
    )

    interview = InterviewPreparation(
        questions=[
            InterviewQuestion(
                question_id="question-001",
                category=InterviewCategory.TECHNICAL,
                difficulty=InterviewDifficulty.EASY,
                question="How comfortable are you with Python?",
                related_requirement_id="requirement-001",
                related_evidence_ids=["evidence-001"],
            )
        ],
        answers=[
            InterviewAnswer(
                question_id="question-001",
                suggested_answer=(
                    "I have used Python to develop several software projects."
                ),
                evidence_ids=["evidence-001"],
            )
        ],
    )

    result = AnalysisResult(
        metadata=ProcessingMetadata(
            request_id="request-001",
            status=ProcessingStatus.COMPLETED,
            created_at=datetime.now(),
        ),
        candidate=candidate,
        job=job,
        match=match,
        tailored_cv=tailored_cv,
        interview_preparation=interview,
    )

    assert result.metadata.status == ProcessingStatus.COMPLETED
    assert result.candidate.name == "Asad Abbas"
    assert result.job.title == "Backend Developer"
    assert result.match.summary.strong_matches == 1
    assert result.tailored_cv.validation.status == CVValidationStatus.PASSED
    assert len(result.interview_preparation.questions) == 1