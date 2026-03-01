import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-flash")


def generate_answer(question: str, chunks: list[dict]) -> dict:
    """Send question + relevant chunks to Gemini and get a grounded answer."""

    if not chunks:
        return {
            "answer": "I don't have enough information in the uploaded documents to answer this question.",
            "sources": []
        }

    # Build context from chunks
    context = ""
    for i, chunk in enumerate(chunks):
        source = chunk["metadata"].get("source", "unknown")
        page = chunk["metadata"].get("page", "")
        page_info = f" (page {page})" if page else ""
        context += f"\n--- Excerpt {i+1} from {source}{page_info} ---\n{chunk['text']}\n"

    prompt = f"""You are a helpful document assistant. Answer the user's question based ONLY on the provided document excerpts below. 

Rules:
- Only use information from the excerpts to answer
- If the excerpts don't contain enough information, say so clearly
- Cite which excerpt(s) you used in your answer
- Be concise and direct

DOCUMENT EXCERPTS:
{context}

USER QUESTION: {question}

ANSWER:"""

    try:
        response = model.generate_content(prompt)
        
        # Extract source references
        sources = []
        seen = set()
        for chunk in chunks:
            source = chunk["metadata"].get("source", "unknown")
            page = chunk["metadata"].get("page", "")
            key = f"{source}_p{page}"
            if key not in seen:
                seen.add(key)
                source_info = {"source": source}
                if page:
                    source_info["page"] = page
                source_info["similarity"] = chunk.get("similarity", 0)
                sources.append(source_info)

        return {
            "answer": response.text,
            "sources": sources
        }

    except Exception as e:
        return {
            "answer": f"Error generating response: {str(e)}",
            "sources": []
        }