from flask_socketio import Namespace, emit, join_room, leave_room
from app.events.connection_events import ConnectionEvents
from app.events.message_events import MessageEvents
from app.events.user_events import UserEvents
from app.utils.decorators import require_auth

class ChatNamespace(Namespace):
    def on_connect(self, data):
        """Handle connection to chat namespace"""
        return ConnectionEvents.handle_connect(self.request.sid, data)
    
    def on_disconnect(self, data):
        """Handle disconnection from chat namespace"""
        return ConnectionEvents.handle_disconnect(self.request.sid, data)
    
    def on_join_room(self, data):
        """Handle joining a chat room"""
        return ConnectionEvents.handle_join_room(self.request.sid, data)
    
    def on_leave_room(self, data):
        """Handle leaving a chat room"""
        return ConnectionEvents.handle_leave_room(self.request.sid, data)
    
    def on_send_message(self, data):
        """Handle sending a message"""
        return MessageEvents.handle_send_message(self.request.sid, data)
    
    def on_mark_read(self, data):
        """Handle marking a message as read"""
        return MessageEvents.handle_mark_read(self.request.sid, data)
    
    def on_mark_delivered(self, data):
        """Handle marking a message as delivered"""
        return MessageEvents.handle_mark_delivered(self.request.sid, data)
    
    def on_get_messages(self, data):
        """Handle getting messages for a room"""
        return MessageEvents.handle_get_messages(self.request.sid, data)
    
    def on_typing_start(self, data):
        """Handle typing start indicator"""
        return MessageEvents.handle_typing_start(self.request.sid, data)
    
    def on_typing_stop(self, data):
        """Handle typing stop indicator"""
        return MessageEvents.handle_typing_stop(self.request.sid, data)
    
    def on_get_typing_users(self, data):
        """Handle getting typing users in a room"""
        return MessageEvents.handle_get_typing_users(self.request.sid, data)
    
    def on_get_online_users(self, data):
        """Handle getting online users"""
        return UserEvents.handle_get_online_users(self.request.sid, data)
    
    def on_get_all_users(self, data):
        """Handle getting all users"""
        return UserEvents.handle_get_all_users(self.request.sid, data)
    
    def on_get_user_profile(self, data):
        """Handle getting user profile"""
        return UserEvents.handle_get_user_profile(self.request.sid, data)
    
    def on_search_users(self, data):
        """Handle searching users"""
        return UserEvents.handle_search_users(self.request.sid, data)
    
    def on_get_user_statistics(self, data):
        """Handle getting user statistics"""
        return UserEvents.handle_get_user_statistics(self.request.sid, data)
    
    def on_create_room(self, data):
        """Handle creating a new chat room"""
        return UserEvents.handle_create_room(self.request.sid, data)
    
    def on_get_rooms(self, data):
        """Handle getting all available rooms"""
        return UserEvents.handle_get_rooms(self.request.sid, data)
    
    def on_update_presence(self, data):
        """Handle updating user presence"""
        return UserEvents.handle_update_presence(self.request.sid, data)
    
    def on_set_typing_status(self, data):
        """Handle setting user typing status"""
        return UserEvents.handle_set_typing_status(self.request.sid, data)
    
    def on_heartbeat(self, data):
        """Handle heartbeat to keep connection alive"""
        return ConnectionEvents.handle_heartbeat(self.request.sid, data) 