import React, { useState, useRef, useEffect } from 'react';
import { PaperAirplaneIcon } from '@heroicons/react/24/solid';

interface InputBoxProps {
  onSendMessage: (message: string) => void;
  isLoading?: boolean;
}

export const InputBox: React.FC<InputBoxProps> = ({ onSendMessage, isLoading = false }) => {
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // 자동 높이 조정 (최대 8줄)
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 160)}px`;
    }
  }, [message]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !isLoading) {
      onSendMessage(message.trim());
      setMessage('');
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const isButtonEnabled = message.trim() && !isLoading;

  return (
    <div className="bg-white/95 backdrop-blur-sm border-t border-gray-200/50 px-4 py-4">
      <form onSubmit={handleSubmit} className="flex w-full items-start gap-3">
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={e => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="메시지를 입력하세요..."
            disabled={isLoading}
            rows={1}
            style={{ 
              minHeight: '48px', 
              maxHeight: '160px',
              paddingTop: '12px',
              paddingBottom: '12px'
            }}
            maxLength={1000}
            className="w-full resize-none rounded-3xl px-5 
                     bg-gray-50 
                     border border-gray-200
                     focus:ring-2 focus:ring-blue-500/20 
                     focus:border-blue-400 
                     focus:bg-white
                     outline-none text-base leading-6
                     text-gray-900 
                     placeholder:text-gray-500
                     shadow-sm transition-all duration-200 ease-in-out
                     disabled:bg-gray-100 
                     disabled:text-gray-400 
                     disabled:cursor-not-allowed
                     touch-manipulation"
          />
          {/* 문자 수 표시 */}
          {message.length > 800 && (
            <div className="absolute -top-6 right-2 text-xs text-gray-400">
              {message.length}/1000
            </div>
          )}
        </div>
        
        <button
          type="submit"
          disabled={!isButtonEnabled}
          style={{ marginTop: '0px' }}
          className={`flex items-center justify-center w-12 h-12 rounded-full shadow-lg transition-all duration-200 ease-in-out transform flex-shrink-0 touch-manipulation
            ${isButtonEnabled 
              ? 'bg-blue-600 hover:bg-blue-700 hover:shadow-xl hover:scale-105 active:scale-95 text-white' 
              : 'bg-gray-300 text-gray-500 cursor-not-allowed shadow-sm'
            }
            ${isLoading ? 'animate-pulse' : ''}
          `}
          aria-label="메시지 전송"
        >
          {isLoading ? (
            <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
          ) : (
            <PaperAirplaneIcon className="w-5 h-5 transform -rotate-45" />
          )}
        </button>
      </form>
    </div>
  );
};
