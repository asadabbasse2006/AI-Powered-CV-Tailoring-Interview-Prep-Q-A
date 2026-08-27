"use strict";


/* =========================================================
   CONFIGURATION
========================================================= */

const API_BASE_URL = "http://127.0.0.1:8000/api/v1";


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

document.addEventListener("DOMContentLoaded", () => {

    initializeElements();

    attachEventListeners();

    updateCharacterCount();

});


/* =========================================================
   INITIALIZE DOM
========================================================= */

function initializeElements() {

    elements.cvInput =
        document.getElementById("cv-file");

    elements.fileUploadArea =
        document.getElementById("file-upload-area");

    elements.selectedFile =
        document.getElementById("selected-file");

    elements.selectedFileName =
        document.getElementById("selected-file-name");

    elements.removeFileButton =
        document.getElementById("remove-file");

    elements.jobDescription =
        document.getElementById("job-description");

    elements.charCount =
        document.getElementById("character-count");

    elements.analyzeButton =
        document.getElementById("analyze-button");

    elements.loadingState =
        document.getElementById("loading-state");

    elements.errorMessage =
        document.getElementById("error-message");

    elements.errorText =
        document.getElementById("error-text");

    elements.resultsSection =
        document.getElementById("results");

    elements.tailoredCVSection =
        document.getElementById("tailored-cv");

    elements.interviewSection =
        document.getElementById("interview");

    elements.newAnalysisSection =
        document.getElementById("new-analysis");

    elements.newAnalysisButton =
        document.getElementById("new-analysis-button");

    elements.copyCVButton =
        document.getElementById("copy-cv");

    elements.downloadCVButton =
        document.getElementById("download-cv");

    elements.tailoredCVContent =
        document.getElementById("tailored-cv-content");

    console.log("DOM initialized:", elements);
}


/* =========================================================
   EVENT LISTENERS
========================================================= */

function attachEventListeners() {

    /* CV selection */

    if (elements.cvInput) {

        elements.cvInput.addEventListener(
            "change",
            handleFileSelection
        );
    }


    /* Remove CV */

    if (elements.removeFileButton) {

        elements.removeFileButton.addEventListener(
            "click",
            removeSelectedFile
        );
    }


    /* Character counter */

    if (elements.jobDescription) {

        elements.jobDescription.addEventListener(
            "input",
            updateCharacterCount
        );
    }


    /*
     * IMPORTANT:
     *
     * There is NO form in your HTML.
     *
     * Therefore we listen directly to
     * the Analyze button.
     */

    if (elements.analyzeButton) {

        elements.analyzeButton.addEventListener(
            "click",
            handleAnalysisSubmit
        );
    }


    /* New analysis */

    if (elements.newAnalysisButton) {

        elements.newAnalysisButton.addEventListener(
            "click",
            resetApplication
        );
    }


    /* Copy CV */

    if (elements.copyCVButton) {

        elements.copyCVButton.addEventListener(
            "click",
            copyTailoredCV
        );
    }


    /* Download CV */

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

    const file = event.target.files[0];

    if (!file) {
        return;
    }


    /* Validate PDF */

    if (
        file.type !== "application/pdf" &&
        !file.name.toLowerCase().endsWith(".pdf")
    ) {

        showError(
            "Please upload a PDF CV."
        );

        elements.cvInput.value = "";

        state.selectedFile = null;

        return;
    }


    /* Validate size */

    const maxSize =
        10 * 1024 * 1024;

    if (file.size > maxSize) {

        showError(
            "CV file is too large. Maximum allowed size is 10 MB."
        );

        elements.cvInput.value = "";

        state.selectedFile = null;

        return;
    }


    /* Save file */

    state.selectedFile = file;

    hideError();

    displaySelectedFile(file);
}


