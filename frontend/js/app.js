"use strict";


/* =========================================================
   CONFIGURATION
========================================================= */

const API_BASE_URL =
    "http://127.0.0.1:8000/api/v1";


/* =========================================================
   APPLICATION STATE
========================================================= */

const state = {
    selectedFile: null,
    analysisResult: null,
    requestId: null,
};


/* =========================================================
   DOM ELEMENTS
========================================================= */

const elements = {};


/* =========================================================
   INITIALIZATION
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    () => {

        initializeElements();

        attachEventListeners();

        updateCharacterCount();

    }
);


/* =========================================================
   INITIALIZE ELEMENTS
========================================================= */

function initializeElements() {

    elements.form =
        document.getElementById(
            "analysis-form"
        );


    elements.cvInput =
        document.getElementById(
            "cv-file"
        );


    elements.fileUploadArea =
        document.getElementById(
            "file-upload-area"
        );


    elements.selectedFile =
        document.getElementById(
            "selected-file"
        );


    elements.selectedFileName =
        document.getElementById(
            "selected-file-name"
        );


    elements.removeFileButton =
        document.getElementById(
            "remove-file"
        );


    elements.jobDescription =
        document.getElementById(
            "job-description"
        );


    elements.charCount =
        document.getElementById(
            "match-score"
        );


    elements.analyzeButton =
        document.getElementById(
            "analyze-button"
        );


    elements.loadingState =
        document.getElementById(
            "loading-state"
        );


    elements.errorMessage =
        document.getElementById(
            "error-message"
        );


    elements.errorText =
        document.getElementById(
            "error-text"
        );


    elements.resultsSection =
        document.getElementById(
            "results"
        );


    elements.tailoredCVSection =
        document.getElementById(
            "tailored-cv"
        );


    elements.interviewSection =
        document.getElementById(
            "interview"
        );


    elements.newAnalysisSection =
        document.getElementById(
            "new-analysis"
        );


    elements.newAnalysisButton =
        document.getElementById(
            "new-analysis-button"
        );


    elements.copyCVButton =
        document.getElementById(
            "copy-cv"
        );


    elements.downloadCVButton =
        document.getElementById(
            "download-cv"
        );


    elements.tailoredCVContent =
        document.getElementById(
            "tailored-cv-content"
        );
}


/* =========================================================
   EVENT LISTENERS
========================================================= */

function attachEventListeners() {

    if (elements.cvInput) {

        elements.cvInput.addEventListener(
            "change",
            handleFileSelection
        );

    }


    if (elements.removeFileButton) {

        elements.removeFileButton.addEventListener(
            "click",
            removeSelectedFile
        );

    }


    if (elements.jobDescription) {

        elements.jobDescription.addEventListener(
            "input",
            updateCharacterCount
        );

    }


    if (elements.form) {

        elements.form.addEventListener(
            "submit",
            handleAnalysisSubmit
        );

    }


    if (elements.newAnalysisButton) {

        elements.newAnalysisButton.addEventListener(
            "click",
            resetApplication
        );

    }


    if (elements.copyCVButton) {

        elements.copyCVButton.addEventListener(
            "click",
            copyTailoredCV
        );

    }


    if (elements.downloadCVButton) {

        elements.downloadCVButton.addEventListener(
            "click",
            downloadTailoredCV
        );

    }
}


/* =========================================================
   FILE HANDLING
========================================================= */

function handleFileSelection(event) {

    const file =
        event.target.files[0];


    if (!file) {
        return;
    }


    /*
     * Validate PDF
     */

    if (
        file.type !== "application/pdf" &&
        !file.name
            .toLowerCase()
            .endsWith(".pdf")
    ) {

        showError(
            "Please upload a PDF CV."
        );

        elements.cvInput.value = "";

        return;
    }


    /*
     * Validate size
     */

    const maxSize =
        10 * 1024 * 1024;


    if (file.size > maxSize) {

        showError(
            "CV file is too large. Maximum allowed size is 10 MB."
        );

        elements.cvInput.value = "";

        return;
    }


    state.selectedFile = file;

    hideError();

    displaySelectedFile(file);
}


