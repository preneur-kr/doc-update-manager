#!/usr/bin/env python3
"""
Render 배포를 위한 환경 변수 설정 도우미 스크립트

이 스크립트는 Google Service Account credentials 파일을 JSON 문자열로 변환하여
Render 환경 변수로 설정할 수 있도록 도와줍니다.
"""

import json
import os
import sys
from pathlib import Path

def read_credentials_file(file_path: str) -> dict:
    """Google Service Account credentials 파일을 읽습니다."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ 파일을 찾을 수 없습니다: {file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ JSON 파싱 오류: {e}")
        return None

def main():
    print("🚀 Render 배포를 위한 환경 변수 설정 도우미")
    print("=" * 50)
    
    # 1. Google Credentials 파일 경로 확인
    credentials_path = input("Google Service Account credentials 파일 경로를 입력하세요 (예: credentials/service-account.json): ").strip()
    
    if not credentials_path:
        print("❌ 파일 경로를 입력해주세요.")
        return
    
    # 2. credentials 파일 읽기
    credentials_data = read_credentials_file(credentials_path)
    if not credentials_data:
        return
    
    # 3. JSON 문자열로 변환
    credentials_json = json.dumps(credentials_data, separators=(',', ':'))
    
    print("\n✅ Google Credentials 변환 완료!")
    print("=" * 50)
    print("📋 Render 환경 변수 설정 가이드:")
    print()
    print("1. Render 대시보드에서 프로젝트로 이동")
    print("2. 'Environment' 탭 클릭")
    print("3. 'Environment Variables' 섹션에서 다음 변수들을 추가:")
    print()
    print("🔑 GOOGLE_CREDENTIALS_JSON")
    print("값: (아래 JSON 문자열을 복사하여 붙여넣기)")
    print("-" * 30)
    print(credentials_json)
    print("-" * 30)
    print()
    print("📝 기타 필요한 환경 변수들:")
    print("• SLACK_BOT_TOKEN")
    print("• SLACK_SIGNING_SECRET") 
    print("• GOOGLE_SHEET_ID")
    print("• OPENAI_API_KEY")
    print("• PINECONE_API_KEY")
    print("• PINECONE_ENV")
    print("• PINECONE_INDEX_NAME")
    print()
    print("⚠️  주의사항:")
    print("• JSON 문자열에 줄바꿈이나 공백이 포함되지 않도록 주의하세요")
    print("• 환경 변수 설정 후 서비스를 재배포해야 합니다")
    print("• Slack Request URL을 Render 주소로 업데이트해야 합니다")

if __name__ == "__main__":
    main() 