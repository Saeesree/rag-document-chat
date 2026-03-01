import os
from pypdf import PdfReader
from docx import Document


def parse_file(file_path: str, filename: str) -> list[dict]:
    """Parse file and return list of {text, metadata} dicts per section."""
    ext = os.path.splitext(filename)[1].lower()

    if ext == ".pdf":
        return _parse_pdf(file_path, filename)
    elif ext == ".docx":
        return _parse_docx(file_path, filename)
    elif ext == ".txt":
        return _parse_txt(file_path, filename)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def _parse_pdf(file_path: str, filename: str) -> list[dict]:
    reader = PdfReader(file_path)
    sections = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text and text.strip():
            sections.append({
                "text": text.strip(),
                "metadata": {"source": filename, "page": i + 1, "type": "pdf"}
            })
    return sections


def _parse_docx(file_path: str, filename: str) -> list[dict]:
    doc = Document(file_path)
    sections = []
    for i, para in enumerate(doc.paragraphs):
        if para.text.strip():
            sections.append({
                "text": para.text.strip(),
                "metadata": {"source": filename, "paragraph_index": i, "type": "docx"}
            })
    return sections


def _parse_txt(file_path: str, filename: str) -> list[dict]:
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    return [
        {"text": p, "metadata": {"source": filename, "paragraph_index": i, "type": "txt"}}
        for i, p in enumerate(paragraphs)
    ]


def chunk_text(sections: list[dict], overlap_percentage: float = 0.15, max_words: int = 1000) -> list[dict]:
    """
    Chunk parsed sections into retrieval-ready pieces with metadata.
    - Merges short sections (headings) into the next one
    - Splits oversized paragraphs at max_words ceiling
    - Applies overlap from previous chunk
    """
    # Flatten: merge short sections, respect page boundaries
    merged = []
    buffer_text = ""
    buffer_meta = None

    for section in sections:
        text = section["text"]
        meta = section["metadata"]

        if len(text.split()) < 15:
            buffer_text += " " + text
            if not buffer_meta:
                buffer_meta = meta
        else:
            if buffer_text:
                merged.append({"text": (buffer_text + " " + text).strip(), "metadata": buffer_meta or meta})
                buffer_text = ""
                buffer_meta = None
            else:
                merged.append({"text": text, "metadata": meta})

    if buffer_text:
        merged.append({"text": buffer_text.strip(), "metadata": buffer_meta or {}})

    # Split oversized chunks
    split_chunks = []
    for item in merged:
        words = item["text"].split()
        if len(words) > max_words:
            for j in range(0, len(words), max_words):
                split_chunks.append({
                    "text": " ".join(words[j:j + max_words]),
                    "metadata": item["metadata"]
                })
        else:
            split_chunks.append(item)

    # Apply overlap
    final_chunks = []
    for i, chunk in enumerate(split_chunks):
        if i == 0:
            final_chunks.append(chunk)
        else:
            prev_words = split_chunks[i - 1]["text"].split()
            overlap_count = max(1, int(len(prev_words) * overlap_percentage))
            overlap_text = " ".join(prev_words[-overlap_count:])
            final_chunks.append({
                "text": overlap_text + " " + chunk["text"],
                "metadata": chunk["metadata"]
            })

    return final_chunks