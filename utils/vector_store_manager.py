"""
Vector store management for Notebook-RAG application.
"""

import os
import shutil
import torch
import chromadb
from typing import List, Dict, Any, Optional, Union
from pathlib import Path

from langchain_huggingface import HuggingFaceEmbeddings

from .paths import Paths

class VectorStoreManager:
    """Class for managing ChromaDB vector stores for notebooks."""
    
    @staticmethod
    def get_embedding_model():
        """
        Get the embedding model.
        
        Returns:
            HuggingFaceEmbeddings: The embedding model.
        """
        device = (
            "cuda"
            if torch.cuda.is_available()
            else "mps" if torch.backends.mps.is_available() else "cpu"
        )
        return HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": device},
        )
    
    @staticmethod
    def embed_documents(documents: List[str]) -> List[List[float]]:
        """
        Embed documents using the embedding model.
        
        Args:
            documents: List of document texts to embed.
            
        Returns:
            List of document embeddings.
        """
        model = VectorStoreManager.get_embedding_model()
        return model.embed_documents(documents)
    
    @staticmethod
    def embed_query(query: str) -> List[float]:
        """
        Embed a query using the embedding model.
        
        Args:
            query: Query text to embed.
            
        Returns:
            Query embedding.
        """
        model = VectorStoreManager.get_embedding_model()
        return model.embed_query(query)
    
    @staticmethod
    def initialize_collection(
        notebook_name: str,
        delete_existing: bool = False
    ) -> chromadb.Collection:
        """
        Initialize a ChromaDB collection for a notebook.
        
        Args:
            notebook_name: Name of the notebook.
            delete_existing: Whether to delete the existing collection if it exists.
            
        Returns:
            The ChromaDB collection.
        """
        persist_directory = Paths.get_notebook_vector_db_dir(notebook_name)
        
        if os.path.exists(persist_directory) and delete_existing:
            shutil.rmtree(persist_directory)
        
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client with persistent storage
        client = chromadb.PersistentClient(path=persist_directory)
        
        # Create or get a collection
        try:
            # Try to get existing collection first
            collection = client.get_collection(name=notebook_name)
            print(f"Retrieved existing collection for notebook: {notebook_name}")
        except Exception:
            # If collection doesn't exist, create it
            collection = client.create_collection(
                name=notebook_name,
                metadata={
                    "hnsw:space": "cosine",
                    "hnsw:batch_size": 10000,
                },  # Use cosine distance for semantic search
            )
            print(f"Created new collection for notebook: {notebook_name}")
        
        return collection
    
    @staticmethod
    def get_collection(notebook_name: str) -> chromadb.Collection:
        """
        Get a ChromaDB collection for a notebook.
        
        Args:
            notebook_name: Name of the notebook.
            
        Returns:
            The ChromaDB collection.
            
        Raises:
            FileNotFoundError: If the collection does not exist.
        """
        persist_directory = Paths.get_notebook_vector_db_dir(notebook_name)
        
        if not os.path.exists(persist_directory):
            raise FileNotFoundError(f"Vector store for notebook '{notebook_name}' does not exist.")
        
        client = chromadb.PersistentClient(path=persist_directory)
        return client.get_collection(name=notebook_name)
    
    @staticmethod
    def add_documents(
        collection: chromadb.Collection,
        documents: List[str],
        metadata: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """
        Add documents to a ChromaDB collection.
        
        Args:
            collection: The ChromaDB collection.
            documents: List of document texts to add.
            metadata: Optional list of metadata for each document.
        """
        next_id = collection.count()
        
        # Generate embeddings for the documents
        embeddings = VectorStoreManager.embed_documents(documents)
        
        # Generate IDs for the documents
        ids = [f"document_{i}" for i in range(next_id, next_id + len(documents))]
        
        # Add documents to the collection
        if metadata:
            collection.add(
                embeddings=embeddings,
                ids=ids,
                documents=documents,
                metadatas=metadata
            )
        else:
            collection.add(
                embeddings=embeddings,
                ids=ids,
                documents=documents
            )
    
    @staticmethod
    def retrieve_relevant_documents(
        notebook_name: str,
        query: str,
        n_results: int = 5,
        threshold: float = 0.3
    ) -> List[str]:
        """
        Retrieve relevant documents from a notebook's vector store.
        
        Args:
            notebook_name: Name of the notebook.
            query: Query text.
            n_results: Number of results to retrieve.
            threshold: Similarity threshold.
            
        Returns:
            List of relevant document texts.
            
        Raises:
            FileNotFoundError: If the collection does not exist.
        """
        # Get the collection
        collection = VectorStoreManager.get_collection(notebook_name)
        
        # Embed the query
        query_embedding = VectorStoreManager.embed_query(query)
        
        # Query the collection
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "distances"],
        )
        
        # Filter results by threshold
        relevant_documents = []
        for i, distance in enumerate(results["distances"][0]):
            if distance < threshold:
                relevant_documents.append(results["documents"][0][i])
        
        return relevant_documents
    
    @staticmethod
    def list_notebooks() -> List[str]:
        """
        List all available notebooks.
        
        Returns:
            List of notebook names.
        """
        vector_db_dir = Paths.get_vector_db_dir()
        
        if not os.path.exists(vector_db_dir):
            return []
        
        return [
            d for d in os.listdir(vector_db_dir)
            if os.path.isdir(os.path.join(vector_db_dir, d))
        ]
    
    @staticmethod
    def delete_notebook(notebook_name: str) -> bool:
        """
        Delete a notebook's vector store.
        
        Args:
            notebook_name: Name of the notebook.
            
        Returns:
            True if the notebook was deleted, False otherwise.
        """
        notebook_dir = Paths.get_notebook_vector_db_dir(notebook_name)
        
        if not os.path.exists(notebook_dir):
            return False
        
        # First, try to close any open connections to the ChromaDB collection
        try:
            # Create a client to the collection's directory
            client = chromadb.PersistentClient(path=notebook_dir)
            
            # Get the collection if it exists
            try:
                collection = client.get_collection(name=notebook_name)
                # Delete the collection through the API first
                client.delete_collection(name=notebook_name)
            except Exception:
                # Collection might not exist or other error
                pass
            
            # Explicitly delete client to close connections
            try:
                del collection
            except:
                pass
            
            try:
                del client
            except:
                pass
            
            # Force garbage collection to release file handles
            import gc
            gc.collect()
        except Exception as e:
            print(f"Error closing ChromaDB connections: {str(e)}")
        
        # Wait a moment to ensure file handles are released
        import time
        time.sleep(1)
        
        # Try to delete directory with multiple approaches
        success = False
        
        # Approach 1: Use shutil.rmtree directly
        try:
            shutil.rmtree(notebook_dir)
            success = True
        except Exception as e:
            print(f"First deletion attempt failed: {str(e)}")
        
        # Approach 2: Use os.system to force deletion (Windows specific)
        if not success and os.name == 'nt':  # Windows
            try:
                import subprocess
                subprocess.run(f'rd /s /q "{notebook_dir}"', shell=True)
                success = not os.path.exists(notebook_dir)
            except Exception as e:
                print(f"Second deletion attempt failed: {str(e)}")
        
        # Approach 3: Try with ignore_errors
        if not success:
            try:
                shutil.rmtree(notebook_dir, ignore_errors=True)
                success = not os.path.exists(notebook_dir)
            except Exception as e:
                print(f"Third deletion attempt failed: {str(e)}")
        
        return success