function displaySelectedFile(file) {

    if (!elements.selectedFile) {
        return;
    }


    if (elements.selectedFileName) {

        elements.selectedFileName.textContent =
            `${file.name} (${formatFileSize(file.size)})`;

    }


    elements.selectedFile.classList.remove(
        "hidden"
    );
}


function removeSelectedFile() {

    state.selectedFile = null;


    if (elements.cvInput) {
        elements.cvInput.value = "";
    }


    if (elements.selectedFile) {

        elements.selectedFile.classList.add(
            "hidden"
        );

    }
}


function formatFileSize(bytes) {

    if (bytes < 1024) {
        return `${bytes} B`;
    }


    if (bytes < 1024 * 1024) {

        return `${(
            bytes / 1024
        ).toFixed(1)} KB`;

    }


    return `${(
        bytes /
        (1024 * 1024)
    ).toFixed(1)} MB`;
}


/* =========================================================
   CHARACTER COUNT
========================================================= */

function updateCharacterCount() {

    if (
        !elements.jobDescription ||
        !elements.charCount
    ) {
        return;
    }


    const count =
        elements.jobDescription
            .value
            .length;


    elements.charCount.textContent =
        `${count.toLocaleString()} characters`;
}


/* =========================================================
   ANALYSIS SUBMISSION
========================================================= */

async function handleAnalysisSubmit(event) {

    event.preventDefault();

    hideError();


    /*
     * Validate CV
     */

    if (!state.selectedFile) {

        showError(
            "Please upload your CV before starting the analysis."
        );

        return;
    }


    /*
     * Validate job description
     */

    const jobDescription =
        elements.jobDescription
            ? elements.jobDescription.value.trim()
            : "";


    if (!jobDescription) {

        showError(
            "Please enter a job description."
        );

        return;
    }


    /*
     * Show loading
     */

    setAnalysisLoading(true);


    try {

        const formData =
            new FormData();


        formData.append(
            "cv",
            state.selectedFile
        );


        formData.append(
            "job_description",
            jobDescription
        );


        console.log(
            "Sending CV analysis request..."
        );


        const response =
            await fetch(
                `${API_BASE_URL}/analyze`,
                {
                    method: "POST",
                    body: formData,
                }
            );


        const data =
            await parseResponse(
                response
            );


        console.log(
            "API response:",
            data
        );


        if (!response.ok) {

            throw new Error(
                data?.detail ||
                "CV analysis failed."
            );

        }


        /*
         * Save result
         */

        state.analysisResult =
            data;


        state.requestId =
            data?.metadata?.request_id ||
            null;


        /*
         * Render everything
         */

        renderAnalysisResult(
            data
        );


        setAnalysisLoading(false);


        scrollToResults();

    }
    catch (error) {

        console.error(
            "Analysis request failed:",
            error
        );


        setAnalysisLoading(false);


        showError(
            error.message ||
            "Unable to complete CV analysis."
        );

    }
}


/* =========================================================
   RESPONSE PARSER
========================================================= */

async function parseResponse(response) {

    const contentType =
        response.headers.get(
            "content-type"
        ) || "";


    if (
        contentType.includes(
            "application/json"
        )
    ) {

        return await response.json();

    }


    const text =
        await response.text();


    return {
        detail:
            text ||
            "Unexpected server response.",
    };
}


/* =========================================================
   LOADING
========================================================= */

function setAnalysisLoading(
    isLoading
) {

    if (elements.analyzeButton) {

        elements.analyzeButton.disabled =
            isLoading;


        if (isLoading) {

            elements.analyzeButton.dataset
                .originalText =
                elements.analyzeButton.textContent
                    .trim();


            elements.analyzeButton.textContent =
                "Analyzing...";

        }
        else {

            elements.analyzeButton.textContent =
                elements.analyzeButton.dataset
                    .originalText ||
                "Analyze CV";

        }

    }


    if (elements.loadingState) {

        elements.loadingState.classList.toggle(
            "hidden",
            !isLoading
        );

    }
}


/* =========================================================
   ERROR HANDLING
========================================================= */

