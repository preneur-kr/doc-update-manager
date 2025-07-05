import { useState, useEffect } from 'react'
import { ChatWindow } from './components/Chat/ChatWindow'
import type { ChatMessage } from './types/chat'
import { sendChatMessage, checkChatApiHealth } from './api/chatApi'
import './styles/globals.css'

function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      content: '안녕하세요! 호텔 정책에 대해 궁금한 점이 있으시면 언제든 물어보세요.',
      isUser: false,
      timestamp: new Date()
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [apiStatus, setApiStatus] = useState<'checking' | 'connected' | 'disconnected'>('checking');

  useEffect(() => {
    const checkApi = async () => {
      try {
        const isHealthy = await checkChatApiHealth();
        setApiStatus(isHealthy ? 'connected' : 'disconnected');
      } catch (error) {
        setApiStatus('disconnected');
      }
    };
    checkApi();
  }, []);

  const handleSendMessage = async (message: string) => {
    if (!message.trim()) return;
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      content: message,
      isUser: true,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    try {
      const response = await sendChatMessage({ message });
      const botMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        content: response.answer,
        isUser: false,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        content: error instanceof Error ? error.message : '서버와의 통신 중 오류가 발생했습니다.',
        isUser: false,
        timestamp: new Date()
      }]);
    } finally {
      setIsLoading(false);
    }
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

export default App
