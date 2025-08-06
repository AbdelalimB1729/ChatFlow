from datetime import datetime
from typing import Dict, List, Optional
import uuid

class User:
    def __init__(self, user_id: str, username: str, email: str):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.is_online = False
        self.last_seen = datetime.utcnow()
        self.typing_in = None
        self.socket_id = None
        self.created_at = datetime.utcnow()

class Message:
    def __init__(self, message_id: str, sender_id: str, content: str, room_id: str, message_type: str = 'text'):
        self.message_id = message_id
        self.sender_id = sender_id
        self.content = content
        self.room_id = room_id
        self.message_type = message_type
        self.timestamp = datetime.utcnow()
        self.read_by = []
        self.delivered_to = []

class ChatRoom:
    def __init__(self, room_id: str, name: str, room_type: str = 'public'):
        self.room_id = room_id
        self.name = name
        self.room_type = room_type
        self.members = []
        self.created_at = datetime.utcnow()
        self.last_activity = datetime.utcnow()

class TypingIndicator:
    def __init__(self, user_id: str, room_id: str):
        self.user_id = user_id
        self.room_id = room_id
        self.timestamp = datetime.utcnow()

# In-memory storage
users: Dict[str, User] = {}
messages: Dict[str, Message] = {}
chat_rooms: Dict[str, ChatRoom] = {}
typing_indicators: Dict[str, TypingIndicator] = {}
message_queue: List[Message] = [] 