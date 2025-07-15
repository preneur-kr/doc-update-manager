import type { ChatResponse, ChatMessage } from '../types/chat';
import { debugLog, registerDebugFunctions, onlyInDev } from '../utils/debugUtils';
import { CONFIG } from '../config/env';

// 🔧 환경설정에서 API 설정 가져오기
const { BASE_URL: API_BASE_URL } = CONFIG.API;

// 🔒 보안: 개발 환경에서만 디버깅 로그
debugLog.log('🌐 API_BASE_URL:', API_BASE_URL);
debugLog.log(
  '🌐 환경변수 VITE_API_BASE_URL:',
  import.meta.env.VITE_API_BASE_URL
);
debugLog.log('🌐 모든 환경변수:', import.meta.env);

export interface ChatRequest {
  message: string;
  category?: string;
  section?: string;
}

// 타입 명시적 re-export
export type { ChatMessage, ChatResponse };

/**
 * 챗봇 API와 통신하여 호텔 정책 질문에 대한 답변을 받습니다.
 */
export const sendChatMessage = async (
  request: ChatRequest
): Promise<ChatResponse> => {
  const url = `${API_BASE_URL}/api/v1/chat`;
  const startTime = performance.now();

  debugLog.log('🚀 API 호출 시작:', {
    url,
    baseUrl: API_BASE_URL,
    request,
    timestamp: new Date().toISOString(),
  });

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    const responseTime = performance.now() - startTime;

    debugLog.log('📡 API 응답 상태:', {
      status: response.status,
      statusText: response.statusText,
      ok: response.ok,
      responseTime: `${responseTime.toFixed(2)}ms`,
    });

    if (!response.ok) {
      const errorText = await response.text();
      debugLog.error('❌ API 오류 응답:', errorText);

      // 성능 메트릭 로그 (오류 시)
      debugLog.log('📊 성능 메트릭 (오류):', {
        responseTime: `${responseTime.toFixed(2)}ms`,
        status: 'error',
        statusCode: response.status,
      });

      throw new Error(
        `API 요청 실패: ${response.status} ${response.statusText}`
      );
    }

    const data: ChatResponse = await response.json();
    const totalTime = performance.now() - startTime;

    // 성능 메트릭 로그 (성공 시)
    debugLog.log('📊 성능 메트릭 (성공):', {
      responseTime: `${totalTime.toFixed(2)}ms`,
      status: 'success',
      messageLength: request.message.length,
      responseLength: data.answer.length,
      isFallback: data.is_fallback,
    });

    debugLog.log('✅ API 응답 성공:', data);
    return data;
  } catch (error) {
    const errorTime = performance.now() - startTime;

    // 성능 메트릭 로그 (예외 시)
    debugLog.log('📊 성능 메트릭 (예외):', {
      responseTime: `${errorTime.toFixed(2)}ms`,
      status: 'exception',
      error: error instanceof Error ? error.message : 'unknown',
    });

    debugLog.error('💥 채팅 API 호출 중 오류:', error);
    throw new Error(
      '서버와의 통신 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.'
    );
  }
};

/**
 * 챗봇 API 빠른 준비 상태를 확인합니다.
 * Render의 cold start를 고려하여 충분한 타임아웃 설정
 */
export const checkChatApiReady = async (
  timeout: number = CONFIG.API.TIMEOUT_QUICK
): Promise<{ ready: boolean; status: string }> => {
  const healthUrl = `${API_BASE_URL}/health`;
  const startTime = performance.now();
  debugLog.log(
    '⚡ 빠른 준비 상태 체크 시작:',
    healthUrl,
    `(타임아웃: ${timeout}ms)`
  );

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    const response = await fetch(healthUrl, {
      signal: controller.signal,
      headers: {
        Accept: 'application/json',
      },
    });

    clearTimeout(timeoutId);
    const responseTime = performance.now() - startTime;

    if (response.ok) {
      const data = await response.json();
      debugLog.log(
        '⚡ 빠른 준비 상태 응답:',
        data,
        `(${responseTime.toFixed(0)}ms)`
      );
      // health 엔드포인트는 항상 ready=true로 처리
      return {
        ready: true,
        status: data.status || 'ready',
      };
    } else {
      debugLog.warn(
        '⚠️ 헬스 체크 HTTP 오류:',
        response.status,
        `(${responseTime.toFixed(0)}ms)`
      );
      return { ready: false, status: 'error' };
    }
  } catch (error) {
    const responseTime = performance.now() - startTime;
    if (error instanceof Error && error.name === 'AbortError') {
      debugLog.error(
        '❌ 빠른 준비 상태 확인 타임아웃:',
        timeout + 'ms',
        `(실제: ${responseTime.toFixed(0)}ms)`
      );
    } else {
      debugLog.error(
        '❌ 빠른 준비 상태 확인 중 오류:',
        error,
        `(${responseTime.toFixed(0)}ms)`
      );
    }
    return { ready: false, status: 'error' };
  }
};

