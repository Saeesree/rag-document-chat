"""
Database management for Notebook-RAG application.
"""

import os
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from .paths import Paths

class DatabaseManager:
    """Class for managing SQLite database operations."""
    
    @staticmethod
    def get_db_connection():
        """
        Get a connection to the SQLite database.
        
        Returns:
            sqlite3.Connection: Database connection.
        """
        db_path = Paths.get_database_path()
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        return conn
    
    @staticmethod
    def initialize_database():
        """
        Initialize the database with required tables.
        """
        conn = DatabaseManager.get_db_connection()
        cursor = conn.cursor()
        
        # Create notebooks table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS notebooks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP NOT NULL,
            CHECK(length(name) >= 3)
        )
        ''')
        
        # Create files table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            notebook_id INTEGER NOT NULL,
            original_filename TEXT NOT NULL,
            stored_filename TEXT NOT NULL,
            upload_date TIMESTAMP NOT NULL,
            is_processed BOOLEAN NOT NULL DEFAULT 0,
            FOREIGN KEY (notebook_id) REFERENCES notebooks (id) ON DELETE CASCADE
        )
        ''')
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def create_notebook(name: str) -> bool:
        """
        Create a new notebook.
        
        Args:
            name: Name of the notebook.
            
        Returns:
            bool: True if successful, False otherwise.
            
        Raises:
            ValueError: If the notebook name is invalid.
        """
        # Validate notebook name
        if not name or len(name) < 3:
            raise ValueError("Notebook name must be at least 3 characters long.")
        
        conn = DatabaseManager.get_db_connection()
        cursor = conn.cursor()
        
        try:
            now = datetime.now().isoformat()
            cursor.execute(
                "INSERT INTO notebooks (name, created_at, updated_at) VALUES (?, ?, ?)",
                (name, now, now)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Notebook with this name already exists
            conn.rollback()
            raise ValueError(f"Notebook with name '{name}' already exists.")
        finally:
            conn.close()
    
    @staticmethod
    def get_notebook_by_name(name: str) -> Optional[Dict[str, Any]]:
        """
        Get a notebook by name.
        
        Args:
            name: Name of the notebook.
            
        Returns:
            Optional[Dict[str, Any]]: Notebook data or None if not found.
        """
        conn = DatabaseManager.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM notebooks WHERE name = ?", (name,))
        notebook = cursor.fetchone()
        
        conn.close()
        
        if notebook:
            return dict(notebook)
        return None
    
    @staticmethod
    def list_notebooks() -> List[Dict[str, Any]]:
        """
        List all notebooks.
        
        Returns:
            List[Dict[str, Any]]: List of notebook data.
        """
        conn = DatabaseManager.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM notebooks ORDER BY updated_at DESC")
        notebooks = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return notebooks
    
    @staticmethod
    def update_notebook(name: str) -> bool:
        """
        Update a notebook's updated_at timestamp.
        
        Args:
            name: Name of the notebook.
            
        Returns:
            bool: True if successful, False if notebook not found.
        """
        conn = DatabaseManager.get_db_connection()
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        cursor.execute(
            "UPDATE notebooks SET updated_at = ? WHERE name = ?",
            (now, name)
        )
        
        if cursor.rowcount > 0:
            conn.commit()
            conn.close()
            return True
        else:
            conn.close()
            return False
    
    @staticmethod
    def delete_notebook(name: str) -> bool:
        """
        Delete a notebook.
        
        Args:
            name: Name of the notebook.
            
        Returns:
            bool: True if successful, False if notebook not found.
        """
        conn = DatabaseManager.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM notebooks WHERE name = ?", (name,))
        
        if cursor.rowcount > 0:
            conn.commit()
            conn.close()
            return True
        else:
            conn.close()
            return False
    
    @staticmethod
    def add_file(notebook_name: str, original_filename: str, stored_filename: str) -> bool:
        """
        Add a file to a notebook.
        
        Args:
            notebook_name: Name of the notebook.
            original_filename: Original filename.
            stored_filename: Stored filename.
            
        Returns:
            bool: True if successful, False otherwise.
            
        Raises:
            ValueError: If the notebook does not exist.
        """
        # Get notebook ID
        notebook = DatabaseManager.get_notebook_by_name(notebook_name)
        if not notebook:
            raise ValueError(f"Notebook '{notebook_name}' does not exist.")
        
        conn = DatabaseManager.get_db_connection()
        cursor = conn.cursor()
        
        try:
            now = datetime.now().isoformat()
            cursor.execute(
                "INSERT INTO files (notebook_id, original_filename, stored_filename, upload_date, is_processed) VALUES (?, ?, ?, ?, ?)",
                (notebook["id"], original_filename, stored_filename, now, False)
            )
            conn.commit()
            
            # Update notebook's updated_at timestamp
            DatabaseManager.update_notebook(notebook_name)
            
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    @staticmethod
    def get_files_by_notebook(notebook_name: str) -> List[Dict[str, Any]]:
        """
        Get all files for a notebook.
        
        Args:
            notebook_name: Name of the notebook.
            
        Returns:
            List[Dict[str, Any]]: List of file data.
            
        Raises:
            ValueError: If the notebook does not exist.
        """
        # Get notebook ID
        notebook = DatabaseManager.get_notebook_by_name(notebook_name)
        if not notebook:
            raise ValueError(f"Notebook '{notebook_name}' does not exist.")
        
        conn = DatabaseManager.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM files WHERE notebook_id = ? ORDER BY upload_date DESC",
            (notebook["id"],)
        )
        files = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return files
    
    @staticmethod
    def get_unprocessed_files(notebook_name: str) -> List[Dict[str, Any]]:
        """
        Get all unprocessed files for a notebook.
        
        Args:
            notebook_name: Name of the notebook.
            
        Returns:
            List[Dict[str, Any]]: List of unprocessed file data.
            
        Raises:
            ValueError: If the notebook does not exist.
        """
        # Get notebook ID
        notebook = DatabaseManager.get_notebook_by_name(notebook_name)
        if not notebook:
            raise ValueError(f"Notebook '{notebook_name}' does not exist.")
        
        conn = DatabaseManager.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM files WHERE notebook_id = ? AND is_processed = 0 ORDER BY upload_date DESC",
            (notebook["id"],)
        )
        files = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return files
    
    @staticmethod
    def mark_file_as_processed(file_id: int) -> bool:
        """
        Mark a file as processed.
        
        Args:
            file_id: ID of the file.
            
        Returns:
            bool: True if successful, False if file not found.
        """
        conn = DatabaseManager.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE files SET is_processed = 1 WHERE id = ?",
            (file_id,)
        )
        
        if cursor.rowcount > 0:
            conn.commit()
            conn.close()
            return True
        else:
            conn.close()
            return False
