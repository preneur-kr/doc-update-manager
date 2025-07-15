import React, { useEffect, useState } from 'react';
import {
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline';

export type ToastType = 'success' | 'error' | 'warning' | 'info';

interface ToastProps {
  id: string;
  type: ToastType;
  title: string;
  message?: string;
  duration?: number;
  onClose: (id: string) => void;
  position?: 'top' | 'bottom';
}

const toastIcons = {
  success: CheckCircleIcon,
  error: XCircleIcon,
  warning: ExclamationTriangleIcon,
  info: InformationCircleIcon,
};

const toastColors = {
  success: 'bg-green-50 border-green-200 text-green-800',
  error: 'bg-red-50 border-red-200 text-red-800',
  warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
  info: 'bg-blue-50 border-blue-200 text-blue-800',
};

const iconColors = {
  success: 'text-green-400',
  error: 'text-red-400',
  warning: 'text-yellow-400',
  info: 'text-blue-400',
};

export const Toast: React.FC<ToastProps> = ({
  id,
  type,
  title,
  message,
  duration = 4000,
  onClose,
  position = 'top',
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [isExiting, setIsExiting] = useState(false);

  const Icon = toastIcons[type];

  useEffect(() => {
    // 등장 애니메이션
    const showTimer = setTimeout(() => setIsVisible(true), 50);

    // 자동 닫기
    const hideTimer = setTimeout(() => {
      setIsExiting(true);
      setTimeout(() => onClose(id), 300);
    }, duration);

    return () => {
      clearTimeout(showTimer);
      clearTimeout(hideTimer);
    };
  }, [id, duration, onClose]);

  const handleClose = () => {
    setIsExiting(true);
    setTimeout(() => onClose(id), 300);
  };

  return (
    <div
      className={`
        fixed left-4 right-4 z-50 transform transition-all duration-300 ease-out
        ${position === 'top' ? 'top-4 safe-area-top' : 'bottom-4 safe-area-bottom'}
        ${
          isVisible && !isExiting
            ? 'translate-y-0 opacity-100'
            : position === 'top'
              ? '-translate-y-full opacity-0'
              : 'translate-y-full opacity-0'
        }
      `}
    >
      <div
        className={`
          ${toastColors[type]}
          rounded-2xl border shadow-lg backdrop-blur-sm
          p-4 mx-auto max-w-sm
          touch-manipulation
        `}
      >
        <div className='flex items-start space-x-3'>
          <Icon
            className={`w-6 h-6 ${iconColors[type]} flex-shrink-0 mt-0.5`}
          />

          <div className='flex-1 min-w-0'>
            <p className='text-sm font-semibold leading-tight'>{title}</p>
            {message && (
              <p className='text-xs mt-1 opacity-90 leading-relaxed'>
                {message}
              </p>
            )}
          </div>

          <button
            onClick={handleClose}
            className='flex-shrink-0 ml-2 p-1 rounded-full hover:bg-black/10 transition-colors duration-200 touch-feedback'
            aria-label='알림 닫기'
          >
            <XMarkIcon className='w-4 h-4 opacity-60' />
          </button>
        </div>
      </div>
    </div>
  );
};

// 토스트 컨테이너 컴포넌트
interface ToastContainerProps {
  toasts: Array<{
    id: string;
    type: ToastType;
    title: string;
    message?: string;
    duration?: number;
  }>;
  onClose: (id: string) => void;
  position?: 'top' | 'bottom';
}

export const ToastContainer: React.FC<ToastContainerProps> = ({
  toasts,
  onClose,
  position = 'top',
}) => {
  return (
    <>
      {toasts.map(toast => (
        <Toast
          key={toast.id}
          id={toast.id}
          type={toast.type}
          title={toast.title}
          message={toast.message}
          duration={toast.duration}
          onClose={onClose}
          position={position}
        />
      ))}
    </>
  );
};
