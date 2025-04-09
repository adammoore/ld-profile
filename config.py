"""
Configuration settings for the Learning Disability Profile application.

This module contains configuration variables used throughout the application,
including database settings, file paths, and application constants.
"""

import os
import streamlit as st
from pathlib import Path

# Application information
APP_NAME = "Learning Disability Profile Creator"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Adam Vials Moore"
APP_LICENSE = "Apache License 2.0"
APP_FOOTER = f"© 2025 {APP_NAME} | GDPR Compliant | Apache License 2.0"

# Database settings
DB_TYPE = "sqlite"  # Options: sqlite, mysql, postgresql
DB_NAME = "profiles.db"
DB_PATH = Path("./data") / DB_NAME

# Construct database URL based on DB_TYPE
if DB_TYPE == "sqlite":
    DATABASE_URL = f"sqlite:///{DB_PATH}"
else:
    # For MySQL or PostgreSQL, you would need to set these environment variables
    # or use st.secrets in production
    DB_USER = os.environ.get("DB_USER", "")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PORT = os.environ.get("DB_PORT", "3306" if DB_TYPE == "mysql" else "5432")
    
    if DB_TYPE == "mysql":
        DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    elif DB_TYPE == "postgresql":
        DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# File storage paths
DATA_DIR = Path("./data")
PROFILE_DATA_DIR = DATA_DIR / "profile_data"
IMAGES_DIR = PROFILE_DATA_DIR / "images"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
PROFILE_DATA_DIR.mkdir(exist_ok=True)
IMAGES_DIR.mkdir(exist_ok=True)

# Form field options (for dropdown menus)
BUILD_OPTIONS = ["Slim", "Average", "Athletic", "Heavy", "Other"]
HAIR_COLOR_OPTIONS = ["Black", "Brown", "Blonde", "Red", "Grey", "White", "Other"]
EYE_COLOR_OPTIONS = ["Brown", "Blue", "Green", "Hazel", "Grey", "Other"]

# Physical attribute ranges
HEIGHT_MIN_CM = 30
HEIGHT_MAX_CM = 250
HEIGHT_DEFAULT_CM = 170

WEIGHT_MIN_KG = 1
WEIGHT_MAX_KG = 250
WEIGHT_DEFAULT_KG = 70

# Define page icons and colors (for UI consistency)
ICONS = {
    "profile": "👤",
    "missing": "🔍",
    "documents": "📄",
    "settings": "⚙️",
    "warning": "⚠️",
    "success": "✅",
    "error": "❌",
    "info": "ℹ️",
    "database": "💾",
}

# PDF generation settings
PDF_PAGE_SIZE = (595.27, 841.89)  # A4 in points
PDF_MARGIN = 72  # 1 inch margin in points
