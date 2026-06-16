from pathlib import Path

import fitz


class PdfTextExtractor:
    def extract_text(self, file_path: str, max_chars: int = 8000) -> str:
        path = Path(file_path)

        if not path.exists() or not path.is_file():
            raise FileNotFoundError("Document file was not found.")

        if path.suffix.lower() != ".pdf":
            raise ValueError("Only PDF files are supported.")

        text_parts = []
        total_chars = 0

        with fitz.open(path) as document:
            for page in document:
                page_text = page.get_text("text").strip()

                if not page_text:
                    continue

                text_parts.append(page_text)
                total_chars += len(page_text)

                if total_chars >= max_chars:
                    break

        extracted_text = "\n\n".join(text_parts).strip()

        if len(extracted_text) > max_chars:
            extracted_text = extracted_text[:max_chars]

        return extracted_text