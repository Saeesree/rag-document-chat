"""
Path configuration for Notebook-RAG application.
"""

import os
from pathlib import Path

class Paths:
    """Class for managing application paths."""
    
    @staticmethod
    def get_root_dir():
        """Get the root directory of the application."""
        return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    @staticmethod
    def get_app_dir():
        """Get the application directory."""
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    @staticmethod
    def get_utils_dir():
        """Get the utils directory."""
        return os.path.dirname(os.path.abspath(__file__))
    
    @staticmethod
    def get_env_path():
        """Get the path to the .env file."""
        return os.path.join(Paths.get_root_dir(), ".env")
    
    @staticmethod
    def get_config_dir():
        """Get the config directory."""
        return os.path.join(Paths.get_app_dir(), "config")
    
    @staticmethod
    def get_app_config_path():
        """Get the path to the app config file."""
        return os.path.join(Paths.get_config_dir(), "config.yaml")
    
    @staticmethod
    def get_prompt_config_path():
        """Get the path to the prompt config file."""
        return os.path.join(Paths.get_config_dir(), "prompt_config.yaml")
    
    @staticmethod
    def get_data_dir():
        """Get the data directory."""
        return os.path.join(Paths.get_app_dir(), "data")
    
    @staticmethod
    def get_vector_db_dir():
        """Get the vector database directory."""
        return os.path.join(Paths.get_app_dir(), "vector_db")
    
    @staticmethod
    def get_notebook_vector_db_dir(notebook_name):
        """Get the vector database directory for a specific notebook."""
        return os.path.join(Paths.get_vector_db_dir(), notebook_name)
    
    @staticmethod
    def get_uploaded_files_dir():
        """Get the uploaded files directory."""
        return os.path.join(Paths.get_app_dir(), "uploaded_files")
    
    @staticmethod
    def get_notebook_files_dir(notebook_name):
        """Get the uploaded files directory for a specific notebook."""
        return os.path.join(Paths.get_uploaded_files_dir(), notebook_name)
    
    @staticmethod
    def get_database_path():
        """Get the SQLite database file path."""
        return os.path.join(Paths.get_app_dir(), "notebooks.db")
    
    @staticmethod
    def ensure_directories_exist():
        """Ensure all required directories exist."""
        directories = [
            Paths.get_config_dir(),
            Paths.get_data_dir(),
            Paths.get_vector_db_dir(),
            Paths.get_uploaded_files_dir()
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
