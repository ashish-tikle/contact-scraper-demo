import logging
import re
from typing import List, Dict, Optional

def setup_logger(debug: bool) -> logging.Logger:
    """
    Configure and return a logger with console handler.
    
    Args:
        debug: If True, set level to DEBUG; otherwise INFO
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("contact_scraper")
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    logger.handlers.clear()
    
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG if debug else logging.INFO)
    
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger


def is_valid_email(email: str) -> bool:
    """
    Validate email address using RFC-lite regex pattern.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email matches basic validation pattern
    """
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def canonical_phone(phone: str) -> str:
    """
    Normalize phone number by keeping only leading '+' and digits.
    
    Args:
        phone: Phone number string to normalize
        
    Returns:
        Canonicalized phone number ('+' prefix preserved if present, digits only)
    """
    if not phone:
        return ""
    
    phone = phone.strip()
    has_plus = phone.startswith('+')
    digits = ''.join(c for c in phone if c.isdigit())
    
    return f"+{digits}" if has_plus and digits else digits


def dedupe_records(records: List[Dict]) -> List[Dict]:
    """
    Remove duplicate records based on normalized email and phone number.
    
    Uses (email.lower(), canonical_phone(phone)) as the deduplication key.
    Keeps the first occurrence of each unique record.
    
    Args:
        records: List of contact dictionaries
        
    Returns:
        Deduplicated list of records
    """
    seen = set()
    unique_records = []
    
    for record in records:
        email = (record.get('email') or '').lower()
        phone = canonical_phone(record.get('phone') or '')
        
        key = (email, phone)
        
        if key not in seen:
            seen.add(key)
            unique_records.append(record)
    
    return unique_records