import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { ChatBubbleLeftIcon, UserIcon } from '@heroicons/react/24/outline';

interface ChatBubbleProps {
  message: string;
  isUser: boolean;
  timestamp: Date;
}

export const ChatBubble: React.FC<ChatBubbleProps> = ({ 
  message, 
  isUser, 
  timestamp
}) => {
  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: false 
    });
  };

  return (
    <div className={`flex w-full ${isUser ? 'justify-end' : 'justify-start'} items-end gap-3 mb-4`}>
      {/* 아바타 - 봇 메시지일 때만 표시 */}
      {!isUser && (
        <div className="w-9 h-9 rounded-full bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center shadow-md flex-shrink-0">
          <ChatBubbleLeftIcon className="w-5 h-5 text-white" />
        </div>
      )}
      
      {/* 메시지 버블 */}
      <div className={`relative max-w-[85%] md:max-w-[70%] ${isUser ? 'order-first' : ''}`}>
        <div
          className={`px-4 py-3 rounded-2xl shadow-sm text-[15px] leading-relaxed break-words relative
            ${isUser 
              ? 'bg-blue-600 text-white rounded-br-md ml-auto' 
              : 'bg-white text-gray-800 rounded-bl-md border border-gray-100'
            }
          `}
        >
          {/* 마크다운 렌더링 */}
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              code({node, ...props}) {
                // @ts-expect-error: react-markdown v8+ passes 'inline' in props
                const isInline = props.inline;
                return !isInline ? (
                  <pre className={`rounded-lg p-3 my-2 overflow-x-auto text-sm ${
                    isUser 
                      ? 'bg-blue-800 text-blue-100' 
                      : 'bg-gray-900 text-gray-100'
                  }`}>
                    <code {...props}>{props.children}</code>
                  </pre>
                ) : (
                  <code className={`rounded px-1.5 py-0.5 text-sm font-mono ${
                    isUser 
                      ? 'bg-blue-500 text-blue-100' 
                      : 'bg-gray-100 text-pink-600'
                  }`} {...props}>
                    {props.children}
                  </code>
                );
              },
              a({href, children, ...props}) {
                return (
                  <a 
                    href={href} 
                    className={`underline hover:no-underline transition-colors duration-300 ${
                      isUser 
                        ? 'text-blue-200 hover:text-white' 
                        : 'text-blue-600 hover:text-blue-800'
                    }`}
                    target="_blank" 
                    rel="noopener noreferrer" 
                    {...props}
                  >
                    {children}
                  </a>
                );
              },
              strong({children, ...props}) {
                return <strong className="font-semibold" {...props}>{children}</strong>;
              }
            }}
          >
            {message}
          </ReactMarkdown>
        </div>
        
        {/* 타임스탬프 */}
        <div className={`flex items-center mt-1 ${isUser ? 'justify-end' : 'justify-start'}`}>
          <span className="text-xs text-gray-400 select-none">
            {formatTime(timestamp)}
          </span>
        </div>
      </div>
      
      {/* 사용자 아바타 */}
      {isUser && (
        <div className="w-9 h-9 rounded-full bg-gradient-to-br from-gray-600 to-gray-700 flex items-center justify-center shadow-md flex-shrink-0">
          <UserIcon className="w-5 h-5 text-white" />
        </div>
      )}
    </div>
  );
};

