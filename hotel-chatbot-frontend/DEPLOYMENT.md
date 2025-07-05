# 호텔 챗봇 프론트엔드 배포 가이드

## 🚀 Render 배포 방법

### 1. GitHub 저장소 연결
1. [Render 대시보드](https://dashboard.render.com)에 로그인
2. "New +" → "Static Site" 선택
3. GitHub 저장소 연결 (hotel-chatbot-frontend)

### 2. 배포 설정
- **Name**: `hotel-chatbot-frontend`
- **Branch**: `main`
- **Root Directory**: `hotel-chatbot-frontend`
- **Build Command**: `npm ci && npm run build`
- **Publish Directory**: `dist`

### 3. 환경 변수 설정
```
VITE_API_BASE_URL=https://doc-update-manager.onrender.com
VITE_APP_ENV=production
```

### 4. 배포 후 확인사항
- [ ] 챗봇 기본 기능 테스트
- [ ] 모바일 반응형 확인
- [ ] PWA 설치 테스트
- [ ] API 연동 확인

## 🔧 배포 문제 해결 이력

### v1.0.1 - TypeScript 빌드 오류 수정 (2024-12-19)
**문제**: Render에서 TypeScript 빌드 실패
**원인**: `verbatimModuleSyntax: true` 설정으로 인한 엄격한 import/export 검증
**해결**: 
- `tsconfig.app.json`에서 `verbatimModuleSyntax: false`로 변경
- `chatApi.ts`에서 타입 export 명시적으로 정리
- 순환 참조 가능성 제거

**변경 파일**:
- `tsconfig.app.json`: verbatimModuleSyntax 비활성화
- `src/api/chatApi.ts`: 타입 export 구조 개선

## 🔧 로컬 개발 환경

### 설치 및 실행
```bash
npm install
npm run dev
```

### 빌드 테스트
```bash
npm run build
npm run preview
```

## 📱 기능 목록

### ✅ 완료된 기능
- 실시간 채팅 인터페이스
- 호텔 정책 질의응답
- 빠른 답변 버튼 (FAQ 6개)
- 모바일 최적화 (터치, 뷰포트)
- PWA 지원 (설치 가능)
- 대화 히스토리 저장
- 타이핑 인디케이터
- 토스트 알림
- 접근성 최적화

### 🎨 디자인 특징
- 라이트 모드 전용 디자인
- 호텔 브랜딩 컬러 (블루 계열)
- 부드러운 애니메이션
- 모바일 우선 반응형
- 터치 친화적 UI

## 🌐 배포 URL
- **예상 URL**: `https://hotel-chatbot-frontend.onrender.com`
- **백엔드 API**: `https://doc-update-manager.onrender.com`

## 📋 QR 코드 생성
배포 완료 후 QR 코드를 생성하여 모바일 접속을 편리하게 할 수 있습니다.

## 🐛 트러블슈팅

### TypeScript 빌드 오류
- **증상**: `verbatimModuleSyntax` 관련 오류
- **해결**: `tsconfig.app.json`에서 해당 옵션 비활성화

### API 연동 오류
- **증상**: CORS 또는 네트워크 오류
- **해결**: 환경 변수 `VITE_API_BASE_URL` 확인

### 모바일 렌더링 문제
- **증상**: 뷰포트 또는 터치 반응 이상
- **해결**: 브라우저 캐시 삭제 후 재접속 