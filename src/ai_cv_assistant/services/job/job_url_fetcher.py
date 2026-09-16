from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup


class JobURLFetcher:
    """
    Fetches and extracts readable text from a public job-posting URL.

    The fetcher is intentionally independent of the LLM and job
    extraction logic.

    Flow:

        Job URL
           ↓
        HTTP request
           ↓
        HTML
           ↓
        BeautifulSoup
           ↓
        Job description text
    """

    DEFAULT_TIMEOUT = 20.0

    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    )

    def __init__(
        self,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self.timeout = timeout

    def fetch(self, job_url: str) -> str:
        """
        Fetch a job posting and return cleaned text.

        Args:
            job_url:
                Public URL of the job posting.

        Returns:
            Cleaned text extracted from the webpage.

        Raises:
            TypeError:
                If job_url is not a string.

            ValueError:
                If the URL is invalid or no useful text is found.

            RuntimeError:
                If the webpage cannot be fetched.
        """

        self._validate_url(job_url)

        try:
            response = httpx.get(
                job_url,
                headers={
                    "User-Agent": self.USER_AGENT,
                    "Accept": "text/html,application/xhtml+xml",
                },
                timeout=self.timeout,
                follow_redirects=True,
            )

            response.raise_for_status()

        except httpx.TimeoutException as exc:
            raise RuntimeError(
                "The job posting URL timed out."
            ) from exc

        except httpx.HTTPStatusError as exc:
            raise RuntimeError(
                f"Unable to fetch job posting. "
                f"HTTP status: {exc.response.status_code}."
            ) from exc

        except httpx.RequestError as exc:
            raise RuntimeError(
                "Unable to access the job posting URL."
            ) from exc

        return self._extract_text(response.text)

    @staticmethod
    def _validate_url(job_url: str) -> None:
        if not isinstance(job_url, str):
            raise TypeError(
                "job_url must be a string."
            )

        job_url = job_url.strip()

        if not job_url:
            raise ValueError(
                "job_url cannot be empty."
            )

        parsed = urlparse(job_url)

        if parsed.scheme not in {"http", "https"}:
            raise ValueError(
                "job_url must use http or https."
            )

        if not parsed.netloc:
            raise ValueError(
                "job_url must contain a valid domain."
            )

    @staticmethod
    def _extract_text(html: str) -> str:
        if not isinstance(html, str):
            raise TypeError(
                "HTML content must be a string."
            )

        if not html.strip():
            raise ValueError(
                "The job posting page is empty."
            )

        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        # Remove elements that normally do not contain
        # useful job-description information.
        for element in soup(
            [
                "script",
                "style",
                "noscript",
                "svg",
                "iframe",
                "nav",
                "footer",
                "header",
            ]
        ):
            element.decompose()

        # Prefer the main article/content area when available.
        content = (
            soup.find("main")
            or soup.find("article")
            or soup.body
            or soup
        )

        text = content.get_text(
            separator="\n",
            strip=True,
        )

        lines = []

        for line in text.splitlines():
            cleaned = " ".join(line.split())

            if cleaned:
                lines.append(cleaned)

        result = "\n".join(lines)

        if not result.strip():
            raise ValueError(
                "Could not extract useful text from the job posting."
            )

        return result