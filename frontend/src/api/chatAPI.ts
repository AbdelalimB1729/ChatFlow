import socketAPI from './socket';
import { SOCKET_EVENTS } from '../utils/constants';
import { Message, ChatRoom, TypingIndicator, SendMessageData, JoinRoomData, LeaveRoomData } from '../types/chatTypes';

export class ChatAPI {
  // Message operations
  sendMessage(data: SendMessageData): void {
    socketAPI.sendMessage(data.content, data.room_id, data.message_type);
  }

  markMessageRead(messageId: string): void {
    socketAPI.markMessageRead(messageId);
  }

  markMessageDelivered(messageId: string): void {
    socketAPI.markMessageDelivered(messageId);
  }

  getMessages(roomId: string, limit: number = 50, offset: number = 0): void {
    socketAPI.getMessages(roomId, limit, offset);
  }

  // Room operations
  joinRoom(data: JoinRoomData): void {
    socketAPI.joinRoom(data.room_id);
  }

  leaveRoom(data: LeaveRoomData): void {
    socketAPI.leaveRoom(data.room_id);
  }

  createRoom(name: string, roomType: string = 'public'): void {
    socketAPI.createRoom(name, roomType);
  }

  getRooms(): void {
    socketAPI.getRooms();
  }

  // Typing operations
  startTyping(roomId: string): void {
    socketAPI.startTyping(roomId);
  }

  stopTyping(roomId: string): void {
    socketAPI.stopTyping(roomId);
  }

  getTypingUsers(roomId: string): void {
    socketAPI.getTypingUsers(roomId);
  }

  // Event listeners
  onNewMessage(callback: (message: Message) => void): void {
    socketAPI.on(SOCKET_EVENTS.NEW_MESSAGE, callback);
  }

  onMessageSent(callback: (data: { message_id: string; timestamp: string }) => void): void {
    socketAPI.on(SOCKET_EVENTS.MESSAGE_SENT, callback);
  }

  onMessageRead(callback: (data: { message_id: string; user_id: string; timestamp: string }) => void): void {
    socketAPI.on(SOCKET_EVENTS.MESSAGE_READ, callback);
  }

  onMessageDelivered(callback: (data: { message_id: string; user_id: string; timestamp: string }) => void): void {
    socketAPI.on(SOCKET_EVENTS.MESSAGE_DELIVERED, callback);
  }

  onRoomMessages(callback: (data: { room_id: string; messages: Message[]; limit: number; offset: number }) => void): void {
    socketAPI.on(SOCKET_EVENTS.ROOM_MESSAGES, callback);
  }

  onJoinedRoom(callback: (data: { room_id: string; message: string }) => void): void {
    socketAPI.on(SOCKET_EVENTS.JOINED_ROOM, callback);
  }

  onLeftRoom(callback: (data: { room_id: string; message: string }) => void): void {
    socketAPI.on(SOCKET_EVENTS.LEFT_ROOM, callback);
  }

  onUserJoinedRoom(callback: (data: { user_id: string; room_id: string; username: string }) => void): void {
    socketAPI.on(SOCKET_EVENTS.USER_JOINED_ROOM, callback);
  }

  onUserLeftRoom(callback: (data: { user_id: string; room_id: string; username: string }) => void): void {
    socketAPI.on(SOCKET_EVENTS.USER_LEFT_ROOM, callback);
  }

  onUserTyping(callback: (data: { user_id: string; room_id: string; username: string; is_typing: boolean }) => void): void {
    socketAPI.on(SOCKET_EVENTS.USER_TYPING, callback);
  }

  onTypingUsers(callback: (data: { room_id: string; users: string[] }) => void): void {
    socketAPI.on(SOCKET_EVENTS.TYPING_USERS, callback);
  }

  onRoomCreated(callback: (room: ChatRoom) => void): void {
    socketAPI.on(SOCKET_EVENTS.ROOM_CREATED, callback);
  }

  onRoomCreatedConfirmation(callback: (data: { message: string; room: ChatRoom }) => void): void {
    socketAPI.on(SOCKET_EVENTS.ROOM_CREATED_CONFIRMATION, callback);
  }

  onAvailableRooms(callback: (data: { rooms: ChatRoom[] }) => void): void {
    socketAPI.on(SOCKET_EVENTS.AVAILABLE_ROOMS, callback);
  }

  onError(callback: (data: { message: string }) => void): void {
    socketAPI.on(SOCKET_EVENTS.ERROR, callback);
  }

  // Remove event listeners
  offNewMessage(callback?: Function): void {
    socketAPI.off(SOCKET_EVENTS.NEW_MESSAGE, callback);
  }

  offMessageSent(callback?: Function): void {
    socketAPI.off(SOCKET_EVENTS.MESSAGE_SENT, callback);
  }

  offMessageRead(callback?: Function): void {
    socketAPI.off(SOCKET_EVENTS.MESSAGE_READ, callback);
  }

  offMessageDelivered(callback?: Function): void {
    socketAPI.off(SOCKET_EVENTS.MESSAGE_DELIVERED, callback);
  }

  offRoomMessages(callback?: Function): void {
    socketAPI.off(SOCKET_EVENTS.ROOM_MESSAGES, callback);
  }

  offJoinedRoom(callback?: Function): void {
    socketAPI.off(SOCKET_EVENTS.JOINED_ROOM, callback);
  }

  offLeftRoom(callback?: Function): void {
    socketAPI.off(SOCKET_EVENTS.LEFT_ROOM, callback);
  }

  offUserJoinedRoom(callback?: Function): void {
    socketAPI.off(SOCKET_EVENTS.USER_JOINED_ROOM, callback);
  }

  offUserLeftRoom(callback?: Function): void {
    socketAPI.off(SOCKET_EVENTS.USER_LEFT_ROOM, callback);
  }

  offUserTyping(callback?: Function): void {
    socketAPI.off(SOCKET_EVENTS.USER_TYPING, callback);
  }

  offTypingUsers(callback?: Function): void {
    socketAPI.off(SOCKET_EVENTS.TYPING_USERS, callback);
  }

  offRoomCreated(callback?: Function): void {
    socketAPI.off(SOCKET_EVENTS.ROOM_CREATED, callback);
  }

  offRoomCreatedConfirmation(callback?: Function): void {
    socketAPI.off(SOCKET_EVENTS.ROOM_CREATED_CONFIRMATION, callback);
  }

  offAvailableRooms(callback?: Function): void {
    socketAPI.off(SOCKET_EVENTS.AVAILABLE_ROOMS, callback);
  }

  offError(callback?: Function): void {
    socketAPI.off(SOCKET_EVENTS.ERROR, callback);
  }
}

export const chatAPI = new ChatAPI();
export default chatAPI; 