function showError(message) {

    console.error(
        "Frontend error:",
        message
    );


    if (!elements.errorMessage) {

        alert(message);

        return;
    }


    if (elements.errorText) {

        elements.errorText.textContent =
            message;

    }


    elements.errorMessage.classList.remove(
        "hidden"
    );
}


function hideError() {

    if (elements.errorMessage) {

        elements.errorMessage.classList.add(
            "hidden"
        );

    }
}


/* =========================================================
   RENDER COMPLETE RESULT
========================================================= */

function renderAnalysisResult(result) {

    if (!result) {
        return;
    }


    console.log(
        "Rendering analysis result..."
    );


    renderCandidate(
        result.candidate
    );


    renderJob(
        result.job
    );


    renderMatch(
        result.match
    );


    renderTailoredCV(
        result.tailored_cv
    );


    renderInterviewPreparation(
        result.interview_preparation
    );


    /*
     * Show sections
     */

    showSection(
        elements.resultsSection
    );


    showSection(
        elements.tailoredCVSection
    );


    showSection(
        elements.interviewSection
    );


    showSection(
        elements.newAnalysisSection
    );
}


/* =========================================================
   CANDIDATE
========================================================= */

function renderCandidate(
    candidate
) {

    setText(
        "candidate-name",
        candidate?.name ||
        "Unknown Candidate"
    );


    setText(
        "candidate-email",
        candidate?.email ||
        "No email available"
    );


    setText(
        "candidate-location",
        candidate?.location ||
        "Location not available"
    );


    const skillsContainer =
        document.getElementById(
            "skills-list"
        );


    if (!skillsContainer) {
        return;
    }


    skillsContainer.innerHTML = "";


    const skills =
        candidate?.skills || [];


    skills.forEach(
        skill => {

            const tag =
                document.createElement(
                    "span"
                );


            tag.className =
                "skill-tag";


            tag.textContent =
                typeof skill === "string"
                    ? skill
                    : skill?.name || "";


            if (tag.textContent) {

                skillsContainer.appendChild(
                    tag
                );

            }

        }
    );
}


/* =========================================================
   JOB
========================================================= */

function renderJob(job) {

    setText(
        "job-title",
        job?.title ||
        "Job Position"
    );


    setText(
        "job-company",
        job?.company ||
        "Company not specified"
    );


    setText(
        "job-location",
        job?.location ||
        "Location not specified"
    );
}


/* =========================================================
   MATCHING
========================================================= */

function renderMatch(match) {

    if (!match) {
        return;
    }


    const summary =
        match.summary || {};


    /*
     * Score
     */

    const score =
        Number(
            summary.score ?? 0
        );


    setText(
        "match-score",
        score
    );


    setText(
        "strong-matches",
        summary.strong_matches ?? 0
    );


    setText(
        "partial-matches",
        summary.partial_matches ?? 0
    );


    setText(
        "no-evidence",
        summary.no_evidence ?? 0
    );


    /*
     * Requirements
     */

    const container =
        document.getElementById(
            "matching-results"
        );


    if (!container) {
        return;
    }


    container.innerHTML = "";


    const results =
        match.results || [];


    if (results.length === 0) {

        container.innerHTML =
            "<p>No requirement matching data available.</p>";

        return;
    }


    results.forEach(
        item => {

            const wrapper =
                document.createElement(
                    "div"
                );


            wrapper.className =
                "match-item";


            const header =
                document.createElement(
                    "div"
                );


            header.className =
                "match-item-header";


            const requirement =
                document.createElement(
                    "span"
                );


            requirement.className =
                "match-requirement";


            requirement.textContent =
                getRequirementName(
                    item
                );


            const status =
                document.createElement(
                    "span"
                );


            status.className =
                `match-status ${
                    item.status || ""
                }`;


            status.textContent =
                formatStatus(
                    item.status
                );


            header.appendChild(
                requirement
            );


            header.appendChild(
                status
            );


            const reason =
                document.createElement(
                    "p"
                );


            reason.className =
                "match-reason";


            reason.textContent =
                item.reason ||
                "No additional information available.";


            wrapper.appendChild(
                header
            );


            wrapper.appendChild(
                reason
            );


            container.appendChild(
                wrapper
            );

        }
    );
}


