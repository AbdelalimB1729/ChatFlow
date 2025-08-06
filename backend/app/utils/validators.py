import re
from typing import Dict, Any, List

def validate_username(username: str) -> bool:
    """Validate username format"""
    if not username or len(username) < 3 or len(username) > 20:
        return False
    return bool(re.match(r'^[a-zA-Z0-9_]+$', username))

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_message_content(content: str) -> bool:
    """Validate message content"""
    if not content or len(content.strip()) == 0:
        return False
    if len(content) > 1000:
        return False
    return True

def validate_room_id(room_id: str) -> bool:
    """Validate room ID format"""
    if not room_id or len(room_id) < 1:
        return False
    return True

def sanitize_input(text: str) -> str:
    """Sanitize user input"""
    if not text:
        return ""
    # Remove potentially dangerous characters
    text = re.sub(r'[<>]', '', text)
    return text.strip()

def validate_user_data(data: Dict[str, Any]) -> List[str]:
    """Validate user registration data"""
    errors = []
    
    if not validate_username(data.get('username', '')):
        errors.append('Invalid username format')
    
    if not validate_email(data.get('email', '')):
        errors.append('Invalid email format')
    
    if len(data.get('password', '')) < 6:
        errors.append('Password must be at least 6 characters')
    
    return errors 