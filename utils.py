def extract_coordinates(location_text: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Extract coordinates from location text if present.
    
    Args:
        location_text: Location description that may contain coordinates
        
    Returns:
        Tuple of (latitude, longitude) or (None, None) if not found
    """
    if not location_text:
        return None, None
    
    # Check for coordinates in format (Coordinates: 51.5074, -0.1278)
    if "coordinates:" in location_text.lower():
        try:
            # Extract the part after "Coordinates:"
            coords_part = location_text.lower().split("coordinates:")[1].strip()
            # Remove closing parenthesis if present
            if coords_part.endswith(')'):
                coords_part = coords_part[:-1]
            # Split by comma
            lat_str, lng_str = coords_part.split(',')
            return float(lat_str.strip()), float(lng_str.strip())
        except Exception as e:
            logger.error(f"Error extracting coordinates from '{location_text}': {str(e)}")
    
    return None, None

def geocode_location(location_text: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Geocode a location string to get coordinates.
    
    Args:
        location_text: Location description to geocode
        
    Returns:
        Tuple of (latitude, longitude) or (None, None) if geocoding fails
    """
    try:
        # First try to extract coordinates if they're already in the text
        lat, lng = extract_coordinates(location_text)
        if lat and lng:
            return lat, lng
        
        # Otherwise, try to geocode the location
        from geopy.geocoders import Nominatim
        from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
        
        geolocator = Nominatim(user_agent="learning_disability_profile_app")
        
        # Clean the location text - remove any coordinate parts
        if "coordinates:" in location_text.lower():
            clean_location = location_text.lower().split("coordinates:")[0].strip()
            # Remove trailing parenthesis if any
            if clean_location.endswith('('):
                clean_location = clean_location[:-1].strip()
        else:
            clean_location = location_text
        
        # If the clean location is empty, return None
        if not clean_location:
            return None, None
        
        # Try to geocode
        location = geolocator.geocode(clean_location)
        if location:
            return location.latitude, location.longitude
            
    except (GeocoderTimedOut, GeocoderUnavailable) as e:
        logger.warning(f"Geocoding service timed out or unavailable: {str(e)}")
    except Exception as e:
        logger.error(f"Error geocoding location '{location_text}': {str(e)}")
    
    return None, None

def generate_location_map(location_text: str, width: int = 800, height: int = 500) -> Optional[str]:
    """
    Generate an HTML map for a location.
    
    Args:
        location_text: Location description to map
        width: Width of the map in pixels
        height: Height of the map in pixels
        
    Returns:
        HTML string for the map, or None if mapping fails
    """
    try:
        import folium
        
        # Try to get coordinates from the location text
        lat, lng = geocode_location(location_text)
        
        if not lat or not lng:
            return None
        
        # Create a map centered at the location
        m = folium.Map(location=[lat, lng], zoom_start=15)
        
        # Add a marker for the location
        folium.Marker(
            [lat, lng],
            popup=location_text,
            tooltip="Last seen here",
            icon=folium.Icon(color="red", icon="info-sign")
        ).add_to(m)
        
        # Add a circle to indicate approximate area
        folium.Circle(
            radius=200,  # 200m radius around the point
            location=[lat, lng],
            color="red",
            fill=True,
            fill_color="red",
            fill_opacity=0.1
        ).add_to(m)
        
        # Return the HTML representation
        return m._repr_html_()
        
    except Exception as e:
        logger.error(f"Error generating map for location '{location_text}': {str(e)}")
        return None
