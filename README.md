# 📄 RAG Document Chat

A full-stack application that lets you upload documents and chat with them using AI. Organize your files into notebooks, process them, and ask natural language questions — powered by OpenAI and ChromaDB.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?style=flat-square&logo=fastapi)
![Next.js](https://img.shields.io/badge/Next.js-16-black?style=flat-square&logo=next.js)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-412991?style=flat-square&logo=openai)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20Store-orange?style=flat-square)

---

## ✨ Features

- 📁 **Multi-Notebook Support** — Organize documents into separate notebooks for different projects
- 📄 **Multiple File Formats** — Upload PDF, TXT, MD, and DOCX files
- 🧠 **RAG Pipeline** — Retrieval-Augmented Generation for accurate, document-grounded answers
- 💬 **Natural Language Chat** — Ask questions and get answers based on your documents
- 💾 **Persistent Storage** — ChromaDB for vector embeddings, SQLite for metadata
- ⚡ **Fast & Efficient** — Skips reprocessing of already embedded documents

---

## 🏗️ Architecture

```
rag-document-chat/
├── main.py                  # FastAPI backend
├── utils/
│   ├── conversation_manager.py   # LLM interaction & RAG chain
│   ├── document_processor.py     # Text extraction & chunking
│   ├── vector_store_manager.py   # ChromaDB management
│   ├── database_manager.py       # SQLite operations
│   ├── prompt_builder.py         # Prompt templates
│   ├── config_manager.py         # YAML config loader
│   └── paths.py                  # Path management
├── config/
│   ├── config.yaml               # App configuration
│   └── prompt_config.yaml        # Prompt templates
├── frontend/                     # Next.js application
│   └── app/
│       └── page.tsx              # Main UI
├── uploaded_files/               # Uploaded documents (per notebook)
├── vector_db/                    # ChromaDB collections (per notebook)
├── notebooks.db                  # SQLite metadata database
└── .env                          # API keys
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- OpenAI API Key

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/Saeesree/rag-document-chat.git
cd rag-document-chat

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
copy .env.template .env      # Windows
cp .env.template .env        # Mac/Linux
```

Add your OpenAI API key to `.env`:
```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx
```

Start the backend:
```bash
uvicorn main:app --reload
```
Backend runs at **http://localhost:8000**

---

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```
Frontend runs at **http://localhost:3000**

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/notebooks` | List all notebooks |
| POST | `/api/notebooks` | Create a notebook |
| DELETE | `/api/notebooks/{name}` | Delete a notebook |
| GET | `/api/notebooks/{name}/files` | List files in notebook |
| POST | `/api/notebooks/{name}/upload` | Upload a file |
| POST | `/api/notebooks/{name}/process` | Embed files into vector store |
| POST | `/api/chat` | Chat with documents |
| GET | `/api/health` | Health check |

Interactive API docs available at **http://localhost:8000/docs**

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 16, TypeScript, Tailwind CSS |
| Backend | FastAPI, Python 3.10+ |
| LLM | OpenAI GPT-4o-mini |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 |
| Vector Store | ChromaDB |
| Database | SQLite |
| RAG Framework | LangChain |

---

## ⚙️ Configuration

Edit `config/config.yaml` to change LLM provider or model:

```yaml
llm:
  provider: "openai"
  model: "gpt-4o-mini"  # or gpt-4o, gpt-3.5-turbo

providers:
  openai:
    models: ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]
  ollama:
    models: ["deepseek-r1:1.5b"]
    host: "http://localhost:11434"
```

---

## 📝 Usage

1. **Create a Notebook** — Click `+` in the sidebar and give it a name
2. **Upload Documents** — Click `↑ Upload` and select PDF, TXT, MD, or DOCX files
3. **Process Files** — Click `⚡ Process Files` to embed documents into the vector store
4. **Chat** — Ask questions about your documents in the chat box

---

## 🔮 Roadmap

- [ ] Chat history persistence
- [ ] Source citations in responses
- [ ] Excel and PowerPoint support
- [ ] User authentication
- [ ] Deployment to Vercel + Railway

---

## 📄 License

This project is based on [Notebook-RAG](https://github.com/Eng-Elias/notebook_rag) by Eng. Elias, licensed under CC BY-NC-SA 4.0.