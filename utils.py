"""
Utility functions for the Learning Disability Profile application.

This module provides utility functions for file handling, data processing,
geolocation, map generation, and other helper functionality used across
the application.

Author: Adam Vials Moore
License: Apache License 2.0
"""

import os
import uuid
import datetime
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

import streamlit as st
from PIL import Image

from config import PROFILE_DATA_DIR, IMAGES_DIR, MAP_SEARCH_RADIUS_METERS

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
        
        # Contact information
        'emergency_contact_name': '',
        'emergency_contact_relationship': '',
        'emergency_contact_mobile': '',
        'emergency_contact_email': '',
        'emergency_contact': '',  # Legacy field
        
        # Physical description
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
        
        # Profile sections
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


def generate_short_summary(text: str, max_words: int = 15) -> str:
    """
    Generate a shorter summary of a longer text.
    
    Creates a concise version of longer text by extracting the first
    sentence or the first N words, suitable for display in posters
    or summary views.
    
    Args:
        text: The original text to summarize
        max_words: Maximum number of words in the summary
        
    Returns:
        A shorter version of the original text
    """
    if not text:
        return ""
    
    # Simple summarization: take the first sentence or first N words
    sentences = text.split('.')
    first_sentence = sentences[0].strip()
    
    words = first_sentence.split()
    if len(words) <= max_words:
        return first_sentence
    
    # Take the first max_words words and add ellipsis
    short_summary = ' '.join(words[:max_words]) + '...'
    return short_summary


def extract_coordinates(location_text: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Extract coordinates from location text if present.
    
    Parses location text to find latitude and longitude coordinates,
    typically in the format "... (Coordinates: 51.5074, -0.1278)".
    
    Args:
        location_text: Location description that may contain coordinates
        
    Returns:
        Tuple of (latitude, longitude) or (None, None) if not found
    """
    if not location_text:
        return None, None
    
    # Check for coordinates in format (Coordinates: 51.5074, -0.1278)
    if "coordinates:" in location_text.lower():
        try:
            # Extract the part after "Coordinates:"
            coords_part = location_text.lower().split("coordinates:")[1].strip()
            # Remove closing parenthesis if present
            if coords_part.endswith(')'):
                coords_part = coords_part[:-1]
            # Split by comma
            lat_str, lng_str = coords_part.split(',')
            return float(lat_str.strip()), float(lng_str.strip())
        except Exception as e:
            logger.error(f"Error extracting coordinates from '{location_text}': {str(e)}")
    
    return None, None


def geocode_location(location_text: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Geocode a location string to get coordinates.
    
    First attempts to extract coordinates from the text if present,
    then falls back to geocoding the location description using
    the Nominatim geocoding service.
    
    Args:
        location_text: Location description to geocode
        
    Returns:
        Tuple of (latitude, longitude) or (None, None) if geocoding fails
    """
    try:
        # First try to extract coordinates if they're already in the text
        lat, lng = extract_coordinates(location_text)
        if lat is not None and lng is not None:
            return lat, lng
        
        # Otherwise, try to geocode the location
        try:
            from geopy.geocoders import Nominatim
            from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
            
            geolocator = Nominatim(user_agent="learning_disability_profile_app")
            
            # Clean the location text - remove any coordinate parts
            if "coordinates:" in location_text.lower():
                clean_location = location_text.lower().split("coordinates:")[0].strip()
                # Remove trailing parenthesis if any
                if clean_location.endswith('('):
                    clean_location = clean_location[:-1].strip()
            else:
                clean_location = location_text
            
            # If the clean location is empty, return None
            if not clean_location:
                return None, None
            
            # Try to geocode
            location = geolocator.geocode(clean_location)
            if location:
                return location.latitude, location.longitude
        except ImportError:
            logger.warning("Geopy not installed, cannot geocode location")
        except (GeocoderTimedOut, GeocoderUnavailable) as e:
            logger.warning(f"Geocoding service timed out or unavailable: {str(e)}")
        except Exception as e:
            logger.error(f"Error geocoding location '{location_text}': {str(e)}")
    except Exception as e:
        logger.error(f"Error geocoding: {str(e)}")
    
    return None, None


def generate_location_map(location_text: str, width: int = 800, height: int = 500) -> Optional[str]:
    """
    Generate an HTML map for a location.
    
    Creates an interactive Folium map centered on the given location,
    with a marker and a search radius circle, and returns the HTML
    representation for embedding in a web page.
    
    Args:
        location_text: Location description to map
        width: Width of the map in pixels
        height: Height of the map in pixels
        
    Returns:
        HTML string for the map, or None if mapping fails
    """
    try:
        # Try to import folium for map generation
        try:
            import folium
        except ImportError:
            logger.warning("Folium not installed, cannot generate map")
            return None
