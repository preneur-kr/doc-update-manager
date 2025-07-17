import { useReducer, useCallback, useEffect, useRef } from 'react';
import type { ChatMessage } from '../types/chat';
import { ChatService, type ApiStatus } from '../services/chatService';
import { CONFIG } from '../config/env';

interface ChatState {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  apiStatus: ApiStatus;
  isChatStarted: boolean;
}

type ChatAction =
  | { type: 'ADD_MESSAGE'; payload: ChatMessage }
  | { type: 'ADD_MESSAGES'; payload: ChatMessage[] }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'SET_API_STATUS'; payload: ApiStatus }
  | { type: 'SET_CHAT_STARTED'; payload: boolean }
  | { type: 'CLEAR_HISTORY' }
  | { type: 'CLEAR_ERROR' };

const chatReducer = (state: ChatState, action: ChatAction): ChatState => {
  switch (action.type) {
    case 'ADD_MESSAGE':
      return {
        ...state,
        messages: [...state.messages, action.payload],
        error: null,
      };
    case 'ADD_MESSAGES':
      return {
        ...state,
        messages: [...state.messages, ...action.payload],
        error: null,
      };
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload, isLoading: false };
    case 'SET_API_STATUS':
      return { ...state, apiStatus: action.payload };
    case 'SET_CHAT_STARTED':
      return { ...state, isChatStarted: action.payload };
    case 'CLEAR_HISTORY':
      return {
        ...state,
        messages: [{
          id: '1',
          content: CONFIG.HOTEL.WELCOME_MESSAGE,
          isUser: false,
          timestamp: new Date(),
        }],
        error: null,
      };
    case 'CLEAR_ERROR':
      return { ...state, error: null };
    default:
      return state;
  }
};

const initialState: ChatState = {
  messages: [{
    id: '1',
    content: CONFIG.HOTEL.WELCOME_MESSAGE,
    isUser: false,
    timestamp: new Date(),
  }],
  isLoading: false,
  error: null,
  apiStatus: 'checking',
  isChatStarted: false,
};

export interface UseChatOptions {
  onError?: (title: string, message?: string) => void;
  autoStart?: boolean;
}

export const useChat = (options: UseChatOptions = {}) => {
  const [state, dispatch] = useReducer(chatReducer, initialState);
  const chatServiceRef = useRef<ChatService | null>(null);
  const { onError, autoStart = true } = options;

  // 채팅 서비스 초기화
  useEffect(() => {
    if (!chatServiceRef.current) {
      chatServiceRef.current = new ChatService({
        onApiStatusChange: (status) => dispatch({ type: 'SET_API_STATUS', payload: status }),
        onError: onError || (() => {}),
      });

      if (autoStart) {
        chatServiceRef.current.initializeConnection();
      }
    }

    return () => {
      if (chatServiceRef.current) {
        chatServiceRef.current.destroy();
        chatServiceRef.current = null;
      }
    };
  }, [onError, autoStart]);

  const sendMessage = useCallback(async (content: string) => {
    if (!chatServiceRef.current || !content.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      content: content.trim(),
      isUser: true,
      timestamp: new Date(),
    };

    dispatch({ type: 'ADD_MESSAGE', payload: userMessage });
    dispatch({ type: 'SET_LOADING', payload: true });
    dispatch({ type: 'CLEAR_ERROR' });

    const result = await chatServiceRef.current.sendMessage(content, state.apiStatus);

    if (result.success && result.response) {
      const botMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        content: result.response,
        isUser: false,
        timestamp: new Date(),
      };
      dispatch({ type: 'ADD_MESSAGE', payload: botMessage });
    } else if (result.response) {
      // 실패한 경우에도 에러 메시지를 봇 메시지로 표시
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        content: result.response,
        isUser: false,
        timestamp: new Date(),
      };
      dispatch({ type: 'ADD_MESSAGE', payload: errorMessage });
    }

    dispatch({ type: 'SET_LOADING', payload: false });
  }, [state.apiStatus]);

  const addMessage = useCallback((message: ChatMessage) => {
    dispatch({ type: 'ADD_MESSAGE', payload: message });
  }, []);

  const addMessages = useCallback((messages: ChatMessage[]) => {
    dispatch({ type: 'ADD_MESSAGES', payload: messages });
  }, []);

  const clearHistory = useCallback(() => {
    dispatch({ type: 'CLEAR_HISTORY' });
  }, []);

  const clearError = useCallback(() => {
    dispatch({ type: 'CLEAR_ERROR' });
  }, []);

  const startChat = useCallback(() => {
    dispatch({ type: 'SET_CHAT_STARTED', payload: true });
  }, []);

  const exitChat = useCallback(() => {
    dispatch({ type: 'SET_CHAT_STARTED', payload: false });
    clearHistory();
  }, [clearHistory]);

  const initializeConnection = useCallback(() => {
    if (chatServiceRef.current) {
      chatServiceRef.current.initializeConnection();
    }
  }, []);

  return {
    // State
    messages: state.messages,
    isLoading: state.isLoading,
    error: state.error,
    apiStatus: state.apiStatus,
    isChatStarted: state.isChatStarted,
    
    // Actions
    sendMessage,
    addMessage,
    addMessages,
    clearHistory,
    clearError,
    startChat,
    exitChat,
    initializeConnection,
  };
};
