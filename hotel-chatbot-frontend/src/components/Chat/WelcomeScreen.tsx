import React from 'react';

interface WelcomeScreenProps {
  onStartChat: () => void;
  apiStatus?: 'checking' | 'warming_up' | 'connected' | 'disconnected';
}

export const WelcomeScreen: React.FC<WelcomeScreenProps> = ({ onStartChat, apiStatus = 'connected' }) => {
  return (
    <div className="flex-1 flex flex-col justify-center px-4 sm:px-6 py-8 bg-gray-50">
      {/* 상단 여백을 위한 spacer */}
      <div className="flex-1"></div>
      
      <div className="text-center max-w-md mx-auto">
        {/* 채팅 아이콘 - 배경 없이 아이콘만 */}
        <div className="flex items-center justify-center mx-auto mb-2">
          <svg className="w-20 h-20 sm:w-24 sm:h-24 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
          </svg>
        </div>
        
        {/* 메인 텍스트 - 더 연한 회색 */}
        <h1 className="text-base sm:text-lg font-medium text-gray-400 mb-8">
          대화를 시작해보세요
        </h1>
      </div>
      
      {/* 하단 여백과 버튼 */}
      <div className="flex-1 flex items-end pb-8">
        <div className="w-full text-center">
          {/* 새 문의하기 버튼 - 연결 상태에 따른 조건부 렌더링 */}
          <button
            onClick={onStartChat}
            disabled={apiStatus !== 'connected'}
            className={`min-w-[200px] sm:min-w-[240px] min-h-[52px] sm:min-h-[56px] text-white px-6 sm:px-8 py-3 sm:py-4 font-medium text-base sm:text-lg flex items-center justify-center mx-auto transition-all duration-200 shadow-lg focus:outline-none focus:ring-2 focus:ring-offset-2 ${
              apiStatus === 'connected' 
                ? 'hover:scale-105 active:scale-95 hover:shadow-xl cursor-pointer' 
                : 'opacity-60 cursor-not-allowed'
            }`}
            style={{
              background: apiStatus === 'connected' 
                ? 'linear-gradient(135deg, #0538FF 0%, #5799F7 100%)'
                : 'linear-gradient(135deg, #6B7280 0%, #9CA3AF 100%)',
              borderRadius: '28px',
              border: 'none'
            }}
            onMouseEnter={(e) => {
              if (apiStatus === 'connected') {
                e.currentTarget.style.background = 'linear-gradient(135deg, #0429D6 0%, #4B8BF5 100%)';
                e.currentTarget.style.transform = 'scale(1.05)';
              }
            }}
            onMouseLeave={(e) => {
              if (apiStatus === 'connected') {
                e.currentTarget.style.background = 'linear-gradient(135deg, #0538FF 0%, #5799F7 100%)';
                e.currentTarget.style.transform = 'scale(1)';
              }
            }}
            onMouseDown={(e) => {
              if (apiStatus === 'connected') {
                e.currentTarget.style.transform = 'scale(0.95)';
              }
            }}
            onMouseUp={(e) => {
              if (apiStatus === 'connected') {
                e.currentTarget.style.transform = 'scale(1.05)';
              }
            }}
            aria-label="새 문의 시작하기"
          >
{apiStatus === 'connected' ? '새 문의하기' :
             apiStatus === 'warming_up' ? '서버 준비 중...' :
             apiStatus === 'checking' ? '연결 확인 중...' : '연결 끊김'}
            {apiStatus === 'connected' ? (
              <svg 
                className="w-5 h-5 sm:w-6 sm:h-6 ml-3 flex-shrink-0" 
                viewBox="0 0 24 24" 
                fill="none"
                style={{ transform: 'rotate(-35deg)' }}
              >
                <path 
                  d="M2 21L23 12L2 3V10L17 12L2 14V21Z" 
                  fill="currentColor"
                />
              </svg>
            ) : (
              <div className="ml-3 w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin flex-shrink-0"></div>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}; 