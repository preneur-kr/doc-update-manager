import { useState, useCallback } from 'react';
import type { ToastType } from '../components/UI/Toast';
import { CONFIG } from '../config/env';

interface ToastItem {
  id: string;
  type: ToastType;
  title: string;
  message?: string;
  duration?: number;
}

export const useToast = () => {
  const [toasts, setToasts] = useState<ToastItem[]>([]);

  const addToast = useCallback(
    (type: ToastType, title: string, message?: string, duration?: number) => {
      const id =
        Date.now().toString() + Math.random().toString(36).substr(2, 9);
      const newToast: ToastItem = {
        id,
        type,
        title,
        message,
        duration: duration || CONFIG.UI.TOAST_DEFAULT_DURATION,
      };

      setToasts(prev => {
        // 설정된 최대 토스트 개수만 표시
        const maxToasts = CONFIG.UI.TOAST_MAX_COUNT;
        const newToasts = [newToast, ...prev];
        return newToasts.slice(0, maxToasts);
      });

      return id;
    },
    []
  );

  const removeToast = useCallback((id: string) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  }, []);

  const clearAllToasts = useCallback(() => {
    setToasts([]);
  }, []);

  // 편의 메서드들
  const success = useCallback(
    (title: string, message?: string, duration?: number) => {
      return addToast('success', title, message, duration);
    },
    [addToast]
  );

  const error = useCallback(
    (title: string, message?: string, duration?: number) => {
      return addToast('error', title, message, duration);
    },
    [addToast]
  );

  const warning = useCallback(
    (title: string, message?: string, duration?: number) => {
      return addToast('warning', title, message, duration);
    },
    [addToast]
  );

  const info = useCallback(
    (title: string, message?: string, duration?: number) => {
      return addToast('info', title, message, duration);
    },
    [addToast]
  );

  return {
    toasts,
    addToast,
    removeToast,
    clearAllToasts,
    success,
    error,
    warning,
    info,
  };
};
