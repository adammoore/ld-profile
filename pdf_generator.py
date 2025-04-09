"""
PDF generation functionality for the Learning Disability Profile application.

This module provides functions and classes for creating PDF documents from profile data,
including one-page profiles and missing person posters. It supports:
- Creating one-page profiles based on person-centered planning approaches
- Generating missing person posters with identification information
- Including maps and location details in missing person posters
- Adding QR codes for digital access to location information

Dependencies:
- reportlab: For generating complex PDFs (one-page profiles)
- fpdf: For simpler PDF generation (missing person posters)
- folium: For map generation (optional)
- qrcode: For QR code generation (optional)
- PIL/Pillow: For image handling
"""

import io
import os
import logging
import tempfile
from typing import Dict, Any, Optional, BinaryIO, Tuple

import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    Image as ReportLabImage
)
from fpdf import FPDF

from models import ProfileData
from config import PDF_PAGE_SIZE, PDF_MARGIN

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_profile_pdf(profile_data: Dict[str, Any]) -> BinaryIO:
    """
    Create a PDF of the one-page profile based on person-centered planning approaches.
    
    This function generates a comprehensive PDF document that includes:
    - Basic personal information
    - Physical description
    - What's important to the person
    - How to support the person
    - Communication preferences
    - Medical information
    - Places the person might go
    - Travel patterns and routines
    
    Args:
        profile_data: Dictionary containing the person's profile information
        
    Returns:
        BytesIO object containing the PDF document, ready for downloading
        
    Raises:
        Exception: If there's an error during PDF generation
    """
    logger.info(f"Creating profile PDF for {profile_data.get('name', 'unknown')}")
    
    # Create buffer for PDF output
    pdf_buffer = io.BytesIO()
    
    # Create PDF document with A4 size and margins
    doc = SimpleDocTemplate(
        pdf_buffer, 
        pagesize=A4,
        rightMargin=PDF_MARGIN, 
        leftMargin=PDF_MARGIN,
        topMargin=PDF_MARGIN, 
        bottomMargin=PDF_MARGIN
    )
    
    # Get base styles and create custom styles for consistent formatting
    styles = getSampleStyleSheet()
    
    # Create custom heading and paragraph styles to avoid conflicts with base styles
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
    
    # Initialize the story (content elements that will be added to the PDF)
    story = []
    
    # === TITLE SECTION ===
    title = f"One-Page Profile: {profile_data.get('name', '')}"
    story.append(Paragraph(title, heading1_style))
    story.append(Spacer(1, 0.3*inch))
    
    # === PROFILE IMAGE SECTION ===
    # Add profile image if available
    profile_image = profile_data.get('profile_image')
    if profile_image and os.path.exists(profile_image):
        try:
            img = ReportLabImage(profile_image, width=2*inch, height=2*inch)
            story.append(img)
            story.append(Spacer(1, 0.2*inch))
        except Exception as e:
            logger.error(f"Error adding profile image to PDF: {str(e)}")
    
    # === BASIC INFORMATION TABLE ===
    basic_info = [
        ['Name', profile_data.get('name', '')],
        ['Date of Birth', profile_data.get('dob', '')],
        ['NHS Number', profile_data.get('nhs_number', '')],
        ['Emergency Contact', profile_data.get('emergency_contact', '')]
    ]
    
    # Create a table with two columns of specific widths
    basic_info_table = Table(basic_info, colWidths=[100, 350])
    
    # Style the table with grey headers and gridlines
    basic_info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),  # Grey background for headers
        ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (1, 0), (1, -1), colors.white),  # White background for data cells
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),   # Grid lines
    ]))
    
    story.append(basic_info_table)
    story.append(Spacer(1, 0.3*inch))
    
    # === IMPORTANT INFORMATION SECTION ===
    story.append(Paragraph("Important Information to Keep Me Safe", heading2_style))
    
    # --- Physical Description Table ---
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
    
    # === ONE-PAGE PROFILE SECTIONS ===
    # --- What's Important To Me Section ---
    story.append(Paragraph("What's Important To Me:", heading2_style))
    story.append(Paragraph(profile_data.get('important_to_me', ''), normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    # --- How Best To Support Me Section ---
    story.append(Paragraph("How Best To Support Me:", heading2_style))
    story.append(Paragraph(profile_data.get('how_to_support', ''), normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    # --- Communication Section ---
    story.append(Paragraph("How I Communicate:", heading2_style))
    story.append(Paragraph(profile_data.get('communication', ''), normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    # === HERBERT/PHILOMENA PROTOCOL SECTIONS ===
    # --- Medical Information Section ---
    story.append(Paragraph("Medical Information:", heading2_style))
    story.append(Paragraph(profile_data.get('medical_info', ''), normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    # --- Places I Might Go Section ---
    story.append(Paragraph("Places I Might Go:", heading2_style))
    story.append(Paragraph(profile_data.get('places_might_go', ''), normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    # --- Travel Patterns and Routines Section ---
    story.append(Paragraph("Travel Patterns and Routines:", heading2_style))
    story.append(Paragraph(profile_data.get('travel_routines', ''), normal_style))
    
    # === FOOTER SECTION ===
    # Add a footer with data protection notice
    story.append(Spacer(1, 0.5*inch))
    footer_text = "CONFIDENTIAL - Data Protection: This document contains personal data subject to GDPR. Handle according to data protection policies."
    story.append(Paragraph(footer_text, normal_style))
    
    # Build the PDF document from the story elements
    try:
        doc.build(story)
        logger.info(f"Profile PDF created successfully for {profile_data.get('name', 'unknown')}")
    except Exception as e:
        logger.error(f"Error building profile PDF: {str(e)}")
        raise
    
    return pdf_buffer


class MissingPersonPoster(FPDF):
    """
    Custom FPDF class for creating missing person posters.
    
    This class extends the FPDF base class to create specialized missing person
    posters with consistent formatting. It automatically adds a header to each
    page with the "MISSING PERSON" title and the person's name.
    """
    
    def __init__(self, profile_data: Dict[str, Any]):
        """
        Initialize the missing person poster.
        
        Args:
            profile_data: Dictionary containing the person's profile information
        """
        super().__init__()
        self.profile_data = profile_data
    
    def header(self):
        """
        Add a standard header to each page of the poster.
        
        This method is automatically called by FPDF when a new page is added.
        It adds a "MISSING PERSON" title and a subtitle with the person's name.
        """
        # Add "MISSING PERSON" title
        self.set_font('Arial', 'B', 24)
        self.cell(0, 15, 'MISSING PERSON', 0, 1, 'C')
        
        # Add the person's name as a subtitle
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, f"URGENT: Please help find {self.profile_data.get('name', '')}", 0, 1, 'C')
        
        # Add some space after the header
        self.ln(5)


def create_missing_person_poster(profile_data: Dict[str, Any]) -> BinaryIO:
    """
    Create a comprehensive missing person poster PDF.
    
    This function generates a multi-page PDF poster that includes:
    - The person's photo and physical description
    - When and where they were last seen
    - A map of the last known location (if coordinates are available)
    - A QR code linking to Google Maps
    - Important information about medical needs and communication
    - Contact information for reporting sightings
    
    Args:
        profile_data: Dictionary containing the person's profile information
        
    Returns:
        BytesIO object containing the PDF poster, ready for downloading
        
    Raises:
        Exception: If there's an error during PDF generation
    """
    logger.info(f"Creating missing person poster for {profile_data.get('name', 'unknown')}")
    
    # Create buffer for PDF output
    pdf_buffer = io.BytesIO()
    
    # Create poster using the custom MissingPersonPoster class
    poster = MissingPersonPoster(profile_data)
    
    # === PAGE 1: MAIN INFORMATION ===
    poster.add_page()
    
    # --- Profile Image Section ---
    # Add profile image if available (centered near the top of the page)
    profile_image = profile_data.get('profile_image')
    if profile_image and os.path.exists(profile_image):
        try:
            # FPDF expects file paths as str objects, not bytes
            if isinstance(profile_image, bytes):
                profile_image = profile_image.decode('utf-8')
            
            poster.image(profile_image, x=75, y=40, w=60, h=60)
        except Exception as e:
            logger.error(f"Error adding profile image to poster: {str(e)}")
    
    # --- Description Section ---
    # Add physical description details
    poster.ln(70)  # Move down past the image
    poster.set_font('Arial', 'B', 12)
    poster.cell(0, 10, 'DESCRIPTION:', 0, 1)
    poster.set_font('Arial', '', 12)
    
    # Add each description element on its own line
    poster.multi_cell(0, 8, f"Name: {profile_data.get('name', '')}")
    poster.multi_cell(0, 8, f"Age: {profile_data.get('age', '')}")
    poster.multi_cell(0, 8, f"Height: {profile_data.get('height', '')}")
    poster.multi_cell(0, 8, f"Build: {profile_data.get('build', '')}")
    poster.multi_cell(0, 8, f"Hair: {profile_data.get('hair', '')}")
    poster.multi_cell(0, 8, f"Eyes: {profile_data.get('eyes', '')}")
    poster.multi_cell(0, 8, f"Distinguishing features: {profile_data.get('distinguishing_features', '')}")
    
    # --- Last Seen Information Section ---
    poster.ln(10)  # Add some space
    poster.set_font('Arial', 'B', 12)
    poster.cell(0, 10, 'LAST SEEN:', 0, 1)
    poster.set_font('Arial', '', 12)
    
    # Add when and where the person was last seen
    poster.multi_cell(0, 8, f"Date and time: {profile_data.get('last_seen_datetime', 'Unknown')}")
    poster.multi_cell(0, 8, f"Location: {profile_data.get('last_seen_location', 'Unknown')}")
    poster.multi_cell(0, 8, f"Wearing: {profile_data.get('last_seen_wearing', 'Unknown')}")
    
    # === PAGE 2: MAP AND LOCATION (OPTIONAL) ===
    # Try to add a map for the last seen location if possible
    try:
        # Import optional dependencies for map generation
        from utils import geocode_location
        import folium
        
        # Get coordinates from the location text
        location_text = profile_data.get('last_seen_location', '')
        lat, lng = geocode_location(location_text)
        
        # If coordinates were found, add a map page
        if lat is not None and lng is not None:
            # Create a map centered at the coordinates
            m = folium.Map(location=[lat, lng], zoom_start=15)
            
            # Add a marker at the exact location
            folium.Marker(
                [lat, lng],
                popup=location_text,
                tooltip="Last seen here",
                icon=folium.Icon(color="red", icon="info-sign")
            ).add_to(m)
            
            # Add a circle to indicate approximate area (200m radius)
            folium.Circle(
                radius=200,
                location=[lat, lng],
                color="red",
                fill=True,
                fill_color="red",
                fill_opacity=0.1
            ).add_to(m)
            
            # Save the map to a temporary HTML file (needed for folium)
            with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as tmp:
                m.save(tmp.name)
                
                # Add a new page for the map information
                poster.add_page()
                poster.set_font('Arial', 'B', 14)
                poster.cell(0, 10, 'LOCATION MAP', 0, 1, 'C')
                poster.set_font('Arial', '', 12)
                
                # Add location details
                poster.multi_cell(0, 8, f"Last seen at: {location_text}")
                poster.multi_cell(0, 8, f"Coordinates: {lat:.6f}, {lng:.6f}")
                poster.ln(10)
                
                # Add help text for using the digital options
                poster.multi_cell(0, 8, "For an interactive map, scan the QR code or visit the URL below:")
                
                # Generate a Google Maps URL that opens at the specified location
                google_maps_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lng}"
                poster.multi_cell(0, 8, google_maps_url)
                
                # Try to generate and add a QR code for the Google Maps link
                try:
                    import qrcode
                    from PIL import Image
                    
                    # Generate QR code containing the Google Maps URL
                    qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=10,
                        border=4,
                    )
                    qr.add_data(google_maps_url)
                    qr.make(fit=True)
                    
                    # Create an image from the QR Code
                    img = qr.make_image(fill_color="black", back_color="white")
                    
                    # Save the QR code to a temporary file
                    qr_temp = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
                    img.save(qr_temp.name)
                    qr_temp.close()
                    
                    # Add the QR code to the PDF (centered)
                    poster.image(qr_temp.name, x=85, y=poster.get_y() + 10, w=40, h=40)
                    
                    # Clean up the temporary file
                    os.unlink(qr_temp.name)
                except ImportError:
                    # If qrcode library is not available, just skip the QR code
                    poster.multi_cell(0, 8, "QR code generation not available. Please use the URL above.")
                except Exception as e:
                    logger.error(f"Error generating QR code: {str(e)}")
                
                # Clean up the temporary map file
                tmp.close()
                os.unlink(tmp.name)
    except (ImportError, Exception) as e:
        logger.warning(f"Could not add map to poster: {str(e)}")
    
    # === PAGE 3: IMPORTANT INFORMATION ===
    poster.add_page()
    poster.set_font('Arial', 'B', 12)
    poster.cell(0, 10, 'IMPORTANT INFORMATION:', 0, 1)
    poster.set_font('Arial', '', 12)
    
    # Add concise medical and communication information
    poster.multi_cell(0, 8, f"Medical needs: {profile_data.get('medical_info_short', 'Unknown')}")
    poster.multi_cell(0, 8, f"Communication: {profile_data.get('communication_short', 'Unknown')}")
    poster.multi_cell(0, 8, f"Places they might go: {profile_data.get('places_might_go_short', 'Unknown')}")
    
    # --- Contact Information Section ---
    poster.ln(10)
    poster.set_font('Arial', 'B', 14)
    poster.cell(0, 10, 'IF YOU HAVE ANY INFORMATION PLEASE CONTACT:', 0, 1, 'C')
    poster.set_font('Arial', 'B', 12)
    poster.cell(0, 8, 'Police: 101 or 999 in an emergency', 0, 1, 'C')
    poster.cell(0, 8, f"Reference: {profile_data.get('reference_number', 'Please quote name')}", 0, 1, 'C')
    
    # Generate the final PDF and write to buffer
    try:
        # Get PDF as bytes using the 'S' (string) output destination
        pdf_bytes = poster.output(dest='S')
        
        # Handle string vs bytes output (FPDF inconsistency)
        if isinstance(pdf_bytes, str):
            pdf_bytes = pdf_bytes.encode('latin1')  # FPDF uses latin1 encoding
            
        # Write the bytes to our buffer
        pdf_buffer.write(pdf_bytes)
        logger.info(f"Missing person poster created successfully for {profile_data.get('name', 'unknown')}")
    except Exception as e:
        logger.error(f"Error creating missing person poster: {str(e)}")
        raise
    
    return pdf_buffer
