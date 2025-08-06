import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import socketAPI from '../api/socket';
import { ConnectionState } from '../types/socketTypes';
import { SOCKET_EVENTS } from '../utils/constants';

interface SocketContextType extends ConnectionState {
  connect: () => Promise<void>;
  connectToChat: () => Promise<void>;
  disconnect: () => void;
  isConnected: () => boolean;
  isConnecting: () => boolean;
}

const SocketContext = createContext<SocketContextType | undefined>(undefined);

interface SocketProviderProps {
  children: ReactNode;
}

export const SocketProvider: React.FC<SocketProviderProps> = ({ children }) => {
  const [connectionState, setConnectionState] = useState<ConnectionState>({
    isConnected: false,
    isConnecting: false,
    error: null
  });

  useEffect(() => {
    const updateConnectionState = () => {
      const state = socketAPI.getConnectionState();
      setConnectionState(state);
    };

    const handleConnected = () => {
      setConnectionState(prev => ({
        ...prev,
        isConnected: true,
        isConnecting: false,
        error: null
      }));
    };

    const handleDisconnected = () => {
      setConnectionState(prev => ({
        ...prev,
        isConnected: false,
        isConnecting: false
      }));
    };

    const handleError = (data: any) => {
      setConnectionState(prev => ({
        ...prev,
        error: data.message,
        isConnecting: false
      }));
    };

    const handleConnectError = (error: any) => {
      setConnectionState(prev => ({
        ...prev,
        error: error.message,
        isConnecting: false
      }));
    };

    // Register event listeners
    socketAPI.on(SOCKET_EVENTS.CONNECT, handleConnected);
    socketAPI.on(SOCKET_EVENTS.DISCONNECT, handleDisconnected);
    socketAPI.on(SOCKET_EVENTS.ERROR, handleError);
    socketAPI.on('connect_error', handleConnectError);

    // Initial state update
    updateConnectionState();

    return () => {
      // Cleanup event listeners
      socketAPI.off(SOCKET_EVENTS.CONNECT, handleConnected);
      socketAPI.off(SOCKET_EVENTS.DISCONNECT, handleDisconnected);
      socketAPI.off(SOCKET_EVENTS.ERROR, handleError);
      socketAPI.off('connect_error', handleConnectError);
    };
  }, []);

  const connect = async (): Promise<void> => {
    try {
      setConnectionState(prev => ({ ...prev, isConnecting: true, error: null }));
      await socketAPI.connect();
    } catch (error) {
      setConnectionState(prev => ({
        ...prev,
        isConnecting: false,
        error: error instanceof Error ? error.message : 'Connection failed'
      }));
      throw error;
    }
  };

  const connectToChat = async (): Promise<void> => {
    try {
      await socketAPI.connectToChat();
    } catch (error) {
      setConnectionState(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Chat connection failed'
      }));
      throw error;
    }
  };

  const disconnect = (): void => {
    socketAPI.disconnect();
  };

  const isConnected = (): boolean => {
    return socketAPI.isConnected();
  };

  const isConnecting = (): boolean => {
    return socketAPI.isConnecting();
  };

  const value: SocketContextType = {
    ...connectionState,
    connect,
    connectToChat,
    disconnect,
    isConnected,
    isConnecting
  };

  return (
    <SocketContext.Provider value={value}>
      {children}
    </SocketContext.Provider>
  );
};

export const useSocket = (): SocketContextType => {
  const context = useContext(SocketContext);
  if (context === undefined) {
    throw new Error('useSocket must be used within a SocketProvider');
  }
  return context;
}; 