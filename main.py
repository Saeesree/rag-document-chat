"""
FastAPI backend for rag-document-chat
"""
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import shutil
import os

from utils.database_manager import DatabaseManager
from utils.document_processor import DocumentProcessor
from utils.vector_store_manager import VectorStoreManager
from utils.conversation_manager import ConversationManager
from utils.paths import Paths

app = FastAPI(title="rag-document-chat API")
DatabaseManager.initialize_database()
Paths.ensure_directories_exist()

# Allow Next.js frontend to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Request Models ────────────────────────────────────────────────────────────

class CreateNotebookRequest(BaseModel):
    name: str

class ChatRequest(BaseModel):
    notebook_name: str
    query: str
    provider: Optional[str] = None
    model_name: Optional[str] = None

# ─── Notebooks ─────────────────────────────────────────────────────────────────

@app.get("/api/notebooks")
def list_notebooks():
    """Get all notebooks."""
    notebooks = DatabaseManager.list_notebooks()
    return {"notebooks": notebooks}


@app.post("/api/notebooks")
def create_notebook(request: CreateNotebookRequest):
    """Create a new notebook."""
    if len(request.name) < 3:
        raise HTTPException(status_code=400, detail="Notebook name must be at least 3 characters.")
    
    existing = DatabaseManager.list_notebooks()
    if any(n["name"] == request.name for n in existing):
        raise HTTPException(status_code=400, detail="Notebook with this name already exists.")
    
    notebook = DatabaseManager.create_notebook(request.name)
    
    # Create the folder for uploaded files
    notebook_dir = Paths.get_notebook_files_dir(request.name)
    os.makedirs(notebook_dir, exist_ok=True)
    
    return {"message": "Notebook created successfully."}


@app.delete("/api/notebooks/{notebook_name}")
def delete_notebook(notebook_name: str):
    """Delete a notebook and all its files."""
    try:
        VectorStoreManager.delete_notebook(notebook_name)
        DatabaseManager.delete_notebook(notebook_name)
        
        notebook_dir = Paths.get_notebook_files_dir(notebook_name)
        if os.path.exists(notebook_dir):
            shutil.rmtree(notebook_dir)
        
        return {"message": f"Notebook '{notebook_name}' deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ─── Documents ─────────────────────────────────────────────────────────────────

@app.get("/api/notebooks/{notebook_name}/files")
def list_files(notebook_name: str):
    """List all files in a notebook."""
    files = DatabaseManager.get_files_by_notebook(notebook_name)
    return {"files": files}


@app.post("/api/notebooks/{notebook_name}/upload")
def upload_file(notebook_name: str, file: UploadFile = File(...)):
    """Upload a file to a notebook."""
    allowed = [".pdf", ".txt", ".md"]
    ext = os.path.splitext(file.filename)[1].lower()
    
    if ext not in allowed:
        raise HTTPException(status_code=400, detail=f"File type not supported. Allowed: {allowed}")
    
    notebook_dir = Paths.get_notebook_files_dir(notebook_name)
    os.makedirs(notebook_dir, exist_ok=True)
    
    file_path = os.path.join(notebook_dir, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    DatabaseManager.add_file(notebook_name, file.filename, file.filename)
    
    return {"message": f"File '{file.filename}' uploaded successfully."}


@app.post("/api/notebooks/{notebook_name}/process")
def process_files(notebook_name: str):
    """Process and embed all unprocessed files in a notebook."""
    files = DatabaseManager.get_files_by_notebook(notebook_name)
    unprocessed = [f for f in files if not f.get("is_processed")]

    if not unprocessed:
        return {"message": "All files are already processed."}

    # Initialize the vector store collection for this notebook
    collection = VectorStoreManager.initialize_collection(notebook_name)

    results = []
    for file in unprocessed:
        try:
            notebook_dir = Paths.get_notebook_files_dir(notebook_name)
            file_path = os.path.join(notebook_dir, file["stored_filename"])

            # Extract text and chunk it
            chunks = DocumentProcessor.process_document(file_path=file_path)

            # Store chunks in ChromaDB
            metadata = [{"source": file["original_filename"]} for _ in chunks]
            VectorStoreManager.add_documents(collection, chunks, metadata)

            # Mark as processed in database
            DatabaseManager.mark_file_as_processed(file["id"])
            results.append({"file": file["original_filename"], "status": "success"})
        except Exception as e:
            import traceback
            traceback.print_exc()
            results.append({"file": file["original_filename"], "status": "failed", "error": str(e)})

    return {"results": results}

# ─── Chat ──────────────────────────────────────────────────────────────────────

@app.post("/api/chat")
def chat(request: ChatRequest):
    """Chat with documents in a notebook."""
    try:
        response = ConversationManager.respond_to_query(
            notebook_name=request.notebook_name,
            query=request.query,
            provider=request.provider,
            model_name=request.model_name,
      # Adjusted threshold for better relevance filtering
        )
        return {"response": response}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ─── Health Check ──────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {"status": "ok", "app": "rag-document-chat"}
