# 🎯 벡터 유사도 Threshold 조정 및 테스트 가이드

## 📋 개요

이 가이드는 챗봇의 벡터 유사도 임계값을 안전하게 조정하고 테스트하는 방법을 설명합니다.

## 🔍 현재 상태 확인

### 현재 Threshold 설정
- **기본값**: `0.65` (기존 0.7에서 조정)
- **설정 방법**: 환경변수 `VECTOR_SIMILARITY_THRESHOLD`
- **설정 파일**: `config/threshold_settings.example` 참조

## 🚀 로컬 테스트 방법

### 1️⃣ 환경 설정

```bash
# 1. 가상환경 활성화
source .venv/bin/activate

# 2. 환경변수 설정 (선택사항)
export VECTOR_SIMILARITY_THRESHOLD=0.65

# 또는 .env 파일에 추가:
echo "VECTOR_SIMILARITY_THRESHOLD=0.65" >> .env
```

### 2️⃣ Threshold 테스트 스크립트 실행

```bash
# 전체 threshold 분석 실행
PYTHONPATH=. python test_threshold.py
```

### 3️⃣ 개별 질문 테스트

```bash
# 특정 질문으로 테스트
PYTHONPATH=. python -c "
import asyncio
from scripts.query_runner import run_query

async def test():
    answer, results, is_fallback = await run_query(
        '체크인 시간이 언제인가요?',
        score_threshold=0.65
    )
    print(f'답변: {answer}')
    print(f'Fallback: {is_fallback}')
    if results:
        print(f'최고 점수: {results[0][1]:.3f}')

asyncio.run(test())
"
```

### 4️⃣ 백엔드 서버로 테스트

```bash
# 1. 백엔드 서버 실행
PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 2. API 테스트 (다른 터미널에서)
curl -X POST "http://localhost:8000/api/v1/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "체크인 시간이 언제인가요?"}'
```

## 📊 확인할 로그 및 메시지

### 콘솔 로그 예시

```bash
🎯 벡터 유사도 임계값: 0.65
🔍 유사도 검색 임계값: 0.65
📝 채팅 요청 받음: 체크인 시간이 언제인가요?
🔍 벡터 검색 완료: 2개 결과 (임계값: 0.65)
  1. 점수: 0.856 | 체크인(입실)은 오후 3시부터(15:00부터)입니다...
  2. 점수: 0.723 | 체크아웃(퇴실)은 다음날 오후 11시(11:00)입니다...
✅ 채팅 응답 완료: 45자
```

### 중요한 메트릭들

- **🎯 벡터 유사도 임계값**: 현재 설정된 threshold 값
- **🔍 벡터 검색 완료**: 검색된 문서 수와 점수
- **점수**: 각 문서의 유사도 점수 (0.0~1.0)
- **Fallback 여부**: 안전장치 작동 여부

## ⚙️ Threshold 조정 권장사항

### 🎯 권장 설정값

| Threshold | 응답률 | 안전성 | 사용 시기 |
|-----------|--------|--------|-----------|
| **0.65** | 75% | 보통 | **🎯 권장 (균형)** |
| 0.7 | 60% | 높음 | 안전성 우선 |
| 0.6 | 85% | 보통 | 응답률 우선 |
| 0.75 | 45% | 매우높음 | 초기 운영 |
| 0.55 | 90% | 낮음 | ⚠️ 위험 |

### 📈 단계적 조정 방법

1. **1단계**: 현재 `0.65`로 2주간 운영
2. **성과 확인**: Fallback 비율과 사용자 만족도 모니터링
3. **2단계**: 필요시 `0.6` 또는 `0.7`로 미세 조정
4. **안정화**: 최적값 확정 후 고정

## 🛡️ 안전장치 확인

### 다층 보안 시스템

1. **1차**: 벡터 유사도 필터링 (`score >= threshold`)
2. **2차**: GPT 응답 Fallback 감지 (11개 키워드)
3. **3차**: 프롬프트 레벨 제약 (명시적 지침)
4. **4차**: 실시간 모니터링 및 알림

### Fallback 감지 키워드

```python
FALLBACK_INDICATORS = [
    "정확한 안내가 어렵습니다",
    "자세한 정보는 없습니다",
    "명확하지 않습니다",
    "해당 정보는 제공되지 않습니다",
    # ... 총 11개
]
```

## 🔧 문제 해결

### 자주 발생하는 문제들

#### 1. 응답률이 너무 낮은 경우
```bash
# 해결: threshold 낮추기
export VECTOR_SIMILARITY_THRESHOLD=0.6
```

#### 2. 관련 없는 답변이 나오는 경우
```bash
# 해결: threshold 높이기  
export VECTOR_SIMILARITY_THRESHOLD=0.75
```

#### 3. 환경변수가 적용되지 않는 경우
```bash
# 확인: 현재 설정값 출력
PYTHONPATH=. python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('Threshold:', os.getenv('VECTOR_SIMILARITY_THRESHOLD', '0.65'))
"
```

## 📈 성능 모니터링

### 주요 지표

- **응답률**: (총 질문 - Fallback 수) / 총 질문 × 100
- **평균 유사도 점수**: 검색된 문서들의 평균 점수
- **Fallback 비율**: Fallback 응답 / 총 응답 × 100
- **사용자 만족도**: 실제 사용자 피드백

### 모니터링 도구

- **Slack 알림**: Fallback 발생시 즉시 알림
- **Google Sheets**: 모든 대화 로그 기록
- **콘솔 로그**: 실시간 성능 메트릭

## ⚠️ 주의사항

1. **운영 환경 적용 전 충분한 테스트 필요**
2. **0.5 이하로는 절대 설정하지 말 것**
3. **변경 후 최소 1주일간 모니터링**
4. **급격한 변경보다는 점진적 조정 권장**
5. **백업 계획 수립 (원래 값으로 롤백 가능)**

## 🎯 결론

- **권장 Threshold**: `0.65`
- **모니터링 기간**: 2주
- **조정 주기**: 월 1회 검토
- **안전 범위**: `0.55` ~ `0.8`

---

💡 **추가 문의사항이 있으시면 개발팀에게 연락해주세요!** 