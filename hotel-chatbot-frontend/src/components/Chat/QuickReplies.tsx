import React from 'react';

interface QuickReply {
  id: string;
  text: string;
  message: string;
}

interface QuickRepliesProps {
  onSelectReply: (message: string) => void;
  isVisible?: boolean;
}

const quickReplies: QuickReply[] = [
  {
    id: 'invoice',
    text: '📄 인보이스 발행하기',
    message: '인보이스를 발행해주세요'
  },
  {
    id: 'parking',
    text: '🚗 주차 안내',
    message: '주차 가능한가요?'
  },
  {
    id: 'reservation_status',
    text: '📋 예약 현황 보러가기',
    message: '예약 현황을 확인하고 싶어요'
  },
  {
    id: 'cancel',
    text: '❌ 취소 정책',
    message: '취소 정책이 궁금해요'
  }
];

export const QuickReplies: React.FC<QuickRepliesProps> = ({ onSelectReply, isVisible = true }) => {
  if (!isVisible) return null;

  return (
    <div className="px-2 sm:px-3 py-3 sm:py-4 bg-gray-50 border-t border-gray-100">
      <div className="mb-3">
        <p className="text-sm text-gray-600 font-medium">빠른 답변</p>
      </div>
      <div className="flex flex-wrap gap-2">
        {quickReplies.map((reply) => {
          return (
            <button
              key={reply.id}
              onClick={() => onSelectReply(reply.message)}
              className="inline-block min-h-[40px] px-3 py-2 bg-white border border-gray-200 text-left transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              style={{
                borderRadius: '24px'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#f8fafc';
                e.currentTarget.style.borderColor = '#e2e8f0';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = '#ffffff';
                e.currentTarget.style.borderColor = '#e5e7eb';
              }}
              onMouseDown={(e) => {
                e.currentTarget.style.backgroundColor = '#f1f5f9';
              }}
              onMouseUp={(e) => {
                e.currentTarget.style.backgroundColor = '#f8fafc';
              }}
              aria-label={`빠른 답변: ${reply.text}`}
            >
              <span className="text-sm font-medium text-gray-800">
                {reply.text}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}; 