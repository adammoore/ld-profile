"""
Optional database helper for storing profiles in a database instead of session state.
To use this, uncomment the relevant sections in app.py and install the required packages:
pip install sqlalchemy pymysql cryptography
"""

import json
import datetime
import sqlalchemy as sa
from sqlalchemy import create_engine, Column, String, LargeBinary, DateTime, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from cryptography.fernet import Fernet

# Create database connection
# Replace with your own database URL
DATABASE_URL = "sqlite:///./profiles.db"  # For production, use MySQL/PostgreSQL
engine = create_engine(DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)

# Define the Profile model
class Profile(Base):
    __tablename__ = "profiles"
    
    profile_id = Column(String(36), primary_key=True)
    encrypted_data = Column(LargeBinary, nullable=False)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f"<Profile {self.profile_id}>"

# Create tables
Base.metadata.create_all(engine)

class DatabaseHelper:
    def __init__(self, encryption_key=None):
        """Initialize database helper with encryption key"""
        self.session = Session()
        if encryption_key is None:
            self.encryption_key = Fernet.generate_key()
        else:
            self.encryption_key = encryption_key
        self.cipher_suite = Fernet(self.encryption_key)
    
    def encrypt_data(self, data):
        """Encrypt profile data"""
        return self.cipher_suite.encrypt(json.dumps(data).encode())
    
    def decrypt_data(self, encrypted_data):
        """Decrypt profile data"""
        return json.loads(self.cipher_suite.decrypt(encrypted_data).decode())
    
    def save_profile(self, profile_data):
        """Save profile to database"""
        profile_id = profile_data.get('profile_id')
        encrypted_data = self.encrypt_data(profile_data)
        
        # Check if profile exists
        existing_profile = self.session.query(Profile).filter_by(profile_id=profile_id).first()
        
        if existing_profile:
            # Update existing profile
            existing_profile.encrypted_data = encrypted_data
            existing_profile.last_updated = datetime.datetime.utcnow()
        else:
            # Create new profile
            new_profile = Profile(
                profile_id=profile_id,
                encrypted_data=encrypted_data
            )
            self.session.add(new_profile)
            
        self.session.commit()
        return profile_id
    
    def load_profile(self, profile_id):
        """Load profile from database"""
        profile = self.session.query(Profile).filter_by(profile_id=profile_id).first()
        if not profile:
            return None
        
        return self.decrypt_data(profile.encrypted_data)
    
    def delete_profile(self, profile_id):
        """Delete profile from database"""
        profile = self.session.query(Profile).filter_by(profile_id=profile_id).first()
        if profile:
            self.session.delete(profile)
            self.session.commit()
            return True
        return False
    
    def get_all_profiles(self):
        """Get all profiles from database"""
        profiles = {}
        for profile in self.session.query(Profile).all():
            profile_data = self.decrypt_data(profile.encrypted_data)
            profiles[profile.profile_id] = profile_data
        
        return profiles
    
    def close(self):
        """Close database session"""
        self.session.close()

# Usage example:
# db = DatabaseHelper()
# profile_id = db.save_profile(profile_data)
# profile = db.load_profile(profile_id)
# db.close()
