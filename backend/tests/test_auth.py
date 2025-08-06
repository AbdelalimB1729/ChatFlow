import pytest
from flask_jwt_extended import decode_token

from app.services.auth_service import AuthService
from app.models import User, UserSession

def test_register_user(client, session):
    """Test user registration."""
    response = client.post('/api/auth/register', json={
        'email': 'new@example.com',
        'username': 'newuser',
        'password': 'Password123!'
    })
    
    assert response.status_code == 201
    assert 'access_token' in response.json
    
    # Verify user was created
    user = User.query.filter_by(email='new@example.com').first()
    assert user is not None
    assert user.username == 'newuser'
    assert not user.email_verified

def test_register_user_duplicate_email(client, test_user):
    """Test registration with duplicate email."""
    response = client.post('/api/auth/register', json={
        'email': test_user.email,
        'username': 'different',
        'password': 'Password123!'
    })
    
    assert response.status_code == 400
    assert 'email already exists' in response.json['message'].lower()

def test_login_success(client, test_user):
    """Test successful login."""
    response = client.post('/api/auth/login', json={
        'email': test_user.email,
        'password': 'password123!'
    })
    
    assert response.status_code == 200
    assert 'access_token' in response.json
    assert 'refresh_token' in response.json
    
    # Verify session was created
    session = UserSession.query.filter_by(user_id=test_user.id).first()
    assert session is not None
    assert session.is_active

def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    response = client.post('/api/auth/login', json={
        'email': 'wrong@example.com',
        'password': 'wrongpass'
    })
    
    assert response.status_code == 401
    assert 'invalid credentials' in response.json['message'].lower()

def test_refresh_token(client, test_user, redis):
    """Test refresh token functionality."""
    # First login to get tokens
    response = client.post('/api/auth/login', json={
        'email': test_user.email,
        'password': 'password123!'
    })
    
    refresh_token = response.json['refresh_token']
    
    # Use refresh token to get new access token
    response = client.post('/api/auth/refresh', headers={
        'Authorization': f'Bearer {refresh_token}'
    })
    
    assert response.status_code == 200
    assert 'access_token' in response.json
    
    # Verify new access token is valid
    new_token = response.json['access_token']
    decoded = decode_token(new_token)
    assert decoded['sub'] == test_user.id

def test_logout(client, auth_headers, redis):
    """Test logout functionality."""
    response = client.post('/api/auth/logout', headers=auth_headers)
    
    assert response.status_code == 200
    
    # Verify refresh token was invalidated
    refresh_token = auth_headers['Authorization'].split()[1]
    assert not redis.exists(f'refresh_token:{refresh_token}')

def test_logout_all_devices(client, auth_headers, test_user, session):
    """Test logging out from all devices."""
    # Create multiple sessions
    for _ in range(3):
        session = UserSession(
            user_id=test_user.id,
            device_info={'device': 'test'},
            is_active=True
        )
        session.add(session)
    session.commit()
    
    response = client.post('/api/auth/logout-all', headers=auth_headers)
    
    assert response.status_code == 200
    
    # Verify all sessions were invalidated
    active_sessions = UserSession.query.filter_by(
        user_id=test_user.id,
        is_active=True
    ).count()
    assert active_sessions == 0

def test_password_reset_request(client, test_user, redis):
    """Test password reset request."""
    response = client.post('/api/auth/reset-password', json={
        'email': test_user.email
    })
    
    assert response.status_code == 200
    
    # Verify reset token was created
    reset_tokens = redis.keys(f'reset_token:*:{test_user.id}')
    assert len(reset_tokens) == 1

def test_password_reset_confirm(client, test_user, redis):
    """Test password reset confirmation."""
    # Create reset token
    token = 'test-reset-token'
    redis.setex(
        f'reset_token:{token}:{test_user.id}',
        300,  # 5 minutes
        'true'
    )
    
    response = client.post('/api/auth/reset-password/confirm', json={
        'token': token,
        'new_password': 'NewPassword123!'
    })
    
    assert response.status_code == 200
    
    # Verify password was changed
    user = User.query.get(test_user.id)
    assert AuthService.verify_password('NewPassword123!', user.password)
    
    # Verify token was consumed
    assert not redis.exists(f'reset_token:{token}:{test_user.id}')

def test_verify_email(client, test_user):
    """Test email verification."""
    # Create verification token
    token = AuthService._generate_verification_token()
    test_user.verification_token = token
    session.commit()
    
    response = client.post('/api/auth/verify-email', json={
        'token': token
    })
    
    assert response.status_code == 200
    
    # Verify email was marked as verified
    user = User.query.get(test_user.id)
    assert user.email_verified
    assert user.verification_token is None

@pytest.mark.parametrize('password,valid', [
    ('short', False),
    ('no-numbers', False),
    ('12345678', False),
    ('Password123', False),
    ('Password123!', True),
])
def test_password_strength(password, valid):
    """Test password strength validation."""
    result = AuthService.validate_password_strength(password)
    assert result['valid'] == valid