#!/bin/bash

# 호텔 챗봇 프론트엔드 디렉토리 구조 생성 스크립트

echo "🏗️  호텔 챗봇 프론트엔드 디렉토리 구조를 생성합니다..."

# 기본 디렉토리 생성
mkdir -p src/components/Chat
mkdir -p src/components/UI
mkdir -p src/components/Layout
mkdir -p src/hooks
mkdir -p src/api
mkdir -p src/types
mkdir -p src/utils
mkdir -p src/styles

echo "✅ 디렉토리 구조 생성 완료!"

# 기본 파일 생성
echo "📝 기본 파일들을 생성합니다..."

# src/api/chatApi.ts
cat > src/api/chatApi.ts << 'EOF'
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface ChatMessage {
  id: string;
  content: string;
  isUser: boolean;
  timestamp: Date;
}

export interface ChatResponse {
  answer: string;
  is_fallback: boolean;
}

export const sendMessage = async (message: string): Promise<ChatResponse> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ question: message }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('API 호출 실패:', error);
    throw error;
  }
};
EOF

# src/types/chat.ts
cat > src/types/chat.ts << 'EOF'
export interface ChatMessage {
  id: string;
  content: string;
  isUser: boolean;
  timestamp: Date;
}

export interface ChatResponse {
  answer: string;
  is_fallback: boolean;
}
EOF

# src/hooks/useChat.ts
cat > src/hooks/useChat.ts << 'EOF'
import { useReducer, useCallback } from 'react';
import { sendMessage, ChatMessage } from '../api/chatApi';

interface ChatState {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
}

type ChatAction =
  | { type: 'ADD_MESSAGE'; payload: ChatMessage }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'CLEAR_ERROR' };

const chatReducer = (state: ChatState, action: ChatAction): ChatState => {
  switch (action.type) {
    case 'ADD_MESSAGE':
      return {
        ...state,
        messages: [...state.messages, action.payload],
        error: null,
      };
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload, isLoading: false };
    case 'CLEAR_ERROR':
      return { ...state, error: null };
    default:
      return state;
  }
};

export const useChat = () => {
  const [state, dispatch] = useReducer(chatReducer, {
    messages: [],
    isLoading: false,
    error: null,
  });

  const sendMessageHandler = useCallback(async (content: string) => {
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      content,
      isUser: true,
      timestamp: new Date(),
    };

    dispatch({ type: 'ADD_MESSAGE', payload: userMessage });
    dispatch({ type: 'SET_LOADING', payload: true });
    dispatch({ type: 'CLEAR_ERROR' });

    try {
      const response = await sendMessage(content);
      
      const botMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        content: response.answer,
        isUser: false,
        timestamp: new Date(),
      };

      dispatch({ type: 'ADD_MESSAGE', payload: botMessage });
    } catch (error) {
      dispatch({ 
        type: 'SET_ERROR', 
        payload: '메시지 전송에 실패했습니다. 다시 시도해주세요.' 
      });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  }, []);

  return {
    messages: state.messages,
    isLoading: state.isLoading,
    error: state.error,
    sendMessage: sendMessageHandler,
    clearError: () => dispatch({ type: 'CLEAR_ERROR' }),
  };
};
EOF

# src/components/Chat/InputBox.tsx
cat > src/components/Chat/InputBox.tsx << 'EOF'
import { useState } from 'react';

interface InputBoxProps {
  onSendMessage: (message: string) => void;
  isLoading?: boolean;
}

export const InputBox = ({ onSendMessage, isLoading = false }: InputBoxProps) => {
  const [message, setMessage] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !isLoading) {
      onSendMessage(message.trim());
      setMessage('');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2 p-4 border-t">
      <input
        type="text"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="메시지를 입력하세요..."
        disabled={isLoading}
        className="flex-1 px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      <button
        type="submit"
        disabled={isLoading || !message.trim()}
        className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
      >
        {isLoading ? '전송 중...' : '전송'}
      </button>
    </form>
  );
};
EOF

# src/components/Chat/ChatBubble.tsx
cat > src/components/Chat/ChatBubble.tsx << 'EOF'
interface ChatBubbleProps {
  message: string;
  isUser: boolean;
  timestamp: Date;
}

export const ChatBubble = ({ message, isUser, timestamp }: ChatBubbleProps) => (
  <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
    <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
      isUser 
        ? 'bg-blue-500 text-white' 
        : 'bg-gray-200 text-gray-800'
    }`}>
      <p className="text-sm">{message}</p>
      <p className={`text-xs mt-1 ${
        isUser ? 'text-blue-100' : 'text-gray-500'
      }`}>
        {timestamp.toLocaleTimeString()}
      </p>
    </div>
  </div>
);
EOF

# src/components/Chat/MessageList.tsx
cat > src/components/Chat/MessageList.tsx << 'EOF'
import { ChatBubble } from './ChatBubble';
import { ChatMessage } from '../../types/chat';

interface MessageListProps {
  messages: ChatMessage[];
}

export const MessageList = ({ messages }: MessageListProps) => (
  <div className="flex-1 overflow-y-auto p-4">
    {messages.map((message) => (
      <ChatBubble
        key={message.id}
        message={message.content}
        isUser={message.isUser}
        timestamp={message.timestamp}
      />
    ))}
  </div>
);
EOF

# src/components/Chat/ChatWindow.tsx
cat > src/components/Chat/ChatWindow.tsx << 'EOF'
import { MessageList } from './MessageList';
import { InputBox } from './InputBox';
import { ChatMessage } from '../../types/chat';

interface ChatWindowProps {
  messages: ChatMessage[];
  onSendMessage: (message: string) => void;
  isLoading: boolean;
}

export const ChatWindow = ({ messages, onSendMessage, isLoading }: ChatWindowProps) => (
  <div className="max-w-2xl mx-auto h-screen flex flex-col">
    <MessageList messages={messages} />
    <InputBox onSendMessage={onSendMessage} isLoading={isLoading} />
  </div>
);
EOF

# src/styles/globals.css
cat > src/styles/globals.css << 'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
EOF

# .env.local
cat > .env.local << 'EOF'
VITE_API_URL=http://localhost:8000
EOF

# .env.production
cat > .env.production << 'EOF'
VITE_API_URL=https://hotel-bot-api.onrender.com
EOF

echo "✅ 기본 파일 생성 완료!"

echo "
🎉 프론트엔드 구조 생성이 완료되었습니다!

다음 단계:
1. npm install
2. npm install -D tailwindcss postcss autoprefixer
3. npx tailwindcss init -p
4. src/main.tsx에서 './styles/globals.css' import 추가
5. npm run dev

Happy coding! 🚀
" 