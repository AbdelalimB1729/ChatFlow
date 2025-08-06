from flask_socketio import emit
from app.services.chat_service import ChatService
from app.services.user_service import UserService
from app.utils.decorators import require_auth, rate_limit_messages, validate_message_data

class MessageEvents:
    @staticmethod
    @require_auth
    @rate_limit_messages()
    @validate_message_data
    def handle_send_message(sid, data):
        """Handle sending a message"""
        user_id = data.get('user_id')
        content = data.get('content')
        room_id = data.get('room_id')
        message_type = data.get('message_type', 'text')
        
        # Send message through service
        result = ChatService.send_message(user_id, content, room_id, message_type)
        if not result['success']:
            emit('error', {'message': result['error']})
            return
        
        message_data = result['message']
        
        # Emit message to room
        emit('new_message', message_data, room=room_id)
        
        # Emit delivery confirmation to sender
        emit('message_sent', {
            'message_id': message_data['message_id'],
            'timestamp': message_data['timestamp']
        })
    
    @staticmethod
    @require_auth
    def handle_mark_read(sid, data):
        """Handle marking a message as read"""
        user_id = data.get('user_id')
        message_id = data.get('message_id')
        
        if not message_id:
            emit('error', {'message': 'Message ID required'})
            return
        
        result = ChatService.mark_message_read(user_id, message_id)
        if not result['success']:
            emit('error', {'message': result['error']})
            return
        
        # Emit read receipt to room
        emit('message_read', {
            'message_id': message_id,
            'user_id': user_id,
            'timestamp': '2024-01-01T00:00:00Z'
        }, broadcast=True)
    
    @staticmethod
    @require_auth
    def handle_mark_delivered(sid, data):
        """Handle marking a message as delivered"""
        user_id = data.get('user_id')
        message_id = data.get('message_id')
        
        if not message_id:
            emit('error', {'message': 'Message ID required'})
            return
        
        result = ChatService.mark_message_delivered(user_id, message_id)
        if not result['success']:
            emit('error', {'message': result['error']})
            return
        
        # Emit delivery receipt to room
        emit('message_delivered', {
            'message_id': message_id,
            'user_id': user_id,
            'timestamp': '2024-01-01T00:00:00Z'
        }, broadcast=True)
    
    @staticmethod
    @require_auth
    def handle_get_messages(sid, data):
        """Handle getting messages for a room"""
        room_id = data.get('room_id')
        limit = data.get('limit', 50)
        offset = data.get('offset', 0)
        
        if not room_id:
            emit('error', {'message': 'Room ID required'})
            return
        
        messages = ChatService.get_room_messages(room_id, limit, offset)
        emit('room_messages', {
            'room_id': room_id,
            'messages': messages,
            'limit': limit,
            'offset': offset
        })
    
    @staticmethod
    @require_auth
    def handle_typing_start(sid, data):
        """Handle typing start indicator"""
        user_id = data.get('user_id')
        room_id = data.get('room_id')
        
        if not room_id:
            emit('error', {'message': 'Room ID required'})
            return
        
        # Set typing indicator
        result = ChatService.set_typing_indicator(user_id, room_id, True)
        if not result['success']:
            emit('error', {'message': result['error']})
            return
        
        # Emit typing indicator to room
        emit('user_typing', {
            'user_id': user_id,
            'room_id': room_id,
            'username': UserService.get_user_by_id(user_id)['username'],
            'is_typing': True
        }, room=room_id)
    
    @staticmethod
    @require_auth
    def handle_typing_stop(sid, data):
        """Handle typing stop indicator"""
        user_id = data.get('user_id')
        room_id = data.get('room_id')
        
        if not room_id:
            emit('error', {'message': 'Room ID required'})
            return
        
        # Remove typing indicator
        result = ChatService.set_typing_indicator(user_id, room_id, False)
        if not result['success']:
            emit('error', {'message': result['error']})
            return
        
        # Emit typing stop to room
        emit('user_typing', {
            'user_id': user_id,
            'room_id': room_id,
            'username': UserService.get_user_by_id(user_id)['username'],
            'is_typing': False
        }, room=room_id)
    
    @staticmethod
    @require_auth
    def handle_get_typing_users(sid, data):
        """Handle getting typing users in a room"""
        room_id = data.get('room_id')
        
        if not room_id:
            emit('error', {'message': 'Room ID required'})
            return
        
        typing_users = ChatService.get_typing_users(room_id)
        emit('typing_users', {
            'room_id': room_id,
            'users': typing_users
        }) 