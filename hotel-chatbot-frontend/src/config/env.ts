// 🔧 환경변수 관리 및 기본값 설정
// 프로덕션에서는 .env 파일이나 배포 환경에서 오버라이드 가능

/**
 * API 관련 설정
 */
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'https://doc-update-manager.onrender.com',
  TIMEOUT_QUICK: Number(import.meta.env.VITE_API_TIMEOUT_QUICK) || 5000,
  TIMEOUT_HEALTH: Number(import.meta.env.VITE_API_TIMEOUT_HEALTH) || 8000,
  TIMEOUT_EXTENDED: Number(import.meta.env.VITE_API_TIMEOUT_EXTENDED) || 6000,
  RETRY_COUNT: Number(import.meta.env.VITE_API_RETRY_COUNT) || 4,
  RETRY_DELAY: Number(import.meta.env.VITE_API_RETRY_DELAY) || 1000,
  RETRY_DELAY_EXTENDED: Number(import.meta.env.VITE_API_RETRY_DELAY_EXTENDED) || 1500,
  HEALTH_CHECK_INTERVAL: Number(import.meta.env.VITE_API_HEALTH_CHECK_INTERVAL) || 30000,
  RECONNECT_DELAY: Number(import.meta.env.VITE_API_RECONNECT_DELAY) || 1000,
} as const;

/**
 * UI 관련 설정
 */
export const UI_CONFIG = {
  MAX_MESSAGE_LENGTH: Number(import.meta.env.VITE_MAX_MESSAGE_LENGTH) || 1000,
  TEXTAREA_MAX_HEIGHT: Number(import.meta.env.VITE_TEXTAREA_MAX_HEIGHT) || 120,
  TOAST_DEFAULT_DURATION: Number(import.meta.env.VITE_TOAST_DEFAULT_DURATION) || 4000,
  TOAST_MAX_COUNT: Number(import.meta.env.VITE_TOAST_MAX_COUNT) || 3,
  STREAMING_TEXT_SPEED: Number(import.meta.env.VITE_STREAMING_TEXT_SPEED) || 30,
  STREAMING_TEXT_START_DELAY: Number(import.meta.env.VITE_STREAMING_TEXT_START_DELAY) || 300,
  LINK_MAX_COUNT_PER_LINE: Number(import.meta.env.VITE_LINK_MAX_COUNT_PER_LINE) || 10,
  QUICK_REPLIES_THRESHOLD: Number(import.meta.env.VITE_QUICK_REPLIES_THRESHOLD) || 2,
  AUTO_SCROLL_THRESHOLD: Number(import.meta.env.VITE_AUTO_SCROLL_THRESHOLD) || 20,
  SCROLL_BEHAVIOR_DELAY: Number(import.meta.env.VITE_SCROLL_BEHAVIOR_DELAY) || 100,
} as const;

/**
 * 스토리지 관련 설정
 */
export const STORAGE_CONFIG = {
  CHAT_HISTORY_KEY: import.meta.env.VITE_STORAGE_KEY || 'hotel-chatbot-history-v2',
  MAX_MESSAGES: Number(import.meta.env.VITE_MAX_MESSAGES) || 50,
} as const;

/**
 * 호텔 정보 설정
 */
export const HOTEL_CONFIG = {
  NAME: import.meta.env.VITE_HOTEL_NAME || '서정적인 호텔',
  SUBTITLE: import.meta.env.VITE_HOTEL_SUBTITLE || 'AI가 바로 답변해 드려요',
  WELCOME_MESSAGE: import.meta.env.VITE_WELCOME_MESSAGE || 
    '🏨 서정적인 호텔 고객센터 💬\n\n안녕하세요, 고객님! 😊\n\n투숙하시는 동안 불편한 점이나 궁금한 점이 있으신가요? 필요한 서비스나 문의사항이 있으시면 언제든 말씀해주세요.\n\n🚀 자주 문의하시는 내용이라면?\n아래 버튼을 눌러 바로 확인해보세요!',
} as const;

/**
 * 디버그 관련 설정
 */
export const DEBUG_CONFIG = {
  ENABLE_DEBUG_FUNCTIONS: import.meta.env.VITE_ENABLE_DEBUG_FUNCTIONS === 'true' || import.meta.env.DEV,
} as const;

/**
 * 전체 설정 객체 (타입 안전성을 위한 통합)
 */
export const CONFIG = {
  API: API_CONFIG,
  UI: UI_CONFIG,
  STORAGE: STORAGE_CONFIG,
  HOTEL: HOTEL_CONFIG,
  DEBUG: DEBUG_CONFIG,
} as const;

// 개발 환경에서 설정 정보 출력
if (import.meta.env.DEV) {
  console.log('🔧 환경설정 로딩 완료:', CONFIG);
} 