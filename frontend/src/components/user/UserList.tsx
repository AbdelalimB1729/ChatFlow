import React from 'react';
import { User } from '../../types/userTypes';
import { formatUsername, formatRelativeTime } from '../../utils/formatters';

interface UserListProps {
  users: User[];
}

const UserList: React.FC<UserListProps> = ({ users }) => {
  if (users.length === 0) {
    return (
      <div className="text-center py-4">
        <p className="text-sm text-gray-500">No users found</p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {users.map((user) => (
        <div
          key={user.user_id}
          className="flex items-center space-x-3 p-2 rounded-lg hover:bg-gray-50 transition-colors cursor-pointer"
        >
          {/* Avatar */}
          <div className="relative">
            <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
              <span className="text-white text-sm font-medium">
                {user.username.charAt(0).toUpperCase()}
              </span>
            </div>
            {/* Online Status Indicator */}
            <div className={`absolute -bottom-1 -right-1 w-3 h-3 rounded-full border-2 border-white ${
              user.is_online ? 'bg-green-500' : 'bg-gray-400'
            }`}></div>
          </div>
          
          {/* User Info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium text-gray-800 truncate">
                {formatUsername(user.username)}
              </p>
              <span className="text-xs text-gray-500">
                {user.is_online ? 'Online' : formatRelativeTime(user.last_seen)}
              </span>
            </div>
            <p className="text-xs text-gray-500 truncate">
              {user.email}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
};

export default UserList; 