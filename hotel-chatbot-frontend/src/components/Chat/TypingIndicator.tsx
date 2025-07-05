import React from 'react';
import { ChatBubbleLeftIcon } from '@heroicons/react/24/outline';

interface TypingIndicatorProps {
  isVisible: boolean;
  userName?: string;
}

export const TypingIndicator: React.FC<TypingIndicatorProps> = ({ isVisible, userName = "AI 어시스턴트" }) => {
  if (!isVisible) return null;

  return (
    <div className="flex w-full justify-start items-end gap-3 mb-4 animate-fade-in">
      {/* 아바타 */}
      <div className="w-9 h-9 rounded-full bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center shadow-md flex-shrink-0">
        <ChatBubbleLeftIcon className="w-5 h-5 text-white" />
      </div>
      
      {/* 타이핑 버블 */}
      <div className="relative max-w-[85%] md:max-w-[70%]">
        <div className="px-4 py-3 rounded-2xl shadow-sm bg-white border border-gray-100 rounded-bl-md">
          {/* 타이핑 애니메이션 */}
          <div className="flex items-center space-x-3">
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
            </div>
            <span className="text-sm text-gray-500 font-medium">{userName}이(가) 입력 중...</span>
          </div>
        </div>
        
        {/* 타임스탬프 자리 (빈 공간) */}
        <div className="flex items-center mt-1 justify-start">
          <span className="text-xs text-transparent select-none">00:00</span>
        </div>
      </div>
    </div>
  );
}; 