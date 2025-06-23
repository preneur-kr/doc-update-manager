# 🚀 Render 배포 가이드

이 문서는 Hotel Bot API를 Render에 배포하는 방법을 설명합니다.

## 📋 사전 준비사항

### 1. Render 계정
- [Render](https://render.com) 계정 생성
- GitHub 저장소 연결

### 2. 환경 변수 준비
다음 환경 변수들을 준비해주세요:

#### Slack 관련
- `SLACK_BOT_TOKEN`: Slack Bot User OAuth Token
- `SLACK_SIGNING_SECRET`: Slack App Signing Secret

#### Google Sheets 관련
- `GOOGLE_SHEET_ID`: Google Sheets 문서 ID
- `GOOGLE_CREDENTIALS_JSON`: Google Service Account credentials (JSON 문자열)

#### OpenAI 관련
- `OPENAI_API_KEY`: OpenAI API Key

#### Pinecone 관련
- `PINECONE_API_KEY`: Pinecone API Key
- `PINECONE_ENV`: Pinecone Environment
- `PINECONE_INDEX_NAME`: Pinecone Index Name

## 🔧 배포 단계

### 1단계: Google Credentials 설정

```bash
# Google Credentials를 JSON 문자열로 변환
python scripts/setup_render_env.py
```

이 스크립트를 실행하면 Google Service Account credentials 파일을 JSON 문자열로 변환하여 Render 환경 변수로 설정할 수 있습니다.

### 2단계: Render 프로젝트 생성

1. Render 대시보드에서 "New +" 클릭
2. "Web Service" 선택
3. GitHub 저장소 연결
4. 프로젝트 설정:
   - **Name**: `hotel-bot-api`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port 8000`

### 3단계: 환경 변수 설정

Render 대시보드의 "Environment" 탭에서 다음 환경 변수들을 설정:

#### 필수 환경 변수
```
GOOGLE_CREDENTIALS_JSON=<Google Service Account JSON 문자열>
SLACK_BOT_TOKEN=<Slack Bot Token>
SLACK_SIGNING_SECRET=<Slack Signing Secret>
GOOGLE_SHEET_ID=<Google Sheets ID>
OPENAI_API_KEY=<OpenAI API Key>
PINECONE_API_KEY=<Pinecone API Key>
PINECONE_ENV=<Pinecone Environment>
PINECONE_INDEX_NAME=<Pinecone Index Name>
```

#### 선택적 환경 변수 (기본값 있음)
```
SLACK_DEFAULT_CHANNEL=general
GOOGLE_DOC_LOG_SHEET_NAME=doc_update_logs
GOOGLE_CHAT_LOG_SHEET_NAME=chat_logs
GOOGLE_FALLBACK_LOG_SHEET_NAME=fallback_logs
ENVIRONMENT=production
```

### 4단계: 배포 및 확인

1. "Create Web Service" 클릭하여 배포 시작
2. 배포 완료 후 제공되는 URL 확인 (예: `https://hotel-bot-api.onrender.com`)
3. 다음 엔드포인트로 서비스 상태 확인:
   - `https://hotel-bot-api.onrender.com/` - 기본 상태
   - `https://hotel-bot-api.onrender.com/health` - 헬스 체크
   - `https://hotel-bot-api.onrender.com/ping` - 핑 테스트

### 5단계: Slack 설정 업데이트

1. [Slack API](https://api.slack.com/apps) 페이지로 이동
2. 해당 앱 선택
3. "Event Subscriptions" 섹션에서:
   - **Request URL**: `https://hotel-bot-api.onrender.com/api/v1/slack/events`
   - **Enable Events**: 활성화
4. "Interactivity & Shortcuts" 섹션에서:
   - **Request URL**: `https://hotel-bot-api.onrender.com/api/v1/slack/events`

## 🔍 배포 후 확인사항

### 1. 서비스 상태 확인
```bash
curl https://hotel-bot-api.onrender.com/health
```

### 2. Slack 이벤트 테스트
- Slack에서 봇에게 메시지 전송
- Google Sheets에 로그가 기록되는지 확인

### 3. 로그 확인
- Render 대시보드의 "Logs" 탭에서 애플리케이션 로그 확인
- 오류나 경고 메시지 확인

## 🛠️ 문제 해결

### 일반적인 문제들

#### 1. 환경 변수 누락
```
Missing required environment variables: GOOGLE_CREDENTIALS_JSON, SLACK_BOT_TOKEN
```
**해결**: Render 환경 변수에서 누락된 변수 추가

#### 2. Google Sheets 권한 오류
```
insufficient permission
```
**해결**: Google Sheets 문서에 서비스 계정 이메일을 편집자로 추가

#### 3. Slack 서명 검증 실패
```
Invalid Slack request signature
```
**해결**: `SLACK_SIGNING_SECRET` 환경 변수 확인

#### 4. Pinecone 연결 오류
```
Pinecone connection failed
```
**해결**: Pinecone API 키와 환경 설정 확인

### 로그 확인 방법

1. Render 대시보드 → 프로젝트 → "Logs" 탭
2. 실시간 로그 스트림 확인
3. 오류 메시지 분석

## 📞 지원

문제가 발생하면 다음을 확인해주세요:

1. Render 로그에서 오류 메시지
2. 환경 변수 설정 상태
3. Slack 앱 설정 상태
4. Google Sheets 권한 설정

## 🔄 업데이트 배포

코드 변경 후 자동 배포가 활성화되어 있으면 GitHub에 푸시하면 자동으로 배포됩니다.

수동 배포가 필요한 경우:
1. Render 대시보드에서 "Manual Deploy" 클릭
2. "Deploy latest commit" 선택 