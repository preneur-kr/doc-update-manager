import { useState, useEffect } from 'react'
import { ChatWindow } from './components/Chat/ChatWindow'
import { MenuDropdown } from './components/Chat/MenuDropdown'
import { WelcomeScreen } from './components/Chat/WelcomeScreen'
import type { ChatMessage } from './types/chat'
import { sendChatMessage, checkChatApiHealthWithRetry, checkChatApiReady } from './api/chatApi'
import { useChatHistory } from './hooks/useChatHistory'
import { useToast } from './hooks/useToast'
import { ToastContainer } from './components/UI/Toast'

import './styles/globals.css'

function App() {
  const { messages, addMessage, clearHistory } = useChatHistory();
  const { toasts, removeToast, error: showError } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [apiStatus, setApiStatus] = useState<'checking' | 'warming_up' | 'connected' | 'disconnected'>('checking');
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
      } catch (error) {
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
      showError('연결 확인 중', '서버 연결을 확인하는 중입니다. 잠시 후 다시 시도해주세요.');
      return;
    }
    
    if (apiStatus === 'warming_up') {
      showError('서버 준비 중', '서버가 준비 중입니다. 잠시 후 다시 시도해주세요.');
      return;
    }
    
    if (apiStatus === 'disconnected') {
      showError('서버 연결 오류', '서버에 연결할 수 없습니다. 연결 상태를 확인해주세요.');
      return;
    }
    
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      content: message,
      isUser: true,
      timestamp: new Date()
    };
    
    addMessage(userMessage);
    setIsLoading(true);
    
    try {
      const response = await sendChatMessage({ message });
      const botMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        content: response.answer,
        isUser: false,
        timestamp: new Date()
      };
      addMessage(botMessage);
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        content: error instanceof Error ? error.message : '서버와의 통신 중 오류가 발생했습니다.',
        isUser: false,
        timestamp: new Date()
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
    <div className="min-h-screen w-full bg-gradient-to-br from-neutral-100 via-white to-primary-50 flex items-center justify-center px-2 md:px-0">
      <div className="w-full max-w-[430px] h-[98vh] flex flex-col rounded-3xl shadow-2xl overflow-hidden border border-neutral-200 bg-white/95 relative">
        {/* 상단바 */}
        <div className="flex items-center justify-between px-5 py-3 border-b border-neutral-200 bg-white/95">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center text-lg font-bold text-primary-600 shadow border border-primary-200">A</div>
            <div className="font-semibold text-lg text-neutral-900 tracking-tight">챗봇</div>
          </div>
          <div className="flex items-center space-x-2">
            <span className={`w-2 h-2 rounded-full ${apiStatus === 'connected' ? 'bg-green-400' : apiStatus === 'checking' ? 'bg-yellow-300' : 'bg-red-400'}`}></span>
          </div>
        </div>
        {/* 채팅창 */}
        <div className="flex-1 flex flex-col bg-neutral-100">
          <ChatWindow 
            messages={messages} 
            onSendMessage={handleSendMessage} 
            isLoading={isLoading} 
          />
        </div>
      </div>
    </div>
  )
}

export default App; 