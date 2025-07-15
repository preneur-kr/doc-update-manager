import React from 'react';

interface TypingIndicatorProps {
  isVisible: boolean;
  userName?: string;
}

export const TypingIndicator: React.FC<TypingIndicatorProps> = ({
  isVisible,
}) => {
  if (!isVisible) return null;

  return (
    <div className='flex items-start max-w-[85%] mb-4 opacity-0 animate-slide-in-left'>
      {/* 아바타 */}
      <div
        className='w-8 h-8 sm:w-9 sm:h-9 rounded-full flex items-center justify-center text-white text-sm sm:text-base mr-2 sm:mr-3 flex-shrink-0 shadow-md'
        style={{
          background: 'linear-gradient(135deg, #0538FF 0%, #5799F7 100%)',
        }}
      >
        💬
      </div>

      {/* 타이핑 버블 */}
      <div className='bg-gray-100 px-4 py-3 rounded-3xl rounded-bl-lg shadow-sm'>
        <div className='flex space-x-1'>
          <div className='w-2 h-2 bg-gray-400 rounded-full animate-typing-bounce'></div>
          <div
            className='w-2 h-2 bg-gray-400 rounded-full animate-typing-bounce'
            style={{ animationDelay: '-0.32s' }}
          ></div>
          <div
            className='w-2 h-2 bg-gray-400 rounded-full animate-typing-bounce'
            style={{ animationDelay: '-0.16s' }}
          ></div>
        </div>
      </div>
    </div>
  );
};
