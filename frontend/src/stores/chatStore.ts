import { create } from 'zustand';
import { ChatState, Message, ChatRoom, TypingIndicator } from '../types/chatTypes';

interface ChatStore extends ChatState {
  // Actions
  setMessages: (messages: Message[]) => void;
  addMessage: (message: Message) => void;
  updateMessage: (messageId: string, updates: Partial<Message>) => void;
  removeMessage: (messageId: string) => void;
  setCurrentRoom: (room: ChatRoom | null) => void;
  setTypingUsers: (users: TypingIndicator[]) => void;
  addTypingUser: (user: TypingIndicator) => void;
  removeTypingUser: (userId: string, roomId: string) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearError: () => void;
  clearMessages: () => void;
  clearTypingUsers: () => void;
  reset: () => void;
}

const initialState: ChatState = {
  messages: [],
  currentRoom: null,
  typingUsers: [],
  isLoading: false,
  error: null
};

export const useChatStore = create<ChatStore>((set, get) => ({
  ...initialState,

  setMessages: (messages) => set({ messages }),

  addMessage: (message) => set((state) => ({
    messages: [message, ...state.messages]
  })),

  updateMessage: (messageId, updates) => set((state) => ({
    messages: state.messages.map((msg) =>
      msg.message_id === messageId ? { ...msg, ...updates } : msg
    )
  })),

  removeMessage: (messageId) => set((state) => ({
    messages: state.messages.filter((msg) => msg.message_id !== messageId)
  })),

  setCurrentRoom: (room) => set({ currentRoom: room }),

  setTypingUsers: (users) => set({ typingUsers: users }),

  addTypingUser: (user) => set((state) => {
    const existingIndex = state.typingUsers.findIndex(
      (u) => u.user_id === user.user_id && u.room_id === user.room_id
    );

    if (existingIndex >= 0) {
      // Update existing typing user
      const updatedUsers = [...state.typingUsers];
      updatedUsers[existingIndex] = user;
      return { typingUsers: updatedUsers };
    } else {
      // Add new typing user
      return { typingUsers: [...state.typingUsers, user] };
    }
  }),

  removeTypingUser: (userId, roomId) => set((state) => ({
    typingUsers: state.typingUsers.filter(
      (user) => !(user.user_id === userId && user.room_id === roomId)
    )
  })),

  setLoading: (isLoading) => set({ isLoading }),

  setError: (error) => set({ error }),

  clearError: () => set({ error: null }),

  clearMessages: () => set({ messages: [] }),

  clearTypingUsers: () => set({ typingUsers: [] }),

  reset: () => set(initialState)
})); 