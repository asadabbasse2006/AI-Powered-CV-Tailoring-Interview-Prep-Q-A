import re

class TextCleaner:

    def clean(self,text: str):
        if not isinstance(text, str):
            raise TypeError("Text must be of type str.")

        if not text.strip():
            raise ValueError("Text cannot be empty.")

        text = self._normalize_line_endings(text)
        text = self._normalize_whitespace(text)
        text = self._normalize_bullets(text)
        text = self._remove_excessive_blank_lines(text)

        return text.strip()

    @staticmethod
    def _normalize_line_endings(text):
        return text.replace("\r\n", "\n").replace("\r", "\n")

    @staticmethod
    def _normalize_whitespace(text):
        lines = text.split("\n")

        cleaned_lines = []

        for line in lines:
            line = line.replace("\t"," ")

            line = re.sub(r"[ ]{2,}", " ", line)
            line = line.strip()

            cleaned_lines.append(line)

        return "\n".join(cleaned_lines)

    @staticmethod
    def _normalize_bullets(text):

        bullet_pattern = r"^[\s]*[•●▪◦‣⁃∙]\s*"
        lines = text.split("\n")

        normalized_lines = []

        for line in lines:
            line = re.sub(bullet_pattern, "- ", line)
            normalized_lines.append(line)

        return "\n".join(normalized_lines)

    @staticmethod
    def _remove_excessive_blank_lines(text):
        lines = text.split("\n")

        return re.sub(r"\n{3,}", "\n\n", text)