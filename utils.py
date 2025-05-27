import json
import os
import datetime # datetime은 dday_cog 등 다른 곳에서 사용될 수 있으므로 유지합니다.

# 데이터 파일 경로
DATA_FILE = "misobot_data.json"

# 데이터 파일이 없으면 빈 JSON 객체로 생성
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", encoding='utf-8') as f: # encoding 추가
        json.dump({}, f)


def load_data():
    # 데이터 파일 읽기
    try:
        with open(DATA_FILE, "r", encoding='utf-8') as f: # encoding 추가
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"데이터 로드 오류: {e}. 빈 데이터 반환.")
        return {}


def save_data(data):
    # 데이터 파일 저장
    with open(DATA_FILE, "w", encoding='utf-8') as f: # encoding 추가
        json.dump(data, f, indent=4, ensure_ascii=False) # indent=4로 가독성 향상, ensure_ascii=False로 한글 유지


def get_user_data(user_id):
    # 사용자 데이터 가져오기/초기화 (dday, sm_messages 필드만 주로 관리)
    data = load_data()
    user_id_str = str(user_id) # 사용자 ID를 문자열로 일관되게 사용
    user_data = data.setdefault(user_id_str, {}) # 사용자 기본 노드가 없으면 생성

    migrated = False # 데이터 구조 변경으로 인해 저장 필요 여부 플래그

    # 'sm_messages' 필드 확인 및 초기화 (sm_cog.py에서 사용)
    if "sm_messages" not in user_data or not isinstance(user_data.get("sm_messages"), list):
        user_data["sm_messages"] = []
        migrated = True

    # 'dday' 필드 확인 및 초기화 (dday_cog.py에서 사용)
    if "dday" not in user_data or not isinstance(user_data.get("dday"), list):
        user_data["dday"] = []
        migrated = True

    # --- 아래 필드들은 타이머/투두 기능 제거로 인해 데이터 파일에서 정리 ---
    # 해당 필드들이 존재하면 삭제하여 더 이상 사용하지 않음을 명시하고 데이터 파일을 깔끔하게 유지
    fields_to_remove = ["items", "timers", "todo", "done", "activities"]
    for field in fields_to_remove:
        if field in user_data:
            del user_data[field]
            migrated = True
            print(f"User {user_id_str}: 이전 필드 '{field}' 삭제됨.")

    if migrated:
        # data[user_id_str] = user_data # setdefault로 이미 user_data는 data의 일부를 참조하므로 이 줄은 불필요
        save_data(data) # 변경 사항이 있을 경우에만 전체 데이터 저장

    return user_data

# check_and_reset_daily_activities 함수는 타이머/투두 기능과 함께 제거되었습니다.
# format_time 함수는 타이머 기능과 함께 제거되었습니다.