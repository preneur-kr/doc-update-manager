import React from 'react';

interface LinkifyOptions {
  isUserMessage?: boolean;
}

/**
 * 텍스트에서 URL을 감지하고 클릭 가능한 링크로 변환합니다.
 * 단순화된 접근 방식으로 구현 (Fragment 문제 해결)
 */
export const linkifyText = (text: string, options: LinkifyOptions = {}): React.ReactNode => {
  const { isUserMessage = false } = options;
  
  if (!text || typeof text !== 'string') {
    return text;
  }

  // 링크 스타일 클래스
  const linkClass = isUserMessage
    ? 'text-blue-200 hover:text-blue-100 underline font-medium'
    : 'text-blue-600 hover:text-blue-800 underline font-medium';

  // 🔧 줄바꿈 처리: 먼저 줄 단위로 분할
  const lines = text.split('\n');
  const processedLines: React.ReactNode[] = [];

  lines.forEach((line, lineIndex) => {
    if (lineIndex > 0) {
      processedLines.push(React.createElement('br', { key: `br-${lineIndex}` }));
    }

    // 각 줄에서 URL 처리
    const urlRegex = /(https?:\/\/[^\s<>"{}|\\^`\[\]]+|www\.[^\s<>"{}|\\^`\[\]]+|[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,})/g;
    const parts: React.ReactNode[] = [];
    let lastIndex = 0;
    let match;
    let matchCount = 0;

    console.log('🔗 줄 처리:', { lineIndex, line, hasMatch: urlRegex.test(line) });
    
    // 정규식 다시 초기화
    urlRegex.lastIndex = 0;

    while ((match = urlRegex.exec(line)) !== null) {
      matchCount++;
      
      if (matchCount > 10) {
        console.warn('🚨 linkifyText: 무한루프 방지');
        break;
      }

      const matchStart = match.index;
      const matchEnd = urlRegex.lastIndex;
      let url = match[0];

      // 🔧 URL 정규화: www나 도메인만 있는 경우 https 추가
      let linkUrl = url;
      if (url.startsWith('www.')) {
        linkUrl = 'https://' + url;
      } else if (!url.startsWith('http://') && !url.startsWith('https://') && /^[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}/.test(url)) {
        linkUrl = 'https://' + url;
      }

      console.log(`🔗 URL 발견 ${matchCount}:`, { originalUrl: url, linkUrl, start: matchStart, end: matchEnd });

      // URL 앞의 텍스트 추가
      if (matchStart > lastIndex) {
        const beforeText = line.substring(lastIndex, matchStart);
        parts.push(beforeText);
      }

      // 🔧 링크 클릭 핸들러
      const handleLinkClick = (e: React.MouseEvent) => {
        e.preventDefault();
        e.stopPropagation();
        
        console.log('🔗 링크 클릭:', linkUrl);
        
        try {
          window.open(linkUrl, '_blank', 'noopener,noreferrer');
        } catch (error) {
          console.error('🔗 링크 열기 실패:', error);
          window.location.href = linkUrl;
        }
      };

      // 🔧 링크 요소 생성 (React.createElement 사용)
      const linkElement = React.createElement('a', {
        key: `link-${lineIndex}-${matchCount}`,
        href: linkUrl,
        onClick: handleLinkClick,
        className: linkClass,
        style: {
          cursor: 'pointer',
          pointerEvents: 'auto',
          display: 'inline',
          color: isUserMessage ? '#93c5fd' : '#2563eb',
          textDecoration: 'underline'
        },
        target: '_blank',
        rel: 'noopener noreferrer'
      }, url); // 표시는 원본 URL로

      parts.push(linkElement);
      lastIndex = matchEnd;
    }

    // 남은 텍스트 추가
    if (lastIndex < line.length) {
      const remainingText = line.substring(lastIndex);
      parts.push(remainingText);
    }

    // 이 줄의 모든 parts를 processedLines에 추가
    if (parts.length === 0) {
      processedLines.push(line || '');
    } else {
      processedLines.push(...parts);
    }
  });

  // 🔧 최종 결과 반환
  if (processedLines.length === 0) {
    return text;
  }

  if (processedLines.length === 1) {
    return processedLines[0];
  }

  console.log('🔗 linkifyText 완료:', { 
    totalParts: processedLines.length, 
    hasLinks: processedLines.some(part => React.isValidElement(part) && part.type === 'a')
  });
  
  return React.createElement('span', {
    key: 'linkified-content',
    style: { display: 'contents' }
  }, ...processedLines);
};

/**
 * 텍스트에 링크가 포함되어 있는지 확인
 */
export const hasLinks = (text: string): boolean => {
  if (!text || typeof text !== 'string') return false;
  const urlRegex = /https?:\/\/[^\s<>"{}|\\^`\[\]]+/g;
  return urlRegex.test(text);
};

/**
 * URL이 유효한지 검증
 */
export const isValidUrl = (url: string): boolean => {
  try {
    const urlObj = new URL(url);
    return urlObj.protocol === 'http:' || urlObj.protocol === 'https:';
  } catch {
    return false;
  }
};

/**
 * 개발용 테스트 함수
 */
export const testLinkify = (testText?: string) => {
  const defaultText = testText || `테스트 메시지입니다. 
링크를 확인해보세요: https://www.google.com
그리고 이것도: http://www.naver.com
마지막으로: https://github.com/test/repo`;

  console.log('🧪 linkifyText 테스트 시작');
  console.log('📝 입력 텍스트:', defaultText);
  
  const result = linkifyText(defaultText);
  console.log('✅ 결과:', result);
  console.log('🔍 결과 타입:', typeof result);
  console.log('⚛️ React 요소인가?', React.isValidElement(result));
  
  return {
    input: defaultText,
    output: result,
    hasLinks: hasLinks(defaultText)
  };
};

// 전역 함수로 등록 (개발용)
if (typeof window !== 'undefined') {
  (window as any).testLinkify = testLinkify;
  console.log('🔗 testLinkify 함수가 window.testLinkify()로 등록되었습니다.');
  
  // 실제 DOM 렌더링 테스트 함수
  (window as any).testDOMRendering = () => {
    console.log('🧪 DOM 렌더링 테스트 시작');
    
    // 1. linkifyText 함수 테스트
    const testText = "링크 테스트: https://www.naver.com";
    const result = linkifyText(testText);
    console.log('📝 입력 텍스트:', testText);
    console.log('⚛️ linkifyText 결과:', result);
    console.log('🔍 결과 타입:', typeof result);
    console.log('✅ React 요소인가?', React.isValidElement(result));
    
    // 2. 현재 DOM의 <a> 태그 개수 확인
    const links = document.querySelectorAll('a');
    console.log('🔗 현재 DOM의 <a> 태그 개수:', links.length);
    links.forEach((link, index) => {
      console.log(`📎 링크 ${index + 1}:`, link.href, link.textContent);
    });
    
    // 3. ChatBubble 컴포넌트 찾기
    const chatBubbles = document.querySelectorAll('[class*="rounded-3xl"]');
    console.log('💬 ChatBubble 개수:', chatBubbles.length);
    
    return {
      linkifyResult: result,
      domLinks: links.length,
      chatBubbles: chatBubbles.length
    };
  };
  
  // 🔧 새로운 강력한 DOM 실시간 검사 함수
  (window as any).debugChatLinks = () => {
    console.log('🔍 === 챗봇 링크 실시간 디버깅 ===');
    
    // 1. 모든 채팅 버블 찾기
    const chatBubbles = document.querySelectorAll('[class*="rounded-3xl"]');
    console.log(`💬 총 ChatBubble 개수: ${chatBubbles.length}`);
    
    chatBubbles.forEach((bubble, index) => {
      console.log(`\n--- 버블 ${index + 1} ---`);
      console.log('📄 innerHTML:', bubble.innerHTML);
      console.log('📝 textContent:', bubble.textContent);
      
      // 버블 내 링크 찾기
      const linksInBubble = bubble.querySelectorAll('a');
      console.log(`🔗 버블 내 <a> 태그 개수: ${linksInBubble.length}`);
      
      linksInBubble.forEach((link, linkIndex) => {
        console.log(`  📎 링크 ${linkIndex + 1}:`);
        console.log(`    - href: ${link.href}`);
        console.log(`    - text: ${link.textContent}`);
        console.log(`    - visible: ${window.getComputedStyle(link).display !== 'none'}`);
        console.log(`    - clickable: ${window.getComputedStyle(link).pointerEvents !== 'none'}`);
        console.log(`    - color: ${window.getComputedStyle(link).color}`);
        console.log(`    - css: ${link.style.cssText}`);
      });
      
      // URL 패턴이 있는데 링크가 없는 경우 체크
      const hasUrlPattern = /https?:\/\/[^\s]+/.test(bubble.textContent || '');
      if (hasUrlPattern && linksInBubble.length === 0) {
        console.log('⚠️ URL 패턴은 있지만 <a> 태그가 없음!');
        console.log('📝 텍스트:', bubble.textContent);
      }
    });
    
    // 2. 전역 링크 상태
    const allLinks = document.querySelectorAll('a');
    console.log(`\n🌐 전체 페이지 <a> 태그 개수: ${allLinks.length}`);
    
    // 3. React DevTools 정보 (가능한 경우)
    const reactRoot = document.getElementById('root');
    if (reactRoot && (reactRoot as any)._reactInternalFiber) {
      console.log('⚛️ React 상태 확인 가능');
    }
    
    return {
      totalBubbles: chatBubbles.length,
      totalLinks: allLinks.length,
      bubblesWithLinks: Array.from(chatBubbles).filter(b => b.querySelectorAll('a').length > 0).length
    };
  };
  
  // 🔧 메시지 타입 검사 함수
  (window as any).debugMessageTypes = () => {
    console.log('🔍 === 메시지 타입 디버깅 ===');
    
    // localStorage에서 메시지 히스토리 확인 (가능한 경우)
    const chatHistory = localStorage.getItem('chatHistory');
    if (chatHistory) {
      try {
        const messages = JSON.parse(chatHistory);
        console.log('💾 저장된 메시지 개수:', messages.length);
        messages.forEach((msg: any, index: number) => {
          console.log(`메시지 ${index + 1}:`, {
            type: typeof msg.content,
            content: msg.content,
            isUser: msg.isUser
          });
        });
      } catch (e) {
        console.log('💾 메시지 히스토리 파싱 실패');
      }
    }
    
    return true;
  };
  
  // 🔧 강제 링크 테스트 함수
  (window as any).forceTestLink = (text?: string) => {
    const testText = text || "강제 테스트: https://www.google.com 링크입니다";
    console.log('🚀 강제 링크 테스트 시작');
    console.log('📝 테스트 텍스트:', testText);
    
    const result = linkifyText(testText);
    console.log('⚛️ linkifyText 결과:', result);
    
    // 임시 div에 렌더링해서 실제 HTML 확인
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = result?.toString() || 'null';
    console.log('🔧 toString() 결과:', tempDiv.innerHTML);
    
    return result;
  };
  
  console.log('🧪 모든 디버깅 함수가 등록되었습니다:');
  console.log('  - window.testDOMRendering()');
  console.log('  - window.debugChatLinks()');
  console.log('  - window.debugMessageTypes()');
  console.log('  - window.forceTestLink()');
} 