#!/usr/bin/env python3
"""
🎯 벡터 유사도 Threshold 테스트 스크립트

이 스크립트는 다양한 threshold 값으로 챗봇의 응답을 테스트합니다.
환각(hallucination) 방지와 응답률의 균형을 찾는 데 도움이 됩니다.
"""

import os
import asyncio
import sys
from dotenv import load_dotenv

# 현재 디렉터리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.query_runner import run_query

# 환경변수 로드
load_dotenv()

# 🎯 테스트할 threshold 값들
TEST_THRESHOLDS = [0.8, 0.75, 0.7, 0.65, 0.6, 0.55, 0.5]

# 📝 테스트 질문들 (다양한 난이도)
TEST_QUESTIONS = [
    {
        "question": "체크인 시간이 언제인가요?",
        "expected": "정확한 답변 가능",  # 문서에 명시된 내용
        "difficulty": "쉬움"
    },
    {
        "question": "반려동물과 함께 투숙할 수 있나요?",
        "expected": "정확한 답변 가능",  # 문서에 명시된 내용
        "difficulty": "쉬움"
    },
    {
        "question": "늦은 체크아웃 요금은 얼마인가요?",
        "expected": "정확한 답변 가능",  # 문서에 명시된 내용  
        "difficulty": "보통"
    },
    {
        "question": "호텔 주변에 맛집이 있나요?",
        "expected": "fallback 응답",  # 문서에 없는 내용
        "difficulty": "어려움"
    },
    {
        "question": "조식 메뉴는 어떻게 되나요?",
        "expected": "부분적 답변 또는 fallback",  # 조식 제공은 명시되어 있지만 메뉴는 없음
        "difficulty": "보통"
    },
    {
        "question": "와이파이 비밀번호가 뭔가요?",
        "expected": "fallback 응답",  # 문서에 없는 내용
        "difficulty": "어려움"
    }
]

async def test_threshold(threshold: float):
    """특정 threshold로 모든 테스트 질문 실행"""
    print(f"\n{'='*50}")
    print(f"🎯 THRESHOLD: {threshold}")
    print(f"{'='*50}")
    
    results = []
    
    for i, test_case in enumerate(TEST_QUESTIONS, 1):
        question = test_case["question"]
        expected = test_case["expected"]
        difficulty = test_case["difficulty"]
        
        print(f"\n📝 테스트 {i}: {question}")
        print(f"   난이도: {difficulty} | 예상: {expected}")
        print("-" * 50)
        
        try:
            # 질문 실행
            answer, search_results, is_fallback = await run_query(
                question=question,
                score_threshold=threshold
            )
            
            # 결과 분석
            result_type = "fallback" if is_fallback else "정상 응답"
            score_info = f"최고점수: {search_results[0][1]:.3f}" if search_results else "검색결과 없음"
            
            print(f"✅ 응답: {result_type}")
            print(f"📊 {score_info}")
            print(f"🗣️ 답변: {answer[:100]}{'...' if len(answer) > 100 else ''}")
            
            # 결과 저장
            results.append({
                "question": question,
                "answer": answer,
                "is_fallback": is_fallback,
                "search_results": len(search_results),
                "top_score": search_results[0][1] if search_results else 0,
                "difficulty": difficulty,
                "expected": expected
            })
            
        except Exception as e:
            print(f"❌ 오류: {str(e)}")
            results.append({
                "question": question,
                "error": str(e),
                "is_fallback": True,
                "search_results": 0,
                "top_score": 0,
                "difficulty": difficulty,
                "expected": expected
            })
    
    return results

async def run_threshold_analysis():
    """모든 threshold에 대해 테스트 실행 및 분석"""
    print("🚀 벡터 유사도 Threshold 분석 시작")
    print("=" * 60)
    
    all_results = {}
    
    for threshold in TEST_THRESHOLDS:
        results = await test_threshold(threshold)
        all_results[threshold] = results
    
    # 결과 요약 분석
    print(f"\n{'='*60}")
    print("📊 THRESHOLD 분석 요약")
    print(f"{'='*60}")
    
    print(f"{'Threshold':<10} {'응답율':<8} {'Fallback율':<10} {'평균점수':<10} {'안전성':<8}")
    print("-" * 50)
    
    for threshold in TEST_THRESHOLDS:
        results = all_results[threshold]
        total_questions = len(results)
        fallback_count = sum(1 for r in results if r.get('is_fallback', True))
        response_rate = ((total_questions - fallback_count) / total_questions) * 100
        fallback_rate = (fallback_count / total_questions) * 100
        
        # 평균 점수 계산 (오류가 없는 경우만)
        valid_scores = [r['top_score'] for r in results if 'error' not in r and r['top_score'] > 0]
        avg_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0
        
        # 안전성 평가 (간단한 휴리스틱)
        safety = "높음" if threshold >= 0.7 else "보통" if threshold >= 0.6 else "낮음"
        
        print(f"{threshold:<10} {response_rate:<7.1f}% {fallback_rate:<9.1f}% {avg_score:<9.3f} {safety:<8}")
    
    # 권장사항
    print(f"\n{'='*60}")
    print("💡 권장사항")
    print(f"{'='*60}")
    
    print("🎯 권장 Threshold: 0.65")
    print("   - 적절한 응답률과 안전성의 균형")
    print("   - 환각 위험 최소화")
    print("   - 사용자 만족도 고려")
    
    print("\n⚠️ 주의사항:")
    print("   - 0.6 이하: 관련 없는 답변 위험 증가")
    print("   - 0.75 이상: 응답률 크게 감소")
    print("   - 실제 운영 전 충분한 테스트 필요")

def main():
    """메인 실행 함수"""
    if __name__ == "__main__":
        try:
            # 비동기 실행
            asyncio.run(run_threshold_analysis())
        except KeyboardInterrupt:
            print("\n\n⏹️ 테스트가 중단되었습니다.")
        except Exception as e:
            print(f"\n❌ 테스트 실행 중 오류: {str(e)}")

# 스크립트 직접 실행 시
if __name__ == "__main__":
    main() 