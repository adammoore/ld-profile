"""
Document generator UI component for the Learning Disability Profile application.

This module contains the UI for generating documents from profiles, including:
- One-page profiles for understanding and supporting the person
- Missing person posters with critical identification information
- Interactive maps of the last known location (when available)

The document generator provides preview capabilities and downloadable PDFs
that can be shared with caregivers, support workers, or emergency services.

Author: Adam Vials Moore
License: Apache License 2.0
"""

import os
import datetime
import streamlit as st
from typing import Dict, Any, Optional, Tuple

from config import ICONS, MAP_SEARCH_RADIUS_METERS, MAP_DEFAULT_ZOOM
from pdf_generator import create_profile_pdf, create_missing_person_poster
from utils import sanitize_filename, geocode_location, display_contact_info
from database import get_database_manager

# Try to import optional mapping libraries
try:
    from streamlit_folium import folium_static
    import folium
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False


def render_document_generator() -> None:
    """
    Render the document generation UI.
    
    This function displays the document generation interface, including:
    - Profile summary for reference
    - One-page profile generation button and download link
    - Missing person poster generation button and download link
    - Interactive map of last known location (when available)
    - Usage instructions for the generated documents
    
    The UI adapts based on the available data and installed dependencies.
    If mapping libraries are not available, the map features will be disabled
    but the rest of the functionality will continue to work.
    
    Returns:
        None
    """
    # Check if a profile is selected
    current_profile_id = st.session_state.get('current_profile_id')
    if not current_profile_id:
        st.warning(f"{ICONS['warning']} Please create or select a profile first")
        return
    
    # Load profile data from the database
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
    
    # Page title and header
    st.write("## Document Generation")
    st.write(f"Generate documents for: **{profile_data.get('name', '')}**")
    
    # === PROFILE SUMMARY SECTION ===
    # Show a preview of the profile information
    with st.expander("View Profile Summary", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.write("### Basic Information")
            st.write(f"**Name:** {profile_data.get('name', 'Not specified')}")
            st.write(f"**Date of Birth:** {profile_data.get('dob', 'Not specified')}")
            st.write(f"**Age:** {profile_data.get('age', 'Not specified')}")
            st.write(f"**NHS Number:** {profile_data.get('nhs_number', 'Not specified')}")
            
            # Display emergency contact information
            st.write("### Emergency Contact")
            contact_info = display_contact_info(profile_data)
            
            if any([contact_info['name'], contact_info['relationship'], 
                    contact_info['mobile'], contact_info['email']]):
                if contact_info['name']:
                    st.write(f"**Name:** {contact_info['name']}")
                if contact_info['relationship']:
                    st.write(f"**Relationship:** {contact_info['relationship']}")
                if contact_info['mobile']:
                    st.write(f"**Mobile:** {contact_info['mobile']}")
                if contact_info['email']:
                    st.write(f"**Email:** {contact_info['email']}")
            else:
                # Fallback to legacy field
                st.write(f"**Emergency Contact:** {profile_data.get('emergency_contact', 'Not specified')}")
            
            st.write("### Physical Description")
            st.write(f"**Height:** {profile_data.get('height', 'Not specified')}")
            st.write(f"**Weight:** {profile_data.get('weight', 'Not specified')}")
            st.write(f"**Build:** {profile_data.get('build', 'Not specified')}")
            st.write(f"**Hair:** {profile_data.get('hair', 'Not specified')}")
            st.write(f"**Eyes:** {profile_data.get('eye_color', 'Not specified')}")
            st.write(f"**Distinguishing Features:** {profile_data.get('distinguishing_features', 'None specified')}")
        
        with col2:
            # Display profile image if available
            if profile_data.get('profile_image') and os.path.exists(profile_data.get('profile_image')):
                st.image(profile_data.get('profile_image'), width=200)
                st.caption("Profile Photo")
            else:
                st.write("No profile image available")
            
            # If missing person info is available, show it
            if profile_data.get('last_seen_date'):
                st.write("### Missing Person Info")
                st.write(f"**Last Seen:** {profile_data.get('last_seen_datetime', 'Not specified')}")
                st.write(f"**Location:** {profile_data.get('last_seen_location', 'Not specified')}")
                st.write(f"**Wearing:** {profile_data.get('last_seen_wearing', 'Not specified')}")
    
    # === LOCATION MAP SECTION ===
    # Display map for the last seen location if available
    if profile_data.get('last_seen_location'):
        render_location_map(profile_data.get('last_seen_location', ''))
    
    # === ONE-PAGE PROFILE SECTION ===
    st.write("### One-Page Profile")
    st.write("This document contains comprehensive information about the person to help others understand and support them.")
    
    # Button to generate the profile PDF
    generate_profile_button = st.button(
        f"{ICONS['documents']} Generate One-Page Profile", 
        type="primary",
        key="generate_profile_button"
    )
    
    if generate_profile_button:
        generate_profile_document(profile_data)
    
    # === MISSING PERSON POSTER SECTION ===
    st.write("### Missing Person Poster")
    st.write("This document can be used in an emergency if the person becomes missing.")
    
    # Check if required missing person information is available
    missing_info_complete = all([
        profile_data.get('last_seen_date'),
        profile_data.get('last_seen_location')
    ])
    
    if not missing_info_complete:
        st.warning(f"{ICONS['warning']} Missing person information is incomplete. Please update it in the 'Missing Person Information' section before generating a poster.")
    
    # Button to generate the missing person poster
    generate_poster_button = st.button(
        f"{ICONS['documents']} Generate Missing Person Poster", 
        disabled=not missing_info_complete, 
        type="primary",
        key="generate_poster_button"
    )
    
    if generate_poster_button:
        generate_missing_person_document(profile_data)
    
    # === INSTRUCTIONS SECTION ===
    # Show usage instructions in an expandable section
    with st.expander("How to use these documents"):
        st.write("""
        #### One-Page Profile
        The one-page profile should be shared with people who support the individual. It helps them understand:
        - What's important to the person
        - How best to support them
        - How they communicate
        
        #### Missing Person Poster
        If the person goes missing:
        1. Call the police immediately (101 or 999 in an emergency)
        2. Generate and download the missing person poster
        3. Share the poster with local community, businesses, and on social media
        4. Provide the police with the one-page profile for more detailed information
        """)


def render_location_map(location_text: str) -> None:
    """
    Render an interactive map for a given location.
    
    This function attempts to display an interactive map of the location where 
    the person was last seen. It includes:
    - A marker at the exact location
    - A circle showing a 200m radius search area
    - A link to open the location in Google Maps
    - Detailed location information in an expandable section
    
    The map will only be displayed if:
    1. The folium and streamlit-folium libraries are installed
    2. The location text can be geocoded to valid coordinates
    
    If either condition fails, appropriate messages are displayed.
    
    Args:
        location_text: The textual description of the location
        
    Returns:
        None
    """
    st.write("### Last Seen Location")
    
    # Only attempt to show a map if the mapping libraries are available
    if FOLIUM_AVAILABLE:
        try:
            # Get coordinates for the location
            lat, lng = geocode_location(location_text)
            
            # If coordinates were found, create and display the map
            if lat is not None and lng is not None:
                # Create a folium map centered at the coordinates
                m = folium.Map(location=[lat, lng], zoom_start=MAP_DEFAULT_ZOOM)
                
                # Add a marker at the exact location
                folium.Marker(
                    [lat, lng],
                    popup=location_text,
                    tooltip="Last seen here",
                    icon=folium.Icon(color="red", icon="info-sign")
                ).add_to(m)
                
                # Add a circle to indicate approximate search area
                folium.Circle(
                    radius=MAP_SEARCH_RADIUS_METERS,
                    location=[lat, lng],
                    color="red",
                    fill=True,
                    fill_color="red",
                    fill_opacity=0.1
                ).add_to(m)
                
                # Display the map using streamlit-folium
                st.write("Interactive map of the last seen location:")
                folium_static(m, width=700, height=400)
                
                # Add a link to open the location in Google Maps
                google_maps_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lng}"
                st.markdown(f"[Open in Google Maps]({google_maps_url})")
                
                # Show additional location details in an expandable section
                with st.expander("Location Details"):
                    st.write(f"**Address:** {location_text}")
                    st.write(f"**Coordinates:** {lat:.6f}, {lng:.6f}")
                    st.write(f"**Search Radius:** {MAP_SEARCH_RADIUS_METERS} meters (indicated by red circle)")
                    
                    # Add copyable coordinate text
                    coord_str = f"{lat:.6f}, {lng:.6f}"
                    st.code(coord_str, language=None)
                    st.info("Click above to copy coordinates")
            else:
                # If geocoding failed, show an informative message
                st.info(f"Could not generate map for location: {location_text}")
                st.write("Try entering a more specific location or adding more details like city and postal code.")
        except Exception as e:
            # Handle any exceptions that occur during map generation
            st.error(f"Error generating map: {str(e)}")
            st.write("Please check that the location text is valid and try again.")
    else:
        # If mapping libraries aren't available, show installation instructions
        st.info("Map display is not available. Install streamlit-folium to see a map of the last known location.")


