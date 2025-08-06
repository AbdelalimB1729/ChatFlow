import re
from typing import Dict, Optional, Union
from email_validator import validate_email as validate_email_format, EmailNotValidError
import magic
from werkzeug.datastructures import FileStorage

# Regex patterns
USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{3,32}$')
PASSWORD_PATTERN = re.compile(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$')
ROOM_NAME_PATTERN = re.compile(r'^[\w\s-]{3,100}$')
URL_PATTERN = re.compile(
    r'^https?:\/\/'  # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE
)

def validate_email(email: str) -> bool:
    """
    Validate email format and domain.
    
    Args:
        email: Email address to validate
        
    Returns:
        bool: True if email is valid
    """
    try:
        validate_email_format(email)
        return True
    except EmailNotValidError:
        return False

def validate_password_strength(password: str) -> Dict[str, bool]:
    """
    Validate password strength against multiple criteria.
    
    Args:
        password: Password to validate
        
    Returns:
        Dict with validation results for each criterion
    """
    results = {
        'length': len(password) >= 8,
        'uppercase': bool(re.search(r'[A-Z]', password)),
        'lowercase': bool(re.search(r'[a-z]', password)),
        'numbers': bool(re.search(r'\d', password)),
        'special': bool(re.search(r'[@$!%*#?&]', password)),
        'no_common': not _is_common_password(password),
        'no_personal': True  # Would need user info to check
    }
    
    results['valid'] = all(results.values())
    return results

def validate_username(username: str) -> bool:
    """
    Validate username format.
    
    Args:
        username: Username to validate
        
    Returns:
        bool: True if username is valid
    """
    return bool(USERNAME_PATTERN.match(username))

def validate_room_name(name: str) -> bool:
    """
    Validate chat room name.
    
    Args:
        name: Room name to validate
        
    Returns:
        bool: True if room name is valid
    """
    return bool(ROOM_NAME_PATTERN.match(name))

def validate_message_content(
    content: str,
    message_type: str = 'text',
    max_length: int = 5000
) -> bool:
    """
    Validate chat message content.
    
    Args:
        content: Message content to validate
        message_type: Type of message ('text', 'html', etc.)
        max_length: Maximum allowed length
        
    Returns:
        bool: True if content is valid
    """
    if not content or len(content) > max_length:
        return False
        
    if message_type == 'text':
        return True
    elif message_type == 'html':
        return _is_safe_html(content)
    else:
        return False

def validate_file_upload(
    file: FileStorage,
    allowed_types: Optional[Dict[str, list]] = None,
    max_size: int = 10 * 1024 * 1024  # 10MB
) -> Dict[str, Union[bool, str]]:
    """
    Validate file upload.
    
    Args:
        file: File to validate
        allowed_types: Dict of allowed MIME types and extensions
        max_size: Maximum file size in bytes
        
    Returns:
        Dict with validation results and detected type
    """
    if not file:
        return {'valid': False, 'error': 'No file provided'}
        
    # Check file size
    file.seek(0, 2)  # Seek to end
    size = file.tell()
    file.seek(0)  # Reset position
    
    if size > max_size:
        return {'valid': False, 'error': 'File too large'}
        
    # Detect MIME type
    mime_type = magic.from_buffer(file.read(2048), mime=True)
    file.seek(0)  # Reset position
    
    if allowed_types and mime_type not in allowed_types:
        return {'valid': False, 'error': 'Invalid file type'}
        
    # Validate extension if provided
    if allowed_types and file.filename:
        ext = file.filename.rsplit('.', 1)[-1].lower()
        if ext not in allowed_types.get(mime_type, []):
            return {'valid': False, 'error': 'Invalid file extension'}
            
    return {
        'valid': True,
        'mime_type': mime_type,
        'size': size
    }

def validate_url(url: str) -> bool:
    """
    Validate URL format.
    
    Args:
        url: URL to validate
        
    Returns:
        bool: True if URL is valid
    """
    return bool(URL_PATTERN.match(url))

def sanitize_html(html: str) -> str:
    """
    Sanitize HTML content.
    
    Args:
        html: HTML content to sanitize
        
    Returns:
        str: Sanitized HTML
    """
    from bs4 import BeautifulSoup
    
    # Define allowed tags and attributes
    allowed_tags = {
        'a': ['href', 'title'],
        'b': [],
        'i': [],
        'strong': [],
        'em': [],
        'p': [],
        'br': [],
        'ul': [],
        'ol': [],
        'li': [],
        'code': [],
        'pre': []
    }
    
    soup = BeautifulSoup(html, 'html.parser')
    
    for tag in soup.find_all(True):
        if tag.name not in allowed_tags:
            tag.unwrap()
        else:
            # Remove disallowed attributes
            allowed_attrs = allowed_tags[tag.name]
            for attr in list(tag.attrs):
                if attr not in allowed_attrs:
                    del tag[attr]
                    
            # Sanitize URLs in href attributes
            if 'href' in tag.attrs:
                if not validate_url(tag['href']):
                    del tag['href']
                    
    return str(soup)

def _is_common_password(password: str) -> bool:
    """
    Check if password is in list of common passwords.
    
    Args:
        password: Password to check
        
    Returns:
        bool: True if password is common
    """
    # This would typically check against a database or file of common passwords
    common_passwords = {'password', '123456', 'qwerty', 'letmein'}
    return password.lower() in common_passwords

def _is_safe_html(html: str) -> bool:
    """
    Check if HTML content is safe.
    
    Args:
        html: HTML content to check
        
    Returns:
        bool: True if HTML is safe
    """
    # This is a basic check - production code should use a proper HTML sanitizer
    dangerous_patterns = [
        r'<script',
        r'javascript:',
        r'onerror=',
        r'onclick=',
        r'onload=',
        r'<iframe',
        r'<object',
        r'<embed'
    ]
    
    return not any(re.search(pattern, html, re.IGNORECASE) 
                  for pattern in dangerous_patterns)

def validate_phone_number(phone: str) -> bool:
    """
    Validate phone number format.
    
    Args:
        phone: Phone number to validate
        
    Returns:
        bool: True if phone number is valid
    """
    # This is a basic check - production code should use a proper phone number library
    pattern = re.compile(r'^\+?1?\d{9,15}$')
    return bool(pattern.match(phone))

def validate_json_structure(
    data: Dict,
    required_fields: Dict[str, type]
) -> Dict[str, Union[bool, list]]:
    """
    Validate JSON data structure.
    
    Args:
        data: JSON data to validate
        required_fields: Dict of required fields and their types
        
    Returns:
        Dict with validation results and errors
    """
    errors = []
    
    for field, field_type in required_fields.items():
        if field not in data:
            errors.append(f"Missing required field: {field}")
        elif not isinstance(data[field], field_type):
            errors.append(
                f"Invalid type for field {field}. "
                f"Expected {field_type.__name__}, got {type(data[field]).__name__}"
            )
            
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }