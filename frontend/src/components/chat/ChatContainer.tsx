import React, { useEffect, useRef, useState } from 'react';
import { Box, Paper, Typography, useTheme } from '@mui/material';
import { AnimatePresence, motion } from 'framer-motion';
import AutoSizer from 'react-virtualized-auto-sizer';
import { VariableSizeList as List } from 'react-window';
import { format } from 'date-fns';
import { useTranslation } from 'react-i18next';

import { useChat } from '../../contexts/ChatContext';
import { useAuth } from '../../hooks/useAuth';
import MessageInput from './MessageInput';
import MessageList from './MessageList';
import TypingIndicator from './TypingIndicator';
import { Message } from '../../types/chatTypes';

const ChatContainer: React.FC = () => {
  const theme = useTheme();
  const { t } = useTranslation();
  const { user } = useAuth();
  const {
    activeRoom,
    messages,
    typingUsers,
    onlineUsers,
    sendMessage,
    handleTyping,
    loadMessages,
  } = useChat();

  const [isLoading, setIsLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [page, setPage] = useState(1);
  const listRef = useRef<List>(null);
  const observerRef = useRef<IntersectionObserver>();
  const lastMessageRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    if (lastMessageRef.current) {
      lastMessageRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages[activeRoom?.id || '']?.length]);

  // Load initial messages
  useEffect(() => {
    if (activeRoom) {
      setIsLoading(true);
      loadMessages(activeRoom.id)
        .then((data) => {
          setHasMore(data.hasMore);
          setPage(1);
        })
        .finally(() => setIsLoading(false));
    }
  }, [activeRoom, loadMessages]);

  // Setup infinite scroll
  useEffect(() => {
    if (!activeRoom) return;

    const options = {
      root: null,
      rootMargin: '20px',
      threshold: 1.0,
    };

    const handleObserver = (entries: IntersectionObserverEntry[]) => {
      const target = entries[0];
      if (target.isIntersecting && hasMore && !isLoading) {
        setPage((prev) => prev + 1);
        setIsLoading(true);
        loadMessages(activeRoom.id, page + 1)
          .then((data) => {
            setHasMore(data.hasMore);
          })
          .finally(() => setIsLoading(false));
      }
    };

    observerRef.current = new IntersectionObserver(handleObserver, options);

    if (lastMessageRef.current) {
      observerRef.current.observe(lastMessageRef.current);
    }

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, [activeRoom, hasMore, isLoading, loadMessages, page]);

  // Handle message submission
  const handleSendMessage = async (content: string, attachments?: File[]) => {
    if (!activeRoom || !content.trim()) return;

    try {
      await sendMessage(activeRoom.id, content, attachments);
      // Reset input and scroll to bottom handled by effects
    } catch (error) {
      console.error('Error sending message:', error);
      // Show error notification
    }
  };

  // Calculate message groups for better UI
  const getMessageGroups = (messages: Message[]) => {
    const groups: Message[][] = [];
    let currentGroup: Message[] = [];
    let lastSenderId: string | null = null;
    let lastTimestamp: Date | null = null;

    messages.forEach((message) => {
      const messageDate = new Date(message.sentAt);
      const timeDiff = lastTimestamp
        ? (messageDate.getTime() - lastTimestamp.getTime()) / 1000 / 60
        : 0;

      if (
        message.senderId !== lastSenderId ||
        timeDiff > 5 // Group break after 5 minutes
      ) {
        if (currentGroup.length > 0) {
          groups.push([...currentGroup]);
        }
        currentGroup = [message];
      } else {
        currentGroup.push(message);
      }

      lastSenderId = message.senderId;
      lastTimestamp = messageDate;
    });

    if (currentGroup.length > 0) {
      groups.push(currentGroup);
    }

    return groups;
  };

  // Render message group
  const MessageGroup: React.FC<{ messages: Message[] }> = ({ messages }) => {
    const firstMessage = messages[0];
    const isCurrentUser = firstMessage.senderId === user?.id;

    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: isCurrentUser ? 'flex-end' : 'flex-start',
          mb: 2,
        }}
      >
        <Typography
          variant="caption"
          sx={{ mb: 0.5, color: theme.palette.text.secondary }}
        >
          {firstMessage.senderName} •{' '}
          {format(new Date(firstMessage.sentAt), 'HH:mm')}
        </Typography>
        {messages.map((message, index) => (
          <motion.div
            key={message.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2 }}
          >
            <Paper
              elevation={1}
              sx={{
                p: 1.5,
                mb: 0.5,
                maxWidth: '70%',
                backgroundColor: isCurrentUser
                  ? theme.palette.primary.main
                  : theme.palette.background.paper,
                color: isCurrentUser ? 'white' : 'inherit',
                borderRadius: 2,
                ...(isCurrentUser
                  ? { borderTopRightRadius: index === 0 ? 2 : 1 }
                  : { borderTopLeftRadius: index === 0 ? 2 : 1 }),
              }}
            >
              <Typography variant="body1">{message.content}</Typography>
              {message.attachments?.map((attachment) => (
                <Box
                  key={attachment.url}
                  component="img"
                  src={attachment.url}
                  alt={attachment.name}
                  sx={{
                    maxWidth: '100%',
                    maxHeight: 200,
                    borderRadius: 1,
                    mt: 1,
                  }}
                />
              ))}
            </Paper>
          </motion.div>
        ))}
      </Box>
    );
  };

  if (!activeRoom) {
    return (
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100%',
        }}
      >
        <Typography variant="h6" color="textSecondary">
          {t('chat.selectRoom')}
        </Typography>
      </Box>
    );
  }

  const messageGroups = getMessageGroups(messages[activeRoom.id] || []);

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        bgcolor: 'background.default',
      }}
    >
      {/* Room Header */}
      <Paper
        elevation={2}
        sx={{
          p: 2,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          borderBottom: 1,
          borderColor: 'divider',
        }}
      >
        <Box>
          <Typography variant="h6">{activeRoom.name}</Typography>
          <Typography variant="caption" color="textSecondary">
            {onlineUsers.size} {t('chat.online')}
          </Typography>
        </Box>
      </Paper>

      {/* Messages Area */}
      <Box sx={{ flex: 1, overflow: 'hidden', position: 'relative' }}>
        <AutoSizer>
          {({ height, width }) => (
            <List
              ref={listRef}
              height={height}
              width={width}
              itemCount={messageGroups.length}
              itemSize={() => 100} // Dynamic size based on content
              itemData={messageGroups}
            >
              {({ index, style }) => (
                <div style={style}>
                  <MessageGroup messages={messageGroups[index]} />
                </div>
              )}
            </List>
          )}
        </AutoSizer>

        {/* Loading indicator */}
        <AnimatePresence>
          {isLoading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              style={{
                position: 'absolute',
                top: 0,
                left: '50%',
                transform: 'translateX(-50%)',
                padding: theme.spacing(1),
                backgroundColor: theme.palette.background.paper,
                borderRadius: theme.shape.borderRadius,
                boxShadow: theme.shadows[1],
              }}
            >
              <Typography variant="body2">{t('chat.loading')}</Typography>
            </motion.div>
          )}
        </AnimatePresence>
      </Box>

      {/* Typing Indicator */}
      <TypingIndicator users={typingUsers[activeRoom.id] || []} />

      {/* Message Input */}
      <MessageInput
        onSend={handleSendMessage}
        onTyping={() => handleTyping(activeRoom.id)}
      />
    </Box>
  );
};

export default ChatContainer;