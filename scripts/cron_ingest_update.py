import os
import time
from dotenv import load_dotenv
from datetime import datetime
from scripts.embed_runner import run_embedding
from scripts.slack_alert_manager import SlackAlertManager
from scripts.doc_change_detector import DocChangeDetector

# ✅ .env 로드
load_dotenv()

# ✅ 문서 경로 및 상태 저장 파일 경로
DOC_PATH = "docs/hotel_policy.txt"
STATE_FILE = "data/last_ingest_timestamp.txt"

# ✅ 문서 최종 수정 시간 확인
def get_last_modified_time(path: str) -> float:
    return os.path.getmtime(path)

# ✅ 이전 타임스탬프 로드
def load_previous_timestamp() -> float:
    try:
        with open(STATE_FILE, 'r') as f:
            return float(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 0.0

# ✅ 현재 타임스탬프 저장
def save_current_timestamp(timestamp: float) -> None:
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        f.write(str(timestamp))

# ✅ 변경 여부 감지 및 처리
def check_and_update_embedding():
    print("🔁 문서 변경 여부 확인 중...")

    last_modified = get_last_modified_time(DOC_PATH)
    previous_timestamp = load_previous_timestamp()

    print(f"📁 이전 업데이트 시각: {datetime.fromtimestamp(previous_timestamp)}")
    print(f"📁 현재 수정 시각: {datetime.fromtimestamp(last_modified)}")

    if last_modified > previous_timestamp:
        print("✅ 문서 변경 감지됨 → 임베딩 업데이트 시작")

        # 벡터 임베딩 재실행
        run_embedding(DOC_PATH)

        # 문서 변경 감지 및 키워드 추출
        detector = DocChangeDetector(DOC_PATH)
        updated_keywords, added_chunks, removed_chunks, modified_chunks, change_details = detector.detect_changes()

        # Slack Block Kit 알림 전송
        SlackAlertManager.send_doc_update_alert(
            file_path=DOC_PATH,
            updated_at=datetime.fromtimestamp(last_modified).strftime("%Y-%m-%d %H:%M:%S"),
            updated_keywords=updated_keywords,
            added_chunks=added_chunks,
            removed_chunks=removed_chunks,
            modified_chunks=modified_chunks,
            change_details=change_details
        )

        # 변경 시간 저장
        save_current_timestamp(last_modified)
    else:
        print("⏸ 변경 없음 → 업데이트 생략")

# ✅ 단독 실행 시
if __name__ == "__main__":
    check_and_update_embedding()