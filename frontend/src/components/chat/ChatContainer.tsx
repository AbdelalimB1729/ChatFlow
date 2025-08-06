import React, { useState, useEffect } from 'react';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import TypingIndicator from './TypingIndicator';
import { useChat } from '../../hooks/useChat';
import { useAuth } from '../../hooks/useAuth';
import { ChatRoom } from '../../types/chatTypes';

const ChatContainer: React.FC = () => {
  const { 
    messages, 
    currentRoom, 
    typingUsers, 
    isLoading, 
    error,
    sendMessage,
    joinRoom,
    leaveRoom,
    getMessages,
    startTyping,
    stopTyping,
    clearError
  } = useChat();
  
  const { user } = useAuth();
  const [selectedRoom, setSelectedRoom] = useState<ChatRoom | null>(null);
  const [messageText, setMessageText] = useState('');

  // Demo room for testing
  const demoRoom: ChatRoom = {
    room_id: 'demo-room-1',
    name: 'General',
    room_type: 'public',
    created_at: '2024-01-01T00:00:00Z',
    last_activity: '2024-01-01T00:00:00Z',
    member_count: 5
  };

  useEffect(() => {
    if (!selectedRoom) {
      setSelectedRoom(demoRoom);
    }
  }, [selectedRoom]);

  useEffect(() => {
    if (selectedRoom) {
      joinRoom(selectedRoom.room_id);
      getMessages(selectedRoom.room_id);
    }
  }, [selectedRoom, joinRoom, getMessages]);

  const handleSendMessage = (content: string) => {
    if (!selectedRoom || !content.trim()) return;
    
    sendMessage(content, selectedRoom.room_id);
    setMessageText('');
  };

  const handleTyping = (isTyping: boolean) => {
    if (!selectedRoom) return;
    
    if (isTyping) {
      startTyping(selectedRoom.room_id);
    } else {
      stopTyping(selectedRoom.room_id);
    }
  };

  const handleRoomChange = (room: ChatRoom) => {
    if (selectedRoom) {
      leaveRoom(selectedRoom.room_id);
    }
    setSelectedRoom(room);
  };

  if (error) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="text-red-500 mb-4">
            <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Error</h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={clearError}
            className="btn btn-primary"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="spinner w-8 h-8 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading chat...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Chat Header */}
      <div className="border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-800">
              {selectedRoom?.name || 'Select a room'}
            </h2>
            <p className="text-sm text-gray-500">
              {selectedRoom?.member_count || 0} members
            </p>
          </div>
          
          <div className="flex items-center space-x-2">
            <div className="text-sm text-gray-500">
              {typingUsers.length > 0 && (
                <span className="text-blue-600">
                  {typingUsers.map(u => u.username).join(', ')} typing...
                </span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-hidden">
        <MessageList 
          messages={messages}
          currentUserId={user?.user_id}
          onMessageRead={(messageId) => {
            // Handle message read
          }}
        />
      </div>

      {/* Typing Indicator */}
      {typingUsers.length > 0 && (
        <TypingIndicator users={typingUsers} />
      )}

      {/* Message Input */}
      <div className="border-t border-gray-200 p-4">
        <MessageInput
          value={messageText}
          onChange={setMessageText}
          onSend={handleSendMessage}
          onTyping={handleTyping}
          disabled={!selectedRoom}
          placeholder={selectedRoom ? `Message in ${selectedRoom.name}...` : 'Select a room to start chatting'}
        />
      </div>
    </div>
  );
};

export default ChatContainer; 