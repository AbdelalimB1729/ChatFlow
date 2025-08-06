import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { AuthState, AuthUser, LoginData, RegisterData } from '../types/userTypes';
import socketAPI from '../api/socket';
import { SOCKET_EVENTS } from '../utils/constants';

interface AuthContextType extends AuthState {
  login: (data: LoginData) => void;
  register: (data: RegisterData) => void;
  logout: () => void;
  authenticate: (token: string) => void;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

type AuthAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_USER'; payload: AuthUser }
  | { type: 'SET_ERROR'; payload: string }
  | { type: 'CLEAR_ERROR' }
  | { type: 'LOGOUT' };

const authReducer = (state: AuthState, action: AuthAction): AuthState => {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    case 'SET_USER':
      return { 
        ...state, 
        user: action.payload, 
        isAuthenticated: true, 
        error: null,
        isLoading: false 
      };
    case 'SET_ERROR':
      return { ...state, error: action.payload, isLoading: false };
    case 'CLEAR_ERROR':
      return { ...state, error: null };
    case 'LOGOUT':
      return { 
        ...state, 
        user: null, 
        isAuthenticated: false, 
        error: null,
        isLoading: false 
      };
    default:
      return state;
  }
};

const initialState: AuthState = {
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  useEffect(() => {
    // Check for stored token on mount
    const token = localStorage.getItem('authToken');
    if (token) {
      authenticate(token);
    }
  }, []);

  useEffect(() => {
    // Socket event listeners
    const handleAuthenticated = (data: any) => {
      const user: AuthUser = {
        user_id: data.user_id,
        username: data.username,
        email: data.email,
        token: localStorage.getItem('authToken') || ''
      };
      dispatch({ type: 'SET_USER', payload: user });
    };

    const handleRegistered = (data: any) => {
      const user: AuthUser = {
        user_id: data.user.user_id,
        username: data.user.username,
        email: data.user.email,
        token: data.token
      };
      localStorage.setItem('authToken', data.token);
      dispatch({ type: 'SET_USER', payload: user });
    };

    const handleLoggedIn = (data: any) => {
      const user: AuthUser = {
        user_id: data.user.user_id,
        username: data.user.username,
        email: data.user.email,
        token: data.token
      };
      localStorage.setItem('authToken', data.token);
      dispatch({ type: 'SET_USER', payload: user });
    };

    const handleLoggedOut = () => {
      localStorage.removeItem('authToken');
      dispatch({ type: 'LOGOUT' });
    };

    const handleError = (data: any) => {
      dispatch({ type: 'SET_ERROR', payload: data.message });
    };

    // Register event listeners
    socketAPI.on(SOCKET_EVENTS.AUTHENTICATED, handleAuthenticated);
    socketAPI.on(SOCKET_EVENTS.REGISTERED, handleRegistered);
    socketAPI.on(SOCKET_EVENTS.LOGGED_IN, handleLoggedIn);
    socketAPI.on(SOCKET_EVENTS.LOGGED_OUT, handleLoggedOut);
    socketAPI.on(SOCKET_EVENTS.ERROR, handleError);

    return () => {
      // Cleanup event listeners
      socketAPI.off(SOCKET_EVENTS.AUTHENTICATED, handleAuthenticated);
      socketAPI.off(SOCKET_EVENTS.REGISTERED, handleRegistered);
      socketAPI.off(SOCKET_EVENTS.LOGGED_IN, handleLoggedIn);
      socketAPI.off(SOCKET_EVENTS.LOGGED_OUT, handleLoggedOut);
      socketAPI.off(SOCKET_EVENTS.ERROR, handleError);
    };
  }, []);

  const login = (data: LoginData) => {
    dispatch({ type: 'SET_LOADING', payload: true });
    dispatch({ type: 'CLEAR_ERROR' });
    socketAPI.login(data.username, data.password);
  };

  const register = (data: RegisterData) => {
    dispatch({ type: 'SET_LOADING', payload: true });
    dispatch({ type: 'CLEAR_ERROR' });
    socketAPI.register(data.username, data.email, data.password);
  };

  const logout = () => {
    socketAPI.logout();
  };

  const authenticate = (token: string) => {
    dispatch({ type: 'SET_LOADING', payload: true });
    dispatch({ type: 'CLEAR_ERROR' });
    socketAPI.authenticate(token);
  };

  const clearError = () => {
    dispatch({ type: 'CLEAR_ERROR' });
  };

  const value: AuthContextType = {
    ...state,
    login,
    register,
    logout,
    authenticate,
    clearError
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}; 