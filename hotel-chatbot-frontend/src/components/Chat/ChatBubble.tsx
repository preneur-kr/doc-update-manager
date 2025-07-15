import React, { useState, useRef } from 'react';
import { linkifyText } from '../../utils/linkUtils';
import { debugLog } from '../../utils/debugUtils';

interface ChatBubbleProps {
  message: string; // 원본 문자열 메시지 (UI 변경 없이 유지)
  isUser: boolean;
  timestamp: Date;
}

// 🔧 안전한 링크 변환 함수 (보안 개선)
const createSecureLinkifiedContent = (text: string, isUserMessage: boolean): React.ReactNode => {
  const urlRegex = /(https?:\/\/[^\s<>"{}|\\^`[\]]+|www\.[^\s<>"{}|\\^`[\]]+|[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,})/g;
  
  const parts: React.ReactNode[] = [];
  let match;
  let matchCount = 0;

  // 줄바꿈 처리를 위해 먼저 라인별로 분할
  const lines = text.split('\n');
  
  lines.forEach((line, lineIndex) => {
    if (lineIndex > 0) {
      parts.push(<br key={`br-${lineIndex}`} />);
    }

    let lineLastIndex = 0;
    urlRegex.lastIndex = 0; // 정규식 상태 초기화

    while ((match = urlRegex.exec(line)) !== null && matchCount < 10) {
      matchCount++;
      const matchStart = match.index;
      const url = match[0];

      // URL 앞의 텍스트 추가
      if (matchStart > lineLastIndex) {
        const beforeText = line.substring(lineLastIndex, matchStart);
        parts.push(beforeText);
      }

      // 🔒 보안: URL 정규화 및 검증
      let linkUrl = url;
      if (url.startsWith('www.')) {
        linkUrl = 'https://' + url;
      } else if (!url.startsWith('http://') && !url.startsWith('https://')) {
        // 도메인 패턴 검증
        if (/^[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}/.test(url)) {
          linkUrl = 'https://' + url;
        }
      }

      // 🔒 보안: 악성 URL 패턴 검사
      const isSafeUrl = /^https?:\/\/[a-zA-Z0-9][a-zA-Z0-9.-]*[a-zA-Z0-9]\.[a-zA-Z]{2,}(\/[^\s<>"'`]*)?$/.test(linkUrl);
      
      if (isSafeUrl) {
        // 안전한 링크 컴포넌트 생성
        const linkElement = (
          <a
            key={`link-${lineIndex}-${matchCount}`}
            href={linkUrl}
            target="_blank"
            rel="noopener noreferrer"
            className={
              isUserMessage
                ? 'text-blue-200 hover:text-blue-100 underline font-medium'
                : 'text-blue-600 hover:text-blue-800 underline font-medium'
            }
            style={{
              cursor: 'pointer',
              pointerEvents: 'auto',
              display: 'inline',
            }}
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              
              try {
                window.open(linkUrl, '_blank', 'noopener,noreferrer');
              } catch (error) {
                debugLog.error('링크 열기 실패:', error);
                // fallback: 현재 페이지에서 열기
                window.location.href = linkUrl;
              }
            }}
          >
            {url}
          </a>
        );
        parts.push(linkElement);
      } else {
        // 안전하지 않은 URL은 일반 텍스트로 표시
        debugLog.warn('안전하지 않은 URL 감지:', url);
        parts.push(url);
      }

      lineLastIndex = urlRegex.lastIndex;
    }

    // 라인의 남은 텍스트 추가
    if (lineLastIndex < line.length) {
      const remainingText = line.substring(lineLastIndex);
      parts.push(remainingText);
    }
  });

  return parts.length === 0 ? text : (
    <span style={{ display: 'contents' }}>
      {parts}
    </span>
  );
};

