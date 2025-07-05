#!/usr/bin/env python3
"""
배포 후 자동 검증 스크립트
Usage: python test_deployment.py
"""

import requests
import json
import time
from typing import Dict, Any, List, Tuple
import sys

# 설정
BASE_URL = "https://doc-update-manager.onrender.com"
TIMEOUT = 60  # 채팅 엔드포인트는 OpenAI API 호출로 인해 더 오래 걸릴 수 있음
TEST_RESULTS: List[Tuple[str, bool, str]] = []

def log_test(test_name: str, passed: bool, message: str = ""):
    """테스트 결과 로깅"""
    status = "✅ PASS" if passed else "❌ FAIL"
    TEST_RESULTS.append((test_name, passed, message))
    print(f"{status} {test_name}: {message}")

def test_health_endpoints():
    """헬스 체크 엔드포인트 테스트"""
    print("\n🔍 1. API 동작 검증")
    
    # 기본 헬스 체크
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
        log_test("기본 헬스 체크", response.status_code == 200, f"Status: {response.status_code}")
    except Exception as e:
        log_test("기본 헬스 체크", False, f"Error: {str(e)}")
    
    # API 헬스 체크
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health", timeout=TIMEOUT)
        log_test("API 헬스 체크", response.status_code == 200, f"Status: {response.status_code}")
    except Exception as e:
        log_test("API 헬스 체크", False, f"Error: {str(e)}")
    
    # OpenAPI 문서
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=TIMEOUT)
        log_test("OpenAPI 문서", response.status_code == 200, f"Status: {response.status_code}")
    except Exception as e:
        log_test("OpenAPI 문서", False, f"Error: {str(e)}")

def test_chat_endpoint():
    """채팅 엔드포인트 테스트"""
    # 정상 요청
    try:
        payload = {
            "message": "안녕하세요. 테스트 메시지입니다.",
            "session_id": "test-session-123"
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/chat",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            # 응답 구조: {"answer": "...", "is_fallback": false, "timestamp": "...", "search_results": [...]}
            has_answer = "answer" in data and data["answer"]
            has_search_results = "search_results" in data and isinstance(data["search_results"], list)
            
            if has_answer:
                log_test("채팅 엔드포인트 정상 요청", True, f"응답 길이: {len(data['answer'])}, 검색 결과: {len(data.get('search_results', []))}")
            else:
                log_test("채팅 엔드포인트 정상 요청", False, f"응답 구조: {list(data.keys())}")
        else:
            log_test("채팅 엔드포인트 정상 요청", False, f"Status: {response.status_code}")
            
    except Exception as e:
        log_test("채팅 엔드포인트 정상 요청", False, f"Error: {str(e)}")

def test_error_cases():
    """에러 케이스 테스트"""
    print("\n🔍 3. 에러 케이스 테스트")
    
    # 404 테스트
    try:
        response = requests.get(f"{BASE_URL}/nonexistent-endpoint", timeout=TIMEOUT)
        log_test("404 Not Found", response.status_code == 404, f"Status: {response.status_code}")
    except Exception as e:
        log_test("404 Not Found", False, f"Error: {str(e)}")
    
    # 잘못된 JSON 요청
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/chat",
            data="invalid json",
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT
        )
        log_test("잘못된 JSON 처리", response.status_code in [400, 422], f"Status: {response.status_code}")
    except Exception as e:
        log_test("잘못된 JSON 처리", False, f"Error: {str(e)}")
    
    # 필수 필드 누락
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/chat",
            json={},  # 빈 객체
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT
        )
        log_test("필수 필드 누락 처리", response.status_code in [400, 422], f"Status: {response.status_code}")
    except Exception as e:
        log_test("필수 필드 누락 처리", False, f"Error: {str(e)}")

def test_cors_headers():
    """CORS 헤더 테스트"""
    print("\n🔍 2. CORS 정책 테스트")
    
    try:
        # OPTIONS 요청 (Preflight)
        response = requests.options(
            f"{BASE_URL}/api/v1/chat",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            },
            timeout=TIMEOUT
        )
        
        cors_headers = {
            "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
            "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
            "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers")
        }
        
        has_cors = any(cors_headers.values())
        log_test("CORS Preflight 요청", has_cors, f"CORS 헤더: {bool(has_cors)}")
        
    except Exception as e:
        log_test("CORS Preflight 요청", False, f"Error: {str(e)}")

def test_response_format():
    """응답 형식 테스트"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
        
        # Content-Type 확인
        content_type = response.headers.get("Content-Type", "")
        is_json = "application/json" in content_type
        log_test("JSON 응답 형식", is_json, f"Content-Type: {content_type}")
        
        # JSON 파싱 가능 여부
        try:
            response.json()
            log_test("JSON 파싱 가능", True, "응답이 유효한 JSON")
        except:
            log_test("JSON 파싱 가능", False, "JSON 파싱 실패")
            
    except Exception as e:
        log_test("응답 형식 테스트", False, f"Error: {str(e)}")

def test_performance():
    """성능 테스트"""
    print("\n🔍 6. 성능 테스트")
    
    try:
        start_time = time.time()
        response = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
        end_time = time.time()
        
        response_time = end_time - start_time
        is_fast = response_time < 5.0  # 5초 이내
        
        log_test("응답 시간", is_fast, f"{response_time:.2f}초")
        
    except Exception as e:
        log_test("응답 시간", False, f"Error: {str(e)}")

def print_summary():
    """테스트 결과 요약"""
    print("\n" + "="*60)
    print("📊 테스트 결과 요약")
    print("="*60)
    
    total_tests = len(TEST_RESULTS)
    passed_tests = sum(1 for _, passed, _ in TEST_RESULTS if passed)
    failed_tests = total_tests - passed_tests
    
    print(f"총 테스트: {total_tests}")
    print(f"✅ 성공: {passed_tests}")
    print(f"❌ 실패: {failed_tests}")
    print(f"성공률: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests > 0:
        print("\n❌ 실패한 테스트:")
        for test_name, passed, message in TEST_RESULTS:
            if not passed:
                print(f"  - {test_name}: {message}")
    
    print("\n" + "="*60)
    return failed_tests == 0

def main():
    """메인 실행 함수"""
    print("🚀 배포 후 자동 검증 시작")
    print(f"대상 URL: {BASE_URL}")
    print("="*60)
    
    # 테스트 실행
    test_health_endpoints()
    test_response_format()
    test_cors_headers()
    test_chat_endpoint()
    test_error_cases()
    test_performance()
    
    # 결과 요약
    success = print_summary()
    
    # 종료 코드
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 