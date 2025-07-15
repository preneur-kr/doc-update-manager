import React from 'react';

interface HeaderProps {
  apiStatus: 'checking' | 'connected' | 'disconnected';
}

export const Header: React.FC<HeaderProps> = ({ apiStatus }) => {
  const getStatusColor = () => {
    switch (apiStatus) {
      case 'connected':
        return 'bg-green-500';
      case 'disconnected':
        return 'bg-red-500';
      default:
        return 'bg-yellow-500';
    }
  };

  const getStatusText = () => {
    switch (apiStatus) {
      case 'connected':
        return '연결됨';
      case 'disconnected':
        return '연결 안됨';
      default:
        return '확인 중...';
    }
  };

  const getStatusTextColor = () => {
    switch (apiStatus) {
      case 'connected':
        return 'text-green-600';
      case 'disconnected':
        return 'text-red-600';
      default:
        return 'text-yellow-600';
    }
  };

  return (
    <header className='bg-white/80 backdrop-blur-md shadow-lg border-b border-neutral-200 sticky top-0 z-50'>
      <div className='max-w-4xl mx-auto px-6 py-4'>
        <div className='flex items-center justify-between'>
          {/* 로고 및 브랜딩 */}
          <div className='flex items-center space-x-4'>
            {/* 호텔 로고 */}
            <div className='relative'>
              <div className='w-12 h-12 bg-gradient-to-br from-primary-600 to-primary-800 rounded-2xl shadow-lg flex items-center justify-center'>
                <span className='text-white text-xl font-bold'>🏨</span>
              </div>
              {/* 애니메이션 효과 */}
              <div className='absolute -top-1 -right-1 w-4 h-4 bg-green-500 rounded-full animate-pulse-slow'></div>
            </div>

            {/* 브랜드 정보 */}
            <div className='space-y-1'>
              <h1 className='text-2xl font-bold gradient-text'>
                호텔 정책 챗봇
              </h1>
              <p className='text-sm text-neutral-600 font-medium'>
                AI 기반 호텔 정책 안내 서비스
              </p>
            </div>
          </div>

          {/* 우측 상태 표시 */}
          <div className='flex items-center space-x-6'>
            {/* API 상태 */}
            <div className='flex items-center space-x-2 bg-white/60 backdrop-blur-sm px-4 py-2 rounded-xl border border-neutral-200'>
              <div
                className={`w-3 h-3 rounded-full ${getStatusColor()} animate-pulse-slow`}
              ></div>
              <span className={`text-sm font-medium ${getStatusTextColor()}`}>
                {getStatusText()}
              </span>
            </div>

            {/* 추가 기능 버튼들 */}
            <div className='flex items-center space-x-2'>
              <button className='p-2 text-neutral-600 hover:text-primary-600 hover:bg-primary-50 rounded-xl transition-all duration-200'>
                <svg
                  className='w-5 h-5'
                  fill='none'
                  stroke='currentColor'
                  viewBox='0 0 24 24'
                >
                  <path
                    strokeLinecap='round'
                    strokeLinejoin='round'
                    strokeWidth={2}
                    d='M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z'
                  />
                  <path
                    strokeLinecap='round'
                    strokeLinejoin='round'
                    strokeWidth={2}
                    d='M15 12a3 3 0 11-6 0 3 3 0 016 0z'
                  />
                </svg>
              </button>

              <button className='p-2 text-neutral-600 hover:text-primary-600 hover:bg-primary-50 rounded-xl transition-all duration-200'>
                <svg
                  className='w-5 h-5'
                  fill='none'
                  stroke='currentColor'
                  viewBox='0 0 24 24'
                >
                  <path
                    strokeLinecap='round'
                    strokeLinejoin='round'
                    strokeWidth={2}
                    d='M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
                  />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
