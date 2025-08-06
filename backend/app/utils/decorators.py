import time
from functools import wraps
from flask_socketio import emit, disconnect
from app.models import users
from app.config import Config

def require_auth(f):
    @wraps(f)
    def decorated_function(sid, data, *args, **kwargs):
        user_id = data.get('user_id')
        if not user_id or user_id not in users:
            emit('error', {'message': 'Authentication required'})
            return
        return f(sid, data, *args, **kwargs)
    return decorated_function

def rate_limit_messages(limit=Config.RATE_LIMIT_MESSAGES, window=60):
    def decorator(f):
        message_timestamps = {}
        
        @wraps(f)
        def decorated_function(sid, data, *args, **kwargs):
            user_id = data.get('user_id')
            current_time = time.time()
            
            if user_id not in message_timestamps:
                message_timestamps[user_id] = []
            
            # Remove timestamps older than window
            message_timestamps[user_id] = [
                ts for ts in message_timestamps[user_id] 
                if current_time - ts < window
            ]
            
            if len(message_timestamps[user_id]) >= limit:
                emit('error', {'message': 'Rate limit exceeded'})
                return
            
            message_timestamps[user_id].append(current_time)
            return f(sid, data, *args, **kwargs)
        return decorated_function
    return decorator

def validate_message_data(f):
    @wraps(f)
    def decorated_function(sid, data, *args, **kwargs):
        required_fields = ['content', 'room_id']
        for field in required_fields:
            if field not in data or not data[field]:
                emit('error', {'message': f'Missing required field: {field}'})
                return
        return f(sid, data, *args, **kwargs)
    return decorated_function 