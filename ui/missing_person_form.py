"""
Missing person form UI component for the Learning Disability Profile application.

This module contains the UI for updating missing person information, including
last seen details, location information, additional photos, and key details
for emergency responders.

Author: Adam Vials Moore
License: Apache License 2.0
"""

import os
import datetime
import streamlit as st
from typing import Dict, Any, List, Optional, Tuple

from config import ICONS
from models import MISSING_PERSON_REQUIRED_FIELDS
from utils import save_uploaded_image, generate_short_summary
from database import get_database_manager

# Try to import the geolocation component
try:
    from streamlit_geolocation import streamlit_geolocation
    GEOLOCATION_AVAILABLE = True
except ImportError:
    GEOLOCATION_AVAILABLE = False


def render_missing_person_form() -> None:
    """
    Render the missing person information form.
    
    This function displays a form for entering missing person information,
    including:
    - When and where the person was last seen
    - What they were wearing
    - Current location (using geolocation if available)
    - Additional photos for identification
    - Short summaries of key information for posters
    
    The form includes validation and appropriate help text for each field.
    When submitted, the data is saved to the database.
    
    Returns:
        None
    """
    # Check if a profile is selected
    current_profile_id = st.session_state.get('current_profile_id')
    if not current_profile_id:
        st.warning(f"{ICONS['warning']} Please create or select a profile first")
        return
    
    # Load profile data
    db_manager = get_database_manager()
    try:
        profile_data = db_manager.load_profile(current_profile_id)
        if not profile_data:
            st.error(f"{ICONS['error']} Failed to load profile. It may have been deleted.")
            st.session_state.current_profile_id = None
            st.rerun()
            return
    except Exception as e:
        st.error(f"{ICONS['error']} Error loading profile: {str(e)}")
        return
    
    st.write("## Missing Person Information")
    st.write(f"Updating information for: **{profile_data.get('name', '')}**")
    
    # Show a preview of the profile
    with st.expander("View Profile Summary", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Name:** ", profile_data.get('name', 'Not specified'))
            st.write("**Age:** ", profile_data.get('age', 'Not specified'))
            st.write("**Height:** ", profile_data.get('height', 'Not specified'))
            st.write("**Build:** ", profile_data.get('build', 'Not specified'))
            st.write("**Hair:** ", profile_data.get('hair', 'Not specified'))
            st.write("**Eyes:** ", profile_data.get('eye_color', 'Not specified'))
        
        with col2:
            # Display profile image if available
            if profile_data.get('profile_image') and os.path.exists(profile_data.get('profile_image')):
                st.image(profile_data.get('profile_image'), width=150)
            else:
                st.write("No profile image available")
    
    # Create form for missing person data entry
    with st.form("missing_person_form"):
        # === WHEN AND WHERE LAST SEEN SECTION ===
        st.write("### When and Where Last Seen")
        st.write("This information is essential for finding the person")
        
        col1, col2 = st.columns(2)
        with col1:
            # Date last seen field with appropriate default
            last_seen_date = st.date_input(
                "Date Last Seen", 
                value=datetime.datetime.now() if not profile_data.get('last_seen_date') else 
                      datetime.datetime.strptime(profile_data.get('last_seen_date'), '%Y-%m-%d').date(),
                help="The date when the person was last seen"
            )
            
            # Time last seen field with appropriate default
            # Parse the time if it exists
            if profile_data.get('last_seen_time'):
                try:
                    time_parts = profile_data.get('last_seen_time').split(':')
                    default_time = datetime.time(int(time_parts[0]), int(time_parts[1]))
                except (ValueError, IndexError):
                    default_time = datetime.datetime.now().time()
            else:
                default_time = datetime.datetime.now().time()
            
            last_seen_time = st.time_input(
                "Time Last Seen", 
                value=default_time,
                help="The approximate time when the person was last seen"
            )
        
        with col2:
            # Clothing description field
            last_seen_wearing = st.text_area(
                "Clothing When Last Seen", 
                value=profile_data.get('last_seen_wearing', ''),
                help="Detailed description of what the person was wearing when last seen"
            )
            
            # Police reference number field
            reference_number = st.text_input(
                "Police Reference Number (if available)", 
                value=profile_data.get('reference_number', ''),
                help="Any reference number provided by police for the missing person case"
            )
        
        # === LOCATION INFORMATION SECTION ===
        st.write("### Location Information")
        
        # Geolocation widget if available
        location_lat, location_lng = None, None
        if GEOLOCATION_AVAILABLE:
            st.write("You can use your current location or enter a location manually.")
            
            location_col1, location_col2 = st.columns([1, 3])
            with location_col1:
                use_current_location = st.checkbox(
                    "Use my current location", 
                    value=False,
                    help="Use your browser's geolocation to get your current coordinates"
                )
            
            # Get location from browser if checkbox is checked
            if use_current_location:
                with location_col2:
                    try:
                        loc = streamlit_geolocation()
                        if loc and isinstance(loc, dict) and 'latitude' in loc and 'longitude' in loc:
                            location_lat = loc['latitude']
                            location_lng = loc['longitude']
                            if location_lat is not None and location_lng is not None:
                                st.success(f"Location detected: {location_lat:.6f}, {location_lng:.6f}")
                            else:
                                st.info("Waiting for location data...")
                        else:
                            st.info("Waiting for location permission...")
                    except Exception as e:
                        st.error(f"Error accessing geolocation: {str(e)}")
                        st.info("Please enter the location manually below.")
        else:
            # Show message if geolocation is not available
            st.info("Geolocation is not available. Please enter the location manually.")
        
        # Location text input field
        last_seen_location = st.text_input(
            "Location Last Seen", 
            value=profile_data.get('last_seen_location', ''),
            help="The address or detailed description of where the person was last seen"
        )
        
        # If we have coordinates from geolocation, append them to the location
        if location_lat and location_lng:
            if last_seen_location:
                last_seen_location += f" (Coordinates: {location_lat:.6f}, {location_lng:.6f})"
            else:
                last_seen_location = f"Coordinates: {location_lat:.6f}, {location_lng:.6f}"
        
        # === ADDITIONAL PHOTOS SECTION ===
        st.write("### Additional Photos")
        st.write("Upload additional recent photos that can help identify the person")
        
        additional_photos = st.file_uploader(
            "Upload additional photos", 
            type=["jpg", "jpeg", "png"], 
            accept_multiple_files=True,
            help="Recent photos showing different angles, hairstyles, or clothing"
        )
        
        # Display existing additional photos in a gallery
        existing_photos = profile_data.get('additional_images', [])
        if existing_photos:
            st.write("Current additional photos:")
            
            # Create columns for the gallery
            num_cols = 3
            cols = st.columns(num_cols)
            
            # Display each photo in a column
            for i, photo_path in enumerate(existing_photos):
                if os.path.exists(photo_path):
                    with cols[i % num_cols]:
                        try:
                            st.image(photo_path, width=150)
                            st.caption(f"Photo {i+1}")
                        except Exception as e:
                            st.error(f"Error displaying photo: {str(e)}")
        
        # Display newly uploaded photos in a gallery
        if additional_photos:
            st.write("New photos to be added:")
            
            # Create columns for the gallery
            num_cols = 3
            cols = st.columns(num_cols)
            
            # Display each new photo in a column
            for i, photo in enumerate(additional_photos):
                with cols[i % num_cols]:
                    st.image(photo, width=150)
                    st.caption(f"New Photo {i+1}")
        
        # === SHORT SUMMARIES SECTION ===
        st.write("### Additional Information for Missing Person Poster")
        st.write("Please provide short, concise versions of key information for the poster (limit to 1-2 sentences)")
        
        # Generate short summaries from the full information if not already provided
        default_medical_short = profile_data.get('medical_info_short', '')
        if not default_medical_short and profile_data.get('medical_info'):
            default_medical_short = generate_short_summary(profile_data.get('medical_info', ''))
        
        default_communication_short = profile_data.get('communication_short', '')
        if not default_communication_short and profile_data.get('communication'):
            default_communication_short = generate_short_summary(profile_data.get('communication', ''))
        
        default_places_short = profile_data.get('places_might_go_short', '')
        if not default_places_short and profile_data.get('places_might_go'):
            default_places_short = generate_short_summary(profile_data.get('places_might_go', ''))
        
        # Display the short summary inputs with generated defaults
        medical_info_short = st.text_input(
            "Medical Information (short version)", 
            value=default_medical_short,
            help="Brief summary of critical medical needs that emergency responders should know"
        )
        
        communication_short = st.text_input(
            "Communication (short version)", 
            value=default_communication_short,
            help="Brief summary of how to communicate effectively with the person"
        )
        
        places_might_go_short = st.text_input(
            "Places They Might Go (short version)", 
            value=default_places_short,
            help="Brief list of the most likely locations to check first"
        )
        
        # Submit button
        submit_button = st.form_submit_button(
            "Update Missing Person Information", 
            type="primary",
            help="Save the missing person information"
        )
    
    # Process form submission
    if submit_button:
        # Validate required fields
        missing_fields = []
        if not last_seen_date:
            missing_fields.append("Date Last Seen")
        if not last_seen_location:
            missing_fields.append("Location Last Seen")
        
        if missing_fields:
            st.error(f"{ICONS['error']} Please fill in the following required fields: {', '.join(missing_fields)}")
            return
        
        try:
            # Format the datetime for better display
            last_seen_datetime = f"{last_seen_date.strftime('%d %B %Y')} at {last_seen_time.strftime('%H:%M')}"
            
            # Update profile with missing person information
            profile_data['last_seen_date'] = last_seen_date.isoformat()
            profile_data['last_seen_time'] = last_seen_time.strftime('%H:%M')
            profile_data['last_seen_datetime'] = last_seen_datetime
            profile_data['last_seen_location'] = last_seen_location
            profile_data['last_seen_wearing'] = last_seen_wearing
            profile_data['reference_number'] = reference_number
            profile_data['medical_info_short'] = medical_info_short
            profile_data['communication_short'] = communication_short
            profile_data['places_might_go_short'] = places_might_go_short
            
            # Save additional photos
            if additional_photos:
                additional_image_paths = profile_data.get('additional_images', []) or []
                for photo in additional_photos:
                    image_path = save_uploaded_image(photo, profile_data['profile_id'], 'additional')
                    if image_path:
                        additional_image_paths.append(image_path)
                
                profile_data['additional_images'] = additional_image_paths
            
            # Save updated profile to the database
            db_manager = get_database_manager()
            db_manager.save_profile(profile_data)
            
            # Show success message
            st.success(f"{ICONS['success']} Missing person information updated successfully!")
            st.rerun()
        except Exception as e:
            # Handle any errors during saving
            st.error(f"{ICONS['error']} Error updating missing person information: {str(e)}")
