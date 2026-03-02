"""
Document processing utilities for Notebook-RAG application.
"""

import os
from typing import List, Optional, Union
from pathlib import Path
import PyPDF2
from langchain_text_splitters import RecursiveCharacterTextSplitter

class DocumentProcessor:
    """Class for processing documents (PDF, TXT, MD) and splitting them into chunks."""
    
    @staticmethod
    def extract_text_from_pdf(file_path: Union[str, Path]) -> str:
        """
        Extract text from a PDF file.
        
        Args:
            file_path: Path to the PDF file.
            
        Returns:
            Extracted text as a string.
            
        Raises:
            FileNotFoundError: If the file does not exist.
            IOError: If there's an error reading the file.
        """
        file_path = Path(file_path)
        
        # Check if file exists
        if not file_path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        # Extract text from PDF
        try:
            text = ""
            with open(file_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            raise IOError(f"Error reading PDF file: {e}") from e
    
    @staticmethod
    def extract_text_from_txt(file_path: Union[str, Path]) -> str:
        """
        Extract text from a TXT file.
        
        Args:
            file_path: Path to the TXT file.
            
        Returns:
            Extracted text as a string.
            
        Raises:
            FileNotFoundError: If the file does not exist.
            IOError: If there's an error reading the file.
        """
        file_path = Path(file_path)
        
        # Check if file exists
        if not file_path.exists():
            raise FileNotFoundError(f"TXT file not found: {file_path}")
        
        # Read text from TXT file
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()
        except IOError as e:
            raise IOError(f"Error reading TXT file: {e}") from e
    
    @staticmethod
    def extract_text_from_md(file_path: Union[str, Path]) -> str:
        """
        Extract text from a Markdown file.
        
        Args:
            file_path: Path to the Markdown file.
            
        Returns:
            Extracted text as a string.
            
        Raises:
            FileNotFoundError: If the file does not exist.
            IOError: If there's an error reading the file.
        """
        # Markdown files are essentially text files, so we can use the same function
        return DocumentProcessor.extract_text_from_txt(file_path)
    
    @staticmethod
    def extract_text_from_file(file_path: Union[str, Path]) -> str:
        """
        Extract text from a file based on its extension.
        
        Args:
            file_path: Path to the file.
            
        Returns:
            Extracted text as a string.
            
        Raises:
            ValueError: If the file extension is not supported.
            FileNotFoundError: If the file does not exist.
            IOError: If there's an error reading the file.
        """
        file_path = Path(file_path)
        
        # Check file extension and call appropriate function
        extension = file_path.suffix.lower()
        if extension == ".pdf":
            return DocumentProcessor.extract_text_from_pdf(file_path)
        elif extension == ".txt":
            return DocumentProcessor.extract_text_from_txt(file_path)
        elif extension == ".md":
            return DocumentProcessor.extract_text_from_md(file_path)
        else:
            raise ValueError(f"Unsupported file extension: {extension}")
    
    @staticmethod
    def chunk_text(
        text: str, 
        chunk_size: int = 1000, 
        chunk_overlap: int = 200
    ) -> List[str]:
        """
        Split text into chunks using RecursiveCharacterTextSplitter.
        
        Args:
            text: The text to split.
            chunk_size: Maximum size of each chunk.
            chunk_overlap: Overlap between chunks.
            
        Returns:
            List of text chunks.
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        return text_splitter.split_text(text)
    
    @staticmethod
    def process_document(
        file_path: Union[str, Path],
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ) -> List[str]:
        """
        Process a document by extracting text and splitting it into chunks.
        
        Args:
            file_path: Path to the document.
            chunk_size: Maximum size of each chunk.
            chunk_overlap: Overlap between chunks.
            
        Returns:
            List of text chunks.
            
        Raises:
            ValueError: If the file extension is not supported.
            FileNotFoundError: If the file does not exist.
            IOError: If there's an error reading the file.
        """
        # Extract text from file
        text = DocumentProcessor.extract_text_from_file(file_path)
        
        # Split text into chunks
        return DocumentProcessor.chunk_text(text, chunk_size, chunk_overlap)
