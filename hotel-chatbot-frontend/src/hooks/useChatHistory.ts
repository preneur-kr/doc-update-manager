import { useState, useEffect } from 'react';
import type { ChatMessage } from '../types/chat';

const STORAGE_KEY = 'hotel-chatbot-history-v2';
const MAX_MESSAGES = 50; // 최대 저장할 메시지 수

export const useChatHistory = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  // 초기 메시지 로드
  useEffect(() => {
    const loadHistory = () => {
      try {
        const stored = localStorage.getItem(STORAGE_KEY);
        if (stored) {
          const parsed = JSON.parse(stored);
          // 날짜 객체로 변환
          const messagesWithDates = parsed.map((msg: any) => ({
            ...msg,
            timestamp: new Date(msg.timestamp)
          }));
          setMessages(messagesWithDates);
        } else {
          // 기본 웰컴 메시지
          const welcomeMessage: ChatMessage = {
            id: '1',
            content: '🏨 서정적인 호텔 고객센터 💬\n\n안녕하세요, 고객님! 😊\n\n투숙하시는 동안 불편한 점이나 궁금한 점이 있으신가요? 필요한 서비스나 문의사항이 있으시면 언제든 말씀해주세요.\n\n🚀 자주 문의하시는 내용이라면?\n아래 버튼을 눌러 바로 확인해보세요!',
            isUser: false,
            timestamp: new Date()
          };
          setMessages([welcomeMessage]);
        }
      } catch (error) {
        console.error('Failed to load chat history:', error);
        // 기본 웰컴 메시지
        const welcomeMessage: ChatMessage = {
          id: '1',
          content: '🏨 서정적인 호텔 고객센터 💬\n\n안녕하세요, 고객님! 😊\n\n투숙하시는 동안 불편한 점이나 궁금한 점이 있으신가요? 필요한 서비스나 문의사항이 있으시면 언제든 말씀해주세요.\n\n🚀 자주 문의하시는 내용이라면?\n아래 버튼을 눌러 바로 확인해보세요!',
          isUser: false,
          timestamp: new Date()
        };
        setMessages([welcomeMessage]);
      }
    };

    loadHistory();
  }, []);

  // 메시지 변경 시 저장
  useEffect(() => {
    if (messages.length > 0) {
      try {
        // 최대 메시지 수 제한
        const messagesToSave = messages.slice(-MAX_MESSAGES);
        localStorage.setItem(STORAGE_KEY, JSON.stringify(messagesToSave));
      } catch (error) {
        console.error('Failed to save chat history:', error);
      }
    }
  }, [messages]);

  const addMessage = (message: ChatMessage) => {
    setMessages(prev => [...prev, message]);
  };

  const addMessages = (newMessages: ChatMessage[]) => {
    setMessages(prev => [...prev, ...newMessages]);
  };

  const clearHistory = () => {
    try {
      localStorage.removeItem(STORAGE_KEY);
      const welcomeMessage: ChatMessage = {
        id: '1',
        content: '🏨 서정적인 호텔 고객센터 💬\n\n안녕하세요, 고객님! 😊\n\n투숙하시는 동안 불편한 점이나 궁금한 점이 있으신가요? 필요한 서비스나 문의사항이 있으시면 언제든 말씀해주세요.\n\n🚀 자주 문의하시는 내용이라면?\n아래 버튼을 눌러 바로 확인해보세요!',
        isUser: false,
        timestamp: new Date()
      };
      setMessages([welcomeMessage]);
    } catch (error) {
      console.error('Failed to clear chat history:', error);
    }
  };

  return {
    messages,
    addMessage,
    addMessages,
    clearHistory,
    setMessages
  };
}; 