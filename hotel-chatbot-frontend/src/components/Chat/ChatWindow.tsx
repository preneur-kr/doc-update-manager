import React, { useRef, useEffect, useState } from 'react';
import { MessageList } from './MessageList';
import { InputBox } from './InputBox';
import { QuickReplies } from './QuickReplies';
import type { ChatMessage } from '../../types/chat';

interface ChatWindowProps {
  messages: ChatMessage[];
  onSendMessage: (message: string) => void;
  isLoading: boolean;
  isMenuOpen?: boolean;
}

export const ChatWindow: React.FC<ChatWindowProps> = ({ messages, onSendMessage, isLoading, isMenuOpen = false }) => {
  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const messagesContainerRef = useRef<HTMLDivElement | null>(null);
  const [showQuickReplies, setShowQuickReplies] = useState(true);
  const [isUserScrolling, setIsUserScrolling] = useState(false);
  const [lastMessageCount, setLastMessageCount] = useState(0);

  // 사용자가 스크롤 중인지 감지 (더 정확한 감지)
  useEffect(() => {
    const container = messagesContainerRef.current;
    if (!container) return;

    const handleScroll = () => {
      const { scrollTop, scrollHeight, clientHeight } = container;
      const isAtBottom = scrollHeight - scrollTop - clientHeight < 20; // 20px 여유
      setIsUserScrolling(!isAtBottom);
    };

    container.addEventListener('scroll', handleScroll, { passive: true });
    return () => container.removeEventListener('scroll', handleScroll);
  }, []);

  // 새 메시지가 올 때만 자동 스크롤 (더 스마트한 로직)
  useEffect(() => {
    const isNewMessage = messages.length > lastMessageCount;
    setLastMessageCount(messages.length);

    if (isNewMessage && !isUserScrolling) {
      // 약간의 지연을 두어 DOM 업데이트 후 스크롤
      setTimeout(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    }
  }, [messages, isUserScrolling, lastMessageCount]);

  // 메시지가 3개 이상이면 빠른 답변 숨기기
  useEffect(() => {
    setShowQuickReplies(messages.length <= 2);
  }, [messages.length]);

  const handleQuickReply = (message: string) => {
    onSendMessage(message);
    setShowQuickReplies(false);
  };

  return (
    <div className={`flex flex-col h-full relative transition-colors duration-300 ${
      isMenuOpen ? 'bg-gray-100' : 'bg-gray-50'
    }`}>
      {/* 메시지 리스트 - 고정 높이로 스크롤 강제 */}
      <div 
        ref={messagesContainerRef}
        className="flex-1 px-2 sm:px-3 py-4 sm:py-6 overflow-y-scroll overscroll-contain" 
        style={{ 
          WebkitOverflowScrolling: 'touch',
          scrollBehavior: 'smooth',
          maxHeight: isMenuOpen ? 'calc(100vh - 350px)' : 'calc(100vh - 200px)', // 메뉴 열림 상태에 따라 높이 조정
          minHeight: '300px' // 최소 높이 보장
        }}
      >
        <MessageList messages={messages} isLoading={isLoading} />
        <div ref={messagesEndRef} />
      </div>
      
      {/* 빠른 답변 */}
      {showQuickReplies && !isLoading && (
        <QuickReplies onSelectReply={handleQuickReply} isVisible={showQuickReplies} />
      )}
      
      {/* 하단 입력창 - 항상 표시 */}
      <InputBox onSendMessage={onSendMessage} isLoading={isLoading} />
    </div>
  );
};
