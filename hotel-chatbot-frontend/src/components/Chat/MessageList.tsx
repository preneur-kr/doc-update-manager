import React from 'react';
import { ChatBubble } from './ChatBubble';
import { TypingIndicator } from './TypingIndicator';
import type { ChatMessage } from '../../types/chat';

interface MessageListProps {
  messages: ChatMessage[];
  isLoading?: boolean;
}

export const MessageList: React.FC<MessageListProps> = ({ messages, isLoading = false }) => {
  return (
    <div className="flex flex-col px-2 sm:px-3 py-4">
      {messages.map((msg) => (
        <ChatBubble
          key={msg.id}
          message={msg.content}
          isUser={msg.isUser}
          timestamp={msg.timestamp}
        />
      ))}
      
      {/* 타이핑 인디케이터 */}
      <TypingIndicator isVisible={isLoading} />
    </div>
  );
};
