import { useState, useEffect } from 'react';
import type { ChatMessage } from '../types/chat';
import { CONFIG } from '../config/env';

const { CHAT_HISTORY_KEY: STORAGE_KEY, MAX_MESSAGES } = CONFIG.STORAGE;

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
          const messagesWithDates = parsed.map((msg: Omit<ChatMessage, 'timestamp'> & { timestamp: string }) => ({
            ...msg,
            timestamp: new Date(msg.timestamp),
          }));
          setMessages(messagesWithDates);
        } else {
          // 기본 웰컴 메시지
          const welcomeMessage: ChatMessage = {
            id: '1',
            content: CONFIG.HOTEL.WELCOME_MESSAGE,
            isUser: false,
            timestamp: new Date(),
          };
          setMessages([welcomeMessage]);
        }
      } catch (error) {
        console.error('Failed to load chat history:', error);
        // 기본 웰컴 메시지
        const welcomeMessage: ChatMessage = {
          id: '1',
          content: CONFIG.HOTEL.WELCOME_MESSAGE,
          isUser: false,
          timestamp: new Date(),
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
        content: CONFIG.HOTEL.WELCOME_MESSAGE,
        isUser: false,
        timestamp: new Date(),
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
    setMessages,
  };
};
