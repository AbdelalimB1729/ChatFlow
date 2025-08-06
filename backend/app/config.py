import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key'
    SOCKET_CORS_ORIGINS = os.environ.get('SOCKET_CORS_ORIGINS') or 'http://localhost:3001'
    MESSAGE_QUEUE_SIZE = 1000
    RATE_LIMIT_MESSAGES = 10  # messages per minute
    RATE_LIMIT_CONNECTIONS = 5  # connections per minute
    HEARTBEAT_INTERVAL = 30  # seconds
    TYPING_TIMEOUT = 5  # seconds 