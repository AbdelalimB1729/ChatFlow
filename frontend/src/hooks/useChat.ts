import { useEffect, useCallback, useRef } from 'react';
import { useChat as useChatContext } from '../contexts/ChatContext';
import { useAuth } from '../contexts/AuthContext';
import { validateMessage } from '../utils/validators';
import { TYPING_TIMEOUT } from '../utils/constants';

export const useChat = () => {
  const chatContext = useChatContext();
  const { user } = useAuth();
  const typingTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const sendMessage = useCallback((content: string, roomId: string, messageType: string = 'text') => {
    if (!user) return;

    const validation = validateMessage(content);
    if (!validation.isValid) {
      chatContext.setError(validation.errors[0]);
      return;
    }

    chatContext.sendMessage(content, roomId, messageType);
    chatContext.clearError();
  }, [user, chatContext]);

  const joinRoom = useCallback((roomId: string) => {
    if (!user) return;
    chatContext.joinRoom(roomId);
  }, [user, chatContext]);

  const leaveRoom = useCallback((roomId: string) => {
    if (!user) return;
    chatContext.leaveRoom(roomId);
  }, [user, chatContext]);

  const startTyping = useCallback((roomId: string) => {
    if (!user) return;
    
    // Clear existing timeout
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }
    
    chatContext.startTyping(roomId);
    
    // Set timeout to stop typing
    typingTimeoutRef.current = setTimeout(() => {
      chatContext.stopTyping(roomId);
    }, TYPING_TIMEOUT);
  }, [user, chatContext]);

  const stopTyping = useCallback((roomId: string) => {
    if (!user) return;
    
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
      typingTimeoutRef.current = null;
    }
    
    chatContext.stopTyping(roomId);
  }, [user, chatContext]);

  const markMessageRead = useCallback((messageId: string) => {
    if (!user) return;
    chatContext.markMessageRead(messageId);
  }, [user, chatContext]);

  const markMessageDelivered = useCallback((messageId: string) => {
    if (!user) return;
    chatContext.markMessageDelivered(messageId);
  }, [user, chatContext]);

  const createRoom = useCallback((name: string, roomType: string = 'public') => {
    if (!user) return;
    chatContext.createRoom(name, roomType);
  }, [user, chatContext]);

  const getMessages = useCallback((roomId: string, limit: number = 50, offset: number = 0) => {
    chatContext.getMessages(roomId, limit, offset);
  }, [chatContext]);

  const getOnlineUsers = useCallback(() => {
    chatContext.getOnlineUsers();
  }, [chatContext]);

  const getAllUsers = useCallback(() => {
    chatContext.getAllUsers();
  }, [chatContext]);

  const getUserProfile = useCallback((userId: string) => {
    chatContext.getUserProfile(userId);
  }, [chatContext]);

  const searchUsers = useCallback((query: string) => {
    chatContext.searchUsers(query);
  }, [chatContext]);

  const getUserStatistics = useCallback(() => {
    chatContext.getUserStatistics();
  }, [chatContext]);

  const getRooms = useCallback(() => {
    chatContext.getRooms();
  }, [chatContext]);

  const updatePresence = useCallback(() => {
    if (!user) return;
    chatContext.updatePresence();
  }, [user, chatContext]);

  const clearError = useCallback(() => {
    chatContext.clearError();
  }, [chatContext]);

  const clearMessages = useCallback(() => {
    chatContext.clearMessages();
  }, [chatContext]);

  const clearTypingUsers = useCallback(() => {
    chatContext.clearTypingUsers();
  }, [chatContext]);

  const reset = useCallback(() => {
    chatContext.reset();
  }, [chatContext]);

  // Cleanup typing timeout on unmount
  useEffect(() => {
    return () => {
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
    };
  }, []);

  return {
    ...chatContext,
    sendMessage,
    joinRoom,
    leaveRoom,
    startTyping,
    stopTyping,
    markMessageRead,
    markMessageDelivered,
    createRoom,
    getMessages,
    getOnlineUsers,
    getAllUsers,
    getUserProfile,
    searchUsers,
    getUserStatistics,
    getRooms,
    updatePresence,
    clearError,
    clearMessages,
    clearTypingUsers,
    reset
  };
}; 