// 🚀 성능 최적화 유틸리티 함수들

/**
 * 메모리 사용량 모니터링 (개발 환경에서만)
 */
export const measureMemory = (): Promise<any> => {
  if ('memory' in performance && import.meta.env.DEV) {
    return Promise.resolve((performance as any).memory);
  }
  return Promise.resolve(null);
};

/**
 * 컴포넌트 렌더링 성능 측정
 */
export const measureRender = (componentName: string) => {
  if (!import.meta.env.DEV) return { start: () => {}, end: () => {} };

  let startTime: number;
  
  return {
    start: () => {
      startTime = performance.now();
    },
    end: () => {
      const endTime = performance.now();
      const duration = endTime - startTime;
      console.log(`🎯 ${componentName} 렌더링 시간: ${duration.toFixed(2)}ms`);
      return duration;
    }
  };
};

/**
 * 이미지 지연 로딩을 위한 Intersection Observer 래퍼
 */
export const createLazyImageObserver = (callback: (entry: IntersectionObserverEntry) => void) => {
  if (typeof IntersectionObserver === 'undefined') {
    return null;
  }

  return new IntersectionObserver(
    (entries) => {
      entries.forEach(callback);
    },
    {
      threshold: 0.1,
      rootMargin: '50px 0px',
    }
  );
};

/**
 * 메모리 누수 방지를 위한 디바운스 함수
 */
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  delay: number
): ((...args: Parameters<T>) => void) => {
  let timeoutId: number | undefined;

  return (...args: Parameters<T>) => {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }
    
    timeoutId = setTimeout(() => {
      func(...args);
    }, delay);
  };
};

/**
 * 스로틀링 함수 (성능 최적화)
 */
export const throttle = <T extends (...args: any[]) => any>(
  func: T,
  limit: number
): ((...args: Parameters<T>) => void) => {
  let inThrottle: boolean;

  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
};

/**
 * 청크 단위 데이터 처리 (대용량 데이터용)
 */
export const processInChunks = async <T, R>(
  items: T[],
  processor: (item: T) => R | Promise<R>,
  chunkSize: number = 100,
  delay: number = 0
): Promise<R[]> => {
  const results: R[] = [];
  
  for (let i = 0; i < items.length; i += chunkSize) {
    const chunk = items.slice(i, i + chunkSize);
    const chunkResults = await Promise.all(
      chunk.map(processor)
    );
    
    results.push(...chunkResults);
    
    // 다음 청크 처리 전 지연 (UI 블로킹 방지)
    if (delay > 0 && i + chunkSize < items.length) {
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
  
  return results;
};

/**
 * 컴포넌트 마운트/언마운트 추적 (메모리 누수 디버깅)
 */
export const createComponentTracker = (componentName: string) => {
  if (!import.meta.env.DEV) {
    return { mount: () => {}, unmount: () => {} };
  }

  return {
    mount: () => {
      console.log(`🟢 ${componentName} 마운트됨`);
    },
    unmount: () => {
      console.log(`🔴 ${componentName} 언마운트됨`);
    }
  };
};

/**
 * 성능 메트릭 수집기
 */
export class PerformanceCollector {
  private metrics: Map<string, number[]> = new Map();
  
  measure(key: string, value: number) {
    if (!this.metrics.has(key)) {
      this.metrics.set(key, []);
    }
    
    this.metrics.get(key)!.push(value);
    
    // 최대 100개 측정값만 유지 (메모리 절약)
    const values = this.metrics.get(key)!;
    if (values.length > 100) {
      values.shift();
    }
  }
  
  getStats(key: string) {
    const values = this.metrics.get(key) || [];
    if (values.length === 0) return null;
    
    const avg = values.reduce((sum, val) => sum + val, 0) / values.length;
    const min = Math.min(...values);
    const max = Math.max(...values);
    
    return { avg, min, max, count: values.length };
  }
  
  clear() {
    this.metrics.clear();
  }
}

// 전역 성능 수집기 인스턴스
export const globalPerformanceCollector = new PerformanceCollector(); 