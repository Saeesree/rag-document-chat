from sentence_transformers import SentenceTransformer

# Load model once at startup (not per request)
model = SentenceTransformer("all-MiniLM-L6-v2")


def get_embeddings(texts: list[str]) -> list[list[float]]:
    """Convert a list of text strings into embedding vectors."""
    embeddings = model.encode(texts, show_progress_bar=True)
    return embeddings.tolist()