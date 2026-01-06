"""
Utility functions for the application
"""
from flask_jwt_extended import get_jwt_identity
from datetime import datetime


def get_current_user_id():
    """
    Get current user ID from JWT token
    Returns integer user ID
    """
    user_id_str = get_jwt_identity()
    return int(user_id_str) if user_id_str else None


def parse_datetime(date_string):
    """
    Parse datetime string from frontend (ISO 8601 format with 'Z')
    Handles formats like: '2025-10-29T16:00:00.000Z' or '2025-10-29T16:00:00Z'
    Returns datetime object or None
    """
    if not date_string:
        return None
    
    try:
        # Remove 'Z' and milliseconds, replace with UTC offset
        if date_string.endswith('Z'):
            # Remove 'Z'
            date_string = date_string[:-1]
            # Remove milliseconds if present (.000, .123, etc.)
            if '.' in date_string:
                date_string = date_string.split('.')[0]
            # Parse as UTC datetime
            return datetime.fromisoformat(date_string)
        else:
            return datetime.fromisoformat(date_string)
    except Exception as e:
        print(f"Error parsing datetime '{date_string}': {e}")
        return None

