import type { ChatResponse } from '../types/chat';

// API 기본 URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

// 개발 환경에서 API URL 로깅
if (import.meta.env.DEV) {
  console.log('🔧 API Base URL:', API_BASE_URL || '환경 변수가 설정되지 않음');
}

export interface ChatRequest {
  message: string;
  category?: string;
  section?: string;
}

/**
 * 챗봇 API와 통신하여 호텔 정책 질문에 대한 답변을 받습니다.
 */
export const sendChatMessage = async (request: ChatRequest): Promise<ChatResponse> => {
  if (!API_BASE_URL) {
    console.error('❌ API Base URL이 설정되지 않았습니다. .env 파일을 확인해주세요.');
    throw new Error('API 설정이 올바르지 않습니다. 관리자에게 문의해주세요.');
  }

  try {
    const url = `${API_BASE_URL}/api/v1/chat`;
    console.log('📤 API Request:', {
      url,
      data: request
    });

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    console.log('📥 API Response Status:', response.status, response.statusText);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ API Error:', {
        status: response.status,
        statusText: response.statusText,
        error: errorText
      });
      throw new Error(`API 요청 실패: ${response.status} ${response.statusText}`);
    }

    const data: ChatResponse = await response.json();
    console.log('✅ API Response Data:', data);
    return data;
  } catch (error) {
    console.error('❌ Chat API Error:', error);
    throw new Error('서버와의 통신 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.');
  }
};

/**
 * 챗봇 API 상태를 확인합니다.
 */
export const checkChatApiHealth = async (): Promise<boolean> => {
  try {
    const healthUrl = `${API_BASE_URL}/api/v1/health`;
    console.log('🏥 Health Check URL:', healthUrl);
    const response = await fetch(healthUrl);
    console.log('🏥 Health Check Status:', response.status, response.statusText);
    return response.ok;
  } catch (error) {
    console.error('❌ Health Check Error:', error);
    return false;
  }
}; 