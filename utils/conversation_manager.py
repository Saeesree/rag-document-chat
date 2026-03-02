"""
Conversation management for Notebook-RAG application.
"""

from typing import Optional
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama

from .vector_store_manager import VectorStoreManager
from .prompt_builder import PromptBuilder
from .config_manager import ConfigManager

class ConversationManager:
    """Class for managing conversations with documents."""
    
    @staticmethod
    def get_llm(provider: Optional[str], model_name: Optional[str] = None):
        """
        Get a language model instance based on the configuration.
        
        Args:
            model_name: Optional model name to use. If not provided, will use the one from config.
            
        Returns:
            Language model instance.
        """
        # Get config
        app_config = ConfigManager.get_app_config()
        llm_config = app_config.get("llm", {})
        
        # Get provider and model
        if not provider:
            provider = llm_config.get("provider", "groq")
        if not model_name:
            model_name = llm_config.get("model", "meta-llama/llama-4-scout-17b-16e-instruct")
        
        if provider == "groq":
            return ChatGroq(model=model_name)

        elif provider == "ollama":
            return ChatOllama(model=model_name)

        else:
            raise Exception("Invalid LLM provider")

    @staticmethod
    def respond_to_query(
        notebook_name: str,
        query: str,
        n_results: int = 5,
        threshold: float = 0.3,
        provider: Optional[str] = None,
        model_name: Optional[str] = None,
    ) -> str:
        """
        Respond to a query using RAG.
        
        Args:
            notebook_name: Name of the notebook to query.
            query: Query text.
            n_results: Number of results to retrieve.
            threshold: Similarity threshold.
            model_name: Optional model name to use.
            
        Returns:
            Response text.
            
        Raises:
            FileNotFoundError: If the notebook does not exist.
        """
        # Retrieve relevant documents
        relevant_documents = VectorStoreManager.retrieve_relevant_documents(
            notebook_name=notebook_name,
            query=query,
            n_results=n_results,
            threshold=threshold,
        )
        
        # If no relevant documents were found
        if not relevant_documents:
            return "I couldn't find any relevant information in this notebook to answer your question."
        
        # Get prompt config
        prompt_config = ConfigManager.get_prompt_config()
        rag_assistant_prompt = prompt_config.get("rag_assistant_prompt", {})
        
        # Prepare input data
        input_data = (
            f"Relevant documents:\n\n{relevant_documents}\n\nUser's question:\n\n{query}"
        )
        
        # Build prompt
        prompt = PromptBuilder.build_prompt_from_config(
            config=rag_assistant_prompt,
            input_data=input_data,
        )
        
        # Get LLM
        llm = ConversationManager.get_llm(provider, model_name)
        
        # Generate response
        response = llm.invoke(prompt)
        
        return response.content
    
    @staticmethod
    def create_system_prompt(notebook_name: str) -> str:
        """
        Create a system prompt for a notebook.
        
        Args:
            notebook_name: Name of the notebook.
            
        Returns:
            System prompt text.
        """
        prompt_config = ConfigManager.get_prompt_config()
        system_prompt_config = prompt_config.get("ai_assistant_system_prompt_advanced", {})
        
        return PromptBuilder.build_system_prompt_from_config(
            config=system_prompt_config,
            document_content=f"You are assisting with the notebook '{notebook_name}'."
        )
