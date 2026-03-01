def search(collection_name: str, query_embedding: list[float], top_k: int = 5, threshold: float = 0.3):
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