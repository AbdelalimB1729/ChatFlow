import React from 'react';
import { UserProfile as UserProfileType } from '../../types/userTypes';
import { formatUsername, formatRelativeTime } from '../../utils/formatters';

interface UserProfileProps {
  user: UserProfileType;
}

const UserProfile: React.FC<UserProfileProps> = ({ user }) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center space-x-4 mb-6">
        {/* Avatar */}
        <div className="relative">
          <div className="w-16 h-16 bg-blue-500 rounded-full flex items-center justify-center">
            <span className="text-white text-xl font-semibold">
              {user.username.charAt(0).toUpperCase()}
            </span>
          </div>
          {/* Online Status */}
          <div className={`absolute -bottom-1 -right-1 w-4 h-4 rounded-full border-2 border-white ${
            user.is_online ? 'bg-green-500' : 'bg-gray-400'
          }`}></div>
        </div>
        
        {/* User Info */}
        <div className="flex-1">
          <h2 className="text-xl font-semibold text-gray-800">
            {formatUsername(user.username)}
          </h2>
          <p className="text-gray-600">{user.email}</p>
          <p className={`text-sm font-medium ${
            user.is_online ? 'text-green-600' : 'text-gray-500'
          }`}>
            {user.is_online ? 'Online' : `Last seen ${formatRelativeTime(user.last_seen)}`}
          </p>
        </div>
      </div>
      
      {/* User Details */}
      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-xs text-gray-500 uppercase tracking-wide">User ID</label>
            <p className="text-sm font-medium text-gray-800">{user.user_id}</p>
          </div>
          <div>
            <label className="text-xs text-gray-500 uppercase tracking-wide">Status</label>
            <p className={`text-sm font-medium ${
              user.is_online ? 'text-green-600' : 'text-gray-500'
            }`}>
              {user.is_online ? 'Online' : 'Offline'}
            </p>
          </div>
        </div>
        
        <div>
          <label className="text-xs text-gray-500 uppercase tracking-wide">Last Seen</label>
          <p className="text-sm font-medium text-gray-800">
            {formatRelativeTime(user.last_seen)}
          </p>
        </div>
        
        {user.created_at && (
          <div>
            <label className="text-xs text-gray-500 uppercase tracking-wide">Member Since</label>
            <p className="text-sm font-medium text-gray-800">
              {new Date(user.created_at).toLocaleDateString()}
            </p>
          </div>
        )}
        
        {user.typing_in && (
          <div>
            <label className="text-xs text-gray-500 uppercase tracking-wide">Currently Typing In</label>
            <p className="text-sm font-medium text-blue-600">{user.typing_in}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default UserProfile; 