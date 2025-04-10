"""
Profile form UI component for the Learning Disability Profile application.

This module contains the UI for creating and editing profiles, including
form fields for personal details, emergency contacts, physical description,
and support needs.

Author: Adam Vials Moore
License: Apache License 2.0
"""

import datetime
import pandas as pd
import streamlit as st
from typing import Dict, Any, Optional, List

from config import (
    ICONS, BUILD_OPTIONS, HAIR_COLOR_OPTIONS, EYE_COLOR_OPTIONS, RELATIONSHIP_OPTIONS,
    HEIGHT_MIN_CM, HEIGHT_MAX_CM, HEIGHT_DEFAULT_CM,
    WEIGHT_MIN_KG, WEIGHT_MAX_KG, WEIGHT_DEFAULT_KG
)
from models import Profile, PROFILE_REQUIRED_FIELDS
from utils import (
    save_uploaded_image, calculate_age, format_height, format_weight,
    format_contact_info
)
from database import get_database_manager


def render_profile_form() -> None:
    """
    Render the profile creation/editing form.
    
    This function displays a comprehensive form for entering profile information,
    including:
    - Basic personal details
    - Emergency contact information
    - Physical description
    - One-page profile information
    - Herbert/Philomena Protocol details
    
    If a profile is currently selected, the form is pre-populated with the
    existing data for editing. Otherwise, a new profile is created.
    
    The form includes validation and appropriate help text for each field.
    When submitted, the data is saved to the database.
    
    Returns:
        None
    """
    st.write("## Personal Profile Information")
    st.write("Create a profile based on Herbert and Philomena protocols")
    
    # Load existing profile if editing
    db_manager = get_database_manager()
    current_profile_id = st.session_state.get('current_profile_id')
    
    if current_profile_id:
        try:
            profile_data = db_manager.load_profile(current_profile_id)
            if not profile_data:
                st.error(f"{ICONS['error']} Failed to load profile. It may have been deleted.")
                st.session_state.current_profile_id = None
                st.rerun()
                return
        except Exception as e:
            st.error(f"{ICONS['error']} Error loading profile: {str(e)}")
            profile_data = {}
    else:
        profile_data = {}
    
    # Create a form for profile data entry
    with st.form("profile_form"):
        # === BASIC INFORMATION SECTION ===
        st.write("### Basic Information")
        
        col1, col2 = st.columns(2)
        with col1:
            # Name field
            name = st.text_input(
                "Full Name", 
                value=profile_data.get('name', ''),
                help="The person's full legal name"
            )
            
            # Date of birth field with age calculation
            dob = st.date_input(
                "Date of Birth", 
                value=None if not profile_data.get('dob') else pd.to_datetime(profile_data.get('dob')),
                help="The person's date of birth"
            )
            
            # Calculate and show age
            if dob:
                age = calculate_age(dob)
                age_display = f"{age} years"
            else:
                age = ""
                age_display = "Not specified"
            
            st.write(f"**Age:** {age_display}")
            
            # NHS number field
            nhs_number = st.text_input(
                "NHS Number", 
                value=profile_data.get('nhs_number', ''),
                help="10-digit NHS number for medical identification"
            )
            
            # === EMERGENCY CONTACT SECTION ===
            st.write("### Emergency Contact Information")
            st.write("This information will be used in case of emergency")
            
            # Contact name field
            contact_name = st.text_input(
                "Contact Name", 
                value=profile_data.get('emergency_contact_name', ''),
                help="Full name of emergency contact person"
            )
            
            # Relationship dropdown with custom option
            selected_relationship = profile_data.get('emergency_contact_relationship', RELATIONSHIP_OPTIONS[0])
            relationship_index = RELATIONSHIP_OPTIONS.index(selected_relationship) if selected_relationship in RELATIONSHIP_OPTIONS else 0
            
            relationship = st.selectbox(
                "Relationship to Person", 
                options=RELATIONSHIP_OPTIONS,
                index=relationship_index,
                help="Relationship of the emergency contact to the person"
            )
            
            # Allow custom relationship if "Other" is selected
            if relationship == "Other":
                relationship = st.text_input(
                    "Please specify relationship", 
                    value=profile_data.get('emergency_contact_relationship_other', '')
                )
            
            # Contact phone and email fields
            contact_mobile = st.text_input(
                "Mobile Number", 
                value=profile_data.get('emergency_contact_mobile', ''),
                help="Mobile phone number of emergency contact"
            )
            
            contact_email = st.text_input(
                "Email Address", 
                value=profile_data.get('emergency_contact_email', ''),
                help="Email address of emergency contact"
            )
            
            # Format emergency contact information for display and backward compatibility
            emergency_contact = ""
            if contact_name:
                emergency_contact += f"{contact_name}"
            if relationship:
                emergency_contact += f" ({relationship})"
            if contact_mobile:
                emergency_contact += f" - Mobile: {contact_mobile}"
            if contact_email:
                emergency_contact += f" - Email: {contact_email}"
        
        with col2:
            # Profile image upload
            st.write("Profile Photo")
            st.write("Upload a clear, recent photo of the person's face")
            profile_image_file = st.file_uploader(
                "Upload a profile photo", 
                type=["jpg", "jpeg", "png"],
                help="Choose a clear photo showing the person's face to help with identification"
            )
            
            # Display current or new profile image
            if profile_image_file:
                st.image(profile_image_file, width=150)
                st.caption("New profile photo to be uploaded")
            elif profile_data.get('profile_image') and os.path.exists(profile_data.get('profile_image')):
                try:
                    st.image(profile_data.get('profile_image'), width=150)
                    st.caption("Current profile photo")
                except Exception as e:
                    st.error(f"Error displaying profile image: {str(e)}")
                    st.info("Please upload a new profile photo")
        
        # === PHYSICAL DESCRIPTION SECTION ===
        st.write("### Physical Description")
        st.write("These details help identify the person if they become missing")
        
        col1, col2 = st.columns(2)
        with col1:
            # Height selector with cm and imperial conversion
            height_cm = st.number_input(
                "Height (cm)", 
                min_value=HEIGHT_MIN_CM, 
                max_value=HEIGHT_MAX_CM, 
                value=int(profile_data.get('height_cm', HEIGHT_DEFAULT_CM)),
                help="Height in centimeters"
            )
            
            # Show the formatted height display
            st.write(f"**Height display:** {format_height(height_cm)}")
            
            # Weight selector with kg and imperial conversion
            weight_kg = st.number_input(
                "Weight (kg)",
                min_value=WEIGHT_MIN_KG, 
                max_value=WEIGHT_MAX_KG,
                value=int(profile_data.get('weight_kg', WEIGHT_DEFAULT_KG)),
                help="Weight in kilograms"
            )
            
            # Show the formatted weight display
            st.write(f"**Weight display:** {format_weight(weight_kg)}")
            
            # Build dropdown with custom option
            selected_build = profile_data.get('build', BUILD_OPTIONS[0])
            build_index = BUILD_OPTIONS.index(selected_build) if selected_build in BUILD_OPTIONS else 0
            
            build = st.selectbox(
                "Build", 
                options=BUILD_OPTIONS,
                index=build_index,
                help="General body build/frame"
            )
            
            # Custom build input if "Other" is selected
            if build == "Other":
                build = st.text_input(
                    "Please specify build", 
                    value=profile_data.get('build_other', '')
                )
        
        with col2:
            # Hair color dropdown with custom option
            selected_hair_color = profile_data.get('hair_color', HAIR_COLOR_OPTIONS[0])
            hair_color_index = HAIR_COLOR_OPTIONS.index(selected_hair_color) if selected_hair_color in HAIR_COLOR_OPTIONS else 0
            
            hair_color = st.selectbox(
                "Hair Color", 
                options=HAIR_COLOR_OPTIONS,
                index=hair_color_index,
                help="Primary hair color"
            )
            
            # Custom hair color input if "Other" is selected
            if hair_color == "Other":
                hair_color = st.text_input(
                    "Please specify hair color", 
                    value=profile_data.get('hair_color_other', '')
                )
            
            # Hair style field
            hair_style = st.text_input(
                "Hair Style", 
                value=profile_data.get('hair_style', ''),
                help="Current hairstyle (e.g., short, long, curly, straight)"
            )
            
            # Eye color dropdown with custom option
            selected_eye_color = profile_data.get('eye_color', EYE_COLOR_OPTIONS[0])
            eye_color_index = EYE_COLOR_OPTIONS.index(selected_eye_color) if selected_eye_color in EYE_COLOR_OPTIONS else 0
            
            eye_color = st.selectbox(
                "Eye Color", 
                options=EYE_COLOR_OPTIONS,
                index=eye_color_index,
                help="Eye color"
            )
            
            # Custom eye color input if "Other" is selected
            if eye_color == "Other":
                eye_color = st.text_input(
                    "Please specify eye color", 
                    value=profile_data.get('eye_color_other', '')
                )
        
        # Combine hair details for display
        hair = f"{hair_color} {hair_style}" if hair_style else hair_color
        
        # Distinguishing features section
        st.write("### Distinguishing Features")
        st.write("Any notable physical characteristics that would help identify the person")
        
        distinguishing_features = st.text_area(
            "Distinguishing Features", 
            value=profile_data.get('distinguishing_features', ''),
            help="Birthmarks, scars, tattoos, or other noticeable features"
        )
        
        # === ONE-PAGE PROFILE SECTIONS ===
        st.write("### One-Page Profile Information")
        st.write("This information helps others understand and support the person effectively")
        
        important_to_me = st.text_area(
            "What's Important To Me", 
            value=profile_data.get('important_to_me', ''), 
            height=150,
            help="Describe what matters most to the person - their preferences, interests, routines, and values"
        )
        
        how_to_support = st.text_area(
            "How Best To Support Me", 
            value=profile_data.get('how_to_support', ''),
            height=150,
            help="Describe the best ways to provide support, including approaches that work well and those to avoid"
        )
        
        communication = st.text_area(
            "How I Communicate", 
            value=profile_data.get('communication', ''),
            height=150,
            help="Describe communication methods, preferences, any communication aids used, and how the person expresses themselves"
        )
        
        # === HERBERT/PHILOMENA PROTOCOL SECTIONS ===
        st.write("### Additional Information (Herbert/Philomena Protocol)")
        st.write("This information is essential if the person becomes missing")
        
        medical_info = st.text_area(
            "Medical Information", 
            value=profile_data.get('medical_info', ''),
            height=150,
            help="Include medications, conditions, allergies, and any health needs requiring urgent attention"
        )
        
        places_might_go = st.text_area(
            "Places I Might Go", 
            value=profile_data.get('places_might_go', ''),
            height=150,
            help="List places the person might go if missing - previous homes, favorite places, familiar locations, etc."
        )
        
        travel_routines = st.text_area(
            "Travel Patterns and Routines", 
            value=profile_data.get('travel_routines', ''),
            height=150,
            help="Describe how the person typically travels, regular routes, routines, and travel preferences"
        )
        
        # === GDPR/PRIVACY SECTION ===
        st.write("### Data Protection")
        gdpr_consent = st.checkbox(
            "I understand this information will be stored securely and used only for the purpose of supporting this person", 
            value=bool(profile_data.get('gdpr_consent', False)),
            help="Consent is required to store this information under GDPR regulations"
        )
        
        # Submit button
        submit_button = st.form_submit_button(
            "Save Profile", 
            type="primary",
            help="Save the profile information"
        )
    
    # Process form submission
    if submit_button:
        # Validate required fields
        missing_fields = []
        if not name:
            missing_fields.append("Name")
        if not gdpr_consent:
            missing_fields.append("Data protection consent")
        
        if missing_fields:
            st.error(f"{ICONS['error']} Please fill in the following required fields: {', '.join(missing_fields)}")
            return
        
        # Create or update profile
        try:
            # Prepare profile data
            new_profile = Profile(
                name=name,
                dob=dob,
                age=age,
                nhs_number=nhs_number,
                
                # Detailed emergency contact information
                emergency_contact_name=contact_name,
                emergency_contact_relationship=relationship,
                emergency_contact_mobile=contact_mobile,
                emergency_contact_email=contact_email,
                emergency_contact=emergency_contact,  # Combined format for backward compatibility
                
                # Physical description
                height_cm=height_cm,
                weight_kg=weight_kg,
                build=build,
                hair_color=hair_color,
                hair_style=hair_style,
                eye_color=eye_color,
                distinguishing_features=distinguishing_features,
                
                # One-page profile information
                important_to_me=important_to_me,
                how_to_support=how_to_support,
                communication=communication,
                
                # Herbert/Philomena protocol information
                medical_info=medical_info,
                places_might_go=places_might_go,
                travel_routines=travel_routines,
                
                # Consent
                gdpr_consent=gdpr_consent
            )
            
            # If editing an existing profile, keep the ID
            if current_profile_id:
                new_profile.profile_id = current_profile_id
            
            # Convert to dictionary
            new_profile_data = new_profile.to_dict()
            
            # Handle profile image
            if profile_image_file:
                # Save new image
                image_path = save_uploaded_image(
                    profile_image_file, 
                    new_profile_data['profile_id'], 
                    'profile'
                )
                new_profile_data['profile_image'] = image_path
            elif profile_data.get('profile_image'):
                # Keep existing image
                new_profile_data['profile_image'] = profile_data.get('profile_image')
            
            # Save to database
            db_manager = get_database_manager()
            profile_id = db_manager.save_profile(new_profile_data)
            
            # Update session state
            st.session_state.current_profile_id = profile_id
            
            # Show success message
            st.success(f"{ICONS['success']} Profile saved successfully!")
            
            # Refresh the page to show the updated profile
            st.rerun()
        except Exception as e:
            st.error(f"{ICONS['error']} Error saving profile: {str(e)}")
