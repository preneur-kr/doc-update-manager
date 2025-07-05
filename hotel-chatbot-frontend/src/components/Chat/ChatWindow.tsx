import React, { useRef, useEffect } from 'react';
import { MessageList } from './MessageList';
import { InputBox } from './InputBox';
import type { ChatMessage } from '../../types/chat';

interface ChatWindowProps {
  messages: ChatMessage[];
  onSendMessage: (message: string) => void;
  isLoading: boolean;
}

export const ChatWindow: React.FC<ChatWindowProps> = ({ messages, onSendMessage, isLoading }) => {
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex flex-col h-full relative bg-dark-800">
      {/* 메시지 리스트 */}
      <div className="flex-1 px-3 py-4 overflow-y-auto scrollbar-thin scrollbar-thumb-dark-700 scrollbar-track-dark-900">
    <MessageList messages={messages} />
        <div ref={messagesEndRef} />
      </div>
      {/* 하단 입력창 */}
      <div className="px-3 pb-4 pt-2 bg-gradient-to-t from-dark-800 via-dark-800/90 to-transparent sticky bottom-0 z-10">
    <InputBox onSendMessage={onSendMessage} isLoading={isLoading} />
      </div>
  </div>
);
};