function getRequirementName(item) {

    if (item?.requirement_id) {
        return item.requirement_id;
    }


    if (item?.name) {
        return item.name;
    }


    return "Requirement";
}


function formatStatus(status) {

    if (!status) {
        return "Unknown";
    }


    return status
        .replaceAll(
            "_",
            " "
        )
        .replace(
            /\b\w/g,
            letter =>
                letter.toUpperCase()
        );
}


/* =========================================================
   TAILORED CV
========================================================= */

function renderTailoredCV(
    tailoredCV
) {

    if (!tailoredCV) {
        return;
    }


    if (!elements.tailoredCVContent) {
        return;
    }


    const markdown =
        tailoredCV.markdown ||
        buildCVMarkdown(
            tailoredCV
        );


    elements.tailoredCVContent.textContent =
        markdown;
}


function buildCVMarkdown(cv) {

    const lines = [];


    if (cv?.candidate_name) {

        lines.push(
            `# ${cv.candidate_name}`
        );

        lines.push("");

    }


    const sections =
        cv?.sections || [];


    sections.forEach(
        section => {

            lines.push(
                `## ${section.title}`
            );


            lines.push("");


            lines.push(
                section.content || ""
            );


            lines.push("");

        }
    );


    return lines.join(
        "\n"
    );
}


/* =========================================================
   INTERVIEW PREPARATION
========================================================= */

function renderInterviewPreparation(
    interviewPreparation
) {

    const container =
        document.getElementById(
            "interview-questions"
        );


    if (!container) {
        return;
    }


    container.innerHTML = "";


    if (!interviewPreparation) {

        container.innerHTML =
            "<p>No interview preparation available.</p>";

        return;
    }


    const questions =
        interviewPreparation.questions ||
        [];


    const answers =
        interviewPreparation.answers ||
        [];


    if (questions.length === 0) {

        container.innerHTML =
            "<p>No interview questions available.</p>";

        return;
    }


    questions.forEach(
        question => {

            const answer =
                answers.find(
                    item =>
                        item.question_id ===
                        question.question_id
                );


            const card =
                document.createElement(
                    "article"
                );


            card.className =
                "interview-card";


            /*
             * Question
             */

            const questionSection =
                document.createElement(
                    "div"
                );


            questionSection.className =
                "interview-question";


            const meta =
                document.createElement(
                    "div"
                );


            meta.className =
                "question-meta";


            const category =
                document.createElement(
                    "span"
                );


            category.className =
                "question-category";


            category.textContent =
                question.category ||
                "General";


            const difficulty =
                document.createElement(
                    "span"
                );


            difficulty.className =
                "question-difficulty";


            difficulty.textContent =
                question.difficulty ||
                "Unknown";


            meta.appendChild(
                category
            );


            meta.appendChild(
                difficulty
            );


            const questionTitle =
                document.createElement(
                    "h3"
                );


            questionTitle.textContent =
                question.question ||
                "Interview Question";


            questionSection.appendChild(
                meta
            );


            questionSection.appendChild(
                questionTitle
            );


            /*
             * Answer
             */

            const answerSection =
                document.createElement(
                    "div"
                );


            answerSection.className =
                "interview-answer";


            const answerLabel =
                document.createElement(
                    "span"
                );


            answerLabel.className =
                "answer-label";


            answerLabel.textContent =
                "Suggested Answer";


            const answerText =
                document.createElement(
                    "p"
                );


            answerText.textContent =
                answer?.suggested_answer ||
                "No suggested answer available.";


            answerSection.appendChild(
                answerLabel
            );


            answerSection.appendChild(
                answerText
            );


            /*
             * Warnings
             */

            if (
                Array.isArray(
                    answer?.warnings
                )
            ) {

                answer.warnings.forEach(
                    warningText => {

                        const warning =
                            document.createElement(
                                "div"
                            );


                        warning.className =
                            "interview-warning";


                        warning.textContent =
                            warningText;


                        answerSection.appendChild(
                            warning
                        );

                    }
                );

            }


            card.appendChild(
                questionSection
            );


            card.appendChild(
                answerSection
            );


            container.appendChild(
                card
            );

        }
    );
}


