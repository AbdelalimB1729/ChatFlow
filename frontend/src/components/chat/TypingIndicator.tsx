import React from 'react';
import { TypingIndicator as TypingIndicatorType } from '../../types/chatTypes';

interface TypingIndicatorProps {
  users: TypingIndicatorType[];
}

const TypingIndicator: React.FC<TypingIndicatorProps> = ({ users }) => {
  if (users.length === 0) return null;

  const typingUsers = users.filter(user => user.is_typing);
  
  if (typingUsers.length === 0) return null;

  return (
    <div className="px-4 py-2 bg-gray-50 border-t border-gray-200">
      <div className="flex items-center space-x-2">
        <div className="flex space-x-1">
          <div className="typing-dot w-2 h-2 bg-gray-400 rounded-full"></div>
          <div className="typing-dot w-2 h-2 bg-gray-400 rounded-full"></div>
          <div className="typing-dot w-2 h-2 bg-gray-400 rounded-full"></div>
        </div>
        <span className="text-sm text-gray-600">
          {typingUsers.length === 1 
            ? `${typingUsers[0].username} is typing...`
            : `${typingUsers.map(u => u.username).join(', ')} are typing...`
          }
        </span>
      </div>
    </div>
  );
};

export default TypingIndicator; 