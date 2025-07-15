import { useState, useCallback, useEffect } from 'react';

interface QueuedMessage {
  id: string;
  content: string;
  timestamp: Date;
}

interface UseMessageQueueOptions {
  apiStatus: 'checking' | 'connected' | 'disconnected';
  onSendMessage: (message: string) => Promise<void>;
}

export const useMessageQueue = ({
  apiStatus,
  onSendMessage,
}: UseMessageQueueOptions) => {
  const [messageQueue, setMessageQueue] = useState<QueuedMessage[]>([]);
  const [isProcessingQueue, setIsProcessingQueue] = useState(false);

  const processQueue = useCallback(async () => {
    if (messageQueue.length === 0 || isProcessingQueue) return;

    setIsProcessingQueue(true);

    try {
      // 큐의 첫 번째 메시지 처리
      const [firstMessage, ...remainingMessages] = messageQueue;

      await onSendMessage(firstMessage.content);

      // 성공적으로 전송된 메시지를 큐에서 제거
      setMessageQueue(remainingMessages);
    } catch (error) {
      console.error('큐 메시지 전송 실패:', error);
      // 실패 시 큐를 그대로 유지하여 재시도 가능하도록 함
    } finally {
      setIsProcessingQueue(false);
    }
  }, [messageQueue, isProcessingQueue, onSendMessage]);

  // API 연결 완료 시 큐의 메시지들을 자동 전송
  useEffect(() => {
    if (
      apiStatus === 'connected' &&
      messageQueue.length > 0 &&
      !isProcessingQueue
    ) {
      processQueue();
    }
  }, [apiStatus, messageQueue.length, isProcessingQueue, processQueue]);

  const queueMessage = useCallback((message: string) => {
    const queuedMessage: QueuedMessage = {
      id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
      content: message,
      timestamp: new Date(),
    };

    setMessageQueue(prev => [...prev, queuedMessage]);
  }, []);

  const clearQueue = useCallback(() => {
    setMessageQueue([]);
  }, []);

  return {
    messageQueue,
    queueMessage,
    clearQueue,
    isProcessingQueue,
    hasQueuedMessages: messageQueue.length > 0,
  };
};
