from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from sqlalchemy import and_, or_
from werkzeug.datastructures import FileStorage

from ..extensions import db, redis_client
from ..models import User, UserProfile, UserPreferences, UserActivity
from ..utils.validators import validate_email, validate_username
from .auth_service import AuthService

class UserService:
    @classmethod
    def get_user_by_id(cls, user_id: int) -> Optional[User]:
        """Get user by ID with caching."""
        # Try cache first
        cached_user = cls._get_cached_user(user_id)
        if cached_user:
            return cached_user

        # Query database if cache miss
        user = User.query.get(user_id)
        if user:
            cls._cache_user(user)
        return user

    @classmethod
    def update_user_profile(cls, user_id: int, profile_data: Dict) -> UserProfile:
        """Update user profile information."""
        profile = UserProfile.query.filter_by(user_id=user_id).first()
        if not profile:
            profile = UserProfile(user_id=user_id)
            db.session.add(profile)

        # Update allowed fields
        allowed_fields = [
            'full_name', 'bio', 'location', 'website',
            'company', 'job_title', 'phone_number'
        ]
        
        for field in allowed_fields:
            if field in profile_data:
                setattr(profile, field, profile_data[field])

        db.session.commit()
        
        # Invalidate cache
        cls._invalidate_user_cache(user_id)
        
        return profile

    @classmethod
    def update_user_preferences(cls, user_id: int, 
                              preferences_data: Dict) -> UserPreferences:
        """Update user preferences."""
        prefs = UserPreferences.query.filter_by(user_id=user_id).first()
        if not prefs:
            prefs = UserPreferences(user_id=user_id)
            db.session.add(prefs)

        # Update allowed preferences
        allowed_prefs = [
            'theme', 'language', 'timezone',
            'notifications_enabled', 'email_notifications',
            'push_notifications', 'chat_sounds'
        ]
        
        for pref in allowed_prefs:
            if pref in preferences_data:
                setattr(prefs, pref, preferences_data[pref])

        db.session.commit()
        return prefs

    @classmethod
    def update_avatar(cls, user_id: int, avatar_file: FileStorage) -> str:
        """Update user's avatar image."""
        if not cls._is_valid_image(avatar_file):
            raise ValueError("Invalid image file")

        # Process and store avatar
        avatar_url = cls._store_avatar(avatar_file)

        profile = UserProfile.query.filter_by(user_id=user_id).first()
        if not profile:
            profile = UserProfile(user_id=user_id)
            db.session.add(profile)

        # Delete old avatar if exists
        if profile.avatar_url:
            cls._delete_avatar(profile.avatar_url)

        profile.avatar_url = avatar_url
        db.session.commit()

        # Invalidate cache
        cls._invalidate_user_cache(user_id)

        return avatar_url

    @classmethod
    def change_email(cls, user_id: int, new_email: str, password: str) -> None:
        """Change user's email address with verification."""
        user = cls.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        # Verify password
        if not AuthService.verify_password(password, user.password):
            raise ValueError("Invalid password")

        # Validate new email
        if not validate_email(new_email):
            raise ValueError("Invalid email format")

        # Check if email is already taken
        if User.query.filter(
            and_(User.email == new_email, User.id != user_id)
        ).first():
            raise ValueError("Email already in use")

        # Generate verification token
        verification_token = AuthService._generate_verification_token()
        
        # Store pending email change
        redis_client.setex(
            f"email_change:{user_id}",
            timedelta(hours=24),
            f"{new_email}:{verification_token}"
        )

        # Send verification email
        cls._send_email_change_verification(new_email, verification_token)

    @classmethod
    def verify_email_change(cls, user_id: int, token: str) -> None:
        """Verify email change with token."""
        key = f"email_change:{user_id}"
        stored_data = redis_client.get(key)
        
        if not stored_data:
            raise ValueError("Invalid or expired token")

        new_email, stored_token = stored_data.decode().split(':')
        if token != stored_token:
            raise ValueError("Invalid token")

        # Update email
        user = cls.get_user_by_id(user_id)
        user.email = new_email
        db.session.commit()

        # Cleanup
        redis_client.delete(key)
        cls._invalidate_user_cache(user_id)

    @classmethod
    def change_username(cls, user_id: int, new_username: str) -> None:
        """Change user's username."""
        if not validate_username(new_username):
            raise ValueError("Invalid username format")

        # Check if username is taken
        if User.query.filter(
            and_(User.username == new_username, User.id != user_id)
        ).first():
            raise ValueError("Username already taken")

        user = cls.get_user_by_id(user_id)
        user.username = new_username
        db.session.commit()

        cls._invalidate_user_cache(user_id)

    @classmethod
    def get_user_activity(cls, user_id: int, 
                         days: int = 30) -> List[UserActivity]:
        """Get user's recent activity."""
        since = datetime.utcnow() - timedelta(days=days)
        
        return UserActivity.query.filter(
            and_(
                UserActivity.user_id == user_id,
                UserActivity.timestamp >= since
            )
        ).order_by(UserActivity.timestamp.desc()).all()

    @classmethod
    def record_activity(cls, user_id: int, activity_type: str, 
                       details: Optional[Dict] = None) -> UserActivity:
        """Record a user activity."""
        activity = UserActivity(
            user_id=user_id,
            activity_type=activity_type,
            details=details or {},
            timestamp=datetime.utcnow()
        )
        db.session.add(activity)
        db.session.commit()
        return activity

    @classmethod
    def search_users(cls, query: str, exclude_ids: List[int] = None, 
                    limit: int = 20) -> List[User]:
        """Search users by username or email."""
        filters = [
            or_(
                User.username.ilike(f"%{query}%"),
                User.email.ilike(f"%{query}%")
            )
        ]
        
        if exclude_ids:
            filters.append(~User.id.in_(exclude_ids))

        return User.query.filter(and_(*filters))\
            .limit(limit)\
            .all()

    @staticmethod
    def _get_cached_user(user_id: int) -> Optional[User]:
        """Get user from cache."""
        data = redis_client.get(f"user:{user_id}")
        return User.from_json(data) if data else None

    @staticmethod
    def _cache_user(user: User) -> None:
        """Cache user data in Redis."""
        redis_client.setex(
            f"user:{user.id}",
            timedelta(minutes=30),
            user.to_json()
        )

    @staticmethod
    def _invalidate_user_cache(user_id: int) -> None:
        """Invalidate user cache."""
        redis_client.delete(f"user:{user_id}")

    @staticmethod
    def _is_valid_image(file: FileStorage) -> bool:
        """Validate image file."""
        # Implementation for image validation
        # This would typically check file type, size, dimensions, etc.
        return True

    @staticmethod
    def _store_avatar(file: FileStorage) -> str:
        """Store avatar file and return URL."""
        # Implementation for file storage
        # This would typically use a service like S3 or local storage
        return "avatar_url_here"

    @staticmethod
    def _delete_avatar(avatar_url: str) -> None:
        """Delete avatar file."""
        # Implementation for file deletion
        pass

    @staticmethod
    def _send_email_change_verification(email: str, token: str) -> None:
        """Send email change verification email."""
        # Implementation for sending email
        pass