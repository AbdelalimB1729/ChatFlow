import React, { createContext, useContext, useEffect, ReactNode } from 'react';
import { useAuth } from './AuthContext';
import { useSocket } from './SocketContext';
import { useChatStore } from '../stores/chatStore';
import { useUserStore } from '../stores/userStore';
import chatAPI from '../api/chatAPI';
import { Message, ChatRoom, TypingIndicator } from '../types/chatTypes';
import { SOCKET_EVENTS } from '../utils/constants';

interface ChatContextType {
  // State
  messages: Message[];
  currentRoom: ChatRoom | null;
  typingUsers: TypingIndicator[];
  isLoading: boolean;
  error: string | null;
  onlineUsers: any[];
  allUsers: any[];
  
  // Actions
  sendMessage: (content: string, roomId: string, messageType?: string) => void;
  joinRoom: (roomId: string) => void;
  leaveRoom: (roomId: string) => void;
  createRoom: (name: string, roomType?: string) => void;
  getMessages: (roomId: string, limit?: number, offset?: number) => void;
  markMessageRead: (messageId: string) => void;
  markMessageDelivered: (messageId: string) => void;
  startTyping: (roomId: string) => void;
  stopTyping: (roomId: string) => void;
  getOnlineUsers: () => void;
  getAllUsers: () => void;
  getUserProfile: (userId: string) => void;
  searchUsers: (query: string) => void;
  getUserStatistics: () => void;
  getRooms: () => void;
  updatePresence: () => void;
  setTypingStatus: (roomId: string, isTyping: boolean) => void;
  clearError: () => void;
  clearMessages: () => void;
  clearTypingUsers: () => void;
  reset: () => void;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

interface ChatProviderProps {
  children: ReactNode;
}

export const ChatProvider: React.FC<ChatProviderProps> = ({ children }) => {
  const { user, isAuthenticated } = useAuth();
  const { isConnected } = useSocket();
  
  const {
    messages,
    currentRoom,
    typingUsers,
    isLoading,
    error,
    setMessages,
    addMessage,
    updateMessage,
    setCurrentRoom,
    setTypingUsers,
    addTypingUser,
    removeTypingUser,
    setLoading,
    setError,
    clearError,
    clearMessages,
    clearTypingUsers,
    reset
  } = useChatStore();

  const {
    onlineUsers,
    allUsers,
    setOnlineUsers,
    setAllUsers,
    addOnlineUser,
    removeOnlineUser
  } = useUserStore();

  useEffect(() => {
    if (!isAuthenticated || !isConnected) return;

    // Chat event listeners
    const handleNewMessage = (message: Message) => {
      addMessage(message);
    };

    const handleMessageRead = (data: any) => {
      updateMessage(data.message_id, { read_by: [...(messages.find(m => m.message_id === data.message_id)?.read_by || []), data.user_id] });
    };

    const handleMessageDelivered = (data: any) => {
      updateMessage(data.message_id, { delivered_to: [...(messages.find(m => m.message_id === data.message_id)?.delivered_to || []), data.user_id] });
    };

    const handleRoomMessages = (data: any) => {
      setMessages(data.messages);
    };

    const handleJoinedRoom = (data: any) => {
      // Handle room joined confirmation
    };

    const handleLeftRoom = (data: any) => {
      // Handle room left confirmation
    };

    const handleUserJoinedRoom = (data: any) => {
      // Handle user joined room notification
    };

    const handleUserLeftRoom = (data: any) => {
      // Handle user left room notification
    };

    const handleUserTyping = (data: any) => {
      const typingUser: TypingIndicator = {
        user_id: data.user_id,
        room_id: data.room_id,
        username: data.username,
        is_typing: data.is_typing
      };
      
      if (data.is_typing) {
        addTypingUser(typingUser);
      } else {
        removeTypingUser(data.user_id, data.room_id);
      }
    };

    const handleTypingUsers = (data: any) => {
      // Handle typing users update
    };

    const handleRoomCreated = (room: ChatRoom) => {
      // Handle room created
    };

    const handleAvailableRooms = (data: any) => {
      // Handle available rooms update
    };

    const handleOnlineUsers = (data: any) => {
      setOnlineUsers(data.users);
    };

    const handleAllUsers = (data: any) => {
      setAllUsers(data.users);
    };

    const handleUserOnline = (data: any) => {
      addOnlineUser(data);
    };

    const handleUserOffline = (data: any) => {
      removeOnlineUser(data.user_id);
    };

    const handleError = (data: any) => {
      setError(data.message);
    };

    // Register event listeners
    chatAPI.onNewMessage(handleNewMessage);
    chatAPI.onMessageRead(handleMessageRead);
    chatAPI.onMessageDelivered(handleMessageDelivered);
    chatAPI.onRoomMessages(handleRoomMessages);
    chatAPI.onJoinedRoom(handleJoinedRoom);
    chatAPI.onLeftRoom(handleLeftRoom);
    chatAPI.onUserJoinedRoom(handleUserJoinedRoom);
    chatAPI.onUserLeftRoom(handleUserLeftRoom);
    chatAPI.onUserTyping(handleUserTyping);
    chatAPI.onTypingUsers(handleTypingUsers);
    chatAPI.onRoomCreated(handleRoomCreated);
    chatAPI.onAvailableRooms(handleAvailableRooms);
    chatAPI.onError(handleError);

    // Socket event listeners for user management
    chatAPI.onOnlineUsers(handleOnlineUsers);
    chatAPI.onAllUsers(handleAllUsers);
    chatAPI.onUserOnline(handleUserOnline);
    chatAPI.onUserOffline(handleUserOffline);

    return () => {
      // Cleanup event listeners
      chatAPI.offNewMessage(handleNewMessage);
      chatAPI.offMessageRead(handleMessageRead);
      chatAPI.offMessageDelivered(handleMessageDelivered);
      chatAPI.offRoomMessages(handleRoomMessages);
      chatAPI.offJoinedRoom(handleJoinedRoom);
      chatAPI.offLeftRoom(handleLeftRoom);
      chatAPI.offUserJoinedRoom(handleUserJoinedRoom);
      chatAPI.offUserLeftRoom(handleUserLeftRoom);
      chatAPI.offUserTyping(handleUserTyping);
      chatAPI.offTypingUsers(handleTypingUsers);
      chatAPI.offRoomCreated(handleRoomCreated);
      chatAPI.offAvailableRooms(handleAvailableRooms);
      chatAPI.offError(handleError);
    };
  }, [isAuthenticated, isConnected, user]);

  const sendMessage = (content: string, roomId: string, messageType: string = 'text') => {
    if (!user) return;
    chatAPI.sendMessage({ content, room_id: roomId, message_type: messageType });
  };

  const joinRoom = (roomId: string) => {
    if (!user) return;
    chatAPI.joinRoom({ room_id: roomId });
  };

  const leaveRoom = (roomId: string) => {
    if (!user) return;
    chatAPI.leaveRoom({ room_id: roomId });
  };

  const createRoom = (name: string, roomType: string = 'public') => {
    if (!user) return;
    chatAPI.createRoom(name, roomType);
  };

  const getMessages = (roomId: string, limit: number = 50, offset: number = 0) => {
    chatAPI.getMessages(roomId, limit, offset);
  };

  const markMessageRead = (messageId: string) => {
    if (!user) return;
    chatAPI.markMessageRead(messageId);
  };

  const markMessageDelivered = (messageId: string) => {
    if (!user) return;
    chatAPI.markMessageDelivered(messageId);
  };

  const startTyping = (roomId: string) => {
    if (!user) return;
    chatAPI.startTyping(roomId);
  };

  const stopTyping = (roomId: string) => {
    if (!user) return;
    chatAPI.stopTyping(roomId);
  };

  const getOnlineUsers = () => {
    chatAPI.getOnlineUsers();
  };

  const getAllUsers = () => {
    chatAPI.getAllUsers();
  };

  const getUserProfile = (userId: string) => {
    chatAPI.getUserProfile(userId);
  };

  const searchUsers = (query: string) => {
    chatAPI.searchUsers(query);
  };

  const getUserStatistics = () => {
    chatAPI.getUserStatistics();
  };

  const getRooms = () => {
    chatAPI.getRooms();
  };

  const updatePresence = () => {
    if (!user) return;
    chatAPI.updatePresence();
  };

  const setTypingStatus = (roomId: string, isTyping: boolean) => {
    if (!user) return;
    chatAPI.setTypingStatus(roomId, isTyping);
  };

  const value: ChatContextType = {
    messages,
    currentRoom,
    typingUsers,
    isLoading,
    error,
    onlineUsers,
    allUsers,
    sendMessage,
    joinRoom,
    leaveRoom,
    createRoom,
    getMessages,
    markMessageRead,
    markMessageDelivered,
    startTyping,
    stopTyping,
    getOnlineUsers,
    getAllUsers,
    getUserProfile,
    searchUsers,
    getUserStatistics,
    getRooms,
    updatePresence,
    setTypingStatus,
    clearError,
    clearMessages,
    clearTypingUsers,
    reset
  };

  return (
    <ChatContext.Provider value={value}>
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = (): ChatContextType => {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
}; 