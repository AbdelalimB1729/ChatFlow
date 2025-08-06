import jwt
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from app.models import users, User
from app.config import Config
from app.utils.validators import validate_username, validate_email, sanitize_input

class AuthService:
    @staticmethod
    def generate_token(user_id: str) -> str:
        """Generate JWT token for user"""
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(days=1),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm='HS256')
    
    @staticmethod
    def verify_token(token: str) -> Optional[str]:
        """Verify JWT token and return user_id"""
        try:
            payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
            return payload.get('user_id')
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    @staticmethod
    def register_user(username: str, email: str, password: str) -> Dict[str, Any]:
        """Register a new user"""
        username = sanitize_input(username)
        email = sanitize_input(email)
        
        # Check if user already exists
        for user in users.values():
            if user.username == username:
                return {'success': False, 'error': 'Username already exists'}
            if user.email == email:
                return {'success': False, 'error': 'Email already exists'}
        
        # Validate input
        if not validate_username(username):
            return {'success': False, 'error': 'Invalid username format'}
        if not validate_email(email):
            return {'success': False, 'error': 'Invalid email format'}
        if len(password) < 6:
            return {'success': False, 'error': 'Password too short'}
        
        # Create new user
        user_id = str(uuid.uuid4())
        user = User(user_id=user_id, username=username, email=email)
        users[user_id] = user
        
        token = AuthService.generate_token(user_id)
        return {
            'success': True,
            'user': {
                'user_id': user_id,
                'username': username,
                'email': email
            },
            'token': token
        }
    
    @staticmethod
    def login_user(username: str, password: str) -> Dict[str, Any]:
        """Login user (simplified - no password verification in this demo)"""
        username = sanitize_input(username)
        
        # Find user by username
        user = None
        for u in users.values():
            if u.username == username:
                user = u
                break
        
        if not user:
            return {'success': False, 'error': 'User not found'}
        
        # In a real app, verify password here
        # For demo purposes, we'll accept any password
        
        token = AuthService.generate_token(user.user_id)
        return {
            'success': True,
            'user': {
                'user_id': user.user_id,
                'username': user.username,
                'email': user.email
            },
            'token': token
        }
    
    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[User]:
        """Get user by ID"""
        return users.get(user_id)
    
    @staticmethod
    def get_user_by_token(token: str) -> Optional[User]:
        """Get user by JWT token"""
        user_id = AuthService.verify_token(token)
        if user_id:
            return users.get(user_id)
        return None 