/**
 * 챗봇 API 상태를 확인합니다.
 * Render 서버의 지연을 고려한 충분한 타임아웃 설정
 */
export const checkChatApiHealth = async (
  timeout: number = CONFIG.API.TIMEOUT_HEALTH
): Promise<boolean> => {
  const healthUrl = `${API_BASE_URL}/health`;
  const startTime = performance.now();
  debugLog.log('🏥 헬스 체크 시작:', healthUrl, `(타임아웃: ${timeout}ms)`);

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    const response = await fetch(healthUrl, {
      signal: controller.signal,
      headers: {
        Accept: 'application/json',
      },
    });

    clearTimeout(timeoutId);
    const responseTime = performance.now() - startTime;

    debugLog.log('🏥 헬스 체크 응답:', {
      status: response.status,
      statusText: response.statusText,
      ok: response.ok,
      responseTime: `${responseTime.toFixed(0)}ms`,
    });
    return response.ok;
  } catch (error) {
    const responseTime = performance.now() - startTime;
    if (error instanceof Error && error.name === 'AbortError') {
      debugLog.error(
        '❌ API 상태 확인 타임아웃:',
        timeout + 'ms',
        `(실제: ${responseTime.toFixed(0)}ms)`
      );
    } else {
      debugLog.error(
        '❌ API 상태 확인 중 오류:',
        error,
        `(${responseTime.toFixed(0)}ms)`
      );
    }
    return false;
  }
};

/**
 * 빠른 준비 상태 체크와 재시도 로직
 * 지수 백오프(Exponential Backoff)를 적용하여 안정적인 연결 보장
 *
 * @param maxRetries 최대 재시도 횟수 (기본 4회)
 * @param baseDelay 기본 지연 시간 (기본 1초, 지수적으로 증가)
 * @param timeout 각 요청의 타임아웃 (기본 8초)
 * @returns 연결 성공 여부
 */
export const checkChatApiHealthWithRetry = async (
  maxRetries: number = 4,
  baseDelay: number = 1000,
  timeout: number = 8000
): Promise<boolean> => {
  debugLog.log(
    `🔄 헬스 체크 재시도 시작 - 최대 ${maxRetries}회, 기본지연 ${baseDelay}ms, 타임아웃 ${timeout}ms`
  );

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    const attemptStartTime = performance.now();
    debugLog.log(`🔄 헬스 체크 시도 ${attempt}/${maxRetries}`);

    const isHealthy = await checkChatApiHealth(timeout);
    const attemptTime = performance.now() - attemptStartTime;

    if (isHealthy) {
      debugLog.log(
        `✅ 헬스 체크 성공 (${attempt}회차, ${attemptTime.toFixed(0)}ms)`
      );
      return true;
    }

    debugLog.warn(
      `❌ 헬스 체크 실패 (${attempt}회차, ${attemptTime.toFixed(0)}ms)`
    );

    // 마지막 시도가 아닌 경우에만 재시도 대기
    if (attempt < maxRetries) {
      // 지수 백오프: 1초 → 2초 → 4초 → 8초
      const delay = baseDelay * Math.pow(2, attempt - 1);
      const maxDelay = 8000; // 최대 8초로 제한
      const actualDelay = Math.min(delay, maxDelay);

      debugLog.log(
        `⏳ ${actualDelay}ms 후 재시도... (지수 백오프: ${attempt}회차)`
      );

      // 지연 구현 - Promise 기반
      await new Promise(resolve => setTimeout(resolve, actualDelay));
    }
  }

  debugLog.error(`❌ 모든 헬스 체크 시도 실패 (총 ${maxRetries}회 시도 완료)`);
  return false;
};

// 기존 코드와의 호환성을 위한 별칭 (deprecated)
export const sendMessage = sendChatMessage;

