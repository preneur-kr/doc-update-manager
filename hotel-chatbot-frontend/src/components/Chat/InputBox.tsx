import React, { useState, useRef, useEffect } from 'react';
import EmojiPicker, { EmojiClickData } from 'emoji-picker-react';
import { FaceSmileIcon } from '@heroicons/react/24/outline';
import { CONFIG } from '../../config/env';

interface InputBoxProps {
  onSendMessage: (message: string) => void;
  isLoading?: boolean;
}

export const InputBox: React.FC<InputBoxProps> = ({
  onSendMessage,
  isLoading = false,
}) => {
  const [message, setMessage] = useState('');
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const emojiPickerRef = useRef<HTMLDivElement>(null);

  // 자동 높이 조정 (최대 8줄)
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, CONFIG.UI.TEXTAREA_MAX_HEIGHT)}px`;
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

  const hasMessage = message.trim().length > 0;
  const isButtonEnabled = hasMessage && !isLoading;

  // 이모지 선택 핸들러
  const handleEmojiClick = (emojiData: EmojiClickData) => {
    setMessage(prev => prev + emojiData.emoji);
    setShowEmojiPicker(false);
    textareaRef.current?.focus();
  };

  // 이모지 피커 외부 클릭 감지
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        emojiPickerRef.current &&
        !emojiPickerRef.current.contains(event.target as Node)
      ) {
        setShowEmojiPicker(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // 로딩 중일 때는 입력창 자체를 숨김
  if (isLoading) {
    return null;
  }

  return (
    <div>
      {/* 입력 영역 */}
      <div className='px-2 sm:px-3 py-3 bg-white'>
        <form
          onSubmit={handleSubmit}
          className='flex items-center gap-2 sm:gap-3'
        >
          {/* 중앙 입력창 - 채널톡 스타일 */}
          <div className='flex-1 bg-gray-100 rounded-full px-3 py-2 min-h-[36px] sm:min-h-[40px] flex items-center'>
            <textarea
              ref={textareaRef}
              value={message}
              onChange={e => setMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={
                isLoading
                  ? 'AI가 답변 중입니다...'
                  : message.length > 0
                    ? '질문을 입력해 주세요...'
                    : '메시지를 입력하세요...'
              }
              rows={1}
              disabled={isLoading}
              style={{
                minHeight: '20px',
                maxHeight: '100px',
                resize: 'none',
                lineHeight: '1.4',
              }}
              maxLength={CONFIG.UI.MAX_MESSAGE_LENGTH}
              className={`flex-1 bg-transparent border-none outline-none text-sm text-black placeholder:text-gray-400 leading-tight ${
                isLoading ? 'cursor-not-allowed opacity-60' : ''
              }`}
            />
          </div>

          {/* 오른쪽 이모지 버튼 */}
          <div className='relative'>
            <button
              type='button'
              onClick={() => setShowEmojiPicker(!showEmojiPicker)}
              className='text-gray-500 hover:text-gray-700 transition-colors duration-150 p-1 rounded-full hover:bg-gray-100 flex items-center justify-center'
              title='이모지'
            >
              <FaceSmileIcon className='w-5 h-5' />
            </button>

            {/* 이모지 피커 */}
            {showEmojiPicker && (
              <div
                ref={emojiPickerRef}
                className='absolute bottom-full right-0 mb-2 z-50'
              >
                <EmojiPicker
                  onEmojiClick={handleEmojiClick}
                  width={window.innerWidth < 640 ? 280 : 300}
                  height={window.innerWidth < 640 ? 350 : 400}
                  previewConfig={{ showPreview: false }}
                  skinTonesDisabled
                />
              </div>
            )}
          </div>

          {/* 동적 전송 버튼 - 채널톡 스타일 */}
          {hasMessage && !isLoading && (
            <button
              type='submit'
              disabled={!isButtonEnabled}
              className='px-3 py-2 min-h-[36px] sm:min-h-[40px] flex items-center justify-center text-white transition-all duration-150 hover:scale-105 active:scale-95 shadow-md hover:shadow-xl'
              style={{
                background: 'linear-gradient(135deg, #0538FF 0%, #5799F7 100%)',
                borderRadius: '12px',
                border: 'none',
              }}
              onMouseEnter={e => {
                e.currentTarget.style.background =
                  'linear-gradient(135deg, #0429D6 0%, #4B8BF5 100%)';
              }}
              onMouseLeave={e => {
                e.currentTarget.style.background =
                  'linear-gradient(135deg, #0538FF 0%, #5799F7 100%)';
              }}
              title='전송'
              aria-label='전송'
            >
              <svg
                className='w-6 h-6 sm:w-7 sm:h-7'
                viewBox='0 0 24 24'
                fill='none'
                style={{ transform: 'rotate(-45deg)' }}
              >
                <path
                  d='M2 21L23 12L2 3V10L17 12L2 14V21Z'
                  fill='currentColor'
                />
              </svg>
            </button>
          )}
        </form>
      </div>
    </div>
  );
};
