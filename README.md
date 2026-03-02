# Notebook-RAG

[![CC BY-NC-SA 4.0][cc-by-nc-sa-shield]][cc-by-nc-sa]

A modular Streamlit application for document chat with multiple notebooks using Retrieval-Augmented Generation (RAG).

This project is the Module1 publication for Ready Tensor Agentic AI Developer Certification 2025:
[AAIDC2025 Module1 Project - Notebook-RAG](https://app.readytensor.ai/publications/HnFeAayhC99X)

![Notebook-RAG](Notebook-RAG.png)

📺 [Watch the demo video](https://youtu.be/dmYY6ZKtUrc)

## TL;DR

Notebook-RAG is a RAG application that lets you organize documents into separate notebooks, automatically process them, and chat with them using various LLM providers. It has been tested with software engineering papers from [this GitHub repository](https://github.com/facundoolano/software-papers), but you can use it with any text, markdown, or PDF files.

## What is this about? (Purpose)

Notebook-RAG solves the problem of organizing and interacting with multiple document collections through a conversational interface. It enables users to:

1. Create and manage separate notebooks for different document collections or projects
2. Upload and automatically embed documents and store them in a vector database
3. Chat with documents using state-of-the-art retrieval-augmented generation
4. Configure different LLM providers based on needs and availability

This tool is designed for researchers, knowledge workers, and developers who need to interact with multiple document collections through natural language.

## Why does it matter? (Value/Impact)

Notebook-RAG addresses several key challenges in document management and retrieval:

1. **Information Overload**: Helps users extract relevant information from large document collections through natural language queries
2. **Context Organization**: Allows separation of different document contexts into distinct notebooks
3. **Flexibility**: Supports multiple LLM providers, allowing users to choose based on performance, cost, or privacy requirements
4. **Persistence**: Maintains document organization and processing status across sessions
5. **Efficiency**: Prevents redundant processing of documents, saving time and computational resources

Unlike single-context RAG applications, Notebook-RAG's multi-notebook architecture enables users to maintain separate document contexts for different projects or domains, improving retrieval relevance and reducing context confusion.

## Features

- **Multiple Notebooks**: Create and manage separate notebooks for different document collections
- **Document Upload**: Upload PDF, TXT, and MD files with automatic organization into notebook-specific directories
- **Automatic Processing**: Document extraction, chunking, and embedding with intelligent status tracking
- **Persistent Storage**: 
  - ChromaDB vector collections for document embeddings
  - SQLite database for notebook and file metadata
  - Organized file storage in notebook-specific directories
- **Interactive Chat**: Natural language interaction with documents using RAG
- **Multi-LLM Support**: Configure and switch between LLM providers:
  - Groq (default cloud provider)
  - Ollama (local models for privacy and offline use)

## Technical Architecture

Notebook-RAG follows a modular, object-oriented architecture that separates concerns and enables easy maintenance and extension:

### Core Components

1. **Document Processing Pipeline**
   - Extracts text from various document formats using specialized extractors
   - Chunks text into manageable segments using LangChain text splitters
   - Embeds chunks using Sentence Transformers for semantic search

2. **Vector Store Management**
   - Interfaces with ChromaDB for efficient vector storage and retrieval
   - Maintains separate collections per notebook for context isolation
   - Implements robust deletion with multi-step fallback strategies

3. **Conversation Management**
   - Abstracts LLM provider interfaces for consistent API access
   - Implements provider-specific initialization and API calls
   - Handles prompt construction and response generation

4. **Database Management**
   - Maintains notebook and file metadata in SQLite
   - Tracks processing status to prevent redundant operations
   - Enforces data integrity with proper validation

5. **File System Management**
   - Organizes uploaded files in notebook-specific directories
   - Implements robust file operations with proper error handling
   - Ensures consistent naming and directory structure

### Project Structure

```
notebook_rag/
├── app.py                  # Main Streamlit application
├── config/                 # Configuration files
│   ├── config.yaml         # Application configuration
│   └── prompt_config.yaml  # Prompt templates
├── utils/                  # Utility modules
│   ├── paths.py            # Path management
│   ├── config_manager.py   # Configuration loading
│   ├── prompt_builder.py   # Prompt construction
│   ├── document_processor.py # Document processing
│   ├── vector_store_manager.py # ChromaDB management
│   ├── conversation_manager.py # LLM interaction
│   └── database_manager.py # SQLite database operations
├── uploaded_files/         # Directory for uploaded files (organized by notebook)
├── vector_db/             # Directory for ChromaDB collections
├── notebooks.db           # SQLite database for metadata
├── .env                    # Environment variables (API keys)
├── requirements.txt        # Dependencies
└── README.md               # This file
```

### Technical Validation

The application has been tested with various document types and LLM providers to ensure reliability and performance:

- **Document Processing**: Successfully handles PDF, TXT, and MD files with proper text extraction and chunking
- **Vector Retrieval**: ChromaDB integration provides efficient semantic search with high relevance
- **Multi-LLM Support**: Tested with Groq and Ollama for compatibility and consistent performance
- **Persistence**: SQLite database ensures reliable metadata storage and retrieval across sessions
- **File Management**: Robust file handling with proper error handling and cleanup mechanisms
- **Notebook Deletion**: Multi-step deletion process handles file locks and ensures complete cleanup

### Limitations

- Currently supports only text-based documents (PDF, TXT, MD)
- Does not support image or audio content extraction
- Performance depends on the chosen LLM provider's capabilities and rate limits
- Local LLM performance depends on user hardware capabilities
- No built-in document versioning or history tracking

## Setup and Installation

### Prerequisites

- Python 3.10 installed
- Git (optional, for cloning the repository)
- API keys for LLM providers (Groq recommended as default)

### Installation Steps

1. Clone this repository or download the source code:
   ```bash
   git clone <repository_url>
   cd notebook-rag
   ```

2. Create a virtual environment:
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # Linux/Mac
   python -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   for CUDA support run this commands too:
   ```bash
   pip install -r requirements_cuda.txt
   ```

4. Create a `.env` file in the project root with your API keys:
   ```
   # Required for Groq LLM provider
   GROQ_API_KEY=your_groq_api_key
   ```

5. Run the application:
   ```bash
   streamlit run app.py
   ```
   The application will be available at http://localhost:8501 in your web browser.

## Detailed Usage Guide

### 1. Notebook Management

#### Creating a Notebook
- Navigate to the sidebar on the left side of the application
- Enter a unique notebook name in the text input field (minimum 3 characters required)
- Click the "Create Notebook" button
- The new notebook will be automatically selected and ready for use
- A new directory will be created at `uploaded_files/<notebook_name>` to store your documents

#### Selecting a Notebook
- Use the dropdown menu in the sidebar labeled "Select Notebook"
- Choose an existing notebook from the list
- The notebook's content and chat interface will be displayed in the main area

### 2. Document Management

#### Uploading Documents
- With a notebook selected, locate the file uploader in the main area
- Click "Browse files" to open your system's file picker
- Select one or more supported files (PDF, TXT, MD)
- Files will be automatically uploaded to the notebook-specific directory
- Uploaded files will appear in the "Uploaded Files" list

#### Processing Documents
- After uploading files, click the "Process Files" button
- The system will extract text, chunk it, and create embeddings
- Already processed files will be skipped to save time
- Processing status is tracked in the database for persistence

### 3. LLM Configuration

#### Selecting a Provider
- In the sidebar, locate the "LLM Provider" dropdown
- Choose from available providers (Groq, Ollama)
- Each provider has different characteristics:
  - Groq: Cloud-based, requires API key, higher quality
  - Ollama: Local models, no API key, runs on your hardware

#### Selecting a Model
- After choosing a provider, use the "LLM Model" dropdown
- Select from available models for the chosen provider
- Model selection affects response quality and speed

### 4. Chatting with Documents

#### Asking Questions
- With a notebook selected and documents processed, use the chat interface
- Type your question in the text input at the bottom of the chat area
- Press Enter or click the send button to submit your question
- The system will:
  1. Find relevant document chunks using semantic search
  2. Generate a response using the selected LLM
  3. Display the response

## Configuration

The application can be configured through the `config.yaml` and `prompt_config.yaml` files:

- **config.yaml**: Configure LLM providers and models, vector database parameters, memory strategies, and reasoning strategies
- **prompt_config.yaml**: Configure prompt templates for system and RAG

### LLM Configuration

The application supports multiple LLM providers that can be configured in the `config.yaml` file.

You can also change the LLM provider and model at runtime through the application interface.

### Database Configuration

The application uses SQLite to store:
- Notebook metadata (name, creation date, update date)
- File metadata (original filename, stored filename, upload date, processing status)

This ensures persistence across application restarts and prevents reprocessing of already processed files.

## License

This application is open-source and is released under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License. See the [LICENSE](LICENSE) file for details.

Shield: [![CC BY-NC-SA 4.0][cc-by-nc-sa-shield]][cc-by-nc-sa]

This work is licensed under a
[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License][cc-by-nc-sa].

[![CC BY-NC-SA 4.0][cc-by-nc-sa-image]][cc-by-nc-sa]

[cc-by-nc-sa]: http://creativecommons.org/licenses/by-nc-sa/4.0/
[cc-by-nc-sa-image]: https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png
[cc-by-nc-sa-shield]: https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg
