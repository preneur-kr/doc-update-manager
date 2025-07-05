import type { ChatResponse, ChatMessage } from '../types/chat';

// API 기본 URL - 환경 변수 사용
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

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
export const sendChatMessage = async (request: ChatRequest): Promise<ChatResponse> => {
  const url = `${API_BASE_URL}/api/v1/chat`;
  console.log('🚀 API 호출 시작:', {
    url,
    baseUrl: API_BASE_URL,
    request
  });

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    console.log('📡 API 응답 상태:', {
      status: response.status,
      statusText: response.statusText,
      ok: response.ok
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ API 오류 응답:', errorText);
      throw new Error(`API 요청 실패: ${response.status} ${response.statusText}`);
    }

    const data: ChatResponse = await response.json();
    console.log('✅ API 응답 성공:', data);
    return data;
  } catch (error) {
    console.error('💥 채팅 API 호출 중 오류:', error);
    throw new Error('서버와의 통신 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.');
  }
};

/**
 * 챗봇 API 상태를 확인합니다.
 */
export const checkChatApiHealth = async (): Promise<boolean> => {
  const healthUrl = `${API_BASE_URL}/health`;
  console.log('🏥 헬스 체크 시작:', healthUrl);
  
  try {
    const response = await fetch(healthUrl);
    console.log('🏥 헬스 체크 응답:', {
      status: response.status,
      statusText: response.statusText,
      ok: response.ok
    });
    return response.ok;
  } catch (error) {
    console.error('❌ API 상태 확인 중 오류:', error);
    return false;
  }
};

// 기존 코드와의 호환성을 위한 별칭 (deprecated)
export const sendMessage = sendChatMessage;
