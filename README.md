# ChatFlow

ChatFlow is a modern, real-time chat application built with Python (Flask) backend and React TypeScript frontend. It features a robust architecture with real-time messaging, user authentication, and advanced security measures.

## Features

### Backend
- **Authentication & Authorization**
  - JWT-based authentication with refresh tokens
  - Role-based access control
  - Email verification
  - Password reset functionality
  - Session management across devices

- **Real-time Communication**
  - WebSocket-based messaging
  - Typing indicators
  - Online presence tracking
  - Message read receipts

- **Chat Features**
  - Group chat rooms
  - Private messaging
  - File sharing
  - Message history
  - User mentions

- **Security**
  - Rate limiting
  - Input validation
  - XSS protection
  - CSRF protection
  - SQL injection prevention

- **Performance**
  - Redis caching
  - Database connection pooling
  - Message pagination
  - WebSocket message queuing

### Frontend
- **Modern UI Components**
  - Material-UI based design
  - Responsive layout
  - Dark/light theme support
  - Animated transitions

- **Real-time Features**
  - Instant messaging
  - Live typing indicators
  - Online status updates
  - Real-time notifications

- **Performance Optimizations**
  - Virtual scrolling for messages
  - Lazy loading of images
  - Efficient state management
  - Optimistic updates

## Technology Stack

### Backend
- Flask
- Flask-SocketIO
- SQLAlchemy
- Redis
- Celery
- JWT
- PostgreSQL

### Frontend
- React
- TypeScript
- Material-UI
- Socket.IO Client
- React Query
- Zustand

## Getting Started

### Prerequisites
- Python 3.8+
- Node.js 16+
- Redis
- PostgreSQL

### Backend Setup

1. Create a virtual environment:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Initialize the database:
   ```bash
   flask db upgrade
   ```

5. Run the server:
   ```bash
   python run.py
   ```

### Frontend Setup

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. Run the development server:
   ```bash
   npm start
   ```

## Project Structure

### Backend
```
backend/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── models.py
│   ├── extensions.py
│   ├── events/
│   │   ├── connection_events.py
│   │   ├── message_events.py
│   │   └── user_events.py
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── chat_service.py
│   │   └── user_service.py
│   ├── sockets/
│   │   ├── chat_namespace.py
│   │   └── main_socket.py
│   └── utils/
│       ├── decorators.py
│       └── validators.py
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   └── test_chat.py
└── requirements.txt
```

### Frontend
```
frontend/
├── public/
├── src/
│   ├── api/
│   ├── components/
│   │   ├── chat/
│   │   ├── layout/
│   │   ├── ui/
│   │   └── user/
│   ├── contexts/
│   ├── hooks/
│   ├── stores/
│   ├── types/
│   └── utils/
├── package.json
└── tsconfig.json
```

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

### E2E Tests
```bash
cd frontend
npm run test:e2e
```

## Security Considerations

- All passwords are hashed using bcrypt
- JWT tokens are short-lived with refresh token rotation
- Rate limiting is implemented on sensitive endpoints
- Input validation and sanitization for all user inputs
- CORS is properly configured
- WebSocket connections are authenticated
- File uploads are validated and scanned
- SQL queries are parameterized

## Performance Optimizations

- Redis caching for frequently accessed data
- Database connection pooling
- WebSocket message queuing
- Frontend virtual scrolling
- Efficient state management
- Asset optimization and lazy loading
- API response pagination

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Flask](https://flask.palletsprojects.com/)
- [React](https://reactjs.org/)
- [Material-UI](https://mui.com/)
- [Socket.IO](https://socket.io/)