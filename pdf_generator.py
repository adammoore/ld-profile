"""
PDF generation functionality for the Learning Disability Profile application.

This module provides functions for creating PDF documents from profile data,
including one-page profiles and missing person posters.
"""

import io
import os
import logging
from typing import Dict, Any, Optional, BinaryIO

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
    Create a PDF of the one-page profile.
    
    Args:
        profile_data: Dictionary containing profile data
        
    Returns:
        BytesIO object containing the PDF
    """
    logger.info(f"Creating profile PDF for {profile_data.get('name', 'unknown')}")
    
    # Create buffer for PDF
    pdf_buffer = io.BytesIO()
    
    # Create PDF document
    doc = SimpleDocTemplate(
        pdf_buffer, 
        pagesize=A4,
        rightMargin=PDF_MARGIN, 
        leftMargin=PDF_MARGIN,
        topMargin=PDF_MARGIN, 
        bottomMargin=PDF_MARGIN
    )
    
    # Get base styles and create custom styles
    styles = getSampleStyleSheet()
    
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
    
    # Create the story (content)
    story = []
    
    # Title
    title = f"One-Page Profile: {profile_data.get('name', '')}"
    story.append(Paragraph(title, heading1_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Add profile image if available
    profile_image = profile_data.get('profile_image')
    if profile_image and os.path.exists(profile_image):
        try:
            img = ReportLabImage(profile_image, width=2*inch, height=2*inch)
            story.append(img)
            story.append(Spacer(1, 0.2*inch))
        except Exception as e:
            logger.error(f"Error adding profile image to PDF: {str(e)}")
    
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
    
    # What's important to me section
    story.append(Paragraph("What's Important To Me:", heading2_style))
    story.append(Paragraph(profile_data.get('important_to_me', ''), normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    # How to support me section
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
    
    # Places I might go section
    story.append(Paragraph("Places I Might Go:", heading2_style))
    story.append(Paragraph(profile_data.get('places_might_go', ''), normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Travel patterns and routines
    story.append(Paragraph("Travel Patterns and Routines:", heading2_style))
    story.append(Paragraph(profile_data.get('travel_routines', ''), normal_style))
    
    # Footer with data protection notice
    story.append(Spacer(1, 0.5*inch))
    footer_text = "CONFIDENTIAL - Data Protection: This document contains personal data subject to GDPR. Handle according to data protection policies."
    story.append(Paragraph(footer_text, normal_style))
    
    # Build the PDF
    try:
        doc.build(story)
        logger.info(f"Profile PDF created successfully for {profile_data.get('name', 'unknown')}")
    except Exception as e:
        logger.error(f"Error building profile PDF: {str(e)}")
        raise
    
    return pdf_buffer


class MissingPersonPoster(FPDF):
    """Custom FPDF class for creating missing person posters."""
    
    def __init__(self, profile_data: Dict[str, Any]):
        """
        Initialize the missing person poster.
        
        Args:
            profile_data: Dictionary containing profile data
        """
        super().__init__()
        self.profile_data = profile_data
    
    def header(self):
        """Add header to the poster."""
        self.set_font('Arial', 'B', 24)
        self.cell(0, 15, 'MISSING PERSON', 0, 1, 'C')
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, f"URGENT: Please help find {self.profile_data.get('name', '')}", 0, 1, 'C')
        self.ln(5)


def create_missing_person_poster(profile_data: Dict[str, Any]) -> BinaryIO:
    """
    Create a missing person poster PDF.
    
    Args:
        profile_data: Dictionary containing profile data
        
    Returns:
        BytesIO object containing the PDF
    """
    logger.info(f"Creating missing person poster for {profile_data.get('name', 'unknown')}")
    
    # Create buffer for PDF
    pdf_buffer = io.BytesIO()
    
    # Create poster
    poster = MissingPersonPoster(profile_data)
    poster.add_page()
    
    # Add profile image if available
    profile_image = profile_data.get('profile_image')
    if profile_image and os.path.exists(profile_image):
        try:
            # FPDF expects file paths as str objects, not bytes
            # First, ensure the profile_image is a string
            if isinstance(profile_image, bytes):
                profile_image = profile_image.decode('utf-8')
            
            poster.image(profile_image, x=75, y=40, w=60, h=60)
        except Exception as e:
            logger.error(f"Error adding profile image to poster: {str(e)}")
    
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
    poster.multi_cell(0, 8, f"Date and time: {profile_data.get('last_seen_datetime', 'Unknown')}")
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
    
    # Output PDF bytes to buffer correctly
    try:
        pdf_bytes = poster.output(dest='S')  # 'S' means return as string/bytes
        
        # Make sure we're writing bytes, not str
        if isinstance(pdf_bytes, str):
            pdf_bytes = pdf_bytes.encode('latin1')  # FPDF uses latin1 encoding
            
        pdf_buffer.write(pdf_bytes)
        logger.info(f"Missing person poster created successfully for {profile_data.get('name', 'unknown')}")
    except Exception as e:
        logger.error(f"Error creating missing person poster: {str(e)}")
        raise
    
    return pdf_buffer
