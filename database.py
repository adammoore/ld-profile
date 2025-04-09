"""
Database functionality for the Learning Disability Profile application.

This module provides classes and functions for interacting with the database,
including connection management, CRUD operations, and data encryption.
"""

import json
import datetime
import logging
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

import sqlalchemy as sa
from sqlalchemy import create_engine, Column, String, LargeBinary, DateTime, MetaData, Table, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from cryptography.fernet import Fernet

import streamlit as st
from config import DATABASE_URL, DATA_DIR

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create base class for SQLAlchemy models
Base = declarative_base()

class Profile(Base):
    """SQLAlchemy model for storing profile data."""
    
    __tablename__ = "profiles"
    
    profile_id = Column(String(36), primary_key=True)
    encrypted_data = Column(LargeBinary, nullable=False)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f"<Profile {self.profile_id}>"


class DatabaseManager:
    """
    Manages database operations and encryption for profile data.
    
    This class provides methods for managing database connections,
    CRUD operations on profiles, and encryption of sensitive data.
    """
    
    def __init__(self, database_url: str = DATABASE_URL, encryption_key: Optional[bytes] = None):
        """
        Initialize the database manager.
        
        Args:
            database_url: The SQLAlchemy database URL
            encryption_key: Optional encryption key. If not provided, a new one is generated
        """
        self.database_url = database_url
        self._engine = None
        self._session_factory = None
        
        # Set up encryption
        if encryption_key is None:
            # Generate a new key
            self.encryption_key = Fernet.generate_key()
        else:
            self.encryption_key = encryption_key
            
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Initialize database
        self._initialize_database()
        
    def _initialize_database(self) -> None:
        """Initialize the database connection and create tables if they don't exist."""
        try:
            # Create SQLite directory if it doesn't exist
            if self.database_url.startswith('sqlite'):
                db_path = Path(self.database_url.replace('sqlite:///', ''))
                db_dir = db_path.parent
                db_dir.mkdir(exist_ok=True)
            
            # Create engine and session factory
            self._engine = create_engine(self.database_url)
            self._session_factory = sessionmaker(bind=self._engine)
            
            # Create tables if they don't exist
            Base.metadata.create_all(self._engine)
            
            logger.info(f"Database initialized successfully at {self.database_url}")
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise
    
    def get_session(self) -> Session:
        """
        Get a database session.
        
        Returns:
            A SQLAlchemy session object
        """
        if self._session_factory is None:
            self._initialize_database()
        return self._session_factory()
    
    def encrypt_data(self, data: Dict[str, Any]) -> bytes:
        """
        Encrypt profile data.
        
        Args:
            data: Dictionary containing profile data
            
        Returns:
            Encrypted data as bytes
        """
        return self.cipher_suite.encrypt(json.dumps(data).encode())
    
    def decrypt_data(self, encrypted_data: bytes) -> Dict[str, Any]:
        """
        Decrypt profile data.
        
        Args:
            encrypted_data: Encrypted data as bytes
            
        Returns:
            Dictionary containing decrypted profile data
        """
        return json.loads(self.cipher_suite.decrypt(encrypted_data).decode())
    
    def save_profile(self, profile_data: Dict[str, Any]) -> str:
        """
        Save a profile to the database.
        
        Args:
            profile_data: Dictionary containing profile data
            
        Returns:
            Profile ID
        """
        profile_id = profile_data.get('profile_id')
        encrypted_data = self.encrypt_data(profile_data)
        
        session = self.get_session()
        try:
            # Check if profile exists
            existing_profile = session.query(Profile).filter_by(profile_id=profile_id).first()
            
            if existing_profile:
                # Update existing profile
                existing_profile.encrypted_data = encrypted_data
                existing_profile.last_updated = datetime.datetime.utcnow()
                logger.info(f"Updated profile {profile_id}")
            else:
                # Create new profile
                new_profile = Profile(
                    profile_id=profile_id,
                    encrypted_data=encrypted_data
                )
                session.add(new_profile)
                logger.info(f"Created new profile {profile_id}")
                
            session.commit()
            return profile_id
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving profile: {str(e)}")
            raise
        finally:
            session.close()
    
    def load_profile(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """
        Load a profile from the database.
        
        Args:
            profile_id: ID of the profile to load
            
        Returns:
            Dictionary containing profile data, or None if not found
        """
        session = self.get_session()
        try:
            profile = session.query(Profile).filter_by(profile_id=profile_id).first()
            if not profile:
                logger.warning(f"Profile {profile_id} not found")
                return None
            
            logger.info(f"Loaded profile {profile_id}")
            return self.decrypt_data(profile.encrypted_data)
        except Exception as e:
            logger.error(f"Error loading profile {profile_id}: {str(e)}")
            return None
        finally:
            session.close()
    
    def delete_profile(self, profile_id: str) -> bool:
        """
        Delete a profile from the database.
        
        Args:
            profile_id: ID of the profile to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        session = self.get_session()
        try:
            profile = session.query(Profile).filter_by(profile_id=profile_id).first()
            if profile:
                session.delete(profile)
                session.commit()
                logger.info(f"Deleted profile {profile_id}")
                return True
            logger.warning(f"Attempted to delete non-existent profile {profile_id}")
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Error deleting profile {profile_id}: {str(e)}")
            return False
        finally:
            session.close()
    
    def get_all_profiles(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all profiles from the database.
        
        Returns:
            Dictionary mapping profile IDs to profile data
        """
        session = self.get_session()
        try:
            profiles = {}
            for profile in session.query(Profile).all():
                profile_data = self.decrypt_data(profile.encrypted_data)
                profiles[profile.profile_id] = profile_data
            
            logger.info(f"Loaded {len(profiles)} profiles")
            return profiles
        except Exception as e:
            logger.error(f"Error getting all profiles: {str(e)}")
            return {}
        finally:
            session.close()
    
    def test_connection(self) -> bool:
        """
        Test the database connection.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            inspector = inspect(self._engine)
            # Check if the profiles table exists
            tables = inspector.get_table_names()
            logger.info(f"Database connection test successful. Tables: {tables}")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {str(e)}")
            return False
    
    def close(self) -> None:
        """Close the database connection."""
        if self._engine:
            self._engine.dispose()
            logger.info("Database connection closed")


# Initialize database manager
def get_database_manager() -> DatabaseManager:
    """
    Get or create the database manager instance.
    
    Returns:
        DatabaseManager instance
    """
    # Use the existing manager if it exists in session state
    if 'db_manager' not in st.session_state:
        # Get or create encryption key
        if 'encryption_key' not in st.session_state:
            st.session_state.encryption_key = Fernet.generate_key()
        
        # Create new manager
        st.session_state.db_manager = DatabaseManager(
            database_url=DATABASE_URL,
            encryption_key=st.session_state.encryption_key
        )
    
    return st.session_state.db_manager
