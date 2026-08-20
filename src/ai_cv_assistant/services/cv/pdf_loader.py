from pathlib import Path

import fitz

class PDFExtractionError(Exception):
    pass

class PDFLoader:

    @staticmethod
    def extract_text(file_path: str | Path):
        path = Path(file_path)

        if not path.exists():
            raise PDFExtractionError(f'File {file_path} does not exist')

        if not path.is_file():
            raise PDFExtractionError(f'File {file_path} is not a file')

        if path.suffix.lower() != ".pdf":
            raise PDFExtractionError("The file must be in PDF format")


        try:
            document = fitz.open(path)

        except Exception as e:
            raise PDFExtractionError("Unable to open PDF.")

        pages = []

        for page in document:
            text = page.get_text("text")

            if text:
                pages.append(text)

        extracted_text = "\n".join(pages).strip()

        if not extracted_text:
            raise PDFExtractionError("No text could be extracted. The PDF may be scanned or image based")

        return extracted_text
