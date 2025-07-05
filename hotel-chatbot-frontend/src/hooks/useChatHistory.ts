import { useState, useEffect } from 'react';
import type { ChatMessage } from '../types/chat';

const STORAGE_KEY = 'hotel-chatbot-history';
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
            content: '안녕하세요! 호텔 정책에 대해 궁금한 점이 있으시면 언제든 물어보세요.',
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
          content: '안녕하세요! 호텔 정책에 대해 궁금한 점이 있으시면 언제든 물어보세요.',
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
        content: '안녕하세요! 호텔 정책에 대해 궁금한 점이 있으시면 언제든 물어보세요.',
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