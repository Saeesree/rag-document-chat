from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.embeddings import get_embeddings
from services.vector_store import search
from services.gemini import generate_answer

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    question: str
    collection_name: str


@router.post("/")
async def chat(request: ChatRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        # 1. Convert question to embedding
        query_embedding = get_embeddings([request.question])[0]

        # 2. Search ChromaDB for relevant chunks
        relevant_chunks = search(
            collection_name=request.collection_name,
            query_embedding=query_embedding,
            top_k=5,
            threshold=0.3
        )

        # 3. Send question + chunks to Gemini
        result = generate_answer(request.question, relevant_chunks)

        return {
            "answer": result["answer"],
            "sources": result["sources"],
            "chunks_used": len(relevant_chunks)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")