def generate_profile_document(profile_data: Dict[str, Any]) -> None:
    """
    Generate a one-page profile PDF document.
    
    This function creates a comprehensive one-page profile PDF that includes:
    - Basic personal information
    - Physical description
    - What's important to the person
    - How best to support them
    - Communication preferences and methods
    
    If generation is successful, a download button is displayed.
    If an error occurs, an error message is shown.
    
    Args:
        profile_data: Dictionary containing the person's profile information
        
    Returns:
        None
    """
    try:
        # Create the PDF with a loading spinner
        with st.spinner("Generating profile PDF..."):
            pdf_buffer = create_profile_pdf(profile_data)
            pdf_buffer.seek(0)  # Reset buffer position to beginning
        
        # Prepare filename with date and sanitized name
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        safe_name = sanitize_filename(profile_data.get('name', 'profile'))
        filename = f"{safe_name}_{current_date}_one_page_profile.pdf"
        
        # Show success message and download button
        st.success(f"{ICONS['success']} One-Page Profile generated successfully!")
        st.download_button(
            label=f"{ICONS['documents']} Download One-Page Profile PDF",
            data=pdf_buffer,
            file_name=filename,
            mime="application/pdf",
            key="download_profile_button"
        )
    except Exception as e:
        # Handle any errors during generation
        st.error(f"{ICONS['error']} Error generating profile PDF: {str(e)}")
        st.write("Please try again or contact support if the problem persists.")


