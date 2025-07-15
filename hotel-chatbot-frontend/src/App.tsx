import { useState, useEffect } from 'react';
import { ChatWindow } from './components/Chat/ChatWindow';
import { MenuDropdown } from './components/Chat/MenuDropdown';
import { WelcomeScreen } from './components/Chat/WelcomeScreen';
import type { ChatMessage } from './types/chat';
import {
  sendChatMessage,
  checkChatApiHealthWithRetry,
  checkChatApiReady,
} from './api/chatApi';
import { useChatHistory } from './hooks/useChatHistory';
import { useToast } from './hooks/useToast';
import { ToastContainer } from './components/UI/Toast';

import './styles/globals.css';

function App() {
  const { messages, addMessage, clearHistory } = useChatHistory();
  const { toasts, removeToast, error: showError } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [apiStatus, setApiStatus] = useState<
    'checking' | 'warming_up' | 'connected' | 'disconnected'
  >('checking');
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isChatStarted, setIsChatStarted] = useState(false);

  // API 상태 확인 최적화 - 빠른 준비 상태 체크
  useEffect(() => {
    let mounted = true;
    let healthCheckInterval: number;

    const checkApiWithRetry = async () => {
      try {
        console.log('🔄 API 연결 상태 체크 시작');
        // 헬스 체크로 연결 상태 확인 (Render cold start 고려한 타임아웃)
        const readyCheck = await checkChatApiReady(5000);
        console.log('🔄 첫 번째 체크 결과:', readyCheck);

        if (mounted) {
          if (readyCheck.ready) {
            console.log('✅ 연결 성공!');
            setApiStatus('connected');
          } else {
            console.log('⚠️ 첫 번째 체크 실패, 재시도 중...');
            // 실패 시 재시도 (지수 백오프, 4회 시도, 8초 타임아웃)
            const isHealthy = await checkChatApiHealthWithRetry(4, 1000, 8000);
            console.log('🔄 재시도 결과:', isHealthy);
            setApiStatus(isHealthy ? 'connected' : 'disconnected');
          }
        }

        // 연결 성공 시 주기적 체크 시작 (30초마다)
        if (mounted && readyCheck.ready && !healthCheckInterval) {
          healthCheckInterval = window.setInterval(async () => {
            if (mounted) {
              console.log('🔄 주기적 연결 상태 체크');
              const quickCheck = await checkChatApiReady(6000);
              console.log('🔄 주기적 체크 결과:', quickCheck);
              if (mounted) {
                setApiStatus(quickCheck.ready ? 'connected' : 'disconnected');
              }
            }
          }, 30000);
        }
      } catch {
        if (mounted) {
          setApiStatus('disconnected');
        }
      }
    };

    checkApiWithRetry();

    return () => {
      mounted = false;
      if (healthCheckInterval) {
        clearInterval(healthCheckInterval);
      }
    };
  }, []);

  const handleSendMessage = async (message: string) => {
    if (!message.trim()) return;

    // API 연결 상태 확인
    if (apiStatus === 'checking') {
      showError(
        '연결 확인 중',
        '서버 연결을 확인하는 중입니다. 잠시 후 다시 시도해주세요.'
      );
      return;
    }

    if (apiStatus === 'warming_up') {
      showError(
        '서버 준비 중',
        '서버가 준비 중입니다. 잠시 후 다시 시도해주세요.'
      );
      return;
    }

    if (apiStatus === 'disconnected') {
      showError(
        '서버 연결 오류',
        '서버에 연결할 수 없습니다. 연결 상태를 확인해주세요.'
      );
      return;
    }

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      content: message,
      isUser: true,
      timestamp: new Date(),
    };

    addMessage(userMessage);
    setIsLoading(true);

    try {
      const response = await sendChatMessage({ message });
      const botMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        content: response.answer,
        isUser: false,
        timestamp: new Date(),
      };
      addMessage(botMessage);
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        content:
          error instanceof Error
            ? error.message
            : '서버와의 통신 중 오류가 발생했습니다.',
        isUser: false,
        timestamp: new Date(),
      };
      addMessage(errorMessage);
      showError('전송 실패', '메시지 전송 중 오류가 발생했습니다.');

      // 연결 오류 시 상태 재확인
      setApiStatus('checking');
      setTimeout(async () => {
        const isHealthy = await checkChatApiHealthWithRetry(3, 1500, 8000);
        setApiStatus(isHealthy ? 'connected' : 'disconnected');
      }, 1000);
    } finally {
      setIsLoading(false);
    }
  };

  const handleExitChat = () => {
    // 상담 종료 로직 - 초기 화면으로 돌아가기
    setIsChatStarted(false);
    clearHistory();
    setIsMenuOpen(false);
  };

  const handleStartChat = () => {
    setIsChatStarted(true);
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
                서정적인 호텔
              </div>
              <div className='text-sm text-gray-500 leading-tight'>
                AI가 바로 답변해 드려요
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
          <WelcomeScreen onStartChat={handleStartChat} apiStatus={apiStatus} />
        ) : (
          <ChatWindow
            messages={messages}
            onSendMessage={handleSendMessage}
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
