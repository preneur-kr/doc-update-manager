import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface ChatBubbleProps {
  message: string;
  isUser: boolean;
  timestamp: Date;
  isFirst?: boolean;
}

export const ChatBubble: React.FC<ChatBubbleProps> = ({ message, isUser, timestamp }) => {
  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: false 
    });
  };

  return (
    <div className={`flex w-full ${isUser ? 'justify-end' : 'justify-start'} items-end gap-2`}>
      {/* 아바타 */}
      {!isUser ? (
        <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center text-xl select-none">
          <span role="img" aria-label="bot">🤖</span>
        </div>
      ) : (
        <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-base font-semibold text-white select-none">
          U
        </div>
      )}
      {/* 메시지 버블 */}
      <div className={`relative max-w-[80%] md:max-w-md ${isUser ? 'order-2' : 'order-1'}`}>
        <div
          className={`px-4 py-3 md:px-5 md:py-3 rounded-3xl shadow-md text-sm break-words
            ${isUser ? 'bg-blue-600 text-white rounded-br-xl' : 'bg-gray-200 text-gray-900 rounded-bl-xl'}
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
                  <pre className="bg-gray-800 text-white rounded-lg p-3 my-2 overflow-x-auto text-xs"><code {...props}>{props.children}</code></pre>
                ) : (
                  <code className="bg-gray-100 text-pink-600 rounded px-1 py-0.5 text-xs" {...props}>{props.children}</code>
                );
              },
              a({href, children, ...props}) {
                return <a href={href} className="text-blue-500 underline" target="_blank" rel="noopener noreferrer" {...props}>{children}</a>;
              },
              li({children, ...props}) {
                return <li className="ml-4 list-disc text-sm" {...props}>{children}</li>;
              },
              strong({children, ...props}) {
                return <strong className="font-semibold" {...props}>{children}</strong>;
              },
              em({children, ...props}) {
                return <em className="italic" {...props}>{children}</em>;
              },
            }}
          >
            {message}
          </ReactMarkdown>
          {/* 타임스탬프 */}
          <span className="block text-xs text-gray-400 text-right mt-1 select-none">{formatTime(timestamp)}</span>
        </div>
      </div>
    </div>
  );
};
