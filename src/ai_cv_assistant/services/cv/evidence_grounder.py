import re


class EvidenceGrounder:
    """
    Finds supporting evidence for extracted CV claims
    directly inside the original CV text.

    This component is deterministic and does not use an LLM.
    """

    def ground(
        self,
        claim: str,
        cv_text: str,
    ) -> str | None:
        if not isinstance(claim, str):
            raise TypeError("Claim must be a string.")

        if not isinstance(cv_text, str):
            raise TypeError("CV text must be a string.")

        claim = claim.strip()
        cv_text = cv_text.strip()

        if not claim:
            raise ValueError("Claim cannot be empty.")

        if not cv_text:
            raise ValueError("CV text cannot be empty.")

        return self._find_sentence(claim, cv_text)

    def _find_sentence(
        self,
        claim: str,
        cv_text: str,
    ) -> str | None:
        """
        Find a sentence containing the claim.

        Matching is case-insensitive.
        """

        sentences = re.split(
            r"(?<=[.!?])\s+|\n+",
            cv_text,
        )

        normalized_claim = claim.casefold()

        for sentence in sentences:
            cleaned_sentence = sentence.strip()

            if not cleaned_sentence:
                continue

            if normalized_claim in cleaned_sentence.casefold():
                return cleaned_sentence

        return None