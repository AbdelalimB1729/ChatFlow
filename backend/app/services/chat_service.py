from datetime import datetime
from typing import Dict, List, Optional, Tuple

from sqlalchemy import and_, or_

from ..extensions import db, redis_client
from ..models import ChatRoom, Message, User, ChatRoomMember
from ..utils.validators import validate_message_content

class ChatService:
    @classmethod
    def create_room(cls, creator_id: int, name: str, is_private: bool = False, 
                   member_ids: Optional[List[int]] = None) -> ChatRoom:
        """Create a new chat room."""
        # Validate room name
        if not name or len(name) > 100:
            raise ValueError("Invalid room name")

        # Create room
        room = ChatRoom(
            name=name,
            creator_id=creator_id,
            is_private=is_private,
            created_at=datetime.utcnow()
        )
        db.session.add(room)
        db.session.flush()  # Get room ID without committing

        # Add creator as member and admin
        creator_member = ChatRoomMember(
            room_id=room.id,
            user_id=creator_id,
            is_admin=True,
            joined_at=datetime.utcnow()
        )
        db.session.add(creator_member)

        # Add other members if provided
        if member_ids:
            for member_id in member_ids:
                if member_id != creator_id:
                    member = ChatRoomMember(
                        room_id=room.id,
                        user_id=member_id,
                        joined_at=datetime.utcnow()
                    )
                    db.session.add(member)

        db.session.commit()
        return room

    @classmethod
    def send_message(cls, room_id: int, sender_id: int, content: str, 
                    message_type: str = 'text', file_url: Optional[str] = None) -> Message:
        """Send a message to a chat room."""
        # Validate membership
        if not cls.is_room_member(room_id, sender_id):
            raise ValueError("User is not a member of this room")

        # Validate content
        if not validate_message_content(content, message_type):
            raise ValueError("Invalid message content")

        # Create message
        message = Message(
            room_id=room_id,
            sender_id=sender_id,
            content=content,
            message_type=message_type,
            file_url=file_url,
            sent_at=datetime.utcnow()
        )
        db.session.add(message)
        db.session.commit()

        # Update room's last activity
        cls._update_room_activity(room_id)

        # Store in Redis for real-time features
        cls._cache_message(message)

        return message

    @classmethod
    def get_room_messages(cls, room_id: int, user_id: int, 
                         page: int = 1, per_page: int = 50) -> Tuple[List[Message], bool]:
        """Get paginated messages for a room."""
        if not cls.is_room_member(room_id, user_id):
            raise ValueError("User is not a member of this room")

        # Try getting from cache first
        cached_messages = cls._get_cached_messages(room_id, page, per_page)
        if cached_messages:
            return cached_messages, len(cached_messages) == per_page

        # Query database if cache miss
        messages = Message.query.filter_by(room_id=room_id)\
            .order_by(Message.sent_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)

        # Cache results
        cls._cache_messages(room_id, messages.items)

        return messages.items, messages.has_next

    @classmethod
    def mark_messages_read(cls, room_id: int, user_id: int, 
                         message_ids: List[int]) -> None:
        """Mark messages as read by user."""
        if not cls.is_room_member(room_id, user_id):
            raise ValueError("User is not a member of this room")

        # Update read status in Redis
        cls._update_message_read_status(room_id, user_id, message_ids)

        # Update last read timestamp
        member = ChatRoomMember.query.filter_by(
            room_id=room_id, user_id=user_id
        ).first()
        member.last_read_at = datetime.utcnow()
        db.session.commit()

    @classmethod
    def get_user_rooms(cls, user_id: int) -> List[Dict]:
        """Get all rooms for a user with unread counts."""
        memberships = ChatRoomMember.query.filter_by(user_id=user_id).all()
        
        rooms = []
        for membership in memberships:
            room = membership.room
            unread_count = cls._get_unread_count(room.id, user_id)
            
            rooms.append({
                'id': room.id,
                'name': room.name,
                'is_private': room.is_private,
                'last_message': cls._get_last_message(room.id),
                'unread_count': unread_count,
                'members': cls._get_room_members(room.id)
            })
            
        return rooms

    @classmethod
    def add_room_member(cls, room_id: int, user_id: int, 
                       added_by_id: int) -> ChatRoomMember:
        """Add a member to a chat room."""
        # Verify admin privileges
        if not cls.is_room_admin(room_id, added_by_id):
            raise ValueError("Only admins can add members")

        # Check if already a member
        if cls.is_room_member(room_id, user_id):
            raise ValueError("User is already a member")

        member = ChatRoomMember(
            room_id=room_id,
            user_id=user_id,
            joined_at=datetime.utcnow()
        )
        db.session.add(member)
        db.session.commit()

        return member

    @classmethod
    def remove_room_member(cls, room_id: int, user_id: int, 
                          removed_by_id: int) -> None:
        """Remove a member from a chat room."""
        # Verify admin privileges
        if not cls.is_room_admin(room_id, removed_by_id):
            raise ValueError("Only admins can remove members")

        member = ChatRoomMember.query.filter_by(
            room_id=room_id, user_id=user_id
        ).first()
        
        if not member:
            raise ValueError("User is not a member")

        if member.is_admin and cls._count_room_admins(room_id) <= 1:
            raise ValueError("Cannot remove the last admin")

        db.session.delete(member)
        db.session.commit()

    @staticmethod
    def is_room_member(room_id: int, user_id: int) -> bool:
        """Check if user is a member of the room."""
        return ChatRoomMember.query.filter_by(
            room_id=room_id, user_id=user_id
        ).first() is not None

    @staticmethod
    def is_room_admin(room_id: int, user_id: int) -> bool:
        """Check if user is an admin of the room."""
        member = ChatRoomMember.query.filter_by(
            room_id=room_id, user_id=user_id
        ).first()
        return member is not None and member.is_admin

    @staticmethod
    def _update_room_activity(room_id: int) -> None:
        """Update room's last activity timestamp."""
        room = ChatRoom.query.get(room_id)
        room.last_activity = datetime.utcnow()
        db.session.commit()

    @staticmethod
    def _cache_message(message: Message) -> None:
        """Cache message in Redis."""
        key = f"message:{message.room_id}:{message.id}"
        redis_client.setex(
            key,
            timedelta(days=1),
            message.to_json()
        )

    @staticmethod
    def _get_cached_messages(room_id: int, page: int, 
                           per_page: int) -> Optional[List[Message]]:
        """Get cached messages from Redis."""
        pattern = f"message:{room_id}:*"
        keys = redis_client.keys(pattern)
        if not keys:
            return None

        messages = []
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page

        for key in sorted(keys)[start_idx:end_idx]:
            message_data = redis_client.get(key)
            if message_data:
                messages.append(Message.from_json(message_data))

        return messages if messages else None

    @staticmethod
    def _cache_messages(room_id: int, messages: List[Message]) -> None:
        """Cache multiple messages in Redis."""
        pipeline = redis_client.pipeline()
        for message in messages:
            key = f"message:{room_id}:{message.id}"
            pipeline.setex(
                key,
                timedelta(days=1),
                message.to_json()
            )
        pipeline.execute()

    @staticmethod
    def _update_message_read_status(room_id: int, user_id: int, 
                                  message_ids: List[int]) -> None:
        """Update message read status in Redis."""
        pipeline = redis_client.pipeline()
        for msg_id in message_ids:
            key = f"read:{room_id}:{msg_id}"
            pipeline.sadd(key, user_id)
            pipeline.expire(key, timedelta(days=7))
        pipeline.execute()

    @classmethod
    def _get_unread_count(cls, room_id: int, user_id: int) -> int:
        """Get number of unread messages in a room."""
        member = ChatRoomMember.query.filter_by(
            room_id=room_id, user_id=user_id
        ).first()
        
        if not member or not member.last_read_at:
            return Message.query.filter_by(room_id=room_id).count()

        return Message.query.filter(
            Message.room_id == room_id,
            Message.sent_at > member.last_read_at
        ).count()

    @staticmethod
    def _get_last_message(room_id: int) -> Optional[Dict]:
        """Get the last message in a room."""
        message = Message.query.filter_by(room_id=room_id)\
            .order_by(Message.sent_at.desc())\
            .first()
            
        if not message:
            return None
            
        return {
            'content': message.content,
            'sender': message.sender.username,
            'sent_at': message.sent_at.isoformat()
        }

    @staticmethod
    def _get_room_members(room_id: int) -> List[Dict]:
        """Get all members of a room."""
        members = ChatRoomMember.query.filter_by(room_id=room_id)\
            .join(User)\
            .all()
            
        return [{
            'id': member.user.id,
            'username': member.user.username,
            'is_admin': member.is_admin,
            'joined_at': member.joined_at.isoformat()
        } for member in members]

    @staticmethod
    def _count_room_admins(room_id: int) -> int:
        """Count number of admins in a room."""
        return ChatRoomMember.query.filter_by(
            room_id=room_id, is_admin=True
        ).count()