from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

import bcrypt
from flask import current_app
from flask_jwt_extended import create_access_token, create_refresh_token

from ..extensions import db, redis_client
from ..models import User, UserSession
from ..utils.validators import validate_password_strength

class AuthService:
    @staticmethod
    def hash_password(password: str) -> bytes:
        """Hash a password using bcrypt with salt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt)

    @staticmethod
    def verify_password(password: str, hashed: bytes) -> bool:
        """Verify a password against its hash."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed)

    @classmethod
    def register_user(cls, email: str, password: str, username: str) -> Tuple[User, str]:
        """Register a new user with email verification."""
        # Validate password strength
        if not validate_password_strength(password):
            raise ValueError("Password does not meet security requirements")

        # Check if user exists
        if User.query.filter((User.email == email) | (User.username == username)).first():
            raise ValueError("User with this email or username already exists")

        # Create user
        hashed_password = cls.hash_password(password)
        user = User(
            email=email,
            username=username,
            password=hashed_password,
            email_verified=False,
            verification_token=cls._generate_verification_token()
        )
        
        db.session.add(user)
        db.session.commit()

        # Send verification email
        cls._send_verification_email(user)
        
        # Generate tokens
        access_token = cls.create_access_token(user)
        
        return user, access_token

    @classmethod
    def login(cls, email: str, password: str, device_info: Dict) -> Tuple[str, str]:
        """Login user and return access and refresh tokens."""
        user = User.query.filter_by(email=email).first()
        
        if not user or not cls.verify_password(password, user.password):
            raise ValueError("Invalid credentials")

        if not user.email_verified:
            raise ValueError("Email not verified")

        if user.is_blocked:
            raise ValueError("Account is blocked")

        # Check for suspicious login patterns
        if cls._is_suspicious_login(user, device_info):
            cls._trigger_2fa(user)
            raise ValueError("Additional verification required")

        # Create session
        session = UserSession(
            user_id=user.id,
            device_info=device_info,
            ip_address=device_info.get('ip_address'),
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
        db.session.add(session)
        db.session.commit()

        # Generate tokens
        access_token = cls.create_access_token(user)
        refresh_token = cls.create_refresh_token(user)

        # Store refresh token in Redis with user info
        cls._store_refresh_token(refresh_token, user.id, device_info)

        return access_token, refresh_token

    @staticmethod
    def create_access_token(user: User) -> str:
        """Create a new access token for user."""
        expires_delta = timedelta(minutes=current_app.config['JWT_ACCESS_TOKEN_EXPIRES'])
        
        additional_claims = {
            'email': user.email,
            'username': user.username,
            'roles': [role.name for role in user.roles],
            'permissions': user.get_permissions()
        }
        
        return create_access_token(
            identity=user.id,
            expires_delta=expires_delta,
            additional_claims=additional_claims
        )

    @staticmethod
    def create_refresh_token(user: User) -> str:
        """Create a new refresh token for user."""
        expires_delta = timedelta(days=current_app.config['JWT_REFRESH_TOKEN_EXPIRES'])
        return create_refresh_token(
            identity=user.id,
            expires_delta=expires_delta
        )

    @classmethod
    def refresh_access_token(cls, refresh_token: str, device_info: Dict) -> str:
        """Create new access token using refresh token."""
        # Verify refresh token in Redis
        user_id = cls._verify_refresh_token(refresh_token, device_info)
        if not user_id:
            raise ValueError("Invalid refresh token")

        user = User.query.get(user_id)
        if not user:
            raise ValueError("User not found")

        return cls.create_access_token(user)

    @classmethod
    def logout(cls, refresh_token: str) -> None:
        """Logout user by invalidating refresh token."""
        redis_client.delete(f"refresh_token:{refresh_token}")

    @classmethod
    def logout_all_devices(cls, user_id: int) -> None:
        """Logout user from all devices."""
        pattern = f"refresh_token:*:{user_id}"
        tokens = redis_client.keys(pattern)
        if tokens:
            redis_client.delete(*tokens)

        # Invalidate all sessions
        UserSession.query.filter_by(user_id=user_id).update({
            'is_active': False,
            'ended_at': datetime.utcnow()
        })
        db.session.commit()

    @staticmethod
    def _generate_verification_token() -> str:
        """Generate a random token for email verification."""
        import secrets
        return secrets.token_urlsafe(32)

    @staticmethod
    def _send_verification_email(user: User) -> None:
        """Send verification email to user."""
        # Implementation for sending email
        # This would typically use a service like SendGrid or AWS SES
        pass

    @staticmethod
    def _is_suspicious_login(user: User, device_info: Dict) -> bool:
        """Check if login attempt is suspicious."""
        # Implementation for fraud detection
        # This would typically check IP reputation, device fingerprint, etc.
        return False

    @staticmethod
    def _trigger_2fa(user: User) -> None:
        """Trigger two-factor authentication."""
        # Implementation for 2FA
        # This would typically send SMS or email with code
        pass

    @staticmethod
    def _store_refresh_token(token: str, user_id: int, device_info: Dict) -> None:
        """Store refresh token in Redis with device info."""
        key = f"refresh_token:{token}:{user_id}"
        redis_client.setex(
            key,
            timedelta(days=current_app.config['JWT_REFRESH_TOKEN_EXPIRES']),
            str(device_info)
        )

    @staticmethod
    def _verify_refresh_token(token: str, device_info: Dict) -> Optional[int]:
        """Verify refresh token and device info in Redis."""
        pattern = f"refresh_token:{token}:*"
        keys = redis_client.keys(pattern)
        if not keys:
            return None

        key = keys[0]
        stored_device_info = eval(redis_client.get(key))
        if stored_device_info.get('device_id') != device_info.get('device_id'):
            return None

        return int(key.split(':')[2])