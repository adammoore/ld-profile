import streamlit as st
import pandas as pd
import os
import io
import base64
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as ReportLabImage, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
import tempfile
import json
import uuid
import datetime
import hashlib
from fpdf import FPDF
import shutil
from cryptography.fernet import Fernet

# Import the database helper
try:
    from db_helper import DatabaseHelper
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

# Set page config
st.set_page_config(
    page_title="Learning Disability Profile Creator",
    page_icon="👤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables
if 'profiles' not in st.session_state:
    st.session_state.profiles = {}
if 'current_profile_id' not in st.session_state:
    st.session_state.current_profile_id = None
if 'encryption_key' not in st.session_state:
    # Generate a key for encryption (in production, store securely)
    st.session_state.encryption_key = Fernet.generate_key()
    st.session_state.cipher_suite = Fernet(st.session_state.encryption_key)
if 'use_database' not in st.session_state:
    st.session_state.use_database = DB_AVAILABLE
if 'db' not in st.session_state and st.session_state.use_database and DB_AVAILABLE:
    # Initialize database connection
    st.session_state.db = DatabaseHelper(st.session_state.encryption_key)

# Data storage functions
def encrypt_data(data):
    """Encrypt sensitive data"""
    return st.session_state.cipher_suite.encrypt(json.dumps(data).encode())

def decrypt_data(encrypted_data):
    """Decrypt sensitive data"""
    return json.loads(st.session_state.cipher_suite.decrypt(encrypted_data).decode())

def save_profile(profile_data):
    """Save profile to secure storage"""
    # Create a unique ID if new profile
    if 'profile_id' not in profile_data:
        profile_data['profile_id'] = str(uuid.uuid4())
        profile_data['created_date'] = datetime.datetime.now().isoformat()
    
    profile_data['last_updated'] = datetime.datetime.now().isoformat()
    
    # Determine whether to use database or session state
    if st.session_state.use_database and DB_AVAILABLE:
        # Save to database
        st.session_state.db.save_profile(profile_data)
    else:
        # Store in session state as fallback
        st.session_state.profiles[profile_data['profile_id']] = profile_data
    
    st.session_state.current_profile_id = profile_data['profile_id']
    return profile_data['profile_id']

def load_profile(profile_id):
    """Load profile from storage"""
    if st.session_state.use_database and DB_AVAILABLE:
        # Load from database
        return st.session_state.db.load_profile(profile_id)
    else:
        # Load from session state as fallback
        return st.session_state.profiles.get(profile_id)

def delete_profile(profile_id):
    """Delete profile from storage (with proper audit trail)"""
    if st.session_state.use_database and DB_AVAILABLE:
        # Delete from database
        return st.session_state.db.delete_profile(profile_id)
    else:
        # Delete from session state as fallback
        if profile_id in st.session_state.profiles:
            del st.session_state.profiles[profile_id]
            return True
    return False

def get_all_profiles():
    """Get all profiles from storage"""
    if st.session_state.use_database and DB_AVAILABLE:
        # Get all profiles from database
        return st.session_state.db.get_all_profiles()
    else:
        # Get all profiles from session state as fallback
        return st.session_state.profiles

# Image handling functions
def save_uploaded_image(uploaded_file, profile_id, image_type):
    """Save uploaded image and return path"""
    if uploaded_file is None:
        return None
        
    # Create directory for this profile if it doesn't exist
    profile_dir = f"profile_data/{profile_id}/images"
    os.makedirs(profile_dir, exist_ok=True)
    
    # Generate unique filename
    file_extension = os.path.splitext(uploaded_file.name)[1]
    filename = f"{image_type}_{uuid.uuid4()}{file_extension}"
    filepath = os.path.join(profile_dir, filename)
    
    # Save the file
    with open(filepath, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return filepath

def get_image_as_base64(image_path):
    """Convert image to base64 for embedding in PDFs"""
    if not image_path or not os.path.exists(image_path):
        return None
        
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# PDF generation functions
def create_profile_pdf(profile_data):
    """Create a PDF of the profile"""
    pdf_buffer = io.BytesIO()
    
    doc = SimpleDocTemplate(
        pdf_buffer, 
        pagesize=A4,
        rightMargin=72, 
        leftMargin=72,
        topMargin=72, 
        bottomMargin=72
    )
    
    # Get the sample styles
    styles = getSampleStyleSheet()
    
    # Create custom styles instead of adding to the stylesheet
    heading1_style = ParagraphStyle(
        'CustomHeading1', 
        parent=styles['Heading1'],
        fontSize=18, 
        spaceAfter=12
    )
    
    heading2_style = ParagraphStyle(
        'CustomHeading2', 
        parent=styles['Heading2'],
        fontSize=14, 
        spaceAfter=8, 
        spaceBefore=14
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal', 
        parent=styles['Normal'],
        fontSize=12, 
        spaceAfter=6
    )
    
    story = []
    
    # Title
    story.append(Paragraph(f"One-Page Profile: {profile_data.get('name', '')}", heading1_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Add profile image
    profile_image = profile_data.get('profile_image')
    if profile_image and os.path.exists(profile_image):
        img = ReportLabImage(profile_image, width=2*inch, height=2*inch)
        story.append(img)
        story.append(Spacer(1, 0.2*inch))
    
    # Core information table
    basic_info = [
        ['Name', profile_data.get('name', '')],
        ['Date of Birth', profile_data.get('dob', '')],
        ['NHS Number', profile_data.get('nhs_number', '')],
        ['Emergency Contact', profile_data.get('emergency_contact', '')]
    ]
    
    basic_info_table = Table(basic_info, colWidths=[100, 350])
    basic_info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (1, 0), (1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    
    story.append(basic_info_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Herbert Protocol sections
    story.append(Paragraph("Important Information to Keep Me Safe", heading2_style))
    
    # Physical description
    story.append(Paragraph("Physical Description:", heading2_style))
    description_data = [
        ['Height', profile_data.get('height', '')],
        ['Build', profile_data.get('build', '')],
        ['Hair Color/Style', profile_data.get('hair', '')],
        ['Eye Color', profile_data.get('eyes', '')],
        ['Distinguishing Features', profile_data.get('distinguishing_features', '')]
    ]
    
    description_table = Table(description_data, colWidths=[150, 300])
    description_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (1, 0), (1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    
    story.append(description_table)
    story.append(Spacer(1, 0.2*inch))
    
    # What's important to me section (from one-page profiles)
    story.append(Paragraph("What's Important To Me:", heading2_style))
    story.append(Paragraph(profile_data.get('important_to_me', ''), normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    # How to support me section (from one-page profiles)
    story.append(Paragraph("How Best To Support Me:", heading2_style))
    story.append(Paragraph(profile_data.get('how_to_support', ''), normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Communication section
    story.append(Paragraph("How I Communicate:", heading2_style))
    story.append(Paragraph(profile_data.get('communication', ''), normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Medical information
    story.append(Paragraph("Medical Information:", heading2_style))
    story.append(Paragraph(profile_data.get('medical_info', ''), normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Places I might go section (Herbert Protocol)
    story.append(Paragraph("Places I Might Go:", heading2_style))
    story.append(Paragraph(profile_data.get('places_might_go', ''), normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Travel patterns and routines
    story.append(Paragraph("Travel Patterns and Routines:", heading2_style))
    story.append(Paragraph(profile_data.get('travel_routines', ''), normal_style))
    
    # Footer with data protection notice
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("CONFIDENTIAL - Data Protection: This document contains personal data subject to GDPR. Handle according to data protection policies.", normal_style))
    
    doc.build(story)
    
    return pdf_buffer

def create_missing_person_poster(profile_data):
    """Create a missing person poster PDF"""
    pdf_buffer = io.BytesIO()
    
    class MissingPersonPoster(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 24)
            self.cell(0, 15, 'MISSING PERSON', 0, 1, 'C')
            self.set_font('Arial', 'B', 16)
            self.cell(0, 10, f"URGENT: Please help find {profile_data.get('name', '')}", 0, 1, 'C')
            self.ln(5)
            
    poster = MissingPersonPoster()
    poster.add_page()
    
    # Add profile image
    profile_image = profile_data.get('profile_image')
    if profile_image and os.path.exists(profile_image):
        poster.image(profile_image, x=75, y=40, w=60, h=60)
    
    # Add description
    poster.ln(70)
    poster.set_font('Arial', 'B', 12)
    poster.cell(0, 10, 'DESCRIPTION:', 0, 1)
    poster.set_font('Arial', '', 12)
    poster.multi_cell(0, 8, f"Name: {profile_data.get('name', '')}")
    poster.multi_cell(0, 8, f"Age: {profile_data.get('age', '')}")
    poster.multi_cell(0, 8, f"Height: {profile_data.get('height', '')}")
    poster.multi_cell(0, 8, f"Build: {profile_data.get('build', '')}")
    poster.multi_cell(0, 8, f"Hair: {profile_data.get('hair', '')}")
    poster.multi_cell(0, 8, f"Eyes: {profile_data.get('eyes', '')}")
    poster.multi_cell(0, 8, f"Distinguishing features: {profile_data.get('distinguishing_features', '')}")
    
    # Last seen information
    poster.ln(10)
    poster.set_font('Arial', 'B', 12)
    poster.cell(0, 10, 'LAST SEEN:', 0, 1)
    poster.set_font('Arial', '', 12)
    poster.multi_cell(0, 8, f"Date and time: {profile_data.get('last_seen_time', 'Unknown')}")
    poster.multi_cell(0, 8, f"Location: {profile_data.get('last_seen_location', 'Unknown')}")
    poster.multi_cell(0, 8, f"Wearing: {profile_data.get('last_seen_wearing', 'Unknown')}")
    
    # Important information
    poster.ln(10)
    poster.set_font('Arial', 'B', 12)
    poster.cell(0, 10, 'IMPORTANT INFORMATION:', 0, 1)
    poster.set_font('Arial', '', 12)
    poster.multi_cell(0, 8, f"Medical needs: {profile_data.get('medical_info_short', 'Unknown')}")
    poster.multi_cell(0, 8, f"Communication: {profile_data.get('communication_short', 'Unknown')}")
    poster.multi_cell(0, 8, f"Places they might go: {profile_data.get('places_might_go_short', 'Unknown')}")
    
    # Contact information
    poster.ln(10)
    poster.set_font('Arial', 'B', 14)
    poster.cell(0, 10, 'IF YOU HAVE ANY INFORMATION PLEASE CONTACT:', 0, 1, 'C')
    poster.set_font('Arial', 'B', 12)
    poster.cell(0, 8, 'Police: 101 or 999 in an emergency', 0, 1, 'C')
    poster.cell(0, 8, f"Reference: {profile_data.get('reference_number', 'Please quote name')}", 0, 1, 'C')
    
    # Use the BytesIO object correctly with FPDF
    # Note: We need to get the PDF as bytes first, then write to the buffer
    pdf_bytes = poster.output(dest='S')  # 'S' means return as string/bytes
    pdf_buffer.write(pdf_bytes)
    
    return pdf_buffer

# UI Functions
def profile_form():
    """Form for creating/editing profiles"""
    st.write("### Personal Profile Information")
    st.write("Create a profile based on Herbert and Philomena protocols")
    
    # Load existing profile if editing
    if st.session_state.current_profile_id:
        profile_data = load_profile(st.session_state.current_profile_id)
    else:
        profile_data = {}
    
    # Basic information
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name", value=profile_data.get('name', ''),
                           help="The person's full legal name")
        
        dob = st.date_input("Date of Birth", 
                          value=None if not profile_data.get('dob') else pd.to_datetime(profile_data.get('dob')),
                          help="The person's date of birth")
        
        # Calculate age from DOB if available
        if dob:
            today = datetime.date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            age_display = f"{age} years"
        else:
            age_display = "Not specified"
            age = ""
        
        st.write(f"**Age:** {age_display}")
        
        nhs_number = st.text_input("NHS Number", value=profile_data.get('nhs_number', ''),
                                 help="10-digit NHS number for medical identification")
        
        emergency_contact = st.text_input("Emergency Contact Details", 
                                        value=profile_data.get('emergency_contact', ''),
                                        help="Name and phone number of primary emergency contact")
    
    with col2:
        # Profile image upload
        st.write("Profile Photo")
        st.write("Upload a clear, recent photo of the person's face")
        profile_image = st.file_uploader("Upload a profile photo", type=["jpg", "jpeg", "png"])
        if profile_image:
            st.image(profile_image, width=150)
        elif profile_data.get('profile_image') and os.path.exists(profile_data.get('profile_image')):
            st.image(profile_data.get('profile_image'), width=150)
    
    # Physical description
    st.write("### Physical Description")
    st.write("These details help identify the person if they become missing")
    
    col1, col2 = st.columns(2)
    with col1:
        # Height selector with cm
        height_cm = st.number_input("Height (cm)", 
                                  min_value=30, max_value=250, 
                                  value=int(profile_data.get('height_cm', 170)),
                                  help="Height in centimeters")
        
        # Convert to formatted display
        height = f"{height_cm} cm ({height_cm//30.48} ft {round((height_cm%30.48)/2.54)} in)"
        
        # Weight selector with kg
        weight_kg = st.number_input("Weight (kg)",
                                  min_value=1, max_value=250,
                                  value=int(profile_data.get('weight_kg', 70)),
                                  help="Weight in kilograms")
        
        # Convert to formatted display
        weight = f"{weight_kg} kg ({round(weight_kg*2.2)} lbs)"
        
        build_options = ["Slim", "Average", "Athletic", "Heavy", "Other"]
        build = st.selectbox("Build", 
                           options=build_options,
                           index=build_options.index(profile_data.get('build', 'Average')) if profile_data.get('build') in build_options else 0,
                           help="General body build/frame")
        
        if build == "Other":
            build = st.text_input("Please specify build", value=profile_data.get('build_other', ''))
    
    with col2:
        hair_color_options = ["Black", "Brown", "Blonde", "Red", "Grey", "White", "Other"]
        hair_color = st.selectbox("Hair Color", 
                                options=hair_color_options,
                                index=hair_color_options.index(profile_data.get('hair_color', 'Brown')) if profile_data.get('hair_color') in hair_color_options else 0,
                                help="Primary hair color")
        
        if hair_color == "Other":
            hair_color = st.text_input("Please specify hair color", value=profile_data.get('hair_color_other', ''))
        
        hair_style = st.text_input("Hair Style", value=profile_data.get('hair_style', ''),
                                help="Current hairstyle (e.g., short, long, curly, straight)")
        
        eye_color_options = ["Brown", "Blue", "Green", "Hazel", "Grey", "Other"]
        eye_color = st.selectbox("Eye Color", 
                               options=eye_color_options,
                               index=eye_color_options.index(profile_data.get('eye_color', 'Brown')) if profile_data.get('eye_color') in eye_color_options else 0,
                               help="Eye color")
        
        if eye_color == "Other":
            eye_color = st.text_input("Please specify eye color", value=profile_data.get('eye_color_other', ''))
    
    # Combine hair details
    hair = f"{hair_color} {hair_style}" if hair_style else hair_color
    
    # Distinguishing features section
    st.write("### Distinguishing Features")
    st.write("Any notable physical characteristics that would help identify the person")
    
    distinguishing_features = st.text_area("Distinguishing Features", 
                                         value=profile_data.get('distinguishing_features', ''),
                                         help="Birthmarks, scars, tattoos, or other noticeable features")
    
    # One-page profile sections
    st.write("### One-Page Profile Information")
    st.write("This information helps others understand and support the person effectively")
    
    important_to_me = st.text_area("What's Important To Me", 
                                 value=profile_data.get('important_to_me', ''), 
                                 help="Describe what matters most to the person - their preferences, interests, routines, and values")
    
    how_to_support = st.text_area("How Best To Support Me", 
                                value=profile_data.get('how_to_support', ''),
                                help="Describe the best ways to provide support, including approaches that work well and those to avoid")
    
    communication = st.text_area("How I Communicate", 
                              value=profile_data.get('communication', ''),
                              help="Describe communication methods, preferences, any communication aids used, and how the person expresses themselves")
    
    # Herbert/Philomena Protocol sections
    st.write("### Additional Information (Herbert/Philomena Protocol)")
    st.write("This information is essential if the person becomes missing")
    
    medical_info = st.text_area("Medical Information", 
                             value=profile_data.get('medical_info', ''),
                             help="Include medications, conditions, allergies, and any health needs requiring urgent attention")
    
    places_might_go = st.text_area("Places I Might Go", 
                                value=profile_data.get('places_might_go', ''),
                                help="List places the person might go if missing - previous homes, favorite places, familiar locations, etc.")
    
    travel_routines = st.text_area("Travel Patterns and Routines", 
                                value=profile_data.get('travel_routines', ''),
                                help="Describe how the person typically travels, regular routes, routines, and travel preferences")
    
    # GDPR/Privacy confirmation
    st.write("### Data Protection")
    gdpr_consent = st.checkbox("I understand this information will be stored securely and used only for the purpose of supporting this person", 
                             value=True if profile_data else False)
    
    # Save button
    if st.button("Save Profile", type="primary", disabled=(not gdpr_consent)):
        # Prepare data object
        new_profile_data = {
            'name': name,
            'dob': dob.strftime('%Y-%m-%d') if dob else '',
            'age': age,
            'nhs_number': nhs_number,
            'emergency_contact': emergency_contact,
            'height': height,  # Formatted display height
            'height_cm': height_cm,  # Numeric value for calculations
            'weight': weight,  # Formatted display weight
            'weight_kg': weight_kg,  # Numeric value for calculations
            'build': build,
            'hair': hair,
            'hair_color': hair_color,
            'hair_style': hair_style,
            'eyes': eye_color,
            'eye_color': eye_color,
            'distinguishing_features': distinguishing_features,
            'important_to_me': important_to_me,
            'how_to_support': how_to_support,
            'communication': communication,
            'medical_info': medical_info,
            'places_might_go': places_might_go,
            'travel_routines': travel_routines,
            'gdpr_consent': gdpr_consent
        }
        
        # Retain profile ID if editing
        if st.session_state.current_profile_id:
            new_profile_data['profile_id'] = st.session_state.current_profile_id
        
        # Handle profile image
        if profile_image:
            # Save new image
            profile_id = new_profile_data.get('profile_id', str(uuid.uuid4()))
            image_path = save_uploaded_image(profile_image, profile_id, 'profile')
            new_profile_data['profile_image'] = image_path
        elif profile_data.get('profile_image'):
            # Keep existing image
            new_profile_data['profile_image'] = profile_data.get('profile_image')
        
        # Save profile
        profile_id = save_profile(new_profile_data)
        st.success(f"Profile saved successfully!")
        st.session_state.current_profile_id = profile_id
        
        # Refresh the page to show the updated profile
        st.rerun()  # Using st.rerun instead of experimental_rerun

def missing_person_form():
    """Form for updating missing person information"""
    if not st.session_state.current_profile_id:
        st.warning("Please create or select a profile first")
        return
    
    profile_data = load_profile(st.session_state.current_profile_id)
    
    st.write("### Missing Person Information")
    st.write(f"Updating information for: **{profile_data.get('name', '')}**")
    
    # Missing person details
    col1, col2 = st.columns(2)
    with col1:
        last_seen_date = st.date_input("Date Last Seen", 
                                     value=datetime.datetime.now(),
                                     help="The date when the person was last seen")
        
        last_seen_time = st.time_input("Time Last Seen", 
                                     value=datetime.datetime.now().time(),
                                     help="The approximate time when the person was last seen")
        
        last_seen_location = st.text_input("Location Last Seen", 
                                         value=profile_data.get('last_seen_location', ''),
                                         help="The address or detailed description of where the person was last seen")
    
    with col2:
        last_seen_wearing = st.text_area("Clothing When Last Seen", 
                                       value=profile_data.get('last_seen_wearing', ''),
                                       help="Detailed description of what the person was wearing when last seen")
        
        reference_number = st.text_input("Police Reference Number (if available)", 
                                       value=profile_data.get('reference_number', ''),
                                       help="Any reference number provided by police for the missing person case")
    
    # Additional images for missing person poster
    st.write("### Additional Photos")
    st.write("Upload additional recent photos that can help identify the person")
    
    additional_photos = st.file_uploader("Upload additional photos", 
                                       type=["jpg", "jpeg", "png"], 
                                       accept_multiple_files=True,
                                       help="Recent photos showing different angles, hairstyles, or clothing")
    
    # Display existing additional photos
    if profile_data.get('additional_images'):
        st.write("Current additional photos:")
        existing_photo_cols = st.columns(3)
        for i, photo_path in enumerate(profile_data.get('additional_images', [])):
            if os.path.exists(photo_path):
                with existing_photo_cols[i % 3]:
                    st.image(photo_path, width=150)
                    st.caption(f"Photo {i+1}")
    
    # Display newly uploaded photos
    if additional_photos:
        st.write("New photos to be added:")
        new_photo_cols = st.columns(3)
        for i, photo in enumerate(additional_photos):
            with new_photo_cols[i % 3]:
                st.image(photo, width=150)
                st.caption(f"New Photo {i+1}")
    
    # Short versions for poster
    st.write("### Additional Information for Missing Person Poster")
    st.write("Please provide short, concise versions of key information for the poster (limit to 1-2 sentences)")
    
    medical_info_short = st.text_input("Medical Information (short version)", 
                                     value=profile_data.get('medical_info_short', ''),
                                     help="Brief summary of critical medical needs that emergency responders should know")
    
    communication_short = st.text_input("Communication (short version)", 
                                      value=profile_data.get('communication_short', ''),
                                      help="Brief summary of how to communicate effectively with the person")
    
    places_might_go_short = st.text_input("Places They Might Go (short version)", 
                                        value=profile_data.get('places_might_go_short', ''),
                                        help="Brief list of the most likely locations to check first")
    
    # Save button
    if st.button("Update Missing Person Information", type="primary"):
        # Format the datetime for better display
        last_seen_datetime = f"{last_seen_date.strftime('%d %B %Y')} at {last_seen_time.strftime('%H:%M')}"
        
        # Update profile with missing person information
        profile_data['last_seen_date'] = last_seen_date.strftime('%Y-%m-%d')
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
                additional_image_paths.append(image_path)
            
            profile_data['additional_images'] = additional_image_paths
        
        # Save updated profile
        save_profile(profile_data)
        st.success("Missing person information updated successfully!")
        st.rerun()  # Using st.rerun instead of experimental_rerun

def view_generate_documents():
    """View and generate documents from profile"""
    if not st.session_state.current_profile_id:
        st.warning("Please create or select a profile first")
        return
    
    profile_data = load_profile(st.session_state.current_profile_id)
    
    st.write("### View and Generate Documents")
    st.write(f"Documents for: **{profile_data.get('name', '')}**")
    
    # Generate one-page profile
    if st.button("Generate One-Page Profile"):
        pdf_buffer = create_profile_pdf(profile_data)
        pdf_buffer.seek(0)
        
        st.download_button(
            label="Download One-Page Profile PDF",
            data=pdf_buffer,
            file_name=f"{profile_data.get('name', 'profile').replace(' ', '_')}_one_page_profile.pdf",
            mime="application/pdf"
        )
    
    # Generate missing person poster
    missing_info_complete = all([
        profile_data.get('last_seen_date'),
        profile_data.get('last_seen_location')
    ])
    
    if not missing_info_complete:
        st.warning("Missing person information is incomplete. Please update it before generating a poster.")
    
    if st.button("Generate Missing Person Poster", disabled=not missing_info_complete):
        poster_buffer = create_missing_person_poster(profile_data)
        poster_buffer.seek(0)
        
        st.download_button(
            label="Download Missing Person Poster PDF",
            data=poster_buffer,
            file_name=f"{profile_data.get('name', 'profile').replace(' ', '_')}_missing_person_poster.pdf",
            mime="application/pdf"
        )

# Main app
def main():
    # Create necessary directories
    os.makedirs("profile_data", exist_ok=True)
    
    st.title("Learning Disability Profile Creator")
    
    # Sidebar for navigation and profile selection
    with st.sidebar:
        st.header("Navigation")
        
        # Profile selection
        st.subheader("Select Profile")
        
        profile_options = ["Create New Profile"] + list(st.session_state.profiles.keys())
        profile_display = ["Create New Profile"] + [p.get('name', f"Profile {i}") for i, p in enumerate(st.session_state.profiles.values())]
        
        profile_map = dict(zip(profile_display, profile_options))
        
        selected_profile_display = st.selectbox(
            "Select a profile",
            options=profile_display,
            index=0 if not st.session_state.current_profile_id else profile_display.index(
                next((name for name, id in profile_map.items() if id == st.session_state.current_profile_id), "Create New Profile")
            )
        )
        
        selected_profile = profile_map[selected_profile_display]
        
        if selected_profile != "Create New Profile":
            st.session_state.current_profile_id = selected_profile
        else:
            st.session_state.current_profile_id = None
        
        # Navigation options
        st.subheader("Actions")
        nav_option = st.radio(
            "Choose an action:",
            options=["Edit Profile", "Missing Person Information", "Generate Documents"]
        )
        
        # Delete profile option
        if st.session_state.current_profile_id:
            if st.button("Delete Current Profile", type="secondary"):
                delete_profile(st.session_state.current_profile_id)
                st.session_state.current_profile_id = None
                st.success("Profile deleted successfully!")
                st.experimental_rerun()
    
    # Main content area
    if nav_option == "Edit Profile":
        profile_form()
    elif nav_option == "Missing Person Information":
        missing_person_form()
    elif nav_option == "Generate Documents":
        view_generate_documents()
    
    # Footer
    st.markdown("---")
    st.caption("© 2025 Learning Disability Profile Creator | GDPR Compliant | Data stored securely in accordance with UK law")

if __name__ == "__main__":
    main()