def generate_missing_person_document(profile_data: Dict[str, Any]) -> None:
    """
    Generate a missing person poster PDF document.
    
    This function creates a missing person poster PDF that includes:
    - The person's photo and physical description
    - When and where they were last seen
    - A map of the last known location (if coordinates are available)
    - Important information about medical needs and communication
    - Contact information for reporting sightings
    
    If generation is successful, a download button is displayed.
    If an error occurs, an error message is shown.
    
    Args:
        profile_data: Dictionary containing the person's profile information
        
    Returns:
        None
    """
    try:
        # Create the poster with a loading spinner
        with st.spinner("Generating missing person poster..."):
            poster_buffer = create_missing_person_poster(profile_data)
            poster_buffer.seek(0)  # Reset buffer position to beginning
        
        # Prepare filename with date and sanitized name
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        safe_name = sanitize_filename(profile_data.get('name', 'profile'))
        filename = f"{safe_name}_{current_date}_missing_person_poster.pdf"
        
        # Show success message and download button
        st.success(f"{ICONS['success']} Missing Person Poster generated successfully!")
        st.download_button(
            label=f"{ICONS['documents']} Download Missing Person Poster PDF",
            data=poster_buffer,
            file_name=filename,
            mime="application/pdf",
            key="download_poster_button"
        )
    except Exception as e:
        # Handle any errors during generation
        st.error(f"{ICONS['error']} Error generating missing person poster: {str(e)}")
        st.write("Please try again or contact support if the problem persists.")
