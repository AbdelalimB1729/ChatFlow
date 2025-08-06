import { useEffect, useCallback } from 'react';
import { useSocket as useSocketContext } from '../contexts/SocketContext';
import { useAuth } from '../contexts/AuthContext';
import socketAPI from '../api/socket';

export const useSocket = () => {
  const socketContext = useSocketContext();
  const { user, isAuthenticated } = useAuth();

  const connect = useCallback(async () => {
    try {
      await socketContext.connect();
      if (isAuthenticated && user) {
        await socketContext.connectToChat();
      }
    } catch (error) {
      console.error('Socket connection failed:', error);
      throw error;
    }
  }, [socketContext, isAuthenticated, user]);

  const disconnect = useCallback(() => {
    socketContext.disconnect();
  }, [socketContext]);

  useEffect(() => {
    if (isAuthenticated && user) {
      connect();
    }
  }, [isAuthenticated, user, connect]);

  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    ...socketContext,
    connect,
    disconnect
  };
}; 