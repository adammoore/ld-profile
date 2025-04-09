"""
Learning Disability Profile Application.

This application helps create and manage profiles for people with learning disabilities
based on Herbert and Philomena protocols, supporting one-page profiles and missing
person information.

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
    """Main application entry point."""
    # Set page config
    st.set_page_config(
        page_title=APP_NAME,
        page_icon=ICONS['profile'],
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Add custom CSS
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
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        st.error(f"{ICONS['error']} An unexpected error occurred: {str(e)}")
        st.error("Please try refreshing the page or contact support.")
