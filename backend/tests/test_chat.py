import pytest
from datetime import datetime, timedelta

from app.services.chat_service import ChatService
from app.models import ChatRoom, Message, ChatRoomMember

def test_create_room(session, test_user):
    """Test creating a chat room."""
    room = ChatService.create_room(
        creator_id=test_user.id,
        name='Test Room',
        is_private=False
    )
    
    assert room.name == 'Test Room'
    assert room.creator_id == test_user.id
    assert not room.is_private
    
    # Verify creator was added as admin
    member = ChatRoomMember.query.filter_by(
        room_id=room.id,
        user_id=test_user.id
    ).first()
    assert member is not None
    assert member.is_admin

def test_create_private_room(session, test_user):
    """Test creating a private room with members."""
    other_user = User(
        email='other@example.com',
        username='otheruser',
        password=b'hashedpass'
    )
    session.add(other_user)
    session.commit()
    
    room = ChatService.create_room(
        creator_id=test_user.id,
        name='Private Chat',
        is_private=True,
        member_ids=[test_user.id, other_user.id]
    )
    
    assert room.is_private
    
    # Verify both users are members
    members = ChatRoomMember.query.filter_by(room_id=room.id).all()
    assert len(members) == 2
    assert {m.user_id for m in members} == {test_user.id, other_user.id}

def test_send_message(session, test_user, test_room):
    """Test sending a message to a room."""
    message = ChatService.send_message(
        room_id=test_room.id,
        sender_id=test_user.id,
        content='Hello, world!'
    )
    
    assert message.content == 'Hello, world!'
    assert message.sender_id == test_user.id
    assert message.room_id == test_room.id
    
    # Verify room's last activity was updated
    room = ChatRoom.query.get(test_room.id)
    assert (datetime.utcnow() - room.last_activity) < timedelta(seconds=1)

def test_send_message_with_attachment(session, test_user, test_room):
    """Test sending a message with attachment."""
    message = ChatService.send_message(
        room_id=test_room.id,
        sender_id=test_user.id,
        content='Check this out!',
        message_type='image',
        file_url='https://example.com/image.jpg'
    )
    
    assert message.message_type == 'image'
    assert message.file_url == 'https://example.com/image.jpg'

def test_get_room_messages(session, test_user, test_room):
    """Test getting paginated room messages."""
    # Create multiple messages
    messages = []
    for i in range(60):  # More than default page size
        message = Message(
            room_id=test_room.id,
            sender_id=test_user.id,
            content=f'Message {i}',
            sent_at=datetime.utcnow() - timedelta(minutes=i)
        )
        messages.append(message)
    
    session.add_all(messages)
    session.commit()
    
    # Get first page
    page_1_messages, has_more = ChatService.get_room_messages(
        test_room.id,
        test_user.id
    )
    
    assert len(page_1_messages) == 50  # Default page size
    assert has_more
    
    # Get second page
    page_2_messages, has_more = ChatService.get_room_messages(
        test_room.id,
        test_user.id,
        page=2
    )
    
    assert len(page_2_messages) == 10
    assert not has_more

def test_mark_messages_read(session, test_user, test_room):
    """Test marking messages as read."""
    # Create some messages
    messages = []
    for i in range(5):
        message = Message(
            room_id=test_room.id,
            sender_id=test_user.id,
            content=f'Message {i}'
        )
        messages.append(message)
    
    session.add_all(messages)
    session.commit()
    
    message_ids = [m.id for m in messages]
    
    ChatService.mark_messages_read(
        test_room.id,
        test_user.id,
        message_ids
    )
    
    # Verify last read timestamp was updated
    member = ChatRoomMember.query.filter_by(
        room_id=test_room.id,
        user_id=test_user.id
    ).first()
    assert member.last_read_at is not None

def test_get_user_rooms(session, test_user):
    """Test getting user's rooms with metadata."""
    # Create multiple rooms with different states
    room1 = ChatRoom(name='Room 1', creator_id=test_user.id)
    room2 = ChatRoom(name='Room 2', creator_id=test_user.id)
    session.add_all([room1, room2])
    session.commit()
    
    # Add user as member
    for room in [room1, room2]:
        member = ChatRoomMember(
            room_id=room.id,
            user_id=test_user.id,
            is_admin=True
        )
        session.add(member)
    
    # Add some messages
    message1 = Message(
        room_id=room1.id,
        sender_id=test_user.id,
        content='Latest message in room 1'
    )
    session.add(message1)
    session.commit()
    
    rooms = ChatService.get_user_rooms(test_user.id)
    
    assert len(rooms) == 2
    
    # Verify room metadata
    room1_data = next(r for r in rooms if r['id'] == room1.id)
    assert room1_data['name'] == 'Room 1'
    assert room1_data['last_message']['content'] == 'Latest message in room 1'

def test_add_room_member(session, test_user, test_room):
    """Test adding a member to a room."""
    new_user = User(
        email='new@example.com',
        username='newuser',
        password=b'hashedpass'
    )
    session.add(new_user)
    session.commit()
    
    member = ChatService.add_room_member(
        room_id=test_room.id,
        user_id=new_user.id,
        added_by_id=test_user.id
    )
    
    assert member.user_id == new_user.id
    assert member.room_id == test_room.id
    assert not member.is_admin

def test_remove_room_member(session, test_user, test_room):
    """Test removing a member from a room."""
    # Add another admin to avoid last admin removal
    other_admin = User(
        email='admin@example.com',
        username='admin',
        password=b'hashedpass'
    )
    session.add(other_admin)
    session.commit()
    
    admin_member = ChatRoomMember(
        room_id=test_room.id,
        user_id=other_admin.id,
        is_admin=True
    )
    session.add(admin_member)
    session.commit()
    
    # Remove regular member
    regular_user = User(
        email='regular@example.com',
        username='regular',
        password=b'hashedpass'
    )
    session.add(regular_user)
    
    regular_member = ChatRoomMember(
        room_id=test_room.id,
        user_id=regular_user.id
    )
    session.add(regular_member)
    session.commit()
    
    ChatService.remove_room_member(
        room_id=test_room.id,
        user_id=regular_user.id,
        removed_by_id=test_user.id
    )
    
    # Verify member was removed
    member = ChatRoomMember.query.filter_by(
        room_id=test_room.id,
        user_id=regular_user.id
    ).first()
    assert member is None

def test_remove_last_admin(session, test_user, test_room):
    """Test preventing removal of last admin."""
    with pytest.raises(ValueError, match='Cannot remove the last admin'):
        ChatService.remove_room_member(
            room_id=test_room.id,
            user_id=test_user.id,
            removed_by_id=test_user.id
        )