"""
Document generator UI component for the Learning Disability Profile application.

This module contains the UI for generating documents from profiles, including:
- One-page profiles for understanding and supporting the person
- Missing person posters with critical identification information
- Interactive maps of the last known location (when available)

The document generator provides preview capabilities and downloadable PDFs
that can be shared with caregivers, support workers, or emergency services.
"""

import os
import datetime
import streamlit as st
from typing import Dict, Any, Optional, Tuple

from config import ICONS
from pdf_generator import create_profile_pdf, create_missing_person_poster
from utils import sanitize_filename, geocode_location
from database import get_database_manager

# Try to import optional mapping libraries
try:
    from streamlit_folium import folium_static
    import folium
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False


def render_document_generator() -> None:
    """
    Render the document generation UI.
    
    This function displays the document generation interface, including:
    - Profile summary for reference
    - One-page profile generation button and download link
    - Missing person poster generation button and download link
    - Interactive map of last known location (when available)
    - Usage instructions for the generated documents
    
    The UI adapts based on the available data and installed dependencies.
    If mapping libraries are not available, the map features will be disabled
    but the rest of the functionality will continue to work.
    
    Returns:
        None
    """
    # Check if a profile is selected
    current_profile_id = st.session_state.get('current_profile_id')
    if not current_profile_id:
        st.warning(f"{ICONS['warning']} Please create or select a profile first")
        return
    
    # Load profile data from the database
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
    
    # Page title and header
    st.write("## Document Generation")
    st.write(f"Generate documents for: **{profile_data.get('name', '')}**")
    
    # === PROFILE SUMMARY SECTION ===
    # Show a preview of the profile information
    with st.expander("View Profile Summary", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.write("### Basic Information")
            st.write(f"**Name:** {profile_data.get('name', 'Not specified')}")
            st.write(f"**Date of Birth:** {profile_data.get('dob', 'Not specified')}")
            st.write(f"**Age:** {profile_data.get('age', 'Not specified')}")
            st.write(f"**NHS Number:** {profile_data.get('nhs_number', 'Not specified')}")
            st.write(f"**Emergency Contact:** {profile_data.get('emergency_contact', 'Not specified')}")
            
            st.write("### Physical Description")
            st.write(f"**Height:** {profile_data.get('height', 'Not specified')}")
            st.write(f"**Weight:** {profile_data.get('weight', 'Not specified')}")
            st.write(f"**Build:** {profile_data.get('build', 'Not specified')}")
            st.write(f"**Hair:** {profile_data.get('hair', 'Not specified')}")
            st.write(f"**Eyes:** {profile_data.get('eye_color', 'Not specified')}")
            st.write(f"**Distinguishing Features:** {profile_data.get('distinguishing_features', 'None specified')}")
        
        with col2:
            # Display profile image if available
            if profile_data.get('profile_image') and os.path.exists(profile_data.get('profile_image')):
                st.image(profile_data.get('profile_image'), width=200)
                st.caption("Profile Photo")
            else:
                st.write("No profile image available")
            
            # If missing person info is available, show it
            if profile_data.get('last_seen_date'):
                st.write("### Missing Person Info")
                st.write(f"**Last Seen:** {profile_data.get('last_seen_datetime', 'Not specified')}")
                st.write(f"**Location:** {profile_data.get('last_seen_location', 'Not specified')}")
                st.write(f"**Wearing:** {profile_data.get('last_seen_wearing', 'Not specified')}")
    
    # === LOCATION MAP SECTION ===
    # Display map for the last seen location if available
    if profile_data.get('last_seen_location'):
        render_location_map(profile_data.get('last_seen_location', ''))
    
    # === ONE-PAGE PROFILE SECTION ===
    st.write("### One-Page Profile")
    st.write("This document contains comprehensive information about the person to help others understand and support them.")
    
    # Button to generate the profile PDF
    generate_profile_button = st.button(
        f"{ICONS['documents']} Generate One-Page Profile", 
        type="primary",
        key="generate_profile_button"
    )
    
    if generate_profile_button:
        generate_profile_document(profile_data)
    
    # === MISSING PERSON POSTER SECTION ===
    st.write("### Missing Person Poster")
    st.write("This document can be used in an emergency if the person becomes missing.")
    
    # Check if required missing person information is available
    missing_info_complete = all([
        profile_data.get('last_seen_date'),
        profile_data.get('last_seen_location')
    ])
    
    if not missing_info_complete:
        st.warning(f"{ICONS['warning']} Missing person information is incomplete. Please update it in the 'Missing Person Information' section before generating a poster.")
    
    # Button to generate the missing person poster
    generate_poster_button = st.button(
        f"{ICONS['documents']} Generate Missing Person Poster", 
        disabled=not missing_info_complete, 
        type="primary",
        key="generate_poster_button"
    )
    
    if generate_poster_button:
        generate_missing_person_document(profile_data)
    
    # === INSTRUCTIONS SECTION ===
    # Show usage instructions in an expandable section
    with st.expander("How to use these documents"):
        st.write("""
        #### One-Page Profile
        The one-page profile should be shared with people who support the individual. It helps them understand:
        - What's important to the person
        - How best to support them
        - How they communicate
        
        #### Missing Person Poster
        If the person goes missing:
        1. Call the police immediately (101 or 999 in an emergency)
        2. Generate and download the missing person poster
        3. Share the poster with local community, businesses, and on social media
        4. Provide the police with the one-page profile for more detailed information
        """)


def render_location_map(location_text: str) -> None:
    """
    Render an interactive map for a given location.
    
    This function attempts to display an interactive map of the location where 
    the person was last seen. It includes:
    - A marker at the exact location
    - A circle showing a 200m radius search area
    - A link to open the location in Google Maps
    - Detailed location information in an expandable section
    
    The map will only be displayed if:
    1. The folium and streamlit-folium libraries are installed
    2. The location text can be geocoded to valid coordinates
    
    If either condition fails, appropriate messages are displayed.
    
    Args:
        location_text: The textual description of the location
        
    Returns:
        None
    """
    st.write("### Last Seen Location")
    
    # Only attempt to show a map if the mapping libraries are available
    if FOLIUM_AVAILABLE:
        try:
            # Get coordinates for the location
            lat, lng = geocode_location(location_text)
            
            # If coordinates were found, create and display the map
            if lat is not None and lng is not None:
                # Create a folium map centered at the coordinates
                m = folium.Map(location=[lat, lng], zoom_start=15)
                
                # Add a marker at the exact location
                folium.Marker(
                    [lat, lng],
                    popup=location_text,
                    tooltip="Last seen here",
                    icon=folium.Icon(color="red", icon="info-sign")
                ).add_to(m)
                
                # Add a circle to indicate approximate search area (200m radius)
                folium.Circle(
                    radius=200,
                    location=[lat, lng],
                    color="red",
                    fill=True,
                    fill_color="red",
                    fill_opacity=0.1
                ).add_to(m)
                
                # Display the map using streamlit-folium
                st.write("Interactive map of the last seen location:")
                folium_static(m, width=700, height=400)
                
                # Add a link to open the location in Google Maps
                google_maps_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lng}"
                st.markdown(f"[Open in Google Maps]({google_maps_url})")
                
                # Show additional location details in an expandable section
                with st.expander("Location Details"):
                    st.write(f"**Address:** {location_text}")
                    st.write(f"**Coordinates:** {lat:.6f}, {lng:.6f}")
                    st.write("**Search Radius:** 200 meters (indicated by red circle)")
                    
                    # Add copyable coordinate text
                    coord_str = f"{lat:.6f}, {lng:.6f}"
                    st.code(coord_str, language=None)
                    st.info("Click above to copy coordinates")
            else:
                # If geocoding failed, show an informative message
                st.info(f"Could not generate map for location: {location_text}")
                st.write("Try entering a more specific location or adding more details like city and postal code.")
        except Exception as e:
            # Handle any exceptions that occur during map generation
            st.error(f"Error generating map: {str(e)}")
            st.write("Please check that the location text is valid and try again.")
    else:
        # If mapping libraries aren't available, show installation instructions
        st.info("Map display is not available. Install streamlit-folium to see a map of the last known location.")


