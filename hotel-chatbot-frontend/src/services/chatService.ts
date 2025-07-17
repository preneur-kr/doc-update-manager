import {
  sendChatMessage,
  checkChatApiHealthWithRetry,
  checkChatApiReady,
} from '../api/chatApi';
import { CONFIG } from '../config/env';
import { debugLog } from '../utils/debugUtils';

export type ApiStatus = 'checking' | 'warming_up' | 'connected' | 'disconnected';

export interface ChatServiceOptions {
  onApiStatusChange: (status: ApiStatus) => void;
  onError: (title: string, message?: string) => void;
}

export class ChatService {
  private healthCheckInterval: number | null = null;
  private mounted = true;

  constructor(private options: ChatServiceOptions) {}

  /**
   * API 연결 상태를 확인하고 주기적 모니터링을 시작합니다.
   */
  async initializeConnection(): Promise<void> {
    try {
      debugLog.log('🔄 API 연결 상태 체크 시작');
      
      // 헬스 체크로 연결 상태 확인 (Render cold start 고려한 타임아웃)
      const readyCheck = await checkChatApiReady(CONFIG.API.TIMEOUT_QUICK);
      debugLog.log('🔄 첫 번째 체크 결과:', readyCheck);

      if (this.mounted) {
        if (readyCheck.ready) {
          debugLog.log('✅ 연결 성공!');
          this.options.onApiStatusChange('connected');
        } else {
          debugLog.log('⚠️ 첫 번째 체크 실패, 재시도 중...');
          // 실패 시 재시도 (지수 백오프, 설정된 재시도 횟수 및 타임아웃)
          const isHealthy = await checkChatApiHealthWithRetry(
            CONFIG.API.RETRY_COUNT,
            CONFIG.API.RETRY_DELAY,
            CONFIG.API.TIMEOUT_HEALTH
          );
          debugLog.log('🔄 재시도 결과:', isHealthy);
          this.options.onApiStatusChange(isHealthy ? 'connected' : 'disconnected');
        }
      }

      // 연결 성공 시 주기적 체크 시작 (설정된 간격으로)
      if (this.mounted && readyCheck.ready && !this.healthCheckInterval) {
        this.startHealthCheck();
      }
    } catch {
      if (this.mounted) {
        this.options.onApiStatusChange('disconnected');
      }
    }
  }

  /**
   * 주기적 헬스 체크를 시작합니다.
   */
  private startHealthCheck(): void {
    this.healthCheckInterval = window.setInterval(async () => {
      if (this.mounted) {
        debugLog.log('🔄 주기적 연결 상태 체크');
        const quickCheck = await checkChatApiReady(CONFIG.API.TIMEOUT_EXTENDED);
        debugLog.log('🔄 주기적 체크 결과:', quickCheck);
        if (this.mounted) {
          this.options.onApiStatusChange(quickCheck.ready ? 'connected' : 'disconnected');
        }
      }
    }, CONFIG.API.HEALTH_CHECK_INTERVAL);
  }

  /**
   * 채팅 메시지를 전송합니다.
   */
  async sendMessage(
    message: string, 
    currentApiStatus: ApiStatus
  ): Promise<{ success: boolean; response?: string }> {
    if (!message.trim()) {
      return { success: false };
    }

    // API 연결 상태 확인
    if (currentApiStatus === 'checking') {
      this.options.onError(
        '연결 확인 중',
        '서버 연결을 확인하는 중입니다. 잠시 후 다시 시도해주세요.'
      );
      return { success: false };
    }

    if (currentApiStatus === 'warming_up') {
      this.options.onError(
        '서버 준비 중',
        '서버가 준비 중입니다. 잠시 후 다시 시도해주세요.'
      );
      return { success: false };
    }

    if (currentApiStatus === 'disconnected') {
      this.options.onError(
        '서버 연결 오류',
        '서버에 연결할 수 없습니다. 연결 상태를 확인해주세요.'
      );
      return { success: false };
    }

    try {
      const response = await sendChatMessage({ message });
      return { success: true, response: response.answer };
    } catch (error) {
      this.options.onError('전송 실패', '메시지 전송 중 오류가 발생했습니다.');

      // 연결 오류 시 상태 재확인
      this.options.onApiStatusChange('checking');
      setTimeout(async () => {
        const isHealthy = await checkChatApiHealthWithRetry(
          CONFIG.API.RETRY_COUNT - 1, // 오류 시에는 재시도 횟수를 줄임
          CONFIG.API.RETRY_DELAY_EXTENDED,
          CONFIG.API.TIMEOUT_HEALTH
        );
        this.options.onApiStatusChange(isHealthy ? 'connected' : 'disconnected');
      }, CONFIG.API.RECONNECT_DELAY);

      const errorMessage = error instanceof Error ? error.message : '서버와의 통신 중 오류가 발생했습니다.';
      return { success: false, response: errorMessage };
    }
  }

  /**
   * 서비스를 정리합니다.
   */
  destroy(): void {
    this.mounted = false;
    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval);
      this.healthCheckInterval = null;
    }
  }
} 