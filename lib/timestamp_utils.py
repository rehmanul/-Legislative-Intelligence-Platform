"""
Timestamp Utilities
Normalize and parse timestamps with edge case handling.
"""

import re
from datetime import datetime, timezone, timedelta
from typing import Optional


def normalize_timestamp(ts_str: str) -> str:
    """
    Normalize timestamp string to ISO-8601 UTC format.
    
    Handles:
    - Double timezone suffixes (+00:00+00:00)
    - Z suffix conversion
    - Mixed formats
    """
    if not ts_str:
        return ""
    
    # Remove double timezone suffixes (e.g., +00:00+00:00 -> +00:00)
    ts_str = re.sub(r'([+-]\d{2}:\d{2})([+-]\d{2}:\d{2})$', r'\1', ts_str)
    
    # Convert Z to +00:00
    if ts_str.endswith('Z'):
        ts_str = ts_str[:-1] + '+00:00'
    
    # Ensure timezone if missing
    if not re.search(r'[+-]\d{2}:\d{2}$', ts_str):
        # If no timezone, assume UTC
        if 'T' in ts_str:
            ts_str = ts_str + '+00:00'
        else:
            # Date only, add time and timezone
            ts_str = ts_str + 'T00:00:00+00:00'
    
    return ts_str


def parse_timestamp(ts_str: str) -> Optional[datetime]:
    """
    Parse ISO timestamp to datetime object with robust error handling.
    
    Handles:
    - Double timezone suffixes
    - Mixed offset-naive and offset-aware
    - Invalid ISO formats
    - Missing timezones (assumes UTC)
    """
    if not ts_str:
        return None
    
    try:
        # Normalize first
        normalized = normalize_timestamp(ts_str)
        
        # Parse with fromisoformat
        dt = datetime.fromisoformat(normalized)
        
        # Ensure timezone-aware (default to UTC if naive)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        
        return dt
    except (ValueError, AttributeError) as e:
        # Try fallback parsing
        try:
            # Try common formats
            formats = [
                '%Y-%m-%dT%H:%M:%S.%f%z',
                '%Y-%m-%dT%H:%M:%S%z',
                '%Y-%m-%dT%H:%M:%S.%fZ',
                '%Y-%m-%dT%H:%M:%SZ',
                '%Y-%m-%dT%H:%M:%S',
            ]
            
            for fmt in formats:
                try:
                    dt = datetime.strptime(ts_str.replace('Z', '+00:00'), fmt)
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    return dt
                except ValueError:
                    continue
            
            # Last resort: try to extract date/time components
            match = re.match(r'(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2})(?:\.(\d+))?(?:([+-]\d{2}:\d{2})|Z)?', ts_str)
            if match:
                date_str, time_str, micro_str, tz_str = match.groups()
                dt_str = f"{date_str}T{time_str}"
                if micro_str:
                    dt_str += f".{micro_str[:6]}"  # Limit microseconds to 6 digits
                
                dt = datetime.fromisoformat(dt_str)
                if tz_str:
                    # Parse timezone offset
                    tz_match = re.match(r'([+-])(\d{2}):(\d{2})', tz_str)
                    if tz_match:
                        sign, hours, minutes = tz_match.groups()
                        offset = int(hours) * 60 + int(minutes)
                        if sign == '-':
                            offset = -offset
                        dt = dt.replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(minutes=offset)))
                    else:
                        dt = dt.replace(tzinfo=timezone.utc)
                else:
                    dt = dt.replace(tzinfo=timezone.utc)
                
                return dt
            
            return None
        except Exception:
            return None


def ensure_timezone_aware(dt: datetime) -> datetime:
    """
    Ensure datetime is timezone-aware (defaults to UTC if naive).
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def format_timestamp(dt: datetime) -> str:
    """
    Format datetime to ISO-8601 UTC string (Z suffix).
    """
    dt = ensure_timezone_aware(dt)
    # Convert to UTC
    dt_utc = dt.astimezone(timezone.utc)
    # Format with Z suffix
    return dt_utc.isoformat().replace('+00:00', 'Z')