function displaySelectedFile(file) {

    if (
        !elements.selectedFile ||
        !elements.selectedFileName
    ) {
        return;
    }

    elements.selectedFileName.textContent =
        `${file.name} (${formatFileSize(file.size)})`;

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

    hideError();
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
   CHARACTER COUNTER
========================================================= */

function updateCharacterCount() {

    if (
        !elements.jobDescription ||
        !elements.charCount
    ) {
        return;
    }

    const count =
        elements.jobDescription.value.length;

    elements.charCount.textContent =
        `${count.toLocaleString()} characters`;
}


/* =========================================================
   ANALYSIS
========================================================= */

async function handleAnalysisSubmit() {

    console.log("Analyze button clicked.");

    hideError();


    /* -------------------------------------------------------
       Validate CV
    ------------------------------------------------------- */

    if (!state.selectedFile) {

        showError(
            "Please upload your CV before starting the analysis."
        );

        return;
    }


    /* -------------------------------------------------------
       Validate job description
    ------------------------------------------------------- */

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


    /* -------------------------------------------------------
       Start loading
    ------------------------------------------------------- */

    setAnalysisLoading(true);


    try {

        /* ---------------------------------------------------
           Create multipart form data
        --------------------------------------------------- */

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


        /* ---------------------------------------------------
           Send request
        --------------------------------------------------- */

        const response =
            await fetch(
                `${API_BASE_URL}/analyze`,
                {
                    method: "POST",
                    body: formData,
                }
            );


        console.log(
            "API response:",
            response.status
        );


        /* ---------------------------------------------------
           Parse response
        --------------------------------------------------- */

        const data =
            await parseResponse(response);


        console.log(
            "API data:",
            data
        );


        /* ---------------------------------------------------
           Handle API error
        --------------------------------------------------- */

        if (!response.ok) {

            throw new Error(
                data?.detail ||
                `Analysis failed with status ${response.status}.`
            );
        }


        /* ---------------------------------------------------
           Save result
        --------------------------------------------------- */

        state.analysisResult =
            data;


        state.requestId =
            data?.metadata?.request_id ||
            null;


        console.log(
            "Analysis completed:",
            state.requestId
        );


        /* ---------------------------------------------------
           Render results
        --------------------------------------------------- */

        renderAnalysisResult(data);


        /* ---------------------------------------------------
           Stop loading
        --------------------------------------------------- */

        setAnalysisLoading(false);


        /* ---------------------------------------------------
           Scroll
        --------------------------------------------------- */

        scrollToResults();

    } catch (error) {

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

function setAnalysisLoading(isLoading) {

    if (elements.analyzeButton) {

        elements.analyzeButton.disabled =
            isLoading;


        if (isLoading) {

            elements.analyzeButton.dataset
                .originalText =
                elements.analyzeButton.textContent;


            elements.analyzeButton.textContent =
                "Analyzing...";

        } else {

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
   COMPLETE RESULT
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


    /* Show result sections */

    if (elements.resultsSection) {

        elements.resultsSection.classList.remove(
            "hidden"
        );
    }


    if (elements.tailoredCVSection) {

        elements.tailoredCVSection.classList.remove(
            "hidden"
        );
    }


    if (elements.interviewSection) {

        elements.interviewSection.classList.remove(
            "hidden"
        );
    }


    if (elements.newAnalysisSection) {

        elements.newAnalysisSection.classList.remove(
            "hidden"
        );
    }
}


/* =========================================================
   CANDIDATE
========================================================= */

function renderCandidate(candidate) {

    const name =
        document.getElementById(
            "candidate-name"
        );

    const email =
        document.getElementById(
            "candidate-email"
        );

    const location =
        document.getElementById(
            "candidate-location"
        );


    if (name) {

        name.textContent =
            candidate?.name ||
            "Unknown Candidate";
    }


    if (email) {

        email.textContent =
            candidate?.email ||
            "No email available";
    }


    if (location) {

        location.textContent =
            candidate?.location ||
            "Location not available";
    }


    /* Skills */

    const skillsContainer =
        document.getElementById(
            "skills-list"
        );


    if (!skillsContainer) {
        return;
    }


    skillsContainer.innerHTML = "";


    const skills =
        candidate?.skills ||
        [];


    skills.forEach(skill => {

        const tag =
            document.createElement(
                "span"
            );


        tag.className =
            "skill-tag";


        tag.textContent =
            typeof skill === "string"
                ? skill
                : skill.name;


        skillsContainer.appendChild(
            tag
        );
    });
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
        match.summary ||
        {};


    /* Score */

    const score =
        document.getElementById(
            "match-score"
        );


    if (score) {

        const numericScore =
            Number(
                summary.score ?? 0
            );


        score.textContent =
            numericScore;
    }


    /* Statistics */

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


    /* Requirements */

    const container =
        document.getElementById(
            "matching-results"
        );


    if (!container) {
        return;
    }


    container.innerHTML = "";


    const results =
        match.results ||
        [];


    results.forEach(item => {

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
            getRequirementName(item);


        const status =
            document.createElement(
                "span"
            );


        status.className =
            `match-status ${item.status || ""}`;


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
    });
}


function getRequirementName(item) {

    return (
        item.requirement ||
        item.requirement_id ||
        item.name ||
        "Requirement"
    );
}


function formatStatus(status) {

    if (!status) {
        return "Unknown";
    }


    return status
        .replaceAll("_", " ")
        .replace(
            /\b\w/g,
            letter =>
                letter.toUpperCase()
        );
}


/* =========================================================
   TAILORED CV
========================================================= */

function renderTailoredCV(tailoredCV) {

    if (!tailoredCV) {
        return;
    }


    if (!elements.tailoredCVContent) {
        return;
    }


    let content = "";


    if (
        typeof tailoredCV === "string"
    ) {

        content =
            tailoredCV;

    } else if (
        tailoredCV.markdown
    ) {

        content =
            tailoredCV.markdown;

    } else {

        content =
            buildCVMarkdown(
                tailoredCV
            );
    }


    elements.tailoredCVContent.textContent =
        content;
}


function buildCVMarkdown(cv) {

    const lines = [];


    if (cv.candidate_name) {

        lines.push(
            `# ${cv.candidate_name}`
        );

        lines.push("");
    }


    const sections =
        cv.sections ||
        [];


    sections.forEach(section => {

        lines.push(
            `## ${section.title}`
        );


        lines.push("");


        lines.push(
            section.content || ""
        );


        lines.push("");
    });


    return lines.join("\n");
}


/* =========================================================
   INTERVIEW PREPARATION
========================================================= */

function renderInterviewPreparation(
    interviewPreparation
) {

    if (!interviewPreparation) {
        return;
    }


    const container =
        document.getElementById(
            "interview-questions"
        );


    if (!container) {
        return;
    }


    container.innerHTML = "";


    const questions =
        interviewPreparation.questions ||
        [];


    const answers =
        interviewPreparation.answers ||
        [];


    questions.forEach(question => {

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


        /* Question */

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
            "Question unavailable";


        questionSection.appendChild(
            meta
        );


        questionSection.appendChild(
            questionTitle
        );


        /* Answer */

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


        /* Warnings */

        if (
            answer?.warnings &&
            answer.warnings.length
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
    });
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


    const text =
        elements.tailoredCVContent
            .textContent;


    if (!text.trim()) {

        showError(
            "There is no tailored CV to copy."
        );

        return;
    }


    try {

        await navigator.clipboard.writeText(
            text
        );


        elements.copyCVButton.textContent =
            "Copied!";


        setTimeout(() => {

            elements.copyCVButton.textContent =
                "Copy CV";

        }, 2000);

    } catch (error) {

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
   DOWNLOAD MARKDOWN
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


    if (!content.trim()) {

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
        "tailored_cv.md";


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


/* =========================================================
   SCROLL TO RESULTS
========================================================= */

function scrollToResults() {

    if (
        !elements.resultsSection
    ) {
        return;
    }


    elements.resultsSection.scrollIntoView({
        behavior: "smooth",
        block: "start",
    });
}


/* =========================================================
   RESET
========================================================= */

function resetApplication() {

    state.selectedFile = null;

    state.analysisResult = null;

    state.requestId = null;


    /* Reset CV */

    if (elements.cvInput) {

        elements.cvInput.value =
            "";
    }


    if (elements.selectedFile) {

        elements.selectedFile.classList.add(
            "hidden"
        );
    }


    /* Reset job description */

    if (elements.jobDescription) {

        elements.jobDescription.value =
            "";
    }


    updateCharacterCount();


    /* Hide results */

    if (elements.resultsSection) {

        elements.resultsSection.classList.add(
            "hidden"
        );
    }


    if (elements.tailoredCVSection) {

        elements.tailoredCVSection.classList.add(
            "hidden"
        );
    }


    if (elements.interviewSection) {

        elements.interviewSection.classList.add(
            "hidden"
        );
    }


    if (elements.newAnalysisSection) {

        elements.newAnalysisSection.classList.add(
            "hidden"
        );
    }


    hideError();


    /* Scroll to analysis */

    const analysisSection =
        document.getElementById(
            "analyze"
        );


    if (analysisSection) {

        analysisSection.scrollIntoView({
            behavior: "smooth",
            block: "start",
        });
    }
}