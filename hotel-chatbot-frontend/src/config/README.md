# 환경변수 설정 가이드

## 개요
이 애플리케이션은 환경변수를 통해 다양한 설정을 관리합니다. 모든 환경변수는 기본값이 설정되어 있어 즉시 사용 가능합니다.

## 환경변수 설정 방법

### 1. .env 파일 생성
프로젝트 루트에 `.env` 파일을 생성하여 환경변수를 설정할 수 있습니다:

```bash
# hotel-chatbot-frontend/.env
VITE_API_BASE_URL=https://your-api-server.com
VITE_HOTEL_NAME=Your Hotel Name
```

### 2. 배포 환경에서 설정
Render, Vercel, Netlify 등의 배포 플랫폼에서 환경변수를 직접 설정할 수 있습니다.

## 환경변수 목록

### API 설정
| 변수명 | 기본값 | 설명 |
|--------|--------|------|
| `VITE_API_BASE_URL` | `https://doc-update-manager.onrender.com` | 백엔드 API 기본 URL |
| `VITE_API_TIMEOUT_QUICK` | `5000` | 빠른 API 타임아웃 (ms) |
| `VITE_API_TIMEOUT_HEALTH` | `8000` | 헬스체크 타임아웃 (ms) |
| `VITE_API_TIMEOUT_EXTENDED` | `6000` | 확장 타임아웃 (ms) |
| `VITE_API_RETRY_COUNT` | `4` | API 재시도 횟수 |
| `VITE_API_RETRY_DELAY` | `1000` | 재시도 지연시간 (ms) |
| `VITE_API_RETRY_DELAY_EXTENDED` | `1500` | 확장 재시도 지연시간 (ms) |
| `VITE_API_HEALTH_CHECK_INTERVAL` | `30000` | 헬스체크 간격 (ms) |
| `VITE_API_RECONNECT_DELAY` | `1000` | 재연결 지연시간 (ms) |

### UI 설정
| 변수명 | 기본값 | 설명 |
|--------|--------|------|
| `VITE_MAX_MESSAGE_LENGTH` | `1000` | 메시지 최대 길이 |
| `VITE_TEXTAREA_MAX_HEIGHT` | `120` | 텍스트 입력창 최대 높이 (px) |
| `VITE_TOAST_DEFAULT_DURATION` | `4000` | 토스트 기본 표시시간 (ms) |
| `VITE_TOAST_MAX_COUNT` | `3` | 최대 토스트 개수 |
| `VITE_STREAMING_TEXT_SPEED` | `30` | 스트리밍 텍스트 속도 (ms) |
| `VITE_STREAMING_TEXT_START_DELAY` | `300` | 스트리밍 시작 지연 (ms) |
| `VITE_LINK_MAX_COUNT_PER_LINE` | `10` | 줄당 최대 링크 수 |
| `VITE_QUICK_REPLIES_THRESHOLD` | `2` | 빠른 답변 표시 임계값 |
| `VITE_AUTO_SCROLL_THRESHOLD` | `20` | 자동 스크롤 임계값 (px) |
| `VITE_SCROLL_BEHAVIOR_DELAY` | `100` | 스크롤 동작 지연 (ms) |

### 스토리지 설정
| 변수명 | 기본값 | 설명 |
|--------|--------|------|
| `VITE_STORAGE_KEY` | `hotel-chatbot-history-v2` | 로컬스토리지 키 |
| `VITE_MAX_MESSAGES` | `50` | 최대 저장 메시지 수 |

### 호텔 정보 설정
| 변수명 | 기본값 | 설명 |
|--------|--------|------|
| `VITE_HOTEL_NAME` | `서정적인 호텔` | 호텔 이름 |
| `VITE_HOTEL_SUBTITLE` | `AI가 바로 답변해 드려요` | 서브타이틀 |
| `VITE_WELCOME_MESSAGE` | (긴 메시지) | 웰컴 메시지 |

### 디버그 설정
| 변수명 | 기본값 | 설명 |
|--------|--------|------|
| `VITE_ENABLE_DEBUG_FUNCTIONS` | `true` (개발), `false` (프로덕션) | 디버그 함수 활성화 |

## 사용 방법

### 코드에서 사용
```typescript
import { CONFIG } from '@/config/env';

// API 설정 사용
const apiUrl = CONFIG.API.BASE_URL;
const timeout = CONFIG.API.TIMEOUT_QUICK;

// UI 설정 사용
const maxLength = CONFIG.UI.MAX_MESSAGE_LENGTH;
const hotelName = CONFIG.HOTEL.NAME;
```

### 타입 안전성
모든 설정은 TypeScript로 타입이 정의되어 있어 안전하게 사용할 수 있습니다.

### 기본값 보장
환경변수가 설정되지 않은 경우에도 적절한 기본값이 제공되어 애플리케이션이 정상 작동합니다.

## 배포 시 주의사항

1. **VITE_ 접두사**: Vite에서 클라이언트에 노출되는 환경변수는 반드시 `VITE_` 접두사가 필요합니다.

2. **보안**: 민감한 정보(API 키, 비밀번호 등)는 클라이언트 환경변수에 포함하지 마세요.

3. **빌드 시점**: 환경변수는 빌드 시점에 번들에 포함되므로, 배포 후 변경하려면 재빌드가 필요합니다.

## 예시 .env 파일

```bash
# .env
VITE_API_BASE_URL=https://your-production-api.com
VITE_HOTEL_NAME=Grand Hotel
VITE_HOTEL_SUBTITLE=Premium AI Service
VITE_MAX_MESSAGE_LENGTH=2000
VITE_TOAST_DEFAULT_DURATION=5000
``` 