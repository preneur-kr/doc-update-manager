import React from 'react';
import { 
  ClockIcon, 
  TruckIcon, 
  HomeIcon, 
  CreditCardIcon,
  QuestionMarkCircleIcon,
  CalendarDaysIcon
} from '@heroicons/react/24/outline';

interface QuickReply {
  id: string;
  text: string;
  icon: React.ComponentType<{ className?: string }>;
  message: string;
}

interface QuickRepliesProps {
  onSelectReply: (message: string) => void;
  isVisible?: boolean;
}

const quickReplies: QuickReply[] = [
  {
    id: 'checkin',
    text: '체크인 시간',
    icon: ClockIcon,
    message: '체크인 시간이 언제인가요?'
  },
  {
    id: 'parking',
    text: '주차 안내',
    icon: TruckIcon,
    message: '주차 가능한가요?'
  },
  {
    id: 'breakfast',
    text: '조식 안내',
    icon: HomeIcon,
    message: '조식 제공하나요?'
  },
  {
    id: 'cancel',
    text: '취소 정책',
    icon: CreditCardIcon,
    message: '취소 정책이 궁금해요'
  },
  {
    id: 'reservation',
    text: '예약 변경',
    icon: CalendarDaysIcon,
    message: '예약 변경은 어떻게 하나요?'
  },
  {
    id: 'other',
    text: '기타 문의',
    icon: QuestionMarkCircleIcon,
    message: '기타 문의사항이 있어요'
  }
];

export const QuickReplies: React.FC<QuickRepliesProps> = ({ onSelectReply, isVisible = true }) => {
  if (!isVisible) return null;

  return (
    <div className="px-4 py-4 bg-white/95 backdrop-blur-sm border-t border-gray-100">
      <div className="mb-3">
        <span className="text-sm font-medium text-gray-600">빠른 답변</span>
      </div>
      
      <div className="grid grid-cols-2 gap-3 max-w-md">
        {quickReplies.map((reply) => {
          const IconComponent = reply.icon;
          return (
            <button
              key={reply.id}
              onClick={() => onSelectReply(reply.message)}
              className="flex items-center gap-3 px-4 py-3 rounded-xl 
                       min-h-[48px]
                       bg-gray-50 
                       hover:bg-blue-50 
                       active:bg-blue-100
                       border border-gray-200 
                       hover:border-blue-200 
                       transition-all duration-200 ease-in-out
                       text-left text-sm font-medium
                       text-gray-700 
                       hover:text-blue-700 
                       group
                       transform active:scale-95
                       shadow-sm hover:shadow-md"
            >
              <IconComponent className="w-5 h-5 text-gray-500 group-hover:text-blue-500 flex-shrink-0 transition-colors duration-200" />
              <span className="truncate leading-tight">{reply.text}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}; 