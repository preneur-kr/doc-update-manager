import { useState } from 'react';
import { ChatWindow } from './components/Chat/ChatWindow';
import { MenuDropdown } from './components/Chat/MenuDropdown';
import { WelcomeScreen } from './components/Chat/WelcomeScreen';
import { useChat } from './hooks/useChat';
import { useToast } from './hooks/useToast';
import { ToastContainer } from './components/UI/Toast';
import { CONFIG } from './config/env';

import './styles/globals.css';

function App() {
  const { toasts, removeToast, error: showError } = useToast();
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  // 통합된 채팅 상태 관리
  const {
    messages,
    isLoading,
    apiStatus,
    isChatStarted,
    sendMessage,
    startChat,
    exitChat,
  } = useChat({
    onError: showError, // 토스트 에러 핸들러 연결
  });

  const handleExitChat = () => {
    // 상담 종료 로직 - 초기 화면으로 돌아가기
    exitChat();
    setIsMenuOpen(false);
  };

  return (
    <div className='min-h-screen bg-gray-50 flex flex-col overflow-hidden'>
      {/* 헤더 - 개선된 디자인 */}
      <div className='bg-white border-b border-gray-200 shadow-sm px-5 py-4'>
        <div className='flex items-center justify-between'>
          <div className='flex items-center gap-3'>
            <div
              className='w-10 h-10 rounded-full flex items-center justify-center text-white text-lg shadow-sm'
              style={{
                background: 'linear-gradient(135deg, #0538FF 0%, #5799F7 100%)',
              }}
            >
              💬
            </div>
            <div className='flex flex-col'>
              <div className='text-lg font-bold text-black leading-tight'>
                {CONFIG.HOTEL.NAME}
              </div>
              <div className='text-sm text-gray-500 leading-tight'>
                {CONFIG.HOTEL.SUBTITLE}
              </div>
            </div>
          </div>

          <div className='flex items-center'>
            <MenuDropdown
              onExitChat={handleExitChat}
              onMenuStateChange={setIsMenuOpen}
            />
          </div>
        </div>
      </div>

      {/* 연결 상태 표시 (개선된 버전) */}
      {apiStatus !== 'connected' && (
        <div
          className={`px-4 py-2 border-b ${
            apiStatus === 'warming_up'
              ? 'bg-blue-50 border-blue-200'
              : apiStatus === 'checking'
                ? 'bg-yellow-50 border-yellow-200'
                : 'bg-red-50 border-red-200'
          }`}
        >
          <div className='flex items-center justify-center space-x-2'>
            <span
              className={`w-2 h-2 rounded-full ${
                apiStatus === 'warming_up'
                  ? 'bg-blue-400 animate-pulse'
                  : apiStatus === 'checking'
                    ? 'bg-yellow-400 animate-pulse'
                    : 'bg-red-400'
              }`}
            ></span>
            <span className='text-xs text-gray-600'>
              {apiStatus === 'warming_up'
                ? '서버 워밍업 중...'
                : apiStatus === 'checking'
                  ? '연결 확인 중...'
                  : '연결 끊김'}
            </span>
          </div>
        </div>
      )}

      {/* 메인 콘텐츠 */}
      <div className='flex-1 flex flex-col bg-gray-50'>
        {!isChatStarted ? (
          <WelcomeScreen onStartChat={startChat} apiStatus={apiStatus} />
        ) : (
          <ChatWindow
            messages={messages}
            onSendMessage={sendMessage}
            isLoading={isLoading}
            isMenuOpen={isMenuOpen}
          />
        )}
      </div>

      {/* 토스트 알림 */}
      <ToastContainer toasts={toasts} onClose={removeToast} position='top' />
    </div>
  );
}

export default App;
