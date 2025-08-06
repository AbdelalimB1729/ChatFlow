import { io, Socket } from 'socket.io-client';
import { SOCKET_CONFIG, SOCKET_EVENTS, HEARTBEAT_INTERVAL } from '../utils/constants';
import { ConnectionState, SocketResponse } from '../types/socketTypes';

class SocketAPI {
  private socket: Socket | null = null;
  private chatSocket: Socket | null = null;
  private connectionState: ConnectionState = {
    isConnected: false,
    isConnecting: false,
    error: null
  };
  private eventListeners: Map<string, Function[]> = new Map();
  private heartbeatInterval: NodeJS.Timeout | null = null;

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.socket?.connected) {
        resolve();
        return;
      }

      this.connectionState.isConnecting = true;
      this.connectionState.error = null;

      this.socket = io(SOCKET_CONFIG.url, SOCKET_CONFIG.options);

      this.socket.on(SOCKET_EVENTS.CONNECT, () => {
        this.connectionState.isConnected = true;
        this.connectionState.isConnecting = false;
        this.startHeartbeat();
        this.emit('connected', {});
        resolve();
      });

      this.socket.on(SOCKET_EVENTS.DISCONNECT, () => {
        this.connectionState.isConnected = false;
        this.connectionState.isConnecting = false;
        this.stopHeartbeat();
        this.emit('disconnected', {});
      });

      this.socket.on(SOCKET_EVENTS.ERROR, (data) => {
        this.connectionState.error = data.message;
        this.emit('error', data);
        reject(new Error(data.message));
      });

      this.socket.on('connect_error', (error) => {
        this.connectionState.error = error.message;
        this.connectionState.isConnecting = false;
        this.emit('error', { message: error.message });
        reject(error);
      });
    });
  }

  connectToChat(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.chatSocket?.connected) {
        resolve();
        return;
      }

      this.chatSocket = io(`${SOCKET_CONFIG.url}/chat`, SOCKET_CONFIG.options);

      this.chatSocket.on(SOCKET_EVENTS.CONNECT, () => {
        this.emit('chat_connected', {});
        resolve();
      });

      this.chatSocket.on(SOCKET_EVENTS.DISCONNECT, () => {
        this.emit('chat_disconnected', {});
      });

      this.chatSocket.on(SOCKET_EVENTS.ERROR, (data) => {
        this.emit('error', data);
        reject(new Error(data.message));
      });
    });
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
    if (this.chatSocket) {
      this.chatSocket.disconnect();
      this.chatSocket = null;
    }
    this.stopHeartbeat();
    this.connectionState.isConnected = false;
    this.connectionState.isConnecting = false;
  }

  emit(event: string, data: any): void {
    if (this.socket?.connected) {
      this.socket.emit(event, data);
    }
  }

  emitToChat(event: string, data: any): void {
    if (this.chatSocket?.connected) {
      this.chatSocket.emit(event, data);
    }
  }

  on(event: string, callback: Function): void {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, []);
    }
    this.eventListeners.get(event)!.push(callback);

    if (this.socket) {
      this.socket.on(event, callback);
    }
    if (this.chatSocket) {
      this.chatSocket.on(event, callback);
    }
  }

  off(event: string, callback?: Function): void {
    if (callback) {
      const listeners = this.eventListeners.get(event) || [];
      const index = listeners.indexOf(callback);
      if (index > -1) {
        listeners.splice(index, 1);
      }
    } else {
      this.eventListeners.delete(event);
    }

    if (this.socket) {
      this.socket.off(event, callback);
    }
    if (this.chatSocket) {
      this.chatSocket.off(event, callback);
    }
  }

  getConnectionState(): ConnectionState {
    return { ...this.connectionState };
  }

  isConnected(): boolean {
    return this.connectionState.isConnected;
  }

  isConnecting(): boolean {
    return this.connectionState.isConnecting;
  }

  private startHeartbeat(): void {
    this.stopHeartbeat();
    this.heartbeatInterval = setInterval(() => {
      if (this.socket?.connected) {
        this.emit(SOCKET_EVENTS.HEARTBEAT, {});
      }
    }, HEARTBEAT_INTERVAL);
  }

  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  // Authentication methods
  authenticate(token: string): void {
    this.emit(SOCKET_EVENTS.AUTHENTICATE, { token });
  }

  register(username: string, email: string, password: string): void {
    this.emit(SOCKET_EVENTS.REGISTER, { username, email, password });
  }

  login(username: string, password: string): void {
    this.emit(SOCKET_EVENTS.LOGIN, { username, password });
  }

  logout(): void {
    this.emit(SOCKET_EVENTS.LOGOUT, {});
  }

  // Chat methods
  joinRoom(roomId: string): void {
    this.emitToChat(SOCKET_EVENTS.JOIN_ROOM, { room_id: roomId });
  }

  leaveRoom(roomId: string): void {
    this.emitToChat(SOCKET_EVENTS.LEAVE_ROOM, { room_id: roomId });
  }

  sendMessage(content: string, roomId: string, messageType: string = 'text'): void {
    this.emitToChat(SOCKET_EVENTS.SEND_MESSAGE, {
      content,
      room_id: roomId,
      message_type: messageType
    });
  }

  markMessageRead(messageId: string): void {
    this.emitToChat(SOCKET_EVENTS.MARK_READ, { message_id: messageId });
  }

  markMessageDelivered(messageId: string): void {
    this.emitToChat(SOCKET_EVENTS.MARK_DELIVERED, { message_id: messageId });
  }

  getMessages(roomId: string, limit: number = 50, offset: number = 0): void {
    this.emitToChat(SOCKET_EVENTS.GET_MESSAGES, {
      room_id: roomId,
      limit,
      offset
    });
  }

  startTyping(roomId: string): void {
    this.emitToChat(SOCKET_EVENTS.TYPING_START, { room_id: roomId });
  }

  stopTyping(roomId: string): void {
    this.emitToChat(SOCKET_EVENTS.TYPING_STOP, { room_id: roomId });
  }

  getTypingUsers(roomId: string): void {
    this.emitToChat(SOCKET_EVENTS.GET_TYPING_USERS, { room_id: roomId });
  }

  // User methods
  getOnlineUsers(): void {
    this.emitToChat(SOCKET_EVENTS.GET_ONLINE_USERS, {});
  }

  getAllUsers(): void {
    this.emitToChat(SOCKET_EVENTS.GET_ALL_USERS, {});
  }

  getUserProfile(userId: string): void {
    this.emitToChat(SOCKET_EVENTS.GET_USER_PROFILE, { target_user_id: userId });
  }

  searchUsers(query: string): void {
    this.emitToChat(SOCKET_EVENTS.SEARCH_USERS, { query });
  }

  getUserStatistics(): void {
    this.emitToChat(SOCKET_EVENTS.GET_USER_STATISTICS, {});
  }

  // Room methods
  createRoom(name: string, roomType: string = 'public'): void {
    this.emitToChat(SOCKET_EVENTS.CREATE_ROOM, {
      room_name: name,
      room_type: roomType
    });
  }

  getRooms(): void {
    this.emitToChat(SOCKET_EVENTS.GET_ROOMS, {});
  }

  // Presence methods
  updatePresence(): void {
    this.emitToChat(SOCKET_EVENTS.UPDATE_PRESENCE, {});
  }

  setTypingStatus(roomId: string, isTyping: boolean): void {
    this.emitToChat(SOCKET_EVENTS.SET_TYPING_STATUS, {
      room_id: roomId,
      is_typing: isTyping
    });
  }
}

export const socketAPI = new SocketAPI();
export default socketAPI; 