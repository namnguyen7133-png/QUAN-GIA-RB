import os
import json
from datetime import datetime

# ===== cấu hình log =====
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

DUP_LOG = os.path.join(LOG_DIR, "duplicate_log.json")
EVENT_LOG = os.path.join(LOG_DIR, "event_log.json")

# ===== dữ liệu giả (nếu chưa có) =====
duplicates = []
moved = 0

# ========= LOG JSON =========
with open(DUP_LOG, "w", encoding="utf-8") as f:
    json.dump(duplicates, f, indent=2, ensure_ascii=False)

event = {
    "time": datetime.utcnow().isoformat(),
    "duplicates": len(duplicates),
    "moved": moved
}

# đảm bảo EVENT_LOG luôn là list
data = []

if os.path.exists(EVENT_LOG):
    try:
        with open(EVENT_LOG, encoding="utf-8") as f:
            loaded = json.load(f)
            if isinstance(loaded, list):
                data = loaded
    except Exception:
        pass

data.append(event)

with open(EVENT_LOG, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
