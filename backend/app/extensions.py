from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from redis import Redis
from celery import Celery
from prometheus_client import Counter, Histogram
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
socketio = SocketIO()
jwt = JWTManager()
cors = CORS()

# Redis connection
redis_client = Redis(
    host='localhost',  # Configure from environment in production
    port=6379,
    db=0,
    decode_responses=True
)

# Celery configuration
celery = Celery(
    'chatflow',
    broker='redis://localhost:6379/1',
    backend='redis://localhost:6379/2'
)

# Prometheus metrics
http_request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

websocket_connections = Counter(
    'websocket_connections_total',
    'Total WebSocket connections'
)

websocket_messages = Counter(
    'websocket_messages_total',
    'Total WebSocket messages',
    ['event_type']
)

db_query_duration = Histogram(
    'db_query_duration_seconds',
    'Database query duration in seconds',
    ['query_type']
)

cache_hits = Counter(
    'cache_hits_total',
    'Total cache hits',
    ['cache_type']
)

cache_misses = Counter(
    'cache_misses_total',
    'Total cache misses',
    ['cache_type']
)

def init_extensions(app):
    """Initialize Flask extensions."""
    # Initialize SQLAlchemy
    db.init_app(app)
    
    # Initialize Flask-Migrate
    migrate.init_app(app, db)
    
    # Initialize Flask-JWT-Extended
    jwt.init_app(app)
    
    # Initialize CORS
    cors.init_app(app)
    
    # Initialize Flask-SocketIO
    socketio.init_app(
        app,
        cors_allowed_origins="*",  # Configure properly in production
        message_queue='redis://localhost:6379/1',
        async_mode='eventlet'
    )
    
    # Initialize Celery
    celery.conf.update(app.config)
    
    # Initialize Sentry
    if app.config.get('SENTRY_DSN'):
        sentry_sdk.init(
            dsn=app.config['SENTRY_DSN'],
            integrations=[
                FlaskIntegration(),
                RedisIntegration(),
                SqlalchemyIntegration()
            ],
            environment=app.config.get('FLASK_ENV', 'production'),
            traces_sample_rate=1.0
        )
    
    # Setup database connection pooling
    if not app.config['SQLALCHEMY_ENGINE_OPTIONS']:
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_size': 10,
            'max_overflow': 20,
            'pool_pre_ping': True,
            'pool_recycle': 300
        }
    
    # Setup Redis connection pool
    app.redis_pool = redis_client.connection_pool
    
    # Register metrics middleware
    @app.before_request
    def before_request():
        from flask import request, g
        import time
        g.start_time = time.time()
    
    @app.after_request
    def after_request(response):
        from flask import request, g
        import time
        
        # Record request duration
        duration = time.time() - g.start_time
        http_request_duration.labels(
            method=request.method,
            endpoint=request.endpoint
        ).observe(duration)
        
        # Count total requests
        http_requests_total.labels(
            method=request.method,
            endpoint=request.endpoint,
            status=response.status_code
        ).inc()
        
        return response
    
    # Register WebSocket metrics
    @socketio.on('connect')
    def handle_connect():
        websocket_connections.inc()
    
    @socketio.on_error_default
    def handle_error(e):
        if app.config.get('SENTRY_DSN'):
            sentry_sdk.capture_exception(e)
    
    # Setup database query metrics
    import sqlalchemy
    
    @sqlalchemy.event.listens_for(db.engine, 'before_cursor_execute')
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        conn.info.setdefault('query_start_time', []).append(time.time())
    
    @sqlalchemy.event.listens_for(db.engine, 'after_cursor_execute')
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        total = time.time() - conn.info['query_start_time'].pop()
        
        # Determine query type (SELECT, INSERT, etc.)
        query_type = statement.split()[0].upper()
        
        db_query_duration.labels(
            query_type=query_type
        ).observe(total)
    
    # Setup cache metrics
    def record_cache_operation(hit: bool, cache_type: str):
        if hit:
            cache_hits.labels(cache_type=cache_type).inc()
        else:
            cache_misses.labels(cache_type=cache_type).inc()
    
    app.record_cache_operation = record_cache_operation