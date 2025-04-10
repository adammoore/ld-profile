"""
Learning Disability Profile Application.

This application helps create and manage profiles for people with learning disabilities
based on Herbert and Philomena protocols, supporting one-page profiles and missing
person information.

It provides a comprehensive set of features for creating, editing, and managing
profiles, as well as generating documents for various purposes. The application
is designed to be user-friendly, accessible, and compliant with data protection
regulations.

Author: Adam Vials Moore
License: Apache License 2.0
"""

import streamlit as st
import logging
from pathlib import Path

# Import configuration
from config import APP_NAME, ICONS, APP_FOOTER, DATA_DIR

# Import UI components
from ui import (
    render_sidebar,
    render_profile_form,
    render_missing_person_form,
    render_document_generator
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(DATA_DIR / 'app.log')
    ]
)
logger = logging.getLogger(__name__)


def main():
    """
    Main application entry point.
    
    This function initializes the application, sets up the page configuration,
    and renders the appropriate UI components based on user navigation. It also
    handles top-level error handling for the application.
    
    The application flow:
    1. Set up the page configuration and styling
    2. Render the sidebar navigation
    3. Render the appropriate page based on navigation selection
    4. Add a footer with application information
    
    Returns:
        None
    """
    # Set page config
    st.set_page_config(
        page_title=APP_NAME,
        page_icon=ICONS['profile'],
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Add custom CSS for better styling
    st.markdown("""
    <style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    h1, h2, h3 {
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    .st-emotion-cache-q8sbsg p {
        font-size: 15px !important;
    }
    /* Improve form styling */
    div[data-testid="stForm"] {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e9ecef;
    }
    /* Improve expandable sections */
    details {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
    /* Improve button styling */
    .stButton > button {
        font-weight: 600;
    }
    /* Add spacing between sections */
    h3 {
        margin-top: 2rem !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # App title
    st.title(f"{ICONS['profile']} {APP_NAME}")
    
    # Render the sidebar and get the selected navigation option
    nav_option = render_sidebar()
    
    # Render the appropriate page based on navigation selection
    if nav_option == "Edit Profile":
        render_profile_form()
    elif nav_option == "Missing Person Information":
        render_missing_person_form()
    elif nav_option == "Generate Documents":
        render_document_generator()
    
    # Footer
    st.markdown("---")
    st.caption(APP_FOOTER)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # Handle any unhandled exceptions
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        st.error(f"{ICONS['error']} An unexpected error occurred: {str(e)}")
        st.error("Please try refreshing the page or contact support.")
