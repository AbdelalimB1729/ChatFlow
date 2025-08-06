import React, { createContext, useCallback, useContext, useEffect, useReducer } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useSocket } from '../hooks/useSocket';
import { useAuth } from '../hooks/useAuth';
import { Message, Room, ChatState, ChatAction, ChatContextType } from '../types/chatTypes';
import { debounce } from 'lodash';

const initialState: ChatState = {
  activeRoom: null,
  rooms: [],
  messages: {},
  typingUsers: {},
  onlineUsers: new Set(),
  unreadCounts: {},
  lastReadTimestamps: {},
};

function chatReducer(state: ChatState, action: ChatAction): ChatState {
  switch (action.type) {
    case 'SET_ACTIVE_ROOM':
      return {
        ...state,
        activeRoom: action.payload,
      };
    case 'SET_ROOMS':
      return {
        ...state,
        rooms: action.payload,
      };
    case 'ADD_ROOM':
      return {
        ...state,
        rooms: [...state.rooms, action.payload],
      };
    case 'UPDATE_ROOM':
      return {
        ...state,
        rooms: state.rooms.map(room =>
          room.id === action.payload.id ? { ...room, ...action.payload } : room
        ),
      };
    case 'SET_MESSAGES':
      return {
        ...state,
        messages: {
          ...state.messages,
          [action.payload.roomId]: action.payload.messages,
        },
      };
    case 'ADD_MESSAGE':
      const roomId = action.payload.roomId;
      return {
        ...state,
        messages: {
          ...state.messages,
          [roomId]: [...(state.messages[roomId] || []), action.payload.message],
        },
        unreadCounts: {
          ...state.unreadCounts,
          [roomId]: state.activeRoom?.id !== roomId 
            ? (state.unreadCounts[roomId] || 0) + 1 
            : 0,
        },
      };
    case 'SET_TYPING_USERS':
      return {
        ...state,
        typingUsers: {
          ...state.typingUsers,
          [action.payload.roomId]: action.payload.users,
        },
      };
    case 'SET_ONLINE_USERS':
      return {
        ...state,
        onlineUsers: new Set(action.payload),
      };
    case 'UPDATE_UNREAD_COUNTS':
      return {
        ...state,
        unreadCounts: {
          ...state.unreadCounts,
          [action.payload.roomId]: action.payload.count,
        },
      };
    case 'MARK_ROOM_READ':
      return {
        ...state,
        unreadCounts: {
          ...state.unreadCounts,
          [action.payload]: 0,
        },
        lastReadTimestamps: {
          ...state.lastReadTimestamps,
          [action.payload]: new Date().toISOString(),
        },
      };
    default:
      return state;
  }
}

const ChatContext = createContext<ChatContextType | null>(null);

export function ChatProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(chatReducer, initialState);
  const { socket } = useSocket();
  const { user } = useAuth();
  const queryClient = useQueryClient();

  // Handle real-time events
  useEffect(() => {
    if (!socket || !user) return;

    socket.on('message:new', (message: Message) => {
      dispatch({
        type: 'ADD_MESSAGE',
        payload: { roomId: message.roomId, message },
      });
      
      // Update room's last message
      const room = state.rooms.find(r => r.id === message.roomId);
      if (room) {
        dispatch({
          type: 'UPDATE_ROOM',
          payload: {
            ...room,
            lastMessage: message,
            lastActivity: new Date().toISOString(),
          },
        });
      }
    });

    socket.on('room:update', (room: Room) => {
      dispatch({ type: 'UPDATE_ROOM', payload: room });
    });

    socket.on('typing:update', ({ roomId, users }: { roomId: string; users: string[] }) => {
      dispatch({
        type: 'SET_TYPING_USERS',
        payload: { roomId, users },
      });
    });

    socket.on('presence:update', (onlineUserIds: string[]) => {
      dispatch({ type: 'SET_ONLINE_USERS', payload: onlineUserIds });
    });

    return () => {
      socket.off('message:new');
      socket.off('room:update');
      socket.off('typing:update');
      socket.off('presence:update');
    };
  }, [socket, user, state.rooms]);

  // Handle typing indicator
  const debouncedEmitTyping = useCallback(
    debounce((roomId: string, isTyping: boolean) => {
      socket?.emit('typing:status', { roomId, isTyping });
    }, 300),
    [socket]
  );

  const handleTyping = useCallback(
    (roomId: string) => {
      if (!socket || !state.activeRoom) return;
      debouncedEmitTyping(roomId, true);
    },
    [socket, state.activeRoom, debouncedEmitTyping]
  );

  // Message handling
  const sendMessage = useCallback(
    async (roomId: string, content: string, attachments?: File[]) => {
      if (!socket || !user) return;

      try {
        // Handle file uploads if any
        let fileUrls: string[] = [];
        if (attachments?.length) {
          fileUrls = await Promise.all(
            attachments.map(async (file) => {
              const formData = new FormData();
              formData.append('file', file);
              const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData,
              });
              const data = await response.json();
              return data.url;
            })
          );
        }

        // Emit message with optional attachments
        socket.emit('message:send', {
          roomId,
          content,
          attachments: fileUrls,
        });

        // Stop typing indicator
        debouncedEmitTyping(roomId, false);
      } catch (error) {
        console.error('Error sending message:', error);
        throw error;
      }
    },
    [socket, user, debouncedEmitTyping]
  );

  // Room management
  const createRoom = useCallback(
    async (name: string, members: string[], isPrivate: boolean = false) => {
      if (!socket || !user) return;

      try {
        const response = await fetch('/api/rooms', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name, members, isPrivate }),
        });

        const room = await response.json();
        dispatch({ type: 'ADD_ROOM', payload: room });
        return room;
      } catch (error) {
        console.error('Error creating room:', error);
        throw error;
      }
    },
    [socket, user]
  );

  const joinRoom = useCallback(
    (roomId: string) => {
      if (!socket || !user) return;

      socket.emit('room:join', { roomId });
      dispatch({ type: 'SET_ACTIVE_ROOM', payload: roomId });

      // Mark room as read when joining
      dispatch({ type: 'MARK_ROOM_READ', payload: roomId });
    },
    [socket, user]
  );

  const leaveRoom = useCallback(
    (roomId: string) => {
      if (!socket || !user) return;

      socket.emit('room:leave', { roomId });
      if (state.activeRoom === roomId) {
        dispatch({ type: 'SET_ACTIVE_ROOM', payload: null });
      }
    },
    [socket, user, state.activeRoom]
  );

  // Message loading and pagination
  const loadMessages = useCallback(
    async (roomId: string, page: number = 1) => {
      try {
        const response = await fetch(`/api/rooms/${roomId}/messages?page=${page}`);
        const data = await response.json();
        
        dispatch({
          type: 'SET_MESSAGES',
          payload: {
            roomId,
            messages: page === 1 ? data.messages : [...(state.messages[roomId] || []), ...data.messages],
          },
        });
        
        return data;
      } catch (error) {
        console.error('Error loading messages:', error);
        throw error;
      }
    },
    [state.messages]
  );

  // Context value
  const value = {
    activeRoom: state.activeRoom,
    rooms: state.rooms,
    messages: state.messages,
    typingUsers: state.typingUsers,
    onlineUsers: state.onlineUsers,
    unreadCounts: state.unreadCounts,
    lastReadTimestamps: state.lastReadTimestamps,
    sendMessage,
    handleTyping,
    createRoom,
    joinRoom,
    leaveRoom,
    loadMessages,
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
}

export function useChat() {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
}