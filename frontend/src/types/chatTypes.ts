export interface Message {
  message_id: string;
  sender_id: string;
  content: string;
  room_id: string;
  message_type: 'text' | 'image' | 'file';
  timestamp: string;
  sender_username: string;
  read_by: string[];
  delivered_to: string[];
}

export interface ChatRoom {
  room_id: string;
  name: string;
  room_type: 'public' | 'private';
  created_at: string;
  last_activity: string;
  member_count: number;
}

export interface TypingIndicator {
  user_id: string;
  room_id: string;
  username: string;
  is_typing: boolean;
}

export interface MessageReceipt {
  message_id: string;
  user_id: string;
  timestamp: string;
}

export interface ChatState {
  messages: Message[];
  currentRoom: ChatRoom | null;
  typingUsers: TypingIndicator[];
  isLoading: boolean;
  error: string | null;
}

export interface SendMessageData {
  content: string;
  room_id: string;
  message_type?: 'text' | 'image' | 'file';
}

export interface JoinRoomData {
  room_id: string;
}

export interface LeaveRoomData {
  room_id: string;
}

export interface TypingData {
  room_id: string;
  is_typing: boolean;
} 