"""
Data models for the Learning Disability Profile application.

This module defines data structures and validation for profile data.
"""

import uuid
import datetime
from typing import Dict, List, Optional, Any, TypedDict, Union
from dataclasses import dataclass, field

class ProfileData(TypedDict, total=False):
    """TypedDict representing the structure of profile data."""
    
    # Identification
    profile_id: str
    created_date: str
    last_updated: str
    
    # Basic information
    name: str
    dob: str
    age: Union[int, str]
    nhs_number: str
    emergency_contact: str
    
    # Physical description
    height: str
    height_cm: int
    weight: str
    weight_kg: int
    build: str
    build_other: str
    hair: str
    hair_color: str
    hair_style: str
    eyes: str
    eye_color: str
    eye_color_other: str
    distinguishing_features: str
    
    # One-page profile info
    important_to_me: str
    how_to_support: str
    communication: str
    
    # Herbert/Philomena protocol info
    medical_info: str
    places_might_go: str
    travel_routines: str
    
    # Missing person info
    last_seen_date: str
    last_seen_time: str
    last_seen_datetime: str
    last_seen_location: str
    last_seen_wearing: str
    reference_number: str
    medical_info_short: str
    communication_short: str
    places_might_go_short: str
    
    # Images
    profile_image: str
    additional_images: List[str]
    
    # Consent
    gdpr_consent: bool


