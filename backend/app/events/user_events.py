from flask_socketio import emit
from app.services.user_service import UserService
from app.services.chat_service import ChatService
from app.utils.decorators import require_auth

class UserEvents:
    @staticmethod
    @require_auth
    def handle_get_online_users(sid, data):
        """Handle getting online users"""
        online_users = UserService.get_online_users()
        emit('online_users', {'users': online_users})
    
    @staticmethod
    @require_auth
    def handle_get_all_users(sid, data):
        """Handle getting all users"""
        all_users = UserService.get_all_users()
        emit('all_users', {'users': all_users})
    
    @staticmethod
    @require_auth
    def handle_get_user_profile(sid, data):
        """Handle getting user profile"""
        user_id = data.get('user_id')
        target_user_id = data.get('target_user_id', user_id)
        
        profile = UserService.get_user_profile(target_user_id)
        if not profile:
            emit('error', {'message': 'User not found'})
            return
        
        emit('user_profile', {'profile': profile})
    
    @staticmethod
    @require_auth
    def handle_search_users(sid, data):
        """Handle searching users"""
        query = data.get('query', '')
        
        if not query:
            emit('error', {'message': 'Search query required'})
            return
        
        matching_users = UserService.search_users(query)
        emit('search_results', {'users': matching_users})
    
    @staticmethod
    @require_auth
    def handle_get_user_statistics(sid, data):
        """Handle getting user statistics"""
        user_id = data.get('user_id')
        
        stats = UserService.get_user_statistics(user_id)
        if 'error' in stats:
            emit('error', {'message': stats['error']})
            return
        
        emit('user_statistics', {'statistics': stats})
    
    @staticmethod
    @require_auth
    def handle_create_room(sid, data):
        """Handle creating a new chat room"""
        user_id = data.get('user_id')
        room_name = data.get('room_name')
        room_type = data.get('room_type', 'public')
        
        if not room_name:
            emit('error', {'message': 'Room name required'})
            return
        
        result = ChatService.create_room(room_name, room_type, user_id)
        if not result['success']:
            emit('error', {'message': result['error']})
            return
        
        # Emit room created to all clients
        emit('room_created', result['room'], broadcast=True)
        
        # Emit confirmation to creator
        emit('room_created_confirmation', {
            'message': 'Room created successfully',
            'room': result['room']
        })
    
    @staticmethod
    @require_auth
    def handle_get_rooms(sid, data):
        """Handle getting all available rooms"""
        rooms = ChatService.get_rooms()
        emit('available_rooms', {'rooms': rooms})
    
    @staticmethod
    @require_auth
    def handle_update_presence(sid, data):
        """Handle updating user presence"""
        user_id = data.get('user_id')
        
        result = UserService.update_user_presence(user_id)
        if not result['success']:
            emit('error', {'message': result['error']})
            return
        
        # Emit presence update to all clients
        emit('user_presence_updated', {
            'user_id': user_id,
            'timestamp': '2024-01-01T00:00:00Z'
        }, broadcast=True)
    
    @staticmethod
    @require_auth
    def handle_set_typing_status(sid, data):
        """Handle setting user typing status"""
        user_id = data.get('user_id')
        room_id = data.get('room_id')
        is_typing = data.get('is_typing', False)
        
        if not room_id:
            emit('error', {'message': 'Room ID required'})
            return
        
        result = UserService.set_typing_status(user_id, room_id, is_typing)
        if not result['success']:
            emit('error', {'message': result['error']})
            return
        
        # Emit typing status to room
        emit('user_typing_status', {
            'user_id': user_id,
            'room_id': room_id,
            'is_typing': is_typing,
            'username': UserService.get_user_by_id(user_id)['username']
        }, room=room_id) 