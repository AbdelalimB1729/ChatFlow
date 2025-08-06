from flask_socketio import Namespace, emit, disconnect
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.utils.decorators import require_auth

class MainSocket(Namespace):
    def on_connect(self, data):
        """Handle initial connection"""
        emit('connected', {
            'message': 'Connected to ChatBridgePro',
            'version': '1.0.0'
        })
    
    def on_disconnect(self, data):
        """Handle disconnection"""
        user_id = data.get('user_id')
        if user_id:
            UserService.set_user_offline(user_id)
            emit('user_offline', {
                'user_id': user_id,
                'message': 'User disconnected'
            }, broadcast=True)
    
    def on_authenticate(self, data):
        """Handle user authentication"""
        token = data.get('token')
        if not token:
            emit('error', {'message': 'Authentication token required'})
            return
        
        user = AuthService.get_user_by_token(token)
        if not user:
            emit('error', {'message': 'Invalid authentication token'})
            return
        
        # Set user online
        UserService.set_user_online(user.user_id, self.request.sid)
        
        emit('authenticated', {
            'user_id': user.user_id,
            'username': user.username,
            'email': user.email,
            'message': 'Successfully authenticated'
        })
        
        # Emit user online to all clients
        emit('user_online', {
            'user_id': user.user_id,
            'username': user.username,
            'message': 'User came online'
        }, broadcast=True)
    
    def on_register(self, data):
        """Handle user registration"""
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not all([username, email, password]):
            emit('error', {'message': 'Username, email, and password required'})
            return
        
        result = AuthService.register_user(username, email, password)
        if not result['success']:
            emit('error', {'message': result['error']})
            return
        
        emit('registered', {
            'user': result['user'],
            'token': result['token'],
            'message': 'Registration successful'
        })
    
    def on_login(self, data):
        """Handle user login"""
        username = data.get('username')
        password = data.get('password')
        
        if not all([username, password]):
            emit('error', {'message': 'Username and password required'})
            return
        
        result = AuthService.login_user(username, password)
        if not result['success']:
            emit('error', {'message': result['error']})
            return
        
        emit('logged_in', {
            'user': result['user'],
            'token': result['token'],
            'message': 'Login successful'
        })
    
    @require_auth
    def on_get_user_info(self, data):
        """Handle getting user information"""
        user_id = data.get('user_id')
        
        profile = UserService.get_user_profile(user_id)
        if not profile:
            emit('error', {'message': 'User not found'})
            return
        
        emit('user_info', {'profile': profile})
    
    @require_auth
    def on_logout(self, data):
        """Handle user logout"""
        user_id = data.get('user_id')
        
        UserService.set_user_offline(user_id)
        
        emit('logged_out', {
            'message': 'Successfully logged out'
        })
        
        # Emit user offline to all clients
        emit('user_offline', {
            'user_id': user_id,
            'message': 'User logged out'
        }, broadcast=True)
    
    def on_error(self, data):
        """Handle socket errors"""
        emit('error', {
            'message': 'An error occurred',
            'details': data.get('details', 'Unknown error')
        })
    
    def on_heartbeat(self, data):
        """Handle heartbeat for connection monitoring"""
        emit('heartbeat_response', {
            'timestamp': '2024-01-01T00:00:00Z',
            'status': 'alive'
        }) 