def generate_profile_document(profile_data: Dict[str, Any]) -> None:
    """
    Generate a one-page profile PDF document.
    
    This function creates a comprehensive one-page profile PDF that includes:
    - Basic personal information
    - Physical description
    - What's important to the person
    - How best to support them
    - Communication preferences and methods
    
    If generation is successful, a download button is displayed.
    If an error occurs, an error message is shown.
    
    Args:
        profile_data: Dictionary containing the person's profile information
        
    Returns:
        None
    """
    try:
        # Create the PDF with a loading spinner
        with st.spinner("Generating profile PDF..."):
            pdf_buffer = create_profile_pdf(profile_data)
            pdf_buffer.seek(0)  # Reset buffer position to beginning
        
        # Prepare filename with date and sanitized name
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        safe_name = sanitize_filename(profile_data.get('name', 'profile'))
        filename = f"{safe_name}_{current_date}_one_page_profile.pdf"
        
        # Show success message and download button
        st.success(f"{ICONS['success']} One-Page Profile generated successfully!")
        st.download_button(
            label=f"{ICONS['documents']} Download One-Page Profile PDF",
            data=pdf_buffer,
            file_name=filename,
            mime="application/pdf",
            key="download_profile_button"
        )
    except Exception as e:
        # Handle any errors during generation
        st.error(f"{ICONS['error']} Error generating profile PDF: {str(e)}")
        st.write("Please try again or contact support if the problem persists.")