/* =========================================================
   COPY TAILORED CV
========================================================= */

async function copyTailoredCV() {

    if (
        !elements.tailoredCVContent
    ) {
        return;
    }


    const content =
        elements.tailoredCVContent
            .textContent;


    if (!content) {

        showError(
            "There is no tailored CV to copy."
        );

        return;
    }


    try {

        await navigator.clipboard.writeText(
            content
        );


        const originalText =
            elements.copyCVButton
                .textContent;


        elements.copyCVButton.textContent =
            "Copied!";


        setTimeout(
            () => {

                elements.copyCVButton.textContent =
                    originalText;

            },
            1500
        );

    }
    catch (error) {

        console.error(
            "Copy failed:",
            error
        );


        showError(
            "Unable to copy the tailored CV."
        );

    }
}


/* =========================================================
   DOWNLOAD TAILORED CV
========================================================= */

function downloadTailoredCV() {

    if (
        !elements.tailoredCVContent
    ) {
        return;
    }


    const content =
        elements.tailoredCVContent
            .textContent;


    if (!content) {

        showError(
            "There is no tailored CV to download."
        );

        return;
    }


    const blob =
        new Blob(
            [content],
            {
                type: "text/markdown;charset=utf-8",
            }
        );


    const url =
        URL.createObjectURL(
            blob
        );


    const link =
        document.createElement(
            "a"
        );


    link.href =
        url;


    link.download =
        "tailored-cv.md";


    document.body.appendChild(
        link
    );


    link.click();


    link.remove();


    URL.revokeObjectURL(
        url
    );
}


/* =========================================================
   UTILITY
========================================================= */

function setText(
    id,
    value
) {

    const element =
        document.getElementById(
            id
        );


    if (element) {

        element.textContent =
            String(value);

    }
}


function showSection(
    element
) {

    if (element) {

        element.classList.remove(
            "hidden"
        );

    }
}


function hideSection(
    element
) {

    if (element) {

        element.classList.add(
            "hidden"
        );

    }
}


/* =========================================================
   SCROLL
========================================================= */

function scrollToResults() {

    if (!elements.resultsSection) {
        return;
    }


    elements.resultsSection.scrollIntoView(
        {
            behavior: "smooth",
            block: "start",
        }
    );
}


/* =========================================================
   RESET APPLICATION
========================================================= */

function resetApplication() {

    state.selectedFile = null;

    state.analysisResult = null;

    state.requestId = null;


    /*
     * Reset form
     */

    if (elements.form) {
        elements.form.reset();
    }


    /*
     * Reset file UI
     */

    if (elements.selectedFile) {

        elements.selectedFile.classList.add(
            "hidden"
        );

    }


    /*
     * Reset character counter
     */

    updateCharacterCount();


    /*
     * Hide result sections
     */

    hideSection(
        elements.resultsSection
    );


    hideSection(
        elements.tailoredCVSection
    );


    hideSection(
        elements.interviewSection
    );


    hideSection(
        elements.newAnalysisSection
    );


    /*
     * Clear result containers
     */

    const matchingResults =
        document.getElementById(
            "matching-results"
        );


    if (matchingResults) {
        matchingResults.innerHTML = "";
    }


    const skillsList =
        document.getElementById(
            "skills-list"
        );


    if (skillsList) {
        skillsList.innerHTML = "";
    }


    const interviewQuestions =
        document.getElementById(
            "interview-questions"
        );


    if (interviewQuestions) {
        interviewQuestions.innerHTML = "";
    }


    if (elements.tailoredCVContent) {

        elements.tailoredCVContent.textContent =
            "";

    }


    hideError();


    /*
     * Return to analysis section
     */

    const analysisSection =
        document.getElementById(
            "analyze"
        );


    if (analysisSection) {

        analysisSection.scrollIntoView(
            {
                behavior: "smooth",
                block: "start",
            }
        );

    }
}
