"""
Conversation management for Notebook-RAG application.
"""

from typing import Optional
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

from .vector_store_manager import VectorStoreManager
from .prompt_builder import PromptBuilder
from .config_manager import ConfigManager

class ConversationManager:
    """Class for managing conversations with documents."""
    
    @staticmethod
    def get_llm(provider: Optional[str], model_name: Optional[str] = None):
        app_config = ConfigManager.get_app_config()
        llm_config = app_config.get("llm", {})
        
        if not provider:
            provider = llm_config.get("provider", "openai")
        if not model_name:
            model_name = llm_config.get("model", "gpt-4o-mini")
        
        if provider == "openai":
            return ChatOpenAI(model=model_name)

        elif provider == "groq":
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
        threshold: float = 0.8,
        provider: Optional[str] = None,
        model_name: Optional[str] = None,
    ) -> str:
        relevant_documents = VectorStoreManager.retrieve_relevant_documents(
            notebook_name=notebook_name,
            query=query,
            n_results=n_results,
            threshold=threshold,
        )
        
        if not relevant_documents:
            return "I couldn't find any relevant information in this notebook to answer your question."
        
        prompt_config = ConfigManager.get_prompt_config()
        rag_assistant_prompt = prompt_config.get("rag_assistant_prompt", {})
        
        input_data = (
            f"Relevant documents:\n\n{relevant_documents}\n\nUser's question:\n\n{query}"
        )
        
        prompt = PromptBuilder.build_prompt_from_config(
            config=rag_assistant_prompt,
            input_data=input_data,
        )
        
        llm = ConversationManager.get_llm(provider, model_name)
        response = llm.invoke(prompt)
        
        return response.content
    
    @staticmethod
    def create_system_prompt(notebook_name: str) -> str:
        prompt_config = ConfigManager.get_prompt_config()
        system_prompt_config = prompt_config.get("ai_assistant_system_prompt_advanced", {})
        
        return PromptBuilder.build_system_prompt_from_config(
            config=system_prompt_config,
            document_content=f"You are assisting with the notebook '{notebook_name}'."
        )
