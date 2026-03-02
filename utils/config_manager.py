"""
Configuration management for Notebook-RAG application.
"""

import os
import yaml
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Any, Optional

from .paths import Paths

class ConfigManager:
    """Class for managing application configuration."""
    
    @staticmethod
    def load_yaml_config(file_path: str) -> Dict[str, Any]:
        """
        Load a YAML configuration file.
        
        Args:
            file_path: Path to the YAML file.
            
        Returns:
            Parsed YAML content as a dictionary.
            
        Raises:
            FileNotFoundError: If the file does not exist.
            yaml.YAMLError: If there's an error parsing YAML.
            IOError: If there's an error reading the file.
        """
        file_path = Path(file_path)
        
        # Check if file exists
        if not file_path.exists():
            raise FileNotFoundError(f"YAML config file not found: {file_path}")
        
        # Read and parse the YAML file
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return yaml.safe_load(file)
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Error parsing YAML file: {e}") from e
        except IOError as e:
            raise IOError(f"Error reading YAML file: {e}") from e
    
    @staticmethod
    def load_env(api_key_type: str = "GROQ_API_KEY") -> None:
        """
        Load environment variables from a .env file and check for required keys.
        
        Args:
            api_key_type: The API key to check for.
            
        Raises:
            AssertionError: If required keys are missing.
        """
        # Load environment variables from .env file
        load_dotenv(Paths.get_env_path(), override=True)
        
        # Check if API key has been loaded
        api_key = os.getenv(api_key_type)
        
        assert api_key, f"Environment variable '{api_key_type}' has not been loaded or is not set in the .env file."
    
    @staticmethod
    def get_app_config() -> Dict[str, Any]:
        """
        Get the application configuration.
        
        Returns:
            The application configuration as a dictionary.
        """
        return ConfigManager.load_yaml_config(Paths.get_app_config_path())
    
    @staticmethod
    def get_prompt_config() -> Dict[str, Any]:
        """
        Get the prompt configuration.
        
        Returns:
            The prompt configuration as a dictionary.
        """
        return ConfigManager.load_yaml_config(Paths.get_prompt_config_path())
    
    @staticmethod
    def save_yaml_config(config: Dict[str, Any], file_path: str) -> None:
        """
        Save a configuration dictionary to a YAML file.
        
        Args:
            config: The configuration dictionary to save.
            file_path: The path to save the configuration to.
            
        Raises:
            IOError: If there's an error writing the file.
        """
        file_path = Path(file_path)
        
        # Create directory if it doesn't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                yaml.dump(config, file, default_flow_style=False)
        except IOError as e:
            raise IOError(f"Error writing YAML file: {e}") from e
