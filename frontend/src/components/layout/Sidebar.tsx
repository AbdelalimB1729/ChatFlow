import React, { useState, useEffect } from 'react';
import UserList from '../user/UserList';
import { useChat } from '../../hooks/useChat';
import { useAuth } from '../../hooks/useAuth';
import { AuthUser } from '../../types/userTypes';

interface SidebarProps {
  user: AuthUser | null;
  onLogout: () => void;
  isConnected: boolean;
  socketError: string | null;
}

const Sidebar: React.FC<SidebarProps> = ({ user, onLogout, isConnected, socketError }) => {
  const { onlineUsers, allUsers, getOnlineUsers, getAllUsers } = useChat();
  const [activeTab, setActiveTab] = useState<'users' | 'rooms' | 'profile'>('users');

  useEffect(() => {
    if (isConnected) {
      getOnlineUsers();
      getAllUsers();
    }
  }, [isConnected, getOnlineUsers, getAllUsers]);

  return (
    <div className="bg-white border-r border-gray-200 flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center">
            <span className="text-white font-semibold text-lg">
              {user?.username?.charAt(0).toUpperCase()}
            </span>
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-gray-800">{user?.username}</h3>
            <p className="text-sm text-gray-500">{user?.email}</p>
          </div>
        </div>
        
        {/* Connection Status */}
        <div className="mt-3 flex items-center space-x-2">
          <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
          <span className="text-xs text-gray-500">
            {isConnected ? 'Online' : 'Offline'}
          </span>
        </div>
        
        {socketError && (
          <div className="mt-2 p-2 bg-red-100 border border-red-300 rounded text-xs text-red-700">
            {socketError}
          </div>
        )}
      </div>

      {/* Navigation Tabs */}
      <div className="flex border-b border-gray-200">
        <button
          onClick={() => setActiveTab('users')}
          className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
            activeTab === 'users'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Users ({onlineUsers.length})
        </button>
        <button
          onClick={() => setActiveTab('rooms')}
          className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
            activeTab === 'rooms'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Rooms
        </button>
        <button
          onClick={() => setActiveTab('profile')}
          className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
            activeTab === 'profile'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Profile
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto">
        {activeTab === 'users' && (
          <div className="p-4">
            <h4 className="text-sm font-medium text-gray-700 mb-3">Online Users</h4>
            <UserList users={onlineUsers} />
            
            <h4 className="text-sm font-medium text-gray-700 mb-3 mt-6">All Users</h4>
            <UserList users={allUsers} />
          </div>
        )}
        
        {activeTab === 'rooms' && (
          <div className="p-4">
            <div className="mb-4">
              <h4 className="text-sm font-medium text-gray-700 mb-2">Create New Room</h4>
              <div className="space-y-2">
                <input
                  type="text"
                  placeholder="Room name"
                  className="input text-sm"
                />
                <select className="input text-sm">
                  <option value="public">Public</option>
                  <option value="private">Private</option>
                </select>
                <button className="btn btn-primary w-full text-sm">
                  Create Room
                </button>
              </div>
            </div>
            
            <h4 className="text-sm font-medium text-gray-700 mb-3">Available Rooms</h4>
            <div className="space-y-2">
              <div className="p-3 bg-gray-50 rounded-lg">
                <h5 className="font-medium text-gray-800">General</h5>
                <p className="text-xs text-gray-500">5 members</p>
              </div>
              <div className="p-3 bg-gray-50 rounded-lg">
                <h5 className="font-medium text-gray-800">Random</h5>
                <p className="text-xs text-gray-500">3 members</p>
              </div>
            </div>
          </div>
        )}
        
        {activeTab === 'profile' && (
          <div className="p-4">
            <h4 className="text-sm font-medium text-gray-700 mb-3">User Profile</h4>
            <div className="space-y-3">
              <div>
                <label className="text-xs text-gray-500">Username</label>
                <p className="text-sm font-medium text-gray-800">{user?.username}</p>
              </div>
              <div>
                <label className="text-xs text-gray-500">Email</label>
                <p className="text-sm font-medium text-gray-800">{user?.email}</p>
              </div>
              <div>
                <label className="text-xs text-gray-500">User ID</label>
                <p className="text-sm font-medium text-gray-800">{user?.user_id}</p>
              </div>
              <div>
                <label className="text-xs text-gray-500">Status</label>
                <p className="text-sm font-medium text-green-600">Online</p>
              </div>
            </div>
            
            <div className="mt-6">
              <button
                onClick={onLogout}
                className="btn btn-danger w-full text-sm"
              >
                Logout
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Sidebar; 