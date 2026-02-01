import re
from typing import List, Dict, Optional, Set, Tuple
from bs4 import BeautifulSoup, Tag

"""
Parser module for extracting contact information from HTML using BeautifulSoup and regex.
"""



# Robust regex patterns for contact extraction
EMAIL_RE = re.compile(
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    re.IGNORECASE
)

PHONE_RE = re.compile(
    r'(?:\+?\d{1,3}[\s.-]?)?'  # Optional country code
    r'(?:\(?\d{2,4}\)?[\s.-]?)?'  # Optional area code
    r'\d{3,4}[\s.-]?\d{3,4}(?:[\s.-]?\d{1,4})?',  # Main number
    re.IGNORECASE
)

# Pattern for extracting names from text like "Name: John Doe" or "Contact - Jane Roe"
NAME_PATTERN = re.compile(
    r'(?:name|contact|person)[\s:=-]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
    re.IGNORECASE
)


def extract_contacts(html: str, source_url: str) -> List[Dict]:
    """
    Extract contact information from HTML content.
    
    Args:
        html: Raw HTML content as string
        source_url: URL of the source page
        
    Returns:
        List of contact dictionaries with keys: name, email, phone, source_url
    """
    soup = BeautifulSoup(html, 'lxml')
    
    # Combine both extraction strategies
    structured = _extract_structured(soup)
    text_based = _extract_candidates_via_text(soup)
    
    # Merge all contacts
    all_contacts = structured + text_based
    
    # Deduplicate using tuple of (name, email, phone)
    seen: Set[Tuple[Optional[str], Optional[str], Optional[str]]] = set()
    unique_contacts = []
    
    for contact in all_contacts:
        key = (
            contact.get('name', '').strip().lower() if contact.get('name') else None,
            contact.get('email', '').strip().lower() if contact.get('email') else None,
            contact.get('phone', '').strip() if contact.get('phone') else None
        )
        
        # Skip if all fields are empty or if already seen
        if not any(key) or key in seen:
            continue
            
        seen.add(key)
        contact['source_url'] = source_url
        unique_contacts.append(contact)
    
    return unique_contacts


def _extract_structured(soup: BeautifulSoup) -> List[Dict]:
    """
    Extract contacts from structured HTML elements like tables and mailto links.
    
    Args:
        soup: BeautifulSoup parsed HTML
        
    Returns:
        List of contact dictionaries
    """
    contacts = []
    
    # Strategy 1: Extract from tables
    contacts.extend(_extract_from_tables(soup))
    
    # Strategy 2: Extract mailto links
    contacts.extend(_extract_mailto_links(soup))
    
    # Strategy 3: Extract from semantic elements
    contacts.extend(_extract_semantic_elements(soup))
    
    return contacts


def _extract_from_tables(soup: BeautifulSoup) -> List[Dict]:
    """Extract contacts from HTML tables."""
    contacts = []
    
    for table in soup.find_all('table'):
        rows = table.find_all('tr')
        if not rows:
            continue
            
        # Try to detect header row
        header_row = rows[0]
        headers = [th.get_text(strip=True).lower() for th in header_row.find_all(['th', 'td'])]
        
        # Map column indices
        name_idx = email_idx = phone_idx = None
        for idx, header in enumerate(headers):
            if 'name' in header or 'contact' in header or 'person' in header:
                name_idx = idx
            elif 'email' in header or 'mail' in header:
                email_idx = idx
            elif 'phone' in header or 'tel' in header or 'mobile' in header:
                phone_idx = idx
        
        # Process data rows
        start_idx = 1 if any([name_idx, email_idx, phone_idx]) else 0
        for row in rows[start_idx:]:
            cells = row.find_all(['td', 'th'])
            if not cells:
                continue
                
            contact = {}
            
            # Extract based on column mapping
            if name_idx is not None and name_idx < len(cells):
                contact['name'] = cells[name_idx].get_text(strip=True)
            if email_idx is not None and email_idx < len(cells):
                contact['email'] = cells[email_idx].get_text(strip=True)
            if phone_idx is not None and phone_idx < len(cells):
                contact['phone'] = cells[phone_idx].get_text(strip=True)
            
            # Fallback: search all cells for patterns
            for cell in cells:
                text = cell.get_text(strip=True)
                if not contact.get('email'):
                    email_match = EMAIL_RE.search(text)
                    if email_match:
                        contact['email'] = email_match.group(0)
                if not contact.get('phone'):
                    phone_match = PHONE_RE.search(text)
                    if phone_match:
                        contact['phone'] = phone_match.group(0)
            
            if contact:
                contacts.append(contact)
    
    return contacts


def _extract_mailto_links(soup: BeautifulSoup) -> List[Dict]:
    """Extract contacts from mailto links."""
    contacts = []
    
    for link in soup.find_all('a', href=re.compile(r'^mailto:', re.IGNORECASE)):
        email = link.get('href', '').replace('mailto:', '').split('?')[0].strip()
        name = link.get_text(strip=True)
        
        if EMAIL_RE.match(email):
            contact = {'email': email}
            if name and name != email:
                contact['name'] = name
            contacts.append(contact)
    
    return contacts


def _extract_semantic_elements(soup: BeautifulSoup) -> List[Dict]:
    """Extract contacts from elements with semantic class/id names."""
    contacts = []
    semantic_patterns = ['name', 'fullname', 'contact', 'email', 'phone', 'tel', 'mobile']
    
    for pattern in semantic_patterns:
        # Find by class or id
        elements = soup.find_all(class_=re.compile(pattern, re.IGNORECASE))
        elements.extend(soup.find_all(id=re.compile(pattern, re.IGNORECASE)))
        
        for elem in elements:
            text = elem.get_text(strip=True)
            contact = {}
            
            if 'email' in pattern or 'mail' in pattern:
                email_match = EMAIL_RE.search(text)
                if email_match:
                    contact['email'] = email_match.group(0)
            elif 'phone' in pattern or 'tel' in pattern or 'mobile' in pattern:
                phone_match = PHONE_RE.search(text)
                if phone_match:
                    contact['phone'] = phone_match.group(0)
            elif 'name' in pattern or 'contact' in pattern:
                if text and len(text) > 2:
                    contact['name'] = text
            
            if contact:
                contacts.append(contact)
    
    return contacts


def _extract_candidates_via_text(soup: BeautifulSoup) -> List[Dict]:
    """
    Extract contacts using regex patterns on raw text content.
    
    Args:
        soup: BeautifulSoup parsed HTML
        
    Returns:
        List of contact dictionaries
    """
    contacts = []
    text = soup.get_text()
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        contact = {}
        
        # Extract email
        email_match = EMAIL_RE.search(line)
        if email_match:
            contact['email'] = email_match.group(0)
        
        # Extract phone
        phone_match = PHONE_RE.search(line)
        if phone_match:
            contact['phone'] = phone_match.group(0)
        
        # Extract name using heuristic patterns
        name_match = NAME_PATTERN.search(line)
        if name_match:
            contact['name'] = name_match.group(1).strip()
        
        if contact:
            contacts.append(contact)
    
    return contacts