export const SOCKET_URL = 'http://localhost:5001';
export const CHAT_NAMESPACE = '/chat';
export const MAIN_NAMESPACE = '/';

export const SOCKET_EVENTS = {
  // Connection events
  CONNECT: 'connect',
  DISCONNECT: 'disconnect',
  CONNECTED: 'connected',
  
  // Authentication events
  AUTHENTICATE: 'authenticate',
  AUTHENTICATED: 'authenticated',
  REGISTER: 'register',
  REGISTERED: 'registered',
  LOGIN: 'login',
  LOGGED_IN: 'logged_in',
  LOGOUT: 'logout',
  LOGGED_OUT: 'logged_out',
  
  // Room events
  JOIN_ROOM: 'join_room',
  JOINED_ROOM: 'joined_room',
  LEAVE_ROOM: 'leave_room',
  LEFT_ROOM: 'left_room',
  USER_JOINED_ROOM: 'user_joined_room',
  USER_LEFT_ROOM: 'user_left_room',
  
  // Message events
  SEND_MESSAGE: 'send_message',
  NEW_MESSAGE: 'new_message',
  MESSAGE_SENT: 'message_sent',
  MARK_READ: 'mark_read',
  MESSAGE_READ: 'message_read',
  MARK_DELIVERED: 'mark_delivered',
  MESSAGE_DELIVERED: 'message_delivered',
  GET_MESSAGES: 'get_messages',
  ROOM_MESSAGES: 'room_messages',
  
  // Typing events
  TYPING_START: 'typing_start',
  TYPING_STOP: 'typing_stop',
  USER_TYPING: 'user_typing',
  GET_TYPING_USERS: 'get_typing_users',
  TYPING_USERS: 'typing_users',
  
  // User events
  GET_ONLINE_USERS: 'get_online_users',
  ONLINE_USERS: 'online_users',
  GET_ALL_USERS: 'get_all_users',
  ALL_USERS: 'all_users',
  USER_ONLINE: 'user_online',
  USER_OFFLINE: 'user_offline',
  GET_USER_PROFILE: 'get_user_profile',
  USER_PROFILE: 'user_profile',
  SEARCH_USERS: 'search_users',
  SEARCH_RESULTS: 'search_results',
  GET_USER_STATISTICS: 'get_user_statistics',
  USER_STATISTICS: 'user_statistics',
  
  // Room management
  CREATE_ROOM: 'create_room',
  ROOM_CREATED: 'room_created',
  ROOM_CREATED_CONFIRMATION: 'room_created_confirmation',
  GET_ROOMS: 'get_rooms',
  AVAILABLE_ROOMS: 'available_rooms',
  
  // Presence
  UPDATE_PRESENCE: 'update_presence',
  USER_PRESENCE_UPDATED: 'user_presence_updated',
  SET_TYPING_STATUS: 'set_typing_status',
  USER_TYPING_STATUS: 'user_typing_status',
  
  // Heartbeat
  HEARTBEAT: 'heartbeat',
  HEARTBEAT_RESPONSE: 'heartbeat_response',
  
  // Error
  ERROR: 'error'
} as const;

export const MESSAGE_TYPES = {
  TEXT: 'text',
  IMAGE: 'image',
  FILE: 'file'
} as const;

export const ROOM_TYPES = {
  PUBLIC: 'public',
  PRIVATE: 'private'
} as const;

export const SOCKET_CONFIG = {
  url: SOCKET_URL,
  options: {
    transports: ['websocket', 'polling'],
    autoConnect: false,
    reconnection: true,
    reconnectionAttempts: 5,
    reconnectionDelay: 1000
  }
};

export const HEARTBEAT_INTERVAL = 30000; // 30 seconds
export const TYPING_TIMEOUT = 5000; // 5 seconds
export const MESSAGE_LIMIT = 50;
export const RECONNECTION_DELAY = 1000; 