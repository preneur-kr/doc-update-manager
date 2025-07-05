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

  return (
    <div className="bg-white border-t border-gray-200 px-3 py-3 md:px-4 md:py-4 flex items-end gap-2">
      <form onSubmit={handleSubmit} className="flex w-full items-end gap-2">
        <textarea
          ref={textareaRef}
          value={message}
          onChange={e => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="메시지를 입력하세요..."
          disabled={isLoading}
          rows={1}
          style={{ minHeight: '40px', maxHeight: '160px' }}
          maxLength={1000}
          className="flex-1 resize-none rounded-full px-4 py-2 bg-white border border-gray-300 focus:ring-2 focus:ring-blue-300 focus:border-blue-300 outline-none text-base text-gray-900 placeholder:text-gray-400 shadow-sm transition-all duration-200"
        />
        <button
          type="submit"
          disabled={isLoading || !message.trim()}
          className={`flex items-center justify-center w-11 h-11 md:w-12 md:h-12 rounded-full shadow-md transition-all duration-200
            ${isLoading || !message.trim() ? 'bg-gray-300 text-gray-500 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700 text-white'}`}
          aria-label="메시지 전송"
        >
          <PaperAirplaneIcon className="w-5 h-5 transform rotate-45" />
        </button>
      </form>
    </div>
  );
};
