from flask import Flask
from flask_socketio import SocketIO
from app.config import Config
from app.extensions import socketio
from app.sockets.chat_namespace import ChatNamespace
from app.sockets.main_socket import MainSocket

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    socketio.init_app(app, cors_allowed_origins=app.config['SOCKET_CORS_ORIGINS'])
    
    # Register socket namespaces
    socketio.on_namespace(ChatNamespace('/chat'))
    socketio.on_namespace(MainSocket('/'))
    
    return app 