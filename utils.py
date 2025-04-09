"""
Utility functions for the Learning Disability Profile application.

This module provides utility functions for file handling, data processing,
and other helper functionality used across the application.
"""

import os
import uuid
import datetime
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

import streamlit as st
from PIL import Image

from config import PROFILE_DATA_DIR, IMAGES_DIR

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def save_uploaded_image(uploaded_file, profile_id: str, image_type: str) -> Optional[str]:
    """
    Save an uploaded image file and return the file path.
    
    Args:
        uploaded_file: The StreamlitUploadedFile object
        profile_id: The ID of the profile this image belongs to
        image_type: Type of image (profile, additional)
        
    Returns:
        Path to the saved image, or None if upload failed
    """
    if uploaded_file is None:
        return None
        
    try:
        # Create directory for this profile if it doesn't exist
        profile_image_dir = IMAGES_DIR / profile_id
        profile_image_dir.mkdir(exist_ok=True, parents=True)
        
        # Generate unique filename
        file_extension = Path(uploaded_file.name).suffix.lower()
        filename = f"{image_type}_{uuid.uuid4()}{file_extension}"
        filepath = profile_image_dir / filename
        
        # Save the file
        with open(filepath, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        logger.info(f"Saved image {filename} for profile {profile_id}")
        return str(filepath)
    except Exception as e:
        logger.error(f"Error saving image: {str(e)}")
        return None

def get_image_dimensions(image_path: str) -> Tuple[int, int]:
    """
    Get the dimensions of an image.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Tuple of (width, height) in pixels
    """
    try:
        with Image.open(image_path) as img:
            return img.size
    except Exception as e:
        logger.error(f"Error getting image dimensions: {str(e)}")
        return (0, 0)

def calculate_age(dob: datetime.date) -> int:
    """
    Calculate age from date of birth.
    
    Args:
        dob: Date of birth
        
    Returns:
        Age in years
    """
    today = datetime.date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

def format_height(height_cm: int) -> str:
    """
    Format height in cm to a display string with imperial conversion.
    
    Args:
        height_cm: Height in centimeters
        
    Returns:
        Formatted string with cm and ft/in
    """
    feet = height_cm // 30.48
    inches = round((height_cm % 30.48) / 2.54)
    
    # Handle the case where inches is 12 (should be 1 foot, 0 inches)
    if inches == 12:
        feet += 1
        inches = 0
        
    return f"{height_cm} cm ({int(feet)}' {inches}\")"

def format_weight(weight_kg: int) -> str:
    """
    Format weight in kg to a display string with imperial conversion.
    
    Args:
        weight_kg: Weight in kilograms
        
    Returns:
        Formatted string with kg and lbs
    """
    pounds = round(weight_kg * 2.2046)
    return f"{weight_kg} kg ({pounds} lbs)"

def sanitize_filename(name: str) -> str:
    """
    Convert a string to a safe filename.
    
    Args:
        name: Original string
        
    Returns:
        Safe filename string
    """
    # Replace spaces with underscores and remove other invalid characters
    return "".join(c if c.isalnum() or c in ['-', '_'] else '_' for c in name.replace(' ', '_'))

def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> List[str]:
    """
    Validate that required fields are present and not empty.
    
    Args:
        data: Dictionary of form data
        required_fields: List of field names that are required
        
    Returns:
        List of missing field names, empty if all required fields are present
    """
    missing = []
    for field in required_fields:
        if field not in data or not data[field]:
            missing.append(field)
    return missing

def get_profile_for_display(profile_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepare profile data for display, ensuring all expected fields are present.
    
    Args:
        profile_data: Raw profile data
        
    Returns:
        Profile data with defaults for missing fields
    """
    # Add default values for any missing fields to avoid errors in the UI
    defaults = {
        'name': 'Unknown',
        'dob': '',
        'age': '',
        'nhs_number': '',
        'emergency_contact': '',
        'height': '',
        'height_cm': 170,
        'weight': '',
        'weight_kg': 70,
        'build': '',
        'hair': '',
        'hair_color': '',
        'hair_style': '',
        'eyes': '',
        'eye_color': '',
        'distinguishing_features': '',
        'important_to_me': '',
        'how_to_support': '',
        'communication': '',
        'medical_info': '',
        'places_might_go': '',
        'travel_routines': '',
        'profile_image': '',
        'additional_images': []
    }
    
    # Create a new dict with defaults and override with actual values
    display_data = {**defaults, **profile_data}
    return display_data

def cleanup_old_files(max_age_days: int = 30) -> int:
    """
    Clean up temporary files older than specified age.
    
    Args:
        max_age_days: Maximum age in days for files to keep
        
    Returns:
        Number of files deleted
    """
    cutoff_time = datetime.datetime.now() - datetime.timedelta(days=max_age_days)
    count = 0
    
    try:
        # Walk through the profile data directory
        for root, dirs, files in os.walk(PROFILE_DATA_DIR):
            for file in files:
                file_path = os.path.join(root, file)
                file_modified = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                
                # Delete if older than cutoff
                if file_modified < cutoff_time:
                    os.remove(file_path)
                    count += 1
                    logger.info(f"Deleted old file: {file_path}")
    except Exception as e:
        logger.error(f"Error cleaning up old files: {str(e)}")
    
    return count
