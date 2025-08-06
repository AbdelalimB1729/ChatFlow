import os
import tempfile
import pytest
from flask_socketio import SocketIOTestClient
from fakeredis import FakeRedis

from app import create_app
from app.extensions import db as _db, redis_client, socketio
from app.models import User, ChatRoom, Message

@pytest.fixture(scope='session')
def app():
    """Create application for the tests."""
    # Create temp file for SQLite database
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'JWT_SECRET_KEY': 'test-secret-key',
        'REDIS_URL': 'memory://',
    })
    
    # Create tables
    with app.app_context():
        _db.create_all()
    
    yield app
    
    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture(scope='session')
def db(app):
    """Database fixture for the tests."""
    with app.app_context():
        yield _db

@pytest.fixture(scope='function')
def session(db):
    """Creates a new database session for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()
    
    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)
    
    db.session = session
    
    yield session
    
    transaction.rollback()
    connection.close()
    session.remove()

@pytest.fixture(scope='function')
def client(app):
    """Create Flask test client."""
    return app.test_client()

@pytest.fixture(scope='function')
def socket_client(app, client):
    """Create Socket.IO test client."""
    return SocketIOTestClient(app, socketio)

@pytest.fixture(scope='function')
def redis(app):
    """Create fake Redis client."""
    fake_redis = FakeRedis()
    redis_client.connection_pool = fake_redis.connection_pool
    return fake_redis

@pytest.fixture
def auth_headers(client, test_user):
    """Get auth headers for test user."""
    response = client.post('/api/auth/login', json={
        'email': test_user.email,
        'password': 'password123!'
    })
    token = response.json['access_token']
    return {'Authorization': f'Bearer {token}'}

@pytest.fixture
def test_user(session):
    """Create test user."""
    user = User(
        email='test@example.com',
        username='testuser',
        password=b'$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY.FhjJ4bx9YXa6',  # password123!
        email_verified=True
    )
    session.add(user)
    session.commit()
    return user

@pytest.fixture
def test_room(session, test_user):
    """Create test chat room."""
    room = ChatRoom(
        name='Test Room',
        creator_id=test_user.id
    )
    session.add(room)
    session.commit()
    return room

@pytest.fixture
def test_message(session, test_user, test_room):
    """Create test message."""
    message = Message(
        content='Test message',
        sender_id=test_user.id,
        room_id=test_room.id
    )
    session.add(message)
    session.commit()
    return message