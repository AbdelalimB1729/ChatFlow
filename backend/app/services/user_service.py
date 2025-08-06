from datetime import datetime
from typing import List, Dict, Any, Optional
from app.models import users, User
from app.utils.validators import validate_username, sanitize_input

class UserService:
    @staticmethod
    def get_online_users() -> List[Dict[str, Any]]:
        """Get all online users"""
        online_users = []
        for user in users.values():
            if user.is_online:
                online_users.append({
                    'user_id': user.user_id,
                    'username': user.username,
                    'email': user.email,
                    'last_seen': user.last_seen.isoformat(),
                    'is_online': user.is_online
                })
        return online_users
    
    @staticmethod
    def get_all_users() -> List[Dict[str, Any]]:
        """Get all users"""
        return [
            {
                'user_id': user.user_id,
                'username': user.username,
                'email': user.email,
                'last_seen': user.last_seen.isoformat(),
                'is_online': user.is_online,
                'created_at': user.created_at.isoformat()
            }
            for user in users.values()
        ]
    
    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        user = users.get(user_id)
        if user:
            return {
                'user_id': user.user_id,
                'username': user.username,
                'email': user.email,
                'last_seen': user.last_seen.isoformat(),
                'is_online': user.is_online,
                'created_at': user.created_at.isoformat()
            }
        return None
    
    @staticmethod
    def set_user_online(user_id: str, socket_id: str) -> Dict[str, Any]:
        """Set user as online"""
        if user_id not in users:
            return {'success': False, 'error': 'User not found'}
        
        user = users[user_id]
        user.is_online = True
        user.last_seen = datetime.utcnow()
        user.socket_id = socket_id
        
        return {'success': True, 'message': 'User set online'}
    
    @staticmethod
    def set_user_offline(user_id: str) -> Dict[str, Any]:
        """Set user as offline"""
        if user_id not in users:
            return {'success': False, 'error': 'User not found'}
        
        user = users[user_id]
        user.is_online = False
        user.last_seen = datetime.utcnow()
        user.socket_id = None
        user.typing_in = None
        
        return {'success': True, 'message': 'User set offline'}
    
    @staticmethod
    def update_user_presence(user_id: str) -> Dict[str, Any]:
        """Update user's last seen timestamp"""
        if user_id not in users:
            return {'success': False, 'error': 'User not found'}
        
        user = users[user_id]
        user.last_seen = datetime.utcnow()
        
        return {'success': True}
    
    @staticmethod
    def set_typing_status(user_id: str, room_id: str, is_typing: bool) -> Dict[str, Any]:
        """Set user's typing status in a room"""
        if user_id not in users:
            return {'success': False, 'error': 'User not found'}
        
        user = users[user_id]
        if is_typing:
            user.typing_in = room_id
        else:
            user.typing_in = None
        
        return {'success': True}
    
    @staticmethod
    def get_user_profile(user_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed user profile"""
        user = users.get(user_id)
        if not user:
            return None
        
        return {
            'user_id': user.user_id,
            'username': user.username,
            'email': user.email,
            'is_online': user.is_online,
            'last_seen': user.last_seen.isoformat(),
            'created_at': user.created_at.isoformat(),
            'typing_in': user.typing_in,
            'socket_id': user.socket_id
        }
    
    @staticmethod
    def search_users(query: str) -> List[Dict[str, Any]]:
        """Search users by username or email"""
        query = sanitize_input(query).lower()
        if not query:
            return []
        
        matching_users = []
        for user in users.values():
            if (query in user.username.lower() or 
                query in user.email.lower()):
                matching_users.append({
                    'user_id': user.user_id,
                    'username': user.username,
                    'email': user.email,
                    'is_online': user.is_online,
                    'last_seen': user.last_seen.isoformat()
                })
        
        return matching_users
    
    @staticmethod
    def get_user_statistics(user_id: str) -> Dict[str, Any]:
        """Get user statistics"""
        user = users.get(user_id)
        if not user:
            return {'error': 'User not found'}
        
        # Calculate some basic statistics
        total_users = len(users)
        online_users = len([u for u in users.values() if u.is_online])
        
        return {
            'user_id': user_id,
            'username': user.username,
            'total_users': total_users,
            'online_users': online_users,
            'user_created_at': user.created_at.isoformat(),
            'last_seen': user.last_seen.isoformat(),
            'is_online': user.is_online
        } 