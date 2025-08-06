export interface ValidationResult {
  isValid: boolean;
  errors: string[];
}

export const validateMessage = (content: string): ValidationResult => {
  const errors: string[] = [];
  
  if (!content || content.trim().length === 0) {
    errors.push('Message cannot be empty');
  }
  
  if (content.length > 1000) {
    errors.push('Message is too long (max 1000 characters)');
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
};

export const validateRoomName = (name: string): ValidationResult => {
  const errors: string[] = [];
  
  if (!name || name.trim().length === 0) {
    errors.push('Room name cannot be empty');
  }
  
  if (name.length > 50) {
    errors.push('Room name is too long (max 50 characters)');
  }
  
  if (!/^[a-zA-Z0-9\s-_]+$/.test(name)) {
    errors.push('Room name contains invalid characters');
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
};

export const validateLoginForm = (username: string, password: string): ValidationResult => {
  const errors: string[] = [];
  
  if (!username || username.trim().length === 0) {
    errors.push('Username is required');
  }
  
  if (!password || password.length === 0) {
    errors.push('Password is required');
  }
  
  if (password.length < 6) {
    errors.push('Password must be at least 6 characters');
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
};

export const validateRegisterForm = (
  username: string, 
  email: string, 
  password: string, 
  confirmPassword: string
): ValidationResult => {
  const errors: string[] = [];
  
  if (!username || username.trim().length === 0) {
    errors.push('Username is required');
  } else if (username.length < 3) {
    errors.push('Username must be at least 3 characters');
  } else if (username.length > 20) {
    errors.push('Username must be less than 20 characters');
  } else if (!/^[a-zA-Z0-9_]+$/.test(username)) {
    errors.push('Username can only contain letters, numbers, and underscores');
  }
  
  if (!email || email.trim().length === 0) {
    errors.push('Email is required');
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    errors.push('Please enter a valid email address');
  }
  
  if (!password || password.length === 0) {
    errors.push('Password is required');
  } else if (password.length < 6) {
    errors.push('Password must be at least 6 characters');
  }
  
  if (password !== confirmPassword) {
    errors.push('Passwords do not match');
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
};

export const validateSearchQuery = (query: string): ValidationResult => {
  const errors: string[] = [];
  
  if (!query || query.trim().length === 0) {
    errors.push('Search query is required');
  }
  
  if (query.length < 2) {
    errors.push('Search query must be at least 2 characters');
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
};

export const validateRoomId = (roomId: string): ValidationResult => {
  const errors: string[] = [];
  
  if (!roomId || roomId.trim().length === 0) {
    errors.push('Room ID is required');
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
};

export const validateUserId = (userId: string): ValidationResult => {
  const errors: string[] = [];
  
  if (!userId || userId.trim().length === 0) {
    errors.push('User ID is required');
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
};

export const sanitizeInput = (input: string): string => {
  if (!input) return '';
  return input.trim().replace(/[<>]/g, '');
};

export const isOnline = (lastSeen: string): boolean => {
  const lastSeenDate = new Date(lastSeen);
  const now = new Date();
  const diffInMinutes = (now.getTime() - lastSeenDate.getTime()) / (1000 * 60);
  return diffInMinutes < 5; // Consider online if last seen within 5 minutes
}; 