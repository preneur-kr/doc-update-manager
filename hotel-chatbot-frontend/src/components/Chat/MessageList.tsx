import React from 'react';
import { ChatBubble } from './ChatBubble';
import type { ChatMessage } from '../../types/chat';

interface MessageListProps {
  messages: ChatMessage[];
}

export const MessageList: React.FC<MessageListProps> = ({ messages }) => {
  return (
    <div className="flex flex-col gap-3 px-2 md:px-4 py-6">
      {messages.map((msg, idx) => (
        <ChatBubble
          key={msg.id}
          message={msg.content}
          isUser={msg.isUser}
          timestamp={msg.timestamp}
          isFirst={idx === 0 || messages[idx-1].isUser !== msg.isUser}
        />
      ))}
    </div>
  );
};
