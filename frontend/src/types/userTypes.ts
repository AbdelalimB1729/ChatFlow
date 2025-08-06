export interface User {
  user_id: string;
  username: string;
  email: string;
  is_online: boolean;
  last_seen: string;
  created_at?: string;
}

export interface UserProfile extends User {
  typing_in: string | null;
  socket_id: string | null;
}

export interface UserStatistics {
  user_id: string;
  username: string;
  total_users: number;
  online_users: number;
  user_created_at: string;
  last_seen: string;
  is_online: boolean;
}

export interface AuthUser {
  user_id: string;
  username: string;
  email: string;
  token: string;
}

export interface LoginData {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
}

export interface AuthState {
  user: AuthUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface UserState {
  onlineUsers: User[];
  allUsers: User[];
  currentUser: UserProfile | null;
  isLoading: boolean;
  error: string | null;
} 