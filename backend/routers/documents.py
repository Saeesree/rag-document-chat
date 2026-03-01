import os
import shutil
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException
from services.parser import parse_file, chunk_text
from services.embeddings import get_embeddings
from services.vector_store import add_documents, delete_collection, list_collections

router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    # Validate file type
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}. Allowed: {ALLOWED_EXTENSIONS}")

    # Save uploaded file to temp location
    tmp_dir = tempfile.mkdtemp()
    tmp_path = os.path.join(tmp_dir, file.filename)

    try:
        with open(tmp_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # 1. Parse the file into sections with metadata
        sections = parse_file(tmp_path, file.filename)
        if not sections:
            raise HTTPException(status_code=400, detail="No text could be extracted from the file.")

        # 2. Chunk the sections
        chunks = chunk_text(sections)
        if not chunks:
            raise HTTPException(status_code=400, detail="No chunks could be created from the file.")

        # 3. Generate embeddings
        texts = [chunk["text"] for chunk in chunks]
        embeddings = get_embeddings(texts)

        # 4. Store in ChromaDB (use filename as collection name)
        collection_name = file.filename.replace(" ", "_").replace(".", "_")
        num_stored = add_documents(collection_name, chunks, embeddings)

        return {
            "message": f"Successfully processed {file.filename}",
            "collection_name": collection_name,
            "chunks_created": len(chunks),
            "chunks_stored": num_stored
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    finally:
        # Clean up temp file
        shutil.rmtree(tmp_dir, ignore_errors=True)


@router.delete("/{collection_name}")
async def delete_document(collection_name: str):
    success = delete_collection(collection_name)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found.")
    return {"message": f"Deleted {collection_name}"}


@router.get("/")
async def get_documents():
    collections = list_collections()
    return {"documents": collections}