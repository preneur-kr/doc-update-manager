import React, { useState, useRef, useEffect } from 'react';

interface MenuDropdownProps {
  onExitChat?: () => void;
  onMenuStateChange?: (isOpen: boolean) => void;
}

export const MenuDropdown: React.FC<MenuDropdownProps> = ({
  onExitChat,
  onMenuStateChange,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // 메뉴 상태 변경 시 상위 컴포넌트에 알림
  useEffect(() => {
    onMenuStateChange?.(isOpen);
  }, [isOpen, onMenuStateChange]);

  // 외부 클릭 시 드롭다운 닫기
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleExitChat = () => {
    if (window.confirm('정말로 상담을 종료하시겠습니까?')) {
      onExitChat?.();
      setIsOpen(false);
    }
  };

  return (
    <>
      <div className='relative'>
        {/* 메뉴 버튼 */}
        <button
          onClick={() => setIsOpen(!isOpen)}
          className='text-lg text-gray-600 hover:text-gray-800 p-2 rounded-full hover:bg-gray-100 transition-colors duration-150'
          title='메뉴'
          aria-label='메뉴'
        >
          ⋯
        </button>
      </div>

      {/* 메뉴 모달 */}
      {isOpen && (
        <>
          {/* 디밍 오버레이 - 반투명 */}
          <div
            className='fixed inset-0 z-50'
            style={{ backgroundColor: 'rgba(0, 0, 0, 0.3)' }}
            onClick={() => setIsOpen(false)}
          />

          {/* 하단 슬라이드업 메뉴 */}
          <div
            ref={dropdownRef}
            id='menu-panel'
            role='dialog'
            aria-modal='true'
            aria-labelledby='menu-title'
            className='fixed bottom-0 left-0 right-0 bg-white rounded-t-2xl shadow-2xl z-50'
            style={{
              animation: 'slideUp 0.3s ease-out forwards',
            }}
            onKeyDown={e => {
              if (e.key === 'Tab') {
                e.preventDefault();
                setIsOpen(false);
              }
            }}
          >
            <div className='px-4 py-3'>
              {/* 상단 핸들 바 */}
              <div className='w-8 h-1 bg-gray-300 rounded-full mx-auto mb-3'></div>

              {/* 헤더 영역 */}
              <div className='flex items-center justify-between mb-2'>
                <h2
                  id='menu-title'
                  className='text-base sm:text-lg font-medium text-gray-700 px-1'
                >
                  더보기
                </h2>
                <button
                  onClick={() => setIsOpen(false)}
                  className='w-8 h-8 sm:w-9 sm:h-9 text-gray-400 hover:text-gray-600 transition-colors duration-150 flex items-center justify-center rounded-full hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2'
                  aria-label='닫기'
                >
                  <svg
                    className='w-5 h-5 sm:w-6 sm:h-6'
                    fill='none'
                    stroke='currentColor'
                    viewBox='0 0 24 24'
                  >
                    <path
                      strokeLinecap='round'
                      strokeLinejoin='round'
                      strokeWidth={2}
                      d='M6 18L18 6M6 6l12 12'
                    />
                  </svg>
                </button>
              </div>

              {/* 메뉴 아이템 */}
              <div>
                <button
                  onClick={handleExitChat}
                  className='w-full text-left px-2 py-2 min-h-[40px] text-base sm:text-lg text-red-600 hover:bg-red-50 active:bg-red-100 transition-colors duration-150 flex items-center rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2'
                >
                  <svg
                    className='w-4 h-4 sm:w-5 sm:h-5 mr-2 text-red-500 flex-shrink-0'
                    fill='none'
                    stroke='currentColor'
                    viewBox='0 0 24 24'
                  >
                    <path
                      strokeLinecap='round'
                      strokeLinejoin='round'
                      strokeWidth={2}
                      d='M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1'
                    />
                  </svg>
                  상담 나가기
                </button>
              </div>
            </div>
          </div>
        </>
      )}
    </>
  );
};
