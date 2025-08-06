import { create } from 'zustand';
import { UserState, User, UserProfile, UserStatistics } from '../types/userTypes';

interface UserStore extends UserState {
  // Actions
  setOnlineUsers: (users: User[]) => void;
  setAllUsers: (users: User[]) => void;
  setCurrentUser: (user: UserProfile | null) => void;
  addOnlineUser: (user: User) => void;
  removeOnlineUser: (userId: string) => void;
  updateUser: (userId: string, updates: Partial<User>) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearError: () => void;
  clearOnlineUsers: () => void;
  clearAllUsers: () => void;
  reset: () => void;
}

const initialState: UserState = {
  onlineUsers: [],
  allUsers: [],
  currentUser: null,
  isLoading: false,
  error: null
};

export const useUserStore = create<UserStore>((set, get) => ({
  ...initialState,

  setOnlineUsers: (users) => set({ onlineUsers: users }),

  setAllUsers: (users) => set({ allUsers: users }),

  setCurrentUser: (user) => set({ currentUser: user }),

  addOnlineUser: (user) => set((state) => {
    const existingIndex = state.onlineUsers.findIndex((u) => u.user_id === user.user_id);
    
    if (existingIndex >= 0) {
      // Update existing user
      const updatedUsers = [...state.onlineUsers];
      updatedUsers[existingIndex] = user;
      return { onlineUsers: updatedUsers };
    } else {
      // Add new user
      return { onlineUsers: [...state.onlineUsers, user] };
    }
  }),

  removeOnlineUser: (userId) => set((state) => ({
    onlineUsers: state.onlineUsers.filter((user) => user.user_id !== userId)
  })),

  updateUser: (userId, updates) => set((state) => ({
    onlineUsers: state.onlineUsers.map((user) =>
      user.user_id === userId ? { ...user, ...updates } : user
    ),
    allUsers: state.allUsers.map((user) =>
      user.user_id === userId ? { ...user, ...updates } : user
    ),
    currentUser: state.currentUser?.user_id === userId 
      ? { ...state.currentUser, ...updates } 
      : state.currentUser
  })),

  setLoading: (isLoading) => set({ isLoading }),

  setError: (error) => set({ error }),

  clearError: () => set({ error: null }),

  clearOnlineUsers: () => set({ onlineUsers: [] }),

  clearAllUsers: () => set({ allUsers: [] }),

  reset: () => set(initialState)
})); 