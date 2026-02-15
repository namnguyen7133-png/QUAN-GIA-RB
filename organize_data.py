import os
import json
import hashlib
from datetime import datetime
import shutil

# ===== VÙNG CHO PHÉP =====
ALLOWED_FOLDERS = ['SUC_KHOE', 'CHAM_SOC_GIA_DINH', 'LAP_TRINH_ROBOT']

# ===== VÙNG CẤM (mobile store) =====
FORBIDDEN_KEYWORDS = ['mobile', 'store', 'appstore', 'playstore']

DUPLICATE_LOG = 'duplicate_log.json'
CALENDAR_LOG = 'calendar_event_log.json'


def is_forbidden(path: str) -> bool:
    p = path.lower()
    return any(k in p for k in FORBIDDEN_KEYWORDS)


def is_allowed_folder(path: str) -> bool:
    return any(path.startswith(f) for f in ALLOWED_FOLDERS)


def load_json(path):
    if not os.path.exists(path):
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


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

    # đảm bảo thư mục tồn tại
    for folder in ALLOWED_FOLDERS:
        if is_forbidden(folder):
            print(f"⛔ Bỏ qua thư mục cấm: {folder}")
            continue
        os.makedirs(folder, exist_ok=True)

    # quét file HTML ở root
    for filename in os.listdir('.'):
        if is_forbidden(filename):
            print(f"⛔ Bỏ qua vùng cấm: {filename}")
            continue

        if not filename.lower().endswith('.html'):
            continue
        if not os.path.isfile(filename):
            continue

        try:
            with open(filename, 'rb') as f:
                content = f.read()
        except Exception as e:
            print(f"⚠️ Không đọc được {filename}: {e}")
            continue

        content_hash = hash_html(content)

        # === CHECK TRÙNG ===
        if content_hash in duplicate_log:
            print(f"🔁 Trùng: {filename}")
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
        print(f"📅 Calendar: {status}")

        # ===== CHỌN THƯ MỤC ĐÍCH =====
        target_folder = ALLOWED_FOLDERS[0]

        if is_forbidden(target_folder):
            print(f"⛔ Target bị cấm: {target_folder}")
            continue

        try:
            shutil.move(filename, os.path.join(target_folder, filename))
            print(f"✅ {filename} → {target_folder}")
        except Exception as e:
            print(f"⚠️ Move lỗi {filename}: {e}")

    save_json(DUPLICATE_LOG, duplicate_log)
    save_json(CALENDAR_LOG, calendar_log)

    print("🏁 Hoàn tất – không đụng mobile store")


if __name__ == "__main__":
    main()
