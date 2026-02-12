import os
import json
import hashlib
from datetime import datetime
import shutil

# ===== KHÓA CỨNG VÙNG CẤM =====
ALLOWED_FOLDERS = ['SUC_KHOE', 'CHAM_SOC_GIA_DINH', 'LAP_TRINH_ROBOT']
FORBIDDEN_KEYWORDS = ['mobile', 'store', 'appstore', 'playstore']

DUPLICATE_LOG = 'duplicate_log.json'
CALENDAR_LOG = 'calendar_event_log.json'


def assert_safe_path(path: str):
    p = path.lower()
    for k in FORBIDDEN_KEYWORDS:
        if k in p:
            raise RuntimeError(f"⛔ VÙNG CẤM: {path}")


def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def hash_html(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def calendar_readonly_status(content_hash, calendar_log):
    info = calendar_log.get(content_hash)
    if not info:
        return "NOT_IN_CALENDAR"
    return info.get("display_status", "UNKNOWN")


def main():
    print("🤖 Robot dedup HTML khởi động")

    duplicate_log = load_json(DUPLICATE_LOG)
    calendar_log = load_json(CALENDAR_LOG)

    for folder in ALLOWED_FOLDERS:
        assert_safe_path(folder)
        os.makedirs(folder, exist_ok=True)

    for filename in os.listdir('.'):
        assert_safe_path(filename)

        if not filename.lower().endswith('.html'):
            continue
        if not os.path.isfile(filename):
            continue

        with open(filename, 'rb') as f:
            content = f.read()

        content_hash = hash_html(content)

        # === CHECK TRÙNG ===
        if content_hash in duplicate_log:
            print(f"🔁 Trùng nội dung: {filename} → bỏ qua")
            continue

        now = datetime.now().isoformat()

        duplicate_log[content_hash] = {
            "filename": filename,
            "first_seen": now
        }

        calendar_log.setdefault(content_hash, {
            "display_status": "READY",
            "created_at": now
        })

        status = calendar_readonly_status(content_hash, calendar_log)
        print(f"📅 Calendar (read-only): {status}")

        target_folder = ALLOWED_FOLDERS[0]
        shutil.move(filename, os.path.join(target_folder, filename))

        print(f"✅ File mới: {filename} → {target_folder}")

    save_json(DUPLICATE_LOG, duplicate_log)
    save_json(CALENDAR_LOG, calendar_log)

    print("🏁 Hoàn tất – không ghi Calendar – không đụng mobile store")


if __name__ == "__main__":
    main()
