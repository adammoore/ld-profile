"""
Document generator UI component for the Learning Disability Profile application.

This module contains the UI for generating documents from profiles.
"""

import os
import datetime
import streamlit as st
from typing import Dict, Any

from config import ICONS
from pdf_generator import create_profile_pdf, create_missing_person_poster
from utils import sanitize_filename
from database import get_database_manager


def render_document_generator() -> None:
    """Render the document generation UI."""
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
    
    st.write("## Document Generation")
    st.write(f"Generate documents for: **{profile_data.get('name', '')}**")
    
    # Show a preview of the profile
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
    
    # Generate one-page profile section
    st.write("### One-Page Profile")
    st.write("This document contains comprehensive information about the person to help others understand and support them.")
    
    generate_profile_button = st.button(
        f"{ICONS['documents']} Generate One-Page Profile", 
        type="primary",
        key="generate_profile_button"
    )
    
    if generate_profile_button:
        try:
            # Create PDF
            with st.spinner("Generating profile PDF..."):
                pdf_buffer = create_profile_pdf(profile_data)
                pdf_buffer.seek(0)
            
            # Get current date for filename
            current_date = datetime.datetime.now().strftime("%Y-%m-%d")
            safe_name = sanitize_filename(profile_data.get('name', 'profile'))
            
            # Create download button
            st.success(f"{ICONS['success']} One-Page Profile generated successfully!")
            st.download_button(
                label=f"{ICONS['documents']} Download One-Page Profile PDF",
                data=pdf_buffer,
                file_name=f"{safe_name}_{current_date}_one_page_profile.pdf",
                mime="application/pdf",
                key="download_profile_button"
            )
        except Exception as e:
            st.error(f"{ICONS['error']} Error generating profile PDF: {str(e)}")
            st.write("Please try again or contact support if the problem persists.")
    
    # Generate missing person poster section
    st.write("### Missing Person Poster")
    st.write("This document can be used in an emergency if the person becomes missing.")
    
    # Check if missing person information is complete
    missing_info_complete = all([
        profile_data.get('last_seen_date'),
        profile_data.get('last_seen_location')
    ])
    
    if not missing_info_complete:
        st.warning(f"{ICONS['warning']} Missing person information is incomplete. Please update it in the 'Missing Person Information' section before generating a poster.")
    
    generate_poster_button = st.button(
        f"{ICONS['documents']} Generate Missing Person Poster", 
        disabled=not missing_info_complete, 
        type="primary",
        key="generate_poster_button"
    )
    
    if generate_poster_button:
        try:
            # Create poster
            with st.spinner("Generating missing person poster..."):
                poster_buffer = create_missing_person_poster(profile_data)
                poster_buffer.seek(0)
            
            # Get current date for filename
            current_date = datetime.datetime.now().strftime("%Y-%m-%d")
            safe_name = sanitize_filename(profile_data.get('name', 'profile'))
            
            # Create download button
            st.success(f"{ICONS['success']} Missing Person Poster generated successfully!")
            st.download_button(
                label=f"{ICONS['documents']} Download Missing Person Poster PDF",
                data=poster_buffer,
                file_name=f"{safe_name}_{current_date}_missing_person_poster.pdf",
                mime="application/pdf",
                key="download_poster_button"
            )
        except Exception as e:
            st.error(f"{ICONS['error']} Error generating missing person poster: {str(e)}")
            st.write("Please try again or contact support if the problem persists.")
    
    # Add instructions
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