/**
 * 🧪 테스트 및 디버깅용 유틸 함수들
 */

/**
 * 헬스 체크 성능 테스트 함수
 * 여러 번 연속으로 헬스 체크를 실행하여 응답 시간 분포 확인
 */
export const testHealthCheckPerformance = async (testCount: number = 5) => {
  debugLog.log(`🧪 헬스 체크 성능 테스트 시작 (${testCount}회)`);
  const results = [];

  for (let i = 1; i <= testCount; i++) {
    debugLog.log(`--- 테스트 ${i}/${testCount} ---`);
    const startTime = performance.now();

    try {
      const result = await checkChatApiReady(8000);
      const endTime = performance.now();
      const duration = endTime - startTime;

      results.push({
        test: i,
        success: result.ready,
        duration: Math.round(duration),
        status: result.status,
      });

      debugLog.log(
        `✅ 테스트 ${i} 완료: ${duration.toFixed(0)}ms, 성공: ${result.ready}`
      );
    } catch (error) {
      const endTime = performance.now();
      const duration = endTime - startTime;

      results.push({
        test: i,
        success: false,
        duration: Math.round(duration),
        error: error instanceof Error ? error.message : 'Unknown error',
      });

      debugLog.log(
        `❌ 테스트 ${i} 실패: ${duration.toFixed(0)}ms, 오류: ${error}`
      );
    }

    // 테스트 간 1초 대기
    if (i < testCount) {
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  }

  // 결과 요약
  const successCount = results.filter(r => r.success).length;
  const avgDuration =
    results.reduce((sum, r) => sum + r.duration, 0) / results.length;
  const maxDuration = Math.max(...results.map(r => r.duration));
  const minDuration = Math.min(...results.map(r => r.duration));

  debugLog.log(`📊 성능 테스트 결과 요약:`);
  debugLog.log(
    `  - 성공률: ${successCount}/${testCount} (${((successCount / testCount) * 100).toFixed(1)}%)`
  );
  debugLog.log(`  - 평균 응답시간: ${avgDuration.toFixed(0)}ms`);
  debugLog.log(`  - 최대 응답시간: ${maxDuration}ms`);
  debugLog.log(`  - 최소 응답시간: ${minDuration}ms`);

  return {
    results,
    summary: {
      successRate: successCount / testCount,
      avgDuration: Math.round(avgDuration),
      maxDuration,
      minDuration,
    },
  };
};

/**
 * 재시도 로직 테스트 함수
 * 의도적으로 짧은 타임아웃을 사용하여 재시도 동작 확인
 */
export const testRetryLogic = async () => {
  debugLog.log('🧪 재시도 로직 테스트 시작');

  // 매우 짧은 타임아웃으로 실패를 유도하여 재시도 로직 테스트
  const result = await checkChatApiHealthWithRetry(3, 500, 100);

  debugLog.log('🧪 재시도 로직 테스트 완료:', result);
  return result;
};

/**
 * 전체 연결 플로우 테스트
 * 실제 App.tsx에서 사용하는 것과 동일한 로직으로 테스트
 */
export const testFullConnectionFlow = async () => {
  debugLog.log('🧪 전체 연결 플로우 테스트 시작');

  try {
    // 1단계: 빠른 체크
    debugLog.log('1️⃣ 빠른 연결 체크');
    const quickCheck = await checkChatApiReady(5000);

    if (quickCheck.ready) {
      debugLog.log('✅ 빠른 체크 성공 - 연결 완료');
      return { success: true, method: 'quick' };
    }

    // 2단계: 재시도 로직
    debugLog.log('2️⃣ 재시도 로직 실행');
    const retryResult = await checkChatApiHealthWithRetry(4, 1000, 8000);

    if (retryResult) {
      debugLog.log('✅ 재시도 성공 - 연결 완료');
      return { success: true, method: 'retry' };
    } else {
      debugLog.log('❌ 모든 시도 실패 - 연결 실패');
      return { success: false, method: 'failed' };
    }
  } catch (error) {
    debugLog.error('❌ 연결 플로우 테스트 중 오류:', error);
    return { success: false, method: 'error', error };
  }
};

// 🔒 보안: 개발 환경에서만 전역 함수 등록
onlyInDev(() => {
  registerDebugFunctions({
    testHealthPerformance: testHealthCheckPerformance,
    testRetryLogic,
    testConnectionFlow: testFullConnectionFlow,
  });
});