def generate_missing_person_document(profile_data: Dict[str, Any]) -> None:
    """
    Generate a missing person poster PDF document.
    
    This function creates a missing person poster PDF that includes:
    - The person's photo and physical description
    - When and where they were last seen
    - A map of the last known location (if coordinates are available)
    - Important information about medical needs and communication
    - Contact information for reporting sightings
    
    If generation is successful, a download button is displayed.
    If an error occurs, an error message is shown.
    
    Args:
        profile_data: Dictionary containing the person's profile information
        
    Returns:
        None
    """
    try:
        # Create the poster with a loading spinner
        with st.spinner("Generating missing person poster..."):
            poster_buffer = create_missing_person_poster(profile_data)
            poster_buffer.seek(0)  # Reset buffer position to beginning
        
        # Prepare filename with date and sanitized name
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        safe_name = sanitize_filename(profile_data.get('name', 'profile'))
        filename = f"{safe_name}_{current_date}_missing_person_poster.pdf"
        
        # Show success message and download button
        st.success(f"{ICONS['success']} Missing Person Poster generated successfully!")
        st.download_button(
            label=f"{ICONS['documents']} Download Missing Person Poster PDF",
            data=poster_buffer,
            file_name=filename,
            mime="application/pdf",
            key="download_poster_button"
        )
    except Exception as e:
        # Handle any errors during generation
        st.error(f"{ICONS['error']} Error generating missing person poster: {str(e)}")
        st.write("Please try again or contact support if the problem persists.")
