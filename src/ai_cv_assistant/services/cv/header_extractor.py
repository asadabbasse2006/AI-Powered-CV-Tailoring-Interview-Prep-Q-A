import re
from urllib.parse import urlparse

from pydantic import HttpUrl

from src.ai_cv_assistant.schemas.cv_sections import DetectedCV


class CVHeader:
    """Structured information extracted from a CV header."""

    def __init__(
        self,
        name: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        location: str | None = None,
        linkedin_url: str | None = None,
        github_url: str | None = None,
        portfolio_url: str | None = None,
    ):
        self.name = name
        self.email = email
        self.phone = phone
        self.location = location
        self.linkedin_url = linkedin_url
        self.github_url = github_url
        self.portfolio_url = portfolio_url


class HeaderExtractor:
    """Extract contact information from the beginning of a CV."""

    EMAIL_PATTERN = re.compile(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    )

    PHONE_PATTERN = re.compile(
        r"""
        (?<!\d)
        (?:\+?\d{1,3}[\s.-]?)?
        (?:\(?\d{2,4}\)?[\s.-]?)?
        \d{3,4}[\s.-]?\d{3,4}
        (?!\d)
        """,
        re.VERBOSE,
    )

    URL_PATTERN = re.compile(
        r"(?:https?://|www\.)[^\s<>()]+",
        re.IGNORECASE,
    )

    LINKEDIN_PATTERN = re.compile(
        r"(?:https?://)?(?:www\.)?linkedin\.com/[^\s<>()]+",
        re.IGNORECASE,
    )

    GITHUB_PATTERN = re.compile(
        r"(?:https?://)?(?:www\.)?github\.com/[^\s<>()]+",
        re.IGNORECASE,
    )

    def extract(self, text: str) -> CVHeader:
        if not isinstance(text, str):
            raise TypeError("CV text must be a string.")

        if not text.strip():
            raise ValueError("CV text cannot be empty.")

        header_text = self._get_header_text(text)

        email = self._extract_email(header_text)
        phone = self._extract_phone(header_text)
        linkedin_url = self._extract_linkedin(header_text)
        github_url = self._extract_github(header_text)

        urls = self._extract_urls(header_text)

        portfolio_url = self._extract_portfolio(
            urls=urls,
            linkedin_url=linkedin_url,
            github_url=github_url,
        )

        name = self._extract_name(
            header_text=header_text,
            email=email,
            phone=phone,
            linkedin_url=linkedin_url,
            github_url=github_url,
            urls=urls,
        )

        location = self._extract_location(
            header_text=header_text,
            name=name,
            email=email,
            phone=phone,
            linkedin_url=linkedin_url,
            github_url=github_url,
            portfolio_url=portfolio_url,
        )

        return CVHeader(
            name=name,
            email=email,
            phone=phone,
            location=location,
            linkedin_url=linkedin_url,
            github_url=github_url,
            portfolio_url=portfolio_url,
        )

    @staticmethod
    def _get_header_text(text: str) -> str:
        """
        Use the content before the first recognized CV section.

        If no section exists, use the first 15 non-empty lines.
        """
        lines = text.splitlines()

        header_lines: list[str] = []

        for line in lines:
            stripped = line.strip()

            if not stripped:
                if header_lines:
                    header_lines.append("")
                continue

            header_lines.append(stripped)

            if len(header_lines) >= 15:
                break

        return "\n".join(header_lines)

    @classmethod
    def _extract_email(cls, text: str) -> str | None:
        match = cls.EMAIL_PATTERN.search(text)

        if not match:
            return None

        return match.group(0)

    @classmethod
    def _extract_phone(cls, text: str) -> str | None:
        for match in cls.PHONE_PATTERN.finditer(text):
            value = match.group(0).strip()

            digits = re.sub(r"\D", "", value)

            # Avoid treating years or tiny numeric values as phone numbers.
            if len(digits) >= 7:
                return value

        return None

    @classmethod
    def _extract_linkedin(cls, text: str) -> str | None:
        match = cls.LINKEDIN_PATTERN.search(text)

        if not match:
            return None

        return cls._normalize_url(match.group(0))

    @classmethod
    def _extract_github(cls, text: str) -> str | None:
        match = cls.GITHUB_PATTERN.search(text)

        if not match:
            return None

        return cls._normalize_url(match.group(0))

    @classmethod
    def _extract_urls(cls, text: str) -> list[str]:
        urls = []

        for match in cls.URL_PATTERN.findall(text):
            normalized = cls._normalize_url(match)

            if normalized not in urls:
                urls.append(normalized)

        return urls

    @staticmethod
    def _normalize_url(url: str) -> str:
        url = url.strip().rstrip(".,;")

        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"

        return url

    @staticmethod
    def _extract_portfolio(
        urls: list[str],
        linkedin_url: str | None,
        github_url: str | None,
    ) -> str | None:
        excluded_domains = {
            "linkedin.com",
            "www.linkedin.com",
            "github.com",
            "www.github.com",
        }

        for url in urls:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()

            if domain in excluded_domains:
                continue

            return url

        return None

    @staticmethod
    def _extract_name(
        header_text: str,
        email: str | None,
        phone: str | None,
        linkedin_url: str | None,
        github_url: str | None,
        urls: list[str],
    ) -> str | None:
        lines = [
            line.strip()
            for line in header_text.splitlines()
            if line.strip()
        ]

        if not lines:
            return None

        excluded_patterns = [
            r"email",
            r"phone",
            r"mobile",
            r"contact",
            r"linkedin",
            r"github",
            r"portfolio",
            r"website",
            r"www\.",
            r"https?://",
            r"@",
        ]

        for line in lines:
            if email and email in line:
                continue

            if phone and phone in line:
                continue

            if any(
                re.search(pattern, line, re.IGNORECASE)
                for pattern in excluded_patterns
            ):
                continue

            words = line.split()

            # A reasonable name candidate usually has 2–5 words.
            if 2 <= len(words) <= 5:
                if all(
                    re.fullmatch(r"[A-Za-zÀ-ÖØ-öø-ÿ'.-]+", word)
                    for word in words
                ):
                    return line

        return None

    @staticmethod
    def _extract_location(
        header_text: str,
        name: str | None,
        email: str | None,
        phone: str | None,
        linkedin_url: str | None,
        github_url: str | None,
        portfolio_url: str | None,
    ) -> str | None:
        """
        Conservative location extraction.

        We only use lines explicitly containing common location
        separators/labels. We do not guess a person's location.
        """

        for line in header_text.splitlines():
            stripped = line.strip()

            if not stripped:
                continue

            if re.match(
                r"^(location|address|based in)\s*[:\-]",
                stripped,
                re.IGNORECASE,
            ):
                value = re.sub(
                    r"^(location|address|based in)\s*[:\-]\s*",
                    "",
                    stripped,
                    flags=re.IGNORECASE,
                ).strip()

                if value:
                    return value

        return None