#!/usr/bin/env python3
"""
로컬과 프로덕션 환경의 프롬프트 비교 스크립트
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.query_runner import load_prompt_template, DEFAULT_PROMPT_TEMPLATE

def compare_prompts():
    print("🔍 프롬프트 환경 비교 분석")
    print("=" * 60)
    
    # 1. 현재 로드되는 프롬프트
    current_prompt = load_prompt_template()
    
    # 2. DEFAULT_PROMPT_TEMPLATE과 비교
    file_prompt_path = "prompts/prompt_hotel_policy.txt"
    
    print(f"📁 프롬프트 파일 경로: {file_prompt_path}")
    print(f"📂 파일 존재 여부: {os.path.exists(file_prompt_path)}")
    
    if os.path.exists(file_prompt_path):
        with open(file_prompt_path, 'r', encoding='utf-8') as f:
            file_prompt = f.read()
        print(f"📄 파일 프롬프트 길이: {len(file_prompt)}자")
        print(f"🏷️  현재 사용 프롬프트 길이: {len(current_prompt)}자")
        
        # 같은지 확인
        if file_prompt.strip() == current_prompt.strip():
            print("✅ 파일 프롬프트를 사용 중")
            prompt_source = "FILE"
        else:
            print("❌ 다른 프롬프트 사용 중")
            prompt_source = "UNKNOWN"
    else:
        print("⚠️  파일이 없어 DEFAULT_PROMPT_TEMPLATE 사용")
        prompt_source = "DEFAULT"
    
    # DEFAULT와 비교
    if DEFAULT_PROMPT_TEMPLATE.strip() == current_prompt.strip():
        print("🔄 DEFAULT_PROMPT_TEMPLATE과 일치")
        if prompt_source == "UNKNOWN":
            prompt_source = "DEFAULT"
    else:
        print("🔄 DEFAULT_PROMPT_TEMPLATE과 다름")
    
    print(f"\n🎯 최종 판정: {prompt_source} 프롬프트 사용 중")
    
    print("\n📝 현재 사용 중인 프롬프트:")
    print("-" * 40)
    print(current_prompt)
    print("-" * 40)
    
    print(f"\n🏷️  언어: {'영어' if 'English' in current_prompt or 'hotel concierge' in current_prompt else '한국어'}")
    print(f"🎨 스타일: {'공식적' if 'professional' in current_prompt.lower() else '친근함'}")
    print(f"📏 길이: {len(current_prompt)}자")

if __name__ == "__main__":
    compare_prompts()
