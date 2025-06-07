import unittest
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.answer_guard import is_fallback_like_response

class TestAnswerGuard(unittest.TestCase):
    """answer_guard 모듈의 fallback-like 응답 감지 기능을 테스트합니다."""

    def test_fallback_like_responses(self):
        """fallback-like 응답을 감지하는 테스트 케이스들입니다."""
        
        # True를 반환해야 하는 fallback-like 응답들
        fallback_cases = [
            {
                "name": "기본 fallback 문구",
                "answer": "죄송합니다. 해당 내용에 대해 정확한 안내가 어렵습니다."
            },
            {
                "name": "시간 정보 부재",
                "answer": "문서에 명확한 시간 정보가 없어 정확한 안내가 어렵습니다."
            },
            {
                "name": "복합 fallback 문구",
                "answer": "해당 정보는 제공되지 않으며, 문서에서도 확인할 수 없습니다."
            }
        ]

        # False를 반환해야 하는 정상 응답들
        normal_cases = [
            {
                "name": "정확한 시간 정보",
                "answer": "체크인은 오후 5시부터 가능합니다."
            },
            {
                "name": "정책 안내",
                "answer": "예약인원 외 추가 인원 출입 시 이유 불문 강제 퇴실 조치됩니다."
            },
            {
                "name": "일반적인 안내",
                "answer": "조식 서비스는 아침 8시부터 10시까지 공용공간에서 제공됩니다."
            }
        ]

        # Fallback-like 응답 테스트
        for case in fallback_cases:
            with self.subTest(case=case["name"]):
                self.assertTrue(
                    is_fallback_like_response(case["answer"]),
                    f"Fallback-like 응답이 감지되지 않았습니다: {case['answer']}"
                )

        # 정상 응답 테스트
        for case in normal_cases:
            with self.subTest(case=case["name"]):
                self.assertFalse(
                    is_fallback_like_response(case["answer"]),
                    f"정상 응답이 fallback-like로 잘못 감지되었습니다: {case['answer']}"
                )

if __name__ == '__main__':
    unittest.main(verbosity=2) 