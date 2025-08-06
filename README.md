# ChatBridgePro

An enterprise-grade, modular real-time chat application built with Flask backend and React frontend with TypeScript.

## Features

### Backend Features
- **Modular Architecture**: Clean separation of concerns with services, events, and utilities
- **Socket.IO Integration**: Real-time communication with namespaces for different features
- **JWT Authentication**: Secure token-based authentication system
- **Rate Limiting**: Built-in rate limiting for messages and connections
- **Message Validation**: Comprehensive input validation and sanitization
- **Typing Indicators**: Real-time typing status for users
- **Message Read Receipts**: Track message delivery and read status
- **Online Status Tracking**: Monitor user presence and activity
- **Heartbeat System**: Connection monitoring and health checks
- **Error Handling**: Robust error handling and logging

### Frontend Features
- **React with TypeScript**: Modern, type-safe frontend development
- **Context API**: Centralized state management
- **Custom Hooks**: Reusable logic for socket operations and chat functionality
- **Zustand Stores**: Lightweight state management for persistence
- **Responsive Design**: Mobile-first responsive layout
- **Real-time Updates**: Live message updates and user presence
- **Typing Indicators**: Visual feedback for user typing activity
- **Message Read Receipts**: Visual indicators for message status
- **Error Boundaries**: Graceful error handling and recovery
- **Loading States**: Comprehensive loading and error states

## Project Structure

```
ChatBridgePro/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── extensions.py
│   │   ├── models.py
│   │   ├── events/
│   │   │   ├── connection_events.py
│   │   │   ├── message_events.py
│   │   │   └── user_events.py
│   │   ├── services/
│   │   │   ├── auth_service.py
│   │   │   ├── chat_service.py
│   │   │   └── user_service.py
│   │   ├── sockets/
│   │   │   ├── chat_namespace.py
│   │   │   └── main_socket.py
│   │   └── utils/
│   │       ├── decorators.py
│   │       └── validators.py
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── api/
│   │   │   ├── socket.ts
│   │   │   └── chatAPI.ts
│   │   ├── components/
│   │   │   ├── chat/
│   │   │   │   ├── ChatContainer.tsx
│   │   │   │   ├── MessageInput.tsx
│   │   │   │   ├── MessageList.tsx
│   │   │   │   └── TypingIndicator.tsx
│   │   │   ├── user/
│   │   │   │   ├── UserList.tsx
│   │   │   │   ├── UserProfile.tsx
│   │   │   │   └── AuthForm.tsx
│   │   │   ├── ui/
│   │   │   │   ├── Notification.tsx
│   │   │   │   ├── Loader.tsx
│   │   │   │   └── ErrorBoundary.tsx
│   │   │   └── layout/
│   │   │       ├── MainLayout.tsx
│   │   │       └── Sidebar.tsx
│   │   ├── contexts/
│   │   │   ├── ChatContext.tsx
│   │   │   ├── SocketContext.tsx
│   │   │   └── AuthContext.tsx
│   │   ├── hooks/
│   │   │   ├── useSocket.ts
│   │   │   ├── useChat.ts
│   │   │   └── useAuth.ts
│   │   ├── stores/
│   │   │   ├── chatStore.ts
│   │   │   └── userStore.ts
│   │   ├── types/
│   │   │   ├── chatTypes.ts
│   │   │   ├── userTypes.ts
│   │   │   └── socketTypes.ts
│   │   ├── utils/
│   │   │   ├── formatters.ts
│   │   │   ├── validators.ts
│   │   │   └── constants.ts
│   │   ├── App.tsx
│   │   ├── index.tsx
│   │   └── index.css
│   ├── package.json
│   └── tsconfig.json
└── README.md
```

## Installation

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables (create a `.env` file):
```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-super-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production
SOCKET_CORS_ORIGINS=http://localhost:3001
```

5. Run the backend server:
```bash
python run.py
```

The backend will run on `http://localhost:5001`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The frontend will run on `http://localhost:3001`

## Usage

1. Open your browser and navigate to `http://localhost:3001`
2. Register a new account or login with existing credentials
3. Start chatting in the real-time chat interface
4. Use the sidebar to view online users and manage rooms

## API Endpoints

### Socket Events

#### Authentication
- `authenticate` - Authenticate user with JWT token
- `register` - Register new user
- `login` - Login user
- `logout` - Logout user

#### Chat
- `join_room` - Join a chat room
- `leave_room` - Leave a chat room
- `send_message` - Send a message
- `get_messages` - Get room messages
- `mark_read` - Mark message as read
- `mark_delivered` - Mark message as delivered

#### Typing
- `typing_start` - Start typing indicator
- `typing_stop` - Stop typing indicator
- `get_typing_users` - Get typing users

#### Users
- `get_online_users` - Get online users
- `get_all_users` - Get all users
- `get_user_profile` - Get user profile
- `search_users` - Search users
- `get_user_statistics` - Get user statistics

#### Rooms
- `create_room` - Create new room
- `get_rooms` - Get available rooms

## Configuration

### Backend Configuration

The backend configuration is managed through the `Config` class in `backend/app/config.py`:

- `SECRET_KEY`: Flask secret key
- `JWT_SECRET_KEY`: JWT token secret
- `SOCKET_CORS_ORIGINS`: CORS origins for Socket.IO
- `MESSAGE_QUEUE_SIZE`: Maximum message queue size
- `RATE_LIMIT_MESSAGES`: Rate limit for messages per minute
- `RATE_LIMIT_CONNECTIONS`: Rate limit for connections per minute
- `HEARTBEAT_INTERVAL`: Heartbeat interval in seconds
- `TYPING_TIMEOUT`: Typing indicator timeout

### Frontend Configuration

The frontend configuration is managed through constants in `frontend/src/utils/constants.ts`:

- `SOCKET_URL`: Backend socket URL
- `HEARTBEAT_INTERVAL`: Heartbeat interval
- `TYPING_TIMEOUT`: Typing indicator timeout
- `MESSAGE_LIMIT`: Message pagination limit

## Development

### Backend Development

The backend follows a modular architecture:

- **Models**: Data models and in-memory storage
- **Services**: Business logic layer
- **Events**: Socket event handlers
- **Utils**: Utility functions and decorators

### Frontend Development

The frontend follows modern React patterns:

- **Contexts**: State management with React Context
- **Hooks**: Custom hooks for reusable logic
- **Stores**: Zustand stores for state persistence
- **Components**: Reusable UI components

## Security Features

- JWT token-based authentication
- Input validation and sanitization
- Rate limiting for API endpoints
- CORS configuration
- Error handling and logging

## Performance Features

- Message pagination
- Typing indicator timeouts
- Connection heartbeat monitoring
- Efficient state management
- Optimized re-renders with React.memo

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please open an issue on the GitHub repository. 