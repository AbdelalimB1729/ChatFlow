import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.models import messages, chat_rooms, users, message_queue, Message, ChatRoom, TypingIndicator
from app.utils.validators import validate_message_content, validate_room_id, sanitize_input

class ChatService:
    @staticmethod
    def send_message(sender_id: str, content: str, room_id: str, message_type: str = 'text') -> Dict[str, Any]:
        """Send a message to a chat room"""
        content = sanitize_input(content)
        
        if not validate_message_content(content):
            return {'success': False, 'error': 'Invalid message content'}
        
        if not validate_room_id(room_id):
            return {'success': False, 'error': 'Invalid room ID'}
        
        if sender_id not in users:
            return {'success': False, 'error': 'User not found'}
        
        if room_id not in chat_rooms:
            return {'success': False, 'error': 'Room not found'}
        
        message_id = str(uuid.uuid4())
        message = Message(
            message_id=message_id,
            sender_id=sender_id,
            content=content,
            room_id=room_id,
            message_type=message_type
        )
        
        messages[message_id] = message
        chat_rooms[room_id].last_activity = datetime.utcnow()
        
        return {
            'success': True,
            'message': {
                'message_id': message_id,
                'sender_id': sender_id,
                'content': content,
                'room_id': room_id,
                'message_type': message_type,
                'timestamp': message.timestamp.isoformat(),
                'sender_username': users[sender_id].username
            }
        }
    
    @staticmethod
    def get_room_messages(room_id: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get messages for a specific room with pagination"""
        if room_id not in chat_rooms:
            return []
        
        room_messages = [
            msg for msg in messages.values() 
            if msg.room_id == room_id
        ]
        
        # Sort by timestamp (newest first)
        room_messages.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Apply pagination
        paginated_messages = room_messages[offset:offset + limit]
        
        return [
            {
                'message_id': msg.message_id,
                'sender_id': msg.sender_id,
                'content': msg.content,
                'room_id': msg.room_id,
                'message_type': msg.message_type,
                'timestamp': msg.timestamp.isoformat(),
                'sender_username': users[msg.sender_id].username if msg.sender_id in users else 'Unknown',
                'read_by': msg.read_by,
                'delivered_to': msg.delivered_to
            }
            for msg in paginated_messages
        ]
    
    @staticmethod
    def create_room(name: str, room_type: str = 'public', creator_id: str = None) -> Dict[str, Any]:
        """Create a new chat room"""
        name = sanitize_input(name)
        
        if not name or len(name.strip()) == 0:
            return {'success': False, 'error': 'Room name is required'}
        
        room_id = str(uuid.uuid4())
        room = ChatRoom(room_id=room_id, name=name, room_type=room_type)
        
        if creator_id and creator_id in users:
            room.members.append(creator_id)
        
        chat_rooms[room_id] = room
        
        return {
            'success': True,
            'room': {
                'room_id': room_id,
                'name': name,
                'room_type': room_type,
                'created_at': room.created_at.isoformat(),
                'member_count': len(room.members)
            }
        }
    
    @staticmethod
    def get_rooms() -> List[Dict[str, Any]]:
        """Get all available chat rooms"""
        return [
            {
                'room_id': room.room_id,
                'name': room.name,
                'room_type': room.room_type,
                'created_at': room.created_at.isoformat(),
                'last_activity': room.last_activity.isoformat(),
                'member_count': len(room.members)
            }
            for room in chat_rooms.values()
        ]
    
    @staticmethod
    def join_room(user_id: str, room_id: str) -> Dict[str, Any]:
        """Join a chat room"""
        if user_id not in users:
            return {'success': False, 'error': 'User not found'}
        
        if room_id not in chat_rooms:
            return {'success': False, 'error': 'Room not found'}
        
        room = chat_rooms[room_id]
        if user_id not in room.members:
            room.members.append(user_id)
        
        return {'success': True, 'message': 'Joined room successfully'}
    
    @staticmethod
    def leave_room(user_id: str, room_id: str) -> Dict[str, Any]:
        """Leave a chat room"""
        if room_id not in chat_rooms:
            return {'success': False, 'error': 'Room not found'}
        
        room = chat_rooms[room_id]
        if user_id in room.members:
            room.members.remove(user_id)
        
        return {'success': True, 'message': 'Left room successfully'}
    
    @staticmethod
    def mark_message_read(user_id: str, message_id: str) -> Dict[str, Any]:
        """Mark a message as read"""
        if message_id not in messages:
            return {'success': False, 'error': 'Message not found'}
        
        message = messages[message_id]
        if user_id not in message.read_by:
            message.read_by.append(user_id)
        
        return {'success': True}
    
    @staticmethod
    def mark_message_delivered(user_id: str, message_id: str) -> Dict[str, Any]:
        """Mark a message as delivered"""
        if message_id not in messages:
            return {'success': False, 'error': 'Message not found'}
        
        message = messages[message_id]
        if user_id not in message.delivered_to:
            message.delivered_to.append(user_id)
        
        return {'success': True}
    
    @staticmethod
    def set_typing_indicator(user_id: str, room_id: str, is_typing: bool) -> Dict[str, Any]:
        """Set typing indicator for a user in a room"""
        if user_id not in users:
            return {'success': False, 'error': 'User not found'}
        
        if room_id not in chat_rooms:
            return {'success': False, 'error': 'Room not found'}
        
        indicator_key = f"{user_id}_{room_id}"
        
        if is_typing:
            typing_indicator = TypingIndicator(user_id=user_id, room_id=room_id)
            typing_indicators[indicator_key] = typing_indicator
        else:
            typing_indicators.pop(indicator_key, None)
        
        return {'success': True}
    
    @staticmethod
    def get_typing_users(room_id: str) -> List[str]:
        """Get list of users currently typing in a room"""
        current_time = datetime.utcnow()
        typing_users = []
        
        for indicator in typing_indicators.values():
            if (indicator.room_id == room_id and 
                (current_time - indicator.timestamp).seconds < 5):
                typing_users.append(indicator.user_id)
        
        return typing_users 