import { useState, useEffect, useRef } from 'react';

interface UseStreamingTextOptions {
  text: string;
  speed?: number; // 글자당 지연 시간 (ms)
  startDelay?: number; // 시작 전 지연 시간 (ms)
  onComplete?: () => void;
}

export const useStreamingText = ({
  text,
  speed = 30,
  startDelay = 300,
  onComplete,
}: UseStreamingTextOptions) => {
  const [displayText, setDisplayText] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [isComplete, setIsComplete] = useState(false);
  const timeoutRef = useRef<number | null>(null);
  const indexRef = useRef(0);

  useEffect(() => {
    // 텍스트가 변경되면 리셋
    setDisplayText('');
    setIsStreaming(false);
    setIsComplete(false);
    indexRef.current = 0;

    if (!text) return;

    // 시작 지연 후 스트리밍 시작
    const startTimeout = setTimeout(() => {
      setIsStreaming(true);
      streamText();
    }, startDelay);

    return () => {
      clearTimeout(startTimeout);
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [text]);

  const streamText = () => {
    if (indexRef.current < text.length) {
      setDisplayText(text.slice(0, indexRef.current + 1));
      indexRef.current += 1;

      timeoutRef.current = setTimeout(streamText, speed);
    } else {
      setIsStreaming(false);
      setIsComplete(true);
      onComplete?.();
    }
  };

  const skipToEnd = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    setDisplayText(text);
    setIsStreaming(false);
    setIsComplete(true);
    indexRef.current = text.length;
    onComplete?.();
  };

  return {
    displayText,
    isStreaming,
    isComplete,
    skipToEnd,
  };
};
