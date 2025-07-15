import React, { useState, useRef } from 'react';
import { linkifyText } from '../../utils/linkUtils';

interface ChatBubbleProps {
  message: string; // 원본 문자열 메시지 (UI 변경 없이 유지)
  isUser: boolean;
  timestamp: Date;
}

export const ChatBubble: React.FC<ChatBubbleProps> = ({ 
  message, 
  isUser, 
  timestamp
}) => {
  const [showCopyFeedback, setShowCopyFeedback] = useState(false);
  const longPressTimerRef = useRef<number | null>(null);



  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(message);
      setShowCopyFeedback(true);
      setTimeout(() => setShowCopyFeedback(false), 2000);
    } catch (err) {
      console.error('복사 실패:', err);
    }
  };



  // 롱프레스 감지 (모바일)
  const handleTouchStart = () => {
    longPressTimerRef.current = setTimeout(() => {
      copyToClipboard();
    }, 800);
  };

  const handleTouchEnd = () => {
    if (longPressTimerRef.current) {
      clearTimeout(longPressTimerRef.current);
    }
  };

  return (
    <div className={`flex items-start max-w-[85%] sm:max-w-[80%] mb-4 opacity-0 ${
      isUser 
        ? 'self-end animate-slide-in-right' 
        : 'self-start animate-slide-in-left'
    }`}>
      {/* 봇 아바타 - 봇 메시지일 때만 표시 */}
      {!isUser && (
        <div className="w-8 h-8 sm:w-9 sm:h-9 rounded-full flex items-center justify-center text-white text-sm sm:text-base mr-2 sm:mr-3 flex-shrink-0 shadow-md"
             style={{
               background: 'linear-gradient(135deg, #0538FF 0%, #5799F7 100%)'
             }}>
          💬
        </div>
      )}
      
      {/* 메시지 버블 */}
      <div 
        className={`relative px-4 py-3 sm:px-6 sm:py-5 min-h-[44px] sm:min-h-[48px] text-base sm:text-lg leading-6 sm:leading-7 break-words flex items-start ${
          isUser 
            ? 'text-white rounded-3xl rounded-br-lg shadow-md' 
            : 'bg-gray-200 text-gray-900 rounded-3xl rounded-bl-lg shadow-sm'
        } hover:opacity-90 transition-opacity duration-150`}
        style={isUser ? {
          background: 'linear-gradient(135deg, #0538FF 0%, #5799F7 100%)'
        } : {}}
        onDoubleClick={copyToClipboard}
        onTouchStart={handleTouchStart}
        onTouchEnd={handleTouchEnd}
        title="텍스트 선택 가능 | 더블클릭으로 전체 복사"
      >
        {/* 메시지 텍스트 - 링크 변환 및 줄바꿈 처리 */}
        <div 
          className="w-full" 
          style={{ 
            userSelect: 'text', 
            WebkitUserSelect: 'text',
            MozUserSelect: 'text',
            msUserSelect: 'text'
          }}
          onClick={(e) => {
            // 링크 클릭 시 버블 클릭 이벤트 방지
            if ((e.target as HTMLElement).tagName === 'A') {
              e.stopPropagation();
            }
          }}
        >
{(() => {
            // 🔧 강화된 디버깅과 타입 검사
            console.log('🔍 === ChatBubble 렌더링 시작 ===');
            console.log('📝 원본 message:', message);
            console.log('🔍 message 타입:', typeof message);
            console.log('📏 message 길이:', message?.length);
            console.log('👤 isUser:', isUser);
            console.log('⏰ timestamp:', timestamp);
            
            // message가 string인지 엄격하게 확인
            if (typeof message === 'string') {
              console.log('✅ message는 string 타입 - linkifyText 호출');
              
              // URL 패턴이 있는지 미리 확인
              const hasUrlPattern = /https?:\/\/[^\s<>"{}|\\^`\[\]]+|www\.[^\s<>"{}|\\^`\[\]]+|[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}/g.test(message);
              console.log('🔗 URL 패턴 존재 여부:', hasUrlPattern);
              
              if (hasUrlPattern) {
                console.log('🔗 URL 발견! linkifyText 호출 중...');
                
                try {
                  const result = linkifyText(message, { isUserMessage: isUser });
                  
                  console.log('⚛️ linkifyText 결과:', result);
                  console.log('🔍 결과 타입:', typeof result);
                  console.log('✅ React 요소인가?', React.isValidElement(result));
                  
                  // 결과가 null이나 undefined인지 확인
                  if (result === null || result === undefined) {
                    console.error('❌ linkifyText가 null/undefined를 반환!');
                    return <span style={{ color: 'red' }}>렌더링 오류</span>;
                  }
                  
                  // 문자열로 변환되었는지 확인
                  if (typeof result === 'string') {
                    console.warn('⚠️ linkifyText 결과가 string으로 변환됨:', result);
                    // 🔧 간단한 fallback: dangerouslySetInnerHTML 사용
                    const simpleLinkified = message.replace(
                      /(https?:\/\/[^\s<>"{}|\\^`\[\]]+|www\.[^\s<>"{}|\\^`\[\]]+|[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,})/g,
                      (url) => {
                        let linkUrl = url;
                        if (url.startsWith('www.')) {
                          linkUrl = 'https://' + url;
                        } else if (!url.startsWith('http://') && !url.startsWith('https://')) {
                          linkUrl = 'https://' + url;
                        }
                        return `<a href="${linkUrl}" target="_blank" rel="noopener noreferrer" style="color: ${isUser ? '#93c5fd' : '#2563eb'}; text-decoration: underline; cursor: pointer;">${url}</a>`;
                      }
                    );
                    return <span dangerouslySetInnerHTML={{ __html: simpleLinkified }} />;
                  }
                  
                  // DOM 렌더링 후 확인을 위한 타이머 (더 정확한 체크)
                  setTimeout(() => {
                    console.log('🔍 === 렌더링 후 DOM 검증 ===');
                    const allLinks = document.querySelectorAll('a');
                    const chatBubbles = document.querySelectorAll('[class*="rounded-3xl"]');
                    
                    console.log('🔗 전체 <a> 태그 개수:', allLinks.length);
                    console.log('💬 ChatBubble 개수:', chatBubbles.length);
                    
                    // 현재 메시지를 포함한 버블 찾기
                    const currentBubble = Array.from(chatBubbles).find(bubble => 
                      bubble.textContent?.includes(message.substring(0, 20))
                    );
                    
                    if (currentBubble) {
                      const linksInCurrentBubble = currentBubble.querySelectorAll('a');
                      console.log('📎 현재 버블의 <a> 태그 개수:', linksInCurrentBubble.length);
                      
                      if (hasUrlPattern && linksInCurrentBubble.length === 0) {
                        console.error('❌ URL이 있지만 <a> 태그가 생성되지 않음!');
                        console.log('📄 버블 innerHTML:', currentBubble.innerHTML);
                      }
                    } else {
                      console.warn('⚠️ 현재 메시지에 해당하는 버블을 찾을 수 없음');
                    }
                  }, 200);
                  
                  console.log('✅ linkifyText 결과 반환');
                  return result;
                  
                } catch (error) {
                  console.error('❌ linkifyText 실행 중 오류:', error);
                  // 🔧 오류 시 간단한 fallback
                  const simpleLinkified = message.replace(
                    /(https?:\/\/[^\s<>"{}|\\^`\[\]]+|www\.[^\s<>"{}|\\^`\[\]]+|[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,})/g,
                    (url) => {
                      let linkUrl = url;
                      if (url.startsWith('www.')) {
                        linkUrl = 'https://' + url;
                      } else if (!url.startsWith('http://') && !url.startsWith('https://')) {
                        linkUrl = 'https://' + url;
                      }
                      return `<a href="${linkUrl}" target="_blank" rel="noopener noreferrer" style="color: ${isUser ? '#93c5fd' : '#2563eb'}; text-decoration: underline; cursor: pointer;">${url}</a>`;
                    }
                  );
                  return <span dangerouslySetInnerHTML={{ __html: simpleLinkified }} />;
                }
              } else {
                console.log('📝 URL 없음 - 원본 텍스트 반환');
                return message;
              }
            } else {
              console.warn('⚠️ message가 string이 아님:', typeof message, message);
              return message;
            }
          })()}
        </div>
        
        {/* 복사 완료 피드백 */}
        {showCopyFeedback && (
          <div className="absolute -top-8 left-1/2 transform -translate-x-1/2 bg-black text-white text-xs px-2 py-1 rounded opacity-90 animate-pulse">
            복사됨
          </div>
        )}
      </div>
    </div>
  );
};

