from functools import wraps
from typing import Callable, List, Optional, Union
from flask import request, current_app, g
from flask_jwt_extended import get_jwt, verify_jwt_in_request
import redis
import time
from ..extensions import redis_client

def require_auth(f: Callable) -> Callable:
    """Decorator to require JWT authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        verify_jwt_in_request()
        return f(*args, **kwargs)
    return decorated

def require_roles(roles: List[str]) -> Callable:
    """Decorator to require specific roles."""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_roles = claims.get('roles', [])
            
            if not any(role in user_roles for role in roles):
                return {'message': 'Insufficient permissions'}, 403
                
            return f(*args, **kwargs)
        return decorated
    return decorator

def require_permissions(permissions: List[str]) -> Callable:
    """Decorator to require specific permissions."""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_permissions = claims.get('permissions', [])
            
            if not all(perm in user_permissions for perm in permissions):
                return {'message': 'Insufficient permissions'}, 403
                
            return f(*args, **kwargs)
        return decorated
    return decorator

def rate_limit(
    limit: int,
    period: int,
    key_prefix: str = 'rl',
    by_user: bool = True,
    by_ip: bool = True
) -> Callable:
    """
    Rate limiting decorator.
    
    Args:
        limit: Number of allowed requests
        period: Time period in seconds
        key_prefix: Redis key prefix
        by_user: Include user ID in rate limit key
        by_ip: Include IP address in rate limit key
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated(*args, **kwargs):
            # Build rate limit key
            key_parts = [key_prefix]
            
            if by_user and hasattr(g, 'user'):
                key_parts.append(str(g.user.id))
                
            if by_ip:
                key_parts.append(request.remote_addr)
                
            key = ':'.join(key_parts)
            
            # Check rate limit
            try:
                pipe = redis_client.pipeline()
                now = time.time()
                pipe.zremrangebyscore(key, 0, now - period)
                pipe.zadd(key, {str(now): now})
                pipe.zcard(key)
                pipe.expire(key, period)
                _, _, count, _ = pipe.execute()
                
                if count > limit:
                    return {
                        'message': 'Too many requests',
                        'retry_after': period
                    }, 429
                    
            except redis.RedisError:
                current_app.logger.exception('Rate limit check failed')
                # Continue on Redis error
                
            return f(*args, **kwargs)
        return decorated
    return decorator

def validate_json(*required_fields: str) -> Callable:
    """Decorator to validate required JSON fields."""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated(*args, **kwargs):
            if not request.is_json:
                return {'message': 'Content-Type must be application/json'}, 400
                
            data = request.get_json()
            missing = [field for field in required_fields if field not in data]
            
            if missing:
                return {
                    'message': 'Missing required fields',
                    'fields': missing
                }, 400
                
            return f(*args, **kwargs)
        return decorated
    return decorator

def cache_response(
    timeout: int,
    key_prefix: str,
    unless: Optional[Callable] = None,
    vary_by_user: bool = False
) -> Callable:
    """
    Cache response decorator.
    
    Args:
        timeout: Cache timeout in seconds
        key_prefix: Redis key prefix
        unless: Function that returns True if response should not be cached
        vary_by_user: Include user ID in cache key
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated(*args, **kwargs):
            if unless and unless():
                return f(*args, **kwargs)
                
            # Build cache key
            key_parts = [key_prefix]
            
            if vary_by_user and hasattr(g, 'user'):
                key_parts.append(str(g.user.id))
                
            # Add query params to key
            query_string = request.query_string.decode('utf-8')
            if query_string:
                key_parts.append(query_string)
                
            cache_key = ':'.join(key_parts)
            
            # Try cache
            try:
                cached = redis_client.get(cache_key)
                if cached:
                    return cached
                    
                # Cache miss, call function
                rv = f(*args, **kwargs)
                redis_client.setex(cache_key, timeout, rv)
                return rv
                
            except redis.RedisError:
                current_app.logger.exception('Cache operation failed')
                return f(*args, **kwargs)
                
        return decorated
    return decorator

def sanitize_input(*fields: str) -> Callable:
    """
    Decorator to sanitize request input fields.
    
    Args:
        fields: Fields to sanitize
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated(*args, **kwargs):
            if request.is_json:
                data = request.get_json()
                for field in fields:
                    if field in data:
                        # Basic HTML escaping
                        data[field] = (
                            str(data[field])
                            .replace('&', '&amp;')
                            .replace('<', '&lt;')
                            .replace('>', '&gt;')
                            .replace('"', '&quot;')
                            .replace("'", '&#x27;')
                        )
                        
            return f(*args, **kwargs)
        return decorated
    return decorator

def audit_log(
    action: str,
    include_request_data: bool = True,
    include_response: bool = False
) -> Callable:
    """
    Decorator to log audit events.
    
    Args:
        action: Audit action name
        include_request_data: Include request data in log
        include_response: Include response data in log
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated(*args, **kwargs):
            # Gather audit data
            audit_data = {
                'action': action,
                'timestamp': time.time(),
                'user_id': g.user.id if hasattr(g, 'user') else None,
                'ip_address': request.remote_addr,
                'user_agent': request.user_agent.string
            }
            
            if include_request_data:
                audit_data.update({
                    'method': request.method,
                    'path': request.path,
                    'query_params': dict(request.args),
                    'request_data': request.get_json() if request.is_json else None
                })
                
            try:
                # Call function
                rv = f(*args, **kwargs)
                
                if include_response:
                    audit_data['response'] = rv
                    
                # Log success
                audit_data['status'] = 'success'
                current_app.logger.info('Audit log', extra=audit_data)
                
                return rv
                
            except Exception as e:
                # Log failure
                audit_data.update({
                    'status': 'error',
                    'error': str(e)
                })
                current_app.logger.error('Audit log', extra=audit_data)
                raise
                
        return decorated
    return decorator