@dataclass
class Profile:
    """
    Profile class for creating and managing profile data.
    
    This class provides methods for creating and validating profile data,
    and for converting between different formats.
    """
    
    # Basic information
    name: str = ""
    dob: Optional[datetime.date] = None
    age: Union[int, str] = ""
    nhs_number: str = ""
    emergency_contact: str = ""
    
    # Physical description
    height_cm: int = 170
    weight_kg: int = 70
    build: str = "Average"
    hair_color: str = "Brown"
    hair_style: str = ""
    eye_color: str = "Brown"
    distinguishing_features: str = ""
    
    # One-page profile info
    important_to_me: str = ""
    how_to_support: str = ""
    communication: str = ""
    
    # Herbert/Philomena protocol info
    medical_info: str = ""
    places_might_go: str = ""
    travel_routines: str = ""
    
    # Missing person info
    last_seen_date: Optional[datetime.date] = None
    last_seen_time: Optional[datetime.time] = None
    last_seen_location: str = ""
    last_seen_wearing: str = ""
    reference_number: str = ""
    medical_info_short: str = ""
    communication_short: str = ""
    places_might_go_short: str = ""
    
    # Images
    profile_image: str = ""
    additional_images: List[str] = field(default_factory=list)
    
    # Consent
    gdpr_consent: bool = False
    
    # Metadata
    profile_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_date: datetime.datetime = field(default_factory=datetime.datetime.now)
    last_updated: datetime.datetime = field(default_factory=datetime.datetime.now)
    
    @property
    def height(self) -> str:
        """Get formatted height string."""
        feet = self.height_cm // 30.48
        inches = round((self.height_cm % 30.48) / 2.54)
        if inches == 12:
            feet += 1
            inches = 0
        return f"{self.height_cm} cm ({int(feet)}' {inches}\")"
    
    @property
    def weight(self) -> str:
        """Get formatted weight string."""
        pounds = round(self.weight_kg * 2.2046)
        return f"{self.weight_kg} kg ({pounds} lbs)"
    
    @property
    def hair(self) -> str:
        """Get combined hair description."""
        return f"{self.hair_color} {self.hair_style}" if self.hair_style else self.hair_color
    
    @property
    def eyes(self) -> str:
        """Get eye color description."""
        return self.eye_color
    
    @property
    def last_seen_datetime(self) -> str:
        """Get formatted last seen datetime."""
        if not self.last_seen_date or not self.last_seen_time:
            return ""
        return f"{self.last_seen_date.strftime('%d %B %Y')} at {self.last_seen_time.strftime('%H:%M')}"
    
    def to_dict(self) -> ProfileData:
        """
        Convert profile to dictionary format for storage.
        
        Returns:
            Dictionary representation of profile
        """
        data: ProfileData = {
            'profile_id': self.profile_id,
            'created_date': self.created_date.isoformat(),
            'last_updated': datetime.datetime.now().isoformat(),
            
            'name': self.name,
            'dob': self.dob.isoformat() if self.dob else '',
            'age': self.age if self.age else '',
            'nhs_number': self.nhs_number,
            'emergency_contact': self.emergency_contact,
            
            'height': self.height,
            'height_cm': self.height_cm,
            'weight': self.weight,
            'weight_kg': self.weight_kg,
            'build': self.build,
            'hair': self.hair,
            'hair_color': self.hair_color,
            'hair_style': self.hair_style,
            'eyes': self.eyes,
            'eye_color': self.eye_color,
            'distinguishing_features': self.distinguishing_features,
            
            'important_to_me': self.important_to_me,
            'how_to_support': self.how_to_support,
            'communication': self.communication,
            
            'medical_info': self.medical_info,
            'places_might_go': self.places_might_go,
            'travel_routines': self.travel_routines,
            
            'profile_image': self.profile_image,
            'additional_images': self.additional_images,
            
            'gdpr_consent': self.gdpr_consent,
        }
        
        # Add missing person info if available
        if self.last_seen_date:
            data['last_seen_date'] = self.last_seen_date.isoformat()
        if self.last_seen_time:
            data['last_seen_time'] = self.last_seen_time.strftime('%H:%M')
        if self.last_seen_date and self.last_seen_time:
            data['last_seen_datetime'] = self.last_seen_datetime
        
        data['last_seen_location'] = self.last_seen_location
        data['last_seen_wearing'] = self.last_seen_wearing
        data['reference_number'] = self.reference_number
        data['medical_info_short'] = self.medical_info_short
        data['communication_short'] = self.communication_short
        data['places_might_go_short'] = self.places_might_go_short
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Profile':
        """
        Create a Profile instance from dictionary data.
        
        Args:
            data: Dictionary containing profile data
            
        Returns:
            Profile instance
        """
        profile = cls()
        
        # Set basic attributes directly from data
        for attr in ['name', 'nhs_number', 'emergency_contact', 'build', 
                     'hair_color', 'hair_style', 'eye_color', 'distinguishing_features',
                     'important_to_me', 'how_to_support', 'communication',
                     'medical_info', 'places_might_go', 'travel_routines',
                     'last_seen_location', 'last_seen_wearing', 'reference_number',
                     'medical_info_short', 'communication_short', 'places_might_go_short',
                     'profile_image', 'gdpr_consent', 'profile_id']:
            if attr in data:
                setattr(profile, attr, data[attr])
        
        # Handle numeric values
        if 'height_cm' in data:
            profile.height_cm = int(data['height_cm'])
        if 'weight_kg' in data:
            profile.weight_kg = int(data['weight_kg'])
        
        # Handle dates and times
        if 'dob' in data and data['dob']:
            try:
                profile.dob = datetime.date.fromisoformat(data['dob'])
                # Calculate age from DOB
                today = datetime.date.today()
                profile.age = today.year - profile.dob.year - ((today.month, today.day) < (profile.dob.month, profile.dob.day))
            except (ValueError, TypeError):
                pass
        
        if 'last_seen_date' in data and data['last_seen_date']:
            try:
                profile.last_seen_date = datetime.date.fromisoformat(data['last_seen_date'])
            except (ValueError, TypeError):
                pass
        
        if 'last_seen_time' in data and data['last_seen_time']:
            try:
                hours, minutes = map(int, data['last_seen_time'].split(':'))
                profile.last_seen_time = datetime.time(hours, minutes)
            except (ValueError, TypeError):
                pass
        
        # Handle lists
        if 'additional_images' in data and isinstance(data['additional_images'], list):
            profile.additional_images = data['additional_images']
        
        # Handle timestamps
        if 'created_date' in data and data['created_date']:
            try:
                profile.created_date = datetime.datetime.fromisoformat(data['created_date'])
            except (ValueError, TypeError):
                pass
        
        if 'last_updated' in data and data['last_updated']:
            try:
                profile.last_updated = datetime.datetime.fromisoformat(data['last_updated'])
            except (ValueError, TypeError):
                pass
        
        return profile
    
    def validate(self) -> List[str]:
        """
        Validate profile data.
        
        Returns:
            List of validation error messages, empty if valid
        """
        errors = []
        
        # Check required fields
        if not self.name:
            errors.append("Name is required")
        
        if self.gdpr_consent is not True:
            errors.append("You must consent to data storage")
        
        return errors


# Required fields for different operations
PROFILE_REQUIRED_FIELDS = ['name', 'gdpr_consent']
MISSING_PERSON_REQUIRED_FIELDS = ['last_seen_date', 'last_seen_time', 'last_seen_location']
