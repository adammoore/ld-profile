"""
Sidebar UI component for the Learning Disability Profile application.

This module contains the sidebar navigation UI for the application.
"""

import streamlit as st
from typing import Dict, Any, List, Tuple

from config import ICONS
from database import get_database_manager

def render_sidebar() -> str:
    """
    Render the sidebar navigation and return the selected action.
    
    Returns:
        The selected navigation option
    """
    st.sidebar.title(f"{ICONS['profile']} Navigation")
    
    # Database status indicator
    db_manager = get_database_manager()
    db_status = db_manager.test_connection()
    
    if db_status:
        st.sidebar.success(f"{ICONS['database']} Database connected and working")
    else:
        st.sidebar.warning(f"{ICONS['warning']} Database connection issues - using session storage")
    
    # Profile selection
    st.sidebar.header("Select Profile")
    
    # Get all profiles from the database
    try:
        all_profiles = db_manager.get_all_profiles()
    except Exception as e:
        st.sidebar.error(f"{ICONS['error']} Error loading profiles: {str(e)}")
        all_profiles = {}
    
    # Create options for the selectbox
    profile_options = ["Create New Profile"] + list(all_profiles.keys())
    profile_labels = ["Create New Profile"] + [
        p.get('name', f"Profile {i}") for i, p in enumerate(all_profiles.values())
    ]
    
    # Map display names to profile IDs
    profile_map = dict(zip(profile_labels, profile_options))
    
    # Determine the current index
    current_profile_id = st.session_state.get('current_profile_id')
    current_index = 0
    
    if current_profile_id:
        # Find the index of the current profile
        for i, (label, profile_id) in enumerate(profile_map.items()):
            if profile_id == current_profile_id:
                current_index = i
                break
    
    # Display the profile selection dropdown
    selected_profile_label = st.sidebar.selectbox(
        "Select a profile",
        options=profile_labels,
        index=current_index,
        help="Choose an existing profile or create a new one"
    )
    
    # Get the selected profile ID
    selected_profile_id = profile_map[selected_profile_label]
    
    # Update the session state
    if selected_profile_id != "Create New Profile":
        st.session_state.current_profile_id = selected_profile_id
    else:
        st.session_state.current_profile_id = None
    
    # Navigation options
    st.sidebar.header("Actions")
    nav_option = st.sidebar.radio(
        "Choose an action:",
        options=["Edit Profile", "Missing Person Information", "Generate Documents"],
        help="Select what you want to do with the profile"
    )
    
    # Delete profile option
    if st.session_state.get('current_profile_id'):
        if st.sidebar.button("Delete Current Profile", type="secondary"):
            try:
                # Delete the profile
                success = db_manager.delete_profile(st.session_state.current_profile_id)
                if success:
                    st.sidebar.success(f"{ICONS['success']} Profile deleted successfully!")
                    st.session_state.current_profile_id = None
                    # Force a rerun to refresh the UI
                    st.rerun()
                else:
                    st.sidebar.error(f"{ICONS['error']} Failed to delete profile")
            except Exception as e:
                st.sidebar.error(f"{ICONS['error']} Error deleting profile: {str(e)}")
    
    # About section
    with st.sidebar.expander("About"):
        st.write("""
        This application helps create and manage profiles for people with learning 
        disabilities based on Herbert and Philomena protocols. It allows for creation 
        of one-page profiles and missing person information.
        """)
        st.write("Developed by Adam Vials Moore")
        st.write("License: Apache 2.0")
    
    return nav_option
