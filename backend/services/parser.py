import os
from pypdf import PdfReader
from docx import Document


def parse_file(file_path: str, filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()

    if ext == ".pdf":
        reader = PdfReader(file_path)
        return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())

    elif ext == ".docx":
        doc = Document(file_path)
        return "\n".join(para.text for para in doc.paragraphs if para.text)

    elif ext == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    else:
        raise ValueError(f"Unsupported file type: {ext}")


def chunk_text(text: str, overlap_percentage: float = 0.15) -> list[str]:
    # Split by paragraph (double newline or single newline)
    raw_paragraphs = [p.strip() for p in text.split("\n") if p.strip()]

    # Merge very short paragraphs (headings, single lines) with the next one
    paragraphs = []
    buffer = ""
    for para in raw_paragraphs:
        if len(para.split()) < 15:  # too short, merge with next
            buffer += " " + para
        else:
            if buffer:
                paragraphs.append((buffer + " " + para).strip())
                buffer = ""
            else:
                paragraphs.append(para)
    if buffer:
        paragraphs.append(buffer.strip())

    if not paragraphs:
        return []

    # Apply overlap: carry last X% words of previous paragraph into next chunk
    chunks = []
    for i, para in enumerate(paragraphs):
        if i == 0:
            chunks.append(para)
        else:
            prev_words = paragraphs[i - 1].split()
            overlap_word_count = max(1, int(len(prev_words) * overlap_percentage))
            overlap_text = " ".join(prev_words[-overlap_word_count:])
            chunks.append(overlap_text + " " + para)

    return chunks