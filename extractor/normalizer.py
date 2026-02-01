from .utils import canonical_phone

"""Normalization helpers for contact data."""



def normalize_name(name: str) -> str:
    """Collapse whitespace and convert to Title Case.
    
    Args:
        name: Raw name string
        
    Returns:
        Normalized name in Title Case
    """
    return ' '.join(name.split()).title()


def normalize_email(email: str) -> str:
    """Strip whitespace and convert to lowercase.
    
    Args:
        email: Raw email string
        
    Returns:
        Normalized email in lowercase
    """
    return email.strip().lower()


def normalize_phone(phone: str) -> str:
    """Normalize phone number using canonical format.
    
    Args:
        phone: Raw phone number string
        
    Returns:
        Canonicalized phone number
    """
    return canonical_phone(phone)


def normalize_record(r: dict) -> dict:
    """Normalize all fields in a contact record.
    
    Args:
        r: Dictionary containing contact fields (name, email, phone, source_url)
        
    Returns:
        New dictionary with normalized field values
    """
    normalized = {}
    
    if 'name' in r:
        normalized['name'] = normalize_name(r['name'])
    if 'email' in r:
        normalized['email'] = normalize_email(r['email'])
    if 'phone' in r:
        normalized['phone'] = normalize_phone(r['phone'])
    if 'source_url' in r:
        normalized['source_url'] = r['source_url'].strip()
    
    return normalized