export const ChatBubble: React.FC<ChatBubbleProps> = ({
  message,
  isUser,
}) => {
  const [showCopyFeedback, setShowCopyFeedback] = useState(false);
  const longPressTimerRef = useRef<number | null>(null);

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(message);
      setShowCopyFeedback(true);
      setTimeout(() => setShowCopyFeedback(false), 2000);
    } catch (err) {
      debugLog.error('복사 실패:', err);
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
    <div
      className={`flex items-start max-w-[85%] sm:max-w-[80%] mb-4 opacity-0 ${
        isUser
          ? 'self-end animate-slide-in-right'
          : 'self-start animate-slide-in-left'
      }`}
    >
      {/* 봇 아바타 - 봇 메시지일 때만 표시 */}
      {!isUser && (
        <div
          className='w-8 h-8 sm:w-9 sm:h-9 rounded-full flex items-center justify-center text-white text-sm sm:text-base mr-2 sm:mr-3 flex-shrink-0 shadow-md'
          style={{
            background: 'linear-gradient(135deg, #0538FF 0%, #5799F7 100%)',
          }}
        >
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
        style={
          isUser
            ? {
                background: 'linear-gradient(135deg, #0538FF 0%, #5799F7 100%)',
              }
            : {}
        }
        onDoubleClick={copyToClipboard}
        onTouchStart={handleTouchStart}
        onTouchEnd={handleTouchEnd}
        title='텍스트 선택 가능 | 더블클릭으로 전체 복사'
      >
        {/* 메시지 텍스트 - 링크 변환 및 줄바꿈 처리 */}
        <div
          className='w-full'
          style={{
            userSelect: 'text',
            WebkitUserSelect: 'text',
            MozUserSelect: 'text',
            msUserSelect: 'text',
          }}
          onClick={e => {
            // 링크 클릭 시 버블 클릭 이벤트 방지
            if ((e.target as HTMLElement).tagName === 'A') {
              e.stopPropagation();
            }
          }}
        >
          {(() => {
            // 🔒 보안 개선: dangerouslySetInnerHTML 완전 제거
            debugLog.log('🔍 === ChatBubble 렌더링 시작 (보안 개선) ===');
            debugLog.log('📝 원본 message:', message);
            debugLog.log('🔍 message 타입:', typeof message);
            debugLog.log('👤 isUser:', isUser);

            // message가 string인지 확인
            if (typeof message === 'string') {
              // URL 패턴이 있는지 확인
              const hasUrlPattern = /(https?:\/\/[^\s<>"{}|\\^`[\]]+|www\.[^\s<>"{}|\\^`[\]]+|[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,})/g.test(message);
              
              if (hasUrlPattern) {
                debugLog.log('🔗 URL 발견! 안전한 링크 변환 중...');
                
                try {
                  // 1차: linkifyText 함수 시도
                  const result = linkifyText(message, { isUserMessage: isUser });
                  
                  // React 요소가 제대로 반환되었는지 확인
                  if (React.isValidElement(result) || Array.isArray(result)) {
                    debugLog.log('✅ linkifyText 성공, React 요소 반환');
                    return result;
                  }
                  
                  // 문자열이 반환된 경우 보안 함수 사용
                  debugLog.log('⚠️ linkifyText가 문자열 반환, 보안 함수로 대체');
                  return createSecureLinkifiedContent(message, isUser);
                  
                } catch (error) {
                  debugLog.error('❌ linkifyText 실행 중 오류:', error);
                  // 🔒 오류 시에도 보안 함수 사용
                  return createSecureLinkifiedContent(message, isUser);
                }
              } else {
                debugLog.log('📝 URL 없음 - 원본 텍스트 반환');
                return message;
              }
            } else {
              debugLog.warn('⚠️ message가 string이 아님:', typeof message, message);
              return message;
            }
          })()}
        </div>

        {/* 복사 완료 피드백 */}
        {showCopyFeedback && (
          <div className='absolute -top-8 left-1/2 transform -translate-x-1/2 bg-black text-white text-xs px-2 py-1 rounded opacity-90 animate-pulse'>
            복사됨
          </div>
        )}
      </div>
    </div>
  );
};
