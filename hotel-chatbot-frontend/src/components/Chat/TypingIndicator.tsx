import React from 'react';

interface TypingIndicatorProps {
  isVisible: boolean;
  userName?: string;
}

export const TypingIndicator: React.FC<TypingIndicatorProps> = ({ isVisible, userName = "호텔 직원" }) => {
  if (!isVisible) return null;

  return (
    <div className="flex justify-start mb-4 animate-fade-in">
      <div className="relative max-w-xs lg:max-w-md order-1">
        <div className="relative px-5 py-3 rounded-2xl shadow-lg bg-white text-gray-900 rounded-bl-md border border-gray-100">
          {/* 꼬리 */}
          <svg className="absolute left-[-8px] bottom-0" width="16" height="24" viewBox="0 0 16 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M16 24C8 24 0 16 0 8V0H16V24Z" fill="white" stroke="#e5e7eb" strokeWidth="1" />
          </svg>
          
          {/* 타이핑 애니메이션 */}
          <div className="flex items-center space-x-2">
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
            </div>
            <span className="text-sm text-gray-500">{userName}이(가) 입력 중...</span>
          </div>
        </div>
      </div>
    </div>
  );
}; 