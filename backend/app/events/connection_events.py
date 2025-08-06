from flask_socketio import emit, join_room, leave_room
from app.services.user_service import UserService
from app.services.chat_service import ChatService
from app.utils.decorators import require_auth

class ConnectionEvents:
    @staticmethod
    def handle_connect(sid, data):
        """Handle client connection"""
        user_id = data.get('user_id')
        if not user_id:
            emit('error', {'message': 'User ID required for connection'})
            return False
        
        # Set user online
        result = UserService.set_user_online(user_id, sid)
        if not result['success']:
            emit('error', {'message': result['error']})
            return False
        
        # Emit connection success
        emit('connected', {
            'user_id': user_id,
            'message': 'Successfully connected'
        })
        
        # Emit online users list
        online_users = UserService.get_online_users()
        emit('online_users', {'users': online_users})
        
        # Emit available rooms
        rooms = ChatService.get_rooms()
        emit('available_rooms', {'rooms': rooms})
        
        return True
    
    @staticmethod
    def handle_disconnect(sid, data):
        """Handle client disconnection"""
        user_id = data.get('user_id')
        if user_id:
            # Set user offline
            UserService.set_user_offline(user_id)
            
            # Emit user went offline to all clients
            emit('user_offline', {
                'user_id': user_id,
                'message': 'User went offline'
            }, broadcast=True)
    
    @staticmethod
    @require_auth
    def handle_join_room(sid, data):
        """Handle joining a chat room"""
        user_id = data.get('user_id')
        room_id = data.get('room_id')
        
        if not room_id:
            emit('error', {'message': 'Room ID required'})
            return
        
        # Join the room
        join_room(room_id)
        
        # Add user to room in service
        result = ChatService.join_room(user_id, room_id)
        if not result['success']:
            emit('error', {'message': result['error']})
            return
        
        # Emit join confirmation
        emit('joined_room', {
            'room_id': room_id,
            'message': 'Successfully joined room'
        })
        
        # Emit to room that user joined
        emit('user_joined_room', {
            'user_id': user_id,
            'room_id': room_id,
            'username': UserService.get_user_by_id(user_id)['username']
        }, room=room_id)
        
        # Send recent messages
        messages = ChatService.get_room_messages(room_id, limit=20)
        emit('room_messages', {
            'room_id': room_id,
            'messages': messages
        })
    
    @staticmethod
    @require_auth
    def handle_leave_room(sid, data):
        """Handle leaving a chat room"""
        user_id = data.get('user_id')
        room_id = data.get('room_id')
        
        if not room_id:
            emit('error', {'message': 'Room ID required'})
            return
        
        # Leave the room
        leave_room(room_id)
        
        # Remove user from room in service
        result = ChatService.leave_room(user_id, room_id)
        if not result['success']:
            emit('error', {'message': result['error']})
            return
        
        # Emit leave confirmation
        emit('left_room', {
            'room_id': room_id,
            'message': 'Successfully left room'
        })
        
        # Emit to room that user left
        emit('user_left_room', {
            'user_id': user_id,
            'room_id': room_id,
            'username': UserService.get_user_by_id(user_id)['username']
        }, room=room_id)
    
    @staticmethod
    @require_auth
    def handle_heartbeat(sid, data):
        """Handle heartbeat to keep connection alive"""
        user_id = data.get('user_id')
        
        # Update user presence
        UserService.update_user_presence(user_id)
        
        # Emit heartbeat response
        emit('heartbeat_response', {
            'timestamp': '2024-01-01T00:00:00Z'
        }) 