import { useState, useEffect } from 'react'
import { ChatWindow } from './components/Chat/ChatWindow'
import type { ChatMessage } from './types/chat'
import { sendChatMessage, checkChatApiHealth } from './api/chatApi'
import { useChatHistory } from './hooks/useChatHistory'
import { useToast } from './hooks/useToast'
import { ToastContainer } from './components/UI/Toast'
import { TrashIcon } from '@heroicons/react/24/outline'
import './styles/globals.css'

function App() {
  const { messages, addMessage, clearHistory } = useChatHistory();
  const { toasts, removeToast, success, error: showError, info } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [apiStatus, setApiStatus] = useState<'checking' | 'connected' | 'disconnected'>('checking');

  // API 상태 확인 최적화
  useEffect(() => {
    let mounted = true;
    
    const checkApi = async () => {
      try {
        const isHealthy = await checkChatApiHealth();
        if (mounted) {
          setApiStatus(isHealthy ? 'connected' : 'disconnected');
        }
      } catch (error) {
        if (mounted) {
          setApiStatus('disconnected');
        }
      }
    };
    
    checkApi();
    
    return () => {
      mounted = false;
    };
  }, []);

  const handleSendMessage = async (message: string) => {
    if (!message.trim()) return;
    
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
      success('답변 완료', '메시지가 성공적으로 전송되었습니다.', 2000);
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        content: error instanceof Error ? error.message : '서버와의 통신 중 오류가 발생했습니다.',
        isUser: false,
        timestamp: new Date()
      };
      addMessage(errorMessage);
      showError('전송 실패', '메시지 전송 중 오류가 발생했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearHistory = () => {
    if (window.confirm('대화 기록을 모두 삭제하시겠습니까?')) {
      clearHistory();
      info('기록 삭제', '대화 기록이 모두 삭제되었습니다.', 3000);
    }
  };

  return (
    <div className="min-h-screen-mobile w-full bg-gradient-to-br from-neutral-100 via-white to-blue-50 flex items-center justify-center px-2 md:px-0 safe-area-all">
      <div className="w-full max-w-[430px] h-[98vh] h-[98dvh] flex flex-col rounded-3xl shadow-2xl overflow-hidden border border-neutral-200 bg-white/95 backdrop-blur-sm relative touch-manipulation">
        {/* 상단바 - 모바일 최적화 */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-neutral-200 bg-white/95 backdrop-blur-sm">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center text-lg font-bold text-white shadow-md">
              🏨
            </div>
            <div className="font-semibold text-lg text-neutral-900 tracking-tight">호텔 챗봇</div>
          </div>
          
          <div className="flex items-center space-x-1">
            {/* 대화 기록 삭제 버튼 - 모바일 터치 최적화 */}
            <button
              onClick={handleClearHistory}
              className="mobile-button-secondary touch-feedback touch-highlight-none"
              title="대화 기록 삭제"
              aria-label="대화 기록 삭제"
            >
              <TrashIcon className="w-5 h-5 text-gray-500" />
            </button>
          </div>
        </div>
        
        {/* 연결 상태 표시 - 모바일 최적화 */}
        <div className="px-4 py-2 bg-gray-50 border-b border-gray-100">
          <div className="flex items-center justify-center space-x-2">
            <span className={`w-2 h-2 rounded-full ${
              apiStatus === 'connected' ? 'bg-green-400' : 
              apiStatus === 'checking' ? 'bg-yellow-300' : 'bg-red-400'
            }`}></span>
            <span className="text-xs text-gray-500">
              {apiStatus === 'connected' ? '연결됨' : 
               apiStatus === 'checking' ? '확인 중' : '연결 끊김'}
            </span>
          </div>
        </div>
        
        {/* 채팅창 */}
        <div className="flex-1 flex flex-col bg-gray-50">
          <ChatWindow 
            messages={messages} 
            onSendMessage={handleSendMessage} 
            isLoading={isLoading} 
          />
        </div>
      </div>
      
      {/* 토스트 알림 */}
      <ToastContainer
        toasts={toasts}
        onClose={removeToast}
        position="top"
      />
    </div>
  )
}

export default App
