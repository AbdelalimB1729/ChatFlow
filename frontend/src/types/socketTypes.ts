export interface SocketEvent {
  event: string;
  data: any;
}

export interface ConnectionState {
  isConnected: boolean;
  isConnecting: boolean;
  error: string | null;
}

export interface SocketConfig {
  url: string;
  options: {
    transports: string[];
    autoConnect: boolean;
    reconnection: boolean;
    reconnectionAttempts: number;
    reconnectionDelay: number;
  };
}

export interface SocketResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface HeartbeatData {
  timestamp: string;
  status: 'alive' | 'dead';
}

export interface ErrorResponse {
  message: string;
  details?: string;
}

export interface ConnectedResponse {
  message: string;
  version: string;
}

export interface AuthenticatedResponse {
  user_id: string;
  username: string;
  email: string;
  message: string;
}

export interface RegisteredResponse {
  user: {
    user_id: string;
    username: string;
    email: string;
  };
  token: string;
  message: string;
}

export interface LoggedInResponse {
  user: {
    user_id: string;
    username: string;
    email: string;
  };
  token: string;
  message: string;
} 