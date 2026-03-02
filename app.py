"""
Notebook-RAG: A Streamlit application for document chat with multiple notebooks.
"""

import os
from dotenv import load_dotenv
import streamlit as st
import uuid
from datetime import datetime

from utils.paths import Paths
from utils.config_manager import ConfigManager
from utils.document_processor import DocumentProcessor
from utils.vector_store_manager import VectorStoreManager
from utils.conversation_manager import ConversationManager
from utils.database_manager import DatabaseManager

load_dotenv()

# Initialize paths and database
Paths.ensure_directories_exist()
DatabaseManager.initialize_database()

# Page configuration
st.set_page_config(
    page_title="Notebook-RAG",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "notebooks" not in st.session_state:
    st.session_state.notebooks = [notebook["name"] for notebook in DatabaseManager.list_notebooks()]
if "selected_notebook" not in st.session_state:
    st.session_state.selected_notebook = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = {}
if "documents" not in st.session_state:
    st.session_state.documents = {}
if "llm_provider" not in st.session_state:
    app_config = ConfigManager.get_app_config()
    st.session_state.llm_provider = app_config.get("llm", {}).get("provider", "groq")
if "llm_model" not in st.session_state:
    app_config = ConfigManager.get_app_config()
    st.session_state.llm_model = app_config.get("llm", {}).get("model", "meta-llama/llama-4-scout-17b-16e-instruct")
if "notebook_selector" not in st.session_state:
    st.session_state.notebook_selector = None

def create_notebook():
    """Create a new notebook."""
    notebook_name = st.session_state.new_notebook_name
    
    try:
        # Validate notebook name
        if not notebook_name or len(notebook_name) < 3:
            st.error("Notebook name must be at least 3 characters long.")
            return
            
        # Validate and normalize notebook name for ChromaDB compatibility
        # Replace spaces with dashes
        notebook_name = notebook_name.replace(" ", "-")
        
        # Check if name starts and ends with alphanumeric character
        import re
        if not re.match(r'^[a-zA-Z0-9].*[a-zA-Z0-9]$', notebook_name):
            st.error("Notebook name must start and end with a letter or number.")
            return
            
        # Check if normalized name contains only allowed characters
        if not re.match(r'^[a-zA-Z0-9._-]+$', notebook_name):
            st.error("Notebook name can only contain letters, numbers, periods, underscores, and dashes.")
            return

        DatabaseManager.create_notebook(notebook_name)
        
        # Initialize collection
        VectorStoreManager.initialize_collection(notebook_name)
        
        # Create notebook directory for files
        os.makedirs(Paths.get_notebook_files_dir(notebook_name), exist_ok=True)
        
        # Update notebooks list
        st.session_state.notebooks = [notebook["name"] for notebook in DatabaseManager.list_notebooks()]
        
        # Select the new notebook
        st.session_state.selected_notebook = notebook_name
        st.session_state.notebook_selector = notebook_name
        
        # Initialize chat history for the new notebook
        if notebook_name not in st.session_state.chat_history:
            st.session_state.chat_history[notebook_name] = []
        
        # Initialize documents for the new notebook
        if notebook_name not in st.session_state.documents:
            st.session_state.documents[notebook_name] = []
        
        # Clear the input field
        st.session_state.new_notebook_name = ""
        
        st.success(f"Notebook '{notebook_name}' created successfully.")
    except ValueError as e:
        st.error(str(e))

def delete_notebook():
    """Delete the selected notebook."""
    notebook_name = st.session_state.selected_notebook
    if notebook_name:
        try:
            # Delete the notebook from database
            DatabaseManager.delete_notebook(notebook_name)
            
            # Try to delete the notebook's vector store with error handling
            try:
                VectorStoreManager.delete_notebook(notebook_name)
            except Exception as e:
                st.warning(f"Could not completely delete vector store: {str(e)}")
                # Try to force close any open file handles
                import gc
                gc.collect()
                
                # Try to delete the directory manually
                vector_db_dir = Paths.get_notebook_vector_db_dir(notebook_name)
                if os.path.exists(vector_db_dir):
                    try:
                        import shutil
                        shutil.rmtree(vector_db_dir, ignore_errors=True)
                    except Exception:
                        pass
            
            # Delete the notebook's files directory
            notebook_files_dir = Paths.get_notebook_files_dir(notebook_name)
            if os.path.exists(notebook_files_dir):
                try:
                    import shutil
                    shutil.rmtree(notebook_files_dir, ignore_errors=True)
                except Exception as e:
                    st.warning(f"Could not completely delete files directory: {str(e)}")
            
            # Update notebooks list
            st.session_state.notebooks = [notebook["name"] for notebook in DatabaseManager.list_notebooks()]
            
            # Clear selected notebook
            st.session_state.selected_notebook = None
            st.session_state.notebook_selector = None if not st.session_state.notebooks else st.session_state.notebooks[0]
            
            # Clear chat history for the deleted notebook
            if notebook_name in st.session_state.chat_history:
                del st.session_state.chat_history[notebook_name]
            
            # Clear documents for the deleted notebook
            if notebook_name in st.session_state.documents:
                del st.session_state.documents[notebook_name]
            
            st.success(f"Notebook '{notebook_name}' deleted successfully.")
        except Exception as e:
            st.error(f"Error deleting notebook: {str(e)}")

def select_notebook():
    """Select a notebook."""
    notebook_name = st.session_state.notebook_selector
    
    # If "None" is selected, clear the selected notebook
    if notebook_name == "None":
        st.session_state.selected_notebook = None
        return
    
    # Otherwise, set the selected notebook
    if notebook_name:
        st.session_state.selected_notebook = notebook_name
        
        # Initialize chat history for the selected notebook
        if notebook_name not in st.session_state.chat_history:
            st.session_state.chat_history[notebook_name] = []
        
        # Load documents for the selected notebook
        try:
            files = DatabaseManager.get_files_by_notebook(notebook_name)
            st.session_state.documents[notebook_name] = [file["original_filename"] for file in files]
        except ValueError:
            st.session_state.documents[notebook_name] = []

def process_uploaded_files(uploaded_files):
    """Process uploaded files and add them to the selected notebook."""
    notebook_name = st.session_state.selected_notebook
    if not notebook_name:
        st.error("Please select a notebook first.")
        return
    
    # Get the collection
    try:
        collection = VectorStoreManager.get_collection(notebook_name)
    except FileNotFoundError:
        st.error(f"Notebook '{notebook_name}' not found.")
        return
    
    # Create notebook directory if it doesn't exist
    notebook_files_dir = Paths.get_notebook_files_dir(notebook_name)
    os.makedirs(notebook_files_dir, exist_ok=True)
    
    # Process each file
    for uploaded_file in uploaded_files:
        # Generate a unique filename to store
        file_extension = uploaded_file.name.split('.')[-1]
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        stored_filename = f"{timestamp}_{unique_id}.{file_extension}"
        stored_file_path = os.path.join(notebook_files_dir, stored_filename)
        
        # Save the uploaded file to the notebook's directory
        with open(stored_file_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        
        # Add file to database
        try:
            DatabaseManager.add_file(notebook_name, uploaded_file.name, stored_filename)
            st.success(f"File '{uploaded_file.name}' uploaded successfully.")
        except ValueError as e:
            st.error(str(e))
            # Delete the file if there was an error
            if os.path.exists(stored_file_path):
                os.remove(stored_file_path)

def process_files():
    """Process files in the selected notebook."""
    notebook_name = st.session_state.selected_notebook
    if not notebook_name:
        st.error("Please select a notebook first.")
        return
    
    # Get the collection
    try:
        collection = VectorStoreManager.get_collection(notebook_name)
    except FileNotFoundError:
        st.error(f"Notebook '{notebook_name}' not found.")
        return
    
    # Get unprocessed files
    try:
        unprocessed_files = DatabaseManager.get_unprocessed_files(notebook_name)
        
        if not unprocessed_files:
            st.info("No new files to process.")
            return
        
        # Process each unprocessed file
        for file in unprocessed_files:
            file_path = os.path.join(Paths.get_notebook_files_dir(notebook_name), file["stored_filename"])
            
            try:
                # Process the document
                chunks = DocumentProcessor.process_document(file_path)
                
                # Add the document to the collection
                VectorStoreManager.add_documents(
                    collection=collection,
                    documents=chunks,
                    metadata=[{"source": file["original_filename"]} for _ in chunks]
                )
                
                # Mark file as processed
                DatabaseManager.mark_file_as_processed(file["id"])
                
                # Add the document to the session state if not already there
                if notebook_name not in st.session_state.documents:
                    st.session_state.documents[notebook_name] = []
                if file["original_filename"] not in st.session_state.documents[notebook_name]:
                    st.session_state.documents[notebook_name].append(file["original_filename"])
                
                st.success(f"Successfully processed '{file['original_filename']}' and added to notebook '{notebook_name}'.")
            except Exception as e:
                st.error(f"Error processing '{file['original_filename']}': {str(e)}")
    except ValueError as e:
        st.error(str(e))

def send_message():
    """Send a message to the selected notebook."""
    message = st.session_state.message_input
    notebook_name = st.session_state.selected_notebook
    
    if not message or not notebook_name:
        return
    
    # Add user message to chat history
    if notebook_name not in st.session_state.chat_history:
        st.session_state.chat_history[notebook_name] = []
    st.session_state.chat_history[notebook_name].append({"role": "user", "content": message})
    
    # Get response from the model
    try:
        # Get vectordb parameters from config
        app_config = ConfigManager.get_app_config()
        vectordb_params = app_config.get("vectordb", {})
        
        # Generate response
        response = ConversationManager.respond_to_query(
            notebook_name=notebook_name,
            query=message,
            n_results=vectordb_params.get("n_results", 5),
            threshold=vectordb_params.get("threshold", 0.3),
            provider=st.session_state.llm_provider,
            model_name=st.session_state.llm_model
        )
        
        # Add assistant response to chat history
        st.session_state.chat_history[notebook_name].append({"role": "assistant", "content": response})
    except Exception as e:
        # Add error message to chat history
        st.session_state.chat_history[notebook_name].append({"role": "assistant", "content": f"Error: {str(e)}"})

def update_llm_settings():
    """Update LLM settings."""
    provider = st.session_state.llm_provider_selector
    model = st.session_state.llm_model_selector
    
    st.session_state.llm_provider = provider
    st.session_state.llm_model = model
    
    st.success(f"LLM settings updated: Provider: {provider}, Model: {model}")

# Sidebar
with st.sidebar:
    st.title("Notebook-RAG 📚")
    st.write("Chat with your documents in organized notebooks.")
    
    # Create new notebook
    st.subheader("Create New Notebook")
    st.text_input("Notebook Name (min 3 chars)", key="new_notebook_name")
    st.button("Create Notebook", on_click=create_notebook)
    
    # Select notebook
    st.subheader("Select Notebook")
    if st.session_state.notebooks:
        # Add "None" as the first option
        options = ["None"] + st.session_state.notebooks
        st.selectbox(
            "Choose a notebook",
            options=options,
            index=0 if st.session_state.notebook_selector is None else options.index(st.session_state.notebook_selector) if st.session_state.notebook_selector in options else 0,
            key="notebook_selector",
            on_change=select_notebook
        )
    else:
        st.info("No notebooks available. Create one to get started.")
    
    # Delete notebook
    if st.session_state.selected_notebook:
        st.button("Delete Selected Notebook", on_click=delete_notebook)
    
    # Upload documents
    if st.session_state.selected_notebook:
        st.subheader("Upload Documents")
        st.write("Supported formats: PDF, TXT, MD")
        uploaded_files = st.file_uploader(
            "Choose files (files will be uploaded automatically)",
            accept_multiple_files=True,
            type=["pdf", "txt", "md"],
            on_change=lambda: process_uploaded_files(st.session_state.uploaded_files) if 'uploaded_files' in st.session_state else None,
            key="uploaded_files"
        )
        if uploaded_files:
            st.button("Process Files", on_click=process_files)

    # LLM Settings
    st.subheader("LLM Settings")
    
    # Get available providers and models from config
    app_config = ConfigManager.get_app_config()
    providers_config = app_config.get("providers", {})
    
    # Provider selector
    provider_options = list(providers_config.keys())
    st.selectbox(
        "LLM Provider",
        options=provider_options,
        index=provider_options.index(st.session_state.llm_provider) if st.session_state.llm_provider in provider_options else 0,
        key="llm_provider_selector"
    )
    
    # Model selector based on selected provider
    selected_provider = st.session_state.llm_provider_selector
    model_options = providers_config.get(selected_provider, {}).get("models", [])
    
    st.selectbox(
        "LLM Model",
        options=model_options,
        index=model_options.index(st.session_state.llm_model) if st.session_state.llm_model in model_options else 0,
        key="llm_model_selector"
    )
    
    st.button("Update LLM Settings", on_click=update_llm_settings)
    
    st.markdown("---")


# Main content
if st.session_state.selected_notebook:
    st.title(f"Notebook: {st.session_state.selected_notebook}")
    
    # Display documents
    if st.session_state.selected_notebook in st.session_state.documents and st.session_state.documents[st.session_state.selected_notebook]:
        st.subheader("Documents")
        for doc in st.session_state.documents[st.session_state.selected_notebook]:
            st.write(f"- {doc}")
    
    # Chat interface
    st.subheader("Chat")
    
    # Display chat history
    if st.session_state.selected_notebook in st.session_state.chat_history:
        for message in st.session_state.chat_history[st.session_state.selected_notebook]:
            if message["role"] == "user":
                st.chat_message("user").write(message["content"])
            else:
                st.chat_message("assistant").write(message["content"])
    
    # Message input
    st.chat_input("Ask a question about your documents", key="message_input", on_submit=send_message)
else:
    st.title("Welcome to Notebook-RAG")
    st.write("Please select or create a notebook to get started.")
    if st.session_state.notebooks:
        st.info("Select a notebook from the dropdown in the sidebar to begin.")
    else:
        st.info("Use the sidebar to create a new notebook to get started.")

# Footer
st.markdown("---")
st.caption("Notebook-RAG: A document chat application with multiple notebooks")
