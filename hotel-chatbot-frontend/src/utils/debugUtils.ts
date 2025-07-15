// 🔒 보안: 개발/프로덕션 환경 구분 디버그 유틸리티

const isDevelopment = import.meta.env.DEV;

/**
 * 개발 환경에서만 콘솔 로그를 출력하는 안전한 함수들
 */
export const debugLog = {
  log: (...args: unknown[]) => {
    if (isDevelopment) {
      console.log(...args);
    }
  },
  
  warn: (...args: unknown[]) => {
    if (isDevelopment) {
      console.warn(...args);
    }
  },
  
  error: (...args: unknown[]) => {
    if (isDevelopment) {
      console.error(...args);
    }
  },
  
  info: (...args: unknown[]) => {
    if (isDevelopment) {
      console.info(...args);
    }
  },
  
  debug: (...args: unknown[]) => {
    if (isDevelopment) {
      console.debug(...args);
    }
  }
};

/**
 * 개발 환경에서만 실행되는 함수
 */
export const onlyInDev = (callback: () => void) => {
  if (isDevelopment) {
    callback();
  }
};

/**
 * 프로덕션에서는 제거되는 디버그 전용 함수 등록
 */
export const registerDebugFunctions = (debugFunctions: Record<string, unknown>) => {
  if (isDevelopment && typeof window !== 'undefined') {
    Object.entries(debugFunctions).forEach(([name, func]) => {
      (window as unknown as Record<string, unknown>)[name] = func;
    });
    debugLog.log('🧪 디버그 함수들이 등록되었습니다:', Object.keys(debugFunctions));
  }
};

export { isDevelopment }; 