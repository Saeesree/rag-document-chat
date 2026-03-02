import os
import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv

load_dotenv()

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")

client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)


def get_or_create_collection(name: str):
    """Get existing collection or create a new one."""
    return client.get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"}
    )


def add_documents(collection_name: str, chunks: list[dict], embeddings: list[list[float]]):
    """Store chunks with their embeddings and metadata in ChromaDB."""
    collection = get_or_create_collection(collection_name)

    ids = [f"{collection_name}_chunk_{i}" for i in range(len(chunks))]
    documents = [chunk["text"] for chunk in chunks]
    metadatas = [chunk["metadata"] for chunk in chunks]

    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )

    return len(ids)


def search(collection_name: str, query_embedding: list[float], top_k: int = 5, threshold: float = 0.7):
    """Search for the most relevant chunks. Filter out weak matches."""
    collection = get_or_create_collection(collection_name)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    filtered = []
    for i, distance in enumerate(results["distances"][0]):
        similarity = 1 - distance
        if similarity >= threshold:
            filtered.append({
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "similarity": round(similarity, 4)
            })

    return filtered


def delete_collection(collection_name: str):
    """Delete a document's entire collection."""
    try:
        client.delete_collection(collection_name)
        return True
    except Exception:
        return False


def list_collections() -> list[str]:
    """List all stored document collections."""
    return [col.name for col in client.list_collections()]